import os
import json
import logging
import subprocess
import threading
import typing
import typing
import sys
import time

from .. import service, voice, errors
from .. import constants
from .. import languages
# from .. import system_utils # lazy loaded
from aqt import mw

logger = logging.getLogger(__name__)

class SherpaProcessPool:
    def __init__(self, max_processes=4):
        self._max_processes = max_processes
        self._pool = [] # List of (process, current_executable, current_script, last_used_time)
        self._lock = threading.Lock()
        self._semaphore = threading.Semaphore(max_processes)
        self._cleanup_timer = None
        self._max_idle_age = 30 # Reduce to 30 seconds for RAM efficiency
        self._start_cleanup_timer()

    def update_max_processes(self, new_max):
        """Dynamically update the maximum number of processes in the pool."""
        with self._lock:
            # We don't shrink existing until they are released or cleaned up
            diff = new_max - self._max_processes
            self._max_processes = new_max
            if diff > 0:
                for _ in range(diff):
                    self._semaphore.release()
            elif diff < 0:
                for _ in range(abs(diff)):
                    # Try to acquire without blocking to shrink immediately
                    # if possible, otherwise it will shrink as processes are released
                    self._semaphore.acquire(blocking=False)
            logger.info(f"SherpaPool: Max processes updated to {new_max}")

    def _start_cleanup_timer(self):
        # Run cleanup every 15 seconds
        self._cleanup_timer = threading.Timer(15.0, self._cleanup_idle)
        self._cleanup_timer.daemon = True
        self._cleanup_timer.start()

    def _cleanup_idle(self):
        with self._lock:
            now = time.time()
            alive_pool = []
            for proc, exe, script, last_time in self._pool:
                if now - last_time > self._max_idle_age:
                    logger.info(f"SherpaPool: Cleaning up idle process {exe}")
                    try:
                        proc.stdin.close()
                        proc.terminate()
                        # Give it a moment to die, then kill if still alive
                        def force_kill(p):
                            try:
                                if p.poll() is None: p.kill()
                            except: pass
                        threading.Timer(2.0, force_kill, args=(proc,)).start()
                    except: pass
                else:
                    alive_pool.append((proc, exe, script, last_time))
            self._pool = alive_pool
        self._start_cleanup_timer()

    def stop_all(self):
        with self._lock:
            for proc, exe, script, last_time in self._pool:
                try:
                    proc.stdin.close()
                    proc.terminate()
                except: pass
            self._pool = []

    def get_process(self, executable_path, script_path, debug_enabled=False):
        # Limit concurrency - this will block until a process is available
        self._semaphore.acquire()
        
        # Non-blocking check for idle process matching both exe and script
        with self._lock:
            for i, (proc, exe, script, last_time) in enumerate(self._pool):
                if proc.poll() is None and exe == executable_path and script == script_path:
                    p, e, s, _ = self._pool.pop(i)
                    return p
        
        # Start new
        return self._start_new(executable_path, script_path, debug_enabled)

    def warmup(self, executable_path, script_path, init_payload=None):
        """Pre-starts a process and optionally sends an initialization payload."""
        with self._lock:
            # Check if we already have an idle process for this
            for proc, exe, script, _ in self._pool:
                if proc.poll() is None and exe == executable_path and script == script_path:
                    return # Already warmed up
        
        proc = self._start_new(executable_path, script_path, debug_enabled=True)
        if init_payload:
            try:
                proc.stdin.write((json.dumps(init_payload) + "\n").encode('utf-8'))
                proc.stdin.flush()
                # Wait for response with timeout to ensure it's ready
                proc.stdout.readline()
            except Exception as e:
                logger.warning(f"SherpaPool: Warmup payload failed: {e}")
        
        self.release_process(proc, executable_path, script_path)
        logger.info(f"SherpaPool: Process warmed up for {script_path}")

    def release_process(self, proc, executable_path, script_path):
        with self._lock:
            if proc.poll() is None:
                self._pool.append((proc, executable_path, script_path, time.time()))
            else:
                pass
            # Always release the semaphore
            self._semaphore.release()

    def _start_new(self, executable_path, script_path, debug_enabled=False):
        cwd = os.path.dirname(executable_path)
        
        startupinfo = None
        if os.name == 'nt':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        env = os.environ.copy()
        if debug_enabled:
            appdata = os.environ.get('APPDATA')
            if appdata:
                log_dir = os.path.join(appdata, 'Anki2', 'addons21', 'Superfreetts', 'user_files')
                os.makedirs(log_dir, exist_ok=True)
                # Unique log file per process based on script name
                script_basename = os.path.splitext(os.path.basename(script_path))[0]
                env['SUPERFREETTS_LOG_FILE'] = os.path.join(log_dir, f'{script_basename}_{int(time.time()*1000)}.log')

        logger.info(f"Starting NEW Sherpa Process: {executable_path}")
        
        proc = subprocess.Popen(
            [executable_path, script_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=cwd,
            startupinfo=startupinfo,
            env=env,
            text=False,
            bufsize=0
        )
        
        def drain_stderr(pipe):
            try:
                while True:
                    line = pipe.readline()
                    if not line: break
                    msg = line.decode('utf-8', errors='ignore').strip()
                    if msg:
                        logger.info(f"[SherpaPool Process] {msg}")
            except: pass
        
        threading.Thread(target=drain_stderr, args=(proc.stderr,), daemon=True).start()
        return proc

# Use 4 parallel generations by default (Save RAM for 8GB machines)
_sherpa_pool = SherpaProcessPool(max_processes=4)

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

    def enabled_by_default(self):
        return True

    def configuration_options(self):
        from .. import system_utils
        return {
            'python_path': ('file', 'Python Executable Path (python.exe);;All Files (*)'),
        }
    
    def advanced_configuration_options(self):
        """Advanced settings for power users (hidden in dropdown)"""
        from .. import system_utils
        from .. import cpu_utils
        return {
            'use_gpu': ('bool', 'Use AMD/DirectML GPU (Windows)', system_utils.is_amd_gpu_detected()),
            'num_threads': ('number', 'CPU Threads (0=Auto)', 1, 0, system_utils.get_total_cpu_count()),
            'concurrency_workers': ('number', 'Concurrency Workers (1-N)', 1, 1, cpu_utils.CPUInfo.get_max_workers()),
            'debug_logging': ('bool', 'Enable Debug Logging', False),
        }

    def voice_list(self) -> typing.List[voice.TtsVoice_v3]:
        # We manually list installed models from data/mms_models
        from ..component_mms_manager import DATA_DIR
        model_dir = os.path.join(DATA_DIR, 'mms_models')
        
        if not os.path.exists(model_dir):
            return []
            
        voices = []
        try:
            dirs = [d for d in os.listdir(model_dir) if os.path.isdir(os.path.join(model_dir, d))]
            # Sort to put common/top languages first (optional, but nice)
            top_langs = ["eng", "kor", "jpn", "cmn", "vie"]
            dirs.sort(key=lambda x: (x not in top_langs, top_langs.index(x) if x in top_langs else x))

            for lang_code in dirs:
                # Map MMS lang_code to AudioLanguage
                audio_lang = languages.get_audio_lang_from_mms(lang_code)
                if audio_lang:
                    # Check if model.onnx exists
                    m_dir = os.path.join(model_dir, lang_code)
                    if not os.path.exists(os.path.join(m_dir, "model.onnx")):
                        continue
                    
                    # Highlight high-quality Piper models
                    quality_suffix = ""
                    if os.path.exists(os.path.join(m_dir, "is_piper.txt")):
                        quality_suffix = " (High Quality)"

                    voice_options = {
                        'speed': {
                            'type': 'number', 'default': 1.0, 'min': 0.5, 'max': 2.0,
                            'label': 'Speed',
                            'tooltip': 'Speed multiplier. 1.0 = normal, 2.0 = 2x faster, 0.5 = 2x slower'
                        },
                    }
                    voices.append(voice.build_voice_v3(
                        name=f"Sherpa - {audio_lang.name}{quality_suffix}",
                        gender=constants.Gender.Any,
                        language=audio_lang,
                        service=self,
                        voice_key=f"mms_{lang_code}",
                        options=voice_options
                    ))
        except Exception as e:
             logger.error(f"MmsTTS: Error listing models: {e}")

        # Add a dummy voice if none found to avoid errors
        if not voices:
             voices.append(voice.build_voice_v3(
                 name="MmsTTS - No Models Installed",
                 gender=constants.Gender.Any,
                 language=languages.AudioLanguage.en_US,
                 service=self,
                 voice_key="mms_none",
                 options={}
             ))
        return voices

    def get_tts_audio(self, source_text, voice: voice.TtsVoice_v3, options):
        # Log to debug file to verify Anki is actually calling us
        debug_enabled = self.get_configuration_value_optional('debug_logging', False)
        if debug_enabled:
            try:
                appdata = os.environ.get('APPDATA')
                if appdata:
                    log_dir = os.path.join(appdata, 'Anki2', 'addons21', 'Superfreetts', 'user_files')
                    os.makedirs(log_dir, exist_ok=True)
                    with open(os.path.join(log_dir, 'sherpa_debug.log'), 'a', encoding='utf-8') as f:
                        f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] ServiceMMS received: {source_text[:50]}...\n")
            except: pass

        if voice.voice_key == "mms_none": return None
        
        python_path = self.get_configuration_value_optional('python_path', '')
        if not python_path:
            # Try to use Kokoro's python if configured
            from ..component_kokoro_manager import PYTHON_EXE
            python_path = PYTHON_EXE
            
        if not os.path.exists(python_path):
            raise errors.RequestError(source_text, voice, "Python engine (Sherpa) not found. Please install MMS/Kokoro backend.")

        lang_code = voice.voice_key.replace("mms_", "")
        from ..component_mms_manager import DATA_DIR
        model_dir = os.path.join(DATA_DIR, 'mms_models', lang_code)
        
        if not os.path.exists(model_dir):
            raise errors.RequestError(source_text, voice, f"MMS Model for {lang_code} not installed.")

        import tempfile
        fd, temp_path = tempfile.mkstemp(suffix='.wav')
        os.close(fd)

        try:
            # Get process from pool
            script_path = os.path.join(os.path.dirname(__file__), 'sherpa_runner_v2.py')
            process = _sherpa_pool.get_process(python_path, script_path, debug_enabled=debug_enabled)
            
            from .. import system_utils
            # Prepare optimization params
            threads_opt = self.get_configuration_value_optional('num_threads', 1)
            if threads_opt <= 0:
                # For pooled operations, use 1 thread per process
                threads_opt = 1 
            
            use_gpu = self.get_configuration_value_optional('use_gpu', system_utils.is_amd_gpu_detected())
            provider = "cpu"
            if use_gpu and system_utils.is_amd_gpu_detected():
                provider = "directml"
            
            clean_text = source_text.replace("\n", " ").strip()
            lexicon_path = os.path.join(model_dir, "lexicon.txt")
            has_lexicon = os.path.exists(lexicon_path)

            request = {
                "text": clean_text,
                "lang_code": lang_code,
                "model_dir": model_dir,
                "output_file": temp_path,
                "num_threads": int(threads_opt),
                "provider": provider,
                "lexicon_path": lexicon_path if has_lexicon else "",
                "speed": options.get('speed', 1.0)
            }
            
            # Send and Receive
            payload = json.dumps(request) + "\n"
            try:
                process.stdin.write(payload.encode('utf-8'))
                process.stdin.flush()
                response_line = process.stdout.readline()
                if not response_line:
                    raise Exception("Sherpa process closed stream.")
                
                resp = json.loads(response_line.decode('utf-8').strip())
            finally:
                # Return process to pool
                _sherpa_pool.release_process(process, python_path, script_path)
            
            if resp.get("status") == "ok":
                if os.path.exists(temp_path):
                    with open(temp_path, 'rb') as f:
                        audio_data = f.read()
                    return audio_data
                else:
                    raise Exception("Audio file not found after generation.")
            else:
                raise Exception(f"Sherpa Error: {resp.get('message')}")

        except Exception as e:
            # Don't kill the process immediately on logical errors, only on pipe errors (handled above)
            raise errors.RequestError(source_text, voice, str(e))
        finally:
            if os.path.exists(temp_path):
                try: os.remove(temp_path)
                except: pass
