import sys
import os
import pytest
from unittest.mock import MagicMock

# Setup mock environment similar to conftest.py
mock_anki = MagicMock()
mock_aqt = MagicMock()
sys.modules['anki'] = mock_anki
sys.modules['anki.hooks'] = MagicMock()
sys.modules['anki.sound'] = MagicMock()
sys.modules['aqt'] = mock_aqt
sys.modules['aqt.gui_hooks'] = MagicMock()
sys.modules['aqt.qt'] = MagicMock()
sys._pytest_mode = True

# Add paths
addon_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, addon_dir)
sys.path.insert(0, os.path.join(addon_dir, 'external'))

from superfreetss_addon import resource_manager

def test_psutil_integration():
    """Verify that psutil is detected and working"""
    assert resource_manager.HAS_PSUTIL is True
    
    monitor = resource_manager.ResourceMonitor()
    assert monitor.process is not None
    
    ram_usage = monitor._get_ram_usage()
    print(f"\nDetected RAM Usage: {ram_usage}MB")
    assert ram_usage > 0
    
    status = monitor.report_status()
    assert "RAM:" in status
    assert "MB" in status

if __name__ == "__main__":
    # Test detection directly
    try:
        import psutil
        print(f"psutil found at: {psutil.__file__}")
        print(f"RAM Usage: {psutil.Process().memory_info().rss / 1024 / 1024:.2f} MB")
    except ImportError:
        print("psutil NOT found in current path")
