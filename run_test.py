import os
import sys
from unittest.mock import MagicMock

# Mock Anki before anything else
sys.modules['aqt'] = MagicMock()
sys.modules['aqt.qt'] = MagicMock()
sys.modules['aqt.gui_hooks'] = MagicMock()
sys.modules['anki'] = MagicMock()
sys.modules['anki.sound'] = MagicMock()
import aqt
aqt.mw = MagicMock()
aqt.mw.addonManager = MagicMock()

# Add current dir to path
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

try:
    from superfreetss_addon.engine_manager import EngineManager
    from superfreetss_addon.sherpa_manager import SherpaManager
    
    print("--- 1. Testing EngineManager ---")
    success = EngineManager.ensure_installed()
    print(f"EngineManager Success: {success}")
    print(f"Python EXE: {EngineManager.get_python_exe()}")

    print("\n--- 2. Testing SherpaManager ---")
    success_sherpa = SherpaManager.ensure_installed()
    print(f"SherpaManager Success: {success_sherpa}")
    print(f"Sherpa Installed: {SherpaManager.is_installed()}")

    print("\n--- 3. Testing Import in Portable Python ---")
    if success and success_sherpa:
        python_exe = EngineManager.get_python_exe()
        libs_dir = SherpaManager.get_libs_dir()
        
        test_script = f"import sys; sys.path.insert(0, r'{libs_dir}'); import sherpa_onnx; import numpy; import soundfile; print('SUCCESS: All dependencies imported!')"
        import subprocess
        result = subprocess.run([python_exe, "-c", test_script], capture_output=True, text=True)
        print(f"Subprocess Out: {result.stdout}")
        print(f"Subprocess Err: {result.stderr}")

except Exception as e:
    import traceback
    traceback.print_exc()
