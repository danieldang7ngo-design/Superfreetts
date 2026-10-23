import re
from typing import List, Any

from . import errors
from . import text_utils
from . import constants
from . import logging_utils

logger = logging_utils.get_child_logger(__name__)


def keep_only_sound_tags(field_value):
    matches = re.findall(r"\[sound:[^\]]+\]", field_value)
    return " ".join(matches)


def get_collection_sound_tag(anki_utils, full_filename, audio_filename, added_media_files=None):
    # A batch usually shares one audio file between many notes.  media_add_file
    # is idempotent but not free, so callers may pass a per-batch set to skip
    # repeat calls for files that were already imported.
    if added_media_files is None or full_filename not in added_media_files:
        anki_utils.media_add_file(full_filename)
        if added_media_files is not None:
            added_media_files.add(full_filename)
    return f"[sound:{audio_filename}]", audio_filename


def update_note_with_audio(anki_utils, note, batch, source_text, sound_file, full_filename, anki_collection, update_collection=True, added_media_files=None):
    target_field = batch.target.target_field
    if target_field not in note:
        raise errors.TargetFieldNotFoundError(target_field)

    sound_tag, _ = get_collection_sound_tag(anki_utils, full_filename, sound_file, added_media_files)
    target_field_content = note[target_field]

    if batch.target.remove_sound_tag:
        target_field_content = text_utils.strip_sound_tag(target_field_content)

    # Idempotent re-apply: a checkpointed resume (or a batch re-run) can target
    # a note that already references this exact audio file.  Never add a second
    # identical [sound:...] tag.
    if batch.target.text_and_sound_tag:
        if sound_tag not in target_field_content:
            target_field_content = f"{target_field_content} {sound_tag}"
    else:
        target_field_content = keep_only_sound_tags(target_field_content)
        if sound_tag not in target_field_content:
            target_field_content = f"{target_field_content} {sound_tag}"

    note[target_field] = target_field_content.strip()
    if update_collection:
        anki_collection.update_note(note)
    return note[target_field]


def ensure_note_tag(note: Any, tag_name: str) -> bool:
    """Add *tag_name* to *note* if not already present.

    Returns ``True`` if the tag was added, ``False`` if it already existed.
    Works with both the new ``note.add_tag()`` API and the legacy ``note.tags``
    list approach.
    """
    tags = list(getattr(note, 'tags', []) or [])
    if tag_name in tags:
        return False

    if hasattr(note, 'add_tag'):
        try:
            note.add_tag(tag_name)
            return True
        except Exception as e:
            logger.debug(f'falling back to direct tag assignment for [{tag_name}]: {e}')

    tags.append(tag_name)
    note.tags = tags
    return True


def tag_error_notes(
    anki_utils: Any,
    note_ids: List[int],
    anki_collection: Any,
    tag_name: str = constants.WORKFLOW_ERROR_TAG,
) -> int:
    """Tag all notes in *note_ids* with *tag_name*.

    Skips duplicates (each note_id is processed only once).
    Returns the number of notes actually tagged.
    """
    tagged_count = 0
    notes_to_update = []
    for note_id in dict.fromkeys(note_ids):
        note = anki_utils.get_note_by_id(note_id)
        if ensure_note_tag(note, tag_name):
            notes_to_update.append(note)

    if not notes_to_update:
        return tagged_count

    update_notes = getattr(anki_collection, 'update_notes', None)
    if callable(update_notes):
        update_notes(notes_to_update)
        tagged_count = len(notes_to_update)
    else:
        # Older Anki builds / test doubles may only expose update_note().
        for note in notes_to_update:
            anki_collection.update_note(note)
            tagged_count += 1
    return tagged_count

