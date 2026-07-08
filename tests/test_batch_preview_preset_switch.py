"""
Tests for batch preview preset switch cache invalidation fix.

Tests the fix for: "Batch Preview Board Shows Wrong Source/Processed Text After Preset Change"
- Primary fix: invalidate_all() clears cache on preset switch
- Secondary fix: generation counter guards against in-flight stale responses
"""

import sys
import pytest
from unittest.mock import MagicMock, patch, call

# Setup mock Anki/Qt before importing components
from . import mock_anki
mock_anki.mock_all()

from superfreetts_addon.component_batch_preview import BatchPreviewTableModel, BatchPreview
from superfreetts_addon import batch_status, config_models, constants


# ─────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────

def make_mock_hypertts():
    """Create a mock HyperTTS instance with minimal required methods."""
    mock_hypertts = MagicMock()
    mock_hypertts.get_ui_language.return_value = "en"
    mock_hypertts.populate_batch_status_processed_text = MagicMock()
    mock_hypertts.anki_utils = MagicMock()
    mock_hypertts.anki_utils.run_on_main = MagicMock(side_effect=lambda fn: fn())
    return mock_hypertts


def make_batch_status_with_notes(hypertts, note_ids, fields_map=None):
    """Create a BatchStatus with mocked notes.
    
    Args:
        hypertts: Mock HyperTTS instance
        note_ids: List of note IDs
        fields_map: Dict mapping note_id -> fields (for resolving source text)
    """
    if fields_map is None:
        fields_map = {note_id: {f"field_{i}": f"Text for note {note_id}"} for note_id, i in zip(note_ids, range(len(note_ids)))}
    
    bs = batch_status.BatchStatus(hypertts.anki_utils, note_ids, MagicMock())
    
    # Initialize note_status_map with NoteStatus objects
    for note_id in note_ids:
        bs.note_status_map[note_id] = batch_status.NoteStatus(note_id)
    
    # Ensure note_id_map is set up (maps note_id to position in note_id_list)
    bs.note_id_map = {note_id: idx for idx, note_id in enumerate(note_ids)}
    
    return bs


def make_source_model(field_name):
    """Create a BatchSource pointing to a specific field."""
    source = config_models.BatchSource(
        mode=constants.BatchMode.simple,
        source_field=field_name,
        use_selection=False
    )
    return source


def make_text_processing_model(rule_name=None):
    """Create a TextProcessing model."""
    tp = config_models.TextProcessing()
    if rule_name:
        # Apply a named rule to identify this processing variant
        tp.preset_name = rule_name
    return tp


def make_batch_model(source, text_processing=None):
    """Create a minimal BatchModel for preset switching."""
    model = MagicMock()
    model.source = source
    model.text_processing = text_processing or make_text_processing_model()
    return model


# ─────────────────────────────────────────────────────────────
# Tests
# ─────────────────────────────────────────────────────────────

class TestBatchPreviewPresetSwitch:
    """Test batch preview cache invalidation on preset switch."""

    def test_invalidate_all_clears_loaded_pages(self):
        """invalidate_all() should clear loaded_pages and loading_pages."""
        mock_hypertts = make_mock_hypertts()
        note_ids = [1, 2, 3, 4, 5]
        bs = make_batch_status_with_notes(mock_hypertts, note_ids)
        
        table_model = BatchPreviewTableModel(bs, mock_hypertts)
        
        # Simulate loading page 0
        table_model.loaded_pages.add(0)
        table_model.loading_pages.add(1)
        table_model.loaded_note_ids = [1, 2]
        
        # Verify state before invalidation
        assert 0 in table_model.loaded_pages
        assert 1 in table_model.loading_pages
        
        # Call invalidate_all (table_view is None, so it falls back to load_page(0))
        with patch.object(table_model, 'load_page'):
            table_model.invalidate_all()
        
        # Verify all caches cleared
        assert len(table_model.loaded_pages) == 0
        assert len(table_model.loading_pages) == 0
        assert table_model.loaded_note_ids == []
        assert table_model.is_loading is False

    def test_invalidate_all_increments_generation(self):
        """invalidate_all() should increment generation counter."""
        mock_hypertts = make_mock_hypertts()
        note_ids = [1, 2, 3]
        bs = make_batch_status_with_notes(mock_hypertts, note_ids)
        
        table_model = BatchPreviewTableModel(bs, mock_hypertts)
        initial_gen = table_model.generation
        
        with patch.object(table_model, 'load_page'):
            table_model.invalidate_all()
        
        assert table_model.generation == initial_gen + 1

    def test_repro_preset_switch_clears_cache(self):
        """Repro test: switching presets should clear stale text from previous preset.
        
        Steps:
        1. Load Preset A (field="Front") into table, fetch page 0
        2. Verify source_text reflects Preset A's field
        3. Switch to Preset B (field="Back")
        4. Verify loaded_pages was cleared and generation bumped
        5. After new fetch completes, verify text reflects Preset B's field
        """
        mock_hypertts = make_mock_hypertts()
        note_ids = [1, 2]
        
        # Create NoteStatus for each note
        bs = make_batch_status_with_notes(mock_hypertts, note_ids)
        
        table_model = BatchPreviewTableModel(bs, mock_hypertts)
        
        # === Step 1: Load Preset A ===
        preset_a_source = make_source_model("Front")
        preset_a_model = make_batch_model(preset_a_source)
        
        # Mock BatchPreview context to load the model
        table_model.batch_status.source_model = preset_a_source
        
        # Simulate page 0 load for Preset A: mark as loaded and set text
        table_model.loaded_pages.add(0)
        bs.note_status_map[1].source_text = "Front field text (Preset A)"
        bs.note_status_map[2].source_text = "Front field text (Preset A)"
        
        # === Step 2: Verify Preset A text is visible ===
        assert bs.note_status_map[1].source_text == "Front field text (Preset A)"
        
        # === Step 3: Switch to Preset B ===
        gen_before = table_model.generation
        preset_b_source = make_source_model("Back")
        preset_b_model = make_batch_model(preset_b_source)
        
        with patch.object(table_model, 'load_page') as mock_load_page:
            table_model.invalidate_all()
        
        # === Step 4: Verify cache cleared and generation bumped ===
        assert table_model.generation == gen_before + 1
        assert len(table_model.loaded_pages) == 0
        # load_page(0) should be called by invalidate_all when table_view is None
        mock_load_page.assert_called()
        
        # === Step 5: Simulate new fetch under Preset B completing ===
        # Update notes to reflect Preset B's text
        bs.note_status_map[1].source_text = "Back field text (Preset B)"
        bs.note_status_map[2].source_text = "Back field text (Preset B)"
        
        # Call _on_page_processed with correct generation
        table_model._on_page_processed(None, 0, table_model.generation)
        
        # Verify text now reflects Preset B
        assert bs.note_status_map[1].source_text == "Back field text (Preset B)"
        assert 0 in table_model.loaded_pages

    def test_generation_guard_discards_stale_response(self):
        """Stale in-flight response from old preset should be discarded.
        
        Steps:
        1. Start a page fetch under Preset A (generation 1)
        2. Switch to Preset B before fetch completes (generation increments to 2)
        3. Deliver the (stale) Preset-A fetch callback with generation=1
        4. Verify it is discarded and page is NOT marked loaded
        5. Verify a new fetch will pick it up for Preset B
        """
        mock_hypertts = make_mock_hypertts()
        note_ids = [1, 2, 3, 4, 5]
        bs = make_batch_status_with_notes(mock_hypertts, note_ids)
        
        table_model = BatchPreviewTableModel(bs, mock_hypertts)
        
        # === Step 1: Load page 0 under generation 1 ===
        gen_1 = table_model.generation  # Should be 0 initially
        table_model.loading_pages.add(0)
        
        # === Step 2: Switch presets (invalidate_all increments generation) ===
        with patch.object(table_model, 'load_page'):
            table_model.invalidate_all()
        gen_2 = table_model.generation  # Should be 1 now
        assert gen_2 == gen_1 + 1
        
        # === Step 3: Deliver stale response with old generation ===
        table_model.loading_pages.add(0)  # Re-add to simulate in-flight fetch
        table_model._on_page_processed(None, 0, gen_1)  # Use OLD generation
        
        # === Step 4: Verify stale response discarded ===
        # Page should NOT be in loaded_pages
        assert 0 not in table_model.loaded_pages
        # loading_pages should be empty (discarded)
        assert 0 not in table_model.loading_pages
        
        # === Step 5: Verify new fetch will load the page ===
        table_model.loading_pages.add(0)  # Simulate new fetch for page 0
        table_model._on_page_processed(None, 0, gen_2)  # Use CURRENT generation
        
        # Now page should be marked loaded
        assert 0 in table_model.loaded_pages

    def test_generation_guard_on_failure_callback(self):
        """Stale failure response from old preset should be discarded (same as success)."""
        mock_hypertts = make_mock_hypertts()
        note_ids = [1, 2]
        bs = make_batch_status_with_notes(mock_hypertts, note_ids)
        
        table_model = BatchPreviewTableModel(bs, mock_hypertts)
        
        gen_1 = table_model.generation
        table_model.loading_pages.add(0)
        
        # Switch presets
        with patch.object(table_model, 'load_page'):
            table_model.invalidate_all()
        gen_2 = table_model.generation
        
        # Deliver stale failure with old generation
        table_model.loading_pages.add(0)
        table_model._on_page_failed(Exception("old fetch failed"), 0, gen_1)
        
        # Verify page not marked loaded and loading_pages cleared
        assert 0 not in table_model.loaded_pages
        assert 0 not in table_model.loading_pages
        
        # Deliver new failure with current generation
        table_model.loading_pages.add(0)
        table_model._on_page_failed(Exception("new fetch failed"), 0, gen_2)
        
        # This time it should be processed (page removed from loading_pages)
        assert 0 not in table_model.loading_pages

    def test_batch_preview_load_model_calls_invalidate_all(self):
        """BatchPreview.load_model() should call invalidate_all() instead of load_page(0)."""
        mock_hypertts = make_mock_hypertts()
        note_ids = [1, 2, 3]
        bs = make_batch_status_with_notes(mock_hypertts, note_ids)
        
        # Create a minimal BatchPreview instance
        dialog_mock = MagicMock()
        batch_preview = BatchPreview(
            mock_hypertts,
            dialog_mock,
            note_ids,
            MagicMock(),  # sample_selection_fn
            MagicMock(),  # batch_start_fn
            MagicMock(),  # batch_end_fn
        )
        
        # Mock the table model's methods
        with patch.object(batch_preview.batch_preview_table_model, 'invalidate_all') as mock_invalidate:
            # Create a dummy model and load it
            source = make_source_model("SomeField")
            model = make_batch_model(source)
            
            batch_preview.load_model(model)
            
            # Verify invalidate_all was called
            mock_invalidate.assert_called_once()

    def test_multi_page_invalidation(self):
        """Invalidation should handle multi-page batches correctly.
        
        Steps:
        1. Batch with >100 notes, load pages 0 and 1 under Preset A
        2. Mark both as loaded
        3. Switch to Preset B via invalidate_all
        4. Verify both pages cleared and will be re-requested
        """
        mock_hypertts = make_mock_hypertts()
        # Create batch with 250 notes (3 pages of 100)
        note_ids = list(range(1, 251))
        bs = make_batch_status_with_notes(mock_hypertts, note_ids)
        
        table_model = BatchPreviewTableModel(bs, mock_hypertts)
        table_model.page_size = 100
        
        # Load pages 0 and 1 under Preset A
        table_model.loaded_pages.add(0)
        table_model.loaded_pages.add(1)
        table_model.loaded_note_ids = list(range(1, 201))  # First 200 notes
        
        # Verify state before invalidation
        assert len(table_model.loaded_pages) == 2
        
        # Invalidate for Preset B
        with patch.object(table_model, 'load_page') as mock_load_page:
            table_model.invalidate_all()
        
        # Verify all pages cleared
        assert len(table_model.loaded_pages) == 0
        assert table_model.loaded_note_ids == []
        
        # Verify load_page was called to re-request visible pages
        mock_load_page.assert_called()

    def test_table_view_none_fallback(self):
        """invalidate_all() should fall back to load_page(0) when table_view is None."""
        mock_hypertts = make_mock_hypertts()
        note_ids = [1, 2, 3]
        bs = make_batch_status_with_notes(mock_hypertts, note_ids)
        
        table_model = BatchPreviewTableModel(bs, mock_hypertts)
        table_model.table_view = None  # Simulate not-yet-drawn dialog
        
        with patch.object(table_model, 'load_page') as mock_load_page:
            table_model.invalidate_all()
        
        # Should fall back to load_page(0)
        mock_load_page.assert_called_with(0)

    def test_table_view_load_visible_pages(self):
        """invalidate_all() should call _load_visible_pages() when table_view exists."""
        mock_hypertts = make_mock_hypertts()
        note_ids = [1, 2, 3, 4, 5]
        bs = make_batch_status_with_notes(mock_hypertts, note_ids)
        
        table_model = BatchPreviewTableModel(bs, mock_hypertts)
        
        # Create a mock table_view
        table_model.table_view = MagicMock()
        table_model.table_view.viewport.return_value = MagicMock()
        table_model.table_view.rowAt.side_effect = [0, 2]  # First visible row, last visible row
        
        with patch.object(table_model, '_load_visible_pages') as mock_load_visible:
            table_model.invalidate_all()
        
        # Should call _load_visible_pages when table_view is set
        mock_load_visible.assert_called_once()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
