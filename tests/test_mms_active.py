import sys
import os
import pytest
from unittest.mock import MagicMock

# Setup mock environment similar to conftest.py
mock_anki = MagicMock()
mock_aqt = MagicMock()
sys.modules['anki'] = mock_anki
sys.modules['anki.hooks'] = MagicMock()
sys.modules['anki.sound'] = MagicMock()
sys.modules['aqt'] = mock_aqt
sys.modules['aqt.gui_hooks'] = MagicMock()
sys.modules['aqt.qt'] = MagicMock()
sys._pytest_mode = True

# Add paths
addon_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, addon_dir)
sys.path.insert(0, os.path.join(addon_dir, 'external'))

from superfreetss_addon.services import service_mms
from superfreetss_addon import voice
from superfreetss_addon import constants
from superfreetss_addon import languages

def test_mms_english_generation():
    """Verify that MMS can generate English audio"""
    mms = service_mms.MmsTTS()
    
    # Check if eng voice is in the list
    voices = mms.voice_list()
    eng_voice = next((v for v in voices if "eng" in v.voice_key), None)
    
    if not eng_voice:
        pytest.skip("English MMS model not found in voice list")
    
    print(f"Testing with voice: {eng_voice.name} ({eng_voice.voice_key})")
    
    # Generate audio
    text = "This is a test of the Meta Multi-Speaker Text-to-Speech system."
    audio_data = mms.get_tts_audio(text, eng_voice, {})
    
    assert audio_data is not None
    assert len(audio_data) > 0
    print(f"Success! Generated {len(audio_data)} bytes of audio.")

if __name__ == "__main__":
    # Allow manual run
    import pytest
    pytest.main([__file__, "-s"])
