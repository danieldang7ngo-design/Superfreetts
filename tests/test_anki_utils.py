"""Tests for the Anki/aqt boundary layer (``anki_utils``).

Every Anki API call in the add-on funnels through ``anki_utils`` - that is what
keeps the rest of the test suite Anki-free.  The behaviours pinned here are the
ones callers actually rely on: config round-trips, UI-language fallback to
English, night-mode colours/stylesheets (regression guard for Issue #1, where
light-mode colours leaked into night mode), the batched note lookup and the
undo/editor/dialog wrappers.
"""

import os
import types
from unittest.mock import MagicMock

import pytest

from superfreetts_addon import anki_utils, config_models, constants, i18n


@pytest.fixture
def mw(monkeypatch):
    """Fresh ``aqt.mw`` so each test controls the Anki surface it touches."""
    mw = MagicMock()
    monkeypatch.setattr(anki_utils.aqt, "mw", mw)
    return mw


@pytest.fixture
def anki():
    return anki_utils.AnkiUtils()


@pytest.fixture
def night_mode(monkeypatch):
    """Install a controllable ``aqt.theme.theme_manager``."""

    def _set(enabled):
        manager = types.SimpleNamespace(night_mode=enabled)
        monkeypatch.setattr(anki_utils.aqt.theme, "theme_manager", manager, raising=False)
        return manager

    return _set


# --------------------------------------------------------------------------- #
# config
# --------------------------------------------------------------------------- #


@pytest.mark.unit
def test_get_config_uses_addon_name(mw, anki):
    mw.addonManager.getConfig.return_value = {"preferences": {"ui_language": "vi"}}

    assert anki.get_config() == {"preferences": {"ui_language": "vi"}}
    mw.addonManager.getConfig.assert_called_once_with(constants.CONFIG_ADDON_NAME)


@pytest.mark.unit
def test_write_config_forwards_to_addon_manager(mw, anki):
    payload = {"service_config": {"EdgeTTS": {"concurrency_workers": 3}}}

    anki.write_config(payload)

    mw.addonManager.writeConfig.assert_called_once_with(constants.CONFIG_ADDON_NAME, payload)


@pytest.mark.unit
def test_get_addon_dir_is_the_package_parent():
    # get_addon_dir() climbs one level above the module: the directory Anki
    # installs as the add-on folder (which contains superfreetts_addon/).
    addon_dir = anki_utils.AnkiUtils().get_addon_dir()
    package_dir = os.path.dirname(os.path.abspath(anki_utils.__file__))

    # The contract is "one level above the package", not the name of the
    # directory the repository happens to be cloned into (CI uses
    # Superfreetts/, dev machines use superfreetts/).
    assert os.path.normcase(os.path.abspath(addon_dir)) == os.path.normcase(
        os.path.dirname(package_dir)
    )
    assert os.path.isdir(os.path.join(addon_dir, "superfreetts_addon"))


@pytest.mark.unit
def test_get_user_files_dir_lives_under_addon_dir():
    user_files_dir = anki_utils.AnkiUtils().get_user_files_dir()
    addon_dir = anki_utils.AnkiUtils().get_addon_dir()

    assert os.path.normpath(user_files_dir) == os.path.normpath(
        os.path.join(addon_dir, "user_files")
    )


# --------------------------------------------------------------------------- #
# UI language
# --------------------------------------------------------------------------- #


@pytest.mark.unit
def test_get_ui_language_returns_supported_language(mw, anki):
    mw.addonManager.getConfig.return_value = {"preferences": {"ui_language": "vi"}}

    assert anki.get_ui_language() == "vi"


@pytest.mark.unit
def test_get_ui_language_falls_back_to_english_for_unsupported_language(mw, anki):
    mw.addonManager.getConfig.return_value = {"preferences": {"ui_language": "klingon"}}

    assert anki.get_ui_language() == "en"


@pytest.mark.unit
def test_get_ui_language_defaults_to_english_for_empty_config(mw, anki):
    mw.addonManager.getConfig.return_value = {}

    assert anki.get_ui_language() == "en"


@pytest.mark.unit
def test_get_ui_language_defaults_to_english_when_config_is_none(mw, anki):
    mw.addonManager.getConfig.return_value = None

    assert anki.get_ui_language() == "en"


@pytest.mark.unit
def test_get_ui_language_falls_back_to_raw_dict_when_deserialization_fails(mw, anki, monkeypatch):
    mw.addonManager.getConfig.return_value = {"preferences": {"ui_language": "ja"}}

    def boom(_config):
        raise ValueError("corrupt preferences")

    monkeypatch.setattr(config_models, "deserialize_preferences", boom)

    assert anki.get_ui_language() == "ja"


@pytest.mark.unit
def test_get_ui_language_falls_back_to_english_when_deserialization_fails_without_key(
    mw, anki, monkeypatch
):
    mw.addonManager.getConfig.return_value = {"preferences": {}}

    def boom(_config):
        raise ValueError("corrupt preferences")

    monkeypatch.setattr(config_models, "deserialize_preferences", boom)

    assert anki.get_ui_language() == "en"


@pytest.mark.unit
def test_every_supported_language_is_accepted(mw, anki):
    for language in i18n.SUPPORTED_LANGUAGES:
        mw.addonManager.getConfig.return_value = {"preferences": {"ui_language": language}}
        assert anki.get_ui_language() == language


# --------------------------------------------------------------------------- #
# night mode / colours (Issue #1 regression guard)
# --------------------------------------------------------------------------- #


@pytest.mark.unit
@pytest.mark.parametrize("enabled", [False, True])
def test_night_mode_enabled_reads_theme_manager(night_mode, anki, enabled):
    night_mode(enabled)

    assert anki.night_mode_enabled() is enabled


@pytest.mark.unit
@pytest.mark.parametrize(
    ("enabled", "expected"),
    [
        (False, constants.GREEN_COLOR_REGULAR),
        (True, constants.GREEN_COLOR_NIGHTMODE),
    ],
)
def test_get_green_css_color_switches_with_night_mode(night_mode, anki, enabled, expected):
    night_mode(enabled)

    assert anki.get_green_css_color() == expected


@pytest.mark.unit
@pytest.mark.parametrize(
    ("enabled", "expected"),
    [
        (False, constants.RED_COLOR_REGULAR),
        (True, constants.RED_COLOR_NIGHTMODE),
    ],
)
def test_get_red_css_color_switches_with_night_mode(night_mode, anki, enabled, expected):
    night_mode(enabled)

    assert anki.get_red_css_color() == expected


@pytest.mark.unit
def test_light_and_night_colours_are_distinct(night_mode, anki):
    # Issue #1: the light-mode colours were reused in night mode, which made the
    # status text unreadable on a dark background.
    night_mode(False)
    light = (anki.get_green_css_color(), anki.get_red_css_color())

    night_mode(True)
    dark = (anki.get_green_css_color(), anki.get_red_css_color())

    assert light[0] != dark[0]
    assert light[1] != dark[1]


@pytest.mark.unit
@pytest.mark.parametrize(
    ("enabled", "expected"),
    [
        (False, constants.GREEN_STYLESHEET),
        (True, constants.GREEN_STYLESHEET_NIGHTMODE),
    ],
)
def test_get_green_stylesheet_switches_with_night_mode(night_mode, anki, enabled, expected):
    night_mode(enabled)

    stylesheet = anki.get_green_stylesheet()

    assert stylesheet == expected
    assert "background-color" in stylesheet


@pytest.mark.unit
@pytest.mark.parametrize(
    ("enabled", "expected"),
    [
        (False, constants.RED_STYLESHEET),
        (True, constants.RED_STYLESHEET_NIGHTMODE),
    ],
)
def test_get_red_stylesheet_switches_with_night_mode(night_mode, anki, enabled, expected):
    night_mode(enabled)

    stylesheet = anki.get_red_stylesheet()

    assert stylesheet == expected
    assert "background-color" in stylesheet


@pytest.mark.unit
def test_red_stylesheet_differs_between_modes(night_mode, anki):
    night_mode(False)
    light = anki.get_red_stylesheet()
    night_mode(True)
    dark = anki.get_red_stylesheet()

    assert light != dark


# --------------------------------------------------------------------------- #
# batched note lookup
# --------------------------------------------------------------------------- #


class _FakeDb:
    """Minimal stand-in for ``aqt.mw.col.db`` that records the batched queries."""

    def __init__(self, rows):
        self.rows = rows
        self.calls = []

    def all(self, sql, *params):
        self.calls.append((sql, params))
        wanted = set(params)
        return [row for row in self.rows if row[0] in wanted]


def _install_collection(mw, rows, models):
    db = _FakeDb(rows)
    mw.col.db = db
    mw.col.models.get.side_effect = lambda mid: models.get(mid)
    return db


@pytest.mark.unit
def test_get_note_field_maps_returns_field_dict_per_note(mw, anki):
    _install_collection(
        mw,
        [(1, 10, "front one\x1fback one"), (2, 10, "front two\x1fback two")],
        {10: {"flds": [{"name": "Front"}, {"name": "Back"}]}},
    )

    field_maps = anki.get_note_field_maps([1, 2])

    assert field_maps == {
        1: {"Front": "front one", "Back": "back one"},
        2: {"Front": "front two", "Back": "back two"},
    }


@pytest.mark.unit
def test_get_note_field_maps_chunks_large_batches(mw, anki):
    note_ids = list(range(1, 1202))  # 500 + 500 + 201
    rows = [(note_id, 10, "f\x1fb") for note_id in note_ids]
    db = _install_collection(mw, rows, {10: {"flds": [{"name": "Front"}, {"name": "Back"}]}})

    field_maps = anki.get_note_field_maps(note_ids)

    assert len(field_maps) == len(note_ids)
    assert [len(params) for _sql, params in db.calls] == [500, 500, 201]
    for sql, params in db.calls:
        assert sql.count("?") == len(params)


@pytest.mark.unit
def test_get_note_field_maps_omits_missing_notes(mw, anki):
    _install_collection(
        mw,
        [(7, 10, "present\x1fyes")],
        {10: {"flds": [{"name": "Front"}, {"name": "Back"}]}},
    )

    field_maps = anki.get_note_field_maps([7, 8, 9])

    assert set(field_maps) == {7}


@pytest.mark.unit
def test_get_note_field_maps_handles_multiple_note_types(mw, anki):
    _install_collection(
        mw,
        [(1, 10, "a\x1fb"), (2, 20, "x\x1fy\x1fz")],
        {
            10: {"flds": [{"name": "Front"}, {"name": "Back"}]},
            20: {"flds": [{"name": "Word"}, {"name": "Reading"}, {"name": "Meaning"}]},
        },
    )

    field_maps = anki.get_note_field_maps([1, 2])

    assert field_maps[1] == {"Front": "a", "Back": "b"}
    assert field_maps[2] == {"Word": "x", "Reading": "y", "Meaning": "z"}
    # one model lookup per note type, cached across rows
    assert mw.col.models.get.call_count == 2


@pytest.mark.unit
def test_get_note_field_maps_tolerates_unknown_note_type(mw, anki):
    _install_collection(mw, [(1, 99, "a\x1fb")], {99: None})

    assert anki.get_note_field_maps([1]) == {1: {}}


@pytest.mark.unit
def test_get_note_field_maps_with_no_ids_skips_database(mw, anki):
    db = _install_collection(mw, [], {})

    assert anki.get_note_field_maps([]) == {}
    assert db.calls == []


# --------------------------------------------------------------------------- #
# misc helpers
# --------------------------------------------------------------------------- #


@pytest.mark.unit
def test_restrict_message_length_keeps_short_messages(anki):
    assert anki.restrict_message_length("short") == "short"


@pytest.mark.unit
def test_restrict_message_length_truncates_and_ellipsises(anki):
    message = "x" * (constants.MESSAGE_TEXT_MAX_LENGTH + 50)

    restricted = anki.restrict_message_length(message)

    assert restricted.endswith("...")
    assert restricted.startswith("x" * constants.MESSAGE_TEXT_MAX_LENGTH)
    assert len(restricted) == constants.MESSAGE_TEXT_MAX_LENGTH + 3


@pytest.mark.unit
def test_ensure_anki_collection_open_raises_when_collection_closed(mw, monkeypatch):
    mw.col = None
    monkeypatch.setattr(anki_utils.aqt, "mw", mw)

    with pytest.raises(anki_utils.errors.CollectionNotOpen):
        anki_utils.ensure_anki_collection_open()


@pytest.mark.unit
def test_get_current_time_returns_datetime(anki):
    import datetime

    assert isinstance(anki.get_current_time(), datetime.datetime)


@pytest.mark.unit
def test_get_uuid_is_unique(anki):
    assert anki.get_uuid() != anki.get_uuid()


# --------------------------------------------------------------------------- #
# undo
# --------------------------------------------------------------------------- #


@pytest.mark.unit
@pytest.mark.parametrize(
    ("method_name", "undo_entry"),
    [
        ("undo_start", constants.UNDO_ENTRY_NAME),
        ("undo_tts_tag_start", constants.UNDO_ENTRY_ADD_TTS_TAG),
    ],
)
def test_undo_start_creates_custom_entry(mw, anki, method_name, undo_entry):
    mw.col.add_custom_undo_entry.return_value = 4242

    assert getattr(anki, method_name)() == 4242
    mw.col.add_custom_undo_entry.assert_called_once_with(undo_entry)


@pytest.mark.unit
def test_undo_end_merges_on_main_thread(mw, anki, monkeypatch):
    monkeypatch.setattr(anki_utils.AnkiUtils, "run_on_main", lambda self, fn: fn())

    anki.undo_end(77)

    mw.col.merge_undo_entries.assert_called_once_with(77)
    mw.update_undo_actions.assert_called_once()
    mw.autosave.assert_called_once()


@pytest.mark.unit
def test_undo_end_swallows_errors(mw, anki, monkeypatch):
    monkeypatch.setattr(anki_utils.AnkiUtils, "run_on_main", lambda self, fn: fn())
    mw.col.merge_undo_entries.side_effect = RuntimeError("collection closed")

    anki.undo_end(5)  # must not raise


# --------------------------------------------------------------------------- #
# notes / cards / media
# --------------------------------------------------------------------------- #


@pytest.mark.unit
def test_get_note_by_id(mw, anki):
    mw.col.get_note.return_value = "note"

    assert anki.get_note_by_id(3) == "note"
    mw.col.get_note.assert_called_once_with(3)


@pytest.mark.unit
def test_model_and_deck_helpers(mw, anki):
    mw.col.models.get.return_value = {"name": "Basic"}
    mw.col.decks.get.return_value = {"name": "Default"}
    mw.col.models.id_for_name.return_value = 11
    mw.col.decks.id_for_name.return_value = 22

    assert anki.get_model(10) == {"name": "Basic"}
    assert anki.get_note_type_name(10) == "Basic"
    assert anki.get_deck(20) == {"name": "Default"}
    assert anki.get_deck_name(20) == "Default"
    assert anki.get_model_id("Basic") == 11
    assert anki.get_deck_id("Default") == 22


@pytest.mark.unit
def test_media_add_file_returns_stored_name(mw, anki):
    mw.col.media.add_file.return_value = "stored.mp3"

    assert anki.media_add_file("/tmp/x.mp3") == "stored.mp3"
    mw.col.media.add_file.assert_called_once_with("/tmp/x.mp3")


@pytest.mark.unit
def test_update_note_and_update_notes(mw, anki):
    anki.update_note("n1")
    anki.update_notes(["n1", "n2"])

    mw.col.update_note.assert_called_once_with("n1")
    mw.col.update_notes.assert_called_once_with(["n1", "n2"])


@pytest.mark.unit
def test_save_note_type_update(mw, anki):
    anki.save_note_type_update({"name": "Basic"})

    mw.col.models.update_dict.assert_called_once_with({"name": "Basic"})


@pytest.mark.unit
def test_create_card_from_note_uses_ephemeral_card(anki):
    note = MagicMock()
    note.ephemeral_card.return_value = "card"

    result = anki.create_card_from_note(note, 1, "model", "template")

    assert result == "card"
    note.ephemeral_card.assert_called_once_with(
        1, custom_note_type="model", custom_template="template"
    )


@pytest.mark.unit
def test_get_anki_collection(mw, anki):
    assert anki.get_anki_collection() is mw.col


# --------------------------------------------------------------------------- #
# sound / tts tags
# --------------------------------------------------------------------------- #


@pytest.mark.unit
def test_extract_tts_tags_filters_other_av_tags(monkeypatch):
    class _DummyTTSTag:
        def __init__(self, text):
            self.text = text

    monkeypatch.setattr(anki_utils.anki.sound, "TTSTag", _DummyTTSTag, raising=False)
    tags = [_DummyTTSTag("a"), "not-a-tag", _DummyTTSTag("b")]

    extracted = anki_utils.AnkiUtils().extract_tts_tags(tags)

    assert [tag.text for tag in extracted] == ["a", "b"]


@pytest.mark.unit
def test_play_anki_sound_tag_plays_first_file(mw, anki, monkeypatch):
    class _DummySoundTag:
        def __init__(self, filename):
            self.filename = filename

    av_player = MagicMock()
    monkeypatch.setattr(anki_utils.aqt.sound, "av_player", av_player, raising=False)
    monkeypatch.setattr(anki_utils.anki.sound, "SoundOrVideoTag", _DummySoundTag, raising=False)
    monkeypatch.setattr(
        anki_utils.anki.template,
        "av_tags_to_native",
        lambda av_tags: [_DummySoundTag("one.mp3"), _DummySoundTag("two.mp3")],
        raising=False,
    )
    mw.col.backend.extract_av_tags.return_value = types.SimpleNamespace(av_tags=["raw"])

    anki.play_anki_sound_tag("[sound:one.mp3]")

    av_player.play_file.assert_called_once_with("one.mp3")


@pytest.mark.unit
def test_play_anki_sound_tag_without_sound_tags_does_nothing(mw, anki, monkeypatch):
    av_player = MagicMock()
    monkeypatch.setattr(anki_utils.aqt.sound, "av_player", av_player, raising=False)
    monkeypatch.setattr(anki_utils.anki.template, "av_tags_to_native", lambda av_tags: [], raising=False)
    mw.col.backend.extract_av_tags.return_value = types.SimpleNamespace(av_tags=[])

    anki.play_anki_sound_tag("no sound")

    av_player.play_file.assert_not_called()


# --------------------------------------------------------------------------- #
# background ops / timers
# --------------------------------------------------------------------------- #


@pytest.mark.unit
def test_run_in_background_collection_op_wraps_undo(mw, anki, monkeypatch):
    seen = []
    query_op = MagicMock()
    monkeypatch.setattr(anki_utils.aqt.operations, "QueryOp", query_op, raising=False)

    def update_fn(col):
        seen.append(col)

    anki.run_in_background_collection_op("parent", update_fn, "success")

    kwargs = query_op.call_args.kwargs
    assert kwargs["parent"] == "parent"
    assert kwargs["success"] == "success"
    wrapper = kwargs["op"]
    wrapper("collection")
    assert seen == ["collection"]
    mw.col.add_custom_undo_entry.assert_called_once_with(constants.UNDO_ENTRY_NAME)
    mw.col.merge_undo_entries.assert_called_once()


@pytest.mark.unit
def test_run_in_background_collection_op_swallows_merge_error(mw, anki, monkeypatch):
    query_op = MagicMock()
    monkeypatch.setattr(anki_utils.aqt.operations, "QueryOp", query_op, raising=False)
    mw.col.merge_undo_entries.side_effect = RuntimeError("too many")

    anki.run_in_background_collection_op(None, lambda col: None, None)

    wrapper = query_op.call_args.kwargs["op"]
    assert wrapper("collection") is False


@pytest.mark.unit
def test_run_in_background_and_run_on_main_delegate(mw, anki):
    anki.run_in_background("task", "done")
    mw.taskman.run_in_background.assert_called_once_with("task", "done")

    anki.run_on_main("callback")
    mw.taskman.run_on_main.assert_called_once_with("callback")


@pytest.mark.unit
def test_wire_typing_timer_returns_timer(anki):
    timer = anki.wire_typing_timer(MagicMock(), MagicMock())

    assert isinstance(timer, anki_utils.TextInputTypingTimer)


@pytest.mark.unit
def test_call_on_timer_expire_replaces_and_starts_timer(anki):
    timer = types.SimpleNamespace(timer_obj=MagicMock(), delay_ms=250)

    anki.call_on_timer_expire(timer, "task")

    timer.timer_obj.start.assert_called_once_with(250)


# --------------------------------------------------------------------------- #
# dialogs / messages
# --------------------------------------------------------------------------- #


@pytest.mark.unit
def test_create_copyable_messagebox_truncates_and_keeps_full_text(anki):
    long_message = "y" * (constants.MESSAGE_TEXT_MAX_LENGTH + 10)

    box = anki._create_copyable_messagebox("title", long_message, "icon")

    assert box.setDetailedText.call_args.args[0] == long_message
    assert box.setText.call_args.args[0].endswith("\n...")


@pytest.mark.unit
def test_create_copyable_messagebox_short_message_not_detailed(anki):
    box = anki._create_copyable_messagebox("title", "short", "icon", rich_text=True)

    box.setText.assert_called_once_with("short")
    box.setTextFormat.assert_called_once()


@pytest.mark.unit
@pytest.mark.parametrize("method_name", ["info_message", "critical_message"])
def test_message_helpers_exec(anki, monkeypatch, method_name):
    message_box = MagicMock()
    monkeypatch.setattr(anki_utils.aqt.qt, "QMessageBox", message_box, raising=False)

    getattr(anki, method_name)("hello", None)

    message_box.return_value.exec.assert_called_once()


@pytest.mark.unit
def test_tooltip_message_truncates(anki, monkeypatch):
    captured = {}
    monkeypatch.setattr(anki_utils.aqt.utils, "tooltip", lambda message: captured.setdefault("m", message), raising=False)

    anki.tooltip_message("z" * (constants.MESSAGE_TEXT_MAX_LENGTH + 1))

    assert captured["m"].endswith("...")


@pytest.mark.unit
def test_display_preset_rules_status_uses_tooltip(anki, monkeypatch):
    calls = []
    monkeypatch.setattr(anki_utils.AnkiUtils, "run_on_main", lambda self, fn: fn())
    monkeypatch.setattr(anki_utils.aqt.utils, "closeTooltip", lambda: calls.append("close"), raising=False)
    monkeypatch.setattr(
        anki_utils.aqt.utils,
        "tooltip",
        lambda message, period=None: calls.append(("tooltip", message, period)),
        raising=False,
    )

    anki.display_preset_rules_status("status text")

    assert ("tooltip", "status text", 5000) in calls


@pytest.mark.unit
def test_ask_user_and_get_text(anki, monkeypatch):
    monkeypatch.setattr(anki_utils.aqt.utils, "askUser", lambda message, parent=None, title=None: True, raising=False)
    monkeypatch.setattr(
        anki_utils.aqt.utils,
        "getText",
        lambda message, parent, default=None, title=None: (default, True),
        raising=False,
    )

    assert anki.ask_user("sure?", None) is True
    assert anki.ask_user_get_text("name?", None, "d", "Title") == ("d", True)


@pytest.mark.unit
def test_display_dialog_returns_exec_result(anki):
    dialog = MagicMock()
    dialog.exec.return_value = 1

    assert anki.display_dialog(dialog) == 1


@pytest.mark.unit
def test_wait_for_dialog_input_execs(anki):
    dialog = MagicMock()

    anki.wait_for_dialog_input(dialog, "id")

    dialog.exec.assert_called_once()


@pytest.mark.unit
def test_ask_user_choose_from_list_returns_row(anki, monkeypatch):
    dialog = MagicMock()
    dialog.return_value.exec.return_value = 1
    list_widget = MagicMock()
    list_widget.return_value.currentRow.return_value = 2
    monkeypatch.setattr(anki_utils.aqt.qt, "QDialog", dialog, raising=False)
    monkeypatch.setattr(anki_utils.aqt.qt, "QListWidget", list_widget, raising=False)
    monkeypatch.setattr(anki_utils.aqt.qt, "QVBoxLayout", MagicMock(), raising=False)
    monkeypatch.setattr(anki_utils.aqt.qt, "QDialogButtonBox", MagicMock(), raising=False)

    row, result = anki.ask_user_choose_from_list(None, "pick", ["a", "b", "c"])

    assert (row, result) == (2, 1)
    list_widget.return_value.addItems.assert_called_once_with(["a", "b", "c"])
    list_widget.return_value.setCurrentRow.assert_called_once_with(0)


# --------------------------------------------------------------------------- #
# clipboard / editor / progress / broadcasts
# --------------------------------------------------------------------------- #


@pytest.mark.unit
def test_clipboard_helpers(anki, monkeypatch):
    application = MagicMock()
    application.clipboard.return_value.text.return_value = "copied"
    monkeypatch.setattr(anki_utils.aqt.qt, "QApplication", application, raising=False)

    assert anki.get_clipboard_content() == "copied"
    anki.clear_clipboard_contents()
    application.clipboard.return_value.clear.assert_called_once()


@pytest.mark.unit
def test_play_sound_runs_on_main(anki, monkeypatch):
    av_player = MagicMock()
    monkeypatch.setattr(anki_utils.aqt.sound, "av_player", av_player, raising=False)
    monkeypatch.setattr(anki_utils.AnkiUtils, "run_on_main", lambda self, fn: fn())

    anki.play_sound("a.mp3")

    av_player.insert_file.assert_called_once_with("a.mp3")


@pytest.mark.unit
def test_progress_bar_start_stop(mw, anki):
    anki.show_progress_bar("working")
    anki.stop_progress_bar()

    mw.progress.start.assert_called_once()
    mw.progress.finish.assert_called_once()


@pytest.mark.unit
def test_editor_set_field_value_updates_note_and_webview(anki):
    editor = MagicMock()
    editor.note.fields = ["old"]

    anki.editor_set_field_value(editor, 0, "new")

    assert editor.note.fields == ["new"]
    editor.web.eval.assert_called_once()


@pytest.mark.unit
def test_editor_set_field_value_rejects_bad_index(anki):
    editor = MagicMock()
    editor.note.fields = ["only"]

    with pytest.raises(Exception):
        anki.editor_set_field_value(editor, 3, "new")


@pytest.mark.unit
def test_loading_indicators_noop_without_editor(anki):
    anki.show_loading_indicator(None, 0)
    anki.hide_loading_indicator(None, 0, "original")


@pytest.mark.unit
def test_loading_indicators_eval_js(anki):
    editor = MagicMock()

    anki.show_loading_indicator(editor, 1)
    anki.hide_loading_indicator(editor, 1, "original")

    assert editor.web.eval.call_count == 2


@pytest.mark.unit
def test_broadcasts_do_not_raise(anki, mw):
    anki.broadcast_audio_added()
    anki.broadcast_services_configured()
    anki.send_deck_browser_webview_command("cmd")

    mw.deckBrowser.web.eval.assert_called_once_with("cmd")


@pytest.mark.unit
def test_send_deck_browser_command_skips_missing_browser(anki, mw):
    mw.deckBrowser = None

    anki.send_deck_browser_webview_command("cmd")  # must not raise


# --------------------------------------------------------------------------- #
# error reporting
# --------------------------------------------------------------------------- #


@pytest.mark.unit
def test_report_error_event_sends_stats(anki, monkeypatch):
    events = []
    monkeypatch.setattr(anki_utils.sc_error, "send_event", lambda *args: events.append(args))

    anki.report_error_event("boom")

    assert len(events) == 1
    assert events[0][2]["error_message"] == "boom"


@pytest.mark.unit
def test_report_known_exception_tooltip(anki, monkeypatch):
    messages = []
    monkeypatch.setattr(anki_utils.AnkiUtils, "tooltip_message", lambda self, m: messages.append(m))
    monkeypatch.setattr(anki_utils.AnkiUtils, "report_error_event", lambda self, m: None)

    anki.report_known_exception_interactive_tooltip(RuntimeError("bad"), "saving")

    assert messages == ["Encountered an error while saving: bad"]


@pytest.mark.unit
def test_report_known_exception_dialog(anki, monkeypatch):
    messages = []
    monkeypatch.setattr(anki_utils.AnkiUtils, "critical_message", lambda self, m, p=None: messages.append(m))
    monkeypatch.setattr(anki_utils.AnkiUtils, "report_error_event", lambda self, m: None)

    anki.report_known_exception_interactive_dialog(RuntimeError("bad"), "loading")

    assert messages == ["Encountered an error while loading: bad"]


@pytest.mark.unit
def test_report_unknown_exception_interactive_wraps_string(anki, monkeypatch):
    messages = []
    captured = []
    monkeypatch.setattr(anki_utils.AnkiUtils, "critical_message", lambda self, m, p=None: messages.append(m))
    monkeypatch.setattr(anki_utils.AnkiUtils, "report_error_event", lambda self, m: None)
    monkeypatch.setattr(anki_utils.logger, "critical", lambda *a, **k: captured.append(a))

    anki.report_unknown_exception_interactive("plain string", "syncing")
    anki.report_unknown_exception_background("another string")

    assert len(messages) == 1
    assert "unknown error" in messages[0]
