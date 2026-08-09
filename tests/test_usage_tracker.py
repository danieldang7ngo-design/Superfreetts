"""
Tests for superfreetts_addon.usage_tracker.UsageTracker.

Verifies local-only usage logging: session creation, aggregation, persistence
(flush + reload), summary math, monthly series and defensive error handling.
"""

import json
import os
import time

import pytest

from superfreetts_addon import constants
from superfreetts_addon import context
from superfreetts_addon import usage_tracker


@pytest.fixture
def tracker(tmp_path):
    return usage_tracker.UsageTracker(str(tmp_path))


@pytest.fixture
def batch_context():
    ctx = context.AudioRequestContext(constants.AudioRequestReason.batch)
    return ctx


def test_initial_summary_is_zero(tracker):
    summary = tracker.get_summary()
    assert summary["files_generated"] == 0
    assert summary["notes_updated"] == 0
    assert summary["realtime_plays"] == 0
    assert summary["cache_hits"] == 0
    assert summary["chars_generated"] == 0
    assert summary["generation_time_s"] == 0.0
    assert summary["money_saved_usd"] == 0.0
    assert summary["by_engine"] == {}


def test_record_file_generated_batch(tracker, batch_context):
    tracker.record_file_generated(batch_context, "EdgeTTS", 100, 1.5)
    summary = tracker.get_summary()
    assert summary["files_generated"] == 1
    assert summary["chars_generated"] == 100
    assert summary["by_engine"] == {"EdgeTTS": 1}
    assert summary["generation_time_s"] == pytest.approx(1.5)


def test_money_saved_scales_with_chars(tracker, batch_context):
    tracker.record_file_generated(batch_context, "EdgeTTS", 250000, 1.0)
    summary = tracker.get_summary()
    assert summary["money_saved_usd"] == pytest.approx(
        constants.USAGE_MONTHLY_COST_USD
    )


def test_realtime_play_uses_one_daily_session(tracker):
    tracker.record_realtime_play()
    tracker.record_realtime_play()
    summary = tracker.get_summary()
    assert summary["realtime_plays"] == 2
    sessions = tracker.get_recent_sessions(limit=10)
    assert len(sessions) == 1
    assert sessions[0]["kind"] == usage_tracker.SESSION_KIND_REALTIME


def test_note_updated_attaches_to_batch_session(tracker, batch_context):
    session_id = batch_context.get_batch_uuid_str()
    tracker.start_batch_session(session_id)
    tracker.record_note_updated(session_id)
    tracker.record_note_updated(session_id)
    summary = tracker.get_summary()
    assert summary["notes_updated"] == 2


def test_cache_hit_counts_separately(tracker, batch_context):
    tracker.record_cache_hit(batch_context, "PiperTTS", 50)
    summary = tracker.get_summary()
    assert summary["cache_hits"] == 1
    assert summary["files_generated"] == 0


def test_flush_and_reload_persists(tmp_path):
    tracker = usage_tracker.UsageTracker(str(tmp_path))
    ctx = context.AudioRequestContext(constants.AudioRequestReason.batch)
    tracker.record_file_generated(ctx, "Kokoro", 500, 2.0)
    tracker.flush()

    log_path = os.path.join(str(tmp_path), constants.USAGE_LOG_FILENAME)
    assert os.path.isfile(log_path)

    reloaded = usage_tracker.UsageTracker(str(tmp_path))
    summary = reloaded.get_summary()
    assert summary["files_generated"] == 1
    assert summary["chars_generated"] == 500
    assert summary["by_engine"] == {"Kokoro": 1}


def test_corrupt_log_file_is_tolerated(tmp_path):
    log_path = os.path.join(str(tmp_path), constants.USAGE_LOG_FILENAME)
    with open(log_path, "w", encoding="utf-8") as f:
        f.write("{ not valid json")
    tracker = usage_tracker.UsageTracker(str(tmp_path))
    summary = tracker.get_summary()
    assert summary["files_generated"] == 0


def test_monthly_series_groups_by_month(tracker, batch_context):
    tracker.record_file_generated(batch_context, "EdgeTTS", 100, 1.0)
    tracker.record_file_generated(batch_context, "EdgeTTS", 50, 0.5)
    monthly = tracker.get_monthly_series()
    assert len(monthly) == 1
    entry = monthly[0]
    assert entry["month"] == time.strftime("%Y-%m")
    assert entry["files_generated"] == 2
    assert entry["chars_generated"] == 150
