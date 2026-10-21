"""Tests for the shared HTTP timeout/error helper."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import requests

from superfreetts_addon import errors
from superfreetts_addon import http_utils


@pytest.mark.unit
def test_get_supplies_default_timeout():
    with patch.object(http_utils.requests, "get") as mocked_get:
        http_utils.get("https://example.invalid/")
    assert mocked_get.call_args.kwargs["timeout"] == http_utils.DEFAULT_TIMEOUT


@pytest.mark.unit
def test_get_keeps_explicit_timeout():
    with patch.object(http_utils.requests, "get") as mocked_get:
        http_utils.get("https://example.invalid/", timeout=7)
    assert mocked_get.call_args.kwargs["timeout"] == 7


@pytest.mark.unit
def test_audio_request_maps_transport_error_to_audio_not_found():
    voice = MagicMock()
    with patch.object(
        http_utils.requests,
        "get",
        side_effect=requests.exceptions.Timeout("slow"),
    ):
        with pytest.raises(errors.AudioNotFoundError):
            http_utils.get_audio(
                "https://example.invalid/audio.mp3",
                "hello",
                voice,
            )


@pytest.mark.unit
def test_services_do_not_call_requests_get_directly():
    """A new direct request call must not bypass the shared timeout helper."""
    offenders = []
    addon_dir = Path(__file__).resolve().parent.parent / "superfreetts_addon"
    for path in addon_dir.rglob("*.py"):
        if path.name == "http_utils.py":
            continue
        text = path.read_text(encoding="utf-8")
        if "requests.get(" in text:
            offenders.append(str(path.relative_to(addon_dir)))
    assert not offenders, f"direct requests.get calls: {offenders}"
