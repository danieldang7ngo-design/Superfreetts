
# python imports
import os
import sys
import re
import hashlib
import random
import copy
import json
import datetime
import time
import concurrent.futures
from typing import List, Dict, Tuple, Optional, Any
import pprint

# anki imports
import aqt
import aqt.progress
import aqt.addcards
import anki.notes
import anki.cards
import aqt.operations
import aqt.qt

from . import constants
from . import options
from . import voice as voice_module
from . import errors
from . import text_utils
from . import config_models
from . import context
from . import batch_executor
from . import logging_utils
from . import gui
from . import preset_rules_status
from . import i18n
from . import batch_constants
from . import performance_tracker
from . import cpu_utils
logger = logging_utils.get_child_logger(__name__)


class SuperFreeTTS():
    """
    should have awareness of:
    - anki concepts such as notes, editor
    - understand how user has configured their presets
    should not have awareness of:
    - services (route through servicemanager)
    """

    def __init__(self, anki_utils: Any, service_manager: Any) -> None:
        """Initialize SuperFreeTTS with Anki utilities and service manager."""
        self.anki_utils = anki_utils
        self.service_manager = service_manager
        self.error_manager = errors.ErrorManager(self.anki_utils)
        self.config = self.anki_utils.get_config()
        self.latest_saved_batch_name: Optional[str] = None
        self.text_processing_cache = {}  # Simple dict for processed text caching
        
        # Initialize multi-engine executor with settings from service configurations
        try:
            config = self.anki_utils.get_config()
            service_config_map = config.get('service_config', {})
            prefs = self.get_preferences()  # For backward compatibility fallback
            
            # Apply logging preferences based on stored debug mode
            self.apply_logging_preferences()
            
            # Default concurrency workers for each service
            defaults = {
                'PiperTTS': 1,
                'KokoroTTS': 1,
                'EdgeTTS': 1,
                'MmsTTS': 1,
            }
            
            # Fallback to preferences if available (backward compatibility)
            pref_fallback = {
                'PiperTTS': getattr(prefs, 'piper_workers', 1),
                'KokoroTTS': getattr(prefs, 'kokoro_workers', 1),
                'EdgeTTS': getattr(prefs, 'edgetts_workers', 1),
                'MmsTTS': getattr(prefs, 'mms_workers', 1),
            }
            
            # Service name mappings for executor pool naming
            service_pool_map = {
                'PiperTTS': 'Piper',
                'KokoroTTS': 'Kokoro',
                'EdgeTTS': 'EdgeTTS',
                'MmsTTS': 'MMS',
            }
            
            # Build engine config from service configurations
            engine_config = {}
            for service_name, pool_name in service_pool_map.items():
                service_config = service_config_map.get(service_name, {})
                # Try service config first, then prefer fallback (for backward compat), then default
                concurrency = service_config.get('concurrency_workers') or pref_fallback.get(service_name) or defaults.get(service_name, 1)
                
                # Validate against physical CPU cores
                max_workers = cpu_utils.CPUInfo.get_max_workers()
                if concurrency > max_workers:
                    logger.warning(f'Service {service_name} concurrency_workers ({concurrency}) exceeds physical CPU cores ({max_workers}), capping to {max_workers}')
                    concurrency = max_workers
                engine_config[pool_name] = max(1, concurrency)
            
            self.executor = batch_executor.get_multi_engine_executor(engine_config=engine_config)
            logger.info(f'[INIT] Multi-engine executor configured with CPU-validated settings: {engine_config}')
        except Exception as e:
            logger.warning(f'[INIT] Failed to initialize multi-engine executor, falling back to unified: {e}')
            self.executor = batch_executor.get_batch_executor(max_workers=1)

        # do maintenance        # migration
        self.perform_config_migration()
        # register added audio
        self.config_register_added_audio()
        
        # Cleanup cache
        self.cleanup_user_files()

    def cleanup_user_files(self) -> None:
        """
        Delete files in user_files older than cache_retention_days.

        Notes:
        - Runs quickly and defensively on the main thread.
        - Only touches the addon's own user_files directory.
        - Uses os.scandir for better performance on large directories.
        """
        try:
            prefs = self.get_preferences()
            if not prefs.cache_enabled:
                return

            retention_days = max(0, prefs.cache_retention_days)
            if retention_days == 0:
                return

            cutoff_time = datetime.datetime.now().timestamp() - (retention_days * 86400)

            user_files_dir = os.path.join(self.anki_utils.get_addon_dir(), 'user_files')
            if not os.path.isdir(user_files_dir):
                return

            logger.info(f'{batch_constants.INFO_CACHE_CLEANUP_STARTED} Retention: {retention_days} days.')
            deleted = 0
            scanned = 0

            # Use scandir for better performance and to avoid extra stat calls
            with os.scandir(user_files_dir) as it:
                for entry in it:
                    if not entry.is_file():
                        continue
                    scanned += 1
                    try:
                        file_mtime = entry.stat().st_mtime
                        if file_mtime < cutoff_time:
                            os.remove(entry.path)
                            deleted += 1
                    except OSError as e:
                        logger.warning(f'{batch_constants.WARNING_CACHE_DELETE_ERROR} {entry.path}: {e}')

            logger.info(f'{batch_constants.INFO_CACHE_CLEANUP_FINISHED} Scanned {scanned} files, deleted {deleted} old files.')
        except Exception as e:
            logger.error(f'{batch_constants.ERROR_CACHE_CLEANUP_EXCEPTION}: {e}')

    def _set_batch_status_with_ui_refresh(self, batch_status, message):
        """Set batch status message and allow UI to refresh by processing Qt events."""
        batch_status.set_status_message(message)
        # Process Qt events to allow UI to update with the status message
        try:
            aqt.qt.QApplication.instance().processEvents()
        except Exception as e:
            logger.debug(f'Error processing Qt events: {e}')

    def process_batch_audio(self, note_id_list, batch: config_models.BatchConfig, batch_status, anki_collection):
        import time
        start_time = time.time()

        tasks = []
        audio_request_context = context.AudioRequestContext(constants.AudioRequestReason.batch)

        # Initialize executor (already created in __init__, just get reference)
        logger.info(f'[BATCH] Using multi-engine batch executor')

        # Simple checkpoint management
        batch_name = batch.name or f"batch_{int(time.time())}"
        original_note_id_list = note_id_list[:]  # Keep original for checkpoint save
        checkpoint_data = self.executor.checkpoint.load(batch_name)
        checkpoint = None
        checkpoint_enabled = True
        
        # Check for resumable batch
        if checkpoint_data and checkpoint_data.get('completed_indices'):
            completed = checkpoint_data.get('completed_indices', [])
            
            # Filter to only pending notes
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
            # First time: initialize checkpoint dict
            checkpoint = {
                'batch_name': batch_name,
                'completed_indices': [],
                'note_id_list': original_note_id_list,
                'errors': {}
            }

        
        # Use batch_running_action_context to properly signal UI start/end
        # This calls notify_start() on enter (triggers show_running_stack + progress bar)
        # and notify_end() on exit (triggers show_completed_stack or show_not_running_stack)
        with batch_status.get_batch_running_action_context():
            try:
                # 0. Pre-load voice list
                lang = self.get_ui_language()
                self._set_batch_status_with_ui_refresh(batch_status, i18n.get_text("status_loading_voices", lang))
                logger.info(f'[BATCH] Pre-loading voice list for faster audio generation...')
                pre_load_start = time.time()
                try:
                    _ = self.service_manager.full_voice_list()
                    pre_load_time = time.time() - pre_load_start
                    logger.info(f'[BATCH] Voice list pre-loaded in {pre_load_time:.2f}s')
                except Exception as e:
                    logger.warning(f'[BATCH] Voice list pre-load failed: {e}')

                # 1. Prepare requests
                self._set_batch_status_with_ui_refresh(batch_status, i18n.get_text("status_preparing_notes", lang).format(len(note_id_list)))
                logger.info(f'[BATCH] Starting to prepare {len(note_id_list)} notes...')
                extract_start = time.time()

                for idx, note_id in enumerate(note_id_list):
                    if not batch_status.must_continue: break

                    note = self.anki_utils.get_note_by_id(note_id)
                    try:
                        source_text = self.get_source_text(note, batch.source, None)
                        
                        # Simple text cache for processing efficiency
                        cache_key = f"{source_text}_{id(batch.text_processing)}"
                        if cache_key not in self.text_processing_cache:
                            processed_text = self.process_text(source_text, batch.text_processing)
                            self.text_processing_cache[cache_key] = processed_text
                        else:
                            processed_text = self.text_processing_cache[cache_key]
                            logger.debug(f"[BATCH] Text cache hit")
                        
                        # Priority mode voice list state
                        priority_voice_list = None
                        if batch.voice_selection.selection_mode == constants.VoiceSelectionMode.priority:
                            # We should initialize this outside the loop if we want it to persist,
                            # but priority mode with unified batch executor is tricky since we group tasks.
                            # Best effort: use the original list every time, or we can't fall back easily.
                            # For now, let's just let it act like single/random if priority.
                            priority_voice_list = copy.copy(batch.voice_selection.voice_list)

                        chosen_voice = self.choose_voice(batch.voice_selection, priority_voice_list)

                        # Create simple task dict (no MemoryPool)
                        task = {
                            'note_id': note_id,
                            'source_text': source_text,
                            'processed_text': processed_text,
                            'batch': batch,
                            'audio_request_context': audio_request_context,
                            'chosen_voice': chosen_voice
                        }
                        tasks.append(task)
                    except Exception as e:
                        with batch_status.get_note_action_context(note_id, False) as note_action_context:
                            note_action_context.set_error(e)

                extract_time = time.time() - extract_start
                logger.info(f'[BATCH] Prepared {len(tasks)} notes in {extract_time:.2f}s')

                if not batch_status.must_continue: return

                # 2. Deduplication
                self._set_batch_status_with_ui_refresh(batch_status, i18n.get_text("status_analyzing_duplicates", lang))
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

                # 3. Parallel Generation with unified executor
                prefs = self.get_preferences()
                max_workers = max(1, min(prefs.batch_concurrency, cpu_utils.CPUInfo.get_max_workers()))
                logger.info(f"[BATCH] Parallel generation requested: {max_workers} workers (engine pools may override)")

                batch_status.total_unique_tasks = unique_count
                batch_status.unique_tasks_completed = 0

                self._set_batch_status_with_ui_refresh(batch_status, i18n.get_text("status_generating_audio", lang).format(unique_count))
                logger.info(f"[BATCH] Starting audio generation with {max_workers} workers ({unique_count} unique combinations)")
                gen_start = time.time()

                audio_cache = self._execute_unique_tasks_unified(tasks, dedup_map, batch_status, max_workers)

                gen_time = time.time() - gen_start
                logger.info(f'[BATCH] Generated {len(audio_cache)} audio files in {gen_time:.2f}s')

                batch_status.futures_to_cancel.clear()

                # 4. Apply cached results to all notes
                batch_status.total_unique_tasks = 0
                batch_status.unique_tasks_completed = 0
                
                self._set_batch_status_with_ui_refresh(batch_status, i18n.get_text("status_applying_notes", lang).format(len(tasks)))

                logger.info(f'[BATCH] Applying audio to {len(tasks)} notes...')
                apply_start = time.time()
                results = self._apply_batch_deduplication(tasks, dedup_map, audio_cache, batch_status)
                apply_time = time.time() - apply_start
                logger.info(f'[BATCH] Applied results in {apply_time:.2f}s')

                # Release large intermediate data structures to free memory
                audio_cache.clear()
                del audio_cache
                dedup_map.clear()
                del dedup_map
                tasks.clear()
                del tasks

                # 5. Update Notes
                self._set_batch_status_with_ui_refresh(batch_status, i18n.get_text("status_saving_collection", lang))
                logger.info(f'[BATCH] Updating Anki collection with {len(results)} note changes...')
                update_start = time.time()

                for idx, (note_id, source_text, processed_text, sound_file, full_filename, is_error) in enumerate(results):
                    if not batch_status.must_continue:
                        break

                    note_status = batch_status.note_status_map.get(note_id)
                    already_done = note_status and note_status.status == constants.BatchNoteStatus.Done

                    with batch_status.get_note_action_context(note_id, False) as note_action_context:
                        try:
                            if is_error:
                                # is_error now contains the actual exception object from the task
                                note_action_context.set_error(is_error)
                                if checkpoint:
                                    checkpoint['errors'][str(idx)] = str(is_error)
                            else:
                                note = self.anki_utils.get_note_by_id(note_id)
                                self._update_note_with_audio(note, batch, source_text, sound_file, full_filename, anki_collection)

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
                    
                    if checkpoint and checkpoint_enabled:
                        try:
                            completed_list = checkpoint.get('completed_indices', [])
                            if idx not in completed_list:
                                completed_list.append(idx)
                            self.executor.checkpoint.save(batch_name, completed_list, checkpoint.get('note_id_list', []), checkpoint.get('errors', {}))
                        except Exception as e:
                            logger.warning(f'[BATCH] Failed to save checkpoint: {e}')
                            checkpoint_enabled = False

                update_time = time.time() - update_start
                total_time = time.time() - start_time
                logger.info(f'[BATCH] Completed in {total_time:.2f}s')

                # Release large data structures
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
                # Simple cleanup
                batch_status.futures_to_cancel.clear()
                self.text_processing_cache.clear()
                logger.info(f'[BATCH] Cleanup complete')


    def _collect_batch_duplicates(self, tasks: List[Dict[str, Any]]) -> Dict[Tuple, List[int]]:
        """
        Analyze tasks to identify duplicate (processed_text, voice_id) combinations.
        Optimized: O(n) time complexity with direct tuple keys, no redundant hashing.
        
        Args:
            tasks: List of task dictionaries containing note data and configuration
            
        Returns:
            Deduplication map: {(processed_text, voice_id): [task_indices]}
        """
        dedup_map = {}

        if not tasks:
            return dedup_map

        # For all modes, voice is determined per task explicitly using 'chosen_voice'
        for task_idx, task_data in enumerate(tasks):
            processed_text = task_data['processed_text']
            voice_with_options = task_data.get('chosen_voice')
            voice_id = voice_with_options.voice_id if voice_with_options else None

            if voice_id is None:
                dedup_key = (f'no_voice_{task_idx}',)
            else:
                # Direct tuple key - simple and efficient
                dedup_key = (processed_text, voice_id)

            if dedup_key not in dedup_map:
                dedup_map[dedup_key] = []
            dedup_map[dedup_key].append(task_idx)

        return dedup_map

    def _execute_unique_tasks_unified(self, tasks, dedup_map, batch_status, max_workers=4):
        """
        Execute unique tasks using MultiEngineExecutor with DYNAMIC BATCHING.
        Groups tasks by (service, voice) and chunks them into vector IPC calls.
        """
        lang = self.get_ui_language()
        audio_cache = {}
        completed_count = 0
        unique_count = len(dedup_map)
        
        # 1. Group tasks by (service, voice_id) for batching compatibility
        engine_groups = {} # (service_name, voice_id) -> list of (dedup_key, task_data, task_indices)
        
        for dedup_key, task_indices in dedup_map.items():
            task_idx = task_indices[0]
            task_data = tasks[task_idx]
            service_name = self.executor.detect_service(task_data)
            
            # Extract voice_id safely
            chosen_voice = task_data.get('chosen_voice')
            # Voice ID can be complex, stringify for dictionary key
            voice_id_str = str(chosen_voice.voice_id) if chosen_voice else "None"
            
            group_key = (service_name, voice_id_str)
            if group_key not in engine_groups:
                engine_groups[group_key] = []
            engine_groups[group_key].append((dedup_key, task_data, task_indices))
            
        # 2. Chunk groups into batches and submit to per-engine executors
        # Enforce strict 10-item (MAX_BATCH_SIZE) and 3000-character (MAX_TOTAL_CHARS) limits
        future_to_chunk = {} # future -> chunk of (dedup_key, task_data, task_indices)
        
        for (service_name, _), group_tasks in engine_groups.items():
            executor_pool = self.executor.get_executor(service_name)
            
            chunk = []
            chunk_chars = 0
            for item in group_tasks:
                dedup_key, task_data, task_indices = item
                # Bound character count based on input text
                text = task_data['source_text']
                text_len = len(text)
                
                # Check bounds
                if len(chunk) >= 10 or (chunk_chars + text_len > 3000 and chunk):
                    # Dispatch current chunk to engine
                    future = executor_pool.submit(self._generate_audio_batch_task, list(chunk))
                    future_to_chunk[future] = list(chunk)
                    chunk = []
                    chunk_chars = 0
                
                chunk.append(item)
                chunk_chars += text_len
            
            if chunk:
                future = executor_pool.submit(self._generate_audio_batch_task, list(chunk))
                future_to_chunk[future] = list(chunk)
        
        # 3. Collect results as batches complete
        for future in concurrent.futures.as_completed(future_to_chunk):
            if not batch_status.must_continue:
                for pending_future in future_to_chunk:
                    if not pending_future.done(): pending_future.cancel()
                break
                
            chunk = future_to_chunk[future]
            try:
                # Enforce strict 25s timeout per batch as mandated
                batch_results = future.result(timeout=25.0) 
                
                for i, (dedup_key, task_data, task_indices) in enumerate(chunk):
                    result_tuple = batch_results[i] if i < len(batch_results) else (None, Exception("Internal error"))
                    audio_cache[dedup_key] = result_tuple
                    result, error = result_tuple
                    
                    # Mark progress
                    completed_count += 1
                    batch_status.unique_tasks_completed = completed_count
                    
                    # Update progress for all notes using this combination
                    is_successful = result is not None
                    for task_idx in task_indices:
                        note_id = tasks[task_idx]['note_id']
                        with batch_status.get_note_action_context(note_id, False) as ctx:
                            if is_successful:
                                src, proc, audio_fn, full_fn = result
                                ctx.set_source_text(src)
                                ctx.set_processed_text(proc)
                                ctx.set_sound(audio_fn)
                                ctx.set_status(constants.BatchNoteStatus.Done)
                            else:
                                ctx.set_error(error if error else Exception(i18n.get_text("error_audio_gen_failed", lang)))
                        batch_status.notify_change(note_id)
                
                batch_status.set_status_message(f"Generating... ({completed_count}/{unique_count})")
                
            except Exception as e:
                logger.error(f"[BATCH] Batch execution failed: {e}")
                # Mark all items in this chunk as failed
                for dedup_key, _, task_indices in chunk:
                    audio_cache[dedup_key] = (None, e)
                    completed_count += 1
                    for task_idx in task_indices:
                        note_id = tasks[task_idx]['note_id']
                        with batch_status.get_note_action_context(note_id, False) as ctx:
                            ctx.set_error(e)
                        batch_status.notify_change(note_id)

        return audio_cache

    def _apply_batch_deduplication(self, tasks, dedup_map, audio_cache, batch_status):
        """
        Apply cached audio results to all task indices (including duplicates).
        Returns list of (note_id, source_text, processed_text, sound_file, full_filename) tuples.
        """
        results = []

        for dedup_key, task_indices in dedup_map.items():
            if dedup_key not in audio_cache:
                logger.warning(f'audio cache missing result for dedup_key')
                continue

            cached_result = audio_cache[dedup_key]
            res, err = cached_result
            if res is None:
                # This combination failed, skip all tasks using it
                for task_idx in task_indices:
                    note_id = tasks[task_idx]['note_id']
                    results.append((note_id, None, None, None, None, err))  # error object instead of boolean
                continue

            source_text, processed_text, sound_file, full_filename = res

            # Apply to all tasks using this combination
            for task_idx in task_indices:
                note_id = tasks[task_idx]['note_id']
                results.append((note_id, source_text, processed_text, sound_file, full_filename, None))  # None = no error

        return results

    def _generate_audio_batch_task(self, chunk):
        first_item = chunk[0][1]
        batch_cfg = first_item['batch']
        chosen_voice = first_item.get('chosen_voice')
        
        # 1. Prepare texts for batch
        source_texts = [item[1]['processed_text'] for item in chunk]
        
        # 2. Check individual items for existing cache files to avoid redundant calling
        results = [None] * len(chunk)
        missing_indices = []
        missing_texts = []
        
        voice_id = chosen_voice.voice_id if chosen_voice else None
        voice_options = chosen_voice.options if chosen_voice else {}
        
        for i, (dedup_key, task_data, _) in enumerate(chunk):
            proc_text = task_data['processed_text']
            
            hash_str = self.get_hash_for_audio_request(proc_text, voice_id, voice_options)
            format = options.AudioFormat.mp3
            if options.AUDIO_FORMAT_PARAMETER in voice_options:
                format = options.AudioFormat[voice_options[options.AUDIO_FORMAT_PARAMETER]]
            
            full_filename = self.get_full_audio_file_name(hash_str, format)
            audio_filename = self.get_audio_filename(hash_str, format)
            
            if os.path.exists(full_filename) and os.path.getsize(full_filename) > 0:
                results[i] = ((task_data['source_text'], proc_text, audio_filename, full_filename), None)
            else:
                missing_indices.append(i)
                missing_texts.append(proc_text)
        
        # 3. Call batch API for missing items
        if missing_texts:
            service_error = None
            try:
                # Locate actual voice object
                voice = self.service_manager.locate_voice(voice_id)
                audio_datas = self.service_manager.get_tts_audio_batch(missing_texts, voice, voice_options)
                
                for i, idx in enumerate(missing_indices):
                    audio_data = audio_datas[i] if i < len(audio_datas) else None
                    if audio_data:
                        task_data = chunk[idx][1]
                        proc_text = task_data['processed_text']
                        
                        # Re-calculate filename for writing
                        hash_str = self.get_hash_for_audio_request(proc_text, voice_id, voice_options)
                        format = options.AudioFormat.mp3
                        if options.AUDIO_FORMAT_PARAMETER in voice_options:
                             format = options.AudioFormat[voice_options[options.AUDIO_FORMAT_PARAMETER]]
                        
                        full_fn = self.get_full_audio_file_name(hash_str, format)
                        audio_fn = self.get_audio_filename(hash_str, format)
                        
                        with open(full_fn, 'wb') as f:
                            f.write(audio_data)
                        
                        # Cache in memory
                        self.executor.cache_result(proc_text, str(voice_id), task_data['source_text'], audio_fn, full_fn)
                        results[idx] = ((task_data['source_text'], proc_text, audio_fn, full_fn), None)
                    else:
                        results[idx] = (None, Exception(i18n.get_text("error_audio_gen_failed", self.get_ui_language())))
            except Exception as e:
                logger.error(f"[BATCH] Service batch call failed: {e}")
                service_error = e
            
            # If service call failed, mark all missing items with that error
            if service_error:
                for idx in missing_indices:
                    results[idx] = (None, service_error)
        
        # Ensure no None in results (fallback for any unhandled indices)
        for i in range(len(results)):
            if results[i] is None:
                results[i] = (None, Exception("Audio generation was skipped or interrupted"))
                
        return results

    def _update_note_with_audio(self, note, batch, source_text, sound_file, full_filename, anki_collection):
        # Helper to update the note object
        target_field = batch.target.target_field
        if target_field not in note:
            # Should have been caught earlier but check again
            return

        sound_tag, _ = self.get_collection_sound_tag(full_filename, sound_file)
        
        target_field_content = note[target_field]
        
        if batch.target.remove_sound_tag:
            target_field_content = text_utils.strip_sound_tag(target_field_content)
        
        if batch.target.text_and_sound_tag:
            target_field_content = f'{target_field_content} {sound_tag}'
        else:
            target_field_content = self.keep_only_sound_tags(target_field_content)
            target_field_content = f'{target_field_content} {sound_tag}'

        note[target_field] = target_field_content.strip()
        anki_collection.update_note(note)

    def process_note_audio(self, batch: config_models.BatchConfig, note, add_mode, audio_request_context, text_override, anki_collection):
        target_field = batch.target.target_field

        if target_field not in note:
            raise errors.TargetFieldNotFoundError(target_field)

        source_text = self.get_source_text(note, batch.source, text_override)
        processed_text = self.process_text(source_text, batch.text_processing)

        full_filename, audio_filename = self.get_audio_file(processed_text, batch.voice_selection, audio_request_context)
        sound_tag, sound_file = self.get_collection_sound_tag(full_filename, audio_filename)

        target_field_content = note[target_field]
        
        # do we need to remove existing sound tags ?
        if batch.target.remove_sound_tag == True:
            target_field_content = text_utils.strip_sound_tag(target_field_content)
        
        if batch.target.text_and_sound_tag == True:
            # user wants text and sound tag together, append the sound tag
            target_field_content = f'{target_field_content} {sound_tag}'
        else:
            # user only wants sound tags
            target_field_content = self.keep_only_sound_tags(target_field_content)
            target_field_content = f'{target_field_content} {sound_tag}'

        target_field_content = target_field_content.strip()

        logger.debug(f'setting note[{target_field}] to {target_field_content}')
        note[target_field] = target_field_content
        if not add_mode:
            anki_collection.update_note(note)

        return source_text, processed_text, sound_file, full_filename

    def get_note_audio(self, batch, note, audio_request_context, text_override):
        source_text = self.get_source_text(note, batch.source, text_override)
        processed_text = text_utils.process_text(source_text, batch.text_processing)
        if len(processed_text) == 0:
            raise errors.SourceTextEmpty()        
        return self.get_audio_file(processed_text, batch.voice_selection, audio_request_context)

    def get_realtime_audio(self, realtime_model: config_models.RealtimeConfigSide, text):
        source_text = text
        processed_text = text_utils.process_text(source_text, realtime_model.text_processing)
        if len(processed_text) == 0:
            raise errors.SourceTextEmpty()
        return self.get_audio_file(processed_text, realtime_model.voice_selection, context.AudioRequestContext(constants.AudioRequestReason.realtime))

    def get_audio_file(self, processed_text, voice_selection, audio_request_context):
        # sanity checks
        if voice_selection.selection_mode in [constants.VoiceSelectionMode.priority, constants.VoiceSelectionMode.random]:
            if len(voice_selection.voice_list) == 0:
                raise errors.NoVoicesAdded()

        # this voice_list copy is only used for priority mode
        voice_list = None
        priority_mode = voice_selection.selection_mode == constants.VoiceSelectionMode.priority
        if priority_mode:
            voice_list = copy.copy(voice_selection.voice_list)
        sound_found = False
        # loop while we haven't found the sound. this will be used for priority mode
        loop_condition = True
        while loop_condition:
            try:
                voice_with_options = self.choose_voice(voice_selection, voice_list)
                logger.debug(f'about to generate audio file and write to file for {processed_text}')
                voice_id = voice_with_options.voice_id
                assert isinstance(voice_id, voice_module.TtsVoiceId_v3), \
                    f"Expected voice_id to be TtsVoiceId_v3, got {type(voice_id).__name__}, voice_with_options: {type(voice_with_options).__name__}"

                full_filename, audio_filename = self.generate_audio_write_file(processed_text, 
                    voice_with_options.voice_id, voice_with_options.options, audio_request_context)
                logger.debug(f'finished generating audio file and write to file for {processed_text}')
                self.anki_utils.run_on_main(self.config_register_added_audio)
                return full_filename, audio_filename
            except errors.AudioNotFoundError as exc:
                # try the next voice, as long as one is available
                if not priority_mode:
                    # re-raise the exception
                    raise exc
            loop_condition = priority_mode and sound_found == False and len(voice_list) > 0
        raise errors.AudioNotFoundAnyVoiceError(processed_text)

    def choose_voice(self, voice_selection, voice_list) -> config_models.VoiceWithOptions:
        if voice_selection.selection_mode == constants.VoiceSelectionMode.single:
            return voice_selection.voice
        elif voice_selection.selection_mode == constants.VoiceSelectionMode.random:
            logger.info(f'choosing from {len(voice_selection.voice_list)} voices')
            choice = random.choices(voice_selection.voice_list, weights=[x.random_weight for x in voice_selection.voice_list])
            return choice[0]
        elif voice_selection.selection_mode == constants.VoiceSelectionMode.priority:
            # remove that voice from possible list
            voice = voice_list.pop(0)
            return voice

    def editor_note_add_audio(self, 
            batch: config_models.BatchConfig, 
            editor_context: config_models.EditorContext,
            text_input = None):
        # used by :
        #  - component_batch.py
        #  - component_mappingrule.py

        # adding audio after the cursor is not yet supported
        if batch.target.insert_location == config_models.InsertLocation.CURSOR_LOCATION:
            lang = self.get_ui_language()
            raise errors.SuperFreeTTSError(i18n.get_text("error_insert_cursor_unsupported", lang))

        logger.debug(f'editor_note_add_audio, editor_context: {editor_context}')
        logger.debug(f'editor_note_add_audio, batch: {repr(batch)}')
        # editor, note, add_mode, text_override
        # don't perform undo, it doesn't actually work, because of the way we call update_note
        audio_request_context = context.AudioRequestContext(constants.AudioRequestReason.editor_browser)
        if editor_context.add_mode:
            audio_request_context = context.AudioRequestContext(constants.AudioRequestReason.editor_add)
        text_override = None
        if text_input != None:
            # most likely coming from the Easy mode where the user directly inputs text
            text_override = text_input
        else:
            if batch.source.use_selection:
                if editor_context.selected_text != None:
                    text_override = editor_context.selected_text
        logger.debug(f'text_override: {text_override}')
        source_text, processed_text, sound_file, full_filename = self.process_note_audio(batch, editor_context.note, editor_context.add_mode,
            audio_request_context, text_override, self.anki_utils.get_anki_collection())
        logger.debug('after process_note_audio')
        logger.debug(f'about to call editor.set_note: {editor_context.note}')
        def get_set_note_lambda(editor, note):
            def editor_set_note():
                editor.set_note(note)
            return editor_set_note
        self.anki_utils.run_on_main(get_set_note_lambda(editor_context.editor, editor_context.note))
        logger.debug('after set_note')
        self.anki_utils.play_sound(full_filename)

    def editor_note_process_rule(self, rule: config_models.MappingRule, editor_context: config_models.EditorContext):
        """process a single rule, unconditionally"""
        preset = self.load_preset(rule.preset_id)
        self.editor_note_add_audio(preset, editor_context)


    # editor related functions
    # ========================

    def get_editor_context(self, editor) -> config_models.EditorContext:
        logger.debug(f'anki editor configuration: currentField: {editor.currentField} '
                     f'last_field_index: {editor.last_field_index} '
                     f'addMode: {editor.addMode} '
                     f'selectedText: [{editor.web.selectedText()}] '
                     + (f'card.note.items: {pprint.pformat(editor.card.note().items())} '
                        f'card.note_type name: {pprint.pformat(editor.card.note_type()["name"])} '
                        if editor.card is not None else 'card: None')
                     )

        selected_text = None

        current_field_num = editor.currentField
        # has the user put the cursor inside a field ?
        current_field_name = None
        if current_field_num != None:
            deck_note_type = self.get_editor_deck_note_type(editor)
            model = aqt.mw.col.models.get(deck_note_type.model_id)
            current_field_name = model['flds'][current_field_num]['name']

        if len(editor.web.selectedText()) > 0:
            # need to get the field name for selected text
            if current_field_num != None:
                selected_text = editor.web.selectedText()

        editor_context = config_models.EditorContext(note=editor.note, 
            editor=editor, 
            add_mode=editor.addMode,
            selected_text=selected_text,
            current_field=current_field_name,
            clipboard=self.anki_utils.get_clipboard_content())
        logger.debug(f'editor_context: {editor_context}')
        return editor_context

    def get_editor_deck_note_type(self, editor) -> config_models.DeckNoteType:
        note = editor.note
        if note == None:
            raise RuntimeError(f'editor.note not found')

        if editor.addMode:
            add_cards: aqt.addcards.AddCards = editor.parentWindow
            return config_models.DeckNoteType(model_id=note.mid, deck_id=add_cards.deckChooser.selectedId())
        else:
            if editor.card == None:
                raise RuntimeError(f'editor.card not found')
            return config_models.DeckNoteType(model_id=note.mid, deck_id=editor.card.did)


    # text processing
    # ===============

    def get_source_text(self, note, batch_source, text_override):
        if text_override != None:
            return text_override

        if batch_source.mode == constants.BatchMode.simple:
            if batch_source.source_field not in note:
                raise errors.SourceFieldNotFoundError(batch_source.source_field)
            source_text = note[batch_source.source_field]
        elif batch_source.mode == constants.BatchMode.template:
            source_text = self.expand_simple_template(note, batch_source.source_template)
        elif batch_source.mode == constants.BatchMode.advanced_template:
            source_text = self.expand_advanced_template(note, batch_source.source_template)
        return source_text

    def expand_simple_template(self, note, source_template):
        field_values = self.get_field_values(note)
        # logger.info(f'field_values: {field_values}')
        try:
            return source_template.format_map(field_values)
        except Exception as e:
            raise errors.TemplateExpansionError(e)

    def expand_advanced_template(self, note, source_template):
        lang = self.get_ui_language()
        raise errors.SuperFreeTTSError(i18n.get_text("error_advanced_template_lite", lang))

    def get_field_values(self, note):
        field_values = {}
        for field_name in list(note.keys()):
            field_values[field_name] = note[field_name]
        return field_values

    def process_text(self, source_text, batch_text_processing):
        processed_text = text_utils.process_text(source_text, batch_text_processing)
        # logger.info(f'before text processing: [{source_text}], after text processing: [{processed_text}]')
        if len(processed_text) == 0:
            raise errors.SourceTextEmpty()
        return processed_text

    # sound generation
    # ================

    def preview_note_audio_editor(self, batch, editor_context: config_models.EditorContext):
        text_override = None
        if batch.source.use_selection:
            if editor_context.selected_text != None:
                text_override = editor_context.selected_text
        self.preview_note_audio(batch, editor_context.note, text_override)

    def preview_note_audio(self, batch, note, text_override):
        batch.validate()
        full_filename, audio_filename = self.get_note_audio(batch, 
            note, context.AudioRequestContext(constants.AudioRequestReason.preview), text_override)
        self.anki_utils.play_sound(full_filename)
    
    def play_realtime_audio(self, realtime_model: config_models.RealtimeConfigSide, text):
        full_filename, audio_filename = self.get_realtime_audio(realtime_model, text)
        self.anki_utils.play_sound(full_filename)

    def play_sound(self, source_text, voice_id, options):
        logger.info(f'playing audio for {source_text}')
        if source_text == None or len(source_text) == 0:
            raise errors.SourceTextEmpty()        
        full_filename, audio_filename = self.generate_audio_write_file(source_text, voice_id, options, context.AudioRequestContext(constants.AudioRequestReason.preview))
        self.anki_utils.play_sound(full_filename)

    def get_preview_all_rules_task(self, deck_note_type: config_models.DeckNoteType,editor_context: config_models.EditorContext, preset_mapping_rules: config_models.PresetMappingRules):
        def preview_fn():
            status = preset_rules_status.PresetRulesStatus('Previewing', self.anki_utils)
            for absolute_index, subset_index, rule in preset_mapping_rules.iterate_applicable_rules(deck_note_type, False):
                with status.get_rule_action_context(rule) as rule_action_context:
                    logger.debug(f'previewing audio for rule {rule}')
                    preset = self.load_preset(rule.preset_id)
                    rule_action_context.set_preset(preset)
                    self.preview_note_audio_editor(preset, editor_context)
        return preview_fn

    def get_preview_all_rules_done(self):
        lang = self.get_ui_language()
        def done_fn(result):
            with self.error_manager.get_single_action_context(i18n.get_text("title_previewing_rule", lang)):
                result = result.result()
        return done_fn

    def preview_all_mapping_rules(self, editor_context: config_models.EditorContext, preset_mapping_rules: config_models.PresetMappingRules = None):
        if preset_mapping_rules == None:
            # load the saved rules
            preset_mapping_rules = self.load_mapping_rules()

        if len(preset_mapping_rules.rules) == 0:
            raise errors.NoPresetMappingRulesDefined()

        deck_note_type = self.get_editor_deck_note_type(editor_context.editor)
        # we want audio generation to happen in the background, but the tooltips will be generated in foreground to display immediately
        self.anki_utils.run_in_background(self.get_preview_all_rules_task(deck_note_type, editor_context, preset_mapping_rules), self.get_preview_all_rules_done())

    def get_apply_all_rules_task(self, deck_note_type: config_models.DeckNoteType,editor_context: config_models.EditorContext, preset_mapping_rules: config_models.PresetMappingRules):
        def apply_fn():
            status = preset_rules_status.PresetRulesStatus('Applying', self.anki_utils)
            for absolute_index, subset_index, rule in preset_mapping_rules.iterate_applicable_rules(deck_note_type, False):
                with status.get_rule_action_context(rule) as rule_action_context:
                    logger.debug(f'previewing audio for rule {rule}')
                    preset = self.load_preset(rule.preset_id)
                    rule_action_context.set_preset(preset)
                    self.editor_note_add_audio(preset, editor_context)
        return apply_fn

    def get_apply_all_rules_done(self):
        lang = self.get_ui_language()
        def done_fn(result):
            with self.error_manager.get_single_action_context(i18n.get_text("title_running_rules", lang)):
                result = result.result()
        return done_fn

    def apply_all_mapping_rules(self, editor_context: config_models.EditorContext, preset_mapping_rules: config_models.PresetMappingRules = None):
        if preset_mapping_rules == None:
            # load the saved rules
            preset_mapping_rules = self.load_mapping_rules()

        if len(preset_mapping_rules.rules) == 0:
            raise errors.NoPresetMappingRulesDefined()

        deck_note_type = self.get_editor_deck_note_type(editor_context.editor)
        # we want audio generation to happen in the background, but the tooltips will be generated in foreground to display immediately
        self.anki_utils.run_in_background(self.get_apply_all_rules_task(deck_note_type, editor_context, preset_mapping_rules), self.get_apply_all_rules_done())


    # processing of sound tags / collection stuff
    # ===========================================

    def generate_audio_write_file(self, source_text, voice_id: voice_module.TtsVoiceId_v3, voice_options, audio_request_context):
        assert isinstance(voice_id, voice_module.TtsVoiceId_v3), f"Expected voice_id to be TtsVoiceId_v3, got {type(voice_id).__name__}"
        format = options.AudioFormat.mp3 # default to mp3
        if options.AUDIO_FORMAT_PARAMETER in voice_options:
            format = options.AudioFormat[voice_options[options.AUDIO_FORMAT_PARAMETER]]

        # write to user files directory
        hash_str = self.get_hash_for_audio_request(source_text, voice_id, voice_options)
        audio_filename = self.get_audio_filename(hash_str, format)
        full_filename = self.get_full_audio_file_name(hash_str, format)
        logger.info(f'requesting audio for hash {hash_str}, full filename {full_filename}')
        
        # Start performance tracking (only active in debug mode)
        tracker = performance_tracker.get_performance_tracker()
        try:
            # Extract voice name for tracking (safely handle various voice_key formats)
            service_name = getattr(voice_id, 'service', 'unknown')
            if hasattr(voice_id, 'voice_key'):
                if isinstance(voice_id.voice_key, dict):
                    voice_key_name = voice_id.voice_key.get('name', 'unknown')
                else:
                    voice_key_name = str(voice_id.voice_key)
            else:
                voice_key_name = 'unknown'
            voice_name = f"{service_name}:{voice_key_name}"
        except Exception as e:
            voice_name = str(voice_id)
            logger.debug(f'Error extracting voice name for tracking: {e}')
        tracker.start_generation(source_text, voice_name)
        
        try:
            if not os.path.exists(full_filename) or os.path.getsize(full_filename) == 0:

                # get the voice which corresponds to the voice_id
                voice = self.service_manager.locate_voice(voice_id)
                logger.info(f'located voice: {voice}')

                audio_data = self.service_manager.get_tts_audio(source_text, voice, voice_options, audio_request_context)
                logger.info(f'not found in cache, requesting')
                logger.debug(f'opening {full_filename}')
                f = open(full_filename, 'wb')
                logger.debug(f'done opening {full_filename}')
                f.write(audio_data)
                logger.debug(f'wrote audio data')
                f.close()
            else:
                logger.info(f'file exists in cache')
        finally:
            # End performance tracking (only active in debug mode)
            duration = tracker.end_generation()
        
        return full_filename, audio_filename

    def get_collection_sound_tag(self, full_filename, audio_filename):
        self.anki_utils.media_add_file(full_filename)
        return f'[sound:{audio_filename}]', audio_filename

    def get_full_audio_file_name(self, hash_str, format: options.AudioFormat):
        # return the absolute path of the audio file in the user_files directory
        user_files_dir = self.anki_utils.get_user_files_dir()
        # Ensure the directory exists
        if not os.path.isdir(user_files_dir):
            logger.info(f"Creating missing user_files directory at {user_files_dir}")
            os.makedirs(user_files_dir, exist_ok=True)
        filename = self.get_audio_filename(hash_str, format)
        return os.path.join(user_files_dir, filename)
    
    def get_audio_filename(self, hash_str, format: options.AudioFormat):
        extension_map = {
            options.AudioFormat.mp3: 'mp3',
            options.AudioFormat.ogg_vorbis: 'ogg',
            options.AudioFormat.ogg_opus: 'ogg',
        }
        extension = extension_map[format]
        filename = f'superfreetss-{hash_str}.{extension}'
        return filename

    def get_hash_for_audio_request(self, source_text, voice_id: voice_module.TtsVoiceId_v3, options):
        combined_data = {
            'source_text': source_text,
            'voice_id': voice_id,
            'options': options
        }
        return hashlib.sha224(str(combined_data).encode('utf-8')).hexdigest()

    def keep_only_sound_tags(self, field_value):
        matches = re.findall(r'\[sound:[^\]]+\]', field_value)
        return ' '.join(matches)


    # processing of Anki TTS tags
    # ===========================

    def get_audio_filename_tts_tag(self, tts_tag):
        preset = self.extract_preset(tts_tag.other_args)
        realtime_side_model = self.get_realtime_side_config(preset)
        full_filename, audio_filename = self.get_realtime_audio(realtime_side_model, tts_tag.field_text)
        return full_filename

    def build_realtime_tts_tag(self, realtime_side_model: config_models.RealtimeConfigSide, setting_key):
        logger.debug('build_realtime_tts_tag')
        if realtime_side_model.source.mode == constants.RealtimeSourceType.AnkiTTSTag:
            logger.debug(f'build_realtime_tts_tag, realtime_side_model: {realtime_side_model}')
            
            # get the audio language of the first voice
            voice_selection = realtime_side_model.voice_selection
            logger.debug(f'voice_selection.selection_mode: {voice_selection.selection_mode}')
            # first, we need to get the voice_id
            if voice_selection.selection_mode == constants.VoiceSelectionMode.single:
                voice_id = voice_selection.voice.voice_id
            else:
                voice_id = voice_selection.get_voice_list()[0].voice_id
            # now, locate the voice for this voice id
            voice = self.service_manager.locate_voice(voice_id)
            audio_language = voice_module.get_audio_language_for_voice(voice)


            field_format = realtime_side_model.source.field_name
            if realtime_side_model.source.field_type == constants.AnkiTTSFieldType.Cloze:
                field_format = f'cloze:{realtime_side_model.source.field_name}'
            elif realtime_side_model.source.field_type == constants.AnkiTTSFieldType.ClozeOnly:
                field_format = f'cloze-only:{realtime_side_model.source.field_name}'
            return '{{tts ' + f"""{audio_language.name} {constants.TTS_TAG_HYPERTTS_PRESET}={setting_key} voices={constants.TTS_TAG_VOICE}:{field_format}""" + '}}'
        else:
            raise Exception(f'unsupported RealtimeSourceType: {realtime_side_model.source.mode}')

    def extract_preset(self, extra_args_array):
        subset = [x for x in extra_args_array if constants.TTS_TAG_HYPERTTS_PRESET in x]
        if len(subset) != 1:
            logger.error(f'could not process TTS tag extra args: {extra_args_array}')
            raise errors.TTSTagProcessingError()
        array_entry = subset[0]
        components = array_entry.split('=')
        return components[1]

    def get_realtime_side_config(self, preset):
        # based 
        if constants.AnkiCardSide.Front.name in preset:
            # front
            preset_name = preset.replace(constants.AnkiCardSide.Front.name + '_', '')
            return self.load_realtime_config(preset_name).front
        else:
            # back
            preset_name = preset.replace(constants.AnkiCardSide.Back.name + '_', '')
            return self.load_realtime_config(preset_name).back


    def card_template_has_tts_tag(self, note, side, card_ord):
        # return preset name if found
        note_model = note.note_type()
        card_template = note_model["tmpls"][card_ord]
        side_template_key = 'qfmt'
        if side == constants.AnkiCardSide.Back:
            side_template_key = 'afmt'
        side_template = card_template[side_template_key]
        side_template = side_template.replace('\n', ' ')
        m = re.match(r'.*{{tts.*superfreetss_preset=([^\s]+).*}}.*', side_template)
        if m != None:
            preset_name = m.groups()[0]
            preset_name = preset_name.replace(side.name + '_', '')
            logger.info(f'found preset name in TTS tag inside card template: {preset_name}')
            return preset_name
        else:
            logger.info(f'didnt find a TTS tag in card template: {side_template}')
        return None


    def remove_tts_tag(self, card_template):
        return re.sub('{{tts.*}}', '', card_template)

    def set_tts_tag_note_model(self, realtime_side_model: config_models.RealtimeConfigSide, setting_key, note_model, side, card_ord, clear_only):
        logger.debug('set_tts_tag_note_model')
        # build tts tag
        tts_tag = self.build_realtime_tts_tag(realtime_side_model, setting_key)
        logger.info(f'tts tag: {tts_tag}')

        return self.alter_tts_tag_note_model(note_model, side, card_ord, clear_only, tts_tag)


    def alter_tts_tag_note_model(self, note_model, side, card_ord, clear_only, tts_tag):
        # alter card template
        card_template = note_model["tmpls"][card_ord]
        side_template_key = 'qfmt'
        if side == constants.AnkiCardSide.Back:
            side_template_key = 'afmt'
        side_template = card_template[side_template_key]
        side_template = self.remove_tts_tag(side_template)
        if not clear_only:
            side_template += '\n' + tts_tag
        card_template[side_template_key] = side_template

        note_model["tmpls"][card_ord] = card_template

        return note_model

    def render_card_template_extract_tts_tag(self, realtime_model: config_models.RealtimeConfig, note, side, card_ord):
        realtime_model.validate()
        note_model = note.note_type()
        note_model = copy.deepcopy(note_model)
        note_model = self.set_tts_tag_note_model(realtime_model, 'preview', note_model, side, card_ord, False)
        logger.debug(f'render_card_template_extract_tts_tag, note_model {pprint.pformat(note_model, compact=True, width=500)}')

        card = self.anki_utils.create_card_from_note(note, card_ord, note_model, note_model["tmpls"][card_ord])
        if side == constants.AnkiCardSide.Front:
            return self.anki_utils.extract_tts_tags(card.question_av_tags())
        elif side == constants.AnkiCardSide.Back:
            return self.anki_utils.extract_tts_tags(card.answer_av_tags())

    def build_side_settings_key(self, card_side: constants.AnkiCardSide, settings_key):
        return f'{card_side.name}_{settings_key}'


    def persist_realtime_config_update_note_type(self, realtime_model: config_models.RealtimeConfig, note, card_ord, current_settings_key):
        logger.debug('persist_realtime_config_update_note_type')
        undo_id = self.anki_utils.undo_tts_tag_start()

        settings_key = self.save_realtime_config(realtime_model, current_settings_key)
        note_model = note.note_type()
        
        # proces front side
        side = constants.AnkiCardSide.Front
        if realtime_model.front.side_enabled:
            side_settings_key = self.build_side_settings_key(side, settings_key)
            note_model = self.set_tts_tag_note_model(realtime_model.front, side_settings_key, note_model, side, card_ord, False)
        else:
            note_model = self.set_tts_tag_note_model(realtime_model.front, None, note_model, side, card_ord, True)

        # process back side
        side = constants.AnkiCardSide.Back
        if realtime_model.back.side_enabled:
            side_settings_key = self.build_side_settings_key(side, settings_key)
            note_model = self.set_tts_tag_note_model(realtime_model.back, side_settings_key, note_model, side, card_ord, False)
        else:
            note_model = self.set_tts_tag_note_model(realtime_model.back, None, note_model, side, card_ord, True)

        # save note model
        self.anki_utils.save_note_type_update(note_model)

        self.anki_utils.undo_end(undo_id)

    def remove_tts_tags(self, note, card_ord):
        logger.debug('remove_tts_tags')
        undo_id = self.anki_utils.undo_tts_tag_start()
        note_model = note.note_type()
        side = constants.AnkiCardSide.Front
        note_model = self.alter_tts_tag_note_model(note_model, side, card_ord, True, None)
        side = constants.AnkiCardSide.Back
        note_model = self.alter_tts_tag_note_model(note_model, side, card_ord, True, None)
        self.anki_utils.save_note_type_update(note_model)
        self.anki_utils.undo_end(undo_id)        


    # functions related to getting data from notes
    # ============================================

    def get_all_fields_from_notes(self, note_id_list):
        field_name_set = {}
        for note_id in note_id_list:
            note = self.anki_utils.get_note_by_id(note_id)
            for field in self.get_fields_from_note(note):
                field_name_set[field] = True
        return list(field_name_set.keys())

    def get_fields_from_note(self, note):
        return list(note.keys())

    def populate_batch_status_processed_text(self, note_id_list, batch_source, text_processing, batch_status):
        with batch_status.get_batch_running_action_context():
            for note_id in note_id_list:
                with batch_status.get_note_action_context(note_id, True) as note_action_context:
                    note = self.anki_utils.get_note_by_id(note_id)
                    source_text, processed_text = self.get_source_processed_text(note, batch_source, text_processing)
                    note_action_context.set_source_text(source_text)
                    note_action_context.set_processed_text(processed_text)
                    note_action_context.set_status(constants.BatchNoteStatus.OK)
                if batch_status.must_continue == False:
                    logger.info('batch_status execution interrupted')
                    break

    def get_source_processed_text(self, note, batch_source, text_processing):
        source_text = self.get_source_text(note, batch_source, None)
        logger.debug(f'get_source_processed_text: source_text: {source_text}')
        processed_text = text_utils.process_text(source_text, text_processing)
        return source_text, processed_text

    # functions related to addon config
    # =================================

    # presets
    
    def get_preset_list(self) -> List[config_models.PresetInfo]:
        if constants.CONFIG_PRESETS not in self.config:
            return []
        preset_list = []
        for preset_id, preset_data in self.config[constants.CONFIG_PRESETS].items():
            preset_list.append(config_models.PresetInfo(id=preset_id, name=preset_data['name']))
        # sort alphabetically
        preset_list.sort(key=lambda x: x.name)
        return preset_list

    def save_preset(self, preset: config_models.BatchConfig):
        preset.validate()
        if constants.CONFIG_PRESETS not in self.config:
            self.config[constants.CONFIG_PRESETS] = {}
        self.config[constants.CONFIG_PRESETS][preset.uuid] = preset.serialize()
        self.anki_utils.write_config(self.config)
        logger.info(f'saved preset [{preset.name}] {pprint.pformat(preset.serialize(), compact=True, width=500)}')

    def load_preset(self, preset_id: str) -> config_models.BatchConfig:
        logger.info(f'loading preset [{preset_id}]')
        if preset_id not in self.config[constants.CONFIG_PRESETS]:
            raise errors.PresetNotFound(preset_id)
        return self.deserialize_batch_config(self.config[constants.CONFIG_PRESETS][preset_id])

    def get_preset_name(self, preset_id: str) -> str:
        if preset_id not in self.config[constants.CONFIG_PRESETS]:
            raise errors.PresetNotFound(preset_id)        
        return self.config[constants.CONFIG_PRESETS][preset_id]['name']

    def delete_preset(self, preset_id: str):
        if preset_id not in self.config[constants.CONFIG_PRESETS]:
            raise errors.PresetNotFound(preset_id)
        del self.config[constants.CONFIG_PRESETS][preset_id]
        self.anki_utils.write_config(self.config)        

    def get_next_preset_name(self) -> str:
        """returns the next available preset name which doesn't collide with others"""
        preset_list: List[config_models.PresetInfo] = self.get_preset_list()
        preset_name_dict = {}
        for preset_info in preset_list:
            preset_name_dict[preset_info.name] = True
        i = 1
        new_preset_name = f'Preset {i}'
        while new_preset_name in preset_name_dict:
            i += 1
            new_preset_name = f'Preset {i}'
        return new_preset_name

    # default presets / easy mode

    def get_default_easy_preset_name(self, deck_note_type: config_models.DeckNoteType) -> str:
        note_type_name = self.anki_utils.get_note_type_name(deck_note_type.model_id)
        deck_name = self.anki_utils.get_deck_name(deck_note_type.deck_id)
        return f'Default {note_type_name} {deck_name}'

    def get_default_preset_id(self, deck_note_type: config_models.DeckNoteType) -> str:
        # returns preset_id or None
        mapping_rules = self.load_mapping_rules()
        return mapping_rules.get_default_preset_id(deck_note_type)

    def save_default_preset(self, deck_note_type: config_models.DeckNoteType, preset: config_models.BatchConfig):
        # first, save the preset
        self.save_preset(preset)
        # associate the preset with the deck_note_type
        mapping_rules = self.load_mapping_rules()
        mapping_rules.set_default_preset_id(deck_note_type, preset.uuid)
        # save the mapping rules
        self.save_mapping_rules(mapping_rules)
        

    # mapping rules
    def save_mapping_rules(self, mapping_rules: config_models.PresetMappingRules):
        self.config[constants.CONFIG_MAPPING_RULES] = config_models.serialize_preset_mapping_rules(mapping_rules)
        self.anki_utils.write_config(self.config)
        logger.info('saved mapping rules')

    def load_mapping_rules(self) -> config_models.PresetMappingRules:
        if constants.CONFIG_MAPPING_RULES not in self.config:
            return config_models.PresetMappingRules()
        return config_models.deserialize_preset_mapping_rules(self.config[constants.CONFIG_MAPPING_RULES])
    
    # realtime config

    def save_realtime_config(self, realtime_model, settings_key):
        realtime_model.validate()
        if constants.CONFIG_REALTIME_CONFIG not in self.config:
            self.config[constants.CONFIG_REALTIME_CONFIG] = {}
        
        if settings_key == None:
            # find a free name
            key_index = 0
            candidate_key = f'realtime_{key_index}'
            while candidate_key in self.config[constants.CONFIG_REALTIME_CONFIG]:
                key_index += 1
                candidate_key = f'realtime_{key_index}'
            final_key = candidate_key
        else:
            # use the key provided
            final_key = settings_key
        self.config[constants.CONFIG_REALTIME_CONFIG][final_key] = realtime_model.serialize()
        self.anki_utils.write_config(self.config)
        return final_key

    def load_realtime_config(self, settings_key):
        logger.info(f'loading realtime config [{settings_key}]')
        if settings_key not in self.config[constants.CONFIG_REALTIME_CONFIG]:
            raise errors.RealtimePresetNotFound(settings_key)
        realtime_config = self.config[constants.CONFIG_REALTIME_CONFIG][settings_key]
        logger.info(f'loaded realtime config {pprint.pformat(realtime_config, compact=True, width=500)}')
        return self.deserialize_realtime_config(realtime_config)

    # services config

    def get_client_uuid(self) -> str:
        return self.get_configuration().user_uuid

    def save_configuration(self, configuration_model):
        configuration_model = self.service_manager.remove_non_existent_services(configuration_model)
        configuration_model.validate()
        self.config[constants.CONFIG_CONFIGURATION] = config_models.serialize_configuration(configuration_model)
        self.anki_utils.write_config(self.config)

    def get_configuration(self) -> config_models.Configuration:
        return self.deserialize_configuration(self.config.get(constants.CONFIG_CONFIGURATION, {}))

    def save_superfreetss_pro_api_key(self, api_key: str):
        """Super Free TTS: Pro mode disabled, no-op."""
        pass

    def reconfigure_service_manager(self):
        """reconfigures the service manager with the current configuration"""
        configuration = self.get_configuration()
        preferences = self.get_preferences()
        disable_ssl_verification = preferences.error_handling.disable_ssl_verification
        services_enabled = self.service_manager.configure(configuration, disable_ssl_verification)
        self.service_manager.clear_voice_list_cache()
        logger.debug(f'reconfigure_service_manager, services_enabled: {services_enabled}')
        
        # Recreate batch executor with updated worker configuration
        try:
            service_config_map = configuration.get_service_config()
            
            defaults = {
                'PiperTTS': 2,
                'KokoroTTS': 1,
                'EdgeTTS': 3,
                'MmsTTS': 1,
            }
            pref_fallback = {}
            service_pool_map = {
                'PiperTTS': 'Piper',
                'KokoroTTS': 'Kokoro',
                'EdgeTTS': 'EdgeTTS',
                'MmsTTS': 'MMS',
            }
            
            engine_config = {}
            for service_name, pool_name in service_pool_map.items():
                service_config = service_config_map.get(service_name, {})
                concurrency = service_config.get('concurrency_workers') or pref_fallback.get(service_name) or defaults.get(service_name, 1)
                
                max_workers = cpu_utils.CPUInfo.get_max_workers()
                if concurrency > max_workers:
                    logger.warning(f'Service {service_name} concurrency_workers ({concurrency}) exceeds physical CPU cores ({max_workers}), capping to {max_workers}')
                    concurrency = max_workers
                engine_config[pool_name] = max(1, concurrency)
            
            self.executor = batch_executor.get_multi_engine_executor(engine_config=engine_config)
            logger.info(f'[RECONFIG] Batch executor updated with new settings: {engine_config}')
        except Exception as e:
            logger.warning(f'[RECONFIG] Failed to update batch executor: {e}')
        
        if services_enabled:
            # at least one service was enabled
            self.anki_utils.broadcast_services_configured()

    def config_register_added_audio(self):
        """registers that the user has added audio, so we can show the welcome screen"""
        configuration = self.get_configuration()
        if configuration.trial_registration_step == config_models.TrialRegistrationStep.pending_add_audio:
            configuration.trial_registration_step = config_models.TrialRegistrationStep.finished
            configuration.display_introduction_message = False
            self.save_configuration(configuration)
            self.anki_utils.run_on_main(self.anki_utils.broadcast_audio_added)

    def superfreetss_pro_enabled(self):
        # Super Free TTS: Pro always disabled
        return False

    def set_editor_use_selection(self, use_selection):
        self.config[constants.CONFIG_USE_SELECTION] = use_selection
        self.anki_utils.write_config(self.config)

    def get_editor_use_selection(self):
        return self.config.get(constants.CONFIG_USE_SELECTION, False)

    # preferences
    def get_preferences(self):
        return self.deserialize_preferences(self.config.get(constants.CONFIG_PREFERENCES, {}))

    def apply_logging_preferences(self):
        """Apply logging preferences from configuration."""
        try:
            prefs = self.get_preferences()
            if prefs.error_handling.debug_mode:
                log_dir = self.anki_utils.get_user_files_dir()
                if not os.path.isdir(log_dir):
                    os.makedirs(log_dir, exist_ok=True)
                log_path = os.path.join(log_dir, 'superfreetss.log')
                logging_utils.configure_file_logging(log_path)
                logger.info(f"Debug logging enabled. Log file: {log_path}")
            else:
                logging_utils.configure_silent()
        except Exception as e:
            # Fallback to silent if preferences can't be loaded yet
            logging_utils.configure_silent()

    def save_preferences(self, preferences_model):
        self.config[constants.CONFIG_PREFERENCES] = config_models.serialize_preferences(preferences_model)
        self.anki_utils.write_config(self.config)
        # Refresh menu language immediately
        gui.update_menu_language(self)
        # Apply logging preferences
        self.apply_logging_preferences()
        # reconfigure service manager to apply new SSL settings
        self.reconfigure_service_manager()
        
        # Super Free TTS: Update worker pool size
        try:
            from .services import service_mms
            service_mms._sherpa_pool.update_max_processes(preferences_model.sherpa_max_processes)
        except Exception as pool_err:
            logger.warning(f"Failed to update worker pool: {pool_err}")

    # ui language
    # ===========

    def get_ui_language(self) -> str:
        """
        Lấy ngôn ngữ giao diện hiện tại cho Super Free TTS.
        - Đọc từ Preferences.ui_language
        - Nếu không hợp lệ hoặc chưa set, fallback về 'en'
        """
        prefs = self.get_preferences()
        lang = getattr(prefs, "ui_language", "en")
        if lang not in i18n.SUPPORTED_LANGUAGES:
            lang = "en"
        return lang

    # deserialization routines for loading from config
    # ================================================

    def perform_config_migration(self):
        self.config = config_models.migrate_configuration(self.anki_utils, self.config)
        self.anki_utils.write_config(self.config)

    def deserialize_batch_config(self, batch_config):
        batch = config_models.BatchConfig(self.anki_utils)
        source = config_models.deserialize_batchsource(batch_config['source'])
        target = config_models.deserialize_batch_target(batch_config['target'])
        voice_selection = self.deserialize_voice_selection(batch_config['voice_selection'])

        text_processing_config = batch_config.get('text_processing', {})
        text_processing = self.deserialize_text_processing(text_processing_config)

        batch.set_source(source)
        batch.set_target(target)
        batch.set_voice_selection(voice_selection)
        batch.text_processing = text_processing
        batch.uuid = batch_config['uuid']
        batch.name = batch_config['name']
        
        return batch

    def deserialize_realtime_config(self, realtime_config):
        realtime = config_models.RealtimeConfig()
        realtime.front = self.deserialize_realtime_side_config(realtime_config['front'])
        realtime.back = self.deserialize_realtime_side_config(realtime_config['back'])
        return realtime

    def deserialize_realtime_side_config(self, realtime_side_config):
        realtime_side = config_models.RealtimeConfigSide()
        realtime_side.side_enabled = realtime_side_config['side_enabled']
        if not realtime_side.side_enabled:
            return realtime_side

        realtime_source_type = constants.RealtimeSourceType[realtime_side_config['source']['mode']]
        if realtime_source_type == constants.RealtimeSourceType.AnkiTTSTag:
            source = config_models.RealtimeSourceAnkiTTS()
            source.field_name = realtime_side_config['source']['field_name']
            source.field_type = constants.AnkiTTSFieldType[realtime_side_config['source']['field_type']]
        else:
            raise Exception(f'unsupported RealtimeSourceType: {realtime_source_type}')
        voice_selection = self.deserialize_voice_selection(realtime_side_config['voice_selection'])
        text_processing_config = realtime_side_config.get('text_processing', {})
        text_processing = self.deserialize_text_processing(text_processing_config)

        realtime_side.source = source
        realtime_side.voice_selection = voice_selection
        realtime_side.text_processing = text_processing
        
        return realtime_side       

    def deserialize_voice_selection(self, voice_selection_config):
        voice_selection_mode = constants.VoiceSelectionMode[voice_selection_config['voice_selection_mode']]
        if voice_selection_mode == constants.VoiceSelectionMode.single:
            single = config_models.VoiceSelectionSingle()
            voice_id = voice_module.deserialize_voice_id_v3(voice_selection_config['voice']['voice_id'])
            voice_options = voice_selection_config['voice']['options']
            single.set_voice(config_models.VoiceWithOptions(voice_id, voice_options))
            return single
        elif voice_selection_mode == constants.VoiceSelectionMode.random:
            random = config_models.VoiceSelectionRandom()
            for voice_data in voice_selection_config['voice_list']:
                voice_id = voice_module.deserialize_voice_id_v3(voice_data['voice_id'])
                try:
                    # try to locate the voice
                    voice = self.service_manager.locate_voice(voice_id)
                    random.add_voice(config_models.VoiceWithOptionsRandom(voice_id, voice_data['options'], voice_data['weight']))
                except errors.VoiceIdNotFound as exc:
                    logger.warning(f'voice_id not found: {voice_id}, omitting from random selection')
            return random
        elif voice_selection_mode == constants.VoiceSelectionMode.priority:
            priority = config_models.VoiceSelectionPriority()
            for voice_data in voice_selection_config['voice_list']:
                voice_id = voice_module.deserialize_voice_id_v3(voice_data['voice_id'])
                try:
                    # try to locate the voice
                    voice = self.service_manager.locate_voice(voice_id)
                    priority.add_voice(config_models.VoiceWithOptionsPriority(voice_id, voice_data['options']))
                except errors.VoiceIdNotFound as exc:
                    logger.warning(f'voice_id not found: {voice_id}, omitting from priority selection')
            return priority

    def deserialize_text_processing(self, text_processing_config):
        text_processing = config_models.TextProcessing()
        text_processing.html_to_text_line = text_processing_config.get('html_to_text_line', constants.TEXT_PROCESSING_DEFAULT_HTMLTOTEXTLINE)
        text_processing.strip_brackets = text_processing_config.get('strip_brackets', constants.TEXT_PROCESSING_DEFAULT_STRIP_BRACKETS)
        text_processing.strip_cloze = text_processing_config.get('strip_cloze', constants.TEXT_PROCESSING_DEFAULT_STRIP_CLOZE)
        text_processing.ssml_convert_characters = text_processing_config.get('ssml_convert_characters', constants.TEXT_PROCESSING_DEFAULT_SSML_CHARACTERS)
        text_processing.run_replace_rules_after = text_processing_config.get('run_replace_rules_after', constants.TEXT_PROCESSING_DEFAULT_REPLACE_AFTER)
        text_processing.ignore_case = text_processing_config.get('ignore_case', constants.TEXT_PROCESSING_DEFAULT_IGNORE_CASE)
        rules = text_processing_config.get('text_replacement_rules', [])
        for rule in rules:
            rule_obj = config_models.TextReplacementRule(constants.TextReplacementRuleType[rule['rule_type']])
            rule_obj.source = rule['source']
            rule_obj.target = rule['target']
            text_processing.add_text_replacement_rule(rule_obj)
        return text_processing

    def deserialize_configuration(self, configuration_config) -> config_models.Configuration:
        return config_models.deserialize_configuration(configuration_config)

    def deserialize_preferences(self, preferences_config):
        return config_models.deserialize_preferences(preferences_config)

    # error handling
    # ==============
    def get_tts_player_action_context(self):
        lang = self.get_ui_language()
        return self.error_manager.get_single_action_context_configurable(i18n.get_text("title_playing_realtime", lang), 
            self.get_preferences().error_handling.realtime_tts_errors_dialog_type)
