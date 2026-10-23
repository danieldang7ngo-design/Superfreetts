import copy
import os
import sys

import pytest

addon_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, addon_dir)

from superfreetts_addon import config_models
from superfreetts_addon import constants
from superfreetts_addon import context
from superfreetts_addon import superfreetts
from superfreetts_addon import voice
from tests.conftest import MockAnkiUtils


class DummyServiceManager:
    """Records batch calls and returns voice-tagged audio per call voice."""

    def __init__(self):
        self.batch_calls = []

    def locate_voice(self, voice_id):
        class DummyVoice:
            def __init__(self, voice_id):
                self.voice_id = voice_id

        return DummyVoice(voice_id)

    def get_tts_audio_batch(self, texts, located_voice, options):
        service = located_voice.voice_id.service
        key = located_voice.voice_id.voice_key
        self.batch_calls.append((service, key, list(texts)))
        return [f"audio:{key}:{text}".encode("utf-8") for text in texts]

    def get_tts_audio(self, source_text, located_voice, options, audio_request_context):
        key = located_voice.voice_id.service
        return f"audio:{key}:{source_text}".encode("utf-8")

    def full_voice_list(self):
        return []


class DummyAnkiUtils(MockAnkiUtils):
    def __init__(self, tmp_path):
        super().__init__()
        self._user_files_dir = str(tmp_path)

    def get_user_files_dir(self):
        return self._user_files_dir

    def media_add_file(self, full_filename):
        pass

    def run_on_main(self, fn):
        return fn()


def _make_batch(anki_utils):
    batch = config_models.BatchConfig(anki_utils)
    batch.name = "sequence-test"
    batch.target = config_models.BatchTarget(target_field="Sound")
    batch.source = config_models.BatchSource(mode=constants.BatchMode.simple, source_field="Front")
    batch.voice_selection = config_models.VoiceSelectionSequence()
    batch.voice_selection.add_voice(
        config_models.VoiceWithOptionsSequence(
            voice.TtsVoiceId_v3(voice_key="female_1", service="EdgeTTS"), {}
        )
    )
    batch.voice_selection.add_voice(
        config_models.VoiceWithOptionsSequence(
            voice.TtsVoiceId_v3(voice_key="male_1", service="EdgeTTS"), {}
        )
    )
    return batch


def _make_chunk(batch, texts):
    chunk = []
    for idx, text in enumerate(texts):
        chosen = batch.voice_selection.voice_list[idx % 2]
        task_data = {
            "note_id": idx + 1,
            "source_text": text,
            "processed_text": text,
            "batch": batch,
            "audio_request_context": context.AudioRequestContext(constants.AudioRequestReason.batch),
            "chosen_voice": chosen,
        }
        dedup_key = (text, chosen.voice_id)
        chunk.append((dedup_key, task_data, [idx]))
    return chunk


@pytest.mark.unit
def test_mixed_voice_chunk_generates_with_each_item_own_voice(tmp_path):
    """Sequence preset: alternating voices in one chunk must each be generated
    with their own voice, not the first item's voice for the whole chunk."""
    anki_utils = DummyAnkiUtils(tmp_path)
    service_manager = DummyServiceManager()
    hypertts = superfreetts.SuperFreeTTS(anki_utils, service_manager)
    batch = _make_batch(anki_utils)

    texts = [f"sentence number {i}" for i in range(6)]
    chunk = _make_chunk(batch, texts)

    results = hypertts._generate_audio_batch_task(chunk)

    assert len(results) == 6
    for i, (result, error) in enumerate(results):
        assert error is None, f"item {i} failed: {error}"
        assert result is not None
        source_text, processed_text, audio_filename, full_filename = result
        assert source_text == texts[i]
        expected_key = "female_1" if i % 2 == 0 else "male_1"
        assert open(full_filename, "rb").read() == f"audio:{expected_key}:{texts[i]}".encode("utf-8")

    # The service batch API takes one voice per call, so a mixed chunk must be
    # split: one call for female texts, one for male texts.
    assert len(service_manager.batch_calls) == 2
    by_voice = {key: called_texts for _, key, called_texts in service_manager.batch_calls}
    assert by_voice["female_1"] == [texts[0], texts[2], texts[4]]
    assert by_voice["male_1"] == [texts[1], texts[3], texts[5]]


@pytest.mark.unit
def test_single_voice_chunk_still_uses_one_batch_call(tmp_path):
    """Single-voice chunks keep the old efficient path: exactly one call."""
    anki_utils = DummyAnkiUtils(tmp_path)
    service_manager = DummyServiceManager()
    hypertts = superfreetts.SuperFreeTTS(anki_utils, service_manager)
    batch = _make_batch(anki_utils)

    texts = [f"other sentence {i}" for i in range(3)]
    chosen = batch.voice_selection.voice_list[0]
    chunk = []
    for idx, text in enumerate(texts):
        task_data = {
            "note_id": 100 + idx,
            "source_text": text,
            "processed_text": text,
            "batch": batch,
            "audio_request_context": context.AudioRequestContext(constants.AudioRequestReason.batch),
            "chosen_voice": chosen,
        }
        chunk.append(((text, chosen.voice_id), task_data, [idx]))

    results = hypertts._generate_audio_batch_task(chunk)

    assert len(results) == 3
    assert all(error is None for _, error in results)
    assert len(service_manager.batch_calls) == 1
    service, key, called_texts = service_manager.batch_calls[0]
    assert key == "female_1"
    assert called_texts == texts


@pytest.mark.unit
def test_rerun_after_fix_reads_correct_cached_audio(tmp_path):
    """Regression for the poisoned-cache symptom: after a correct batch, a
    second run (all cache hits) must return each note's own voice audio."""
    anki_utils = DummyAnkiUtils(tmp_path)
    service_manager = DummyServiceManager()
    hypertts = superfreetts.SuperFreeTTS(anki_utils, service_manager)
    batch = _make_batch(anki_utils)

    texts = [f"rerun sentence {i}" for i in range(4)]
    chunk = _make_chunk(batch, texts)
    first = hypertts._generate_audio_batch_task(chunk)
    assert all(error is None for _, error in first)

    calls_after_first = len(service_manager.batch_calls)

    # Second run with fresh task dicts (simulates re-running the batch): every
    # item must be served from cache with no new service calls.
    chunk2 = _make_chunk(batch, texts)
    second = hypertts._generate_audio_batch_task(chunk2)

    assert len(service_manager.batch_calls) == calls_after_first
    for i, (result, error) in enumerate(second):
        assert error is None
        expected_key = "female_1" if i % 2 == 0 else "male_1"
        assert result[0] == texts[i]
        assert open(result[3], "rb").read() == f"audio:{expected_key}:{texts[i]}".encode("utf-8")


@pytest.mark.unit
def test_batch_task_voice_key_splits_voice_and_options():
    female = config_models.VoiceWithOptionsSequence(
        voice.TtsVoiceId_v3(voice_key="female_1", service="EdgeTTS"), {}
    )
    male = config_models.VoiceWithOptionsSequence(
        voice.TtsVoiceId_v3(voice_key="male_1", service="EdgeTTS"), {}
    )
    female_loud = config_models.VoiceWithOptionsSequence(
        voice.TtsVoiceId_v3(voice_key="female_1", service="EdgeTTS"), {"rate": "+10%"}
    )
    key = superfreetts.SuperFreeTTS._batch_task_voice_key
    assert key(female) == key(copy.copy(female))
    assert key(female) != key(male)
    assert key(female) != key(female_loud)
