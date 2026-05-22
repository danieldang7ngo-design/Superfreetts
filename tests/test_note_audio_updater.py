import os
import sys
from unittest.mock import Mock

import pytest

from tests import mock_anki

mock_anki.mock_all()

addon_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, addon_dir)
sys.path.insert(0, os.path.join(addon_dir, "external"))

from superfreetss_addon import config_models, errors, note_audio_updater


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

