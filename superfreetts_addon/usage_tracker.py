"""
usage_tracker.py — Local-only usage logging and dashboard stats for Super Free TTS.

Tracks what the user creates (aggregate per session, not per file) and stores it
in a gitignored JSON file under ``user_files/``. Everything stays on the local
machine — no telemetry, no network requests, consistent with the Lite build.

Session model:
  - batch   : one batch run  = one session (keyed by AudioRequestContext.batch_uuid)
  - single  : one easy/editor note add = one session
  - realtime: all plays on a calendar day merged into one session

The tracker is deliberately defensive: every public method is wrapped so a
storage error never breaks TTS generation.
"""

import json
import os
import threading
import time

from typing import Any, Dict, List

from . import constants
from . import logging_utils

logger = logging_utils.get_child_logger(__name__)

# Session kinds
SESSION_KIND_BATCH = "batch"
SESSION_KIND_SINGLE = "single"
SESSION_KIND_REALTIME = "realtime"


class UsageTracker:
    def __init__(self, user_files_dir: str) -> None:
        self._user_files_dir = user_files_dir
        self._file_path = os.path.join(user_files_dir, constants.USAGE_LOG_FILENAME)
        self._lock = threading.Lock()
        self._sessions: Dict[str, Dict[str, Any]] = {}
        self._dirty = False
        self._load()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _default_session(self, session_id: str, kind: str, label: str = "") -> Dict[str, Any]:
        return {
            "id": session_id,
            "kind": kind,
            "label": label,
            "date": time.strftime("%Y-%m-%d"),
            "files_generated": 0,
            "chars_generated": 0,
            "notes_updated": 0,
            "realtime_plays": 0,
            "cache_hits": 0,
            "generation_time_s": 0.0,
            "by_engine": {},
        }

    def _load(self) -> None:
        try:
            if os.path.isfile(self._file_path):
                with open(self._file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self._sessions = data.get("sessions", {})
        except Exception as e:
            logger.warning(f"[USAGE] Failed to load usage log, starting fresh: {e}")
            self._sessions = {}

    def flush(self) -> None:
        """Atomically persist the current in-memory sessions to disk."""
        try:
            with self._lock:
                if not self._dirty:
                    return
                data = {
                    "schema_version": constants.USAGE_SCHEMA_VERSION,
                    "sessions": self._sessions,
                }
                os.makedirs(self._user_files_dir, exist_ok=True)
                tmp_path = self._file_path + ".tmp"
                with open(tmp_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                os.replace(tmp_path, self._file_path)
                self._dirty = False
        except Exception as e:
            logger.warning(f"[USAGE] Failed to flush usage log: {e}")

    def _get_or_create_session(self, session_id: str, kind: str, label: str = "") -> Dict[str, Any]:
        with self._lock:
            session = self._sessions.get(session_id)
            if session is None:
                session = self._default_session(session_id, kind, label)
                self._sessions[session_id] = session
                self._dirty = True
            return session

    def _session_info_for_context(self, audio_request_context) -> (str, str):
        """Return ``(session_id, kind)`` for an AudioRequestContext.

        - realtime reason → one session per calendar day
        - everything else (batch / editor / preview excluded by caller) →
          one session per AudioRequestContext (its batch_uuid), which is one
          per batch run or per single-note add.
        """
        if audio_request_context is None:
            return f"{SESSION_KIND_SINGLE}_{time.strftime('%Y-%m-%d')}", SESSION_KIND_SINGLE
        reason = audio_request_context.audio_request_reason
        if reason == constants.AudioRequestReason.realtime:
            date_str = time.strftime("%Y-%m-%d")
            return f"{SESSION_KIND_REALTIME}_{date_str}", SESSION_KIND_REALTIME
        if reason in (constants.AudioRequestReason.batch,):
            return audio_request_context.get_batch_uuid_str(), SESSION_KIND_BATCH
        return audio_request_context.get_batch_uuid_str(), SESSION_KIND_SINGLE

    def _record_generation(self, session_id: str, kind: str, engine: str, chars: int, duration_s: float) -> None:
        session = self._get_or_create_session(session_id, kind)
        session["files_generated"] += 1
        session["chars_generated"] += chars
        session["generation_time_s"] += duration_s
        session["by_engine"][engine] = session["by_engine"].get(engine, 0) + 1
        self._dirty = True

    def _record_cache_hit(self, session_id: str, kind: str, engine: str, chars: int) -> None:
        session = self._get_or_create_session(session_id, kind)
        session["cache_hits"] += 1
        self._dirty = True

    def _record_note_updated(self, session_id: str) -> None:
        session = self._get_or_create_session(session_id, SESSION_KIND_BATCH)
        session["notes_updated"] += 1
        self._dirty = True

    def _record_realtime_play(self) -> None:
        date_str = time.strftime("%Y-%m-%d")
        session_id = f"{SESSION_KIND_REALTIME}_{date_str}"
        session = self._get_or_create_session(session_id, SESSION_KIND_REALTIME)
        session["realtime_plays"] += 1
        self._dirty = True

    # ------------------------------------------------------------------
    # Public recording API (thread-safe, defensive)
    # ------------------------------------------------------------------

    def start_batch_session(self, session_id: str) -> None:
        """Pre-create a batch session so note_updated records land on it."""
        try:
            self._get_or_create_session(session_id, SESSION_KIND_BATCH)
        except Exception as e:
            logger.warning(f"[USAGE] start_batch_session failed: {e}")

    def record_file_generated(self, audio_request_context, engine: str, chars: int, duration_s: float) -> None:
        try:
            session_id, kind = self._session_info_for_context(audio_request_context)
            self._record_generation(session_id, kind, engine, chars, duration_s)
        except Exception as e:
            logger.warning(f"[USAGE] record_file_generated failed: {e}")

    def record_cache_hit(self, audio_request_context, engine: str, chars: int) -> None:
        try:
            session_id, kind = self._session_info_for_context(audio_request_context)
            self._record_cache_hit(session_id, kind, engine, chars)
        except Exception as e:
            logger.warning(f"[USAGE] record_cache_hit failed: {e}")

    def record_note_updated(self, session_id: str) -> None:
        try:
            self._record_note_updated(session_id)
        except Exception as e:
            logger.warning(f"[USAGE] record_note_updated failed: {e}")

    def record_realtime_play(self) -> None:
        try:
            self._record_realtime_play()
        except Exception as e:
            logger.warning(f"[USAGE] record_realtime_play failed: {e}")

    # ------------------------------------------------------------------
    # Reporting API
    # ------------------------------------------------------------------

    def get_summary(self) -> Dict[str, Any]:
        self.flush()
        with self._lock:
            sessions = list(self._sessions.values())
            files_generated = sum(s["files_generated"] for s in sessions)
            chars_generated = sum(s["chars_generated"] for s in sessions)
            notes_updated = sum(s["notes_updated"] for s in sessions)
            realtime_plays = sum(s["realtime_plays"] for s in sessions)
            cache_hits = sum(s["cache_hits"] for s in sessions)
            generation_time_s = sum(s["generation_time_s"] for s in sessions)
            by_engine: Dict[str, int] = {}
            for s in sessions:
                for engine, count in s["by_engine"].items():
                    by_engine[engine] = by_engine.get(engine, 0) + count
            money_saved_usd = (
                chars_generated
                * constants.USAGE_MONTHLY_COST_USD
                / constants.USAGE_MONTHLY_CHARS_ALLOWED
            )
            return {
                "files_generated": files_generated,
                "chars_generated": chars_generated,
                "notes_updated": notes_updated,
                "realtime_plays": realtime_plays,
                "cache_hits": cache_hits,
                "generation_time_s": generation_time_s,
                "money_saved_usd": money_saved_usd,
                "by_engine": by_engine,
            }

    def get_recent_sessions(self, limit: int = 20) -> List[Dict[str, Any]]:
        self.flush()
        with self._lock:
            sessions = list(self._sessions.values())
            sessions.sort(key=lambda s: s.get("date", ""), reverse=True)
            return sessions[:limit]

    def get_monthly_series(self) -> List[Dict[str, Any]]:
        """Aggregate sessions per month (YYYY-MM), only months with activity."""
        self.flush()
        monthly: Dict[str, Dict[str, Any]] = {}
        with self._lock:
            for s in self._sessions.values():
                month = s.get("date", "")[:7]
                if not month:
                    continue
                entry = monthly.setdefault(
                    month,
                    {"month": month, "files_generated": 0, "notes_updated": 0, "chars_generated": 0},
                )
                entry["files_generated"] += s["files_generated"]
                entry["notes_updated"] += s["notes_updated"]
                entry["chars_generated"] += s["chars_generated"]
        return [monthly[k] for k in sorted(monthly.keys())]
