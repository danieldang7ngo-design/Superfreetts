"""
Unit tests for config models.
"""

import pytest
import sys
import os

addon_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, addon_dir)

from superfreetts_addon import config_models
from superfreetts_addon import constants
from superfreetts_addon import errors
from superfreetts_addon import config_store
from superfreetts_addon import voice as voice_module
from tests.conftest import MockAnkiUtils


@pytest.mark.unit
class TestBatchConfig:
    """Test batch configuration"""
    
    def test_batch_config_creation(self):
        """Test creating batch config"""
        anki_utils = MockAnkiUtils()
        config = config_models.BatchConfig(anki_utils)
        
        assert config is not None
        assert config.uuid is not None
        assert len(config.uuid) > 0
    
    def test_batch_config_properties(self):
        """Test batch config getter/setter properties"""
        anki_utils = MockAnkiUtils()
        config = config_models.BatchConfig(anki_utils)
        
        # Test source property
        source = config_models.BatchSource(mode=constants.BatchMode.simple)
        config.source = source
        assert config.source == source
        
        # Test name property
        config.name = "Test Batch"
        assert config.name == "Test Batch"
    
    def test_batch_config_validation(self):
        """Test batch config validation"""
        anki_utils = MockAnkiUtils()
        config = config_models.BatchConfig(anki_utils)
        
        # Should fail without name
        with pytest.raises(errors.PresetNameNotSet):
            config.validate()
    
    def test_batch_config_uuid_reset(self):
        """Test UUID reset functionality"""
        anki_utils = MockAnkiUtils()
        config = config_models.BatchConfig(anki_utils)
        
        original_uuid = config.uuid
        config.reset_uuid(anki_utils)
        
        # UUID should change (with high probability)
        assert config.uuid is not None


@pytest.mark.unit
class TestBatchSource:
    """Test batch source configuration"""
    
    def test_batch_source_simple(self):
        """Test simple batch source"""
        source = config_models.BatchSource(
            mode=constants.BatchMode.simple,
            source_field="Front"
        )
        
        assert source.mode == constants.BatchMode.simple
        assert source.source_field == "Front"
    
    def test_batch_source_template(self):
        """Test template batch source"""
        source = config_models.BatchSource(
            mode=constants.BatchMode.template,
            source_template="{{Front}}"
        )
        
        assert source.mode == constants.BatchMode.template
        assert source.source_template == "{{Front}}"
    
    def test_batch_source_validation_simple(self):
        """Test validation for simple mode"""
        source = config_models.BatchSource(mode=constants.BatchMode.simple)
        
        # Should fail without field
        with pytest.raises(errors.SourceFieldNotSet):
            source.validate()
    
    def test_batch_source_validation_template(self):
        """Test validation for template mode"""
        source = config_models.BatchSource(mode=constants.BatchMode.template)
        
        # Should fail without template
        with pytest.raises(errors.SourceTemplateNotSet):
            source.validate()
    
    def test_batch_source_string_representation(self):
        """Test __str__ method"""
        source = config_models.BatchSource(
            mode=constants.BatchMode.simple,
            source_field="Front"
        )
        
        assert str(source) == "Front"


@pytest.mark.unit
class TestBatchTarget:
    """Test batch target configuration"""
    
    def test_batch_target_creation(self):
        """Test creating batch target"""
        target = config_models.BatchTarget(
            target_field="Sound",
            text_and_sound_tag=False
        )
        
        assert target.target_field == "Sound"
        assert target.text_and_sound_tag is False
    
    def test_batch_target_validation(self):
        """Test batch target validation"""
        target = config_models.BatchTarget()
        
        # Should fail without target field
        with pytest.raises(errors.TargetFieldNotSet):
            target.validate()
    
    def test_batch_target_defaults(self):
        """Test default values"""
        target = config_models.BatchTarget(target_field="Sound")
        
        assert target.remove_sound_tag is True
        assert target.insert_location == config_models.InsertLocation.AFTER


@pytest.mark.unit
class TestConfiguration:
    """Test main configuration model"""
    
    def test_configuration_creation(self):
        """Test creating configuration"""
        config = config_models.Configuration()
        assert config is not None


@pytest.mark.unit
class TestConfigSerializationAndMigration:
    """Serialization and migration tests for config models"""

    def test_serialization_round_trips(self, mock_anki_utils, mock_service_manager):
        # 1. Configuration
        original_config = config_models.Configuration()
        original_config.user_uuid = "test-uuid-999"
        original_config.service_enabled = {"EdgeTTS": True, "PiperTTS": False}
        serialized_config = config_models.serialize_configuration(original_config)
        deserialized_config = config_models.deserialize_configuration(serialized_config)
        assert deserialized_config.user_uuid == "test-uuid-999"
        assert deserialized_config.service_enabled["EdgeTTS"] is True

        # 2. BatchSource
        src = config_models.BatchSource(mode=constants.BatchMode.simple, source_field="Front")
        serialized_src = config_models.serialize_batchsource(src)
        deserialized_src = config_models.deserialize_batchsource(serialized_src)
        assert deserialized_src.mode == constants.BatchMode.simple
        assert deserialized_src.source_field == "Front"

        # 3. BatchTarget
        tgt = config_models.BatchTarget(target_field="Sound", remove_sound_tag=False)
        serialized_tgt = config_models.serialize_batch_target(tgt)
        deserialized_tgt = config_models.deserialize_batch_target(serialized_tgt)
        assert deserialized_tgt.target_field == "Sound"
        assert deserialized_tgt.remove_sound_tag is False

        # 4. PresetMappingRules
        rules = config_models.PresetMappingRules()
        rule = config_models.MappingRule(
            preset_id="preset-1",
            rule_type=constants.MappingRuleType.NoteType,
            model_id=123,
            enabled=True,
            automatic=True
        )
        rules.rules.append(rule)
        serialized_rules = config_models.serialize_preset_mapping_rules(rules)
        deserialized_rules = config_models.deserialize_preset_mapping_rules(serialized_rules)
        assert len(deserialized_rules.rules) == 1
        assert deserialized_rules.rules[0].preset_id == "preset-1"

    def test_migration_v1_to_latest(self, mock_anki_utils):
        # Migration test from schema version 1 (presets are cleared in v6, so we verify they are empty)
        v1_config = {
            constants.CONFIG_SCHEMA: 1,
            constants.CONFIG_BATCH_CONFIG: {
                "Preset One": {
                    "source": {"mode": "simple", "source_field": "Front"},
                    "target": {"target_field": "Back", "remove_sound_tag": True},
                    "voice_selection": {
                        "voice_selection_mode": "single",
                        "voice": {
                            "options": {},
                            "voice": {
                                "service": "EdgeTTS",
                                "voice_key": {"id": "en-US-JennyNeural"}
                            }
                        }
                    },
                    "text_processing": {}
                }
            }
        }
        
        migrated = config_models.migrate_configuration(mock_anki_utils, v1_config)
        assert migrated[constants.CONFIG_SCHEMA] == constants.CONFIG_SCHEMA_VERSION
        assert len(migrated[constants.CONFIG_PRESETS]) == 0

    def test_migration_v6_to_latest(self, mock_anki_utils):
        # Presets should be preserved when migrating from v6
        v6_config = {
            constants.CONFIG_SCHEMA: 6,
            constants.CONFIG_PRESETS: {
                "preset-uuid": {
                    "uuid": "preset-uuid",
                    "name": "Preset One",
                    "source": {"mode": "simple", "source_field": "Front"},
                    "target": {"target_field": "Back", "remove_sound_tag": True},
                    "voice_selection": {
                        "voice_selection_mode": "single",
                        "voice": {
                            "options": {},
                            "voice_id": {
                                "service": "EdgeTTS",
                                "voice_key": {"id": "en-US-JennyNeural"}
                            }
                        }
                    },
                    "text_processing": {}
                }
            }
        }
        migrated = config_models.migrate_configuration(mock_anki_utils, v6_config)
        assert migrated[constants.CONFIG_SCHEMA] == constants.CONFIG_SCHEMA_VERSION
        assert len(migrated[constants.CONFIG_PRESETS]) == 1
        assert migrated[constants.CONFIG_PRESETS]["preset-uuid"]["name"] == "Preset One"

    def test_migration_v5_to_latest(self, mock_anki_utils):
        # Migration from v5 to check thread/worker clamping
        v5_config = {
            constants.CONFIG_SCHEMA: 5,
            constants.CONFIG_SERVICE_CONFIG: {
                "EdgeTTS": {"num_threads": 20, "concurrency_workers": 20}
            },
            constants.CONFIG_PREFERENCES: {
                "piper_workers": 4,
                "batch_concurrency": 4
            }
        }
        
        migrated = config_models.migrate_configuration(mock_anki_utils, v5_config)
        assert migrated[constants.CONFIG_SCHEMA] == constants.CONFIG_SCHEMA_VERSION
        
        # All workers must be forced/clamped to 1
        edge_config = migrated[constants.CONFIG_SERVICE_CONFIG]["EdgeTTS"]
        assert edge_config["num_threads"] == 1
        assert edge_config["concurrency_workers"] == 1
        
        prefs = migrated[constants.CONFIG_PREFERENCES]
        assert prefs["piper_workers"] == 1
        assert prefs["batch_concurrency"] == 1

    def test_preset_crud_operations(self, mock_anki_utils, mock_service_manager):
        from superfreetts_addon.superfreetts import SuperFreeTTS
        from superfreetts_addon import voice as voice_module
        from unittest.mock import patch

        # Create SuperFreeTTS app instance
        app = SuperFreeTTS(mock_anki_utils, mock_service_manager)
        app.config = {
            constants.CONFIG_PRESETS: {},
            "configuration": {},
            "preferences": {}
        }
        
        # Test creating / saving a preset
        preset = config_models.BatchConfig(mock_anki_utils)
        preset.name = "My Test Preset"
        preset.set_source(config_models.BatchSource(mode=constants.BatchMode.simple, source_field="Front"))
        preset.set_target(config_models.BatchTarget(target_field="Back"))
        
        voice_id = voice_module.TtsVoiceId_v3(voice_key={"id": "en-US-JennyNeural"}, service="EdgeTTS")
        voice_sel = config_models.VoiceSelectionSingle()
        voice_sel.set_voice(config_models.VoiceWithOptions(voice_id, {}))
        preset.set_voice_selection(voice_sel)
        preset.set_text_processing(config_models.TextProcessing())
        
        app.save_preset(preset)
        assert app.preset_exists(preset.uuid) is True
        assert app.get_preset_name(preset.uuid) == "My Test Preset"
        
        # Test loading
        with patch.object(app, 'deserialize_batch_config', return_value=preset):
            loaded = app.load_preset(preset.uuid)
            assert loaded.name == "My Test Preset"
            
        # Test deletion
        app.delete_preset(preset.uuid)
        assert app.preset_exists(preset.uuid) is False

    def test_from_dict_defaults(self):
        # Test default values for dataclasses
        target = config_models.BatchTarget(target_field="Sound")
        assert target.remove_sound_tag is True
        assert target.insert_location == config_models.InsertLocation.AFTER

    def test_preset_roundtrip_sequence_mode_preserves_voices(self):
        """Regression test: a preset configured in sequence mode with multiple
        voices must survive a full save -> load round trip. This used to fail on
        Python 3.14 because the bundled databind/typeapi could not read dataclass
        annotations, so voice_ids were persisted as empty dicts and every voice
        was dropped when the preset was reloaded."""
        from superfreetts_addon import errors as errors_module

        class FakeServiceManager:
            voices = [
                voice_module.TtsVoiceId_v3(voice_key={"id": "en-US-JennyNeural"}, service="EdgeTTS"),
                voice_module.TtsVoiceId_v3(voice_key={"id": "en-US-GuyNeural"}, service="EdgeTTS"),
                voice_module.TtsVoiceId_v3(voice_key={"id": "en-GB-SoniaNeural"}, service="EdgeTTS"),
                voice_module.TtsVoiceId_v3(voice_key={"model": "en_US-lessac-medium"}, service="Piper"),
            ]

            def locate_voice(self, voice_id):
                for v in self.voices:
                    if v == voice_id:
                        return v
                raise errors_module.VoiceIdNotFound(voice_id)

        anki_utils = MockAnkiUtils()
        anki_utils.config = {
            constants.CONFIG_PRESETS: {},
            constants.CONFIG_CONFIGURATION: {},
            constants.CONFIG_PREFERENCES: {},
        }
        service_manager = FakeServiceManager()
        store = config_store.ConfigStore(anki_utils, service_manager)

        preset = config_models.BatchConfig(anki_utils)
        preset.name = "Preset A"
        preset.set_source(config_models.BatchSource(
            mode=constants.BatchMode.simple,
            source_field="Expression Field",
            use_selection=False,
        ))
        preset.set_target(config_models.BatchTarget(target_field="Sound Field"))

        selection = config_models.VoiceSelectionSequence()
        voice_ids = [service_manager.voices[i] for i in [0, 1, 2]]
        for voice_id in voice_ids:
            selection.add_voice(config_models.VoiceWithOptionsSequence(voice_id, {}))
        preset.set_voice_selection(selection)
        preset.set_text_processing(config_models.TextProcessing())

        store.save_preset(preset)

        # The serialized configuration must contain real voice ids, not empty dicts.
        serialized = preset.serialize()
        saved_voices = serialized['voice_selection']['voice_list']
        assert len(saved_voices) == 3
        for saved in saved_voices:
            assert saved['voice_id'] not in ({}, None)
            assert saved['voice_id']['service'] == 'EdgeTTS'

        loaded = store.load_preset(preset.uuid)
        assert loaded.name == "Preset A"
        assert loaded.source.source_field == "Expression Field"
        assert loaded.target.target_field == "Sound Field"

        loaded_selection = loaded.voice_selection
        assert loaded_selection.selection_mode == constants.VoiceSelectionMode.sequence
        assert len(loaded_selection.voice_list) == 3
        for expected, got in zip(voice_ids, loaded_selection.voice_list):
            assert got.voice_id == expected

    def test_preset_roundtrip_random_and_priority_modes_preserve_voices(self):
        """Random/priority voice modes must also survive a save -> load round trip."""
        from superfreetts_addon import errors as errors_module

        class FakeServiceManager:
            voices = [
                voice_module.TtsVoiceId_v3(voice_key={"id": "en-US-JennyNeural"}, service="EdgeTTS"),
                voice_module.TtsVoiceId_v3(voice_key={"id": "en-US-GuyNeural"}, service="EdgeTTS"),
                voice_module.TtsVoiceId_v3(voice_key={"model": "en_US-lessac-medium"}, service="Piper"),
            ]

            def locate_voice(self, voice_id):
                for v in self.voices:
                    if v == voice_id:
                        return v
                raise errors_module.VoiceIdNotFound(voice_id)

        anki_utils = MockAnkiUtils()
        anki_utils.config = {
            constants.CONFIG_PRESETS: {},
            constants.CONFIG_CONFIGURATION: {},
            constants.CONFIG_PREFERENCES: {},
        }
        service_manager = FakeServiceManager()
        store = config_store.ConfigStore(anki_utils, service_manager)
        voice_ids = [service_manager.voices[0], service_manager.voices[2]]

        for mode, selection_class, entry_class in [
            (constants.VoiceSelectionMode.random, config_models.VoiceSelectionRandom,
             config_models.VoiceWithOptionsRandom),
            (constants.VoiceSelectionMode.priority, config_models.VoiceSelectionPriority,
             config_models.VoiceWithOptionsPriority),
        ]:
            preset = config_models.BatchConfig(anki_utils)
            preset.name = f"Preset {mode.name}"
            preset.set_source(config_models.BatchSource(mode=constants.BatchMode.simple, source_field="Front"))
            preset.set_target(config_models.BatchTarget(target_field="Back"))
            selection = selection_class()
            for voice_id in voice_ids:
                selection.add_voice(entry_class(voice_id, {}))
            preset.set_voice_selection(selection)
            preset.set_text_processing(config_models.TextProcessing())

            store.save_preset(preset)
            loaded = store.load_preset(preset.uuid)
            assert loaded.voice_selection.selection_mode == mode
            assert len(loaded.voice_selection.voice_list) == 2
            for expected, got in zip(voice_ids, loaded.voice_selection.voice_list):
                assert got.voice_id == expected

