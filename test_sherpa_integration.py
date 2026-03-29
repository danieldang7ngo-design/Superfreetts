import os
import sys
import json
import subprocess
import time

# Paths
ADDON_DIR = os.path.dirname(os.path.abspath(__file__))
PYTHON_EXE = os.path.join(ADDON_DIR, 'data', 'kokoro_engine', 'python.exe')
LIBS_DIR = os.path.join(ADDON_DIR, 'libs')
RUNNER_PATH = os.path.join(ADDON_DIR, 'services', 'piper_runner.py')

def verify():
    print("--- Sherpa-ONNX Unified Verification ---")
    
    # 1. Check SherpaManager
    try:
        from superfreetss_addon.sherpa_manager import SherpaManager
        print(f"Manager Location: {SherpaManager.get_libs_dir()}")
        print(f"Is Installed (locally): {SherpaManager.is_installed()}")
    except ImportError as e:
        print(f"Error importing SherpaManager: {e}")
        return

    # 2. Check Portable Python
    if not os.path.exists(PYTHON_EXE):
        print(f"Warning: Portable Python not found at {PYTHON_EXE}")
        return
    print(f"Using Python: {PYTHON_EXE}")

    # 3. Verify Runner can import from libs/
    # We simulate a subprocess run
    print(f"Testing runner import chain: {RUNNER_PATH}")
    
    # We use a small script that just tries to import sherpa_onnx
    test_code = f"""
import sys
import os
# The runner adds this automatically in our new implementation
base_dir = os.path.dirname(os.path.dirname(r'{RUNNER_PATH}'))
libs_path = os.path.join(base_dir, 'libs')
if os.path.exists(libs_path):
    sys.path.insert(0, libs_path)

try:
    import sherpa_onnx
    print(f"SUCCESS: Imported sherpa_onnx v{{sherpa_onnx.__version__}} from {{sherpa_onnx.__file__}}")
except ImportError as e:
    print(f"FAILED: {{e}}")
    print(f"Path: {{sys.path}}")
"""
    
    with open('tmp_test_sherpa.py', 'w', encoding='utf-8') as f:
        f.write(test_code)
    
    try:
        res = subprocess.run([PYTHON_EXE, 'tmp_test_sherpa.py'], capture_output=True, text=True)
        print("Subprocess Output:")
        print(res.stdout)
        if res.stderr:
            print("Subprocess Errors:")
            print(res.stderr)
    finally:
        if os.path.exists('tmp_test_sherpa.py'):
            os.remove('tmp_test_sherpa.py')

if __name__ == "__main__":
    verify()
