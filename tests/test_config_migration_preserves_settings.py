"""Upgrades must never overwrite or delete settings the user chose.

The schema 5 -> 6 migration used to clear presets, mapping rules and realtime
config, and every worker/concurrency value was forced to 1.  An upgrade could
therefore silently destroy a user's setup.  These tests pin the new contract:
migration only creates missing containers, bumps the schema, and leaves every
existing value untouched - and a backup is written before anything changes.
"""

import copy
import json

from . import mock_anki

mock_anki.mock_all()

from superfreetts_addon import config_models, config_store, constants


def _preset(name="Preset One"):
    return {
        "uuid": "preset-uuid",
        "name": name,
        "source": {"mode": "simple", "source_field": "Front"},
        "target": {"target_field": "Back", "remove_sound_tag": True},
        "voice_selection": {
            "voice_selection_mode": "single",
            "voice": {
                "options": {},
                "voice_id": {"service": "EdgeTTS", "voice_key": {"id": "en-US-JennyNeural"}},
            },
        },
        "text_processing": {},
    }


def test_v5_upgrade_keeps_every_user_setting(mock_anki_utils):
    rules = {
        "rules": [
            {
                "preset_id": "preset-uuid",
                "rule_type": "DeckNoteType",
                "model_id": 1234,
                "enabled": True,
                "automatic": True,
                "deck_id": 5678,
                "is_default": False,
            }
        ],
        "use_easy_mode": True,
    }
    realtime = {"front": {"preset": "my-preset"}}
    config = {
        constants.CONFIG_SCHEMA: 5,
        constants.CONFIG_PRESETS: {"preset-uuid": _preset()},
        constants.CONFIG_MAPPING_RULES: copy.deepcopy(rules),
        constants.CONFIG_REALTIME_CONFIG: copy.deepcopy(realtime),
        constants.CONFIG_SERVICE_CONFIG: {
            "EdgeTTS": {"num_threads": 20, "concurrency_workers": 20}
        },
        constants.CONFIG_PREFERENCES: {"piper_workers": 4, "batch_concurrency": 4},
    }

    migrated = config_models.migrate_configuration(mock_anki_utils, config)

    assert migrated[constants.CONFIG_SCHEMA] == constants.CONFIG_SCHEMA_VERSION
    assert list(migrated[constants.CONFIG_PRESETS]) == ["preset-uuid"]
    assert migrated[constants.CONFIG_PRESETS]["preset-uuid"]["name"] == "Preset One"
    assert migrated[constants.CONFIG_MAPPING_RULES] == rules
    assert migrated[constants.CONFIG_REALTIME_CONFIG] == realtime
    assert migrated[constants.CONFIG_SERVICE_CONFIG]["EdgeTTS"] == {
        "num_threads": 20,
        "concurrency_workers": 20,
    }
    assert migrated[constants.CONFIG_PREFERENCES]["piper_workers"] == 4
    assert migrated[constants.CONFIG_PREFERENCES]["batch_concurrency"] == 4

    # Preserved rules must still deserialize, otherwise the mapping-rule UI
    # would crash on the next launch.
    parsed = config_models.deserialize_preset_mapping_rules(
        migrated[constants.CONFIG_MAPPING_RULES]
    )
    assert len(parsed.rules) == 1
    assert parsed.rules[0].preset_id == "preset-uuid"
    assert parsed.use_easy_mode is True


def test_v1_batch_config_is_converted_without_clearing_presets(mock_anki_utils):
    config = {
        constants.CONFIG_SCHEMA: 1,
        constants.CONFIG_PRESETS: {"keep-uuid": _preset("Keep me")},
        constants.CONFIG_BATCH_CONFIG: {
            "Preset One": {
                "source": {"mode": "simple", "source_field": "Front"},
                "target": {"target_field": "Back", "remove_sound_tag": True},
                "voice_selection": {
                    "voice_selection_mode": "single",
                    "voice": {
                        "options": {},
                        "voice": {"service": "EdgeTTS", "voice_key": {"id": "en-US-JennyNeural"}},
                    },
                },
                "text_processing": {},
            }
        },
    }

    migrated = config_models.migrate_configuration(mock_anki_utils, config)

    presets = migrated[constants.CONFIG_PRESETS]
    assert set(presets) == {"keep-uuid", "test-uuid-12345"}
    assert presets["keep-uuid"]["name"] == "Keep me"
    assert presets["test-uuid-12345"]["name"] == "Preset One"


def test_non_int_schema_does_not_crash_and_keeps_settings(mock_anki_utils):
    # A corrupt/hand-edited schema value reached migrate_configuration() and
    # crashed add-on startup (string vs int comparison).
    config = {
        constants.CONFIG_SCHEMA: "5",
        constants.CONFIG_PRESETS: {"preset-uuid": _preset()},
        constants.CONFIG_PREFERENCES: {"batch_concurrency": 4},
    }

    migrated = config_models.migrate_configuration(mock_anki_utils, config)

    assert migrated[constants.CONFIG_SCHEMA] == constants.CONFIG_SCHEMA_VERSION
    assert migrated[constants.CONFIG_PRESETS]["preset-uuid"]["name"] == "Preset One"
    assert migrated[constants.CONFIG_PREFERENCES]["batch_concurrency"] == 4


def test_missing_containers_are_created(mock_anki_utils):
    migrated = config_models.migrate_configuration(
        mock_anki_utils, {constants.CONFIG_SCHEMA: 5}
    )

    assert migrated[constants.CONFIG_PRESETS] == {}
    assert migrated[constants.CONFIG_REALTIME_CONFIG] == {}
    assert migrated[constants.CONFIG_WORKFLOWS] == {}
    assert migrated[constants.CONFIG_PREFERENCES]["cache_enabled"] is True
    assert migrated[constants.CONFIG_SCHEMA] == constants.CONFIG_SCHEMA_VERSION


class _FakeAnkiUtils:
    def __init__(self, config, user_files):
        self._config = config
        self._user_files = str(user_files)

    def get_config(self):
        return self._config

    def write_config(self, config):
        self._config = config

    def get_user_files_dir(self):
        return self._user_files

    def get_uuid(self):
        return "generated-uuid"


def test_backup_is_written_before_migration(tmp_path):
    original = {
        constants.CONFIG_SCHEMA: 5,
        constants.CONFIG_PRESETS: {"preset-uuid": _preset()},
        constants.CONFIG_PREFERENCES: {"batch_concurrency": 6},
        constants.CONFIG_MAPPING_RULES: {"rules": [{"rule_id": "keep-me"}]},
    }
    store = config_store.ConfigStore(
        _FakeAnkiUtils(copy.deepcopy(original), tmp_path), service_manager=None
    )

    store.perform_config_migration()

    backups = sorted(tmp_path.glob("config_backup_schema5_*.json"))
    assert len(backups) == 1
    saved = json.loads(backups[0].read_text(encoding="utf-8"))
    assert saved[constants.CONFIG_SCHEMA] == 5
    assert saved[constants.CONFIG_PRESETS]["preset-uuid"]["name"] == "Preset One"
    assert saved[constants.CONFIG_PREFERENCES]["batch_concurrency"] == 6

    # The live config keeps the same settings, not the migrated defaults.
    assert store.config[constants.CONFIG_PRESETS]["preset-uuid"]["name"] == "Preset One"
    assert store.config[constants.CONFIG_PREFERENCES]["batch_concurrency"] == 6
    assert store.config[constants.CONFIG_SCHEMA] == constants.CONFIG_SCHEMA_VERSION


def test_fresh_install_writes_no_backup(tmp_path):
    store = config_store.ConfigStore(_FakeAnkiUtils({}, tmp_path), service_manager=None)

    store.perform_config_migration()

    assert list(tmp_path.glob("config_backup_*.json")) == []
    assert store.config[constants.CONFIG_SCHEMA] == constants.CONFIG_SCHEMA_VERSION
