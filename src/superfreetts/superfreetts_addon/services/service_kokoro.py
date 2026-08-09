import sys
import os
import subprocess
import json
import io
import threading
import time
from typing import List, Optional

from .. import voice
from .. import service
from .. import errors
from .. import constants
from .. import languages
from .. import logging_utils

logger = logging_utils.get_child_logger(__name__)

from .service_mms import SherpaProcessPool
_kokoro_pool = SherpaProcessPool("Kokoro", max_processes=2)

# Standard Voices included in the 35MB Official v1.0 Bundle
KOKORO_V10_VOICES = [
    # American English (af, am)
    {"key": "af_alloy", "name": "Alloy (American Female)", "lang": languages.AudioLanguage.en_US, "gender": constants.Gender.Female},
    {"key": "af_aoede", "name": "Aoede (American Female)", "lang": languages.AudioLanguage.en_US, "gender": constants.Gender.Female},
    {"key": "af_bella", "name": "Bella (American Female)", "lang": languages.AudioLanguage.en_US, "gender": constants.Gender.Female},
    {"key": "af_heart", "name": "Heart (American Female)", "lang": languages.AudioLanguage.en_US, "gender": constants.Gender.Female},
    {"key": "af_jessica", "name": "Jessica (American Female)", "lang": languages.AudioLanguage.en_US, "gender": constants.Gender.Female},
    {"key": "af_kore", "name": "Kore (American Female)", "lang": languages.AudioLanguage.en_US, "gender": constants.Gender.Female},
    {"key": "af_nicole", "name": "Nicole (American Female)", "lang": languages.AudioLanguage.en_US, "gender": constants.Gender.Female},
    {"key": "af_nova", "name": "Nova (American Female)", "lang": languages.AudioLanguage.en_US, "gender": constants.Gender.Female},
    {"key": "af_river", "name": "River (American Female)", "lang": languages.AudioLanguage.en_US, "gender": constants.Gender.Female},
    {"key": "af_sarah", "name": "Sarah (American Female)", "lang": languages.AudioLanguage.en_US, "gender": constants.Gender.Female},
    {"key": "af_sky", "name": "Sky (American Female)", "lang": languages.AudioLanguage.en_US, "gender": constants.Gender.Female},
    {"key": "am_adam", "name": "Adam (American Male)", "lang": languages.AudioLanguage.en_US, "gender": constants.Gender.Male},
    {"key": "am_echo", "name": "Echo (American Male)", "lang": languages.AudioLanguage.en_US, "gender": constants.Gender.Male},
    {"key": "am_eric", "name": "Eric (American Male)", "lang": languages.AudioLanguage.en_US, "gender": constants.Gender.Male},
    {"key": "am_fenrir", "name": "Fenrir (American Male)", "lang": languages.AudioLanguage.en_US, "gender": constants.Gender.Male},
    {"key": "am_liam", "name": "Liam (American Male)", "lang": languages.AudioLanguage.en_US, "gender": constants.Gender.Male},
    {"key": "am_michael", "name": "Michael (American Male)", "lang": languages.AudioLanguage.en_US, "gender": constants.Gender.Male},
    {"key": "am_onyx", "name": "Onyx (American Male)", "lang": languages.AudioLanguage.en_US, "gender": constants.Gender.Male},
    {"key": "am_puck", "name": "Puck (American Male)", "lang": languages.AudioLanguage.en_US, "gender": constants.Gender.Male},
    {"key": "am_santa", "name": "Santa (American Male)", "lang": languages.AudioLanguage.en_US, "gender": constants.Gender.Male},
    
    # British English (bf, bm)
    {"key": "bf_alice", "name": "Alice (British Female)", "lang": languages.AudioLanguage.en_GB, "gender": constants.Gender.Female},
    {"key": "bf_emma", "name": "Emma (British Female)", "lang": languages.AudioLanguage.en_GB, "gender": constants.Gender.Female},
    {"key": "bf_isabella", "name": "Isabella (British Female)", "lang": languages.AudioLanguage.en_GB, "gender": constants.Gender.Female},
    {"key": "bf_lily", "name": "Lily (British Female)", "lang": languages.AudioLanguage.en_GB, "gender": constants.Gender.Female},
    {"key": "bm_daniel", "name": "Daniel (British Male)", "lang": languages.AudioLanguage.en_GB, "gender": constants.Gender.Male},
    {"key": "bm_fable", "name": "Fable (British Male)", "lang": languages.AudioLanguage.en_GB, "gender": constants.Gender.Male},
    {"key": "bm_george", "name": "George (British Male)", "lang": languages.AudioLanguage.en_GB, "gender": constants.Gender.Male},
    {"key": "bm_lewis", "name": "Lewis (British Male)", "lang": languages.AudioLanguage.en_GB, "gender": constants.Gender.Male},

    # Spanish (ef, em)
    {"key": "ef_dora", "name": "Dora (Spanish Female)", "lang": languages.AudioLanguage.es_ES, "gender": constants.Gender.Female},
    {"key": "em_alex", "name": "Alex (Spanish Male)", "lang": languages.AudioLanguage.es_ES, "gender": constants.Gender.Male},
    {"key": "em_santa", "name": "Santa (Spanish Male)", "lang": languages.AudioLanguage.es_ES, "gender": constants.Gender.Male},

    # French (ff)
    {"key": "ff_siwis", "name": "Siwis (French Female)", "lang": languages.AudioLanguage.fr_FR, "gender": constants.Gender.Female},

    # Hindi (hf, hm)
    {"key": "hf_alpha", "name": "Alpha (Hindi Female)", "lang": languages.AudioLanguage.hi_IN, "gender": constants.Gender.Female},
    {"key": "hf_beta", "name": "Beta (Hindi Female)", "lang": languages.AudioLanguage.hi_IN, "gender": constants.Gender.Female},
    {"key": "hm_omega", "name": "Omega (Hindi Male)", "lang": languages.AudioLanguage.hi_IN, "gender": constants.Gender.Male},
    {"key": "hm_psi", "name": "Psi (Hindi Male)", "lang": languages.AudioLanguage.hi_IN, "gender": constants.Gender.Male},

    # Italian (if, im)
    {"key": "if_sara", "name": "Sara (Italian Female)", "lang": languages.AudioLanguage.it_IT, "gender": constants.Gender.Female},
    {"key": "im_nicola", "name": "Nicola (Italian Male)", "lang": languages.AudioLanguage.it_IT, "gender": constants.Gender.Male},

    # Japanese (jf, jm)
    {"key": "jf_alpha", "name": "Alpha (Japanese Female)", "lang": languages.AudioLanguage.ja_JP, "gender": constants.Gender.Female},
    {"key": "jf_gongitsune", "name": "Gongitsune (Japanese Female)", "lang": languages.AudioLanguage.ja_JP, "gender": constants.Gender.Female},
    {"key": "jf_nezumi", "name": "Nezumi (Japanese Female)", "lang": languages.AudioLanguage.ja_JP, "gender": constants.Gender.Female},
    {"key": "jf_tebukuro", "name": "Tebukuro (Japanese Female)", "lang": languages.AudioLanguage.ja_JP, "gender": constants.Gender.Female},
    {"key": "jm_kumo", "name": "Kumo (Japanese Male)", "lang": languages.AudioLanguage.ja_JP, "gender": constants.Gender.Male},

    # Portuguese (pf, pm)
    {"key": "pf_dora", "name": "Dora (Portuguese Female)", "lang": languages.AudioLanguage.pt_BR, "gender": constants.Gender.Female},
    {"key": "pm_alex", "name": "Alex (Portuguese Male)", "lang": languages.AudioLanguage.pt_BR, "gender": constants.Gender.Male},
    {"key": "pm_santa", "name": "Santa (Portuguese Male)", "lang": languages.AudioLanguage.pt_BR, "gender": constants.Gender.Male},

    # Chinese (zf, zm)
    {"key": "zf_xiaobei", "name": "Xiaobei (Chinese Female)", "lang": languages.AudioLanguage.zh_CN, "gender": constants.Gender.Female},
    {"key": "zf_xiaoni", "name": "Xiaoni (Chinese Female)", "lang": languages.AudioLanguage.zh_CN, "gender": constants.Gender.Female},
    {"key": "zf_xiaoxiao", "name": "Xiaoxiao (Chinese Female)", "lang": languages.AudioLanguage.zh_CN, "gender": constants.Gender.Female},
    {"key": "zf_xiaoyi", "name": "Xiaoyi (Chinese Female)", "lang": languages.AudioLanguage.zh_CN, "gender": constants.Gender.Female},
    {"key": "zm_yunjian", "name": "Yunjian (Chinese Male)", "lang": languages.AudioLanguage.zh_CN, "gender": constants.Gender.Male},
    {"key": "zm_yunxi", "name": "Yunxi (Chinese Male)", "lang": languages.AudioLanguage.zh_CN, "gender": constants.Gender.Male},
    {"key": "zm_yunxia", "name": "Yunxia (Chinese Male)", "lang": languages.AudioLanguage.zh_CN, "gender": constants.Gender.Male},
    {"key": "zm_yunyang", "name": "Yunyang (Chinese Male)", "lang": languages.AudioLanguage.zh_CN, "gender": constants.Gender.Male},
]

class KokoroTTS(service.ServiceBase):
    CONFIG_ENGINE_PATH = 'engine_path' # Path to python.exe of the portable environment

    def __init__(self):
        service.ServiceBase.__init__(self)
        # Extreme Optimization: Eager warmup of a Kokoro process
        threading.Thread(target=self._low_priority_warmup, daemon=True).start()

    def _low_priority_warmup(self):
        # Wait a bit for Anki to settle
        time.sleep(2)
        try:
            from aqt import mw
            engine_path = self.get_configuration_value_optional(self.CONFIG_ENGINE_PATH, '')
            # If user didn't configure an engine path, fall back to the packaged engine if present
            if not engine_path:
                possible = os.path.join(constants.KOKORO_ENGINE_DIR, 'python.exe')
                if os.path.exists(possible):
                    engine_path = possible

            if engine_path and os.path.exists(engine_path):
                script_path = os.path.join(os.path.dirname(__file__), 'kokoro_runner.py')
                # Ensure hyper_tts is initialized
                if not hasattr(mw, "hyper_tts") or not mw.hyper_tts:
                    return
                
                installed = self.voice_list()
                if not installed or installed[0].voice_key == "none":
                    return

                process = _kokoro_pool.get_process(engine_path, script_path, debug_enabled=True)
                _kokoro_pool.release_process(process, engine_path, script_path)
        except Exception as e:
                logger.warning(f"Kokoro warmup failed: {e}")

    @property
    def name(self):
        return "KokoroTTS"

    @property
    def display_name(self):
        return "Kokoro (High Fidelity)"

    @property
    def service_type(self) -> constants.ServiceType:
        return constants.ServiceType.tts

    @property
    def service_fee(self) -> constants.ServiceFee:
        return constants.ServiceFee.free
        
    def cloudlanguagetools_enabled(self):
        return False

    def enabled_by_default(self):
        return True

    def configuration_options(self):
        return {
            self.CONFIG_ENGINE_PATH: ('file', 'Kokoro path', 'Executable (python.exe);;All Files (*)'),
        }
    
    def advanced_configuration_options(self):
        """Advanced settings for power users (hidden in dropdown)"""
        from .. import system_utils
        return {
            'num_threads': ('number', 'CPU Threads (0=Auto/Serial)', 1, 0, system_utils.get_total_cpu_count()),
            'concurrency_workers': ('number', 'Concurrency Workers (1-N)', 1, 1, system_utils.get_max_workers()),
            'debug_logging': ('bool', 'Enable Debug Logging', False),
        }

    def voice_list(self) -> List[voice.TtsVoice_v3]:
        from ..constants import KOKORO_ENGINE_DIR
        models_dir = os.path.join(KOKORO_ENGINE_DIR, "models")
        voices_bundle = os.path.join(models_dir, "voices-v1.0.bin")
        
        # If the official bundle doesn't exist, we show nothing (except a placeholder)
        if not os.path.exists(voices_bundle):
            return [voice.build_voice_v3(
                name="Kokoro - Model/Voices not installed",
                gender=constants.Gender.Any,
                language=languages.AudioLanguage.en_US,
                service=self,
                voice_key="none",
                options={}
            )]

        installed_voices = []
        for v in KOKORO_V10_VOICES:
            voice_options = {
                'speed': {
                    'type': 'number', 'default': 1.0, 'min': 0.5, 'max': 2.0,
                    'label': 'Speed',
                    'tooltip': 'Speed multiplier. 1.0 = normal, 2.0 = 2x faster, 0.5 = 2x slower'
                },
            }
            installed_voices.append(voice.build_voice_v3(
                name=f"Kokoro - {v['name']}",
                gender=v['gender'],
                language=v['lang'],
                service=self,
                voice_key=v['key'],
                options=voice_options
            ))
            
        return installed_voices

    def get_tts_audio(self, source_text, voice: voice.TtsVoice_v3, options):
        engine_path = self.get_configuration_value_optional(self.CONFIG_ENGINE_PATH, '')
        # If not explicitly configured, try packaged engine
        if not engine_path:
            possible = os.path.join(constants.KOKORO_ENGINE_DIR, 'python.exe')
            if os.path.exists(possible):
                engine_path = possible

        if not engine_path or not os.path.exists(engine_path):
             raise errors.RequestError(source_text, voice, "Kokoro engine not configured.")
             
        debug_enabled = self.get_configuration_value_optional('debug_logging', False)

        if debug_enabled:
            try:
                from .. import service_logger
                service_logger.write_log('kokoro', 'runtime', 'INFO', 'TTS Request', {
                    'Voice': voice.voice_key,
                    'Text': f'"{source_text[:50]}..." ({len(source_text)} chars)'
                })
            except Exception as e:
                logger.warning(f"Debug logging setup failed: {e}")

        for attempt in [1, 2]:
            try:
                # Get process from pool
                script_path = os.path.join(os.path.dirname(__file__), 'kokoro_runner.py')
                process = _kokoro_pool.get_process(engine_path, script_path, debug_enabled=debug_enabled)
                
                try:
                    threads_opt = self.get_configuration_value_optional('num_threads', 1)
                    if threads_opt <= 0:
                        threads_opt = 1

                    request = {
                        "text": source_text.strip(),
                        "voice": voice.voice_key,
                        "output_file": "MEMORY", 
                        "threads": int(threads_opt),
                        "speed": options.get('speed', 1.0),
                    }
                    payload = json.dumps(request) + "\n"
                    
                    process.stdin.write(payload.encode('utf-8'))
                    process.stdin.flush()
                    
                    response_line = process.stdout.readline()
                    if not response_line:
                        raise BrokenPipeError("Kokoro process closed stream.")
                    
                    resp_text = response_line.decode('utf-8', errors='replace').strip()
                    try:
                        resp = json.loads(resp_text)
                    except Exception:
                        raise Exception(f"Invalid JSON from Kokoro: {resp_text}")

                    if resp.get("status") == "ok":
                        import base64
                        audio_b64 = resp.get("audio_b64")
                        if audio_b64:
                            return base64.b64decode(audio_b64)
                        else:
                            raise Exception("No audio data in Kokoro response.")
                    else:
                        raise Exception(f"Kokoro Error: {resp.get('message')}")
                        
                except (BrokenPipeError, ConnectionResetError, EOFError) as e:
                    process.is_healthy = False
                    if attempt == 1:
                        logger.warning(f"KokoroTTS: Retry 1/1 after process failure: {e}")
                        continue
                    raise e
                finally:
                    _kokoro_pool.release_process(process, engine_path, script_path)
            except Exception as e:
                if attempt == 2:
                    logger.warning(f"Exception while generating kokoro audio (persistent): {e}")
                    raise errors.RequestError(source_text, voice, str(e))

    def get_tts_audio_batch(self, source_texts: List[str], voice: voice.TtsVoice_v3, options: dict) -> List[Optional[bytes]]:
        engine_path = self.get_configuration_value_optional(self.CONFIG_ENGINE_PATH, '')
        if not engine_path:
            possible = os.path.join(constants.KOKORO_ENGINE_DIR, 'python.exe')
            if os.path.exists(possible):
                engine_path = possible

        if not engine_path or not os.path.exists(engine_path):
             return [None] * len(source_texts)
             
        debug_enabled = self.get_configuration_value_optional('debug_logging', False)
        for attempt in [1, 2]:
            try:
                # Get process from pool
                script_path = os.path.join(os.path.dirname(__file__), 'kokoro_runner.py')
                process = _kokoro_pool.get_process(engine_path, script_path, debug_enabled=debug_enabled)
                
                try:
                    tasks = []
                    for text in source_texts:
                        tasks.append({
                            "text": text,
                            "voice": voice.voice_key,
                            "speed": options.get('speed', 1.0)
                        })
                    
                    threads_opt = self.get_configuration_value_optional('num_threads', 1)
                    if threads_opt <= 0:
                        threads_opt = 1

                    request = {
                        "action": "generate_batch",
                        "tasks": tasks,
                        "threads": int(threads_opt),
                    }
                    payload = json.dumps(request) + "\n"
                    process.stdin.write(payload.encode('utf-8'))
                    process.stdin.flush()
                    
                    response_line = process.stdout.readline()
                    if not response_line:
                        raise BrokenPipeError("Kokoro process closed stream.")
                    
                    resp_data = response_line.decode('utf-8', errors='replace').strip()
                    try:
                        resp = json.loads(resp_data)
                    except Exception:
                        raise Exception(f"Invalid JSON from Kokoro: {resp_data}")

                    if resp.get("status") == "ok":
                        import base64
                        results = []
                        for item in resp.get("results", []):
                            if item.get("status") == "ok" and item.get("audio_b64"):
                                results.append(base64.b64decode(item["audio_b64"]))
                            else:
                                results.append(None)
                        return results
                    else:
                        raise Exception(f"Kokoro batch Error: {resp.get('message')}")
                
                except (BrokenPipeError, ConnectionResetError, EOFError) as e:
                    process.is_healthy = False
                    if attempt == 1:
                        logger.warning(f"Kokoro Batch: Retry 1/1 after process failure: {e}")
                        continue
                    raise e
                finally:
                    _kokoro_pool.release_process(process, engine_path, script_path)
                    
            except Exception as e:
                if attempt == 2:
                    logger.warning(f"Exception while generating kokoro audio batch (persistent): {e}")
                    return [None] * len(source_texts)
