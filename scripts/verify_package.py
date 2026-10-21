#!/usr/bin/env python3
"""Validate a built SuperFreeTTS .ankiaddon before publishing.

Checks:
  * required files are present and local state is absent
  * version metadata is internally consistent
  * EdgeTTS cannot exceed the source worker cap
  * no psutil or compiled binaries were bundled
  * the packaged modules import and RAM detection works in a clean interpreter

Usage:
    python scripts/verify_package.py SuperFreeTTS.ankiaddon
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
TARGET_VERSION = "26.10.2"

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
)

FORBIDDEN_FILE_NAMES = {
    "meta.json",
    "notes.db",
    "_local_override.py",
    ".coverage",
    "service_onnx_general.py",
}

FORBIDDEN_SUFFIXES = (".so", ".pyd", ".dll", ".dylib", ".exe", ".pyc", ".pyo")


def _error(message: str) -> None:
    print(f"[verify] ERROR: {message}", file=sys.stderr)


def _read_source_worker_cap() -> int:
    path = ROOT / "superfreetts_addon" / "batch_constants.py"
    text = path.read_text(encoding="utf-8")
    match = re.search(
        r"^EDGETTS_MAX_WORKERS\s*:\s*Final\[int\]\s*=\s*(\d+)",
        text,
        flags=re.MULTILINE,
    )
    if not match:
        raise ValueError(f"EDGETTS_MAX_WORKERS not found in {path}")
    return int(match.group(1))


def verify_archive(archive: Path) -> list[str]:
    errors: list[str] = []
    if not archive.is_file():
        return [f"archive not found: {archive}"]

    with zipfile.ZipFile(archive) as zf:
        names = {name.replace("\\", "/") for name in zf.namelist() if not name.endswith("/")}

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
