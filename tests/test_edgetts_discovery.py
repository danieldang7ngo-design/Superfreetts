import os
import sys

import logging
logging.basicConfig(level=logging.DEBUG)

addon_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, addon_dir)
sys.path.insert(0, os.path.join(addon_dir, 'external'))

from tests import mock_anki

mock_anki.mock_all()

from superfreetts_addon.servicemanager import ServiceManager

def test_edgetts_discovery():
    services_dir = os.path.join(addon_dir, 'superfreetts_addon', 'services')
    sm = ServiceManager(services_dir, 'superfreetts_addon.services', False)
    sm.init_services()
    sm.instantiate_all_services(instantiate_expensive=True)
    
    print("Discovered services:", sm.services.keys())
    assert "EdgeTTS" in sm.services

if __name__ == '__main__':
    test_edgetts_discovery()
