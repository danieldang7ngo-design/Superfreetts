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
    monkeypatch.setattr(system_utils, "get_cpu_threads", lambda: 8)
    monkeypatch.setattr(system_utils, "get_max_workers", lambda: 16)
    monkeypatch.setattr(system_utils, "get_available_ram_mb", lambda: 8580)
    monkeypatch.setattr(system_utils, "get_ram_detection_source", lambda: "linux_meminfo")
    with patch.object(orch, "auto_scale_pool"):
        config = orch.build_engine_config(
            {},
            enabled_services={"PiperTTS", "KokoroTTS", "MmsTTS", "SupertonicTTS"},
        )

    # One shared 4290MB budget for all four local engines.
    assert config["Piper"] == 3
    assert config["Kokoro"] == 3
    assert config["MMS"] == 2
    assert config["Supertonic"] == 2
    info_messages = [str(call.args[0]) for call in logger.info.call_args_list]
    assert any(
        "[RAM] source=linux_meminfo available_mb=8580" in message
        for message in info_messages
    )
    assert any("[RAM-CAP] KokoroTTS" in message for message in info_messages)


@pytest.mark.unit
def test_build_engine_config_disabled_engines_do_not_consume_budget(monkeypatch):
    orch = tts_orchestrator.TTSOrchestrator(MagicMock())
    monkeypatch.setattr(system_utils, "get_cpu_threads", lambda: 8)
    monkeypatch.setattr(system_utils, "get_max_workers", lambda: 16)
    monkeypatch.setattr(system_utils, "get_available_ram_mb", lambda: 3000)
    monkeypatch.setattr(system_utils, "get_ram_detection_source", lambda: "linux_meminfo")
    with patch.object(orch, "auto_scale_pool"):
        config = orch.build_engine_config(
            {},
            enabled_services={"PiperTTS"},
        )

    # 1500MB budget / 200MB per Piper process -> 7, not 1.
    assert config["Piper"] == 7
    assert config["Kokoro"] == 1
    assert config["MMS"] == 1
    assert config["Supertonic"] == 1


@pytest.mark.unit
def test_build_engine_config_minimum_exceeds_budget_warns(monkeypatch):
    orch = tts_orchestrator.TTSOrchestrator(MagicMock())
    logger = MagicMock()
    monkeypatch.setattr(tts_orchestrator, "logger", logger)
    monkeypatch.setattr(system_utils, "get_cpu_threads", lambda: 8)
    monkeypatch.setattr(system_utils, "get_max_workers", lambda: 16)
    monkeypatch.setattr(system_utils, "get_available_ram_mb", lambda: 3000)
    monkeypatch.setattr(system_utils, "get_ram_detection_source", lambda: "linux_meminfo")
    with patch.object(orch, "auto_scale_pool"):
        config = orch.build_engine_config(
            {},
            enabled_services={"PiperTTS", "KokoroTTS", "MmsTTS", "SupertonicTTS"},
        )

    assert config["Piper"] == 1
    assert config["Kokoro"] == 1
    assert config["MMS"] == 1
    assert config["Supertonic"] == 1
    warning_messages = [str(call.args[0]) for call in logger.warning.call_args_list]
    assert any("one-worker-per-enabled-engine minimum" in message for message in warning_messages)


@pytest.mark.unit
def test_build_engine_config_edge_is_always_capped(monkeypatch):
    orch = tts_orchestrator.TTSOrchestrator(MagicMock())
    logger = MagicMock()
    monkeypatch.setattr(tts_orchestrator, "logger", logger)
    monkeypatch.setattr(system_utils, "get_cpu_threads", lambda: 8)
    monkeypatch.setattr(system_utils, "get_max_workers", lambda: 16)
    monkeypatch.setattr(system_utils, "get_available_ram_mb", lambda: 10000)
    monkeypatch.setattr(system_utils, "get_ram_detection_source", lambda: "linux_meminfo")
    with patch.object(orch, "auto_scale_pool"):
        config = orch.build_engine_config(
            {"EdgeTTS": {"concurrency_workers": 99}},
            enabled_services=set(),
        )

    assert config["EdgeTTS"] == 3
    warning_messages = [str(call.args[0]) for call in logger.warning.call_args_list]
    assert any("EdgeTTS concurrency_workers (99)" in message for message in warning_messages)


@pytest.mark.unit
def test_build_engine_config_warns_when_ram_unknown(monkeypatch):
    orch = tts_orchestrator.TTSOrchestrator(MagicMock())
    logger = MagicMock()
    monkeypatch.setattr(tts_orchestrator, "logger", logger)
    monkeypatch.setattr(system_utils, "get_cpu_threads", lambda: 8)
    monkeypatch.setattr(system_utils, "get_max_workers", lambda: 8)
    monkeypatch.setattr(system_utils, "get_available_ram_mb", lambda: None)
    monkeypatch.setattr(system_utils, "get_ram_detection_source", lambda: "unknown")
    with patch.object(orch, "auto_scale_pool"):
        config = orch.build_engine_config(
            {},
            enabled_services={"PiperTTS", "KokoroTTS", "MmsTTS", "SupertonicTTS"},
        )

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


@pytest.mark.unit
def test_shared_budget_allocator_single_engine_uses_full_budget():
    allocation, meta = system_utils.allocate_local_engine_workers(
        cpu_caps={"Piper": 8},
        ram_per_process_mb={"Piper": 200},
        enabled_engines={"Piper"},
        available_ram_mb=3000,
    )
    assert allocation == {"Piper": 7}
    assert meta["budget_mb"] == 1500
    assert meta["over_budget"] is False


@pytest.mark.unit
def test_shared_budget_allocator_balances_two_engines():
    allocation, meta = system_utils.allocate_local_engine_workers(
        cpu_caps={"Piper": 8, "Kokoro": 6},
        ram_per_process_mb={"Piper": 200, "Kokoro": 500},
        enabled_engines={"Piper", "Kokoro"},
        available_ram_mb=6880,
    )
    assert allocation == {"Piper": 7, "Kokoro": 4}
    assert meta["estimated_mb"] == 3400


@pytest.mark.unit
def test_shared_budget_allocator_splits_four_engines():
    allocation, meta = system_utils.allocate_local_engine_workers(
        cpu_caps={"Piper": 8, "Kokoro": 8, "MMS": 8, "Supertonic": 8},
        ram_per_process_mb={"Piper": 200, "Kokoro": 500, "MMS": 500, "Supertonic": 500},
        enabled_engines={"Piper", "Kokoro", "MMS", "Supertonic"},
        available_ram_mb=6880,
    )
    assert allocation == {"Piper": 2, "Kokoro": 2, "MMS": 2, "Supertonic": 2}
    assert meta["estimated_mb"] == 3400


@pytest.mark.unit
def test_shared_budget_allocator_disabled_engine_costs_nothing():
    allocation, meta = system_utils.allocate_local_engine_workers(
        cpu_caps={"Piper": 8, "Kokoro": 8},
        ram_per_process_mb={"Piper": 200, "Kokoro": 500},
        enabled_engines={"Piper"},
        available_ram_mb=3000,
    )
    assert allocation == {"Piper": 7, "Kokoro": 1}
    assert meta["estimated_mb"] == 1400


@pytest.mark.unit
def test_shared_budget_allocator_preserves_manual_override():
    allocation, meta = system_utils.allocate_local_engine_workers(
        cpu_caps={"Piper": 8, "Kokoro": 8},
        ram_per_process_mb={"Piper": 200, "Kokoro": 500},
        enabled_engines={"Piper", "Kokoro"},
        available_ram_mb=6880,
        manual_workers={"Kokoro": 10},
    )
    assert allocation["Kokoro"] == 10
    assert allocation["Piper"] == 1
    assert meta["over_budget"] is True
    # The warning about the one-worker minimum must not be triggered by a
    # manual override; it is reserved for configurations where even one
    # worker per enabled engine cannot fit.
    assert meta["minimum_over_budget"] is False


@pytest.mark.unit
def test_shared_budget_allocator_unknown_ram_uses_cpu_caps():
    allocation, meta = system_utils.allocate_local_engine_workers(
        cpu_caps={"Piper": 8, "Kokoro": 6},
        ram_per_process_mb={"Piper": 200, "Kokoro": 500},
        enabled_engines={"Piper", "Kokoro"},
        available_ram_mb=None,
    )
    assert allocation == {"Piper": 8, "Kokoro": 6}
    assert meta["budget_mb"] is None
    assert meta["over_budget"] is False


@pytest.mark.unit
def test_shared_budget_allocator_keeps_minimum_when_over_budget():
    allocation, meta = system_utils.allocate_local_engine_workers(
        cpu_caps={"Piper": 8, "Kokoro": 8, "MMS": 8, "Supertonic": 8},
        ram_per_process_mb={"Piper": 200, "Kokoro": 500, "MMS": 500, "Supertonic": 500},
        enabled_engines={"Piper", "Kokoro", "MMS", "Supertonic"},
        available_ram_mb=3000,
    )
    assert allocation == {"Piper": 1, "Kokoro": 1, "MMS": 1, "Supertonic": 1}
    assert meta["minimum_over_budget"] is True
    assert meta["estimated_mb"] == 1700
