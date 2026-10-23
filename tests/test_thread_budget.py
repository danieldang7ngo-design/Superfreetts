"""Thread-budget tests (audit finding P1-5).

``sum(workers x threads)`` must stay within the machine's logical CPU count.
``get_cpu_threads()`` (cores - 1, capped at 8) is only a default *worker*
count, so using it as the budget allowed 8 workers x 8 threads = 64 compute
threads on an 8-thread laptop.
"""

from unittest.mock import MagicMock, patch

import pytest

from superfreetts_addon import batch_constants, system_utils, tts_orchestrator


@pytest.mark.unit
def test_eight_by_eight_exceeds_sixteen_cpus():
    budget = system_utils.compute_thread_budget({'Kokoro': 8}, {'Kokoro': 8}, cpu_count=16)

    assert budget['total_threads'] == 64
    assert budget['over_budget'] is True
    assert budget['per_pool']['Kokoro'] == {'workers': 8, 'threads': 8, 'threads_total': 64}


@pytest.mark.unit
def test_two_by_eight_fits_sixteen_cpus():
    budget = system_utils.compute_thread_budget({'Kokoro': 2}, {'Kokoro': 8}, cpu_count=16)

    assert budget['total_threads'] == 16
    assert budget['over_budget'] is False


@pytest.mark.unit
def test_edge_tts_is_not_part_of_the_cpu_budget():
    budget = system_utils.compute_thread_budget(
        {'EdgeTTS': 100, 'Piper': 1}, {'Piper': 1}, cpu_count=4
    )

    assert 'EdgeTTS' not in budget['per_pool']
    assert budget['total_threads'] == 1


@pytest.mark.unit
def test_invalid_values_degrade_to_one_thread():
    budget = system_utils.compute_thread_budget(
        {'Piper': 'nonsense', 'MMS': 0}, {'Piper': 'bad', 'MMS': -3}, cpu_count=4
    )

    assert budget['per_pool']['Piper']['workers'] == 1
    assert budget['per_pool']['Piper']['threads'] == 1
    assert budget['per_pool']['MMS']['workers'] == 1
    assert budget['per_pool']['MMS']['threads'] == 1


def _make_orchestrator():
    return tts_orchestrator.TTSOrchestrator(MagicMock())


@pytest.mark.unit
def test_build_engine_config_lowers_automatic_workers_to_fit_threads():
    """8x8 Kokoro + 8x8 Piper on 16 CPUs must be lowered automatically."""
    orch = _make_orchestrator()
    with patch.object(system_utils, 'get_cpu_threads', return_value=8), \
         patch.object(system_utils, 'get_max_workers', return_value=16), \
         patch.object(system_utils, 'get_total_cpu_count', return_value=16), \
         patch.object(system_utils, 'get_available_ram_mb', return_value=100_000), \
         patch.object(orch, 'auto_scale_pool'):
        engine_config = orch.build_engine_config(
            service_config_map={
                'KokoroTTS': {'num_threads': 8},
                'PiperTTS': {'num_threads': 8},
            },
            enabled_services={'KokoroTTS', 'PiperTTS'},
        )

    total = (
        engine_config['Kokoro'] * 8
        + engine_config['Piper'] * 8
    )
    assert total <= 16
    assert engine_config['Kokoro'] >= 1
    assert engine_config['Piper'] >= 1


@pytest.mark.unit
def test_build_engine_config_keeps_manual_override_but_warns():
    """Explicit concurrency_workers is preserved even when over budget."""
    orch = _make_orchestrator()
    with patch.object(system_utils, 'get_cpu_threads', return_value=8), \
         patch.object(system_utils, 'get_max_workers', return_value=16), \
         patch.object(system_utils, 'get_total_cpu_count', return_value=16), \
         patch.object(system_utils, 'get_available_ram_mb', return_value=100_000), \
         patch.object(orch, 'auto_scale_pool'), \
         patch.object(tts_orchestrator.logger, 'warning') as warn:
        engine_config = orch.build_engine_config(
            service_config_map={
                'KokoroTTS': {'concurrency_workers': 4, 'num_threads': 8},
            },
            enabled_services={'KokoroTTS'},
        )

    assert engine_config['Kokoro'] == 4
    messages = [str(call.args[0]) for call in warn.call_args_list]
    assert any('[THREAD-CAP]' in message for message in messages)


@pytest.mark.unit
def test_valid_thread_budget_is_left_alone():
    """2 workers x 8 threads on 16 CPUs is valid and must not be touched."""
    orch = _make_orchestrator()
    with patch.object(system_utils, 'get_cpu_threads', return_value=8), \
         patch.object(system_utils, 'get_max_workers', return_value=16), \
         patch.object(system_utils, 'get_total_cpu_count', return_value=16), \
         patch.object(system_utils, 'get_available_ram_mb', return_value=100_000), \
         patch.object(orch, 'auto_scale_pool'):
        engine_config = orch.build_engine_config(
            service_config_map={
                'KokoroTTS': {'num_threads': 8},
            },
            enabled_services={'KokoroTTS'},
        )

    # Kokoro's automatic worker cap is 2 (KOKORO_MAX_AUTO_WORKERS).
    assert engine_config['Kokoro'] == 2
    # Only enabled engines consume the budget (2 x 8 = 16 threads).
    assert engine_config['Kokoro'] * 8 <= 16
    assert engine_config['Piper'] == 1


@pytest.mark.unit
def test_default_num_threads_is_one_and_never_over_budget():
    """With default settings (num_threads=1) the budget check is a no-op."""
    orch = _make_orchestrator()
    with patch.object(system_utils, 'get_cpu_threads', return_value=8), \
         patch.object(system_utils, 'get_max_workers', return_value=8), \
         patch.object(system_utils, 'get_total_cpu_count', return_value=8), \
         patch.object(system_utils, 'get_available_ram_mb', return_value=100_000), \
         patch.object(orch, 'auto_scale_pool'):
        engine_config = orch.build_engine_config(
            service_config_map={},
            enabled_services={'PiperTTS', 'MmsTTS', 'SupertonicTTS'},
        )

    assert engine_config['EdgeTTS'] == batch_constants.EDGETTS_MAX_WORKERS
    assert engine_config['Piper'] + engine_config['MMS'] + engine_config['Supertonic'] <= 8


@pytest.mark.unit
def test_local_thread_counts_reads_service_configuration():
    orch = _make_orchestrator()
    counts = orch._local_thread_counts({
        'KokoroTTS': {'num_threads': 4},
        'PiperTTS': {'num_threads': '2'},
        'MmsTTS': {},
        'SupertonicTTS': {'num_threads': 0},
    })

    assert counts['Kokoro'] == 4
    assert counts['Piper'] == 2
    assert counts['MMS'] == 1
    assert counts['Supertonic'] == 1
