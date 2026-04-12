import os
import sys

import logging
logging.basicConfig(level=logging.DEBUG)

addon_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, addon_dir)
sys.path.insert(0, os.path.join(addon_dir, 'external'))

from tests.conftest import MockAnkiUtils, MockServiceManager
from superfreetss_addon import logging_utils
from superfreetss_addon.servicemanager import ServiceManager

def test_edgetts_discovery():
    services_dir = os.path.join(addon_dir, 'superfreetss_addon', 'services')
    sm = ServiceManager(services_dir, 'superfreetss_addon.services', False)
    sm.init_services()
    sm.instantiate_all_services(instantiate_expensive=True)
    
    print("Discovered services:", sm.services.keys())
    assert "EdgeTTS" in sm.services

if __name__ == '__main__':
    test_edgetts_discovery()
