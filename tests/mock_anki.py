import sys
import types
from unittest.mock import MagicMock

class MockModule(types.ModuleType):
    def __init__(self, name):
        super().__init__(name)
        self.__path__ = []

    def __getattr__(self, name):
        # Return a MagicMock for any missing attribute
        # But we must avoid infinite recursion for common special attributes
        if name.startswith('__'):
            raise AttributeError(name)
        return MagicMock()

def mock_all():
    sys._pytest_mode = True
    
    # Clean up existing anki/aqt mocks
    for m in list(sys.modules.keys()):
        if m.startswith('aqt') or m.startswith('anki'):
            del sys.modules[m]

    # Create root packages as MockModules
    aqt = MockModule('aqt')
    sys.modules['aqt'] = aqt
    
    anki = MockModule('anki')
    sys.modules['anki'] = anki
    
    # Create common submodules
    sub_names = [
        'aqt.qt', 'aqt.progress', 'aqt.addcards', 'aqt.operations', 'aqt.utils',
        'aqt.editor', 'aqt.gui_hooks', 'aqt.sound', 'aqt.browser', 'aqt.profiles',
        'aqt.deckconf', 'aqt.stats', 'aqt.import_export', 'aqt.addons', 'aqt.main',
        'aqt.tts', 'aqt.theme', 'aqt.webview', 'aqt.models',
        'anki.notes', 'anki.cards', 'anki.hooks', 'anki.utils', 'anki.errors', 'anki.sound',
        'anki.decks', 'anki.models', 'anki.sched', 'anki.collection', 'anki.storage'
    ]
    
    for name in sub_names:
        m = MockModule(name)
        sys.modules[name] = m
        # Link to parent
        parent_name, child_name = name.split('.')
        parent = sys.modules[parent_name]
        setattr(parent, child_name, m)

    # Special case: aqt.qt wildcard import support
    # QObject must be a type for subclassing to work
    
    # Create a base class that can accept arbitrary __init__ arguments
    class MockSignal:
        def emit(self, *args, **kwargs):
            pass
        
        def connect(self, *args, **kwargs):
            pass
    
    class MockQtBase:
        def __init__(self, *args, **kwargs):
            self.dataChanged = MockSignal()
        
        def beginResetModel(self):
            pass
        
        def endResetModel(self):
            pass
        
        def createIndex(self, row, col):
            return MagicMock()
        
        def columnCount(self, parent):
            return 0
    
    qt_classes = [
        'QObject', 'QWidget', 'QDialog', 'QVBoxLayout', 'QHBoxLayout', 'pyqtSignal', 'Qt', 'QApplication',
        'QAbstractTableModel', 'QAbstractListModel', 'QModelIndex', 'QListView', 'QTableView', 'QHeaderView',
        'QListWidgetItem', 'QTableWidgetItem', 'QAbstractItemView', 'QVariant', 'QSize', 'QRect', 'QPoint'
    ]
    for cls in qt_classes:
        if cls in ['pyqtSignal', 'Qt']:
            setattr(sys.modules['aqt.qt'], cls, MagicMock())
        else:
            setattr(sys.modules['aqt.qt'], cls, type(cls, (MockQtBase,), {}))
    
    # We must set __all__ for from aqt.qt import * to work
    sys.modules['aqt.qt'].__all__ = qt_classes
    
    # Setup mw with some expected nested attributes
    aqt.mw = MagicMock()
    aqt.mw.pm = MagicMock()
    aqt.mw.pm.meta = {}
    aqt.mw.addonManager = MagicMock()
    
    # Mock Note class for anki.notes
    class MockNote(dict):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.id = 0
            self.fields = list(self.keys())
        def flush(self): pass
        def note_type(self): return MagicMock()
    sys.modules['anki.notes'].Note = MockNote
