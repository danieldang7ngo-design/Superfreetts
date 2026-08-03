import sys
import os
import subprocess
import json
import io
import threading
import time
import tempfile
from typing import List, Optional

from .. import voice as voice_module
from .. import service
from .. import errors
from .. import constants
from .. import languages
from .. import logging_utils
from .. import system_utils

logger = logging_utils.get_child_logger(__name__)
 
from .service_mms import SherpaProcessPool
_piper_pool = SherpaProcessPool("Piper", max_processes=2)

def _get_kokoro_engine_dir():
    try:
        return constants.KOKORO_ENGINE_DIR
    except AttributeError:
        return None

def _get_python_exe():
    try:
        from ..engine_manager import EngineManager
        return EngineManager.get_python_exe()
    except ImportError:
        return None

# Known Piper dataset/voice names -> gender (Rhasspy/Piper common models)
_PIPER_DATASET_GENDER = {
    'amy': constants.Gender.Female,
    'kristin': constants.Gender.Female,
    'ljspeech': constants.Gender.Female,
    'lessac': constants.Gender.Male,
    'ryan': constants.Gender.Male,
    'john': constants.Gender.Male,
    'joe': constants.Gender.Male,
    'sam': constants.Gender.Male,
    'norman': constants.Gender.Male,
    'bryce': constants.Gender.Male,
    'reza_ibrahim': constants.Gender.Male,
    'kusal': constants.Gender.Male,
    'hfc_female': constants.Gender.Female,
    'hfc_male': constants.Gender.Male,
}

def _piper_infer_gender(config: dict, voice_name: str, dataset: str) -> constants.Gender:
    """Infer gender from Piper model JSON/config, dataset name, or voice filename."""
    g = config.get('gender') or config.get('voice', {}).get('gender')
    if g is not None:
        s = str(g).strip().lower()
        if s in ('male', 'm'):
            return constants.Gender.Male
        if s in ('female', 'f'):
            return constants.Gender.Female
    key = (dataset or voice_name).lower()
    if 'female' in key:
        return constants.Gender.Female
    if 'male' in key:
        return constants.Gender.Male
    for part in key.replace('-', '_').split('_'):
        if part in _PIPER_DATASET_GENDER:
            return _PIPER_DATASET_GENDER[part]
    if key in _PIPER_DATASET_GENDER:
        return _PIPER_DATASET_GENDER[key]
    return constants.Gender.Any


class PiperTTS(service.ServiceBase):
    CONFIG_EXECUTABLE_PATH = 'executable_path'
    CONFIG_MODELS_PATH = 'models_path'

    def __init__(self):
        service.ServiceBase.__init__(self)

    @property
    def name(self):
        return "PiperTTS"

    @property
    def display_name(self):
        return "Piper (Offline AI)"

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
            self.CONFIG_EXECUTABLE_PATH: ('directory', 'Python Folder (Manual Override, Optional)'),
            self.CONFIG_MODELS_PATH: ('directory', 'Piper Models Folder (Manual Override, Optional)'),
        }
    
    def advanced_configuration_options(self):
        """Advanced settings for power users (hidden in dropdown)"""
        from .. import system_utils
        return {
            'num_threads': ('number', 'CPU Threads (0=Auto/Serial)', 1, 0, system_utils.get_total_cpu_count()),
            'concurrency_workers': ('number', 'Concurrency Workers (1-N)', 1, 1, system_utils.get_max_workers()),
            'debug_logging': ('bool', 'Enable Debug Logging', False)
        }

    def _get_piper_exe(self):
        """
        Return the path to the python executable that will run piper_runner.py.
        Try user config first, then auto-detect from profile.
        """
        # Try user manual override first
        user_python_folder = self.get_configuration_value_optional(self.CONFIG_EXECUTABLE_PATH, '')
        if user_python_folder and os.path.isdir(user_python_folder):
            python_exe = os.path.join(user_python_folder, 'python.exe')
            if os.path.exists(python_exe):
                logger.info(f"[PiperTTS] ✓ Using manual Python path: {python_exe}")
                return python_exe
            else:
                logger.warning(f"[PiperTTS] ⚠ Manual Python path does not contain python.exe: {user_python_folder}")
        
        # Auto-detect from profile
        python_exe = _get_python_exe()
        logger.info(f"[PiperTTS] Auto-detecting Python: {python_exe}")
        if python_exe and os.path.exists(python_exe):
            logger.info(f"[PiperTTS] ✓ Using auto-detected Python: {python_exe}")
            return python_exe
        
        logger.error(f"[PiperTTS] ❌ Python not found (manual: {user_python_folder}, auto: {python_exe})")
        return None
    
    def _get_piper_engine_dir(self):
        """
        Get the Piper engine directory, using safe path if needed.
        """
        default_dir = constants.PIPER_ENGINE_DIR
        
        # Check if path has problematic characters
        if system_utils.has_problematic_path_chars(default_dir):
            logger.warning(f"[PiperTTS] ⚠ Default engine path contains special characters: {default_dir}")
            
            # Use safe location
            safe_base = system_utils.get_safe_data_dir()
            safe_engine_dir = os.path.join(safe_base, 'piper_engine')
            
            if os.path.exists(safe_engine_dir):
                logger.info(f"[PiperTTS] ✓ Using safe engine path: {safe_engine_dir}")
                return safe_engine_dir
            
            # Try to migrate if old path exists
            if os.path.exists(default_dir):
                logger.info(f"[PiperTTS] Migrating engine from problematic path to safe location...")
                if system_utils.migrate_data_to_safe_location(default_dir, safe_engine_dir):
                    logger.info(f"[PiperTTS] ✓ Migration successful. New engine path: {safe_engine_dir}")
                    return safe_engine_dir
            
            # Return safe path anyway (will need setup)
            return safe_engine_dir
        
        return default_dir

    def _resolve_espeak_data_dir(self):
        """Resolve the espeak-ng-data directory required for Piper phonemization."""
        # Get engine dir (handles special characters automatically)
        engine_dir = self._get_piper_engine_dir()
        path = os.path.join(engine_dir, 'piper', 'espeak-ng-data')
        
        if os.path.exists(path):
            return path
        
        # Fallback: check models directory as alternative location
        models_path = self._resolve_models_dir()
        if models_path:
            alt_path = os.path.join(models_path, 'espeak-ng-data')
            if os.path.exists(alt_path):
                logger.info(f"[PiperTTS] ✓ Found espeak-ng-data in models dir: {alt_path}")
                return alt_path
        
        logger.warning(f"[PiperTTS] ⚠ espeak-ng-data not found at {path} or in models directory")
        return None

    def _resolve_models_dir(self):
        """Resolve Piper models directory: user config or auto-detect."""
        # Try user config first (manual override)
        models_path = self.get_configuration_value_optional(self.CONFIG_MODELS_PATH, '')
        if models_path and os.path.exists(models_path):
            # Validate: check if folder contains .onnx files
            has_models = any(f.endswith('.onnx.json') for f in os.listdir(models_path) if os.path.isfile(os.path.join(models_path, f)))
            if has_models:
                logger.info(f"[PiperTTS] ✓ Using manual models path: {models_path}")
                return models_path
            else:
                logger.warning(f"[PiperTTS] ⚠ Manual path has no .onnx models: {models_path}")
        
        # Check if default path has problematic characters
        default_dir = constants.PIPER_MODELS_DIR
        
        if system_utils.has_problematic_path_chars(default_dir):
            logger.warning(f"[PiperTTS] ⚠ Default models path contains special characters: {default_dir}")
            
            # Try safe location
            safe_base = system_utils.get_safe_data_dir()
            safe_models_dir = os.path.join(safe_base, 'piper_models')
            
            if os.path.exists(safe_models_dir):
                has_models = any(f.endswith('.onnx.json') for f in os.listdir(safe_models_dir) if os.path.isfile(os.path.join(safe_models_dir, f)))
                if has_models:
                    logger.info(f"[PiperTTS] ✓ Using safe models path: {safe_models_dir}")
                    return safe_models_dir
            
            # Try to migrate if old path exists
            if os.path.exists(default_dir):
                logger.info(f"[PiperTTS] Migrating models from problematic path to safe location...")
                if system_utils.migrate_data_to_safe_location(default_dir, safe_models_dir):
                    logger.info(f"[PiperTTS] ✓ Migration successful. New models path: {safe_models_dir}")
                    return safe_models_dir
        
        # Fallback: auto-detect from profile (original logic)
        if os.path.exists(default_dir):
            has_models = any(f.endswith('.onnx.json') for f in os.listdir(default_dir) if os.path.isfile(os.path.join(default_dir, f)))
            if has_models:
                logger.info(f"[PiperTTS] ✓ Auto-detected models path: {default_dir}")
                return default_dir
            else:
                logger.warning(f"[PiperTTS] ⚠ Auto-detected path has no .onnx models: {default_dir}")
        
        logger.error(f"[PiperTTS] ❌ No models directory found (manual: {models_path}, auto: {default_dir})")
        return None

    def voice_list(self) -> List[voice_module.TtsVoice_v3]:
        voices = []
        
        # Scan models folder
        models_path = self._resolve_models_dir()
        if models_path and os.path.exists(models_path):
            logger.info(f"Piper: Listing models in {models_path}")
            try:
                files = os.listdir(models_path)
                logger.info(f"Piper: Found {len(files)} files in models directory.")
                for filename in files:
                    if filename.endswith('.onnx.json'):
                        json_path = os.path.join(models_path, filename)
                        onnx_path = os.path.join(models_path, filename.replace('.json', ''))
                        
                        if not os.path.exists(onnx_path):
                            logger.warning(f"Piper: Missing .onnx file for config {filename}")
                            continue
                            
                        try:
                            with open(json_path, 'r', encoding='utf-8') as f:
                                config = json.load(f)
                            
                            lang_code_raw = config.get('language', {}).get('code', '')
                            lang_code = lang_code_raw.replace('-', '_')
                            
                            audio_lang = None
                            for name, member in languages.AudioLanguage.__members__.items():
                                if name.lower() == lang_code.lower():
                                    audio_lang = member
                                    break
                            
                            if audio_lang:
                                voice_name = os.path.basename(onnx_path).replace('.onnx', '')
                                lang_name = config.get('language', {}).get('name_english', '')
                                if not lang_name:
                                    lang_name = config.get('language', {}).get('name_native', voice_name)
                                quality = config.get('audio', {}).get('quality', config.get('voice', {}).get('quality', 'medium'))
                                dataset = config.get('dataset', '')
                                if dataset:
                                    friendly_name = f"Piper - {lang_name} ({dataset}) [{quality}]"
                                else:
                                    friendly_name = f"Piper - {lang_name} - {voice_name} [{quality}]"

                                gender = _piper_infer_gender(config, voice_name, dataset)
                                voice_options = {
                                    'length_scale': {
                                        'type': 'number', 'default': 1.0, 'min': 0.1, 'max': 3.0,
                                        'label': 'Speed',
                                        'tooltip': 'Speech speed multiplier. 1.0 = normal, 0.5 = 2x faster, 2.0 = 2x slower'
                                    },
                                }
                                voices.append(voice_module.build_voice_v3(
                                    name=friendly_name,
                                    gender=gender,
                                    language=audio_lang,
                                    service=self,
                                    voice_key=voice_name,
                                    options=voice_options
                                ))
                                logger.info(f"Piper: Loaded voice {friendly_name}")
                            else:
                                logger.warning(f"Piper: Unsupported language code '{lang_code_raw}' (mapped to '{lang_code}') in {filename}")
                        except Exception as e:
                            logger.error(f"Piper: Error parsing model config {json_path}: {e}")
            except PermissionError as e:
                logger.error(f"[PiperTTS] ❌ PERMISSION DENIED accessing {models_path}")
                logger.error(f"[PiperTTS] Error details: {e}")
                logger.error(f"[PiperTTS] Check folder permissions or antivirus settings")
                import traceback
                logger.error(traceback.format_exc())
            except Exception as e:
                logger.error(f"Piper: Error listing piper models in {models_path}: {e}")
                import traceback
                logger.error(traceback.format_exc())
            
        # Add a placeholder voice if none found
        if not voices:
             voice_options = {
                 'length_scale': {
                     'type': 'number', 'default': 1.0, 'min': 0.1, 'max': 3.0,
                     'label': 'Speed',
                     'tooltip': 'Speech speed multiplier. 1.0 = normal, 0.5 = 2x faster, 2.0 = 2x slower'
                 },
                 'sentence_silence': {
                     'type': 'number', 'default': 0.2, 'min': 0.0, 'max': 2.0,
                     'label': 'Pause (seconds)',
                     'tooltip': 'Silence between sentences in seconds. 0.2 = default, 0 = no pause'
                 },
             }
             voices.append(voice_module.build_voice_v3(
                 name="Piper - No Models Installed (Check Config)",
                 gender=constants.Gender.Any,
                 language=languages.AudioLanguage.en_US,
                 service=self,
                 voice_key="piper_none",
                 options=voice_options
             ))
             logger.info("Piper: Added placeholder voice because no models were found.")

        logger.info(f"Piper: Returning {len(voices)} voices.")
        return voices

    def get_tts_audio(self, source_text, voice: voice_module.TtsVoice_v3, options):
        if voice.voice_key == "piper_none":
            raise errors.RequestError(source_text, voice, "No Piper models installed. Please setup Piper and download voices.")

        debug_enabled = self.get_configuration_value_optional('debug_logging', False)
        models_path = self._resolve_models_dir()

        if debug_enabled:
            try:
                from .. import service_logger
                service_logger.write_log('piper', 'runtime', 'INFO', 'TTS Request', {
                    'Voice': voice.voice_key,
                    'Text': f'"{source_text[:50]}..." ({len(source_text)} chars)'
                })
            except Exception as e:
                logger.warning(f"Debug logging setup failed: {e}")

        if not models_path:
            raise errors.RequestError(source_text, voice, "No Piper models directory found. Please set 'Piper Models Directory' in configuration or run Setup Piper.")

        piper_exe = self._get_piper_exe()
        if not piper_exe:
            raise errors.RequestError(source_text, voice, "Piper engine (piper.exe) not found. Please click 'Setup Piper' in configuration.")

        model_file = os.path.join(models_path, voice.voice_key + ".onnx")
        if not os.path.exists(model_file):
            raise errors.RequestError(source_text, voice, f"Model file not found: {model_file}")

        for attempt in [1, 2]:
            try:
                # Get process from pool
                script_path = os.path.join(os.path.dirname(__file__), 'piper_runner.py')
                if not os.path.exists(script_path):
                    raise errors.RequestError(source_text, voice, f"piper_runner.py not found at: {script_path}")
                
                try:
                    process = _piper_pool.get_process(piper_exe, script_path, debug_enabled=debug_enabled)
                except (PermissionError, OSError) as e:
                    logger.error(f"[PiperTTS] ❌ ACCESS DENIED when creating process!")
                    logger.error(f"[PiperTTS] Executable: {piper_exe}")
                    logger.error(f"[PiperTTS] Script: {script_path}")
                    logger.error(f"[PiperTTS] Error: {e}")
                    import traceback
                    logger.error(traceback.format_exc())
                    raise errors.RequestError(source_text, voice, f"Access denied to Piper engine or script. Check antivirus or permissions.")
                
                try:
                    # Prepare Piper-specific config
                    tokens_path = model_file + ".json" 
                    
                    length_scale = options.get('length_scale', 1.0)
                    data_dir = self._resolve_espeak_data_dir()
                    if not data_dir:
                        raise errors.RequestError(source_text, voice, "espeak-ng-data directory not found. Please run 'Setup Piper' to install the complete Piper engine.")
                    num_threads = self.get_configuration_value_optional('num_threads', 1)

                    request = {
                        "text": source_text,
                        "model_path": model_file,
                        "tokens_path": tokens_path,
                        "data_dir": data_dir,
                        "sid": 0,
                        "speed": length_scale,
                        "num_threads": num_threads
                    }
                    
                    payload = json.dumps(request) + "\n"
                    process.stdin.write(payload.encode('utf-8'))
                    process.stdin.flush()
                    
                    response_line = process.stdout.readline()
                    if not response_line:
                        raise BrokenPipeError("Piper process closed stream.")
                    
                    resp_data = response_line.decode('utf-8', errors='replace').strip()
                    try:
                        resp = json.loads(resp_data)
                    except Exception:
                        raise Exception(f"Invalid JSON from Piper: {resp_data}")

                    if resp.get("status") == "ok":
                        import base64
                        audio_b64 = resp.get("audio_b64")
                        if audio_b64:
                            audio_data = base64.b64decode(audio_b64)
                            
                            # Convert to MP3 if requested
                            # Use the global preferences from superfreetts.
                            # Better: use the global preferences from superfreetts or similar.
                            # In this context, we don't have direct access to the Preferences object unless we pass it.
                            # However, we can use aqt.mw.pm.meta to get the raw config or use the existing service config.
                            
                            # Actually, service.py has access to the configuration via self.get_configuration_value_optional
                            # but audio_format is a global preference.
                            
                            import aqt
                            from .. import constants as addon_constants
                            config = aqt.mw.addonManager.getConfig(addon_constants.CONFIG_ADDON_NAME) or {}
                            prefs = config.get(addon_constants.CONFIG_PREFERENCES, {})
                            pref_format = prefs.get("audio_format", "mp3")
                            
                            if pref_format == "mp3":
                                logger.debug("PiperTTS: Converting WAV to MP3")
                                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as wav_file:
                                    wav_file.write(audio_data)
                                    wav_path = wav_file.name
                                
                                mp3_path = wav_path.replace(".wav", ".mp3")
                                try:
                                    aqt.sound._encode_mp3(wav_path, mp3_path)
                                    with open(mp3_path, "rb") as mp3_file:
                                        audio_data = mp3_file.read()
                                finally:
                                    if os.path.exists(wav_path): os.remove(wav_path)
                                    if os.path.exists(mp3_path): os.remove(mp3_path)
                            
                            return audio_data
                        else:
                            raise Exception("No audio data in Piper response.")
                    else:
                        raise Exception(f"Piper Error: {resp.get('message')}")
                        
                except (BrokenPipeError, ConnectionResetError, EOFError) as e:
                    process.is_healthy = False
                    if attempt == 1:
                        logger.warning(f"PiperTTS: Retry 1/1 after process failure: {e}")
                        continue
                    raise e
                finally:
                    _piper_pool.release_process(process, piper_exe, script_path)
                    
            except Exception as e:
                if attempt == 2:
                    logger.warning(f"Exception while generating piper audio (persistent): {e}")
                    raise errors.RequestError(source_text, voice, str(e))

    def get_tts_audio_batch(self, source_texts: List[str], voice: voice_module.TtsVoice_v3, options: dict) -> List[Optional[bytes]]:
        if not source_texts:
            return []
            
        piper_exe = self._get_piper_exe()
        if not piper_exe:
             logger.error("[PiperTTS Batch] No piper_exe found!")
             return [None] * len(source_texts)
        
        models_path = self._resolve_models_dir()
        if not models_path:
             return [None] * len(source_texts)

        model_file = os.path.join(models_path, voice.voice_key + ".onnx")
        if not os.path.exists(model_file):
             return [None] * len(source_texts)

        debug_enabled = self.get_configuration_value_optional('debug_logging', False)
        
        for attempt in [1, 2]:
            try:
                # Get process from pool
                script_path = os.path.join(os.path.dirname(__file__), 'piper_runner.py')
                if not os.path.exists(script_path):
                    logger.error(f"[PiperTTS Batch] Script not found: {script_path}")
                    return [None] * len(source_texts)
                
                try:
                    process = _piper_pool.get_process(piper_exe, script_path, debug_enabled=debug_enabled)
                except (PermissionError, OSError) as e:
                    logger.error(f"[PiperTTS Batch] ❌ ACCESS DENIED when creating process!")
                    logger.error(f"[PiperTTS Batch] Executable: {piper_exe}")
                    logger.error(f"[PiperTTS Batch] Script: {script_path}")
                    logger.error(f"[PiperTTS Batch] Error: {e}")
                    import traceback
                    logger.error(traceback.format_exc())
                    return [None] * len(source_texts)
                
                try:
                    tokens_path = model_file + ".json"
                    data_dir = self._resolve_espeak_data_dir()
                    if not data_dir:
                        raise errors.RequestError(source_text, voice, "espeak-ng-data directory not found. Please run 'Setup Piper' to install the complete Piper engine.")
                    tasks = []
                    for text in source_texts:
                        tasks.append({
                            "text": text,
                            "model_path": model_file,
                            "tokens_path": tokens_path,
                            "data_dir": data_dir,
                            "sid": 0,
                            "speed": options.get('length_scale', 1.0),
                            "num_threads": self.get_configuration_value_optional('num_threads', 1)
                        })
                    
                    num_threads = self.get_configuration_value_optional('num_threads', 1)
                    request = {
                        "action": "generate_batch",
                        "tasks": tasks,
                        "num_threads": int(num_threads),
                    }
                    payload = json.dumps(request) + "\n"
                    process.stdin.write(payload.encode('utf-8'))
                    process.stdin.flush()
                    
                    response_line = process.stdout.readline()
                    if not response_line:
                        raise BrokenPipeError("Piper process closed stream.")
                    
                    resp_text = response_line.decode('utf-8', errors='replace').strip()
                    try:
                        resp = json.loads(resp_text)
                    except Exception:
                        raise Exception(f"Invalid JSON from Piper: {resp_text}")

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
                        raise Exception(f"Piper batch Error: {resp.get('message')}")

                except (BrokenPipeError, ConnectionResetError, EOFError) as e:
                    process.is_healthy = False
                    if attempt == 1:
                        logger.warning(f"PiperTTS Batch: Retry 1/1 after process failure: {e}")
                        continue
                    raise e
                finally:
                    _piper_pool.release_process(process, piper_exe, script_path)
                    
            except Exception as e:
                if attempt == 2:
                    logger.warning(f"Exception while generating piper audio batch (persistent): {e}")
                    return [None] * len(source_texts)
