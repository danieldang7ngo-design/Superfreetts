import base64
import json
import os
import re
from typing import List, Optional

from .. import constants
from .. import errors
from .. import languages
from .. import logging_utils
from .. import service
from .. import voice as voice_module
from .service_mms import SherpaProcessPool

logger = logging_utils.get_child_logger(__name__)

_supertonic_pool = SherpaProcessPool("Supertonic", max_processes=2)

SUPERTONIC_BUILTIN_VOICES = [
    ("M1", "Male 1", constants.Gender.Male),
    ("M2", "Male 2", constants.Gender.Male),
    ("M3", "Male 3", constants.Gender.Male),
    ("M4", "Male 4", constants.Gender.Male),
    ("M5", "Male 5", constants.Gender.Male),
    ("F1", "Female 1", constants.Gender.Female),
    ("F2", "Female 2", constants.Gender.Female),
    ("F3", "Female 3", constants.Gender.Female),
    ("F4", "Female 4", constants.Gender.Female),
    ("F5", "Female 5", constants.Gender.Female),
]

SUPERTONIC_BUILTIN_KEYS = {key for key, _, _ in SUPERTONIC_BUILTIN_VOICES}

SUPERTONIC_LANGUAGE_BY_AUDIO_LANGUAGE = {
    languages.AudioLanguage.ar_XA: "ar",
    languages.AudioLanguage.bg_BG: "bg",
    languages.AudioLanguage.hr_HR: "hr",
    languages.AudioLanguage.cs_CZ: "cs",
    languages.AudioLanguage.da_DK: "da",
    languages.AudioLanguage.de_DE: "de",
    languages.AudioLanguage.et_EE: "et",
    languages.AudioLanguage.el_GR: "el",
    languages.AudioLanguage.en_US: "en",
    languages.AudioLanguage.en_GB: "en",
    languages.AudioLanguage.es_ES: "es",
    languages.AudioLanguage.es_MX: "es",
    languages.AudioLanguage.fi_FI: "fi",
    languages.AudioLanguage.fr_FR: "fr",
    languages.AudioLanguage.hi_IN: "hi",
    languages.AudioLanguage.hu_HU: "hu",
    languages.AudioLanguage.id_ID: "id",
    languages.AudioLanguage.it_IT: "it",
    languages.AudioLanguage.ja_JP: "ja",
    languages.AudioLanguage.ko_KR: "ko",
    languages.AudioLanguage.lv_LV: "lv",
    languages.AudioLanguage.lt_LT: "lt",
    languages.AudioLanguage.nl_NL: "nl",
    languages.AudioLanguage.pl_PL: "pl",
    languages.AudioLanguage.pt_BR: "pt",
    languages.AudioLanguage.pt_PT: "pt",
    languages.AudioLanguage.ro_RO: "ro",
    languages.AudioLanguage.ru_RU: "ru",
    languages.AudioLanguage.sk_SK: "sk",
    languages.AudioLanguage.sl_SI: "sl",
    languages.AudioLanguage.sv_SE: "sv",
    languages.AudioLanguage.tr_TR: "tr",
    languages.AudioLanguage.uk_UA: "uk",
    languages.AudioLanguage.vi_VN: "vi",
}

SUPERTONIC_AUDIO_LANGUAGES = tuple(SUPERTONIC_LANGUAGE_BY_AUDIO_LANGUAGE.keys())


def normalize_custom_voice_name(path: str) -> str:
    base = os.path.splitext(os.path.basename(path or ""))[0]
    name = re.sub(r"[^A-Za-z0-9_. -]+", "_", base).strip(" ._")
    return name or "custom_voice"


def is_reserved_voice_name(name: str) -> bool:
    return name.upper() in SUPERTONIC_BUILTIN_KEYS


def list_custom_voice_files(directory: str) -> List[str]:
    if not directory or not os.path.isdir(directory):
        return []
    files = []
    for filename in sorted(os.listdir(directory)):
        if filename.lower().endswith(".json"):
            files.append(os.path.join(directory, filename))
    return files


def is_supertonic_ready(cache_path: Optional[str] = None) -> bool:
    cache_path = cache_path or constants.SUPERTONIC_CACHE_DIR
    marker = os.path.join(cache_path, "supertonic_model.ready")
    if os.path.exists(marker):
        return True
    if not os.path.isdir(cache_path):
        return False
    for root, dirs, files in os.walk(cache_path):
        if files:
            return True
        if root != cache_path:
            break
    return False


class SupertonicTTS(service.ServiceBase):
    CONFIG_ENGINE_PATH = "engine_path"
    CONFIG_CACHE_PATH = "cache_path"
    CONFIG_CUSTOM_VOICES_PATH = "custom_voices_path"

    @property
    def name(self):
        return "SupertonicTTS"

    @property
    def display_name(self):
        return "Supertonic 3 (Offline AI)"

    @property
    def service_type(self) -> constants.ServiceType:
        return constants.ServiceType.tts

    @property
    def service_fee(self) -> constants.ServiceFee:
        return constants.ServiceFee.free

    def enabled_by_default(self):
        return False

    def cloudlanguagetools_enabled(self):
        return False

    def configuration_options(self):
        return {
            self.CONFIG_ENGINE_PATH: ("file", "Supertonic Python path", "Executable (python.exe);;All Files (*)"),
            self.CONFIG_CACHE_PATH: ("directory", "Supertonic Model Cache Folder (Optional)"),
            self.CONFIG_CUSTOM_VOICES_PATH: ("directory", "Supertonic Custom Voices Folder (Optional)"),
        }

    def advanced_configuration_options(self):
        from .. import cpu_utils

        return {
            "concurrency_workers": ("number", "Concurrency Workers (1-N)", 1, 1, cpu_utils.CPUInfo.get_max_workers()),
            "total_steps": ("number", "Generation Steps (5-12)", 8, 5, 12),
            "max_chunk_length": ("number", "Max Chunk Length", 300, 80, 1000),
            "silence_duration": ("number", "Silence Between Chunks", 0.3, 0, 3),
            "lang_override": str,
            "debug_logging": ("bool", "Enable Debug Logging", False),
        }

    def _get_python_exe(self):
        configured = self.get_configuration_value_optional(self.CONFIG_ENGINE_PATH, "")
        if configured and os.path.exists(configured):
            if os.path.isdir(configured):
                candidate = os.path.join(configured, "python.exe")
                if os.path.exists(candidate):
                    return candidate
            return configured
        try:
            from ..engine_manager import EngineManager

            python_exe = EngineManager.get_python_exe()
            if os.path.exists(python_exe):
                return python_exe
        except Exception:
            pass
        return None

    def _get_cache_path(self):
        return self.get_configuration_value_optional(self.CONFIG_CACHE_PATH, "") or constants.SUPERTONIC_CACHE_DIR

    def _get_custom_voices_path(self):
        return self.get_configuration_value_optional(self.CONFIG_CUSTOM_VOICES_PATH, "") or constants.SUPERTONIC_CUSTOM_VOICES_DIR

    def _voice_options(self):
        return {
            "speed": {
                "type": "number",
                "default": 1.0,
                "min": 0.7,
                "max": 2.0,
                "label": "Speed",
                "tooltip": "Speech speed multiplier. 1.0 = normal.",
            },
        }

    def _build_supertonic_voice(self, name: str, gender: constants.Gender, audio_language: languages.AudioLanguage, voice_key) -> voice_module.TtsVoice_v3:
        return voice_module.build_voice_v3(
            name=name,
            gender=gender,
            language=audio_language,
            service=self,
            voice_key=voice_key,
            options=self._voice_options(),
        )

    def voice_list(self) -> List[voice_module.TtsVoice_v3]:
        cache_path = self._get_cache_path()
        if not is_supertonic_ready(cache_path):
            return [
                voice_module.build_voice_v3(
                    name="Supertonic - Model not installed",
                    gender=constants.Gender.Any,
                    language=languages.AudioLanguage.en_US,
                    service=self,
                    voice_key="supertonic_none",
                    options={},
                )
            ]

        voices = []
        for audio_language in SUPERTONIC_AUDIO_LANGUAGES:
            lang_code = SUPERTONIC_LANGUAGE_BY_AUDIO_LANGUAGE[audio_language]
            for key, label, gender in SUPERTONIC_BUILTIN_VOICES:
                voices.append(
                    self._build_supertonic_voice(
                        name=f"Supertonic - {label}",
                        gender=gender,
                        audio_language=audio_language,
                        voice_key={"style": key, "lang": lang_code},
                    )
                )

        for path in list_custom_voice_files(self._get_custom_voices_path()):
            name = normalize_custom_voice_name(path)
            if is_reserved_voice_name(name):
                continue
            for audio_language in SUPERTONIC_AUDIO_LANGUAGES:
                lang_code = SUPERTONIC_LANGUAGE_BY_AUDIO_LANGUAGE[audio_language]
                voices.append(
                    self._build_supertonic_voice(
                        name=f"Supertonic - {name}",
                        gender=constants.Gender.Any,
                        audio_language=audio_language,
                        voice_key={"style": f"custom:{name}", "lang": lang_code},
                    )
                )
        return voices

    def _get_voice_style_key(self, voice_key) -> str:
        if isinstance(voice_key, dict):
            return voice_key.get("style") or "M1"
        return "M1" if voice_key == "supertonic_none" else voice_key

    def _get_voice_language_override(self, voice_key) -> Optional[str]:
        if isinstance(voice_key, dict):
            lang_code = voice_key.get("lang")
            if lang_code:
                return lang_code
        return None

    def _get_custom_voice_path(self, voice_key) -> Optional[str]:
        voice_key = self._get_voice_style_key(voice_key)
        if not voice_key.startswith("custom:"):
            return None
        wanted = voice_key.split(":", 1)[1]
        for path in list_custom_voice_files(self._get_custom_voices_path()):
            if normalize_custom_voice_name(path) == wanted:
                return path
        return None

    def _language_code(self, voice: voice_module.TtsVoice_v3) -> str:
        override = self.get_configuration_value_optional("lang_override", "")
        if override and override.strip():
            return override.strip()
        voice_lang = self._get_voice_language_override(getattr(voice, "voice_key", None))
        if voice_lang:
            return voice_lang
        audio_lang = voice_module.get_audio_language_for_voice(voice)
        return SUPERTONIC_LANGUAGE_BY_AUDIO_LANGUAGE.get(audio_lang, "na")

    def _base_task(self, text: str, voice: voice_module.TtsVoice_v3, options: dict) -> dict:
        voice_key = voice.voice_key
        style_key = self._get_voice_style_key(voice_key)
        custom_voice_path = self._get_custom_voice_path(voice_key)
        return {
            "text": text,
            "voice": style_key,
            "custom_voice_path": custom_voice_path,
            "cache_path": self._get_cache_path(),
            "lang": self._language_code(voice),
            "speed": options.get("speed", 1.0),
            "total_steps": self.get_configuration_value_optional("total_steps", 8),
            "max_chunk_length": self.get_configuration_value_optional("max_chunk_length", 300),
            "silence_duration": self.get_configuration_value_optional("silence_duration", 0.3),
        }

    def _get_runner_process(self, source_text, voice):
        python_exe = self._get_python_exe()
        if not python_exe:
            raise errors.RequestError(source_text, voice, "Supertonic Python runtime not configured. Please run Supertonic Setup.")
        if not is_supertonic_ready(self._get_cache_path()):
            raise errors.RequestError(source_text, voice, "Supertonic model not installed. Please run Supertonic Setup.")
        script_path = os.path.join(os.path.dirname(__file__), "supertonic_runner.py")
        debug_enabled = self.get_configuration_value_optional("debug_logging", False)
        return _supertonic_pool.get_process(python_exe, script_path, debug_enabled=debug_enabled), python_exe, script_path

    def get_tts_audio(self, source_text, voice: voice_module.TtsVoice_v3, options):
        if voice.voice_key == "supertonic_none":
            raise errors.RequestError(source_text, voice, "Supertonic model not installed. Please run Supertonic Setup.")

        for attempt in [1, 2]:
            process = None
            python_exe = None
            script_path = None
            try:
                process, python_exe, script_path = self._get_runner_process(source_text, voice)
                request = self._base_task(source_text, voice, options)
                process.stdin.write((json.dumps(request) + "\n").encode("utf-8"))
                process.stdin.flush()
                line = process.stdout.readline()
                if not line:
                    raise BrokenPipeError("Supertonic process closed stream.")
                resp = json.loads(line.decode("utf-8").strip())
                if resp.get("status") == "ok" and resp.get("audio_b64"):
                    return base64.b64decode(resp["audio_b64"])
                raise RuntimeError(resp.get("message") or "Supertonic generation failed")
            except (BrokenPipeError, ConnectionResetError, EOFError):
                if process is not None:
                    process.is_healthy = False
                if attempt == 1:
                    continue
                raise
            except Exception as exc:
                if attempt == 2:
                    logger.warning(f"Exception while generating Supertonic audio: {exc}")
                    raise errors.RequestError(source_text, voice, str(exc))
            finally:
                if process is not None and python_exe and script_path:
                    _supertonic_pool.release_process(process, python_exe, script_path)

    def get_tts_audio_batch(self, source_texts: List[str], voice: voice_module.TtsVoice_v3, options: dict) -> List[Optional[bytes]]:
        if not source_texts:
            return []
        if voice.voice_key == "supertonic_none":
            return [None] * len(source_texts)

        for attempt in [1, 2]:
            process = None
            python_exe = None
            script_path = None
            try:
                process, python_exe, script_path = self._get_runner_process("", voice)
                tasks = [self._base_task(text, voice, options) for text in source_texts]
                request = {"action": "generate_batch", "tasks": tasks}
                process.stdin.write((json.dumps(request) + "\n").encode("utf-8"))
                process.stdin.flush()
                line = process.stdout.readline()
                if not line:
                    raise BrokenPipeError("Supertonic process closed stream.")
                resp = json.loads(line.decode("utf-8").strip())
                if resp.get("status") != "ok":
                    raise RuntimeError(resp.get("message") or "Supertonic batch generation failed")
                results = []
                for item in resp.get("results", []):
                    if item.get("status") == "ok" and item.get("audio_b64"):
                        results.append(base64.b64decode(item["audio_b64"]))
                    else:
                        results.append(None)
                if len(results) < len(source_texts):
                    results.extend([None] * (len(source_texts) - len(results)))
                return results[: len(source_texts)]
            except (BrokenPipeError, ConnectionResetError, EOFError):
                if process is not None:
                    process.is_healthy = False
                if attempt == 1:
                    continue
                raise
            except Exception as exc:
                if attempt == 2:
                    logger.warning(f"Exception while generating Supertonic audio batch: {exc}")
                    return [None] * len(source_texts)
            finally:
                if process is not None and python_exe and script_path:
                    _supertonic_pool.release_process(process, python_exe, script_path)

        return [None] * len(source_texts)
