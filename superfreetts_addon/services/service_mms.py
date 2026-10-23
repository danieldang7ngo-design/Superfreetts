import os
import json
import logging
import typing

from .. import service, voice, errors
from .. import constants
from .. import languages
from ..mms_engine_manager import MmsEngineManager
# from .. import system_utils # lazy loaded

logger = logging.getLogger(__name__)

from .process_pool import (  # noqa: F401 - re-exported for the other local engines
    DynamicSemaphore,
    EngineBusyError,
    IpcTimeoutError,
    SherpaProcessPool,
    read_response,
    start_stdout_reader,
    terminate_process,
)

# Default pool for MMS and other legacy services
_sherpa_pool = SherpaProcessPool("MMS", max_processes=2)

class MmsTTS(service.ServiceBase):
    def __init__(self):
        super().__init__()
        # Proactively ensure the portable python environment is correctly configured
        self._ensure_python_environment()

    def _ensure_python_environment(self):
        """Proactively ensure the MMS-dedicated python environment is ready."""
        try:
            mms_engine_dir = constants.MMS_ENGINE_DIR
            if os.path.exists(mms_engine_dir):
                # Fix ._pth if needed
                pth_files = [f for f in os.listdir(mms_engine_dir) if f.endswith('._pth')]
                if pth_files:
                    pth_path = os.path.join(mms_engine_dir, pth_files[0])
                    with open(pth_path, 'r') as f:
                        content = f.read()
                    
                    if '#import site' in content:
                        logger.info("MmsTTS: Proactively enabling 'import site' in .pth file")
                        content = content.replace('#import site', 'import site')
                        with open(pth_path, 'w') as f:
                            f.write(content)
            
            # Check if MMS engine needs installation
            if not MmsEngineManager.is_installed():
                logger.info("MmsTTS: MMS Engine not fully installed. Will install when models are downloaded.")
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
        return {
            'engine_path': ('file', 'MMS path', 'Executable (python3);;Executable (python.exe);;All Files (*)'),
        }

    CONFIG_ENGINE_PATH = 'engine_path'

    def _get_python_exe(self):
        """Return a usable Python executable for the sherpa runner.

        Honors the configured ``engine_path`` first (needed on Linux/macOS,
        where the Windows-only bootstrap is skipped and the runner uses a
        user-provided virtualenv instead of the system ``python3``).
        Falls back to the dedicated Windows embeddable engine, then to the
        system interpreter.
        """
        engine_path = self.get_configuration_value_optional(self.CONFIG_ENGINE_PATH, '')
        if engine_path and os.path.exists(engine_path):
            if os.path.isdir(engine_path):
                for exe_name in ('python.exe', 'python3', 'python'):
                    candidate = os.path.join(engine_path, exe_name)
                    if os.path.exists(candidate):
                        return candidate
            return engine_path
        return MmsEngineManager.get_python_exe()
    
    def advanced_configuration_options(self):
        """Advanced settings for power users (hidden in dropdown)"""
        from .. import system_utils
        return {
            'num_threads': ('number', 'CPU Threads (0=Auto)', 1, 0, system_utils.get_total_cpu_count()),
            'concurrency_workers': ('number', 'Concurrency Workers (1-N)', 1, 1, system_utils.get_max_workers()),
            'debug_logging': ('bool', 'Enable Debug Logging', False),
        }

    def voice_list(self) -> typing.List[voice.TtsVoice_v3]:
        # We manually list installed models from data/mms_models
        model_dir = os.path.join(constants.DATA_DIR, 'mms_models')
        
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
                from .. import service_logger
                service_logger.write_log('mms', 'runtime', 'INFO', 'TTS Request', {
                    'Voice': voice.voice_key,
                    'Text': f'"{source_text[:50]}..." ({len(source_text)} chars)'
                })
            except Exception as e:
                logger.warning(f"Debug logging failed: {e}")

        if voice.voice_key == "mms_none": return None
        
        # Always use MMS-dedicated engine (auto-detected or configured)
        python_path = self._get_python_exe()
            
        if not os.path.exists(python_path):
            raise errors.RequestError(source_text, voice, "MMS Engine not found. Please install an MMS language from the MMS Manager first.")

        lang_code = voice.voice_key.replace("mms_", "")
        model_dir = os.path.join(constants.DATA_DIR, 'mms_models', lang_code)
        
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
                        # Prepare optimization params
                        threads_opt = self.get_configuration_value_optional('num_threads', 1)
                        if threads_opt <= 0:
                            # For pooled operations, use 1 thread per process
                            threads_opt = 1 
                        
                        provider = "cpu"
                        
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
                        
                        response_line = read_response(process, "MMS")
                        if not response_line:
                            raise BrokenPipeError("Sherpa process closed stream.")
                        
                        resp = json.loads(response_line.decode('utf-8', errors='replace').strip())
                        
                        if resp.get("status") == "ok":
                            if os.path.exists(temp_path):
                                with open(temp_path, 'rb') as f:
                                    audio_data = f.read()
                                return audio_data
                            else:
                                raise Exception("Audio file not found after generation.")
                        else:
                            raise Exception(f"Sherpa Error: {resp.get('message')}")
                            
                    except (BrokenPipeError, ConnectionResetError, EOFError, IpcTimeoutError) as e:
                        process.is_healthy = False
                        if attempt == 1:
                            logger.warning(f"MmsTTS: Retry 1/1 after process failure: {e}")
                            continue
                        raise e
                    finally:
                        # Return process to pool
                        _sherpa_pool.release_process(process, python_path, script_path)
                except Exception as e:
                    if isinstance(e, EngineBusyError):
                        raise errors.RequestError(source_text, voice, str(e))
                    if attempt == 2:
                        raise errors.RequestError(source_text, voice, str(e))
        finally:
            if os.path.exists(temp_path):
                try: os.remove(temp_path)
                except Exception: pass

    def get_tts_audio_batch(self, source_texts: typing.List[str], voice: voice.TtsVoice_v3, options: dict) -> typing.List[typing.Optional[bytes]]:
        if not source_texts:
            return []

        if voice.voice_key == "mms_none": return [None] * len(source_texts)

        # Always use MMS-dedicated engine (auto-detected or configured)
        python_path = self._get_python_exe()
            
        if not os.path.exists(python_path):
            return [None] * len(source_texts)

        lang_code = voice.voice_key.replace("mms_", "")
        model_dir = os.path.join(constants.DATA_DIR, 'mms_models', lang_code)
        
        if not os.path.exists(model_dir):
            return [None] * len(source_texts)

        debug_enabled = self.get_configuration_value_optional('debug_logging', False)
        
        for attempt in [1, 2]:
            try:
                script_path = os.path.join(os.path.dirname(__file__), 'sherpa_runner_v2.py')
                process = _sherpa_pool.get_process(python_path, script_path, debug_enabled=debug_enabled)
                
                try:
                    threads_opt = self.get_configuration_value_optional('num_threads', 1)
                    if threads_opt <= 0: threads_opt = 1 
                    
                    provider = "cpu"
                    
                    import tempfile
                    tasks = []
                    temp_paths = []
                    try:
                        for text in source_texts:
                            fd, t_path = tempfile.mkstemp(suffix='.wav')
                            os.close(fd)
                            temp_paths.append(t_path)

                            clean_text = text.replace("\n", " ").strip()
                            tasks.append({
                                "text": clean_text,
                                "model_dir": model_dir,
                                "output_file": t_path,
                                "speed": options.get('speed', 1.0)
                            })

                        request = {
                            "action": "generate_batch",
                            "tasks": tasks,
                            "num_threads": int(threads_opt),
                            "provider": provider
                        }

                        payload = json.dumps(request) + "\n"
                        process.stdin.write(payload.encode('utf-8'))
                        process.stdin.flush()

                        response_line = read_response(process, "MMS", chunk=True)
                        if not response_line:
                            raise BrokenPipeError("Sherpa process closed stream during batch.")

                        resp = json.loads(response_line.decode('utf-8', errors='replace').strip())

                        results = []
                        if resp.get("status") == "ok":
                            for i, task_resp in enumerate(resp.get("results", [])):
                                t_path = temp_paths[i]
                                if task_resp.get("status") == "ok" and os.path.exists(t_path):
                                    with open(t_path, 'rb') as f:
                                        results.append(f.read())
                                else:
                                    results.append(None)
                        else:
                            logger.error(f"MmsTTS Batch Error: {resp.get('message')}")
                            results = [None] * len(source_texts)

                        return results
                    finally:
                        # Run even on readline/JSON/retry failures so a broken
                        # chunk cannot leak temp WAV files into the system /tmp.
                        for t_path in temp_paths:
                            try:
                                if os.path.exists(t_path):
                                    os.remove(t_path)
                            except OSError:
                                pass
                            
                except (BrokenPipeError, ConnectionResetError, EOFError, IpcTimeoutError) as e:
                    process.is_healthy = False
                    if attempt == 1:
                        logger.warning(f"MmsTTS Batch: Retry 1/1 after process failure: {e}")
                        continue
                    raise e
                finally:
                    _sherpa_pool.release_process(process, python_path, script_path)
            except Exception as e:
                if isinstance(e, EngineBusyError):
                    logger.error(f"MmsTTS batch skipped, engine busy: {e}")
                    return [None] * len(source_texts)
                if attempt == 2:
                    logger.error(f"MmsTTS Batch Failed: {e}")
                    return [None] * len(source_texts)
