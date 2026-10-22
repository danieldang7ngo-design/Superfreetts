"""Lifecycle tests for the shared local-engine process pool."""

from unittest.mock import MagicMock

import pytest

from superfreetts_addon.services.service_mms import SherpaProcessPool


class FakeProcess:
    def __init__(self):
        self.stdin = MagicMock()
        self.stdout = MagicMock()
        self.stderr = MagicMock()
        self.is_healthy = True
        self.returncode = None
        self.terminate_calls = 0

    def poll(self):
        return self.returncode

    def terminate(self):
        self.terminate_calls += 1
        self.returncode = 0

    def wait(self, timeout=None):
        return self.returncode


@pytest.mark.unit
def test_stop_all_terminates_active_processes(monkeypatch):
    pool = SherpaProcessPool("test", max_processes=2)
    pool._cleanup_timer.cancel()
    proc = FakeProcess()
    monkeypatch.setattr(pool, "_start_new", lambda *args, **kwargs: proc)

    leased = pool.get_process("engine", "runner.py", debug_enabled=False)
    assert leased is proc
    assert proc in pool._active
    assert pool._total_spawned == 1

    pool.stop_all()

    assert proc.terminate_calls == 1
    assert proc.is_healthy is False
    assert pool._active == set()
    assert pool._pool == []
    assert pool._total_spawned == 0
    for pipe in (proc.stdin, proc.stdout, proc.stderr):
        pipe.close.assert_called_once()


@pytest.mark.unit
def test_release_moves_process_from_active_to_idle(monkeypatch):
    pool = SherpaProcessPool("test", max_processes=2)
    pool._cleanup_timer.cancel()
    proc = FakeProcess()
    monkeypatch.setattr(pool, "_start_new", lambda *args, **kwargs: proc)

    leased = pool.get_process("engine", "runner.py", debug_enabled=False)
    pool.release_process(leased, "engine", "runner.py")

    assert proc not in pool._active
    assert [entry[0] for entry in pool._pool] == [proc]
    assert pool._total_spawned == 1

    pool.stop_all()
    assert proc.terminate_calls == 1


@pytest.mark.unit
def test_pool_reused_after_stop_all_restarts_cleanup_timer(monkeypatch):
    pool = SherpaProcessPool("test", max_processes=2)
    pool._cleanup_timer.cancel()
    proc = FakeProcess()
    monkeypatch.setattr(pool, "_start_new", lambda *args, **kwargs: proc)

    pool.stop_all()
    assert pool._cleanup_enabled is False

    leased = pool.get_process("engine", "runner.py", debug_enabled=False)

    assert leased is proc
    assert pool._cleanup_enabled is True
    assert pool._cleanup_timer.is_alive()
    pool.release_process(leased, "engine", "runner.py")
    pool.stop_all()
