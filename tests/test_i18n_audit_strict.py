"""The i18n audit can gate more than English.

``--strict-locales`` exists because English being complete does not mean the
shipped UI is: a key added without a Vietnamese translation silently falls back
to English, and that is the regression this gate is meant to catch.
"""

import importlib.util
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
AUDIT_PATH = REPO_ROOT / "scripts" / "i18n_audit.py"


@pytest.fixture(scope="module")
def audit():
    spec = importlib.util.spec_from_file_location("sftts_i18n_audit_strict", AUDIT_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.unit
def test_parse_locale_list_trims_and_dedupes(audit):
    assert audit.parse_locale_list(" en , vi ,en,") == ["en", "vi"]


@pytest.mark.unit
def test_default_strict_locales_are_english_and_vietnamese(audit):
    assert audit.parse_locale_list(audit.DEFAULT_STRICT_LOCALES) == ["en", "vi"]


@pytest.mark.unit
def test_check_passes_for_shipped_locales(audit, capsys):
    assert audit.main(["--check"]) == 0

    output = capsys.readouterr().out
    assert "strict locales (en, vi):" in output
    assert "OK" in output


@pytest.mark.unit
def test_check_fails_when_a_strict_locale_is_incomplete(audit, capsys):
    # Japanese is only partially translated; gating it must fail the build.
    assert audit.main(["--check", "--strict-locales", "en,ja"]) == 1

    assert "ja.json is missing" in capsys.readouterr().err


@pytest.mark.unit
def test_unknown_strict_locale_is_rejected(audit):
    with pytest.raises(SystemExit) as excinfo:
        audit.main(["--strict-locales", "en,klingon"])

    assert excinfo.value.code == 2


@pytest.mark.unit
def test_report_without_check_never_fails(audit, capsys):
    assert audit.main(["--strict-locales", "en,ja"]) == 0
    assert "keys used in code" in capsys.readouterr().out

@pytest.mark.unit
def test_min_coverage_defaults_to_disabled(audit, capsys):
    assert audit.main(["--check"]) == 0

    output = capsys.readouterr().out
    assert "used-key coverage" not in output


@pytest.mark.unit
def test_min_coverage_reports_every_locale(audit, capsys):
    assert audit.main(["--check", "--min-coverage", "10"]) == 0

    output = capsys.readouterr().out
    assert "used-key coverage (minimum 10.0%):" in output
    assert "en" in output
    assert "ja" in output


@pytest.mark.unit
def test_min_coverage_fails_a_locale_below_the_floor(audit, capsys):
    # ja/zh only carry a small subset of the used keys; a 40% floor must fail
    # even though en and vi are complete.
    assert audit.main(["--check", "--min-coverage", "40", "--strict-locales", "en,vi"]) == 1

    captured = capsys.readouterr()
    assert "ja.json covers" in captured.err
    assert "minimum 40.0%" in captured.err
    assert "LOW" in captured.out


@pytest.mark.unit
def test_min_coverage_passes_when_every_locale_clears_the_floor(audit):
    assert audit.main(["--check", "--min-coverage", "15"]) == 0


@pytest.mark.unit
def test_min_coverage_without_check_only_reports(audit, capsys):
    assert audit.main(["--min-coverage", "99.5"]) == 0

    output = capsys.readouterr().out
    assert "LOW" in output
