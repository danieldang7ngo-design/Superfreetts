import os
import sys
import types
from unittest.mock import Mock

import pytest

from tests import mock_anki

mock_anki.mock_all()

addon_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, addon_dir)
sys.path.insert(0, os.path.join(addon_dir, "external"))

from superfreetts_addon import config_models, errors, note_audio_updater


class MockAnkiUtils:
    def __init__(self):
        self.added = []

    def media_add_file(self, full_filename):
        self.added.append(full_filename)


def make_batch(text_and_sound_tag=False, remove_sound_tag=True):
    batch = Mock()
    batch.target = config_models.BatchTarget(
        target_field="Audio",
        text_and_sound_tag=text_and_sound_tag,
        remove_sound_tag=remove_sound_tag,
    )
    return batch


def test_update_note_sound_only_replaces_existing_sound_tags():
    anki_utils = MockAnkiUtils()
    collection = Mock()
    note = {"Audio": "old text [sound:old.mp3]"}

    result = note_audio_updater.update_note_with_audio(
        anki_utils, note, make_batch(), "source", "new.mp3", "/tmp/new.mp3", collection
    )

    assert result == "[sound:new.mp3]"
    assert note["Audio"] == "[sound:new.mp3]"
    assert anki_utils.added == ["/tmp/new.mp3"]
    collection.update_note.assert_called_once_with(note)


def test_update_note_text_and_sound_appends_sound_tag():
    note = {"Audio": "old text [sound:old.mp3]"}

    result = note_audio_updater.update_note_with_audio(
        MockAnkiUtils(), note, make_batch(text_and_sound_tag=True), "source", "new.mp3", "/tmp/new.mp3", Mock()
    )

    assert result == "old text [sound:new.mp3]"


def test_update_note_keep_existing_sound_tags_appends_new_sound():
    note = {"Audio": "old text [sound:old.mp3]"}

    result = note_audio_updater.update_note_with_audio(
        MockAnkiUtils(), note, make_batch(remove_sound_tag=False), "source", "new.mp3", "/tmp/new.mp3", Mock()
    )

    assert result == "[sound:old.mp3] [sound:new.mp3]"


def test_update_note_missing_target_field_raises():
    with pytest.raises(errors.TargetFieldNotFoundError):
        note_audio_updater.update_note_with_audio(
            MockAnkiUtils(), {"Front": "text"}, make_batch(), "source", "new.mp3", "/tmp/new.mp3", Mock()
        )

def test_update_note_text_and_sound_is_idempotent():
    """Resume/at-least-once apply must not duplicate an identical sound tag."""
    note = {"Audio": "text [sound:new.mp3]"}

    result = note_audio_updater.update_note_with_audio(
        MockAnkiUtils(), note, make_batch(text_and_sound_tag=True), "source", "new.mp3", "/tmp/new.mp3", Mock()
    )

    assert result == "text [sound:new.mp3]"
    assert result.count("[sound:new.mp3]") == 1


def test_update_note_sound_only_is_idempotent():
    note = {"Audio": "[sound:new.mp3]"}

    result = note_audio_updater.update_note_with_audio(
        MockAnkiUtils(), note, make_batch(remove_sound_tag=False), "source", "new.mp3", "/tmp/new.mp3", Mock()
    )

    assert result == "[sound:new.mp3]"


def test_added_media_files_set_skips_repeated_media_add():
    anki_utils = MockAnkiUtils()
    added_media_files = set()
    first = {"Audio": ""}
    second = {"Audio": ""}

    note_audio_updater.update_note_with_audio(
        anki_utils, first, make_batch(), "source", "shared.mp3", "/tmp/shared.mp3", Mock(),
        added_media_files=added_media_files,
    )
    note_audio_updater.update_note_with_audio(
        anki_utils, second, make_batch(), "source", "shared.mp3", "/tmp/shared.mp3", Mock(),
        added_media_files=added_media_files,
    )

    assert anki_utils.added == ["/tmp/shared.mp3"]
    assert first["Audio"] == "[sound:shared.mp3]"
    assert second["Audio"] == "[sound:shared.mp3]"


def test_tag_error_notes_uses_single_batch_update():
    notes = {1: types.SimpleNamespace(tags=[]), 2: types.SimpleNamespace(tags=[])}
    anki_utils = Mock()
    anki_utils.get_note_by_id.side_effect = notes.get
    collection = Mock()

    tagged = note_audio_updater.tag_error_notes(
        anki_utils, [1, 2, 2], collection, tag_name="tts-error"
    )

    assert tagged == 2
    assert notes[1].tags == ["tts-error"]
    collection.update_notes.assert_called_once()
    collection.update_note.assert_not_called()


def test_tag_error_notes_falls_back_to_update_note_without_batch_api():
    class LegacyCollection:
        def __init__(self):
            self.updated = []

        def update_note(self, note):
            self.updated.append(note)

    notes = {1: types.SimpleNamespace(tags=[])}
    anki_utils = Mock()
    anki_utils.get_note_by_id.side_effect = notes.get
    collection = LegacyCollection()

    tagged = note_audio_updater.tag_error_notes(
        anki_utils, [1], collection, tag_name="tts-error"
    )

    assert tagged == 1
    assert collection.updated == [notes[1]]
