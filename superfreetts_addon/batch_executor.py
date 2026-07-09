"""
Unified Batch Executor - Simplified threading, resource management, and caching.

Replaces:
  - resource_manager.py (ResourceMonitor, MemoryPool, SmartLRUCache)
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
import time
from typing import Dict, Optional, Any, List, Callable, Tuple
from datetime import datetime, timedelta
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


class UnifiedCache:
    """Minimal LRU cache using OrderedDict. Supports size-based or entry-count eviction."""
    
    def __init__(self, max_size_mb: int = 100):
        self.cache = OrderedDict()
        self.max_entries = 1000
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.current_size = 0
        self.hits = 0
        self.misses = 0
    
    @property
    def _use_size(self) -> bool:
        return self.max_size_bytes > 0
    
    def get(self, key: str) -> Optional[Any]:
        if key in self.cache:
            self.cache.move_to_end(key)
            self.hits += 1
            val = self.cache[key]
            return val[0] if isinstance(val, tuple) else val
        self.misses += 1
        return None
    
    def put(self, key: str, value: Any, size_bytes: int = 0):
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
        self.cache.clear()
        self.current_size = 0
    
    def stats(self) -> dict:
        total = max(self.hits + self.misses, 1)
        return {
            'entries': len(self.cache),
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': f"{(self.hits / total * 100):.1f}%",
        }


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
        Simple heuristic: GC if RAM growth > 300MB or every 100 items.
        No complex thresholds.
        """
        ram_usage = self._get_ram_usage()
        ram_growth = ram_usage - self.initial_ram_mb
        
        # Aggressive but simple: every 100 items OR significant growth
        return ram_growth > 300 or (items_processed > 0 and items_processed % 100 == 0)
    
    def maybe_gc(self, items_processed: int):
        """Run GC if needed"""
        if self.should_gc(items_processed):
            gc.collect()
            logger.debug(f"[BATCH] GC triggered (items={items_processed})")
    
    def get_status(self) -> str:
        """Get RAM status string"""
        ram = self._get_ram_usage()
        return f"RAM: {ram}MB/{self.max_ram_mb}MB"


class CheckpointManager:
    """
    Lightweight crash recovery - saves progress after each note.
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
    
    def save(self, batch_name: str, completed_indices: List[int], note_id_list: List[int], errors: Dict = None):
        """Save checkpoint"""
        with self._lock:
            try:
                path = self._get_path(batch_name)
                data = {
                    'batch_name': batch_name,
                    'completed_indices': completed_indices,
                    'note_id_list': note_id_list,
                    'errors': errors or {},
                    'timestamp': datetime.now().isoformat(),
                }
                with open(path, 'w') as f:
                    json.dump(data, f)
            except Exception as e:
                logger.warning(f"[BATCH] Checkpoint save failed: {e}")
    
    def load(self, batch_name: str) -> Optional[dict]:
        """Load checkpoint if exists"""
        with self._lock:
            try:
                path = self._get_path(batch_name)
                if os.path.exists(path):
                    with open(path, 'r') as f:
                        return json.load(f)
            except Exception as e:
                logger.warning(f"[BATCH] Checkpoint load failed: {e}")
        return None
    
    def remove(self, batch_name: str):
        """Remove checkpoint after batch complete"""
        with self._lock:
            try:
                path = self._get_path(batch_name)
                if os.path.exists(path):
                    os.remove(path)
            except Exception as e:
                logger.warning(f"[BATCH] Checkpoint remove failed: {e}")


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
        results = executor.execute(
            tasks=task_list,
            on_progress=callback,
            batch_name='my_batch'
        )
    """
    
    def __init__(self, max_workers: int = 1, max_ram_mb: int = 3000, cache_size_mb: int = 100):
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)
        self.monitor = SimpleResourceMonitor(max_ram_mb)
        self.cache = UnifiedCache(max_size_mb=cache_size_mb)
        self.checkpoint = CheckpointManager()
        self.max_workers = max_workers
        self.items_processed = 0
    
    def execute(
        self,
        tasks: List[Dict],
        on_progress: Callable,
        batch_name: str = 'default',
        enable_checkpoint: bool = True,
    ) -> List[Tuple]:
        """
        Execute batch of tasks with thread pool.
        
        Args:
            tasks: List of task dicts
            on_progress: Callback(note_id, result_tuple) after each task completes
            batch_name: Name for checkpoint/logging
            enable_checkpoint: Save progress for crash recovery
            
        Returns:
            List of (note_id, source_text, processed_text, sound_file, full_filename, is_error) tuples
        """
        results = []
        completed_indices = []
        errors = {}
        future_to_task = {}
        items_processed = 0
        
        # Check for resumable checkpoint
        checkpoint_data = None
        if enable_checkpoint:
            checkpoint_data = self.checkpoint.load(batch_name)
            if checkpoint_data:
                completed_indices = checkpoint_data.get('completed_indices', [])
                errors = checkpoint_data.get('errors', {})
                logger.info(f"[BATCH] Resuming batch: {len(completed_indices)} already done")
        
        # Submit only non-completed tasks
        for idx, task in enumerate(tasks):
            if idx in completed_indices:
                continue  # Skip already done
            
            future = self.executor.submit(self._execute_single_task, task)
            future_to_task[future] = (idx, task)
        
        # Collect results as they complete
        for future in concurrent.futures.as_completed(future_to_task):
            idx, task = future_to_task[future]
            items_processed += 1
            
            try:
                result = future.result()
                results.append(result)
                completed_indices.append(idx)
                
                # Callback for UI update
                if on_progress:
                    on_progress(task['note_id'], result)
                
                # Save checkpoint
                if enable_checkpoint:
                    self.checkpoint.save(batch_name, completed_indices, [t['note_id'] for t in tasks], errors)
                
                # Lightweight GC
                self.monitor.maybe_gc(items_processed)
                
            except Exception as e:
                logger.error(f"[BATCH] Task {idx} failed: {e}")
                errors[str(idx)] = str(e)
                result = (task['note_id'], None, None, None, None, True)  # error marker
                results.append(result)
                if on_progress:
                    on_progress(task['note_id'], result)
        
        # Cleanup checkpoint after success
        if enable_checkpoint:
            self.checkpoint.remove(batch_name)
        
        self.items_processed += items_processed
        logger.info(f"[BATCH] Completed {items_processed} tasks. Cache: {self.cache.stats()}")
        
        return results
    
    def _execute_single_task(self, task: Dict) -> Tuple:
        """
        Execute single audio generation task in worker thread.
        Returns: (note_id, source_text, processed_text, sound_file, full_filename, is_error)
        """
        note_id = task['note_id']
        processed_text = task['processed_text']
        batch = task['batch']
        audio_request_context = task['audio_request_context']
        
        # Check cache first
        chosen_voice = task.get('chosen_voice')
        voice_id_str = str(chosen_voice.voice_id) if chosen_voice else 'None'
        cache_key = f"{processed_text}_{voice_id_str}"
        cached = self.cache.get(cache_key)
        if cached:
            source_text, audio_filename, full_filename = cached
            return (note_id, source_text, processed_text, audio_filename, full_filename, False)
        
        # Cache miss - generate audio (this is the expensive part - passed to caller)
        # Caller (superfreetts.py) will call get_audio_file() 
        # We just return placeholder; actual implementation in superfreetts
        return None  # Caller handles generation
    
    def cache_result(self, processed_text: str, voice_id: str, source_text: str, audio_filename: str, full_filename: str):
        """Cache successful audio generation result"""
        cache_key = f"{processed_text}_{voice_id}"
        self.cache.put(cache_key, (source_text, audio_filename, full_filename))
    
    def shutdown(self, wait: bool = True):
        """Shutdown thread pool"""
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
        results = executor.execute(tasks, on_progress, batch_name)
    """
    
    def __init__(self, engine_config: Dict[str, int] = None, cache_size_mb: int = 100):
        """
        Args:
            engine_config: Dict mapping engine name → worker count
            cache_size_mb: Unified cache size in MB
        """
        from . import system_utils
        cpu_default = max(2, system_utils.get_max_workers())
        self.engine_config = engine_config or {
            'Piper': cpu_default,
            'Kokoro': cpu_default,
            'EdgeTTS': batch_constants.EDGETTS_MAX_WORKERS,
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
        """
        Detect TTS service name from task's selected voice.
        Returns service name or 'default'
        """
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
    
    def execute(
        self,
        tasks: List[Dict],
        on_progress: Callable,
        batch_name: str = 'default',
        enable_checkpoint: bool = True,
    ) -> List[Tuple]:
        """
        Execute batch with per-engine worker pools.
        
        Args:
            tasks: List of task dicts with 'batch' containing voice_selection
            on_progress: Callback(note_id, result)
            batch_name: Name for checkpoint
            enable_checkpoint: Enable crash recovery
            
        Returns:
            List of (note_id, source_text, processed_text, sound_file, full_filename, is_error)
        """
        results = []
        completed_indices = []
        errors = {}
        future_to_task = {}
        
        # Check for resumable checkpoint
        checkpoint_data = None
        if enable_checkpoint:
            checkpoint_data = self.checkpoint.load(batch_name)
            if checkpoint_data:
                completed_indices = checkpoint_data.get('completed_indices', [])
                errors = checkpoint_data.get('errors', {})
                logger.info(f"[BATCH] Resuming: {len(completed_indices)} already done")
        
        # Group tasks by service/engine for load analysis
        tasks_by_service = {}
        for idx, task in enumerate(tasks):
            if idx in completed_indices:
                continue
            
            service = self.detect_service(task)
            if service not in tasks_by_service:
                tasks_by_service[service] = []
            tasks_by_service[service].append((idx, task))
        
        # Log distribution
        for service, task_list in tasks_by_service.items():
            executor = self.get_executor(service)
            worker_count = executor._max_workers
            logger.info(f"[BATCH] Engine {service}: {len(task_list)} tasks → {worker_count} workers")
        
        # Submit tasks to appropriate engine-specific executors
        for idx, task in enumerate(tasks):
            if idx in completed_indices:
                continue
            
            service = self.detect_service(task)
            executor = self.get_executor(service)
            
            # Submit to service-specific executor
            future = executor.submit(self._execute_single_task, task)
            future_to_task[future] = (idx, task, service)
        
        # Collect results as they complete (in any order, from any executor)
        items_processed = 0
        for future in concurrent.futures.as_completed(future_to_task):
            idx, task, service = future_to_task[future]
            items_processed += 1
            
            try:
                result = future.result()
                results.append(result)
                completed_indices.append(idx)
                
                if on_progress:
                    on_progress(task['note_id'], result)
                
                if enable_checkpoint:
                    checkpoint_data_to_save = checkpoint_data or {
                        'batch_name': batch_name,
                        'completed_indices': [],
                        'note_id_list': [t.get('note_id') for t in tasks],
                        'errors': {}
                    }
                    checkpoint_data_to_save['completed_indices'] = completed_indices
                    self.checkpoint.save(
                        batch_name,
                        completed_indices,
                        checkpoint_data_to_save.get('note_id_list', []),
                        errors
                    )
                
                self.monitor.maybe_gc(items_processed)
                
            except Exception as e:
                logger.error(f"[BATCH] Task {idx} ({service}) failed: {e}")
                errors[str(idx)] = str(e)
                result = (task['note_id'], None, None, None, None, True)
                results.append(result)
                if on_progress:
                    on_progress(task['note_id'], result)
        
        # Cleanup
        if enable_checkpoint:
            self.checkpoint.remove(batch_name)
        
        logger.info(f"[BATCH] Completed {items_processed} tasks via multi-engine executor. Distribution:")
        for service in self.engine_config.keys():
            if service != 'default':
                executor = self.get_executor(service)
                logger.info(f"  {service}: {executor._max_workers} workers, {self.cache.stats()}")
        
        return results
    
    def _execute_single_task(self, task: Dict) -> Tuple:
        """Execute single task - implemented by caller via callback"""
        # This is just placeholder - actual implementation is in superfreetts.py
        # For now return None to indicate generation needed
        return None
    
    def cache_result(self, processed_text: str, voice_id: str, source_text: str, audio_filename: str, full_filename: str):
        """Cache result"""
        cache_key = f"{processed_text}_{voice_id}"
        self.cache.put(cache_key, (source_text, audio_filename, full_filename))
    
    def shutdown(self, wait: bool = True):
        """Shutdown all executors"""
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
    if _executor is None:
        _executor = UnifiedBatchExecutor(max_workers=max_workers)
    return _executor


def reset_batch_executor():
    """Reset global executor"""
    global _executor
    if _executor:
        _executor.shutdown()
        _executor = None


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
    if _multi_executor is None:
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
