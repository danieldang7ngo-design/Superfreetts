import os
import sys

# Change to the directory of the script
script_dir = os.path.dirname(os.path.abspath(__file__))
addon_path = os.path.join(script_dir, 'superfreetss_addon')
if addon_path not in sys.path:
    sys.path.insert(0, addon_path)

# Mock Anki/aqt
from unittest.mock import MagicMock
sys.modules['aqt'] = MagicMock()
sys.modules['aqt.qt'] = MagicMock()
sys.modules['aqt.gui_hooks'] = MagicMock()
sys.modules['anki'] = MagicMock()
sys.modules['anki.sound'] = MagicMock()

import aqt
aqt.mw = MagicMock()
aqt.mw.addonManager = MagicMock()

try:
    from engine_manager import EngineManager
    from sherpa_manager import SherpaManager
    
    print("--- 1. Testing EngineManager ---")
    def on_progress(data):
        print(f"Engine Progress: {data}")
    
    success = EngineManager.ensure_installed(progress_callback=on_progress)
    print(f"EngineManager Success: {success}")
    print(f"Python EXE: {EngineManager.get_python_exe()}")

    print("\n--- 2. Testing SherpaManager ---")
    def on_sherpa_progress(data):
        print(f"Sherpa Progress: {data}")
        
    success_sherpa = SherpaManager.ensure_installed(progress_callback=on_sherpa_progress)
    print(f"SherpaManager Success: {success_sherpa}")
    print(f"Sherpa Installed: {SherpaManager.is_installed()}")

    print("\n--- 3. Testing Import in Portable Python ---")
    if success and success_sherpa:
        python_exe = EngineManager.get_python_exe()
        libs_dir = SherpaManager.get_libs_dir()
        
        # Test command
        # Use r'' for path to avoid backslash escaping issues on Windows
        test_script = f"import sys; sys.path.insert(0, r'{libs_dir}'); import sherpa_onnx; import numpy; import soundfile; print('SUCCESS: All dependencies imported!')"
        test_cmd = [python_exe, "-c", test_script]
        
        import subprocess
        result = subprocess.run(test_cmd, capture_output=True, text=True)
        print(f"Subprocess Return Code: {result.returncode}")
        print(f"Subprocess Out: {result.stdout}")
        print(f"Subprocess Err: {result.stderr}")

except Exception as e:
    import traceback
    traceback.print_exc()
