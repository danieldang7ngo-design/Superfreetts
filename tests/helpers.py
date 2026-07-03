import os
import sys
import tempfile
import shutil
from unittest.mock import MagicMock
from superfreetts_addon.service import ServiceBase
from superfreetts_addon.voice import TtsVoice_v3, TtsVoiceId_v3
from superfreetts_addon import constants
from superfreetts_addon.languages import AudioLanguage, Language

class FakeService(ServiceBase):
    def __init__(self):
        super().__init__()
        self._voices = []
        # Populate with a default voice
        v = TtsVoice_v3(
            name="FakeVoice",
            voice_key={"id": "fake_voice"},
            options={},
            service="FakeService",
            gender=constants.Gender.Male,
            audio_languages=[AudioLanguage(lang=Language.en, region=None)],
            service_fee=constants.ServiceFee.free
        )
        self._voices.append(v)
        self.fail_count = 0
        self.call_count = 0

    @property
    def service_type(self) -> constants.ServiceType:
        return constants.ServiceType.tts

    @property
    def service_fee(self) -> constants.ServiceFee:
        return constants.ServiceFee.free

    def voice_list(self):
        return self._voices

    def get_tts_audio(self, source_text, voice, options):
        self.call_count += 1
        if self.fail_count > 0:
            self.fail_count -= 1
            raise Exception("FakeService deliberate failure")
        # Return deterministic audio bytes based on text
        return f"audio-for-{source_text}".encode('utf-8')

    def generate_audio(self, source_text, voice, options):
        return self.get_tts_audio(source_text, voice, options)

def FakeServiceVoice(name="FakeVoice", service="FakeService", **kwargs):
    default_kwargs = {
        "name": name,
        "voice_key": {"id": name.lower()},
        "options": {},
        "service": service,
        "gender": constants.Gender.Male,
        "audio_languages": [AudioLanguage(lang=Language.en, region=None)],
        "service_fee": constants.ServiceFee.free
    }
    default_kwargs.update(kwargs)
    return TtsVoice_v3(**default_kwargs)

def make_config_dict(version=7, **overrides):
    # Builds config dicts at any version for migration testing
    # Root keys based on config.json
    config = {
        constants.CONFIG_SCHEMA: version,
        "configuration": {
            "service_enabled": {
                "EdgeTTS": True,
                "FakeService": True
            },
            "service_config": {
                "EdgeTTS": {
                    "concurrency_workers": 20
                }
            },
            "display_introduction_message": True
        },
        "preferences": {
            "ui_language": "vi",
            "cache_enabled": True
        },
        constants.CONFIG_PRESETS: {},
        constants.CONFIG_MAPPING_RULES: {
            "rules": []
        },
        "batch_config": {},
        "realtime_config": {},
        "default_presets": {}
    }
    config.update(overrides)
    return config

class TempMediaDir:
    def __init__(self):
        self.path = None

    def __enter__(self):
        self.path = tempfile.mkdtemp()
        return self.path

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.path and os.path.exists(self.path):
            shutil.rmtree(self.path)
