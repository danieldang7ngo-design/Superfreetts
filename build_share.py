"""
Build a shareable .ankiaddon for Super Free TTS.

What this does:
- Copies the addon source into a clean staging folder.
- Strips local-only stuff (caches, mp3s, dev mirrors, __pycache__, meta.json, etc.).
- Keeps the EdgeTTS worker cap at 3 (default from batch_constants.py).
- Zips staging into SuperFreeTTS.ankiaddon at the workspace root.

Run from the addon root:
    python build_share.py
"""

from __future__ import annotations

import os
import json
import re
import shutil
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DIST = ROOT / "dist"
STAGING = DIST / "staging"
OUTPUT = ROOT / "SuperFreeTTS.ankiaddon"

# Files/dirs to copy from the addon root.
TOP_LEVEL_INCLUDES = [
    "__init__.py",
    "manifest.json",
    "LICENSE",
    "superfreetts_addon",
    "external",
    "graphics",
    "tools",
]

# Anything matching these names anywhere in the tree is dropped.
EXCLUDE_DIR_NAMES = {
    "__pycache__",
    ".git",
    ".github",
    ".pytest_cache",
    ".mypy_cache",
    "cache",          # superfreetts_addon/cache/
    "user_files",     # mp3 cache, batch state, etc.
    "git-objects-tmp",
    "superfreetts-mirror.git",
    "test",           # comtypes/test, gtts/tests — irrelevant at runtime
    "tests",
}

EXCLUDE_FILE_SUFFIXES = (
    ".pyc",
    ".pyo",
    ".ankiaddon",
    ".so",
    ".pyd",
    ".dll",
    ".dylib",
    ".exe",
)
EXCLUDE_FILE_NAMES = {
    "meta.json",                       # Anki regenerates this on install
    "superfreetts-work.index",
    "_local_override.py",
    "build_share.py",
    "set_edge_workers_20.py",
}


def log(msg: str) -> None:
    print(f"[build] {msg}")


def should_skip_dir(path: Path) -> bool:
    return path.name in EXCLUDE_DIR_NAMES


def should_skip_file(path: Path) -> bool:
    if path.name in EXCLUDE_FILE_NAMES:
        return True
    if path.suffix.lower() in EXCLUDE_FILE_SUFFIXES:
        return True
    # Skip test files inside vendored libs (comtypes/test, gtts/tests, *_test.py)
    if path.name.endswith("_test.py") or path.name.startswith("test_"):
        return True
    return False


def copy_tree(src: Path, dst: Path) -> None:
    """Recursive copy that respects EXCLUDE_* rules."""
    if src.is_file():
        if should_skip_file(src):
            return
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        return

    if not src.is_dir():
        return

    if should_skip_dir(src):
        return

    dst.mkdir(parents=True, exist_ok=True)
    for child in src.iterdir():
        if child.is_dir():
            if should_skip_dir(child):
                continue
            copy_tree(child, dst / child.name)
        else:
            if should_skip_file(child):
                continue
            shutil.copy2(child, dst / child.name)


def patch_file(path: Path, replacements: list[tuple[str, str]], *, regex: bool = False) -> None:
    text = path.read_text(encoding="utf-8")
    original = text
    for old, new in replacements:
        if regex:
            new_text, count = re.subn(old, new, text)
            if count == 0:
                raise RuntimeError(f"Patch pattern not found in {path.name}: {old!r}")
            text = new_text
        else:
            if old not in text:
                raise RuntimeError(f"Patch string not found in {path.name}: {old!r}")
            text = text.replace(old, new)
    if text == original:
        return
    path.write_text(text, encoding="utf-8")


# No longer patching code since the source files now use EDGETTS_MAX_WORKERS = 3 by default.
# The user can toggle to 20 locally via set_edge_workers_20.py which is gitignored.


def _read_edge_workers_cap() -> int:
    """Read the committed source cap without importing the add-on package."""
    source = (ROOT / "superfreetts_addon" / "batch_constants.py").read_text(encoding="utf-8")
    match = re.search(r"EDGETTS_MAX_WORKERS\s*:\s*Final\[int\]\s*=\s*(\d+)", source)
    if not match:
        raise RuntimeError("Could not find EDGETTS_MAX_WORKERS in batch_constants.py")
    return int(match.group(1))


def patch_config_json(stage: Path) -> None:
    """Create a clean default config for redistribution.

    Start from the repository's tracked config so defaults do not drift, then
    strip local state and force the EdgeTTS worker count to the source cap.
    """
    target = stage / "config.json"
    try:
        config = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))
    except Exception as exc:
        raise RuntimeError(f"Could not read repository config.json: {exc}") from exc

    configuration = config.setdefault("configuration", {})
    service_config = configuration.setdefault("service_config", {})
    edge_config = service_config.setdefault("EdgeTTS", {})
    edge_config["concurrency_workers"] = _read_edge_workers_cap()

    # Never ship local presets/mapping rules or user-specific batch state.
    config["presets"] = {}
    config["mapping_rules"] = {"rules": []}
    config["batch_config"] = {}
    config["realtime_config"] = {}
    config["default_presets"] = {}
    config.setdefault("preferences", {})
    config["preferences"]["ui_language"] = "en"

    target.write_text(json.dumps(config, indent=4) + "\n", encoding="utf-8")


def stage_sources() -> None:
    if STAGING.exists():
        shutil.rmtree(STAGING)
    STAGING.mkdir(parents=True)

    # Copy whitelisted top-level entries.
    for name in TOP_LEVEL_INCLUDES:
        src = ROOT / name
        if not src.exists():
            log(f"skip missing: {name}")
            continue
        copy_tree(src, STAGING / name)

    # Always ship a clean config.json (overwrites any copied one).
    patch_config_json(STAGING)


# Staging patching is no longer required because the base code already uses EDGETTS_MAX_WORKERS = 3.


def zip_stage() -> Path:
    if OUTPUT.exists():
        OUTPUT.unlink()
    with zipfile.ZipFile(OUTPUT, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(STAGING.rglob("*")):
            if path.is_dir():
                continue
            arcname = path.relative_to(STAGING).as_posix()
            zf.write(path, arcname)
    return OUTPUT


def main() -> int:
    log("staging sources...")
    stage_sources()

    log(f"zipping -> {OUTPUT.name}")
    out = zip_stage()

    size_mb = out.stat().st_size / (1024 * 1024)
    log(f"done: {out} ({size_mb:.2f} MB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
