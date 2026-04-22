import aqt.qt

from typing import Any, List, Optional

from . import batch_status
from . import errors
from . import gui_utils
from . import logging_utils

logger = logging_utils.get_child_logger(__name__)


class WorkflowDialog(aqt.qt.QDialog):
    def __init__(self, hypertts: Any, note_id_list: List[int]) -> None:
        super(aqt.qt.QDialog, self).__init__()
        self.hypertts = hypertts
        self.note_id_list = note_id_list
        self.current_batch_status: Optional[batch_status.BatchStatus] = None
        self.workflow_cancelled = False
        self.workflow_running = False
        self.workflow_preset_ids: List[str] = []
        self.current_preset_name = ""
        self.current_preset_index = 0
        self.total_presets = 0

        self.setWindowFlag(aqt.qt.Qt.WindowType.WindowMinMaxButtonsHint, True)
        self.setStyleSheet(gui_utils.get_dynamic_stylesheet())
        self.setWindowTitle("Super Free TTS: Workflow")
        self.resize(860, 560)

        self._build_ui()
        self._populate_available_presets()
        self._refresh_button_states()

    def _build_ui(self) -> None:
        self.main_layout = aqt.qt.QVBoxLayout(self)

        info_label = aqt.qt.QLabel(
            f"Run multiple presets in sequence on the same {len(self.note_id_list)} selected notes."
        )
        info_label.setWordWrap(True)
        self.main_layout.addWidget(info_label)

        lists_layout = aqt.qt.QHBoxLayout()

        available_group = aqt.qt.QGroupBox("Available Presets")
        available_layout = aqt.qt.QVBoxLayout()
        self.available_list = aqt.qt.QListWidget()
        self.available_list.setSelectionMode(aqt.qt.QAbstractItemView.SelectionMode.ExtendedSelection)
        available_layout.addWidget(self.available_list)
        available_group.setLayout(available_layout)
        lists_layout.addWidget(available_group, stretch=1)

        controls_layout = aqt.qt.QVBoxLayout()
        controls_layout.addStretch()
        self.add_button = aqt.qt.QPushButton("Add ->")
        self.remove_button = aqt.qt.QPushButton("<- Remove")
        self.up_button = aqt.qt.QPushButton("Up")
        self.down_button = aqt.qt.QPushButton("Down")
        self.clear_button = aqt.qt.QPushButton("Clear")
        controls_layout.addWidget(self.add_button)
        controls_layout.addWidget(self.remove_button)
        controls_layout.addWidget(self.up_button)
        controls_layout.addWidget(self.down_button)
        controls_layout.addWidget(self.clear_button)
        controls_layout.addStretch()
        lists_layout.addLayout(controls_layout)

        workflow_group = aqt.qt.QGroupBox("Workflow Order")
        workflow_layout = aqt.qt.QVBoxLayout()
        self.workflow_list = aqt.qt.QListWidget()
        self.workflow_list.setSelectionMode(aqt.qt.QAbstractItemView.SelectionMode.SingleSelection)
        workflow_layout.addWidget(self.workflow_list)
        workflow_group.setLayout(workflow_layout)
        lists_layout.addWidget(workflow_group, stretch=1)

        self.main_layout.addLayout(lists_layout)

        progress_group = aqt.qt.QGroupBox("Progress")
        progress_layout = aqt.qt.QVBoxLayout()
        self.workflow_status_label = aqt.qt.QLabel("Ready.")
        self.workflow_status_label.setWordWrap(True)
        self.current_preset_label = aqt.qt.QLabel("Current preset: -")
        self.preset_progress = aqt.qt.QProgressBar()
        self.note_progress = aqt.qt.QProgressBar()
        self.note_progress.setFormat("%p%")
        progress_layout.addWidget(self.workflow_status_label)
        progress_layout.addWidget(self.current_preset_label)
        progress_layout.addWidget(self.preset_progress)
        progress_layout.addWidget(self.note_progress)
        progress_group.setLayout(progress_layout)
        self.main_layout.addWidget(progress_group)

        buttons_layout = aqt.qt.QHBoxLayout()
        buttons_layout.addStretch()
        self.run_button = aqt.qt.QPushButton("Run Workflow")
        self.stop_button = aqt.qt.QPushButton("Stop")
        self.close_button = aqt.qt.QPushButton("Close")
        self.stop_button.setEnabled(False)
        buttons_layout.addWidget(self.run_button)
        buttons_layout.addWidget(self.stop_button)
        buttons_layout.addWidget(self.close_button)
        self.main_layout.addLayout(buttons_layout)

        self.add_button.clicked.connect(self._add_selected_presets)
        self.remove_button.clicked.connect(self._remove_selected_preset)
        self.up_button.clicked.connect(lambda: self._move_selected_preset(-1))
        self.down_button.clicked.connect(lambda: self._move_selected_preset(1))
        self.clear_button.clicked.connect(self._clear_workflow)
        self.run_button.clicked.connect(self._run_workflow)
        self.stop_button.clicked.connect(self._stop_workflow)
        self.close_button.clicked.connect(self.close)
        self.available_list.itemSelectionChanged.connect(self._refresh_button_states)
        self.workflow_list.itemSelectionChanged.connect(self._refresh_button_states)

    def _populate_available_presets(self) -> None:
        self.available_list.clear()
        for preset in self.hypertts.get_preset_list():
            item = aqt.qt.QListWidgetItem(preset.name)
            item.setData(aqt.qt.Qt.ItemDataRole.UserRole, preset.id)
            self.available_list.addItem(item)

    def _refresh_button_states(self) -> None:
        running = self.workflow_running
        has_available_selection = len(self.available_list.selectedItems()) > 0
        has_workflow_selection = self.workflow_list.currentRow() >= 0
        has_workflow_items = self.workflow_list.count() > 0

        self.add_button.setEnabled((not running) and has_available_selection)
        self.remove_button.setEnabled((not running) and has_workflow_selection)
        self.up_button.setEnabled((not running) and has_workflow_selection and self.workflow_list.currentRow() > 0)
        self.down_button.setEnabled(
            (not running)
            and has_workflow_selection
            and self.workflow_list.currentRow() < self.workflow_list.count() - 1
        )
        self.clear_button.setEnabled((not running) and has_workflow_items)
        self.run_button.setEnabled((not running) and has_workflow_items)
        self.stop_button.setEnabled(running)
        self.close_button.setEnabled(not running)

    def _add_selected_presets(self) -> None:
        for item in self.available_list.selectedItems():
            new_item = aqt.qt.QListWidgetItem(item.text())
            new_item.setData(aqt.qt.Qt.ItemDataRole.UserRole, item.data(aqt.qt.Qt.ItemDataRole.UserRole))
            self.workflow_list.addItem(new_item)
        self._refresh_button_states()

    def _remove_selected_preset(self) -> None:
        row = self.workflow_list.currentRow()
        if row >= 0:
            self.workflow_list.takeItem(row)
        self._refresh_button_states()

    def _move_selected_preset(self, direction: int) -> None:
        row = self.workflow_list.currentRow()
        if row < 0:
            return
        target_row = row + direction
        if target_row < 0 or target_row >= self.workflow_list.count():
            return
        item = self.workflow_list.takeItem(row)
        self.workflow_list.insertItem(target_row, item)
        self.workflow_list.setCurrentRow(target_row)
        self._refresh_button_states()

    def _clear_workflow(self) -> None:
        self.workflow_list.clear()
        self._refresh_button_states()

    def _set_running_state(self, running: bool) -> None:
        self.workflow_running = running
        self._refresh_button_states()

    def _run_workflow(self) -> None:
        if self.workflow_list.count() == 0:
            raise errors.HyperTTSError("Add at least one preset to the workflow.")

        self.workflow_preset_ids = [
            self.workflow_list.item(i).data(aqt.qt.Qt.ItemDataRole.UserRole)
            for i in range(self.workflow_list.count())
        ]
        self.workflow_cancelled = False
        self.current_preset_index = 0
        self.total_presets = len(self.workflow_preset_ids)
        self.preset_progress.setRange(0, self.total_presets)
        self.preset_progress.setValue(0)
        self.note_progress.setRange(0, 100)
        self.note_progress.setValue(0)
        self.workflow_status_label.setText("Starting workflow...")
        self.current_preset_label.setText("Current preset: -")
        self._set_running_state(True)

        self.hypertts.anki_utils.run_in_background_collection_op(
            self,
            self._run_workflow_collection_op,
            self._run_workflow_done,
        )

    def _stop_workflow(self) -> None:
        self.workflow_cancelled = True
        if self.current_batch_status is not None:
            self.current_batch_status.stop()
        self.workflow_status_label.setText("Stopping workflow...")

    def _run_workflow_collection_op(self, anki_collection: Any) -> None:
        for preset_index, preset_id in enumerate(self.workflow_preset_ids, start=1):
            if self.workflow_cancelled:
                break

            preset = self.hypertts.load_preset(preset_id)
            self.current_preset_index = preset_index
            self.current_preset_name = preset.name
            self.current_batch_status = batch_status.BatchStatus(
                self.hypertts.anki_utils, self.note_id_list, self
            )

            self.hypertts.anki_utils.run_on_main(
                lambda idx=preset_index, total=self.total_presets, name=preset.name: self._workflow_preset_started(
                    idx, total, name
                )
            )
            self.hypertts.process_batch_audio(
                self.note_id_list,
                preset,
                self.current_batch_status,
                anki_collection,
            )

            if not self.current_batch_status.must_continue:
                self.workflow_cancelled = True
                break

        self.current_batch_status = None

    def _run_workflow_done(self, result: Any) -> None:
        logger.debug(f"workflow finished, result: {result}")
        self.hypertts.anki_utils.run_on_main(self._finish_workflow_ui)

    def _finish_workflow_ui(self) -> None:
        completed = not self.workflow_cancelled
        if completed:
            self.workflow_status_label.setText("Workflow completed.")
            self.current_preset_label.setText(
                f"Current preset: done ({self.total_presets}/{self.total_presets})"
            )
            self.preset_progress.setValue(self.total_presets)
            self.note_progress.setValue(100)
        else:
            self.workflow_status_label.setText("Workflow stopped.")
        self._set_running_state(False)

    def _workflow_preset_started(self, preset_index: int, total_presets: int, preset_name: str) -> None:
        self.preset_progress.setRange(0, total_presets)
        self.preset_progress.setValue(max(0, preset_index - 1))
        self.note_progress.setValue(0)
        self.current_preset_label.setText(
            f"Current preset: {preset_name} ({preset_index}/{total_presets})"
        )
        self.workflow_status_label.setText(f"Running preset: {preset_name}")

    def batch_start(self) -> None:
        pass

    def batch_end(self, completed: bool) -> None:
        def update() -> None:
            if completed:
                self.note_progress.setValue(100)
                self.preset_progress.setValue(self.current_preset_index)
                self.workflow_status_label.setText(
                    f"Completed preset: {self.current_preset_name}"
                )
            else:
                self.workflow_status_label.setText(
                    f"Stopped during preset: {self.current_preset_name}"
                )

        self.hypertts.anki_utils.run_on_main(update)

    def batch_change(
        self,
        note_id: int,
        row: int,
        total_count: int,
        completed_count: int,
        start_time: Any,
        current_time: Any,
    ) -> None:
        current_batch_status = self.current_batch_status
        if current_batch_status is None:
            return

        if current_batch_status.total_unique_tasks > 0:
            progress_done = current_batch_status.unique_tasks_completed
            progress_total = current_batch_status.total_unique_tasks
        else:
            progress_done = completed_count
            progress_total = total_count

        progress_percent = 0
        if progress_total > 0:
            progress_percent = int((progress_done / progress_total) * 100)
        status_message = current_batch_status.status_message or f"Processing note {note_id}"

        self.hypertts.anki_utils.run_on_main(
            lambda pct=progress_percent, msg=status_message: self._update_note_progress(pct, msg)
        )

    def _update_note_progress(self, progress_percent: int, status_message: str) -> None:
        self.note_progress.setValue(max(0, min(100, progress_percent)))
        self.workflow_status_label.setText(
            f"{status_message} [{self.current_preset_name}]"
        )

    def closeEvent(self, event: Any) -> None:
        if self.workflow_running:
            event.ignore()
            return
        super(aqt.qt.QDialog, self).closeEvent(event)


def create_workflow_dialog_browser(hypertts: Any, note_id_list: List[int]) -> None:
    if len(note_id_list) == 0:
        raise errors.NoNotesSelected()

    dialog = WorkflowDialog(hypertts, note_id_list)
    hypertts.anki_utils.wait_for_dialog_input(dialog, "workflow")
