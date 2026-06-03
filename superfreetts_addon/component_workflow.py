import aqt.qt

from typing import Any, List, Optional

from . import batch_status
from . import component_failure_report
from . import config_models
from . import constants
from . import errors
from . import gui_utils
from . import i18n
from . import logging_utils

logger = logging_utils.get_child_logger(__name__)

UNSAVED_NEW_WORKFLOW = 'UNSAVED_NEW_WORKFLOW'


class WorkflowDialog(aqt.qt.QDialog):
    def __init__(
        self,
        hypertts: Any,
        note_id_list: List[int],
        workflow_id: Optional[str] = None,
        autorun: bool = False,
    ) -> None:
        super(aqt.qt.QDialog, self).__init__()
        self.hypertts = hypertts
        self.note_id_list = note_id_list
        self.current_batch_status: Optional[batch_status.BatchStatus] = None
        self.workflow_cancelled = False
        self.workflow_running = False
        self.skip_close_prompt = False
        self.current_preset_name = ""
        self.current_preset_index = 0
        self.total_presets = 0
        self.workflow_model: Optional[config_models.WorkflowConfig] = None
        self.model_changed = False
        self.last_saved_workflow_id = None
        self.combobox_suspend_events = False
        self.autorun = autorun
        self.workflow_failure_records: List[batch_status.FailureRecord] = []
        self.failed_note_ids_to_tag: List[int] = []
        self.pending_generated_audio = {}
        self.workflow_operation: Optional[str] = None
        self.apply_workflow_indices: List[int] = []

        self.setWindowFlag(aqt.qt.Qt.WindowType.WindowMinMaxButtonsHint, True)
        self.setStyleSheet(gui_utils.get_dynamic_stylesheet())
        self.setWindowTitle(self._text("workflow_dialog_title"))
        self.resize(920, 620)

        self._build_ui()
        self._populate_available_presets()
        self.new_workflow()

        if workflow_id != None:
            self.load_workflow(workflow_id)

        if self.autorun:
            aqt.qt.QTimer.singleShot(0, self.run_workflow_button_pressed)

    def _text(self, key: str, **kwargs: Any) -> str:
        text = i18n.get_text(key, self.hypertts.get_ui_language())
        if kwargs:
            return text.format(**kwargs)
        return text

    def _build_ui(self) -> None:
        lang = self.hypertts.get_ui_language()
        self.main_layout = aqt.qt.QVBoxLayout(self)

        top_layout = aqt.qt.QHBoxLayout()
        top_layout.addWidget(aqt.qt.QLabel(self._text("workflow_label_name")))
        self.workflow_name_combobox = aqt.qt.QComboBox()
        top_layout.addWidget(self.workflow_name_combobox, stretch=1)

        self.new_button = aqt.qt.QPushButton(i18n.get_text("button_new", lang))
        self.open_button = aqt.qt.QPushButton(i18n.get_text('button_open', lang))
        self.save_button = aqt.qt.QPushButton(i18n.get_text('button_save', lang))
        self.duplicate_button = aqt.qt.QPushButton(i18n.get_text('button_duplicate', lang))
        self.rename_button = aqt.qt.QPushButton(i18n.get_text('button_rename', lang))
        self.delete_button = aqt.qt.QPushButton(i18n.get_text('button_delete', lang))

        for button in [
            self.new_button,
            self.open_button,
            self.save_button,
            self.duplicate_button,
            self.rename_button,
            self.delete_button,
        ]:
            top_layout.addWidget(button)

        self.main_layout.addLayout(top_layout)

        info_label = aqt.qt.QLabel(
            self._text("workflow_info_selected_notes", count=len(self.note_id_list))
        )
        info_label.setWordWrap(True)
        self.main_layout.addWidget(info_label)

        lists_layout = aqt.qt.QHBoxLayout()

        available_group = aqt.qt.QGroupBox(self._text("workflow_available_presets"))
        available_layout = aqt.qt.QVBoxLayout()
        self.available_list = aqt.qt.QListWidget()
        self.available_list.setSelectionMode(aqt.qt.QAbstractItemView.SelectionMode.ExtendedSelection)
        available_layout.addWidget(self.available_list)
        available_group.setLayout(available_layout)
        lists_layout.addWidget(available_group, stretch=1)

        controls_layout = aqt.qt.QVBoxLayout()
        controls_layout.addStretch()
        self.add_button = aqt.qt.QPushButton(self._text("workflow_add"))
        self.remove_button = aqt.qt.QPushButton(self._text("workflow_remove"))
        self.up_button = aqt.qt.QPushButton(self._text("workflow_up"))
        self.down_button = aqt.qt.QPushButton(self._text("workflow_down"))
        self.clear_button = aqt.qt.QPushButton(self._text("workflow_clear"))
        for button in [
            self.add_button,
            self.remove_button,
            self.up_button,
            self.down_button,
            self.clear_button,
        ]:
            controls_layout.addWidget(button)
        controls_layout.addStretch()
        lists_layout.addLayout(controls_layout)

        workflow_group = aqt.qt.QGroupBox(self._text("workflow_order"))
        workflow_layout = aqt.qt.QVBoxLayout()
        self.workflow_list = aqt.qt.QListWidget()
        self.workflow_list.setSelectionMode(aqt.qt.QAbstractItemView.SelectionMode.SingleSelection)
        workflow_layout.addWidget(self.workflow_list)
        workflow_group.setLayout(workflow_layout)
        lists_layout.addWidget(workflow_group, stretch=1)

        self.main_layout.addLayout(lists_layout)

        progress_group = aqt.qt.QGroupBox(self._text("workflow_progress"))
        progress_layout = aqt.qt.QVBoxLayout()
        self.workflow_status_label = aqt.qt.QLabel(self._text("workflow_ready"))
        self.workflow_status_label.setWordWrap(True)
        self.current_preset_label = aqt.qt.QLabel(self._text("workflow_current_preset_idle"))
        self.preset_progress = aqt.qt.QProgressBar()
        self.note_progress = aqt.qt.QProgressBar()
        self.note_progress.setFormat('%p%')
        progress_layout.addWidget(self.workflow_status_label)
        progress_layout.addWidget(self.current_preset_label)
        progress_layout.addWidget(self.preset_progress)
        progress_layout.addWidget(self.note_progress)
        progress_group.setLayout(progress_layout)
        self.main_layout.addWidget(progress_group)

        buttons_layout = aqt.qt.QHBoxLayout()
        buttons_layout.addStretch()
        self.run_button = aqt.qt.QPushButton(self._text("workflow_generate_all"))
        self.apply_selected_button = aqt.qt.QPushButton(self._text("workflow_apply_selected"))
        self.apply_all_button = aqt.qt.QPushButton(self._text("workflow_apply_all"))
        self.stop_button = aqt.qt.QPushButton(i18n.get_text("button_stop", lang))
        self.close_button = aqt.qt.QPushButton(i18n.get_text('button_close', lang))
        buttons_layout.addWidget(self.run_button)
        buttons_layout.addWidget(self.apply_selected_button)
        buttons_layout.addWidget(self.apply_all_button)
        buttons_layout.addWidget(self.stop_button)
        buttons_layout.addWidget(self.close_button)
        self.main_layout.addLayout(buttons_layout)

        gui_utils.configure_pastel_button(self.save_button, style_name='emerald', font_size=10)
        gui_utils.configure_pastel_button(self.run_button, style_name='emerald', is_primary=True, font_size=11)
        gui_utils.configure_pastel_button(self.apply_selected_button, style_name='blue', font_size=10)
        gui_utils.configure_pastel_button(self.apply_all_button, style_name='emerald', font_size=10)
        gui_utils.configure_pastel_button(self.open_button, style_name='blue', font_size=10)
        gui_utils.configure_pastel_button(self.duplicate_button, style_name='purple', font_size=10)
        gui_utils.configure_pastel_button(self.rename_button, style_name='amber', font_size=10)
        gui_utils.configure_pastel_button(self.delete_button, style_name='rose', font_size=10)
        gui_utils.configure_pastel_button(self.new_button, style_name='blue', font_size=10)

        self.new_button.clicked.connect(self.new_workflow_button_pressed)
        self.open_button.clicked.connect(self.open_workflow_button_pressed)
        self.save_button.clicked.connect(self.save_workflow_button_pressed)
        self.duplicate_button.clicked.connect(self.duplicate_workflow_button_pressed)
        self.rename_button.clicked.connect(self.rename_workflow_button_pressed)
        self.delete_button.clicked.connect(self.delete_workflow_button_pressed)
        self.add_button.clicked.connect(self.add_selected_presets)
        self.remove_button.clicked.connect(self.remove_selected_preset)
        self.up_button.clicked.connect(lambda: self.move_selected_preset(-1))
        self.down_button.clicked.connect(lambda: self.move_selected_preset(1))
        self.clear_button.clicked.connect(self.clear_workflow)
        self.run_button.clicked.connect(self.run_workflow_button_pressed)
        self.apply_selected_button.clicked.connect(self.apply_selected_preset_button_pressed)
        self.apply_all_button.clicked.connect(self.apply_all_presets_button_pressed)
        self.stop_button.clicked.connect(self.stop_workflow)
        self.close_button.clicked.connect(self.close_button_pressed)
        self.available_list.itemSelectionChanged.connect(self.refresh_button_states)
        self.workflow_list.itemSelectionChanged.connect(self.refresh_button_states)
        self.workflow_name_combobox.currentIndexChanged.connect(self.workflow_combobox_changed)

    def _populate_available_presets(self) -> None:
        self.available_list.clear()
        for preset in self.hypertts.get_preset_list():
            item = aqt.qt.QListWidgetItem(preset.name)
            item.setData(aqt.qt.Qt.ItemDataRole.UserRole, preset.id)
            self.available_list.addItem(item)

    def _workflow_item_text(self, preset_id: str, workflow_index: Optional[int] = None) -> str:
        if self.hypertts.preset_exists(preset_id):
            preset_name = self.hypertts.get_preset_name(preset_id)
            if workflow_index in self.pending_generated_audio:
                return self._text("workflow_preset_ready_to_apply", preset_name=preset_name)
            return preset_name
        return self._text("workflow_missing_preset", preset_id=preset_id)

    def refresh_workflow_item_labels(self) -> None:
        for index in range(self.workflow_list.count()):
            item = self.workflow_list.item(index)
            preset_id = item.data(aqt.qt.Qt.ItemDataRole.UserRole)
            item.setText(self._workflow_item_text(preset_id, index))

    def clear_pending_generated_audio(self) -> None:
        self.pending_generated_audio.clear()
        if hasattr(self, 'workflow_list'):
            self.refresh_workflow_item_labels()

    def update_workflow_dropdown(self, current_name: str, current_id: Optional[str]) -> None:
        workflow_list = self.hypertts.get_workflow_list()
        saved_names = {workflow.id: workflow.name for workflow in workflow_list}
        self.combobox_suspend_events = True
        self.workflow_name_combobox.clear()

        selected_index = None
        for index, workflow in enumerate(workflow_list):
            self.workflow_name_combobox.addItem(workflow.name, workflow.id)
            if current_id == workflow.id and saved_names.get(workflow.id) == current_name:
                selected_index = index

        if selected_index is None:
            self.workflow_name_combobox.addItem(current_name, UNSAVED_NEW_WORKFLOW)
            selected_index = self.workflow_name_combobox.count() - 1

        self.workflow_name_combobox.setCurrentIndex(selected_index)
        self.combobox_suspend_events = False

    def workflow_combobox_changed(self, index: int) -> None:
        if self.combobox_suspend_events or index < 0 or self.workflow_running:
            return

        workflow_id = self.workflow_name_combobox.itemData(index)
        if workflow_id == UNSAVED_NEW_WORKFLOW:
            return

        if self.workflow_model != None and workflow_id != getattr(self.workflow_model, 'uuid', None):
            self.save_workflow_if_changed()
            self.load_workflow(workflow_id)

    def load_model(self, workflow_model: config_models.WorkflowConfig) -> None:
        self.workflow_model = workflow_model
        self.workflow_list.clear()
        self.update_workflow_dropdown(workflow_model.name, workflow_model.uuid)
        self.clear_pending_generated_audio()
        for index, preset_id in enumerate(workflow_model.preset_ids):
            item = aqt.qt.QListWidgetItem(self._workflow_item_text(preset_id, index))
            item.setData(aqt.qt.Qt.ItemDataRole.UserRole, preset_id)
            self.workflow_list.addItem(item)
        self.model_changed = False
        self.refresh_button_states()

    def new_workflow(self, workflow_name: Optional[str] = None) -> None:
        if workflow_name == None:
            workflow_name = self.hypertts.get_next_workflow_name()
        workflow_model = config_models.WorkflowConfig(self.hypertts.anki_utils)
        workflow_model.name = workflow_name
        self.load_model(workflow_model)
        self.model_changed = True
        self.disable_delete_button()
        self.refresh_button_states()

    def new_workflow_after_delete(self) -> None:
        if self.workflow_model == None:
            self.new_workflow()
            return
        self.workflow_model.reset_uuid(self.hypertts.anki_utils)
        self.workflow_model.name = self.hypertts.get_next_workflow_name()
        self.workflow_model.preset_ids = []
        self.load_model(self.workflow_model)
        self.model_changed = True
        self.disable_delete_button()
        self.refresh_button_states()

    def load_workflow(self, workflow_id: str) -> None:
        workflow_model = self.hypertts.load_workflow(workflow_id)
        self.load_model(workflow_model)
        self.enable_delete_button()

    def choose_existing_workflow(self, title: str) -> Optional[str]:
        workflow_list = self.hypertts.get_workflow_list()
        workflow_name_list = [workflow.name for workflow in workflow_list]
        if len(workflow_name_list) == 0:
            raise errors.HyperTTSError(self._text("workflow_no_saved"))
        chosen_row, retvalue = self.hypertts.anki_utils.ask_user_choose_from_list(self, title, workflow_name_list)
        if retvalue == 1:
            return workflow_list[chosen_row].id
        return None

    def enable_delete_button(self) -> None:
        self.delete_button.setEnabled(True)

    def disable_delete_button(self) -> None:
        self.delete_button.setEnabled(False)

    def get_model(self) -> config_models.WorkflowConfig:
        if self.workflow_model == None:
            raise errors.HyperTTSError('Workflow model not initialized.')
        self.workflow_model.preset_ids = [
            self.workflow_list.item(index).data(aqt.qt.Qt.ItemDataRole.UserRole)
            for index in range(self.workflow_list.count())
        ]
        return self.workflow_model

    def refresh_button_states(self) -> None:
        running = self.workflow_running
        has_available_selection = len(self.available_list.selectedItems()) > 0
        selected_workflow_row = self.workflow_list.currentRow()
        has_workflow_selection = selected_workflow_row >= 0
        has_workflow_items = self.workflow_list.count() > 0
        has_saved_workflows = len(self.hypertts.get_workflow_list()) > 0
        has_pending_generated_audio = len(self.pending_generated_audio) > 0
        has_selected_pending_audio = selected_workflow_row in self.pending_generated_audio

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
        self.apply_selected_button.setEnabled((not running) and has_selected_pending_audio)
        self.apply_all_button.setEnabled((not running) and has_pending_generated_audio)
        self.stop_button.setEnabled(running)
        self.close_button.setEnabled(not running)
        self.new_button.setEnabled(not running)
        self.open_button.setEnabled((not running) and has_saved_workflows)
        self.save_button.setEnabled((not running) and self.model_changed)
        self.duplicate_button.setEnabled((not running) and has_saved_workflows)
        self.rename_button.setEnabled(not running)
        if running:
            self.delete_button.setEnabled(False)
        elif self.workflow_model != None and self.hypertts.workflow_exists(self.workflow_model.uuid):
            self.delete_button.setEnabled(True)

    def mark_model_changed(self) -> None:
        self.clear_pending_generated_audio()
        self.model_changed = True
        self.refresh_button_states()

    def add_selected_presets(self) -> None:
        for item in self.available_list.selectedItems():
            new_item = aqt.qt.QListWidgetItem(item.text())
            new_item.setData(aqt.qt.Qt.ItemDataRole.UserRole, item.data(aqt.qt.Qt.ItemDataRole.UserRole))
            self.workflow_list.addItem(new_item)
        self.mark_model_changed()

    def remove_selected_preset(self) -> None:
        row = self.workflow_list.currentRow()
        if row >= 0:
            self.workflow_list.takeItem(row)
            self.mark_model_changed()

    def move_selected_preset(self, direction: int) -> None:
        row = self.workflow_list.currentRow()
        if row < 0:
            return
        target_row = row + direction
        if target_row < 0 or target_row >= self.workflow_list.count():
            return
        item = self.workflow_list.takeItem(row)
        self.workflow_list.insertItem(target_row, item)
        self.workflow_list.setCurrentRow(target_row)
        self.mark_model_changed()

    def clear_workflow(self) -> None:
        self.workflow_list.clear()
        self.mark_model_changed()

    def validate_workflow_for_run(self) -> config_models.WorkflowConfig:
        workflow_model = self.get_model()
        workflow_model.validate()
        missing_preset_ids = self.hypertts.get_missing_workflow_preset_ids(workflow_model)
        if missing_preset_ids:
            missing_text = ', '.join(missing_preset_ids)
            raise errors.HyperTTSError(
                self._text("workflow_missing_presets_run", presets=missing_text)
            )
        return workflow_model

    def save_workflow(self) -> None:
        workflow_model = self.get_model()
        workflow_model.validate()
        self.hypertts.save_workflow(workflow_model)
        self.model_changed = False
        self.last_saved_workflow_id = workflow_model.uuid
        self.enable_delete_button()
        self.update_workflow_dropdown(workflow_model.name, workflow_model.uuid)
        self.refresh_button_states()

    def save_workflow_if_changed(self) -> None:
        if not self.model_changed:
            return
        proceed = self.hypertts.anki_utils.ask_user(
            self._text("workflow_save_changes_prompt"),
            self,
        )
        if proceed:
            self.save_workflow()

    def new_workflow_button_pressed(self) -> None:
        with self.hypertts.error_manager.get_single_action_context('Creating Workflow'):
            self.save_workflow_if_changed()
            self.new_workflow()

    def open_workflow_button_pressed(self) -> None:
        with self.hypertts.error_manager.get_single_action_context('Opening Workflow'):
            workflow_id = self.choose_existing_workflow(self._text("workflow_choose_open"))
            if workflow_id != None:
                self.save_workflow_if_changed()
                self.load_workflow(workflow_id)

    def save_workflow_button_pressed(self) -> None:
        with self.hypertts.error_manager.get_single_action_context('Saving Workflow'):
            self.save_workflow()

    def duplicate_workflow_button_pressed(self) -> None:
        with self.hypertts.error_manager.get_single_action_context('Duplicating Workflow'):
            workflow_id = self.choose_existing_workflow(self._text("workflow_choose_duplicate"))
            if workflow_id != None:
                self.load_workflow(workflow_id)
                self.workflow_model.reset_uuid(self.hypertts.anki_utils)
                self.workflow_model.name = self.workflow_model.name + ' (copy)'
                self.update_workflow_dropdown(self.workflow_model.name, self.workflow_model.uuid)
                self.model_changed = True
                self.disable_delete_button()
                self.refresh_button_states()

    def rename_workflow_button_pressed(self) -> None:
        with self.hypertts.error_manager.get_single_action_context('Renaming Workflow'):
            current_name = self.get_model().name
            new_name, result = self.hypertts.anki_utils.ask_user_get_text(
                self._text("workflow_enter_new_name"),
                self,
                current_name,
                self._text("workflow_rename_title"),
            )
            if result == 1:
                self.workflow_model.name = new_name
                self.update_workflow_dropdown(new_name, self.workflow_model.uuid)
                self.mark_model_changed()

    def delete_workflow_button_pressed(self) -> None:
        workflow_model = self.get_model()
        if not self.hypertts.workflow_exists(workflow_model.uuid):
            self.new_workflow_after_delete()
            return
        proceed = self.hypertts.anki_utils.ask_user(
            self._text("workflow_delete_confirm", name=workflow_model.name),
            self,
        )
        if proceed:
            with self.hypertts.error_manager.get_single_action_context('Deleting Workflow'):
                self.hypertts.delete_workflow(workflow_model.uuid)
                self.new_workflow_after_delete()

    def run_workflow_button_pressed(self) -> None:
        with self.hypertts.error_manager.get_single_action_context('Running Workflow'):
            workflow_model = self.validate_workflow_for_run()
            self.workflow_cancelled = False
            self.current_preset_index = 0
            self.total_presets = len(workflow_model.preset_ids)
            self.clear_pending_generated_audio()
            self.workflow_operation = 'generate'
            self.workflow_failure_records = []
            self.failed_note_ids_to_tag = []
            self.preset_progress.setRange(0, self.total_presets)
            self.preset_progress.setValue(0)
            self.note_progress.setRange(0, 100)
            self.note_progress.setValue(0)
            self.workflow_status_label.setText(self._text("workflow_starting"))
            self.current_preset_label.setText(self._text("workflow_current_preset_idle"))
            self.workflow_running = True
            self.refresh_button_states()

            self.hypertts.anki_utils.run_in_background_collection_op(
                self,
                self.run_workflow_collection_op,
                self.run_workflow_done,
            )

    def apply_selected_preset_button_pressed(self) -> None:
        row = self.workflow_list.currentRow()
        if row not in self.pending_generated_audio:
            return
        self.apply_generated_workflow_indices([row])

    def apply_all_presets_button_pressed(self) -> None:
        pending_indices = sorted(self.pending_generated_audio.keys())
        if len(pending_indices) == 0:
            return
        self.apply_generated_workflow_indices(pending_indices)

    def apply_generated_workflow_indices(self, workflow_indices: List[int]) -> None:
        with self.hypertts.error_manager.get_single_action_context('Applying Workflow Audio'):
            self.workflow_cancelled = False
            self.current_preset_index = 0
            self.total_presets = len(workflow_indices)
            self.workflow_operation = 'apply'
            self.apply_workflow_indices = workflow_indices
            self.workflow_failure_records = []
            self.failed_note_ids_to_tag = []
            self.preset_progress.setRange(0, self.total_presets)
            self.preset_progress.setValue(0)
            self.note_progress.setRange(0, 100)
            self.note_progress.setValue(0)
            self.workflow_status_label.setText(self._text("workflow_applying_starting"))
            self.current_preset_label.setText(self._text("workflow_current_preset_idle"))
            self.workflow_running = True
            self.refresh_button_states()

            self.hypertts.anki_utils.run_in_background_collection_op(
                self,
                self.apply_generated_workflow_collection_op,
                self.apply_generated_workflow_done,
            )

    def stop_workflow(self) -> None:
        self.workflow_cancelled = True
        if self.current_batch_status != None:
            self.current_batch_status.stop()
        self.workflow_status_label.setText(self._text("workflow_stopping"))

    def close_button_pressed(self) -> None:
        if self.workflow_running:
            return
        self.save_workflow_if_changed()
        self.skip_close_prompt = True
        self.accept()

    def run_workflow_collection_op(self, anki_collection: Any) -> None:
        workflow_model = self.get_model()
        for preset_index, preset_id in enumerate(workflow_model.preset_ids, start=1):
            if self.workflow_cancelled:
                break

            if not self.hypertts.preset_exists(preset_id):
                raise errors.HyperTTSError(
                    self._text("workflow_missing_preset_single", preset_id=preset_id)
                )

            preset = self.hypertts.load_preset(preset_id)
            self.current_preset_index = preset_index
            self.current_preset_name = preset.name
            self.current_batch_status = batch_status.BatchStatus(
                self.hypertts.anki_utils, self.note_id_list, self
            )

            self.hypertts.anki_utils.run_on_main(
                lambda idx=preset_index, total=self.total_presets, name=preset.name: self.workflow_preset_started(
                    idx, total, name
                )
            )

            self.current_batch_status.begin()
            try:
                prepared_batch = self.hypertts.prepare_batch_audio_generation(
                    self.note_id_list,
                    preset,
                    self.current_batch_status,
                )
                generated_results = self.hypertts.generate_prepared_batch_audio(
                    prepared_batch,
                    self.current_batch_status,
                )
            except Exception:
                self.current_batch_status.end(False)
                raise
            else:
                self.pending_generated_audio[preset_index - 1] = {
                    'preset': preset,
                    'results': generated_results,
                    'batch_status': self.current_batch_status,
                }
                self.current_batch_status.end(True)

            self.workflow_failure_records.extend(
                self.current_batch_status.get_failure_records(preset_name=preset.name)
            )

            if not self.current_batch_status.must_continue:
                self.workflow_cancelled = True
                break

        self.current_batch_status = None

    def apply_generated_workflow_collection_op(self, anki_collection: Any) -> None:
        for apply_index, workflow_index in enumerate(self.apply_workflow_indices, start=1):
            if self.workflow_cancelled:
                break

            pending_audio = self.pending_generated_audio.get(workflow_index)
            if pending_audio == None:
                continue

            preset = pending_audio['preset']
            generated_results = pending_audio['results']
            self.current_preset_index = apply_index
            self.current_preset_name = preset.name
            self.current_batch_status = pending_audio['batch_status']

            self.hypertts.anki_utils.run_on_main(
                lambda idx=apply_index, total=self.total_presets, name=preset.name: self.workflow_preset_apply_started(
                    idx, total, name
                )
            )

            self.current_batch_status.begin()
            try:
                self.hypertts.apply_generated_batch_audio(
                    generated_results,
                    preset,
                    self.current_batch_status,
                    anki_collection,
                )
            except Exception:
                self.current_batch_status.end(False)
                raise
            else:
                self.current_batch_status.end(True)
                del self.pending_generated_audio[workflow_index]

            self.workflow_failure_records.extend(
                self.current_batch_status.get_failure_records(preset_name=preset.name)
            )

            if not self.current_batch_status.must_continue:
                self.workflow_cancelled = True
                break

        self.current_batch_status = None

    def run_workflow_done(self, result: Any) -> None:
        logger.debug(f'workflow finished, result: {result}')
        self.hypertts.anki_utils.run_on_main(self.finish_workflow_ui)

    def apply_generated_workflow_done(self, result: Any) -> None:
        logger.debug(f'workflow apply finished, result: {result}')
        self.hypertts.anki_utils.run_on_main(self.finish_workflow_apply_ui)

    def finish_workflow_ui(self) -> None:
        completed = not self.workflow_cancelled
        if completed:
            if len(self.pending_generated_audio) > 0:
                self.workflow_status_label.setText(
                    self._text("workflow_generated_ready", count=len(self.pending_generated_audio))
                )
            else:
                self.workflow_status_label.setText(self._text("workflow_completed"))
            self.current_preset_label.setText(
                self._text(
                    "workflow_completed_current_preset",
                    done=self.total_presets,
                    total=self.total_presets,
                )
            )
            self.preset_progress.setValue(self.total_presets)
            self.note_progress.setValue(100)
        else:
            self.workflow_status_label.setText(self._text("workflow_stopped"))
        self.workflow_running = False
        self.workflow_operation = None
        self.refresh_workflow_item_labels()
        self.refresh_button_states()

    def finish_workflow_apply_ui(self) -> None:
        completed = not self.workflow_cancelled
        if completed:
            if len(self.pending_generated_audio) > 0:
                self.workflow_status_label.setText(
                    self._text("workflow_apply_completed_remaining", count=len(self.pending_generated_audio))
                )
            else:
                self.workflow_status_label.setText(self._text("workflow_apply_completed"))
            self.current_preset_label.setText(
                self._text(
                    "workflow_completed_current_preset",
                    done=self.total_presets,
                    total=self.total_presets,
                )
            )
            self.preset_progress.setValue(self.total_presets)
            self.note_progress.setValue(100)
        else:
            self.workflow_status_label.setText(self._text("workflow_stopped"))
        self.workflow_running = False
        self.workflow_operation = None
        self.apply_workflow_indices = []
        self.refresh_workflow_item_labels()
        self.refresh_button_states()
        self.show_failure_report_if_needed()

    def workflow_preset_started(self, preset_index: int, total_presets: int, preset_name: str) -> None:
        self.preset_progress.setRange(0, total_presets)
        self.preset_progress.setValue(max(0, preset_index - 1))
        self.note_progress.setValue(0)
        self.current_preset_label.setText(
            self._text(
                "workflow_current_preset_progress",
                preset_name=preset_name,
                index=preset_index,
                total=total_presets,
            )
        )
        self.workflow_status_label.setText(
            self._text("workflow_generating_preset", preset_name=preset_name)
        )

    def workflow_preset_apply_started(self, preset_index: int, total_presets: int, preset_name: str) -> None:
        self.preset_progress.setRange(0, total_presets)
        self.preset_progress.setValue(max(0, preset_index - 1))
        self.note_progress.setValue(0)
        self.current_preset_label.setText(
            self._text(
                "workflow_current_preset_progress",
                preset_name=preset_name,
                index=preset_index,
                total=total_presets,
            )
        )
        self.workflow_status_label.setText(
            self._text("workflow_applying_preset", preset_name=preset_name)
        )

    def batch_start(self) -> None:
        pass

    def batch_end(self, completed: bool) -> None:
        def update() -> None:
            if completed:
                self.note_progress.setValue(100)
                self.preset_progress.setValue(self.current_preset_index)
                if self.workflow_operation == 'apply':
                    self.workflow_status_label.setText(
                        self._text("workflow_applied_preset", preset_name=self.current_preset_name)
                    )
                else:
                    self.workflow_status_label.setText(
                        self._text("workflow_generated_preset", preset_name=self.current_preset_name)
                    )
            else:
                self.workflow_status_label.setText(
                    self._text("workflow_stopped_preset", preset_name=self.current_preset_name)
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
        if current_batch_status == None:
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
        status_message = current_batch_status.status_message or self._text(
            "workflow_processing_note",
            note_id=note_id,
        )

        self.hypertts.anki_utils.run_on_main(
            lambda pct=progress_percent, msg=status_message: self.update_note_progress(pct, msg)
        )

    def update_note_progress(self, progress_percent: int, status_message: str) -> None:
        self.note_progress.setValue(max(0, min(100, progress_percent)))
        self.workflow_status_label.setText(f'{status_message} [{self.current_preset_name}]')

    def show_failure_report_if_needed(self) -> None:
        if len(self.workflow_failure_records) == 0:
            return
        add_tag_requested = component_failure_report.show_failure_report(
            self.hypertts,
            self,
            self.workflow_failure_records,
        )
        if add_tag_requested:
            self.failed_note_ids_to_tag = list(
                dict.fromkeys(record.note_id for record in self.workflow_failure_records)
            )
            self.hypertts.anki_utils.run_in_background_collection_op(
                self,
                self.apply_error_tags_fn,
                self.finished_apply_error_tags_fn,
            )

    def apply_error_tags_fn(self, anki_collection: Any) -> None:
        self.hypertts.tag_error_notes(self.failed_note_ids_to_tag, anki_collection)

    def finished_apply_error_tags_fn(self, result: Any) -> None:
        if len(self.failed_note_ids_to_tag) == 0:
            return
        self.hypertts.anki_utils.tooltip_message(
            self._text(
                "workflow_error_tag_added",
                tag=constants.WORKFLOW_ERROR_TAG,
                count=len(self.failed_note_ids_to_tag),
            )
        )
        self.failed_note_ids_to_tag = []

    def closeEvent(self, event: Any) -> None:
        if self.workflow_running:
            event.ignore()
            return
        if self.skip_close_prompt:
            self.skip_close_prompt = False
            super(aqt.qt.QDialog, self).closeEvent(event)
            return
        self.save_workflow_if_changed()
        super(aqt.qt.QDialog, self).closeEvent(event)


def create_workflow_dialog_browser(
    hypertts: Any,
    note_id_list: List[int],
    workflow_id: Optional[str] = None,
    autorun: bool = False,
) -> None:
    if len(note_id_list) == 0:
        raise errors.NoNotesSelected()

    dialog = WorkflowDialog(hypertts, note_id_list, workflow_id=workflow_id, autorun=autorun)
    hypertts.anki_utils.wait_for_dialog_input(dialog, constants.DIALOG_ID_WORKFLOW)
