"""
Unit tests for voice module.
"""

import pytest
import sys
import os

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
        test_voice = voice.build_voice_v3(
            name="Test Voice",
            gender=constants.Gender.Male,
            language=languages.AudioLanguage.en_US,
            service=None,
            voice_key="test-key",
            options={}
        )
        
        assert test_voice is not None
        assert test_voice.name == "Test Voice"
        assert test_voice.gender == constants.Gender.Male
        assert test_voice.language == languages.AudioLanguage.en_US
    
    def test_build_voice_v3_with_options(self):
        """Test voice creation with options"""
        options = {"pitch": "normal", "speed": 1.0}
        test_voice = voice.build_voice_v3(
            name="Voice with Options",
            gender=constants.Gender.Female,
            language=languages.AudioLanguage.vi_VN,
            service=None,
            voice_key="vi-vn-female",
            options=options
        )
        
        assert test_voice.options == options


@pytest.mark.unit
class TestVoiceId:
    """Test voice ID handling"""
    
    def test_voice_id_creation(self):
        """Test creating voice IDs"""
        voice_id = voice.TtsVoiceId_v3(
            service_name="EdgeTTS",
            language=languages.AudioLanguage.en_US,
            voice_key="en-US-AriaNeural"
        )
        
        assert voice_id.service_name == "EdgeTTS"
        assert voice_id.language == languages.AudioLanguage.en_US
        assert voice_id.voice_key == "en-US-AriaNeural"


@pytest.mark.unit
class TestVoiceStringRepresentation:
    """Test voice string formatting"""
    
    def test_voice_str_function(self):
        """Test voice_str() function"""
        test_voice = voice.TtsVoice_v3(
            name="English Female",
            gender=constants.Gender.Female,
            language=languages.AudioLanguage.en_US,
            service=None,
            voice_id=voice.TtsVoiceId_v3(
                service_name="EdgeTTS",
                language=languages.AudioLanguage.en_US,
                voice_key="en-US-AriaNeural"
            ),
            options={}
        )
        
        voice_string = voice.voice_str(test_voice)
        assert isinstance(voice_string, str)
        assert len(voice_string) > 0
