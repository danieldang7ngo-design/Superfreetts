
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
from . import gui_utils
from . import preset_rules_status
from . import i18n
from . import batch_constants
from . import performance_tracker
from . import system_utils
from . import batch_progress_ui
from . import audio_file_store
from . import note_audio_updater
from . import source_text_resolver
from . import config_store as config_store_module
from . import realtime_manager as realtime_manager_module
from . import batch_orchestrator as batch_orchestrator_module
from . import audio_generator as audio_generator_module
from . import editor_manager as editor_manager_module
from . import usage_tracker
logger = logging_utils.get_child_logger(__name__)


class SuperFreeTTS():
    """
    Thin orchestrator / facade for the Super Free TTS addon.

    Wires together all domain modules and exposes a stable public API
    that the UI components and Anki hooks call into.  All business logic
    lives in dedicated sub-modules:

      config_store      — config, presets, workflows, preferences, migration
      realtime_manager  — {{tts}} tag rendering and realtime playback
      batch_orchestrator — batch task preparation, execution, apply
      audio_generator   — single-note audio generation, voice choice
      editor_manager    — Anki editor bridge and Mapping-Rules runner
      note_audio_updater — note field update helpers

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

        from .tts_orchestrator import TTSOrchestrator
        from .ui_controller import UIController
        from .job_pipeline import JobPipeline

        from .tts_orchestrator import TTSOrchestrator
        from .ui_controller import UIController
        from .job_pipeline import JobPipeline

        self.config_store = config_store_module.ConfigStore(anki_utils, service_manager)
        self.config = self.config_store.config

        # Apply the saved UI theme before any dialog is built.
        gui_utils.set_active_theme(self.config_store.get_ui_theme())

        self.orchestrator = TTSOrchestrator(self)
        self.ui = UIController(self)
        self.pipeline = JobPipeline(self)

        self.realtime_manager = realtime_manager_module.RealtimeManager(self)
        self.batch_orchestrator = batch_orchestrator_module.BatchOrchestrator(self)
        self.audio_store = audio_file_store.AudioFileStore(self.anki_utils, self.get_preferences)
        self.audio_generator = audio_generator_module.AudioGenerator(self)
        self.editor_manager = editor_manager_module.EditorManager(self)

        try:
            self.usage_tracker = usage_tracker.UsageTracker(self.anki_utils.get_user_files_dir())
        except Exception as e:
            logger.warning(f"[USAGE] Failed to initialize usage tracker: {e}")
            self.usage_tracker = None

        # Apply logging preferences based on stored debug mode
        self.orchestrator.apply_logging_preferences()

        # Initialize multi-engine executor with settings from service configurations
        try:
            configuration_config = self.config.get(constants.CONFIG_CONFIGURATION, {})
            service_config_map = configuration_config.get(constants.CONFIG_SERVICE_CONFIG, {})
            engine_config = self.orchestrator.build_engine_config(service_config_map)
            self.executor = batch_executor.get_multi_engine_executor(engine_config=engine_config)
            self.orchestrator.executor = self.executor
            logger.info(f'[INIT] Multi-engine executor configured with CPU-validated settings: {engine_config}')
        except Exception as e:
            logger.warning(f'[INIT] Failed to initialize multi-engine executor, falling back to unified: {e}')
            self.executor = batch_executor.get_batch_executor(max_workers=1)
            self.orchestrator.executor = self.executor

        # Maintenance: migration, audio registration, cache cleanup
        self.perform_config_migration()
        self.config_register_added_audio()
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

            logger.info(f'[CACHE] Starting cache cleanup. Retention: {retention_days} days.')
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
                        logger.warning(f'[CACHE] Error deleting {entry.path}: {e}')

            logger.info(f'[CACHE] Cache cleanup finished. Scanned {scanned} files, deleted {deleted} old files.')
        except Exception as e:
            logger.error(f'[CACHE] Error during cache cleanup: {e}')

    def _set_batch_status_with_ui_refresh(self, batch_status, message, phase=None):
        """Set stable batch phase/status; UI refresh is scheduled by BatchStatus."""
        if phase is not None:
            batch_status.set_phase(phase)
        batch_status.set_status_message(message)

    # =========================================================================
    # Batch orchestration — delegated to BatchOrchestrator
    # =========================================================================

    def prepare_batch_audio_generation(self, note_id_list, batch, batch_status):
        return self.batch_orchestrator.prepare_batch_audio_generation(note_id_list, batch, batch_status)

    def generate_prepared_batch_audio(self, prepared_batch, batch_status):
        return self.batch_orchestrator.generate_prepared_batch_audio(prepared_batch, batch_status)

    def apply_generated_batch_audio(self, generated_results, batch, batch_status, anki_collection):
        return self.batch_orchestrator.apply_generated_batch_audio(generated_results, batch, batch_status, anki_collection)

    def apply_generated_batch_audio_chunk(self, generated_results_chunk, batch, batch_status, anki_collection):
        return self.batch_orchestrator.apply_generated_batch_audio_chunk(generated_results_chunk, batch, batch_status, anki_collection)

    def process_batch_audio(self, note_id_list, batch, batch_status, anki_collection):
        return self.batch_orchestrator.process_batch_audio(note_id_list, batch, batch_status, anki_collection)

    def _collect_batch_duplicates(self, tasks):
        return self.batch_orchestrator._collect_batch_duplicates(tasks)

    def _execute_unique_tasks_unified(self, tasks, dedup_map, batch_status):
        return self.batch_orchestrator._execute_unique_tasks_unified(tasks, dedup_map, batch_status)

    def _apply_batch_deduplication(self, tasks, dedup_map, audio_cache, batch_status):
        return self.batch_orchestrator._apply_batch_deduplication(tasks, dedup_map, audio_cache, batch_status)

    def populate_batch_status_processed_text(self, note_id_list, batch_source, text_processing, batch_status):
        return self.batch_orchestrator.populate_batch_status_processed_text(note_id_list, batch_source, text_processing, batch_status)

    def get_source_processed_text(self, note, batch_source, text_processing):
        return self.batch_orchestrator.get_source_processed_text(note, batch_source, text_processing)

    # =========================================================================
    # Audio sequence / batch task workers — kept here (used by batch_orchestrator
    # via self.hypertts)
    # =========================================================================

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
                batch_call_start = time.time()
                audio_datas = self.service_manager.get_tts_audio_batch(missing_texts, voice, voice_options)
                batch_call_elapsed = time.time() - batch_call_start
                # Spread the measured wall-clock time across generated files
                per_file_elapsed = batch_call_elapsed / max(len(missing_texts), 1)
                
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
                        try:
                            service_name = getattr(voice_id, 'service', 'unknown')
                            self.usage_tracker.record_file_generated(
                                task_data.get('audio_request_context'), service_name, len(proc_text), per_file_elapsed
                            )
                        except Exception as usage_error:
                            logger.debug(f"[USAGE] batch record failed: {usage_error}")
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

    # =========================================================================
    # Audio generation — delegated to AudioGenerator
    # =========================================================================

    def choose_voice(self, voice_selection, voice_list, sequence_index=None) -> config_models.VoiceWithOptions:
        return self.audio_generator.choose_voice(voice_selection, voice_list, sequence_index)

    def generate_audio_write_file(self, source_text, voice_id: voice_module.TtsVoiceId_v3, voice_options, audio_request_context):
        return self.audio_generator.generate_audio_write_file(source_text, voice_id, voice_options, audio_request_context)

    def get_audio_file(self, processed_text, voice_selection, audio_request_context):
        return self.audio_generator.get_audio_file(processed_text, voice_selection, audio_request_context)

    def process_note_audio(self, batch: config_models.BatchConfig, note, add_mode, audio_request_context, text_override, anki_collection):
        return self.audio_generator.process_note_audio(batch, note, add_mode, audio_request_context, text_override, anki_collection)

    def get_note_audio(self, batch, note, audio_request_context, text_override):
        return self.audio_generator.get_note_audio(batch, note, audio_request_context, text_override)

    def play_sound(self, source_text, voice_id, options):
        return self.audio_generator.play_sound(source_text, voice_id, options)

    def get_realtime_audio(self, realtime_model: config_models.RealtimeConfigSide, text):
        return self.realtime_manager.get_realtime_audio(realtime_model, text)

    # =========================================================================
    # Note update helpers — delegated to note_audio_updater
    # =========================================================================

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

    def ensure_note_tag(self, note, tag_name: str) -> bool:
        return note_audio_updater.ensure_note_tag(note, tag_name)

    def tag_error_notes(self, note_ids: List[int], anki_collection, tag_name: str = constants.WORKFLOW_ERROR_TAG) -> int:
        return note_audio_updater.tag_error_notes(self.anki_utils, note_ids, anki_collection, tag_name)

    # =========================================================================
    # Editor & Mapping Rules — delegated to EditorManager
    # =========================================================================

    def editor_note_add_audio(self, batch: config_models.BatchConfig, editor_context: config_models.EditorContext, text_input=None):
        return self.editor_manager.editor_note_add_audio(batch, editor_context, text_input)

    def editor_note_process_rule(self, rule: config_models.MappingRule, editor_context: config_models.EditorContext):
        return self.editor_manager.editor_note_process_rule(rule, editor_context)

    def get_editor_context(self, editor) -> config_models.EditorContext:
        return self.editor_manager.get_editor_context(editor)

    def get_editor_deck_note_type(self, editor) -> config_models.DeckNoteType:
        return self.editor_manager.get_editor_deck_note_type(editor)

    def preview_note_audio_editor(self, batch, editor_context: config_models.EditorContext):
        return self.editor_manager.preview_note_audio_editor(batch, editor_context)

    def preview_note_audio(self, batch, note, text_override):
        return self.editor_manager.preview_note_audio(batch, note, text_override)

    def get_preview_all_rules_task(self, deck_note_type: config_models.DeckNoteType, editor_context: config_models.EditorContext, preset_mapping_rules: config_models.PresetMappingRules):
        return self.editor_manager.get_preview_all_rules_task(deck_note_type, editor_context, preset_mapping_rules)

    def get_preview_all_rules_done(self):
        return self.editor_manager.get_preview_all_rules_done()

    def preview_all_mapping_rules(self, editor_context: config_models.EditorContext, preset_mapping_rules: config_models.PresetMappingRules = None):
        return self.editor_manager.preview_all_mapping_rules(editor_context, preset_mapping_rules)

    def preview_with_quick_preset_picker(self, editor_context: config_models.EditorContext):
        return self.editor_manager.preview_with_quick_preset_picker(editor_context)

    def get_apply_all_rules_task(self, deck_note_type: config_models.DeckNoteType, editor_context: config_models.EditorContext, preset_mapping_rules: config_models.PresetMappingRules):
        return self.editor_manager.get_apply_all_rules_task(deck_note_type, editor_context, preset_mapping_rules)

    def get_apply_all_rules_done(self):
        return self.editor_manager.get_apply_all_rules_done()

    def apply_all_mapping_rules(self, editor_context: config_models.EditorContext, preset_mapping_rules: config_models.PresetMappingRules = None):
        return self.editor_manager.apply_all_mapping_rules(editor_context, preset_mapping_rules)

    # =========================================================================
    # Note field helpers
    # =========================================================================

    def get_all_fields_from_notes(self, note_id_list):
        field_name_set = {}
        CHUNK = 500
        for i in range(0, len(note_id_list), CHUNK):
            chunk = note_id_list[i:i + CHUNK]
            placeholders = ",".join("?" * len(chunk))
            rows = aqt.mw.col.db.all(
                f"SELECT DISTINCT mid FROM notes WHERE id IN ({placeholders})",
                *chunk,
            )
            for (mid,) in rows:
                notetype = aqt.mw.col.models.get(mid)
                if notetype:
                    for f in notetype['flds']:
                        field_name_set[f['name']] = True
        return list(field_name_set.keys())

    def get_fields_from_note(self, note):
        return list(note.keys())

    # processing of sound tags / collection stuff
    # ===========================================

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
    def play_realtime_audio(self, realtime_model: config_models.RealtimeConfigSide, text):
        return self.realtime_manager.play_realtime_audio(realtime_model, text)

    # =========================================================================
    # Text processing — delegated to source_text_resolver
    # =========================================================================

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
        self.orchestrator.reconfigure_service_manager()
        self.executor = self.orchestrator.executor

    def config_register_added_audio(self):
        """Register that the user has added audio (welcome-screen state machine)."""
        configuration = self.get_configuration()
        if configuration.trial_registration_step == config_models.TrialRegistrationStep.pending_add_audio:
            configuration.trial_registration_step = config_models.TrialRegistrationStep.finished
            configuration.display_introduction_message = False
            self.save_configuration(configuration)
            self.anki_utils.run_on_main(self.anki_utils.broadcast_audio_added)

    def superfreetts_pro_enabled(self): return False  # Pro always disabled

    # usage tracking
    def get_usage_summary(self):
        if self.usage_tracker is None:
            return {}
        return self.usage_tracker.get_summary()

    def get_usage_recent_sessions(self, limit=20):
        if self.usage_tracker is None:
            return []
        return self.usage_tracker.get_recent_sessions(limit)

    def get_usage_monthly_series(self):
        if self.usage_tracker is None:
            return []
        return self.usage_tracker.get_monthly_series()

    def flush_usage(self):
        if self.usage_tracker is None:
            return
        self.usage_tracker.flush()

    # editor selection flag
    def set_editor_use_selection(self, use_selection): return self.config_store.set_editor_use_selection(use_selection)
    def get_editor_use_selection(self): return self.config_store.get_editor_use_selection()

    # preferences
    def get_preferences(self): return self.config_store.get_preferences()
    def get_ui_language(self): return self.config_store.get_ui_language()
    def get_ui_theme(self): return self.config_store.get_ui_theme()

    def apply_logging_preferences(self):
        self.orchestrator.apply_logging_preferences()

    def save_preferences(self, preferences_model):
        self.config_store.save_preferences(preferences_model)
        gui_utils.set_active_theme(getattr(preferences_model, 'ui_theme', 'vibrant'))
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
