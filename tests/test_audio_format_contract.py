"""Audio format contract: the file extension must match the bytes inside.

Covers the 2026-10-22 audit finding P1-1: local engines returned WAV while
the cache named files after the *requested* format, so the default mp3
preference produced WAV payloads inside .mp3 files.
"""

import os
import sys

import pytest

from tests import mock_anki

mock_anki.mock_all()

addon_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, addon_dir)
sys.path.insert(0, os.path.join(addon_dir, "external"))

from superfreetts_addon import audio_file_store, config_models, options, voice


WAV_BYTES = b"RIFF" + (36).to_bytes(4, "little") + b"WAVEfmt " + b"\x00" * 64
MP3_BYTES = b"ID3\x04\x00\x00\x00\x00\x00\x00" + b"\x00" * 64
OGG_BYTES = b"OggS" + b"\x00" * 64


class MockAnkiUtils:
    def __init__(self, user_files_dir):
        self.user_files_dir = str(user_files_dir)

    def get_user_files_dir(self):
        return self.user_files_dir


def make_voice_id(name="Jenny", service="EdgeTTS"):
    return voice.TtsVoiceId_v3({"name": name}, service)


def make_store(tmp_path, audio_format):
    prefs = config_models.Preferences()
    prefs.audio_format = audio_format
    return audio_file_store.AudioFileStore(MockAnkiUtils(tmp_path), lambda: prefs)


@pytest.mark.unit
@pytest.mark.parametrize(
    "payload,expected",
    [
        (WAV_BYTES, options.AudioFormat.wav),
        (MP3_BYTES, options.AudioFormat.mp3),
        (OGG_BYTES, options.AudioFormat.ogg_opus),
        (b"\xff\xfb\x90\x00" + b"\x00" * 20, options.AudioFormat.mp3),
        (b"", None),
        (b"audio-bytes", None),
        (b"RIFF1234JUNK", None),
    ],
)
def test_detect_audio_format_from_magic_bytes(payload, expected):
    assert audio_file_store.detect_audio_format(payload) == expected


@pytest.mark.unit
def test_default_preferences_use_wav():
    assert config_models.Preferences().audio_format == "wav"
    assert config_models.deserialize_preferences({}).audio_format == "wav"


@pytest.mark.unit
def test_wav_bytes_requested_as_mp3_are_saved_with_wav_extension(tmp_path):
    store = make_store(tmp_path, "mp3")
    request_key = store.build_request_key("hello", make_voice_id(), {})
    assert request_key.audio_format == options.AudioFormat.mp3.name

    result = store.write_audio_file_atomic(request_key, WAV_BYTES)

    assert result.audio_filename.endswith(".wav")
    with open(result.full_filename, "rb") as f:
        assert f.read() == WAV_BYTES

    # The cache lookup for the same request must find the real file.
    cached = store.get_cached_file(request_key)
    assert cached is not None
    assert cached.full_filename == result.full_filename
    assert cached.audio_filename.endswith(".wav")


@pytest.mark.unit
def test_mp3_bytes_requested_as_wav_are_saved_with_mp3_extension(tmp_path):
    store = make_store(tmp_path, "wav")
    request_key = store.build_request_key("hello", make_voice_id(), {})

    result = store.write_audio_file_atomic(request_key, MP3_BYTES)

    assert result.audio_filename.endswith(".mp3")
    assert os.path.exists(result.full_filename)
    assert store.get_cached_file(request_key).audio_filename.endswith(".mp3")


@pytest.mark.unit
def test_matching_format_keeps_the_requested_extension(tmp_path):
    store = make_store(tmp_path, "wav")
    request_key = store.build_request_key("hello", make_voice_id(), {})
    result = store.write_audio_file_atomic(request_key, WAV_BYTES)
    assert result.audio_filename.endswith(".wav")


@pytest.mark.unit
def test_stale_cache_file_with_wrong_content_is_discarded(tmp_path):
    """Old builds wrote WAV bytes into .mp3 names; those must not be served."""
    store = make_store(tmp_path, "mp3")
    request_key = store.build_request_key("hello", make_voice_id(), {})
    stale = store.get_file_result(request_key)
    os.makedirs(os.path.dirname(stale.full_filename), exist_ok=True)
    with open(stale.full_filename, "wb") as f:
        f.write(WAV_BYTES)

    assert store.get_cached_file(request_key) is None
    assert not os.path.exists(stale.full_filename)


@pytest.mark.unit
def test_unknown_bytes_are_not_deleted(tmp_path):
    """Content we cannot fingerprint must be treated leniently."""
    store = make_store(tmp_path, "wav")
    request_key = store.build_request_key("hello", make_voice_id(), {})
    result = store.get_file_result(request_key)
    os.makedirs(os.path.dirname(result.full_filename), exist_ok=True)
    with open(result.full_filename, "wb") as f:
        f.write(b"audio-bytes")

    assert store.get_cached_file(request_key) is not None
    assert os.path.exists(result.full_filename)


@pytest.mark.unit
def test_legacy_ogg_preference_degrades_to_wav(tmp_path):
    store = make_store(tmp_path, "ogg")
    assert store.resolve_audio_format({}) == options.AudioFormat.wav
    key = store.build_request_key("hello", make_voice_id(), {})
    assert key.audio_format == options.AudioFormat.wav.name
    assert not store.get_file_result(key).audio_filename.endswith(".ogg")


@pytest.mark.unit
def test_legacy_ogg_voice_option_degrades_to_wav(tmp_path):
    store = make_store(tmp_path, "wav")
    resolved = store.resolve_audio_format({options.AUDIO_FORMAT_PARAMETER: "ogg"})
    assert resolved == options.AudioFormat.wav


@pytest.mark.unit
def test_legacy_pcm_voice_option_maps_to_wav(tmp_path):
    store = make_store(tmp_path, "wav")
    resolved = store.resolve_audio_format({options.AUDIO_FORMAT_PARAMETER: "pcm"})
    assert resolved == options.AudioFormat.wav


@pytest.mark.unit
def test_unknown_voice_option_format_is_ignored_not_fatal(tmp_path):
    store = make_store(tmp_path, "wav")
    resolved = store.resolve_audio_format({options.AUDIO_FORMAT_PARAMETER: "flac"})
    assert resolved == options.AudioFormat.wav


@pytest.mark.unit
def test_unknown_preference_falls_back_to_wav(tmp_path):
    store = make_store(tmp_path, "flac")
    assert store.resolve_audio_format({}) == options.AudioFormat.wav


@pytest.mark.unit
@pytest.mark.parametrize(
    "filename,is_cache",
    [
        ("superfreetts-" + "a" * 56 + ".wav", True),
        ("superfreetts-" + "0" * 56 + ".mp3", True),
        ("superfreetts-" + "f" * 56 + ".ogg", True),
        ("superfreetts-" + "a" * 56 + ".tmp", False),
        ("superfreetts-" + "a" * 55 + ".wav", False),
        ("superfreetts-" + "g" * 56 + ".wav", False),
        ("usage_log.json", False),
        ("superfreetts.log", False),
        ("batch_state", False),
        ("", False),
    ],
)
def test_cache_filename_predicate(filename, is_cache):
    assert audio_file_store.is_cache_audio_filename(filename) is is_cache
