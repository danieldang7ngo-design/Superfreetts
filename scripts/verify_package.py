#!/usr/bin/env python3
"""Validate a built SuperFreeTTS .ankiaddon before publishing.

Checks:
  * required files are present and local state is absent
  * every packaged .py matches the source tree byte-for-byte
  * version metadata is internally consistent
  * EdgeTTS cannot exceed the source worker cap
  * no psutil or compiled binaries were bundled
  * the packaged modules import and RAM detection works in a clean interpreter

Usage:
    python scripts/verify_package.py SuperFreeTTS.ankiaddon
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
TARGET_VERSION = "26.10.3"

REQUIRED_FILES = {
    "__init__.py",
    "manifest.json",
    "config.json",
    "superfreetts_addon/version.py",
    "superfreetts_addon/system_utils.py",
    "superfreetts_addon/batch_constants.py",
    "superfreetts_addon/services/service_edgetts.py",
    "superfreetts_addon/services/service_mms.py",
    "superfreetts_addon/services/service_kokoro.py",
    "superfreetts_addon/services/service_supertonic.py",
    "superfreetts_addon/archive_utils.py",
    "superfreetts_addon/locales/en.json",
    "superfreetts_addon/locales/vi.json",
    "superfreetts_addon/locales/ko.json",
    "superfreetts_addon/locales/ja.json",
    "superfreetts_addon/locales/zh-CN.json",
    "superfreetts_addon/locales/zh-TW.json",
    "superfreetts_addon/locales/sv.json",
}

FORBIDDEN_DIR_PREFIXES = (
    "external/psutil/",
    "external/psutil-",
    "user_files/",
    "superfreetts_addon/cache/",
    "superfreetts_addon/data/",   # engines/models are downloaded at runtime
)

FORBIDDEN_FILE_NAMES = {
    "meta.json",
    "notes.db",
    "_local_override.py",
    ".coverage",
    "service_onnx_general.py",
}

FORBIDDEN_SUFFIXES = (
    ".so",
    ".pyd",
    ".dll",
    ".dylib",
    ".exe",
    ".pyc",
    ".pyo",
    ".onnx",
    ".ort",
)

BINARY_MAGICS = (
    b"\x7fELF",
    b"MZ",
    b"\xca\xfe\xba\xbe",
    b"\xce\xfa\xed\xfe",
    b"\xcf\xfa\xed\xfe",
    b"\xfe\xed\xfa\xce",
    b"\xfe\xed\xfa\xcf",
)

# A source-only add-on is a few MB.  Anything larger means runtime engine or
# model data leaked into the archive (117 MB once shipped this way).
MAX_ARCHIVE_BYTES = 25 * 1024 * 1024

# Payloads that must be byte-identical to the working tree.  A stale
# SuperFreeTTS.ankiaddon is how a fixed source (the EdgeTTS
# api.msedgeservices.com endpoint, for instance) once shipped as the old code:
# the archive was zipped earlier and nothing compared it against the sources.
# Translation files and the manifest drift just as silently, so they are
# compared too instead of only checking that they exist.
SOURCE_PARITY_TREES = ("superfreetts_addon", "external")
SOURCE_PARITY_EXTRA_FILES = ("manifest.json",)
SOURCE_PARITY_EXTRA_GLOBS = ("superfreetts_addon/locales/*.json",)

# Mirrors build_share.py's exclusions: it never packages test helpers,
# _local_override.py, or anything under a test/tests/__pycache__ directory.
SOURCE_PARITY_SKIPPED_NAMES = {"_local_override.py"}
SOURCE_PARITY_SKIPPED_PREFIXES = ("test_",)
SOURCE_PARITY_SKIPPED_SUFFIXES = ("_test.py",)


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _is_parity_payload(name: str) -> bool:
    """True for packaged files that must match the source tree byte-for-byte."""
    if name.endswith(".py") and name.split("/", 1)[0] in SOURCE_PARITY_TREES:
        return True
    if name in SOURCE_PARITY_EXTRA_FILES:
        return True
    return any(Path(name).match(pattern) for pattern in SOURCE_PARITY_EXTRA_GLOBS)


def _collect_source_files() -> dict[str, Path]:
    """Every source file that has to appear in the package, by archive path."""
    files: dict[str, Path] = {}
    for tree in SOURCE_PARITY_TREES:
        base = ROOT / tree
        if not base.is_dir():
            continue
        for path in base.rglob("*.py"):
            if "__pycache__" in path.parts:
                continue
            files[path.relative_to(ROOT).as_posix()] = path
    for pattern in SOURCE_PARITY_EXTRA_GLOBS:
        for path in sorted(ROOT.glob(pattern)):
            if path.is_file():
                files[path.relative_to(ROOT).as_posix()] = path
    for name in SOURCE_PARITY_EXTRA_FILES:
        path = ROOT / name
        if path.is_file():
            files[name] = path
    return files


def _should_package_source(relative_path: str) -> bool:
    name = Path(relative_path).name
    if name in SOURCE_PARITY_SKIPPED_NAMES:
        return False
    if name.startswith(SOURCE_PARITY_SKIPPED_PREFIXES):
        return False
    if name.endswith(SOURCE_PARITY_SKIPPED_SUFFIXES):
        return False
    parts = Path(relative_path).parts[:-1]
    if any(part in {"__pycache__", "test", "tests"} for part in parts):
        return False
    return True


def verify_source_parity(zf: zipfile.ZipFile, names: set[str]) -> list[str]:
    """Compare every packaged .py against the file on disk, byte-for-byte.

    Two failure modes are reported:

    * a packaged payload whose bytes differ from the source (stale archive), or
      that has no source file at all (deleted module still shipped);
    * a source file under ``superfreetts_addon/`` -- ``.py``, a locale, or
      ``manifest.json`` -- that is missing from the package (build filtered it
      after the fix landed).

    Translations are compared as strictly as code: a locale that exists but is
    older than ``superfreetts_addon/locales/*.json`` ships stale strings.
    """
    errors: list[str] = []

    source_files = _collect_source_files()

    packaged = sorted(name for name in names if _is_parity_payload(name))
    packaged_set = set(packaged)

    for name in packaged:
        path = source_files.get(name)
        if path is None:
            errors.append(f"packaged python file has no source counterpart: {name}")
            continue
        try:
            archived_bytes = zf.read(name)
        except Exception as exc:
            errors.append(f"could not read packaged python file {name}: {exc}")
            continue
        try:
            source_bytes = path.read_bytes()
        except OSError as exc:
            errors.append(f"could not read source file {path}: {exc}")
            continue
        if _sha256(archived_bytes) != _sha256(source_bytes):
            errors.append(f"packaged file differs from source: {name}")

    for relative in sorted(source_files):
        if relative == "manifest.json":
            if relative not in packaged_set:
                errors.append(f"source file missing from package: {relative}")
            continue
        if not relative.startswith("superfreetts_addon/"):
            continue
        if relative.endswith(".py"):
            if not _should_package_source(relative):
                continue
            kind = "python file"
        else:
            kind = "locale file"
        if relative not in packaged_set:
            errors.append(f"source {kind} missing from package: {relative}")

    return errors



def _has_binary_magic(archive: zipfile.ZipFile, name: str) -> bool:
    try:
        with archive.open(name) as handle:
            head = handle.read(4)
    except Exception:
        return False
    return any(head.startswith(magic) for magic in BINARY_MAGICS)


def _error(message: str) -> None:
    print(f"[verify] ERROR: {message}", file=sys.stderr)


def _read_source_worker_cap() -> int:
    path = ROOT / "superfreetts_addon" / "batch_constants.py"
    text = path.read_text(encoding="utf-8")
    # Accept both layouts of the cap:
    #   _DEFAULT_EDGETTS_MAX_WORKERS: Final[int] = 3   (immutable literal)
    #   EDGETTS_MAX_WORKERS: Final[int] = 3            (older single-name form)
    #   EDGETTS_MAX_WORKERS: int = ...                 (alias, override friendly)
    match = re.search(
        r"^(?:_DEFAULT_)?EDGETTS_MAX_WORKERS\s*(?::\s*(?:Final\[int\]|int))?\s*=\s*(\d+)",
        text,
        flags=re.MULTILINE,
    )
    if not match:
        raise ValueError(f"EDGETTS_MAX_WORKERS not found in {path}")
    return int(match.group(1))


def verify_archive(archive: Path, check_source_parity: bool = True) -> list[str]:
    errors: list[str] = []
    if not archive.is_file():
        return [f"archive not found: {archive}"]

    size_mb = archive.stat().st_size / 1024 / 1024
    if archive.stat().st_size > MAX_ARCHIVE_BYTES:
        errors.append(
            f"archive is too large ({size_mb:.1f} MB); runtime engine/model data "
            "must not be bundled"
        )

    with zipfile.ZipFile(archive) as zf:
        names = {name.replace("\\", "/") for name in zf.namelist() if not name.endswith("/")}

        if check_source_parity:
            errors.extend(verify_source_parity(zf, names))

        for required in sorted(REQUIRED_FILES):
            if required not in names:
                errors.append(f"missing required file: {required}")

        for name in sorted(names):
            lower = name.lower()
            if any(lower.startswith(prefix) for prefix in FORBIDDEN_DIR_PREFIXES):
                errors.append(f"forbidden path in package: {name}")
            if Path(lower).name in FORBIDDEN_FILE_NAMES:
                errors.append(f"forbidden local-state file: {name}")
            if lower.endswith(FORBIDDEN_SUFFIXES):
                errors.append(f"compiled/binary file in package: {name}")
            if ".so." in lower:
                errors.append(f"versioned shared library in package: {name}")
            if _has_binary_magic(zf, name):
                errors.append(f"compiled/binary file in package: {name}")
            if "/tests/" in lower or lower.startswith("tests/"):
                errors.append(f"test file in package: {name}")

        if "config.json" not in names:
            return errors

        config = json.loads(zf.read("config.json").decode("utf-8"))
        edge = (
            config.get("configuration", {})
            .get("service_config", {})
            .get("EdgeTTS", {})
        )
        workers = edge.get("concurrency_workers")
        if not isinstance(workers, int):
            errors.append(f"EdgeTTS concurrency_workers is not an int: {workers!r}")
        elif workers > _read_source_worker_cap():
            errors.append(
                f"EdgeTTS concurrency_workers={workers} exceeds source cap "
                f"{_read_source_worker_cap()}"
            )

        language = config.get("preferences", {}).get("ui_language")
        if language != "en":
            errors.append(f"published config must default to English, got {language!r}")

        enabled_services = config.get("configuration", {}).get("service_enabled", {})
        for service_name in ("EdgeTTS", "PiperTTS", "KokoroTTS", "MmsTTS", "SupertonicTTS"):
            if service_name not in enabled_services:
                errors.append(f"service_enabled is missing {service_name}")
        supertonic = (
            config.get("configuration", {})
            .get("service_config", {})
            .get("SupertonicTTS", {})
        )
        if supertonic.get("concurrency_workers") != 1:
            errors.append(
                "SupertonicTTS concurrency_workers must be pinned to 1, "
                f"got {supertonic.get('concurrency_workers')!r}"
            )

        if "manifest.json" not in names or "superfreetts_addon/version.py" not in names:
            # Already reported as missing required files; reading them here
            # would crash the gate with a KeyError instead of a clean message.
            return errors

        manifest = json.loads(zf.read("manifest.json").decode("utf-8"))
        manifest_version = manifest.get("version")
        version_text = zf.read("superfreetts_addon/version.py").decode("utf-8")
        version_match = re.search(
            r"ANKI_SUPER_FREE_TTS_VERSION\s*=\s*['\"]([^'\"]+)['\"]",
            version_text,
        )
        if manifest_version != TARGET_VERSION:
            errors.append(
                f"manifest version is {manifest_version!r}, expected {TARGET_VERSION!r}"
            )
        if not version_match:
            errors.append("could not parse version.py")
        elif version_match.group(1) != manifest_version:
            errors.append(
                f"version mismatch: manifest={manifest_version!r} "
                f"version.py={version_match.group(1)!r}"
            )
        elif version_match.group(1) != TARGET_VERSION:
            errors.append(
                f"version.py is {version_match.group(1)!r}, expected {TARGET_VERSION!r}"
            )

    if not errors:
        with tempfile.TemporaryDirectory(prefix="superfreetts-verify-") as tmp:
            with zipfile.ZipFile(archive) as zf:
                zf.extractall(tmp)

            env = dict(os.environ)
            env["PYTHONPATH"] = os.pathsep.join(
                [tmp, os.path.join(tmp, "external"), env.get("PYTHONPATH", "")]
            ).rstrip(os.pathsep)
            smoke = subprocess.run(
                [
                    sys.executable,
                    "-S",  # prove the package does not rely on host site-packages
                    "-c",
                    (
                        "import sys;"
                        "sys._pytest_mode = True;"
                        "import json;"
                        "import requests, charset_normalizer, aiohttp, edge_tts;"
                        "import superfreetts_addon.system_utils as system_utils;"
                        "import superfreetts_addon.servicemanager as servicemanager;"
                        "from superfreetts_addon import batch_constants;"
                        "assert requests.__version__ == '2.32.4';"
                        "assert charset_normalizer.__version__ == '3.4.2';"
                        "assert aiohttp.__version__ == '3.13.3';"
                        "assert edge_tts.__version__ == '7.3.1';"
                        "print(json.dumps({"
                        "'ram_mb': system_utils.get_available_ram_mb(),"
                        "'ram_source': system_utils.get_ram_detection_source(),"
                        "'edge_cap': batch_constants.EDGETTS_MAX_WORKERS,"
                        "'requests': requests.__version__,"
                        "'charset_normalizer': charset_normalizer.__version__,"
                        "'aiohttp': aiohttp.__version__,"
                        "'edge_tts': edge_tts.__version__,"
                        "'servicemanager_loaded': bool(servicemanager.ServiceManager)"
                        "}))"
                    ),
                ],
                cwd=tmp,
                env=env,
                capture_output=True,
                text=True,
                timeout=60,
            )
            if smoke.returncode != 0:
                errors.append(
                    "packaged import/RAM smoke test failed:\n"
                    f"{smoke.stdout}\n{smoke.stderr}"
                )
            else:
                print(f"[verify] smoke: {smoke.stdout.strip()}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "archive",
        nargs="?",
        default=str(ROOT / "SuperFreeTTS.ankiaddon"),
    )
    args = parser.parse_args()

    archive = Path(args.archive)
    errors = verify_archive(archive)
    if errors:
        for error in errors:
            _error(error)
        return 1

    print(f"[verify] OK: {archive} ({archive.stat().st_size / 1024 / 1024:.2f} MB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
