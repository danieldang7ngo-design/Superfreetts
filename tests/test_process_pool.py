"""Resource-management regressions for the shared local-engine process pool.

Covers: stopping checked-out and idle processes without holding the pool lock,
deferred termination on a debug-flag mismatch, the module-level pool registry,
shrinking ``max_processes`` without waiting for the 180 s idle timer, parallel
(UI-thread-safe) shutdown of many processes and pools, and terminating a
process that already exited.
"""

import os
import time
from unittest.mock import MagicMock

import pytest

from superfreetts_addon.services import process_pool
from superfreetts_addon.services.service_mms import SherpaProcessPool


class FakeProcess:
    def __init__(self, pid=4242):
        self.stdin = MagicMock()
        self.stdout = MagicMock()
        self.stderr = MagicMock()
        self.is_healthy = True
        self.returncode = None
        self.terminate_calls = 0
        self.pid = pid
        self.debug_enabled = False
        self.owns_process_group = False

    def poll(self):
        return self.returncode

    def terminate(self):
        self.terminate_calls += 1
        self.returncode = 0

    def wait(self, timeout=None):
        return self.returncode


def _record_terminations(pool, monkeypatch):
    """Replace safe_terminate with a recorder that checks the lock state."""
    calls = []

    def safe_terminate(proc):
        calls.append((proc, pool._lock.locked()))
        process_pool.terminate_process(proc)

    monkeypatch.setattr(pool, "safe_terminate", safe_terminate)
    return calls


@pytest.mark.unit
def test_stop_all_terminates_idle_and_active_processes_outside_lock(monkeypatch):
    pool = SherpaProcessPool("test", max_processes=2)
    idle = FakeProcess(1)
    active = FakeProcess(2)
    procs = iter([idle, active])
    monkeypatch.setattr(pool, "_start_new", lambda *args, **kwargs: next(procs))

    leased_idle = pool.get_process("engine", "runner.py", debug_enabled=False)
    leased_active = pool.get_process("engine", "runner.py", debug_enabled=False)
    pool.release_process(leased_idle, "engine", "runner.py")
    assert leased_active in pool._active
    assert idle not in pool._active

    calls = _record_terminations(pool, monkeypatch)
    pool.stop_all()

    terminated = [proc for proc, _locked in calls]
    assert terminated == [idle, active] or terminated == [active, idle]
    # safe_terminate() blocks for seconds; it must never run under the lock.
    assert [locked for _proc, locked in calls] == [False, False]
    assert idle.terminate_calls == 1
    assert active.terminate_calls == 1
    assert idle.is_healthy is False
    assert active.is_healthy is False
    assert pool._active == set()
    assert pool._pool == []
    assert pool._total_spawned == 0


@pytest.mark.unit
def test_stop_all_cancels_idle_cleanup_timer(monkeypatch):
    pool = SherpaProcessPool("test", max_processes=1)
    proc = FakeProcess()
    monkeypatch.setattr(pool, "_start_new", lambda *args, **kwargs: proc)
    leased = pool.get_process("engine", "runner.py", debug_enabled=False)
    pool.release_process(leased, "engine", "runner.py")
    assert pool._cleanup_timer is not None

    pool.stop_all()

    assert pool._cleanup_timer is None
    assert pool._cleanup_enabled is False


@pytest.mark.unit
def test_debug_flag_mismatch_terminates_after_lock_release(monkeypatch):
    pool = SherpaProcessPool("test", max_processes=2)
    old = FakeProcess(1)
    new = FakeProcess(2)
    procs = iter([old, new])
    monkeypatch.setattr(pool, "_start_new", lambda *args, **kwargs: next(procs))

    leased = pool.get_process("engine", "runner.py", debug_enabled=False)
    pool.release_process(leased, "engine", "runner.py")

    calls = _record_terminations(pool, monkeypatch)
    replacement = pool.get_process("engine", "runner.py", debug_enabled=True)

    try:
        assert replacement is new
        assert [proc for proc, _locked in calls] == [old]
        assert [locked for _proc, locked in calls] == [False]
        assert old.terminate_calls == 1
        assert pool._total_spawned == 1
        assert [entry[0] for entry in pool._pool] == []
    finally:
        pool.stop_all()


@pytest.mark.unit
def test_pool_registers_itself_on_construction():
    pool = SherpaProcessPool("registered", max_processes=1)

    assert pool in process_pool.get_registered_pools()

    pool.stop_all()


@pytest.mark.unit
def test_stop_all_registered_pools_stops_every_pool():
    pool_a = SherpaProcessPool("registered-a", max_processes=1)
    pool_b = SherpaProcessPool("registered-b", max_processes=1)
    pool_a.stop_all = MagicMock()
    pool_b.stop_all = MagicMock()

    process_pool.stop_all_registered_pools()

    pool_a.stop_all.assert_called_once_with()
    pool_b.stop_all.assert_called_once_with()


@pytest.mark.unit
def test_register_pool_registers_atexit_hook_once(monkeypatch):
    registered = []
    monkeypatch.setattr(process_pool.atexit, "register", registered.append)
    monkeypatch.setattr(process_pool, "_atexit_registered", False)

    class DummyPool:
        def stop_all(self):
            pass

    dummy = DummyPool()
    process_pool.register_pool(dummy)
    process_pool.register_pool(dummy)
    process_pool.ensure_atexit_registration()

    assert registered == [process_pool.stop_all_registered_pools]


@pytest.mark.unit
def test_stop_all_registered_pools_survives_a_failing_pool(monkeypatch):
    good = SherpaProcessPool("good", max_processes=1)
    bad = SherpaProcessPool("bad", max_processes=1)
    good.stop_all = MagicMock()
    bad.stop_all = MagicMock(side_effect=RuntimeError("boom"))

    process_pool.stop_all_registered_pools()

    good.stop_all.assert_called_once_with()


@pytest.mark.unit
def test_shutdown_stops_pool_created_after_import():
    """shutdown() must use the registry, not a hardcoded list of four pools."""
    from superfreetts_addon import superfreetts as superfreetts_module

    late_pool = SherpaProcessPool("late", max_processes=1)
    late_pool.stop_all = MagicMock()
    stts = object.__new__(superfreetts_module.SuperFreeTTS)
    stts.executor = None
    stts.usage_tracker = None

    stts.shutdown()

    late_pool.stop_all.assert_called_once_with()


@pytest.mark.unit
def test_shrinking_max_processes_reaps_idle_surplus_immediately(monkeypatch):
    pool = SherpaProcessPool("shrink", max_processes=3)
    procs = [FakeProcess(pid) for pid in range(3)]
    remaining = iter(procs)
    monkeypatch.setattr(pool, "_start_new", lambda *args, **kwargs: next(remaining))

    leased = [pool.get_process("engine", "runner.py", debug_enabled=False) for _ in range(3)]
    for proc in leased:
        pool.release_process(proc, "engine", "runner.py")
    assert pool._total_spawned == 3
    assert len(pool._pool) == 3

    calls = _record_terminations(pool, monkeypatch)
    pool.update_max_processes(1)

    # Shrinking now terminates concurrently, so the order is not guaranteed.
    assert {proc for proc, _locked in calls} == {procs[0], procs[1]}
    assert [locked for _proc, locked in calls] == [False, False]
    assert [entry[0] for entry in pool._pool] == [procs[2]]
    assert pool._total_spawned == 1
    assert pool._max_processes == 1

    pool.stop_all()


@pytest.mark.unit
def test_increasing_max_processes_terminates_nothing(monkeypatch):
    pool = SherpaProcessPool("grow", max_processes=1)
    proc = FakeProcess()
    monkeypatch.setattr(pool, "_start_new", lambda *args, **kwargs: proc)
    leased = pool.get_process("engine", "runner.py", debug_enabled=False)
    pool.release_process(leased, "engine", "runner.py")

    calls = _record_terminations(pool, monkeypatch)
    pool.update_max_processes(4)

    assert calls == []
    assert pool._max_processes == 4
    assert len(pool._pool) == 1

    pool.stop_all()


@pytest.mark.unit
def test_terminate_process_handles_already_exited_process():
    proc = FakeProcess()
    proc.returncode = 0

    # Used to raise UnboundLocalError on group_signalled and then skip terminate.
    process_pool.terminate_process(proc)

    assert proc.is_healthy is False
    for pipe in (proc.stdin, proc.stdout, proc.stderr):
        pipe.close.assert_called_once()


@pytest.mark.skipif(os.name == "nt", reason="POSIX process-group path")
@pytest.mark.unit
def test_terminate_process_ignores_groups_for_exited_process(monkeypatch):
    proc = FakeProcess()
    proc.returncode = 0
    proc.owns_process_group = True
    monkeypatch.setattr(process_pool, "_signal_process_group", lambda *args: True)

    process_pool.terminate_process(proc)

    assert proc.is_healthy is False


class SlowProcess(FakeProcess):
    """Fake runner whose graceful exit takes ``delay`` seconds.

    Real ``terminate_process()`` waits up to 2 s + 1 s per runner, which is why
    shutdown has to terminate runners concurrently instead of one by one.
    """

    def __init__(self, pid=4242, delay=0.3):
        super().__init__(pid)
        self.delay = delay

    def terminate(self):
        time.sleep(self.delay)
        super().terminate()


def _lease(pool, monkeypatch, count, process_factory=FakeProcess):
    procs = [process_factory(pid) for pid in range(count)]
    remaining = iter(procs)
    monkeypatch.setattr(pool, "_start_new", lambda *args, **kwargs: next(remaining))
    leased = [pool.get_process("engine", "runner.py", debug_enabled=False) for _ in range(count)]
    return procs, leased


@pytest.mark.unit
def test_stop_all_terminates_four_processes_in_parallel(monkeypatch):
    """4 runners x 0.3 s must not cost 4 x 0.3 s on the UI thread."""
    pool = SherpaProcessPool("parallel-stop", max_processes=4)
    procs, _leased = _lease(pool, monkeypatch, 4, process_factory=SlowProcess)

    # Same recorder contract as _record_terminations(), but the real (slow)
    # terminate_process() runs so the elapsed time is meaningful.
    calls = []
    lock = pool._lock

    def record_and_terminate(proc):
        calls.append((proc, lock.locked()))
        process_pool.terminate_process(proc)

    monkeypatch.setattr(pool, "safe_terminate", record_and_terminate)

    started = time.monotonic()
    pool.stop_all()
    elapsed = time.monotonic() - started

    assert sorted(proc.terminate_calls for proc in procs) == [1, 1, 1, 1]
    assert [locked for _proc, locked in calls] == [False, False, False, False]
    assert elapsed < 0.5, f"stop_all() took {elapsed:.2f}s; termination is serial"
    assert pool._active == set()
    assert pool._pool == []


@pytest.mark.unit
def test_update_max_processes_terminates_four_processes_in_parallel(monkeypatch):
    """Lowering the worker count from the settings UI must not block serially.

    ``update_max_processes()`` runs on Anki's UI thread (the settings dialog);
    four idle runners that each take 0.3 s to stop used to cost 1.2 s of frozen
    UI.  They must now be terminated concurrently.
    """
    pool = SherpaProcessPool("shrink-parallel", max_processes=4)
    procs, leased = _lease(pool, monkeypatch, 4, process_factory=SlowProcess)
    for proc in leased:
        pool.release_process(proc, "engine", "runner.py")
    assert len(pool._pool) == 4

    calls = []
    lock = pool._lock

    def record_and_terminate(proc):
        calls.append((proc, lock.locked()))
        process_pool.terminate_process(proc)

    monkeypatch.setattr(pool, "safe_terminate", record_and_terminate)

    started = time.monotonic()
    pool.update_max_processes(0)
    elapsed = time.monotonic() - started

    assert {proc for proc, _locked in calls} == set(procs)
    assert [locked for _proc, locked in calls] == [False, False, False, False]
    assert sorted(proc.terminate_calls for proc in procs) == [1, 1, 1, 1]
    assert elapsed < 0.8, (
        f"update_max_processes(0) took {elapsed:.2f}s; termination is serial"
    )
    assert pool._max_processes == 0
    assert pool._total_spawned == 0
    assert pool._pool == []

    pool.stop_all()


@pytest.mark.unit
def test_stop_all_registered_pools_stops_pools_in_parallel(monkeypatch):
    """4 pools x 2 runners x 0.3 s must finish well under the 3 s budget."""
    pools = []
    pools_procs = []
    for index in range(4):
        pool = SherpaProcessPool(f"parallel-pool-{index}", max_processes=2)
        procs, _leased = _lease(pool, monkeypatch, 2, process_factory=SlowProcess)
        pools.append(pool)
        pools_procs.append(procs)

    started = time.monotonic()
    process_pool.stop_all_registered_pools()
    elapsed = time.monotonic() - started

    assert elapsed < 1.0, f"registry shutdown took {elapsed:.2f}s; pools are serial"
    assert elapsed < 3.0
    for procs in pools_procs:
        assert sorted(proc.terminate_calls for proc in procs) == [1, 1]
    for pool in pools:
        assert pool._active == set()
        assert pool._pool == []


@pytest.mark.unit
def test_atexit_handler_stops_every_registered_pool(monkeypatch):
    """The registered atexit hook stops all pools, including late ones."""
    registered = []
    monkeypatch.setattr(process_pool.atexit, "register", registered.append)
    monkeypatch.setattr(process_pool, "_atexit_registered", False)

    pools = [SherpaProcessPool(f"atexit-{index}", max_processes=1) for index in range(4)]
    for pool in pools:
        pool.stop_all = MagicMock()

    process_pool.ensure_atexit_registration()

    assert registered == [process_pool.stop_all_registered_pools]
    # Call the handler the interpreter would run at exit.
    registered[0]()
    for pool in pools:
        pool.stop_all.assert_called_once_with()


@pytest.mark.unit
def test_release_process_stops_surplus_runner_after_shrink(monkeypatch):
    """A runner returned after the cap shrank must not be parked over the cap."""
    pool = SherpaProcessPool("release-shrink", max_processes=2)
    procs, leased = _lease(pool, monkeypatch, 2)
    assert len(pool._active) == 2

    # Both runners are checked out, so nothing can be reaped yet.
    pool.update_max_processes(1)
    assert pool._total_spawned == 2

    calls = _record_terminations(pool, monkeypatch)
    pool.release_process(leased[0], "engine", "runner.py")

    assert [proc for proc, _locked in calls] == [procs[0]]
    assert [locked for _proc, locked in calls] == [False]
    assert pool._total_spawned == 1
    assert pool._pool == []

    pool.release_process(leased[1], "engine", "runner.py")
    assert [entry[0] for entry in pool._pool] == [procs[1]]
    assert pool._total_spawned == 1

    pool.stop_all()
