"""
Unit tests for voice module.
"""

import pytest
import sys
import os
from unittest.mock import Mock

addon_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, addon_dir)

from superfreetss_addon import voice
from superfreetss_addon import constants
from superfreetss_addon import languages


@pytest.mark.unit
class TestVoiceGeneration:
    """Test voice creation and serialization"""
    
    def test_build_voice_v3_basic(self):
        """Test basic voice creation"""
        mock_service = Mock()
        mock_service.name = "EdgeTTS"
        mock_service.service_fee = constants.ServiceFee.free
        
        test_voice = voice.build_voice_v3(
            name="Test Voice",
            gender=constants.Gender.Male,
            language=languages.AudioLanguage.en_US,
            service=mock_service,
            voice_key="test-key",
            options={}
        )
        
        assert test_voice is not None
        assert test_voice.name == "Test Voice"
        assert test_voice.gender == constants.Gender.Male
        assert languages.AudioLanguage.en_US in test_voice.audio_languages
    
    def test_build_voice_v3_with_options(self):
        """Test voice creation with options"""
        mock_service = Mock()
        mock_service.name = "PiperTTS"
        mock_service.service_fee = constants.ServiceFee.free
        
        options = {"pitch": "normal", "speed": 1.0}
        test_voice = voice.build_voice_v3(
            name="Voice with Options",
            gender=constants.Gender.Female,
            language=languages.AudioLanguage.vi_VN,
            service=mock_service,
            voice_key="vi-vn-female",
            options=options
        )
        
        assert test_voice.options == options
        assert languages.AudioLanguage.vi_VN in test_voice.audio_languages


@pytest.mark.unit
class TestVoiceId:
    """Test voice ID handling"""
    
    def test_voice_id_creation(self):
        """Test creating voice IDs"""
        voice_id = voice.TtsVoiceId_v3(
            service="EdgeTTS",
            voice_key="en-US-AriaNeural"
        )
        
        assert voice_id.service == "EdgeTTS"
        assert voice_id.voice_key == "en-US-AriaNeural"


@pytest.mark.unit
class TestVoiceStringRepresentation:
    """Test voice string formatting"""
    
    def test_voice_str_function(self):
        """Test voice_str() function"""
        test_voice = voice.TtsVoice_v3(
            name="English Female",
            gender=constants.Gender.Female,
            audio_languages=[languages.AudioLanguage.en_US],
            service="EdgeTTS",
            voice_key={"test": "key"},
            service_fee=constants.ServiceFee.free,
            options={}
        )
        
        voice_string = voice.voice_str(test_voice)
        assert isinstance(voice_string, str)
        assert len(voice_string) > 0
