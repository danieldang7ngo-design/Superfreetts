# REFERENCE.md — Architecture, API, Deps, Tests

## 1. Architecture Layers

```
Anki UI (Qt/WebView) — Browser menu, Editor buttons, Player
  |  gui.py + component_*.py
  |  GUI / Dialog Layer
  |
  v  SuperFreeTTS (superfreetts.py) — Facade
 /|\
ConfigStore  BatchOrchestrator  AudioGenerator  Realtime  Editor
  |              |                   |          Manager   Manager
  v              v                   v
config_models  batch_executor    audio_file_store
                   |
              ServiceManager
                   |
            +------+------+------+
            v      v      v      v
         EdgeTTS  Piper  Kokoro  MMS …
```

## 2. Data Flows

### Batch
```
component_batch.py → SuperFreeTTS.process_batch_audio()
  → BatchOrchestrator
    Phase 1: extract field text (source_text_resolver), clean
             (text_utils), resolve voice (audio_generator)
    Phase 2: dedup by (text+voice+format)
    Phase 3: submit to MultiEngineExecutor → check audio_file_store
             → miss: service.get_tts_audio_batch()
    Phase 4: write [sound:...] tags, commit chunks
```
### Editor "Add Audio"
```
Speaker icon → AudioGenerator.process_note_audio()
  → resolve text, select voice, check cache/generate → write tag
```
Editor button icons (`icon_speaker`, `icon_play`, `icon_settings`) live in
`graphics/` and are Lucide SVGs (ISC license, attribution in `graphics/NOTICE`).
Registered in `constants.py` (`GRAPHICS_ICON_*`), wired to buttons in
`gui.py` `setup_editor_buttons()`.
### Realtime Card Review
```
{{tts superfreetts_preset=X}} → RealtimeManager.get_audio_filename_tts_tag()
  → parse preset, fetch config, AudioGenerator.get_audio_file()
```

## 3. Concurrency
- `MultiEngineExecutor` routes to per-engine thread pools (EdgeTTS/Piper/Kokoro/MMS)
- EdgeTTS pool: `EDGETTS_MAX_WORKERS=3`, uses `asyncio.run()+asyncio.gather()`
- Local neural engines: `SherpaProcessPool` (persistent subprocess, JSON stdin/stdout)
- `BoundedThreadPoolExecutor`: semaphore-capped queue
- `SimpleResourceMonitor`: GC trigger on RAM threshold

## 4. Vendored Deps (`external/`)

| Engine | Libs |
|--------|------|
| EdgeTTS | `edge_tts`, `edge_playback`, `aiohttp`+deps (`aiosignal`, `frozenlist`, `multidict`, `yarl`, `attrs`), `psutil` |
| Google TTS | `gtts`, `click` |
| Windows SAPI | `comtypes` |
| eSpeak-ng | `espeakng` |
| General | `requests`, `urllib3`, `certifi`, `tabulate`, `cachetools`, `typing_extensions` |

~15-20 MB total. Safe to strip: `*.dist-info/`, `__pycache__/`, test files.

## 5. Test Suite

```powershell
python -m pytest tests/ -v --tb=short                  # all (~200)
python -m pytest tests/test_batch_cache_dedup.py -v     # single file
```

Skip files that run real TTS at import + `sys.exit()` (crash pytest):
`test_edgetts_sequence_mode.py`, `test_edgetts_vietnamese_batch.py`,
`test_edgetts_direct.py`, `test_edgetts_discovery.py`, `test_edgetts_voices.py`,
`test_edge.py`, `test_async.py`, `test_edgetts_continuous_batching.py`,
`test_performance_integration.py`, `test_psutil_integration.py`,
`test_debug_mode.py` (included in quick suite, passes when `FORCE_DEBUG_MODE=False`).

`conftest.py` calls `mock_anki.mock_all()` — no Anki install needed.
`rtk pytest` swallows stdout on Windows; use `python -m pytest` directly.

## 6. API Index (core classes, 1-line)

| Class | File | Purpose |
|-------|------|---------|
| `SuperFreeTTS` | `superfreetts.py` | Central facade, wires all managers |
| `ConfigStore` | `config_store.py` | Read/write Anki profile config + migrations |
| `ServiceManager` | `servicemanager.py` | Lazy-load TTS engines |
| `ServiceBase` (ABC) | `service.py` | Contract for all TTS engines |
| `BatchOrchestrator` | `batch_orchestrator.py` | Batch pipeline: prepare→dedup→generate→save |
| `AudioGenerator` | `audio_generator.py` | Single-note generation, voice fallback |
| `RealtimeManager` | `realtime_manager.py` | `{{tts}}` tag handling |
| `EditorManager` | `editor_manager.py` | Note editor ↔ TTS bridge |
| `MultiEngineExecutor` | `batch_executor.py` | Per-engine thread pool router |
| `AnkiUtils` | `anki_utils.py` | Isolates all anki/aqt API calls |
| `AudioFileStore` | `audio_file_store.py` | Content-addressed disk cache (SHA-224) |
| `BatchStatus` | `batch_status.py` | Batch state + progress, notifies GUI |

## 7. Module Index

| File | What |
|------|------|
| `batch_constants.py` | Worker caps, timeouts, GC |
| `batch_progress_ui.py` | Batch progress/status UI |
| `batch_state_manager.py` | Checkpoint/resume |
| `system_utils.py` | CPU/GPU detection |
| `performance_tracker.py` | Latency tracking |
| `logging_utils.py` | NullLogger, SentryLogger |
| `constants.py` | Enums, paths, stylesheets |
| `voice.py / voice_cache.py` | Voice models + cache |
| `note_audio_updater.py` | Note field update helpers |
| `source_text_resolver.py` | Template expansion |
| `text_utils.py` | HTML/cloze/bracket strip |
| `engine_manager.py` / `mms_engine_manager.py` | Engine lifecycle (general/MMS) |
| `sherpa_manager.py` | Sherpa-ONNX manager |
| `downloader.py / resource_manager.py` | Model downloads |
| `job_pipeline.py` | Async job pipeline |
| `languages.py` | AudioLanguage enum |
| `options.py` | AudioFormat enum |
| `errors.py` | Exception hierarchy + ErrorManager |
| `tts_orchestrator.py` | Engine config, pool scaling |
| `ttsplayer.py` | Realtime TTS player |
| `ui_controller.py` | UI orchestration |
| `release_notes.py` | Release notes |
| `version.py` | Version constant |

## 8. UI Components (`component_*.py`)

| Group | Files |
|-------|-------|
| Batch | `component_batch.py`, `component_batch_preview.py` |
| Settings | `component_settings.py`, `component_services.py`, `component_preferences.py` |
| Engine setup | `component_piper_setup.py`, `component_piper_manager.py`, `component_kokoro_manager.py`, `component_mms_manager.py`, `component_onnx_manager.py`, `component_supertonic_setup.py`, `component_supertonic_voice_manager.py` |
| Voice/realtime | `component_voiceselection.py`, `component_realtime.py`, `component_realtime_source.py`, `component_realtime_side.py` |
| Mapping | `component_presetmappingrules.py`, `component_mappingrule.py`, `component_choosepreset.py` |
| Note fields | `component_source.py`, `component_target.py`, `component_text_processing.py`, `component_label_preview.py` |
| Misc | `component_about.py`, `component_shortcuts.py`, `component_common.py`, `component_changes.py`, `component_donation.py`, `component_failure_report.py`, `component_release_notes.py`, `component_troubleshooting.py`, `component_welcome.py`, `component_workflow.py` |
