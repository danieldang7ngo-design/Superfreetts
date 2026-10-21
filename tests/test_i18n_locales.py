"""All supported UI languages remain available, with English as fallback."""

import pytest

from superfreetts_addon import i18n


EXPECTED_LANGUAGES = ["en", "vi", "ko", "zh-CN", "zh-TW", "ja", "sv"]


@pytest.mark.unit
def test_all_expected_locales_are_loaded():
    assert i18n.SUPPORTED_LANGUAGES == EXPECTED_LANGUAGES
    for language in EXPECTED_LANGUAGES:
        assert language in i18n.STRINGS
        assert i18n.STRINGS[language], f"{language}.json is empty"


@pytest.mark.unit
def test_incomplete_locale_falls_back_to_english():
    # Keep every language visible even when a translation is missing; a
    # missing key must still produce usable English text, never the raw key.
    assert i18n.get_text("button_close", "sv")
    assert i18n.get_text("button_close", "not-a-language") == i18n.get_text(
        "button_close", "en"
    )
