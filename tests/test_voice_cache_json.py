"""Voice cache must use JSON, not pickle, and survive a process restart."""

import gzip
import json
import os
import time

import pytest

from superfreetts_addon import constants
from superfreetts_addon import languages
from superfreetts_addon import voice
from superfreetts_addon.voice_cache import CACHE_SUFFIX, VoiceListCache


def _sample_voice():
    return voice.TtsVoice_v3(
        name="Alice",
        voice_key={"id": "alice"},
        options={"speed": {"default": 1.0}},
        service="TestService",
        gender=constants.Gender.Female,
        audio_languages=[languages.AudioLanguage.en_US],
        service_fee=constants.ServiceFee.free,
    )


@pytest.mark.unit
def test_voice_cache_round_trips_json_across_instances(tmp_path):
    first = VoiceListCache(str(tmp_path), ttl_seconds=3600)
    first.set("TestService", [_sample_voice()])

    cache_file = tmp_path / f"TestService{CACHE_SUFFIX}"
    assert cache_file.exists()
    assert not list(tmp_path.glob("*.pkl.gz"))

    with gzip.open(cache_file, "rt", encoding="utf-8") as handle:
        payload = json.load(handle)
    assert payload["version"] == 2
    assert payload["voices"][0]["name"] == "Alice"

    # A new instance represents a fresh Anki launch: the disk entry must be
    # usable even though the in-memory timestamp map is empty.
    second = VoiceListCache(str(tmp_path), ttl_seconds=3600)
    restored = second.get("TestService")
    assert restored is not None
    assert len(restored) == 1
    assert restored[0].name == "Alice"
    assert restored[0].voice_key == {"id": "alice"}
    assert restored[0].gender is constants.Gender.Female
    assert restored[0].audio_languages == [languages.AudioLanguage.en_US]


@pytest.mark.unit
def test_voice_cache_rejects_corrupt_json(tmp_path):
    cache = VoiceListCache(str(tmp_path), ttl_seconds=3600)
    cache_file = cache.get_disk_path("TestService")
    cache_file.write_bytes(b"not-json")

    assert cache.get("TestService") is None
    assert not cache_file.exists()


@pytest.mark.unit
def test_voice_cache_cleanup_removes_expired_and_legacy_files(tmp_path):
    cache = VoiceListCache(str(tmp_path), ttl_seconds=1)
    cache.set("TestService", [_sample_voice()])
    cache_file = cache.get_disk_path("TestService")
    old = time.time() - 60
    os.utime(cache_file, (old, old))

    legacy = tmp_path / "OldService_voices.pkl.gz"
    legacy.write_bytes(b"pickle")

    removed = cache.cleanup_expired()

    assert removed == 2
    assert not cache_file.exists()
    assert not legacy.exists()
