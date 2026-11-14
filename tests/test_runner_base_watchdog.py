"""Parent-process watchdog for the local runner scripts.

Runner processes are children of Anki.  When Anki disappears without running
profile shutdown they must exit instead of lingering as orphaned model holders.
"""

import threading
import time

import pytest

from superfreetts_addon.services import runner_base


@pytest.mark.unit
def test_parent_lost_detects_reparenting_on_posix():
    assert runner_base.parent_lost(100, 100) is False
    assert runner_base.parent_lost(100, 1) is True
    assert runner_base.parent_lost(100, 1) is True
    assert runner_base.parent_lost(100, 200) is True


@pytest.mark.unit
def test_parent_lost_ignores_unreliable_parent_pid():
    # Started by init / a container supervisor: nothing to watch.
    assert runner_base.parent_lost(1, 999) is False
    assert runner_base.parent_lost(None, 999) is False


@pytest.mark.unit
def test_parent_lost_uses_pid_identity_on_windows(monkeypatch):
    monkeypatch.setattr(runner_base.os, "name", "nt", raising=False)

    assert runner_base.parent_lost(100, 100) is False
    assert runner_base.parent_lost(100, 200) is True


@pytest.mark.unit
def test_watchdog_exits_after_consecutive_misses():
    readings = iter([100, 999, 100, 999, 999])
    calls = []
    stop = threading.Event()

    thread = runner_base.start_parent_watchdog(
        initial_ppid=100,
        interval=0.01,
        missed_checks=2,
        ppid_reader=lambda: next(readings),
        exit_fn=lambda: calls.append(1),
        stop_event=stop,
    )
    assert thread is not None
    thread.join(2.0)
    stop.set()
    thread.join(1.0)

    # A single miss is ignored; two in a row (after a recovery) trip it.
    assert calls == [1]
    assert not thread.is_alive()


@pytest.mark.unit
def test_watchdog_ignores_a_transient_miss():
    readings = iter([999, 100, 100, 100, 100, 100, 100, 100])
    calls = []
    stop = threading.Event()

    thread = runner_base.start_parent_watchdog(
        initial_ppid=100,
        interval=0.005,
        missed_checks=2,
        ppid_reader=lambda: next(readings),
        exit_fn=lambda: calls.append(1),
        stop_event=stop,
    )
    assert thread is not None
    time.sleep(0.08)
    stop.set()
    thread.join(1.0)

    assert calls == []
    assert not thread.is_alive()


@pytest.mark.unit
def test_watchdog_disabled_by_environment(monkeypatch):
    monkeypatch.setenv(runner_base.PARENT_WATCHDOG_DISABLE_ENV, "1")

    assert runner_base.start_parent_watchdog(initial_ppid=100) is None


@pytest.mark.unit
def test_watchdog_not_started_without_a_real_parent():
    assert runner_base.start_parent_watchdog(initial_ppid=1) is None
    assert runner_base.start_parent_watchdog(initial_ppid=0) is None


@pytest.mark.unit
def test_watchdog_is_a_daemon_thread():
    stop = threading.Event()
    thread = runner_base.start_parent_watchdog(
        initial_ppid=100,
        interval=0.01,
        ppid_reader=lambda: 100,
        exit_fn=lambda: None,
        stop_event=stop,
    )
    assert thread is not None
    try:
        assert thread.daemon is True
        assert thread.name == "superfreetts-parent-watchdog"
    finally:
        stop.set()
        thread.join(1.0)


@pytest.mark.unit
def test_runner_import_does_not_start_watchdog_under_pytest():
    # conftest sets sys._pytest_mode before importing modules; the auto-start
    # at the bottom of runner_base must therefore be skipped here.
    assert hasattr(runner_base.sys, "_pytest_mode")
    assert runner_base.INITIAL_PPID > 0
