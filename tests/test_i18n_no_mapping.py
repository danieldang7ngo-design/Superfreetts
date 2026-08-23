"""
Regression test: the 'no mapping rules' navigation dialog keys must exist
(with a non-empty value) in every supported locale, so Add Audio guidance is
available in all languages (no silent English fallback).
"""
import json
import os

import pytest

from superfreetts_addon import i18n

ADDON_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src", "superfreetts")
LOCALES_DIR = os.path.join(ADDON_DIR, "superfreetts_addon", "locales")

KEYS = [
    "editor_no_mapping_title",
    "editor_no_mapping_message",
    "editor_no_mapping_informative",
    "editor_no_mapping_configure",
    "editor_no_mapping_preview",
]


@pytest.mark.unit
class TestNoMappingI18n:
    @pytest.mark.parametrize("lang", i18n.SUPPORTED_LANGUAGES)
    def test_no_mapping_keys_present(self, lang):
        path = os.path.join(LOCALES_DIR, f"{lang}.json")
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        for key in KEYS:
            assert key in data, f"{key} missing in {lang}"
            assert isinstance(data[key], str) and data[key].strip(), f"{key} empty in {lang}"