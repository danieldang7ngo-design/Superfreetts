import pytest

from superfreetts_addon import component_batch, component_batch_preview


@pytest.mark.unit
def test_rerun_failed_notes_opens_new_batch_dialog(monkeypatch):
    preview = object.__new__(component_batch_preview.BatchPreview)
    preview.batch_model = object()
    preview.hypertts = object()
    preview.dialog = object()

    opened = {}

    def fake_open_batch_dialog_for_model(hypertts, note_ids, batch_model):
        opened['hypertts'] = hypertts
        opened['note_ids'] = note_ids
        opened['batch_model'] = batch_model

    monkeypatch.setattr(component_batch, 'open_batch_dialog_for_model', fake_open_batch_dialog_for_model)

    preview.rerun_failed_notes([101, 102])

    assert opened['note_ids'] == [101, 102]
    assert opened['batch_model'] is not None
