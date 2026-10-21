"""Kokoro warmup must not start before the service is actually enabled."""

from unittest.mock import MagicMock

import pytest

from superfreetts_addon.services import service_kokoro


@pytest.mark.unit
def test_warmup_is_not_started_by_constructor(monkeypatch):
    thread_factory = MagicMock()
    monkeypatch.setattr(service_kokoro.threading, "Thread", thread_factory)

    service_kokoro.KokoroTTS()

    thread_factory.assert_not_called()


@pytest.mark.unit
def test_warmup_starts_only_when_enabled(monkeypatch):
    thread_factory = MagicMock()
    monkeypatch.setattr(service_kokoro.threading, "Thread", thread_factory)
    service = service_kokoro.KokoroTTS()

    service.enabled = False
    service.configure({})
    thread_factory.assert_not_called()

    service.enabled = True
    service.configure({})
    thread_factory.assert_called_once()

    # A second configure call must not spawn another warmup thread.
    service.configure({})
    thread_factory.assert_called_once()
