import os
import sys

import pytest

from tests import mock_anki

mock_anki.mock_all()

addon_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, addon_dir)
sys.path.insert(0, os.path.join(addon_dir, "external"))

from superfreetts_addon import config_models, constants, errors, source_text_resolver


def test_get_source_text_simple_field():
    note = {"Front": "hello"}
    source = config_models.BatchSource(mode=constants.BatchMode.simple, source_field="Front")

    assert source_text_resolver.get_source_text(note, source, None) == "hello"


def test_get_source_text_missing_field_raises():
    note = {"Front": "hello"}
    source = config_models.BatchSource(mode=constants.BatchMode.simple, source_field="Missing")

    with pytest.raises(errors.SourceFieldNotFoundError):
        source_text_resolver.get_source_text(note, source, None)


def test_get_source_text_override_wins():
    note = {"Front": "hello"}
    source = config_models.BatchSource(mode=constants.BatchMode.simple, source_field="Front")

    assert source_text_resolver.get_source_text(note, source, "selected") == "selected"


def test_expand_simple_template_uses_note_fields():
    note = {"Front": "hello", "Back": "world"}
    source = config_models.BatchSource(mode=constants.BatchMode.template, source_template="{Front} {Back}")

    assert source_text_resolver.get_source_text(note, source, None) == "hello world"


def test_advanced_template_lite_error():
    note = {"Front": "hello"}
    source = config_models.BatchSource(mode=constants.BatchMode.advanced_template, source_template="result = 'x'")

    with pytest.raises(errors.SuperFreeTTSError):
        source_text_resolver.get_source_text(note, source, None, "en")


def test_text_processing_cache_key_is_stable_for_equivalent_models():
    left = config_models.TextProcessing()
    right = config_models.TextProcessing()

    assert source_text_resolver.text_processing_cache_key("hello", left) == source_text_resolver.text_processing_cache_key("hello", right)


def test_process_text_pipeline():
    # Verify resolving works with HTML & cloze markers
    tp = config_models.TextProcessing()
    tp.html_to_text_line = True
    tp.strip_cloze = True
    tp.strip_brackets = True

    resolved = source_text_resolver.process_text("<b>{{c1::word}}</b> (ignore)", tp)
    assert resolved == "word "


def test_process_text_empty_raises():
    tp = config_models.TextProcessing()
    tp.strip_brackets = True
    with pytest.raises(errors.SourceTextEmpty):
        source_text_resolver.process_text("(ignore)", tp)


