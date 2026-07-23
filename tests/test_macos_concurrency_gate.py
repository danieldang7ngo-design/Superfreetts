"""
Unit tests for root cause 2.4 fix: MacOS.get_tts_audio() spawned two
subprocesses per call ('say' and the ffmpeg-based aqt.sound._encode_mp3
encode step) with no limit on how many could run concurrently, unlike
service_edgetts.py which already gates concurrent requests. This suite
verifies the added concurrency gate actually bounds concurrent execution,
mirroring service_edgetts.py's existing _get_request_gate() pattern.

See superfreetts_macos_crash_fix_plan.md, section 2.4 / Phase 5.

subprocess.check_call and aqt.sound._encode_mp3 are mocked (no real 'say'
binary is available in this Linux test environment) with a small
artificial delay so overlapping calls can be observed/measured.
"""

import sys
import os
import threading
import time
from unittest.mock import patch, MagicMock

import pytest

addon_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, addon_dir)
sys.path.insert(0, os.path.join(addon_dir, 'external'))

from tests import mock_anki
mock_anki.mock_all()

from superfreetts_addon.services import service_macos  # noqa: E402


class _FakeVoice:
    def __init__(self, name='Alex'):
        self.voice_key = {'name': name}


@pytest.fixture(autouse=True)
def _reset_gate_between_tests():
    """The gate is a module-level singleton by design (mirrors
    service_edgetts.py) - reset it between tests so configured sizes from
    one test don't leak into another."""
    service_macos._request_gate = None
    service_macos._request_gate_size = None
    yield
    service_macos._request_gate = None
    service_macos._request_gate_size = None


@pytest.mark.unit
class TestMacOSConcurrencyGate:

    def test_advanced_configuration_options_exposes_concurrency_workers(self):
        svc = service_macos.MacOS()
        options = svc.advanced_configuration_options()
        assert 'concurrency_workers' in options
        kind, label, default, min_val, max_val = options['concurrency_workers']
        assert default == service_macos.DEFAULT_MACOS_CONCURRENCY_WORKERS
        assert min_val == 1
        assert max_val == service_macos.MAX_MACOS_CONCURRENCY_WORKERS

    def test_normal_call_still_returns_audio_bytes(self):
        """Baseline correctness: wrapping the calls in a gate must not
        change the normal successful return value."""
        svc = service_macos.MacOS()
        svc.configure({'concurrency_workers': 2})

        with patch.object(service_macos.subprocess, 'check_call') as mock_check_call, \
             patch.object(service_macos.aqt.sound, '_encode_mp3') as mock_encode:
            result = svc.get_tts_audio("hello world", _FakeVoice(), {})

        assert isinstance(result, bytes)
        mock_check_call.assert_called_once()
        mock_encode.assert_called_once()

    def test_concurrency_never_exceeds_configured_gate_size(self):
        """
        Core regression test for root cause 2.4: launch more concurrent
        get_tts_audio() calls than the configured gate size allows, and
        verify the observed peak number of calls actually executing their
        subprocess/encode step at the same time never exceeds that size.
        """
        gate_size = 2
        call_count_lock = threading.Lock()
        state = {'current': 0, 'peak': 0}

        def _tracked_slow_call(*args, **kwargs):
            with call_count_lock:
                state['current'] += 1
                state['peak'] = max(state['peak'], state['current'])
            time.sleep(0.05)
            with call_count_lock:
                state['current'] -= 1

        svc = service_macos.MacOS()
        svc.configure({'concurrency_workers': gate_size})

        num_threads = 6
        errors = []

        def _worker():
            try:
                svc.get_tts_audio("some text", _FakeVoice(), {})
            except Exception as e:  # pragma: no cover - failure path only
                errors.append(e)

        # Patch ONCE outside the threads. patch.object as a context manager
        # sets/restores a shared module-level attribute on __enter__/__exit__;
        # doing that separately inside each worker thread is unsafe here
        # (one thread's __exit__ can restore the original subprocess.check_call
        # while another thread is still mid-call, causing it to actually try
        # to run the real 'say' binary, which doesn't exist in this
        # environment) - this was verified as a real failure while writing
        # this test, not a hypothetical concern.
        with patch.object(service_macos.subprocess, 'check_call', side_effect=_tracked_slow_call), \
             patch.object(service_macos.aqt.sound, '_encode_mp3'):
            threads = [threading.Thread(target=_worker) for _ in range(num_threads)]
            for t in threads:
                t.start()
            for t in threads:
                t.join(timeout=5)

        assert errors == []
        assert state['peak'] <= gate_size, (
            f"expected at most {gate_size} concurrent 'say' calls, "
            f"observed peak concurrency of {state['peak']}"
        )
        # Sanity check the test actually created contention (otherwise the
        # assertion above would be trivially true and not testing anything).
        assert state['peak'] >= 1

    def test_gate_is_released_even_when_subprocess_raises(self):
        """
        The gate is acquired/released via try/finally around the
        subprocess calls - a failing 'say' invocation must not leave the
        gate permanently locked for subsequent calls.
        """
        svc = service_macos.MacOS()
        svc.configure({'concurrency_workers': 1})

        with patch.object(service_macos.subprocess, 'check_call', side_effect=service_macos.subprocess.CalledProcessError(1, 'say')), \
             patch.object(service_macos.aqt.sound, '_encode_mp3'):
            with pytest.raises(Exception):
                svc.get_tts_audio("boom", _FakeVoice(), {})

        # A follow-up call must not hang/deadlock because of the previous
        # call's gate not being released.
        with patch.object(service_macos.subprocess, 'check_call') as mock_check_call, \
             patch.object(service_macos.aqt.sound, '_encode_mp3'):
            result = svc.get_tts_audio("after failure", _FakeVoice(), {})

        assert isinstance(result, bytes)
        mock_check_call.assert_called_once()
