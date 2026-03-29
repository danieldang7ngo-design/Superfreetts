import os
import json
import logging
import subprocess
import threading
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
    def __init__(self, name="Shared", max_processes=4):
        self.name = name
        self._max_processes = max_processes
        self._pool = [] # List of (process, current_executable, current_script, last_used_time)
        self._lock = threading.Lock()
        self._semaphore = threading.Semaphore(max_processes)
        self._cleanup_timer = None
        self._max_idle_age = 180 # 180s idle timeout as mandated
        self._total_spawned = 0 # Track total processes (active + idle)
        self._start_cleanup_timer()

    def _start_cleanup_timer(self):
        if self._cleanup_timer:
            self._cleanup_timer.cancel()
        self._cleanup_timer = threading.Timer(15.0, self._cleanup_idle)
        self._cleanup_timer.daemon = True
        self._cleanup_timer.start()

    def _cleanup_idle(self):
        with self._lock:
            now = time.time()
            alive_pool = []
            for proc, exe, script, last_time in self._pool:
                # If process died, hit idle timeout, or is unhealthy, terminate it
                is_unhealthy = not getattr(proc, 'is_healthy', True)
                if proc.poll() is not None or (now - last_time > self._max_idle_age) or is_unhealthy:
                    logger.info(f"SherpaPool[{self.name}]: Cleaning up process {os.path.basename(script)} (Reason: {'Health' if is_unhealthy else 'Timeout/Dead'})")
                    # Offload termination to avoid blocking the lock
                    threading.Thread(target=self.safe_terminate, args=(proc,), daemon=True).start()
                    self._total_spawned -= 1
                else:
                    alive_pool.append((proc, exe, script, last_time))
            self._pool = alive_pool
        self._start_cleanup_timer()

    def safe_terminate(self, proc):
        """Enforce safe termination sequence and pipe closure."""
        try:
            proc.terminate()
            try:
                proc.wait(timeout=2.0)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait(timeout=1.0)
        except:
            pass
        finally:
            # Guaranteed triple pipe closure
            for pipe in [proc.stdin, proc.stdout, proc.stderr]:
                if pipe:
                    try: pipe.close()
                    except: pass
            proc.is_healthy = False

    def get_process(self, executable_path, script_path, debug_enabled=False):
        # Limit concurrency - blocks if max_processes are "out"
        self._semaphore.acquire()
        
        with self._lock:
            # 1. Try to find an idle process for THIS script
            for i, (proc, exe, script, last_time) in enumerate(self._pool):
                if proc.poll() is None and exe == executable_path and script == script_path:
                    p, e, s, _ = self._pool.pop(i)
                    return p
            
            # 2. If no matching idle process, but we have OTHER idle processes and we're at capacity
            # we should kill the oldest idle one to make room for a NEW type (Script)
            if self._total_spawned >= self._max_processes and self._pool:
                # Kill oldest (first in list)
                p, e, s, _ = self._pool.pop(0)
                logger.info(f"SherpaPool[{self.name}]: Capacity reached. Terminating oldest idle {os.path.basename(s)} for new {os.path.basename(script_path)}")
                try:
                    p.stdin.close()
                    p.terminate()
                except: pass
                self._total_spawned -= 1

        # 3. Start new process
        new_proc = self._start_new(executable_path, script_path, debug_enabled)
        with self._lock:
            self._total_spawned += 1
        return new_proc

    def release_process(self, proc, executable_path, script_path):
        with self._lock:
            is_healthy = getattr(proc, 'is_healthy', True)
            if proc.poll() is None and is_healthy:
                self._pool.append((proc, executable_path, script_path, time.time()))
            else:
                self._total_spawned -= 1
                if not is_healthy:
                    threading.Thread(target=self.safe_terminate, args=(proc,), daemon=True).start()
        self._semaphore.release()

    def stop_all(self):
        with self._lock:
            for proc, exe, script, last_time in self._pool:
                try:
                    proc.stdin.close()
                    proc.terminate()
                except: pass
            self._pool = []
            self._total_spawned = 0

    def _start_new(self, executable_path, script_path, debug_enabled=False):
        cwd = os.path.dirname(executable_path)
        startupinfo = None
        if os.name == 'nt':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        env = os.environ.copy()
        logger.info(f"SherpaPool[{self.name}]: Starting NEW Process: {os.path.basename(script_path)}")

        # Observability Upgrade: Initialize the output sink (default to DEVNULL)
        stderr_sink = subprocess.DEVNULL
        
        if debug_enabled:
            try:
                # Log Strategy: Per-engine files in user_files/logs
                log_dir = os.path.join(os.path.dirname(os.path.dirname(script_path)), 'user_files', 'logs')
                os.makedirs(log_dir, exist_ok=True)
                log_path = os.path.join(log_dir, f"{self.name.lower()}_error.log")
                
                # Lightweight Log Rotation (Roll to .old if file > 5MB)
                if os.path.exists(log_path) and os.path.getsize(log_path) > 5 * 1024 * 1024:
                    backup_path = log_path + ".old"
                    if os.path.exists(backup_path): os.remove(backup_path)
                    os.rename(log_path, backup_path)
                
                # Use file-based logging (Safe: No PIPE deadlock risk)
                stderr_sink = open(log_path, "a", encoding='utf-8', buffering=1, errors='replace') # Line-buffered
            except Exception as e:
                logger.warning(f"Failed to initialize file logging for {self.name}: {e}")
                stderr_sink = subprocess.DEVNULL

        proc = subprocess.Popen(
            [executable_path, script_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=stderr_sink,
            cwd=cwd,
            startupinfo=startupinfo,
            env=env,
            text=False,
            bufsize=0
        )
        proc.is_healthy = True
        
        # Guard: Close our handle in parent after child inherits it to avoid leaks
        if hasattr(stderr_sink, 'close') and stderr_sink != subprocess.DEVNULL:
            stderr_sink.close()

        return proc

# Default pool for MMS and other legacy services
_sherpa_pool = SherpaProcessPool("MMS", max_processes=2)

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
            for attempt in [1, 2]:
                try:
                    # Get process from pool
                    script_path = os.path.join(os.path.dirname(__file__), 'sherpa_runner_v2.py')
                    process = _sherpa_pool.get_process(python_path, script_path, debug_enabled=debug_enabled)
                    
                    try:
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
                        process.stdin.write(payload.encode('utf-8'))
                        process.stdin.flush()
                        
                        response_line = process.stdout.readline()
                        if not response_line:
                            raise BrokenPipeError("Sherpa process closed stream.")
                        
                        resp = json.loads(response_line.decode('utf-8').strip())
                        
                        if resp.get("status") == "ok":
                            if os.path.exists(temp_path):
                                with open(temp_path, 'rb') as f:
                                    audio_data = f.read()
                                return audio_data
                            else:
                                raise Exception("Audio file not found after generation.")
                        else:
                            raise Exception(f"Sherpa Error: {resp.get('message')}")
                            
                    except (BrokenPipeError, ConnectionResetError, EOFError) as e:
                        process.is_healthy = False
                        if attempt == 1:
                            logger.warning(f"MmsTTS: Retry 1/1 after process failure: {e}")
                            continue
                        raise e
                    finally:
                        # Return process to pool
                        _sherpa_pool.release_process(process, python_path, script_path)
                except Exception as e:
                    if attempt == 2:
                        raise errors.RequestError(source_text, voice, str(e))
        finally:
            if os.path.exists(temp_path):
                try: os.remove(temp_path)
                except: pass
