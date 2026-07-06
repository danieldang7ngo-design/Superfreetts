import base64
import io
import json
import os
import sys
import traceback

# Ensure the directory containing this script is in sys.path for runner_base import
runner_dir = os.path.dirname(os.path.abspath(__file__))
if runner_dir not in sys.path:
    sys.path.insert(0, runner_dir)

from runner_base import setup_stdio, log
setup_stdio()


_ENGINE = None
_ENGINE_CACHE_KEY = None
_VOICE_STYLE_CACHE = {}


def _set_cache_env(cache_path):
    if not cache_path:
        return
    os.makedirs(cache_path, exist_ok=True)
    os.environ["HF_HOME"] = cache_path
    os.environ["HUGGINGFACE_HUB_CACHE"] = os.path.join(cache_path, "hub")
    os.environ["TORCH_HOME"] = os.path.join(cache_path, "torch")


def _get_engine(cache_path, auto_download=False):
    global _ENGINE, _ENGINE_CACHE_KEY
    _set_cache_env(cache_path)
    cache_key = os.path.abspath(cache_path or "")
    if _ENGINE is not None and _ENGINE_CACHE_KEY == cache_key:
        return _ENGINE

    from supertonic import TTS

    try:
        _ENGINE = TTS(auto_download=auto_download, cache_dir=cache_path)
    except TypeError:
        _ENGINE = TTS(auto_download=auto_download)
    _ENGINE_CACHE_KEY = cache_key
    return _ENGINE


def _load_custom_voice(engine, path):
    if not path:
        return None
    if hasattr(engine, "get_voice_style_from_path"):
        return engine.get_voice_style_from_path(path)
    try:
        from supertonic import get_voice_style_from_path
    except ImportError:
        from supertonic.voice import get_voice_style_from_path
    return get_voice_style_from_path(path)


def _load_builtin_voice_style(engine, voice_name):
    if not voice_name:
        voice_name = "M1"
    if voice_name in _VOICE_STYLE_CACHE:
        return _VOICE_STYLE_CACHE[voice_name]
    if hasattr(engine, "get_voice_style"):
        style = engine.get_voice_style(voice_name)
    else:
        try:
            try:
                from supertonic import get_voice_style
            except ImportError:
                from supertonic.voice import get_voice_style
            style = get_voice_style(voice_name)
        except (ImportError, AttributeError):
            style = voice_name
    _VOICE_STYLE_CACHE[voice_name] = style
    return style


def _to_wav_bytes(result):
    if result is None:
        raise ValueError("Supertonic returned no audio")
    if isinstance(result, bytes):
        return result
    if isinstance(result, bytearray):
        return bytes(result)
    if isinstance(result, str):
        with open(result, "rb") as handle:
            return handle.read()
    if isinstance(result, dict):
        for key in ("wav", "audio", "audio_bytes", "bytes"):
            if key in result:
                return _to_wav_bytes(result[key])
        if "audio_b64" in result:
            return base64.b64decode(result["audio_b64"])
    if isinstance(result, tuple) and len(result) == 2:
        first, second = result
        if isinstance(first, int):
            sample_rate, audio = first, second
        else:
            audio, sample_rate = first, second
        sample_rate = _normalize_sample_rate(sample_rate)
        return _array_to_wav(audio, sample_rate)
    if hasattr(result, "audio") and hasattr(result, "sample_rate"):
        return _array_to_wav(result.audio, result.sample_rate)
    if hasattr(result, "numpy") and hasattr(result, "shape"):
        return _array_to_wav(result, 44100)
    raise TypeError(f"Unsupported Supertonic audio result: {type(result)!r}")


def _normalize_sample_rate(sample_rate):
    try:
        if hasattr(sample_rate, "shape"):
            if getattr(sample_rate, "size", 0) != 1:
                return 44100
            sample_rate = float(sample_rate.reshape(-1)[0])
        sample_rate = int(sample_rate or 44100)
    except Exception:
        return 44100
    if sample_rate < 8000 or sample_rate > 384000:
        return 44100
    return sample_rate


def _normalize_audio_array(audio):
    if hasattr(audio, "shape"):
        try:
            import numpy as np

            audio = np.asarray(audio)
            if audio.ndim == 2:
                if audio.shape[0] == 1:
                    audio = audio.reshape(-1)
                elif audio.shape[0] <= 8 and audio.shape[1] > audio.shape[0]:
                    audio = audio.T
        except Exception:
            pass
    return audio


def _array_to_wav(audio, sample_rate):
    try:
        import soundfile as sf
        audio = _normalize_audio_array(audio)
        buf = io.BytesIO()
        sf.write(buf, audio, _normalize_sample_rate(sample_rate), format="WAV")
        return buf.getvalue()
    except Exception as exc:
        raise RuntimeError(f"Failed to encode Supertonic audio as WAV: {exc}") from exc


def _call_tts(engine, text, voice_value, options):
    kwargs = {
        "text": text,
        "voice": voice_value,
        "lang": options.get("lang", "na"),
        "speed": options.get("speed", 1.0),
        "total_steps": options.get("total_steps", 8),
        "max_chunk_length": options.get("max_chunk_length", 300),
        "silence_duration": options.get("silence_duration", 0.3),
    }
    methods = ("generate", "synthesize", "tts", "__call__")
    last_error = None
    for method_name in methods:
        method = engine if method_name == "__call__" else getattr(engine, method_name, None)
        if method is None:
            continue
        call_variants = [kwargs]
        voice_style_kwargs = dict(kwargs)
        voice_style_kwargs["voice_style"] = voice_style_kwargs.pop("voice")
        call_variants.insert(0, voice_style_kwargs)
        if method_name == "synthesize":
            call_variants = [voice_style_kwargs, kwargs]
        elif method_name in ("generate", "tts", "__call__"):
            call_variants = [kwargs, voice_style_kwargs]
        try:
            for call_kwargs in call_variants:
                try:
                    return method(**call_kwargs)
                except TypeError as exc:
                    last_error = exc
                    continue
        except TypeError as exc:
            last_error = exc
        for call_kwargs in call_variants:
            reduced = dict(call_kwargs)
            reduced.pop("max_chunk_length", None)
            reduced.pop("silence_duration", None)
            try:
                return method(**reduced)
            except TypeError as exc:
                last_error = exc
                continue
        try:
            return method(text, voice_value)
        except TypeError as exc:
            last_error = exc
            continue
    if last_error:
        raise last_error
    raise RuntimeError("No compatible Supertonic synthesis method found")


def generate_one(task):
    text = (task.get("text") or "").strip()
    if not text:
        raise ValueError("Empty text")

    cache_path = task.get("cache_path")
    engine = _get_engine(cache_path, auto_download=bool(task.get("auto_download", False)))
    voice_key = task.get("voice") or "M1"
    custom_voice_path = task.get("custom_voice_path")
    voice_value = _load_custom_voice(engine, custom_voice_path) if custom_voice_path else _load_builtin_voice_style(engine, voice_key)
    audio = _call_tts(engine, text, voice_value, task)
    return _to_wav_bytes(audio)


def handle_request(request):
    if request.get("action") == "generate_batch":
        results = []
        for task in request.get("tasks", []):
            try:
                audio = generate_one(task)
                results.append({"status": "ok", "audio_b64": base64.b64encode(audio).decode("ascii")})
            except Exception as exc:
                results.append({"status": "error", "message": str(exc)})
        return {"status": "ok", "results": results}

    audio = generate_one(request)
    return {"status": "ok", "audio_b64": base64.b64encode(audio).decode("ascii")}


def main():
    log("Supertonic runner ready")
    for line in sys.stdin.buffer:
        try:
            request = json.loads(line.decode("utf-8"))
            response = handle_request(request)
        except Exception as exc:
            log(traceback.format_exc())
            response = {"status": "error", "message": str(exc)}
        sys.stdout.write(json.dumps(response) + "\n")
        sys.stdout.flush()


if __name__ == "__main__":
    main()
