"""Tests for RAM detection that do not depend on psutil being installed."""

from unittest.mock import MagicMock, patch

import pytest

from superfreetts_addon import system_utils
from superfreetts_addon import tts_orchestrator


@pytest.mark.unit
def test_linux_meminfo_uses_mem_available(tmp_path):
    meminfo = tmp_path / "meminfo"
    meminfo.write_text(
        "MemTotal: 16384000 kB\n"
        "MemFree: 1024000 kB\n"
        "Buffers: 1000 kB\n"
        "Cached: 2000 kB\n"
        "MemAvailable: 2097152 kB\n",
        encoding="utf-8",
    )
    assert system_utils._linux_available_ram_mb(str(meminfo)) == 2048


@pytest.mark.unit
def test_linux_meminfo_falls_back_to_free_plus_cache(tmp_path):
    meminfo = tmp_path / "meminfo"
    meminfo.write_text(
        "MemTotal: 16384000 kB\n"
        "MemFree: 1048576 kB\n"
        "Buffers: 2048 kB\n"
        "Cached: 4096 kB\n",
        encoding="utf-8",
    )
    assert system_utils._linux_available_ram_mb(str(meminfo)) == 1030


@pytest.mark.unit
def test_get_available_ram_prefers_psutil(monkeypatch):
    monkeypatch.setattr(system_utils, "_psutil_available_ram_mb", lambda: 1234)
    assert system_utils.get_available_ram_mb() == 1234
    assert system_utils.get_ram_detection_source() == "psutil"


@pytest.mark.unit
def test_get_available_ram_uses_linux_fallback(monkeypatch):
    monkeypatch.setattr(system_utils, "_psutil_available_ram_mb", lambda: None)
    monkeypatch.setattr(system_utils.platform, "system", lambda: "Linux")
    monkeypatch.setattr(system_utils, "_linux_available_ram_mb", lambda: 4321)
    assert system_utils.get_available_ram_mb() == 4321
    assert system_utils.get_ram_detection_source() == "linux_meminfo"


@pytest.mark.unit
def test_get_available_ram_returns_none_when_every_source_fails(monkeypatch):
    monkeypatch.setattr(system_utils, "_psutil_available_ram_mb", lambda: None)
    monkeypatch.setattr(system_utils.platform, "system", lambda: "Linux")

    def fail():
        raise OSError("no meminfo")

    monkeypatch.setattr(system_utils, "_linux_available_ram_mb", fail)
    assert system_utils.get_available_ram_mb() is None


@pytest.mark.unit
def test_compute_accepts_premeasured_ram():
    assert system_utils.compute_ram_aware_concurrency(
        cpu_default=16,
        ram_per_process_mb=500,
        available_ram_mb=8580,
    ) == 8


@pytest.mark.unit
def test_build_engine_config_logs_real_ram_and_caps(monkeypatch):
    orch = tts_orchestrator.TTSOrchestrator(MagicMock())
    logger = MagicMock()
    monkeypatch.setattr(tts_orchestrator, "logger", logger)
    monkeypatch.setattr(system_utils, "get_max_workers", lambda: 16)
    monkeypatch.setattr(system_utils, "get_available_ram_mb", lambda: 8580)
    monkeypatch.setattr(system_utils, "get_ram_detection_source", lambda: "linux_meminfo")
    with patch.object(orch, "auto_scale_pool"):
        config = orch.build_engine_config({})

    assert config["Piper"] == 16
    assert config["Kokoro"] == 8
    assert config["MMS"] == 8
    info_messages = [str(call.args[0]) for call in logger.info.call_args_list]
    assert any(
        "[RAM] source=linux_meminfo available_mb=8580" in message
        for message in info_messages
    )
    assert any("[RAM-CAP] KokoroTTS" in message for message in info_messages)


@pytest.mark.unit
def test_build_engine_config_warns_when_ram_unknown(monkeypatch):
    orch = tts_orchestrator.TTSOrchestrator(MagicMock())
    logger = MagicMock()
    monkeypatch.setattr(tts_orchestrator, "logger", logger)
    monkeypatch.setattr(system_utils, "get_max_workers", lambda: 8)
    monkeypatch.setattr(system_utils, "get_available_ram_mb", lambda: None)
    monkeypatch.setattr(system_utils, "get_ram_detection_source", lambda: "unknown")
    with patch.object(orch, "auto_scale_pool"):
        config = orch.build_engine_config({})

    assert config["Kokoro"] == 8
    warning_messages = [str(call.args[0]) for call in logger.warning.call_args_list]
    assert any(
        "local engine pools are NOT RAM-capped" in message
        for message in warning_messages
    )


@pytest.mark.unit
def test_manual_override_is_kept_but_warned(monkeypatch):
    orch = tts_orchestrator.TTSOrchestrator(MagicMock())
    logger = MagicMock()
    monkeypatch.setattr(tts_orchestrator, "logger", logger)
    monkeypatch.setattr(system_utils, "get_max_workers", lambda: 16)
    monkeypatch.setattr(system_utils, "get_available_ram_mb", lambda: 2000)
    monkeypatch.setattr(system_utils, "get_ram_detection_source", lambda: "linux_meminfo")
    with patch.object(orch, "auto_scale_pool"):
        config = orch.build_engine_config(
            {"KokoroTTS": {"concurrency_workers": 12}}
        )

    assert config["Kokoro"] == 12
    warning_messages = [str(call.args[0]) for call in logger.warning.call_args_list]
    assert any("[RAM-WARN] KokoroTTS" in message for message in warning_messages)
