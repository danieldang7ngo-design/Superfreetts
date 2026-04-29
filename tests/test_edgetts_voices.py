import sys
import os

addon_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, addon_dir)
sys.path.insert(0, os.path.join(addon_dir, 'external'))

from tests import mock_anki

mock_anki.mock_all()

import superfreetss_addon.servicemanager as servicemanager

def main():
    services_dir = os.path.join(addon_dir, 'superfreetss_addon', 'services')
    sm = servicemanager.ServiceManager(services_dir, 'superfreetss_addon.services', False)
    sm.init_services()
    sm.instantiate_service_lazy('EdgeTTS')
    
    edge_service = sm.services.get('EdgeTTS')
    if not edge_service:
        print("EdgeTTS service not instantiated!")
        return

    print(f"EdgeTTS enabled status: {edge_service.enabled}")
    
    print("Fetching voices...")
    # This will exercise run_async_safe and edge_tts module
    voices = edge_service.voice_list()
    print(f"Found {len(voices)} voices for EdgeTTS.")
    if len(voices) == 0:
        print("Voices failed to fetch! It returned 0 length.")
    else:
        print("Voices fetched successfully!")

if __name__ == '__main__':
    main()
