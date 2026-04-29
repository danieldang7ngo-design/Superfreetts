import sys
import os
import traceback

addon_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(addon_dir, 'external'))
sys.path.insert(0, addon_dir)

from tests import mock_anki

mock_anki.mock_all()

try:
    from superfreetss_addon.services import service_edgetts
    print("SUCCESS: imported service_edgetts")
except Exception as e:
    print("FAILED TO IMPORT service_edgetts")
    traceback.print_exc()
