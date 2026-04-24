import aqt.qt

from typing import Any, List

from . import batch_status
from . import constants
from . import gui_utils
from . import i18n


class FailureReportDialog(aqt.qt.QDialog):
    def __init__(self, hypertts: Any, parent: Any, failure_records: List[batch_status.FailureRecord]) -> None:
        super(aqt.qt.QDialog, self).__init__(parent)
        self.hypertts = hypertts
        self.failure_records = failure_records
        self.add_tag_requested = False

        self.setWindowTitle(self._text("failure_report_title"))
        self.setMinimumSize(860, 420)
        self.setStyleSheet(gui_utils.get_dynamic_stylesheet())

        self._build_ui()

    def _text(self, key: str, **kwargs: Any) -> str:
        text = i18n.get_text(key, self.hypertts.get_ui_language())
        if kwargs:
            return text.format(**kwargs)
        return text

    def _build_ui(self) -> None:
        layout = aqt.qt.QVBoxLayout(self)

        unique_note_ids = {record.note_id for record in self.failure_records}
        preset_names = {record.preset_name for record in self.failure_records if record.preset_name}
        if len(preset_names) > 0:
            summary_text = self._text(
                "failure_report_summary_with_presets",
                failures=len(self.failure_records),
                notes=len(unique_note_ids),
                presets=len(preset_names),
            )
        else:
            summary_text = self._text(
                "failure_report_summary_without_presets",
                failures=len(self.failure_records),
                notes=len(unique_note_ids),
            )

        summary_label = aqt.qt.QLabel(summary_text)
        summary_label.setWordWrap(True)
        layout.addWidget(summary_label)

        self.table = aqt.qt.QTableWidget()
        has_preset_column = any(record.preset_name for record in self.failure_records)
        headers = []
        if has_preset_column:
            headers.append(self._text("failure_report_header_preset"))
        headers.extend([
            self._text('failure_report_header_note_id'),
            self._text('failure_report_header_failed_text'),
            self._text('failure_report_header_error'),
        ])

        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setRowCount(len(self.failure_records))
        self.table.setEditTriggers(aqt.qt.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(aqt.qt.QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(aqt.qt.QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)

        for row_index, failure in enumerate(self.failure_records):
            column_index = 0
            if has_preset_column:
                self._set_table_item(row_index, column_index, failure.preset_name or '')
                column_index += 1
            self._set_table_item(row_index, column_index, str(failure.note_id))
            column_index += 1
            self._set_table_item(row_index, column_index, failure.failed_text)
            column_index += 1
            self._set_table_item(row_index, column_index, failure.error_message)

        header = self.table.horizontalHeader()
        try:
            header.setStretchLastSection(True)
            header.setSectionResizeMode(aqt.qt.QHeaderView.ResizeMode.ResizeToContents)
            text_column = len(headers) - 2
            error_column = len(headers) - 1
            header.setSectionResizeMode(text_column, aqt.qt.QHeaderView.ResizeMode.Stretch)
            header.setSectionResizeMode(error_column, aqt.qt.QHeaderView.ResizeMode.Stretch)
        except AttributeError:
            header.setStretchLastSection(True)
            header.setSectionResizeMode(aqt.qt.QHeaderView.ResizeToContents)
            text_column = len(headers) - 2
            error_column = len(headers) - 1
            header.setSectionResizeMode(text_column, aqt.qt.QHeaderView.Stretch)
            header.setSectionResizeMode(error_column, aqt.qt.QHeaderView.Stretch)

        layout.addWidget(self.table, stretch=1)

        button_layout = aqt.qt.QHBoxLayout()
        button_layout.addStretch()
        self.add_tag_button = aqt.qt.QPushButton(
            self._text("failure_report_add_tag", tag=constants.WORKFLOW_ERROR_TAG)
        )
        self.ignore_button = aqt.qt.QPushButton(self._text("failure_report_ignore_close"))
        gui_utils.configure_pastel_button(self.add_tag_button, style_name='rose', is_primary=True, font_size=11)
        gui_utils.configure_secondary_button(self.ignore_button, min_width=130)
        self.add_tag_button.clicked.connect(self.add_tag_button_pressed)
        self.ignore_button.clicked.connect(self.reject)
        button_layout.addWidget(self.add_tag_button)
        button_layout.addWidget(self.ignore_button)
        layout.addLayout(button_layout)

    def _set_table_item(self, row_index: int, column_index: int, value: str) -> None:
        item = aqt.qt.QTableWidgetItem(value)
        item.setToolTip(value)
        self.table.setItem(row_index, column_index, item)

    def add_tag_button_pressed(self) -> None:
        self.add_tag_requested = True
        self.accept()


def show_failure_report(
    hypertts: Any,
    parent: Any,
    failure_records: List[batch_status.FailureRecord],
) -> bool:
    if len(failure_records) == 0:
        return False
    dialog = FailureReportDialog(hypertts, parent, failure_records)
    dialog.exec()
    return dialog.add_tag_requested
