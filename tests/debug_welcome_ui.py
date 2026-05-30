
import sys
import os

# Mock Anki environment
from unittest.mock import MagicMock

# Base directory
# Since this script is now in tests/, we need to go up one level
addon_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(addon_dir)

# Mock modules that might be imported
sys.modules['anki'] = MagicMock()
sys.modules['anki.hooks'] = MagicMock()
sys.modules['aqt'] = MagicMock()
sys.modules['aqt.gui_hooks'] = MagicMock()
sys.modules['anki.sound'] = MagicMock()

import aqt.qt
from aqt.qt import QApplication

# Mock aqt components
aqt.mw = MagicMock()

# Setup local mocks for the addon
from superfreetts_addon import component_welcome

class MockHyperTTS:
    def get_ui_language(self):
        return "vi"
    def get_configuration(self):
        config = MagicMock()
        config.display_introduction_message = True
        return config
    def save_configuration(self, config):
        print("Configuration saved!")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    hypertts = MockHyperTTS()
    dialog = component_welcome.WelcomeDialog(hypertts)
    dialog.show()
    
    sys.exit(app.exec())
