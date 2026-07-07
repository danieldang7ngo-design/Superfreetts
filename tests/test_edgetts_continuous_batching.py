import aiohttp
import asyncio
import os
import sys
from types import SimpleNamespace

from tests import mock_anki

mock_anki.mock_all()

addon_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, addon_dir)
sys.path.insert(0, os.path.join(addon_dir, "external"))

from superfreetts_addon.services import service_edgetts


def test_edgetts_batch_starts_next_item_when_slot_frees(monkeypatch):
    starts = {}
    finishes = {}
    active = {"count": 0, "max": 0}
    delays = {
        "text-0": 0.05,
        "text-1": 0.18,
        "text-2": 0.18,
        "text-3": 0.01,
        "text-4": 0.01,
    }

    class FakeCommunicate:
        def __init__(self, text, voice_key, rate=None, pitch=None, volume=None):
            self.text = text

        async def stream(self):
            loop = asyncio.get_running_loop()
            starts[self.text] = loop.time()
            active["count"] += 1
            active["max"] = max(active["max"], active["count"])
            try:
                await asyncio.sleep(delays[self.text])
                yield {"type": "audio", "data": f"audio:{self.text}".encode("utf-8")}
            finally:
                finishes[self.text] = loop.time()
                active["count"] -= 1

    monkeypatch.setattr(service_edgetts.edge_tts, "Communicate", FakeCommunicate)

    svc = service_edgetts.EdgeTTS()
    config = {
        "concurrency_workers": 3,
        "max_retries": 0,
        "initial_delay_min_ms": 0,
        "initial_delay_max_ms": 0,
        "wave_start_stagger_ms": 0,
        "retry_backoff_seconds": 1,
        "debug_logging": False,
    }
    monkeypatch.setattr(
        svc,
        "get_configuration_value_optional",
        lambda key, default=None: config.get(key, default),
    )

    results = svc.get_tts_audio_batch(
        ["text-0", "text-1", "text-2", "text-3", "text-4"],
        SimpleNamespace(voice_key="fake-voice"),
        {},
    )

    assert results == [
        b"audio:text-0",
        b"audio:text-1",
        b"audio:text-2",
        b"audio:text-3",
        b"audio:text-4",
    ]
    assert active["max"] == 3
    assert starts["text-3"] < finishes["text-1"]
    assert starts["text-3"] < finishes["text-2"]


def test_edgetts_batch_fails_fast_on_connectivity_error(monkeypatch):
    create_calls = {"count": 0}

    class FakeAudioStream:
        def __aiter__(self):
            return self

        async def __anext__(self):
            raise aiohttp.ClientConnectorError(None, OSError("Network is unreachable"))

    class FakeCommunicate:
        def __init__(self, text, voice_key, rate=None, pitch=None, volume=None):
            create_calls["count"] += 1

        def stream(self):
            return FakeAudioStream()

    monkeypatch.setattr(service_edgetts.edge_tts, "Communicate", FakeCommunicate)

    svc = service_edgetts.EdgeTTS()
    config = {
        "concurrency_workers": 1,
        "max_retries": 5,
        "initial_delay_min_ms": 0,
        "initial_delay_max_ms": 0,
        "wave_start_stagger_ms": 0,
        "retry_backoff_seconds": 0,
        "debug_logging": False,
    }
    monkeypatch.setattr(
        svc,
        "get_configuration_value_optional",
        lambda key, default=None: config.get(key, default),
    )

    results = svc.get_tts_audio_batch(["text-0"], SimpleNamespace(voice_key="fake-voice"), {})

    assert results == [None]
    assert create_calls["count"] == 1
