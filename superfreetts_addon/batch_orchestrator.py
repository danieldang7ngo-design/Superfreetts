"""
batch_orchestrator.py — Orchestrates batch audio generation for Super Free TTS.

Handles:
  - Batch task preparation and note analysis.
  - Duplicate task analysis (deduplication).
  - Parallel generation coordination using engine-specific/global executors.
  - Single-transaction note update applications.
  - Checkpoint loading, saving, and deletion for resume.
"""

import time
import copy
import threading
import concurrent.futures
from typing import List, Dict, Tuple, Any, Optional

from . import constants
from . import config_models
from . import errors
from . import context
from . import batch_progress_ui
from . import system_utils
from . import audio_file_store
from . import logging_utils
from . import i18n
from . import source_text_resolver
from . import batch_executor
from . import text_utils

logger = logging_utils.get_child_logger(__name__)


class BatchOrchestrator:
    """
    Orchestrates pre-processing, generation, progress-tracking, deduplication,
    and application of batch audio generation tasks.
    Delegates audio store writes, voice mapping, and note updates back to ``SuperFreeTTS``.
    """

    def __init__(self, hypertts: Any) -> None:
        self.hypertts = hypertts
        self.anki_utils = hypertts.anki_utils
        self.service_manager = hypertts.service_manager
        self.text_processing_cache = hypertts.text_processing_cache

    @property
    def executor(self) -> Any:
        return self.hypertts.executor

    @property
    def audio_store(self) -> Any:
        return self.hypertts.audio_store

    def _set_batch_status_with_ui_refresh(self, batch_status: Any, message: str, phase: Optional[Any] = None) -> None:
        if phase is not None:
            batch_status.set_phase(phase)
        batch_status.set_status_message(message)

    def prepare_batch_audio_generation(self, note_id_list: List[int], batch: config_models.BatchConfig, batch_status: Any) -> Dict[str, Any]:
        """Prepare note/text/voice tasks without generating audio or updating notes."""
        tasks = []
        audio_request_context = context.AudioRequestContext(constants.AudioRequestReason.batch)
        lang = self.hypertts.get_ui_language()

        self._set_batch_status_with_ui_refresh(
            batch_status,
            i18n.get_text("status_loading_voices", lang),
            batch_progress_ui.BatchProgressPhase.LOADING,
        )
        logger.info(f'[BATCH] Pre-loading voice list for faster audio generation...')
        pre_load_start = time.time()
        try:
            _ = self.service_manager.full_voice_list()
            pre_load_time = time.time() - pre_load_start
            logger.info(f'[BATCH] Voice list pre-loaded in {pre_load_time:.2f}s')
        except Exception as e:
            logger.warning(f'[BATCH] Voice list pre-load failed: {e}')

        self._set_batch_status_with_ui_refresh(
            batch_status,
            i18n.get_text("status_preparing_notes", lang).format(len(note_id_list)),
            batch_progress_ui.BatchProgressPhase.PREPARING,
        )
        logger.info(f'[BATCH] Starting to prepare {len(note_id_list)} notes...')
        extract_start = time.time()

        for note_id in note_id_list:
            if not batch_status.must_continue:
                break

            note = self.anki_utils.get_note_by_id(note_id)
            try:
                source_text = self.hypertts.get_source_text(note, batch.source, None)

                cache_key = source_text_resolver.text_processing_cache_key(source_text, batch.text_processing)
                if cache_key not in self.text_processing_cache:
                    processed_text = self.hypertts.process_text(source_text, batch.text_processing)
                    self.text_processing_cache[cache_key] = processed_text
                else:
                    processed_text = self.text_processing_cache[cache_key]
                    logger.debug(f"[BATCH] Text cache hit")

                sequence_index = len(tasks)
                priority_voice_list = None
                if batch.voice_selection.selection_mode == constants.VoiceSelectionMode.priority:
                    priority_voice_list = copy.copy(batch.voice_selection.voice_list)

                chosen_voice = self.hypertts.choose_voice(batch.voice_selection, priority_voice_list, sequence_index)

                task = {
                    'note_id': note_id,
                    'source_text': source_text,
                    'processed_text': processed_text,
                    'batch': batch,
                    'audio_request_context': audio_request_context,
                    'chosen_voice': chosen_voice,
                }

                if priority_voice_list is not None:
                    task['priority_voice_list'] = priority_voice_list
                tasks.append(task)
            except Exception as e:
                with batch_status.get_note_action_context(note_id, False) as note_action_context:
                    note_action_context.set_error(e)

        extract_time = time.time() - extract_start
        logger.info(f'[BATCH] Prepared {len(tasks)} notes in {extract_time:.2f}s')

        self._set_batch_status_with_ui_refresh(
            batch_status,
            i18n.get_text("status_analyzing_duplicates", lang),
            batch_progress_ui.BatchProgressPhase.DEDUPLICATING,
        )
        logger.info(f'[BATCH] Analyzing for duplicate (text + voice) combinations...')
        dedup_start = time.time()
        dedup_map = self._collect_batch_duplicates(tasks)
        dedup_time = time.time() - dedup_start

        unique_count = len(dedup_map)
        total_count = len(tasks)
        if unique_count < total_count and total_count > 0:
            logger.info(f'[BATCH] Deduplication found: {total_count} tasks, {unique_count} unique, {total_count - unique_count} duplicates (saving {((total_count - unique_count) / total_count) * 100:.1f}% TTS calls) - analyzed in {dedup_time:.2f}s')
        else:
            logger.info(f'[BATCH] No duplicates found - analyzed in {dedup_time:.2f}s')

        return {
            'tasks': tasks,
            'dedup_map': dedup_map,
        }

    def generate_prepared_batch_audio(self, prepared_batch: Dict[str, Any], batch_status: Any) -> List[Tuple]:
        """Generate audio files for prepared tasks without touching Anki media or notes."""
        start_time = time.time()
        lang = self.hypertts.get_ui_language()
        tasks = prepared_batch.get('tasks', [])
        dedup_map = prepared_batch.get('dedup_map', {})

        if not batch_status.must_continue:
            return []

        max_workers = system_utils.get_max_workers()
        unique_count = len(dedup_map)
        batch_status.total_unique_tasks = unique_count
        batch_status.unique_tasks_completed = 0

        self._set_batch_status_with_ui_refresh(
            batch_status,
            i18n.get_text("status_generating_audio", lang).format(unique_count),
            batch_progress_ui.BatchProgressPhase.GENERATING,
        )
        logger.info(f"[BATCH] Starting audio generation with {max_workers} workers ({unique_count} unique combinations)")

        audio_cache = self._execute_unique_tasks_unified(tasks, dedup_map, batch_status)
        logger.info(f'[BATCH] Generated {len(audio_cache)} audio files in {time.time() - start_time:.2f}s')

        batch_status.futures_to_cancel.clear()
        batch_status.total_unique_tasks = 0
        batch_status.unique_tasks_completed = 0

        results = self._apply_batch_deduplication(tasks, dedup_map, audio_cache, batch_status)
        audio_cache.clear()
        self.text_processing_cache.clear()

        self._set_batch_status_with_ui_refresh(
            batch_status,
            i18n.get_text("status_ready_to_apply", lang).format(len(results)),
            batch_progress_ui.BatchProgressPhase.COMPLETED,
        )
        logger.info(f'[BATCH] Audio generation ready to apply: {len(results)} note results')
        return results

    def apply_generated_batch_audio(self, generated_results: List[Tuple], batch: config_models.BatchConfig, batch_status: Any, anki_collection: Any) -> None:
        """Apply generated audio results to Anki media and notes."""
        lang = self.hypertts.get_ui_language()
        batch_status.total_unique_tasks = len(generated_results)
        batch_status.unique_tasks_completed = 0

        self._set_batch_status_with_ui_refresh(
            batch_status,
            i18n.get_text("status_applying_notes", lang).format(len(generated_results)),
            batch_progress_ui.BatchProgressPhase.SAVING,
        )
        logger.info(f'[BATCH] Applying generated audio to {len(generated_results)} notes...')
        update_start = time.time()

        notes_to_update = []
        for idx, (note_id, source_text, processed_text, sound_file, full_filename, is_error) in enumerate(generated_results):
            if not batch_status.must_continue:
                break

            with batch_status.get_note_action_context(note_id, False) as note_action_context:
                try:
                    if is_error:
                        note_action_context.set_error(is_error)
                    else:
                        note = self.anki_utils.get_note_by_id(note_id)
                        self.hypertts._update_note_with_audio(note, batch, source_text, sound_file, full_filename, anki_collection, update_collection=False)
                        notes_to_update.append(note)
                        note_action_context.set_source_text(source_text)
                        note_action_context.set_processed_text(processed_text)
                        note_action_context.set_sound(sound_file)
                        note_action_context.set_status(constants.BatchNoteStatus.Done)
                except Exception as e:
                    logger.error(f"Error updating note {note_id}: {e}")
                    note_action_context.set_error(e)

            batch_status.unique_tasks_completed = idx + 1
            batch_status.notify_change(note_id)

        if notes_to_update and batch_status.must_continue:
            logger.info(f'[BATCH] Saving {len(notes_to_update)} notes in single transaction...')
            anki_collection.update_notes(notes_to_update)
            logger.info(f'[BATCH] Notes saved successfully')

        batch_status.total_unique_tasks = 0
        batch_status.unique_tasks_completed = 0
        batch_status.set_status_message(None)
        logger.info(f'[BATCH] Applied generated audio in {time.time() - update_start:.2f}s')

    def process_batch_audio(self, note_id_list: List[int], batch: config_models.BatchConfig, batch_status: Any, anki_collection: Any) -> None:
        start_time = time.time()
        tasks = []
        audio_request_context = context.AudioRequestContext(constants.AudioRequestReason.batch)

        logger.info(f'[BATCH] Using multi-engine batch executor')

        batch_name = batch.name or f"batch_{int(time.time())}"
        original_note_id_list = note_id_list[:]
        checkpoint_data = self.executor.checkpoint.load(batch_name)
        checkpoint = None
        checkpoint_enabled = True
        
        if checkpoint_data and checkpoint_data.get('completed_indices'):
            completed = checkpoint_data.get('completed_indices', [])
            pending_notes = [note_id_list[i] for i in range(len(note_id_list)) if i not in completed]
            if pending_notes:
                logger.info(f'[BATCH] Resuming: {len(pending_notes)}/{len(note_id_list)} notes remaining')
                note_id_list = pending_notes
                checkpoint = checkpoint_data
            else:
                logger.info(f'[BATCH] {batch_name} already completed')
                self.executor.checkpoint.remove(batch_name)
                checkpoint = None
        else:
            checkpoint = {
                'batch_name': batch_name,
                'completed_indices': [],
                'note_id_list': original_note_id_list,
                'errors': {}
            }

        with batch_status.get_batch_running_action_context():
            try:
                lang = self.hypertts.get_ui_language()
                self._set_batch_status_with_ui_refresh(
                    batch_status,
                    i18n.get_text("status_loading_voices", lang),
                    batch_progress_ui.BatchProgressPhase.LOADING,
                )
                logger.info(f'[BATCH] Pre-loading voice list for faster audio generation...')
                pre_load_start = time.time()
                try:
                    _ = self.service_manager.full_voice_list()
                    pre_load_time = time.time() - pre_load_start
                    logger.info(f'[BATCH] Voice list pre-loaded in {pre_load_time:.2f}s')
                except Exception as e:
                    logger.warning(f'[BATCH] Voice list pre-load failed: {e}')

                self._set_batch_status_with_ui_refresh(
                    batch_status,
                    i18n.get_text("status_preparing_notes", lang).format(len(note_id_list)),
                    batch_progress_ui.BatchProgressPhase.PREPARING,
                )
                logger.info(f'[BATCH] Starting to prepare {len(note_id_list)} notes...')
                extract_start = time.time()

                for idx, note_id in enumerate(note_id_list):
                    if not batch_status.must_continue:
                        break

                    note = self.anki_utils.get_note_by_id(note_id)
                    try:
                        source_text = self.hypertts.get_source_text(note, batch.source, None)
                        
                        cache_key = source_text_resolver.text_processing_cache_key(source_text, batch.text_processing)
                        if cache_key not in self.text_processing_cache:
                            processed_text = self.hypertts.process_text(source_text, batch.text_processing)
                            self.text_processing_cache[cache_key] = processed_text
                        else:
                            processed_text = self.text_processing_cache[cache_key]
                            logger.debug(f"[BATCH] Text cache hit")
                        
                        sequence_index = len(tasks)

                        priority_voice_list = None
                        if batch.voice_selection.selection_mode == constants.VoiceSelectionMode.priority:
                            priority_voice_list = copy.copy(batch.voice_selection.voice_list)

                        chosen_voice = self.hypertts.choose_voice(batch.voice_selection, priority_voice_list, sequence_index)

                        task = {
                            'note_id': note_id,
                            'source_text': source_text,
                            'processed_text': processed_text,
                            'batch': batch,
                            'audio_request_context': audio_request_context,
                            'chosen_voice': chosen_voice,
                        }

                        if priority_voice_list is not None:
                            task['priority_voice_list'] = priority_voice_list
                        tasks.append(task)
                    except Exception as e:
                        with batch_status.get_note_action_context(note_id, False) as note_action_context:
                            note_action_context.set_error(e)

                extract_time = time.time() - extract_start
                logger.info(f'[BATCH] Prepared {len(tasks)} notes in {extract_time:.2f}s')

                if not batch_status.must_continue:
                    return

                self._set_batch_status_with_ui_refresh(
                    batch_status,
                    i18n.get_text("status_analyzing_duplicates", lang),
                    batch_progress_ui.BatchProgressPhase.DEDUPLICATING,
                )
                logger.info(f'[BATCH] Analyzing for duplicate (text + voice) combinations...')
                dedup_start = time.time()
                dedup_map = self._collect_batch_duplicates(tasks)
                dedup_time = time.time() - dedup_start

                unique_count = len(dedup_map)
                total_count = len(tasks)
                if unique_count < total_count:
                    logger.info(f'[BATCH] Deduplication found: {total_count} tasks, {unique_count} unique, {total_count - unique_count} duplicates (saving {((total_count - unique_count) / total_count) * 100:.1f}% TTS calls) - analyzed in {dedup_time:.2f}s')
                else:
                    logger.info(f'[BATCH] No duplicates found - analyzed in {dedup_time:.2f}s')

                max_workers = system_utils.get_max_workers()
                logger.info(f"[BATCH] Parallel generation started: engine pools will respect their own limits")

                batch_status.total_unique_tasks = unique_count
                batch_status.unique_tasks_completed = 0

                self._set_batch_status_with_ui_refresh(
                    batch_status,
                    i18n.get_text("status_generating_audio", lang).format(unique_count),
                    batch_progress_ui.BatchProgressPhase.GENERATING,
                )
                logger.info(f"[BATCH] Starting audio generation with {max_workers} workers ({unique_count} unique combinations)")
                gen_start = time.time()

                audio_cache = self._execute_unique_tasks_unified(tasks, dedup_map, batch_status)

                gen_time = time.time() - gen_start
                logger.info(f'[BATCH] Generated {len(audio_cache)} audio files in {gen_time:.2f}s')

                batch_status.futures_to_cancel.clear()

                batch_status.total_unique_tasks = 0
                batch_status.unique_tasks_completed = 0
                
                self._set_batch_status_with_ui_refresh(
                    batch_status,
                    i18n.get_text("status_applying_notes", lang).format(len(tasks)),
                    batch_progress_ui.BatchProgressPhase.SAVING,
                )

                logger.info(f'[BATCH] Applying audio to {len(tasks)} notes...')
                apply_start = time.time()
                results = self._apply_batch_deduplication(tasks, dedup_map, audio_cache, batch_status)
                apply_time = time.time() - apply_start
                logger.info(f'[BATCH] Applied results in {apply_time:.2f}s')

                audio_cache.clear()
                del audio_cache
                dedup_map.clear()
                del dedup_map
                tasks.clear()
                del tasks

                self._set_batch_status_with_ui_refresh(
                    batch_status,
                    i18n.get_text("status_saving_collection", lang),
                    batch_progress_ui.BatchProgressPhase.SAVING,
                )
                logger.info(f'[BATCH] Updating Anki collection with {len(results)} note changes...')
                update_start = time.time()

                notes_to_update = []
                for idx, (note_id, source_text, processed_text, sound_file, full_filename, is_error) in enumerate(results):
                    if not batch_status.must_continue:
                        break

                    note_status = batch_status.note_status_map.get(note_id)
                    already_done = note_status and note_status.status == constants.BatchNoteStatus.Done

                    with batch_status.get_note_action_context(note_id, False) as note_action_context:
                        try:
                            if is_error:
                                note_action_context.set_error(is_error)
                                if checkpoint:
                                    checkpoint['errors'][str(idx)] = str(is_error)
                            else:
                                note = self.anki_utils.get_note_by_id(note_id)
                                self.hypertts._update_note_with_audio(note, batch, source_text, sound_file, full_filename, anki_collection, update_collection=False)
                                notes_to_update.append(note)

                                if not already_done:
                                    note_action_context.set_source_text(source_text)
                                    note_action_context.set_processed_text(processed_text)
                                    note_action_context.set_sound(sound_file)
                                    note_action_context.set_status(constants.BatchNoteStatus.Done)
                        except Exception as e:
                            logger.error(f"Error updating note {note_id}: {e}")
                            note_action_context.set_error(e)
                            if checkpoint:
                                checkpoint['errors'][str(idx)] = str(e)

                if notes_to_update and batch_status.must_continue:
                    logger.info(f'[BATCH] Saving {len(notes_to_update)} notes in single transaction...')
                    anki_collection.update_notes(notes_to_update)
                    logger.info(f'[BATCH] Notes saved successfully')
                    
                    if checkpoint and checkpoint_enabled:
                        try:
                            completed_list = checkpoint.get('completed_indices', [])
                            for idx in range(len(results)):
                                if idx not in completed_list:
                                    completed_list.append(idx)
                            self.executor.checkpoint.save(batch_name, completed_list, checkpoint.get('note_id_list', []), checkpoint.get('errors', {}))
                        except Exception as e:
                            logger.warning(f'[BATCH] Failed to save checkpoint: {e}')
                            checkpoint_enabled = False

                update_time = time.time() - update_start
                total_time = time.time() - start_time
                logger.info(f'[BATCH] Completed in {total_time:.2f}s')

                results.clear()
                del results

                if batch_status.must_continue:
                    if checkpoint and checkpoint_enabled:
                        self.executor.checkpoint.remove(batch_name)
                    logger.info(f'[BATCH] Batch completed successfully')
                else:
                    if checkpoint and checkpoint_enabled:
                        logger.info(f'[BATCH] Batch cancelled, checkpoint saved for resume')
                
                batch_status.set_status_message(None)
            
            finally:
                batch_status.futures_to_cancel.clear()
                self.text_processing_cache.clear()
                logger.info(f'[BATCH] Cleanup complete')

    def _collect_batch_duplicates(self, tasks: List[Dict[str, Any]]) -> Dict[Tuple, List[int]]:
        dedup_map = {}
        if not tasks:
            return dedup_map

        for task_idx, task_data in enumerate(tasks):
            processed_text = task_data['processed_text']
            voice_with_options = task_data.get('chosen_voice')
            voice_id = voice_with_options.voice_id if voice_with_options else None
            voice_options = voice_with_options.options if voice_with_options else {}

            if voice_id is None:
                dedup_key = (f'no_voice_{task_idx}',)
            else:
                dedup_key = self.audio_store.build_request_key(processed_text, voice_id, voice_options)

            if dedup_key not in dedup_map:
                dedup_map[dedup_key] = []
            dedup_map[dedup_key].append(task_idx)

        return dedup_map

    def _execute_unique_tasks_unified(self, tasks: List[Dict], dedup_map: Dict, batch_status: Any) -> Dict[Any, Tuple]:
        lang = self.hypertts.get_ui_language()
        audio_cache = {}
        completed_count = 0
        unique_count = len(dedup_map)
        sequence_mode = (
            len(tasks) > 0
            and tasks[0].get('batch')
            and tasks[0]['batch'].voice_selection.selection_mode == constants.VoiceSelectionMode.sequence
        )
        
        engine_groups = {}

        if not sequence_mode:
            for dedup_key, task_indices in dedup_map.items():
                task_idx = task_indices[0]
                task_data = tasks[task_idx]
                service_name = self.executor.detect_service(task_data)
                chosen_voice = task_data.get('chosen_voice')
                voice_id_str = str(chosen_voice.voice_id) if chosen_voice else "None"

                group_key = (service_name, voice_id_str)
                if group_key not in engine_groups:
                    engine_groups[group_key] = []
                engine_groups[group_key].append((dedup_key, task_data, task_indices))

        BATCH_SIZE_BY_ENGINE = {
            'EdgeTTS': 1,
            'PiperTTS': 1,
            'KokoroTTS': 1,
            'MmsTTS': 1,
            'Piper': 1,
            'Kokoro': 1,
            'MMS': 1,
        }
        DEFAULT_BATCH_SIZE = 1
        all_chunks = []

        sequence_service_gates: Dict[str, threading.BoundedSemaphore] = {}
        sequence_pool: Optional[concurrent.futures.ThreadPoolExecutor] = None

        if sequence_mode:
            ordered_items = []
            for dedup_key, task_indices in dedup_map.items():
                task_idx = task_indices[0]
                ordered_items.append((dedup_key, tasks[task_idx], task_indices))

            service_limits = self.hypertts._get_sequence_service_limits(ordered_items)
            total_seq_workers = max(1, sum(service_limits.values()))

            sequence_service_gates = {
                svc: threading.BoundedSemaphore(limit)
                for svc, limit in service_limits.items()
            }

            sequence_pool = batch_executor.BoundedThreadPoolExecutor(
                max_workers=total_seq_workers,
                thread_name_prefix="TTS-Seq",
                max_waiting_tasks=20,
            )

            logger.info(
                f"[BATCH] Sequence mode — continuous filling: service_limits={service_limits}, "
                f"pool_workers={total_seq_workers}, notes={len(ordered_items)}"
            )

            for item in ordered_items:
                all_chunks.append(('__sequence_single__', [item]))
        else:
            for (service_name, _), group_tasks in engine_groups.items():
                max_batch = BATCH_SIZE_BY_ENGINE.get(service_name, DEFAULT_BATCH_SIZE)
                chunk = []
                chunk_chars = 0
                for item in group_tasks:
                    dedup_key, task_data, task_indices = item
                    text = task_data['source_text']
                    text_len = len(text)

                    if len(chunk) >= max_batch or (chunk_chars + text_len > 3000 and chunk):
                        all_chunks.append((service_name, list(chunk)))
                        chunk = []
                        chunk_chars = 0

                    chunk.append(item)
                    chunk_chars += text_len

                if chunk:
                    all_chunks.append((service_name, list(chunk)))

        future_to_chunk = {}
        future_lock = threading.Lock()
        submit_error = [None]
        last_heartbeat_time = 0
        heartbeat_interval_seconds = 2.0
        
        def _submit_all():
            try:
                for service_name, chunk_items in all_chunks:
                    if not batch_status.must_continue:
                        break
                    if service_name == '__sequence_single__':
                        future = sequence_pool.submit(
                            self.hypertts._generate_audio_single_sequence_task,
                            chunk_items[0],
                            sequence_service_gates,
                        )
                    elif service_name == '__sequence__':
                        executor_pool = self.executor.get_executor(service_name)
                        future = executor_pool.submit(self.hypertts._generate_audio_sequence_task, list(chunk_items))
                    else:
                        executor_pool = self.executor.get_executor(service_name)
                        future = executor_pool.submit(self.hypertts._generate_audio_batch_task, list(chunk_items))
                    with future_lock:
                        future_to_chunk[future] = list(chunk_items)
                        batch_status.futures_to_cancel.append(future)
            except Exception as e:
                logger.error(f"[BATCH] Submit thread error: {e}")
                submit_error[0] = e
        
        submit_thread = threading.Thread(target=_submit_all, daemon=True)
        submit_thread.start()
        stall_timeout_seconds = 60.0
        last_progress_time = time.time()

        while submit_thread.is_alive() or future_to_chunk:
            if not batch_status.must_continue:
                with future_lock:
                    for pending_future in list(future_to_chunk):
                        if not pending_future.done():
                            pending_future.cancel()
                break
            
            done_futures = []
            with future_lock:
                for future in list(future_to_chunk):
                    if future.done():
                        done_futures.append((future, future_to_chunk.pop(future)))
                        try:
                            batch_status.futures_to_cancel.remove(future)
                        except ValueError:
                            pass
            
            if not done_futures:
                current_time = time.time()
                if current_time - last_heartbeat_time >= heartbeat_interval_seconds:
                    with future_lock:
                        active_count = sum(1 for pending_future in future_to_chunk if not pending_future.done())
                    batch_status.set_status_message(
                        i18n.get_text("status_generating_audio_active", lang).format(
                            completed_count,
                            unique_count,
                            active_count,
                        )
                    )
                    last_heartbeat_time = current_time

                # detect stall: no completed futures for a while -> cancel pending and mark errors
                if current_time - last_progress_time > stall_timeout_seconds and len(future_to_chunk) > 0:
                    logger.error(f"[BATCH] Generation stalled for {stall_timeout_seconds}s, cancelling pending tasks")
                    with future_lock:
                        pending = list(future_to_chunk.items())
                        future_to_chunk.clear()
                        for pending_future, chunk in pending:
                            try:
                                pending_future.cancel()
                            except Exception:
                                pass
                            # mark each task in chunk as failed due to stall
                            for dedup_key, task_data, task_indices in chunk:
                                audio_cache[dedup_key] = (None, Exception(i18n.get_text("error_batch_stalled", lang) if i18n.get_text("error_batch_stalled", lang) else "Batch generation stalled"))
                                completed_count += 1
                                batch_status.unique_tasks_completed = completed_count
                                for task_idx in task_indices:
                                    note_id = tasks[task_idx]['note_id']
                                    with batch_status.get_note_action_context(note_id, False) as ctx:
                                        ctx.set_error(Exception(i18n.get_text("error_batch_stalled", lang) if i18n.get_text("error_batch_stalled", lang) else "Batch generation stalled"))
                                    batch_status.notify_change(note_id)
                    # Mark stalled tasks and continue processing remaining futures instead of aborting
                    batch_status.set_status_message(i18n.get_text("status_batch_stalled", lang) if i18n.get_text("status_batch_stalled", lang) else None)

                time.sleep(0.05)
                continue
            
            for future, chunk in done_futures:
                try:
                    batch_results = future.result(timeout=25.0) 
                    
                    for i, (dedup_key, task_data, task_indices) in enumerate(chunk):
                        result_tuple = batch_results[i] if i < len(batch_results) else (None, Exception("Internal error"))
                        audio_cache[dedup_key] = result_tuple
                        result, error = result_tuple
                        
                        completed_count += 1
                        batch_status.unique_tasks_completed = completed_count
                        
                        is_successful = result is not None
                        for task_idx in task_indices:
                            note_id = tasks[task_idx]['note_id']
                            with batch_status.get_note_action_context(note_id, False) as ctx:
                                if is_successful:
                                    src, proc, audio_fn, full_fn = result
                                    ctx.set_source_text(src)
                                    ctx.set_processed_text(proc)
                                    ctx.set_sound(audio_fn)
                                    ctx.set_status(constants.BatchNoteStatus.Generated)
                                else:
                                    ctx.set_error(error if error else Exception(i18n.get_text("error_audio_gen_failed", lang)))
                            batch_status.notify_change(note_id)
                    
                    batch_status.set_status_message(i18n.get_text("status_generating_audio_progress", lang).format(completed_count, unique_count))
                    self.executor.monitor.maybe_gc(completed_count)
                    del batch_results
                    last_progress_time = time.time()
                except Exception as e:
                    logger.error(f"[BATCH] Batch execution failed: {e}")
                    for dedup_key, _, task_indices in chunk:
                        audio_cache[dedup_key] = (None, e)
                        completed_count += 1
                        for task_idx in task_indices:
                            note_id = tasks[task_idx]['note_id']
                            with batch_status.get_note_action_context(note_id, False) as ctx:
                                ctx.set_error(e)
                            batch_status.notify_change(note_id)
                    self.executor.monitor.maybe_gc(completed_count)
        
        submit_thread.join(timeout=5.0)
        if submit_error[0]:
            logger.error(f"[BATCH] Submit thread encountered an error: {submit_error[0]}")

        if sequence_pool is not None:
            try:
                sequence_pool.shutdown(wait=False)
            except Exception:
                pass

        return audio_cache

    def _apply_batch_deduplication(self, tasks: List[Dict], dedup_map: Dict, audio_cache: Dict, batch_status: Any) -> List[Tuple]:
        results = []
        for dedup_key, task_indices in dedup_map.items():
            if dedup_key not in audio_cache:
                logger.warning('audio cache missing result for dedup_key')
                continue

            cached_result = audio_cache[dedup_key]
            res, err = cached_result
            if res is None:
                for task_idx in task_indices:
                    note_id = tasks[task_idx]['note_id']
                    results.append((note_id, None, None, None, None, err))
                continue

            source_text, processed_text, sound_file, full_filename = res
            for task_idx in task_indices:
                note_id = tasks[task_idx]['note_id']
                results.append((note_id, source_text, processed_text, sound_file, full_filename, None))

        return results

    def populate_batch_status_processed_text(self, note_id_list: Optional[List[int]], batch_source: Any, text_processing: Any, batch_status: Any) -> None:
        if note_id_list is None:
            note_id_list = batch_status.note_id_list
        with batch_status.get_batch_running_action_context():
            for note_id in note_id_list:
                with batch_status.get_note_action_context(note_id, True) as note_action_context:
                    note = self.anki_utils.get_note_by_id(note_id)
                    source_text, processed_text = self.get_source_processed_text(note, batch_source, text_processing)
                    note_action_context.set_source_text(source_text)
                    note_action_context.set_processed_text(processed_text)
                    note_action_context.set_status(constants.BatchNoteStatus.OK)
                if not batch_status.must_continue:
                    logger.info('batch_status execution interrupted')
                    break

    def get_source_processed_text(self, note: Any, batch_source: Any, text_processing: Any) -> Tuple[str, str]:
        source_text = self.hypertts.get_source_text(note, batch_source, None)
        logger.debug(f'get_source_processed_text: source_text: {source_text}')
        processed_text = text_utils.process_text(source_text, text_processing)
        return source_text, processed_text
