"""
Resource management for batch processing - RAM, CPU, memory pooling, intelligent GC
"""
import gc
import os
import threading
from functools import lru_cache
from collections import OrderedDict
from typing import Any, Callable, Dict, Optional

# Try to import psutil for memory monitoring, fallback if not available
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False
    import multiprocessing  # Fallback for CPU count only

from . import logging_utils
logger = logging_utils.get_child_logger(__name__)

class ResourceMonitor:
    """Monitor and manage system resources during batch processing"""
    
    def __init__(self, max_ram_mb: int = 3000, max_cores: int = 8):
        self.max_ram_mb = max_ram_mb
        self.max_cores = max_cores
        self.process = psutil.Process(os.getpid()) if HAS_PSUTIL else None
        self.lock = threading.Lock()
        self.initial_ram_mb = self._get_ram_usage()
        
    def _get_ram_usage(self) -> int:
        """Get current process RAM usage in MB"""
        if not HAS_PSUTIL:
            return 0  # Cannot monitor without psutil
        
        try:
            return int(self.process.memory_info().rss / 1024 / 1024)
        except Exception as e:
            logger.warning(f"Failed to get RAM usage: {e}")
            return 0
    
    def get_available_workers(self) -> int:
        """Calculate safe number of workers based on resource limits"""
        with self.lock:
            current_ram = self._get_ram_usage()
            ram_usage_percent = (current_ram / self.max_ram_mb) * 100
            
            # If already using >70% RAM, reduce workers
            if ram_usage_percent > 70:
                safe_workers = max(2, self.max_cores // 2)
                logger.info(f"[RESOURCE] RAM usage {current_ram}MB/{self.max_ram_mb}MB ({ram_usage_percent:.1f}%), reducing workers to {safe_workers}")
                return safe_workers
            
            return self.max_cores
    
    def should_trigger_gc(self, completed_count: int) -> bool:
        """Intelligently decide if GC should run"""
        # Check RAM usage status
        current_ram = self._get_ram_usage()
        ram_growth = current_ram - self.initial_ram_mb
        
        # Trigger GC if:
        # 1. RAM grew by >500MB, OR
        # 2. Processing every 50 items
        if ram_growth > 500 or (completed_count > 0 and completed_count % 50 == 0):
            logger.debug(f"[RESOURCE] GC triggered: RAM growth={ram_growth}MB, completed={completed_count}")
            return True
        
        return False
    
    def report_status(self) -> str:
        """Get human-readable resource status"""
        current_ram = self._get_ram_usage()
        return f"RAM: {current_ram}MB/{self.max_ram_mb}MB (Cores: {self.max_cores})"


class MemoryPool:
    """Memory pool for reusing task objects to reduce allocation overhead"""
    
    def __init__(self, pool_size: int = 100):
        self.pool = []  # Pre-allocated small list (low memory overhead)
        self.pool_size = max(10, pool_size)  # Minimum 10, prevent tiny pools
        self.created_count = 0
        self.lock = threading.Lock()
    
    def acquire(self, note_id: int, **kwargs) -> Dict[str, Any]:
        """Get a reusable task object"""
        with self.lock:
            if self.pool:
                task = self.pool.pop()
                # Reset and reuse
                task.update({
                    'note_id': note_id,
                    'source_text': kwargs.get('source_text'),
                    'processed_text': kwargs.get('processed_text'),
                    'batch': kwargs.get('batch'),
                    'audio_request_context': kwargs.get('audio_request_context'),
                })
                return task
            else:
                self.created_count += 1
                return {
                    'note_id': note_id,
                    'source_text': kwargs.get('source_text'),
                    'processed_text': kwargs.get('processed_text'),
                    'batch': kwargs.get('batch'),
                    'audio_request_context': kwargs.get('audio_request_context'),
                }
    
    def release(self, task: Dict[str, Any]):
        """Return task to pool for reuse"""
        with self.lock:
            if len(self.pool) < self.pool_size:
                # Clear sensitive data
                task_clean = {
                    'note_id': task.get('note_id'),
                    'source_text': None,
                    'processed_text': None,
                    'batch': None,
                    'audio_request_context': None,
                }
                self.pool.append(task_clean)
    
    def stats(self) -> str:
        """Get pool statistics"""
        return f"MemoryPool: {len(self.pool)} available, {self.created_count} total created"


class SmartLRUCache:
    """LRU cache with memory-aware eviction - lazy initialization"""
    
    def __init__(self, maxsize: int = 128, max_memory_mb: int = 500):
        self.cache = None  # Lazy init
        self.maxsize = maxsize
        self.max_memory_mb = max_memory_mb
        self.memory_used = 0
        self.lock = threading.Lock()
        self._initialized = False
    
    def _ensure_initialized(self):
        """Initialize cache on first use"""
        if not self._initialized:
            self.cache = OrderedDict()
            self._initialized = True
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache (move to end for LRU)"""
        if not self._initialized:
            return None
        
        with self.lock:
            if key in self.cache:
                self.cache.move_to_end(key)
                return self.cache[key]
        return None
    
    def put(self, key: str, value: Any, size_bytes: int = 0):
        """Put value in cache, evict if needed"""
        self._ensure_initialized()
        
        with self.lock:
            if key in self.cache:
                self.cache.move_to_end(key)
                return
            
            # Estimate size if not provided
            if size_bytes == 0:
                if isinstance(value, bytes):
                    size_bytes = len(value)
                elif isinstance(value, str):
                    size_bytes = len(value)
                else:
                    size_bytes = 1000
            
            self.memory_used += size_bytes
            
            # Evict oldest entries if over capacity
            while len(self.cache) >= self.maxsize or (self.memory_used > self.max_memory_mb * 1024 * 1024):
                if self.cache:
                    evicted_key, evicted_val = self.cache.popitem(last=False)
                    # Track evicted size without creating copies
                    if isinstance(evicted_val, (bytes, str)):
                        self.memory_used -= len(evicted_val)
                    else:
                        self.memory_used -= 1000
                else:
                    break
            
            self.cache[key] = value
    
    def clear(self):
        """Clear cache and release all references"""
        with self.lock:
            if self.cache:
                self.cache.clear()
            self.cache = None
            self.memory_used = 0
            self._initialized = False


class ResourceManager:
    """Centralized resource management - monitors, optimizes, pools"""
    
    def __init__(self, max_ram_mb: int = 3000, max_cores: int = 8):
        self.monitor = ResourceMonitor(max_ram_mb, max_cores)
        self.memory_pool = MemoryPool(pool_size=min(50, max(20, max_cores * 5)))  # Reduced from max_cores*10
        # Smaller cache sizes to reduce startup RAM: 64 items instead of 256
        self.text_cache = SmartLRUCache(maxsize=64, max_memory_mb=50)  # Reduced from 256, 200MB
        self.voice_cache = SmartLRUCache(maxsize=32, max_memory_mb=30)  # Reduced from 64, 100MB
        self.gc_threshold = 50  # Run GC every X items
        self.items_since_gc = 0
        self.lock = threading.Lock()
        
        # Performance tracking (for debug mode)
        self.task_times = []  # List of (task_id, duration_ms)
        self.batch_start_time = None
        self.completed_tasks = 0
    
    def calculate_optimal_workers(self) -> int:
        """Calculate optimal worker count based on resources"""
        return self.monitor.get_available_workers()
    
    def get_or_create_task(self, note_id: int, **kwargs) -> Dict[str, Any]:
        """Get task from pool or create new"""
        return self.memory_pool.acquire(note_id, **kwargs)
    
    def free_task(self, task: Dict[str, Any]):
        """Return task to pool"""
        self.memory_pool.release(task)
    
    def cache_processed_text(self, key: str, text: str):
        """Cache processed text to avoid re-processing"""
        self.text_cache.put(key, text, size_bytes=len(text))
    
    def get_cached_text(self, key: str) -> Optional[str]:
        """Retrieve cached processed text"""
        return self.text_cache.get(key)
    
    def cache_voice_data(self, key: str, data: bytes):
        """Cache voice data (audio bytes)"""
        self.voice_cache.put(key, data, size_bytes=len(data))
    
    def get_cached_voice(self, key: str) -> Optional[bytes]:
        """Retrieve cached voice data"""
        return self.voice_cache.get(key)
    
    def maybe_gc(self, completed_count: int):
        """Intelligently run garbage collection"""
        with self.lock:
            self.items_since_gc += 1
            
            if self.items_since_gc >= self.gc_threshold or self.monitor.should_trigger_gc(completed_count):
                logger.debug(f"[RESOURCE] Running smart GC (completed={completed_count})")
                ram_growth = self.monitor._get_ram_usage() - self.monitor.initial_ram_mb
                if ram_growth > 300:
                    gc.collect()
                    logger.info(f"[RESOURCE] Full GC triggered (RAM growth: {ram_growth}MB)")
                else:
                    gc.collect(generation=0)
                self.items_since_gc = 0
    
    def get_status(self) -> str:
        """Get comprehensive resource status"""
        # Handle lazy-initialized caches (may be None)
        text_cache_size = len(self.text_cache.cache) if self.text_cache._initialized and self.text_cache.cache else 0
        voice_cache_size = len(self.voice_cache.cache) if self.voice_cache._initialized and self.voice_cache.cache else 0
        
        status = {
            'monitor': self.monitor.report_status(),
            'memory_pool': self.memory_pool.stats(),
            'text_cache': f"TextCache: {text_cache_size}/{self.text_cache.maxsize}",
            'voice_cache': f"VoiceCache: {voice_cache_size}/{self.voice_cache.maxsize}",
        }
        return " | ".join(status.values())
    
    def record_task_time(self, duration_ms: float):
        """Record task generation time for performance tracking"""
        with self.lock:
            self.task_times.append(duration_ms)
            # Cap to prevent unbounded memory growth
            if len(self.task_times) > 100:
                self.task_times = self.task_times[-100:]
            self.completed_tasks += 1
    
    def get_performance_stats(self) -> dict:
        """Get performance stats (avg speed, min/max time)"""
        with self.lock:
            if not self.task_times:
                return {}
            
            total_time_ms = sum(self.task_times)
            avg_time_ms = total_time_ms / len(self.task_times)
            min_time_ms = min(self.task_times)
            max_time_ms = max(self.task_times)
            cards_per_second = 1000 / avg_time_ms if avg_time_ms > 0 else 0
            
            return {
                'total_cards': len(self.task_times),
                'avg_time_ms': avg_time_ms,
                'min_time_ms': min_time_ms,
                'max_time_ms': max_time_ms,
                'cards_per_second': cards_per_second,
                'total_time_ms': total_time_ms
            }
    
    def reset(self):
        """Reset all caches and release memory"""
        self.text_cache.clear()
        self.voice_cache.clear()
        self.memory_pool.pool.clear()
        self.items_since_gc = 0
        self.task_times.clear()
        self.completed_tasks = 0
        # Force full GC after clearing all caches
        gc.collect()
        logger.info("[RESOURCE] Resource manager reset")


# Global singleton instance
_resource_manager = None

def get_resource_manager(max_ram_mb: int = 3000, max_cores: int = 8) -> ResourceManager:
    """Get or create global resource manager"""
    global _resource_manager
    if _resource_manager is None:
        _resource_manager = ResourceManager(max_ram_mb, max_cores)
    return _resource_manager

def reset_resource_manager():
    """Reset global resource manager"""
    global _resource_manager
    if _resource_manager:
        _resource_manager.reset()
        _resource_manager = None
