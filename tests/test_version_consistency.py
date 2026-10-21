"""Keep release metadata in sync."""

import json
from pathlib import Path

from superfreetts_addon import release_notes
from superfreetts_addon import version


ROOT = Path(__file__).resolve().parent.parent


def test_release_metadata_versions_match():
    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    manifest_version = manifest["version"]

    assert version.ANKI_SUPER_FREE_TTS_VERSION == manifest_version
    assert release_notes.RELEASE_NOTES[0].version == manifest_version

    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    assert f"## {manifest_version}" in changelog
