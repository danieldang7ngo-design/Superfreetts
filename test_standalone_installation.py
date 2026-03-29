import os
import sys
import shutil
import abc
from unittest.mock import MagicMock

# 1. SETUP Paths
script_dir = os.path.dirname(os.path.abspath(__file__))
addon_root = os.path.join(script_dir, 'superfreetss_addon')
if addon_root not in sys.path:
    sys.path.insert(0, addon_root)

# 2. MOCK relative import system for 'from . import ...'
# We'll create a dummy 'superfreetss_addon' package in sys.modules
import types
pkg = types.ModuleType('superfreetss_addon')
pkg.__path__ = [addon_root]
sys.modules['superfreetss_addon'] = pkg

# Mock logging_utils inside the package
mock_logging = types.ModuleType('superfreetss_addon.logging_utils')
mock_logging.get_child_logger = lambda n: MagicMock()
sys.modules['superfreetss_addon.logging_utils'] = mock_logging

# Mock downloader inside the package
mock_downloader = types.ModuleType('superfreetss_addon.downloader')
class DummyDownloader:
    def __init__(self, url, dest, progress_callback=None):
         self.url = url
    def start(self):
         print(f"Mock Download: {self.url}")
mock_downloader.TurboDownloader = DummyDownloader
sys.modules['superfreetss_addon.downloader'] = mock_downloader

# Mock aqt before anything else touches it
sys.modules['aqt'] = MagicMock()
sys.modules['aqt.qt'] = MagicMock()

# Now we can import EngineManager and SherpaManager without errors
try:
    print("Importing EngineManager...")
    from superfreetss_addon.engine_manager import EngineManager
    print("Importing SherpaManager...")
    from superfreetss_addon.sherpa_manager import SherpaManager

    print("\n--- STANDALONE LOGIC TEST ---")
    
    # Verify Paths
    python_exe = EngineManager.get_python_exe()
    print(f"EngineManager Python EXE: {python_exe}")
    if 'python_engine' in python_exe:
        print("SUCCESS: EngineManager path is unified.")
    else:
        print("FAILURE: EngineManager path is wrong.")

    # Verify Sherpa path
    libs_dir = SherpaManager.get_libs_dir()
    print(f"SherpaManager Libs DIR: {libs_dir}")
    if 'libs' in libs_dir and os.path.basename(os.path.dirname(libs_dir)) == 'superfreetss_addon':
        print("SUCCESS: SherpaManager path is correct.")
    else:
        print("FAILURE: SherpaManager path is wrong.")

    # Mock installation check
    # Let's see if is_installed() works (should be False unless already there)
    print(f"Engine Installed: {EngineManager.is_installed()}")
    print(f"Sherpa Installed: {SherpaManager.is_installed()}")

    print("\n--- TEST COMPLETED ---")
    
except Exception as e:
    import traceback
    traceback.print_exc()
