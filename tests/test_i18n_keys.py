"""Localisation guards.

A missing English key makes ``i18n.get_text`` return the key itself, so the UI
shows raw ``snake_case`` text.  These tests fail before that can ship:
  * every key used in code must exist in ``locales/en.json``;
  * translated values must use the same ``{0}``-style placeholders as English,
    otherwise ``str.format`` raises at runtime;
  * a missing translation still falls back to English rather than the key.
"""

import importlib.util
import re
from pathlib import Path

from . import mock_anki

mock_anki.mock_all()

from superfreetts_addon import i18n

REPO_ROOT = Path(__file__).resolve().parents[1]
PLACEHOLDER = re.compile(r"\{(\d+)\}")


def _load_audit():
    spec = importlib.util.spec_from_file_location(
        "sftts_i18n_audit", REPO_ROOT / "scripts" / "i18n_audit.py"
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_every_key_used_in_code_exists_in_english():
    audit = _load_audit()
    english = audit.load_locale("en")
    missing = sorted(audit.keys_used_in_code() - set(english))

    assert missing == [], f"missing English strings for: {missing}"


def test_translations_keep_english_placeholders():
    english = i18n.STRINGS["en"]
    problems = []
    for lang, table in i18n.STRINGS.items():
        if lang == "en":
            continue
        for key, value in table.items():
            reference = english.get(key)
            if reference is None:
                problems.append(f"{lang}:{key} has no English key")
                continue
            if set(PLACEHOLDER.findall(value)) != set(PLACEHOLDER.findall(reference)):
                problems.append(f"{lang}:{key} placeholder mismatch")

    assert problems == [], problems


def test_missing_translation_falls_back_to_english():
    # sv has far fewer keys than en; the English text must still be returned.
    key = "mms_manager_install_success_msg"
    assert key in i18n.STRINGS["en"]
    assert key not in i18n.STRINGS["sv"]
    assert i18n.get_text(key, "sv") == i18n.STRINGS["en"][key]


def test_vietnamese_is_complete():
    # Product decision: English and Vietnamese are the supported UI languages;
    # every other locale is allowed to fall back to English.
    missing = sorted(set(i18n.STRINGS["en"]) - set(i18n.STRINGS["vi"]))
    assert missing == [], f"vi.json is missing: {missing}"


def test_locales_only_define_keys_that_english_knows():
    english = set(i18n.STRINGS["en"])
    for lang, table in i18n.STRINGS.items():
        assert set(table) <= english, f"{lang} defines keys missing from en"


def test_language_dropdown_family_is_complete():
    # component_preferences builds this key dynamically, so a missing entry
    # shows the raw key in the language picker.
    english = i18n.STRINGS["en"]
    missing = [
        lang
        for lang in i18n.SUPPORTED_LANGUAGES
        if f"preferences_option_language_{lang.replace('-', '_')}" not in english
    ]
    assert missing == []


def test_unknown_language_falls_back_to_english():
    key = "menu_services_configuration"
    assert i18n.get_text(key, "xx") == i18n.STRINGS["en"][key]
