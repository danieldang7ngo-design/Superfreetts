"""Behavioural tests for the voice-selection component.

``component_voiceselection`` is the widget that decides which voice (and which
voice options) a preset stores.  Its interesting rules are all reachable
without a real Qt event loop:

* the four filter combos and their cascading repopulation,
* single / random / priority / sequence selection modes,
* adding, removing and reordering entries in the voice list,
* the per-voice options form (number, integer, list and text parameters),
* the model handed back to the batch dialog.

The fake widget layer in :mod:`tests.qt_stub` keeps real state so the
assertions below check what the user would actually see.
"""

import copy
import types
from unittest.mock import MagicMock

import pytest

from superfreetts_addon import component_voiceselection
from superfreetts_addon import config_models
from superfreetts_addon import constants
from superfreetts_addon import errors
from superfreetts_addon import i18n
from superfreetts_addon.languages import AudioLanguage
from superfreetts_addon.voice import TtsVoice_v3, TtsVoiceId_v3, voice_str

from . import qt_stub

ALL = "All"


# --------------------------------------------------------------------------- #
# fixtures
# --------------------------------------------------------------------------- #


def _voice(name, service="EdgeTTS", audio_language=AudioLanguage.en_US, gender=None, options=None):
    voice = TtsVoice_v3(
        name=name,
        voice_key={"id": name.lower()},
        options=options or {},
        service=service,
        gender=gender or constants.Gender.Female,
        audio_languages=[audio_language],
        service_fee=constants.ServiceFee.free,
    )
    if service == "Piper":
        # Real TtsVoice_v3 instances expose ``languages`` as Language enum
        # members, which have ``name``/``lang_name`` but no ``lang_code``.  The
        # Piper branch in voice_selected() must tolerate that (it used to raise
        # AttributeError).
        voice.languages = [audio_language.lang]
    return voice


PIPER_OPTIONS = {
    "length_scale": {
        "type": "number",
        "label": "Speed",
        "min": 0.5,
        "max": 2.0,
        "default": 1.0,
        "tooltip": "1.0 is normal speed",
    },
    "speaker_id": {
        "type": "number_int",
        "label": "Speaker",
        "min": 0,
        "max": 9,
        "default": 0,
    },
    "device": {
        "type": "list",
        "label": "Device",
        "values": ["cpu", "cuda"],
        "default": "cpu",
    },
    "note": {
        "type": "text",
        "label": "Note",
        "default": "",
    },
}


def build_voices():
    return [
        _voice("aria", "EdgeTTS", AudioLanguage.en_US, constants.Gender.Female),
        _voice("guy", "EdgeTTS", AudioLanguage.en_US, constants.Gender.Male),
        _voice("thorsten", "Piper", AudioLanguage.de_DE, constants.Gender.Male, copy.deepcopy(PIPER_OPTIONS)),
        _voice("kyoko", "Piper", AudioLanguage.ja_JP, constants.Gender.Female),
    ]


class FakeHyperTTS:
    def __init__(self, voices=None, lang="en"):
        self.lang = lang
        self.voices = build_voices() if voices is None else voices
        self.played = []
        self.error_manager = MagicMock()
        self.anki_utils = MagicMock()
        self.anki_utils.run_on_main.side_effect = lambda callback, *a, **k: callback(*a, **k)
        self.service_manager = types.SimpleNamespace(
            full_voice_list=lambda: list(self.voices),
            locate_voice=self._locate_voice,
            get_all_services=lambda: [],
        )
        self.sample_text = "hello"
        self.save_calls = []

    def _locate_voice(self, voice_id):
        for voice in self.voices:
            if voice.voice_id == voice_id:
                return voice
        raise errors.VoiceIdNotFound(voice_id)

    def get_ui_language(self):
        return self.lang

    def play_sound(self, text, voice_id, options):
        self.played.append((text, voice_id, dict(options)))

    def save_configuration(self, model):
        self.save_calls.append(model)


@pytest.fixture
def qt(monkeypatch):
    return qt_stub.install(monkeypatch)


@pytest.fixture
def hypertts():
    return FakeHyperTTS()


@pytest.fixture
def changes():
    return MagicMock()


@pytest.fixture
def component(qt, hypertts, changes):
    comp = component_voiceselection.VoiceSelection(hypertts, MagicMock(), changes)
    comp.draw()
    return comp


def _select_voice(component, name):
    """Select a voice by a substring of its display label (language, gender, name)."""
    for index in range(component.voices_combobox.count()):
        if name in component.voices_combobox.itemText(index):
            component.voices_combobox.setCurrentIndex(index)
            return index
    raise AssertionError(f"{name!r} not in {component.voices_combobox.items()}")


def _select(component, combobox, text):
    index = combobox.findText(text)
    assert index >= 0, f"{text!r} not in {combobox.items()}"
    combobox.setCurrentIndex(index)


def _find_button(component, object_name):
    for row in range(component.voice_list_grid_layout.count()):
        widget = component.voice_list_grid_layout.itemAt(row).widget()
        if widget is not None and widget.objectName() == object_name:
            return widget
    raise AssertionError(f"no widget named {object_name}")


# --------------------------------------------------------------------------- #
# get_voices / draw
# --------------------------------------------------------------------------- #


@pytest.mark.unit
def test_get_voices_builds_sorted_filter_values(component):
    assert [voice.name for voice in component.voice_list] == ["aria", "guy", "thorsten", "kyoko"]
    assert component.services == ["EdgeTTS", "Piper"]
    assert [language.lang_name for language in component.languages] == ["English", "German", "Japanese"]
    assert [gender.name for gender in component.genders] == ["Female", "Male"]
    assert len(component.audio_languages) == 3


@pytest.mark.unit
def test_get_voices_defaults_to_the_first_voice_in_single_mode(component):
    model = component.get_model()

    assert isinstance(model, config_models.VoiceSelectionSingle)
    assert model.selection_mode == constants.VoiceSelectionMode.single
    assert model.voice.voice_id == component.voice_list[0].voice_id


@pytest.mark.unit
def test_draw_populates_every_filter_with_an_all_entry(component):
    # index 0 is "All", index 1 is the separator, the rest are the values.
    assert component.services_combobox.itemText(0) == ALL
    assert component.services_combobox.count() == 4  # All + separator + 2 services
    assert component.languages_combobox.count() == 5  # All + separator + 3 languages
    assert component.genders_combobox.count() == 4
    assert component.audio_languages_combobox.count() == 5


@pytest.mark.unit
def test_draw_shows_every_voice_and_enables_the_sample_button(component):
    assert component.voices_combobox.count() == 4
    assert component.voices_combobox.currentIndex() == 0
    assert component.radio_button_single.isChecked() is True
    assert component.play_sample_button.isEnabled() is False  # nothing sampled yet
    assert component.voice_list_display_stack.currentIndex() == 0


@pytest.mark.unit
def test_draw_returns_the_scroll_area(component):
    assert isinstance(component.scroll_area, qt_stub.ScrollArea)
    assert component.scroll_area.widget() is component.layout_widget


# --------------------------------------------------------------------------- #
# filtering
# --------------------------------------------------------------------------- #


@pytest.mark.unit
def test_filtering_by_service_narrows_the_voice_list(component):
    _select(component, component.services_combobox, "Piper")

    assert [voice.name for voice in component.filtered_voice_list] == ["thorsten", "kyoko"]
    assert component.voices_combobox.count() == 2


@pytest.mark.unit
def test_filtering_by_language_narrows_the_voice_list(component):
    _select(component, component.languages_combobox, "German")

    assert [voice.name for voice in component.filtered_voice_list] == ["thorsten"]


@pytest.mark.unit
def test_filtering_by_locale_narrows_the_voice_list(component):
    _select(component, component.audio_languages_combobox, AudioLanguage.ja_JP.audio_lang_name)

    assert [voice.name for voice in component.filtered_voice_list] == ["kyoko"]


@pytest.mark.unit
def test_filtering_by_gender_narrows_the_voice_list(component):
    _select(component, component.genders_combobox, constants.Gender.Male.name)

    assert [voice.name for voice in component.filtered_voice_list] == ["guy", "thorsten"]


@pytest.mark.unit
def test_filters_combine(component):
    _select(component, component.services_combobox, "Piper")
    _select(component, component.genders_combobox, constants.Gender.Male.name)

    assert [voice.name for voice in component.filtered_voice_list] == ["thorsten"]


@pytest.mark.unit
def test_filter_cascade_removes_services_that_no_longer_match(component):
    _select(component, component.languages_combobox, "Japanese")

    # Only Piper provides Japanese, so EdgeTTS must disappear from the service filter.
    assert component.services_combobox.findText("EdgeTTS") == -1
    assert component.services_combobox.findText("Piper") >= 0


@pytest.mark.unit
def test_reset_filters_restores_the_full_list(component):
    _select(component, component.services_combobox, "Piper")
    assert len(component.filtered_voice_list) == 2

    component.reset_filters()

    assert component.services_combobox.currentIndex() == 0
    assert component.languages_combobox.currentIndex() == 0
    assert component.audio_languages_combobox.currentIndex() == 0
    assert component.genders_combobox.currentIndex() == 0
    assert len(component.filtered_voice_list) == 4
    assert component.voices_combobox.count() == 4


@pytest.mark.unit
def test_filter_that_matches_nothing_clears_the_model_voice(component):
    # The cascading filters normally keep at least one voice, but a refresh can
    # empty the list (all services disabled while the dialog stayed open).
    component.voice_list = []

    component.filter_and_draw_voices(is_initial=True)

    assert component.filtered_voice_list == []
    assert component.get_model().voice is None
    assert component.voices_combobox.count() == 0


# --------------------------------------------------------------------------- #
# selection modes
# --------------------------------------------------------------------------- #


@pytest.mark.unit
def test_switching_to_random_replaces_the_model_and_shows_the_list(component, changes):
    component.radio_button_random.setChecked(True)

    assert isinstance(component.get_model(), config_models.VoiceSelectionRandom)
    assert component.voice_list_display_stack.currentIndex() == 1
    assert changes.call_count >= 1
    assert changes.call_args[0][0] is component.get_model()


@pytest.mark.unit
@pytest.mark.parametrize(
    "button_name, expected_type",
    [
        ("radio_button_priority", config_models.VoiceSelectionPriority),
        ("radio_button_sequence", config_models.VoiceSelectionSequence),
    ],
)
def test_switching_to_priority_or_sequence(component, button_name, expected_type):
    getattr(component, button_name).setChecked(True)

    assert isinstance(component.get_model(), expected_type)


@pytest.mark.unit
def test_switching_back_to_single_hides_the_voice_list(component):
    component.radio_button_random.setChecked(True)
    component.radio_button_single.setChecked(True)

    assert isinstance(component.get_model(), config_models.VoiceSelectionSingle)
    assert component.voice_list_display_stack.currentIndex() == 0


# --------------------------------------------------------------------------- #
# per-voice options
# --------------------------------------------------------------------------- #


@pytest.mark.unit
def test_selecting_a_voice_builds_one_widget_per_option(component):
    _select_voice(component, "thorsten")

    widgets = component.voice_options_widgets
    assert set(widgets) == {
        "voice_option_length_scale",
        "voice_option_speaker_id",
        "voice_option_device",
        "voice_option_note",
    }
    assert isinstance(widgets["voice_option_length_scale"], qt_stub.DoubleSpinBox)
    assert isinstance(widgets["voice_option_speaker_id"], qt_stub.SpinBox)
    assert isinstance(widgets["voice_option_device"], qt_stub.ComboBox)
    assert isinstance(widgets["voice_option_note"], qt_stub.LineEdit)
    # 4 option rows, each one label + one widget
    assert component.voice_options_layout.count() == 8


@pytest.mark.unit
def test_option_widgets_start_from_the_voice_defaults(component):
    _select_voice(component, "thorsten")

    widgets = component.voice_options_widgets
    assert widgets["voice_option_length_scale"].value() == 1.0
    assert widgets["voice_option_speaker_id"].value() == 0
    assert widgets["voice_option_device"].currentText() == "cpu"
    assert widgets["voice_option_note"].text() == ""


@pytest.mark.unit
def test_changing_a_number_option_updates_the_model(component):
    _select_voice(component, "thorsten")

    component.voice_options_widgets["voice_option_length_scale"].setValue(1.5)

    assert component.current_voice_options["length_scale"] == 1.5
    assert component.get_model().voice.options["length_scale"] == 1.5
    # untouched options stay out of the (sparse) override dict
    assert "speaker_id" not in component.current_voice_options


@pytest.mark.unit
def test_changing_a_list_option_updates_the_model(component):
    _select_voice(component, "thorsten")

    component.voice_options_widgets["voice_option_device"].setCurrentText("cuda")

    assert component.current_voice_options["device"] == "cuda"
    assert component.get_model().voice.options["device"] == "cuda"


@pytest.mark.unit
def test_changing_a_text_option_updates_the_model(component):
    _select_voice(component, "thorsten")

    component.voice_options_widgets["voice_option_note"].setText("whisper")

    assert component.current_voice_options["note"] == "whisper"


@pytest.mark.unit
def test_selecting_another_voice_rebuilds_the_options_form(component):
    _select_voice(component, "thorsten")
    first_layout_count = component.voice_options_layout.count()

    _select_voice(component, "aria")

    assert component.voice_options_layout.count() == 0
    assert component.voice_options_widgets == {}
    assert first_layout_count == 8


@pytest.mark.unit
def test_piper_japanese_voice_shows_the_warning_label(component):
    _select_voice(component, "kyoko")

    assert component.piper_warning_label.isVisible() is True
    assert "Japanese" in component.piper_warning_label.text()


@pytest.mark.unit
def test_piper_german_voice_hides_the_warning_without_raising(component):
    # Language enum members have no lang_code; the lookup must fall back to name.
    _select_voice(component, "thorsten")

    assert component.piper_warning_label.isVisible() is False


@pytest.mark.unit
def test_non_piper_voice_hides_the_warning_label(component):
    _select_voice(component, "kyoko")
    _select_voice(component, "aria")

    assert component.piper_warning_label.isVisible() is False


# --------------------------------------------------------------------------- #
# add / remove / reorder
# --------------------------------------------------------------------------- #


@pytest.mark.unit
def test_add_voice_appends_a_random_entry_with_the_current_options(component):
    component.radio_button_random.setChecked(True)
    _select_voice(component, "thorsten")
    component.voice_options_widgets["voice_option_device"].setCurrentText("cuda")

    component.add_voice()

    model = component.get_model()
    assert len(model.voice_list) == 1
    entry = model.voice_list[0]
    assert isinstance(entry, config_models.VoiceWithOptionsRandom)
    assert entry.voice_id == component.filtered_voice_list[2].voice_id
    assert entry.options["device"] == "cuda"
    assert entry.random_weight == 1


@pytest.mark.unit
def test_add_voice_requires_a_selection(component):
    component.radio_button_random.setChecked(True)
    component.filtered_voice_list = []

    with pytest.raises(errors.NoVoiceSelected):
        component.add_voice()


@pytest.mark.unit
def test_adding_two_voices_redraws_one_row_per_entry(component):
    component.radio_button_priority.setChecked(True)
    _select_voice(component, "aria")
    component.add_voice()
    _select_voice(component, "guy")
    component.add_voice()

    assert len(component.get_model().voice_list) == 2
    assert component.voice_list_grid_layout.count() == 8  # label+remove+up+down per row


@pytest.mark.unit
def test_remove_button_drops_the_entry_and_notifies(component, changes):
    component.radio_button_priority.setChecked(True)
    _select_voice(component, "aria")
    component.add_voice()
    _select_voice(component, "guy")
    component.add_voice()
    changes.reset_mock()

    _find_button(component, "remove_voice_row_0").pressed.emit()

    remaining = component.get_model().voice_list
    assert len(remaining) == 1
    assert remaining[0].voice_id == component.filtered_voice_list[1].voice_id
    assert changes.call_count >= 1


@pytest.mark.unit
def test_move_down_and_up_reorder_the_list(component):
    component.radio_button_priority.setChecked(True)
    first = component.filtered_voice_list[0]
    second = component.filtered_voice_list[1]
    for voice in (first, second):
        component.voices_combobox.setCurrentIndex(component.voices_combobox.findText(voice_str(voice, "en")))
        component.add_voice()
    model = component.get_model()
    before = [entry.voice_id for entry in model.voice_list]
    assert before == [first.voice_id, second.voice_id]

    def buttons_with_label(label):
        return [
            component.voice_list_grid_layout.itemAt(i).widget()
            for i in range(component.voice_list_grid_layout.count())
            if isinstance(component.voice_list_grid_layout.itemAt(i).widget(), qt_stub.PushButton)
            and component.voice_list_grid_layout.itemAt(i).widget().text() == label
        ]

    buttons_with_label(i18n.get_text("voice_button_move_down", "en"))[0].pressed.emit()

    assert [entry.voice_id for entry in component.get_model().voice_list] == [second.voice_id, first.voice_id]

    # After the swap the second entry sits in row 1, so its "up" button is second.
    buttons_with_label(i18n.get_text("voice_button_move_up", "en"))[1].pressed.emit()

    assert [entry.voice_id for entry in component.get_model().voice_list] == [first.voice_id, second.voice_id]


@pytest.mark.unit
def test_random_weight_change_updates_the_entry(component, changes):
    component.radio_button_random.setChecked(True)
    _select_voice(component, "aria")
    component.add_voice()
    changes.reset_mock()

    spin_boxes = [
        component.voice_list_grid_layout.itemAt(i).widget()
        for i in range(component.voice_list_grid_layout.count())
        if isinstance(component.voice_list_grid_layout.itemAt(i).widget(), qt_stub.SpinBox)
        and not isinstance(component.voice_list_grid_layout.itemAt(i).widget(), qt_stub.DoubleSpinBox)
    ]
    spin_boxes[0].setValue(7)

    assert component.get_model().voice_list[0].random_weight == 7
    assert changes.call_count >= 1


@pytest.mark.unit
def test_unresolvable_voice_in_the_list_is_skipped(component, hypertts):
    component.radio_button_priority.setChecked(True)
    _select_voice(component, "aria")
    component.add_voice()
    hypertts.voices = [voice for voice in hypertts.voices if voice.name != "aria"]

    component.redraw_selected_voices()

    # The row is skipped instead of raising, and the stale entity is kept.
    assert component.voice_list_grid_layout.count() == 0
    assert len(component.get_model().voice_list) == 1


# --------------------------------------------------------------------------- #
# sampling / serialisation
# --------------------------------------------------------------------------- #


@pytest.mark.unit
def test_sample_text_selected_enables_the_play_button(component):
    component.sample_text_selected("Guten Tag")

    assert component.sample_text == "Guten Tag"
    assert component.play_sample_button.isEnabled() is True
    assert component.play_sample_button.text() == i18n.get_text("voice_button_play_sample", "en")


@pytest.mark.unit
def test_play_sample_uses_the_selected_voice_and_options(component, hypertts):
    _select_voice(component, "thorsten")
    component.voice_options_widgets["voice_option_device"].setCurrentText("cuda")
    component.sample_text_selected("Guten Tag")

    component.play_sample()

    assert len(hypertts.played) == 1
    text, voice_id, options = hypertts.played[0]
    assert text == "Guten Tag"
    assert voice_id == component.filtered_voice_list[2].voice_id
    assert options["device"] == "cuda"


@pytest.mark.unit
def test_serialize_reports_the_selection_mode_and_voice(component):
    _select_voice(component, "guy")

    payload = component.serialize()

    assert payload["voice_selection_mode"] == "single"
    assert payload["voice"]["voice_id"]["service"] == "EdgeTTS"
    assert payload["voice"]["options"] == {}


@pytest.mark.unit
def test_serialize_random_mode_lists_every_entry_with_its_weight(component):
    component.radio_button_random.setChecked(True)
    _select_voice(component, "aria")
    component.add_voice()

    payload = component.serialize()

    assert payload["voice_selection_mode"] == "random"
    assert len(payload["voice_list"]) == 1
    assert payload["voice_list"][0]["weight"] == 1


# --------------------------------------------------------------------------- #
# load_model
# --------------------------------------------------------------------------- #


@pytest.mark.unit
def test_load_model_selects_the_saved_voice_and_its_options(component):
    model = config_models.VoiceSelectionSingle()
    target = component.voice_list[2]  # thorsten, the Piper voice
    model.set_voice(config_models.VoiceWithOptions(target.voice_id, {"device": "cuda", "length_scale": 1.25}))

    component.load_model(model)

    assert component.get_model() is model
    assert component.voices_combobox.currentText().startswith("German")
    assert component.current_voice_options["device"] == "cuda"
    assert model.voice.options["device"] == "cuda"
    assert model.voice.options["length_scale"] == 1.25


@pytest.mark.unit
def test_load_model_keeps_a_well_formed_voice_that_cannot_be_located(component, changes):
    """A voice that is unavailable *right now* must not be replaced.

    Opening a preset whose Piper service is temporarily disabled used to
    overwrite the saved voice with the first EdgeTTS voice, so pressing OK
    silently lost the user's Piper selection.
    """
    model = config_models.VoiceSelectionSingle()
    saved_id = TtsVoiceId_v3(voice_key={"id": "removed"}, service="EdgeTTS")
    model.set_voice(config_models.VoiceWithOptions(saved_id, {}))
    changes.reset_mock()  # draw() already reported the initial default voice

    component.load_model(model)

    # The saved voice survives; only the combobox mirrors the first voice.
    assert component.get_model() is model
    assert model.voice.voice_id == saved_id
    assert component.voices_combobox.currentIndex() == 0
    assert component.voices_combobox.currentText().startswith("English")
    # Merely opening the preset must not mark the batch model as changed.
    assert changes.call_count == 0


@pytest.mark.unit
def test_load_model_repairs_a_structurally_broken_voice(component, changes):
    model = config_models.VoiceSelectionSingle()
    model.set_voice(config_models.VoiceWithOptions(TtsVoiceId_v3(voice_key="", service=""), {}))
    changes.reset_mock()  # draw() already reported the initial default voice

    component.load_model(model)

    repaired = component.get_model()
    assert repaired.voice is not None
    assert repaired.voice.voice_id == component.voice_list[0].voice_id
    repaired.validate()
    # A repaired preset must be reported so ComponentBatch stores the fix.
    assert changes.call_count == 1
    assert changes.call_args[0][0] is repaired


@pytest.mark.unit
def test_load_model_random_mode_redraws_the_entries(component):
    first = component.voice_list[0]
    second = component.voice_list[1]
    model = config_models.VoiceSelectionRandom()
    model.add_voice(config_models.VoiceWithOptionsRandom(first.voice_id, {}, random_weight=3))
    model.add_voice(config_models.VoiceWithOptionsRandom(second.voice_id, {}, random_weight=1))

    component.load_model(model)

    assert component.radio_button_random.isChecked() is True
    assert isinstance(component.get_model(), config_models.VoiceSelectionRandom)
    assert component.voice_list_grid_layout.count() == 6


@pytest.mark.unit
def test_no_voices_available_raises(monkeypatch):
    qt_stub.install(monkeypatch)
    empty = FakeHyperTTS(voices=[])
    comp = component_voiceselection.VoiceSelection(empty, MagicMock(), MagicMock())

    with pytest.raises(errors.NoVoicesAvailable):
        comp.get_voices()