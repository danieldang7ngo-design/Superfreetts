from aqt.qt import QListView, QTimer
from .model import NoteModel

def create_note_list_view(parent=None):
    view = QListView(parent)
    view.setModel(NoteModel())
    return view

def wire_search_box(search_box, run_search, delay_ms=250):
    timer = QTimer()
    timer.setSingleShot(True)
    timer.timeout.connect(run_search)
    # connect textChanged to restart timer
    search_box.textChanged.connect(lambda: timer.start(delay_ms))
    return timer
