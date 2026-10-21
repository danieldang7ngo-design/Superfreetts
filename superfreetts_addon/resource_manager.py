"""
Resource management for batch processing - RAM, CPU, memory pooling, intelligent GC
"""
import gc
import os
import platform
import threading
from collections import OrderedDict
from typing import Any, Dict, Optional

# Try to import psutil for memory monitoring, fallback if not available
try:
    import psutil
    HAS_PSUTIL = True
except Exception:
    HAS_PSUTIL = False

from . import logging_utils
logger = logging_utils.get_child_logger(__name__)

# The most recent successful process-RSS source, exposed for diagnostics.
_LAST_PROCESS_RAM_SOURCE = "unknown"


def get_process_ram_source() -> str:
    """Return the method used by the most recent process-RSS read."""
    return _LAST_PROCESS_RAM_SOURCE


def _linux_current_rss_mb(statm_path: str = "/proc/self/statm"):
    """Read current resident pages from /proc without psutil.

    ``statm`` fields are: size, resident, shared, text, lib, data, dt.
    Field 1 (zero-based) is the resident set size in pages.
    """
    with open(statm_path, "r", encoding="utf-8") as handle:
        fields = handle.read().split()
    if len(fields) < 2:
        raise ValueError("unexpected /proc/self/statm format")
    resident_pages = int(fields[1])
    page_size = int(os.sysconf("SC_PAGE_SIZE"))
    return max(0, int(resident_pages * page_size / 1024 / 1024))


def _macos_current_rss_mb():
    """Read current resident size on macOS through Mach task_info.

    This uses only the standard library.  The older fallback in this module
    used ``ru_maxrss``, which is a peak value, not the current RSS.
    """
    try:
        import ctypes

        class TimeValue(ctypes.Structure):
            _fields_ = [
                ("seconds", ctypes.c_int32),
                ("microseconds", ctypes.c_int32),
            ]

        class MachTaskBasicInfo(ctypes.Structure):
            _fields_ = [
                ("virtual_size", ctypes.c_uint64),
                ("resident_size", ctypes.c_uint64),
                ("resident_size_max", ctypes.c_uint64),
                ("user_time", TimeValue),
                ("system_time", TimeValue),
                ("policy", ctypes.c_int32),
                ("suspend_count", ctypes.c_int32),
            ]

        try:
            libc = ctypes.CDLL(None)
        except Exception:
            libc = ctypes.CDLL("/usr/lib/libSystem.B.dylib")

        mach_task_self = getattr(libc, "mach_task_self", None)
        if mach_task_self is not None:
            mach_task_self.restype = ctypes.c_uint32
            task = mach_task_self()
        else:
            task = ctypes.c_uint32.in_dll(libc, "mach_task_self_").value

        info = MachTaskBasicInfo()
        count = ctypes.c_uint32(
            ctypes.sizeof(MachTaskBasicInfo) // ctypes.sizeof(ctypes.c_int32)
        )
        task_info = libc.task_info
        task_info.argtypes = [
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.c_void_p,
            ctypes.POINTER(ctypes.c_uint32),
        ]
        task_info.restype = ctypes.c_int
        # MACH_TASK_BASIC_INFO == 20
        result = task_info(
            task,
            ctypes.c_uint32(20),
            ctypes.byref(info),
            ctypes.byref(count),
        )
        if result != 0:
            raise OSError(result, "task_info(MACH_TASK_BASIC_INFO) failed")
        return max(0, int(info.resident_size / 1024 / 1024))
    except Exception as e:
        logger.debug(f"Failed to get current RSS via macOS task_info: {e}")
        return None


def _windows_current_rss_mb():
    """Read the current Windows working-set size without psutil."""
    try:
        import ctypes
        from ctypes import wintypes

        class PROCESS_MEMORY_COUNTERS(ctypes.Structure):
            _fields_ = [
                ("cb", wintypes.DWORD),
                ("PageFaultCount", wintypes.DWORD),
                ("PeakWorkingSetSize", ctypes.c_size_t),
                ("WorkingSetSize", ctypes.c_size_t),
                ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
                ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                ("PagefileUsage", ctypes.c_size_t),
                ("PeakPagefileUsage", ctypes.c_size_t),
            ]

        counters = PROCESS_MEMORY_COUNTERS()
        counters.cb = ctypes.sizeof(PROCESS_MEMORY_COUNTERS)
        handle = ctypes.windll.kernel32.GetCurrentProcess()
        get_process_memory_info = ctypes.windll.psapi.GetProcessMemoryInfo
        get_process_memory_info.argtypes = [
            wintypes.HANDLE,
            ctypes.POINTER(PROCESS_MEMORY_COUNTERS),
            wintypes.DWORD,
        ]
        get_process_memory_info.restype = wintypes.BOOL
        ok = get_process_memory_info(
            handle,
            ctypes.byref(counters),
            counters.cb,
        )
        if ok:
            return int(counters.WorkingSetSize / 1024 / 1024)
    except Exception as e:
        logger.debug(f"Failed to get current RSS via Windows API: {e}")
    return None


def _get_process_ram_usage_without_psutil() -> int:
    """Best-effort current process RSS in MB when psutil is unavailable.

    Preference order:
      1. OS-specific current RSS (Linux statm, macOS task_info, Windows
         working set).
      2. ``resource.ru_maxrss`` only as a last-resort peak fallback.

    The source of the returned value is recorded in
    ``get_process_ram_source()`` for diagnostics.
    """
    global _LAST_PROCESS_RAM_SOURCE

    system = platform.system()
    value = None
    source = None

    if system == "Windows":
        value = _windows_current_rss_mb()
        source = "windows_working_set"
    elif system == "Linux":
        try:
            value = _linux_current_rss_mb()
            source = "linux_proc"
        except Exception as e:
            logger.debug(f"Failed to read current RSS from /proc: {e}")
    elif system == "Darwin":
        value = _macos_current_rss_mb()
        source = "macos_task_info"

    if value is not None and value >= 0:
        _LAST_PROCESS_RAM_SOURCE = source
        return int(value)

    try:
        import resource

        usage = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        if system == "Darwin":
            fallback = int(usage / 1024 / 1024)
        else:
            fallback = int(usage / 1024)
        if fallback > 0:
            _LAST_PROCESS_RAM_SOURCE = "peak_fallback"
            logger.debug("Using peak RSS fallback; current RSS is unavailable")
            return fallback
    except Exception as e:
        logger.debug(f"Failed to get RAM usage via resource module: {e}")

    _LAST_PROCESS_RAM_SOURCE = "unavailable"
    return 0

class ResourceMonitor:
    """Monitor and manage system resources during batch processing"""
    
    def __init__(self, max_ram_mb: int = 3000, max_cores: int = 8):
        self.max_ram_mb = max_ram_mb
        self.max_cores = max_cores
        self.process = psutil.Process(os.getpid()) if HAS_PSUTIL else None
        self.lock = threading.Lock()
        self.initial_ram_mb = self._get_ram_usage()
        self._last_gc_ram_mb = self.initial_ram_mb
        self._last_gc_completed = 0
        
    def _get_ram_usage(self) -> int:
        """Get current process RAM usage in MB"""
        if not HAS_PSUTIL:
            return _get_process_ram_usage_without_psutil()
        
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
        """Intelligently decide if GC should run.

        The baseline is current RSS at the last collection, not the initial
        or peak RSS.  Otherwise one allocation spike causes a collection on
        every subsequent call.
        """
        current_ram = self._get_ram_usage()
        if current_ram < self._last_gc_ram_mb:
            self._last_gc_ram_mb = current_ram
        ram_growth = current_ram - self._last_gc_ram_mb
        
        # Trigger GC if:
        # 1. RAM grew by >500MB since the last collection, OR
        # 2. Processing every 50 items since the last collection
        interval_elapsed = (
            completed_count > 0
            and completed_count - self._last_gc_completed >= 50
        )
        if ram_growth > 500 or interval_elapsed:
            logger.debug(f"[RESOURCE] GC triggered: RAM growth={ram_growth}MB, completed={completed_count}")
            return True
        
        return False

    def mark_gc(self, completed_count: int = 0) -> None:
        """Record that a garbage collection just finished."""
        self._last_gc_ram_mb = self._get_ram_usage()
        self._last_gc_completed = completed_count
    
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
                ram_growth = self.monitor._get_ram_usage() - self.monitor._last_gc_ram_mb
                if ram_growth > 300:
                    gc.collect()
                    logger.info(f"[RESOURCE] Full GC triggered (RAM growth: {ram_growth}MB)")
                else:
                    gc.collect(generation=0)
                self.monitor.mark_gc(completed_count)
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


