"""Every UI theme renders a complete, themed stylesheet in both modes.

The seven themes share one QSS skeleton, so a missing palette entry or a
forgotten token shows up as an invalid or unthemed stylesheet.  These tests pin
the parts a user would notice: the stylesheet is non-trivial, every core widget
selector is present, and each theme keeps its signature accent colour in light
*and* dark mode (the original bug class here was a light-mode colour leaking
into night mode).
"""

import types

import pytest

from superfreetts_addon import gui_utils


THEMES = ["vibrant", "ollama", "nintendo", "apple", "binance", "clay", "claude"]

# Accent colour that identifies each theme, per mode.
SIGNATURE = {
    "vibrant": {False: "#6366F1", True: "#00E1D9"},
    "ollama": {False: "#000000", True: "#ffffff"},
    "nintendo": {False: "#e60012", True: "#e60012"},
    "apple": {False: "#0066cc", True: "#2997ff"},
    "binance": {False: "#fcd535", True: "#fcd535"},
    "clay": {False: "#ff4d8b", True: "#ff4d8b"},
    "claude": {False: "#cc785c", True: "#cc785c"},
}

# Canvas colour: the surface behind everything, also per mode.
CANVAS = {
    "vibrant": {False: "#EEF2FF", True: "#0B1120"},
    "ollama": {False: "#ffffff", True: "#0a0a0a"},
    "nintendo": {False: "#7a8aba", True: "#20242f"},
    "apple": {False: "#f5f5f7", True: "#1d1d1f"},
    "binance": {False: "#ffffff", True: "#0b0e11"},
    "clay": {False: "#fffaf0", True: "#0a1a1a"},
    "claude": {False: "#faf9f5", True: "#181715"},
}

CORE_SELECTORS = [
    "QDialog",
    "QGroupBox",
    "QPushButton",
    "QComboBox",
    "QTabWidget::pane",
    "QTabBar::tab",
    "QScrollArea",
    "QLineEdit",
]


def _stylesheet(theme, is_dark):
    return getattr(gui_utils, f"_build_{theme}_stylesheet")(is_dark)


theme_param = pytest.mark.parametrize("theme", THEMES)
mode_param = pytest.mark.parametrize("is_dark", [False, True], ids=["light", "dark"])


@pytest.mark.unit
def test_valid_themes_are_the_seven_shipped_themes():
    assert set(gui_utils.VALID_THEMES) == set(THEMES)


@pytest.mark.unit
@pytest.mark.parametrize("theme", THEMES)
@pytest.mark.parametrize("is_dark", [False, True], ids=["light", "dark"])
def test_theme_stylesheet_is_substantial(theme, is_dark):
    stylesheet = _stylesheet(theme, is_dark)

    assert len(stylesheet) > 4000
    assert stylesheet.count("{") == stylesheet.count("}")
    assert stylesheet.lstrip().startswith("QDialog")


@pytest.mark.unit
@pytest.mark.parametrize("theme", THEMES)
@pytest.mark.parametrize("is_dark", [False, True], ids=["light", "dark"])
def test_theme_stylesheet_has_no_unresolved_tokens(theme, is_dark):
    stylesheet = _stylesheet(theme, is_dark)

    assert "$" not in stylesheet
    assert "{hairline}" not in stylesheet
    assert "None" not in stylesheet
    # No empty declaration such as "border: ;" left behind by an absent rule.
    assert "border: ;" not in stylesheet
    assert "color: ;" not in stylesheet


@pytest.mark.unit
@pytest.mark.parametrize("theme", THEMES)
@pytest.mark.parametrize("is_dark", [False, True], ids=["light", "dark"])
def test_theme_stylesheet_targets_core_widgets(theme, is_dark):
    stylesheet = _stylesheet(theme, is_dark)

    missing = [selector for selector in CORE_SELECTORS if selector not in stylesheet]
    assert missing == []


@pytest.mark.unit
@pytest.mark.parametrize("theme", THEMES)
@pytest.mark.parametrize("is_dark", [False, True], ids=["light", "dark"])
def test_theme_keeps_its_signature_accent(theme, is_dark):
    stylesheet = _stylesheet(theme, is_dark)

    assert SIGNATURE[theme][is_dark] in stylesheet


@pytest.mark.unit
@pytest.mark.parametrize("theme", THEMES)
@pytest.mark.parametrize("is_dark", [False, True], ids=["light", "dark"])
def test_theme_keeps_its_canvas_colour(theme, is_dark):
    stylesheet = _stylesheet(theme, is_dark)

    assert f"background: {CANVAS[theme][is_dark]};" in stylesheet


@pytest.mark.unit
@theme_param
def test_light_and_dark_stylesheets_differ(theme):
    light = _stylesheet(theme, False)
    dark = _stylesheet(theme, True)

    assert light != dark
    assert f"background: {CANVAS[theme][False]};" in light
    assert f"background: {CANVAS[theme][True]};" in dark


@pytest.mark.unit
def test_table_view_styling_comes_from_the_shared_dialog_stylesheet():
    # Tables live in the legacy dialog stylesheet that is appended to the theme
    # QSS by the dialogs themselves; make sure that contract still holds.
    from superfreetts_addon import constants

    assert "QTableView" in constants.STYLESHEET_DIALOG
    assert "QHeaderView::section" in constants.STYLESHEET_DIALOG


@pytest.mark.unit
def test_all_theme_outputs_are_distinct():
    rendered = {_stylesheet(theme, dark) for theme in THEMES for dark in (False, True)}

    assert len(rendered) == len(THEMES) * 2


@pytest.mark.unit
@theme_param
@pytest.mark.parametrize("is_dark", [False, True], ids=["light", "dark"])
def test_service_tab_css_is_available_for_every_theme(theme, is_dark):
    extra = gui_utils._build_services_extra_css(theme, is_dark)

    assert extra
    assert 'QToolButton[cssClass="sectionToggle"]' in extra
    assert 'QLabel[cssClass="statusBadgeReady"]' in extra
    assert str(gui_utils._SERVICES_TOKENS[theme][is_dark]["sec_bg"]) in extra


@pytest.mark.unit
def test_get_dynamic_stylesheet_uses_active_theme(monkeypatch):
    monkeypatch.setattr(gui_utils, "is_night_mode", lambda: True)

    for theme in THEMES:
        gui_utils.set_active_theme(theme)
        stylesheet = gui_utils.get_dynamic_stylesheet()

        assert stylesheet.startswith(_stylesheet(theme, True))
        assert gui_utils.get_active_theme() == theme

    gui_utils.set_active_theme("vibrant")


@pytest.mark.unit
def test_get_dynamic_stylesheet_appends_services_css(monkeypatch):
    monkeypatch.setattr(gui_utils, "is_night_mode", lambda: False)
    gui_utils.set_active_theme("claude")

    try:
        stylesheet = gui_utils.get_dynamic_stylesheet()
    finally:
        gui_utils.set_active_theme("vibrant")

    assert stylesheet == _stylesheet("claude", False) + gui_utils._build_services_extra_css(
        "claude", False
    )


@pytest.mark.unit
def test_is_night_mode_reads_theme_manager(monkeypatch):
    monkeypatch.setattr(
        gui_utils.aqt.theme, "theme_manager", types.SimpleNamespace(night_mode=True), raising=False
    )
    assert gui_utils.is_night_mode() is True

    monkeypatch.setattr(
        gui_utils.aqt.theme, "theme_manager", types.SimpleNamespace(night_mode=False), raising=False
    )
    assert gui_utils.is_night_mode() is False


@pytest.mark.unit
def test_set_active_theme_falls_back_to_vibrant():
    gui_utils.set_active_theme("does-not-exist")

    assert gui_utils.get_active_theme() == "vibrant"


@pytest.mark.unit
@pytest.mark.parametrize("theme", THEMES)
def test_theme_metrics_are_complete(theme):
    metrics = gui_utils._THEME_METRICS[theme]

    # Radius/padding/weight tokens used by the shared template must exist for
    # every theme; a missing one would render as a literal "$radius_card".
    for key in ("radius_card", "radius_input", "radius_button", "pad_input", "pad_button", "w_button"):
        assert key in metrics and metrics[key]

    assert metrics["radius_card"].endswith("px")


@pytest.mark.unit
@pytest.mark.parametrize("theme", THEMES)
def test_theme_palettes_define_every_role(theme):
    for dark in (False, True):
        tokens = gui_utils._THEME_TOKENS[theme][dark]
        for role in ("canvas", "card", "card_alt", "ink", "mute", "primary", "tab_text_selected"):
            assert role in tokens, f"{theme} is missing {role}"
            assert tokens[role], f"{theme} has an empty {role}"


@pytest.mark.unit
def test_vibrant_pastel_buttons_swap_colours_on_hover():
    dark = False
    stylesheet = _stylesheet("vibrant", dark)
    pastels = gui_utils._VIBRANT_PASTELS[dark]

    for name, (bg, fg) in pastels.items():
        assert f'QPushButton[cssClass="btnPastel{name}"] {{' in stylesheet
        assert f"background: {bg};" in stylesheet
        assert f"color: {fg};" in stylesheet

    assert len(pastels) == 5


@pytest.mark.unit
@pytest.mark.parametrize("theme", ["ollama", "nintendo", "apple", "binance", "clay", "claude"])
def test_flat_themes_render_one_grouped_pastel_rule(theme):
    stylesheet = _stylesheet(theme, False)

    assert "QPushButton[cssClass=\"btnPastelEmerald\"]," in stylesheet
    assert "QPushButton[cssClass=\"btnPastelPurple\"] {" in stylesheet
    # Flat chip: a single shared background for all five classes.
    assert gui_utils._THEME_TOKENS[theme][False]["pastel_bg"] in stylesheet


@pytest.mark.unit
@pytest.mark.parametrize("theme", THEMES)
@pytest.mark.parametrize("is_dark", [False, True], ids=["light", "dark"])
def test_theme_border_radius_follows_palette(theme, is_dark):
    stylesheet = _stylesheet(theme, is_dark)
    metrics = gui_utils._THEME_METRICS[theme]

    card_rule_start = stylesheet.index('QFrame[cssClass="vibrantCard"]')
    card_rule = stylesheet[card_rule_start : stylesheet.index("}", card_rule_start)]
    assert f"border-radius: {metrics['radius_card']};" in card_rule
