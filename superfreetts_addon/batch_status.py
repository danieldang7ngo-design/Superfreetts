import sys
import time
from dataclasses import dataclass
from typing import List, Dict, Optional, Any

from . import constants
from . import errors
from . import batch_progress_ui
from . import logging_utils
logger = logging_utils.get_child_logger(__name__)


@dataclass
class FailureRecord:
    note_id: int
    failed_text: str
    error_message: str
    source_text: Optional[str] = None
    processed_text: Optional[str] = None
    preset_name: Optional[str] = None

class NoteStatus():
    """Tracks the status and data of a single note in batch processing."""
    
    def __init__(self, note_id: int) -> None:
        """Initialize note status tracking."""
        self.note_id: int = note_id
        self.source_text: Optional[str] = None
        self.processed_text: Optional[str] = None
        self.sound_file: Optional[str] = None
        self.error: Optional[Exception] = None
        self.status: Optional[Any] = None

class BatchNoteActionContext():
    """Context manager for actions on a single note during batch processing."""
    
    def __init__(self, batch_status: 'BatchStatus', note_id: int) -> None:
        """Initialize the context manager."""
        self.batch_status = batch_status
        self.note_id = note_id

    def __enter__(self) -> 'BatchNoteActionContext':
        """Enter context."""
        return self

    def __exit__(self, exception_type: Optional[type], exception_value: Optional[Exception], 
                 traceback: Optional[Any]) -> bool:
        """Exit context and handle exceptions."""
        if exception_value is not None:
            if isinstance(exception_value, errors.HyperTTSError):
                self.batch_status.report_known_error(self.note_id, exception_value)
            else:
                self.batch_status.report_unknown_exception(self.note_id, exception_value)
            self.batch_status.notify_change(self.note_id)
            return True
        self.batch_status.notify_change(self.note_id)
        return False    

    def set_sound(self, sound_file: str) -> None:
        """Set the sound file for this note."""
        self.batch_status.set_sound_file(self.note_id, sound_file)

    def set_source_text(self, source_text: str) -> None:
        """Set the source text for this note."""
        self.batch_status.set_source_text(self.note_id, source_text)

    def set_processed_text(self, processed_text: str) -> None:
        """Set the processed text for this note."""
        self.batch_status.set_processed_text(self.note_id, processed_text)

    def set_status(self, status: Any) -> None:
        """Set the batch status for this note."""
        self.batch_status.set_status(self.note_id, status)

    def set_error(self, exception: Exception) -> None:
        """Set an error for this note and mark status as Error."""
        self.batch_status.report_known_error(self.note_id, exception)

class BatchRunningActionContext():
    """Context manager for running a batch operation."""
    
    def __init__(self, batch_status: 'BatchStatus') -> None:
        """Initialize the context manager."""
        self.batch_status = batch_status

    def __enter__(self) -> 'BatchRunningActionContext':
        """Enter context and mark batch as running."""
        self.batch_status.task_running = True
        self.batch_status.must_continue = True
        self.batch_status.notify_start()
        return self

    def __exit__(self, exception_type: Optional[type], exception_value: Optional[Exception], 
                 traceback: Optional[Any]) -> bool:
        """Exit context and mark batch as complete."""
        self.batch_status.task_running = False
        completed = self.batch_status.must_continue
        self.batch_status.notify_end(completed)
        return False        

class BatchStatus():
    """Tracks the status of batch audio generation operation."""
    
    def __init__(self, anki_utils: Any, note_id_list: List[int], change_listener: Any) -> None:
        """
        Initialize batch status tracking.
        
        Args:
            anki_utils: Anki utilities object
            note_id_list: List of note IDs being processed
            change_listener: Listener for batch status changes (typically UI)
        """
        self.anki_utils = anki_utils
        self.note_id_list = note_id_list
        self.change_listener = change_listener
        self.note_status_array: List[NoteStatus] = []
        self.note_status_map: Dict[int, NoteStatus] = {}
        self.note_id_map: Dict[int, int] = {}
        self.source_model = None
        self.text_processing_model = None
        self.task_running: bool = False
        self.must_continue: bool = False
        self.status_message: Optional[str] = None
        self.phase: str = batch_progress_ui.BatchProgressPhase.LOADING
        self.start_time: Optional[Any] = None
        self.unique_tasks_completed: int = 0
        self.total_unique_tasks: int = 0
        self.futures_to_cancel: List[Any] = []
        self.usage_session_id: Optional[str] = None
        self._change_notify_min_interval = 0.1
        self._last_change_notify_time = None
        i = 0
        for note_id in self.note_id_list:
            note_status = NoteStatus(note_id)
            self.note_status_array.append(note_status)
            self.note_status_map[note_id] = note_status
            self.note_id_map[note_id] = i
            i += 1

    def extend_note_ids(self, additional_note_ids: List[int]):
        """Add more notes to tracking without resetting existing status"""
        for note_id in additional_note_ids:
            if note_id not in self.note_status_map:
                note_status = NoteStatus(note_id)
                self.note_status_array.append(note_status)
                self.note_status_map[note_id] = note_status
                self.note_id_map[note_id] = len(self.note_status_array) - 1
    
    def is_running(self) -> bool:
        """Check if batch is currently running."""
        return self.task_running

    def stop(self) -> None:
        """Stop the running batch and cancel pending futures."""
        logger.info("Stopping current batch")
        self.must_continue = False
        # Cancel all pending futures to avoid blocking on executor shutdown
        for future in self.futures_to_cancel:
            future.cancel()
        self.futures_to_cancel.clear()

    def __getitem__(self, array_index: int) -> NoteStatus:
        """Get note status by array index."""
        return self.note_status_array[array_index]

    def get_batch_running_action_context(self) -> BatchRunningActionContext:
        """Get context manager for batch running operation."""
        return BatchRunningActionContext(self)

    def begin(self) -> None:
        """Mark a multi-step batch operation as running."""
        self.task_running = True
        self.must_continue = True
        self.notify_start()

    def end(self, completed: bool) -> None:
        """Mark a multi-step batch operation as finished."""
        self.task_running = False
        self.notify_end(completed and self.must_continue)

    def get_note_action_context(self, note_id: int, blank_fields: bool) -> BatchNoteActionContext:
        """
        Get context manager for note action.
        
        Args:
            note_id: The note ID to get context for
            blank_fields: If True, reset note fields to blank state
            
        Returns:
            Context manager for note action
        """
        note_status = self.note_status_map[note_id]
        note_status.error = None
        # Only reset status to Processing if this is a new note (blank_fields=True)
        # If blank_fields=False, preserve the current status (e.g., Done from generation phase)
        if blank_fields:
            note_status.status = constants.BatchNoteStatus.Processing
            note_status.source_text = None
            note_status.processed_text = None
            note_status.sound_file = None
        return BatchNoteActionContext(self, note_id)

    # error reporting

    def report_known_error(self, note_id, exception_value):
        self.note_status_map[note_id].status = constants.BatchNoteStatus.Error
        self.note_status_map[note_id].error = exception_value
        self.notify_change(note_id)

    def report_unknown_exception(self, note_id, exception_value):
        self.note_status_map[note_id].status = constants.BatchNoteStatus.Error
        self.note_status_map[note_id].error = exception_value
        self.anki_utils.report_unknown_exception_background(exception_value)
        self.notify_change(note_id)

    # set the various fields on the NoteStatus

    def set_source_text(self, note_id, source_text):
        self.note_status_map[note_id].source_text = source_text
        self.notify_change(note_id)

    def set_processed_text(self, note_id, processed_text):
        self.note_status_map[note_id].processed_text = processed_text
        self.notify_change(note_id)

    def set_sound_file(self, note_id, sound_file):
        self.note_status_map[note_id].sound_file = sound_file
        self.notify_change(note_id)

    def set_status(self, note_id, status):
        self.note_status_map[note_id].status = status
        self.notify_change(note_id)

    def notify_progress(self) -> None:
        """Trigger a UI refresh even when no specific note changed."""
        if len(self.note_id_list) > 0:
            self.notify_change(self.note_id_list[0])

    def set_phase(self, phase: str) -> None:
        """Set stable batch phase independent of translated status text."""
        self.phase = phase
        self.notify_progress()

    def set_status_message(self, message):
        """Set a global status message (e.g., 'Loading voices...', 'Generating audio...')"""
        self.status_message = message
        self.notify_progress()

    def get_progress_counts(self):
        if self.total_unique_tasks > 0:
            return self.unique_tasks_completed, self.total_unique_tasks
        return self.get_completed_count(), len(self.note_id_list)

    def get_completed_count(self):
        """
        Get the actual number of notes that are Done (not just Processing or Error).
        During audio generation phase, this may return 0, so use unique_tasks_completed for ETA.
        """
        completed = 0
        for note_status in self.note_status_array:
            if note_status.status == constants.BatchNoteStatus.Done:
                completed += 1
        return completed
    
    def get_processing_count(self):
        """
        Get number of notes that have been processed (have sound_file set).
        This is useful for tracking progress during audio generation phase.
        """
        processed = 0
        for note_status in self.note_status_array:
            if note_status.sound_file is not None:
                processed += 1
        return processed

    def notify_start(self):
        self.start_time = self.anki_utils.get_current_time()
        self.change_listener.batch_start()

    def notify_change(self, note_id):
        now = time.monotonic()
        if self._last_change_notify_time is not None and (now - self._last_change_notify_time) < self._change_notify_min_interval:
            return
        self._last_change_notify_time = now

        row = self.note_id_map[note_id]
        completed_count, total_count = self.get_progress_counts()
        start_time = self.start_time if self.start_time is not None else self.anki_utils.get_current_time()
        self.change_listener.batch_change(note_id, row, total_count, completed_count, start_time, self.anki_utils.get_current_time())

    def notify_end(self, completed):
        self.change_listener.batch_end(completed)

    def get_failure_records(self, preset_name: Optional[str] = None) -> List[FailureRecord]:
        failure_records: List[FailureRecord] = []
        for note_status in self.note_status_array:
            if note_status.status != constants.BatchNoteStatus.Error:
                continue
            failed_text = note_status.processed_text or note_status.source_text or ''
            error_message = ''
            if note_status.error is not None:
                error_message = str(note_status.error)
            failure_records.append(
                FailureRecord(
                    note_id=note_status.note_id,
                    failed_text=failed_text,
                    error_message=error_message,
                    source_text=note_status.source_text,
                    processed_text=note_status.processed_text,
                    preset_name=preset_name,
                )
            )
        return failure_records

    def get_failed_note_ids(self) -> List[int]:
        failed_note_ids: List[int] = []
        for note_status in self.note_status_array:
            if note_status.status == constants.BatchNoteStatus.Error:
                failed_note_ids.append(note_status.note_id)
        return failed_note_ids
