import os
import sys

from tests import mock_anki

mock_anki.mock_all()

addon_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, addon_dir)
sys.path.insert(0, os.path.join(addon_dir, "external"))

from superfreetts_addon import audio_file_store, config_models, options, voice


class MockAnkiUtils:
    def __init__(self, user_files_dir):
        self.user_files_dir = str(user_files_dir)

    def get_user_files_dir(self):
        return self.user_files_dir


def make_voice_id(name="Jenny", service="EdgeTTS"):
    return voice.TtsVoiceId_v3({"name": name}, service)


def make_store(tmp_path, audio_format="mp3"):
    prefs = config_models.Preferences()
    prefs.audio_format = audio_format
    return audio_file_store.AudioFileStore(MockAnkiUtils(tmp_path), lambda: prefs)


def test_audio_request_key_hash_is_stable_for_option_order(tmp_path):
    store = make_store(tmp_path)
    voice_id = make_voice_id()

    left = store.build_request_key("hello", voice_id, {"b": 2, "a": 1})
    right = store.build_request_key("hello", voice_id, {"a": 1, "b": 2})

    assert left.hash() == right.hash()


def test_audio_format_pref_and_voice_option_resolution(tmp_path):
    store = make_store(tmp_path, audio_format="ogg")

    # OGG is not encodable by any bundled engine, so the legacy preference
    # degrades to WAV instead of producing an invalid .ogg file.
    assert store.resolve_audio_format({}) == options.AudioFormat.wav
    assert store.resolve_audio_format({options.AUDIO_FORMAT_PARAMETER: "mp3"}) == options.AudioFormat.mp3
    assert store.resolve_audio_format({options.AUDIO_FORMAT_PARAMETER: "wav"}) == options.AudioFormat.wav


def test_cached_file_hit_requires_non_empty_file(tmp_path):
    store = make_store(tmp_path)
    request_key = store.build_request_key("hello", make_voice_id(), {})
    result = store.get_file_result(request_key)
    os.makedirs(os.path.dirname(result.full_filename), exist_ok=True)

    open(result.full_filename, "wb").close()
    assert store.get_cached_file(request_key) is None

    with open(result.full_filename, "wb") as f:
        f.write(b"audio")
    cached = store.get_cached_file(request_key)
    assert cached is not None
    assert cached.audio_filename == result.audio_filename


def test_atomic_write_creates_final_file(tmp_path):
    store = make_store(tmp_path)
    request_key = store.build_request_key("hello", make_voice_id(), {})

    result = store.write_audio_file_atomic(request_key, b"audio-bytes")

    with open(result.full_filename, "rb") as f:
        assert f.read() == b"audio-bytes"


def test_verified_cache_skips_repeated_magic_byte_reads(tmp_path, monkeypatch):
    store = make_store(tmp_path)
    request_key = store.build_request_key("hello", make_voice_id(), {})
    result = store.get_file_result(request_key)
    os.makedirs(os.path.dirname(result.full_filename), exist_ok=True)
    with open(result.full_filename, "wb") as f:
        f.write(b"ID3" + b"0" * 32)

    reads = []
    original = audio_file_store._read_magic_bytes

    def counting_read(path, count=12):
        reads.append(path)
        return original(path, count)

    monkeypatch.setattr(audio_file_store, "_read_magic_bytes", counting_read)

    assert store.get_cached_file(request_key) is not None
    assert store.get_cached_file(request_key) is not None
    assert len(reads) == 1

    store.clear_verified_cache()
    assert store.get_cached_file(request_key) is not None
    assert len(reads) == 2


def test_cleanup_removal_respects_verified_cache(tmp_path):
    store = make_store(tmp_path)
    request_key = store.build_request_key("hello", make_voice_id(), {})
    result = store.write_audio_file_atomic(request_key, b"ID3" + b"0" * 32)

    assert store.remove_cached_file_if_unused(result.full_filename) is False
    assert os.path.exists(result.full_filename)

    store.clear_verified_cache()
    assert store.remove_cached_file_if_unused(result.full_filename) is True
    assert not os.path.exists(result.full_filename)


def test_verified_cache_is_bounded(tmp_path, monkeypatch):
    store = make_store(tmp_path)
    store.MAX_VERIFIED_ENTRIES = 2
    for index in range(3):
        store._remember_verified(f"/tmp/file-{index}.wav")
        store._remember_verified(f"/tmp/file-{index}.wav")

    assert len(store._verified_files) == 2
    assert "/tmp/file-0.wav" not in store._verified_files


def test_path_generation_is_deterministic(tmp_path):
    store = make_store(tmp_path)
    voice_id1 = make_voice_id(name="Jenny", service="EdgeTTS")
    voice_id2 = make_voice_id(name="Guy", service="EdgeTTS")

    key1_a = store.build_request_key("hello", voice_id1, {"speed": 10})
    key1_b = store.build_request_key("hello", voice_id1, {"speed": 10})
    key2 = store.build_request_key("hello", voice_id2, {"speed": 10})
    key3 = store.build_request_key("different", voice_id1, {"speed": 10})

    # Same inputs -> same hash
    assert key1_a.hash() == key1_b.hash()
    assert store.get_full_audio_file_name(key1_a.hash(), options.AudioFormat.mp3) == store.get_full_audio_file_name(key1_b.hash(), options.AudioFormat.mp3)

    # Different inputs -> different hashes
    assert key1_a.hash() != key2.hash()
    assert key1_a.hash() != key3.hash()


def test_resolve_audio_format_fallback(tmp_path):
    store = make_store(tmp_path, audio_format="wav")
    # Missing/unknown preference falls back to WAV, the only format every
    # bundled local engine can actually produce.
    assert store.resolve_audio_format(None) == options.AudioFormat.wav
    assert config_models.Preferences().audio_format == "wav"


