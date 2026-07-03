
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
import threading
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
from . import batch_progress_ui
from . import audio_file_store
from . import note_audio_updater
from . import source_text_resolver
from . import config_store as config_store_module
from . import realtime_manager as realtime_manager_module
from . import batch_orchestrator as batch_orchestrator_module
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
        self.latest_saved_batch_name: Optional[str] = None
        self.text_processing_cache = {}  # Simple dict for processed text caching

        # ConfigStore owns all config reads/writes from this point on.
        self.config_store = config_store_module.ConfigStore(anki_utils, service_manager)
        # Expose self.config as a live reference to the same dict for legacy code
        # that still reads self.config directly (updated after migration below).
        self.config = self.config_store.config

        # RealtimeManager owns all template tags and realtime playback.
        self.realtime_manager = realtime_manager_module.RealtimeManager(self)

        # BatchOrchestrator handles all batch logic, deduplication, and checkpoints.
        self.batch_orchestrator = batch_orchestrator_module.BatchOrchestrator(self)

        self.audio_store = audio_file_store.AudioFileStore(self.anki_utils, self.get_preferences)

        # Apply logging preferences based on stored debug mode
        self.apply_logging_preferences()

        # Initialize multi-engine executor with settings from service configurations
        try:
            configuration_config = self.config.get(constants.CONFIG_CONFIGURATION, {})
            service_config_map = configuration_config.get(constants.CONFIG_SERVICE_CONFIG, {})
            engine_config = self._build_engine_config(service_config_map)
            self.executor = batch_executor.get_multi_engine_executor(engine_config=engine_config)
            logger.info(f'[INIT] Multi-engine executor configured with CPU-validated settings: {engine_config}')
        except Exception as e:
            logger.warning(f'[INIT] Failed to initialize multi-engine executor, falling back to unified: {e}')
            self.executor = batch_executor.get_batch_executor(max_workers=1)

        # Maintenance: migration, audio registration, cache cleanup
        self.perform_config_migration()
        self.config_register_added_audio()
        self.cleanup_user_files()

    # =========================================================================
    # Engine configuration helpers (single source of truth)
    # =========================================================================

    def _build_engine_config(self, service_config_map: dict) -> dict:
        """Build engine_config dict from service configurations.
        
        Single source of truth for concurrency defaults, validation, and
        pool scaling.  Called by both __init__ and reconfigure_service_manager.
        """
        defaults = {
            'PiperTTS': 1,
            'KokoroTTS': 1,
            'EdgeTTS': batch_constants.EDGETTS_MAX_WORKERS,
            'MmsTTS': 1,
            'SupertonicTTS': 1,
        }
        service_pool_map = {
            'PiperTTS': 'Piper',
            'KokoroTTS': 'Kokoro',
            'EdgeTTS': 'EdgeTTS',
            'MmsTTS': 'MMS',
            'SupertonicTTS': 'Supertonic',
        }
        engine_config = {}
        for service_name, pool_name in service_pool_map.items():
            service_config = service_config_map.get(service_name, {})
            concurrency = service_config.get('concurrency_workers') or defaults.get(service_name, 1)
            
            # EdgeTTS is I/O-bound → capped by EDGETTS_MAX_WORKERS.
            # Local engines are CPU-bound → capped by physical cores.
            max_cap = batch_constants.EDGETTS_MAX_WORKERS if service_name == 'EdgeTTS' else cpu_utils.CPUInfo.get_max_workers()
            if concurrency > max_cap:
                logger.warning(f'Service {service_name} concurrency_workers ({concurrency}) exceeds max ({max_cap}), capping')
                concurrency = max_cap
            engine_config[pool_name] = max(1, concurrency)
            
            self._auto_scale_pool(pool_name, engine_config[pool_name])
        return engine_config

    def _auto_scale_pool(self, pool_name: str, concurrency: int) -> None:
        """Auto-scale internal process pools for Sherpa-based services."""
        try:
            if pool_name == 'Piper':
                from .services import service_piper
                service_piper._piper_pool.update_max_processes(concurrency)
            elif pool_name == 'Kokoro':
                from .services import service_kokoro
                service_kokoro._kokoro_pool.update_max_processes(concurrency)
            elif pool_name == 'MMS':
                from .services import service_mms
                service_mms._sherpa_pool.update_max_processes(concurrency)
            elif pool_name == 'Supertonic':
                from .services import service_supertonic
                service_supertonic._supertonic_pool.update_max_processes(concurrency)
        except Exception as pool_err:
            logger.warning(f"Failed to auto-scale pool for {pool_name}: {pool_err}")

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

    def _set_batch_status_with_ui_refresh(self, batch_status, message, phase=None):
        """Set stable batch phase/status; UI refresh is scheduled by BatchStatus."""
        if phase is not None:
            batch_status.set_phase(phase)
        batch_status.set_status_message(message)

    def prepare_batch_audio_generation(self, note_id_list, batch, batch_status):
        return self.batch_orchestrator.prepare_batch_audio_generation(note_id_list, batch, batch_status)

    def generate_prepared_batch_audio(self, prepared_batch, batch_status):
        return self.batch_orchestrator.generate_prepared_batch_audio(prepared_batch, batch_status)

    def apply_generated_batch_audio(self, generated_results, batch, batch_status, anki_collection):
        return self.batch_orchestrator.apply_generated_batch_audio(generated_results, batch, batch_status, anki_collection)

    def process_batch_audio(self, note_id_list, batch, batch_status, anki_collection):
        return self.batch_orchestrator.process_batch_audio(note_id_list, batch, batch_status, anki_collection)

    def _collect_batch_duplicates(self, tasks):
        return self.batch_orchestrator._collect_batch_duplicates(tasks)

    def _execute_unique_tasks_unified(self, tasks, dedup_map, batch_status):
        return self.batch_orchestrator._execute_unique_tasks_unified(tasks, dedup_map, batch_status)

    def _apply_batch_deduplication(self, tasks, dedup_map, audio_cache, batch_status):
        return self.batch_orchestrator._apply_batch_deduplication(tasks, dedup_map, audio_cache, batch_status)

    def _get_sequence_service_limits(self, items):
        service_limits = {}
        if not items:
            return service_limits

        for _, task_data, _ in items:
            service_name = self.executor.detect_service(task_data)
            if service_name in service_limits:
                continue

            try:
                configured_workers = self.executor.get_executor(service_name)._max_workers
            except Exception:
                configured_workers = getattr(self.executor, 'engine_config', {}).get('default', 1)

            if service_name == 'EdgeTTS':
                max_cap = batch_constants.EDGETTS_MAX_WORKERS
            else:
                max_cap = min(batch_constants.MAX_WORKER_THREADS, cpu_utils.CPUInfo.get_max_workers())

            service_limits[service_name] = max(1, min(int(configured_workers), max_cap))

        return service_limits

    def _get_sequence_worker_limit(self, items):
        if not items:
            return 1

        service_limits = self._get_sequence_service_limits(items)
        total_limit = sum(service_limits.values()) or 1
        return max(1, min(total_limit, len(items)))

    def _generate_audio_single_sequence_task(
        self,
        item: Tuple,
        service_gates: Dict[str, threading.BoundedSemaphore],
    ) -> List:
        """
        Continuous-fill variant of sequence audio generation.

        Handles exactly ONE (dedup_key, task_data, task_indices) item.
        Returns a 1-element list so the outer result-collection loop
        (which iterates ``enumerate(chunk)``) works identically to the
        chunk-based path.

        ``service_gates`` is a shared dict of BoundedSemaphore objects
        owned by ``_execute_unique_tasks_unified``.  Acquiring the gate
        *inside* the worker (not before submit) means:
          - The outer pool fills up immediately with futures.
          - Workers block only on the gate, not on submission.
          - As soon as one EdgeTTS slot frees, the next worker grabs it.
        """
        dedup_key, task_data, task_indices = item
        chosen_voice = task_data.get('chosen_voice')

        if chosen_voice is None:
            return [(None, errors.NoVoiceSet())]

        proc_text = task_data['processed_text']
        voice_id = chosen_voice.voice_id
        voice_options = chosen_voice.options
        service_name = self.executor.detect_service(task_data)

        request_key = (
            dedup_key
            if isinstance(dedup_key, audio_file_store.AudioRequestKey)
            else self.audio_store.build_request_key(proc_text, voice_id, voice_options)
        )
        cached_file = self.audio_store.get_cached_file(request_key)
        if cached_file is not None:
            return [(
                (task_data['source_text'], proc_text, cached_file.audio_filename, cached_file.full_filename),
                None,
            )]

        gate = service_gates.get(service_name)
        try:
            if gate is not None:
                gate.acquire()
            try:
                full_filename, audio_filename = self.generate_audio_write_file(
                    proc_text,
                    voice_id,
                    voice_options,
                    task_data['audio_request_context'],
                )
            finally:
                if gate is not None:
                    gate.release()
            self.executor.cache_result(
                proc_text, str(request_key),
                task_data['source_text'], audio_filename, full_filename,
            )
            return [(
                (task_data['source_text'], proc_text, audio_filename, full_filename),
                None,
            )]
        except Exception as e:
            return [(None, e)]

    def _generate_audio_sequence_task(self, chunk):
        results = [None] * len(chunk)
        service_gates = {
            service_name: threading.BoundedSemaphore(limit)
            for service_name, limit in self._get_sequence_service_limits(chunk).items()
        }

        def generate_one(idx, item):
            dedup_key, task_data, _ = item
            chosen_voice = task_data.get('chosen_voice')
            if chosen_voice is None:
                return idx, (None, errors.NoVoiceSet())

            proc_text = task_data['processed_text']
            voice_id = chosen_voice.voice_id
            voice_options = chosen_voice.options
            service_name = self.executor.detect_service(task_data)
            request_key = dedup_key if isinstance(dedup_key, audio_file_store.AudioRequestKey) else self.audio_store.build_request_key(proc_text, voice_id, voice_options)
            cached_file = self.audio_store.get_cached_file(request_key)

            if cached_file is not None:
                return idx, ((task_data['source_text'], proc_text, cached_file.audio_filename, cached_file.full_filename), None)

            gate = service_gates.get(service_name)
            try:
                if gate is not None:
                    gate.acquire()
                try:
                    full_filename, audio_filename = self.generate_audio_write_file(
                        proc_text,
                        voice_id,
                        voice_options,
                        task_data['audio_request_context'],
                    )
                finally:
                    if gate is not None:
                        gate.release()
                self.executor.cache_result(proc_text, str(request_key), task_data['source_text'], audio_filename, full_filename)
                return idx, ((task_data['source_text'], proc_text, audio_filename, full_filename), None)
            except Exception as e:
                return idx, (None, e)

        max_sequence_workers = self._get_sequence_worker_limit(chunk)
        with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, max_sequence_workers)) as pool:
            futures = [pool.submit(generate_one, idx, item) for idx, item in enumerate(chunk)]
            for future in concurrent.futures.as_completed(futures):
                idx, result = future.result()
                results[idx] = result

        for i in range(len(results)):
            if results[i] is None:
                results[i] = (None, Exception("Sequence audio generation was skipped or interrupted"))

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
            request_key = dedup_key if isinstance(dedup_key, audio_file_store.AudioRequestKey) else self.audio_store.build_request_key(proc_text, voice_id, voice_options)
            cached_file = self.audio_store.get_cached_file(request_key)

            if cached_file is not None:
                results[i] = ((task_data['source_text'], proc_text, cached_file.audio_filename, cached_file.full_filename), None)
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
                    task_data = chunk[idx][1]
                    if audio_data:
                        proc_text = task_data['processed_text']
                        dedup_key = chunk[idx][0]
                        request_key = dedup_key if isinstance(dedup_key, audio_file_store.AudioRequestKey) else self.audio_store.build_request_key(proc_text, voice_id, voice_options)
                        file_result = self.audio_store.write_audio_file_atomic(request_key, audio_data)
                        
                        # Cache in memory
                        self.executor.cache_result(proc_text, str(request_key), task_data['source_text'], file_result.audio_filename, file_result.full_filename)
                        results[idx] = ((task_data['source_text'], proc_text, file_result.audio_filename, file_result.full_filename), None)
                    else:
                        if batch_cfg.voice_selection.selection_mode == constants.VoiceSelectionMode.priority:
                            results[idx] = self._generate_audio_with_priority_fallback(task_data)
                        else:
                            results[idx] = (None, Exception(i18n.get_text("error_audio_gen_failed", self.get_ui_language())))
            except Exception as e:
                logger.error(f"[BATCH] Service batch call failed: {e}")
                service_error = e
            
            # If service call failed, try fallback for priority mode or mark missing items with that error
            if service_error:
                for idx in missing_indices:
                    task_data = chunk[idx][1]
                    if batch_cfg.voice_selection.selection_mode == constants.VoiceSelectionMode.priority:
                        results[idx] = self._generate_audio_with_priority_fallback(task_data)
                    else:
                        results[idx] = (None, service_error)
        for i in range(len(results)):
            if results[i] is None:
                results[i] = (None, Exception("Audio generation was skipped or interrupted"))
                
        return results

    def _generate_audio_with_priority_fallback(self, task_data):
        """Try remaining priority voices one by one for a single batch task."""
        batch_cfg = task_data['batch']
        voice_selection = batch_cfg.voice_selection
        if voice_selection.selection_mode != constants.VoiceSelectionMode.priority:
            return (None, Exception(i18n.get_text("error_audio_gen_failed", self.get_ui_language())))

        priority_voice_list = task_data.get('priority_voice_list')
        if priority_voice_list is None:
            priority_voice_list = copy.copy(voice_selection.voice_list)
        else:
            priority_voice_list = copy.copy(priority_voice_list)

        source_text = task_data['source_text']
        processed_text = task_data['processed_text']
        while len(priority_voice_list) > 0:
            voice_with_options = self.choose_voice(voice_selection, priority_voice_list)
            try:
                request_key = self.audio_store.build_request_key(processed_text, voice_with_options.voice_id, voice_with_options.options)
                full_filename, audio_filename = self.generate_audio_write_file(
                    processed_text,
                    voice_with_options.voice_id,
                    voice_with_options.options,
                    task_data['audio_request_context'],
                )
                self.executor.cache_result(processed_text, str(request_key), source_text, audio_filename, full_filename)
                return ((source_text, processed_text, audio_filename, full_filename), None)
            except errors.AudioNotFoundError:
                continue
            except Exception as exc:
                return (None, exc)

        return (None, errors.AudioNotFoundAnyVoiceError(processed_text))

    def _update_note_with_audio(self, note, batch, source_text, sound_file, full_filename, anki_collection, update_collection=True):
        note_audio_updater.update_note_with_audio(
            self.anki_utils,
            note,
            batch,
            source_text,
            sound_file,
            full_filename,
            anki_collection,
            update_collection=update_collection,
        )

    def process_note_audio(self, batch: config_models.BatchConfig, note, add_mode, audio_request_context, text_override, anki_collection):
        target_field = batch.target.target_field

        if target_field not in note:
            raise errors.TargetFieldNotFoundError(target_field)

        source_text = self.get_source_text(note, batch.source, text_override)
        processed_text = self.process_text(source_text, batch.text_processing)

        full_filename, audio_filename = self.get_audio_file(processed_text, batch.voice_selection, audio_request_context)
        sound_file = audio_filename
        logger.debug(f'setting note[{target_field}] to audio file {sound_file}')
        note_audio_updater.update_note_with_audio(
            self.anki_utils,
            note,
            batch,
            source_text,
            sound_file,
            full_filename,
            anki_collection,
            update_collection=not add_mode,
        )

        return source_text, processed_text, sound_file, full_filename

    def get_note_audio(self, batch, note, audio_request_context, text_override):
        source_text = self.get_source_text(note, batch.source, text_override)
        processed_text = text_utils.process_text(source_text, batch.text_processing)
        if len(processed_text) == 0:
            raise errors.SourceTextEmpty()        
        return self.get_audio_file(processed_text, batch.voice_selection, audio_request_context)

    def get_realtime_audio(self, realtime_model: config_models.RealtimeConfigSide, text):
        return self.realtime_manager.get_realtime_audio(realtime_model, text)

    def get_audio_file(self, processed_text, voice_selection, audio_request_context):
        # sanity checks
        if voice_selection.selection_mode in [
            constants.VoiceSelectionMode.priority,
            constants.VoiceSelectionMode.random,
            constants.VoiceSelectionMode.sequence,
        ]:
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

    def choose_voice(self, voice_selection, voice_list, sequence_index=None) -> config_models.VoiceWithOptions:
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
        elif voice_selection.selection_mode == constants.VoiceSelectionMode.sequence:
            voice_count = len(voice_selection.voice_list)
            if voice_count == 0:
                raise errors.NoVoicesAdded()
            if sequence_index is None:
                sequence_index = getattr(voice_selection, '_sequence_runtime_index', 0)
                voice_selection._sequence_runtime_index = sequence_index + 1
            return voice_selection.voice_list[sequence_index % voice_count]

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
        return source_text_resolver.get_source_text(note, batch_source, text_override, self.get_ui_language())

    def expand_simple_template(self, note, source_template):
        return source_text_resolver.expand_simple_template(note, source_template)

    def expand_advanced_template(self, note, source_template):
        return source_text_resolver.expand_advanced_template(note, source_template, self.get_ui_language())

    def get_field_values(self, note):
        return source_text_resolver.get_field_values(note)

    def process_text(self, source_text, batch_text_processing):
        return source_text_resolver.process_text(source_text, batch_text_processing)

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
        return self.realtime_manager.play_realtime_audio(realtime_model, text)

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
        request_key = self.audio_store.build_request_key(source_text, voice_id, voice_options)
        cached_file = self.audio_store.get_cached_file(request_key)
        file_result = cached_file or self.audio_store.get_file_result(request_key, cache_hit=False)
        logger.info(f'requesting audio for hash {request_key.hash()}, full filename {file_result.full_filename}')
        
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
            if cached_file is None:

                # get the voice which corresponds to the voice_id
                voice = self.service_manager.locate_voice(voice_id)
                logger.info(f'located voice: {voice}')

                audio_data = self.service_manager.get_tts_audio(source_text, voice, voice_options, audio_request_context)
                logger.info(f'not found in cache, requesting')
                logger.debug(f'writing {file_result.full_filename}')
                file_result = self.audio_store.write_audio_file_atomic(request_key, audio_data)
                logger.debug(f'wrote audio data')
            else:
                logger.info(f'file exists in cache')
        finally:
            # End performance tracking (only active in debug mode)
            duration = tracker.end_generation()
        
        return file_result.full_filename, file_result.audio_filename

    def get_collection_sound_tag(self, full_filename, audio_filename):
        return note_audio_updater.get_collection_sound_tag(self.anki_utils, full_filename, audio_filename)

    def get_full_audio_file_name(self, hash_str, format: options.AudioFormat):
        return self.audio_store.get_full_audio_file_name(hash_str, format)
    
    def get_audio_filename(self, hash_str, format: options.AudioFormat):
        return self.audio_store.get_audio_filename(hash_str, format)

    def get_hash_for_audio_request(self, source_text, voice_id: voice_module.TtsVoiceId_v3, options):
        return self.audio_store.build_request_key(source_text, voice_id, options).hash()

    def keep_only_sound_tags(self, field_value):
        return note_audio_updater.keep_only_sound_tags(field_value)


    # Anki TTS and Card template tags (delegated to RealtimeManager)
    def get_audio_filename_tts_tag(self, tts_tag): return self.realtime_manager.get_audio_filename_tts_tag(tts_tag)
    def build_realtime_tts_tag(self, realtime_side_model, setting_key): return self.realtime_manager.build_realtime_tts_tag(realtime_side_model, setting_key)
    def extract_preset(self, extra_args_array): return self.realtime_manager.extract_preset(extra_args_array)
    def get_realtime_side_config(self, preset): return self.realtime_manager.get_realtime_side_config(preset)
    def card_template_has_tts_tag(self, note, side, card_ord): return self.realtime_manager.card_template_has_tts_tag(note, side, card_ord)
    def remove_tts_tag(self, card_template): return self.realtime_manager.remove_tts_tag(card_template)
    def set_tts_tag_note_model(self, realtime_side_model, setting_key, note_model, side, card_ord, clear_only): return self.realtime_manager.set_tts_tag_note_model(realtime_side_model, setting_key, note_model, side, card_ord, clear_only)
    def alter_tts_tag_note_model(self, note_model, side, card_ord, clear_only, tts_tag): return self.realtime_manager.alter_tts_tag_note_model(note_model, side, card_ord, clear_only, tts_tag)
    def render_card_template_extract_tts_tag(self, realtime_model, note, side, card_ord): return self.realtime_manager.render_card_template_extract_tts_tag(realtime_model, note, side, card_ord)
    def build_side_settings_key(self, card_side, settings_key): return self.realtime_manager.build_side_settings_key(card_side, settings_key)
    def persist_realtime_config_update_note_type(self, realtime_model, note, card_ord, current_settings_key): return self.realtime_manager.persist_realtime_config_update_note_type(realtime_model, note, card_ord, current_settings_key)
    def remove_tts_tags(self, note, card_ord): return self.realtime_manager.remove_tts_tags(note, card_ord)        


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
        return self.batch_orchestrator.populate_batch_status_processed_text(note_id_list, batch_source, text_processing, batch_status)

    def get_source_processed_text(self, note, batch_source, text_processing):
        return self.batch_orchestrator.get_source_processed_text(note, batch_source, text_processing)

    def ensure_note_tag(self, note, tag_name: str) -> bool:
        tags = list(getattr(note, 'tags', []) or [])
        if tag_name in tags:
            return False

        if hasattr(note, 'add_tag'):
            try:
                note.add_tag(tag_name)
                return True
            except Exception as e:
                logger.debug(f'falling back to direct tag assignment for [{tag_name}]: {e}')

        tags.append(tag_name)
        note.tags = tags
        return True

    def tag_error_notes(self, note_ids: List[int], anki_collection, tag_name: str = constants.WORKFLOW_ERROR_TAG) -> int:
        tagged_count = 0
        for note_id in dict.fromkeys(note_ids):
            note = self.anki_utils.get_note_by_id(note_id)
            if self.ensure_note_tag(note, tag_name):
                anki_collection.update_note(note)
                tagged_count += 1
        return tagged_count

    # =========================================================================
    # Config / Preset / Workflow / Realtime — delegated to ConfigStore
    # All methods below are thin wrappers that keep the public API identical
    # while logic lives in superfreetts_addon/config_store.py.
    # =========================================================================

    def perform_config_migration(self):
        self.config_store.perform_config_migration()
        # Keep self.config pointing at the (possibly new) dict after migration
        self.config = self.config_store.config

    # presets
    def get_preset_list(self): return self.config_store.get_preset_list()
    def save_preset(self, preset): return self.config_store.save_preset(preset)
    def load_preset(self, preset_id): return self.config_store.load_preset(preset_id)
    def get_preset_name(self, preset_id): return self.config_store.get_preset_name(preset_id)
    def preset_exists(self, preset_id): return self.config_store.preset_exists(preset_id)
    def delete_preset(self, preset_id): return self.config_store.delete_preset(preset_id)
    def get_next_preset_name(self): return self.config_store.get_next_preset_name()

    # workflows
    def get_workflow_list(self): return self.config_store.get_workflow_list()
    def save_workflow(self, workflow): return self.config_store.save_workflow(workflow)
    def load_workflow(self, workflow_id): return self.config_store.load_workflow(workflow_id)
    def workflow_exists(self, workflow_id): return self.config_store.workflow_exists(workflow_id)
    def get_workflow_name(self, workflow_id): return self.config_store.get_workflow_name(workflow_id)
    def delete_workflow(self, workflow_id): return self.config_store.delete_workflow(workflow_id)
    def get_next_workflow_name(self): return self.config_store.get_next_workflow_name()
    def get_missing_workflow_preset_ids(self, workflow): return self.config_store.get_missing_workflow_preset_ids(workflow)

    # default presets
    def get_default_easy_preset_name(self, dnt): return self.config_store.get_default_easy_preset_name(dnt)
    def get_default_preset_id(self, dnt): return self.config_store.get_default_preset_id(dnt)
    def save_default_preset(self, dnt, preset): return self.config_store.save_default_preset(dnt, preset)

    # mapping rules
    def save_mapping_rules(self, mapping_rules): return self.config_store.save_mapping_rules(mapping_rules)
    def load_mapping_rules(self): return self.config_store.load_mapping_rules()

    # realtime config
    def save_realtime_config(self, realtime_model, settings_key): return self.config_store.save_realtime_config(realtime_model, settings_key)
    def load_realtime_config(self, settings_key): return self.config_store.load_realtime_config(settings_key)

    # global configuration
    def get_configuration(self): return self.config_store.get_configuration()
    def save_configuration(self, configuration_model): return self.config_store.save_configuration(configuration_model)
    def get_client_uuid(self): return self.config_store.get_client_uuid()
    def save_superfreetts_pro_api_key(self, api_key: str): pass  # Pro mode disabled

    def reconfigure_service_manager(self):
        """Reconfigure the service manager with the current configuration."""
        configuration = self.get_configuration()
        preferences = self.get_preferences()
        disable_ssl_verification = preferences.error_handling.disable_ssl_verification
        services_enabled = self.service_manager.configure(configuration, disable_ssl_verification)
        self.service_manager.clear_voice_list_cache()
        logger.debug(f'reconfigure_service_manager, services_enabled: {services_enabled}')
        try:
            service_config_map = configuration.get_service_config()
            engine_config = self._build_engine_config(service_config_map)
            self.executor = batch_executor.get_multi_engine_executor(engine_config=engine_config)
            logger.info(f'[RECONFIG] Batch executor updated with new settings: {engine_config}')
        except Exception as e:
            logger.warning(f'[RECONFIG] Failed to update batch executor: {e}')
        if services_enabled:
            self.anki_utils.broadcast_services_configured()

    def config_register_added_audio(self):
        """Register that the user has added audio (welcome-screen state machine)."""
        configuration = self.get_configuration()
        if configuration.trial_registration_step == config_models.TrialRegistrationStep.pending_add_audio:
            configuration.trial_registration_step = config_models.TrialRegistrationStep.finished
            configuration.display_introduction_message = False
            self.save_configuration(configuration)
            self.anki_utils.run_on_main(self.anki_utils.broadcast_audio_added)

    def superfreetts_pro_enabled(self): return False  # Pro always disabled

    # editor selection flag
    def set_editor_use_selection(self, use_selection): return self.config_store.set_editor_use_selection(use_selection)
    def get_editor_use_selection(self): return self.config_store.get_editor_use_selection()

    # preferences
    def get_preferences(self): return self.config_store.get_preferences()
    def get_ui_language(self): return self.config_store.get_ui_language()

    def apply_logging_preferences(self):
        # Bootstrap path: config_store may not exist yet on very first call from __init__
        if hasattr(self, 'config_store'):
            self.config_store.apply_logging_preferences()
        else:
            # Called before config_store is constructed; use raw config dict
            try:
                prefs = config_models.deserialize_preferences(
                    self.anki_utils.get_config().get(constants.CONFIG_PREFERENCES, {})
                )
                if prefs.error_handling.debug_mode:
                    log_dir = self.anki_utils.get_user_files_dir()
                    if not os.path.isdir(log_dir):
                        os.makedirs(log_dir, exist_ok=True)
                    log_path = os.path.join(log_dir, 'superfreetts.log')
                    logging_utils.configure_file_logging(log_path)
                else:
                    logging_utils.configure_silent()
            except Exception:
                logging_utils.configure_silent()

    def save_preferences(self, preferences_model):
        self.config_store.save_preferences(preferences_model)
        gui.update_menu_language(self)
        self.apply_logging_preferences()
        self.reconfigure_service_manager()

    # deserialization (delegates to config_store)
    def deserialize_batch_config(self, batch_config): return self.config_store.deserialize_batch_config(batch_config)
    def deserialize_workflow_config(self, wf_config): return self.config_store.deserialize_workflow_config(wf_config)
    def deserialize_realtime_config(self, rt_config): return self.config_store.deserialize_realtime_config(rt_config)
    def deserialize_realtime_side_config(self, rts_config): return self.config_store.deserialize_realtime_side_config(rts_config)
    def deserialize_voice_selection(self, vs_config): return self.config_store.deserialize_voice_selection(vs_config)
    def deserialize_text_processing(self, tp_config): return self.config_store.deserialize_text_processing(tp_config)
    def deserialize_configuration(self, cfg): return self.config_store.deserialize_configuration(cfg)
    def deserialize_preferences(self, prefs_cfg): return self.config_store.deserialize_preferences(prefs_cfg)

    # error handling
    def get_tts_player_action_context(self):
        lang = self.get_ui_language()
        return self.error_manager.get_single_action_context_configurable(
            i18n.get_text("title_playing_realtime", lang),
            self.get_preferences().error_handling.realtime_tts_errors_dialog_type
        )
