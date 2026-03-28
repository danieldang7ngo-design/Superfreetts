import sys
import os
import subprocess
import json
import io
import threading
import time
import tempfile
from typing import List, Optional

from superfreetss_addon import voice as voice_module
from superfreetss_addon import service
from superfreetss_addon import errors
from superfreetss_addon import constants
from superfreetss_addon import languages
from superfreetss_addon import logging_utils

logger = logging_utils.get_child_logger(__name__)

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
            self.CONFIG_MODELS_PATH: ('directory', 'Piper Models Directory'),
        }
    
    def advanced_configuration_options(self):
        """Advanced settings for power users (hidden in dropdown)"""
        from .. import system_utils
        from .. import cpu_utils
        return {
            'num_threads': ('number', 'CPU Threads (0=Auto/Serial)', 1, 0, system_utils.get_total_cpu_count()),
            'concurrency_workers': ('number', 'Concurrency Workers (1-N)', 1, 1, cpu_utils.CPUInfo.get_max_workers()),
            'debug_logging': ('bool', 'Enable Debug Logging', False)
        }

    def _get_piper_exe(self):
        exe_path = self.get_configuration_value_optional(self.CONFIG_EXECUTABLE_PATH, '')
        if exe_path and os.path.exists(exe_path):
            return exe_path
        
        # Try default location
        try:
            # Try to avoid relative import if possible
            try:
                from superfreetss_addon import component_piper_setup
            except ImportError:
                from .. import component_piper_setup
            
            if os.path.exists(component_piper_setup.PIPER_EXE_PATH):
                return component_piper_setup.PIPER_EXE_PATH
        except: pass
            
        return None

    def _resolve_models_dir(self):
        """Resolve Piper models directory: config value or default addon path."""
        try:
            from superfreetss_addon import component_piper_setup
        except ImportError:
            from .. import component_piper_setup
        default_dir = component_piper_setup.PIPER_MODELS_DIR
        models_path = self.get_configuration_value_optional(self.CONFIG_MODELS_PATH, '') or None
        if models_path and os.path.exists(models_path):
            return models_path
        if os.path.exists(default_dir):
            logger.info(f"Piper: Using default models path: {default_dir}")
            return default_dir
        return None

    def voice_list(self) -> List[voice_module.TtsVoice_v3]:
        models_path = self._resolve_models_dir()

        voices = []
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
                                    'sentence_silence': {
                                        'type': 'number', 'default': 0.2, 'min': 0.0, 'max': 2.0,
                                        'label': 'Pause (seconds)',
                                        'tooltip': 'Silence between sentences in seconds. 0.2 = default, 0 = no pause'
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
            except Exception as e:
                logger.error(f"Piper: Error listing piper models in {models_path}: {e}")
            
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
        if not models_path:
            raise errors.RequestError(source_text, voice, "No Piper models directory found. Please set 'Piper Models Directory' in configuration or run Setup Piper.")

        piper_exe = self._get_piper_exe()
        if not piper_exe:
            raise errors.RequestError(source_text, voice, "Piper engine (piper.exe) not found. Please click 'Setup Piper' in configuration.")

        model_file = os.path.join(models_path, voice.voice_key + ".onnx")
        if not os.path.exists(model_file):
            raise errors.RequestError(source_text, voice, f"Model file not found: {model_file}")

        # Create temporary file for output
        fd, temp_wav = tempfile.mkstemp(suffix=".wav")
        os.close(fd) # Close it immediately so Piper can write to it
        
        try:
            # Command: piper.exe -m model.onnx -f output.wav
            num_threads = self.get_configuration_value_optional('num_threads', 0)
            cmd = [
                piper_exe,
                "--model", model_file,
                "--output_file", temp_wav
            ]
            if num_threads > 0:
                cmd.extend(["--thread", str(int(num_threads))])
            
            # Speed & silence options
            length_scale = options.get('length_scale', 1.0)
            sentence_silence = options.get('sentence_silence', 0.2)
            cmd.extend(["--length_scale", str(length_scale)])
            cmd.extend(["--sentence_silence", str(sentence_silence)])
            
            # Subprocess usually takes some text via stdin or --input
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            
            stdout, stderr = process.communicate(input=source_text)
            
            if process.returncode != 0:
                logger.warning(f"Piper error: {stderr}")
                raise Exception(f"Piper process failed: {stderr}")

            if not os.path.exists(temp_wav) or os.path.getsize(temp_wav) == 0:
                raise Exception("Piper did not create valid output file.")

            with open(temp_wav, "rb") as f:
                return f.read()

        except Exception as e:
            logger.warning(f'exception while generating piper audio (subprocess): {e}')
            raise errors.RequestError(source_text, voice, str(e))
        finally:
            if os.path.exists(temp_wav):
                try: os.remove(temp_wav)
                except: pass
