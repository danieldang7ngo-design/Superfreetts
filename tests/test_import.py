import sys
import os
import traceback
import types
from unittest.mock import MagicMock

# Mock anki environment
for mod in ['anki', 'anki.hooks', 'aqt', 'aqt.qt', 'aqt.utils', 'aqt.editor', 'aqt.gui_hooks', 'anki.sound']:
    sys.modules[mod] = MagicMock()

addon_dir = r'c:\Users\Administrator\AppData\Roaming\Anki2\addons21\Superfreetts'
sys.path.insert(0, os.path.join(addon_dir, 'external'))
sys.path.insert(0, addon_dir)

try:
    from superfreetss_addon.services import service_edgetts
    print("SUCCESS: imported service_edgetts")
except Exception as e:
    print("FAILED TO IMPORT service_edgetts")
    traceback.print_exc()
