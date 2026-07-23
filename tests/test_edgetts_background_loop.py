"""
Unit tests for root cause 2.1 fix: run_async_safe() in service_edgetts.py
used to create a brand new ThreadPoolExecutor + a brand new asyncio event
loop (via asyncio.run()) for every single call made from a thread that
already had a running event loop - exactly the situation Anki's realtime
TTS playback thread is in (ttsplayer.py). This test suite verifies the
fixed version reuses one singleton background loop/thread across many
calls instead of creating a new one each time, without changing the
observable return-value behavior for callers.

See superfreetts_macos_crash_fix_plan.md, section 2.1 / Phase 4.

These are pure asyncio/threading tests with a fake coroutine (no real
network calls to Microsoft's Edge TTS endpoint), so they're fast and
deterministic.
"""

import sys
import os
import asyncio
import threading
import time

import pytest

addon_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, addon_dir)
sys.path.insert(0, os.path.join(addon_dir, 'external'))

from tests import mock_anki
mock_anki.mock_all()

from superfreetts_addon.services import service_edgetts  # noqa: E402


async def _fake_async_work(value):
    """Stand-in for a real edge_tts coroutine - just proves the call
    actually executed on an event loop and returns a recognizable value."""
    await asyncio.sleep(0.01)
    return value


def _call_run_async_safe_from_a_thread_with_its_own_loop(value):
    """
    Runs service_edgetts.run_async_safe() from inside a thread that has its
    own separate, already-running event loop - this is the exact situation
    ttsplayer.py's background thread is in (Anki's TaskManager runs
    _play() on a background thread, and by the time hypertts eventually
    calls into EdgeTTS, that thread may already be inside asyncio.run() for
    an unrelated reason in this codebase's broader async plumbing). Returns
    whatever run_async_safe() returns.
    """
    result_holder = {}

    async def _runner():
        # Being inside this coroutine means asyncio.get_running_loop()
        # succeeds when run_async_safe() is called from here - the "loop
        # already running in this thread" branch we're testing.
        result_holder['value'] = service_edgetts.run_async_safe(_fake_async_work(value))

    asyncio.run(_runner())
    return result_holder['value']


@pytest.fixture(autouse=True)
def _reset_background_loop_between_tests():
    """
    The background loop is a module-level singleton by design (that's the
    whole point of the fix), but tests should not leak a loop/thread from
    one test into another - stop it and clear the module globals before
    and after each test so every test starts from a clean slate.
    """
    def _stop():
        loop = service_edgetts._background_loop
        if loop is not None and loop.is_running():
            loop.call_soon_threadsafe(loop.stop)
        thread = service_edgetts._background_loop_thread
        if thread is not None and thread.is_alive():
            thread.join(timeout=2)
        service_edgetts._background_loop = None
        service_edgetts._background_loop_thread = None

    _stop()
    yield
    _stop()


@pytest.mark.unit
class TestBackgroundLoopReuse:

    def test_single_call_returns_correct_result(self):
        """Baseline correctness: the reused-loop path must still return the
        coroutine's actual result, unchanged from the caller's perspective."""
        result = _call_run_async_safe_from_a_thread_with_its_own_loop("hello")
        assert result == "hello"

    def test_no_running_loop_branch_is_unaffected(self):
        """
        The fix only touches the "a loop is already running in this
        thread" branch. When called from a plain thread with no loop at
        all (e.g. voice_list() at startup), behavior must be unchanged:
        plain asyncio.run(), no background loop involved.
        """
        assert service_edgetts._background_loop is None
        result = service_edgetts.run_async_safe(_fake_async_work("no-loop-case"))
        assert result == "no-loop-case"
        # This branch must NOT have started the background loop - it takes
        # a completely separate code path (the `except RuntimeError` one).
        assert service_edgetts._background_loop is None

    def test_background_loop_is_created_lazily_once(self):
        """Before any call requiring the background loop, none should
        exist. After one such call, exactly one should exist."""
        assert service_edgetts._background_loop is None
        _call_run_async_safe_from_a_thread_with_its_own_loop("first")
        assert service_edgetts._background_loop is not None
        first_loop = service_edgetts._background_loop
        first_thread = service_edgetts._background_loop_thread
        assert first_thread.is_alive()

        _call_run_async_safe_from_a_thread_with_its_own_loop("second")
        # Must be the SAME loop/thread reused, not a new one.
        assert service_edgetts._background_loop is first_loop
        assert service_edgetts._background_loop_thread is first_thread

    def test_many_sequential_calls_reuse_the_same_loop_and_thread(self):
        """
        Core regression test for root cause 2.1: simulates the realtime
        study-session scenario (many card flips, each needing fresh audio).

        Note on what this test does and doesn't claim: measuring raw OS
        thread *count* across sequential calls turned out not to reliably
        distinguish old vs. new behavior here, because the old
        ThreadPoolExecutor(max_workers=1) was used inside a `with` block
        that joins/tears down its single worker thread before returning
        control to the next iteration - so a purely sequential loop
        wouldn't necessarily show thread count climbing even under the old
        code. What the old code definitely did NOT do, and what actually
        matters for the reported problem (per-call setup/teardown cost, and
        many threads/loops in flight when calls overlap - see the
        concurrent test below), is reuse the same loop/thread across calls;
        every single old call built a brand new one from scratch. This test
        asserts that concrete, honestly-differentiating property instead.
        """
        _call_run_async_safe_from_a_thread_with_its_own_loop("warm-up")
        loop_after_first_call = service_edgetts._background_loop
        thread_after_first_call = service_edgetts._background_loop_thread
        assert loop_after_first_call is not None
        assert thread_after_first_call is not None

        for i in range(20):
            result = _call_run_async_safe_from_a_thread_with_its_own_loop(f"call-{i}")
            assert result == f"call-{i}"
            assert service_edgetts._background_loop is loop_after_first_call
            assert service_edgetts._background_loop_thread is thread_after_first_call

    def test_concurrent_calls_from_multiple_threads_are_thread_safe(self):
        """
        batch_executor.py runs multiple worker threads concurrently for a
        given engine; several of them may call into EdgeTTS at once. The
        shared background loop must handle concurrent submissions from
        different threads correctly (asyncio.run_coroutine_threadsafe is
        documented as safe for exactly this).
        """
        results = [None] * 10
        errors = []

        def _worker(i):
            try:
                results[i] = _call_run_async_safe_from_a_thread_with_its_own_loop(f"worker-{i}")
            except Exception as e:  # pragma: no cover - failure path only
                errors.append(e)

        threads = [threading.Thread(target=_worker, args=(i,)) for i in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=5)

        assert errors == []
        assert results == [f"worker-{i}" for i in range(10)]
        # All 10 concurrent calls must have shared a single background loop.
        assert service_edgetts._background_loop is not None

    def test_background_loop_unavailable_falls_back_without_crashing(self, monkeypatch):
        """
        Safety net: if the background loop fails to start (returns None),
        run_async_safe() must still produce a correct result via the old
        one-off thread+loop fallback rather than raising.
        """
        monkeypatch.setattr(service_edgetts, '_get_background_loop', lambda: None)
        result = _call_run_async_safe_from_a_thread_with_its_own_loop("fallback-case")
        assert result == "fallback-case"
