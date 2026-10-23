"""IPC deadline tests for the local TTS engines (audit finding P1-2).

The failure this guards against: a runner process accepts a request and never
answers.  Before the fix the worker sat inside a blocking ``stdout.readline()``
forever, holding a pool permit, so the pool drained one request at a time and
the user had to restart Anki.
"""

import inspect
import io
import json
import queue
import subprocess
import sys
import threading
import time

import pytest

from superfreetts_addon import batch_constants
from superfreetts_addon.services import (
    process_pool,
    service_kokoro,
    service_mms,
    service_piper,
    service_supertonic,
)
from superfreetts_addon.services.process_pool import (
    DynamicSemaphore,
    EngineBusyError,
    IpcTimeoutError,
    SherpaProcessPool,
    read_response,
    request_timeout,
    start_stdout_reader,
    terminate_process,
)


class HangingProcess:
    """Runner stand-in that never writes a response."""

    def __init__(self):
        self.stdin = io.BytesIO()
        self.stdout = None
        self.stderr = None
        self.is_healthy = True
        self.returncode = None
        self.terminate_calls = 0
        self.ipc_stdout_queue = queue.Queue()

    def poll(self):
        return self.returncode

    def terminate(self):
        self.terminate_calls += 1
        self.returncode = 0

    def wait(self, timeout=None):
        return self.returncode


class FakePool:
    def __init__(self, process=None, error=None):
        self.process = process
        self.error = error
        self.released = 0
        self.requests = 0

    def get_process(self, *args, **kwargs):
        self.requests += 1
        if self.error is not None:
            raise self.error
        return self.process

    def release_process(self, *args, **kwargs):
        self.released += 1


def build_mms(tmp_path, monkeypatch, process):
    (tmp_path / "mms_models" / "eng").mkdir(parents=True)
    monkeypatch.setattr(service_mms.constants, "DATA_DIR", str(tmp_path))

    mms = object.__new__(service_mms.MmsTTS)
    mms._get_python_exe = lambda: sys.executable

    def config_value(key, default=None):
        return 1 if key == "num_threads" else default

    mms.get_configuration_value_optional = config_value
    pool = FakePool(process)
    monkeypatch.setattr(service_mms, "_sherpa_pool", pool)
    voice = type("Voice", (), {"voice_key": "mms_eng"})()
    return mms, voice, pool


@pytest.fixture
def short_deadlines(monkeypatch):
    """Shrink every IPC deadline so tests never wait the real 60-300 s."""
    monkeypatch.setattr(batch_constants, "IPC_SINGLE_REQUEST_TIMEOUT_SECONDS", 0.05)
    monkeypatch.setattr(batch_constants, "IPC_BATCH_REQUEST_TIMEOUT_SECONDS", 0.05)
    monkeypatch.setattr(batch_constants, "IPC_COLD_START_TIMEOUT_SECONDS", 0.05)
    monkeypatch.setattr(batch_constants, "IPC_ACQUIRE_TIMEOUT_SECONDS", 0.05)


# ---------------------------------------------------------------- semaphore


@pytest.mark.unit
def test_semaphore_acquire_times_out_instead_of_blocking():
    semaphore = DynamicSemaphore(1)
    assert semaphore.acquire() is True

    started = time.monotonic()
    assert semaphore.acquire(timeout=0.05) is False
    assert time.monotonic() - started < 1.0

    semaphore.release()
    assert semaphore.acquire(timeout=0.5) is True
    semaphore.release()
    assert semaphore.in_use == 0


@pytest.mark.unit
def test_semaphore_set_max_wakes_waiting_threads():
    semaphore = DynamicSemaphore(1)
    assert semaphore.acquire() is True
    acquired = threading.Event()

    def waiter():
        if semaphore.acquire(timeout=2.0):
            acquired.set()

    thread = threading.Thread(target=waiter, daemon=True)
    thread.start()
    time.sleep(0.05)
    assert not acquired.is_set()

    semaphore.set_max(2)
    assert acquired.wait(timeout=2.0)
    semaphore.release()
    semaphore.release()


# --------------------------------------------------------------- read_response


@pytest.mark.unit
def test_read_response_returns_line_from_reader_thread():
    proc = HangingProcess()
    proc.ipc_stdout_queue.put(b'{"status": "ok"}\n')

    line = read_response(proc, "Test", timeout=1.0)

    assert json.loads(line)["status"] == "ok"
    assert proc.terminate_calls == 0


@pytest.mark.unit
def test_read_response_reports_eof_without_waiting():
    proc = HangingProcess()
    proc.ipc_stdout_eof = True

    started = time.monotonic()
    assert read_response(proc, "Test", timeout=5.0) == b""
    assert time.monotonic() - started < 0.5


@pytest.mark.unit
def test_read_response_timeout_kills_real_runner():
    proc = subprocess.Popen(
        [sys.executable, "-c", "import time; time.sleep(30)"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )
    proc.is_healthy = True

    started = time.monotonic()
    try:
        with pytest.raises(IpcTimeoutError):
            read_response(proc, "Test", timeout=0.3)
        elapsed = time.monotonic() - started
    finally:
        terminate_process(proc)

    assert elapsed < 5.0
    assert proc.poll() is not None, "hung runner must be killed"
    assert proc.is_healthy is False
    assert proc.stdin.closed and proc.stdout.closed


@pytest.mark.unit
def test_reader_thread_marks_eof_after_process_exit():
    proc = subprocess.Popen(
        [sys.executable, "-c", "print('{}')"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )
    start_stdout_reader(proc, "Test")
    assert read_response(proc, "Test", timeout=5.0) == b"{}\n"
    # Second read must hit EOF (process exited), not the deadline.
    assert read_response(proc, "Test", timeout=5.0) == b""
    terminate_process(proc)


# ------------------------------------------------------------- pool deadline


@pytest.mark.unit
def test_pool_get_process_raises_engine_busy_when_pool_is_drained():
    pool = SherpaProcessPool("test", max_processes=1)
    try:
        assert pool._semaphore.acquire(timeout=1.0) is True

        with pytest.raises(EngineBusyError):
            pool.get_process("engine", "runner.py", timeout=0.05)

        # A failed acquire must not release somebody else's permit.
        assert pool._semaphore.in_use == 1
    finally:
        pool._semaphore.release()
        pool.stop_all()


@pytest.mark.unit
def test_pool_releases_permit_when_spawn_fails(monkeypatch):
    pool = SherpaProcessPool("test", max_processes=1)
    try:
        def boom(*args, **kwargs):
            raise OSError("engine missing")

        monkeypatch.setattr(pool, "_start_new", boom)
        with pytest.raises(OSError):
            pool.get_process("engine", "runner.py", timeout=1.0)
        assert pool._semaphore.in_use == 0
    finally:
        pool.stop_all()


@pytest.mark.unit
def test_unhealthy_process_is_not_returned_to_idle_pool():
    """After a timeout the runner is discarded, so a retry spawns a new one."""
    pool = SherpaProcessPool("test", max_processes=1)
    proc = HangingProcess()
    try:
        pool._active.add(proc)
        pool._total_spawned = 1
        pool._semaphore.acquire(timeout=1.0)

        terminate_process(proc)
        pool.release_process(proc, "engine", "runner.py")

        assert proc not in pool._active
        assert pool._pool == []
        assert pool._total_spawned == 0
        assert pool._semaphore.in_use == 0
    finally:
        pool.stop_all()


# --------------------------------------------------------------- deadlines


@pytest.mark.unit
def test_first_request_on_fresh_runner_gets_cold_start_deadline():
    proc = HangingProcess()

    assert request_timeout(proc) == float(batch_constants.IPC_COLD_START_TIMEOUT_SECONDS)
    assert request_timeout(proc) == float(batch_constants.IPC_SINGLE_REQUEST_TIMEOUT_SECONDS)
    assert request_timeout(proc, chunk=True) == float(batch_constants.IPC_BATCH_REQUEST_TIMEOUT_SECONDS)


# ------------------------------------------------------- engine integration


@pytest.mark.unit
def test_mms_single_request_fails_within_deadline(tmp_path, monkeypatch, short_deadlines):
    process = HangingProcess()
    mms, voice, pool = build_mms(tmp_path, monkeypatch, process)

    started = time.monotonic()
    with pytest.raises(service_mms.errors.RequestError):
        mms.get_tts_audio("hello", voice, {})
    elapsed = time.monotonic() - started

    assert elapsed < 5.0
    assert process.terminate_calls >= 1, "the hung runner must be killed"
    assert process.is_healthy is False
    assert pool.released == 2, "permits must be released on every attempt"


@pytest.mark.unit
def test_mms_batch_returns_failed_items_within_deadline(tmp_path, monkeypatch, short_deadlines):
    process = HangingProcess()
    mms, voice, pool = build_mms(tmp_path, monkeypatch, process)
    texts = ["one", "two", "three"]

    started = time.monotonic()
    results = mms.get_tts_audio_batch(texts, voice, {})
    elapsed = time.monotonic() - started

    assert results == [None] * len(texts)
    assert elapsed < 5.0
    assert pool.released == 2


@pytest.mark.unit
def test_engine_busy_is_not_retried(tmp_path, monkeypatch):
    mms, voice, _ = build_mms(tmp_path, monkeypatch, HangingProcess())
    pool = FakePool(error=EngineBusyError("Kokoro engine busy"))
    monkeypatch.setattr(service_mms, "_sherpa_pool", pool)

    results = mms.get_tts_audio_batch(["one"], voice, {})

    assert results == [None]
    assert pool.requests == 1, "a busy pool must fail fast, not wait twice"


LOCAL_ENGINE_MODULES = [
    ("MMS", service_mms),
    ("Kokoro", service_kokoro),
    ("Piper", service_piper),
    ("Supertonic", service_supertonic),
]


@pytest.mark.unit
@pytest.mark.parametrize("engine,module", LOCAL_ENGINE_MODULES)
def test_every_local_engine_reads_through_the_deadline_helper(engine, module):
    """Wiring guard: a raw blocking readline() would reintroduce the hang."""
    source = inspect.getsource(module)

    assert "process.stdout.readline()" not in source
    assert source.count("read_response(process, \"%s\"" % engine) == 2
    assert "IpcTimeoutError" in source
    assert "EngineBusyError" in source


def test_process_pool_reexported_from_service_mms():
    """Other engines and tts_orchestrator import the pool from service_mms."""
    assert service_mms.SherpaProcessPool is process_pool.SherpaProcessPool
    assert service_mms.EngineBusyError is process_pool.EngineBusyError
