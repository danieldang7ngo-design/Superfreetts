"""
Unit tests for unsaved preset preview functionality.
"""

import pytest
import sys
import os
from unittest.mock import MagicMock, patch

addon_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, addon_dir)

from superfreetts_addon import config_models
from superfreetts_addon import constants
from superfreetts_addon import errors
from superfreetts_addon import editor_manager
from tests.conftest import MockAnkiUtils


@pytest.mark.unit
class TestPreviewUnsaved:

    def test_validate_for_preview_without_name(self):
        """Test validate_for_preview succeeds even when preset name is None."""
        anki_utils = MockAnkiUtils()
        config = config_models.BatchConfig(anki_utils)
        config.source = config_models.BatchSource(
            mode=constants.BatchMode.simple,
            source_field="Front"
        )
        config.name = None  # No preset name

        # Normal validate should fail with PresetNameNotSet
        with pytest.raises(errors.PresetNameNotSet):
            config.validate()

        # validate_for_preview should succeed without raising
        config.validate_for_preview()

    def test_preview_all_mapping_rules_with_explicit_unsaved_rules(self):
        """Test preview_all_mapping_rules does not raise NoPresetMappingRulesDefined when passed from UI."""
        mock_hypertts = MagicMock()
        mock_anki_utils = MagicMock()
        mock_hypertts.anki_utils = mock_anki_utils
        
        mgr = editor_manager.EditorManager(mock_hypertts)
        mgr.get_editor_deck_note_type = MagicMock()

        # Explicitly empty rules passed from UI (in-memory)
        empty_rules = config_models.PresetMappingRules()
        mock_editor_context = MagicMock()

        # Should not raise errors.NoPresetMappingRulesDefined
        mgr.preview_all_mapping_rules(mock_editor_context, empty_rules)
        mock_anki_utils.run_in_background.assert_called_once()


    def test_preview_all_mapping_rules_none_rules_raises(self):
        """Test preview_all_mapping_rules raises NoPresetMappingRulesDefined when loading from disk and rules are empty."""
        mock_hypertts = MagicMock()
        mock_hypertts.load_mapping_rules.return_value = config_models.PresetMappingRules()
        
        mgr = editor_manager.EditorManager(mock_hypertts)
        mock_editor_context = MagicMock()

        with pytest.raises(errors.NoPresetMappingRulesDefined):
            mgr.preview_all_mapping_rules(mock_editor_context, None)
