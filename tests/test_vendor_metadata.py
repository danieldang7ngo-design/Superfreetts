"""Guard the vendored dependency metadata used by the shipped add-on."""

import importlib
import importlib.metadata
from pathlib import Path

import pytest
from packaging.version import Version

VENDORED = {
    "requests": "requests",
    "certifi": "certifi",
    "idna": "idna",
    "charset-normalizer": "charset_normalizer",
    "urllib3": "urllib3",
}


@pytest.mark.unit
def test_vendored_metadata_matches_module_versions():
    for distribution, module_name in VENDORED.items():
        metadata_version = importlib.metadata.version(distribution)
        module_version = importlib.import_module(module_name).__version__
        assert Version(metadata_version) == Version(module_version), distribution


@pytest.mark.unit
def test_vendor_tree_has_no_compiled_binaries():
    external = Path(__file__).resolve().parent.parent / "external"
    forbidden = {".so", ".pyd", ".dll", ".dylib", ".exe"}
    offenders = [
        str(path.relative_to(external))
        for path in external.rglob("*")
        if path.is_file() and path.suffix.lower() in forbidden
    ]
    assert not offenders, f"compiled vendor binaries: {offenders}"


@pytest.mark.unit
def test_vendor_pins_match_requirements_vendor_file():
    requirements = Path(__file__).resolve().parent.parent / "requirements-vendor.txt"
    text = requirements.read_text(encoding="utf-8")
    pins = {
        line.split("==", 1)[0].lower(): line.split("==", 1)[1]
        for line in text.splitlines()
        if "==" in line and not line.lstrip().startswith("#")
    }
    assert pins["requests"] == "2.32.4"
    assert pins["certifi"] == "2025.7.9"
    assert pins["idna"] == "3.10"
    assert pins["charset-normalizer"] == "3.4.2"
    assert pins["urllib3"] == "2.5.0"
