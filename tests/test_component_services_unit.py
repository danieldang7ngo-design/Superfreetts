"""Unit tests for the Services settings page logic.

``component_services`` is mostly Qt wiring, but it also owns the rules that
decide what a service row says and does: search text, status badges, config
validation messages and the change callbacks that write into the model.  Those
rules are tested here without building any widgets - a stub service and a
``ServicesPage`` assembled with ``__new__`` are enough.
"""

import types
from unittest.mock import MagicMock

import pytest

from superfreetts_addon import component_services, constants, i18n
from superfreetts_addon.config_models import Configuration


class FakeService:
    """Minimal stand-in for ``ServiceBase`` with configurable options."""

    def __init__(self, name="FakeService", fee="free", options=None, advanced=None, kind="tts"):
        self.name = name
        self.service_fee = types.SimpleNamespace(name=fee)
        self.enabled = True
        self._options = options or {}
        self._advanced = advanced
        self.service_type = types.SimpleNamespace(name=kind)

    def configuration_options(self):
        return self._options

    def advanced_configuration_options(self):
        if self._advanced is None:
            raise AttributeError("no advanced options")
        return self._advanced


def make_page(services=None, lang="en"):
    page = component_services.ServicesPage.__new__(component_services.ServicesPage)
    page.hypertts = MagicMock()
    page.hypertts.get_ui_language.return_value = lang
    page.hypertts.service_manager.get_all_services.return_value = services or []
    page.dialog = MagicMock()
    page.model = Configuration()
    page.service_checkbox_map = {}
    page.service_status_badge_map = {}
    page.service_search_index = {}
    page.service_expand_toggle_map = {}
    page.services_summary_label = None
    page.service_card_map = {}
    page._services_scroll_area = None
    page._services_container_widget = None
    page.enable_model_change = False
    page.option_validation_label_map = {}
    page.search_debounce_timer = None
    page.save_button = MagicMock()
    return page


# --------------------------------------------------------------------------- #
# option labels / search text
# --------------------------------------------------------------------------- #


@pytest.mark.unit
def test_service_option_label_prefers_translation():
    page = make_page()
    service = FakeService(name="EdgeTTS")

    label = page._get_service_option_label(service, "concurrency_workers", (int, "Workers", "", "", 3))

    assert label == i18n.get_text(
        "service_option_EdgeTTS_concurrency_workers", "en"
    ).format(max_workers=3)


@pytest.mark.unit
def test_service_option_label_uses_tuple_label_for_files():
    page = make_page()
    service = FakeService(name="UnknownService")

    label = page._get_service_option_label(service, "engine_path", ("file", "Engine executable", "*.exe"))

    assert label == "Engine executable"


@pytest.mark.unit
def test_service_option_label_falls_back_to_key():
    page = make_page()
    service = FakeService(name="UnknownService")

    assert page._get_service_option_label(service, "mystery", int) == "mystery"


@pytest.mark.unit
def test_search_text_includes_name_options_and_is_lowercase():
    page = make_page()
    service = FakeService(
        name="PiperTTS",
        options={"engine_path": ("file", "Engine executable", "*.exe")},
        advanced=None,
    )

    text = page._build_service_search_text(service, "Local neural voices")

    assert text == text.lower()
    for chunk in ("pipert", "local neural voices", "engine_path", "engine executable"):
        assert chunk in text


@pytest.mark.unit
def test_search_text_survives_broken_option_introspection():
    class Broken(FakeService):
        def configuration_options(self):
            raise RuntimeError("boom")

    page = make_page()

    text = page._build_service_search_text(Broken(name="BrokenTTS"), "desc")

    assert "brokentts" in text


@pytest.mark.unit
def test_search_text_includes_advanced_options():
    page = make_page()
    service = FakeService(
        name="KokoroTTS",
        options={},
        advanced={"voice_cache_dir": ("directory", "Voice cache", "")},
    )

    text = page._build_service_search_text(service, "desc")

    assert "voice_cache_dir" in text
    assert "voice cache" in text


# --------------------------------------------------------------------------- #
# status badges
# --------------------------------------------------------------------------- #


@pytest.mark.unit
def test_status_is_disabled_when_service_disabled():
    page = make_page()
    page.model.set_service_enabled("PiperTTS", False)
    service = FakeService(name="PiperTTS")

    text, css_class = page._get_service_status_info(service)

    assert text == i18n.get_text("service_status_disabled", "en")
    assert css_class == "statusBadgeDisabled"


@pytest.mark.unit
def test_status_is_ready_when_enabled_and_configured():
    page = make_page()
    page.model.set_service_enabled("PiperTTS", True)
    service = FakeService(name="PiperTTS", options={"voice": str})

    text, css_class = page._get_service_status_info(service)

    assert text == i18n.get_text("service_status_ready", "en")
    assert css_class == "statusBadgeReady"


@pytest.mark.unit
def test_status_needs_setup_when_api_key_missing():
    page = make_page()
    page.model.set_service_enabled("OpenAI", True)
    service = FakeService(name="OpenAI", options={"api_key": str})

    text, css_class = page._get_service_status_info(service)

    assert text == i18n.get_text("service_status_setup_needed", "en")
    assert css_class == "statusBadgeSetup"


@pytest.mark.unit
def test_status_needs_setup_when_api_key_is_blank():
    page = make_page()
    page.model.set_service_enabled("OpenAI", True)
    page.model.set_service_configuration_key("OpenAI", "api_key", "   ")
    service = FakeService(name="OpenAI", options={"api_key": str})

    _, css_class = page._get_service_status_info(service)

    assert css_class == "statusBadgeSetup"


@pytest.mark.unit
def test_status_ready_when_api_key_present():
    page = make_page()
    page.model.set_service_enabled("OpenAI", True)
    page.model.set_service_configuration_key("OpenAI", "api_key", "sk-test")
    service = FakeService(name="OpenAI", options={"api_key": str})

    _, css_class = page._get_service_status_info(service)

    assert css_class == "statusBadgeReady"


@pytest.mark.unit
def test_status_needs_setup_when_path_missing(tmp_path):
    page = make_page()
    page.model.set_service_enabled("PiperTTS", True)
    page.model.set_service_configuration_key("PiperTTS", "engine_path", str(tmp_path / "nope"))
    service = FakeService(name="PiperTTS", options={"engine_path": ("file", "Exe", "*.exe")})

    _, css_class = page._get_service_status_info(service)

    assert css_class == "statusBadgeSetup"


@pytest.mark.unit
def test_status_ready_when_path_exists(tmp_path):
    exe = tmp_path / "piper"
    exe.write_text("#!/bin/sh\n")
    page = make_page()
    page.model.set_service_enabled("PiperTTS", True)
    page.model.set_service_configuration_key("PiperTTS", "engine_path", str(exe))
    service = FakeService(name="PiperTTS", options={"engine_path": ("file", "Exe", "*.exe")})

    _, css_class = page._get_service_status_info(service)

    assert css_class == "statusBadgeReady"


@pytest.mark.unit
def test_status_counts_summarise_every_service():
    services = [FakeService(name="A"), FakeService(name="B"), FakeService(name="C")]
    page = make_page(services=services)
    page.model.set_service_enabled("A", True)
    page.model.set_service_enabled("B", False)
    page.model.set_service_enabled("C", True)
    page.model.set_service_configuration_key("C", "api_key", "")
    services[2]._options = {"api_key": str}

    counts = page._get_services_status_counts()

    assert sum(counts.values()) == 3
    assert counts[i18n.get_text("service_status_ready", "en")] == 1
    assert counts[i18n.get_text("service_status_disabled", "en")] == 1
    assert counts[i18n.get_text("service_status_setup_needed", "en")] == 1


@pytest.mark.unit
def test_refresh_summary_label_formats_counts():
    services = [FakeService(name="A")]
    page = make_page(services=services)
    page.services_summary_label = MagicMock()
    page.model.set_service_enabled("A", True)

    page._refresh_services_summary_label()

    expected = i18n.get_text("services_summary_status", "en").format(1, 0, 0)
    page.services_summary_label.setText.assert_called_once_with(expected)


@pytest.mark.unit
def test_refresh_summary_label_without_label_is_noop():
    page = make_page(services=[FakeService(name="A")])

    page._refresh_services_summary_label()  # must not raise


@pytest.mark.unit
def test_refresh_status_badges_updates_known_badges_only():
    page = make_page(services=[FakeService(name="A"), FakeService(name="B")])
    page.model.set_service_enabled("A", False)
    badge = MagicMock()
    page.service_status_badge_map = {"A": badge}

    page._refresh_service_status_badges()

    badge.setText.assert_called_once_with(i18n.get_text("service_status_disabled", "en"))
    badge.setProperty.assert_called_once_with("cssClass", "statusBadgeDisabled")
    badge.style.return_value.unpolish.assert_called_once_with(badge)


# --------------------------------------------------------------------------- #
# validation helpers
# --------------------------------------------------------------------------- #


@pytest.mark.unit
def test_set_validation_label_uses_success_colour():
    page = make_page()
    label = MagicMock()

    page._set_validation_label(label, True, "Looks good")

    label.setText.assert_called_once_with("Looks good")
    stylesheet = label.setStyleSheet.call_args.args[0]
    assert constants.COLOR_ACCENT_DARK in stylesheet


@pytest.mark.unit
def test_set_validation_label_uses_error_colour():
    page = make_page()
    label = MagicMock()

    page._set_validation_label(label, False, "Required")

    assert constants.COLOR_ERROR in label.setStyleSheet.call_args.args[0]


@pytest.mark.unit
def test_required_text_validation_flags_empty_then_filled():
    page = make_page()
    lineedit = MagicMock()
    lineedit.text.return_value = ""
    label = MagicMock()

    page._wire_required_text_validation("api_key", lineedit, label)
    assert label.setText.call_args.args[0] == i18n.get_text("config_validation_required", "en")

    callback = lineedit.textChanged.connect.call_args.args[0]
    callback("sk-test")

    assert label.setText.call_args.args[0] == i18n.get_text("config_validation_value_set", "en")


@pytest.mark.unit
def test_path_validation_reports_found_and_missing(tmp_path):
    page = make_page()
    lineedit = MagicMock()
    lineedit.text.return_value = ""
    label = MagicMock()

    page._wire_path_validation(lineedit, label)
    assert label.setText.call_args.args[0] == i18n.get_text("config_validation_required", "en")

    callback = lineedit.textChanged.connect.call_args.args[0]
    callback(str(tmp_path))
    assert label.setText.call_args.args[0] == i18n.get_text("config_validation_path_found", "en")

    callback(str(tmp_path / "missing"))
    assert label.setText.call_args.args[0] == i18n.get_text("config_validation_path_missing", "en")


# --------------------------------------------------------------------------- #
# setup shortcut / config sync
# --------------------------------------------------------------------------- #


@pytest.mark.unit
@pytest.mark.parametrize("name", ["KokoroTTS", "MmsTTS", "PiperTTS", "SupertonicTTS"])
def test_setup_shortcut_supported_for_local_engines(name):
    page = make_page()

    assert page._supports_setup_shortcut(FakeService(name=name)) is True


@pytest.mark.unit
@pytest.mark.parametrize("name", ["EdgeTTS", "GoogleTranslate", "OpenAI"])
def test_setup_shortcut_not_offered_for_remote_services(name):
    page = make_page()

    assert page._supports_setup_shortcut(FakeService(name=name)) is False


@pytest.mark.unit
def test_set_service_config_value_syncs_visible_lineedit():
    page = make_page()
    lineedit = MagicMock()
    lineedit.text.return_value = ""
    page.dialog.findChild.return_value = lineedit

    page._set_service_config_value_with_ui_sync("PiperTTS", "engine_path", "/opt/piper")

    assert page.model.get_service_configuration_key("PiperTTS", "engine_path") == "/opt/piper"
    lineedit.setText.assert_called_once_with("/opt/piper")


@pytest.mark.unit
def test_set_service_config_value_skips_lineedit_when_already_synced():
    page = make_page()
    lineedit = MagicMock()
    lineedit.text.return_value = "/opt/piper"
    page.dialog.findChild.return_value = lineedit

    page._set_service_config_value_with_ui_sync("PiperTTS", "engine_path", "/opt/piper")

    lineedit.setText.assert_not_called()


@pytest.mark.unit
def test_set_service_config_value_tolerates_missing_widget():
    page = make_page()
    page.dialog.findChild.return_value = None

    page._set_service_config_value_with_ui_sync("PiperTTS", "engine_path", "/opt/piper")

    assert page.model.get_service_configuration_key("PiperTTS", "engine_path") == "/opt/piper"


# --------------------------------------------------------------------------- #
# change callbacks
# --------------------------------------------------------------------------- #


@pytest.mark.unit
def test_enable_change_callback_maps_checked_state():
    page = make_page()
    service = FakeService(name="PiperTTS")

    callback = page.get_service_enable_change_fn(service)
    callback(2)
    assert page.model.get_service_enabled("PiperTTS") is True

    callback(0)
    assert page.model.get_service_enabled("PiperTTS") is False


@pytest.mark.unit
def test_bool_change_callback_maps_checked_state():
    page = make_page()
    service = FakeService(name="PiperTTS")

    callback = page.get_service_config_bool_change_fn(service, "use_gpu")
    callback(2)
    assert page.model.get_service_configuration_key("PiperTTS", "use_gpu") is True

    callback(0)
    assert page.model.get_service_configuration_key("PiperTTS", "use_gpu") is False


@pytest.mark.unit
@pytest.mark.parametrize(
    ("factory", "value"),
    [
        ("get_service_config_str_change_fn", "hello"),
        ("get_service_config_int_change_fn", 7),
        ("get_service_config_float_change_fn", 0.5),
        ("get_service_config_list_change_fn", "a,b"),
    ],
)
def test_config_change_callbacks_write_value(factory, value):
    page = make_page()
    service = FakeService(name="PiperTTS")

    getattr(page, factory)(service, "some_key")(value)

    assert page.model.get_service_configuration_key("PiperTTS", "some_key") == value


@pytest.mark.unit
def test_enabled_widget_name_is_namespaced_by_service():
    page = make_page()

    assert page.get_service_enabled_widget_name(FakeService(name="EdgeTTS")) == "EdgeTTS_enabled"


@pytest.mark.unit
def test_model_change_only_enables_save_button_when_tracking():
    page = make_page()
    page.enable_model_change = False
    page.model_change()
    page.save_button.setEnabled.assert_not_called()

    page.enable_model_change = True
    page.model_change()

    page.save_button.setEnabled.assert_called_once_with(True)
    page.save_button.setProperty.assert_called_once_with("cssClass", "primaryButton")


# --------------------------------------------------------------------------- #
# service list / card styling / save + cancel
# --------------------------------------------------------------------------- #


@pytest.mark.unit
def test_get_service_list_keeps_only_free_services():
    free = FakeService(name="Free", fee="free")
    paid = FakeService(name="Paid", fee="paid")
    page = make_page(services=[free, paid])

    assert page.get_service_list() == [free]


@pytest.mark.unit
def test_apply_service_card_style_sets_state_and_repolishes():
    page = make_page()
    card = MagicMock()

    page._apply_service_card_style(card, True)

    card.setProperty.assert_any_call("cssClass", "serviceCard")
    card.setProperty.assert_any_call("cardState", "enabled")
    card.style.return_value.polish.assert_called_once_with(card)


@pytest.mark.unit
def test_apply_service_card_style_marks_disabled_cards():
    page = make_page()
    card = MagicMock()

    page._apply_service_card_style(card, False)

    card.setProperty.assert_any_call("cardState", "disabled")


@pytest.mark.unit
def test_save_button_saves_and_reconfigures():
    page = make_page()

    page.save_button_pressed()

    page.hypertts.save_configuration.assert_called_once_with(page.model)
    page.hypertts.reconfigure_service_manager.assert_called_once()
    page.dialog.close.assert_called_once()


@pytest.mark.unit
def test_cancel_button_closes_dialog_without_saving():
    page = make_page()

    page.cancel_button_pressed()

    page.dialog.close.assert_called_once()
    page.hypertts.save_configuration.assert_not_called()

# --------------------------------------------------------------------------- #
# rendered widgets (fake Qt)
# --------------------------------------------------------------------------- #


@pytest.fixture
def qt(monkeypatch):
    from . import qt_stub

    return qt_stub.install(monkeypatch)


def drawn_page(services, model=None, lang="en"):
    """A ServicesPage that has actually built its widgets."""
    hypertts = MagicMock()
    hypertts.get_ui_language.return_value = lang
    hypertts.service_manager.get_all_services.return_value = services
    page = component_services.ServicesPage(hypertts, MagicMock())
    page.load_model(model or Configuration())
    layout = component_services.aqt.qt.QVBoxLayout()
    page.draw(layout)
    return page


def _grid_widgets(layout):
    """Collect every named widget, descending into nested option rows."""
    widgets = {}

    def walk(current):
        for index in range(current.count()):
            item = current.itemAt(index)
            widget = item.widget()
            if widget is not None and widget.objectName():
                widgets[widget.objectName()] = widget
            nested = item.layout()
            if nested is not None:
                walk(nested)

    walk(layout)
    return widgets


def _widgets_with_text(layout, text):
    found = []

    def walk(current):
        for index in range(current.count()):
            item = current.itemAt(index)
            widget = item.widget()
            if widget is not None and getattr(widget, "text", None) and widget.text() == text:
                found.append(widget)
            nested = item.layout()
            if nested is not None:
                walk(nested)

    walk(layout)
    return found


def _option_service(name="OptionTTS", options=None):
    return FakeService(
        name=name,
        advanced={},
        options=options
        or {
            "api_key": str,
            "concurrency_workers": int,
            "timeout": float,
            "use_ssml": bool,
            "voice_style": ["neutral", "cheerful"],
        },
    )


@pytest.mark.unit
def test_draw_service_options_builds_one_widget_per_option_type(qt):
    page = make_page([_option_service()])
    layout = qt.QVBoxLayout()

    checkbox = page.draw_service_options(_option_service(), layout)

    widgets = _grid_widgets(layout)
    assert checkbox.objectName() == "OptionTTS_enabled"
    assert isinstance(widgets["OptionTTS_api_key"], qt.LineEdit)
    assert isinstance(widgets["OptionTTS_concurrency_workers"], qt.SpinBox)
    assert isinstance(widgets["OptionTTS_timeout"], qt.DoubleSpinBox)
    assert isinstance(widgets["OptionTTS_use_ssml"], qt.CheckBox)
    assert isinstance(widgets["OptionTTS_voice_style"], qt.ComboBox)
    assert widgets["OptionTTS_voice_style"].items() == ["neutral", "cheerful"]


@pytest.mark.unit
def test_draw_service_options_restores_saved_values(qt):
    page = make_page([_option_service()])
    page.model.set_service_configuration_key("OptionTTS", "api_key", "secret-value")
    page.model.set_service_configuration_key("OptionTTS", "concurrency_workers", 7)
    page.model.set_service_configuration_key("OptionTTS", "timeout", 2.5)
    page.model.set_service_configuration_key("OptionTTS", "use_ssml", True)
    page.model.set_service_configuration_key("OptionTTS", "voice_style", "cheerful")
    layout = qt.QVBoxLayout()

    page.draw_service_options(_option_service(), layout)

    widgets = _grid_widgets(layout)
    assert widgets["OptionTTS_api_key"].text() == "secret-value"
    assert widgets["OptionTTS_concurrency_workers"].value() == 7
    assert widgets["OptionTTS_timeout"].value() == 2.5
    assert widgets["OptionTTS_use_ssml"].isChecked() is True
    assert widgets["OptionTTS_voice_style"].currentText() == "cheerful"


@pytest.mark.unit
def test_draw_service_options_file_row_offers_a_browse_button(qt):
    service = FakeService(
        name="FileTTS", advanced={}, options={"engine_path": ("file", "Engine executable", "*.exe")}
    )
    page = make_page([service])
    layout = qt.QVBoxLayout()

    page.draw_service_options(service, layout)

    assert _widgets_with_text(layout, "Browse...")
    assert isinstance(_grid_widgets(layout)["FileTTS_engine_path"], qt.LineEdit)


@pytest.mark.unit
def test_draw_service_options_secret_keys_get_a_validation_label(qt):
    service = FakeService(name="SecretTTS", advanced={}, options={"api_key": str})
    page = make_page([service])
    layout = qt.QVBoxLayout()

    page.draw_service_options(service, layout)

    label = page.option_validation_label_map["SecretTTS_api_key"]
    assert label.text() == i18n.get_text("config_validation_required", "en")


@pytest.mark.unit
def test_required_text_validation_toggles_with_content(qt):
    page = make_page()
    lineedit = qt.QLineEdit()
    label = qt.QLabel()

    page._wire_required_text_validation("api_key", lineedit, label)
    assert label.text() == i18n.get_text("config_validation_required", "en")

    lineedit.setText("abc123")

    assert label.text() == i18n.get_text("config_validation_value_set", "en")


@pytest.mark.unit
def test_path_validation_reports_missing_and_existing_paths(qt, tmp_path):
    page = make_page()
    lineedit = qt.QLineEdit()
    label = qt.QLabel()

    page._wire_path_validation(lineedit, label)
    assert label.text() == i18n.get_text("config_validation_required", "en")

    missing = tmp_path / "nope.bin"
    lineedit.setText(str(missing))
    assert label.text() == i18n.get_text("config_validation_path_missing", "en")

    existing = tmp_path / "piper.exe"
    existing.write_bytes(b"x")
    lineedit.setText(str(existing))
    assert label.text() == i18n.get_text("config_validation_path_found", "en")


@pytest.mark.unit
def test_service_list_drops_paid_services(qt):
    page = make_page(
        [
            FakeService(name="FreeTTS", fee="free"),
            FakeService(name="PaidTTS", fee="paid"),
        ]
    )

    assert [service.name for service in page.get_service_list()] == ["FreeTTS"]


@pytest.mark.unit
def test_status_info_covers_disabled_setup_needed_and_ready(qt):
    page = make_page()
    service = FakeService(name="EdgeTTS", options={"api_key": str})

    page.model.set_service_enabled("EdgeTTS", False)
    assert page._get_service_status_info(service) == (
        i18n.get_text("service_status_disabled", "en"),
        "statusBadgeDisabled",
    )

    page.model.set_service_enabled("EdgeTTS", True)
    assert page._get_service_status_info(service) == (
        i18n.get_text("service_status_setup_needed", "en"),
        "statusBadgeSetup",
    )

    page.model.set_service_configuration_key("EdgeTTS", "api_key", "set")
    assert page._get_service_status_info(service) == (
        i18n.get_text("service_status_ready", "en"),
        "statusBadgeReady",
    )


@pytest.mark.unit
def test_setup_shortcut_only_for_local_engines(qt):
    page = make_page()

    assert page._supports_setup_shortcut(FakeService(name="PiperTTS")) is True
    assert page._supports_setup_shortcut(FakeService(name="KokoroTTS")) is True
    assert page._supports_setup_shortcut(FakeService(name="EdgeTTS")) is False


@pytest.mark.unit
def test_draw_wires_cards_checkboxes_and_summary(qt):
    model = Configuration()
    model.set_service_enabled("EdgeTTS", True)
    model.set_service_enabled("Duden", True)
    page = drawn_page(
        [_option_service("EdgeTTS"), FakeService(name="Duden", kind="dictionary", advanced={})], model
    )

    assert sorted(page.service_card_map) == ["Duden", "EdgeTTS"]
    assert page.service_checkbox_map["EdgeTTS"].isChecked() is True
    # EdgeTTS is missing its api_key (setup needed), Duden needs nothing (ready)
    assert page.services_summary_label.text() == i18n.get_text(
        "services_summary_status", "en"
    ).format(1, 1, 0)


@pytest.mark.unit
def test_enabling_a_service_marks_the_page_dirty(qt):
    page = drawn_page([_option_service("EdgeTTS")])
    page.save_button.setEnabled(False)

    page.service_checkbox_map["EdgeTTS"].setChecked(False)

    assert page.get_model().get_service_enabled("EdgeTTS") is False
    assert page.save_button.isEnabled() is True
    assert page.service_card_map["EdgeTTS"].property("cardState") == "disabled"


@pytest.mark.unit
def test_save_button_persists_and_closes(qt):
    page = drawn_page([_option_service("EdgeTTS")])

    page.save_button_pressed()

    page.hypertts.save_configuration.assert_called_once_with(page.get_model())
    page.hypertts.reconfigure_service_manager.assert_called_once()
    page.dialog.close.assert_called_once()


@pytest.mark.unit
def test_cancel_button_closes_without_saving(qt):
    page = drawn_page([_option_service("EdgeTTS")])

    page.cancel_button_pressed()

    page.dialog.close.assert_called_once()
    page.hypertts.save_configuration.assert_not_called()
