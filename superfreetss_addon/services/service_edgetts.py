import sys
import io
import asyncio
import threading
import edge_tts
from typing import List

from superfreetss_addon import voice
from superfreetss_addon import service
from superfreetss_addon import errors
from superfreetss_addon import constants
from superfreetss_addon import languages
from superfreetss_addon import logging_utils

logger = logging_utils.get_child_logger(__name__)

class EdgeLoopManager:
    def __init__(self):
        self._loop = None
        self._thread = None
        self._lock = threading.Lock()

    def get_loop(self):
        with self._lock:
            if self._loop is None:
                self._loop = asyncio.new_event_loop()
                self._thread = threading.Thread(target=self._run_loop, daemon=True)
                self._thread.start()
            return self._loop

    def _run_loop(self):
        asyncio.set_event_loop(self._loop)
        self._loop.run_forever()

_edge_manager = EdgeLoopManager()

class EdgeTTS(service.ServiceBase):
    def __init__(self):
        service.ServiceBase.__init__(self)

    @property
    def service_type(self) -> constants.ServiceType:
        return constants.ServiceType.tts

    @property
    def service_fee(self) -> constants.ServiceFee:
        return constants.ServiceFee.free

    def configuration_options(self):
        return {}

    def voice_list(self) -> List[voice.TtsVoice_v3]:
        # Fetching voices still uses a temporary loop for simplicity in this sync call
        try:
            loop = asyncio.new_event_loop()
            try:
                voices_data = loop.run_until_complete(edge_tts.VoicesManager.create())
            finally:
                loop.close()

            voices = []
            for v in voices_data.voices:
                # Map EdgeTTS locale to AudioLanguage
                lang_key = v['Locale'].replace('-', '_')
                audio_lang = None
                try:
                    audio_lang = languages.AudioLanguage[lang_key]
                except KeyError:
                    # Fuzzy matching
                    for al in languages.AudioLanguage:
                        if al.name.startswith(v['Locale'].split('-')[0]):
                            audio_lang = al
                            break
                
                if audio_lang:
                    gender = constants.Gender.Male if v['Gender'] == 'Male' else constants.Gender.Female
                    voices.append(voice.build_voice_v3(
                        name=v['FriendlyName'],
                        gender=gender,
                        language=audio_lang,
                        service=self,
                        voice_key=v['ShortName'],
                        options={}
                    ))
            return voices
        except Exception as e:
            logger.error(f"EdgeTTS: Error fetching voice list: {e}")
            return []

    def get_tts_audio(self, source_text, voice: voice.TtsVoice_v3, options):
        try:
            loop = _edge_manager.get_loop()
            audio_data = io.BytesIO()
            
            async def _stream():
                communicate = edge_tts.Communicate(source_text, voice.voice_key)
                async for chunk in communicate.stream():
                    if chunk["type"] == "audio":
                        audio_data.write(chunk["data"])

            # Run in the persistent background loop
            future = asyncio.run_coroutine_threadsafe(_stream(), loop)
            # Wait for completion (with timeout)
            future.result(timeout=30)
                
            return audio_data.getvalue()
        except Exception as e:
            logger.warning(f'EdgeTTS: exception while retrieving sound for {source_text}: {e}')
            raise errors.RequestError(source_text, voice, str(e))
