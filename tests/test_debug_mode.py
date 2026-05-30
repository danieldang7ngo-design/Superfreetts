"""
Debug Mode Test Script

This script tests the debug mode functionality and performance tracking.
It verifies that:
1. Debug mode can be toggled on/off
2. Performance tracking works correctly in debug mode
3. Logging works as expected

IMPORTANT: Each test saves and restores logging_utils global state
to avoid poisoning subsequent pytest test modules.
"""

import sys
import os
import pytest

# Add the plugin directory to the path
plugin_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, plugin_dir)

from superfreetts_addon import logging_utils
from superfreetts_addon import performance_tracker


@pytest.fixture(autouse=True)
def restore_logging_state():
    """Save and restore logging_utils global state around every test."""
    saved_silent = logging_utils.SILENT_LOGGING_MODE
    saved_force = logging_utils.FORCE_DEBUG_MODE
    yield
    # Restore original state so subsequent tests are not affected
    logging_utils.SILENT_LOGGING_MODE = saved_silent
    logging_utils.FORCE_DEBUG_MODE = saved_force
    # Re-enable console logging if it was active before
    if not saved_silent:
        logging_utils.configure_console_logging()


def test_debug_mode_toggle():
    """Test that debug mode can be toggled"""
    # Force known initial state for this test
    logging_utils.configure_silent()
    assert logging_utils.SILENT_LOGGING_MODE == True, "Should be silent after configure_silent()"

    # Configure console logging (enables debug mode)
    logging_utils.configure_console_logging()
    assert logging_utils.SILENT_LOGGING_MODE == False, "Debug mode should be enabled after configure_console_logging"

    # Configure silent mode again
    logging_utils.configure_silent()
    assert logging_utils.SILENT_LOGGING_MODE == True, "Silent mode should be enabled after configure_silent"


def test_performance_tracking():
    """Test performance tracking functionality"""
    # Enable debug mode for this test
    logging_utils.configure_console_logging()

    # Get tracker
    tracker = performance_tracker.get_performance_tracker()

    # Test starting and ending generation
    import time
    tracker.start_generation("Hello world", "en-US-AriaNeural")
    time.sleep(0.1)  # Simulate generation
    duration = tracker.end_generation()

    assert duration is not None, "Duration should not be None"
    assert duration >= 0.05, f"Duration should be at least 0.05s, got {duration}"

    # Test stats retrieval
    count = tracker.get_generation_count()
    assert count >= 1, f"Should have at least 1 generation tracked, got {count}"

    avg_duration = tracker.get_average_duration()
    assert avg_duration >= 0.05, f"Average duration should be at least 0.05s, got {avg_duration}"

    # Test report generation
    report = tracker.report()
    assert len(report) > 0, "Report should not be empty"
    assert "PERFORMANCE REPORT" in report, "Report should contain header"

    # Reset tracker
    tracker.reset()
    assert tracker.get_generation_count() == 0, "Tracker should be reset"


def test_performance_tracking_disabled_in_silent_mode():
    """Test that performance tracking is disabled in silent mode"""
    # Configure silent mode
    logging_utils.configure_silent()

    # Get tracker
    tracker = performance_tracker.get_performance_tracker()
    tracker.reset()

    # Start and end generation
    tracker.start_generation("Hello", "en-US")
    duration = tracker.end_generation()

    # Should return None in silent mode
    assert duration is None, f"Duration should be None in silent mode, got {duration}"

    # Generation count should be 0
    count = tracker.get_generation_count()
    assert count == 0, f"Generation count should be 0 in silent mode, got {count}"


def test_logger_creation():
    """Test that logger creation works in both modes"""
    # Test in debug mode
    logging_utils.configure_console_logging()
    logger = logging_utils.get_child_logger(__name__)
    assert logger is not None, "Logger should not be None"

    # Test in silent mode
    logging_utils.configure_silent()
    logger = logging_utils.get_child_logger(__name__)
    assert logger is not None, "Logger should not be None"
    assert isinstance(logger, logging_utils.NullLogger), "Logger should be NullLogger in silent mode"


if __name__ == "__main__":
    pytest.main([__file__, '-v'])
