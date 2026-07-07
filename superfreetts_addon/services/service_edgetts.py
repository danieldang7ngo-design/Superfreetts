import aiohttp
import asyncio
import random
import re
import socket
import threading
import time
import unicodedata
import edge_tts
from typing import List, Optional

from .. import voice
from .. import service
from .. import errors
from .. import constants
from .. import languages
from .. import logging_utils
from .. import batch_constants

logger = logging_utils.get_child_logger(__name__)

DEFAULT_MAX_RETRIES = 3
DEFAULT_INITIAL_DELAY_MIN_MS = 0
DEFAULT_INITIAL_DELAY_MAX_MS = 250
DEFAULT_WAVE_START_STAGGER_MS = 150
DEFAULT_RETRY_BACKOFF_SECONDS = 3
DEFAULT_BATCH_WAVE_SIZE = 1
DEFAULT_EDGE_CONNECTIVITY_BACKOFF_SECONDS = 15

_request_gate_lock = threading.Lock()
_request_gate = None
_request_gate_size = None
_edge_connectivity_failure_until = 0.0


def _get_request_gate(size):
    global _request_gate, _request_gate_size
    size = max(1, int(size or 1))
    with _request_gate_lock:
        if _request_gate is None or _request_gate_size != size:
            _request_gate = threading.BoundedSemaphore(size)
            _request_gate_size = size
        return _request_gate


def _is_recent_connectivity_failure():
    return time.time() < _edge_connectivity_failure_until


def _mark_edge_connectivity_failure():
    global _edge_connectivity_failure_until
    _edge_connectivity_failure_until = time.time() + DEFAULT_EDGE_CONNECTIVITY_BACKOFF_SECONDS


def _is_edge_connectivity_available():
    if _is_recent_connectivity_failure():
        return False
    try:
        with socket.create_connection(("www.bing.com", 443), timeout=5):
            return True
    except Exception:
        _mark_edge_connectivity_failure()
        return False

def run_async_safe(coro):
    """
    Safely run an asyncio coroutine from a synchronous context.
    Works whether or not an event loop is already running in the current thread.
    """
    try:
        # Check if there's a running loop in the current thread
        asyncio.get_running_loop()
        # If yes, we can't use asyncio.run() or run_until_complete() here.
        # We run it in a separate thread with its own loop to avoid blocking/crashing.
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            return executor.submit(asyncio.run, coro).result()
    except RuntimeError:
        # No loop running in this thread, safe to use asyncio.run()
        return asyncio.run(coro)

class EdgeTTS(service.ServiceBase):
    def __init__(self):
        service.ServiceBase.__init__(self)

    @property
    def service_type(self) -> constants.ServiceType:
        return constants.ServiceType.tts

    @property
    def service_fee(self) -> constants.ServiceFee:
        return constants.ServiceFee.free

    def enabled_by_default(self):
        return True

    def configuration_options(self):
        return {}

    def advanced_configuration_options(self):
        """Advanced settings for EdgeTTS (hidden in dropdown)"""
        return {
            'concurrency_workers': ('number', f'Concurrency Workers (1-{batch_constants.EDGETTS_MAX_WORKERS})', batch_constants.EDGETTS_MAX_WORKERS, 1, batch_constants.EDGETTS_MAX_WORKERS),
            'max_retries': ('number', 'Retry Attempts', DEFAULT_MAX_RETRIES, 0, 5),
            'initial_delay_min_ms': ('number', 'Minimum Request Jitter (ms)', DEFAULT_INITIAL_DELAY_MIN_MS, 0, 10000),
            'initial_delay_max_ms': ('number', 'Maximum Request Jitter (ms)', DEFAULT_INITIAL_DELAY_MAX_MS, 0, 15000),
            'wave_start_stagger_ms': ('number', 'Wave Start Stagger (ms)', DEFAULT_WAVE_START_STAGGER_MS, 0, 2000),
            'retry_backoff_seconds': ('number', 'Retry Backoff Step (seconds)', DEFAULT_RETRY_BACKOFF_SECONDS, 1, 30),
            'debug_logging': ('bool', 'Enable Debug Logging for EdgeTTS', False)
        }

    def _get_int_config(self, key, default_value):
        try:
            return int(self.get_configuration_value_optional(key, default_value))
        except (TypeError, ValueError):
            return default_value

    def _build_edge_options(self, options: dict):
        speed_val = int(options.get('speed', 0) or 0)
        pitch_val = int(options.get('pitch', 0) or 0)
        volume_val = int(options.get('volume', 0) or 0)
        rate_str = f"{'+' if speed_val >= 0 else ''}{speed_val}%"
        pitch_str = f"{'+' if pitch_val >= 0 else ''}{pitch_val}Hz"
        volume_str = f"{'+' if volume_val >= 0 else ''}{volume_val}%"
        return rate_str, pitch_str, volume_str

    def _is_connectivity_error(self, exception: Exception) -> bool:
        return isinstance(exception, (aiohttp.ClientConnectionError, asyncio.TimeoutError))

    def _is_no_audio_error(self, exception: Exception):
        error_type = type(exception).__name__
        error_message = str(exception)
        return (
            'NoAudioReceived' in error_type
            or 'No audio' in error_message
            or 'no audio' in error_message.lower()
        )

    def _friendly_error_message(self, exception: Exception, text: str, voice_key: str):
        if self._is_connectivity_error(exception):
            return (
                "Microsoft Edge TTS could not connect to the internet. "
                "Please check your connection and try again. "
                f"Voice: {voice_key}; text: {text[:120]}"
            )
        if self._is_no_audio_error(exception):
            return (
                "Microsoft Edge TTS returned no audio. This usually means the service "
                "temporarily limited the connection because too many requests were made. "
                "Please wait 15-30 minutes, or reduce EdgeTTS concurrency/delay settings. "
                f"Voice: {voice_key}; text: {text[:120]}"
            )
        return str(exception)

    def _normalize_text(self, text: str):
        text = unicodedata.normalize('NFC', str(text or ''))
        text = re.sub(r'[\u200b\u200c\u200d\u200e\u200f\ufeff]', '', text)
        text = ''.join(ch if ch in '\n\r\t' or unicodedata.category(ch)[0] != 'C' else ' ' for ch in text)
        return re.sub(r'\s+', ' ', text).strip()

    def voice_list(self) -> List[voice.TtsVoice_v3]:
        # Use run_async_safe to avoid loop conflicts
        try:
            voices_data = run_async_safe(edge_tts.VoicesManager.create())

            voices = []
            for v in voices_data.voices:
                # Map EdgeTTS locale to AudioLanguage
                lang_key = v['Locale'].replace('-', '_')
                audio_lang = None
                try:
                    audio_lang = languages.AudioLanguage[lang_key]
                except KeyError:
                    # Fuzzy matching
                    for al in languages.AudioLanguage:
                        if al.name.startswith(v['Locale'].split('-')[0]):
                            audio_lang = al
                            break
                
                if audio_lang:
                    gender = constants.Gender.Male if v['Gender'] == 'Male' else constants.Gender.Female
                    voice_options = {
                        'speed': {
                            'type': 'number_int', 'default': 0, 'min': -50, 'max': 50,
                            'label': 'Speed %',
                            'tooltip': 'Speaking rate adjustment. 0 = normal, +50 = 50% faster, -50 = 50% slower'
                        },
                        'pitch': {
                            'type': 'number_int', 'default': 0, 'min': -50, 'max': 50,
                            'label': 'Pitch (Hz)',
                            'tooltip': 'Voice pitch adjustment in Hz. 0 = normal, +50 = higher pitch, -50 = lower pitch'
                        },
                        'volume': {
                            'type': 'number_int', 'default': 0, 'min': -50, 'max': 50,
                            'label': 'Volume %',
                            'tooltip': 'Volume adjustment. 0 = normal, +50 = 50% louder, -50 = 50% quieter'
                        },
                    }
                    voices.append(voice.build_voice_v3(
                        name=v['FriendlyName'],
                        gender=gender,
                        language=audio_lang,
                        service=self,
                        voice_key=v['ShortName'],
                        options=voice_options
                    ))
            return voices
        except Exception as e:
            logger.error(f"EdgeTTS: Error fetching voice list: {e}")
            return []

    def get_tts_audio(self, source_text, voice: voice.TtsVoice_v3, options):
        # Implementation for single request
        results = self.get_tts_audio_batch([source_text], voice, options)
        if results and results[0]:
            return results[0]
        raise errors.RequestError(source_text, voice, "EdgeTTS failed to generate audio")

    def get_tts_audio_batch(self, source_texts: List[str], voice: voice.TtsVoice_v3, options: dict) -> List[Optional[bytes]]:
        """
        Synthesize multiple texts in a single asyncio event loop using gather().
        This is much faster than running multiple sequential or even multi-threaded 
        asyncio.run() calls because it reuses loop overhead.
        """
        if not source_texts:
            return []

        if not _is_edge_connectivity_available():
            if self.get_configuration_value_optional('debug_logging', False):
                logger.warning("EdgeTTS: connectivity check failed before batch execution")
            return [None] * len(source_texts)

        debug_enabled = self.get_configuration_value_optional('debug_logging', False)
        max_retries = self._get_int_config('max_retries', DEFAULT_MAX_RETRIES)
        initial_delay_min_ms = self._get_int_config('initial_delay_min_ms', DEFAULT_INITIAL_DELAY_MIN_MS)
        initial_delay_max_ms = self._get_int_config('initial_delay_max_ms', DEFAULT_INITIAL_DELAY_MAX_MS)
        wave_start_stagger_ms = self._get_int_config('wave_start_stagger_ms', DEFAULT_WAVE_START_STAGGER_MS)
        retry_backoff_seconds = self._get_int_config('retry_backoff_seconds', DEFAULT_RETRY_BACKOFF_SECONDS)
        requested_workers = self._get_int_config('concurrency_workers', DEFAULT_BATCH_WAVE_SIZE)
        concurrency_workers = min(batch_constants.EDGETTS_MAX_WORKERS, max(1, requested_workers))

        if initial_delay_max_ms < initial_delay_min_ms:
            initial_delay_min_ms, initial_delay_max_ms = initial_delay_max_ms, initial_delay_min_ms

        normalized_texts = [self._normalize_text(text) for text in source_texts]
        
        async def _stream_batch():
            rate_str, pitch_str, volume_str = self._build_edge_options(options)
            request_gate = _get_request_gate(concurrency_workers)
            
            async def _acquire_request_slot():
                await asyncio.to_thread(request_gate.acquire)

            async def _fetch_one(index, text, worker_index):
                if worker_index > 0 and wave_start_stagger_ms > 0:
                    await asyncio.sleep((worker_index * wave_start_stagger_ms) / 1000)

                if initial_delay_max_ms > 0:
                    delay = random.uniform(initial_delay_min_ms, initial_delay_max_ms) / 1000
                    await asyncio.sleep(delay)

                for attempt in range(max_retries + 1):
                    retry_delay = None
                    await _acquire_request_slot()
                    try:
                        if debug_enabled:
                            logger.debug(
                                f"EdgeTTS: Starting synthesis for '{text[:20]}...' "
                                f"(attempt {attempt + 1}/{max_retries + 1})"
                            )

                        communicate = edge_tts.Communicate(
                            text, voice.voice_key,
                            rate=rate_str, pitch=pitch_str, volume=volume_str
                        )

                        async def _collect_audio():
                            data = b""
                            async for chunk in communicate.stream():
                                if chunk["type"] == "audio":
                                    data += chunk["data"]
                            return data

                        data = await asyncio.wait_for(
                            _collect_audio(),
                            timeout=batch_constants.EDGETTS_TASK_TIMEOUT_SECONDS,
                        )

                        if data:
                            return index, data

                        raise errors.RequestError(text, voice, "EdgeTTS returned empty audio")
                    except Exception as e:
                        if self._is_connectivity_error(e):
                            _mark_edge_connectivity_failure()
                            friendly_message = self._friendly_error_message(e, text, voice.voice_key)
                            logger.warning(
                                f"EdgeTTS Batch: Connectivity exception for text '{text[:20]}...': {friendly_message}"
                            )
                            return index, None
                        elif attempt < max_retries:
                            retry_delay = (attempt + 1) * retry_backoff_seconds
                            if debug_enabled:
                                logger.debug(
                                    f"EdgeTTS: retrying '{text[:20]}...' in {retry_delay}s after: {e}"
                                )
                        else:
                            friendly_message = self._friendly_error_message(e, text, voice.voice_key)
                            logger.warning(f"EdgeTTS Batch: Exception for text '{text[:20]}...': {friendly_message}")
                            return index, None
                    finally:
                        request_gate.release()
                    if retry_delay is not None:
                        await asyncio.sleep(retry_delay)
                        continue

            results = [None] * len(normalized_texts)
            work_queue = asyncio.Queue()
            for item in enumerate(normalized_texts):
                work_queue.put_nowait(item)

            async def _worker(worker_index):
                while True:
                    try:
                        index, text = work_queue.get_nowait()
                    except asyncio.QueueEmpty:
                        return
                    try:
                        result_index, data = await _fetch_one(index, text, worker_index)
                        results[result_index] = data
                    finally:
                        work_queue.task_done()

            worker_count = min(concurrency_workers, len(normalized_texts))
            workers = [
                asyncio.create_task(_worker(worker_index))
                for worker_index in range(worker_count)
            ]
            await asyncio.gather(*workers)
            return results

        try:
            start_time = time.time()
            results = run_async_safe(_stream_batch())
            
            if debug_enabled:
                duration = time.time() - start_time
                success_count = sum(1 for r in results if r is not None)
                try:
                    from .. import service_logger
                    service_logger.write_log('edgetts', 'runtime', 'OK', 'Batch generated', {
                        'Count': f'{success_count}/{len(source_texts)}',
                        'Duration': f'{duration:.2f}s'
                    })
                except: pass
            
            return results
        except Exception as e:
            logger.error(f"EdgeTTS: Batch execution failed: {e}")
            return [None] * len(source_texts)
