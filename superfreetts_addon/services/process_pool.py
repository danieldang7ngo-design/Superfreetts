"""Process pool and IPC deadline helpers for the local TTS engines.

The local engines (MMS/Sherpa, Kokoro, Supertonic, Piper) talk to a long-lived
runner process over stdin/stdout pipes.  A runner that wedges - crashed model,
swapping machine, deadlocked ONNX runtime - used to block the caller forever
inside ``stdout.readline()``.  That permanently held a pool permit and a worker
thread, and the global batch stall detector never noticed because the other
futures kept finishing.  The pool drained until Anki had to be restarted.

This module bounds both halves of the problem:

* ``DynamicSemaphore.acquire(timeout=...)`` gives up with ``EngineBusyError``
  instead of waiting forever for a permit.
* ``read_response()`` reads the JSON reply through a dedicated reader thread
  and a ``queue.Queue`` timeout.  On timeout it terminates the runner, closes
  its pipes and raises ``IpcTimeoutError`` so the calling service can retry
  once with a brand-new process.

Deadlines live in ``batch_constants`` so they are tunable in one place.
"""

import atexit
import logging
import os
import queue
import signal
import subprocess
import threading
import time
import weakref

from .. import batch_constants

logger = logging.getLogger(__name__)

# Bounded wait for stopping processes.  ``terminate_process`` gives a runner
# 2 s to exit gracefully and 1 s more after the kill, so stopping four pools
# with two runners each sequentially blocked Anki's UI thread (``shutdown()``
# walks the registry, and it runs on the UI thread during profile close) for
# ~24 s.  Termination now runs one daemon thread per process and the caller
# waits at most this long in total; anything still running finishes in the
# background instead of freezing the UI.
SHUTDOWN_JOIN_TIMEOUT_SECONDS = 2.5


def _call_quietly(label, func, *args):
    """Call ``func(*args)`` from a worker thread, logging instead of raising."""
    try:
        func(*args)
    except Exception as e:
        logger.warning("%s failed: %s", label, e)


def terminate_processes_parallel(processes, terminate=None, timeout=None):
    """Terminate ``processes`` concurrently, waiting at most ``timeout`` total.

    ``terminate`` defaults to :func:`terminate_process`; pools pass their
    ``safe_terminate`` so a monkeypatched/overridden version keeps working.
    Every process gets its own daemon thread, so a wedged runner cannot hold
    the remaining ones (or the caller) hostage.
    """
    pending = [proc for proc in processes if proc is not None]
    if not pending:
        return
    if timeout is None:
        timeout = SHUTDOWN_JOIN_TIMEOUT_SECONDS
    terminate = terminate or terminate_process
    threads = []
    for index, proc in enumerate(pending):
        thread = threading.Thread(
            target=_call_quietly,
            args=("terminate process %r" % (proc,), terminate, proc),
            name="pool-stop-%d" % index,
            daemon=True,
        )
        thread.start()
        threads.append(thread)
    deadline = time.monotonic() + max(0.0, float(timeout))
    for thread in threads:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            logger.warning(
                "pool shutdown: %d process(es) still stopping after %.1fs; "
                "leaving them to the daemon threads",
                len(pending), timeout,
            )
            return
        thread.join(remaining)


class EngineBusyError(RuntimeError):
    """No runner process became available before the acquire deadline."""


class IpcTimeoutError(RuntimeError):
    """A runner process accepted a request but never answered it."""


class DynamicSemaphore:
    """Semaphore with a dynamic maximum and a bounded wait.

    The maximum can be changed at runtime without leaking permits: ``set_max``
    notifies every waiter so a raised limit takes effect immediately.
    """

    def __init__(self, value=1):
        self._max = value
        self._count = 0
        self._cond = threading.Condition()

    def acquire(self, timeout=None):
        """Acquire a permit.

        Returns True when a permit was taken, False when ``timeout`` (seconds)
        elapsed first.  ``timeout=None`` waits forever (legacy behaviour).
        """
        deadline = None if timeout is None else time.monotonic() + timeout
        with self._cond:
            while self._count >= self._max:
                if deadline is None:
                    self._cond.wait()
                    continue
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    return False
                self._cond.wait(remaining)
            self._count += 1
            return True

    def release(self):
        with self._cond:
            if self._count > 0:
                self._count -= 1
            self._cond.notify()

    def set_max(self, new_max):
        with self._cond:
            self._max = new_max
            self._cond.notify_all()

    @property
    def max_value(self):
        with self._cond:
            return self._max

    @property
    def in_use(self):
        with self._cond:
            return self._count


def _terminate_process_tree_windows(proc, force=False):
    """Best-effort process-tree kill on Windows.

    ``taskkill`` without ``/F`` asks the process tree to exit gracefully first;
    ``/F`` is only used as a fallback when the graceful request does not
    terminate the process.  ``CREATE_NEW_PROCESS_GROUP`` is not required for
    ``taskkill /T`` to walk the child tree.
    """
    if os.name != 'nt':
        return False
    pid = getattr(proc, 'pid', None)
    if not pid:
        return False
    cmd = ['taskkill', '/PID', str(pid), '/T']
    if force:
        cmd.append('/F')
    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=5.0,
        )
        return result.returncode == 0
    except Exception:
        return False


def _signal_process_group(proc, sig):
    """Signal the runner's process group on POSIX.

    Local runners are started with ``start_new_session=True`` so they own a
    process group.  Killing the whole group is what reaps grand-children such
    as the stock ``piper`` binary when the Python runner is wedged.
    """
    if os.name == 'nt' or not getattr(proc, 'owns_process_group', False):
        return False
    pid = getattr(proc, 'pid', None)
    if not pid:
        return False
    try:
        os.killpg(pid, sig)
        return True
    except ProcessLookupError:
        return True
    except OSError:
        return False


def terminate_process(proc):
    """Terminate a runner and its process group, then close its pipes."""
    if proc is None:
        return
    try:
        # Initialise before the branch: when the process already exited,
        # ``proc.poll() is None`` is False, both assignments below are skipped
        # and the old code raised UnboundLocalError on ``group_signalled``.
        group_signalled = False
        if proc.poll() is None:
            if os.name == 'nt':
                group_signalled = _terminate_process_tree_windows(proc)
                if group_signalled:
                    try:
                        proc.wait(timeout=2.0)
                    except subprocess.TimeoutExpired:
                        _terminate_process_tree_windows(proc, force=True)
                        try:
                            proc.wait(timeout=1.0)
                        except Exception:
                            logger.debug(
                                "terminate_process: pid %s still alive after forced taskkill",
                                getattr(proc, "pid", "?"), exc_info=True,
                            )
                else:
                    try:
                        proc.terminate()
                        proc.wait(timeout=2.0)
                    except subprocess.TimeoutExpired:
                        if not _terminate_process_tree_windows(proc, force=True):
                            try:
                                proc.kill()
                            except Exception:
                                logger.debug(
                                    "terminate_process: kill failed for pid %s",
                                    getattr(proc, "pid", "?"), exc_info=True,
                                )
                        try:
                            proc.wait(timeout=1.0)
                        except Exception:
                            logger.debug(
                                "terminate_process: pid %s survived the kill wait",
                                getattr(proc, "pid", "?"), exc_info=True,
                            )
            else:
                group_signalled = _signal_process_group(proc, signal.SIGTERM)
            if not group_signalled and os.name != 'nt':
                proc.terminate()
            if os.name != 'nt':
                try:
                    proc.wait(timeout=2.0)
                except subprocess.TimeoutExpired:
                    if not _signal_process_group(proc, signal.SIGKILL):
                        proc.kill()
                    try:
                        proc.wait(timeout=1.0)
                    except Exception:
                        logger.debug(
                            "terminate_process: pid %s survived the SIGKILL wait",
                            getattr(proc, "pid", "?"), exc_info=True,
                        )
    except Exception:
        logger.debug("terminate_process: unexpected error while stopping %r", proc, exc_info=True)
    finally:
        try:
            proc.is_healthy = False
        except Exception:
            logger.debug("terminate_process: could not mark %r unhealthy", proc, exc_info=True)
        for name, pipe in (("stdin", getattr(proc, "stdin", None)),
                           ("stdout", getattr(proc, "stdout", None)),
                           ("stderr", getattr(proc, "stderr", None))):
            if pipe is not None:
                try:
                    pipe.close()
                except Exception:
                    logger.debug(
                        "terminate_process: closing the %s pipe of %r failed",
                        name, proc, exc_info=True,
                    )


def start_stdout_reader(proc, engine="engine"):
    """Start (once) a thread that pumps ``proc.stdout`` lines into a queue.

    Reading in a helper thread is what makes the deadline possible: the caller
    waits on ``queue.Queue.get(timeout=...)`` and can walk away, then kill the
    runner, instead of being stuck inside a blocking ``readline()``.
    """
    existing = getattr(proc, "ipc_stdout_queue", None)
    if existing is not None:
        return existing

    line_queue = queue.Queue()
    proc.ipc_stdout_queue = line_queue
    proc.ipc_engine = engine
    if getattr(proc, "ipc_requests", None) is None:
        proc.ipc_requests = 0
    stdout = getattr(proc, "stdout", None)

    def _pump():
        try:
            while stdout is not None:
                line = stdout.readline()
                if not line:
                    break
                if isinstance(line, str):
                    line = line.encode("utf-8")
                elif not isinstance(line, (bytes, bytearray)):
                    # Not a real pipe (e.g. a test double): stop instead of
                    # spinning forever on truthy mock objects.
                    break
                line_queue.put(bytes(line))
        except Exception:
            logger.debug("stdout reader for engine=%s stopped", engine, exc_info=True)
        finally:
            # EOF marker: read_response turns this into b"" (broken pipe) and
            # never waits for a response on an already-closed stream.
            try:
                proc.ipc_stdout_eof = True
            except Exception:
                logger.debug(
                    "stdout reader: could not flag EOF for engine=%s", engine, exc_info=True,
                )
            line_queue.put(None)

    thread = threading.Thread(
        target=_pump,
        name="ipc-reader-%s-%s" % (engine, getattr(proc, "pid", "?")),
        daemon=True,
    )
    proc.ipc_reader = thread
    thread.start()
    return line_queue


def request_timeout(proc, chunk=False):
    """Deadline for one request, applying a longer first-request allowance.

    A freshly spawned runner has to load its model before answering (Kokoro and
    Supertonic need roughly 10 s), so the first request on a process gets the
    cold-start deadline.  Later requests on the same warm process use the
    single/chunk deadline.
    """
    first_request = getattr(proc, "ipc_requests", 0) == 0
    try:
        proc.ipc_requests = getattr(proc, "ipc_requests", 0) + 1
    except Exception:
        logger.debug("request_timeout: could not bump the request counter", exc_info=True)
    if first_request:
        return float(batch_constants.IPC_COLD_START_TIMEOUT_SECONDS)
    if chunk:
        return float(batch_constants.IPC_BATCH_REQUEST_TIMEOUT_SECONDS)
    return float(batch_constants.IPC_SINGLE_REQUEST_TIMEOUT_SECONDS)


def read_response(proc, engine="engine", chunk=False, timeout=None):
    """Read one JSON response line, or kill the runner and raise.

    Returns the raw bytes exactly like ``stdout.readline()``; b"" means the
    stream closed (the caller raises BrokenPipeError, which is retried).
    """
    line_queue = getattr(proc, "ipc_stdout_queue", None)
    if line_queue is None:
        line_queue = start_stdout_reader(proc, engine)
    if getattr(proc, "ipc_stdout_eof", False) and line_queue.empty():
        # The stream is already closed (runner died between requests).  Report
        # EOF immediately instead of burning the whole deadline.
        return b""
    if timeout is None:
        timeout = request_timeout(proc, chunk=chunk)
    try:
        line = line_queue.get(timeout=timeout)
    except queue.Empty:
        logger.warning(
            "[IPC] timeout engine=%s waited=%.1fs action=kill+retry",
            engine, timeout,
        )
        terminate_process(proc)
        raise IpcTimeoutError(
            "%s runner did not answer within %.1fs" % (engine, timeout)
        )
    if line is None:
        return b""
    return line


# ---------------------------------------------------------------------------
# Pool registry
#
# Service modules create their pools at import time, and a reloaded service
# creates a new one.  Shutdown used to know only the four built-in pools, so
# every later pool leaked its runner processes.  Pools register themselves and
# shutdown stops the whole registry; atexit is the last-resort path for the
# case where profile_will_close never fires (crash, forced quit).
# ---------------------------------------------------------------------------

_registered_pools = weakref.WeakSet()
_registry_lock = threading.Lock()
_atexit_registered = False


def ensure_atexit_registration():
    """Register the atexit hook exactly once (idempotent)."""
    global _atexit_registered
    with _registry_lock:
        if _atexit_registered:
            return
        atexit.register(stop_all_registered_pools)
        _atexit_registered = True


def register_pool(pool):
    """Track ``pool`` so shutdown stops it even if it is created later."""
    with _registry_lock:
        _registered_pools.add(pool)
    ensure_atexit_registration()


def get_registered_pools():
    """Snapshot of the live pools (weak references, so GC'd pools vanish)."""
    with _registry_lock:
        return list(_registered_pools)


def stop_all_registered_pools():
    """Stop every live pool concurrently.  Safe to call repeatedly and atexit.

    ``shutdown()`` calls this on Anki's UI thread during profile close.  Pools
    used to be stopped one after another, and each pool waited on its runners
    in sequence, so four pools x two runners could freeze the UI for ~24 s.
    Every pool now runs on its own daemon thread and the caller waits at most
    ``SHUTDOWN_JOIN_TIMEOUT_SECONDS`` in total.
    """
    pools = get_registered_pools()
    if not pools:
        return
    threads = []
    for index, pool in enumerate(pools):
        thread = threading.Thread(
            target=_call_quietly,
            args=("stop process pool %s" % (getattr(pool, 'name', '?'),), pool.stop_all),
            name="pool-registry-stop-%d" % index,
            daemon=True,
        )
        thread.start()
        threads.append(thread)
    deadline = time.monotonic() + SHUTDOWN_JOIN_TIMEOUT_SECONDS
    for thread in threads:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            logger.warning(
                "pool shutdown: %d pool(s) still stopping after %.1fs; "
                "leaving them to the daemon threads",
                len(pools), SHUTDOWN_JOIN_TIMEOUT_SECONDS,
            )
            return
        thread.join(remaining)


class SherpaProcessPool:
    """Pool of long-lived runner processes shared by the local engines."""

    def __init__(self, name="Shared", max_processes=4):
        self.name = name
        self._max_processes = max_processes
        self._pool = []  # (process, executable, script, last_used_time)
        self._active = set()  # Processes currently checked out by a worker
        self._lock = threading.Lock()
        self._semaphore = DynamicSemaphore(max_processes)
        self._cleanup_timer = None
        self._cleanup_enabled = True
        self._max_idle_age = 180  # 180s idle timeout as mandated
        self._total_spawned = 0  # Track total processes (active + idle)
        # The timer is armed lazily by release_process(): an empty pool needs
        # no periodic wake-up.  Four service imports used to create/destroy
        # 960 daemon threads per hour just to inspect empty lists.
        register_pool(self)

    def _start_cleanup_timer(self):
        if self._cleanup_timer:
            self._cleanup_timer.cancel()
        self._cleanup_enabled = True
        self._cleanup_timer = threading.Timer(15.0, self._cleanup_idle)
        self._cleanup_timer.daemon = True
        self._cleanup_timer.start()

    def _cleanup_idle(self):
        with self._lock:
            now = time.time()
            alive_pool = []
            for proc, exe, script, last_time in self._pool:
                # If process died, hit idle timeout, or is unhealthy, terminate it
                is_unhealthy = not getattr(proc, 'is_healthy', True)
                if proc.poll() is not None or (now - last_time > self._max_idle_age) or is_unhealthy:
                    logger.info(
                        "SherpaPool[%s]: Cleaning up process %s (Reason: %s)",
                        self.name, os.path.basename(script),
                        'Health' if is_unhealthy else 'Timeout/Dead',
                    )
                    # Offload termination to avoid blocking the lock
                    threading.Thread(target=self.safe_terminate, args=(proc,), daemon=True).start()
                    self._total_spawned = max(0, self._total_spawned - 1)
                else:
                    alive_pool.append((proc, exe, script, last_time))
            self._pool = alive_pool
            if self._cleanup_enabled and self._pool:
                self._start_cleanup_timer()
            else:
                # No idle processes left: end the timer chain instead of
                # keeping a daemon thread alive forever.
                self._cleanup_timer = None

    def safe_terminate(self, proc):
        """Enforce safe termination sequence and pipe closure."""
        terminate_process(proc)

    def get_process(self, executable_path, script_path, debug_enabled=False, timeout=None):
        """Check out a runner process.

        Waits at most ``timeout`` seconds (default ``IPC_ACQUIRE_TIMEOUT_SECONDS``)
        for a permit and raises ``EngineBusyError`` instead of hanging forever.
        """
        if timeout is None:
            timeout = float(batch_constants.IPC_ACQUIRE_TIMEOUT_SECONDS)
        wait_started = time.monotonic()
        acquired = self._semaphore.acquire(timeout=timeout)
        waited = time.monotonic() - wait_started
        if not acquired:
            logger.warning(
                "[IPC] pool busy pool=%s waited=%.1fs action=fail",
                self.name, waited,
            )
            raise EngineBusyError(
                "%s engine busy: all runner processes are still in use "
                "after %.1fs" % (self.name, waited)
            )
        if waited >= 1.0:
            logger.info("[IPC] pool=%s waited=%.2fs acquired=True", self.name, waited)

        # stop_all() disables the idle timer during profile close.  A later
        # checkout means the pool is being reused, so allow release_process()
        # to arm the cleanup timer again.
        self._cleanup_enabled = True

        stale_processes = []
        with self._lock:
            logger.info(f"SherpaPool[{self.name}]: get_process (debug_enabled={debug_enabled})")
            # 1. Try to find an idle process for THIS script with SAME debug setting
            for i, (proc, exe, script, last_time) in enumerate(self._pool):
                if proc.poll() is None and exe == executable_path and script == script_path:
                    # Check if debug setting matches (we need to store it in the pool)
                    current_debug = getattr(proc, 'debug_enabled', False)
                    if current_debug == debug_enabled:
                        logger.info(f"SherpaPool[{self.name}]: Reusing idle process {os.path.basename(script)} (debug={current_debug})")
                        p, e, s, _ = self._pool.pop(i)
                        self._active.add(p)
                        return p
                    else:
                        logger.info(f"SherpaPool[{self.name}]: Terminating idle process {os.path.basename(script)} due to debug mismatch ({current_debug} != {debug_enabled})")
                        # Defer termination until the lock is released: waiting
                        # on a wedged runner inside the lock blocks every other
                        # worker of this pool.
                        self._pool.pop(i)
                        stale_processes.append(proc)
                        self._total_spawned = max(0, self._total_spawned - 1)
                        break  # Start fresh

            # 2. If no matching idle process, but we have OTHER idle processes and we're at capacity
            # we should kill the oldest idle one to make room for a NEW type (Script)
            if self._total_spawned >= self._max_processes and self._pool:
                # Kill oldest (first in list)
                p, e, s, _ = self._pool.pop(0)
                logger.info(f"SherpaPool[{self.name}]: Capacity reached. Terminating oldest idle {os.path.basename(s)} for new {os.path.basename(script_path)}")
                stale_processes.append(p)
                self._total_spawned = max(0, self._total_spawned - 1)

        # Terminate after the pool lock is released; safe_terminate() may wait
        # seconds for the runner (and taskkill) to finish.
        for stale in stale_processes:
            self.safe_terminate(stale)

        # 3. Start new process
        try:
            new_proc = self._start_new(executable_path, script_path, debug_enabled)
            new_proc.debug_enabled = debug_enabled
            with self._lock:
                self._total_spawned += 1
                self._active.add(new_proc)
            return new_proc
        except Exception as e:
            self._semaphore.release()
            logger.error(f"SherpaPool[{self.name}]: Failed to start process {os.path.basename(script_path)}: {e}")
            raise e

    def release_process(self, proc, executable_path, script_path):
        if proc is None:
            self._semaphore.release()
            return

        surplus = None
        with self._lock:
            self._active.discard(proc)
            is_healthy = getattr(proc, 'is_healthy', True)
            if proc.poll() is None and is_healthy:
                if len(self._active) + len(self._pool) < self._max_processes:
                    self._pool.append((proc, executable_path, script_path, time.time()))
                    if self._cleanup_enabled and (
                        self._cleanup_timer is None or not self._cleanup_timer.is_alive()
                    ):
                        self._start_cleanup_timer()
                else:
                    # The cap shrank (update_max_processes) while this runner
                    # was checked out.  Park it and the pool would exceed
                    # max_processes until the 180 s idle timer fired.
                    logger.info(
                        "SherpaPool[%s]: stopping returned process instead of parking "
                        "it (max_processes=%s)", self.name, self._max_processes,
                    )
                    self._total_spawned = max(0, self._total_spawned - 1)
                    surplus = proc
            else:
                self._total_spawned = max(0, self._total_spawned - 1)
                if not is_healthy:
                    threading.Thread(target=self.safe_terminate, args=(proc,), daemon=True).start()
        self._semaphore.release()
        if surplus is not None:
            # Outside the lock: terminating a wedged runner may wait seconds.
            self.safe_terminate(surplus)

    def stop_all(self):
        # Include both idle and checked-out processes.  Previously only the
        # idle pool was terminated, so active runner processes survived
        # profile close and kept their model memory (and pipes) alive.
        # Disable cleanup first so an in-flight _cleanup_idle() cannot
        # re-arm the timer after we cancel it.
        self._cleanup_enabled = False
        with self._lock:
            processes = list(self._active)
            processes.extend(
                proc for proc, _exe, _script, _last in self._pool
                if proc not in self._active
            )
            # Mark unhealthy and detach them while holding the lock so a
            # concurrent release_process() cannot put them back into _pool.
            for proc in processes:
                try:
                    proc.is_healthy = False
                except Exception:
                    logger.debug(
                        "stop_all[%s]: could not mark %r unhealthy", self.name, proc, exc_info=True,
                    )
            self._active.clear()
            self._pool = []
            self._total_spawned = 0

        # Terminate outside the lock and all at once: safe_terminate() blocks
        # for seconds per process and stop_all() runs on Anki's UI thread.
        terminate_processes_parallel(processes, self.safe_terminate)
        # Cancel the idle-cleanup timer so it does not keep the pool alive after stop
        if self._cleanup_timer:
            try:
                self._cleanup_timer.cancel()
            except Exception:
                logger.debug(
                    "stop_all[%s]: cleanup timer cancel failed", self.name, exc_info=True,
                )
        self._cleanup_timer = None

    def update_max_processes(self, new_max):
        stale_processes = []
        with self._lock:
            if new_max == self._max_processes:
                return
            logger.info(f"SherpaPool[{self.name}]: Updating max_processes from {self._max_processes} to {new_max}")
            self._max_processes = new_max
            self._semaphore.set_max(new_max)
            # Shrinking the pool used to leave surplus idle runners alive until
            # the 180 s idle timer reaped them; each one holds its model memory.
            # The surplus is measured against every live process, not just the
            # idle ones: a checked-out runner still counts towards the cap.  A
            # checked-out runner cannot be reaped here, so only the idle
            # processes are dropped (oldest first) and release_process() stops
            # the rest when they come back.
            total_processes = len(self._active) + len(self._pool)
            idle_excess = min(len(self._pool), max(0, total_processes - new_max))
            if idle_excess > 0:
                for _ in range(idle_excess):
                    proc, _exe, _script, _last = self._pool.pop(0)
                    stale_processes.append(proc)
                    self._total_spawned = max(0, self._total_spawned - 1)
        if stale_processes:
            logger.info(
                "SherpaPool[%s]: terminating %s idle process(es) after max_processes shrink",
                self.name, len(stale_processes),
            )
            # Terminate concurrently: update_max_processes() is called from the
            # settings dialog on Anki's UI thread, and each safe_terminate()
            # may block for seconds on a wedged runner.
            terminate_processes_parallel(stale_processes, self.safe_terminate)

    def _start_new(self, executable_path, script_path, debug_enabled=False):
        cwd = os.path.dirname(executable_path)
        startupinfo = None
        if os.name == 'nt':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        env = os.environ.copy()

        # For Piper: pass DATA_DIR so it can find piper.exe in the profile folder
        if 'piper' in script_path.lower():
            try:
                from .. import constants
                data_dir = constants.DATA_DIR
                env['superfreetts_DATA_DIR'] = data_dir
                logger.info(f"SherpaPool[{self.name}]: Set superfreetts_DATA_DIR={data_dir}")
            except Exception as e:
                logger.warning(f"SherpaPool[{self.name}]: Failed to set superfreetts_DATA_DIR: {e}")

        logger.info(f"SherpaPool[{self.name}]: Starting NEW Process: {os.path.basename(script_path)} (debug_enabled={debug_enabled})")

        # Observability Upgrade: Initialize the output sink (default to DEVNULL)
        stderr_sink = subprocess.DEVNULL

        if debug_enabled:
            try:
                # Log Strategy: Per-engine files in user_files/log
                # Absolute path to the addon's root user_files/log
                script_dir = os.path.dirname(os.path.abspath(__file__))
                addon_root = os.path.normpath(os.path.join(script_dir, ".."))
                log_dir = os.path.join(addon_root, 'user_files', 'log')

                logger.info(f"SherpaPool[{self.name}]: Creating log directory at {log_dir}")
                os.makedirs(log_dir, exist_ok=True)

                log_path = os.path.join(log_dir, f"{self.name.lower()}_runtime.log")
                logger.info(f"SherpaPool[{self.name}]: Logging stderr to {log_path}")

                # Lightweight Log Rotation (Roll to .old if file > 5MB)
                if os.path.exists(log_path) and os.path.getsize(log_path) > 5 * 1024 * 1024:
                    backup_path = log_path + ".old"
                    if os.path.exists(backup_path): os.remove(backup_path)
                    os.rename(log_path, backup_path)

                # Use file-based logging (Safe: No PIPE deadlock risk)
                stderr_sink = open(log_path, "a", encoding='utf-8', buffering=1, errors='replace')  # Line-buffered
            except Exception as e:
                logger.warning(f"SherpaPool[{self.name}]: Failed to create log sink: {e}")
                stderr_sink = subprocess.DEVNULL

        # IPC BREAKING BUG FIX:
        # Previously actual_stderr was set to subprocess.STDOUT, which merges logs into
        # the JSON stream. We now use stderr_sink to keep stdout (JSON) clean.
        popen_kwargs = {}
        if os.name == 'nt':
            # ``taskkill /T`` walks the child tree by PID; a new process group
            # is not needed for termination.
            pass
        else:
            # Give every runner its own process group so terminate_process()
            # can reap grand-children (e.g. the piper binary) as well.
            popen_kwargs['start_new_session'] = True
        try:
            proc = subprocess.Popen(
                [executable_path, "-u", script_path],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=(stderr_sink if debug_enabled else subprocess.PIPE),  # capture or redirect to file
                cwd=cwd,
                startupinfo=startupinfo,
                env=env,
                text=False,
                bufsize=0,
                **popen_kwargs
            )
        except Exception:
            # If Popen fails (e.g. executable missing), ensure the sink handle is
            # closed to avoid leaking a file descriptor on every failed spawn.
            if debug_enabled and hasattr(stderr_sink, 'close') and stderr_sink != subprocess.DEVNULL:
                try:
                    stderr_sink.close()
                except Exception:
                    logger.debug(
                        "SherpaPool[%s]: closing the stderr sink after a failed spawn failed",
                        self.name, exc_info=True,
                    )
            raise
        proc.is_healthy = True
        setattr(proc, "owns_process_group", os.name != 'nt')
        # Deadline-enabled reader: every response is read through a queue so a
        # wedged runner can be killed instead of blocking the worker forever.
        start_stdout_reader(proc, self.name)

        # If we captured stderr as a PIPE (debug not enabled), drain & log it at INFO level
        def _drain_stderr(p, debug):
            try:
                for line in iter(p.stderr.readline, b''):
                    try:
                        decoded = line.decode('utf-8', errors='replace')
                        # Not a debug-only channel: surface stderr at INFO so we always have a record
                        logger.info(f"{self.name} stderr: {decoded.rstrip()}")
                    except Exception:
                        logger.debug(
                            "%s stderr: dropping an undecodable line", self.name, exc_info=True,
                        )
            finally:
                try:
                    p.stderr.close()
                except Exception:
                    logger.debug(
                        "%s stderr: closing the drain pipe failed", self.name, exc_info=True,
                    )

        if not debug_enabled:
            threading.Thread(target=_drain_stderr, args=(proc, debug_enabled), daemon=True).start()

        # Guard: Close our file sink handle in parent after child inherits it to avoid leaks
        if debug_enabled and hasattr(stderr_sink, 'close') and stderr_sink != subprocess.DEVNULL:
            try:
                stderr_sink.close()
            except Exception:
                logger.debug(
                    "SherpaPool[%s]: closing the inherited log sink in the parent failed",
                    self.name, exc_info=True,
                )

        return proc
