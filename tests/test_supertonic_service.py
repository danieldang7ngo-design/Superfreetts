import base64
import os
import sys
import types
from unittest.mock import patch

import pytest

import tests.mock_anki as mock_anki

mock_anki.mock_all()

addon_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, addon_dir)
sys.path.insert(0, os.path.join(addon_dir, "external"))

from superfreetts_addon import batch_constants, batch_executor, languages, superfreetts
from superfreetts_addon.services import service_supertonic, supertonic_runner


def make_service(tmp_path):
    svc = service_supertonic.SupertonicTTS()
    svc.configure(
        {
            "engine_path": "python.exe",
            "cache_path": str(tmp_path / "cache"),
            "custom_voices_path": str(tmp_path / "voices"),
            "total_steps": 8,
            "max_chunk_length": 300,
            "silence_duration": 0.3,
        }
    )
    return svc


def test_voice_list_placeholder_when_model_missing(tmp_path):
    svc = make_service(tmp_path)
    voices = svc.voice_list()
    assert len(voices) == 1
    assert voices[0].voice_key == "supertonic_none"
    assert voices[0].service == "SupertonicTTS"


def test_voice_list_includes_builtin_voices_when_installed(tmp_path):
    svc = make_service(tmp_path)
    with patch.object(service_supertonic, "is_supertonic_ready", return_value=True):
        voices = svc.voice_list()

    keys = {(v.voice_key["style"], v.voice_key["lang"]) for v in voices}
    assert {("M1", "en"), ("M2", "en"), ("M3", "en"), ("M4", "en"), ("M5", "en"), ("F1", "en"), ("F2", "en"), ("F3", "en"), ("F4", "en"), ("F5", "en")} <= keys
    assert ("F1", "vi") in keys
    assert len([v for v in voices if v.voice_key["style"].startswith("custom:")]) == 0


def test_custom_voice_scan_and_reserved_collision(tmp_path):
    voices_dir = tmp_path / "voices"
    voices_dir.mkdir()
    (voices_dir / "my voice.json").write_text("{}", encoding="utf-8")
    (voices_dir / "M1.json").write_text("{}", encoding="utf-8")
    svc = make_service(tmp_path)

    with patch.object(service_supertonic, "is_supertonic_ready", return_value=True):
        voices = svc.voice_list()

    keys = {(v.voice_key["style"], v.voice_key["lang"]) for v in voices}
    assert ("custom:my voice", "en") in keys
    assert ("custom:my voice", "vi") in keys
    assert not any(style == "custom:M1" for style, _ in keys)
    assert service_supertonic.is_reserved_voice_name("M1")


def test_language_mapping_and_fallback(tmp_path):
    svc = make_service(tmp_path)
    voice = types.SimpleNamespace(audio_languages=[languages.AudioLanguage.vi_VN])
    assert svc._language_code(voice) == "vi"

    voice.audio_languages = [languages.AudioLanguage.af_ZA]
    assert svc._language_code(voice) == "na"

    svc.configure({"lang_override": "ko", "cache_path": str(tmp_path / "cache")})
    assert svc._language_code(voice) == "ko"


def test_dict_voice_key_carries_language_and_style(tmp_path):
    svc = make_service(tmp_path)
    voice = types.SimpleNamespace(voice_key={"style": "F1", "lang": "vi"}, audio_languages=[languages.AudioLanguage.vi_VN])

    task = svc._base_task("xin chao", voice, {})

    assert task["voice"] == "F1"
    assert task["lang"] == "vi"


def test_batch_executor_selects_supertonic_pool():
    executor = batch_executor.MultiEngineExecutor(engine_config={"Supertonic": 3, "default": 1})
    try:
        selected = executor.get_executor("SupertonicTTS")
        assert selected._max_workers == 3
    finally:
        executor.shutdown(wait=False)


def test_engine_config_scales_supertonic_without_touching_edge_cap():
    instance = superfreetts.SuperFreeTTS.__new__(superfreetts.SuperFreeTTS)
    with patch("superfreetts_addon.cpu_utils.CPUInfo.get_max_workers", return_value=4):
        config = instance._build_engine_config(
            {
                "SupertonicTTS": {"concurrency_workers": 8},
                "EdgeTTS": {"concurrency_workers": 99},
            }
        )

    assert config["Supertonic"] == 4
    assert config["EdgeTTS"] == batch_constants.EDGETTS_MAX_WORKERS


def test_sequence_mode_uses_configured_supertonic_workers():
    instance = superfreetts.SuperFreeTTS.__new__(superfreetts.SuperFreeTTS)
    instance.executor = batch_executor.MultiEngineExecutor(engine_config={"Supertonic": 8, "default": 1})
    voice = types.SimpleNamespace(voice_id=types.SimpleNamespace(service="SupertonicTTS"))
    items = [
        (f"key-{idx}", {"chosen_voice": voice}, [idx])
        for idx in range(12)
    ]
    try:
        with patch("superfreetts_addon.cpu_utils.CPUInfo.get_max_workers", return_value=16):
            assert instance._get_sequence_service_limits(items) == {"SupertonicTTS": 8}
            assert instance._get_sequence_worker_limit(items) == 8
    finally:
        instance.executor.shutdown(wait=False)


class FakeTTS:
    calls = []

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def generate(self, **kwargs):
        FakeTTS.calls.append(kwargs)
        if kwargs["text"] == "bad":
            raise RuntimeError("bad text")
        return b"RIFFfake-wav"


def install_fake_supertonic(monkeypatch):
    FakeTTS.calls = []
    module = types.ModuleType("supertonic")
    module.TTS = FakeTTS
    module.get_voice_style = lambda name: {"style": name}
    module.get_voice_style_from_path = lambda path: {"voice_path": path}
    monkeypatch.setitem(sys.modules, "supertonic", module)
    supertonic_runner._ENGINE = None
    supertonic_runner._ENGINE_CACHE_KEY = None
    supertonic_runner._VOICE_STYLE_CACHE = {}


def test_runner_single_passes_options(monkeypatch, tmp_path):
    install_fake_supertonic(monkeypatch)
    response = supertonic_runner.handle_request(
        {
            "text": "hello",
            "voice": "F1",
            "cache_path": str(tmp_path),
            "lang": "en",
            "speed": 1.2,
            "total_steps": 9,
            "max_chunk_length": 123,
            "silence_duration": 0.4,
        }
    )

    assert response["status"] == "ok"
    assert base64.b64decode(response["audio_b64"]) == b"RIFFfake-wav"
    assert FakeTTS.calls[0]["voice"] == {"style": "F1"}
    assert FakeTTS.calls[0]["speed"] == 1.2
    assert FakeTTS.calls[0]["total_steps"] == 9


def test_runner_batch_preserves_order_and_item_failures(monkeypatch, tmp_path):
    install_fake_supertonic(monkeypatch)
    response = supertonic_runner.handle_request(
        {
            "action": "generate_batch",
            "tasks": [
                {"text": "one", "voice": "M1", "cache_path": str(tmp_path)},
                {"text": "bad", "voice": "M1", "cache_path": str(tmp_path)},
                {"text": "two", "voice": "M1", "cache_path": str(tmp_path)},
            ],
        }
    )

    assert response["status"] == "ok"
    assert [item["status"] for item in response["results"]] == ["ok", "error", "ok"]
