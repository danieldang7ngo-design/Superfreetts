"""
Unit tests for batch_state_manager — BatchStateCheckpoint, BatchStateManager, singletons.
Zero Anki dependency: state_dir always points to tmp_path.
"""

import os
import json
import time
import threading

import pytest

from superfreetts_addon.batch_state_manager import (
    BatchStateCheckpoint,
    BatchStateManager,
    get_batch_state_manager,
    reset_batch_state_manager,
)


# ─────────────────────────────────────────────────────────────
# BatchStateCheckpoint
# ─────────────────────────────────────────────────────────────

class TestBatchStateCheckpoint:

    def test_to_dict_round_trip(self):
        """to_dict → from_dict preserves all fields."""
        original = BatchStateCheckpoint(
            batch_name="my_batch",
            note_id_list=[10, 20, 30],
            completed_indices=[0, 2],
            errors={"1": "timeout"},
        )
        data = original.to_dict()
        restored = BatchStateCheckpoint.from_dict(data)

        assert restored.batch_name == "my_batch"
        assert restored.note_id_list == [10, 20, 30]
        assert restored.completed_indices == [0, 2]
        assert restored.errors == {"1": "timeout"}
        assert restored.version == 1

    def test_from_dict_defaults_on_missing_keys(self):
        """from_dict should not raise when keys are missing — use safe defaults."""
        checkpoint = BatchStateCheckpoint.from_dict({})
        assert checkpoint.batch_name == "unknown"
        assert checkpoint.note_id_list == []
        assert checkpoint.completed_indices == []
        assert checkpoint.errors == {}

    def test_get_pending_notes_all_pending(self):
        """No completed notes → all note_ids returned as pending."""
        cp = BatchStateCheckpoint(
            batch_name="b",
            note_id_list=[1, 2, 3],
            completed_indices=[],
            errors={},
        )
        assert cp.get_pending_notes() == [1, 2, 3]

    def test_get_pending_notes_partial(self):
        """Some completed → only pending note_ids returned."""
        cp = BatchStateCheckpoint(
            batch_name="b",
            note_id_list=[10, 20, 30, 40],
            completed_indices=[0, 2],   # indices 0 and 2 done → notes 10, 30 done
            errors={},
        )
        assert cp.get_pending_notes() == [20, 40]

    def test_get_pending_notes_all_done(self):
        """All completed → empty list."""
        cp = BatchStateCheckpoint(
            batch_name="b",
            note_id_list=[5, 6, 7],
            completed_indices=[0, 1, 2],
            errors={},
        )
        assert cp.get_pending_notes() == []

    def test_to_dict_contains_timestamp_and_version(self):
        """Serialised dict must include timestamp and version for future migrations."""
        cp = BatchStateCheckpoint("b", [1], [], {})
        d = cp.to_dict()
        assert "timestamp" in d
        assert d["version"] == 1


# ─────────────────────────────────────────────────────────────
# BatchStateManager
# ─────────────────────────────────────────────────────────────

@pytest.fixture()
def state_mgr(tmp_path):
    """Isolated BatchStateManager that writes to a tmp directory."""
    return BatchStateManager(state_dir=str(tmp_path / "batch_state"))


class TestBatchStateManager:

    def test_save_and_load_round_trip(self, state_mgr):
        """A saved checkpoint can be loaded and equals the original."""
        cp = BatchStateCheckpoint(
            batch_name="test_batch",
            note_id_list=[1, 2, 3],
            completed_indices=[0],
            errors={},
        )
        state_mgr.save_checkpoint(cp)
        loaded = state_mgr.load_checkpoint("test_batch")

        assert loaded is not None
        assert loaded.batch_name == "test_batch"
        assert loaded.note_id_list == [1, 2, 3]
        assert loaded.completed_indices == [0]

    def test_load_nonexistent_returns_none(self, state_mgr):
        """Loading a batch that was never saved returns None."""
        assert state_mgr.load_checkpoint("does_not_exist") is None

    def test_update_progress_adds_completed_index(self, state_mgr):
        """update_progress appends the index to completed_indices."""
        # First, save a starting checkpoint
        cp = BatchStateCheckpoint("b", [10, 20, 30], [], {})
        state_mgr.save_checkpoint(cp)

        state_mgr.update_progress("b", completed_index=1)
        loaded = state_mgr.load_checkpoint("b")

        assert 1 in loaded.completed_indices

    def test_update_progress_records_error(self, state_mgr):
        """update_progress with an error string stores it in errors dict."""
        cp = BatchStateCheckpoint("b", [10, 20], [], {})
        state_mgr.save_checkpoint(cp)

        state_mgr.update_progress("b", completed_index=0, error="network timeout")
        loaded = state_mgr.load_checkpoint("b")

        assert "0" in loaded.errors
        assert "network timeout" in loaded.errors["0"]

    def test_update_progress_no_op_when_no_checkpoint(self, state_mgr):
        """update_progress silently does nothing if no existing checkpoint."""
        # Should not raise
        state_mgr.update_progress("nonexistent_batch", completed_index=0)

    def test_mark_batch_complete_removes_file(self, state_mgr):
        """mark_batch_complete deletes the checkpoint file from disk."""
        cp = BatchStateCheckpoint("b", [1, 2], [0, 1], {})
        state_mgr.save_checkpoint(cp)

        # Verify file exists
        assert state_mgr.load_checkpoint("b") is not None

        state_mgr.mark_batch_complete("b")
        assert state_mgr.load_checkpoint("b") is None

    def test_mark_batch_complete_nonexistent_no_error(self, state_mgr):
        """mark_batch_complete on missing batch should not raise."""
        state_mgr.mark_batch_complete("ghost_batch")  # should not raise

    def test_get_pending_notes_with_checkpoint(self, state_mgr):
        """get_pending_notes returns notes whose index is not in completed list."""
        note_ids = [100, 200, 300]
        cp = BatchStateCheckpoint("b", note_ids, [0, 2], {})  # notes 100, 300 done
        state_mgr.save_checkpoint(cp)

        pending = state_mgr.get_pending_notes("b", note_ids)
        assert pending == [200]

    def test_get_pending_notes_no_checkpoint_returns_all(self, state_mgr):
        """With no saved checkpoint, all notes are returned as pending."""
        note_ids = [1, 2, 3]
        pending = state_mgr.get_pending_notes("fresh_batch", note_ids)
        assert pending == note_ids

    def test_checkpoint_path_sanitizes_special_characters(self, state_mgr):
        """Batch names with special chars are sanitized to safe filenames."""
        cp = BatchStateCheckpoint("my batch/with:special*chars!", [1], [], {})
        state_mgr.save_checkpoint(cp)

        # File should exist in state dir (sanitized name)
        files = os.listdir(state_mgr.state_dir)
        assert any(f.endswith(".checkpoint.json") for f in files)

    def test_cleanup_old_files_removes_stale(self, state_mgr):
        """cleanup_old_state_files removes checkpoints older than max_age_days."""
        # Save a checkpoint
        cp = BatchStateCheckpoint("stale_batch", [1], [], {})
        state_mgr.save_checkpoint(cp)

        # Manually backdate the file's mtime by 10 days
        checkpoint_path = state_mgr._get_checkpoint_path("stale_batch")
        old_time = time.time() - (10 * 86400)
        os.utime(checkpoint_path, (old_time, old_time))

        # Save a fresh checkpoint (won't be removed)
        fresh = BatchStateCheckpoint("fresh_batch", [2], [], {})
        state_mgr.save_checkpoint(fresh)

        state_mgr.cleanup_old_state_files(max_age_days=7)

        assert state_mgr.load_checkpoint("stale_batch") is None
        assert state_mgr.load_checkpoint("fresh_batch") is not None

    def test_cleanup_keeps_recent_files(self, state_mgr):
        """cleanup_old_state_files preserves files younger than max_age_days."""
        cp = BatchStateCheckpoint("recent_batch", [1], [], {})
        state_mgr.save_checkpoint(cp)

        state_mgr.cleanup_old_state_files(max_age_days=30)

        assert state_mgr.load_checkpoint("recent_batch") is not None

    def test_thread_safety_concurrent_updates(self, tmp_path):
        """Concurrent update_progress calls from multiple threads must not corrupt state."""
        mgr = BatchStateManager(state_dir=str(tmp_path / "concurrent"))
        note_ids = list(range(20))
        cp = BatchStateCheckpoint("concurrent", note_ids, [], {})
        mgr.save_checkpoint(cp)

        errors = []

        def update(idx):
            try:
                mgr.update_progress("concurrent", completed_index=idx)
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=update, args=(i,)) for i in range(20)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert errors == [], f"Thread errors: {errors}"
        # At least some progress was recorded
        loaded = mgr.load_checkpoint("concurrent")
        assert loaded is not None
        assert len(loaded.completed_indices) > 0


# ─────────────────────────────────────────────────────────────
# Singleton helpers
# ─────────────────────────────────────────────────────────────

class TestBatchStateManagerSingleton:

    def setup_method(self):
        """Reset singleton before each test."""
        reset_batch_state_manager()

    def teardown_method(self):
        """Clean up singleton after each test."""
        reset_batch_state_manager()

    def test_get_returns_same_instance(self):
        """Calling get_batch_state_manager() twice returns the same object."""
        a = get_batch_state_manager()
        b = get_batch_state_manager()
        assert a is b

    def test_reset_clears_singleton(self):
        """reset_batch_state_manager() causes next get to return a new instance."""
        a = get_batch_state_manager()
        reset_batch_state_manager()
        b = get_batch_state_manager()
        assert a is not b
