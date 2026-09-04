"""
runner_base.py — Shared IPC boilerplate for subprocess runner scripts.

Provides: setup_stdio(), log(), write_response().

Each runner script (kokoro_runner, piper_runner, sherpa_runner_v2,
supertonic_runner) imports from here instead of re-defining identical
boilerplate.  Only unique logic (model loading, TTS call) stays per-runner.
"""

import os
import sys
import time


def setup_stdio():
    """Force UTF-8 on stdin/stdout/stderr — pipes may not be safe by default."""
    if hasattr(sys.stdin, 'reconfigure'):
        try:
            sys.stdin.reconfigure(encoding='utf-8')
            sys.stdout.reconfigure(encoding='utf-8')
            sys.stderr.reconfigure(encoding='utf-8')
        except Exception:
            pass


def log(msg):
    """Write timestamped message to stderr (captured by Anki/parent process).
    Also appends to SUPERFREETTS_LOG_FILE if that env-var is set.
    """
    sys.stderr.write(f"[{time.strftime('%H:%M:%S')}] {msg}\n")
    sys.stderr.flush()
    log_path = os.environ.get('SUPERFREETTS_LOG_FILE')
    if log_path:
        try:
            with open(log_path, 'a', encoding='utf-8') as fh:
                fh.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")
        except Exception:
            pass


def write_response(response: str) -> bool:
    """Write a UTF-8 JSON line to stdout.buffer with BrokenPipeError guard.

    Returns True on success, False if the pipe is closed.
    """
    try:
        sys.stdout.buffer.write(response.encode('utf-8'))
        sys.stdout.buffer.flush()
        return True
    except (BrokenPipeError, OSError) as exc:
        log(f"stdout closed while writing response: {exc}")
        return False

