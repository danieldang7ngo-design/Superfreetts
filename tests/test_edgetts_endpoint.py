"""Issue #5: EdgeTTS synthesis endpoint moved to api.msedgeservices.com.

Microsoft moved synthesis to api.msedgeservices.com (Edge 155+): the same
TRUSTED_CLIENT_TOKEN is passed as ``Ocp-Apim-Subscription-Key`` instead of
``TrustedClientToken``. The voice-list endpoint stays on the old host.

These tests lock that behaviour in:
- WSS_URL targets the new host with the new query param.
- VOICE_LIST still targets the old host.
- parse_rfc2616_date tolerates malformed dates (incl. IndexError).
- A 403 handshake (WSServerHandshakeError, a ClientResponseError subclass)
  retries once only when the Date header proves significant clock skew;
  otherwise it surfaces with its real status and is never masked by
  SkewAdjustmentError.
- Other 4xx (400/404/429) never enter the skew path; 5xx still do.
"""

import sys
import os

addon_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, addon_dir)
sys.path.insert(0, os.path.join(addon_dir, 'external'))

from unittest.mock import MagicMock

import pytest
from multidict import CIMultiDict

import aiohttp
import edge_tts.voices as voices_mod
from edge_tts import Communicate
from edge_tts import constants
from edge_tts import drm as drm_mod
from edge_tts.drm import DRM
from edge_tts.exceptions import SkewAdjustmentError


def _handshake_403():
    return aiohttp.WSServerHandshakeError(
        MagicMock(), (),
        status=403,
        message="Forbidden",
        headers=CIMultiDict({}),
    )


def test_wss_url_uses_new_synthesis_endpoint():
    assert "api.msedgeservices.com" in constants.WSS_URL
    assert constants.WSS_URL.startswith("wss://api.msedgeservices.com/")
    assert "Ocp-Apim-Subscription-Key=" in constants.WSS_URL
    assert constants.TRUSTED_CLIENT_TOKEN in constants.WSS_URL
    assert "TrustedClientToken" not in constants.WSS_URL
    assert "speech.platform.bing.com" not in constants.WSS_URL


def test_voice_list_stays_on_old_host():
    assert "speech.platform.bing.com" in constants.VOICE_LIST
    assert "api.msedgeservices.com" not in constants.VOICE_LIST
    assert constants.TRUSTED_CLIENT_TOKEN in constants.VOICE_LIST


def test_parse_rfc2616_date_valid():
    parsed = DRM.parse_rfc2616_date("Thu, 01 Jan 1970 00:00:00 GMT")
    assert isinstance(parsed, float)
    assert parsed == pytest.approx(0.0)


def test_parse_rfc2616_date_malformed_returns_none():
    for bad in ["", "not a date", "Sun,", "12:00", "Mon, 99 Foo 2020 99:99:99 GMT",
                "x" * 64, "2020-01-01", "Jan 2020"]:
        assert DRM.parse_rfc2616_date(bad) is None


def test_parse_rfc2616_date_index_error_returns_none(monkeypatch):
    # Regression guard for the except-clause: parsedate_to_datetime rarely
    # raises IndexError on real input, so the branch is forced directly.
    def _boom(date):
        raise IndexError("malformed date internals")

    monkeypatch.setattr(drm_mod, "parsedate_to_datetime", _boom)
    assert DRM.parse_rfc2616_date("anything") is None


def test_synthesis_403_not_wrapped_in_skew_error(monkeypatch):
    err = _handshake_403()
    assert isinstance(err, aiohttp.ClientResponseError)

    async def _boom():
        raise err
        yield  # pragma: no cover - makes this an async generator

    comm = Communicate("Hello world probe", "en-US-AriaNeural")
    monkeypatch.setattr(comm, "_Communicate__stream", _boom)

    async def _collect():
        async for _ in comm.stream():
            pass

    with pytest.raises(aiohttp.WSServerHandshakeError) as exc_info:
        import asyncio
        asyncio.run(_collect())
    assert exc_info.value.status == 403
    assert not isinstance(exc_info.value, SkewAdjustmentError)


def test_voice_list_403_not_wrapped_in_skew_error(monkeypatch):
    err = _handshake_403()

    async def _fake_list_voices(session, ssl_ctx, proxy):
        raise err

    monkeypatch.setattr(voices_mod, "__list_voices", _fake_list_voices)

    def _must_not_run(e):
        raise AssertionError("skew-adjustment must not run for HTTP 4xx")

    monkeypatch.setattr(DRM, "handle_client_response_error", staticmethod(_must_not_run))

    import asyncio
    with pytest.raises(aiohttp.ClientResponseError) as exc_info:
        asyncio.run(voices_mod.list_voices())
    assert exc_info.value.status == 403
    assert not isinstance(exc_info.value, SkewAdjustmentError)


import time
from email.utils import formatdate


def _client_error(status, date=None):
    headers = CIMultiDict({"Date": date} if date else {})
    return aiohttp.ClientResponseError(
        MagicMock(), (),
        status=status,
        message="Forbidden" if status == 403 else "error",
        headers=headers,
    )


def _skewed_date(offset_seconds):
    return formatdate(time.time() + offset_seconds, usegmt=True)


def _drain(comm):
    import asyncio
    out = []

    async def _collect():
        async for msg in comm.stream():
            out.append(msg)

    asyncio.run(_collect())
    return out


def _must_not_run_skew(e):
    raise AssertionError("skew-adjustment must not run on this path")


@pytest.mark.parametrize("status", [400, 404, 429])
def test_synthesis_other_4xx_raise_without_skew(monkeypatch, status):
    err = _client_error(status)

    async def _boom():
        raise err
        yield  # pragma: no cover - makes this an async generator

    comm = Communicate("Hello world probe", "en-US-AriaNeural")
    monkeypatch.setattr(comm, "_Communicate__stream", _boom)
    monkeypatch.setattr(DRM, "adjust_skew_if_significant",
                        staticmethod(_must_not_run_skew))
    monkeypatch.setattr(DRM, "handle_client_response_error",
                        staticmethod(_must_not_run_skew))
    with pytest.raises(aiohttp.ClientResponseError) as exc_info:
        _drain(comm)
    assert exc_info.value.status == status
    assert not isinstance(exc_info.value, SkewAdjustmentError)


def test_synthesis_403_with_significant_skew_retries_once(monkeypatch):
    monkeypatch.setattr(DRM, "clock_skew_seconds", 0.0)
    err = _client_error(403, date=_skewed_date(3600.0))
    calls = {"n": 0}

    async def _flaky():
        calls["n"] += 1
        if calls["n"] == 1:
            raise err
        yield {"type": "audio", "data": b"fake-audio"}

    comm = Communicate("Hello world probe", "en-US-AriaNeural")
    monkeypatch.setattr(comm, "_Communicate__stream", _flaky)
    out = _drain(comm)
    assert calls["n"] == 2
    assert out == [{"type": "audio", "data": b"fake-audio"}]
    assert DRM.clock_skew_seconds == pytest.approx(3600.0, abs=120.0)


def test_synthesis_403_with_insignificant_skew_reraises_original(monkeypatch):
    monkeypatch.setattr(DRM, "clock_skew_seconds", 0.0)
    err = _client_error(403, date=_skewed_date(5.0))

    async def _boom():
        raise err
        yield  # pragma: no cover - makes this an async generator

    comm = Communicate("Hello world probe", "en-US-AriaNeural")
    monkeypatch.setattr(comm, "_Communicate__stream", _boom)
    monkeypatch.setattr(DRM, "handle_client_response_error",
                        staticmethod(_must_not_run_skew))
    import asyncio
    with pytest.raises(aiohttp.ClientResponseError) as exc_info:
        asyncio.run(_drain_async_helper(comm))
    assert exc_info.value is err
    assert not isinstance(exc_info.value, SkewAdjustmentError)
    assert DRM.clock_skew_seconds == 0.0


async def _drain_async_helper(comm):
    async for _ in comm.stream():
        pass


def test_synthesis_403_retry_still_403_reraises_retry_error(monkeypatch):
    monkeypatch.setattr(DRM, "clock_skew_seconds", 0.0)
    first = _client_error(403, date=_skewed_date(3600.0))
    second = _client_error(403)
    calls = {"n": 0}

    async def _always_403():
        calls["n"] += 1
        raise first if calls["n"] == 1 else second
        yield  # pragma: no cover - makes this an async generator

    comm = Communicate("Hello world probe", "en-US-AriaNeural")
    monkeypatch.setattr(comm, "_Communicate__stream", _always_403)
    import asyncio
    with pytest.raises(aiohttp.ClientResponseError) as exc_info:
        asyncio.run(_drain_async_helper(comm))
    assert calls["n"] == 2
    assert exc_info.value is second
    assert exc_info.value.status == 403
    assert not isinstance(exc_info.value, SkewAdjustmentError)


def test_synthesis_5xx_uses_skew_path_and_retries(monkeypatch):
    monkeypatch.setattr(DRM, "clock_skew_seconds", 0.0)
    err = _client_error(500, date=_skewed_date(-7200.0))
    calls = {"n": 0}

    async def _flaky():
        calls["n"] += 1
        if calls["n"] == 1:
            raise err
        yield {"type": "audio", "data": b"fake-audio"}

    comm = Communicate("Hello world probe", "en-US-AriaNeural")
    monkeypatch.setattr(comm, "_Communicate__stream", _flaky)
    out = _drain(comm)
    assert calls["n"] == 2
    assert out == [{"type": "audio", "data": b"fake-audio"}]
    assert DRM.clock_skew_seconds == pytest.approx(-7200.0, abs=120.0)


@pytest.mark.parametrize("status", [400, 404, 429])
def test_voice_list_other_4xx_raise_without_skew(monkeypatch, status):
    err = _client_error(status)

    async def _fake_list_voices(session, ssl_ctx, proxy):
        raise err

    monkeypatch.setattr(voices_mod, "__list_voices", _fake_list_voices)
    monkeypatch.setattr(DRM, "adjust_skew_if_significant",
                        staticmethod(_must_not_run_skew))
    monkeypatch.setattr(DRM, "handle_client_response_error",
                        staticmethod(_must_not_run_skew))
    import asyncio
    with pytest.raises(aiohttp.ClientResponseError) as exc_info:
        asyncio.run(voices_mod.list_voices())
    assert exc_info.value.status == status
    assert not isinstance(exc_info.value, SkewAdjustmentError)


def test_voice_list_403_with_significant_skew_retries_once(monkeypatch):
    monkeypatch.setattr(DRM, "clock_skew_seconds", 0.0)
    err = _client_error(403, date=_skewed_date(3600.0))
    calls = {"n": 0}

    async def _fake_list_voices(session, ssl_ctx, proxy):
        calls["n"] += 1
        if calls["n"] == 1:
            raise err
        return [{"Name": "ok"}]

    monkeypatch.setattr(voices_mod, "__list_voices", _fake_list_voices)
    import asyncio
    data = asyncio.run(voices_mod.list_voices())
    assert data == [{"Name": "ok"}]
    assert calls["n"] == 2
    assert DRM.clock_skew_seconds == pytest.approx(3600.0, abs=120.0)


def test_voice_list_403_retry_still_403_reraises_retry_error(monkeypatch):
    monkeypatch.setattr(DRM, "clock_skew_seconds", 0.0)
    first = _client_error(403, date=_skewed_date(3600.0))
    second = _client_error(403)
    calls = {"n": 0}

    async def _fake_list_voices(session, ssl_ctx, proxy):
        calls["n"] += 1
        raise first if calls["n"] == 1 else second

    monkeypatch.setattr(voices_mod, "__list_voices", _fake_list_voices)
    import asyncio
    with pytest.raises(aiohttp.ClientResponseError) as exc_info:
        asyncio.run(voices_mod.list_voices())
    assert calls["n"] == 2
    assert exc_info.value is second
    assert exc_info.value.status == 403
    assert not isinstance(exc_info.value, SkewAdjustmentError)
