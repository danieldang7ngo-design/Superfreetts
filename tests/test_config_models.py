"""
Unit tests for config models.
"""

import pytest
import sys
import os

addon_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, addon_dir)

from superfreetss_addon import config_models
from superfreetss_addon import constants
from superfreetss_addon import errors
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
