"""Hardening tests for the local Piper and Kokoro runner scripts."""

import json
import os
import subprocess
import sys

addon_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, addon_dir)
sys.path.insert(0, os.path.join(addon_dir, "external"))

from superfreetts_addon.services import kokoro_runner, piper_runner


def test_kokoro_lang_map_includes_hindi():
    assert kokoro_runner.LANG_MAP['h'] == 'hi'
    assert kokoro_runner.LANG_MAP['a'] == 'en-us'


def test_piper_sample_rate_is_read_from_model_config_and_cached(tmp_path):
    model = tmp_path / "voice.onnx"
    model.write_bytes(b"model")
    config = model.with_name(model.name + ".json")
    config.write_text(
        json.dumps({"audio": {"sample_rate": 24000}}),
        encoding="utf-8",
    )
    piper_runner._MODEL_SR_CACHE.clear()

    assert piper_runner.get_model_sample_rate(str(model)) == 24000

    # A later config edit must not be re-read for the same model in this
    # runner process (the cache is the point of the change).
    config.write_text(
        json.dumps({"audio": {"sample_rate": 16000}}),
        encoding="utf-8",
    )
    assert piper_runner.get_model_sample_rate(str(model)) == 24000

    piper_runner._MODEL_SR_CACHE.clear()
    assert piper_runner.get_model_sample_rate(str(model)) == 16000


def test_piper_sample_rate_falls_back_without_config(tmp_path):
    model = tmp_path / "no-config.onnx"
    model.write_bytes(b"model")
    piper_runner._MODEL_SR_CACHE.clear()

    assert piper_runner.get_model_sample_rate(str(model)) == piper_runner.DEFAULT_SAMPLE_RATE


class TimeoutProcess:
    def __init__(self):
        self.returncode = None
        self.killed = False
        self.waited = False

    def communicate(self, input=None, timeout=None):
        raise subprocess.TimeoutExpired(cmd="piper", timeout=timeout)

    def poll(self):
        return self.returncode

    def kill(self):
        self.killed = True
        self.returncode = -9

    def wait(self, timeout=None):
        self.waited = True
        return self.returncode


def test_piper_timeout_reaps_child_process(monkeypatch, tmp_path):
    piper_exe = tmp_path / "piper"
    piper_exe.write_bytes(b"binary")
    model = tmp_path / "voice.onnx"
    model.write_bytes(b"model")
    process = TimeoutProcess()

    monkeypatch.setattr(piper_runner.subprocess, "Popen", lambda *args, **kwargs: process)

    response = piper_runner.generate_single(
        str(piper_exe),
        {
            "text": "hello",
            "model_path": str(model),
            "data_dir": str(tmp_path),
        },
    )

    assert response["status"] == "error"
    assert "timed out" in response["message"]
    assert process.killed is True
    assert process.waited is True
