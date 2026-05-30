"""
Unit tests for constants module.
"""

import pytest
import sys
import os

addon_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, addon_dir)

from superfreetts_addon import constants


@pytest.mark.unit
class TestEnums:
    """Test enum definitions"""
    
    def test_service_type_values(self):
        """Verify ServiceType enum has expected values"""
        assert hasattr(constants.ServiceType, 'tts')
        assert hasattr(constants.ServiceType, 'dictionary')
    
    def test_service_fee_values(self):
        """Verify ServiceFee enum has free and paid"""
        assert hasattr(constants.ServiceFee, 'free')
        assert hasattr(constants.ServiceFee, 'paid')
    
    def test_batch_mode_values(self):
        """Verify BatchMode enum exists"""
        assert hasattr(constants.BatchMode, 'simple')
        assert hasattr(constants.BatchMode, 'template')
    
    def test_gender_enum(self):
        """Verify Gender enum"""
        assert hasattr(constants.Gender, 'Male')
        assert hasattr(constants.Gender, 'Female')
    
    def test_template_format_version(self):
        """Verify TemplateFormatVersion enum"""
        assert hasattr(constants.TemplateFormatVersion, 'v1')


@pytest.mark.unit
class TestConstants:
    """Test constant values"""
    
    def test_config_addon_name_exists(self):
        """Verify CONFIG_ADDON_NAME is defined"""
        assert hasattr(constants, 'CONFIG_ADDON_NAME')
        assert isinstance(constants.CONFIG_ADDON_NAME, str)
        assert len(constants.CONFIG_ADDON_NAME) > 0
    
    def test_stylesheet_exists(self):
        """Verify stylesheet constant exists"""
        assert hasattr(constants, 'STYLESHEET_DIALOG')
        assert isinstance(constants.STYLESHEET_DIALOG, str)
