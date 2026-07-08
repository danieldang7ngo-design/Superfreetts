import time

import pytest

from superfreetts_addon import batch_executor


def test_get_executor_normalizes_service_names_to_pool_names():
    executor = batch_executor.MultiEngineExecutor(engine_config={
        'Piper': 1,
        'Kokoro': 1,
        'EdgeTTS': 1,
        'MMS': 1,
        'Supertonic': 1,
        'default': 1,
    })

    assert executor.get_executor('PiperTTS')._max_workers == 1
    assert executor.get_executor('KokoroTTS')._max_workers == 1
    assert executor.get_executor('EdgeTTS')._max_workers == 1
    assert executor.get_executor('MmsTTS')._max_workers == 1
    assert executor.get_executor('SupertonicTTS')._max_workers == 1

    assert executor.get_executor('PiperTTS') is executor.executors['Piper']
    assert executor.get_executor('KokoroTTS') is executor.executors['Kokoro']
    assert executor.get_executor('EdgeTTS') is executor.executors['EdgeTTS']
    assert executor.get_executor('MmsTTS') is executor.executors['MMS']
    assert executor.get_executor('SupertonicTTS') is executor.executors['Supertonic']


def test_bounded_executor_submit_supports_timeout_when_queue_is_full():
    executor = batch_executor.BoundedThreadPoolExecutor(max_workers=1, max_waiting_tasks=0)

    def slow_work():
        time.sleep(0.2)

    first = executor.submit(slow_work)
    with pytest.raises(TimeoutError):
        executor.submit(lambda: None, timeout=0.05)

    first.result(timeout=1.0)
