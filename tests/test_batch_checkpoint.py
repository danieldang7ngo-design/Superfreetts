"""Checkpoint/resume tests for batch processing (audit finding P1-3).

Regression covered here: checkpoints used to store ``completed_indices`` next
to ``note_id_list``.  Resuming filtered the note list first but then wrote the
*positions in the filtered list* back as indices into the original list, so the
next resume skipped and repeated the wrong notes.
"""

import json

import pytest

from superfreetts_addon import batch_executor
from superfreetts_addon.batch_executor import (
    CHECKPOINT_STATUS_APPLIED,
    CHECKPOINT_STATUS_GENERATED,
    BatchCheckpoint,
    CheckpointManager,
    NullCheckpoint,
)


@pytest.fixture
def manager(tmp_path):
    return CheckpointManager(str(tmp_path))


def checkpoint_path(tmp_path, batch_name="batch"):
    return tmp_path / f"{batch_name}.checkpoint.json"


# ------------------------------------------------------------ CheckpointManager


@pytest.mark.unit
def test_save_load_roundtrip(manager, tmp_path):
    manager.save("batch", [101, 102], {101: CHECKPOINT_STATUS_APPLIED}, {101: "boom"})

    data = manager.load("batch")

    assert data["version"] == 2
    assert data["note_ids"] == [101, 102]
    assert data["statuses"] == {"101": CHECKPOINT_STATUS_APPLIED}
    assert data["errors"] == {"101": "boom"}
    assert not checkpoint_path(tmp_path).with_suffix(".json.tmp").exists()


@pytest.mark.unit
def test_save_is_atomic_and_keeps_previous_file_on_failure(manager, tmp_path, monkeypatch):
    manager.save("batch", [1], {1: CHECKPOINT_STATUS_GENERATED})
    before = checkpoint_path(tmp_path).read_text()

    def boom(src, dst):
        raise OSError("disk full")

    monkeypatch.setattr(batch_executor.os, "replace", boom)
    manager.save("batch", [1], {1: CHECKPOINT_STATUS_APPLIED})

    assert checkpoint_path(tmp_path).read_text() == before
    assert manager.load("batch")["statuses"] == {"1": CHECKPOINT_STATUS_GENERATED}


@pytest.mark.unit
def test_legacy_v1_checkpoint_is_migrated(manager, tmp_path):
    """Old files keyed by index must not crash or lose their notes."""
    legacy = {
        "batch_name": "old",
        "note_id_list": [10, 20, 30],
        "completed_indices": [0, 2],
        "errors": {"1": "boom"},
    }
    checkpoint_path(tmp_path, "old").write_text(json.dumps(legacy))

    data = manager.load("old")

    assert data["version"] == 2
    assert data["note_ids"] == [10, 20, 30]
    assert data["statuses"] == {"10": CHECKPOINT_STATUS_APPLIED, "30": CHECKPOINT_STATUS_APPLIED}
    assert data["errors"] == {"1": "boom"}


@pytest.mark.unit
def test_remove_deletes_file(manager, tmp_path):
    manager.save("batch", [1], {1: CHECKPOINT_STATUS_APPLIED})
    manager.remove("batch")
    assert not checkpoint_path(tmp_path).exists()
    assert manager.load("batch") is None


# --------------------------------------------------------------- BatchCheckpoint


@pytest.mark.unit
def test_resume_tracks_note_ids_not_list_positions(manager, tmp_path):
    """Kill/restart at 25/50/75% must not shift which notes are pending."""
    all_notes = list(range(1, 11))
    checkpoint = BatchCheckpoint(manager, "batch", all_notes)
    checkpoint.mark_applied([1, 2, 3, 4, 5])
    checkpoint.mark_generated([6])

    resumed = BatchCheckpoint(manager, "batch", all_notes)
    assert resumed.load_existing() == 5
    assert resumed.pending_note_ids() == [6, 7, 8, 9, 10]

    # Apply the rest and resume again: nothing left, no note applied twice.
    resumed.mark_applied([6, 7, 8, 9, 10])
    final = BatchCheckpoint(manager, "batch", all_notes)
    assert final.load_existing() == 10
    assert final.pending_note_ids() == []
    stored = manager.load("batch")
    assert set(stored["statuses"]) == {str(note_id) for note_id in all_notes}


@pytest.mark.unit
def test_resume_with_filtered_list_keeps_earlier_statuses(manager):
    """A resume that passes only pending ids must not forget applied ids."""
    checkpoint = BatchCheckpoint(manager, "batch", [1, 2, 3, 4])
    checkpoint.mark_applied([2, 4])

    filtered = BatchCheckpoint(manager, "batch", [1, 3])
    assert filtered.load_existing() == 2
    assert filtered.note_ids == [1, 3, 2, 4]
    assert filtered.pending_note_ids() == [1, 3]


@pytest.mark.unit
def test_generated_status_flushes_on_cadence(manager, tmp_path):
    checkpoint = BatchCheckpoint(manager, "batch", [1, 2, 3, 4, 5, 6], flush_every=5)

    checkpoint.mark_generated([1, 2, 3])
    assert not checkpoint_path(tmp_path).exists()

    checkpoint.mark_generated([4, 5])
    assert checkpoint_path(tmp_path).exists()
    assert manager.load("batch")["statuses"]["1"] == CHECKPOINT_STATUS_GENERATED


@pytest.mark.unit
def test_mark_applied_forces_flush_below_cadence(manager, tmp_path):
    checkpoint = BatchCheckpoint(manager, "batch", [1], flush_every=50)
    checkpoint.mark_applied([1])
    assert checkpoint_path(tmp_path).exists()
    assert manager.load("batch")["statuses"]["1"] == CHECKPOINT_STATUS_APPLIED


@pytest.mark.unit
def test_applied_status_is_never_downgraded(manager):
    checkpoint = BatchCheckpoint(manager, "batch", [1])
    checkpoint.mark_applied([1])
    checkpoint.mark_generated([1])
    assert checkpoint.is_applied(1)
    assert checkpoint.status_of(1) == CHECKPOINT_STATUS_APPLIED


@pytest.mark.unit
def test_errors_are_keyed_by_note_id_and_persist(manager):
    checkpoint = BatchCheckpoint(manager, "batch", [7])
    checkpoint.mark_error(7, RuntimeError("engine failed"))
    checkpoint.flush()

    reloaded = manager.load("batch")
    assert "engine failed" in reloaded["errors"]["7"]


@pytest.mark.unit
def test_remove_disables_later_flush(manager, tmp_path):
    checkpoint = BatchCheckpoint(manager, "batch", [1, 2])
    checkpoint.mark_applied([1])
    checkpoint.remove()

    checkpoint.mark_generated([2])
    checkpoint.flush()

    assert not checkpoint_path(tmp_path).exists()


@pytest.mark.unit
def test_null_checkpoint_is_a_noop():
    checkpoint = NullCheckpoint()
    checkpoint.mark_generated([1])
    checkpoint.mark_applied([1])
    checkpoint.mark_error(1, RuntimeError("boom"))
    checkpoint.flush()
    checkpoint.remove()
    assert checkpoint.enabled is False


# ---------------------------------------------------------- kill/resume matrix (25/50/75%)


@pytest.mark.parametrize("applied_count", [2, 5, 8])
def test_kill_resume_at_fraction_applies_only_remaining(manager, applied_count):
    all_notes = list(range(1, 11))
    applied = all_notes[:applied_count]

    # First run commits `applied_count` notes, then "crashes".
    first = BatchCheckpoint(manager, "batch", all_notes)
    first.mark_applied(applied)

    # Reopen with the same key (resume).
    resumed = BatchCheckpoint(manager, "batch", all_notes)
    assert resumed.load_existing() == applied_count
    assert resumed.pending_note_ids() == all_notes[applied_count:]

    # Apply the rest; nothing is applied twice.
    resumed.mark_applied(all_notes[applied_count:])
    final = BatchCheckpoint(manager, "batch", all_notes)
    assert final.load_existing() == len(all_notes)
    assert final.pending_note_ids() == []
    stored = manager.load("batch")
    assert set(stored["statuses"]) == {str(n) for n in all_notes}
    assert all(v == CHECKPOINT_STATUS_APPLIED for v in stored["statuses"].values())
