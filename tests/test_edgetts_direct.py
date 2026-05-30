import os
import sys

addon_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, addon_dir)
sys.path.insert(0, os.path.join(addon_dir, 'external'))

from tests import mock_anki

mock_anki.mock_all()

try:
    from superfreetts_addon.services.service_edgetts import EdgeTTS
    print("SUCCESS: EdgeTTS class imported directly!")
except Exception as e:
    import traceback
    traceback.print_exc()
