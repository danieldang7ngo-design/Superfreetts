"""Regression test for the Kokoro uninstall error handler."""

from unittest.mock import MagicMock

import pytest

from superfreetts_addon import component_kokoro_manager as kokoro
from superfreetts_addon.services import service_mms


@pytest.mark.unit
def test_uninstall_failure_reports_original_error(monkeypatch, tmp_path):
    manager = object.__new__(kokoro.KokoroInstallManager)
    manager.log = MagicMock()
    manager._on_worker_finished = MagicMock()

    monkeypatch.setattr(kokoro.constants, "KOKORO_ENGINE_DIR", str(tmp_path))
    monkeypatch.setattr(kokoro.shutil, "rmtree", MagicMock(side_effect=OSError("file in use")))
    monkeypatch.setattr(kokoro.subprocess, "run", MagicMock(return_value=MagicMock()))
    monkeypatch.setattr(kokoro.time, "sleep", lambda *_: None)
    monkeypatch.setattr(service_mms._sherpa_pool, "stop_all", MagicMock())
    show_warning = MagicMock()
    monkeypatch.setattr(kokoro, "showWarning", show_warning)
    monkeypatch.setattr(kokoro, "showInfo", MagicMock())
    monkeypatch.setattr(kokoro.mw.taskman, "run_on_main", lambda callback: callback())

    manager._uninstall_worker()

    show_warning.assert_called_once()
    assert "file in use" in show_warning.call_args[0][0]
    manager._on_worker_finished.assert_called_once()
