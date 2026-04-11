import sys
import os
import logging
from unittest.mock import MagicMock

# Setup path
addon_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(addon_path)

# Mock Anki
import tests.mock_anki as mock_anki
mock_anki.mock_all()

import aqt
from tests.conftest import MockAnkiUtils
anki_utils = MockAnkiUtils()
aqt.mw = MagicMock()
aqt.mw.col = MagicMock()

# Setup logging
logging.basicConfig(level=logging.INFO)
root_logger = logging.getLogger()
# Ensure child loggers also log to stdout
for handler in root_logger.handlers:
    root_logger.removeHandler(handler)
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter('%(levelname)s:%(name)s:%(message)s'))
root_logger.addHandler(handler)

from superfreetss_addon import superfreetss
from superfreetss_addon import component_configuration
from superfreetss_addon import constants

# Initialize SuperFreeTTS
from superfreetss_addon import servicemanager
services_dir = os.path.join(addon_path, "superfreetss_addon", "services")
sm = servicemanager.ServiceManager(services_dir, "superfreetss_addon.services", False)
sf = superfreetss.SuperFreeTTS(anki_utils, sm)
sf.service_manager.init_services()
sf.service_manager.instantiate_all_services(instantiate_expensive=True)

print("\n--- Testing ServiceManager.get_all_services() ---")
services = sf.service_manager.get_all_services()
print(f"Total services found: {len(services)}")
for s in services:
    print(f"Service: {s.name:15} | Fee: {s.service_fee} | Type: {s.service_type}")

print("\n--- Simulating ComponentConfiguration.get_service_list() ---")
# Manually simulate the filter logic
service_list = [s for s in services if s.service_fee == constants.ServiceFee.free]
print(f"Filtered (Free) services: {[s.name for s in service_list]}")

print("\n--- Simulating Category Splitting ---")
tts_services = [s for s in service_list if s.service_type == constants.ServiceType.tts]
dict_services = [s for s in service_list if s.service_type == constants.ServiceType.dictionary]
print(f"TTS Services: {[s.name for s in tts_services]}")
print(f"Dict Services: {[s.name for s in dict_services]}")

if "EdgeTTS" not in [s.name for s in tts_services]:
    print("\n[FAIL] EdgeTTS is MISSING from TTS services!")
    # Check why
    edge = next((s for s in services if s.name == "EdgeTTS"), None)
    if edge:
        print(f"EdgeTTS Fee: {edge.service_fee} (Expected: {constants.ServiceFee.free})")
        print(f"EdgeTTS Type: {edge.service_type} (Expected: {constants.ServiceType.tts})")
        print(f"Fee comparison: {edge.service_fee == constants.ServiceFee.free}")
        print(f"Type comparison: {edge.service_type == constants.ServiceType.tts}")
    else:
        print("EdgeTTS was not found in ALL services.")
else:
    print("\n[SUCCESS] EdgeTTS is present in TTS services list.")
