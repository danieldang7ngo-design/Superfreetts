import sys
import os
import logging
from unittest.mock import MagicMock

# Setup path
addon_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(addon_path)

# Mock Anki stuff BEFORE importing superfreetts
import tests.mock_anki as mock_anki
mock_anki.mock_all()

from superfreetts_addon import superfreetts
from superfreetts_addon import constants
from superfreetts_addon import component_configuration

# Setup logging to stdout
logger = logging.getLogger()
logger.setLevel(logging.INFO)
for handler in logger.handlers[:]:
    logger.removeHandler(handler)
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter('%(levelname)s:%(name)s:%(message)s'))
logger.addHandler(handler)

class FakeAnkiUtils:
    def get_addon_instance_path(self): return addon_path
    def get_user_files_path(self): return os.path.join(addon_path, "user_files")
    def get_config(self): return {}
    def save_config(self, config): pass
    def get_uuid(self): return "1234"

anki_utils = FakeAnkiUtils()
sf = superfreetts.SuperFreeTTS(anki_utils)

print("\n--- Testing Service Discovery ---")
sf.service_manager.init_services()
sf.service_manager.instantiate_all_services(instantiate_expensive=True)

print("\n--- Testing get_service_list() Logic ---")
all_services = sf.service_manager.get_all_services()
print(f"Total services registered: {len(all_services)}")
for s in all_services:
    print(f"  - {s.name:15} | Fee: {s.service_fee} | Type: {s.service_type}")

print("\n--- Filtering Free Services ---")
free_services = [s for s in all_services if s.service_fee == constants.ServiceFee.free]
print(f"Free services found: {[s.name for s in free_services]}")

if "EdgeTTS" not in [s.name for s in free_services]:
    print("\n[FAIL] EdgeTTS is missing from Free services!")
    edge = next((s for s in all_services if s.name == "EdgeTTS"), None)
    if edge:
        print(f"EdgeTTS Fee type: {type(edge.service_fee)}")
        print(f"Constants Fee type: {type(constants.ServiceFee.free)}")
        print(f"Equality check (==): {edge.service_fee == constants.ServiceFee.free}")
        print(f"Identity check (is): {edge.service_fee is constants.ServiceFee.free}")
else:
    print("\n[SUCCESS] EdgeTTS is in the Free list.")

print("\n--- Checking Enabled State ---")
for s in free_services:
    enabled = sf.config.get_service_enabled(s.name)
    print(f"  - {s.name:15} | Enabled in config: {enabled}")
