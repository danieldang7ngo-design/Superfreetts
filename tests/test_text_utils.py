import pytest
from superfreetts_addon import text_utils, config_models, constants

@pytest.mark.unit
def test_strip_html_tags():
    # basic tags
    assert text_utils.strip_html("hello <b>world</b>") == "hello world"
    # nested tags
    assert text_utils.strip_html("<div>hello <i>world</i>!</div>") == "hello world!"
    # entities
    assert text_utils.strip_html("A &amp; B &lt; C") == "A & B < C"
    # empty input
    assert text_utils.strip_html("") == ""

@pytest.mark.unit
def test_strip_cloze_markers():
    # {{c1::word}}
    assert text_utils.strip_cloze_markers("hello {{c1::world}}") == "hello world"
    # {{c1::word::hint}}
    assert text_utils.strip_cloze_markers("hello {{c2::world::hint}}") == "hello world"
    # no-cloze passthrough
    assert text_utils.strip_cloze_markers("hello world") == "hello world"

@pytest.mark.unit
def test_strip_brackets():
    # parentheses, brackets, braces, angle brackets
    assert text_utils.strip_brackets("hello (secret) world [skip] {hide} <tag>") == "hello  world   "

@pytest.mark.unit
def test_strip_sound_tag():
    assert text_utils.strip_sound_tag("[sound:my_audio.mp3]") == ""
    assert text_utils.strip_sound_tag("hello [sound:my_audio.mp3] world") == "hello  world"

@pytest.mark.unit
def test_apply_custom_replacements():
    tp = config_models.TextProcessing()
    # Simple replacement
    rule1 = config_models.TextReplacementRule(constants.TextReplacementRuleType.Simple)
    rule1.source = "apple"
    rule1.target = "orange"
    tp.add_text_replacement_rule(rule1)
    
    # Regex replacement
    rule2 = config_models.TextReplacementRule(constants.TextReplacementRuleType.Regex)
    rule2.source = r"\d+"
    rule2.target = "NUMBER"
    tp.add_text_replacement_rule(rule2)

    assert text_utils.process_text_replacement("I have 5 apples", tp) == "I have NUMBER oranges"

@pytest.mark.unit
def test_process_text():
    tp = config_models.TextProcessing()
    tp.enabled = True
    tp.html_to_text_line = True
    tp.strip_brackets = True
    tp.strip_cloze = True
    tp.ssml_convert_characters = True
    tp.run_replace_rules_after = True

    # Test full processing pipeline
    input_text = "<b>Hello</b> (world) {{c1::apples}} & oranges [sound:test.mp3]"
    expected = "Hello  apples &amp; oranges"
    assert text_utils.process_text(input_text, tp) == expected

@pytest.mark.unit
def test_process_text_disabled():
    tp = config_models.TextProcessing()
    tp.enabled = False
    
    input_text = "<b>Hello</b> (world) [sound:test.mp3]"
    assert text_utils.process_text(input_text, tp) == "<b>Hello</b> (world)"
