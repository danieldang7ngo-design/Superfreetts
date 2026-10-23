"""Regression tests for MMS engine-path fallback (NameError fix)."""

from unittest.mock import patch

import pytest

from superfreetts_addon.services import service_mms


def _make_service() -> service_mms.MmsTTS:
    with patch.object(service_mms.MmsTTS, "_ensure_python_environment"):
        return service_mms.MmsTTS()


@pytest.mark.unit
def test_mms_constructor_has_no_filesystem_side_effects():
    with patch.object(service_mms.MmsTTS, "_ensure_python_environment") as ensure:
        svc = service_mms.MmsTTS()

    ensure.assert_not_called()
    assert svc._env_checked is False


@pytest.mark.unit
def test_mms_environment_is_checked_once_when_enabled(tmp_path):
    with patch.object(service_mms.MmsTTS, "_ensure_python_environment") as ensure:
        svc = service_mms.MmsTTS()
        svc.configure({"engine_path": str(tmp_path)})
        svc.configure({"engine_path": str(tmp_path)})
        svc._get_python_exe()

    assert ensure.call_count == 1


@pytest.mark.unit
def test_mms_empty_config_uses_engine_manager_fallback():
    svc = _make_service()
    svc.configure({})
    with patch.object(
        service_mms.MmsEngineManager,
        "get_python_exe",
        return_value="/fallback/python3",
    ):
        assert svc._get_python_exe() == "/fallback/python3"


@pytest.mark.unit
def test_mms_configured_directory_finds_python(tmp_path):
    exe = tmp_path / "python3"
    exe.write_text("", encoding="utf-8")
    svc = _make_service()
    svc.configure({"engine_path": str(tmp_path)})
    assert svc._get_python_exe() == str(exe)


@pytest.mark.unit
def test_mms_configured_file_is_returned(tmp_path):
    exe = tmp_path / "custom-python"
    exe.write_text("", encoding="utf-8")
    svc = _make_service()
    svc.configure({"engine_path": str(exe)})
    assert svc._get_python_exe() == str(exe)


@pytest.mark.unit
def test_mms_missing_path_falls_back(tmp_path):
    svc = _make_service()
    svc.configure({"engine_path": str(tmp_path / "does-not-exist")})
    with patch.object(
        service_mms.MmsEngineManager,
        "get_python_exe",
        return_value="/fallback/python3",
    ):
        assert svc._get_python_exe() == "/fallback/python3"
