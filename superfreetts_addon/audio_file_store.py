import dataclasses
import hashlib
import json
import os
import tempfile
from typing import Any, Dict, Optional

from . import options
from . import voice as voice_module


EXTENSION_BY_FORMAT = {
    options.AudioFormat.mp3: "mp3",
    options.AudioFormat.wav: "wav",
    options.AudioFormat.ogg_vorbis: "ogg",
    options.AudioFormat.ogg_opus: "ogg",
}


@dataclasses.dataclass(frozen=True)
class AudioRequestKey:
    processed_text: str
    voice_id: str
    voice_options: str
    audio_format: str

    def stable_payload(self) -> str:
        return json.dumps(dataclasses.asdict(self), sort_keys=True, ensure_ascii=True)

    def hash(self) -> str:
        return hashlib.sha224(self.stable_payload().encode("utf-8")).hexdigest()


@dataclasses.dataclass(frozen=True)
class AudioFileResult:
    full_filename: str
    audio_filename: str
    cache_hit: bool


def normalize_options(voice_options: Optional[Dict[str, Any]]) -> str:
    return json.dumps(voice_options or {}, sort_keys=True, ensure_ascii=True, default=str)


def serialize_voice_id(voice_id: voice_module.TtsVoiceId_v3) -> str:
    return json.dumps(
        {
            "voice_key": voice_id.voice_key,
            "service": voice_id.service,
        },
        sort_keys=True,
        ensure_ascii=True,
        default=str,
    )


class AudioFileStore:
    def __init__(self, anki_utils, get_preferences):
        self.anki_utils = anki_utils
        self.get_preferences = get_preferences

    def resolve_audio_format(self, voice_options=None):
        audio_format = options.AudioFormat.mp3
        prefs = self.get_preferences()
        if getattr(prefs, "audio_format", None) == "wav":
            audio_format = options.AudioFormat.wav
        elif getattr(prefs, "audio_format", None) == "ogg":
            audio_format = options.AudioFormat.ogg_opus

        voice_options = voice_options or {}
        if options.AUDIO_FORMAT_PARAMETER in voice_options:
            audio_format = options.AudioFormat[voice_options[options.AUDIO_FORMAT_PARAMETER]]
        return audio_format

    def build_request_key(self, processed_text, voice_id, voice_options=None):
        audio_format = self.resolve_audio_format(voice_options)
        return AudioRequestKey(
            processed_text=processed_text,
            voice_id=serialize_voice_id(voice_id),
            voice_options=normalize_options(voice_options),
            audio_format=audio_format.name,
        )

    def get_audio_filename(self, hash_str, audio_format):
        return f"superfreetts-{hash_str}.{EXTENSION_BY_FORMAT[audio_format]}"

    def get_full_audio_file_name(self, hash_str, audio_format):
        user_files_dir = self.anki_utils.get_user_files_dir()
        if not os.path.isdir(user_files_dir):
            os.makedirs(user_files_dir, exist_ok=True)
        return os.path.join(user_files_dir, self.get_audio_filename(hash_str, audio_format))

    def get_cached_file(self, request_key):
        audio_format = options.AudioFormat[request_key.audio_format]
        hash_str = request_key.hash()
        audio_filename = self.get_audio_filename(hash_str, audio_format)
        full_filename = self.get_full_audio_file_name(hash_str, audio_format)
        if os.path.exists(full_filename) and os.path.getsize(full_filename) > 0:
            return AudioFileResult(full_filename, audio_filename, True)
        return None

    def get_file_result(self, request_key, cache_hit=False):
        audio_format = options.AudioFormat[request_key.audio_format]
        hash_str = request_key.hash()
        audio_filename = self.get_audio_filename(hash_str, audio_format)
        full_filename = self.get_full_audio_file_name(hash_str, audio_format)
        return AudioFileResult(full_filename, audio_filename, cache_hit)

    def write_audio_file_atomic(self, request_key, audio_data):
        result = self.get_file_result(request_key, cache_hit=False)
        target_dir = os.path.dirname(result.full_filename)
        os.makedirs(target_dir, exist_ok=True)
        fd, temp_path = tempfile.mkstemp(
            prefix=f".{os.path.basename(result.audio_filename)}.",
            suffix=".tmp",
            dir=target_dir,
        )
        try:
            with os.fdopen(fd, "wb") as f:
                f.write(audio_data)
                f.flush()
                os.fsync(f.fileno())
            os.replace(temp_path, result.full_filename)
        except Exception:
            try:
                os.remove(temp_path)
            except OSError:
                pass
            raise
        return result
