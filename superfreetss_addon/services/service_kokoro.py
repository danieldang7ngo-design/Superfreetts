
import sys
import os
import subprocess
import json
import io
import threading
import time
from typing import List, Optional

from superfreetss_addon import voice
from superfreetss_addon import service
from superfreetss_addon import errors
from superfreetss_addon import constants
from superfreetss_addon import languages
from superfreetss_addon import logging_utils

logger = logging_utils.get_child_logger(__name__)

class KokoroProcessManager:
    def __init__(self):
        self._process = None
        self._current_engine_path = None
        self._lock = threading.Lock()
        self._timer = None
        self._timeout = 120 # 2 minutes

    def get_process(self, executable_path):
        with self._lock:
            # If binary changed, kill existing process
            if self._process and self._current_engine_path != executable_path:
                self.stop_locked()
            
            # Start process if not running
            if self._process is None or self._process.poll() is not None:
                startupinfo = None
                if os.name == 'nt':
                    startupinfo = subprocess.STARTUPINFO()
                    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                
                # Executable path points to python.exe in the portable folder
                # We expect kokoro_runner.py to be in the same services folder as this file
                script_path = os.path.join(os.path.dirname(__file__), 'kokoro_runner.py')
                
                cwd = os.path.dirname(executable_path)
                cmd = [executable_path, script_path]
                
                logger.info(f"Starting persistent Kokoro process: {' '.join(cmd)}")
                self._process = subprocess.Popen(
                    cmd,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    startupinfo=startupinfo,
                    cwd=cwd, # Run in the context of the portable python to find dependencies
                    bufsize=1, 
                    text=False
                )
                self._current_engine_path = executable_path
                
                # Drain stderr
                def drain_stderr(pipe):
                    try:
                        while True:
                            line = pipe.readline()
                            if not line: break
                            logger.debug(f"Kokoro Stderr: {line.decode('utf-8', errors='ignore').strip()}")
                    except: pass
                
                t = threading.Thread(target=drain_stderr, args=(self._process.stderr,), daemon=True)
                t.start()

            self._reset_timer_locked()
            return self._process

    def _reset_timer_locked(self):
        if self._timer:
            self._timer.cancel()
        self._timer = threading.Timer(self._timeout, self.stop)
        self._timer.start()

    def stop(self):
        with self._lock:
            self.stop_locked()

    def stop_locked(self):
        if self._process:
            logger.info(f"Stopping persistent Kokoro process")
            try:
                self._process.stdin.close()
                self._process.terminate()
            except:
                try: self._process.kill()
                except: pass
            self._process = None
            self._current_engine_path = None
        if self._timer:
            self._timer.cancel()
            self._timer = None

_kokoro_manager = KokoroProcessManager()

class KokoroTTS(service.ServiceBase):
    CONFIG_ENGINE_PATH = 'engine_path' # Path to python.exe of the portable environment

    def __init__(self):
        service.ServiceBase.__init__(self)

    @property
    def service_type(self) -> constants.ServiceType:
        return constants.ServiceType.tts

    @property
    def service_fee(self) -> constants.ServiceFee:
        return constants.ServiceFee.free

    def configuration_options(self):
        return {
            self.CONFIG_ENGINE_PATH: ('file', 'Kokoro Python Executable (python.exe);;All Files (*)'),
        }

    def voice_list(self) -> List[voice.TtsVoice_v3]:
        # Full Kokoro v1.0 Voice Library (54 Voices)
        base_voices = [
            # American English (af_*, am_*)
            ("af_alloy", "American Female - Alloy", languages.AudioLanguage.en_US),
            ("af_aoede", "American Female - Aoede", languages.AudioLanguage.en_US),
            ("af_bella", "American Female - Bella", languages.AudioLanguage.en_US),
            ("af_heart", "American Female - Heart", languages.AudioLanguage.en_US),
            ("af_jessica", "American Female - Jessica", languages.AudioLanguage.en_US),
            ("af_kore", "American Female - Kore", languages.AudioLanguage.en_US),
            ("af_nicole", "American Female - Nicole", languages.AudioLanguage.en_US),
            ("af_nova", "American Female - Nova", languages.AudioLanguage.en_US),
            ("af_river", "American Female - River", languages.AudioLanguage.en_US),
            ("af_sarah", "American Female - Sarah", languages.AudioLanguage.en_US),
            ("af_sky", "American Female - Sky", languages.AudioLanguage.en_US),
            ("am_adam", "American Male - Adam", languages.AudioLanguage.en_US),
            ("am_echo", "American Male - Echo", languages.AudioLanguage.en_US),
            ("am_eric", "American Male - Eric", languages.AudioLanguage.en_US),
            ("am_fenrir", "American Male - Fenrir", languages.AudioLanguage.en_US),
            ("am_liam", "American Male - Liam", languages.AudioLanguage.en_US),
            ("am_michael", "American Male - Michael", languages.AudioLanguage.en_US),
            ("am_onyx", "American Male - Onyx", languages.AudioLanguage.en_US),
            ("am_puck", "American Male - Puck", languages.AudioLanguage.en_US),
            ("am_santa", "American Male - Santa", languages.AudioLanguage.en_US),
            
            # British English (bf_*, bm_*)
            ("bf_alice", "British Female - Alice", languages.AudioLanguage.en_GB),
            ("bf_emma", "British Female - Emma", languages.AudioLanguage.en_GB),
            ("bf_isabella", "British Female - Isabella", languages.AudioLanguage.en_GB),
            ("bf_lily", "British Female - Lily", languages.AudioLanguage.en_GB),
            ("bm_daniel", "British Male - Daniel", languages.AudioLanguage.en_GB),
            ("bm_fable", "British Male - Fable", languages.AudioLanguage.en_GB),
            ("bm_george", "British Male - George", languages.AudioLanguage.en_GB),
            ("bm_lewis", "British Male - Lewis", languages.AudioLanguage.en_GB),
            
            # Japanese (jf_*, jm_*)
            ("jf_alpha", "Japanese Female - Alpha", languages.AudioLanguage.ja_JP),
            ("jf_glowing", "Japanese Female - Glowing", languages.AudioLanguage.ja_JP),
            ("jf_nezumi", "Japanese Female - Nezumi", languages.AudioLanguage.ja_JP),
            ("jf_teira", "Japanese Female - Teira", languages.AudioLanguage.ja_JP),
            ("jm_kuma", "Japanese Male - Kuma", languages.AudioLanguage.ja_JP),
            
            # Chinese Mandarin (zf_*, zm_*)
            ("zf_xiaobei", "Chinese Female - Xiaobei", languages.AudioLanguage.zh_CN),
            ("zf_xiaoni", "Chinese Female - Xiaoni", languages.AudioLanguage.zh_CN),
            ("zf_xiaoxiao", "Chinese Female - Xiaoxiao", languages.AudioLanguage.zh_CN),
            ("zf_xiaoyi", "Chinese Female - Xiaoyi", languages.AudioLanguage.zh_CN),
            ("zm_yunjian", "Chinese Male - Yunjian", languages.AudioLanguage.zh_CN),
            ("zm_yunxi", "Chinese Male - Yunxi", languages.AudioLanguage.zh_CN),
            ("zm_yunze", "Chinese Male - Yunze", languages.AudioLanguage.zh_CN),
            
            # Spanish (ef_*, em_*)
            ("ef_dora", "Spanish Female - Dora", languages.AudioLanguage.es_ES),
            ("em_alex", "Spanish Male - Alex", languages.AudioLanguage.es_ES),
            ("em_santa", "Spanish Male - Santa", languages.AudioLanguage.es_ES),
            
            # French (ff_*)
            ("ff_siwis", "French Female - Siwis", languages.AudioLanguage.fr_FR),
            
            # Hindi (hf_*, hm_*)
            ("hf_alpha", "Hindi Female - Alpha", languages.AudioLanguage.hi_IN),
            ("hf_beta", "Hindi Female - Beta", languages.AudioLanguage.hi_IN),
            ("hm_omega", "Hindi Male - Omega", languages.AudioLanguage.hi_IN),
            ("hm_psi", "Hindi Male - Psi", languages.AudioLanguage.hi_IN),
            
            # Italian (if_*, im_*)
            ("if_sara", "Italian Female - Sara", languages.AudioLanguage.it_IT),
            ("im_nicola", "Italian Male - Nicola", languages.AudioLanguage.it_IT),
            
            # Brazilian Portuguese (pf_*, pm_*)
            ("pf_dora", "Portuguese Female - Dora", languages.AudioLanguage.pt_BR),
            ("pm_alex", "Portuguese Male - Alex", languages.AudioLanguage.pt_BR),
            ("pm_santa", "Portuguese Male - Santa", languages.AudioLanguage.pt_BR),
        ]
        
        voices = []
        for v_key, v_name, v_lang in base_voices:
            voices.append(voice.build_voice_v3(
                name=f"Kokoro - {v_name}",
                gender=constants.Gender.Female if 'Female' in v_name else constants.Gender.Male,
                language=v_lang,
                service=self,
                voice_key=v_key,
                options={}
            ))
        return voices

    def get_tts_audio(self, source_text, voice: voice.TtsVoice_v3, options):
        engine_path = self.get_configuration_value_optional(self.CONFIG_ENGINE_PATH, '')
        
        if not engine_path or not os.path.exists(engine_path):
             # Try to find it in the default location: data/kokoro_engine/python.exe
             # This logic can be improved later
             raise errors.RequestError(source_text, voice, "Kokoro engine not configured.")
             
        import tempfile
        fd, temp_path = tempfile.mkstemp(suffix='.wav')
        os.close(fd) 
        
        try:
            process = _kokoro_manager.get_process(engine_path)
            
            request = {
                "text": source_text,
                "voice": voice.voice_key,
                "output_file": temp_path,
                "speed": 1.0 # TODO: Add speed option support
            }
            payload = json.dumps(request) + "\n"
            
            with _kokoro_manager._lock:
                process.stdin.write(payload.encode('utf-8'))
                process.stdin.flush()
                
                response_line = process.stdout.readline()
                if not response_line:
                    raise Exception("Kokoro process died unexpectedly")
                
                _kokoro_manager._reset_timer_locked()

            if os.path.exists(temp_path):
                with open(temp_path, 'rb') as f:
                    audio_data = f.read()
                return audio_data
            else:
                raise Exception("Kokoro did not create output file.")
            
        except Exception as e:
            logger.warning(f'exception while generating kokoro audio: {e}')
            _kokoro_manager.stop()
            raise errors.RequestError(source_text, voice, str(e))
        finally:
            if os.path.exists(temp_path):
                try: os.remove(temp_path)
                except: pass
