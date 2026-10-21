"""Unit tests for the text-processing configuration UI/model."""

from unittest.mock import MagicMock

import pytest

from superfreetts_addon import component_text_processing
from superfreetts_addon import config_models
from superfreetts_addon import constants
from superfreetts_addon import i18n


class FakeHyperTTSS:
    def __init__(self):
        self.anki_utils = MagicMock()
        self.anki_utils.run_on_main.side_effect = lambda callback: callback()
        self.anki_utils.wire_typing_timer.return_value = MagicMock()

    def get_ui_language(self):
        return "en"


@pytest.fixture
def hypertts():
    return FakeHyperTTSS()


@pytest.fixture(autouse=True)
def fake_translations(monkeypatch):
    monkeypatch.setattr(i18n, "get_text", lambda key, lang: key)


def _index(row=0, column=0, valid=True):
    index = MagicMock()
    index.isValid.return_value = valid
    index.row.return_value = row
    index.column.return_value = column
    return index


def _rule(rule_type=constants.TextReplacementRuleType.Simple, source="a", target="b"):
    rule = config_models.TextReplacementRule(rule_type)
    rule.source = source
    rule.target = target
    return rule


@pytest.mark.unit
def test_table_headers_and_dimensions(hypertts):
    model = config_models.TextProcessing()
    table = component_text_processing.TextReplacementsTableModel(
        model, MagicMock(), hypertts
    )

    assert table.num_columns() == 3
    assert table.rowCount(None) == 0
    assert table.columnCount(None) == 3
    assert table._get_headers() == [
        "tp_header_type",
        "tp_header_pattern",
        "tp_header_replacement",
    ]


@pytest.mark.unit
def test_table_flags_and_header_data(hypertts):
    model = config_models.TextProcessing()
    table = component_text_processing.TextReplacementsTableModel(
        model, MagicMock(), hypertts
    )
    qt = component_text_processing.aqt.qt

    for column in (0, 1, 2, 99):
        assert table.flags(_index(column=column)) is not None

    assert table.headerData(
        0, qt.Qt.Orientation.Horizontal, qt.Qt.ItemDataRole.DisplayRole
    ) is not None
    assert table.headerData(
        0, qt.Qt.Orientation.Vertical, qt.Qt.ItemDataRole.DisplayRole
    ) is not None


@pytest.mark.unit
def test_table_data_and_data_display(hypertts):
    model = config_models.TextProcessing()
    model.add_text_replacement_rule(_rule())
    table = component_text_processing.TextReplacementsTableModel(
        model, MagicMock(), hypertts
    )
    qt = component_text_processing.aqt.qt

    assert table.data(_index(valid=False), qt.Qt.ItemDataRole.DisplayRole) is not None
    assert table.data(_index(row=5), qt.Qt.ItemDataRole.DisplayRole) is not None
    for column in (0, 1, 2):
        assert table.data(
            _index(column=column), qt.Qt.ItemDataRole.DisplayRole
        ) is not None
    assert table.data_display(None, qt.Qt.ItemDataRole.DisplayRole) is not None
    assert table.data_display("value", qt.Qt.ItemDataRole.DisplayRole) is not None
    assert table.data_display("value", qt.Qt.ItemDataRole.EditRole) is not None


@pytest.mark.unit
def test_table_set_data_updates_rules(hypertts):
    model = config_models.TextProcessing()
    model.add_text_replacement_rule(_rule())
    callback = MagicMock()
    table = component_text_processing.TextReplacementsTableModel(
        model, callback, hypertts
    )
    qt = component_text_processing.aqt.qt

    assert table.setData(
        _index(valid=False), "x", qt.Qt.ItemDataRole.EditRole
    ) is False
    assert table.setData(
        _index(row=5), "x", qt.Qt.ItemDataRole.EditRole
    ) is False
    assert table.setData(
        _index(column=0), "x", qt.Qt.ItemDataRole.EditRole
    ) is False
    assert table.setData(
        _index(column=1), "new source", qt.Qt.ItemDataRole.EditRole
    ) is True
    assert model.text_replacement_rules[0].source == "new source"
    assert table.setData(
        _index(column=2), "new target", qt.Qt.ItemDataRole.EditRole
    ) is True
    assert model.text_replacement_rules[0].target == "new target"
    assert table.setData(
        _index(column=1), "x", qt.Qt.ItemDataRole.DisplayRole
    ) is False
    assert callback.call_count == 2


@pytest.mark.unit
def test_table_add_delete_and_load(hypertts):
    model = config_models.TextProcessing()
    callback = MagicMock()
    table = component_text_processing.TextReplacementsTableModel(
        model, callback, hypertts
    )
    table.layoutChanged = MagicMock()

    table.add_replacement(constants.TextReplacementRuleType.Simple)
    assert len(model.text_replacement_rules) == 1
    assert callback.call_count == 1

    row = MagicMock()
    row.row.return_value = 0
    table.delete_rows(row)
    assert model.text_replacement_rules == []
    assert callback.call_count == 2

    row.row.return_value = 99
    table.delete_rows(row)
    assert callback.call_count == 2

    replacement = config_models.TextProcessing()
    table.load_model(replacement)
    assert table.model is replacement


@pytest.mark.unit
def test_text_processing_settings_serialize_rules(hypertts):
    component = component_text_processing.TextProcessing(hypertts, MagicMock())
    component.model.add_text_replacement_rule(_rule())

    assert component.get_text_processing_settings() == {
        "replacements": [
            {
                "rule_type": "Simple",
                "source": "a",
                "target": "b",
            }
        ]
    }


@pytest.mark.unit
def test_draw_wires_widgets_and_updates_state(hypertts, monkeypatch):
    qt = component_text_processing.aqt.qt
    for name in (
        "QScrollArea",
        "QWidget",
        "QVBoxLayout",
        "QHBoxLayout",
        "QCheckBox",
        "QGroupBox",
        "QLabel",
        "QLineEdit",
        "QTableView",
        "QPushButton",
    ):
        monkeypatch.setattr(qt, name, MagicMock(name=name))

    callback = MagicMock()
    component = component_text_processing.TextProcessing(hypertts, callback)
    widget = component.draw(embedded=True)

    assert widget is component.layout_widget
    assert len(component.processing_controls) == 12
    component.set_text_processing_rules_widget_state()
    component.enabled_checkbox.setChecked.assert_called()
    component.update_controls_enabled()
    for control in component.processing_controls:
        control.setEnabled.assert_called()

    component.enabled_checkbox_change(2)
    assert component.model.enabled is True
    component.enabled_checkbox_change(0)
    assert component.model.enabled is False
    component.html_to_text_line_checkbox_change(2)
    assert component.model.html_to_text_line is True
    component.strip_brackets_change(2)
    assert component.model.strip_brackets is True
    component.strip_cloze_change(2)
    assert component.model.strip_cloze is True
    component.ssml_convert_characters_checkbox_change(2)
    assert component.model.ssml_convert_characters is True
    component.sanitize_special_characters_checkbox_change(2)
    assert component.model.sanitize_special_characters is True
    component.run_replace_rules_after_checkbox_change(2)
    assert component.model.run_replace_rules_after is True
    component.ignore_case_checkbox_change(2)
    assert component.model.ignore_case is True
    assert callback.called


@pytest.mark.unit
def test_draw_non_embedded_returns_scroll_area(hypertts, monkeypatch):
    qt = component_text_processing.aqt.qt
    for name in (
        "QScrollArea",
        "QWidget",
        "QVBoxLayout",
        "QHBoxLayout",
        "QCheckBox",
        "QGroupBox",
        "QLabel",
        "QLineEdit",
        "QTableView",
        "QPushButton",
    ):
        monkeypatch.setattr(qt, name, MagicMock(name=name))

    component = component_text_processing.TextProcessing(hypertts, MagicMock())
    scroll_area = component.draw(embedded=False)
    assert scroll_area is component.scroll_area
    scroll_area.setWidget.assert_called_with(component.layout_widget)


@pytest.mark.unit
def test_update_transformed_text_blank_success_and_error(hypertts, monkeypatch):
    qt = component_text_processing.aqt.qt
    for name in (
        "QScrollArea",
        "QWidget",
        "QVBoxLayout",
        "QHBoxLayout",
        "QCheckBox",
        "QGroupBox",
        "QLabel",
        "QLineEdit",
        "QTableView",
        "QPushButton",
    ):
        monkeypatch.setattr(qt, name, MagicMock(name=name))

    component = component_text_processing.TextProcessing(hypertts, MagicMock())
    component.draw(embedded=True)

    component.sample_text_input.text.return_value = ""
    component.update_transformed_text()
    component.sample_text_transformed_label.setText.assert_called_with("tp_blank_text")

    component.sample_text_input.text.return_value = "hello"
    component.update_transformed_text()
    assert "hello" in component.sample_text_transformed_label.setText.call_args.args[0]

    monkeypatch.setattr(
        component_text_processing.text_utils,
        "process_text",
        MagicMock(side_effect=RuntimeError("boom")),
    )
    component.update_transformed_text()
    assert "boom" in component.sample_text_transformed_label.setText.call_args.args[0]


@pytest.mark.unit
def test_delete_text_replacement_uses_selection(hypertts, monkeypatch):
    qt = component_text_processing.aqt.qt
    for name in (
        "QScrollArea",
        "QWidget",
        "QVBoxLayout",
        "QHBoxLayout",
        "QCheckBox",
        "QGroupBox",
        "QLabel",
        "QLineEdit",
        "QTableView",
        "QPushButton",
    ):
        monkeypatch.setattr(qt, name, MagicMock(name=name))

    component = component_text_processing.TextProcessing(hypertts, MagicMock())
    component.draw(embedded=True)
    component.model.add_text_replacement_rule(_rule())
    component.textReplacementTableModel.layoutChanged = MagicMock()
    component.table_view.selectionModel.return_value.selectedIndexes.return_value = [
        _index()
    ]

    component.delete_text_replacement()
    assert component.model.text_replacement_rules == []
