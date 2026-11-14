"""
runner_base.py — Shared IPC boilerplate for subprocess runner scripts.

Provides: setup_stdio(), log(), write_response().

Each runner script (kokoro_runner, piper_runner, sherpa_runner_v2,
supertonic_runner) imports from here instead of re-defining identical
boilerplate.  Only unique logic (model loading, TTS call) stays per-runner.
"""

import logging
import os
import sys
import threading
import time


logger = logging.getLogger(__name__)


# Runner processes are children of the Anki process that spawned them.  When
# Anki dies without running shutdown (crash, forced quit, a profile close that
# skips hooks) the local engines survive as orphans: they keep hundreds of MB
# of model memory resident and their pipes keep the pool slot busy until the OS
# eventually reaps them.
INITIAL_PPID = os.getppid()

# Two consecutive bad readings, 5 s apart.  One odd reading must never kill a
# healthy runner; 10 s is short enough that a leaked engine is not left behind
# for the rest of the session.
PARENT_WATCHDOG_INTERVAL_SECONDS = 5.0
PARENT_WATCHDOG_MISSED_CHECKS = 2
PARENT_WATCHDOG_DISABLE_ENV = 'SUPERFREETTS_DISABLE_PARENT_WATCHDOG'


def setup_stdio():
    """Force UTF-8 on stdin/stdout/stderr — pipes may not be safe by default."""
    if hasattr(sys.stdin, 'reconfigure'):
        try:
            sys.stdin.reconfigure(encoding='utf-8')
            sys.stdout.reconfigure(encoding='utf-8')
            sys.stderr.reconfigure(encoding='utf-8')
        except Exception:
            logger.debug("stdio reconfigure failed", exc_info=True)


def log(msg):
    """Write timestamped message to stderr (captured by Anki/parent process).
    Also appends to SUPERFREETTS_LOG_FILE if that env-var is set.
    """
    sys.stderr.write(f"[{time.strftime('%H:%M:%S')}] {msg}\n")
    sys.stderr.flush()
    log_path = os.environ.get('SUPERFREETTS_LOG_FILE')
    if log_path:
        try:
            with open(log_path, 'a', encoding='utf-8') as fh:
                fh.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")
        except Exception:
            logger.debug("could not append to %s", log_path, exc_info=True)


def write_response(response: str) -> bool:
    """Write a UTF-8 JSON line to stdout.buffer with BrokenPipeError guard.

    Returns True on success, False if the pipe is closed.
    """
    try:
        sys.stdout.buffer.write(response.encode('utf-8'))
        sys.stdout.buffer.flush()
        return True
    except (BrokenPipeError, OSError) as exc:
        log(f"stdout closed while writing response: {exc}")
        return False


def _read_parent_pid():
    try:
        return os.getppid()
    except Exception:
        return 0


def parent_lost(initial_ppid, current_ppid):
    """True when the runner's parent disappeared or was replaced."""
    if initial_ppid is None or initial_ppid <= 1:
        # Started by init or a container supervisor: there is no Anki parent to
        # watch, and treating pid 1 as "lost" would kill every runner at once.
        return False
    if os.name == 'nt':
        return current_ppid != initial_ppid
    # POSIX: a dead parent reparents the child to init (ppid 1) or to a
    # subreaper; both mean the Anki process that owned us is gone.
    return current_ppid <= 1 or current_ppid != initial_ppid


def _exit_orphan():
    """Close stdin and hard-exit the runner (called from the watchdog thread)."""
    log('parent process is gone; exiting to avoid an orphaned runner')
    try:
        if sys.stdin is not None:
            sys.stdin.close()
    except Exception:
        logger.debug("closing stdin failed during orphan exit", exc_info=True)
    try:
        sys.stdout.flush()
        sys.stderr.flush()
    except Exception:
        logger.debug("flushing stdio failed during orphan exit", exc_info=True)
    # os._exit: the main thread may be blocked in readline() or model
    # inference, and a thread cannot raise SystemExit in another thread.
    os._exit(0)


def start_parent_watchdog(initial_ppid=None, interval=None, missed_checks=None,
                          ppid_reader=None, exit_fn=None, stop_event=None):
    """Watch the parent process and exit the runner when it disappears.

    Returns the daemon thread, or None when the watchdog is disabled or there
    is no meaningful parent to watch.  Every dependency is injectable so tests
    can drive it without forking a real orphan.
    """
    if os.environ.get(PARENT_WATCHDOG_DISABLE_ENV, '').strip().lower() in (
        '1', 'true', 'yes', 'on'
    ):
        return None
    if initial_ppid is None:
        initial_ppid = INITIAL_PPID
    if initial_ppid <= 1:
        return None
    if interval is None:
        interval = PARENT_WATCHDOG_INTERVAL_SECONDS
    if missed_checks is None:
        missed_checks = PARENT_WATCHDOG_MISSED_CHECKS
    if ppid_reader is None:
        ppid_reader = _read_parent_pid
    if exit_fn is None:
        exit_fn = _exit_orphan

    def _watch():
        misses = 0
        while stop_event is None or not stop_event.is_set():
            if stop_event is not None:
                if stop_event.wait(interval):
                    return
            else:
                time.sleep(interval)
            try:
                current_ppid = ppid_reader()
            except Exception as exc:
                # A failing reader must not kill the watchdog thread.
                log(f'parent watchdog could not read the parent pid: {exc}')
                current_ppid = initial_ppid
            if parent_lost(initial_ppid, current_ppid):
                misses += 1
                if misses >= missed_checks:
                    exit_fn()
                    return
            else:
                misses = 0

    thread = threading.Thread(
        target=_watch, name='superfreetts-parent-watchdog', daemon=True
    )
    thread.start()
    return thread


if not hasattr(sys, '_pytest_mode'):
    # Imported by a runner script (never by Anki itself): guard from the start.
    start_parent_watchdog()

