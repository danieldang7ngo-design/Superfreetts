"""Extended coverage for the JSON voice cache and delta cache."""

import gzip
import json
import os
import time
from unittest.mock import MagicMock

import pytest

from superfreetts_addon import constants
from superfreetts_addon import languages
from superfreetts_addon import voice
from superfreetts_addon import voice_cache
from superfreetts_addon.voice_cache import DeltaCache, VoiceListCache


def _sample_voice(name="Alice"):
    return voice.TtsVoice_v3(
        name=name,
        voice_key={"id": name.lower()},
        options={"speed": {"default": 1.0}},
        service="TestService",
        gender=constants.Gender.Female,
        audio_languages=[languages.AudioLanguage.en_US],
        service_fee=constants.ServiceFee.free,
    )


@pytest.mark.unit
def test_memory_hit_and_expiry(tmp_path, monkeypatch):
    cache = VoiceListCache(str(tmp_path), ttl_seconds=100)
    cache.set("Svc", [_sample_voice()])

    voices = [_sample_voice()]
    cache.memory_cache[cache.get_cache_key("Svc")] = voices
    assert cache.get("Svc") is voices

    real_time = time.time
    monkeypatch.setattr(voice_cache.time, "time", lambda: real_time() + 1000)
    assert cache.get("Svc") is None


@pytest.mark.unit
def test_expired_disk_entry_is_a_miss(tmp_path):
    cache = VoiceListCache(str(tmp_path), ttl_seconds=10)
    cache.set("Svc", [_sample_voice()])
    path = cache.get_disk_path("Svc")
    old = time.time() - 60
    os.utime(path, (old, old))

    fresh_process = VoiceListCache(str(tmp_path), ttl_seconds=10)
    assert fresh_process.get("Svc") is None
    assert path.exists()  # expired entries are removed by cleanup_expired


@pytest.mark.unit
def test_unknown_voice_metadata_falls_back_to_defaults(tmp_path):
    cache = VoiceListCache(str(tmp_path), ttl_seconds=3600)
    path = cache.get_disk_path("Svc")
    payload = {
        "version": voice_cache.CACHE_FORMAT_VERSION,
        "voices": [
            {
                "name": "Mystery",
                "voice_key": {"id": "mystery"},
                "service": "TestService",
                "gender": "Alien",
                "audio_languages": ["Klingon"],
                "service_fee": "barter",
            }
        ],
    }
    with gzip.open(path, "wt", encoding="utf-8") as handle:
        json.dump(payload, handle)

    restored = cache.get("Svc")
    assert restored is not None
    assert restored[0].gender is constants.Gender.Any
    assert restored[0].service_fee is constants.ServiceFee.free
    assert restored[0].audio_languages == [languages.AudioLanguage.en_US]


@pytest.mark.unit
def test_unsupported_cache_version_is_deleted(tmp_path):
    cache = VoiceListCache(str(tmp_path), ttl_seconds=3600)
    path = cache.get_disk_path("Svc")
    with gzip.open(path, "wt", encoding="utf-8") as handle:
        json.dump({"version": 1, "voices": []}, handle)

    assert cache.get("Svc") is None
    assert not path.exists()


@pytest.mark.unit
def test_unchanged_voice_list_does_not_rewrite_disk(tmp_path, monkeypatch):
    cache = VoiceListCache(str(tmp_path), ttl_seconds=3600)
    cache.set("Svc", [_sample_voice()])
    replace = MagicMock()
    monkeypatch.setattr(voice_cache.os, "replace", replace)

    cache.set("Svc", [_sample_voice()])
    replace.assert_not_called()


@pytest.mark.unit
def test_disk_write_failure_is_non_fatal_and_removes_temp(tmp_path, monkeypatch):
    cache = VoiceListCache(str(tmp_path), ttl_seconds=3600)

    def fail_replace(src, dst):
        raise OSError("disk full")

    monkeypatch.setattr(voice_cache.os, "replace", fail_replace)
    cache.set("Svc", [_sample_voice()])

    assert cache.get("Svc") is not None
    assert not list(tmp_path.glob("*.tmp"))


@pytest.mark.unit
def test_clear_one_and_all_services(tmp_path):
    cache = VoiceListCache(str(tmp_path), ttl_seconds=3600)
    cache.set("One", [_sample_voice("One")])
    cache.set("Two", [_sample_voice("Two")])
    legacy = tmp_path / "One_voices.pkl.gz"
    legacy.write_bytes(b"old")

    cache.clear("One")
    assert cache.get_disk_path("One").exists() is False
    assert not legacy.exists()
    assert cache.get_disk_path("Two").exists()

    cache.clear()
    assert not cache.get_disk_path("Two").exists()
    assert cache.memory_cache == {}
    assert cache.cache_times == {}
    assert cache.cache_checksums == {}


@pytest.mark.unit
def test_get_stats_reports_memory_and_disk(tmp_path):
    cache = VoiceListCache(str(tmp_path), ttl_seconds=3600)
    cache.set("Svc", [_sample_voice()])

    stats = cache.get_stats()
    assert stats["memory_entries"] == 1
    assert stats["disk_entries"] == 1
    assert stats["disk_size_mb"] >= 0
    assert stats["ttl_seconds"] == 3600


@pytest.mark.unit
def test_delta_cache_full_and_incremental_updates():
    cache = DeltaCache()
    first = cache.update([{"id": "a"}, {"id": "b"}], is_full_update=True)
    assert first["type"] == "full"
    assert first["changes"] == 2
    assert first["compression_ratio"] == 0

    second = cache.update([{"id": "b"}, {"id": "c"}])
    assert second["type"] == "incremental"
    assert second["changes"] == 2
    assert "c" in cache.delta["added"]
    assert "a" in cache.delta["removed"]
    assert cache.base_snapshot is not None

    empty = cache.update([])
    assert empty["total_items"] == 0
    assert empty["compression_ratio"] == 0
