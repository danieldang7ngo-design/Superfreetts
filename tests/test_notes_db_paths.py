import importlib
import os
import sys

from tests import mock_anki


def test_collection_path_prefers_anki_collection_path():
    mock_anki.mock_all()
    import tools.notes_db as notes_db
    importlib.reload(notes_db)

    sys.modules['aqt'].mw.col.path = 'C:/Users/test/AppData/Roaming/Anki2/User 1/collection.anki2'

    assert notes_db.get_collection_path() == 'C:/Users/test/AppData/Roaming/Anki2/User 1/collection.anki2'


def test_user_files_dir_is_relative_to_addon_package():
    mock_anki.mock_all()
    import tools.notes_db as notes_db
    importlib.reload(notes_db)

    expected = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'user_files')
    assert notes_db.get_addon_user_files_dir() == expected
