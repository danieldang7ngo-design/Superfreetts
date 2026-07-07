# Batch Processing Configuration Constants
# This module centralizes all magic numbers and configuration values used in batch processing

from typing import Final

try:
    from . import _local_override
except Exception:
    _local_override = None

# ============================================================================
# MEMORY MANAGEMENT
# ============================================================================

# Memory usage threshold for aggressive throttling (percent)
# If system exceeds this, batch processing will throttle aggressively
MEMORY_THROTTLE_THRESHOLD: Final[int] = 80  # Throttle at 80% RAM usage

# Garbage collection frequency (number of items between GC calls)
# Lower = more frequent GC, higher = less frequent but more efficient
GC_FREQUENCY_PREPARATION: Final[int] = 20   # GC every 20 notes during preparation
GC_FREQUENCY_GENERATION: Final[int] = 5     # GC every 5 unique tasks (aggressive)
GC_FREQUENCY_APPLICATION: Final[int] = 10   # GC every 10 notes during application
GC_FREQUENCY_UPDATE: Final[int] = 15        # GC every 15 notes during update

# Qt event processing frequency (number of items between processEvents calls)
# Lower = more UI responsiveness, higher = better performance
QT_EVENT_FREQUENCY: Final[int] = 3          # Process Qt events frequently (every 3 tasks)

# ============================================================================
# THREADING & CONCURRENCY
# ============================================================================

# Maximum number of CPU cores to use for batch processing (cap to prevent resource exhaustion)
MAX_WORKER_THREADS: Final[int] = 20

# EdgeTTS concurrency cap (separate from CPU-bound engines).
# Default 3 to avoid Microsoft rate-limiting for most users.
# Power users: run set_edge_workers_20.py at the addon root to raise this locally.
EDGETTS_MAX_WORKERS: Final[int] = 3
if _local_override is not None:
    EDGETTS_MAX_WORKERS = int(getattr(_local_override, "EDGETTS_MAX_WORKERS", EDGETTS_MAX_WORKERS))

# Sequence mode can mix services, so keep its nested pool small enough that
# service-specific caps and memory pressure are not bypassed.
SEQUENCE_MAX_WORKER_THREADS: Final[int] = 4

# Default number of worker threads (4 = auto-detect CPU cores)
DEFAULT_BATCH_CONCURRENCY: Final[int] = 4

# Timeout for executor shutdown in seconds (time to wait for threads to gracefully finish)
EXECUTOR_SHUTDOWN_TIMEOUT_SECONDS: Final[int] = 5

# Timeout per individual audio generation task in seconds (per task, not total)
# Set high because some engines may take longer for first request or on slow networks.
TASK_TIMEOUT_SECONDS: Final[int] = 120  # 2 minutes per task

# Per-request timeout for EdgeTTS. This is shorter to fail fast on network issues.
EDGETTS_TASK_TIMEOUT_SECONDS: Final[int] = 30

# Sleep duration after status message update (seconds) to allow user to see the message
STATUS_MESSAGE_DISPLAY_DELAY_SECONDS: Final[float] = 0.1

# ============================================================================
# CACHE & FILES
# ============================================================================

# Default cache retention period (days)
DEFAULT_CACHE_RETENTION_DAYS: Final[int] = 30

# Maximum cache retention period (days)
MAX_CACHE_RETENTION_DAYS: Final[int] = 365
