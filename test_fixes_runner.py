import sys
import os
from unittest.mock import MagicMock

# 1. Mock dependencies BEFORE importing anything from the package
def mock_modules(names):
    for name in names:
        m = MagicMock()
        if '.' not in name:
            m.__path__ = []
        sys.modules[name] = m

mock_modules([
    'aqt', 'aqt.qt', 'aqt.utils', 'aqt.operations', 'aqt.progress', 'aqt.addcards', 'aqt.browser', 'aqt.gui_hooks',
    'anki', 'anki.notes', 'anki.cards', 'anki.hooks', 'anki.media', 'anki.collection', 'anki.models', 'anki.utils',
    'soundfile', 'sherpa_onnx'
])

# 2. Add current directory to path so superfreetss_addon can be imported
sys.path.append(os.getcwd())

# 3. Import the test class (this will trigger __init__.py but with mocks in place)
from superfreetss_addon.test_fixes import TestFixes
import unittest

if __name__ == '__main__':
    unittest.main()
