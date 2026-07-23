"""
Unit tests for root cause 2.3 minimal fix: EngineManager.ensure_installed()
and MmsEngineManager.ensure_installed() download a Windows Embeddable
Python distribution and run pip installs through it - this can never work
on macOS/Linux. Previously they'd still attempt the multi-MB download and
only fail later inside a subprocess call. Now they fail fast with a clear
message on non-Windows platforms.

See superfreetts_macos_crash_fix_plan.md, section 2.3 / Phase 6.

Note on scope (documented so this isn't mistaken for a bigger claim later):
this does NOT add real macOS/Linux support for these engines - it only
makes the existing "can't work on this platform" outcome fail fast and
clearly instead of after a wasted download attempt. The runtime TTS
generation paths (service_kokoro.py / service_mms.py get_tts_audio) were
found to already fail safely via `errors.RequestError` when the platform-
specific python executable doesn't exist, so no change was needed there -
see the fix plan for the verification that led to this narrower scope.
"""

import sys
import os
from unittest.mock import patch, MagicMock

import pytest

addon_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, addon_dir)
sys.path.insert(0, os.path.join(addon_dir, 'external'))

from tests import mock_anki
mock_anki.mock_all()

from superfreetts_addon import engine_manager  # noqa: E402
from superfreetts_addon import mms_engine_manager  # noqa: E402


@pytest.mark.unit
class TestEngineManagerPlatformGuard:

    def test_ensure_installed_fails_fast_on_non_windows_without_downloading(self):
        with patch.object(engine_manager.platform, 'system', return_value='Darwin'), \
             patch.object(engine_manager, 'TurboDownloader') as mock_downloader, \
             patch.object(engine_manager.EngineManager, 'is_installed', return_value=False):
            result = engine_manager.EngineManager.ensure_installed()

        assert result is False
        mock_downloader.assert_not_called()

    def test_ensure_installed_proceeds_normally_on_windows(self):
        """The guard must only affect non-Windows platforms - on Windows,
        behavior must be unchanged (still attempts installation normally,
        i.e. does not short-circuit to False before even trying)."""
        real_exists = os.path.exists

        def _fake_exists(path):
            # Pretend python.exe and pip.exe already exist so the
            # download/extract branches are skipped (not what this test is
            # about) - defer to the real check for everything else (e.g.
            # os.makedirs's own internal parent-directory check), otherwise
            # os.makedirs breaks in a way unrelated to the fix being tested.
            if str(path).endswith('python.exe') or str(path).endswith('pip.exe'):
                return True
            return real_exists(path)

        with patch.object(engine_manager.platform, 'system', return_value='Windows'), \
             patch.object(engine_manager.EngineManager, 'is_installed', return_value=False), \
             patch.object(engine_manager.EngineManager, '_run_command') as mock_run_command, \
             patch.object(engine_manager, 'TurboDownloader') as mock_downloader_cls, \
             patch.object(engine_manager.zipfile, 'ZipFile'), \
             patch.object(engine_manager.os.path, 'exists', side_effect=_fake_exists):
            engine_manager.EngineManager._installing = False
            engine_manager.EngineManager.ensure_installed()

        # On Windows, since python.exe and pip.exe are mocked as "existing",
        # only the core-foundations pip install commands should run - the
        # key assertion is that we did NOT bail out early like the
        # non-Windows case does (_run_command must have been reached).
        assert mock_run_command.called

    def test_is_installed_unaffected_by_platform(self):
        """is_installed() is a pure path-existence check and must not be
        touched by the platform guard (only ensure_installed's *download*
        behavior should change)."""
        with patch.object(engine_manager.os.path, 'exists', return_value=True):
            assert engine_manager.EngineManager.is_installed() is True
        with patch.object(engine_manager.os.path, 'exists', return_value=False):
            assert engine_manager.EngineManager.is_installed() is False


@pytest.mark.unit
class TestMmsEngineManagerPlatformGuard:

    def test_ensure_installed_fails_fast_on_non_windows_without_downloading(self):
        with patch.object(mms_engine_manager.platform, 'system', return_value='Darwin'), \
             patch.object(mms_engine_manager, 'TurboDownloader') as mock_downloader, \
             patch.object(mms_engine_manager.MmsEngineManager, 'is_installed', return_value=False):
            result = mms_engine_manager.MmsEngineManager.ensure_installed()

        assert result is False
        mock_downloader.assert_not_called()
