import sys
import aqt.qt
import time
import html
import aqt.operations
import copy
from typing import Callable, Optional, List, Any
from datetime import timedelta, datetime

from . import constants
from . import component_common
from . import config_models
from . import batch_status
from . import batch_progress_ui
from . import component_failure_report
from . import logging_utils
from . import i18n
logger = logging_utils.get_child_logger(__name__)

class TableRepaintTimer():
    def __init__(self, delay_ms):
        self.delay_ms = delay_ms
        self.timer_obj = None


class BatchPreviewTableModel(aqt.qt.QAbstractTableModel):
    def __init__(self, batch_status, hypertts):
        aqt.qt.QAbstractTableModel.__init__(self, None)
        self.batch_status = batch_status
        self.hypertts = hypertts
        self.page_size = 100
        self.current_page = 0
        self.total_notes = len(self.batch_status.note_id_list)
        self.loaded_note_ids = []
        self.loaded_pages = set()
        self.loading_pages = set()
        self.is_loading = False
        self.generation = 0
        self.table_view = None
    
    def page_count(self):
        return (self.total_notes + self.page_size - 1) // self.page_size

    def page_for_row(self, row: int):
        if row < 0:
            return 0
        return min(row // self.page_size, max(self.page_count() - 1, 0))

    def invalidate_all(self):
        """Invalidate all cached pages and trigger visible page reload on preset switch."""
        self.generation += 1
        self.loaded_pages = set()
        self.loading_pages = set()
        self.loaded_note_ids = []
        self.is_loading = False
        self.total_notes = len(self.batch_status.note_id_list)
        self.beginResetModel()
        self.endResetModel()
        # Re-load visible pages under new preset
        if self.table_view is not None:
            self._load_visible_pages()
        else:
            # table_view not yet initialized (dialog just opened), load page 0 only
            self.load_page(0)

    def load_page(self, page: int):
        """Load a specific page of notes into the model"""
        if page in self.loaded_pages or page in self.loading_pages:
            return
        if page < 0 or page >= self.page_count():
            return

        start = page * self.page_size
        end = min(start + self.page_size, self.total_notes)
        new_note_ids = self.batch_status.note_id_list[start:end]
        self.loaded_note_ids = sorted(
            set(self.loaded_note_ids).union(new_note_ids),
            key=lambda note_id: self.batch_status.note_id_map.get(note_id, 0),
        )
        self.loading_pages.add(page)
        self.is_loading = True
        self._request_processed_text(new_note_ids, page, self.generation)

    def _get_headers(self):
        lang = self.hypertts.get_ui_language()
        return [
            i18n.get_text('preview_header_note_id', lang),
            i18n.get_text('preview_header_source_text', lang),
            i18n.get_text('preview_header_processed_text', lang),
            i18n.get_text('preview_header_status', lang)
        ]

    def flags(self, index):
        return aqt.qt.Qt.ItemFlag.ItemIsSelectable | aqt.qt.Qt.ItemFlag.ItemIsEnabled

    def rowCount(self, parent):
        # Return total notes so view shows full scrollbar even before pages loaded
        return self.total_notes

    def columnCount(self, parent):
        # logger.debug('SourceTextPreviewTableModel.columnCount')
        return 4
    
    def notifyChange(self, row):
        # logger.info(f'notifyChange, row: {row}')
        start_index = self.createIndex(row, 0)
        end_index = self.createIndex(row, self.columnCount(None) - 1)
        self.dataChanged.emit(start_index, end_index)

    def has_more_pages(self):
        highest_page = max(self.loaded_pages) if self.loaded_pages else -1
        return (highest_page + 1) * self.page_size < self.total_notes

    def load_next_page(self):
        highest_page = max(self.loaded_pages) if self.loaded_pages else -1
        next_page = highest_page + 1
        self.load_page(next_page)

    def _request_processed_text(self, note_ids: List[int], page: int, generation: int):
        # Use QueryOp for background
        op = aqt.operations.QueryOp(
            parent=aqt.mw,
            op=lambda col: self.hypertts.populate_batch_status_processed_text(
                note_ids, self.batch_status.source_model, self.batch_status.text_processing_model, self.batch_status
            ),
            success=lambda result, page=page, gen=generation: self._on_page_processed(result, page, gen),
        ).failure(lambda error, page=page, gen=generation: self._on_page_failed(error, page, gen)).run_in_background()

    def _on_page_processed(self, result, page: int, generation: int):
        # Discard stale result from previous preset generation
        if generation != self.generation:
            self.loading_pages.discard(page)
            return
        self.loading_pages.discard(page)
        self.loaded_pages.add(page)
        self.is_loading = len(self.loading_pages) > 0
        # emit data changed for rows corresponding to the loaded page
        try:
            if len(self.loaded_note_ids) > 0:
                first_note = self.loaded_note_ids[0]
                last_note = self.loaded_note_ids[-1]
                first_row = self.batch_status.note_id_map.get(first_note, 0)
                last_row = self.batch_status.note_id_map.get(last_note, first_row)
                last_col = max(0, self.columnCount(None) - 1)
                self.dataChanged.emit(self.createIndex(first_row, 0), self.createIndex(last_row, last_col))
            else:
                # fallback: refresh whole table
                last_col = max(0, self.columnCount(None) - 1)
                self.dataChanged.emit(self.createIndex(0, 0), self.createIndex(max(0, self.total_notes - 1), last_col))
        except Exception:
            # ensure UI doesn't crash on update
            last_col = max(0, self.columnCount(None) - 1)
            self.dataChanged.emit(self.createIndex(0, 0), self.createIndex(max(0, self.total_notes - 1), last_col))
    
    def _on_page_failed(self, error, page: int, generation: int):
        # Discard stale error from previous preset generation
        if generation != self.generation:
            self.loading_pages.discard(page)
            return
        self.loading_pages.discard(page)
        self.is_loading = len(self.loading_pages) > 0
        logger.error(f"Failed to process page {page}: {error}")

    def _visible_row_range(self):
        if self.table_view is None:
            return 0, min(self.page_size - 1, self.total_notes - 1)
        viewport = self.table_view.viewport()
        if viewport is None:
            return 0, min(self.page_size - 1, self.total_notes - 1)
        first_row = self.table_view.rowAt(0)
        if first_row < 0:
            first_row = 0
        last_row = self.table_view.rowAt(viewport.height() - 1)
        if last_row < 0:
            last_row = min(first_row + self.page_size - 1, self.total_notes - 1)
        return first_row, last_row

    def _load_visible_pages(self):
        if self.total_notes == 0:
            return
        first_row, last_row = self._visible_row_range()
        first_page = self.page_for_row(first_row)
        last_page = self.page_for_row(last_row)
        for page in range(first_page, min(self.page_count(), last_page + 2)):
            self.load_page(page)

    def data(self, index, role):
        if role != aqt.qt.Qt.ItemDataRole.DisplayRole:
            return None
        # logger.debug('SourceTextPreviewTableModel.data')
        if not index.isValid():
            return aqt.qt.QVariant()
        data = None
        # map row -> note id from batch_status
        try:
            note_id = self.batch_status.note_id_list[index.row()]
        except Exception:
            return aqt.qt.QVariant()
        note_status = self.batch_status.note_status_map.get(note_id)

        if note_status is None:
            return aqt.qt.QVariant()

        if index.column() == 0:
            data = note_status.note_id
        elif index.column() == 1:
            data = note_status.source_text
        elif index.column() == 2:
            data = note_status.processed_text            
        elif index.column() == 3:
            if note_status.status != None:
                data = note_status.status.name
        if data != None:
            return aqt.qt.QVariant(data)
        return aqt.qt.QVariant()

    def headerData(self, col, orientation, role):
        # logger.debug('SourceTextPreviewTableModel.headerData')
        if orientation == aqt.qt.Qt.Orientation.Horizontal and role == aqt.qt.Qt.ItemDataRole.DisplayRole:
            return aqt.qt.QVariant(self._get_headers()[col])
        return aqt.qt.QVariant()

class BatchPreview(component_common.ComponentBase):
    def __init__(self, hypertts: Any, dialog: Any, note_id_list: List[int], sample_selection_fn: Callable, batch_start_fn: Callable, batch_end_fn: Callable) -> None:
        """
        Initialize batch preview component.
        
        Args:
            hypertts: Main HyperTTS instance
            dialog: Parent dialog widget
            note_id_list: List of note IDs to process in batch
            sample_selection_fn: Callback function for sample selection
            batch_start_fn: Callback function when batch starts
            batch_end_fn: Callback function when batch ends
        """
        self.hypertts = hypertts
        self.dialog = dialog
        self.note_id_list = note_id_list
        self.sample_selection_fn = sample_selection_fn
        self.batch_start_fn = batch_start_fn
        self.batch_end_fn = batch_end_fn

        self.batch_status = batch_status.BatchStatus(hypertts.anki_utils, note_id_list, self)
        self.batch_preview_table_model = BatchPreviewTableModel(self.batch_status, hypertts)
        self.table_view = None
        # create certain widgets right away
        self.stack = aqt.qt.QStackedWidget()

        self.selected_row = None

        self.apply_to_notes_batch_started = False
        self.failed_note_ids_to_tag: List[int] = []
        self.generated_batch_results = None
        self.prepared_batch_audio = None
        self.generated_batch_model = None
        self.batch_run_mode = 'idle'
        self._apply_chunk_index = 0
        self._apply_undo_id = None
        self._last_batch_change_time = 0.0

        self.table_repaint_timer = TableRepaintTimer(500)
        self.status_label = None
        self._last_batch_change_time = 0.0

    def load_model(self, model):
        self.batch_model = model
        self.batch_status.source_model = model.source
        self.batch_status.text_processing_model = getattr(model, 'text_processing', None) or config_models.TextProcessing()
        self.apply_to_notes_batch_started = False
        self.generated_batch_results = None
        self.prepared_batch_audio = None
        self.generated_batch_model = None
        self.batch_run_mode = 'idle'
        self._apply_chunk_index = 0
        self._apply_undo_id = None
        if self.stack is not None:
            self.hypertts.anki_utils.run_on_main(self.reset_progress_ui)
        if hasattr(self.batch_preview_table_model, 'table_view') and self.table_view is not None:
            self.batch_preview_table_model.table_view = self.table_view
        self.batch_preview_table_model.invalidate_all()
        self._update_status_label()

    def update_batch_status_task(self):
        pass

    def update_batch_status_task_done(self, result):
        logger.info('update_batch_status_task_done')

    def draw(self):
        # populate processed text

        self.batch_preview_layout = aqt.qt.QVBoxLayout()
        self.table_view = aqt.qt.QTableView()
        self.table_view.setModel(self.batch_preview_table_model)
        self.batch_preview_table_model.table_view = self.table_view
        self.table_view.setSelectionMode(aqt.qt.QTableView.SelectionMode.SingleSelection)
        self.table_view.setSelectionBehavior(aqt.qt.QTableView.SelectionBehavior.SelectRows)
        
        # Modern UI tweaks
        self.table_view.setAlternatingRowColors(True)
        self.table_view.setShowGrid(False)
        self.table_view.verticalHeader().setVisible(False)
        try:
            self.table_view.setFrameShape(aqt.qt.QFrame.Shape.NoFrame)
            self.table_view.horizontalHeader().setStretchLastSection(True)
            # Use Interactive mode so users can resize, but initialize with reasonable sizes
            self.table_view.horizontalHeader().setSectionResizeMode(aqt.qt.QHeaderView.ResizeMode.Interactive)
        except AttributeError:
            self.table_view.setFrameShape(aqt.qt.QFrame.NoFrame)
            self.table_view.horizontalHeader().setStretchLastSection(True)
            self.table_view.horizontalHeader().setSectionResizeMode(aqt.qt.QHeaderView.Interactive)

        self.table_view.selectionModel().selectionChanged.connect(self.selection_changed)
        self.table_view.verticalScrollBar().valueChanged.connect(self._check_scroll_load)
        self.batch_preview_table_model.dataChanged.connect(self._update_status_label)
        self.batch_preview_layout.addWidget(self.table_view, stretch=1)

        self.status_label = aqt.qt.QLabel()
        self.batch_preview_layout.addWidget(self.status_label)

        self.error_label = aqt.qt.QLabel()
        self.error_label.setWordWrap(True)
        self.batch_preview_layout.addWidget(self.error_label)

        # create stack of widgets which will be toggled when we're running the batch
        self.batchNotRunningStack = aqt.qt.QWidget()
        self.batchRunningStack = aqt.qt.QWidget()
        self.batchCompletedStack = aqt.qt.QWidget()


        # populate the "notRunning" stack
        notRunningLayout = aqt.qt.QVBoxLayout()
        self.batchNotRunningStack.setLayout(notRunningLayout)

        # populate the "running" stack with enhanced progress widget
        runningLayout = aqt.qt.QVBoxLayout()
        
        # Create enhanced progress widget with stop button
        progress_container = aqt.qt.QWidget()
        progress_layout = aqt.qt.QVBoxLayout(progress_container)
        
        # Create stop button row
        stop_button_layout = aqt.qt.QHBoxLayout()
        self.stop_button = aqt.qt.QPushButton('Stop Batch')
        self.stop_button.setMaximumWidth(120)
        stop_button_layout.addStretch()
        stop_button_layout.addWidget(self.stop_button)
        stop_button_layout.addStretch()
        progress_layout.addLayout(stop_button_layout)
        
        # Add enhanced progress widget
        self.enhanced_progress_widget = batch_progress_ui.BatchProgressWidget(
            cancel_callback=self.stop_button_pressed
        )
        progress_layout.addWidget(self.enhanced_progress_widget)
        
        runningLayout.addWidget(progress_container)
        
        

        self.batchRunningStack.setLayout(runningLayout)

        # populate the completed stack
        completedLayout = aqt.qt.QVBoxLayout()
        label = aqt.qt.QLabel(constants.GUI_TEXT_BATCH_COMPLETED)
        label.setWordWrap(True)
        completedLayout.addWidget(label)
        self.batchCompletedStack.setLayout(completedLayout)

        self.stack.addWidget(self.batchNotRunningStack)
        self.stack.addWidget(self.batchRunningStack)
        self.stack.addWidget(self.batchCompletedStack)
        self.show_not_running_stack()
        self.batch_preview_layout.addWidget(self.stack)

        # wire events
        self.stop_button.pressed.connect(self.stop_button_pressed)

        return self.batch_preview_layout


    def _check_scroll_load(self, value):
        self.batch_preview_table_model._load_visible_pages()
        if value >= self.table_view.verticalScrollBar().maximum() - 50:
            self._load_next_page()

    def _load_next_page(self):
        if not self.batch_preview_table_model.is_loading and self.batch_preview_table_model.has_more_pages():
            self.batch_preview_table_model.load_next_page()

    def _update_status_label(self):
        if self.status_label:
            self.status_label.setText(f"Showing {len(self.batch_preview_table_model.loaded_note_ids)} of {self.batch_preview_table_model.total_notes} notes")

    def show_not_running_stack(self):
        self.stack.setCurrentIndex(0)

    def show_running_stack(self):
        self.stack.setCurrentIndex(1)

    def show_completed_stack(self):
        self.stack.setCurrentIndex(2)

    def reset_progress_ui(self):
        if hasattr(self, 'enhanced_progress_widget'):
            self.enhanced_progress_widget.reset()
        self.show_not_running_stack()

    def selection_changed(self):
        logger.info('selection_changed')
        self.report_sample_text()
        self.update_error_label_for_selected()

    def report_sample_text(self):
        note_status = self.get_selected_note_status()
        if note_status != None:
            text = note_status.processed_text
            self.sample_selection_fn(note_status.note_id, text)

    def update_error_label_for_selected(self):
        note_status = self.get_selected_note_status()
        if note_status != None:        
            if note_status.status == constants.BatchNoteStatus.Error:
                # show error label
                self.error_label.setText('<b>Error:</b> ' + html.escape(str(note_status.error)))
            else:
                self.error_label.setText('')

    def get_selected_note_status(self):
        row_indices = self.table_view.selectionModel().selectedIndexes()
        if len(row_indices) >= 1:
            self.selected_row = row_indices[0].row()
            return self.batch_status[self.selected_row]
        return None

    def has_pending_generated_audio(self):
        return self.generated_batch_results is not None

    def is_applying_generated_audio(self):
        return self.batch_run_mode == 'applying'

    def generate_audio_to_cache(self):
        self.apply_to_notes_batch_started = True
        self.failed_note_ids_to_tag = []
        self.generated_batch_results = None
        self.prepared_batch_audio = None
        self.generated_batch_model = copy.deepcopy(self.batch_model)
        self.batch_run_mode = 'generating'
        self.batch_status.begin()
        aqt.operations.QueryOp(
            parent=self.dialog,
            op=self.prepare_audio_fn,
            success=self.finished_prepare_audio_fn,
        ).failure(self.batch_operation_failed).run_in_background()

    def apply_audio_to_notes(self):
        self.generate_audio_to_cache()

    # Chunk size for the chunked Apply step. Smaller = more frequent gaps
    # for Anki's own background jobs (like automatic backups) to run
    # between chunks, at the cost of slightly more per-chunk overhead.
    # 25 is a starting value — see FIX_PLAN Section 6, test 4, for how to
    # tune it. Do not set below 1.
    APPLY_CHUNK_SIZE = 25

    def apply_generated_audio_to_notes(self):
        if not self.has_pending_generated_audio():
            return
        self.apply_to_notes_batch_started = True
        self.failed_note_ids_to_tag = []
        self.batch_run_mode = 'applying'
        try:
            self._apply_undo_id = aqt.mw.col.add_custom_undo_entry(constants.UNDO_ENTRY_NAME)
        except Exception as e:
            logger.error(f'failed to open undo entry for chunked apply: {e}')
            self.apply_to_notes_batch_started = False
            self.batch_run_mode = 'idle'
            raise
        self.batch_status.begin()
        self.batch_status.total_unique_tasks = len(self.generated_batch_results)
        self.batch_status.unique_tasks_completed = 0
        self._apply_chunk_index = 0
        self._run_next_apply_chunk()

    def _run_next_apply_chunk(self):
        start = self._apply_chunk_index * self.APPLY_CHUNK_SIZE
        end = start + self.APPLY_CHUNK_SIZE
        chunk = self.generated_batch_results[start:end]

        if not chunk or not self.batch_status.must_continue:
            self._finish_apply_chain()
            return

        self._apply_chunk_index += 1

        aqt.operations.QueryOp(
            parent=self.dialog,
            op=lambda col, c=chunk: self.hypertts.apply_generated_batch_audio_chunk(
                c, self.generated_batch_model, self.batch_status, col
            ),
            success=lambda result: self._run_next_apply_chunk(),
        ).failure(self._apply_chunk_failed).run_in_background()

    def _apply_chunk_failed(self, exception):
        """
        Failure handler for a single chunk in the chunked Apply chain.

        Unlike the plain self.batch_operation_failed handler (which is also
        used by the Generate step, where no undo entry is open), this
        handler MUST merge the undo entry opened in
        apply_generated_audio_to_notes before doing anything else. If this
        step is skipped, the undo entry is left open on the collection,
        which blocks every other undoable operation in Anki (including
        Workflow mode's own Apply/Generate) until Anki is restarted.
        """
        try:
            aqt.mw.col.merge_undo_entries(self._apply_undo_id)
        except Exception as e:
            logger.warning(f'exception merging undo entries after failed chunk: {e}')
        self.batch_operation_failed(exception)

    def _finish_apply_chain(self):
        try:
            aqt.mw.col.merge_undo_entries(self._apply_undo_id)
        except Exception as e:
            logger.warning(f'exception merging undo entries after chunked apply: {e}')
        self.finished_apply_audio_fn(None)

    def stop_button_pressed(self):
        self.batch_status.stop()

    def prepare_audio_fn(self, anki_collection):
        return self.hypertts.prepare_batch_audio_generation(self.note_id_list, self.generated_batch_model, self.batch_status)

    def finished_prepare_audio_fn(self, prepared_batch):
        self.prepared_batch_audio = prepared_batch
        if not self.batch_status.must_continue:
            self.batch_status.end(False)
            return
        self.hypertts.anki_utils.run_in_background(self.generate_audio_fn, self.finished_generate_audio_fn)

    def generate_audio_fn(self):
        return self.hypertts.generate_prepared_batch_audio(self.prepared_batch_audio, self.batch_status)

    def finished_generate_audio_fn(self, result):
        try:
            generated_results = result.result()
            self.prepared_batch_audio = None
            if self.batch_status.must_continue:
                self.generated_batch_results = generated_results
                self.batch_run_mode = 'ready'
                self.batch_status.end(True)
            else:
                self.generated_batch_results = None
                self.generated_batch_model = None
                self.batch_run_mode = 'idle'
                self.batch_status.end(False)
        except Exception as e:
            self.batch_operation_failed(e)

    def finished_apply_audio_fn(self, result):
        logger.debug(f'finished_apply_audio_fn, result: {result}')
        self.generated_batch_results = None
        self.generated_batch_model = None
        self.batch_run_mode = 'idle'
        self.batch_status.end(True)
        failure_records = self.batch_status.get_failure_records()
        if len(failure_records) == 0:
            return
        add_tag_requested = component_failure_report.show_failure_report(self.hypertts, self.dialog, failure_records, batch_preview=self)
        if add_tag_requested:
            self.failed_note_ids_to_tag = list(dict.fromkeys(record.note_id for record in failure_records))
            self.hypertts.anki_utils.run_in_background_collection_op(
                self.dialog,
                self.apply_error_tags_fn,
                self.finished_apply_error_tags_fn,
            )

    def apply_error_tags_fn(self, anki_collection):
        self.hypertts.tag_error_notes(self.failed_note_ids_to_tag, anki_collection)

    def finished_apply_error_tags_fn(self, result):
        if len(self.failed_note_ids_to_tag) == 0:
            return
        self.hypertts.anki_utils.tooltip_message(
            i18n.get_text("workflow_error_tag_added", self.hypertts.get_ui_language()).format(
                tag=constants.WORKFLOW_ERROR_TAG,
                count=len(self.failed_note_ids_to_tag),
            )
        )
        self.failed_note_ids_to_tag = []

    def batch_operation_failed(self, exception):
        logger.error(f'batch operation failed: {exception}')
        self.batch_run_mode = 'idle'
        self.prepared_batch_audio = None
        self.generated_batch_results = None
        self.generated_batch_model = None
        self.batch_status.end(False)
        self.hypertts.anki_utils.report_unknown_exception_background(exception)

    def batch_start(self):
        if not self.apply_to_notes_batch_started:
            return
        self.hypertts.anki_utils.run_on_main(self.show_running_stack)
        self.hypertts.anki_utils.run_on_main(self.batch_start_fn)

    def batch_end(self, completed):
        if not self.apply_to_notes_batch_started:
            self.hypertts.anki_utils.run_on_main(self.reset_progress_ui)
            return

        def finish_progress_ui():
            if hasattr(self, 'enhanced_progress_widget'):
                if completed:
                    completed_count, total_count = self.batch_status.get_progress_counts()
                    if total_count > 0:
                        self.enhanced_progress_widget.update_progress(total_count, total_count, self.enhanced_progress_widget.start_time)
                    self.enhanced_progress_widget.set_completed()
                    self.show_running_stack()
                else:
                    self.enhanced_progress_widget.set_cancelled()
                    self.show_not_running_stack()

        self.hypertts.anki_utils.run_on_main(finish_progress_ui)
        if self.apply_to_notes_batch_started:
            self.batch_end_fn(completed)
        self.apply_to_notes_batch_started = False

    def update_progress_bar(self, row: int, total_count: int, completed_count: int, start_time: timedelta, current_time: timedelta) -> None:
        """Single path for progress updates."""
        self._update_enhanced_progress(completed_count, total_count, start_time, current_time)


    def table_viewport_repaint_refresh_timer(self):
        # needs to be called on main thread
        self.hypertts.anki_utils.call_on_timer_expire(self.table_repaint_timer, self.table_viewport_repaint)        

    def table_viewport_repaint(self):
        if self.table_view != None:
            # logger.info('table_viewport_repaint')
            self.table_view.viewport().repaint()
            # If scrollbar reports no room to scroll but more pages exist, attempt to load next page.
            try:
                sb = self.table_view.verticalScrollBar()
                if sb is not None and sb.maximum() <= 0 and self.batch_preview_table_model.has_more_pages():
                    self.batch_preview_table_model.load_next_page()
            except Exception:
                pass

    def batch_change(self, note_id: int, row: int, total_count: int, completed_count: int, start_time: timedelta, current_time: timedelta) -> None:
        """
        Update batch progress display.
        
        Args:
            note_id: Current note being processed
            row: Row index in table
            total_count: Total number of notes
            completed_count: Number of completed notes
            start_time: Batch start time
            current_time: Current time
        """
        now = time.monotonic()
        should_throttle = (
            completed_count != total_count and
            completed_count % 25 != 0 and
            (now - self._last_batch_change_time) < 0.2
        )
        if should_throttle:
            return
        self._last_batch_change_time = now

        # Update table row and progress bar separately on main thread
        self.hypertts.anki_utils.run_on_main(lambda: self.batch_preview_table_model.notifyChange(row))
        self.hypertts.anki_utils.run_on_main(lambda: self.update_progress_bar(row, total_count, completed_count, start_time, current_time))
        self.hypertts.anki_utils.run_on_main(lambda: self.table_viewport_repaint_refresh_timer())
        if row == self.selected_row:
            self.hypertts.anki_utils.run_on_main(self.update_error_label_for_selected)
            self.hypertts.anki_utils.run_on_main(self.report_sample_text)
    
    def _update_enhanced_progress(self, completed_count: int, total_count: int, start_time: timedelta, current_time: timedelta) -> None:
        """Update the enhanced progress widget with current statistics."""
        if hasattr(self, 'enhanced_progress_widget'):
            try:
                # Convert timedelta to datetime for the widget
                start_datetime = datetime.now() - (current_time - start_time)
                self.enhanced_progress_widget.update_progress(completed_count, total_count, start_datetime)
                self.enhanced_progress_widget.set_phase(self.batch_status.phase)
                self.enhanced_progress_widget.set_status_text(self.batch_status.status_message)
            except Exception as e:
                logger.warning(f"Error updating enhanced progress widget: {e}")

    def rerun_failed_notes(self, failed_note_ids: List[int]) -> None:
        """Open a fresh batch dialog for the failed notes without starting the run immediately."""
        if not failed_note_ids:
            return
        from . import component_batch
        batch_model = copy.deepcopy(self.batch_model)
        component_batch.open_batch_dialog_for_model(self.hypertts, failed_note_ids, batch_model)
