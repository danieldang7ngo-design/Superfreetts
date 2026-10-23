# Batch Processing Configuration Constants
# This module centralizes all magic numbers and configuration values used in batch processing

import logging
from typing import Final

logger = logging.getLogger(__name__)

try:
    from . import _local_override
except Exception as e:
    logger.debug(f"No _local_override or failed to load: {e}")
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

# Default number of worker threads (4 = auto-detect CPU cores)
DEFAULT_BATCH_CONCURRENCY: Final[int] = 4

# Timeout for executor shutdown in seconds (time to wait for threads to gracefully finish)
EXECUTOR_SHUTDOWN_TIMEOUT_SECONDS: Final[int] = 5

# Timeout per individual audio generation task in seconds (per task, not total)
# Set high because some engines may take longer for first request or on slow networks.
TASK_TIMEOUT_SECONDS: Final[int] = 120  # 2 minutes per task


# ============================================================================
# LOCAL ENGINE IPC (stdin/stdout runner processes)
# ============================================================================
# A wedged runner must never hold a worker thread forever.  One request gets
# this long before the runner is killed and retried once with a fresh process.
# P95 for the local engines measured 1.6-29.9 s, so 60/120 s leaves room for a
# slow machine while still detecting a real hang.
IPC_SINGLE_REQUEST_TIMEOUT_SECONDS: Final[float] = 60.0
IPC_BATCH_REQUEST_TIMEOUT_SECONDS: Final[float] = 120.0
# The first request on a freshly spawned runner also loads the model (Kokoro
# and Supertonic measured ~10 s for the first three requests), so it gets a
# longer allowance.  It applies to the first request of a process only.
IPC_COLD_START_TIMEOUT_SECONDS: Final[float] = 150.0
# Backstop for a leaked permit: waiting for a pool slot is normal while other
# runners work, but the wait must be bounded or the batch hangs forever.
IPC_ACQUIRE_TIMEOUT_SECONDS: Final[float] = 300.0

# If no batch future completes for this long, assume generation is wedged and
# mark pending tasks as failed. Must be comfortably longer than the slowest
# single task (including first-run model loading), or slow-but-healthy batches
# would be cancelled.
BATCH_STALL_TIMEOUT_SECONDS: Final[int] = 180

# Per-request timeout for EdgeTTS. Raised to 120s because Vietnamese and other
# non-English text with diacritics can take significantly longer on Microsoft's
# server (multi-segment SSML, each with its own WebSocket round-trip).
# Set back to 30s if you prefer quick failure and rely on the retry mechanism.
EDGETTS_TASK_TIMEOUT_SECONDS: Final[int] = 180

# Crash-recovery checkpoint cadence: notes between atomic checkpoint writes.
# The checkpoint file stays small (a note id -> status map) and a crash loses
# at most this many notes of progress, which are re-applied on resume.
CHECKPOINT_FLUSH_EVERY: Final[int] = 50
# The apply phase commits the collection in chunks instead of one transaction
# for the whole batch, so "applied" can be checkpointed as it goes.  A crash
# mid-apply re-applies at most this many notes (same audio file, idempotent).
CHECKPOINT_APPLY_COMMIT_EVERY: Final[int] = 50

# Sleep duration after status message update (seconds) to allow user to see the message
STATUS_MESSAGE_DISPLAY_DELAY_SECONDS: Final[float] = 0.1

# ============================================================================
# CACHE & FILES
# ============================================================================

# Default cache retention period (days)
DEFAULT_CACHE_RETENTION_DAYS: Final[int] = 30

# Maximum cache retention period (days)
MAX_CACHE_RETENTION_DAYS: Final[int] = 365
