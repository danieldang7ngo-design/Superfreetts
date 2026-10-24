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
import hashlib
import threading
from typing import List, Dict, Tuple, Any, Optional

from . import constants
from . import config_models
from . import errors
from . import context
from . import audio_file_store
from . import batch_progress_ui
from . import system_utils
from . import logging_utils
from . import i18n
from . import source_text_resolver
from . import batch_executor
from . import batch_constants
from . import text_utils

logger = logging_utils.get_child_logger(__name__)


def preview_checkpoint_key(batch_model: Any, note_ids: List[int], dedup_map: Dict[Any, Any]) -> str:
    """Stable checkpoint key for the live Batch Preview flow.

    Must NOT use ``str(batch_model)`` / ``str(text_processing)``: the default
    object repr embeds a memory address, so the key would change on every
    open and resume could never match.  Instead the key covers:

    - the ordered note selection,
    - the preset name + target field flags (apply destination),
    - the sorted dedup keys (text + voice + options + format fingerprint).

    Changing voice, format, target field or text processing changes the
    fingerprint, so resume starts over (safe) instead of skipping notes
    that would now need different audio.
    """
    target = getattr(batch_model, 'target', None)
    fingerprint = "|".join([
        ",".join(str(n) for n in (note_ids or [])),
        str(getattr(batch_model, "name", "") or ""),
        str(getattr(target, "target_field", "") or ""),
        str(getattr(target, "text_and_sound_tag", "")),
        str(getattr(target, "remove_sound_tag", "")),
        "|".join(sorted(str(k) for k in (dedup_map or {}).keys())),
    ])
    return "preview-" + hashlib.sha1(fingerprint.encode("utf-8"), usedforsecurity=False).hexdigest()[:16]


class BatchOrchestrator:
    """Orchestrates pre-processing, generation, progress-tracking, deduplication,
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

    def _bind_usage_session(self, batch_status: Any, audio_request_context: Any) -> None:
        """Attach the usage-tracking session id to the batch status so later
        apply phases record note_updated against the same session."""
        try:
            session_id = audio_request_context.get_batch_uuid_str()
            batch_status.usage_session_id = session_id
            self.hypertts.usage_tracker.start_batch_session(session_id)
        except Exception as e:
            logger.debug(f"[USAGE] failed to bind batch session: {e}")

    def _record_note_updated(self, batch_status: Any) -> None:
        try:
            session_id = getattr(batch_status, 'usage_session_id', None)
            if session_id:
                self.hypertts.usage_tracker.record_note_updated(session_id)
        except Exception as e:
            logger.debug(f"[USAGE] failed to record note_updated: {e}")

    def prepare_batch_audio_generation(self, note_id_list: List[int], batch: config_models.BatchConfig, batch_status: Any) -> Dict[str, Any]:
        """Prepare note/text/voice tasks without generating audio or updating notes."""
        tasks = []
        audio_request_context = context.AudioRequestContext(constants.AudioRequestReason.batch)
        lang = self.hypertts.get_ui_language()
        self._bind_usage_session(batch_status, audio_request_context)

        LARGE_BATCH_THRESHOLD = 1000
        if len(note_id_list) >= LARGE_BATCH_THRESHOLD:
            self._set_batch_status_with_ui_refresh(
                batch_status,
                i18n.get_text("status_loading_voices", lang),
                batch_progress_ui.BatchProgressPhase.LOADING,
            )
            logger.info(f'[BATCH] Pre-loading voice list ({len(note_id_list)} notes >= {LARGE_BATCH_THRESHOLD})...')
            pre_load_start = time.time()
            try:
                _ = self.service_manager.full_voice_list()
                pre_load_time = time.time() - pre_load_start
                logger.info(f'[BATCH] Voice list pre-loaded in {pre_load_time:.2f}s')
            except Exception as e:
                logger.warning(f'[BATCH] Voice list pre-load failed: {e}')
        else:
            logger.info(f'[BATCH] Skipping voice pre-load ({len(note_id_list)} notes < threshold {LARGE_BATCH_THRESHOLD})')

        self._set_batch_status_with_ui_refresh(
            batch_status,
            f"Loaded 0 of {len(note_id_list)}",
            batch_progress_ui.BatchProgressPhase.PREPARING,
        )
        logger.info(f'[BATCH] Starting to prepare {len(note_id_list)} notes...')
        extract_start = time.time()

        field_maps = self.anki_utils.get_note_field_maps(note_id_list)

        total_notes = len(note_id_list)
        loaded = 0
        for note_id in note_id_list:
            if not batch_status.must_continue:
                break

            loaded += 1
            batch_status.set_status_message(f"Loaded {loaded} of {total_notes}")

            if note_id not in field_maps:
                with batch_status.get_note_action_context(note_id, False) as note_action_context:
                    note_action_context.set_error(errors.NoteNotFoundError(note_id))
                continue

            note_fields = field_maps[note_id]
            try:
                source_text = self.hypertts.get_source_text(note_fields, batch.source, None)

                cache_key = source_text_resolver.text_processing_cache_key(source_text, batch.text_processing)
                if cache_key not in self.text_processing_cache:
                    processed_text = self.hypertts.process_text(source_text, batch.text_processing)
                    self.text_processing_cache[cache_key] = processed_text
                else:
                    processed_text = self.text_processing_cache[cache_key]
                    logger.debug("[BATCH] Text cache hit")

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

        if total_notes > 0:
            batch_status.set_status_message(f"Loaded {total_notes} of {total_notes}")

        self._set_batch_status_with_ui_refresh(
            batch_status,
            i18n.get_text("status_analyzing_duplicates", lang),
            batch_progress_ui.BatchProgressPhase.DEDUPLICATING,
        )
        logger.info('[BATCH] Analyzing for duplicate (text + voice) combinations...')
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

    def generate_prepared_batch_audio(self, prepared_batch: Dict[str, Any], batch_status: Any, checkpoint: Any = None) -> List[Tuple]:
        """Generate audio files for prepared tasks without touching Anki media or notes."""
        start_time = time.time()
        lang = self.hypertts.get_ui_language()
        tasks = prepared_batch.get('tasks', [])
        dedup_map = prepared_batch.get('dedup_map', {})

        if not batch_status.must_continue:
            return []

        # Available RAM may have changed since the executor was built (e.g.
        # Anki has been open for hours).  Re-size the local engine pools before
        # any new runner process is spawned.
        try:
            self.hypertts.orchestrator.refresh_engine_pools_for_current_ram()
        except Exception as e:
            logger.debug(f'[BATCH] Pre-batch RAM refresh skipped: {e}')

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

        # Pre-populate note_status_map so preview shows text even before
        # individual chunks complete (lazy-load only covers visible pages)
        for task in tasks:
            note_id = task['note_id']
            ns = batch_status.note_status_map.get(note_id)
            if ns is not None and ns.source_text is None:
                ns.source_text = task['source_text']
                ns.processed_text = task['processed_text']

        audio_cache = self._execute_unique_tasks_unified(tasks, dedup_map, batch_status, checkpoint)
        logger.info(f'[BATCH] Generated {len(audio_cache)} audio files in {time.time() - start_time:.2f}s')

        batch_status.clear_futures()
        batch_status.total_unique_tasks = 0
        batch_status.unique_tasks_completed = 0

        results = self._apply_batch_deduplication(tasks, dedup_map, audio_cache, batch_status)
        audio_cache.clear()
        self.text_processing_cache.clear()
        # The legacy UnifiedCache was write-only in the live path.  Ensure no
        # stale tuples survive the batch if another caller populated it.
        executor_cache = getattr(self.executor, 'cache', None)
        if executor_cache is not None:
            try:
                executor_cache.clear()
            except Exception as e:
                logger.debug(f'[BATCH] Could not clear executor cache: {e}')

        self._set_batch_status_with_ui_refresh(
            batch_status,
            i18n.get_text("status_ready_to_apply", lang).format(len(results)),
            batch_progress_ui.BatchProgressPhase.COMPLETED,
        )
        logger.info(f'[BATCH] Audio generation ready to apply: {len(results)} note results')
        return results

    def apply_generated_batch_audio_chunk(self, generated_results_chunk: List[Tuple], batch: config_models.BatchConfig, batch_status: Any, anki_collection: Any, added_media_files: Optional[set] = None) -> int:
        """
        Apply ONE chunk of generated audio results to Anki media and notes.

        This is the chunked counterpart of apply_generated_batch_audio().
        It does the same per-note work (media file copy + field write) and
        the same single collection.update_notes() call, but only for the
        notes passed in generated_results_chunk — NOT the whole batch.

        Important: unlike apply_generated_batch_audio(), this method does
        NOT reset batch_status.total_unique_tasks or
        batch_status.unique_tasks_completed to 0. The caller is responsible
        for setting batch_status.total_unique_tasks ONCE, before applying
        the first chunk, so progress accumulates correctly across chunks.

        Returns the number of notes actually written in this chunk.
        """
        if added_media_files is None:
            added_media_files = set()
        notes_to_update = []
        for (note_id, source_text, processed_text, sound_file, full_filename, is_error) in generated_results_chunk:
            if not batch_status.must_continue:
                break

            with batch_status.get_note_action_context(note_id, False) as note_action_context:
                try:
                    if is_error:
                        note_action_context.set_error(is_error)
                    else:
                        note = self.anki_utils.get_note_by_id(note_id)
                        self.hypertts._update_note_with_audio(note, batch, source_text, sound_file, full_filename, anki_collection, update_collection=False, added_media_files=added_media_files)
                        notes_to_update.append(note)
                        note_action_context.set_source_text(source_text)
                        note_action_context.set_processed_text(processed_text)
                        note_action_context.set_sound(sound_file)
                        note_action_context.set_status(constants.BatchNoteStatus.Done)
                        self._record_note_updated(batch_status)
                except Exception as e:
                    logger.error(f"Error updating note {note_id}: {e}")
                    note_action_context.set_error(e)

            batch_status.unique_tasks_completed += 1
            batch_status.notify_change(note_id)

        # Cancelling stops FUTURE notes.  Notes already processed are saved so
        # the "Done" rows shown in the progress table match the collection.
        if notes_to_update:
            anki_collection.update_notes(notes_to_update)

        return len(notes_to_update)

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
        added_media_files = set()
        for idx, (note_id, source_text, processed_text, sound_file, full_filename, is_error) in enumerate(generated_results):
            if not batch_status.must_continue:
                break

            with batch_status.get_note_action_context(note_id, False) as note_action_context:
                try:
                    if is_error:
                        note_action_context.set_error(is_error)
                    else:
                        note = self.anki_utils.get_note_by_id(note_id)
                        self.hypertts._update_note_with_audio(note, batch, source_text, sound_file, full_filename, anki_collection, update_collection=False, added_media_files=added_media_files)
                        notes_to_update.append(note)
                        note_action_context.set_source_text(source_text)
                        note_action_context.set_processed_text(processed_text)
                        note_action_context.set_sound(sound_file)
                        note_action_context.set_status(constants.BatchNoteStatus.Done)
                        self._record_note_updated(batch_status)
                except Exception as e:
                    logger.error(f"Error updating note {note_id}: {e}")
                    note_action_context.set_error(e)

            batch_status.unique_tasks_completed = idx + 1
            batch_status.notify_change(note_id)

        # Same rule as the chunked apply: a cancel must not throw away notes
        # that were already processed and reported as Done.
        if notes_to_update:
            logger.info(f'[BATCH] Saving {len(notes_to_update)} notes in single transaction...')
            anki_collection.update_notes(notes_to_update)
            logger.info('[BATCH] Notes saved successfully')

        batch_status.total_unique_tasks = 0
        batch_status.unique_tasks_completed = 0
        batch_status.set_status_message(None)
        logger.info(f'[BATCH] Applied generated audio in {time.time() - update_start:.2f}s')

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

    def _execute_unique_tasks_unified(self, tasks: List[Dict], dedup_map: Dict, batch_status: Any, checkpoint: Any = None) -> Dict[Any, Tuple]:
        # Preview generation has no apply phase, so no checkpoint is needed.
        checkpoint = checkpoint or batch_executor.NullCheckpoint()
        lang = self.hypertts.get_ui_language()
        audio_cache = {}
        completed_count = 0
        unique_count = len(dedup_map)
        engine_groups = {}
        cache_hit_count = 0

        for dedup_key, task_indices in dedup_map.items():
            if not batch_status.must_continue:
                break

            task_idx = task_indices[0]
            task_data = tasks[task_idx]
            chosen_voice = task_data.get('chosen_voice')

            # Resolve disk-cache hits before grouping.  Submitting cached work
            # to an engine executor used to waste a pool slot, a process round
            # trip and a batch slot on audio that already exists.
            if isinstance(dedup_key, audio_file_store.AudioRequestKey) and chosen_voice is not None:
                cached_file = self.audio_store.get_cached_file(dedup_key)
                if cached_file is not None:
                    source_text = task_data['source_text']
                    processed_text = task_data['processed_text']
                    audio_cache[dedup_key] = (
                        (source_text, processed_text, cached_file.audio_filename, cached_file.full_filename),
                        None,
                    )
                    completed_count += 1
                    cache_hit_count += 1
                    batch_status.unique_tasks_completed = completed_count

                    generated_ids = []
                    for cached_idx in task_indices:
                        note_id = tasks[cached_idx]['note_id']
                        with batch_status.get_note_action_context(note_id, False) as ctx:
                            ctx.set_source_text(source_text)
                            ctx.set_processed_text(processed_text)
                            ctx.set_sound(cached_file.audio_filename)
                            ctx.set_status(constants.BatchNoteStatus.Generated)
                        generated_ids.append(note_id)
                        batch_status.notify_change(note_id)

                    checkpoint.mark_generated(generated_ids)
                    try:
                        audio_request_context = task_data.get('audio_request_context')
                        if audio_request_context is not None and audio_request_context.audio_request_reason != constants.AudioRequestReason.preview:
                            service_name = getattr(chosen_voice.voice_id, 'service', 'unknown')
                            self.hypertts.usage_tracker.record_cache_hit(
                                audio_request_context, service_name, len(processed_text)
                            )
                    except Exception as usage_error:
                        logger.debug(f"[USAGE] cache hit record failed: {usage_error}")
                    continue

            service_name = self.executor.detect_service(task_data)

            group_key = service_name
            if group_key not in engine_groups:
                engine_groups[group_key] = []
            engine_groups[group_key].append((dedup_key, task_data, task_indices))

        if cache_hit_count:
            checkpoint.flush()
            batch_status.set_status_message(
                i18n.get_text("status_generating_audio_progress", lang).format(completed_count, unique_count)
            )
            logger.info(f"[BATCH] {cache_hit_count} unique task(s) served from disk cache")

        all_chunks = self._build_all_chunks(engine_groups)

        future_to_chunk = {}
        future_lock = threading.Lock()
        submit_error = [None]
        last_heartbeat_time = 0
        heartbeat_interval_seconds = 2.0
        submit_threads = []
        chunks_by_service = {}
        for service_name, chunk_items in all_chunks:
            chunks_by_service.setdefault(service_name, []).append(chunk_items)

        def _submit_service_chunks(service_name: str, chunk_items_list: List[List[Tuple]]) -> None:
            try:
                for chunk_items in chunk_items_list:
                    if not batch_status.must_continue:
                        break
                    try:
                        self.hypertts.orchestrator.apply_deferred_engine_pools()
                    except Exception as e:
                        logger.debug(f'[BATCH] Deferred pool refresh skipped: {e}')
                    executor_pool = self.executor.get_executor(service_name)
                    while batch_status.must_continue:
                        try:
                            submit_kwargs = {}
                            if isinstance(executor_pool, batch_executor.BoundedThreadPoolExecutor):
                                submit_kwargs['timeout'] = 0.1
                            try:
                                future = executor_pool.submit(
                                    self.hypertts._generate_audio_batch_task,
                                    list(chunk_items),
                                    **submit_kwargs,
                                )
                            except RuntimeError as exc:
                                # A concurrent refresh may have shut down the
                                # pool this thread captured.  Retry once on the
                                # freshly rebuilt executor instead of failing
                                # the whole submit.
                                if 'cannot schedule new futures after shutdown' not in str(exc).lower():
                                    raise
                                try:
                                    self.hypertts.orchestrator.refresh_engine_pools_for_current_ram()
                                except Exception as e:
                                    logger.warning(f'[BATCH] Pool refresh failed during submit retry: {e}')
                                # If the pool is still shut down (refresh was
                                # deferred or did not rebuild), force a new
                                # executor before retrying.
                                try:
                                    current_executor = getattr(self.hypertts.orchestrator, 'executor', None)
                                    if getattr(current_executor, '_shutdown', False):
                                        rebuilt = batch_executor.get_multi_engine_executor(
                                            engine_config=getattr(current_executor, 'engine_config', None) or {}
                                        )
                                        self.hypertts.orchestrator.executor = rebuilt
                                        self.hypertts.executor = rebuilt
                                except Exception as e:
                                    logger.warning(f'[BATCH] Forced executor rebuild failed: {e}')
                                try:
                                    self.hypertts.orchestrator.apply_deferred_engine_pools()
                                except Exception as e:
                                    logger.debug(f'[BATCH] Deferred pool refresh skipped: {e}')
                                executor_pool = self.executor.get_executor(service_name)
                                submit_kwargs = {}
                                if isinstance(executor_pool, batch_executor.BoundedThreadPoolExecutor):
                                    submit_kwargs['timeout'] = 0.1
                                future = executor_pool.submit(
                                    self.hypertts._generate_audio_batch_task,
                                    list(chunk_items),
                                    **submit_kwargs,
                                )
                            with future_lock:
                                future_to_chunk[future] = list(chunk_items)
                            batch_status.register_future(future)
                            break
                        except TimeoutError:
                            time.sleep(0.05)
                        except Exception as e:
                            logger.error(f"[BATCH] Submit error for {service_name}: {e}")
                            submit_error[0] = e
                            break
                    if not batch_status.must_continue:
                        break
            except Exception as e:
                logger.error(f"[BATCH] Submit thread error for {service_name}: {e}")
                submit_error[0] = e

        for service_name, chunk_items_list in chunks_by_service.items():
            thread = threading.Thread(target=_submit_service_chunks, args=(service_name, chunk_items_list), daemon=True)
            thread.start()
            submit_threads.append(thread)
        stall_timeout_seconds = float(batch_constants.BATCH_STALL_TIMEOUT_SECONDS)
        last_progress_time = time.time()

        while any(thread.is_alive() for thread in submit_threads) or future_to_chunk:
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
                        batch_status.unregister_future(future)
            
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
                    completed_count = self._handle_stall(
                        future_to_chunk, future_lock, tasks, audio_cache,
                        checkpoint, batch_status, lang, completed_count,
                    )

                time.sleep(0.05)
                continue
            
            for future, chunk in done_futures:
                try:
                    # The future is already known to be done here, so result()
                    # cannot block. Do not add an arbitrary timeout: a large
                    # first batch (Kokoro/MMS model load) can legitimately take
                    # longer than 25 seconds before returning its result.
                    batch_results = future.result()
                    completed_count = self._apply_chunk_results(
                        chunk, batch_results, tasks, audio_cache,
                        checkpoint, batch_status, lang, completed_count,
                    )
                    
                    batch_status.set_status_message(i18n.get_text("status_generating_audio_progress", lang).format(completed_count, unique_count))
                    self.executor.monitor.maybe_gc(completed_count)
                    del batch_results
                    last_progress_time = time.time()
                except Exception as e:
                    logger.error(f"[BATCH] Batch execution failed: {e}")
                    completed_count = self._fail_chunk(
                        chunk, e, tasks, audio_cache, batch_status, completed_count,
                    )
                    self.executor.monitor.maybe_gc(completed_count)
        
        for thread in submit_threads:
            thread.join(timeout=5.0)
        if submit_error[0]:
            logger.error(f"[BATCH] Submit thread encountered an error: {submit_error[0]}")

        if batch_status.must_continue:
            # A submit/worker error is a real failure: surface it and record it.
            self._fill_missing_results(tasks, dedup_map, audio_cache, batch_status, checkpoint)
        else:
            # A user cancel is not a failure.  Leave the remaining notes
            # untouched: no red rows, no error records in the checkpoint (a
            # resume retries every note that is not applied anyway).
            logger.info('[BATCH] Batch cancelled; leaving unprocessed notes untouched')

        checkpoint.flush()
        return audio_cache

    def _fill_missing_results(self, tasks: List[Dict], dedup_map: Dict, audio_cache: Dict, batch_status: Any, checkpoint: Any) -> int:
        """Mark notes whose audio never arrived as failed.

        Only used when the run ended on its own (submit thread error, worker
        exception).  A user cancel deliberately skips this so cancelled notes
        are not reported or checkpointed as errors.
        """
        filled = 0
        lang = self.hypertts.get_ui_language()
        for dedup_key, task_indices in dedup_map.items():
            if dedup_key in audio_cache:
                continue
            missing_error = Exception(i18n.get_text("error_audio_gen_failed", lang))
            audio_cache[dedup_key] = (None, missing_error)
            filled += 1
            for task_idx in task_indices:
                note_id = tasks[task_idx]['note_id']
                with batch_status.get_note_action_context(note_id, False) as ctx:
                    ctx.set_error(missing_error)
                checkpoint.mark_error(note_id, missing_error)
                batch_status.notify_change(note_id)
        return filled

    def _build_all_chunks(self, engine_groups: Dict) -> List[Tuple[str, List[Tuple]]]:
        """Split each engine's tasks into payload-sized chunks.

        Chunking is about what one engine call receives, so the limit is based
        on the *processed* text length, not the raw source text.
        """
        batch_size_by_engine = {
            'EdgeTTS': 3,
            'PiperTTS': 5,
            'KokoroTTS': 5,
            'MmsTTS': 5,
            'Piper': 5,
            'Kokoro': 5,
            'MMS': 5,
            'SupertonicTTS': 5,
            'Supertonic': 5,
        }
        default_batch_size = 1
        all_chunks = []
        for service_name, group_tasks in engine_groups.items():
            max_batch = batch_size_by_engine.get(service_name, default_batch_size)
            chunk = []
            chunk_chars = 0
            for item in group_tasks:
                _, task_data, _ = item
                text_len = len(task_data['processed_text'])

                if len(chunk) >= max_batch or (chunk_chars + text_len > 3000 and chunk):
                    all_chunks.append((service_name, list(chunk)))
                    chunk = []
                    chunk_chars = 0

                chunk.append(item)
                chunk_chars += text_len

            if chunk:
                all_chunks.append((service_name, list(chunk)))
        return all_chunks

    def _apply_chunk_results(self, chunk: List[Tuple], batch_results: List[Tuple], tasks: List[Dict], audio_cache: Dict, checkpoint: Any, batch_status: Any, lang: str, completed_count: int) -> int:
        """Store one finished chunk and update every note that used it."""
        generated_ids = []

        for i, (dedup_key, _, task_indices) in enumerate(chunk):
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
                        src, proc, audio_fn, _ = result
                        ctx.set_source_text(src)
                        ctx.set_processed_text(proc)
                        ctx.set_sound(audio_fn)
                        ctx.set_status(constants.BatchNoteStatus.Generated)
                        generated_ids.append(note_id)
                    else:
                        failure = error if error else Exception(i18n.get_text("error_audio_gen_failed", lang))
                        ctx.set_error(failure)
                        checkpoint.mark_error(note_id, failure)
                batch_status.notify_change(note_id)

        # Checkpoint after every completed chunk (flushed on cadence)
        checkpoint.mark_generated(generated_ids)
        return completed_count

    def _fail_chunk(self, chunk: List[Tuple], error: Exception, tasks: List[Dict], audio_cache: Dict, batch_status: Any, completed_count: int) -> int:
        """Mark every note in a chunk as failed after an unexpected error."""
        for dedup_key, _, task_indices in chunk:
            audio_cache[dedup_key] = (None, error)
            completed_count += 1
            for task_idx in task_indices:
                note_id = tasks[task_idx]['note_id']
                with batch_status.get_note_action_context(note_id, False) as ctx:
                    ctx.set_error(error)
                batch_status.notify_change(note_id)
        return completed_count

    def _handle_stall(self, future_to_chunk: Dict, future_lock: Any, tasks: List[Dict], audio_cache: Dict, checkpoint: Any, batch_status: Any, lang: str, completed_count: int) -> int:
        """Cancel pending futures after the stall timeout and mark their notes.

        The batch keeps running afterwards: another engine may still have
        healthy futures in flight.
        """
        stalled_text = i18n.get_text("error_batch_stalled", lang) or "Batch generation stalled"
        with future_lock:
            pending = list(future_to_chunk.items())
            future_to_chunk.clear()
            for pending_future, chunk in pending:
                try:
                    pending_future.cancel()
                except Exception as e:
                    logger.error(f"Failed to cancel pending future during stall: {e}")
                for dedup_key, _, task_indices in chunk:
                    stall_error = Exception(stalled_text)
                    audio_cache[dedup_key] = (None, stall_error)
                    completed_count += 1
                    batch_status.unique_tasks_completed = completed_count
                    for task_idx in task_indices:
                        note_id = tasks[task_idx]['note_id']
                        with batch_status.get_note_action_context(note_id, False) as ctx:
                            ctx.set_error(stall_error)
                        checkpoint.mark_error(note_id, stall_error)
                        batch_status.notify_change(note_id)

        checkpoint.flush()
        batch_status.set_status_message(i18n.get_text("status_batch_stalled", lang) or None)
        return completed_count

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
        field_maps = self.anki_utils.get_note_field_maps(note_id_list)
        TERMINAL = (constants.BatchNoteStatus.Generated, constants.BatchNoteStatus.Done, constants.BatchNoteStatus.Error)
        for note_id in note_id_list:
            existing = batch_status.note_status_map.get(note_id)
            if existing is not None and existing.status in TERMINAL:
                continue
            with batch_status.get_note_action_context(note_id, True) as note_action_context:
                if note_id not in field_maps:
                    note_action_context.set_error(errors.NoteNotFoundError(note_id))
                else:
                    note_fields = field_maps[note_id]
                    source_text, processed_text = self.get_source_processed_text(note_fields, batch_source, text_processing)
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
