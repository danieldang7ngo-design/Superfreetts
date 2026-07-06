# SuperFreeTTS — API Index

This index catalogs the classes, methods, responsibilities, and dependencies of the SuperFreeTTS codebase.

---

## 1. Core Classes & Facades

### `SuperFreeTTS`
* **File**: [`superfreetts_addon/superfreetts.py`](file:///C:/AI/projects/Superfreetts/superfreetts_addon/superfreetts.py)
* **Responsibility**: Central facade of the application. Wires and orchestrates all managers. Exposes a unified API for the UI.
* **Dependencies**: `ConfigStore`, `AudioFileStore`, `RealtimeManager`, `BatchOrchestrator`, `AudioGenerator`, `EditorManager`, `MultiEngineExecutor`
* **Key Methods**:
  * `process_batch_audio(note_ids, batch_config, batch_status, col)`: Orchestrates preparation, generation, and note updates for a batch.
  * `generate_audio_write_file(source_text, voice_id, options, ctx)`: Generates and caches a single audio file.
  * `get_audio_file(processed_text, voice_selection, ctx)`: Finds/generates audio using a voice selection configuration, handling priority fallbacks.
  * `process_note_audio(batch, note, add_mode, ctx, ...)`: Generates audio and writes the field tag for a single note.
  * `play_sound(source_text, voice_id, options)`: Generates and plays audio instantly.
  * `cleanup_user_files()`: Deletes cached audio files older than the configured TTL.

### `ConfigStore`
* **File**: [`superfreetts_addon/config_store.py`](file:///C:/AI/projects/Superfreetts/superfreetts_addon/config_store.py)
* **Responsibility**: Reads and writes settings from/to Anki's profile configuration database. Handles configuration migrations.
* **Dependencies**: `config_models.py`, `AnkiUtils`
* **Key Methods**:
  * `get_preset_list() -> List[BatchConfig]`: Retrieves all saved presets.
  * `save_preset(preset_id, preset_model)`: Saves or updates a preset.
  * `get_preferences() -> Preferences`: Retrieves preferences object.
  * `save_preferences(prefs)`: Saves user preferences.
  * `load_mapping_rules() -> PresetMappingRules`: Retrieves preset mapping rules.
  * `perform_config_migration()`: Upgrades older config formats to the current version.

### `ServiceManager`
* **File**: [`superfreetts_addon/servicemanager.py`](file:///C:/AI/projects/Superfreetts/superfreetts_addon/servicemanager.py)
* **Responsibility**: Manages lazy registration, instantiation, configuration, and caching of TTS services.
* **Dependencies**: `ServiceBase`, `VoiceListCache`
* **Key Methods**:
  * `init_services()`: Registers all discovered service class types (lazy discovery).
  * `instantiate_service_lazy(service_name) -> ServiceBase`: Dynamically instantiates a service.
  * `get_tts_audio(source_text, voice, options, ctx) -> bytes`: Generates audio for a single request.
  * `get_tts_audio_batch(source_texts, voice, options) -> List[Optional[bytes]]`: Retrieves audio for multiple texts.
  * `full_voice_list(service_name) -> List[TtsVoice_v3]`: Resolves available voices (checks persistent cache, falls back to service query).
  * `locate_voice(voice_id) -> Optional[TtsVoice_v3]`: Locates a voice definition across all services.

### `ServiceBase` (Abstract Base Class)
* **File**: [`superfreetts_addon/service.py`](file:///C:/AI/projects/Superfreetts/superfreetts_addon/service.py)
* **Responsibility**: Abstract contract for concrete TTS service implementations.
* **Key Properties/Methods**:
  * `service_type: ServiceType` (Abstract): Dictates if the service is a local engine, API, or web service.
  * `service_fee: ServiceFee` (Abstract): Dictates if the service is free or paid.
  * `voice_list() -> List[TtsVoice_v3]` (Abstract): Returns supported voices.
  * `get_tts_audio(source_text, voice, options) -> bytes` (Abstract): Generates audio.
  * `get_tts_audio_batch(source_texts, voice, options) -> List[Optional[bytes]]`: Default loop calling `get_tts_audio()`. Concrete classes can override this for native batch APIs.

---

## 2. Domain Managers

### `BatchOrchestrator`
* **File**: [`superfreetts_addon/batch_orchestrator.py`](file:///C:/AI/projects/Superfreetts/superfreetts_addon/batch_orchestrator.py)
* **Responsibility**: Executes batch audio generation pipelines. Divides batch operations into distinct preparation, deduplication, generation, and saving phases.
* **Dependencies**: `AnkiUtils`, `MultiEngineExecutor`, `BatchStatus`, `AudioFileStore`, `SourceTextResolver`, `NoteAudioUpdater`
* **Key Methods**:
  * `prepare_batch_audio_generation(note_ids, batch, batch_status) -> dict`: Resolves note fields, applies text processing, selects voices, and outputs unique task structures.
  * `generate_prepared_batch_audio(prepared_batch, batch_status) -> List[tuple]`: Resolves duplicates and coordinates audio generation in background threads.
  * `apply_generated_batch_audio(generated_results, batch, batch_status, col)`: Writes sound tags to fields and commits notes to the Anki database in a single transaction.
  * `_execute_unique_tasks_unified(tasks, dedup_map, batch_status) -> Dict`: Dispatches chunks of work to per-engine thread pools and tracks completion status.

### `AudioGenerator`
* **File**: [`superfreetts_addon/audio_generator.py`](file:///C:/AI/projects/Superfreetts/superfreetts_addon/audio_generator.py)
* **Responsibility**: Manages audio generation, voice selection strategies, and fallback priorities for single notes.
* **Dependencies**: `ServiceManager`, `AudioFileStore`, `NoteAudioUpdater`, `SourceTextResolver`
* **Key Methods**:
  * `choose_voice(voice_selection, voice_list, sequence_index) -> VoiceWithOptions`: Selects a voice based on mode (single, random, priority, sequence).
  * `generate_audio_write_file(source_text, voice_id, voice_options, ctx) -> Tuple[str, str]`: Coordinates cache lookup and writes new audio to the disk cache.
  * `get_audio_file(processed_text, voice_selection, ctx) -> Tuple[str, str]`: Resolves audio, falling back to alternative voices if the primary voice generation fails.
  * `process_note_audio(batch, note, add_mode, ctx, ...)`: Resolves source text, generates audio, and updates note fields.

### `RealtimeManager`
* **File**: [`superfreetts_addon/realtime_manager.py`](file:///C:/AI/projects/Superfreetts/superfreetts_addon/realtime_manager.py)
* **Responsibility**: Manages the injection, extraction, and realtime playback of `{{tts}}` tags in card review templates.
* **Dependencies**: `ConfigStore`, `AudioGenerator`, `AnkiUtils`
* **Key Methods**:
  * `get_realtime_audio(realtime_model, text) -> Tuple[str, str]`: Generates or resolves card-review audio.
  * `get_audio_filename_tts_tag(tts_tag) -> Tuple[str, str]`: Extracts configuration presets from an Anki TTS tag and resolves its audio filename.
  * `persist_realtime_config_update_note_type(...)`: Updates note types and templates to match the realtime configuration.

### `EditorManager`
* **File**: [`superfreetts_addon/editor_manager.py`](file:///C:/AI/projects/Superfreetts/superfreetts_addon/editor_manager.py)
* **Responsibility**: Integrates TTS actions directly with the Anki card editor interface.
* **Dependencies**: `AudioGenerator`, `AnkiUtils`, `ConfigStore`
* **Key Methods**:
  * `editor_note_add_audio(batch, editor_context, text_input)`: Adds audio to the note currently open in the editor.
  * `apply_all_mapping_rules(editor_context, rules)`: Iterates through defined rules, executing matching presets.
  * `preview_note_audio_editor(batch, editor_context)`: Generates and plays audio for the active note without modifying the card fields.

---

## 3. Concurrency & Execution

### `MultiEngineExecutor`
* **File**: [`superfreetts_addon/batch_executor.py`](file:///C:/AI/projects/Superfreetts/superfreetts_addon/batch_executor.py)
* **Responsibility**: Manages individual thread pools per service engine to optimize resource usage and prevent network congestion or CPU overload.
* **Dependencies**: `BoundedThreadPoolExecutor`
* **Key Methods**:
  * `get_executor(service_name) -> BoundedThreadPoolExecutor`: Retrieves or creates a bounded thread pool dedicated to a specific service.
  * `shutdown()`: Closes all active thread pools.

### `BoundedThreadPoolExecutor`
* **File**: [`superfreetts_addon/batch_executor.py`](file:///C:/AI/projects/Superfreetts/superfreetts_addon/batch_executor.py)
* **Responsibility**: A custom wrapper around Python's standard `ThreadPoolExecutor` that utilizes a semaphore to cap queue size. Prevents excessive memory consumption during large batch runs.

### `SherpaProcessPool`
* **File**: [`superfreetts_addon/services/service_mms.py`](file:///C:/AI/projects/Superfreetts/superfreetts_addon/services/service_mms.py)
* **Responsibility**: Coordinates persistent subprocess pools for CPU-heavy neural network engines (Piper, Kokoro, MMS). Communication occurs via a line-based JSON IPC protocol over stdin/stdout.
* **Key Methods**:
  * `submit(request_dict) -> dict`: Dispatches a JSON command to an available runner subprocess and returns the response.
  * `shutdown()`: Terminates active subprocesses and cleans up resources.

---

## 4. Key Helpers & Utilities

### `AnkiUtils`
* **File**: [`superfreetts_addon/anki_utils.py`](file:///C:/AI/projects/Superfreetts/superfreetts_addon/anki_utils.py)
* **Responsibility**: Abstracts all interactions with `anki` and `aqt` APIs. Isolates dependencies to facilitate unit testing with mock frameworks.
* **Key Methods**:
  * `get_note_by_id(note_id) -> Note`: Retrieves a card note.
  * `update_notes(notes) -> int`: Persists modified notes to the database.
  * `media_add_file(path) -> str`: Places audio files into Anki's media collection.
  * `run_in_background(task_fn, task_done_fn)`: Dispatches tasks to Anki's background thread manager.
  * `run_on_main(task_fn)`: Safely Schedules UI updates to run on Qt's main thread.
  * `play_sound(filename)`: Plays an audio file via Anki's audio player.

### `AudioFileStore`
* **File**: [`superfreetts_addon/audio_file_store.py`](file:///C:/AI/projects/Superfreetts/superfreetts_addon/audio_file_store.py)
* **Responsibility**: A content-addressed cache store that reads and writes TTS audio files to the user's disk directory.
* **Key Methods**:
  * `build_request_key(processed_text, voice_id, voice_options) -> AudioRequestKey`: Compiles parameters and hashes them using SHA-224.
  * `get_cached_file(request_key) -> Optional[AudioFileResult]`: Returns details of a file if it already exists on disk.
  * `write_audio_file_atomic(request_key, audio_data) -> AudioFileResult`: Writes data to a temporary file, then performs an atomic replace operation to prevent file corruption.

### `BatchStatus`
* **File**: [`superfreetts_addon/batch_status.py`](file:///C:/AI/projects/Superfreetts/superfreetts_addon/batch_status.py)
* **Responsibility**: Tracks state transitions (Loading, Preparing, Deduplicating, Generating, Saving) and progress percentages of running batch operations. Notifies GUI listeners of status changes.
