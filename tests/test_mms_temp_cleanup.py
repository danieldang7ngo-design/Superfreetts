"""MMS batch temp WAV files must be removed on every exit path.

Regression test for the 2026-10-22 audit finding P2: the per-task temp files
were cleaned up only after a successful read, so a failed readline, invalid
JSON or a retry leaked them into the system temp directory.
"""

import io
import json
import os
import sys
import tempfile
from types import SimpleNamespace

import pytest

from superfreetts_addon.services import service_mms


WAV_BYTES = b"RIFF" + (36).to_bytes(4, "little") + b"WAVEfmt " + b"\x00" * 64


class FakeProcess:
    def __init__(self, response: bytes):
        self.stdin = io.BytesIO()
        self.stdout = io.BytesIO(response)
        self.is_healthy = True


class FakePool:
    def __init__(self, process):
        self.process = process
        self.released = 0

    def get_process(self, *args, **kwargs):
        return self.process

    def release_process(self, *args, **kwargs):
        self.released += 1


def make_mms(tmp_path, monkeypatch, response, fill_wav=False):
    (tmp_path / "mms_models" / "eng").mkdir(parents=True)
    monkeypatch.setattr(service_mms.constants, "DATA_DIR", str(tmp_path))

    mms = object.__new__(service_mms.MmsTTS)
    mms._get_python_exe = lambda: sys.executable

    def config_value(key, default=None):
        if key == "num_threads":
            return 1
        return default

    mms.get_configuration_value_optional = config_value

    created = []
    real_mkstemp = tempfile.mkstemp

    def tracking_mkstemp(*args, **kwargs):
        fd, path = real_mkstemp(*args, **kwargs)
        created.append(path)
        if fill_wav:
            with os.fdopen(os.dup(fd), "wb") as f:
                f.write(WAV_BYTES)
        return fd, path

    monkeypatch.setattr(tempfile, "mkstemp", tracking_mkstemp)

    pool = FakePool(FakeProcess(response))
    monkeypatch.setattr(service_mms, "_sherpa_pool", pool)
    return mms, created, pool


def run_batch(mms, texts):
    voice = SimpleNamespace(voice_key="mms_eng")
    return mms.get_tts_audio_batch(texts, voice, {})


@pytest.mark.unit
def test_temp_files_cleaned_when_runner_returns_invalid_json(tmp_path, monkeypatch):
    texts = ["one", "two", "three"]
    mms, created, pool = make_mms(tmp_path, monkeypatch, b"not-json\n")

    results = run_batch(mms, texts)

    assert results == [None] * len(texts)
    assert len(created) == 2 * len(texts), "one attempt pair per retry"
    assert all(not os.path.exists(path) for path in created)
    assert pool.released == 2


@pytest.mark.unit
def test_temp_files_cleaned_when_runner_pipe_breaks(tmp_path, monkeypatch):
    texts = ["one", "two"]
    mms, created, pool = make_mms(tmp_path, monkeypatch, b"")

    results = run_batch(mms, texts)

    assert results == [None] * len(texts)
    assert created
    assert all(not os.path.exists(path) for path in created)
    assert pool.released == 2


@pytest.mark.unit
def test_temp_files_cleaned_on_success(tmp_path, monkeypatch):
    texts = ["one", "two"]
    response = json.dumps({"status": "ok", "results": [{"status": "ok"}, {"status": "ok"}]}).encode("utf-8") + b"\n"
    mms, created, pool = make_mms(tmp_path, monkeypatch, response, fill_wav=True)

    results = run_batch(mms, texts)

    assert len(results) == 2
    assert all(result == WAV_BYTES for result in results)
    assert all(not os.path.exists(path) for path in created)
    assert pool.released == 1
