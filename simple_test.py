import os
import sys
from unittest.mock import MagicMock

# 1. SETUP
script_dir = os.path.dirname(os.path.abspath(__file__))
addon_dir = os.path.join(script_dir, 'superfreetss_addon')
sys.path.insert(0, addon_dir)

# 2. MOCK relative import system
sys.modules['aqt'] = MagicMock()
sys.modules['anki'] = MagicMock()

# Create dummy logging_utils
class DummyLogger:
    def info(self, m): print(f"INFO: {m}")
    def error(self, m): print(f"ERROR: {m}")
    def debug(self, m): print(f"DEBUG: {m}")

def get_child_logger(n): return DummyLogger()

# Inject dummy into sys.modules to satisfy relative imports if they were absolute
# Actually, I'll just fix the test script to import successfully.

print(f"Testing EngineManager logic in {addon_dir}...")
from engine_manager import EngineManager

print(f"Is Installed: {EngineManager.is_installed()}")
print(f"Python EXE: {EngineManager.get_python_exe()}")

# Verify the path contains 'python_engine'
if 'python_engine' in EngineManager.get_python_exe():
    print("SUCCESS: Path is correct.")
else:
    print("FAILURE: Path is wrong.")
