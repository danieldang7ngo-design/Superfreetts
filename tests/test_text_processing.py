import os
import sys

from tests import mock_anki

mock_anki.mock_all()

addon_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, addon_dir)
sys.path.insert(0, os.path.join(addon_dir, "external"))

from superfreetss_addon import config_models, constants, text_utils


def make_text_processing(**overrides):
    model = config_models.TextProcessing()
    model.html_to_text_line = False
    model.strip_brackets = False
    model.strip_cloze = False
    model.ssml_convert_characters = False
    model.run_replace_rules_after = False
    model.ignore_case = False
    for key, value in overrides.items():
        setattr(model, key, value)
    return model


def test_default_text_processing_keeps_parentheses_and_square_brackets():
    model = config_models.TextProcessing()

    result = text_utils.process_text("hello (secret) world [skip] {hide}", model)

    assert result == "hello (secret) world [skip] {hide}"


def test_text_processing_can_be_disabled_without_losing_rule_settings():
    model = make_text_processing(strip_brackets=True, html_to_text_line=True)
    model.enabled = False

    result = text_utils.process_text("hello <b>(secret)</b> [sound:old.mp3]", model)

    assert result == "hello <b>(secret)</b>"
    assert model.strip_brackets is True
    assert model.html_to_text_line is True


def test_text_processing_serializes_enabled_flag():
    model = config_models.TextProcessing()
    model.enabled = False

    result = model.serialize()

    assert result["enabled"] is False


def test_strip_brackets_removes_supported_bracket_content():
    model = make_text_processing(strip_brackets=True)

    result = text_utils.process_text("hello (secret) world [skip] {hide} <tag> end", model)

    assert result == "hello  world    end"


def test_html_to_text_removes_tags_and_decodes_entities():
    model = make_text_processing(html_to_text_line=True)

    result = text_utils.process_text("hello <b>bold</b> &amp; nice", model)

    assert result == "hello bold & nice"


def test_strip_cloze_markers_keeps_visible_answer_text():
    model = make_text_processing(strip_cloze=True)

    result = text_utils.process_text("I like {{c1::apples}} and {{c2::oranges::hint}}.", model)

    assert result == "I like apples and oranges."


def test_ssml_character_conversion_escapes_reserved_characters():
    model = make_text_processing(ssml_convert_characters=True)

    result = text_utils.process_text("A & B < C > D", model)

    assert result == "A &amp; B &lt; C &gt; D"


def test_simple_replacement_rule_replaces_literal_text():
    model = make_text_processing()
    rule = config_models.TextReplacementRule(constants.TextReplacementRuleType.Simple)
    rule.source = "foo"
    rule.target = "bar"
    model.add_text_replacement_rule(rule)

    result = text_utils.process_text("foo fighters", model)

    assert result == "bar fighters"


def test_regex_replacement_rule_can_ignore_case():
    model = make_text_processing(ignore_case=True)
    rule = config_models.TextReplacementRule(constants.TextReplacementRuleType.Regex)
    rule.source = "hello"
    rule.target = "hi"
    model.add_text_replacement_rule(rule)

    result = text_utils.process_text("HELLO Hello hello", model)

    assert result == "hi hi hi"


def test_replacement_rules_can_run_after_cleanup_rules():
    model = make_text_processing(strip_brackets=True, run_replace_rules_after=True)
    rule = config_models.TextReplacementRule(constants.TextReplacementRuleType.Simple)
    rule.source = "hello  world"
    rule.target = "clean"
    model.add_text_replacement_rule(rule)

    result = text_utils.process_text("hello (skip) world", model)

    assert result == "clean"
