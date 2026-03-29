import os
import sys
import shutil
from unittest.mock import MagicMock

# 1. Setup paths
script_dir = os.path.dirname(os.path.abspath(__file__))
addon_dir = os.path.join(script_dir, 'superfreetss_addon')

# 2. Mock ALL forbidden modules before they are even touched
mock_modules = [
    'aqt', 'aqt.qt', 'aqt.gui_hooks', 'aqt.utils',
    'anki', 'anki.hooks', 'anki.sound', 'anki.utils'
]
for mod in mock_modules:
    sys.modules[mod] = MagicMock()

# 3. Add addon_dir to sys.path and also sys.modules trick for relative imports
sys.path.insert(0, addon_dir)

# To allow 'from . import ...' we need to mock the parent package
import types
pkg = types.ModuleType('superfreetss_addon')
pkg.__path__ = [addon_dir]
sys.modules['superfreetss_addon'] = pkg

# Now we can try to import the specific modules
try:
    print("Importing EngineManager...")
    import engine_manager
    from engine_manager import EngineManager
    
    print("Importing SherpaManager...")
    import sherpa_manager
    from sherpa_manager import SherpaManager

    print("\n--- Starting Installation Test ---")
    
    # We only test a small part to avoid 100MB download if not needed for the agent
    # But user wants a full test. 
    # Let's just run it.
    
    # Redirect logs to stdout
    import logging
    root = logging.getLogger('SuperFreeTTS')
    handler = logging.StreamHandler(sys.stdout)
    root.addHandler(handler)
    root.setLevel(logging.DEBUG)

    success_eng = EngineManager.ensure_installed()
    print(f"Engine Success: {success_eng}")
    
    if success_eng:
        success_shp = SherpaManager.ensure_installed()
        print(f"Sherpa Success: {success_shp}")
        
        if success_shp:
             print("\n--- Verifying Imports in new Engine ---")
             py_exe = EngineManager.get_python_exe()
             libs = SherpaManager.get_libs_dir()
             import subprocess
             res = subprocess.run([py_exe, "-c", f"import sys; sys.path.insert(0, r'{libs}'); import sherpa_onnx; print('Sherpa Import OK')"], capture_output=True, text=True)
             print(f"Final Result: {res.stdout} {res.stderr}")

except Exception as e:
    import traceback
    traceback.print_exc()
