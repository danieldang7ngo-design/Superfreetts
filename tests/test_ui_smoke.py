"""UI smoke tests: build the main dialogs/pages against a fake Qt.

The rest of the suite tests models and helpers directly.  Nothing built the
actual widgets, so a typo in a page (a renamed attribute, a missing signal
argument, a button wired to a method that no longer exists) only surfaced when
a user opened the add-on.  These tests instantiate every main page in mock
mode, call ``draw()`` and assert on what the user would see: button labels,
enabled/checked state, combo box contents and model synchronisation.

``tests.qt_stub`` supplies the widget layer (see its docstring); every
assertion below is against that layer's real state, not a ``MagicMock``.
"""

import types
from unittest.mock import MagicMock

import pytest

from superfreetts_addon import component_about
from superfreetts_addon import component_presetmappingrules
from superfreetts_addon import component_realtime_side
from superfreetts_addon import component_services
from superfreetts_addon import component_settings
from superfreetts_addon import component_shortcuts
from superfreetts_addon import component_source
from superfreetts_addon import component_target
from superfreetts_addon import component_text_processing
from superfreetts_addon import component_voiceselection
from superfreetts_addon import config_models
from superfreetts_addon import constants
from superfreetts_addon import i18n
from superfreetts_addon import version
from superfreetts_addon.languages import AudioLanguage
from superfreetts_addon.voice import TtsVoice_v3

from . import qt_stub


# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #


class FakeService:
    """A service descriptor shaped like ``ServiceBase`` for the services page."""

    def __init__(self, name, fee="free", kind="tts", options=None, advanced=None, enabled=True):
        self.name = name
        self.service_fee = types.SimpleNamespace(name=fee)
        self.service_type = types.SimpleNamespace(name=kind)
        self.enabled = enabled
        self._options = options or {}
        self._advanced = advanced or {}

    def configuration_options(self):
        return self._options

    def advanced_configuration_options(self):
        return self._advanced


def _voice(name, service="EdgeTTS", audio_language=AudioLanguage.en_US, gender=constants.Gender.Female):
    return TtsVoice_v3(
        name=name,
        voice_key={"id": name.lower()},
        options={},
        service=service,
        gender=gender,
        audio_languages=[audio_language],
        service_fee=constants.ServiceFee.free,
    )


@pytest.fixture
def qt(monkeypatch):
    return qt_stub.install(monkeypatch)


@pytest.fixture
def hypertts():
    hypertts = MagicMock()
    hypertts.get_ui_language.return_value = "en"
    hypertts.anki_utils.wire_typing_timer.return_value = types.SimpleNamespace(enabled=True)
    hypertts.anki_utils.run_on_main.side_effect = lambda callback, *a, **k: callback(*a, **k)
    hypertts.service_manager.get_all_services.return_value = [
        FakeService(
            "EdgeTTS",
            options={
                "api_key": str,
                "concurrency_workers": int,
                "timeout": float,
                "use_ssml": bool,
                "voice_style": ["neutral", "cheerful"],
            },
            advanced={"max_retries": ("number", "Retry attempts", 3, 0, 5), "debug_logging": ("bool", "Debug", False)},
        ),
        FakeService("PiperTTS", options={"executable_path": ("file", "Piper executable", "*.exe")}),
        FakeService("Duden", kind="dictionary"),
    ]
    hypertts.service_manager.full_voice_list.return_value = [
        _voice("aria"),
        _voice("guy", gender=constants.Gender.Male),
        _voice("thorsten", service="Piper", audio_language=AudioLanguage.de_DE, gender=constants.Gender.Male),
    ]
    return hypertts


# --------------------------------------------------------------------------- #
# Batch source
# --------------------------------------------------------------------------- #


@pytest.mark.unit
def test_batch_source_draws_mode_and_field_pickers(qt, hypertts):
    changes = MagicMock()
    source = component_source.BatchSource(hypertts, ["Front", "Back"], changes)
    widget = source.draw()

    assert isinstance(widget, qt_stub.ScrollArea)
    assert source.batch_mode_combobox.items() == [mode.name for mode in constants.BatchMode]
    assert source.source_field_combobox.items() == ["Front", "Back"]
    assert source.source_field_combobox.currentText() == "Front"


@pytest.mark.unit
def test_batch_source_builds_a_model_for_the_selected_field(qt, hypertts):
    source = component_source.BatchSource(hypertts, ["Front", "Back"], MagicMock())
    source.draw()

    source.source_field_combobox.setCurrentIndex(1)

    model = source.get_model()
    assert model.mode == constants.BatchMode.simple
    assert model.source_field == "Back"


@pytest.mark.unit
def test_batch_source_switching_mode_swaps_the_config_stack(qt, hypertts):
    source = component_source.BatchSource(hypertts, ["Front"], MagicMock())
    source.draw()
    assert source.source_config_stack.currentIndex() == 0

    source.batch_mode_combobox.setCurrentText(constants.BatchMode.template.name)

    assert source.source_config_stack.currentIndex() == 1
    assert source.get_model().mode == constants.BatchMode.template


@pytest.mark.unit
def test_batch_source_load_model_restores_template_mode(qt, hypertts):
    source = component_source.BatchSource(hypertts, ["Front"], MagicMock())
    source.draw()
    model = config_models.BatchSource(constants.BatchMode.advanced_template)
    model.source_template = "{{Front}}"

    source.load_model(model)

    assert source.batch_mode_combobox.currentText() == constants.BatchMode.advanced_template.name
    assert source.advanced_template_input.toPlainText() == "{{Front}}"
    assert source.source_config_stack.currentIndex() == 2


# --------------------------------------------------------------------------- #
# Batch target
# --------------------------------------------------------------------------- #


@pytest.mark.unit
def test_batch_target_offers_every_field_and_both_tag_modes(qt, hypertts):
    target = component_target.BatchTarget(hypertts, ["Front", "Back"], MagicMock())
    target.draw()

    assert target.target_field_combobox.items() == ["Front", "Back"]
    assert target.radio_button_sound_only.text() == "Sound Tag only"
    assert target.radio_button_text_sound.text() == "Text and Sound Tag"


@pytest.mark.unit
def test_batch_target_load_model_syncs_radios_and_field(qt, hypertts):
    target = component_target.BatchTarget(hypertts, ["Front", "Back"], MagicMock())
    target.draw()
    model = config_models.BatchTarget()
    model.target_field = "Back"
    model.text_and_sound_tag = True
    model.remove_sound_tag = True

    target.load_model(model)

    assert target.target_field_combobox.currentText() == "Back"
    assert target.radio_button_text_sound.isChecked() is True
    assert target.radio_button_sound_only.isChecked() is False
    assert target.radio_button_remove_sound.isChecked() is True
    assert target.get_model().target_field == "Back"


# --------------------------------------------------------------------------- #
# Text processing
# --------------------------------------------------------------------------- #


@pytest.mark.unit
def test_text_processing_draws_every_rule_checkbox(qt, hypertts):
    processing = component_text_processing.TextProcessing(hypertts, MagicMock())
    widget = processing.draw()

    assert isinstance(widget, qt_stub.ScrollArea)
    assert processing.enabled_checkbox.text() == i18n.get_text("tp_check_enabled", "en")
    assert processing.html_to_text_line_checkbox.text() == i18n.get_text("tp_check_html", "en")
    assert processing.strip_brackets_checkbox.text() == i18n.get_text("tp_check_brackets", "en")
    assert processing.table_view.isEnabled() is True


@pytest.mark.unit
def test_text_processing_disables_controls_when_the_feature_is_off(qt, hypertts):
    processing = component_text_processing.TextProcessing(hypertts, MagicMock())
    processing.draw()
    model = config_models.TextProcessing()
    model.enabled = False

    processing.load_model(model)

    assert processing.enabled_checkbox.isChecked() is False
    assert processing.html_to_text_line_checkbox.isEnabled() is False
    assert processing.table_view.isEnabled() is False


@pytest.mark.unit
def test_text_processing_preview_updates_the_transformed_label(qt, hypertts):
    processing = component_text_processing.TextProcessing(hypertts, MagicMock())
    processing.draw()
    model = config_models.TextProcessing()
    model.enabled = True
    model.strip_brackets = True
    processing.load_model(model)

    processing.sample_text_input.setText("hello [world]")
    processing.update_transformed_text()

    assert processing.sample_text_transformed_label.text() != i18n.get_text("tp_blank_text", "en")


@pytest.mark.unit
def test_text_processing_add_and_remove_rule_buttons_touch_the_model(qt, hypertts):
    processing = component_text_processing.TextProcessing(hypertts, MagicMock())
    processing.draw()
    model = config_models.TextProcessing()
    model.enabled = True
    processing.load_model(model)

    processing.add_replace_simple_button.pressed.emit()

    assert len(processing.get_model().text_replacement_rules) == 1
    assert processing.textReplacementTableModel.rowCount(None) == 1

    # Simulate the row being selected, then press remove.
    processing.table_view._selection_indexes = [types.SimpleNamespace(row=lambda: 0)]
    processing.remove_replace_button.pressed.emit()

    assert processing.get_model().text_replacement_rules == []
    assert processing.textReplacementTableModel.rowCount(None) == 0


# --------------------------------------------------------------------------- #
# About page
# --------------------------------------------------------------------------- #


@pytest.mark.unit
def test_about_page_draws_hero_info_and_footer(qt, hypertts):
    page = component_about.AboutPage(hypertts)
    layout = qt.QVBoxLayout()

    page.draw(layout)

    container = layout.itemAt(0).widget()
    page_layout = container.layout()
    assert page_layout.count() == 5  # hero, info, actions, footer, stretch
    footer = page_layout.itemAt(3).widget()
    assert footer.text() == i18n.get_text("about_footer", "en")
    assert footer.wordWrap() is True


@pytest.mark.unit
def test_about_page_lists_every_contact_with_a_url(qt, hypertts):
    page = component_about.AboutPage(hypertts)

    assert len(page.INFO_ITEMS) == 4
    assert [item["label_key"] for item in page.INFO_ITEMS] == [
        "about_author",
        "about_contributor",
        "about_website",
        "about_github",
    ]
    assert all(item["url"].startswith("https://") for item in page.INFO_ITEMS)


def _all_labels(widget):
    """Collect every QLabel reachable from a widget/layout tree."""
    found = []

    def walk_layout(layout):
        for index in range(layout.count()):
            item = layout.itemAt(index)
            child = item.widget()
            if child is not None and hasattr(child, "text"):
                found.append(child)
            nested = item.layout()
            if nested is None and child is not None and child.layout() is not None:
                nested = child.layout()
            if nested is not None:
                walk_layout(nested)

    if widget.layout() is not None:
        walk_layout(widget.layout())
    return found


@pytest.mark.unit
def test_about_page_shows_the_running_version(qt, hypertts):
    page = component_about.AboutPage(hypertts)

    card = page._build_hero_card("en", page._get_palette(False))

    assert any(version.ANKI_SUPER_FREE_TTS_VERSION in label.text() for label in _all_labels(card))


# --------------------------------------------------------------------------- #
# Shortcuts
# --------------------------------------------------------------------------- #


@pytest.mark.unit
def test_shortcuts_draws_two_groups_and_a_restart_note(qt, hypertts):
    section = component_shortcuts.ShortcutsSection(hypertts, MagicMock(), MagicMock())
    widget = section.draw()

    assert isinstance(widget, qt_stub.Widget)
    assert section.groupbox_add_audio.title() == i18n.get_text("shortcuts_group_add_audio", "en")
    assert section.groupbox_preview_audio.title() == i18n.get_text("shortcuts_group_preview_audio", "en")
    assert section.note_label.text() == i18n.get_text("shortcuts_note_restart", "en")


@pytest.mark.unit
def test_shortcuts_load_model_fills_the_key_editors(qt, hypertts):
    section = component_shortcuts.ShortcutsSection(hypertts, MagicMock(), MagicMock())
    section.draw()
    model = config_models.KeyboardShortcuts()
    model.shortcut_editor_add_audio = "Ctrl+Shift+A"

    section.load_model(model)

    assert section.editor_add_audio_key_sequence.keySequence().toString() == "Ctrl+Shift+A"
    assert section.editor_preview_audio_key_sequence.keySequence().toString() == ""


@pytest.mark.unit
def test_shortcuts_editing_a_sequence_updates_the_model(qt, hypertts):
    changes = MagicMock()
    section = component_shortcuts.ShortcutsSection(hypertts, MagicMock(), changes)
    section.draw()
    section.load_model(config_models.KeyboardShortcuts())

    section.editor_add_audio_key_sequence.keySequenceChanged.emit(qt.QKeySequence("Ctrl+Alt+P"))

    assert section.get_model().shortcut_editor_add_audio == "Ctrl+Alt+P"
    assert changes.call_count == 1


@pytest.mark.unit
def test_shortcuts_clear_button_empties_the_sequence(qt, hypertts):
    section = component_shortcuts.ShortcutsSection(hypertts, MagicMock(), MagicMock())
    section.draw()
    model = config_models.KeyboardShortcuts()
    model.shortcut_editor_add_audio = "Ctrl+Shift+A"
    section.load_model(model)

    section.editor_add_audio_clear_button.pressed.emit()

    assert section.get_model().shortcut_editor_add_audio is None


# --------------------------------------------------------------------------- #
# Services page
# --------------------------------------------------------------------------- #


@pytest.mark.unit
def test_services_page_draws_one_card_per_service_with_status_badges(qt, hypertts):
    page = component_services.ServicesPage(hypertts, MagicMock())
    page.load_model(config_models.Configuration())
    page.draw(qt.QVBoxLayout())

    assert sorted(page.service_card_map) == ["Duden", "EdgeTTS", "PiperTTS"]
    assert sorted(page.service_checkbox_map) == ["Duden", "EdgeTTS", "PiperTTS"]
    assert all(card.property("cssClass") == "serviceCard" for card in page.service_card_map.values())
    assert page.services_summary_label.text()


@pytest.mark.unit
def test_services_page_checkboxes_reflect_the_service_state(qt, hypertts):
    services = hypertts.service_manager.get_all_services()
    for service in services:
        service.enabled = service.name == "PiperTTS"
    page = component_services.ServicesPage(hypertts, MagicMock())
    page.load_model(config_models.Configuration())

    page.draw(qt.QVBoxLayout())

    assert page.service_checkbox_map["EdgeTTS"].isChecked() is False
    assert page.service_checkbox_map["PiperTTS"].isChecked() is True
    assert page.service_card_map["EdgeTTS"].property("cardState") == "disabled"


@pytest.mark.unit
def test_services_page_toggling_a_service_updates_the_model_and_save_button(qt, hypertts):
    for service in hypertts.service_manager.get_all_services():
        service.enabled = False
    page = component_services.ServicesPage(hypertts, MagicMock())
    page.load_model(config_models.Configuration())
    page.draw(qt.QVBoxLayout())
    assert page.save_button.isEnabled() is False

    page.service_checkbox_map["EdgeTTS"].setChecked(True)

    assert page.get_model().service_enabled["EdgeTTS"] is True
    assert page.save_button.isEnabled() is True
    assert page.service_card_map["EdgeTTS"].property("cardState") == "enabled"


@pytest.mark.unit
def test_services_page_search_hides_non_matching_cards(qt, hypertts):
    page = component_services.ServicesPage(hypertts, MagicMock())
    page.load_model(config_models.Configuration())
    page.draw(qt.QVBoxLayout())

    page.search_input.setText("piper")

    assert page.service_card_map["PiperTTS"].isVisible() is True
    assert page.service_card_map["EdgeTTS"].isVisible() is False
    assert page.service_card_map["Duden"].isVisible() is False

    page.search_input.setText("")

    assert page.service_card_map["EdgeTTS"].isVisible() is True


@pytest.mark.unit
def test_services_page_renders_every_option_widget_type(qt, hypertts):
    page = component_services.ServicesPage(hypertts, MagicMock())
    page.load_model(config_models.Configuration())
    page.draw(qt.QVBoxLayout())

    # The option widgets are not exposed by name, so assert on the model wiring
    # instead: changing one writes through to the configuration object.
    page.get_service_config_bool_change_fn(
        types.SimpleNamespace(name="EdgeTTS"), "use_ssml"
    )(2)
    page.get_service_config_int_change_fn(
        types.SimpleNamespace(name="EdgeTTS"), "concurrency_workers"
    )(5)
    page.get_service_config_float_change_fn(
        types.SimpleNamespace(name="EdgeTTS"), "timeout"
    )(2.5)
    page.get_service_config_list_change_fn(
        types.SimpleNamespace(name="EdgeTTS"), "voice_style"
    )("cheerful")

    config = page.get_model()
    assert config.get_service_configuration_key("EdgeTTS", "use_ssml") is True
    assert config.get_service_configuration_key("EdgeTTS", "concurrency_workers") == 5
    assert config.get_service_configuration_key("EdgeTTS", "timeout") == 2.5
    assert config.get_service_configuration_key("EdgeTTS", "voice_style") == "cheerful"


@pytest.mark.unit
def test_services_page_advanced_toggle_reveals_hidden_options(qt, hypertts):
    page = component_services.ServicesPage(hypertts, MagicMock())
    page.load_model(config_models.Configuration())

    layout = qt.QVBoxLayout()
    page.draw_service_advanced_options(
        types.SimpleNamespace(name="EdgeTTS"),
        layout,
        {"max_retries": ("number", "Retry attempts", 3, 0, 5)},
    )

    advanced_row = layout.itemAt(1).layout()
    advanced_button = advanced_row.itemAt(0).widget()
    advanced_widget = layout.itemAt(2).widget()
    assert advanced_button.isCheckable() is True
    assert advanced_button.isChecked() is False
    assert advanced_widget.isVisible() is False

    advanced_button.clicked.emit(True)

    assert advanced_widget.isVisible() is True
    assert advanced_widget.layout().count() == 2  # one row: label + spinbox


# --------------------------------------------------------------------------- #
# Voice selection (smoke only - behaviour is covered in its own module)
# --------------------------------------------------------------------------- #


@pytest.mark.unit
def test_voice_selection_page_builds_in_single_mode(qt, hypertts):
    hypertts.service_manager.locate_voice.side_effect = lambda voice_id: next(
        voice for voice in hypertts.service_manager.full_voice_list() if voice.voice_id == voice_id
    )
    selection = component_voiceselection.VoiceSelection(hypertts, MagicMock(), MagicMock())

    widget = selection.draw()

    assert isinstance(widget, qt_stub.ScrollArea)
    assert selection.voices_combobox.count() == 3
    assert selection.radio_button_single.isChecked() is True
    assert selection.play_sample_button.isEnabled() is False
    assert selection.get_model().voice.voice_id == selection.filtered_voice_list[0].voice_id


# --------------------------------------------------------------------------- #
# Preset mapping rules
# --------------------------------------------------------------------------- #


@pytest.mark.unit
def test_preset_mapping_rules_draw_shows_note_info_and_empty_state(qt, hypertts):
    hypertts.superfreetts_pro_enabled.return_value = False
    hypertts.anki_utils.get_note_type_name.return_value = "Basic"
    hypertts.anki_utils.get_deck_name.return_value = "Default"
    component = component_presetmappingrules.ComponentPresetMappingRules(
        hypertts,
        MagicMock(),
        config_models.DeckNoteType(deck_id=1, model_id=2),
        MagicMock(),
    )

    component.draw(qt.QVBoxLayout())

    assert component.note_type_label.text() == "Basic"
    assert component.deck_name_label.text() == "Default"
    assert component.easy_mode_checkbox.isChecked() is False
    assert component.preview_all_button.isEnabled() is False
    assert component.run_all_button.isEnabled() is False
    assert component.add_rule_button.property("cssClass") == "primaryButton"


@pytest.mark.unit
def test_preset_mapping_rules_load_model_reflects_easy_mode_and_rules(qt, hypertts):
    hypertts.superfreetts_pro_enabled.return_value = False
    hypertts.anki_utils.get_note_type_name.return_value = "Basic"
    hypertts.anki_utils.get_deck_name.return_value = "Default"
    component = component_presetmappingrules.ComponentPresetMappingRules(
        hypertts,
        MagicMock(),
        config_models.DeckNoteType(deck_id=1, model_id=2),
        MagicMock(),
    )
    component.draw(qt.QVBoxLayout())
    model = config_models.PresetMappingRules()
    model.use_easy_mode = True

    component.load_model(model)

    assert component.easy_mode_checkbox.isChecked() is True
    assert component.get_model().use_easy_mode is True
    assert component.save_button.isEnabled() is False


@pytest.mark.unit
def test_preset_mapping_rules_easy_mode_toggle_marks_the_model_changed(qt, hypertts):
    hypertts.superfreetts_pro_enabled.return_value = False
    hypertts.anki_utils.get_note_type_name.return_value = "Basic"
    hypertts.anki_utils.get_deck_name.return_value = "Default"
    component = component_presetmappingrules.ComponentPresetMappingRules(
        hypertts,
        MagicMock(),
        config_models.DeckNoteType(deck_id=1, model_id=2),
        MagicMock(),
    )
    component.draw(qt.QVBoxLayout())
    component.load_model(config_models.PresetMappingRules())

    component.easy_mode_checkbox.setChecked(True)

    assert component.get_model().use_easy_mode is True
    assert component.model_changed is True
    assert component.save_button.isEnabled() is True


# --------------------------------------------------------------------------- #
# Realtime side
# --------------------------------------------------------------------------- #


def _realtime_component(qt, hypertts):
    hypertts.card_template_has_tts_tag.return_value = None
    hypertts.get_fields_from_note.return_value = ["Front", "Back"]
    hypertts.service_manager.locate_voice.side_effect = lambda voice_id: next(
        voice for voice in hypertts.service_manager.full_voice_list() if voice.voice_id == voice_id
    )
    component = component_realtime_side.ComponentRealtimeSide(
        hypertts,
        MagicMock(),
        constants.AnkiCardSide.Front,
        0,
        MagicMock(),
        MagicMock(),
    )
    component.configure_note(MagicMock())
    return component


@pytest.mark.unit
def test_realtime_side_draw_builds_tabs_and_preview(qt, hypertts):
    component = _realtime_component(qt, hypertts)

    layout = component.draw()

    assert isinstance(layout, qt_stub.Layout)
    assert component.side_enabled_checkbox.text() == "Enable Realtime TTS for Front side"
    assert component.side_enabled_checkbox.isChecked() is False
    assert component.tabs.count() == 2
    assert component.preview_sound_button.text() == "Preview Sound"


@pytest.mark.unit
def test_realtime_side_enabling_the_checkbox_updates_the_model(qt, hypertts):
    component = _realtime_component(qt, hypertts)
    component.draw()

    component.side_enabled_checkbox.setChecked(True)

    assert component.get_model().side_enabled is True
    assert component.tabs.isEnabled() is True
    assert component.preview_groupbox.isEnabled() is True


@pytest.mark.unit
def test_realtime_side_load_model_propagates_to_the_child_components(qt, hypertts):
    component = _realtime_component(qt, hypertts)
    component.draw()
    model = config_models.RealtimeConfigSide()
    model.side_enabled = True
    model.source = config_models.RealtimeSourceAnkiTTS()
    model.source.field_name = "Front"
    model.source.field_type = types.SimpleNamespace(name="text")
    model.voice_selection = config_models.VoiceSelectionSingle()
    model.text_processing = config_models.TextProcessing()

    component.load_model(model)

    assert component.get_model() is model
    assert component.side_enabled_checkbox.isChecked() is True
    assert component.voice_selection.get_model() is model.voice_selection
    assert component.text_processing.get_model() is model.text_processing


# --------------------------------------------------------------------------- #
# Settings dialog shell
# --------------------------------------------------------------------------- #


def _settings_dialog(qt, hypertts):
    dialog = component_settings.SettingsDialog.__new__(component_settings.SettingsDialog)
    dialog.hypertts = hypertts
    dialog.initial_tab = 2
    dialog._page_buttons = []
    dialog._page_built = set()
    dialog._saved_once = False
    dialog._initial_snapshot = None
    dialog.services_page = MagicMock()
    dialog.services_page.get_model.return_value = config_models.Configuration()
    dialog.preferences_page = MagicMock()
    dialog.preferences_page.get_model.return_value = config_models.Preferences()
    for page_name in ("changes_page", "donation_page", "about_page", "usage_page"):
        setattr(dialog, page_name, MagicMock())
    for name in (
        "setUpdatesEnabled",
        "setWindowFlag",
        "setStyleSheet",
        "setMinimumSize",
        "setModal",
        "setLayout",
    ):
        setattr(dialog, name, lambda *args, **kwargs: None)
    dialog.setWindowTitle = lambda title: setattr(dialog, "_title", title)
    dialog.resize = lambda width, height: setattr(dialog, "_size", (width, height))
    dialog.findChildren = lambda *args, **kwargs: []
    dialog.style = lambda: qt_stub._Style()
    dialog.accept = MagicMock()
    dialog.reject = MagicMock()
    dialog.setupUi()
    return dialog


@pytest.mark.unit
def test_settings_dialog_builds_six_sidebar_pages(qt, hypertts):
    dialog = _settings_dialog(qt, hypertts)

    assert len(dialog._page_buttons) == 6
    assert [button.text() for button in dialog._page_buttons] == [
        i18n.get_text("tab_services", "en"),
        i18n.get_text("tab_preferences", "en"),
        i18n.get_text("tab_changes", "en"),
        i18n.get_text("tab_donation", "en"),
        i18n.get_text("tab_about", "en"),
        i18n.get_text("tab_usage", "en"),
    ]
    assert dialog.pages.count() == 6
    assert dialog.save_button.text() == i18n.get_text("button_save", "en")
    assert dialog.cancel_button.text() == i18n.get_text("button_cancel", "en")


@pytest.mark.unit
def test_settings_dialog_starts_on_the_requested_page_and_builds_it_once(qt, hypertts):
    dialog = _settings_dialog(qt, hypertts)

    assert dialog.pages.currentIndex() == 2
    assert dialog.changes_page.draw.call_count == 1
    assert dialog.services_page.draw.call_count == 0

    dialog.switch_page(0)
    dialog.switch_page(2)

    assert dialog.pages.currentIndex() == 2
    assert dialog.services_page.draw.call_count == 1
    assert dialog.changes_page.draw.call_count == 1


@pytest.mark.unit
def test_settings_dialog_marks_the_active_sidebar_button(qt, hypertts):
    dialog = _settings_dialog(qt, hypertts)

    dialog.switch_page(4)

    assert dialog._page_buttons[4].property("cssClass") == "tocButtonActive"
    assert dialog._page_buttons[2].property("cssClass") == "tocButtonInactive"


@pytest.mark.unit
def test_settings_dialog_save_writes_configuration_and_preferences(qt, hypertts):
    dialog = _settings_dialog(qt, hypertts)

    dialog.save_and_close()

    hypertts.save_configuration.assert_called_once()
    hypertts.save_preferences.assert_called_once()
    assert dialog._saved_once is True
    dialog.accept.assert_called_once()


@pytest.mark.unit
def test_settings_dialog_cancel_without_changes_closes(qt, hypertts):
    dialog = _settings_dialog(qt, hypertts)

    dialog.cancel()

    dialog.reject.assert_called_once()
    hypertts.anki_utils.ask_user.assert_not_called()
