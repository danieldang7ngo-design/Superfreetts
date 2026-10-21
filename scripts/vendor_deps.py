#!/usr/bin/env python3
"""Check or refresh the pure-Python packages vendored under ``external/``.

Usage:
    python scripts/vendor_deps.py --check   # no network, verify local metadata
    python scripts/vendor_deps.py --apply   # download, verify, and replace

Only the five packages below are managed here.  EdgeTTS and its asyncio
dependencies are also vendored, but changing them is a separate compatibility
decision and should be covered by the EdgeTTS integration tests.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib
import importlib.metadata
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXTERNAL = ROOT / "external"

# wheel SHA-256, not just a version number: a compromised or replaced package
# on the index cannot silently enter the add-on package.
PACKAGES = {
    "requests": (
        "2.32.4",
        "27babd3cda2a6d50b30443204ee89830707d396671944c998b5975b031ac2b2c",
    ),
    "certifi": (
        "2025.7.9",
        "d842783a14f8fdd646895ac26f719a061408834473cfc10203f6a575beb15d39",
    ),
    "idna": (
        "3.10",
        "946d195a0d259cbba61165e88e65941f16e9b36ea6ddb97f00452bae8b1287d3",
    ),
    "charset-normalizer": (
        "3.4.2",
        "7f56930ab0abd1c45cd15be65cc741c28b1c9a34876ce8c17a2fa107810c0af0",
    ),
    "urllib3": (
        "2.5.0",
        "e6b01673c0fa6a13e374b50871808eb3bf7046c4b125b216f6bf1cc604cff0dc",
    ),
}


def _module_name(distribution: str) -> str:
    return distribution.replace("-", "_")


def _normalized(value: str):
    try:
        from packaging.version import Version

        return Version(value)
    except Exception:
        return value


def check() -> int:
    sys.path.insert(0, str(EXTERNAL))
    failures = []
    for distribution, (version, _digest) in PACKAGES.items():
        module_name = _module_name(distribution)
        try:
            metadata_version = importlib.metadata.version(distribution)
            module = importlib.import_module(module_name)
            module_version = getattr(module, "__version__", "")
        except Exception as exc:
            failures.append(f"{distribution}: {type(exc).__name__}: {exc}")
            continue
        if _normalized(metadata_version) != _normalized(version):
            failures.append(
                f"{distribution}: metadata {metadata_version} != pinned {version}"
            )
        if _normalized(module_version) != _normalized(version):
            failures.append(
                f"{distribution}: module {module_version} != pinned {version}"
            )
        print(f"ok  {distribution}=={metadata_version} (module {module_version})")

    if failures:
        print("\nVendor metadata failures:", file=sys.stderr)
        for failure in failures:
            print(f"  - {failure}", file=sys.stderr)
        return 1
    return 0


def _download_wheel(distribution: str, version: str, destination: Path) -> Path:
    subprocess.run(
        [
            sys.executable,
            "-m",
            "pip",
            "download",
            "--no-deps",
            "--only-binary=:all:",
            "--dest",
            str(destination),
            f"{distribution}=={version}",
        ],
        check=True,
    )
    wheels = list(destination.glob("*.whl"))
    if len(wheels) != 1:
        raise RuntimeError(f"expected one wheel for {distribution}, got {wheels}")
    return wheels[0]


def _extract(wheel: Path, destination: Path) -> Path:
    with zipfile.ZipFile(wheel) as archive:
        archive.extractall(destination)
    return destination


def _copy_tree_with_crlf(source: Path, destination: Path) -> None:
    """Copy pure-Python files while preserving the repository's CRLF style."""
    if destination.exists():
        shutil.rmtree(destination)
    for source_file in source.rglob("*"):
        if not source_file.is_file():
            continue
        relative = source_file.relative_to(source)
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        data = source_file.read_bytes()
        if b"\0" not in data:
            data = data.replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")
        target.write_bytes(data)


def apply() -> int:
    with tempfile.TemporaryDirectory(prefix="superfreetts-vendor-") as temp:
        temp_path = Path(temp)
        for distribution, (version, expected_digest) in PACKAGES.items():
            download_dir = temp_path / distribution
            download_dir.mkdir()
            wheel = _download_wheel(distribution, version, download_dir)
            actual_digest = hashlib.sha256(wheel.read_bytes()).hexdigest()
            if actual_digest != expected_digest:
                raise RuntimeError(
                    f"{wheel.name}: SHA-256 {actual_digest} != {expected_digest}"
                )

            extracted = _extract(wheel, temp_path / wheel.stem)
            module_name = _module_name(distribution)
            package_source = extracted / module_name
            if not package_source.is_dir():
                raise RuntimeError(f"{wheel.name}: missing {module_name}/")
            _copy_tree_with_crlf(package_source, EXTERNAL / module_name)

            dist_info_source = next(extracted.glob("*.dist-info"))
            for old in EXTERNAL.glob(f"{module_name}-*.dist-info"):
                shutil.rmtree(old)
            _copy_tree_with_crlf(dist_info_source, EXTERNAL / dist_info_source.name)
            print(f"updated {distribution}=={version}")

    for cache in EXTERNAL.rglob("__pycache__"):
        shutil.rmtree(cache, ignore_errors=True)
    for bytecode in EXTERNAL.rglob("*.pyc"):
        bytecode.unlink(missing_ok=True)
    return check()


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="verify local metadata")
    mode.add_argument("--apply", action="store_true", help="download and replace")
    args = parser.parse_args()
    if args.apply:
        return apply()
    return check()


if __name__ == "__main__":
    raise SystemExit(main())
