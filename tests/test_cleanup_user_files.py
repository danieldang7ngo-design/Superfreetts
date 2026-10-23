"""Cache cleanup must only delete audio cache entries, never user data.

Regression test for the 2026-10-22 audit finding P1-4: cleanup_user_files()
used to delete *every* top-level file in user_files older than the retention
window, including usage_log.json and the debug log.
"""

import os
import time
import threading
from unittest.mock import MagicMock

import pytest

from superfreetts_addon import audio_file_store, config_models, superfreetts, voice


def make_stts(tmp_path, retention_days=30, cache_enabled=True):
    (tmp_path / "user_files").mkdir(parents=True, exist_ok=True)
    stts = object.__new__(superfreetts.SuperFreeTTS)
    anki_utils = MagicMock()
    anki_utils.get_addon_dir.return_value = str(tmp_path)
    stts.anki_utils = anki_utils
    prefs = config_models.Preferences()
    prefs.cache_retention_days = retention_days
    prefs.cache_enabled = cache_enabled
    stts.get_preferences = lambda: prefs
    return stts


def age_file(path, days=90):
    old = time.time() - days * 86400
    os.utime(path, (old, old))


@pytest.mark.unit
def test_only_audio_cache_is_deleted(tmp_path):
    stts = make_stts(tmp_path)
    user_files = tmp_path / "user_files"

    old_cache = user_files / ("superfreetts-" + "a" * 56 + ".wav")
    fresh_cache = user_files / ("superfreetts-" + "b" * 56 + ".mp3")
    usage_log = user_files / "usage_log.json"
    debug_log = user_files / "superfreetts.log"
    backup = user_files / "config-backup.json"
    checkpoint_dir = user_files / "batch_state"
    checkpoint_dir.mkdir()
    checkpoint = checkpoint_dir / "old.checkpoint.json"

    for path in (old_cache, fresh_cache, usage_log, debug_log, backup, checkpoint):
        path.write_bytes(b"x")
    age_file(old_cache)
    age_file(usage_log)
    age_file(debug_log)
    age_file(backup)
    age_file(checkpoint)

    stts.cleanup_user_files()

    assert not old_cache.exists(), "stale audio cache should be deleted"
    assert fresh_cache.exists(), "recent audio cache must be kept"
    assert usage_log.exists(), "usage_log.json is user data"
    assert debug_log.exists(), "debug log is user data"
    assert backup.exists(), "config backup is user data"
    assert checkpoint.exists(), "batch checkpoint enables resume"


@pytest.mark.unit
def test_cleanup_disabled_keeps_everything(tmp_path):
    stts = make_stts(tmp_path, cache_enabled=False)
    cache_file = tmp_path / "user_files" / ("superfreetts-" + "c" * 56 + ".wav")
    cache_file.write_bytes(b"x")
    age_file(cache_file)

    stts.cleanup_user_files()

    assert cache_file.exists()


@pytest.mark.unit
def test_retention_zero_keeps_everything(tmp_path):
    stts = make_stts(tmp_path, retention_days=0)
    cache_file = tmp_path / "user_files" / ("superfreetts-" + "d" * 56 + ".wav")
    cache_file.write_bytes(b"x")
    age_file(cache_file)

    stts.cleanup_user_files()

    assert cache_file.exists()


@pytest.mark.unit
def test_cleanup_ignores_subdirectories_and_odd_cache_names(tmp_path):
    stts = make_stts(tmp_path)
    user_files = tmp_path / "user_files"

    short_hash = user_files / ("superfreetts-" + "e" * 20 + ".wav")
    nested = user_files / "nested"
    nested.mkdir()
    nested_cache = nested / ("superfreetts-" + "f" * 56 + ".wav")
    short_hash.write_bytes(b"x")
    nested_cache.write_bytes(b"x")
    age_file(short_hash)
    age_file(nested_cache)

    stts.cleanup_user_files()

    assert short_hash.exists()
    assert nested_cache.exists()


@pytest.mark.unit
def test_scheduled_cleanup_runs_on_daemon_thread(tmp_path, monkeypatch):
    stts = make_stts(tmp_path)
    called = threading.Event()
    monkeypatch.setattr(stts, "cleanup_user_files", called.set)

    thread = stts.schedule_cleanup_user_files()

    assert thread.daemon is True
    assert called.wait(2.0), "scheduled cleanup did not run"
    assert stts._cleanup_thread is thread


@pytest.mark.unit
def test_cleanup_stops_when_profile_is_closing(tmp_path):
    stts = make_stts(tmp_path)
    stts._shutdown = True
    cache_file = tmp_path / "user_files" / ("superfreetts-" + "a" * 56 + ".wav")
    cache_file.write_bytes(b"x")
    age_file(cache_file)

    stts.cleanup_user_files()

    assert cache_file.exists()


@pytest.mark.unit
def test_cleanup_clears_audio_store_verified_cache(tmp_path):
    stts = make_stts(tmp_path)
    audio_store = MagicMock()
    stts.audio_store = audio_store
    cache_file = tmp_path / "user_files" / ("superfreetts-" + "b" * 56 + ".wav")
    cache_file.write_bytes(b"x")
    age_file(cache_file)

    stts.cleanup_user_files()

    assert not cache_file.exists()
    audio_store.clear_verified_cache.assert_called_once()


@pytest.mark.unit
def test_cleanup_does_not_delete_file_selected_by_live_cache(tmp_path):
    stts = make_stts(tmp_path)
    user_files = tmp_path / "user_files"
    stts.anki_utils.get_user_files_dir.return_value = str(user_files)
    store = audio_file_store.AudioFileStore(stts.anki_utils, stts.get_preferences)
    stts.audio_store = store

    voice_id = voice.TtsVoiceId_v3({"name": "Jenny"}, "EdgeTTS")
    request_key = store.build_request_key("hello", voice_id, {})
    result = store.write_audio_file_atomic(request_key, b"ID3" + b"0" * 32)
    age_file(result.full_filename)

    stts.cleanup_user_files()

    assert os.path.exists(result.full_filename)
