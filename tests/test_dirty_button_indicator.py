"""
Tests for the "dirty" button indicator (Anki Sync-button style).

When the underlying config (fields / voices / text-processing / workflow) changes,
the Generate / Run button should switch to the theme's warning (amber) color so the
user notices audio would need to be regenerated. The color comes from the active
theme's stylesheet via the ``btnPastel*`` classes, so it adapts per-theme.
"""
from unittest.mock import MagicMock

import pytest

from superfreetts_addon import gui_utils, component_batch


class StubButton:
    """Minimal QPushButton stand-in that records cssClass / enabled / tooltip."""

    def __init__(self):
        self.props = {}
        self.enabled = True
        self.tooltip = None
        self.text = None

    def setProperty(self, key, value):
        self.props[key] = value

    def setEnabled(self, value):
        self.enabled = value

    def setToolTip(self, value):
        self.tooltip = value

    def setText(self, value):
        self.text = value

    def style(self):
        return self

    def unpolish(self, widget):
        pass

    def polish(self, widget):
        pass


@pytest.mark.unit
class TestSetButtonDirty:
    def test_dirty_sets_amber_class(self):
        btn = StubButton()
        gui_utils.set_button_dirty(btn, True, normal_style="emerald")
        assert btn.props.get("cssClass") == "btnPastelAmber"

    def test_clean_returns_to_normal_style(self):
        btn = StubButton()
        gui_utils.set_button_dirty(btn, False, normal_style="emerald")
        assert btn.props.get("cssClass") == "btnPastelEmerald"

    def test_custom_dirty_style(self):
        btn = StubButton()
        gui_utils.set_button_dirty(btn, True, normal_style="emerald", dirty_style="rose")
        assert btn.props.get("cssClass") == "btnPastelRose"

    def test_amber_selector_present_in_every_theme(self):
        """The warning class used by the dirty indicator must exist in each theme."""
        for theme in gui_utils.VALID_THEMES:
            gui_utils.set_active_theme(theme)
            css = gui_utils.get_dynamic_stylesheet()
            assert 'cssClass="btnPastelAmber"' in css, f"missing amber in {theme}"


@pytest.mark.unit
class TestBatchDirtyButton:
    def _make_component(self):
        hypertts = MagicMock()
        hypertts.get_ui_language.return_value = "en"
        hypertts.anki_utils = MagicMock()
        dialog = MagicMock()
        comp = component_batch.ComponentBatch(hypertts, dialog)
        # Replace the real (mocked-Qt) button with a controllable stub.
        comp.apply_button = StubButton()
        comp.editor_mode = False
        comp.notes_loaded = True
        return comp

    def test_batch_apply_button_turns_amber_when_config_changed(self):
        comp = self._make_component()
        comp.model_changed = True
        comp.update_save_profile_button_state()
        assert comp.apply_button.props.get("cssClass") == "btnPastelAmber"
        assert comp.apply_button.enabled is True
        assert comp.apply_button.tooltip  # dirty tooltip set

    def test_batch_apply_button_returns_emerald_when_saved(self):
        comp = self._make_component()
        comp.model_changed = False
        comp.update_save_profile_button_state()
        assert comp.apply_button.props.get("cssClass") == "btnPastelEmerald"
        assert comp.apply_button.tooltip == ""

    def test_batch_editor_mode_does_not_recolor(self):
        """In editor mode the button is not a pastel button, so skip recoloring."""
        comp = self._make_component()
        comp.editor_mode = True
        comp.model_changed = True
        comp.update_save_profile_button_state()
        assert "cssClass" not in comp.apply_button.props

    def test_batch_apply_button_not_enabled_before_notes_loaded(self):
        comp = self._make_component()
        comp.notes_loaded = False
        comp.model_changed = True
        comp.update_save_profile_button_state()
        assert comp.apply_button.props.get("cssClass") == "btnPastelEmerald"