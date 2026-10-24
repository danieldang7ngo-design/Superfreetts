"""Stall and unexpected-failure handling for one batch chunk.

These helpers were extracted from ``_execute_unique_tasks_unified``; they own
the "engine stopped answering" path, which is the hardest one to reproduce by
hand.  Pin the three side effects: cache entry, note status, checkpoint record.
"""

from contextlib import contextmanager
from types import SimpleNamespace
from unittest.mock import MagicMock

from . import mock_anki

mock_anki.mock_all()

from superfreetts_addon import batch_orchestrator


class _Ctx:
    def __init__(self):
        self.error = None

    def set_error(self, error):
        self.error = error

    def set_source_text(self, text):
        pass

    def set_processed_text(self, text):
        pass

    def set_sound(self, sound):
        pass

    def set_status(self, status):
        pass


class _Status:
    def __init__(self):
        self.must_continue = True
        self.unique_tasks_completed = 0
        self.total_unique_tasks = 0
        self.usage_session_id = None
        self.errors = {}
        self.messages = []

    @contextmanager
    def get_note_action_context(self, note_id, blank_fields):
        ctx = _Ctx()
        try:
            yield ctx
        finally:
            if ctx.error is not None:
                self.errors[note_id] = ctx.error

    def notify_change(self, note_id):
        pass

    def set_status_message(self, message):
        self.messages.append(message)


def _orchestrator():
    hypertts = SimpleNamespace(
        anki_utils=SimpleNamespace(get_note_by_id=lambda note_id: None),
        service_manager=None,
        text_processing_cache=None,
        get_ui_language=lambda: "en",
    )
    return batch_orchestrator.BatchOrchestrator(hypertts)


def test_stall_marks_every_pending_note_and_cancels_futures():
    orchestrator = _orchestrator()
    status = _Status()
    checkpoint = MagicMock()
    future = MagicMock()
    cache = {}
    chunk = [("key-a", {}, [0]), ("key-b", {}, [1])]
    future_to_chunk = {future: chunk}
    tasks = [{"note_id": 10}, {"note_id": 11}]

    completed = orchestrator._handle_stall(
        future_to_chunk, MagicMock(), tasks, cache, checkpoint, status, "en", 0
    )

    assert completed == 2
    assert future_to_chunk == {}
    future.cancel.assert_called_once()
    assert cache["key-a"][0] is None and cache["key-b"][0] is None
    assert set(status.errors) == {10, 11}
    assert checkpoint.mark_error.call_count == 2
    checkpoint.flush.assert_called_once()
    assert status.messages[-1] is not None


def test_unexpected_chunk_failure_marks_notes_without_checkpointing_errors():
    orchestrator = _orchestrator()
    status = _Status()
    cache = {}
    chunk = [("key-a", {}, [0])]
    tasks = [{"note_id": 10}]

    completed = orchestrator._fail_chunk(chunk, RuntimeError("boom"), tasks, cache, status, 4)

    assert completed == 5
    assert cache["key-a"][0] is None
    assert isinstance(status.errors[10], RuntimeError)
