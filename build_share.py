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
}

EXCLUDE_FILE_SUFFIXES = (".pyc", ".pyo", ".ankiaddon")
EXCLUDE_FILE_NAMES = {
    "meta.json",                       # Anki regenerates this on install
    "superfreetts-work.index",
    "EDGE_TTS_WORKER_20_REPORT.md",
    "_local_override.py",
    "build_share.py",
    "set_edge_workers_20.py",
    "set_edge_workers_3.py",
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


def patch_config_json(stage: Path) -> None:
    """Reset config.json to a clean default for redistribution."""
    target = stage / "config.json"
    clean = (
        "{\n"
        "    \"configuration\": {\n"
        "        \"service_enabled\": {\n"
        "            \"EdgeTTS\": true,\n"
        "            \"PiperTTS\": false,\n"
        "            \"KokoroTTS\": false,\n"
        "            \"MmsTTS\": false,\n"
        "            \"GoogleTranslate\": false,\n"
        "            \"NaverTTS\": false,\n"
        "            \"Sapi5TTS\": false,\n"
        "            \"EspeakNgTTS\": false\n"
        "        },\n"
        "        \"service_config\": {\n"
        "            \"EdgeTTS\": {\n"
        "                \"concurrency_workers\": 3\n"
        "            }\n"
        "        },\n"
        "        \"display_introduction_message\": true\n"
        "    },\n"
        "    \"preferences\": {\n"
        "        \"ui_language\": \"vi\",\n"
        "        \"cache_enabled\": true\n"
        "    },\n"
        "    \"presets\": {},\n"
        "    \"mapping_rules\": {\n"
        "        \"rules\": []\n"
        "    },\n"
        "    \"batch_config\": {},\n"
        "    \"realtime_config\": {},\n"
        "    \"default_presets\": {}\n"
        "}\n"
    )
    target.write_text(clean, encoding="utf-8")


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
