"""
config_store.py — Configuration persistence layer for Super Free TTS.

Responsibility: everything that reads/writes the Anki config dict.
  - Preset CRUD (save, load, delete, list, next name)
  - Workflow CRUD
  - Mapping rules
  - Realtime config (save/load per settings_key)
  - Global configuration & service config
  - Preferences (load, save, apply logging)
  - Deserialization helpers (batch, workflow, realtime, voice_selection, text_processing)
  - Config migration

NOT responsible for:
  - Batch audio generation
  - Realtime TTS rendering
  - Anki UI interactions beyond writing config
"""

import os
import logging
from typing import Any, Callable, Dict, List, Optional

from . import constants
from . import config_models
from . import errors
from . import voice as voice_module
from . import logging_utils
from . import i18n

logger = logging_utils.get_child_logger(__name__)


def _sanitize_for_json(obj):
    """Recursively convert enum.Enum instances to their name strings so
    the resulting structure is JSON serializable.
    """
    import enum as _enum
    if isinstance(obj, _enum.Enum):
        return obj.name
    if isinstance(obj, dict):
        return {k: _sanitize_for_json(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_sanitize_for_json(v) for v in obj]
    return obj


class ConfigStore:
    """
    Single source of truth for reading and writing the addon configuration.

    Receives ``anki_utils`` and a mutable reference to the config dict.
    Call ``reload()`` after ``anki_utils.write_config()`` if the dict is
    replaced externally (e.g. after migration).
    """

    def __init__(self, anki_utils: Any, service_manager: Any) -> None:
        self.anki_utils = anki_utils
        self.service_manager = service_manager
        self.config: Dict = anki_utils.get_config()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _write(self) -> None:
        """Persist current config to Anki."""
        safe_config = _sanitize_for_json(self.config)
        self.anki_utils.write_config(safe_config)

    # ------------------------------------------------------------------
    # Migration
    # ------------------------------------------------------------------

    def perform_config_migration(self) -> None:
        self.config = config_models.migrate_configuration(self.anki_utils, self.config)
        self._write()

    # ------------------------------------------------------------------
    # Presets
    # ------------------------------------------------------------------

    def get_preset_list(self) -> List[config_models.PresetInfo]:
        if constants.CONFIG_PRESETS not in self.config:
            return []
        preset_list = []
        for preset_id, preset_data in self.config[constants.CONFIG_PRESETS].items():
            preset_list.append(config_models.PresetInfo(id=preset_id, name=preset_data['name']))
        preset_list.sort(key=lambda x: x.name)
        return preset_list

    def save_preset(self, preset: config_models.BatchConfig) -> None:
        preset.validate()
        if constants.CONFIG_PRESETS not in self.config:
            self.config[constants.CONFIG_PRESETS] = {}
        self.config[constants.CONFIG_PRESETS][preset.uuid] = preset.serialize()
        self._write()
        logger.info(f'saved preset [{preset.name}] {preset.serialize()}')

    def load_preset(self, preset_id: str) -> config_models.BatchConfig:
        logger.info(f'loading preset [{preset_id}]')
        if preset_id not in self.config.get(constants.CONFIG_PRESETS, {}):
            raise errors.PresetNotFound(preset_id)
        return self.deserialize_batch_config(self.config[constants.CONFIG_PRESETS][preset_id])

    def get_preset_name(self, preset_id: str) -> str:
        if preset_id not in self.config.get(constants.CONFIG_PRESETS, {}):
            raise errors.PresetNotFound(preset_id)
        return self.config[constants.CONFIG_PRESETS][preset_id]['name']

    def preset_exists(self, preset_id: str) -> bool:
        return preset_id in self.config.get(constants.CONFIG_PRESETS, {})

    def delete_preset(self, preset_id: str) -> None:
        if preset_id not in self.config.get(constants.CONFIG_PRESETS, {}):
            raise errors.PresetNotFound(preset_id)
        del self.config[constants.CONFIG_PRESETS][preset_id]
        self._write()

    def get_next_preset_name(self) -> str:
        """Return first available 'Preset N' name that doesn't collide."""
        existing = {p.name for p in self.get_preset_list()}
        i = 1
        name = f'Preset {i}'
        while name in existing:
            i += 1
            name = f'Preset {i}'
        return name

    # ------------------------------------------------------------------
    # Workflows
    # ------------------------------------------------------------------

    def get_workflow_list(self) -> List[config_models.WorkflowInfo]:
        if constants.CONFIG_WORKFLOWS not in self.config:
            return []
        workflow_list = []
        for wf_id, wf_data in self.config[constants.CONFIG_WORKFLOWS].items():
            workflow_list.append(config_models.WorkflowInfo(id=wf_id, name=wf_data['name']))
        workflow_list.sort(key=lambda x: x.name)
        return workflow_list

    def save_workflow(self, workflow: config_models.WorkflowConfig) -> None:
        workflow.validate()
        if constants.CONFIG_WORKFLOWS not in self.config:
            self.config[constants.CONFIG_WORKFLOWS] = {}
        self.config[constants.CONFIG_WORKFLOWS][workflow.uuid] = workflow.serialize()
        self._write()
        logger.info(f'saved workflow [{workflow.name}] {workflow.serialize()}')

    def load_workflow(self, workflow_id: str) -> config_models.WorkflowConfig:
        logger.info(f'loading workflow [{workflow_id}]')
        if workflow_id not in self.config.get(constants.CONFIG_WORKFLOWS, {}):
            raise errors.HyperTTSError(f'Workflow not found: {workflow_id}')
        return self.deserialize_workflow_config(self.config[constants.CONFIG_WORKFLOWS][workflow_id])

    def workflow_exists(self, workflow_id: str) -> bool:
        return workflow_id in self.config.get(constants.CONFIG_WORKFLOWS, {})

    def get_workflow_name(self, workflow_id: str) -> str:
        if workflow_id not in self.config.get(constants.CONFIG_WORKFLOWS, {}):
            raise errors.HyperTTSError(f'Workflow not found: {workflow_id}')
        return self.config[constants.CONFIG_WORKFLOWS][workflow_id]['name']

    def delete_workflow(self, workflow_id: str) -> None:
        if workflow_id not in self.config.get(constants.CONFIG_WORKFLOWS, {}):
            raise errors.HyperTTSError(f'Workflow not found: {workflow_id}')
        del self.config[constants.CONFIG_WORKFLOWS][workflow_id]
        self._write()

    def get_next_workflow_name(self) -> str:
        existing = {w.name for w in self.get_workflow_list()}
        i = 1
        name = f'Workflow {i}'
        while name in existing:
            i += 1
            name = f'Workflow {i}'
        return name

    def get_missing_workflow_preset_ids(self, workflow: config_models.WorkflowConfig) -> List[str]:
        return [pid for pid in workflow.preset_ids if not self.preset_exists(pid)]

    # ------------------------------------------------------------------
    # Default presets / easy mode
    # ------------------------------------------------------------------

    def get_default_easy_preset_name(self, deck_note_type: config_models.DeckNoteType) -> str:
        note_type_name = self.anki_utils.get_note_type_name(deck_note_type.model_id)
        deck_name = self.anki_utils.get_deck_name(deck_note_type.deck_id)
        return f'Default {note_type_name} {deck_name}'

    def get_default_preset_id(self, deck_note_type: config_models.DeckNoteType) -> Optional[str]:
        mapping_rules = self.load_mapping_rules()
        return mapping_rules.get_default_preset_id(deck_note_type)

    def save_default_preset(self, deck_note_type: config_models.DeckNoteType, preset: config_models.BatchConfig) -> None:
        self.save_preset(preset)
        mapping_rules = self.load_mapping_rules()
        mapping_rules.set_default_preset_id(deck_note_type, preset.uuid)
        self.save_mapping_rules(mapping_rules)

    # ------------------------------------------------------------------
    # Mapping rules
    # ------------------------------------------------------------------

    def save_mapping_rules(self, mapping_rules: config_models.PresetMappingRules) -> None:
        self.config[constants.CONFIG_MAPPING_RULES] = config_models.serialize_preset_mapping_rules(mapping_rules)
        self._write()
        logger.info('saved mapping rules')

    def load_mapping_rules(self) -> config_models.PresetMappingRules:
        if constants.CONFIG_MAPPING_RULES not in self.config:
            return config_models.PresetMappingRules()
        return config_models.deserialize_preset_mapping_rules(self.config[constants.CONFIG_MAPPING_RULES])

    # ------------------------------------------------------------------
    # Realtime config
    # ------------------------------------------------------------------

    def save_realtime_config(self, realtime_model, settings_key) -> str:
        realtime_model.validate()
        if constants.CONFIG_REALTIME_CONFIG not in self.config:
            self.config[constants.CONFIG_REALTIME_CONFIG] = {}

        if settings_key is None:
            key_index = 0
            candidate_key = f'realtime_{key_index}'
            while candidate_key in self.config[constants.CONFIG_REALTIME_CONFIG]:
                key_index += 1
                candidate_key = f'realtime_{key_index}'
            final_key = candidate_key
        else:
            final_key = settings_key

        self.config[constants.CONFIG_REALTIME_CONFIG][final_key] = realtime_model.serialize()
        self._write()
        return final_key

    def load_realtime_config(self, settings_key):
        logger.info(f'loading realtime config [{settings_key}]')
        if settings_key not in self.config.get(constants.CONFIG_REALTIME_CONFIG, {}):
            raise errors.RealtimePresetNotFound(settings_key)
        realtime_config = self.config[constants.CONFIG_REALTIME_CONFIG][settings_key]
        logger.info(f'loaded realtime config {realtime_config}')
        return self.deserialize_realtime_config(realtime_config)

    # ------------------------------------------------------------------
    # Global configuration & service config
    # ------------------------------------------------------------------

    def get_configuration(self) -> config_models.Configuration:
        return self.deserialize_configuration(self.config.get(constants.CONFIG_CONFIGURATION, {}))

    def save_configuration(self, configuration_model) -> None:
        configuration_model = self.service_manager.remove_non_existent_services(configuration_model)
        configuration_model.validate()
        self.config[constants.CONFIG_CONFIGURATION] = config_models.serialize_configuration(configuration_model)
        self._write()

    def get_client_uuid(self) -> str:
        return self.get_configuration().user_uuid

    # ------------------------------------------------------------------
    # Editor / selection flag
    # ------------------------------------------------------------------

    def set_editor_use_selection(self, use_selection: bool) -> None:
        self.config[constants.CONFIG_USE_SELECTION] = use_selection
        self._write()

    def get_editor_use_selection(self) -> bool:
        return self.config.get(constants.CONFIG_USE_SELECTION, False)

    # ------------------------------------------------------------------
    # Preferences
    # ------------------------------------------------------------------

    def get_preferences(self):
        return self.deserialize_preferences(self.config.get(constants.CONFIG_PREFERENCES, {}))

    def save_preferences(self, preferences_model) -> None:
        self.config[constants.CONFIG_PREFERENCES] = config_models.serialize_preferences(preferences_model)
        self._write()

    def apply_logging_preferences(self) -> None:
        """Apply debug/silent logging based on stored preferences."""
        try:
            prefs = self.get_preferences()
            if prefs.error_handling.debug_mode:
                log_dir = self.anki_utils.get_user_files_dir()
                if not os.path.isdir(log_dir):
                    os.makedirs(log_dir, exist_ok=True)
                log_path = os.path.join(log_dir, 'superfreetts.log')
                logging_utils.configure_file_logging(log_path)
                logger.info(f"Debug logging enabled. Log file: {log_path}")
            else:
                logging_utils.configure_silent()
        except Exception:
            logging_utils.configure_silent()

    def get_ui_language(self) -> str:
        prefs = self.get_preferences()
        lang = getattr(prefs, 'ui_language', 'en')
        if lang not in i18n.SUPPORTED_LANGUAGES:
            lang = 'en'
        return lang

    # ------------------------------------------------------------------
    # Deserialization helpers
    # ------------------------------------------------------------------

    def deserialize_batch_config(self, batch_config) -> config_models.BatchConfig:
        batch = config_models.BatchConfig(self.anki_utils)
        source = config_models.deserialize_batchsource(batch_config['source'])
        target = config_models.deserialize_batch_target(batch_config['target'])
        voice_selection = self.deserialize_voice_selection(batch_config['voice_selection'])
        text_processing = self.deserialize_text_processing(batch_config.get('text_processing', {}))
        batch.set_source(source)
        batch.set_target(target)
        batch.set_voice_selection(voice_selection)
        batch.text_processing = text_processing
        batch.uuid = batch_config['uuid']
        batch.name = batch_config['name']
        return batch

    def deserialize_workflow_config(self, workflow_config) -> config_models.WorkflowConfig:
        workflow = config_models.WorkflowConfig(self.anki_utils)
        workflow.uuid = workflow_config['uuid']
        workflow.name = workflow_config['name']
        workflow.preset_ids = list(workflow_config.get('preset_ids', []))
        return workflow

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
        text_processing = self.deserialize_text_processing(realtime_side_config.get('text_processing', {}))
        realtime_side.source = source
        realtime_side.voice_selection = voice_selection
        realtime_side.text_processing = text_processing
        return realtime_side

    def deserialize_voice_selection(self, voice_selection_config):
        mode = constants.VoiceSelectionMode[voice_selection_config['voice_selection_mode']]

        if mode == constants.VoiceSelectionMode.single:
            single = config_models.VoiceSelectionSingle()
            voice_id = voice_module.deserialize_voice_id_v3(voice_selection_config['voice']['voice_id'])
            voice_options = voice_selection_config['voice']['options']
            single.set_voice(config_models.VoiceWithOptions(voice_id, voice_options))
            return single

        elif mode == constants.VoiceSelectionMode.random:
            random_sel = config_models.VoiceSelectionRandom()
            for voice_data in voice_selection_config['voice_list']:
                voice_id = voice_module.deserialize_voice_id_v3(voice_data['voice_id'])
                try:
                    self.service_manager.locate_voice(voice_id)
                    random_sel.add_voice(config_models.VoiceWithOptionsRandom(
                        voice_id, voice_data['options'], voice_data['weight']))
                except errors.VoiceIdNotFound:
                    logger.warning(f'voice_id not found: {voice_id}, omitting from random selection')
            return random_sel

        elif mode == constants.VoiceSelectionMode.priority:
            priority = config_models.VoiceSelectionPriority()
            for voice_data in voice_selection_config['voice_list']:
                voice_id = voice_module.deserialize_voice_id_v3(voice_data['voice_id'])
                try:
                    self.service_manager.locate_voice(voice_id)
                    priority.add_voice(config_models.VoiceWithOptionsPriority(voice_id, voice_data['options']))
                except errors.VoiceIdNotFound:
                    logger.warning(f'voice_id not found: {voice_id}, omitting from priority selection')
            return priority

        elif mode == constants.VoiceSelectionMode.sequence:
            sequence = config_models.VoiceSelectionSequence()
            for voice_data in voice_selection_config['voice_list']:
                voice_id = voice_module.deserialize_voice_id_v3(voice_data['voice_id'])
                try:
                    self.service_manager.locate_voice(voice_id)
                    sequence.add_voice(config_models.VoiceWithOptionsSequence(voice_id, voice_data['options']))
                except errors.VoiceIdNotFound:
                    logger.warning(f'voice_id not found: {voice_id}, omitting from sequence selection')
            return sequence

    def deserialize_text_processing(self, text_processing_config) -> config_models.TextProcessing:
        tp = config_models.TextProcessing()
        tp.enabled = text_processing_config.get('enabled', constants.TEXT_PROCESSING_DEFAULT_ENABLED)
        tp.html_to_text_line = text_processing_config.get('html_to_text_line', constants.TEXT_PROCESSING_DEFAULT_HTMLTOTEXTLINE)
        tp.strip_brackets = text_processing_config.get('strip_brackets', constants.TEXT_PROCESSING_DEFAULT_STRIP_BRACKETS)
        tp.strip_cloze = text_processing_config.get('strip_cloze', constants.TEXT_PROCESSING_DEFAULT_STRIP_CLOZE)
        tp.ssml_convert_characters = text_processing_config.get('ssml_convert_characters', constants.TEXT_PROCESSING_DEFAULT_SSML_CHARACTERS)
        tp.run_replace_rules_after = text_processing_config.get('run_replace_rules_after', constants.TEXT_PROCESSING_DEFAULT_REPLACE_AFTER)
        tp.ignore_case = text_processing_config.get('ignore_case', constants.TEXT_PROCESSING_DEFAULT_IGNORE_CASE)
        for rule in text_processing_config.get('text_replacement_rules', []):
            rule_obj = config_models.TextReplacementRule(constants.TextReplacementRuleType[rule['rule_type']])
            rule_obj.source = rule['source']
            rule_obj.target = rule['target']
            tp.add_text_replacement_rule(rule_obj)
        return tp

    def deserialize_configuration(self, configuration_config) -> config_models.Configuration:
        return config_models.deserialize_configuration(configuration_config)

    def deserialize_preferences(self, preferences_config):
        return config_models.deserialize_preferences(preferences_config)
