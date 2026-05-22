import os
import sys

from tests import mock_anki

mock_anki.mock_all()

addon_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, addon_dir)
sys.path.insert(0, os.path.join(addon_dir, "external"))

from superfreetss_addon import audio_file_store, config_models, options, voice


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

    assert store.resolve_audio_format({}) == options.AudioFormat.ogg_opus
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

