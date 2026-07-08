# SuperFreeTTS — API Index

Class/method reference. Read `AGENTS.md` first for rules/tasks/folder map.

## 1. Core Classes & Facades

### `SuperFreeTTS` — `superfreetts_addon/superfreetts.py`
Central facade, wires all managers, exposes unified API to UI.
Deps: `ConfigStore`, `AudioFileStore`, `RealtimeManager`, `BatchOrchestrator`,
`AudioGenerator`, `EditorManager`, `MultiEngineExecutor`.
- `process_batch_audio(note_ids, batch_config, batch_status, col)` — orchestrates batch prep/generate/save.
- `generate_audio_write_file(source_text, voice_id, options, ctx)` — generates + caches one file.
- `get_audio_file(processed_text, voice_selection, ctx)` — finds/generates audio, handles priority fallback.
- `process_note_audio(batch, note, add_mode, ctx, ...)` — generates audio + writes field tag for one note.
- `apply_generated_batch_audio_chunk(generated_results_chunk, batch, batch_status, anki_collection) -> int` — chunked counterpart, does not reset progress counters (caller sets once before first chunk).
- `play_sound(source_text, voice_id, options)` — generate + play instantly.
- `cleanup_user_files()` — deletes cached audio past TTL.

### `ConfigStore` — `superfreetts_addon/config_store.py`
Reads/writes Anki profile config, handles migrations. Deps: `config_models.py`, `AnkiUtils`.
- `get_preset_list() -> List[BatchConfig]`
- `save_preset(preset_id, preset_model)`
- `get_preferences() -> Preferences` / `save_preferences(prefs)`
- `load_mapping_rules() -> PresetMappingRules`
- `perform_config_migration()`

### `ServiceManager` — `superfreetts_addon/servicemanager.py`
Lazy registration/instantiation/caching of TTS services. Deps: `ServiceBase`, `VoiceListCache`.
- `init_services()` — registers discovered service types.
- `instantiate_service_lazy(service_name) -> ServiceBase`
- `get_tts_audio(source_text, voice, options, ctx) -> bytes`
- `get_tts_audio_batch(source_texts, voice, options) -> List[Optional[bytes]]`
- `full_voice_list(service_name) -> List[TtsVoice_v3]` — cache first, then service query.
- `locate_voice(voice_id) -> Optional[TtsVoice_v3]`

### `ServiceBase` (ABC) — `superfreetts_addon/service.py`
Contract for concrete TTS engines.
- `service_type: ServiceType` (abstract)
- `service_fee: ServiceFee` (abstract — must be `free` to load, see `AGENTS.md` rule 6)
- `voice_list() -> List[TtsVoice_v3]` (abstract)
- `get_tts_audio(source_text, voice, options) -> bytes` (abstract)
- `get_tts_audio_batch(...)` — default loops `get_tts_audio()`; override for native batch APIs.

## 2. Domain Managers

### `BatchOrchestrator` — `superfreetts_addon/batch_orchestrator.py`
Batch pipeline: prepare → dedup → generate → save. Deps: `AnkiUtils`,
`MultiEngineExecutor`, `BatchStatus`, `AudioFileStore`, `SourceTextResolver`, `NoteAudioUpdater`.
- `prepare_batch_audio_generation(note_ids, batch, batch_status) -> dict`
- `generate_prepared_batch_audio(prepared_batch, batch_status) -> List[tuple]`
- `apply_generated_batch_audio(generated_results, batch, batch_status, col)` — writes tags, commits in one transaction.
- `apply_generated_batch_audio_chunk(generated_results_chunk, batch, batch_status, anki_collection) -> int` — chunked counterpart, does not reset progress counters (caller sets once before first chunk).
- `_execute_unique_tasks_unified(tasks, dedup_map, batch_status) -> Dict`

### `AudioGenerator` — `superfreetts_addon/audio_generator.py`
Single-note generation, voice selection/fallback. Deps: `ServiceManager`,
`AudioFileStore`, `NoteAudioUpdater`, `SourceTextResolver`.
- `choose_voice(voice_selection, voice_list, sequence_index) -> VoiceWithOptions` (single/random/priority/sequence modes)
- `generate_audio_write_file(source_text, voice_id, voice_options, ctx) -> Tuple[str, str]`
- `get_audio_file(processed_text, voice_selection, ctx) -> Tuple[str, str]` — falls back to alt voices on failure.
- `process_note_audio(batch, note, add_mode, ctx, ...)`

### `RealtimeManager` — `superfreetts_addon/realtime_manager.py`
`{{tts}}` tag injection/extraction/playback. Deps: `ConfigStore`, `AudioGenerator`, `AnkiUtils`.
- `get_realtime_audio(realtime_model, text) -> Tuple[str, str]`
- `get_audio_filename_tts_tag(tts_tag) -> Tuple[str, str]`
- `persist_realtime_config_update_note_type(...)`

### `EditorManager` — `superfreetts_addon/editor_manager.py`
Bridges note editor with TTS actions. Deps: `AudioGenerator`, `AnkiUtils`, `ConfigStore`.
- `editor_note_add_audio(batch, editor_context, text_input)`
- `apply_all_mapping_rules(editor_context, rules)`
- `preview_note_audio_editor(batch, editor_context)` — plays without modifying fields.

## 3. Concurrency & Execution

### `MultiEngineExecutor` — `superfreetts_addon/batch_executor.py`
Per-engine thread pools. Deps: `BoundedThreadPoolExecutor`.
- `get_executor(service_name) -> BoundedThreadPoolExecutor`
- `shutdown()`

### `BoundedThreadPoolExecutor` — `superfreetts_addon/batch_executor.py`
`ThreadPoolExecutor` wrapper with a semaphore-capped queue.

### `SherpaProcessPool` — `superfreetts_addon/services/service_mms.py`
Persistent subprocess pool for CPU-heavy engines (Piper/Kokoro/MMS), JSON IPC over stdin/stdout.
- `submit(request_dict) -> dict`
- `shutdown()`

## 4. Key Helpers

### `AnkiUtils` — `superfreetts_addon/anki_utils.py`
Isolates all `anki`/`aqt` API calls for testability.
- `get_note_by_id(note_id) -> Note`
- `update_notes(notes) -> int`
- `media_add_file(path) -> str`
- `run_in_background(task_fn, task_done_fn)`
- `run_on_main(task_fn)`
- `play_sound(filename)`

### `AudioFileStore` — `superfreetts_addon/audio_file_store.py`
Content-addressed disk cache.
- `build_request_key(processed_text, voice_id, voice_options) -> AudioRequestKey` (SHA-224)
- `get_cached_file(request_key) -> Optional[AudioFileResult]`
- `write_audio_file_atomic(request_key, audio_data) -> AudioFileResult`

### `BatchStatus` — `superfreetts_addon/batch_status.py`
Tracks state (Loading/Preparing/Deduplicating/Generating/Saving) + progress, notifies GUI listeners.

## 5. Services — Full List

### TTS engines (`service_fee = free`, loaded)
`service_edgetts.py`, `service_piper.py`, `service_kokoro.py`, `service_mms.py`,
`service_googletranslate.py`, `service_windows.py` (Windows SAPI, Windows only),
`service_macos.py` (macOS only), `service_espeakng.py`, `service_supertonic.py`.

### Dictionary services (`service_type = dictionary`, free, pronunciation lookups)
`service_cambridge.py`, `service_oxford.py`, `service_duden.py`, `service_dwds.py`,
`service_youdao.py`, `service_spanishdict.py`.

### Not loaded
`service_naver.py` — `service_fee = paid`, skipped by `ServiceManager`.
`service_onnx_general.py` (`OnnxGeneralTTS`) — currently disabled.

### Runners — NOT `ServiceBase` subclasses, don't confuse with services
Helper subprocess/inference wrappers used by the offline engines above:
`services/piper_runner.py`, `services/kokoro_runner.py`,
`services/sherpa_runner.py` / `sherpa_runner_v2.py` (Sherpa-ONNX, backs
MMS/Kokoro). Note: the shipped Piper engine currently drives inference via a
`piper.exe` subprocess inside `service_piper.py` itself, not `piper_runner.py`.

`services/voicelist.py` — static `VOICE_LIST` of paid voices, kept for reference only.

## 6. Module Index (`superfreetts_addon/*.py`)

Quick lookup for files not already covered in `AGENTS.md` or above:

| File | Responsibility |
|---|---|
| `batch_constants.py` | Worker caps, timeouts, GC constants |
| `batch_progress_ui.py` | Batch progress/status UI |
| `batch_state_manager.py` | Checkpoint/resume for batch jobs |
| `system_utils.py` | CPU/GPU detection, thread count calc |
| `performance_tracker.py` | Batch performance/latency tracking |
| `gui_utils.py` | GUI helper functions |
| `logging_utils.py` | `NullLogger`, `SentryLogger`, `SafeStreamHandler` |
| `constants.py` | Enums, paths, GUI strings, stylesheets |
| `voice.py` / `voice_cache.py` | Voice data models + persistent cache |
| `note_audio_updater.py` | Note field update helpers |
| `source_text_resolver.py` | Template expansion, text resolution |
| `text_utils.py` | HTML/cloze/bracket stripping |
| `engine_manager.py` / `mms_engine_manager.py` | Shared Python engine lifecycle (general / MMS-specific) |
| `sherpa_manager.py` | Sherpa-ONNX manager |
| `downloader.py` / `resource_manager.py` | Model file downloads, resource management |
| `job_pipeline.py` | Async job pipeline |
| `languages.py` | `AudioLanguage` enum |
| `options.py` | `AudioFormat` enum |
| `stats.py` | Usage stats |
| `performance_cache.py` | TTL cache |
| `preset_rules_status.py` | Preset rule status model |
| `service_logger.py` | Per-service log writer |
| `release_notes.py` | Release note loading |
| `context.py` | Action context helpers |
| `errors.py` | Exception hierarchy + `ErrorManager` |
| `tts_orchestrator.py` | Engine config, pool auto-scaling |
| `ttsplayer.py` | Realtime TTS player (see `AGENTS.md` §5) |
| `ui_controller.py` | UI orchestration |
| `utils_hf.py` | HuggingFace utils |

### UI components (`component_*.py`) — grouped

- **Batch**: `component_batch.py`, `component_batch_preview.py`
- **Settings**: `component_settings.py` (unified dialog), `component_services.py`,
  `component_preferences.py`
- **Engine setup**: `component_piper_setup.py` / `component_piper_manager.py`
  (HuggingFace voice downloads), `component_kokoro_manager.py`,
  `component_mms_manager.py`, `component_onnx_manager.py`,
  `component_supertonic_setup.py` / `component_supertonic_voice_manager.py`
- **Voice/realtime**: `component_voiceselection.py`, `component_realtime.py`,
  `component_realtime_source.py`, `component_realtime_side.py`
- **Mapping rules**: `component_presetmappingrules.py`, `component_mappingrule.py`,
  `component_choosepreset.py`
- **Note fields**: `component_source.py`, `component_target.py`,
  `component_text_processing.py`, `component_label_preview.py`
- **Misc/meta**: `component_about.py`, `component_shortcuts.py`,
  `component_common.py`, `component_changes.py`, `component_donation.py`,
  `component_failure_report.py`, `component_release_notes.py`,
  `component_troubleshooting.py`, `component_welcome.py`,
  `component_workflow.py`, `component_services_legacy.py`
