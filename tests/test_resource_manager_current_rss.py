"""Regression tests for current-RSS sampling without psutil.

The old fallback used ``resource.ru_maxrss`` on every platform.  That value is
a peak and never decreases, so GC decisions kept seeing a stale high-water
mark after a one-off allocation spike.  These tests pin the platform-specific
current-RSS path and the peak-only fallback.
"""

from unittest.mock import patch

import pytest

from superfreetts_addon import resource_manager


@pytest.mark.unit
def test_linux_current_rss_reads_resident_pages(tmp_path, monkeypatch):
    statm = tmp_path / "statm"
    # 51200 resident pages * 4096 bytes = 200 MiB.
    statm.write_text("100000 51200 100 1 0 200 0\n", encoding="utf-8")
    monkeypatch.setattr(resource_manager.os, "sysconf", lambda name: 4096)

    assert resource_manager._linux_current_rss_mb(str(statm)) == 200


@pytest.mark.unit
def test_linux_current_rss_rejects_bad_statm(tmp_path):
    statm = tmp_path / "statm"
    statm.write_text("broken\n", encoding="utf-8")
    with pytest.raises(ValueError):
        resource_manager._linux_current_rss_mb(str(statm))


@pytest.mark.unit
def test_get_process_ram_prefers_linux_current_rss(monkeypatch):
    monkeypatch.setattr(resource_manager.platform, "system", lambda: "Linux")
    monkeypatch.setattr(
        resource_manager,
        "_linux_current_rss_mb",
        lambda: 123,
    )

    def fail_peak():
        raise AssertionError("peak fallback must not run when current RSS works")

    with patch("resource.getrusage", side_effect=fail_peak):
        assert resource_manager._get_process_ram_usage_without_psutil() == 123
    assert resource_manager.get_process_ram_source() == "linux_proc"


@pytest.mark.unit
def test_get_process_ram_falls_back_to_peak_only_on_failure(monkeypatch):
    monkeypatch.setattr(resource_manager.platform, "system", lambda: "Linux")

    def fail_current():
        raise OSError("cannot read /proc")

    monkeypatch.setattr(resource_manager, "_linux_current_rss_mb", fail_current)

    class Usage:
        ru_maxrss = 204800  # KiB -> 200 MiB

    monkeypatch.setattr("resource.getrusage", lambda who: Usage())

    assert resource_manager._get_process_ram_usage_without_psutil() == 200
    assert resource_manager.get_process_ram_source() == "peak_fallback"


@pytest.mark.unit
def test_resource_monitor_gc_baseline_resets(monkeypatch):
    monitor = resource_manager.ResourceMonitor()
    monitor._last_gc_ram_mb = 100
    monitor._last_gc_completed = 0

    with patch.object(monitor, "_get_ram_usage", return_value=700):
        assert monitor.should_trigger_gc(1) is True

    with patch.object(monitor, "_get_ram_usage", return_value=700):
        monitor.mark_gc(1)

    with patch.object(monitor, "_get_ram_usage", return_value=700):
        assert monitor.should_trigger_gc(2) is False
