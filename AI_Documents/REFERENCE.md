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
`gui.py` `setup_editor_buttons()`. Other Lucide icons: `icon_chevron_down`/
`icon_chevron_right` (Advanced/collapse toggles in `component_services.py`,
`component_realtime_side.py`), `icon_headphones` (AnkiVN Settings menu action,
`gui.py`). No runtime dependency — icons are static SVGs loaded via
`gui_utils.get_graphics_path()`.
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

| Purpose | Vendored libs |
|---------|--------------|
| EdgeTTS | `edge_tts`, `edge_playback`, `aiohttp` + deps (`aiohappyeyeballs`, `aiosignal`, `frozenlist`, `multidict`, `propcache`, `yarl`, `attrs`) |
| Google TTS | `gtts`, `click` |
| Windows SAPI | `comtypes`, `win32com` helpers |
| eSpeak-ng | `espeakng` |
| HTTP/general | `requests==2.32.4`, `urllib3==2.5.0`, `certifi==2025.7.9`, `idna==3.10`, `charset-normalizer==3.4.2`, `tabulate`, `typing_extensions` |
| Helpers | `python-dateutil`, `databind`, `Deprecated`, `nr`, `six`, `typeapi`, `wrapt` |

`psutil` and compiled/C-extension binaries are deliberately **not** vendored.
`requirements-vendor.txt` is the version record for the repaired packages;
`python scripts/vendor_deps.py --check` verifies metadata and module versions.

## 5. Test Suite

```powershell
python -m pytest tests/ -q --tb=short                  # all (420 passed, ~6s)
python -m pytest tests/test_batch_cache_dedup.py -v     # single file
python -m pytest tests/ -q --cov=superfreetts_addon --cov-report=json:coverage.json
python scripts/check_critical_coverage.py coverage.json
```

CI (`.github/workflows/python-test.yml`) runs Ruff, Bandit (`-ll`), Python
3.9/3.11/3.13/3.14, Windows/macOS smoke tests, the coverage floor, the
critical-module 70% gate, and package build/import verification. The test
suite uses `conftest.py` → `mock_anki.mock_all()`; no Anki install is needed.
Runner modules are import-smoke-tested without loading their heavy runtime
dependencies. `rtk pytest` swallows stdout on Windows; use `python -m pytest`
directly.

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
| `batch_state_manager.py` | DEPRECATED — unused; live checkpoint is `batch_executor.CheckpointManager` |
| `services/process_pool.py` | Local-engine process pool, IPC deadlines, kill/retry |
| `system_utils.py` | CPU detection, available-RAM detection, thread budget |
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
| `download_sources.py` | Pinned URLs, sizes and integrity fingerprints |
| `http_utils.py` | Shared HTTP timeout / `AudioNotFoundError` mapping |
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
