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

class PiperProcessManager:
    def __init__(self):
        self._processes = {} # {model_path: process}
        self._lru_order = []
        self._lock = threading.Lock()
        self._timers = {} # {model_path: timer}
        self._timeout = 300 # 5 minutes before stopping an idle process
        self.MAX_PROCESSES = 3

    def get_process(self, executable_path, model_path):
        with self._lock:
            # Check if process exists and is alive
            if model_path in self._processes:
                proc = self._processes[model_path]
                if proc.poll() is None:
                    # Update LRU
                    if model_path in self._lru_order:
                        self._lru_order.remove(model_path)
                    self._lru_order.append(model_path)
                    self._reset_timer_locked(model_path)
                    return proc
                else:
                    # Cleanup dead process
                    del self._processes[model_path]
                    if model_path in self._lru_order:
                        self._lru_order.remove(model_path)

            # Evict if pool is full
            while len(self._processes) >= self.MAX_PROCESSES:
                oldest_model = self._lru_order.pop(0)
                logger.info(f"Piper Pool full, evicting oldest model: {oldest_model}")
                self.stop_process_locked(oldest_model)

            # Start new process
            startupinfo = None
            if os.name == 'nt':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            
            cwd = os.path.dirname(executable_path)
            cmd = [executable_path, '--model', model_path, '--json-input']
            
            logger.info(f"Starting persistent Piper process for model: {model_path}")
            proc = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                startupinfo=startupinfo,
                cwd=cwd,
                bufsize=1,
                text=False
            )
            
            self._processes[model_path] = proc
            self._lru_order.append(model_path)
            
            # Drain stderr in a separate thread
            def drain_stderr(pipe, m_path):
                try:
                    while True:
                        line = pipe.readline()
                        if not line: break
                        logger.debug(f"Piper ({os.path.basename(m_path)}) Stderr: {line.decode('utf-8', errors='ignore').strip()}")
                except: pass
            
            t = threading.Thread(target=drain_stderr, args=(proc.stderr, model_path), daemon=True)
            t.start()
            
            self._reset_timer_locked(model_path)
            return proc

    def _reset_timer_locked(self, model_path):
        if model_path in self._timers:
            self._timers[model_path].cancel()
        
        timer = threading.Timer(self._timeout, self.stop_process, args=[model_path])
        self._timers[model_path] = timer
        timer.start()

    def stop_process(self, model_path):
        with self._lock:
            self.stop_process_locked(model_path)

    def stop_process_locked(self, model_path):
        proc = self._processes.pop(model_path, None)
        if proc:
            logger.info(f"Stopping Piper process for model: {model_path}")
            try:
                proc.stdin.close()
                proc.terminate()
            except:
                try: proc.kill()
                except: pass
        
        timer = self._timers.pop(model_path, None)
        if timer:
            timer.cancel()
            
        if model_path in self._lru_order:
            self._lru_order.remove(model_path)

    def stop_all(self):
        with self._lock:
            models = list(self._processes.keys())
            for m in models:
                self.stop_process_locked(m)

    def stop(self):
        """Deprecated alias for stop_all"""
        self.stop_all()

# Global manager instance
_piper_manager = PiperProcessManager()

class PiperTTS(service.ServiceBase):
    CONFIG_EXECUTABLE_PATH = 'executable_path'
    CONFIG_MODELS_PATH = 'models_path'

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
            self.CONFIG_EXECUTABLE_PATH: ('file', 'Piper Executable (*.exe);;All Files (*)'),
            self.CONFIG_MODELS_PATH: ('directory', 'Select Models Directory')
        }

    def voice_list(self) -> List[voice.TtsVoice_v3]:
        models_path = self.get_configuration_value_optional(self.CONFIG_MODELS_PATH, '')
        logger.info(f"PiperTTS: Scanning for models in: {models_path}")
        if not models_path or not os.path.exists(models_path):
            logger.warning(f"PiperTTS: Models path does not exist or not configured: {models_path}")
            return []

        logger.info(f"PiperTTS: Files in models_path: {os.listdir(models_path)}")
        voices = []
        try:
            # Scan for .onnx.json files
            for filename in os.listdir(models_path):
                if filename.endswith('.onnx.json'):
                    logger.debug(f"PiperTTS: Found model config: {filename}")
                    json_path = os.path.join(models_path, filename)
                    onnx_filename = filename.replace('.json', '')
                    onnx_path = os.path.join(models_path, onnx_filename)
                    
                    if not os.path.exists(onnx_path):
                        continue
                        
                    try:
                        with open(json_path, 'r', encoding='utf-8') as f:
                            config = json.load(f)
                        
                        lang_code = config.get('language', {}).get('code', '')
                        if not lang_code:
                            parts = filename.split('-')
                            if len(parts) > 0:
                                lang_code = parts[0]
                        
                        audio_lang = None
                        try:
                            safe_key = lang_code.replace('-', '_')
                            if safe_key in languages.AudioLanguage.__members__:
                                audio_lang = languages.AudioLanguage[safe_key]
                        except:
                            pass
                        
                        if audio_lang:
                            voice_name = onnx_filename.replace('.onnx', '')
                            # Try to build a much friendlier name from the config
                            lang_name = config.get('language', {}).get('name_english', '')
                            country = config.get('language', {}).get('country_english', '')
                            speaker_name = config.get('voice', {}).get('name', '')
                            quality = config.get('voice', {}).get('quality', '')
                            
                            if lang_name and speaker_name:
                                if country:
                                    friendly_name = f"Piper - {lang_name} ({country}) - {speaker_name} [{quality}]"
                                else:
                                    friendly_name = f"Piper - {lang_name} - {speaker_name} [{quality}]"
                            else:
                                friendly_name = f"Piper - {voice_name}"

                            voices.append(voice.build_voice_v3(
                                name=friendly_name,
                                gender=constants.Gender.Any, # Gender varies by speaker
                                language=audio_lang,
                                service=self,
                                voice_key=voice_name,
                                options={}
                            ))
                            
                    except Exception as e:
                        logger.error(f"Error parsing model config {json_path}: {e}")
                        
        except Exception as e:
            logger.error(f"Error listing piper models: {e}")
            
        return voices

    def get_tts_audio(self, source_text, voice: voice.TtsVoice_v3, options):
        executable_path = self.get_configuration_value_optional(self.CONFIG_EXECUTABLE_PATH, '')
        models_path = self.get_configuration_value_optional(self.CONFIG_MODELS_PATH, '')
        
        if not executable_path or not os.path.exists(executable_path):
            raise errors.RequestError(source_text, voice, "Piper executable not found. Please configure path.")
            
        model_file = os.path.join(models_path, voice.voice_key + ".onnx")
        if not os.path.exists(model_file):
            raise errors.RequestError(source_text, voice, f"Model file not found: {model_file}")

        import tempfile
        fd, temp_path = tempfile.mkstemp(suffix='.wav')
        os.close(fd) 
        
        try:
            # Get or start the persistent process
            process = _piper_manager.get_process(executable_path, model_file)
            
            # Send JSON request with output_file
            request = {
                "text": source_text,
                "output_file": temp_path
            }
            payload = json.dumps(request) + "\n"
            
            # Thread-safe write and read
            with _piper_manager._lock:
                process.stdin.write(payload.encode('utf-8'))
                process.stdin.flush()
                
                # Wait for JSON response on stdout
                response_line = process.stdout.readline()
                if not response_line:
                    raise Exception("Piper process died unexpectedly")
                
                _piper_manager._reset_timer_locked(model_file)

            # Read the generated audio file
            if os.path.exists(temp_path):
                with open(temp_path, 'rb') as f:
                    audio_data = f.read()
                return audio_data
            else:
                raise Exception("Piper did not create output file.")
            
        except Exception as e:
            logger.warning(f'exception while generating piper audio: {e}')
            # On error, it's safer to stop the process as it might be in an inconsistent state
            _piper_manager.stop()
            raise errors.RequestError(source_text, voice, str(e))
        finally:
            if os.path.exists(temp_path):
                try: os.remove(temp_path)
                except: pass
