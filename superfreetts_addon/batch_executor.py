"""
Unified Batch Executor - Simplified threading, resource management, and caching.

Replaces:
  - the old MemoryPool/SmartLRUCache helpers (only RSS monitoring remains
    in resource_manager.py)
  - batch_state_manager.py (complex checkpoint logic)
  - Complex threading in superfreetts.py

Design:
  - Single ThreadPoolExecutor for all batch tasks
  - Unified cache system (no 3 separate caches)
  - Simple resource monitoring (RAM tracking only)
  - Lightweight checkpoint system
  - Zero unnecessary locks
"""

import os
import gc
import json
import threading
import concurrent.futures
from typing import Dict, Optional, Any, List
from datetime import datetime
from collections import OrderedDict

from . import batch_constants
from . import logging_utils
from . import resource_manager

logger = logging_utils.get_child_logger(__name__)


class BoundedThreadPoolExecutor(concurrent.futures.ThreadPoolExecutor):
    """
    ThreadPoolExecutor with a bounded queue.
    Uses a semaphore to cap queued submissions and avoids indefinite blocking
    when the caller is trying to stop a large batch.
    """
    def __init__(self, max_workers, thread_name_prefix='', max_waiting_tasks=50):
        super().__init__(max_workers=max_workers, thread_name_prefix=thread_name_prefix)
        self._semaphore = threading.Semaphore(max_workers + max_waiting_tasks)

    def submit(self, fn, *args, **kwargs):
        timeout = kwargs.pop('timeout', None)
        if timeout is None:
            self._semaphore.acquire()
        else:
            if not self._semaphore.acquire(timeout=timeout):
                raise TimeoutError('Timed out waiting for executor slot')
        try:
            future = super().submit(fn, *args, **kwargs)
        except Exception:
            self._semaphore.release()
            raise
        future.add_done_callback(lambda x: self._semaphore.release())
        return future


def _detect_service_from_task(task: Dict) -> str:
    """Detect the TTS service for a task from its selected voice."""
    try:
        voice = task.get('chosen_voice')
        if not voice:
            # Fallback to older mechanism if chosen_voice is not set
            batch = task.get('batch')
            if not batch or not hasattr(batch, 'voice_selection'):
                return 'default'

            voice_sel = batch.voice_selection
            if hasattr(voice_sel, '_voice_with_options') and voice_sel._voice_with_options:
                voice = voice_sel._voice_with_options
            elif hasattr(voice_sel, 'voice') and voice_sel.voice:
                voice = voice_sel.voice
            elif hasattr(voice_sel, '_voice_list') and voice_sel._voice_list:
                voice = voice_sel._voice_list[0]
            elif hasattr(voice_sel, 'voice_list') and voice_sel.voice_list:
                voice = voice_sel.voice_list[0]

        if not voice:
            return 'default'

        if hasattr(voice, 'voice_id') and hasattr(voice.voice_id, 'service'):
            return voice.voice_id.service
        if hasattr(voice, 'service'):
            return voice.service
        if hasattr(voice, 'voice') and hasattr(voice.voice, 'service'):
            return voice.voice.service
        for attr in ['engine', 'provider', 'tts_engine', 'service_name']:
            if hasattr(voice, attr):
                return getattr(voice, attr)
    except Exception as e:
        logger.debug(f"[BATCH] Failed to detect service: {e}")

    return 'default'


class UnifiedCache:
    """Minimal LRU cache using OrderedDict. Supports size-based or entry-count eviction."""
    
    def __init__(self, max_size_mb: int = 100):
        self.cache = OrderedDict()
        self.max_entries = 1000
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.current_size = 0
        self.hits = 0
        self.misses = 0
        self._lock = threading.RLock()
    
    @property
    def _use_size(self) -> bool:
        return self.max_size_bytes > 0
    
    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            if key in self.cache:
                self.cache.move_to_end(key)
                self.hits += 1
                val = self.cache[key]
                # In size mode the stored value is (value, size_bytes).  Do
                # not unwrap arbitrary tuples when size mode is disabled:
                # callers legitimately cache tuple values too.
                if self._use_size and isinstance(val, tuple) and len(val) == 2:
                    return val[0]
                return val
            self.misses += 1
            return None
    
    def put(self, key: str, value: Any, size_bytes: int = 0):
        with self._lock:
            if self._use_size:
                if size_bytes == 0:
                    size_bytes = len(value) if isinstance(value, (bytes, str)) else 1000

                if key in self.cache:
                    old_val = self.cache[key]
                    if isinstance(old_val, tuple):
                        self.current_size -= old_val[1]
                    del self.cache[key]

                self.cache[key] = (value, size_bytes)
                self.current_size += size_bytes

                while self.current_size > self.max_size_bytes and self.cache:
                    oldest_key, (oldest_val, oldest_size) = self.cache.popitem(last=False)
                    self.current_size -= oldest_size
            else:
                if key in self.cache:
                    del self.cache[key]
                self.cache[key] = value
                while len(self.cache) > self.max_entries and self.cache:
                    self.cache.popitem(last=False)
    
    def clear(self):
        with self._lock:
            self.cache.clear()
            self.current_size = 0
    
    def stats(self) -> dict:
        with self._lock:
            total = max(self.hits + self.misses, 1)
            return {
                'entries': len(self.cache),
                'hits': self.hits,
                'misses': self.misses,
                'hit_rate': f"{(self.hits / total * 100):.1f}%",
            }


class BoundedLRUDict:
    """Small thread-safe LRU mapping used for processed-text caching.

    A plain ``dict`` grew without bound across long Anki sessions (20k-note
    batches).  This keeps a fixed ceiling and exposes the mapping surface the
    batch orchestrator needs (``in``, ``[]``, ``clear``).
    """

    def __init__(self, max_entries: int = 2048):
        self.max_entries = max(1, int(max_entries))
        self._data = OrderedDict()
        self._lock = threading.RLock()

    def __contains__(self, key) -> bool:
        with self._lock:
            return key in self._data

    def __getitem__(self, key):
        with self._lock:
            if key not in self._data:
                raise KeyError(key)
            self._data.move_to_end(key)
            return self._data[key]

    def __setitem__(self, key, value) -> None:
        with self._lock:
            if key in self._data:
                self._data.move_to_end(key)
            self._data[key] = value
            while len(self._data) > self.max_entries:
                self._data.popitem(last=False)

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def clear(self) -> None:
        with self._lock:
            self._data.clear()

    def __len__(self) -> int:
        with self._lock:
            return len(self._data)


class SimpleResourceMonitor:
    """
    Lightweight resource monitoring - RAM only, no CPU/threading complexity.
    """
    
    def __init__(self, max_ram_mb: int = 3000):
        self.max_ram_mb = max_ram_mb
        self.process = None  # Initialize first
        self._has_psutil = False
        
        try:
            import psutil
            self.process = psutil.Process(os.getpid())
            self._has_psutil = True
        except (ImportError, Exception):
            logger.debug("[BATCH] psutil unavailable, using platform memory fallback")
        
        self.initial_ram_mb = self._get_ram_usage()  # Now safe to call
        # GC hysteresis baseline.  Peak RSS (ru_maxrss) never decreases, so
        # using it as "current" made the monitor trigger GC on every chunk
        # after a one-off allocation spike.  Track the RSS at the last GC
        # instead and lower the baseline when memory is actually released.
        self._last_gc_ram_mb = self.initial_ram_mb
        self._last_gc_items = 0
        self._gc_count = 0
    
    def _get_ram_usage(self) -> int:
        """Get current RAM usage in MB"""
        if not self.process:
            return resource_manager._get_process_ram_usage_without_psutil()
        try:
            return int(self.process.memory_info().rss / 1024 / 1024)
        except Exception:
            return resource_manager._get_process_ram_usage_without_psutil()
    
    def should_gc(self, items_processed: int) -> bool:
        """
        GC when RSS has grown >300MB since the last collection, or after
        every 100 completed items since the last collection.

        The baseline is current RSS, not peak RSS.  If the OS reports lower
        RSS than the baseline (memory was released), move the baseline down
        so a later spike is measured from the new, lower level.
        """
        ram_usage = self._get_ram_usage()
        if ram_usage < self._last_gc_ram_mb:
            self._last_gc_ram_mb = ram_usage

        ram_growth = ram_usage - self._last_gc_ram_mb
        interval_elapsed = (
            items_processed > 0
            and items_processed - self._last_gc_items >= 100
        )
        
        # Aggressive but simple: every 100 items OR significant growth
        return ram_growth > 300 or interval_elapsed
    
    def maybe_gc(self, items_processed: int):
        """Run GC if needed and reset the hysteresis baseline."""
        if self.should_gc(items_processed):
            gc.collect()
            self._last_gc_ram_mb = self._get_ram_usage()
            self._last_gc_items = items_processed
            self._gc_count += 1
            logger.debug(f"[BATCH] GC triggered (items={items_processed}, count={self._gc_count})")
    
    def get_status(self) -> str:
        """Get RAM status string"""
        ram = self._get_ram_usage()
        return f"RAM: {ram}MB/{self.max_ram_mb}MB"


CHECKPOINT_VERSION = 2
CHECKPOINT_STATUS_GENERATED = "generated"
CHECKPOINT_STATUS_APPLIED = "applied"


class CheckpointManager:
    """Crash-recovery checkpoint keyed by stable note ID.

    The old format stored two parallel index lists: ``completed_indices``
    (positions in the original selection) next to ``note_id_list``.  A resume
    ran on a filtered list but wrote its indices back as if they indexed the
    original list, so the next resume skipped the wrong notes.

    v2 stores the original note id list once and a ``{note_id: status}`` map
    (``generated`` / ``applied``).  Writes are atomic (temp file +
    ``os.replace``): a crash mid-write keeps the previous checkpoint intact.
    Legacy v1 files are migrated on load.
    """

    def __init__(self, state_dir: Optional[str] = None):
        self.state_dir = state_dir or self._get_default_state_dir()
        self._lock = threading.Lock()
        os.makedirs(self.state_dir, exist_ok=True)

    def _get_default_state_dir(self) -> str:
        """Get default checkpoint directory"""
        addon_dir = os.path.dirname(os.path.dirname(__file__))
        return os.path.join(addon_dir, 'user_files', 'batch_state')

    def _get_path(self, batch_name: str) -> str:
        """Get checkpoint file path"""
        safe_name = "".join(c for c in batch_name if c.isalnum() or c in ('-', '_'))[:50]
        return os.path.join(self.state_dir, f"{safe_name}.checkpoint.json")

    def save(self, batch_name: str, note_ids: List[int], statuses: Dict, errors: Dict = None):
        """Atomically persist the note id -> status map for a batch."""
        with self._lock:
            try:
                path = self._get_path(batch_name)
                data = {
                    'version': CHECKPOINT_VERSION,
                    'batch_name': batch_name,
                    'note_ids': list(note_ids),
                    'statuses': {str(key): value for key, value in statuses.items()},
                    'errors': {str(key): value for key, value in (errors or {}).items()},
                    'timestamp': datetime.now().isoformat(),
                }
                tmp_path = path + '.tmp'
                with open(tmp_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f)
                    f.flush()
                    os.fsync(f.fileno())
                os.replace(tmp_path, path)
            except Exception as e:
                logger.warning(f"[BATCH] Checkpoint save failed: {e}")

    def load(self, batch_name: str) -> Optional[dict]:
        """Load a checkpoint, migrating legacy v1 files to the v2 shape."""
        with self._lock:
            try:
                path = self._get_path(batch_name)
                if os.path.exists(path):
                    with open(path, 'r', encoding='utf-8') as f:
                        return self._migrate(json.load(f))
            except Exception as e:
                logger.warning(f"[BATCH] Checkpoint load failed: {e}")
        return None

    @staticmethod
    def _migrate(data: dict) -> dict:
        if data.get('statuses') is not None:
            return {
                'version': CHECKPOINT_VERSION,
                'batch_name': data.get('batch_name', ''),
                'note_ids': list(data.get('note_ids') or []),
                'statuses': {str(k): v for k, v in (data.get('statuses') or {}).items()},
                'errors': {str(k): v for k, v in (data.get('errors') or {}).items()},
                'timestamp': data.get('timestamp'),
            }
        # Legacy v1: completed_indices are positions in note_id_list.
        note_ids = list(data.get('note_id_list') or [])
        statuses = {}
        for index in data.get('completed_indices') or []:
            if isinstance(index, int) and 0 <= index < len(note_ids):
                statuses[str(note_ids[index])] = CHECKPOINT_STATUS_APPLIED
        return {
            'version': CHECKPOINT_VERSION,
            'batch_name': data.get('batch_name', ''),
            'note_ids': note_ids,
            'statuses': statuses,
            'errors': {str(k): v for k, v in (data.get('errors') or {}).items()},
            'timestamp': data.get('timestamp'),
        }

    def remove(self, batch_name: str):
        """Remove checkpoint after batch complete"""
        with self._lock:
            try:
                path = self._get_path(batch_name)
                if os.path.exists(path):
                    os.remove(path)
            except Exception as e:
                logger.warning(f"[BATCH] Checkpoint remove failed: {e}")


class BatchCheckpoint:
    """Per-note status for one batch run, flushed to disk in chunks.

    Resume policy is **at-least-once**: notes marked ``applied`` are skipped,
    everything else is retried.  Retrying a ``generated`` note is free (the
    audio is content-addressed in the cache) and applying the same audio file
    twice is idempotent, so no note can be lost; a note can only be applied
    again after a crash that happened after the audio was written but before
    the checkpoint flush.
    """

    def __init__(self, manager: CheckpointManager, batch_name: str, note_ids: List[int], flush_every: Optional[int] = None):
        self.manager = manager
        self.batch_name = batch_name
        self.note_ids = list(note_ids)
        self.errors: Dict[str, str] = {}
        self.enabled = True
        self._flush_every = int(flush_every or batch_constants.CHECKPOINT_FLUSH_EVERY)
        self._statuses: Dict[str, str] = {}
        self._pending_writes = 0

    def load_existing(self) -> int:
        """Load a previous checkpoint; returns how many notes are applied."""
        data = self.manager.load(self.batch_name)
        if not data:
            return 0
        # Keep ids that a previous (possibly filtered) run stored: statuses for
        # notes outside this run must survive so they are never applied twice.
        for stored_id in data.get('note_ids') or []:
            if stored_id not in self.note_ids:
                self.note_ids.append(stored_id)
        allowed = {str(note_id) for note_id in self.note_ids}
        self._statuses = {
            key: value for key, value in (data.get('statuses') or {}).items()
            if key in allowed
        }
        self.errors = {
            key: value for key, value in (data.get('errors') or {}).items()
            if key in allowed
        }
        return sum(1 for value in self._statuses.values() if value == CHECKPOINT_STATUS_APPLIED)

    def status_of(self, note_id) -> Optional[str]:
        return self._statuses.get(str(note_id))

    def is_applied(self, note_id) -> bool:
        return self.status_of(note_id) == CHECKPOINT_STATUS_APPLIED

    def pending_note_ids(self) -> List[int]:
        return [note_id for note_id in self.note_ids if not self.is_applied(note_id)]

    def mark_generated(self, note_ids: List[int]) -> None:
        self._mark(note_ids, CHECKPOINT_STATUS_GENERATED)

    def mark_applied(self, note_ids: List[int], force_flush: bool = True) -> None:
        self._mark(note_ids, CHECKPOINT_STATUS_APPLIED, force_flush=force_flush)

    def mark_error(self, note_id, error) -> None:
        self.errors[str(note_id)] = str(error)
        self._pending_writes += 1

    def _mark(self, note_ids, status: str, force_flush: bool = False) -> None:
        changed = 0
        for note_id in note_ids:
            key = str(note_id)
            current = self._statuses.get(key)
            # Never downgrade an applied note back to generated.
            if current == CHECKPOINT_STATUS_APPLIED and status != CHECKPOINT_STATUS_APPLIED:
                continue
            if current != status:
                self._statuses[key] = status
                changed += 1
        self._pending_writes += changed
        if force_flush or self._pending_writes >= self._flush_every:
            self.flush()

    def flush(self) -> None:
        """Write the checkpoint if there is something new to persist."""
        if not self.enabled:
            return
        try:
            self.manager.save(self.batch_name, self.note_ids, self._statuses, self.errors)
            self._pending_writes = 0
        except Exception as e:
            logger.warning(f"[BATCH] Failed to save checkpoint: {e}")
            self.enabled = False

    def remove(self) -> None:
        """Delete the checkpoint and stop any later flush from recreating it."""
        self.enabled = False
        self.manager.remove(self.batch_name)


class NullCheckpoint:
    """No-op checkpoint for preview generation, which never applies notes."""

    enabled = False

    def mark_generated(self, note_ids):
        pass

    def mark_applied(self, note_ids, force_flush: bool = True):
        pass

    def mark_error(self, note_id, error):
        pass

    def flush(self):
        pass

    def remove(self):
        pass


class UnifiedBatchExecutor:
    """
    Single executor for all batch audio generation.
    
    Features:
    - ThreadPoolExecutor core (4-8 workers)
    - Unified cache (100MB default)
    - Simple RAM monitoring + GC
    - Lightweight checkpoint recovery
    - Real-time progress callbacks
    
    Usage:
        executor = UnifiedBatchExecutor(max_workers=4)
        pool = executor.get_executor()
        future = pool.submit(work_function, task)
    """
    
    def __init__(self, max_workers: int = 1, max_ram_mb: int = 3000, cache_size_mb: int = 100):
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)
        self.monitor = SimpleResourceMonitor(max_ram_mb)
        self.cache = UnifiedCache(max_size_mb=cache_size_mb)
        self.checkpoint = CheckpointManager()
        self.max_workers = max_workers
        self.items_processed = 0
        self._shutdown = False
    
    def get_executor(self, service_name: Optional[str] = None) -> concurrent.futures.ThreadPoolExecutor:
        """Return the underlying pool so callers can use either executor type.

        ``service_name`` is accepted for interface parity with
        ``MultiEngineExecutor.get_executor(service_name)``; the unified
        fallback has only one pool and routes everything through it.
        """
        return self.executor

    def detect_service(self, task: Dict) -> str:
        """Interface parity with MultiEngineExecutor for fallback batches."""
        return _detect_service_from_task(task)

    def shutdown(self, wait: bool = True):
        """Shutdown thread pool"""
        self._shutdown = True
        try:
            self.executor.shutdown(wait=wait)
        except Exception as e:
            logger.warning(f"[BATCH] Executor shutdown error: {e}")
    
    def reset(self):
        """Clear all caches and reset state"""
        self.cache.clear()
        self.items_processed = 0
        gc.collect()
        logger.info("[BATCH] Executor reset")


# Global singleton
_executor: Optional[UnifiedBatchExecutor] = None


class MultiEngineExecutor:
    """
    Advanced executor supporting different worker counts per TTS engine.
    
    Example config:
        {
            'Piper': 2,      # 2 workers for Piper
            'Kokoro': 1,     # 1 worker for Kokoro
            'EdgeTTS': 2,    # 2 workers for EdgeTTS (online)
            'default': 4     # fallback for unknown engines
        }
    
    Usage:
        executor = MultiEngineExecutor(engine_config={
            'Piper': 2,
            'Kokoro': 1,
            'default': 4
        })
        pool = executor.get_executor('Piper')
        future = pool.submit(work_function, task)
    """
    
    def __init__(self, engine_config: Dict[str, int] = None, cache_size_mb: int = 100):
        """
        Args:
            engine_config: Dict mapping engine name → worker count
            cache_size_mb: Unified cache size in MB
        """
        from . import system_utils
        cpu_default = max(1, system_utils.get_cpu_threads())
        self.engine_config = engine_config or {
            'Piper': cpu_default,
            'Kokoro': cpu_default,
            'EdgeTTS': batch_constants.EDGETTS_MAX_WORKERS,
            'MMS': cpu_default,
            'Supertonic': cpu_default,
            'default': cpu_default
        }
        
        # Create executors per engine
        self.executors: Dict[str, BoundedThreadPoolExecutor] = {}
        for engine_name, worker_count in self.engine_config.items():
            if engine_name != 'default':
                self.executors[engine_name] = BoundedThreadPoolExecutor(
                    max_workers=max(1, worker_count),
                    thread_name_prefix=f"TTS-{engine_name}",
                    max_waiting_tasks=20 # Bounded backpressure
                )
                logger.info(f"[BATCH] Created bounded executor for {engine_name}: {worker_count} workers")
        
        # Default executor for unknown engines
        self.default_executor = BoundedThreadPoolExecutor(
            max_workers=max(1, self.engine_config.get('default', 1)),
            thread_name_prefix="TTS-Default",
            max_waiting_tasks=20
        )
        
        self.monitor = SimpleResourceMonitor()
        self.cache = UnifiedCache(max_size_mb=cache_size_mb)
        self.checkpoint = CheckpointManager()
        self._shutdown = False
    
    def get_executor(self, service_name: str) -> concurrent.futures.ThreadPoolExecutor:
        """Get executor for given service/engine."""
        service_pool_map = {
            'EdgeTTS': 'EdgeTTS',
            'SupertonicTTS': 'Supertonic',
            'PiperTTS': 'Piper',
            'KokoroTTS': 'Kokoro',
            'MmsTTS': 'MMS',
        }
        normalized = service_pool_map.get(service_name, service_name)
        if normalized != service_name:
            logger.info(f"[BATCH] Normalized service name: {service_name} → {normalized}")

        executor = self.executors.get(normalized, self.default_executor)
        logger.info(f"[BATCH] get_executor({service_name}): using {normalized} with {executor._max_workers} workers")
        return executor
    
    def detect_service(self, task: Dict) -> str:
        """Detect TTS service name from task's selected voice."""
        return _detect_service_from_task(task)
    
    def shutdown(self, wait: bool = True):
        """Shutdown all executors"""
        self._shutdown = True
        for service, executor in self.executors.items():
            try:
                executor.shutdown(wait=wait)
            except Exception as e:
                logger.warning(f"[BATCH] {service} executor shutdown error: {e}")
        
        try:
            self.default_executor.shutdown(wait=wait)
        except Exception as e:
            logger.warning(f"[BATCH] Default executor shutdown error: {e}")
    
    def reset(self):
        """Reset all caches"""
        self.cache.clear()
        gc.collect()
        logger.info("[BATCH] MultiEngine executor reset")


def get_batch_executor(max_workers: int = 1) -> UnifiedBatchExecutor:
    """Get or create global batch executor"""
    global _executor
    if _executor is None or getattr(_executor, '_shutdown', False):
        _executor = UnifiedBatchExecutor(max_workers=max_workers)
    return _executor



# Multi-engine executor singleton
_multi_executor: Optional[MultiEngineExecutor] = None


def get_multi_engine_executor(engine_config: Dict[str, int] = None) -> MultiEngineExecutor:
    """
    Get or create multi-engine executor.
    
    Args:
        engine_config: {service_name: worker_count}
        Example:
            {
                'Piper': 2,
                'Kokoro': 1,
                'EdgeTTS': 2,
                'default': 4
            }
    """
    global _multi_executor
    if _multi_executor is None or getattr(_multi_executor, '_shutdown', False):
        _multi_executor = MultiEngineExecutor(engine_config=engine_config)
    elif engine_config is not None and _multi_executor.engine_config != engine_config:
        # Recreate executor when worker configuration changes.
        _multi_executor.shutdown(wait=False)
        _multi_executor = MultiEngineExecutor(engine_config=engine_config)
    return _multi_executor


def reset_multi_engine_executor():
    """Reset multi-engine executor"""
    global _multi_executor
    if _multi_executor:
        _multi_executor.shutdown()
        _multi_executor = None
