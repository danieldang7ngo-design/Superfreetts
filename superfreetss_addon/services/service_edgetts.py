import os
import sys
import io
import asyncio
import threading
import time
import edge_tts
from typing import List, Optional

from .. import voice
from .. import service
from .. import errors
from .. import constants
from .. import languages
from .. import logging_utils

logger = logging_utils.get_child_logger(__name__)

def run_async_safe(coro):
    """
    Safely run an asyncio coroutine from a synchronous context.
    Works whether or not an event loop is already running in the current thread.
    """
    try:
        # Check if there's a running loop in the current thread
        asyncio.get_running_loop()
        # If yes, we can't use asyncio.run() or run_until_complete() here.
        # We run it in a separate thread with its own loop to avoid blocking/crashing.
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            return executor.submit(asyncio.run, coro).result()
    except RuntimeError:
        # No loop running in this thread, safe to use asyncio.run()
        return asyncio.run(coro)

class EdgeTTS(service.ServiceBase):
    def __init__(self):
        service.ServiceBase.__init__(self)

    @property
    def service_type(self) -> constants.ServiceType:
        return constants.ServiceType.tts

    @property
    def service_fee(self) -> constants.ServiceFee:
        return constants.ServiceFee.free

    def enabled_by_default(self):
        return True

    def configuration_options(self):
        return {}

    def advanced_configuration_options(self):
        """Advanced settings for EdgeTTS (hidden in dropdown)"""
        from .. import cpu_utils
        return {
            'concurrency_workers': ('number', 'Concurrency Workers (1-N)', 1, 1, cpu_utils.CPUInfo.get_max_workers()),
            'debug_logging': ('bool', 'Enable Debug Logging for EdgeTTS', False)
        }

    def voice_list(self) -> List[voice.TtsVoice_v3]:
        # Use run_async_safe to avoid loop conflicts
        try:
            voices_data = run_async_safe(edge_tts.VoicesManager.create())

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
                    voice_options = {
                        'speed': {
                            'type': 'number_int', 'default': 0, 'min': -50, 'max': 50,
                            'label': 'Speed %',
                            'tooltip': 'Speaking rate adjustment. 0 = normal, +50 = 50% faster, -50 = 50% slower'
                        },
                        'pitch': {
                            'type': 'number_int', 'default': 0, 'min': -50, 'max': 50,
                            'label': 'Pitch (Hz)',
                            'tooltip': 'Voice pitch adjustment in Hz. 0 = normal, +50 = higher pitch, -50 = lower pitch'
                        },
                        'volume': {
                            'type': 'number_int', 'default': 0, 'min': -50, 'max': 50,
                            'label': 'Volume %',
                            'tooltip': 'Volume adjustment. 0 = normal, +50 = 50% louder, -50 = 50% quieter'
                        },
                    }
                    voices.append(voice.build_voice_v3(
                        name=v['FriendlyName'],
                        gender=gender,
                        language=audio_lang,
                        service=self,
                        voice_key=v['ShortName'],
                        options=voice_options
                    ))
            return voices
        except Exception as e:
            logger.error(f"EdgeTTS: Error fetching voice list: {e}")
            return []

    def get_tts_audio(self, source_text, voice: voice.TtsVoice_v3, options):
        # Implementation for single request
        results = self.get_tts_audio_batch([source_text], voice, options)
        if results and results[0]:
            return results[0]
        raise errors.RequestError(source_text, voice, "EdgeTTS failed to generate audio")

    def get_tts_audio_batch(self, source_texts: List[str], voice: voice.TtsVoice_v3, options: dict) -> List[Optional[bytes]]:
        """
        Synthesize multiple texts in a single asyncio event loop using gather().
        This is much faster than running multiple sequential or even multi-threaded 
        asyncio.run() calls because it reuses loop overhead.
        """
        if not source_texts:
            return []

        debug_enabled = self.get_configuration_value_optional('debug_logging', False)
        
        async def _stream_batch():
            speed_val = options.get('speed', 0)
            pitch_val = options.get('pitch', 0)
            volume_val = options.get('volume', 0)
            rate_str = f"{'+' if speed_val >= 0 else ''}{speed_val}%"
            pitch_str = f"{'+' if pitch_val >= 0 else ''}{pitch_val}Hz"
            volume_str = f"{'+' if volume_val >= 0 else ''}{volume_val}%"
            
            async def _fetch_one(text):
                try:
                    if debug_enabled:
                         logger.debug(f"EdgeTTS: Starting synthesis for '{text[:20]}...'")
                    
                    communicate = edge_tts.Communicate(
                        text, voice.voice_key,
                        rate=rate_str, pitch=pitch_str, volume=volume_str
                    )
                    data = b""
                    async for chunk in communicate.stream():
                        if chunk["type"] == "audio":
                            data += chunk["data"]
                    return data
                except Exception as e:
                    logger.warning(f"EdgeTTS Batch: Exception for text '{text[:20]}...': {e}")
                    return None

            # Execute all requests in parallel within the SAME event loop
            tasks = [_fetch_one(text) for text in source_texts]
            return await asyncio.gather(*tasks)

        try:
            start_time = time.time()
            results = run_async_safe(_stream_batch())
            
            if debug_enabled:
                duration = time.time() - start_time
                success_count = sum(1 for r in results if r is not None)
                try:
                    from .. import service_logger
                    service_logger.write_log('edgetts', 'runtime', 'OK', 'Batch generated', {
                        'Count': f'{success_count}/{len(source_texts)}',
                        'Duration': f'{duration:.2f}s'
                    })
                except: pass
            
            return results
        except Exception as e:
            logger.error(f"EdgeTTS: Batch execution failed: {e}")
            return [None] * len(source_texts)
