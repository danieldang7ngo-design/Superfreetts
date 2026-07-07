from aqt.qt import QAbstractListModel, QModelIndex, QThreadPool
from .worker import LoadWorker
from tools.notes_db import count_notes

try:
    pool = QThreadPool.globalInstance()
except Exception:
    pool = QThreadPool()

class NoteModel(QAbstractListModel):
    def __init__(self):
        super().__init__()
        self.rows = []
        self.total = count_notes()

    def rowCount(self, parent=None):
        return self.total

    def data(self, index, role):
        if index.row() >= len(self.rows):
            return "..."
        return self.rows[index.row()]

    def canFetchMore(self, parent):
        return len(self.rows) < self.total

    def fetchMore(self, parent):
        pool.start(LoadWorker(len(self.rows), 100, self.on_loaded))

    def on_loaded(self, new_rows):
        start = len(self.rows)
        end = start + len(new_rows) - 1
        if end < start:
            return
        self.beginInsertRows(QModelIndex(), start, end)
        self.rows.extend(new_rows)
        self.endInsertRows()
