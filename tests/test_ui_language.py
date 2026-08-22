"""
Tests for first-run UI language detection (matching Anki's interface language)
and the Welcome dialog language picker support.
"""
import sys
from types import SimpleNamespace

import pytest

from superfreetts_addon import config_store
from superfreetts_addon import i18n


@pytest.mark.unit
class TestDetectAnkiLanguage:
    """detect_anki_language() maps Anki's lang to a supported addon language."""

    def _patch_lang(self, monkeypatch, lang):
        fake = SimpleNamespace(current_lang=lang)
        monkeypatch.setitem(sys.modules, "anki.lang", fake)
        return fake

    def test_supported_language(self, monkeypatch):
        self._patch_lang(monkeypatch, "ja")
        assert config_store.detect_anki_language() == "ja"

    def test_vietnamese(self, monkeypatch):
        self._patch_lang(monkeypatch, "vi")
        assert config_store.detect_anki_language() == "vi"

    def test_unsupported_falls_back_to_english(self, monkeypatch):
        self._patch_lang(monkeypatch, "fr")
        assert config_store.detect_anki_language() == "en"

    def test_empty_falls_back_to_english(self, monkeypatch):
        self._patch_lang(monkeypatch, "")
        assert config_store.detect_anki_language() == "en"

    def test_import_error_falls_back_to_english(self, monkeypatch):
        monkeypatch.delitem(sys.modules, "anki.lang", raising=False)
        assert config_store.detect_anki_language() == "en"


@pytest.mark.unit
class TestEnsureUiLanguage:
    """ensure_ui_language() only overrides the default on first install."""

    def _make_store(self):
        store_cfg = {"preferences": {"ui_language": "vi"}}
        written = {}

        class FakeAnkiUtils:
            def get_config(self):
                return store_cfg

            def write_config(self, config):
                written["config"] = config

        cs = config_store.ConfigStore(FakeAnkiUtils(), None)
        cs.config = store_cfg
        return cs, written

    def test_first_install_sets_detected_language(self, monkeypatch):
        fake = SimpleNamespace(current_lang="ja")
        monkeypatch.setitem(sys.modules, "anki.lang", fake)
        cs, _ = self._make_store()
        cs.ensure_ui_language(True)
        assert cs.get_ui_language() == "ja"

    def test_not_first_install_keeps_language(self, monkeypatch):
        fake = SimpleNamespace(current_lang="ja")
        monkeypatch.setitem(sys.modules, "anki.lang", fake)
        cs, _ = self._make_store()
        cs.ensure_ui_language(False)
        assert cs.get_ui_language() == "vi"