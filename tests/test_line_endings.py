"""Line-ending convention: add-on sources are CRLF, tests are LF.

The repository's sources are checked out as CRLF (Windows-friendly patches), but
four modules had slipped to LF and one was mixed, which made every diff touch
whole files.  Keep the convention enforced instead of documented.
"""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
ADDON_DIR = REPO_ROOT / "superfreetts_addon"
TESTS_DIR = REPO_ROOT / "tests"


def _counts(path):
    data = path.read_bytes()
    crlf = data.count(b"\r\n")
    lone_lf = data.count(b"\n") - crlf
    return crlf, lone_lf


def test_addon_sources_use_crlf_only():
    offenders = []
    for path in sorted(ADDON_DIR.rglob("*.py")):
        crlf, lone_lf = _counts(path)
        if crlf == 0 or lone_lf:
            offenders.append(f"{path.relative_to(REPO_ROOT)} (crlf={crlf}, lf={lone_lf})")

    assert offenders == []


def test_tests_use_lf_only():
    offenders = []
    for path in sorted(TESTS_DIR.rglob("*.py")):
        crlf, lone_lf = _counts(path)
        if crlf:
            offenders.append(f"{path.relative_to(REPO_ROOT)} (crlf={crlf})")

    assert offenders == []
