# Batch Processing Configuration Constants
# This module centralizes all magic numbers and configuration values used in batch processing

from typing import Final

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

# Default number of worker threads (4 = auto-detect CPU cores)
DEFAULT_BATCH_CONCURRENCY: Final[int] = 4

# Timeout for executor shutdown in seconds (time to wait for threads to gracefully finish)
EXECUTOR_SHUTDOWN_TIMEOUT_SECONDS: Final[int] = 5

# Timeout per individual audio generation task in seconds (per task, not total)
# Set high because EdgeTTS might be slow on first request or with network issues
TASK_TIMEOUT_SECONDS: Final[int] = 120  # 2 minutes per task

# ============================================================================
# UI/DISPLAY
# ============================================================================

# Status message icons and formats
STATUS_LOADING_VOICES = "🎙️ Loading voice list..."
STATUS_PREPARING_NOTES = "📝 Preparing {} notes..."
STATUS_ANALYZING_DUPLICATES = "🔍 Analyzing for duplicates..."
STATUS_GENERATING_AUDIO = "🔊 Generating audio ({} unique)..."
STATUS_UPDATING_PROGRESS = "🔊 Generating audio ({}/{} completed)..."
STATUS_APPLYING_RESULTS = "📋 Applying to {} notes..."
STATUS_SAVING_COLLECTION = "💾 Saving to collection..."

# Progress display format
PROGRESS_TEXT_FORMAT = "Completed {} / {}"
ETA_TEXT_FORMAT = "ETA: {}m {}s"
STATUS_SEPARATOR = " — "

# ============================================================================
# DELAYS & TIMING
# ============================================================================

# Sleep duration after status message update (seconds) to allow user to see the message
STATUS_MESSAGE_DISPLAY_DELAY_SECONDS: Final[float] = 0.1

# ============================================================================
# CACHE & FILES
# ============================================================================

# Default cache retention period (days)
DEFAULT_CACHE_RETENTION_DAYS: Final[int] = 30

# Maximum cache retention period (days)
MAX_CACHE_RETENTION_DAYS: Final[int] = 365

# ============================================================================
# ERROR LOGGING
# ============================================================================

# Error message templates
ERROR_VOICE_LIST_PRELOAD_FAILED = "[BATCH] Voice list pre-load failed: {}"
ERROR_AUDIO_GENERATION_FAILED = "Error generating audio for unique task: {}"
ERROR_NOTE_UPDATE_FAILED = "Error updating note {}: {}"
ERROR_QT_EVENTS_PROCESSING_FAILED = "Error processing Qt events: {}"
ERROR_CACHE_FILE_DELETE_FAILED = "Error deleting cache file {}: {}"
ERROR_CACHE_CLEANUP_EXCEPTION = "[CACHE] Error during cache cleanup"
ERROR_CACHE_CLEANUP_FAILED = "Error during cache cleanup: {}"

# ============================================================================
# WARNING MESSAGES
# ============================================================================

WARNING_CACHE_DELETE_ERROR = "[CACHE] Error deleting"

# ============================================================================
# LOGGING MESSAGES
# ============================================================================

# Info message templates
INFO_VOICE_LIST_PRELOADED = "[BATCH] Voice list pre-loaded in {:.2f}s"
INFO_BATCH_STARTING = "[BATCH] Starting to prepare {} notes..."
INFO_BATCH_PREPARED = "[BATCH] Prepared {} notes in {:.2f}s"
INFO_DEDUP_ANALYSIS = "[BATCH] Analyzing for duplicate (text + voice) combinations..."
INFO_DEDUP_FOUND = "[BATCH] Deduplication found: {} tasks, {} unique, {} duplicates (saving {:.1f}% TTS calls) - analyzed in {:.2f}s"
INFO_DEDUP_NOT_FOUND = "[BATCH] No duplicates found - analyzed in {:.2f}s"
INFO_AUDIO_GEN_STARTING = "[BATCH] Starting audio generation with {} threads ({} unique combinations)"
INFO_AUDIO_GEN_COMPLETED = "[BATCH] Generated {} audio files in {:.2f}s"
INFO_RESULTS_APPLIED = "[BATCH] Applied results in {:.2f}s"
INFO_COLLECTION_UPDATING = "[BATCH] Updating Anki collection with {} note changes..."
INFO_COLLECTION_UPDATED = "[BATCH] Updated collection in {:.2f}s"
INFO_BATCH_COMPLETED = "[BATCH] Completed batch in {:.2f}s (extract: {:.2f}s, dedup: {:.2f}s, gen: {:.2f}s, update: {:.2f}s)"
INFO_CPU_CORES_DETECTED = "[BATCH] Auto-detected {} CPU cores, using {} threads for batch processing"
INFO_STOPPING_BATCH = "stopping current batch"
INFO_CACHE_CLEANUP_STARTED = "[CACHE] Starting cache cleanup."
INFO_CACHE_CLEANUP_FINISHED = "[CACHE] Cache cleanup finished."

# ============================================================================
# DEBUG LOGGING
# ============================================================================

DEBUG_CLEANUP_DISABLED = "cleanup_user_files: cache disabled by preferences, skipping"
DEBUG_CLEANUP_RETENTION_ZERO = "cleanup_user_files: retention_days is 0, skipping automatic cleanup"
DEBUG_CLEANUP_DIR_NOT_EXISTS = "cleanup_user_files: user_files dir does not exist at {}"
