import re

from . import errors
from . import text_utils


def keep_only_sound_tags(field_value):
    matches = re.findall(r"\[sound:[^\]]+\]", field_value)
    return " ".join(matches)


def get_collection_sound_tag(anki_utils, full_filename, audio_filename):
    anki_utils.media_add_file(full_filename)
    return f"[sound:{audio_filename}]", audio_filename


def update_note_with_audio(anki_utils, note, batch, source_text, sound_file, full_filename, anki_collection, update_collection=True):
    target_field = batch.target.target_field
    if target_field not in note:
        raise errors.TargetFieldNotFoundError(target_field)

    sound_tag, _ = get_collection_sound_tag(anki_utils, full_filename, sound_file)
    target_field_content = note[target_field]

    if batch.target.remove_sound_tag:
        target_field_content = text_utils.strip_sound_tag(target_field_content)

    if batch.target.text_and_sound_tag:
        target_field_content = f"{target_field_content} {sound_tag}"
    else:
        target_field_content = keep_only_sound_tags(target_field_content)
        target_field_content = f"{target_field_content} {sound_tag}"

    note[target_field] = target_field_content.strip()
    if update_collection:
        anki_collection.update_note(note)
    return note[target_field]
