import os
import sys
import tempfile
import copy
import pytest

addon_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, addon_dir)

from superfreetss_addon import superfreetss
from superfreetss_addon import config_models
from superfreetss_addon import voice
from superfreetss_addon import context
from superfreetss_addon import constants
from superfreetss_addon import errors
from tests.conftest import MockAnkiUtils


class DummyServiceManager:
    def __init__(self):
        self.calls = []

    def locate_voice(self, voice_id):
        class DummyVoice:
            def __init__(self, voice_id):
                self.voice_id = voice_id

        return DummyVoice(voice_id)

    def get_tts_audio_batch(self, missing_texts, voice, voice_options):
        self.calls.append(('batch', voice.voice_id.service, missing_texts))
        if voice.voice_id.service == 'CambridgeTTS':
            return [None for _ in missing_texts]
        return [b'fallback-audio' for _ in missing_texts]

    def get_tts_audio(self, source_text, voice, voice_options, audio_request_context):
        self.calls.append(('single', voice.voice_id.service, source_text))
        if voice.voice_id.service == 'CambridgeTTS':
            raise errors.AudioNotFoundError(source_text, voice)
        return b'fallback-audio'

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


@pytest.mark.unit
def test_batch_priority_fallback_uses_next_voice_if_first_voice_fails(tmp_path):
    anki_utils = DummyAnkiUtils(tmp_path)
    service_manager = DummyServiceManager()
    hypertts = superfreetss.SuperFreeTTS(anki_utils, service_manager)

    batch = config_models.BatchConfig(anki_utils)
    batch.name = 'priority-fallback-test'
    batch.target = config_models.BatchTarget(target_field='Sound')
    batch.source = config_models.BatchSource(mode=constants.BatchMode.simple, source_field='Front')
    batch.voice_selection = config_models.VoiceSelectionPriority()
    batch.voice_selection.add_voice(config_models.VoiceWithOptionsPriority(
        voice.TtsVoiceId_v3(voice_key='cambridge_1', service='CambridgeTTS'), {}
    ))
    batch.voice_selection.add_voice(config_models.VoiceWithOptionsPriority(
        voice.TtsVoiceId_v3(voice_key='edge_1', service='EdgeTTS'), {}
    ))

    source_text = 'hello world'
    processed_text = 'hello world'
    chosen_voice = batch.voice_selection.voice_list[0]
    task_data = {
        'note_id': 1,
        'source_text': source_text,
        'processed_text': processed_text,
        'batch': batch,
        'audio_request_context': context.AudioRequestContext(constants.AudioRequestReason.batch),
        'chosen_voice': chosen_voice,
        'priority_voice_list': copy.copy(batch.voice_selection.voice_list),
    }
    dedup_key = (processed_text, chosen_voice.voice_id)
    chunk = [(dedup_key, task_data, [0])]

    results = hypertts._generate_audio_batch_task(chunk)

    assert len(results) == 1
    result, error = results[0]
    assert error is None
    assert result is not None
    source_text_result, processed_text_result, audio_filename, full_filename = result
    assert source_text_result == source_text
    assert processed_text_result == processed_text
    assert os.path.exists(full_filename)
    assert b'fallback-audio' == open(full_filename, 'rb').read()
    assert ('batch', 'CambridgeTTS', [processed_text]) in service_manager.calls
    assert ('single', 'EdgeTTS', processed_text) in service_manager.calls
