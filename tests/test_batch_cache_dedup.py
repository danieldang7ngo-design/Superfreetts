import os
import sys
import concurrent.futures
from unittest.mock import Mock

from tests import mock_anki
from tests.conftest import MockAnkiUtils

mock_anki.mock_all()

addon_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, addon_dir)
sys.path.insert(0, os.path.join(addon_dir, "external"))

from superfreetts_addon import config_models, constants, context, superfreetts, voice


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


class DummyServiceManager:
    def __init__(self):
        self.batch_calls = []
        self.single_calls = []

    def full_voice_list(self):
        return []

    def locate_voice(self, voice_id):
        located_voice = Mock()
        located_voice.voice_id = voice_id
        return located_voice

    def get_tts_audio_batch(self, source_texts, located_voice, voice_options):
        self.batch_calls.append((list(source_texts), located_voice.voice_id, dict(voice_options)))
        return [f"audio:{text}".encode("utf-8") for text in source_texts]

    def get_tts_audio(self, source_text, located_voice, voice_options, audio_request_context):
        self.single_calls.append((source_text, located_voice.voice_id, dict(voice_options)))
        return f"audio:{source_text}".encode("utf-8")


class DummyExecutor:
    def __init__(self):
        self.cached = []

    def cache_result(self, processed_text, voice_id, source_text, audio_filename, full_filename):
        self.cached.append((processed_text, voice_id, source_text, audio_filename, full_filename))


class DummyMonitor:
    def maybe_gc(self, items_processed):
        pass


class RecordingExecutorPool:
    def __init__(self, max_workers=2):
        self.submitted_chunks = []
        self.pool = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)

    def submit(self, fn, chunk):
        self.submitted_chunks.append(list(chunk))
        return self.pool.submit(fn, chunk)

    def shutdown(self):
        self.pool.shutdown(wait=True)


class ContinuousBatchExecutor:
    def __init__(self):
        self.pool = RecordingExecutorPool(max_workers=2)
        self.monitor = DummyMonitor()

    def detect_service(self, task):
        return task["chosen_voice"].voice_id.service

    def get_executor(self, service_name):
        return self.pool

    def cache_result(self, processed_text, voice_id, source_text, audio_filename, full_filename):
        pass


class DummyNoteActionContext:
    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        return False

    def set_source_text(self, source_text):
        pass

    def set_processed_text(self, processed_text):
        pass

    def set_sound(self, sound_file):
        pass

    def set_status(self, status):
        pass

    def set_error(self, exception):
        pass


class DummyBatchStatus:
    def __init__(self):
        self.must_continue = True
        self.futures_to_cancel = []
        self.unique_tasks_completed = 0
        self.messages = []

    def set_status_message(self, message):
        self.messages.append(message)

    def get_note_action_context(self, note_id, blank_fields):
        return DummyNoteActionContext()

    def notify_change(self, note_id):
        pass


def make_app(tmp_path):
    anki_utils = DummyAnkiUtils(tmp_path)
    service_manager = DummyServiceManager()
    app = superfreetts.SuperFreeTTS(anki_utils, service_manager)
    app.executor = DummyExecutor()
    return app, service_manager


def make_batch(selection_mode=constants.VoiceSelectionMode.single):
    batch = Mock()
    batch.voice_selection = Mock()
    batch.voice_selection.selection_mode = selection_mode
    return batch


def make_voice(name="Jenny", service="EdgeTTS", options=None):
    return config_models.VoiceWithOptions(
        voice.TtsVoiceId_v3(name, service),
        options or {},
    )


def make_task(note_id, text, voice_with_options, batch=None):
    return {
        "note_id": note_id,
        "source_text": text,
        "processed_text": text,
        "batch": batch or make_batch(),
        "audio_request_context": context.AudioRequestContext(constants.AudioRequestReason.batch),
        "chosen_voice": voice_with_options,
    }


def test_collect_batch_duplicates_groups_same_text_voice_and_options(tmp_path):
    app, _ = make_app(tmp_path)
    chosen_voice = make_voice(options={"speed": 1})
    tasks = [
        make_task(1, "hello", chosen_voice),
        make_task(2, "hello", chosen_voice),
    ]

    dedup_map = app._collect_batch_duplicates(tasks)

    assert len(dedup_map) == 1
    assert list(dedup_map.values()) == [[0, 1]]


def test_collect_batch_duplicates_separates_same_text_with_different_voice_options(tmp_path):
    app, _ = make_app(tmp_path)
    tasks = [
        make_task(1, "hello", make_voice(options={"speed": 1})),
        make_task(2, "hello", make_voice(options={"speed": 2})),
        make_task(3, "hello", make_voice(name="Guy", options={"speed": 1})),
    ]

    dedup_map = app._collect_batch_duplicates(tasks)

    assert len(dedup_map) == 3


def test_generate_audio_batch_task_calls_tts_once_for_deduped_text_voice_options(tmp_path):
    app, service_manager = make_app(tmp_path)
    chosen_voice = make_voice(options={"speed": 1})
    tasks = [
        make_task(1, "hello", chosen_voice),
        make_task(2, "hello", chosen_voice),
    ]
    dedup_map = app._collect_batch_duplicates(tasks)
    chunk = [(dedup_key, tasks[indexes[0]], indexes) for dedup_key, indexes in dedup_map.items()]

    results = app._generate_audio_batch_task(chunk)
    expanded = app._apply_batch_deduplication(tasks, dedup_map, {chunk[0][0]: results[0]}, Mock())

    assert len(results) == 1
    assert service_manager.batch_calls == [(["hello"], chosen_voice.voice_id, {"speed": 1})]
    assert [result[0] for result in expanded] == [1, 2]
    assert expanded[0][3] == expanded[1][3]


def test_generate_audio_batch_task_separates_same_text_with_different_options(tmp_path):
    app, service_manager = make_app(tmp_path)
    tasks = [
        make_task(1, "hello", make_voice(options={"speed": 1})),
        make_task(2, "hello", make_voice(options={"speed": 2})),
    ]
    dedup_map = app._collect_batch_duplicates(tasks)
    chunk = [(dedup_key, tasks[indexes[0]], indexes) for dedup_key, indexes in dedup_map.items()]

    results = app._generate_audio_batch_task(chunk)

    assert len(results) == 2
    # Same text with different voice options must be generated separately —
    # one service batch call per voice/options group, each with its own voice.
    # (A single mixed call would synth both items with the first item's voice
    # and store the wrong audio under the second item's cache key.)
    assert service_manager.batch_calls == [
        (["hello"], tasks[0]["chosen_voice"].voice_id, {"speed": 1}),
        (["hello"], tasks[1]["chosen_voice"].voice_id, {"speed": 2}),
    ]


def test_generate_audio_write_file_uses_disk_cache_without_service_call(tmp_path):
    app, service_manager = make_app(tmp_path)
    chosen_voice = make_voice()
    request_key = app.audio_store.build_request_key("hello", chosen_voice.voice_id, chosen_voice.options)
    cached = app.audio_store.write_audio_file_atomic(request_key, b"already-here")

    full_filename, audio_filename = app.generate_audio_write_file(
        "hello",
        chosen_voice.voice_id,
        chosen_voice.options,
        context.AudioRequestContext(constants.AudioRequestReason.batch),
    )

    assert full_filename == cached.full_filename
    assert audio_filename == cached.audio_filename
    assert service_manager.single_calls == []


def test_execute_unique_tasks_submits_offline_items_individually_for_continuous_batching(tmp_path):
    app, _ = make_app(tmp_path)
    app.executor = ContinuousBatchExecutor()
    chosen_voice = make_voice(service="PiperTTS")
    tasks = [
        make_task(1, "short", chosen_voice),
        make_task(2, "a much longer text", chosen_voice),
        make_task(3, "mid", chosen_voice),
    ]
    dedup_map = app._collect_batch_duplicates(tasks)

    def fake_generate_audio_batch_task(chunk):
        results = []
        for _, task_data, _ in chunk:
            note_id = task_data["note_id"]
            results.append((
                (
                    task_data["source_text"],
                    task_data["processed_text"],
                    f"{note_id}.mp3",
                    os.path.join(str(tmp_path), f"{note_id}.mp3"),
                ),
                None,
            ))
        return results

    app._generate_audio_batch_task = fake_generate_audio_batch_task

    audio_cache = app._execute_unique_tasks_unified(tasks, dedup_map, DummyBatchStatus())
    app.executor.pool.shutdown()

    assert sorted(len(chunk) for chunk in app.executor.pool.submitted_chunks) == [3]
    assert len(audio_cache) == 3


def test_execute_unique_tasks_serves_disk_cache_without_submitting(tmp_path):
    app, _ = make_app(tmp_path)
    app.executor = ContinuousBatchExecutor()
    app.usage_tracker = Mock()
    chosen_voice = make_voice()
    cached_text = "already synthesised"
    request_key = app.audio_store.build_request_key(
        cached_text, chosen_voice.voice_id, chosen_voice.options
    )
    cached = app.audio_store.write_audio_file_atomic(request_key, b"RIFF....WAVEfmt ")

    tasks = [
        make_task(1, cached_text, chosen_voice),
        make_task(2, "new text", chosen_voice),
    ]
    dedup_map = app._collect_batch_duplicates(tasks)
    submitted = []

    def fake_generate_audio_batch_task(chunk):
        results = []
        for _, task_data, _ in chunk:
            submitted.append(task_data["note_id"])
            results.append((
                (
                    task_data["source_text"],
                    task_data["processed_text"],
                    f"{task_data['note_id']}.mp3",
                    os.path.join(str(tmp_path), f"{task_data['note_id']}.mp3"),
                ),
                None,
            ))
        return results

    app._generate_audio_batch_task = fake_generate_audio_batch_task
    status = DummyBatchStatus()

    audio_cache = app._execute_unique_tasks_unified(tasks, dedup_map, status)
    app.executor.pool.shutdown()

    # The cached key never reaches an engine pool or a worker chunk.
    assert submitted == [2]
    assert len(audio_cache) == 2
    assert status.unique_tasks_completed == 2
    assert audio_cache[request_key][0][2] == cached.audio_filename
    app.usage_tracker.record_cache_hit.assert_called_once()


def test_execute_unique_tasks_chunks_by_processed_text_length(tmp_path):
    app, _ = make_app(tmp_path)
    app.executor = ContinuousBatchExecutor()
    chosen_voice = make_voice(service="PiperTTS")
    tasks = []
    for note_id in (1, 2):
        task = make_task(note_id, "x", chosen_voice)
        # The engine receives processed_text; chunk sizing must use it, not
        # the (here tiny) source text.
        task["processed_text"] = "y" * 2000 + str(note_id)
        tasks.append(task)
    dedup_map = app._collect_batch_duplicates(tasks)

    def fake_generate_audio_batch_task(chunk):
        return [
            (
                (
                    task_data["source_text"],
                    task_data["processed_text"],
                    f"{task_data['note_id']}.mp3",
                    os.path.join(str(tmp_path), f"{task_data['note_id']}.mp3"),
                ),
                None,
            )
            for _, task_data, _ in chunk
        ]

    app._generate_audio_batch_task = fake_generate_audio_batch_task

    audio_cache = app._execute_unique_tasks_unified(tasks, dedup_map, DummyBatchStatus())
    app.executor.pool.shutdown()

    # 2 x 2000 processed chars exceed the 3000-char chunk limit.
    assert sorted(len(chunk) for chunk in app.executor.pool.submitted_chunks) == [1, 1]
    assert len(audio_cache) == 2
