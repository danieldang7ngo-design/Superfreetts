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
    # Synthetic fixture: its .py payloads are empty, so source parity (which
    # compares against the working tree) is covered separately below.
    assert no_smoke.verify_archive(_archive(no_smoke, tmp_path), check_source_parity=False) == []


def test_engine_data_directory_is_forbidden(no_smoke, tmp_path):
    archive = _archive(
        no_smoke,
        tmp_path,
        [("superfreetts_addon/data/piper_models/en_US-lessac-medium.onnx", b"model")],
    )

    errors = no_smoke.verify_archive(archive, check_source_parity=False)

    assert any("forbidden path in package" in error for error in errors)


def test_extensionless_binary_is_rejected(no_smoke, tmp_path):
    archive = _archive(
        no_smoke,
        tmp_path,
        [("superfreetts_addon/piper", b"\x7fELF\x02\x01\x01" + b"\x00" * 32)],
    )

    errors = no_smoke.verify_archive(archive, check_source_parity=False)

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

    errors = no_smoke.verify_archive(archive, check_source_parity=False)

    assert any("versioned shared library" in error for error in errors)


def test_oversized_archive_is_rejected(no_smoke, tmp_path, monkeypatch):
    monkeypatch.setattr(no_smoke, "MAX_ARCHIVE_BYTES", 10)

    errors = no_smoke.verify_archive(_archive(no_smoke, tmp_path), check_source_parity=False)

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


def _parity_tree(tmp_path, files):
    root = tmp_path / "tree"
    for relative, payload in files.items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(payload)
    return root


def test_source_parity_rejects_stale_python_payload(verifier, tmp_path, monkeypatch):
    root = _parity_tree(
        tmp_path,
        {"superfreetts_addon/module.py": b"NEW = 1\r\n"},
    )
    monkeypatch.setattr(verifier, "ROOT", root)
    archive = tmp_path / "pkg.ankiaddon"
    with zipfile.ZipFile(archive, "w") as zf:
        zf.writestr("superfreetts_addon/module.py", b"OLD = 0\r\n")

    errors = verifier.verify_source_parity(zipfile.ZipFile(archive), {"superfreetts_addon/module.py"})

    assert any(
        "packaged file differs from source: superfreetts_addon/module.py" in error
        for error in errors
    )


def test_source_parity_rejects_python_without_source(verifier, tmp_path, monkeypatch):
    root = _parity_tree(tmp_path, {"superfreetts_addon/kept.py": b"X = 1\n"})
    monkeypatch.setattr(verifier, "ROOT", root)
    archive = tmp_path / "pkg.ankiaddon"
    with zipfile.ZipFile(archive, "w") as zf:
        zf.writestr("superfreetts_addon/kept.py", b"X = 1\n")
        zf.writestr("superfreetts_addon/deleted.py", b"X = 1\n")

    names = {"superfreetts_addon/kept.py", "superfreetts_addon/deleted.py"}
    errors = verifier.verify_source_parity(zipfile.ZipFile(archive), names)

    assert any("no source counterpart: superfreetts_addon/deleted.py" in error for error in errors)


def test_source_parity_reports_module_missing_from_archive(verifier, tmp_path, monkeypatch):
    root = _parity_tree(
        tmp_path,
        {
            "superfreetts_addon/present.py": b"X = 1\n",
            "superfreetts_addon/forgotten.py": b"Y = 2\n",
            "superfreetts_addon/services/test_helper.py": b"Z = 3\n",
        },
    )
    monkeypatch.setattr(verifier, "ROOT", root)
    archive = tmp_path / "pkg.ankiaddon"
    with zipfile.ZipFile(archive, "w") as zf:
        zf.writestr("superfreetts_addon/present.py", b"X = 1\n")

    errors = verifier.verify_source_parity(
        zipfile.ZipFile(archive), {"superfreetts_addon/present.py"}
    )

    assert any(
        "source python file missing from package: superfreetts_addon/forgotten.py" in error
        for error in errors
    )
    # build_share deliberately drops test helpers; parity must not flag them.
    assert not any("test_helper.py" in error for error in errors)


def test_source_parity_rejects_stale_locale_payload(verifier, tmp_path, monkeypatch):
    root = _parity_tree(
        tmp_path,
        {
            "superfreetts_addon/locales/en.json": b'{"voice_button_play": "Play"}\n',
            "manifest.json": b'{"version": "26.10.3"}\n',
        },
    )
    monkeypatch.setattr(verifier, "ROOT", root)
    archive = tmp_path / "pkg.ankiaddon"
    with zipfile.ZipFile(archive, "w") as zf:
        zf.writestr("superfreetts_addon/locales/en.json", b'{"voice_button_play": "Old"}\n')
        zf.writestr("manifest.json", b'{"version": "26.10.3"}\n')

    names = {"superfreetts_addon/locales/en.json", "manifest.json"}
    with zipfile.ZipFile(archive) as zf:
        errors = verifier.verify_source_parity(zf, names)

    assert any(
        "packaged file differs from source: superfreetts_addon/locales/en.json" in error
        for error in errors
    )


def test_source_parity_reports_locale_missing_from_archive(verifier, tmp_path, monkeypatch):
    root = _parity_tree(
        tmp_path,
        {
            "superfreetts_addon/locales/en.json": b"{}\n",
            "superfreetts_addon/locales/vi.json": b"{}\n",
            "manifest.json": b"{}\n",
        },
    )
    monkeypatch.setattr(verifier, "ROOT", root)
    archive = tmp_path / "pkg.ankiaddon"
    with zipfile.ZipFile(archive, "w") as zf:
        zf.writestr("superfreetts_addon/locales/en.json", b"{}\n")
        zf.writestr("manifest.json", b"{}\n")

    names = {"superfreetts_addon/locales/en.json", "manifest.json"}
    with zipfile.ZipFile(archive) as zf:
        errors = verifier.verify_source_parity(zf, names)

    assert any(
        "source locale file missing from package: superfreetts_addon/locales/vi.json"
        in error
        for error in errors
    )


def test_source_parity_reports_manifest_missing_from_archive(verifier, tmp_path, monkeypatch):
    root = _parity_tree(tmp_path, {"manifest.json": b'{"version": "26.10.3"}\n'})
    monkeypatch.setattr(verifier, "ROOT", root)
    archive = tmp_path / "pkg.ankiaddon"
    with zipfile.ZipFile(archive, "w") as zf:
        zf.writestr("superfreetts_addon/version.py", b"")

    with zipfile.ZipFile(archive) as zf:
        errors = verifier.verify_source_parity(zf, {"superfreetts_addon/version.py"})

    assert "source file missing from package: manifest.json" in errors


def test_archive_gate_fails_on_stale_python(no_smoke, tmp_path, monkeypatch):
    archive = _archive(no_smoke, tmp_path)
    root = _parity_tree(
        tmp_path,
        {
            # _archive() writes empty .py payloads; mirror them on disk so the
            # only parity failure is the module this test is about.
            "superfreetts_addon/version.py": b"",
            "superfreetts_addon/batch_constants.py": b"",
        },
    )
    monkeypatch.setattr(no_smoke, "ROOT", root)
    monkeypatch.setattr(no_smoke, "_read_source_worker_cap", lambda: 3)
    with zipfile.ZipFile(archive, "a") as zf:
        zf.writestr("superfreetts_addon/extra.py", b"STALE = 1\r\n")

    errors = no_smoke.verify_archive(archive)

    assert any("no source counterpart: superfreetts_addon/extra.py" in error for error in errors)
