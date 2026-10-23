"""Preview checkpoint resume tests (handoff A+B, step B).

The live batch path is ``component_batch_preview`` (prepare -> generate ->
chunked apply).  After a crash mid-apply, reopening the same batch must skip
notes already ``applied`` without duplicating ``[sound:]`` tags.
"""

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from . import mock_anki

mock_anki.mock_all()

from superfreetts_addon.batch_executor import BatchCheckpoint, CheckpointManager
from superfreetts_addon.batch_orchestrator import preview_checkpoint_key
from superfreetts_addon.component_batch_preview import BatchPreview
import superfreetts_addon.component_batch_preview as preview_module


def patch_query_op():
    """Patch the QueryOp object as seen by component_batch_preview.

    Each test module calls ``mock_all()`` at import time, which replaces
    ``sys.modules['aqt.*']``.  Patching ``"aqt.operations.QueryOp"`` would hit
    whatever mock is current, not the module object the preview code holds.
    """
    return patch.object(preview_module.aqt.operations, "QueryOp", SyncQueryOp)


def make_target(field="Audio", text_and_sound=False, remove_sound=True):
    return SimpleNamespace(
        target_field=field,
        text_and_sound_tag=text_and_sound,
        remove_sound_tag=remove_sound,
    )


def make_model(name="preset", target=None):
    return SimpleNamespace(name=name, target=target or make_target())


def make_dedup(keys):
    return {k: [0] for k in keys}


# ---------------------------------------------------------- key stability


@pytest.mark.unit
def test_preview_key_stable_for_same_inputs():
    model = make_model()
    dedup = make_dedup(["k1", "k2"])
    assert preview_checkpoint_key(model, [1, 2, 3], dedup) == preview_checkpoint_key(
        model, [1, 2, 3], dedup
    )


@pytest.mark.unit
def test_preview_key_changes_with_target_voice_or_format():
    base_model = make_model()
    dedup_base = make_dedup(["audio-a", "audio-b"])
    base = preview_checkpoint_key(base_model, [1, 2], dedup_base)

    # Target field change (apply destination) must change the key.
    other_target = preview_checkpoint_key(make_model(target=make_target("Other")), [1, 2], dedup_base)
    assert other_target != base

    # Voice/format change shows up as different dedup keys.
    other_dedup = preview_checkpoint_key(base_model, [1, 2], make_dedup(["audio-a", "audio-C"]))
    assert other_dedup != base

    # Different note selection must change the key.
    other_notes = preview_checkpoint_key(base_model, [1, 3], dedup_base)
    assert other_notes != base


@pytest.mark.unit
def test_preview_key_does_not_depend_on_memory_address():
    # Two distinct objects with identical content must map to the same key.
    # (Regression: str(TextProcessing) used to embed "object at 0x...".)
    model_a = make_model(name="preset", target=make_target("Audio", False, True))
    model_b = make_model(name="preset", target=make_target("Audio", False, True))
    assert model_a is not model_b
    dedup = make_dedup(["k1"])
    assert preview_checkpoint_key(model_a, [5, 6], dedup) == preview_checkpoint_key(
        model_b, [5, 6], dedup
    )


# ---------------------------------------------------------- preview flow


def make_preview_hypertts(tmp_path):
    hypertts = MagicMock()
    hypertts.get_ui_language.return_value = "en"
    hypertts.executor = SimpleNamespace(checkpoint=CheckpointManager(str(tmp_path)))
    hypertts.anki_utils = MagicMock()
    hypertts.anki_utils.run_on_main.side_effect = lambda fn: fn()
    hypertts.anki_utils.get_current_time.side_effect = __import__("datetime").datetime.now
    return hypertts


def make_preview(tmp_path, note_ids, model=None):
    hypertts = make_preview_hypertts(tmp_path)
    preview = BatchPreview(
        hypertts,
        MagicMock(),
        list(note_ids),
        MagicMock(),
        MagicMock(),
        MagicMock(),
    )
    preview.batch_model = model or make_model()
    preview.generated_batch_model = preview.batch_model
    return preview, hypertts


def fake_results(note_ids):
    return [(nid, f"src {nid}", f"proc {nid}", f"s{nid}.mp3", f"/tmp/s{nid}.mp3", None) for nid in note_ids]


class SyncQueryOp:
    """Run the chunk op inline instead of on a background thread."""

    applied_calls = []

    def __init__(self, parent, op, success):
        self._op = op
        self._success = success
        self._failure = None

    def failure(self, fn):
        self._failure = fn
        return self

    def run_in_background(self):
        col = MagicMock()
        col.add_custom_undo_entry.return_value = 42
        try:
            result = self._op(col)
        except Exception as exc:  # pragma: no cover - defensive
            if self._failure is not None:
                self._failure(exc)
            return
        self._success(result)


@pytest.mark.unit
def test_preview_apply_skips_applied_and_removes_checkpoint(tmp_path):
    note_ids = [1, 2, 3, 4, 5]
    preview, hypertts = make_preview(tmp_path, note_ids)
    preview.APPLY_CHUNK_SIZE = 2

    key = preview_checkpoint_key(preview.batch_model, note_ids, make_dedup(["k"]))
    checkpoint = BatchCheckpoint(hypertts.executor.checkpoint, key, note_ids)
    checkpoint.mark_applied([1, 2])
    preview.batch_checkpoint = checkpoint

    preview.generated_batch_results = fake_results(note_ids)
    preview.batch_status.begin()

    seen = []

    def fake_apply(chunk, batch_model, batch_status, col):
        seen.extend(row[0] for row in chunk)
        return len(chunk)

    hypertts.apply_generated_batch_audio_chunk.side_effect = fake_apply
    preview.finished_apply_audio_fn = MagicMock(wraps=preview.finished_apply_audio_fn)

    with patch_query_op():
        preview._run_next_apply_chunk()

    # Notes 1-2 were already applied: only 3,4,5 go through apply.
    assert seen == [3, 4, 5]
    # After a full run the checkpoint file is removed so the next batch starts clean.
    assert hypertts.executor.checkpoint.load(key) is None
    assert preview.batch_checkpoint is None


@pytest.mark.unit
def test_preview_cancel_keeps_checkpoint_for_resume(tmp_path):
    note_ids = [1, 2, 3, 4]
    preview, hypertts = make_preview(tmp_path, note_ids)
    preview.APPLY_CHUNK_SIZE = 2

    key = preview_checkpoint_key(preview.batch_model, note_ids, make_dedup(["k"]))
    checkpoint = BatchCheckpoint(hypertts.executor.checkpoint, key, note_ids)
    checkpoint.mark_applied([1])
    preview.batch_checkpoint = checkpoint

    preview.generated_batch_results = fake_results(note_ids)
    preview.batch_status.begin()

    def fake_apply_cancel_after_first(chunk, batch_model, batch_status, col):
        # Simulate the user pressing Stop right after the first chunk commits.
        batch_status.stop()
        return len(chunk)

    hypertts.apply_generated_batch_audio_chunk.side_effect = fake_apply_cancel_after_first

    with patch_query_op():
        preview._run_next_apply_chunk()

    stored = hypertts.executor.checkpoint.load(key)
    assert stored is not None
    resumed = BatchCheckpoint(hypertts.executor.checkpoint, key, note_ids)
    assert resumed.load_existing() >= 1
    assert set(resumed.pending_note_ids()) == set(note_ids) - {
        int(k) for k, v in stored["statuses"].items() if v == "applied"
    }
