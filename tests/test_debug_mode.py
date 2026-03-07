"""
Debug Mode Test Script

This script tests the debug mode functionality and performance tracking.
It verifies that:
1. Debug mode can be toggled on/off
2. Performance tracking works correctly in debug mode
3. Logging works as expected
"""

import sys
import os

# Add the plugin directory to the path
plugin_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, plugin_dir)

from superfreetss_addon import logging_utils
from superfreetss_addon import performance_tracker


def test_debug_mode_toggle():
    """Test that debug mode can be toggled"""
    print("[TEST] Testing debug mode toggle...")
    
    # Initially should be silent
    assert logging_utils.SILENT_LOGGING_MODE == True, "Initial mode should be silent"
    print("  ✓ Initial mode is silent")
    
    # Configure console logging (enables debug mode)
    logging_utils.configure_console_logging()
    assert logging_utils.SILENT_LOGGING_MODE == False, "Debug mode should be enabled after configure_console_logging"
    print("  ✓ Debug mode enabled")
    
    # Configure silent mode
    logging_utils.configure_silent()
    assert logging_utils.SILENT_LOGGING_MODE == True, "Silent mode should be enabled after configure_silent"
    print("  ✓ Silent mode enabled")
    
    print("[PASS] Debug mode toggle test\n")


def test_performance_tracking():
    """Test performance tracking functionality"""
    print("[TEST] Testing performance tracking...")
    
    # Enable debug mode
    logging_utils.configure_console_logging()
    
    # Get tracker
    tracker = performance_tracker.get_performance_tracker()
    
    # Test starting and ending generation
    import time
    tracker.start_generation("Hello world", "en-US-AriaNeural")
    time.sleep(0.1)  # Simulate generation
    duration = tracker.end_generation()
    
    assert duration is not None, "Duration should not be None"
    assert duration >= 0.1, f"Duration should be at least 0.1s, got {duration}"
    print(f"  ✓ Generation tracking: {duration:.2f}s")
    
    # Test stats retrieval
    count = tracker.get_generation_count()
    assert count == 1, f"Should have 1 generation tracked, got {count}"
    print(f"  ✓ Generation count: {count}")
    
    avg_duration = tracker.get_average_duration()
    assert avg_duration >= 0.1, f"Average duration should be at least 0.1s, got {avg_duration}"
    print(f"  ✓ Average duration: {avg_duration:.2f}s")
    
    # Test report generation
    report = tracker.report()
    assert len(report) > 0, "Report should not be empty"
    assert "PERFORMANCE REPORT" in report, "Report should contain header"
    print("  ✓ Report generation works")
    
    # Reset tracker
    tracker.reset()
    assert tracker.get_generation_count() == 0, "Tracker should be reset"
    print("  ✓ Tracker reset works")
    
    print("[PASS] Performance tracking test\n")


def test_performance_tracking_disabled_in_silent_mode():
    """Test that performance tracking is disabled in silent mode"""
    print("[TEST] Testing performance tracking in silent mode...")
    
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
    print("  ✓ Generation tracking disabled in silent mode")
    
    # Generation count should be 0
    count = tracker.get_generation_count()
    assert count == 0, f"Generation count should be 0 in silent mode, got {count}"
    print("  ✓ Generation count is 0 in silent mode")
    
    print("[PASS] Performance tracking in silent mode test\n")


def test_logger_creation():
    """Test that logger creation works in both modes"""
    print("[TEST] Testing logger creation...")
    
    # Test in debug mode
    logging_utils.configure_console_logging()
    logger = logging_utils.get_child_logger(__name__)
    assert logger is not None, "Logger should not be None"
    print("  ✓ Logger created in debug mode")
    
    # Test in silent mode
    logging_utils.configure_silent()
    logger = logging_utils.get_child_logger(__name__)
    assert logger is not None, "Logger should not be None"
    assert isinstance(logger, logging_utils.NullLogger), "Logger should be NullLogger in silent mode"
    print("  ✓ Logger created in silent mode")
    
    print("[PASS] Logger creation test\n")


def run_all_tests():
    """Run all tests"""
    print("="*60)
    print("DEBUG MODE & PERFORMANCE TRACKER TESTS")
    print("="*60 + "\n")
    
    try:
        test_debug_mode_toggle()
        test_performance_tracking()
        test_performance_tracking_disabled_in_silent_mode()
        test_logger_creation()
        
        print("="*60)
        print("ALL TESTS PASSED ✓")
        print("="*60)
        return True
    except AssertionError as e:
        print(f"\n[FAIL] {e}")
        return False
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
