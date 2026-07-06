# Super Free TTS by Paul from AnkiVN - Project Documentation

> This document describes the Super Free TTS project in detail. For a quick overview of the architecture and AI Agent-specific guidelines, please read [AI_SUMMARY.md](./AI_SUMMARY.md).

## Table of Contents

- [Overview](#overview)
- [Technologies Used](#technologies-used)
- [Project Architecture](#project-architecture)
- [Usage Guide](#usage-guide)
- [Development Guide](#development-guide)
- [Multi-Language UI](#multi-language-ui)
- [License](#license)
- [Contact & Support](#contact--support)

---

## Overview

### What is this project?

**Super Free TTS** is a **100% FREE** add-on (extension) for [Anki](https://apps.ankiweb.net/) - a popular flashcard learning application. This add-on is **forked from the HyperTTS project** and continues to be developed to serve the community.

**Author**: Paul from AnkiVN

### What problem does it solve?

When learning a language or any subject that requires pronunciation, having audio on flashcards is crucial. However, recording audio manually or finding audio files for each card is very time-consuming. Super Free TTS solves this problem by:

- **Automatically generating audio** from text on flashcards.
- **Supporting multiple FREE TTS engines**: EdgeTTS, Piper (offline), Kokoro (offline), MMS (offline, 1100+ languages), Google Translate, Windows SAPI, macOS TTS, eSpeak-ng.
- **Flexibility**: Add audio to a single card or in bulk (batch); preset mapping rules; real-time TTS.
- **100% Free**: Only loads free engines, no API keys required.

### Information

- **Add-on name**: Super Free TTS
- **Author**: Paul from AnkiVN
- **Current version**: 1.4 (in `version.py`)
- **Website**: ankivn.com
- **Anki compatibility**: `min_point_version: 5`, `max_point_version: 241100` (meta.json)

---

## Technologies Used

### Programming Languages

- **Python 3.x**: Main language of the project
- **PyQt5/PyQt6**: Framework for creating the user interface (UI)
- **HTML/CSS/JavaScript**: Creating web interfaces in Anki's dialogs

### Main Libraries

#### Core Dependencies (in the `external/` folder)

1. **aiohttp (3.13.3)**: Asynchronous HTTP client/server for Python
   - Used to call APIs of TTS services.
2. **edge-tts (7.2.7)**: Python module to use Microsoft Edge TTS
   - High-quality free TTS service.
3. **gtts**: Google Text-to-Speech
   - Free TTS service from Google.
4. **requests**: Simple HTTP library
   - Calling APIs for free TTS services.
5. **tabulate (0.9.0)**: Creating clean data tables
   - Displaying voice lists.
6. **comtypes** (Windows only): COM interface
   - Integrated with Windows SAPI TTS.

### Supported TTS Services (ALL FREE)

The project only loads **TTS services with `service_fee = free`** (paid services like Naver are ignored during initialization).

#### Main TTS Engines (priority order in UI)
| Engine | Description | Online/Offline |
|--------|--------|-----------------|
| **EdgeTTS** | Microsoft Edge TTS (High quality) | Online |
| **PiperTTS** | Piper (Rhasspy) - Multi-language voices, .onnx models | Offline |
| **KokoroTTS** | Kokoro - Natural voices, runs via separate engine | Offline |
| **MmsTTS** | MMS (Massively Multilingual Speech) - 1100+ languages | Offline |
| **GoogleTranslate** | Google Translate TTS | Online |
| **Windows** | Windows SAPI (Windows only) | Offline |
| **MacOS** | macOS built-in TTS (macOS only) | Offline |
| **ESpeakNg** | eSpeak-ng, open-source | Offline |

#### Dictionary Services (pronunciation, `service_type = dictionary`)
- **Cambridge**, **Oxford**, **Duden**, **DWDS**, **Youdao**, **SpanishDict** - All free.
- **Naver**: In the code, it is marked as `service_fee = paid`, so it is **not loaded** in Super Free TTS.

#### Corresponding Service Files (in `services/`)
- `service_edgetts.py`, `service_piper.py`, `service_kokoro.py`, `service_mms.py`, `service_googletranslate.py`, `service_windows.py`, `service_macos.py`, `service_espeakng.py`, `service_supertonic.py`
- Dictionaries: `service_cambridge.py`, `service_oxford.py`, `service_duden.py`, `service_dwds.py`, `service_youdao.py`, `service_spanishdict.py`
- `service_naver.py` (paid - ignored). `service_onnx_general.py` (OnnxGeneralTTS) is currently disabled.

**Runner / helpers (not ServiceBase):** `piper_runner.py` (Piper via sherpa_onnx, JSON stdin/stdout), `kokoro_runner.py`, `sherpa_runner_v2.py` - used for offline inference (MMS/Kokoro). The main Piper engine in the add-on currently uses the `piper.exe` subprocess in `service_piper.py`.

---

## Project Architecture

### Directory Structure

```text
Superfreetts/                       # Root add-on folder (or number ID in addons21/)
+-- __init__.py                     # Entry point, sets up path and imports superfreetts_addon
+-- meta.json                       # Anki config, min/max version, add-on config
|
+-- superfreetts_addon/             # Main source code
|   +-- __init__.py                 # Setup logging, config, ServiceManager, SuperFreeTTS, gui.init
|   +-- superfreetts.py             # ⭐ CORE - SuperFreeTTS class: text extraction, process_batch_audio, presets
|   +-- batch_executor.py           # ⚡ ASYNC - UnifiedBatchExecutor & MultiEngineExecutor (Producer-Consumer pattern)
|   +-- batch_orchestrator.py       # Batch task preparation, execution, apply
|   +-- batch_constants.py          # Worker caps, timeouts, GC constants
|   +-- batch_progress_ui.py        # UI for batch progress and status
|   +-- batch_state_manager.py      # Checkpoint/resume for batch jobs
|   +-- batch_status.py             # Batch status model
|   +-- system_utils.py             # CPU/GPU detection, thread calculation
|   +-- performance_tracker.py      # Tracking batch performance & latency
|   +-- servicemanager.py           # TTS Service Management (lazy loading)
|   +-- anki_utils.py               # Anki API interaction
|   +-- gui.py                      # Menu and main UI actions
|   +-- gui_utils.py                # GUI helpers
|   +-- i18n.py                     # Internationalization (7 locales)
|   +-- logging_utils.py            # NullLogger, SentryLogger, SafeStreamHandler
|   +-- config_models.py            # Dataclass config models + migration
|   +-- config_store.py             # Config persistence layer
|   +-- constants.py                # Enums, paths, GUI strings, stylesheets
|   +-- voice.py                    # Voice data models + serialization
|   +-- voice_cache.py              # Persistent voice cache
|   +-- audio_file_store.py         # Audio file caching, hash-based filenames
|   +-- audio_generator.py          # Single-note audio generation
|   +-- note_audio_updater.py       # Note field update helpers
|   +-- editor_manager.py           # Anki editor bridge, mapping rules
|   +-- source_text_resolver.py     # Template expansion, text processing
|   +-- text_utils.py               # HTML strip, cloze strip, bracket strip
|   +-- engine_manager.py           # Shared Python engine management
|   +-- mms_engine_manager.py       # MMS-specific engine management
|   +-- sherpa_manager.py           # Sherpa ONNX manager
|   +-- downloader.py               # File downloads for model files
|   +-- resource_manager.py         # Manage downloadable resources
|   +-- job_pipeline.py             # Async job pipeline
|   +-- languages.py                # AudioLanguage enum
|   +-- options.py                  # AudioFormat enum
|   +-- stats.py                    # Usage stats
|   +-- performance_cache.py        # TTL cache
|   +-- preset_rules_status.py      # Preset rule status model
|   +-- service_logger.py           # Per-service log writer
|   +-- release_notes.py            # Release note loading
|   +-- context.py                  # Action context helpers
|   +-- errors.py                   # Exception hierarchy + ErrorManager
|   +-- service.py                  # ServiceBase abstract class
|   +-- tts_orchestrator.py         # Engine config, pool auto-scaling
|   +-- ttsplayer.py                # Realtime TTS player
|   +-- ui_controller.py            # UI orchestration
|   +-- utils_hf.py                 # HuggingFace utils
|   +-- version.py                  # Version constant
|   +-- services/                   # TTS & Dictionary engines
|   |   +-- service_edgetts.py      # EdgeTTS (online)
|   |   +-- service_piper.py        # Piper (offline, .onnx + .onnx.json, data/piper_models)
|   |   +-- service_kokoro.py       # Kokoro (offline, data/kokoro_engine)
|   |   +-- service_mms.py          # MMS (offline, 1100+ languages)
|   |   +-- service_googletranslate.py
|   |   +-- service_windows.py      # Windows SAPI
|   |   +-- service_macos.py
|   |   +-- service_espeakng.py
|   |   +-- service_cambridge.py, service_oxford.py, service_duden.py, service_dwds.py
|   |   +-- service_youdao.py, service_spanishdict.py
|   |   +-- service_naver.py        # Paid - Not loaded in Super Free TTS
|   |   +-- service_onnx_general.py # OnnxGeneralTTS (currently disabled)
|   |   +-- voicelist.py            # VOICE_LIST (paid voices, for reference)
|   |   +-- piper_runner.py         # Optional Piper runner (sherpa_onnx, stdin JSON)
|   |   +-- kokoro_runner.py        # Kokoro inference
|   |   +-- sherpa_runner.py / sherpa_runner_v2.py  # Sherpa-ONNX (MMS/Kokoro)
|   |   +-- __init__.py
|   |
|   +-- data/                       # Add-on data (created at runtime if needed)
|   |   +-- piper_models/           # Piper models (.onnx + .onnx.json) - default or configured
|   |   +-- piper_engine/           # Piper binary (after Setup Piper)
|   |   +-- kokoro_engine/          # Kokoro Python/env (if used)
|   |
|   +-- component_*.py              # UI components (multiple files)
|   |   +-- component_batch.py      # Add Audio (Collection), batch preview
|   |   +-- component_batch_preview.py
|   |   +-- component_settings.py   # Unified Settings dialog (Services + Preferences in QTabWidget)
|   |   +-- component_services.py   # Services Configuration (enable/disable, path Piper/Kokoro/MMS/Supertonic)
|   |   +-- component_piper_setup.py    # Setup Piper engine + Manage Voices
|   |   +-- component_piper_manager.py  # Piper: download voices from HuggingFace (voices.json)
|   |   +-- component_kokoro_manager.py # Kokoro: manage engine/voices
|   |   +-- component_mms_manager.py    # MMS: setup languages (1100+)
|   |   +-- component_onnx_manager.py   # ONNX models (if enabled)
|   |   +-- component_supertonic_setup.py   # Supertonic engine setup
|   |   +-- component_supertonic_voice_manager.py # Supertonic voice manager
|   |   +-- component_voiceselection.py # Select voice (single/random/priority)
|   |   +-- component_realtime.py   # Realtime TTS config
|   |   +-- component_realtime_source.py, component_realtime_side.py
|   |   +-- component_presetmappingrules.py, component_mappingrule.py
|   |   +-- component_choosepreset.py
|   |   +-- component_source.py
|   |   +-- component_target.py
|   |   +-- component_text_processing.py
|   |   +-- component_label_preview.py
|   |   +-- component_preferences.py   # Preferences (batch_concurrency, cache, UI language)
|   |   +-- component_about.py, component_shortcuts.py
|   |   +-- component_common.py
|   |   +-- component_changes.py, component_donation.py, component_failure_report.py
|   |   +-- component_release_notes.py, component_troubleshooting.py, component_welcome.py
|   |   +-- component_workflow.py, component_services_legacy.py
|   |
|   +-- external/                   # (if bundled) Libraries: aiohttp, edge_tts, requests, etc.
|
+-- external/                       # Third-party libraries (can be placed outside superfreetts_addon)
|   +-- aiohttp/, edge_tts/, gtts/, requests/, comtypes/, ...
|
+-- user_files/                     # Audio cache (hash-based: superfreetts-{hash}.mp3)
+-- UPGRADE_IDEAS.md                # Upgrade suggestions (currently: optimize add-on loading)
+-- PROJECT_DOCUMENTATION.md        # This document