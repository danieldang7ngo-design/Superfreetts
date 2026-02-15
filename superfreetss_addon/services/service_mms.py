import os
import json
import logging
import subprocess
import threading
import typing
from .. import service, voice, errors
from .. import constants
from aqt import mw

logger = logging.getLogger(__name__)

class SherpaProcessManager:
    def __init__(self):
        self._process = None
        self._lock = threading.Lock()
        self._timer = None
        self._current_executable = None
        self._last_stderr = []

    def get_last_stderr(self):
        with self._lock:
            return "\n".join(self._last_stderr)

    def stop(self):
        with self._lock:
            self.stop_locked()

    def stop_locked(self):
        if self._process:
            try:
                self._process.stdin.close()
                self._process.terminate()
                self._process.wait(timeout=2)
            except:
                try: self._process.kill()
                except: pass
            self._process = None
        if self._timer:
            self._timer.cancel()
            self._timer = None

    def _reset_timer_locked(self):
        if self._timer:
            self._timer.cancel()
        self._timer = threading.Timer(120.0, self.stop)
        self._timer.start()

    def get_process(self, executable_path):
        with self._lock:
            if self._process and self._current_executable != executable_path:
                self.stop_locked()
            
            if self._process is None or self._process.poll() is not None:
                # Reset stderr buffer
                self._last_stderr = []
                
                # Use standardized runner
                script_path = os.path.join(os.path.dirname(__file__), 'sherpa_runner.py')
                cwd = os.path.dirname(executable_path)
                
                startupinfo = None
                if os.name == 'nt':
                    startupinfo = subprocess.STARTUPINFO()
                    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

                self._process = subprocess.Popen(
                    [executable_path, script_path],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    cwd=cwd,
                    startupinfo=startupinfo,
                    text=False,
                    bufsize=1
                )
                self._current_executable = executable_path
                
                # Drain stderr
                def drain_stderr(pipe):
                    try:
                        while True:
                            line = pipe.readline()
                            if not line: break
                            decoded = line.decode('utf-8', errors='ignore').strip()
                            logger.error(f"Sherpa Stderr: {decoded}")
                            with self._lock:
                                self._last_stderr.append(decoded)
                                if len(self._last_stderr) > 20:
                                    self._last_stderr.pop(0)
                    except: pass
                
                threading.Thread(target=drain_stderr, args=(self._process.stderr,), daemon=True).start()

            self._reset_timer_locked()
            return self._process

_sherpa_manager = SherpaProcessManager()

class MmsTTS(service.ServiceBase):
    def __init__(self):
        super().__init__()
        # Proactively ensure the portable python environment is correctly configured
        self._ensure_python_environment()

    def _ensure_python_environment(self):
        try:
            from ..component_mms_manager import KOKORO_ENGINE_DIR
            if os.path.exists(KOKORO_ENGINE_DIR):
                pth_files = [f for f in os.listdir(KOKORO_ENGINE_DIR) if f.endswith('._pth')]
                if pth_files:
                    pth_path = os.path.join(KOKORO_ENGINE_DIR, pth_files[0])
                    with open(pth_path, 'r') as f:
                        content = f.read()
                    
                    if '#import site' in content:
                        logger.info("MmsTTS: Proactively enabling 'import site' in .pth file")
                        content = content.replace('#import site', 'import site')
                        with open(pth_path, 'w') as f:
                            f.write(content)
        except Exception as e:
            logger.warning(f"MmsTTS: Failed to proactively configure python environment: {e}")

    @property
    def name(self):
        return "MmsTTS"

    @property
    def display_name(self):
        return "MMS (Meta Offline)"

    @property
    def service_type(self) -> constants.ServiceType:
        return constants.ServiceType.tts

    @property
    def service_fee(self) -> constants.ServiceFee:
        return constants.ServiceFee.free

    def _log_environment(self, python_exe):
        try:
            import subprocess
            # Aggressive environment check
            cmd = [python_exe, "-c", "import sys; import os; print('PATH=' + str(sys.path)); print('CWD=' + os.getcwd()); pth_files = [f for f in os.listdir('.') if f.endswith('._pth')]; [print('PTH_CONTENT['+f+']=' + open(f).read()) for f in pth_files]"]
            res = subprocess.run(cmd, capture_output=True, text=True, cwd=os.path.dirname(python_exe))
            logger.info(f"MmsTTS Environment Check:\nSTDOUT: {res.stdout}\nSTDERR: {res.stderr}")
        except Exception as e:
            logger.warning(f"MmsTTS: Environment check failed: {e}")

    def configuration_options(self):
        return {
            'python_path': ('file', 'Python Executable Path (python.exe);;All Files (*)'),
        }

    def voice_list(self) -> typing.List[voice.TtsVoice_v3]:
        # We manually list installed models from data/mms_models
        from ..component_mms_manager import DATA_DIR
        from .. import languages
        models_dir = os.path.join(DATA_DIR, 'mms_models')
        voices = []

        # Mapping MMS 3-letter codes to AudioLanguage
        MMS_TO_AUDIO_LANG = {
            "swe": languages.AudioLanguage.sv_SE,
            "vie": languages.AudioLanguage.vi_VN,
            "deu": languages.AudioLanguage.de_DE,
            "fra": languages.AudioLanguage.fr_FR,
            "spa": languages.AudioLanguage.es_ES,
            "ita": languages.AudioLanguage.it_IT,
            "por": languages.AudioLanguage.pt_PT,
            "nld": languages.AudioLanguage.nl_NL,
            "dan": languages.AudioLanguage.da_DK,
            "fin": languages.AudioLanguage.fi_FI,
            "nor": languages.AudioLanguage.nb_NO,
        }
        
        if os.path.exists(models_dir):
            for lang_code in os.listdir(models_dir):
                model_dir = os.path.join(models_dir, lang_code)
                if os.path.isdir(model_dir) and os.path.exists(os.path.join(model_dir, "model.onnx")):
                    # Find human readable name from the JSON file
                    lang_name = lang_code
                    json_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "mms_languages.json")
                    if os.path.exists(json_path):
                        try:
                            with open(json_path, "r", encoding="utf-8") as f:
                                all_langs = json.load(f)
                                for l in all_langs:
                                    if l.get("Iso Code") == lang_code:
                                        lang_name = f"{l.get('Language Name')} ({l.get('Country')})"
                                        break
                        except: pass
                    
                    audio_lang = MMS_TO_AUDIO_LANG.get(lang_code, languages.AudioLanguage.en_US)
                    
                    voices.append(voice.build_voice_v3(
                        name=f"MMS {lang_name} ({lang_code})",
                        gender=constants.Gender.Any,
                        language=audio_lang,
                        service=self,
                        voice_key=f"mms_{lang_code}",
                        options={}
                    ))
        
        if not voices:
            # Add a placeholder to guide user
            voices.append(voice.build_voice_v3(
                name="Click 'Install MMS...' in config",
                gender=constants.Gender.Any,
                language=languages.AudioLanguage.en_US,
                service=self,
                voice_key="mms_none",
                options={}
            ))
            
        return voices

    def get_tts_audio(self, source_text, voice: voice.TtsVoice_v3, options):
        python_path = self.get_configuration_value_optional('python_path', '')
        if not python_path:
            # Try to use Kokoro's python if configured
            from ..component_kokoro_manager import PYTHON_EXE
            python_path = PYTHON_EXE
            
        if not os.path.exists(python_path):
            raise errors.RequestError(source_text, voice, "Python engine (Sherpa) not found.")

        lang_code = voice.voice_key.replace("mms_", "")
        from ..component_mms_manager import DATA_DIR
        model_dir = os.path.join(DATA_DIR, 'mms_models', lang_code)
        
        if not os.path.exists(model_dir):
            raise errors.RequestError(source_text, voice, "MMS Model not installed.")

        import tempfile
        fd, temp_path = tempfile.mkstemp(suffix='.wav')
        os.close(fd)

        try:
            process = _sherpa_manager.get_process(python_path)
            request = {
                "text": source_text,
                "lang_code": lang_code,
                "model_dir": model_dir,
                "output_file": temp_path
            }
            with _sherpa_manager._lock:
                # Ensure the payload ends with a newline
                payload = json.dumps(request) + "\n"
                process.stdin.write(payload.encode('utf-8'))
                process.stdin.flush()
                
                # Read line from stdout buffer
                response_line = process.stdout.readline()
                if not response_line:
                    raise Exception("Sherpa process died")
                
                _sherpa_manager._reset_timer_locked()

            if os.path.exists(temp_path):
                with open(temp_path, 'rb') as f:
                    audio_data = f.read()
                return audio_data
            else:
                raise Exception("MMS did not create audio.")

        except Exception as e:
            _sherpa_manager.stop()
            raise errors.RequestError(source_text, voice, str(e))
        finally:
            if os.path.exists(temp_path):
                try: os.remove(temp_path)
                except: pass
