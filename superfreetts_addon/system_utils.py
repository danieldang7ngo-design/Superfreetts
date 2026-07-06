
import os
import multiprocessing
import platform
import subprocess
import logging

logger = logging.getLogger(__name__)

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
    except:
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

def get_total_cpu_count():
    """Returns the total number of logical processors."""
    try:
        return multiprocessing.cpu_count()
    except:
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
