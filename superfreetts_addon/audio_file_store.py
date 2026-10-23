import dataclasses
import hashlib
import json
import os
import re
import tempfile
import threading
from collections import OrderedDict
from typing import Any, Dict, Optional

from . import logging_utils
from . import options
from . import voice as voice_module

logger = logging_utils.get_child_logger(__name__)


EXTENSION_BY_FORMAT = {
    options.AudioFormat.mp3: "mp3",
    options.AudioFormat.wav: "wav",
    options.AudioFormat.ogg_vorbis: "ogg",
    options.AudioFormat.ogg_opus: "ogg",
}

AUDIO_EXTENSIONS = ("mp3", "wav", "ogg")

# Cache entries are content-addressed: ``superfreetts-<sha224>.<ext>``.
# Anything else living in user_files (usage_log.json, the debug log,
# checkpoint metadata, ...) must never be treated as cache.
CACHE_FILENAME_PATTERN = re.compile(r"^superfreetts-[0-9a-f]{56}\.(?:mp3|wav|ogg)$")

# Default output format.  Local engines (Piper, Kokoro, MMS, Supertonic)
# return WAV bytes and the add-on ships no encoder for them, so WAV is the
# only format that is honest for every local engine.  MP3 remains available
# for engines that really produce MP3 (EdgeTTS, macOS say, eSpeak-ng) and is
# still converted on demand for Piper single-note requests.  OGG has no
# encoder at all and is no longer offered in the UI.
DEFAULT_AUDIO_FORMAT = "wav"

_FORMAT_BY_EXTENSION = {
    "mp3": options.AudioFormat.mp3,
    "wav": options.AudioFormat.wav,
    "ogg": options.AudioFormat.ogg_opus,
}

# Values historical voice presets may contain in their `format` voice option.
_FORMAT_ALIASES = {
    "mp3": options.AudioFormat.mp3,
    "wav": options.AudioFormat.wav,
    "pcm": options.AudioFormat.wav,
    "ogg": options.AudioFormat.ogg_opus,
    "ogg_opus": options.AudioFormat.ogg_opus,
    "ogg_vorbis": options.AudioFormat.ogg_vorbis,
}

_UNSUPPORTED_FORMAT_WARNED = set()
_MISMATCH_WARNED = set()


def _log_mismatch_once(key: str, message: str) -> None:
    """Warn once per situation; repeat occurrences stay at debug level.

    A 500-note batch under a mismatched preference must not produce 500
    identical warnings.
    """
    if key in _MISMATCH_WARNED:
        logger.debug(message)
        return
    _MISMATCH_WARNED.add(key)
    logger.warning(message)


def is_cache_audio_filename(filename: str) -> bool:
    """Return True only for files created by this add-on's audio cache."""
    return bool(CACHE_FILENAME_PATTERN.match(filename or ""))


def detect_audio_format(audio_data: Optional[bytes]) -> Optional[options.AudioFormat]:
    """Detect the container format from magic bytes (best effort).

    Returns None when the bytes are unknown/short, so callers can fall back
    to the requested format instead of guessing.
    """
    if not audio_data:
        return None
    head = bytes(audio_data[:12])
    if head[:4] == b"RIFF" and head[8:12] == b"WAVE":
        return options.AudioFormat.wav
    if head[:4] == b"OggS":
        return options.AudioFormat.ogg_opus
    if head[:3] == b"ID3":
        return options.AudioFormat.mp3
    # Bare MPEG audio frame sync (no ID3 tag): 11 bits set.
    if len(head) >= 2 and head[0] == 0xFF and (head[1] & 0xE0) == 0xE0:
        return options.AudioFormat.mp3
    return None


def _normalize_format(audio_format: Optional[options.AudioFormat]) -> options.AudioFormat:
    """Map every format this build cannot produce onto WAV.

    OGG was previously offered in the UI but no service ever encoded it, so
    a stored ``ogg`` preference or a legacy preset ``format=ogg`` option must
    degrade to WAV rather than producing an invalid ``.ogg`` file.
    """
    if audio_format is None:
        return options.AudioFormat.wav
    if audio_format in (options.AudioFormat.ogg_opus, options.AudioFormat.ogg_vorbis):
        if audio_format not in _UNSUPPORTED_FORMAT_WARNED:
            _UNSUPPORTED_FORMAT_WARNED.add(audio_format)
            logger.warning(
                "[FORMAT] OGG output is not supported by any bundled engine; "
                "falling back to WAV. Existing OGG preferences are ignored."
            )
        return options.AudioFormat.wav
    return audio_format


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
    # Magic-byte validation is cheap per file but is repeated for every note
    # that shares a content-addressed file.  Remembering recently validated
    # paths turns the hot path into a single os.path.exists() + size check.
    MAX_VERIFIED_ENTRIES = 4096

    def __init__(self, anki_utils, get_preferences):
        self.anki_utils = anki_utils
        self.get_preferences = get_preferences
        self._verified_files = OrderedDict()
        self._verified_lock = threading.RLock()

    def _is_verified(self, full_filename):
        with self._verified_lock:
            if full_filename not in self._verified_files:
                return False
            self._verified_files.move_to_end(full_filename)
            return True

    def _remember_verified(self, full_filename):
        with self._verified_lock:
            self._verified_files[full_filename] = True
            self._verified_files.move_to_end(full_filename)
            while len(self._verified_files) > self.MAX_VERIFIED_ENTRIES:
                self._verified_files.popitem(last=False)

    def _forget_verified(self, full_filename):
        with self._verified_lock:
            self._verified_files.pop(full_filename, None)

    def clear_verified_cache(self):
        """Drop remembered magic-byte validations (called after cleanup)."""
        with self._verified_lock:
            self._verified_files.clear()

    def remove_cached_file_if_unused(self, full_filename):
        """Remove a cache file unless a live cache hit has claimed it.

        Cleanup runs on a background thread.  Cache reads and writes mark a
        path verified while holding this lock, so cleanup cannot delete a file
        that a batch has just selected or a writer has just published.  The
        caller is still responsible for checking the file's age.
        """
        with self._verified_lock:
            if full_filename in self._verified_files:
                return False
            try:
                os.remove(full_filename)
                return True
            except FileNotFoundError:
                return False

    def resolve_audio_format(self, voice_options=None):
        prefs = self.get_preferences()
        preference_format = getattr(prefs, "audio_format", None) or DEFAULT_AUDIO_FORMAT
        if preference_format == "mp3":
            audio_format = options.AudioFormat.mp3
        elif preference_format == "ogg":
            audio_format = _normalize_format(options.AudioFormat.ogg_opus)
        else:
            audio_format = options.AudioFormat.wav

        voice_options = voice_options or {}
        if options.AUDIO_FORMAT_PARAMETER in voice_options:
            raw = voice_options[options.AUDIO_FORMAT_PARAMETER]
            requested = _FORMAT_ALIASES.get(str(raw).lower())
            if requested is None:
                logger.warning(
                    f"[FORMAT] ignoring unknown voice option format={raw!r}; "
                    f"using {EXTENSION_BY_FORMAT[audio_format]} instead."
                )
            else:
                audio_format = _normalize_format(requested)
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

    def _file_matches_extension(self, full_filename, audio_format):
        """True when the stored bytes really are the format the name claims."""
        actual = detect_audio_format(_read_magic_bytes(full_filename))
        if actual is None:
            # Unknown/short content: do not delete a file we cannot judge.
            return True
        return EXTENSION_BY_FORMAT[actual] == EXTENSION_BY_FORMAT[audio_format]

    def get_cached_file(self, request_key):
        requested = options.AudioFormat[request_key.audio_format]
        hash_str = request_key.hash()
        candidates = [requested] + [
            _FORMAT_BY_EXTENSION[extension]
            for extension in AUDIO_EXTENSIONS
            if extension != EXTENSION_BY_FORMAT[requested]
        ]
        seen = set()
        for audio_format in candidates:
            extension = EXTENSION_BY_FORMAT[audio_format]
            if extension in seen:
                continue
            seen.add(extension)
            full_filename = self.get_full_audio_file_name(hash_str, audio_format)
            with self._verified_lock:
                if not os.path.exists(full_filename) or os.path.getsize(full_filename) == 0:
                    self._forget_verified(full_filename)
                    continue
                if not self._is_verified(full_filename):
                    if not self._file_matches_extension(full_filename, audio_format):
                        # Left over from an older build that named files after the
                        # requested format instead of the bytes it wrote.
                        _log_mismatch_once(
                            "stale-cache",
                            "[FORMAT] ignoring cache files whose content does not match "
                            "their extension (written by an older build); they are "
                            "deleted and regenerated. This message is logged once.",
                        )
                        self._forget_verified(full_filename)
                        try:
                            os.remove(full_filename)
                        except OSError:
                            pass
                        continue
                    self._remember_verified(full_filename)
                return AudioFileResult(
                    full_filename,
                    self.get_audio_filename(hash_str, audio_format),
                    True,
                )
        return None

    def get_file_result(self, request_key, cache_hit=False, audio_format=None):
        requested = options.AudioFormat[request_key.audio_format]
        if audio_format is None:
            audio_format = requested
        hash_str = request_key.hash()
        audio_filename = self.get_audio_filename(hash_str, audio_format)
        full_filename = self.get_full_audio_file_name(hash_str, audio_format)
        return AudioFileResult(full_filename, audio_filename, cache_hit)

    def write_audio_file_atomic(self, request_key, audio_data):
        requested = options.AudioFormat[request_key.audio_format]
        actual = detect_audio_format(audio_data) or requested
        if EXTENSION_BY_FORMAT[actual] != EXTENSION_BY_FORMAT[requested]:
            _log_mismatch_once(
                f"engine {EXTENSION_BY_FORMAT[actual]} -> {EXTENSION_BY_FORMAT[requested]} request",
                f"[FORMAT] engine returned {EXTENSION_BY_FORMAT[actual]} bytes for a "
                f"{EXTENSION_BY_FORMAT[requested]} request; saving with the real "
                f"extension so playback stays valid.",
            )
        result = self.get_file_result(request_key, cache_hit=False, audio_format=actual)
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
                # No per-file fsync: os.replace() already publishes the complete
                # file atomically.  BatchCheckpoint keeps its fsync for crash
                # recovery, and a 0-byte file is detected and regenerated by
                # get_cached_file() on the next run.  A 500-note batch used to
                # block on 500 disk flushes here.
            with self._verified_lock:
                os.replace(temp_path, result.full_filename)
                self._remember_verified(result.full_filename)
        except Exception:
            self._forget_verified(result.full_filename)
            try:
                os.remove(temp_path)
            except OSError:
                pass
            raise
        return result


def _read_magic_bytes(full_filename, count=12):
    try:
        with open(full_filename, "rb") as f:
            return f.read(count)
    except OSError:
        return b""
