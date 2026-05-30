import sys
import os

# Setup path to include the addon directory
addon_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(addon_dir)

from tests.conftest import MockAnkiUtils
import superfreetts_addon.servicemanager as servicemanager

def main():
    services_dir = os.path.join(addon_dir, 'superfreetts_addon', 'services')
    sm = servicemanager.ServiceManager(services_dir, 'superfreetts_addon.services', False)
    
    # Simulate full startup
    sm.init_services()
    sm.instantiate_all_services(instantiate_expensive=True)
    
    print("Service Visibility Report:")
    print("-" * 30)
    for instance in sm.get_all_services():
        # Check if enabled (should be True for EdgeTTS now)
        print(f"Service: {instance.name:<20} | Enabled: {instance.enabled}")
    print("-" * 30)

if __name__ == '__main__':
    main()
