"""Cancelling a batch must not fake failures or lose finished work.

Two contracts:
  * Cancel stops FUTURE notes; notes already processed are saved, so the
    "Done" rows in the progress table match the collection.
  * Cancel is not an error: the remaining notes are not painted red and no
    error records are written to the checkpoint.
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
        self.status = None
        self.sound = None

    def set_error(self, error):
        self.error = error

    def set_source_text(self, text):
        pass

    def set_processed_text(self, text):
        pass

    def set_sound(self, sound):
        self.sound = sound

    def set_status(self, status):
        self.status = status


class _Status:
    """Minimal BatchStatus stand-in that can flip must_continue on demand."""

    def __init__(self, cancel_after=None):
        self.must_continue = True
        self.unique_tasks_completed = 0
        self.total_unique_tasks = 0
        self.usage_session_id = None
        self.errors = {}
        self.phases = []
        self.messages = []
        self._cancel_after = cancel_after
        self._notified = 0

    @contextmanager
    def get_note_action_context(self, note_id, blank_fields):
        ctx = _Ctx()
        try:
            yield ctx
        finally:
            if ctx.error is not None:
                self.errors[note_id] = ctx.error

    def notify_change(self, note_id):
        self._notified += 1
        if self._cancel_after is not None and self._notified >= self._cancel_after:
            self.must_continue = False

    def set_phase(self, phase):
        self.phases.append(phase)

    def set_status_message(self, message):
        self.messages.append(message)


def _make_orchestrator(notes):
    hypertts = SimpleNamespace(
        anki_utils=SimpleNamespace(get_note_by_id=lambda note_id: notes[note_id]),
        service_manager=None,
        text_processing_cache=None,
        get_ui_language=lambda: "en",
        _update_note_with_audio=lambda note, *args, **kwargs: setattr(note, "audio", True),
    )
    return batch_orchestrator.BatchOrchestrator(hypertts)


def test_cancel_during_apply_still_saves_finished_notes():
    notes = {1: SimpleNamespace(note_id=1), 2: SimpleNamespace(note_id=2)}
    orchestrator = _make_orchestrator(notes)
    collection = MagicMock()
    status = _Status(cancel_after=1)  # cancel arrives right after the first note
    results = [
        (1, "src", "proc", "a.mp3", "/tmp/a.mp3", None),
        (2, "src", "proc", "b.mp3", "/tmp/b.mp3", None),
    ]

    applied = orchestrator.apply_generated_batch_audio_chunk(
        results, SimpleNamespace(), status, collection
    )

    assert applied == 1
    collection.update_notes.assert_called_once()
    saved = collection.update_notes.call_args[0][0]
    assert [note.note_id for note in saved] == [1]


def test_cancel_does_not_mark_remaining_notes_as_errors(monkeypatch):
    orchestrator = _make_orchestrator({})
    status = _Status()
    status.must_continue = False
    calls = []
    monkeypatch.setattr(
        orchestrator, "_fill_missing_results", lambda *args, **kwargs: calls.append(args)
    )

    orchestrator._execute_unique_tasks_unified([], {}, status)

    assert calls == []


def test_completed_run_still_reports_missing_audio(monkeypatch):
    orchestrator = _make_orchestrator({})
    status = _Status()
    calls = []
    monkeypatch.setattr(
        orchestrator, "_fill_missing_results", lambda *args, **kwargs: calls.append(args)
    )

    orchestrator._execute_unique_tasks_unified([], {}, status)

    assert len(calls) == 1


def test_fill_missing_results_marks_and_checkpoints_errors():
    note = SimpleNamespace(note_id=7)
    orchestrator = _make_orchestrator({7: note})
    status = _Status()
    checkpoint = MagicMock()
    cache = {}

    filled = orchestrator._fill_missing_results(
        [{"note_id": 7}], {"dedup-key": [0]}, cache, status, checkpoint
    )

    assert filled == 1
    assert cache["dedup-key"][0] is None
    assert 7 in status.errors
    checkpoint.mark_error.assert_called_once()
