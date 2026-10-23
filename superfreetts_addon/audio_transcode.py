"""Shared audio-transcode helper (handoff A+B follow-up, muc 4).

Policy (user decision 1): save what the engine produces; convert only when
the user picked a different format **and** a converter exists; never convert
when the bytes already match the request.

- Local engines (Piper/Kokoro/MMS/Supertonic): native WAV.
- EdgeTTS: native MP3 (no decoder is bundled, so MP3 -> WAV is unsupported
  and keeps the MP3 bytes with a one-time log).
- WAV -> MP3 uses Anki's bundled ``aqt.sound._encode_mp3`` (ffmpeg-based);
  failures fall back to the original bytes so a batch never loses audio.
"""

import os
import tempfile

from . import audio_file_store
from . import logging_utils
from . import options

logger = logging_utils.get_child_logger(__name__)

# Services whose runner emits WAV bytes.
_WAV_NATIVE_SERVICES = frozenset({
    "PiperTTS", "Piper",
    "KokoroTTS", "Kokoro",
    "MmsTTS", "MMS",
    "SupertonicTTS", "Supertonic",
    "Windows", "macOS", "eSpeak-ng",
})

# Services whose output is MP3.
_MP3_NATIVE_SERVICES = frozenset({"EdgeTTS"})

_CONVERT_FAILED_WARNED: set = set()


def native_format_for(service_name) -> options.AudioFormat:
    """Return the container format a service natively produces."""
    name = str(service_name or "")
    if name in _MP3_NATIVE_SERVICES:
        return options.AudioFormat.mp3
    return options.AudioFormat.wav


def _log_convert_once(key: str, message: str) -> None:
    if key in _CONVERT_FAILED_WARNED:
        logger.debug(message)
        return
    _CONVERT_FAILED_WARNED.add(key)
    logger.warning(message)


def preferred_output_format() -> str:
    """Read the global audio preference (``"mp3"`` or ``"wav"``).

    Anything unexpected (missing config, mocked Anki in tests, legacy
    ``"ogg"``) degrades to ``"wav"`` -- the honest native format -- so
    callers never convert on a guess.
    """
    try:
        import aqt

        from . import constants as addon_constants

        get_config = getattr(getattr(aqt, "mw", None), "addonManager", None)
        if get_config is None:
            return "wav"
        config = get_config.getConfig(addon_constants.CONFIG_ADDON_NAME) or {}
        if not isinstance(config, dict):
            return "wav"
        prefs = config.get(addon_constants.CONFIG_PREFERENCES, {}) or {}
        if not isinstance(prefs, dict):
            return "wav"
        pref = prefs.get("audio_format", "wav")
        if pref == "mp3":
            return "mp3"
        return "wav"
    except Exception:
        return "wav"


def convert_wav_to_mp3(wav_bytes: bytes) -> bytes:
    """Encode WAV bytes to MP3 via Anki's bundled encoder.

    Raises on failure so callers can fall back to the original bytes.
    """
    import aqt

    encode = getattr(getattr(aqt, "sound", None), "_encode_mp3", None)
    if not callable(encode):
        raise RuntimeError("MP3 encoder is not available (aqt.sound._encode_mp3)")
    wav_path = mp3_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as wav_file:
            wav_file.write(wav_bytes)
            wav_path = wav_file.name
        mp3_path = wav_path + ".mp3"
        encode(wav_path, mp3_path)
        with open(mp3_path, "rb") as mp3_file:
            return mp3_file.read()
    finally:
        for path in (wav_path, mp3_path):
            if path:
                try:
                    if os.path.exists(path):
                        os.remove(path)
                except OSError:
                    pass


def maybe_convert(audio_data: bytes, requested_format) -> bytes:
    """Return audio bytes matching ``requested_format`` when possible.

    - Bytes already in the requested format are returned untouched (no
      encoder call, so tests can assert the converter is idle).
    - WAV -> MP3 is attempted via :func:`convert_wav_to_mp3`; on failure
      the original WAV bytes are kept with a one-time warning.
    - Anything else (notably MP3 -> WAV, which needs a decoder we do not
      bundle) keeps the original bytes with a one-time warning.
    """
    if not audio_data:
        return audio_data
    try:
        requested = requested_format
        if isinstance(requested, str):
            requested = audio_file_store._FORMAT_ALIASES.get(requested.lower())
            if requested is None:
                return audio_data
        actual = audio_file_store.detect_audio_format(audio_data)
        if actual is None or actual == requested:
            return audio_data
        if actual == options.AudioFormat.wav and requested == options.AudioFormat.mp3:
            try:
                return convert_wav_to_mp3(audio_data)
            except Exception as e:
                _log_convert_once(
                    "wav-to-mp3-failed",
                    f"[FORMAT] WAV->MP3 conversion failed ({e}); keeping WAV bytes.",
                )
                return audio_data
        _log_convert_once(
            f"unsupported-{audio_file_store.EXTENSION_BY_FORMAT.get(actual, '?')}"
            f"-to-{audio_file_store.EXTENSION_BY_FORMAT.get(requested, '?')}",
            f"[FORMAT] No converter from "
            f"{audio_file_store.EXTENSION_BY_FORMAT.get(actual, '?')} to "
            f"{audio_file_store.EXTENSION_BY_FORMAT.get(requested, '?')}; "
            f"keeping original bytes (EdgeTTS is MP3-only).",
        )
        return audio_data
    except Exception:
        return audio_data


def convert_if_requested(audio_data: bytes, service_name=None) -> bytes:
    """Apply the user preference to native engine bytes (single/batch).

    Services return native bytes; this wrapper converts WAV -> MP3 only
    when the user explicitly picked MP3.  Every other case is a no-op so
    behaviour is unchanged for WAV-preference users and for tests where
    the preference cannot be read.
    """
    if not audio_data:
        return audio_data
    if preferred_output_format() != "mp3":
        return audio_data
    return maybe_convert(audio_data, options.AudioFormat.mp3)
