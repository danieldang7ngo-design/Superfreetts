from aqt.qt import QRunnable

class LoadWorker(QRunnable):
    def __init__(self, offset, limit, callback):
        super().__init__()
        self.offset = offset
        self.limit = limit
        self.callback = callback

    def run(self):
        # DB access must happen inside run()
        from tools.notes_db import fetch_notes
        rows = fetch_notes(limit=self.limit, offset=self.offset)
        try:
            self.callback(rows)
        except Exception:
            # callback runs on main thread typically; ensure exceptions don't kill worker
            pass
