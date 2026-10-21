
import os
import multiprocessing
import platform
import subprocess
import logging
from typing import Any, Dict, Optional, Set, Tuple

# Try to import psutil for system RAM detection, but never rely on it.
# Anki does not guarantee psutil, and a broken/incomplete vendored copy must
# not disable RAM-aware concurrency (the bug that shipped in 26.10.1).
try:
    import psutil
    HAS_PSUTIL = True
except Exception:
    HAS_PSUTIL = False

logger = logging.getLogger(__name__)

# The most recent successful RAM-detection method, exposed for diagnostics.
_LAST_RAM_SOURCE = "unknown"


def _mb_from_bytes(value) -> int:
    return int(value / 1024 / 1024)


def _psutil_available_ram_mb():
    if not HAS_PSUTIL:
        return None
    try:
        return _mb_from_bytes(psutil.virtual_memory().available)
    except Exception as e:
        logger.debug(f"psutil RAM detection failed, trying OS fallback: {e}")
        return None


def _linux_available_ram_mb(meminfo_path: str = "/proc/meminfo"):
    """Read available RAM from /proc/meminfo without psutil.

    ``MemAvailable`` is the kernel's best estimate.  Older kernels may not
    expose it, in which case the traditional MemFree + Buffers + Cached
    approximation is used.
    """
    values = {}
    with open(meminfo_path, "r", encoding="utf-8") as handle:
        for line in handle:
            key, _, rest = line.partition(":")
            if not rest:
                continue
            parts = rest.strip().split()
            if not parts:
                continue
            try:
                values[key.strip()] = int(parts[0])
            except ValueError:
                continue

    if "MemAvailable" in values:
        return int(values["MemAvailable"] / 1024)

    free = values.get("MemFree")
    if free is None:
        raise ValueError("MemFree missing from /proc/meminfo")
    available_kb = (
        free
        + values.get("Buffers", 0)
        + values.get("Cached", 0)
    )
    return int(available_kb / 1024)


def _macos_available_ram_mb():
    """Return a conservative free-RAM estimate using sysconf."""
    page_size = int(os.sysconf("SC_PAGE_SIZE"))
    free_pages = int(os.sysconf("SC_AVPHYS_PAGES"))
    return _mb_from_bytes(page_size * free_pages)


def _windows_available_ram_mb():
    """Return available physical RAM via GlobalMemoryStatusEx."""
    import ctypes
    from ctypes import wintypes

    class MEMORYSTATUSEX(ctypes.Structure):
        _fields_ = [
            ("dwLength", wintypes.DWORD),
            ("dwMemoryLoad", wintypes.DWORD),
            ("ullTotalPhys", ctypes.c_ulonglong),
            ("ullAvailPhys", ctypes.c_ulonglong),
            ("ullTotalPageFile", ctypes.c_ulonglong),
            ("ullAvailPageFile", ctypes.c_ulonglong),
            ("ullTotalVirtual", ctypes.c_ulonglong),
            ("ullAvailVirtual", ctypes.c_ulonglong),
            ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
        ]

    status = MEMORYSTATUSEX()
    status.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
    if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
        raise OSError("GlobalMemoryStatusEx failed")
    return _mb_from_bytes(status.ullAvailPhys)

def get_cpu_threads():
    """
    Returns the optimal number of threads for TTS generation.
    Usually physical cores or logical cores - 2 to avoid freezing the UI.
    Minimum 1, Maximum 8 (diminishing returns often after 4-8 for simple inference).
    """
    try:
        count = multiprocessing.cpu_count()
        # Leave some cores for the UI and OS
        ideal = max(1, count - 1)
        # Cap at 8 to prevent excessive overhead
        return min(ideal, 8)
    except Exception:
        return 1

def get_max_workers():
    """
    Returns the maximum available CPU cores (minimum 1).
    Replaces cpu_utils.CPUInfo.get_max_workers().
    """
    try:
        return max(1, multiprocessing.cpu_count())
    except Exception:
        return 1

def get_available_ram_mb():
    """
    Returns currently available system RAM in MB, or None if it cannot be
    determined by any supported method.

    Detection order:
      1. psutil, when it imports and works.
      2. Linux /proc/meminfo, macOS sysconf, or Windows GlobalMemoryStatusEx.

    Callers MUST treat None as "unknown" and skip RAM-based capping rather
    than guessing a number.
    """
    global _LAST_RAM_SOURCE

    psutil_value = _psutil_available_ram_mb()
    if psutil_value is not None:
        _LAST_RAM_SOURCE = "psutil"
        return psutil_value

    system = platform.system()
    try:
        if system == "Linux":
            value = _linux_available_ram_mb()
            source = "linux_meminfo"
        elif system == "Darwin":
            value = _macos_available_ram_mb()
            source = "macos_sysconf"
        elif system == "Windows":
            value = _windows_available_ram_mb()
            source = "windows_global_memory"
        else:
            return None
    except Exception as e:
        logger.debug(f"OS RAM detection failed on {system}: {e}")
        return None

    if value is None or value <= 0:
        return None
    _LAST_RAM_SOURCE = source
    return int(value)


def get_ram_detection_source() -> str:
    """Return the method used by the most recent successful RAM detection."""
    return _LAST_RAM_SOURCE


def compute_ram_aware_concurrency(
    cpu_default: int,
    ram_per_process_mb,
    ram_budget_ratio: float = 0.5,
    available_ram_mb=None,
):
    """
    Caps a CPU-derived worker/process count by how many of that engine's
    processes would actually fit in available RAM.

    This exists specifically because build_engine_config() in
    tts_orchestrator.py used to size local-engine process pools
    (Piper/Kokoro/MMS/Supertonic) purely from CPU core count, with no
    awareness of per-process memory footprint. On multi-core Macs this let
    the pool spawn as many processes as there are cores even for engines
    that load a few hundred MB of model weights per process, which is the
    documented root cause of >5GB RAM usage in real user reports (see
    root cause 2.6 in the fix plan).

    Args:
        cpu_default: the CPU-core-derived worker count (existing behavior).
        ram_per_process_mb: best-effort estimate of RSS for one process of
            this engine, in MB. Pass None if unknown - in that case this
            function does NOT guess and simply returns cpu_default
            unchanged, per the "don't fabricate numbers" rule.
        ram_budget_ratio: fraction of *currently available* system RAM this
            engine's pool is allowed to consume, reserving the rest for the
            OS, Anki itself, and any other engine pool running concurrently.
            Default 0.5 is a conservative starting point, not a measured
            value - callers/users can override the resulting cap manually
            via the existing `concurrency_workers` config field.
        available_ram_mb: optional pre-measured value, used so one startup
            calculation does not query the OS once per engine.

    Returns:
        An int >= 1. Never raises.
    """
    if ram_per_process_mb is None or ram_per_process_mb <= 0:
        # No reliable per-process estimate available - do not fabricate one.
        return max(1, cpu_default)

    if available_ram_mb is None:
        available_ram_mb = get_available_ram_mb()
    if available_ram_mb is None:
        # Can't measure available RAM (no psutil and every OS fallback
        # failed) - fall back to the pre-existing CPU-only behavior rather
        # than guessing.
        return max(1, cpu_default)

    ram_budget_mb = available_ram_mb * ram_budget_ratio
    ram_bound_concurrency = int(ram_budget_mb // ram_per_process_mb)

    return max(1, min(cpu_default, ram_bound_concurrency))


def allocate_local_engine_workers(
    cpu_caps: Dict[str, int],
    ram_per_process_mb: Dict[str, int],
    enabled_engines: Optional[Set[str]] = None,
    available_ram_mb: Optional[int] = None,
    manual_workers: Optional[Dict[str, int]] = None,
    ram_budget_ratio: float = 0.5,
) -> Tuple[Dict[str, int], Dict[str, Any]]:
    """Size all enabled local-engine pools against one shared RAM budget.

    The previous implementation called ``compute_ram_aware_concurrency()``
    once per engine.  Each call independently assumed it could use 50% of
    the machine's available RAM, so enabling four local engines could
    reserve roughly 200% of RAM.  This allocator reserves one budget for
    the whole group instead.

    Rules:
      * Disabled engines get a harmless placeholder of 1 worker and do not
        consume RAM budget.
      * Manual worker counts are preserved exactly as supplied.  The caller
        is responsible for warning about them and enforcing the hard EdgeTTS
        cap; this function never silently reduces a manual override.
      * Automatic workers start at 1 per enabled engine so every enabled
        engine remains usable even when the shared budget is very small.
      * Remaining budget is handed out round-robin, cheapest engine first,
        until no pool can grow without exceeding the budget or its CPU cap.
      * If RAM cannot be measured, automatic workers fall back to their CPU
        caps (the pre-RAM-awareness behaviour), never higher.

    Returns:
        ``(allocation, metadata)``.  ``allocation`` maps every engine in
        ``cpu_caps`` to an int >= 1.  ``metadata`` is diagnostics only and
        includes the budget, estimated footprint, and over-budget flags.
    """
    cpu_caps = {
        str(engine): max(1, int(cap))
        for engine, cap in (cpu_caps or {}).items()
    }
    ram_per_process_mb = {
        str(engine): max(1, int(ram))
        for engine, ram in (ram_per_process_mb or {}).items()
    }

    manual: Dict[str, int] = {}
    for engine, value in (manual_workers or {}).items():
        try:
            requested = int(value)
        except (TypeError, ValueError):
            continue
        if requested > 0:
            manual[str(engine)] = requested

    if enabled_engines is None:
        enabled = set(cpu_caps)
    elif hasattr(enabled_engines, "items"):
        enabled = {
            str(engine)
            for engine, is_enabled in enabled_engines.items()
            if is_enabled
        }
    else:
        enabled = {str(engine) for engine in enabled_engines}
    enabled = {engine for engine in enabled if engine in cpu_caps}

    allocation: Dict[str, int] = {}
    for engine in cpu_caps:
        if engine in enabled:
            allocation[engine] = manual.get(engine, 1)
        else:
            allocation[engine] = 1

    def _estimated_mb() -> int:
        return sum(
            allocation[engine] * ram_per_process_mb.get(engine, 1)
            for engine in enabled
        )

    if available_ram_mb is None:
        for engine in enabled:
            if engine not in manual:
                allocation[engine] = cpu_caps[engine]
        estimated_mb = _estimated_mb()
        return allocation, {
            "enabled": sorted(enabled),
            "budget_mb": None,
            "estimated_mb": estimated_mb,
            "minimum_estimated_mb": estimated_mb,
            "over_budget": False,
            "minimum_over_budget": False,
            "manual": dict(manual),
        }

    try:
        budget_mb = max(0, int(float(available_ram_mb) * float(ram_budget_ratio)))
    except (TypeError, ValueError):
        budget_mb = 0

    estimated_mb = _estimated_mb()
    minimum_estimated_mb = sum(
        ram_per_process_mb.get(engine, 1) for engine in enabled
    )
    minimum_over_budget = minimum_estimated_mb > budget_mb

    # If even the one-worker-per-engine minimum does not fit, keep the
    # minimum and let the caller warn.  Never disable an enabled engine.
    if not minimum_over_budget:
        while True:
            progressed = False
            for engine in sorted(
                enabled,
                key=lambda name: (ram_per_process_mb.get(name, 1), name),
            ):
                if engine in manual:
                    continue
                if allocation[engine] >= cpu_caps[engine]:
                    continue
                cost = ram_per_process_mb.get(engine, 1)
                if estimated_mb + cost > budget_mb:
                    continue
                allocation[engine] += 1
                estimated_mb += cost
                progressed = True
            if not progressed:
                break

    return allocation, {
        "enabled": sorted(enabled),
        "budget_mb": budget_mb,
        "estimated_mb": estimated_mb,
        "minimum_estimated_mb": minimum_estimated_mb,
        "over_budget": estimated_mb > budget_mb,
        "minimum_over_budget": minimum_over_budget,
        "manual": dict(manual),
    }


def get_total_cpu_count():
    """Returns the total number of logical processors."""
    try:
        return multiprocessing.cpu_count()
    except Exception:
        return 4 # Safety fallback

def is_amd_gpu_detected():
    """
    detects if an AMD GPU is present on Windows (for DirectML support).
    This is a heuristic check.
    """
    if platform.system() != "Windows":
        return False
        
    try:
        # Use an argument list, not shell=True. The command is fixed, but
        # avoiding the shell removes an entire class of injection risk.
        result = subprocess.run(
            ["wmic", "path", "win32_VideoController", "get", "name"],
            capture_output=True,
            text=True,
            errors='replace',
            timeout=10,
        )
        if "AMD" in result.stdout or "Radeon" in result.stdout:
            return True
    except FileNotFoundError:
        logger.debug("wmic not available; falling back to PowerShell GPU check")
        try:
            result = subprocess.run(
                [
                    "powershell", "-NoProfile", "-Command",
                    "Get-CimInstance Win32_VideoController | "
                    "Select-Object -ExpandProperty Name",
                ],
                capture_output=True,
                text=True,
                errors='replace',
                timeout=10,
            )
            if "AMD" in result.stdout or "Radeon" in result.stdout:
                return True
        except Exception as e:
            logger.debug(f"Failed to check GPU via PowerShell: {e}")
    except Exception as e:
        logger.debug(f"Failed to check GPU: {e}")
        
    return False

def get_best_onnx_provider():
    """
    Returns the best available provider for ONNX Runtime.
    Prioritizes DirectML on Windows if AMD GPU is present, or CUDA if NVIDIA.
    Defaults to CPU.
    """
    # Note: efficient detection requires importing onnxruntime, but we want this to be lightweight.
    # We will rely on heuristics or defaults.
    
    # Check for AMD GPU on Windows -> DirectML
    if platform.system() == "Windows" and is_amd_gpu_detected():
        return "directml"
        
    # TODO: Add NVIDIA check if needed, but for now user specifically asked about AMD
    
    return "cpu"
