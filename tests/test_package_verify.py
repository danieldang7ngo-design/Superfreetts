"""The release gate must reject runtime engine data and compiled binaries.

The 26.10.2 archive shipped 83.92 MB because ``build_share`` filtered files by
suffix only (missing ``libonnxruntime.so.1.14.1``, the extensionless ``piper``
binary and ``*.onnx``), and ``verify_package`` did not look at
``superfreetts_addon/data`` at all.
"""

import importlib.util
import json
import zipfile
from pathlib import Path
from types import SimpleNamespace

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]


def _load(module_name, relative_path):
    spec = importlib.util.spec_from_file_location(module_name, REPO_ROOT / relative_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def verifier():
    return _load("sftts_verify_package", Path("scripts") / "verify_package.py")


@pytest.fixture(scope="module")
def builder():
    return _load("sftts_build_share", Path("build_share.py"))


@pytest.fixture
def no_smoke(monkeypatch, verifier):
    """Skip the clean-interpreter smoke test; it needs a real package."""
    monkeypatch.setattr(
        verifier,
        "subprocess",
        SimpleNamespace(
            run=lambda *args, **kwargs: SimpleNamespace(returncode=0, stdout="{}", stderr="")
        ),
    )
    return verifier


def _minimal_config(verifier):
    return {
        "configuration": {
            "service_enabled": {
                "EdgeTTS": True,
                "PiperTTS": False,
                "KokoroTTS": False,
                "MmsTTS": False,
                "SupertonicTTS": False,
            },
            "service_config": {
                "EdgeTTS": {"concurrency_workers": verifier._read_source_worker_cap()},
                "SupertonicTTS": {"concurrency_workers": 1},
            },
        },
        "preferences": {"ui_language": "en"},
    }


def _archive(verifier, tmp_path, extra=()):
    path = tmp_path / "pkg.ankiaddon"
    with zipfile.ZipFile(path, "w") as archive:
        for name in verifier.REQUIRED_FILES:
            if name == "config.json":
                archive.writestr(name, json.dumps(_minimal_config(verifier)))
            elif name == "manifest.json":
                archive.writestr(name, json.dumps({"version": verifier.TARGET_VERSION}))
            elif name == "superfreetts_addon/version.py":
                archive.writestr(
                    name, f"ANKI_SUPER_FREE_TTS_VERSION='{verifier.TARGET_VERSION}'\n"
                )
            else:
                archive.writestr(name, "")
        for name, payload in extra:
            archive.writestr(name, payload)
    return path


def test_clean_archive_passes(no_smoke, tmp_path):
    assert no_smoke.verify_archive(_archive(no_smoke, tmp_path)) == []


def test_engine_data_directory_is_forbidden(no_smoke, tmp_path):
    archive = _archive(
        no_smoke,
        tmp_path,
        [("superfreetts_addon/data/piper_models/en_US-lessac-medium.onnx", b"model")],
    )

    errors = no_smoke.verify_archive(archive)

    assert any("forbidden path in package" in error for error in errors)


def test_extensionless_binary_is_rejected(no_smoke, tmp_path):
    archive = _archive(
        no_smoke,
        tmp_path,
        [("superfreetts_addon/piper", b"\x7fELF\x02\x01\x01" + b"\x00" * 32)],
    )

    errors = no_smoke.verify_archive(archive)

    assert any(
        "compiled/binary file in package: superfreetts_addon/piper" in error
        for error in errors
    )


def test_versioned_shared_library_is_rejected(no_smoke, tmp_path):
    archive = _archive(
        no_smoke,
        tmp_path,
        [("superfreetts_addon/libonnxruntime.so.1.14.1", b"\x7fELF")],
    )

    errors = no_smoke.verify_archive(archive)

    assert any("versioned shared library" in error for error in errors)


def test_oversized_archive_is_rejected(no_smoke, tmp_path, monkeypatch):
    monkeypatch.setattr(no_smoke, "MAX_ARCHIVE_BYTES", 10)

    errors = no_smoke.verify_archive(_archive(no_smoke, tmp_path))

    assert any("archive is too large" in error for error in errors)


def test_build_share_skips_extensionless_binaries(builder, tmp_path):
    elf = tmp_path / "piper"
    elf.write_bytes(b"\x7fELF\x02\x01\x01")
    source = tmp_path / "module.py"
    source.write_text("print('ok')\n", encoding="utf-8")

    assert builder.looks_like_binary(elf) is True
    assert builder.looks_like_binary(source) is False
    assert builder.should_skip_file(tmp_path / "voice.onnx") is True


def test_build_share_treats_engine_data_as_runtime_only(builder):
    data_dir = builder.ROOT / "superfreetts_addon" / "data" / "piper_models"

    assert builder.is_engine_data(data_dir) is True
    assert builder.is_engine_data(builder.ROOT / "superfreetts_addon") is False
