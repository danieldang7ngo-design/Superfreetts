"""
Resource monitoring for batch processing - current process RSS with
platform-specific fallbacks.  Worker pools and caches live in
``batch_executor.py``; the old MemoryPool/SmartLRUCache/ResourceManager
classes were unused and have been removed.
"""
import os
import platform
import threading

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
