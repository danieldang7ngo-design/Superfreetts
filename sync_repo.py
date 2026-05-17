"""
Sync the live addon folder into dist/repo/ (a clone of the GitHub remote).

Usage from the addon root:
    python sync_repo.py

Behavior:
- Copies whitelisted top-level entries (code, manifest, LICENSE, default config,
  build script).
- Skips user data: meta.json, user_files/, cache/, __pycache__/, build artifacts.
- Replaces the corresponding code folders in dist/repo/ to mirror the addon.
- Leaves repo-only docs (README, CHANGELOG, etc.) and the .git folder alone.
"""

from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT / "dist" / "repo"

# Files copied as-is (overwrite repo copy if present).
TOP_LEVEL_FILES = [
    "__init__.py",
    "manifest.json",
    "LICENSE",
    "config.json",
    "build_share.py",
    "sync_repo.py",
]

# Whole directories synced. Existing repo dir is removed first so deletes
# in the addon are reflected in the repo.
SYNCED_DIRS = [
    "superfreetss_addon",
    "external",
    "graphics",
]

EXCLUDE_DIR_NAMES = {
    "__pycache__",
    ".git",
    ".github",
    ".pytest_cache",
    ".mypy_cache",
    "cache",
    "user_files",
    "git-objects-tmp",
    "superfreetss-mirror.git",
    "dist",
}

EXCLUDE_FILE_SUFFIXES = (".pyc", ".pyo", ".ankiaddon")
EXCLUDE_FILE_NAMES = {
    "meta.json",
    "superfreetss-work.index",
    "EDGE_TTS_WORKER_20_REPORT.md",
}


def log(msg: str) -> None:
    print(f"[sync] {msg}")


def should_skip_dir(path: Path) -> bool:
    return path.name in EXCLUDE_DIR_NAMES


def should_skip_file(path: Path) -> bool:
    if path.name in EXCLUDE_FILE_NAMES:
        return True
    return path.suffix.lower() in EXCLUDE_FILE_SUFFIXES


def copy_tree(src: Path, dst: Path) -> None:
    if src.is_file():
        if should_skip_file(src):
            return
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        return
    if not src.is_dir() or should_skip_dir(src):
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


def main() -> int:
    if not (REPO / ".git").exists():
        raise SystemExit(f"missing git clone at {REPO}")

    log("syncing top-level files...")
    for name in TOP_LEVEL_FILES:
        src = ROOT / name
        if not src.exists():
            log(f"  skip missing: {name}")
            continue
        shutil.copy2(src, REPO / name)

    log("syncing source directories...")
    for name in SYNCED_DIRS:
        src = ROOT / name
        dst = REPO / name
        if not src.exists():
            log(f"  skip missing: {name}")
            continue
        if dst.exists():
            shutil.rmtree(dst)
        copy_tree(src, dst)
        log(f"  synced {name}")

    log("done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
