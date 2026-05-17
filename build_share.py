"""
Build a shareable .ankiaddon for Super Free TTS with EdgeTTS capped at 3 workers.

What this does:
- Copies the addon source into a clean staging folder.
- Strips local-only stuff (caches, mp3s, dev mirrors, __pycache__, meta.json, etc.).
- Patches the EdgeTTS worker cap to 3 (your local copy stays at 20).
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
    "superfreetss_addon",
    "external",
    "graphics",
]

# Anything matching these names anywhere in the tree is dropped.
EXCLUDE_DIR_NAMES = {
    "__pycache__",
    ".git",
    ".github",
    ".pytest_cache",
    ".mypy_cache",
    "cache",          # superfreetss_addon/cache/
    "user_files",     # mp3 cache, batch state, etc.
    "git-objects-tmp",
    "superfreetss-mirror.git",
}

EXCLUDE_FILE_SUFFIXES = (".pyc", ".pyo", ".ankiaddon")
EXCLUDE_FILE_NAMES = {
    "meta.json",                       # Anki regenerates this on install
    "superfreetts-work.index",
    "EDGE_TTS_WORKER_20_REPORT.md",
    "build_share.py",
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


def patch_batch_constants(stage: Path) -> None:
    """Add EDGETTS_MAX_WORKERS = 3 next to MAX_WORKER_THREADS."""
    target = stage / "superfreetss_addon" / "batch_constants.py"
    patch_file(
        target,
        [(
            "MAX_WORKER_THREADS: Final[int] = 20\n",
            "MAX_WORKER_THREADS: Final[int] = 20\n\n"
            "# Per-engine ceiling for EdgeTTS in the public release.\n"
            "# Microsoft Edge TTS rate-limits aggressive concurrency,\n"
            "# so the shared build keeps this conservative.\n"
            "EDGETTS_MAX_WORKERS: Final[int] = 3\n",
        )],
    )


def patch_service_edgetts(stage: Path) -> None:
    target = stage / "superfreetss_addon" / "services" / "service_edgetts.py"
    patch_file(
        target,
        [
            (
                "'concurrency_workers': ('number', 'Concurrency Workers (1-20)', 20, 1, batch_constants.MAX_WORKER_THREADS),",
                "'concurrency_workers': ('number', 'Concurrency Workers (1-3)', 3, 1, batch_constants.EDGETTS_MAX_WORKERS),",
            ),
            (
                "concurrency_workers = min(batch_constants.MAX_WORKER_THREADS, max(1, requested_workers))",
                "concurrency_workers = min(batch_constants.EDGETTS_MAX_WORKERS, max(1, requested_workers))",
            ),
        ],
    )


def patch_superfreetss(stage: Path) -> None:
    target = stage / "superfreetss_addon" / "superfreetss.py"
    # There are two engine_config blocks (init + reconfigure). Both reference
    # MAX_WORKER_THREADS in two ways. We patch all four occurrences.
    patch_file(
        target,
        [
            (
                "'EdgeTTS': batch_constants.MAX_WORKER_THREADS,",
                "'EdgeTTS': batch_constants.EDGETTS_MAX_WORKERS,",
            ),
            (
                "max_workers = batch_constants.MAX_WORKER_THREADS if service_name == 'EdgeTTS' else cpu_utils.CPUInfo.get_max_workers()",
                "max_workers = batch_constants.EDGETTS_MAX_WORKERS if service_name == 'EdgeTTS' else cpu_utils.CPUInfo.get_max_workers()",
            ),
        ],
    )


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


def patch_stage() -> None:
    patch_batch_constants(STAGING)
    patch_service_edgetts(STAGING)
    patch_superfreetss(STAGING)


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

    log("patching EdgeTTS worker cap to 3...")
    patch_stage()

    log(f"zipping -> {OUTPUT.name}")
    out = zip_stage()

    size_mb = out.stat().st_size / (1024 * 1024)
    log(f"done: {out} ({size_mb:.2f} MB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
