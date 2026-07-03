"""
Integration tests for batch_executor — focusing on MultiEngineExecutor routing logic,
detect_service(), get_executor(), and end-to-end execute() flow.

Strategy:
- Patch _execute_single_task to return a fake result tuple so we test routing /
  progress / checkpoint logic without needing real TTS audio generation.
- All helpers are local to avoid polluting the session-level ServiceBase subclass list.
"""

import os
import concurrent.futures
from unittest.mock import MagicMock, patch, call

import pytest

from superfreetts_addon.batch_executor import (
    MultiEngineExecutor,
    BoundedThreadPoolExecutor,
    get_multi_engine_executor,
    reset_multi_engine_executor,
)
from superfreetts_addon import batch_constants
from superfreetts_addon.voice import TtsVoice_v3, TtsVoiceId_v3
from superfreetts_addon import constants
from superfreetts_addon.languages import AudioLanguage


# ─────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────

def _make_voice(service_name: str) -> TtsVoice_v3:
    """Create a minimal TtsVoice_v3 tagged with the given service."""
    voice_id = TtsVoiceId_v3({"id": "test_voice"}, service_name)
    return TtsVoice_v3(
        name="TestVoice",
        voice_key={"id": "test_voice"},
        options={},
        service=service_name,
        gender=constants.Gender.Male,
        audio_languages=[AudioLanguage.en_US],
        service_fee=constants.ServiceFee.free,
    )


def _make_task(note_id: int, text: str = "hello", service_name: str = "EdgeTTS") -> dict:
    """Build a minimal task dict matching the shape batch_executor expects."""
    voice = _make_voice(service_name)
    return {
        "note_id": note_id,
        "processed_text": text,
        "batch": MagicMock(),
        "audio_request_context": MagicMock(),
        "chosen_voice": voice,
    }


def _fake_result(task: dict):
    """Fake result tuple: (note_id, src, processed, sound, full_path, is_error)."""
    return (task["note_id"], task["processed_text"], task["processed_text"],
            f"audio_{task['note_id']}.mp3", f"/tmp/audio_{task['note_id']}.mp3", False)


# ─────────────────────────────────────────────────────────────
# detect_service
# ─────────────────────────────────────────────────────────────

class TestDetectService:

    def setup_method(self):
        self.executor = MultiEngineExecutor()

    def teardown_method(self):
        self.executor.shutdown(wait=False)

    def test_detect_service_from_chosen_voice(self):
        """detect_service() reads service name from task['chosen_voice'].voice_id.service."""
        task = _make_task(1, service_name="EdgeTTS")
        assert self.executor.detect_service(task) == "EdgeTTS"

    def test_detect_service_piper(self):
        """detect_service() works for PiperTTS tasks."""
        task = _make_task(1, service_name="PiperTTS")
        assert self.executor.detect_service(task) == "PiperTTS"

    def test_detect_service_no_voice_returns_default(self):
        """detect_service() returns 'default' when chosen_voice is absent and
        there is no batch voice_selection either."""
        # A completely bare task with no voice info at all
        task = {
            "note_id": 99,
            "processed_text": "text",
        }
        result = self.executor.detect_service(task)
        assert result == "default"

    def test_detect_service_none_chosen_voice_returns_default(self):
        """detect_service() returns 'default' when chosen_voice is None and no batch key."""
        # Without a 'batch' key, detect_service cannot follow any voice_selection fallback
        task = {
            "note_id": 2,
            "processed_text": "text",
            "chosen_voice": None,
        }
        result = self.executor.detect_service(task)
        assert result == "default"


# ─────────────────────────────────────────────────────────────
# get_executor / normalization
# ─────────────────────────────────────────────────────────────

class TestGetExecutor:

    def setup_method(self):
        self.executor = MultiEngineExecutor(engine_config={
            "EdgeTTS": 2,
            "Piper": 1,
            "Kokoro": 1,
            "default": 1,
        })

    def teardown_method(self):
        self.executor.shutdown(wait=False)

    def test_get_executor_edgetts_uses_edgetts_pool(self):
        """EdgeTTS service maps to the named EdgeTTS executor pool."""
        pool = self.executor.get_executor("EdgeTTS")
        assert pool is self.executor.executors["EdgeTTS"]

    def test_get_executor_piperts_normalizes_to_piper(self):
        """PiperTTS is stripped to 'Piper' when looking up the executor pool."""
        pool = self.executor.get_executor("PiperTTS")
        assert pool is self.executor.executors["Piper"]

    def test_get_executor_kokorotts_normalizes_to_kokoro(self):
        """KokoroTTS is stripped to 'Kokoro' when looking up the executor pool."""
        pool = self.executor.get_executor("KokoroTTS")
        assert pool is self.executor.executors["Kokoro"]

    def test_get_executor_unknown_uses_default(self):
        """Unknown service name falls back to the default executor pool."""
        pool = self.executor.get_executor("SomeUnknownTTS")
        assert pool is self.executor.default_executor


# ─────────────────────────────────────────────────────────────
# MultiEngineExecutor initialisation
# ─────────────────────────────────────────────────────────────

class TestMultiEngineExecutorInit:

    def test_default_config_respects_edgetts_cap(self):
        """Default engine_config uses EDGETTS_MAX_WORKERS for EdgeTTS."""
        executor = MultiEngineExecutor()
        try:
            edgetts_pool = executor.executors.get("EdgeTTS")
            assert edgetts_pool is not None
            assert edgetts_pool._max_workers == batch_constants.EDGETTS_MAX_WORKERS
        finally:
            executor.shutdown(wait=False)

    def test_custom_engine_config_is_applied(self):
        """Custom engine_config overrides default worker counts."""
        executor = MultiEngineExecutor(engine_config={"EdgeTTS": 5, "default": 2})
        try:
            assert executor.executors["EdgeTTS"]._max_workers == 5
        finally:
            executor.shutdown(wait=False)

    def test_per_engine_executors_are_bounded_thread_pools(self):
        """Each named executor is a BoundedThreadPoolExecutor instance."""
        executor = MultiEngineExecutor(engine_config={"EdgeTTS": 1, "default": 1})
        try:
            for name, pool in executor.executors.items():
                assert isinstance(pool, BoundedThreadPoolExecutor), \
                    f"Expected BoundedThreadPoolExecutor for {name}, got {type(pool)}"
        finally:
            executor.shutdown(wait=False)


# ─────────────────────────────────────────────────────────────
# execute() — end-to-end batch flow (patched _execute_single_task)
# ─────────────────────────────────────────────────────────────

class TestMultiEngineBatchFlow:
    """Integration tests that patch _execute_single_task to return fake tuples."""

    @pytest.fixture(autouse=True)
    def executor(self):
        """Provide a fresh MultiEngineExecutor and shut it down after each test."""
        ex = MultiEngineExecutor(engine_config={"EdgeTTS": 2, "default": 1})
        yield ex
        ex.shutdown(wait=False)

    def test_execute_empty_task_list_returns_empty(self, executor):
        """execute() with no tasks returns an empty list."""
        with patch.object(executor, "_execute_single_task", side_effect=_fake_result):
            results = executor.execute([], on_progress=None, enable_checkpoint=False)
        assert results == []

    def test_execute_returns_one_result_per_task(self, executor):
        """execute() returns exactly one result for each submitted task."""
        tasks = [_make_task(i) for i in range(5)]

        with patch.object(executor, "_execute_single_task", side_effect=_fake_result):
            results = executor.execute(tasks, on_progress=None, enable_checkpoint=False)

        assert len(results) == 5

    def test_execute_calls_on_progress_for_each_task(self, executor):
        """on_progress callback is invoked once per completed task."""
        tasks = [_make_task(i) for i in range(3)]
        progress_calls = []

        def on_progress(note_id, result):
            progress_calls.append(note_id)

        with patch.object(executor, "_execute_single_task", side_effect=_fake_result):
            executor.execute(tasks, on_progress=on_progress, enable_checkpoint=False)

        assert len(progress_calls) == 3
        assert sorted(progress_calls) == [0, 1, 2]

    def test_execute_no_error_flag_in_successful_results(self, executor):
        """Successful results have is_error=False (last element of tuple)."""
        tasks = [_make_task(10)]

        with patch.object(executor, "_execute_single_task", side_effect=_fake_result):
            results = executor.execute(tasks, on_progress=None, enable_checkpoint=False)

        assert results[0][-1] is False   # is_error flag

    def test_execute_error_flag_set_on_exception(self, executor):
        """If _execute_single_task raises, result tuple has is_error=True."""
        tasks = [_make_task(1)]

        with patch.object(executor, "_execute_single_task",
                          side_effect=RuntimeError("deliberate failure")):
            results = executor.execute(tasks, on_progress=None, enable_checkpoint=False)

        assert len(results) == 1
        assert results[0][-1] is True   # is_error flag

    def test_execute_checkpoint_cleaned_up_after_completion(self, executor, tmp_path):
        """Checkpoint file is removed after a successful batch run."""
        # Point checkpoint dir to tmp_path
        executor.checkpoint.state_dir = str(tmp_path)
        tasks = [_make_task(i) for i in range(2)]

        with patch.object(executor, "_execute_single_task", side_effect=_fake_result):
            executor.execute(tasks, on_progress=None, batch_name="testbatch",
                             enable_checkpoint=True)

        # Checkpoint should have been cleaned up
        leftover = [f for f in os.listdir(str(tmp_path)) if "testbatch" in f]
        assert leftover == []

    def test_execute_tasks_routed_to_edgetts_pool(self, executor):
        """EdgeTTS tasks are submitted to the EdgeTTS executor, not the default."""
        tasks = [_make_task(i, service_name="EdgeTTS") for i in range(2)]
        edgetts_pool = executor.executors["EdgeTTS"]

        submit_calls = []
        original_submit = edgetts_pool.submit

        def tracking_submit(fn, *args, **kwargs):
            submit_calls.append(fn)
            return original_submit(fn, *args, **kwargs)

        edgetts_pool.submit = tracking_submit

        with patch.object(executor, "_execute_single_task", side_effect=_fake_result):
            executor.execute(tasks, on_progress=None, enable_checkpoint=False)

        # All 2 tasks should have been routed through the EdgeTTS pool
        assert len(submit_calls) == 2


# ─────────────────────────────────────────────────────────────
# Singleton helpers
# ─────────────────────────────────────────────────────────────

class TestMultiEngineExecutorSingleton:

    def setup_method(self):
        reset_multi_engine_executor()

    def teardown_method(self):
        reset_multi_engine_executor()

    def test_get_returns_same_instance(self):
        """get_multi_engine_executor() returns the same object on repeated calls."""
        a = get_multi_engine_executor()
        b = get_multi_engine_executor()
        assert a is b

    def test_reset_clears_singleton(self):
        """reset_multi_engine_executor() causes next get to return a new instance."""
        a = get_multi_engine_executor()
        reset_multi_engine_executor()
        b = get_multi_engine_executor()
        assert a is not b

    def test_custom_config_triggers_new_executor(self):
        """Passing a different engine_config creates a new executor."""
        a = get_multi_engine_executor(engine_config={"EdgeTTS": 1})
        b = get_multi_engine_executor(engine_config={"EdgeTTS": 5})
        assert a is not b
