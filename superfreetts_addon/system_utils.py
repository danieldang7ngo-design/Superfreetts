
import os
import multiprocessing
import platform
import subprocess
import logging
import re
import shutil

# Try to import psutil for system RAM detection, fallback if not available.
# Same defensive pattern as resource_manager.py (kept consistent on purpose).
try:
    import psutil
    HAS_PSUTIL = True
except Exception:
    HAS_PSUTIL = False

logger = logging.getLogger(__name__)

def has_problematic_path_chars(path):
    """
    Check if a path contains characters that may cause issues with C++ tools on Windows.
    Returns True if the path contains non-ASCII characters or other problematic chars.
    """
    if not path:
        return False
    
    # Check for non-ASCII characters (like ä, ö, ü, ñ, etc.)
    try:
        # If we can encode to ASCII without errors, it's safe
        path.encode('ascii')
        return False
    except UnicodeEncodeError:
        # Contains non-ASCII characters
        return True
    
    # Additional checks for other problematic patterns could be added here
    # For now, non-ASCII is the main issue on Windows with Piper
    return False


def get_safe_data_dir():
    """
    Get a safe data directory path without special characters.
    Returns a path like C:\SuperFreeTTS_Data that is guaranteed to work.
    """
    # Use C:\SuperFreeTTS_Data as the safe fallback location
    safe_dir = r'C:\SuperFreeTTS_Data'
    return safe_dir


def migrate_data_to_safe_location(old_path, new_path):
    """
    Migrate data from old path to new safe path.
    Returns True if migration was successful, False otherwise.
    """
    try:
        if not os.path.exists(old_path):
            logger.warning(f"Old path does not exist: {old_path}")
            return False
        
        # Create new directory if it doesn't exist
        os.makedirs(new_path, exist_ok=True)
        
        # Copy all contents from old to new
        for item in os.listdir(old_path):
            src = os.path.join(old_path, item)
            dst = os.path.join(new_path, item)
            
            if os.path.isdir(src):
                shutil.copytree(src, dst, dirs_exist_ok=True)
            else:
                shutil.copy2(src, dst)
        
        logger.info(f"Successfully migrated data from {old_path} to {new_path}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to migrate data: {e}")
        return False

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
    determined (psutil missing, or the call failed).

    Callers MUST treat None as "unknown" and skip any RAM-based capping in
    that case rather than assuming a value - see root cause 2.6 in
    superfreetts_macos_crash_fix_plan.md: guessing a number here would
    violate the "no fabricated numbers" rule just as badly as the bug
    we're fixing.
    """
    if not HAS_PSUTIL:
        return None
    try:
        return int(psutil.virtual_memory().available / 1024 / 1024)
    except Exception as e:
        logger.debug(f"Failed to get available RAM: {e}")
        return None


def compute_ram_aware_concurrency(cpu_default: int, ram_per_process_mb, ram_budget_ratio: float = 0.5):
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

    Returns:
        An int >= 1. Never raises.
    """
    if ram_per_process_mb is None or ram_per_process_mb <= 0:
        # No reliable per-process estimate available - do not fabricate one.
        return max(1, cpu_default)

    available_ram_mb = get_available_ram_mb()
    if available_ram_mb is None:
        # Can't measure available RAM (no psutil, or call failed) - fall
        # back to the pre-existing CPU-only behavior rather than guessing.
        return max(1, cpu_default)

    ram_budget_mb = available_ram_mb * ram_budget_ratio
    ram_bound_concurrency = int(ram_budget_mb // ram_per_process_mb)

    return max(1, min(cpu_default, ram_bound_concurrency))


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
        # Simple wmic check (fast)
        cmd = "wmic path win32_VideoController get name"
        result = subprocess.run(cmd, capture_output=True, text=True, errors='replace', shell=True)
        if "AMD" in result.stdout or "Radeon" in result.stdout:
            return True
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
