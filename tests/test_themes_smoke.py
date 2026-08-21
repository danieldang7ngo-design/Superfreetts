"""
Smoke tests for all UI theme stylesheet builders.
Verifies every theme produces a non-empty stylesheet in both light and dark.
"""
import pytest

from superfreetts_addon import gui_utils


@pytest.mark.unit
class TestThemeBuilders:
    """Each theme builder must produce a usable stylesheet."""

    # Build directly via get_dynamic_stylesheet by setting the active theme.
    @pytest.mark.parametrize("theme", gui_utils.VALID_THEMES)
    def test_theme_builds_stylesheet(self, theme):
        gui_utils.set_active_theme(theme)
        css = gui_utils.get_dynamic_stylesheet()
        assert isinstance(css, str)
        assert len(css) > 100

    @pytest.mark.parametrize("theme", gui_utils.VALID_THEMES)
    def test_theme_builders_light_dark(self, theme):
        # Call each builder directly with dark=True / dark=False.
        builders = {
            "vibrant": gui_utils._build_vibrant_stylesheet,
            "ollama": gui_utils._build_ollama_stylesheet,
            "apple": gui_utils._build_apple_stylesheet,
            "nintendo": gui_utils._build_nintendo_stylesheet,
            "binance": gui_utils._build_binance_stylesheet,
            "clay": gui_utils._build_clay_stylesheet,
            "claude": gui_utils._build_claude_stylesheet,
        }
        builder = builders[theme]
        for dark in (False, True):
            css = builder(dark)
            assert isinstance(css, str)
            assert len(css) > 100

    def test_valid_themes_list_complete(self):
        expected = {"vibrant", "ollama", "apple", "nintendo", "binance", "clay", "claude"}
        assert set(gui_utils.VALID_THEMES) == expected

    def test_invalid_theme_falls_back(self):
        gui_utils.set_active_theme("not_a_real_theme")
        assert gui_utils.get_active_theme() == "vibrant"

    def test_get_active_theme_default(self):
        gui_utils.set_active_theme("vibrant")
        assert gui_utils.get_active_theme() == "vibrant"

    def test_set_active_theme_valid_themes(self):
        for theme in gui_utils.VALID_THEMES:
            gui_utils.set_active_theme(theme)
            assert gui_utils.get_active_theme() == theme

    @pytest.mark.parametrize("theme", gui_utils.VALID_THEMES)
    def test_services_extra_css_present(self, theme):
        """The Services tab theme selectors must be present for every theme."""
        gui_utils.set_active_theme(theme)
        css = gui_utils.get_dynamic_stylesheet()
        for selector in (
            'sectionToggle',
            'setupAction',
            'serviceSeparator',
            'statusBadgeReady',
            'statusBadgeSetup',
            'statusBadgeDisabled',
            'statusBadgeFree',
            'statusBadgeRecommended',
        ):
            assert f'cssClass="{selector}"' in css, f"missing {selector} in {theme}"