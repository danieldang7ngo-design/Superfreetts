"""Profile-close cleanup should release executors and local-engine pools."""

from unittest.mock import MagicMock

import pytest

from superfreetts_addon import superfreetts
from superfreetts_addon.services import (
    service_kokoro,
    service_mms,
    service_piper,
    service_supertonic,
)


@pytest.mark.unit
def test_shutdown_stops_executor_and_all_local_pools(monkeypatch):
    stts = object.__new__(superfreetts.SuperFreeTTS)
    stts.executor = MagicMock()
    stts.usage_tracker = MagicMock()

    pools = [
        service_piper._piper_pool,
        service_kokoro._kokoro_pool,
        service_mms._sherpa_pool,
        service_supertonic._supertonic_pool,
    ]
    for pool in pools:
        monkeypatch.setattr(pool, "stop_all", MagicMock())

    stts.shutdown()

    stts.executor.shutdown.assert_called_once_with(wait=False)
    stts.usage_tracker.flush.assert_called_once()
    for pool in pools:
        pool.stop_all.assert_called_once()


@pytest.mark.unit
def test_profile_reopen_recreates_executors_after_shutdown():
    stts = object.__new__(superfreetts.SuperFreeTTS)
    stts._shutdown = True
    stts.reconfigure_service_manager = MagicMock()

    stts.on_profile_reopened()

    stts.reconfigure_service_manager.assert_called_once_with()
    assert stts._shutdown is False


@pytest.mark.unit
def test_profile_reopen_is_noop_on_initial_open():
    stts = object.__new__(superfreetts.SuperFreeTTS)
    stts._shutdown = False
    stts.reconfigure_service_manager = MagicMock()

    stts.on_profile_reopened()

    stts.reconfigure_service_manager.assert_not_called()
