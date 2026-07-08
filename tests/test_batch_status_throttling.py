from superfreetts_addon import batch_status


class DummyAnkiUtils:
    def get_current_time(self):
        return 0

    def report_unknown_exception_background(self, exc):
        pass


class DummyListener:
    def __init__(self):
        self.calls = []

    def batch_start(self):
        pass

    def batch_change(self, note_id, row, total_count, completed_count, start_time, current_time):
        self.calls.append((note_id, row, total_count, completed_count))

    def batch_end(self, completed):
        pass


def test_notify_change_is_throttled(monkeypatch):
    listener = DummyListener()
    status = batch_status.BatchStatus(DummyAnkiUtils(), [1, 2, 3], listener)
    status._change_notify_min_interval = 0.1

    times = iter([0.0, 0.05, 0.11, 0.12])
    monkeypatch.setattr(batch_status.time, "monotonic", lambda: next(times))

    status.notify_change(1)
    status.notify_change(2)
    status.notify_change(3)
    status.notify_change(1)

    assert len(listener.calls) == 2
    assert listener.calls[0][0] == 1
    assert listener.calls[1][0] == 3
