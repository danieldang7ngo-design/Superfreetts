"""Regression tests for Issue #4: presets that cannot resolve their voice.

Symptoms: a preset saved with an empty/unavailable voice produced
``No Voice has been set`` when rendering, and ``VoiceIdNotFound(voice_key='',
service='')`` when the preset was used from another tab.  The selection dialog
also failed to report a valid voice when the saved voice was already selected
(``setCurrentIndex`` is a no-op, so no signal fired).
"""

import copy
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from superfreetts_addon import component_voiceselection
from superfreetts_addon import config_models
from superfreetts_addon import config_store
from superfreetts_addon import constants
from superfreetts_addon import errors
from superfreetts_addon import voice as voice_module
from tests.conftest import MockAnkiUtils


class FakeLanguage:
    lang_code = "en"
    lang_name = "English"


class FakeGender:
    name = "Female"


class FakeVoice:
    def __init__(self, key, service="EdgeTTS", options=None):
        self.name = key
        self.voice_key = key
        self.options = options or {}
        self.service = service
        self.gender = FakeGender()
        self.audio_languages = [
            SimpleNamespace(audio_lang_name="English (US)", lang=FakeLanguage())
        ]
        self.languages = [FakeLanguage()]
        self.service_fee = None

    @property
    def voice_id(self):
        return voice_module.TtsVoiceId_v3(self.voice_key, self.service)

    def __repr__(self):
        return f"FakeVoice({self.voice_key!r}, {self.service!r})"


SPEED_OPTION = {
    "speed": {
        "type": "number",
        "min": 0.5,
        "max": 2.0,
        "default": 1.0,
        "label": "Speed",
    }
}


class FakeServiceManager:
    def __init__(self, voices, missing=()):
        self.voices = list(voices)
        self.missing = set(missing)
        self.locate_calls = []

    def full_voice_list(self, single_service_name=None):
        return list(self.voices)

    def locate_voice(self, voice_id):
        self.locate_calls.append(voice_id)
        if voice_id in self.missing:
            raise errors.VoiceIdNotFound(voice_id)
        for voice in self.voices:
            if voice.voice_id == voice_id:
                return voice
        raise errors.VoiceIdNotFound(voice_id)


def _make_store(voices, missing=()):
    manager = FakeServiceManager(voices, missing)
    store = config_store.ConfigStore(MockAnkiUtils(), manager)
    return store, manager


def _single_config(voice_key, service):
    return {
        "voice_selection_mode": "single",
        "voice": {
            "voice_id": {"voice_key": voice_key, "service": service},
            "options": {},
        },
    }


# ---------------------------------------------------------------------------
# ConfigStore.deserialize_voice_selection
# ---------------------------------------------------------------------------


@pytest.mark.unit
@pytest.mark.parametrize(
    "voice_payload",
    [
        {"voice_id": {"voice_key": "", "service": ""}, "options": {}},
        {"voice_id": {}, "options": {}},
        {"voice_id": None, "options": {}},
        None,
        {},
    ],
)
def test_broken_single_preset_is_repaired_to_first_voice(voice_payload):
    voices = [FakeVoice("alpha"), FakeVoice("beta")]
    store, manager = _make_store(voices)

    selection = store.deserialize_voice_selection(
        {"voice_selection_mode": "single", "voice": voice_payload}
    )

    assert selection.selection_mode == constants.VoiceSelectionMode.single
    assert selection.voice is not None
    assert selection.voice.voice_id == voices[0].voice_id
    selection.validate()  # must not raise NoVoiceSet
    # The repaired voice resolves, so preview/audio generation will not raise
    # VoiceIdNotFound.
    assert manager.locate_voice(selection.voice.voice_id) is voices[0]


@pytest.mark.unit
def test_single_preset_with_unavailable_service_voice_is_kept_as_saved():
    """Deserialising must not resolve (or overwrite) a well-formed voice id.

    Resolving called full_voice_list() on the realtime render path and replaced
    the user's saved voice whenever its service happened to be disabled.  The
    selection dialog repairs only structurally broken voice ids and preserves
    a well-formed one that is merely unavailable right now (see
    test_load_model_preserves_voice_that_is_temporarily_unavailable).
    """
    present = FakeVoice("alpha")
    missing_id = voice_module.TtsVoiceId_v3("ghost", "EdgeTTS")
    store, manager = _make_store([present], missing=[missing_id])

    selection = store.deserialize_voice_selection(_single_config("ghost", "EdgeTTS"))

    assert selection.voice.voice_id == missing_id
    assert manager.locate_calls == []
    selection.validate()


@pytest.mark.unit
def test_valid_single_preset_does_not_enumerate_the_voice_list():
    """The realtime path must not pay for full_voice_list()."""
    store, manager = _make_store([FakeVoice("alpha")])
    enumerated = []
    manager.full_voice_list = lambda *args, **kwargs: enumerated.append(1) or []

    selection = store.deserialize_voice_selection(_single_config("alpha", "EdgeTTS"))

    assert selection.voice.voice_id == voice_module.TtsVoiceId_v3("alpha", "EdgeTTS")
    assert enumerated == []
    assert manager.locate_calls == []


@pytest.mark.unit
def test_valid_single_preset_keeps_voice_and_options():
    alpha = FakeVoice("alpha", options=SPEED_OPTION)
    beta = FakeVoice("beta")
    store, manager = _make_store([alpha, beta])

    selection = store.deserialize_voice_selection(
        {
            "voice_selection_mode": "single",
            "voice": {
                "voice_id": {"voice_key": "beta", "service": "EdgeTTS"},
                "options": {"speed": 1.5},
            },
        }
    )

    assert selection.voice.voice_id == beta.voice_id
    assert selection.voice.options == {"speed": 1.5}
    assert manager.locate_calls == []
    selection.validate()


@pytest.mark.unit
def test_single_preset_without_any_available_voice_stays_empty_but_valid_shape():
    store, _manager = _make_store([])

    selection = store.deserialize_voice_selection(_single_config("", ""))

    # No bogus TtsVoiceId_v3('', '') is handed to the batch model; validation
    # reports the real problem (NoVoiceSet) instead of VoiceIdNotFound.
    assert selection.voice is None
    with pytest.raises(errors.NoVoiceSet):
        selection.validate()


@pytest.mark.unit
@pytest.mark.parametrize("mode", ["random", "priority", "sequence"])
def test_multi_voice_preset_with_only_broken_voices_falls_back(mode):
    voices = [FakeVoice("alpha"), FakeVoice("beta")]
    store, _manager = _make_store(voices)
    config = {
        "voice_selection_mode": mode,
        "voice_list": [
            {"voice_id": {"voice_key": "", "service": ""}, "options": {}, "weight": 1},
            {"voice_id": {}, "options": {}},
        ],
    }

    selection = store.deserialize_voice_selection(config)

    assert len(selection.voice_list) == 1
    assert selection.voice_list[0].voice_id == voices[0].voice_id
    selection.validate()  # must not raise NoVoiceSet


@pytest.mark.unit
def test_load_preset_repairs_broken_preset_and_resolves_for_generation():
    voices = [FakeVoice("alpha"), FakeVoice("beta")]
    store, manager = _make_store(voices)
    store.config[constants.CONFIG_PRESETS] = {
        "preset-1": {
            "uuid": "preset-1",
            "name": "Broken preset",
            "source": {"mode": "simple", "source_field": "Front"},
            "target": {},
            "voice_selection": {
                "voice_selection_mode": "single",
                "voice": {
                    "voice_id": {"voice_key": "", "service": ""},
                    "options": {},
                },
            },
        }
    }

    batch = store.load_preset("preset-1")

    assert batch.voice_selection.voice is not None
    assert batch.voice_selection.voice.voice_id == voices[0].voice_id
    batch.voice_selection.validate()
    # Preview / batch generation resolve the voice by id; it must not raise.
    assert manager.locate_voice(batch.voice_selection.voice.voice_id) is voices[0]
    # Saving the repaired preset round-trips without losing the voice.
    assert batch.voice_selection.serialize()["voice"]["voice_id"]["voice_key"] == "alpha"


# ---------------------------------------------------------------------------
# VoiceSelection.load_model
# ---------------------------------------------------------------------------


class FakeCombo:
    def __init__(self, items=None):
        self._items = list(items or [])
        self._index = 0 if self._items else -1

    def count(self):
        return len(self._items)

    def addItem(self, item):
        self._items.append(item)

    def addItems(self, items):
        self._items.extend(items)

    def insertSeparator(self, index):
        pass

    def findText(self, text):
        try:
            return self._items.index(text)
        except ValueError:
            return -1

    def currentIndex(self):
        return self._index

    def setCurrentIndex(self, index):
        # Qt emits currentIndexChanged only when the index actually changes.
        self._index = index

    def currentText(self):
        if 0 <= self._index < len(self._items):
            return self._items[self._index]
        return ""

    def setCurrentText(self, text):
        index = self.findText(text)
        if index >= 0:
            self._index = index


class FakeLayout:
    def __init__(self):
        self.widgets = []

    def count(self):
        return 0

    def itemAt(self, index):
        return SimpleNamespace(widget=lambda: MagicMock())

    def addWidget(self, widget, *args, **kwargs):
        self.widgets.append(widget)


def _make_component(voices, missing=()):
    manager = FakeServiceManager(voices, missing)
    hypertts = SimpleNamespace(
        service_manager=manager,
        get_ui_language=lambda: "en",
    )
    component = component_voiceselection.VoiceSelection.__new__(
        component_voiceselection.VoiceSelection
    )
    component.hypertts = hypertts
    component.dialog = None
    component.enable_model_change_callback = True
    component.updates = []
    component.model_change_callback = component.updates.append
    component.voice_list = list(voices)
    component.filtered_voice_list = list(voices)
    component.audio_languages_combobox = FakeCombo(
        sorted({v.audio_languages[0].audio_lang_name for v in voices})
    )
    component.languages_combobox = FakeCombo(
        sorted({v.languages[0].lang_name for v in voices})
    )
    component.services_combobox = FakeCombo(sorted({v.service for v in voices}))
    component.genders_combobox = FakeCombo(sorted({v.gender.name for v in voices}))
    component.voices_combobox = FakeCombo([v.name for v in voices])
    component.voice_options_layout = FakeLayout()
    component.voice_options_widgets = {}
    component.current_voice_options = {}
    component.piper_warning_label = MagicMock()
    component.radio_button_single = MagicMock()
    component.radio_button_random = MagicMock()
    component.radio_button_priority = MagicMock()
    component.radio_button_sequence = MagicMock()
    return component, manager


@pytest.mark.unit
def test_load_model_keeps_voice_selected_at_index_zero():
    alpha = FakeVoice("alpha", options=SPEED_OPTION)
    beta = FakeVoice("beta")
    component, manager = _make_component([alpha, beta])
    model = config_models.VoiceSelectionSingle()
    model.set_voice(config_models.VoiceWithOptions(alpha.voice_id, {}))

    component.load_model(copy.deepcopy(model))

    assert manager.locate_calls == [alpha.voice_id]
    assert component.voice_selection_model is not None
    assert component.voice_selection_model.voice.voice_id == alpha.voice_id
    component.voice_selection_model.validate()


@pytest.mark.unit
def test_load_model_reports_valid_voice_to_batch_model():
    alpha = FakeVoice("alpha", options=SPEED_OPTION)
    beta = FakeVoice("beta")
    component, _manager = _make_component([alpha, beta])
    batch = config_models.BatchConfig(MockAnkiUtils())
    broken = config_models.VoiceSelectionSingle()
    batch.set_voice_selection(broken)
    notifications = []
    component.model_change_callback = lambda model: (
        notifications.append(model), batch.set_voice_selection(model)
    )

    component.load_model(copy.deepcopy(broken))

    # ComponentBatch received the repaired model, not the voice=None original.
    assert batch.voice_selection is not broken
    assert batch.voice_selection.voice is not None
    assert batch.voice_selection.voice.voice_id == alpha.voice_id
    batch.voice_selection.validate()
    assert notifications


@pytest.mark.unit
def test_load_model_repairs_voice_with_empty_voice_id(monkeypatch):
    """A structurally empty voice id is repaired and reported to the parent."""
    alpha = FakeVoice("alpha", options=SPEED_OPTION)
    beta = FakeVoice("beta")
    component, _manager = _make_component([alpha, beta])
    model = config_models.VoiceSelectionSingle()
    model.set_voice(config_models.VoiceWithOptions(voice_module.TtsVoiceId_v3("", ""), {}))
    batch = config_models.BatchConfig(MockAnkiUtils())
    batch.set_voice_selection(model)
    notifications = []
    component.model_change_callback = lambda loaded: (
        notifications.append(loaded), batch.set_voice_selection(loaded)
    )

    fake_logger = MagicMock()
    monkeypatch.setattr(component_voiceselection, "logger", fake_logger)

    component.load_model(copy.deepcopy(model))

    assert batch.voice_selection.voice.voice_id == alpha.voice_id
    batch.voice_selection.validate()
    assert notifications
    # The repair is a fallback, not silence: it must be logged for support.
    logged = " ".join(str(call.args[0]) for call in fake_logger.warning.call_args_list)
    assert "missing or malformed" in logged


@pytest.mark.unit
def test_load_model_preserves_voice_that_is_temporarily_unavailable(monkeypatch):
    """A well-formed voice id must survive a service being switched off.

    The preset keeps its Piper voice; only the combobox shows the first
    available voice.  No ``model_change_callback`` may fire, otherwise merely
    opening the preset would mark the batch model dirty and persist the
    substitution.
    """
    alpha = FakeVoice("alpha", options=SPEED_OPTION)
    beta = FakeVoice("beta")
    ghost_id = voice_module.TtsVoiceId_v3("ghost", "Piper")
    component, _manager = _make_component([alpha, beta], missing=[ghost_id])
    model = config_models.VoiceSelectionSingle()
    model.set_voice(config_models.VoiceWithOptions(ghost_id, {}))
    batch = config_models.BatchConfig(MockAnkiUtils())
    batch.set_voice_selection(model)
    notifications = []
    component.model_change_callback = lambda loaded: (
        notifications.append(loaded), batch.set_voice_selection(loaded)
    )

    fake_logger = MagicMock()
    monkeypatch.setattr(component_voiceselection, "logger", fake_logger)

    component.load_model(copy.deepcopy(model))

    assert component.get_model().voice.voice_id == ghost_id
    assert batch.voice_selection.voice.voice_id == ghost_id
    assert notifications == []
    assert component.voices_combobox.currentIndex() == 0
    logged = " ".join(str(call.args[0]) for call in fake_logger.warning.call_args_list)
    assert "Voice not found for preset" in logged


@pytest.mark.unit
def test_load_model_applies_saved_options_and_syncs_model():
    alpha = FakeVoice("alpha", options=SPEED_OPTION)
    component, _manager = _make_component([alpha])
    model = config_models.VoiceSelectionSingle()
    model.set_voice(config_models.VoiceWithOptions(alpha.voice_id, {"speed": 1.5}))

    component.load_model(model)

    assert component.current_voice_options == {"speed": 1.5}
    assert component.voice_selection_model.voice.options == {"speed": 1.5}
    widget = component.voice_options_widgets["voice_option_speed"]
    assert widget.setCurrentText.called or widget.setValue.called


@pytest.mark.unit
def test_redraw_selected_voices_skips_unresolvable_voice(monkeypatch):
    alpha = FakeVoice("alpha")
    ghost_id = voice_module.TtsVoiceId_v3("ghost", "EdgeTTS")
    component, _manager = _make_component([alpha], missing=[ghost_id])
    selection = config_models.VoiceSelectionRandom()
    selection.add_voice(config_models.VoiceWithOptionsRandom(alpha.voice_id, {}))
    selection.add_voice(config_models.VoiceWithOptionsRandom(ghost_id, {}))
    component.voice_selection_model = selection
    component.voice_list_grid_layout = FakeLayout()
    monkeypatch.setattr(
        component_voiceselection.voice_module,
        "generate_voice_with_options_str",
        lambda voice, options, lang: f"{voice.name}",
    )

    component.redraw_selected_voices()  # must not raise VoiceIdNotFound

    # One surviving random voice -> label + weight + remove button.
    assert len(component.voice_list_grid_layout.widgets) == 3
