"""Lifecycle tests for the shared local-engine process pool."""

import os
import signal
from unittest.mock import MagicMock

import pytest

from superfreetts_addon.services import process_pool
from superfreetts_addon.services.service_mms import SherpaProcessPool


class FakeProcess:
    def __init__(self):
        self.stdin = MagicMock()
        self.stdout = MagicMock()
        self.stderr = MagicMock()
        self.is_healthy = True
        self.returncode = None
        self.terminate_calls = 0
        self.pid = 4242

    def poll(self):
        return self.returncode

    def terminate(self):
        self.terminate_calls += 1
        self.returncode = 0

    def wait(self, timeout=None):
        return self.returncode


@pytest.mark.skipif(os.name == "nt", reason="POSIX process groups only")
@pytest.mark.unit
def test_terminate_process_signals_whole_group(monkeypatch):
    proc = FakeProcess()
    proc.owns_process_group = True
    calls = []
    monkeypatch.setattr(process_pool.os, "killpg", lambda pid, sig: calls.append((pid, sig)))

    process_pool.terminate_process(proc)

    assert calls == [(proc.pid, signal.SIGTERM)]
    # The group signal replaces proc.terminate(); both must not run.
    assert proc.terminate_calls == 0
    assert proc.is_healthy is False
    proc.stdin.close.assert_called_once()


@pytest.mark.unit
def test_terminate_process_falls_back_to_terminate_without_group():
    proc = FakeProcess()
    proc.owns_process_group = False

    process_pool.terminate_process(proc)

    assert proc.terminate_calls == 1
    assert proc.is_healthy is False


@pytest.mark.unit
def test_stop_all_terminates_active_processes(monkeypatch):
    pool = SherpaProcessPool("test", max_processes=2)
    # The cleanup timer is lazy: an empty pool must not keep a daemon thread.
    assert pool._cleanup_timer is None
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
    proc = FakeProcess()
    monkeypatch.setattr(pool, "_start_new", lambda *args, **kwargs: proc)

    leased = pool.get_process("engine", "runner.py", debug_enabled=False)
    # Only an idle process needs periodic cleanup, so checkout leaves it dormant.
    assert pool._cleanup_timer is None
    pool.release_process(leased, "engine", "runner.py")

    assert proc not in pool._active
    assert [entry[0] for entry in pool._pool] == [proc]
    assert pool._total_spawned == 1
    assert pool._cleanup_timer is not None
    assert pool._cleanup_timer.is_alive()

    pool.stop_all()
    assert proc.terminate_calls == 1
    assert pool._cleanup_timer is None


@pytest.mark.unit
def test_pool_reused_after_stop_all_restarts_cleanup_timer(monkeypatch):
    pool = SherpaProcessPool("test", max_processes=2)
    assert pool._cleanup_timer is None
    proc = FakeProcess()
    monkeypatch.setattr(pool, "_start_new", lambda *args, **kwargs: proc)

    pool.stop_all()
    assert pool._cleanup_enabled is False
    assert pool._cleanup_timer is None

    leased = pool.get_process("engine", "runner.py", debug_enabled=False)

    assert leased is proc
    assert pool._cleanup_enabled is True
    # A checked-out process is never idle, so the timer still waits for release.
    assert pool._cleanup_timer is None
    pool.release_process(leased, "engine", "runner.py")
    assert pool._cleanup_timer is not None
    assert pool._cleanup_timer.is_alive()
    pool.stop_all()


class FakeWindowsProcess(FakeProcess):
    pass


@pytest.mark.unit
def test_terminate_process_tree_windows_graceful_first(monkeypatch):
    proc = FakeProcess()
    monkeypatch.setattr(process_pool.os, "name", "nt", raising=False)
    calls = []

    def fake_run(cmd, **kwargs):
        calls.append(list(cmd))
        result = MagicMock()
        result.returncode = 0
        return result

    monkeypatch.setattr(process_pool.subprocess, "run", fake_run)
    # proc.wait returns None first? Make wait return immediately
    proc.wait = lambda timeout=None: None
    proc.poll = lambda: None

    process_pool.terminate_process(proc)

    assert calls and calls[0] == ["taskkill", "/PID", str(proc.pid), "/T"]
    assert "/F" not in calls[0]
    assert proc.is_healthy is False
