"""
Temporarily suppresses Anki's own automatic backup creation for the
duration of the batch "Apply Generated Audio" step, and restores it on
every exit path: success, failure, or user cancellation. Also repairs
itself automatically if Anki crashes or is force-quit while suppressed.

Why this is needed:
Anki runs a QTimer every 5 minutes that tries to create a backup. The
attempt is wrapped in a QueryOp with a visible "Creating backup..."
progress dialog. If this addon's own Apply step is already using Anki's
single collection-access slot when that timer fires, Anki's backup QueryOp
has to wait its turn -- but its dialog was already shown before its turn
came up, so the dialog appears to freeze on screen until the addon's Apply
step finishes. Suppressing backup creation for the (usually short) duration
of the Apply step prevents this dialog from ever being shown mid-batch.

Why this is safe:
Collection.create_backup is a normal Python method (not a restricted
object), so replacing it on the specific mw.col object currently in use,
and putting the original back afterward, is a safe and reversible
operation. This module never modifies any Anki source file.
"""
from aqt import mw
import logging

logger = logging.getLogger(__name__)

# The key used to remember "backups are currently suppressed" inside the
# user's Anki profile, so a crash can be detected and repaired on next
# launch. This must be a string that is unlikely to collide with any other
# addon's or Anki's own profile keys.
MARKER_KEY = "superfreetts_backup_suppressed"

# How many nested "batch Apply runs" are currently in progress. Using a
# counter instead of a plain True/False flag means that if two Apply runs
# were ever somehow started before the first one finished, backups would
# only be re-enabled after BOTH have finished, not after the first one
# alone. This should not normally happen in this addon's UI (only one
# batch dialog can apply at a time), but the counter costs nothing and
# removes the risk entirely.
_active_count = 0

# Holds the real, original create_backup method while it is replaced, so
# it can be put back exactly as it was.
_original_create_backup = None

# Holds a reference to mw.peroidic_backup_timer while it is stopped,
# so it can be restarted with the correct interval.
_backup_timer_handle = None


def disable_backups():
    """
    Call this exactly once, as the very first line of the batch Apply
    function, before any QueryOp is created.
    """
    global _active_count, _original_create_backup, _backup_timer_handle

    logger.info(f'disable_backups called, current _active_count={_active_count}')

    if _active_count == 0:
        # Stop the periodic backup timer so that Anki never creates the
        # "Creating backup..." QueryOp in the first place. Stopping the
        # timer is the *real* fix — the no-op below is belt-and-suspenders.
        timer = getattr(mw, 'peroidic_backup_timer', None)
        if timer is not None:
            _backup_timer_handle = timer
            timer.stop()
            logger.info("STOPPED periodic backup timer")

        # Save the real method so it can be restored later.
        _original_create_backup = mw.col.create_backup

        def _noop_create_backup(*, backup_folder=None, force=False, wait_for_completion=False):
            # Same keyword arguments as the real method, so any caller of
            # mw.col.create_backup(...) -- including Anki's own periodic
            # timer -- works exactly as before, it just does nothing and
            # reports "no backup was created" (False), matching the real
            # method's return type.
            return False

        logger.info("INSTALLED no-op create_backup (backups suppressed)")
        mw.col.create_backup = _noop_create_backup

        # Record in the user's profile that backups are currently
        # suppressed, so a crash can be detected and repaired next launch.
        mw.pm.profile[MARKER_KEY] = True
        mw.pm.save()

        logger.info("Backup suppression enabled for batch apply run")

    _active_count += 1


def restore_backups(trigger_manual_backup=True):
    """
    Call this exactly once on every path out of the batch Apply function:
    when it finishes normally, when the user cancels it, and when it fails
    with an error. Safe to call even if disable_backups() was never called
    (it will simply do nothing in that case).
    """
    global _active_count, _original_create_backup, _backup_timer_handle

    logger.info(f'restore_backups called, trigger_manual_backup={trigger_manual_backup}, _active_count={_active_count}')

    if _active_count > 0:
        _active_count -= 1

    if _active_count == 0 and _original_create_backup is not None:
        logger.info("RESTORING real create_backup function now (backups go live)")
        mw.col.create_backup = _original_create_backup
        _original_create_backup = None

        # Restart the periodic backup timer.
        if _backup_timer_handle is not None:
            try:
                _backup_timer_handle.start(5 * 60 * 1000)
                logger.info("RESTARTED periodic backup timer")
            except Exception as e:
                logger.warning(f"Failed to restart backup timer: {e}")
            _backup_timer_handle = None

        mw.pm.profile.pop(MARKER_KEY, None)
        mw.pm.save()

        logger.info("Backup suppression disabled, backups restored")

        if trigger_manual_backup:
            try:
                # mw.create_backup_now() is a built-in Anki helper, already
                # designed for exactly this situation ("take a backup right
                # now, as part of a longer background operation"). It blocks
                # until the backup finishes, so it is run on a background
                # thread here rather than directly on the main thread.
                mw.taskman.run_in_background(mw.create_backup_now, lambda _: None)
            except Exception as e:
                logger.warning(f"Post-apply safety backup failed: {e}")


def check_and_heal_stale_disable():
    """
    Call this exactly once, every time an Anki profile is opened (see
    Step 4.4). Detects and repairs a case where a previous session crashed
    or was force-quit while backups were suppressed, leaving the marker
    behind.

    Note: on a fresh Anki launch, mw.col is a brand new Collection object,
    so its create_backup method is already the real, un-replaced one --
    there is nothing to "put back" on the object itself. The only real
    repair needed is: clear the leftover marker, and take one fresh backup
    immediately, since we know the crashed session's scheduled backups
    were skipped the whole time it was suppressed.
    """
    global _active_count, _original_create_backup, _backup_timer_handle

    if mw.pm.profile.get(MARKER_KEY):
        _active_count = 0
        _original_create_backup = None
        _backup_timer_handle = None
        mw.pm.profile.pop(MARKER_KEY, None)
        mw.pm.save()

        logger.info("Repaired a stale backup-suppression marker left over from a crash")

        try:
            mw.taskman.run_in_background(mw.create_backup_now, lambda _: None)
        except Exception as e:
            logger.warning(f"Post-crash safety backup failed: {e}")