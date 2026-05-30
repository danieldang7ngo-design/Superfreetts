# Super Free TTS Project Analysis & AI Context

> **Note to AI Agents and Contributors:** This file provides a concise, high-level overview of the Super Free TTS Anki Add-on project. Read this first to quickly understand the architecture, data flow, and development guidelines before diving into the codebase.

## 1. Overview & Vision
**Super Free TTS** is a 100% free Anki add-on, forked from HyperTTS and maintained by Paul from AnkiVN. Its primary goal is to help users automatically generate text-to-speech (TTS) audio for their flashcards using only free resources.

**Key Values:**
- **Free:** Exclusively uses free TTS engines (EdgeTTS, Piper, Kokoro, MMS, Google Translate, Windows SAPI, macOS TTS, eSpeak-ng).
- **Stability & Performance:** Focuses on non-blocking UI, efficient caching, and reliable background batch processing.
- **Accessibility:** Offers simplified "Easy Mode" for beginners while retaining an advanced "Collection Mode" for power users.

## 2. Core Architecture
The project is built using **Python 3.x**, **PyQt5/PyQt6**, and bundles external requirements within the `external/` directory. 

### Key Components:
- **`superfreetts.py` (Core Logic):** Contains the `SuperFreeTTS` class handling text extraction, text processing (stripping HTML/cloze), audio generation with cache checks, and dynamic batch execution logic.
- **`batch_executor.py` (Async Execution):** Implements `UnifiedBatchExecutor` and `MultiEngineExecutor`. Uses a producer-consumer pattern with background threads to ensure non-blocking UI and interleaved audio generation.
- **`servicemanager.py` (Service Manager):** Handles runtime discovery and lazy-loading of TTS services. It ensures that TTS engines are only initialized when actually needed, preventing slow Anki startup times.
- **`gui.py` & `component_*.py` (UI Components):** Modular UI split into distinct components:
  - Unified settings dialog (`component_unified_settings.py`, `component_configuration.py`, `component_preferences.py`).
  - Batch/Collection Audio dialog (`component_batch.py`).
  - Easy Mode dialog (`component_easy.py`).
  - Realtime Configuration / Voice Selection / Rules dialogs.
- **`services/service_*.py` (TTS Engines):** Implementations of various TTS endpoints extending from `ServiceBase`. They enforce a `service_fee = free` requirement to be loaded. Paid services like Naver are skipped.

### Data Flow for Audio Generation:
1. The user triggers generation (via Easy Mode or Collection Mode).
2. `get_source_text()` extracts content.
3. `get_audio_file()` processes the extracted text and delegates generation to the `ServiceManager` or the new batch executor.
4. The generation utilizes a hashing mechanism for the `(source_text, voice_id, options)` tuple. If a file like `superfreetts-{hash}.mp3` already exists in `user_files/`, it uses the cache; otherwise, it hits the TTS engine asynchronously in the background. EdgeTTS is hard-capped at 3 concurrent workers to ensure stability.

## 3. Key Features & Functionality
- **Flexible UI Modes:** Easy Mode for single notes, Collection Mode for batch processing.
- **Preset Mapping Rules:** Automatically pre-selecting voices or presets based on Anki Deck or Note Type.
- **Realtime TTS:** Dynamically inserts an Anki tag `{{tts ...}}` to stream audio on the fly during review via `ttsplayer.py` instead of saving files.
- **Text Processing:** Tools to automatically clean text (e.g., HTML tags, brackets, cloze deletions) prior to TTS.
- **Localization (i18n):** User interface comes in both English and Ti?ng Vi?t (Vietnamese).

## 4. Development Roadmap Summary
- **Phase P0 & 1 (Completed):** Unified Settings UI & AnkiVN Menu integration. Multi-threading issues fixed, UI freezing reduced, and logging optimized.
- **Phase 2 & 3 (Completed):** UX, Configuration & Performance. Resolved overlap bugs in Preferences, implemented interleaved batch producer-consumer pattern, and added per-service concurrency capping (EdgeTTS limit).
- **Phase 4 & 5 (Completed/In Progress):** Project is fully cleaned (no cache/logs in release). Automated test suites integrated into `tests/`. Plans remain for advanced destination templates.

## 5. Guide for Contributors & AI Agents
If you wish to debug or expand the project, follow these technical guidelines:
- **Debugging:** You can force verbose logging via environment variables (`HYPER_TTS_DEBUG_LOGGING="enable"`).
- **Adding a new TTS Engine:** Create a `services/service_yourservice.py` file inheriting from `ServiceBase`. It must define `service_fee = constants.ServiceFee.free`. The `ServiceManager` will auto-discover and load it.
- **UI Modifications:** Modifying or adding UI windows should follow the component-based architecture inside `superfreetts_addon/`. Visual strings must leverage the localization file `i18n.py`.
- **Layout Bugs:** Be careful with PyQt layouts. Use `setMinimumHeight()` for `QLabel` widgets with `wordWrap=True` inside `QVBoxLayout` to prevent overlapping due to layout height squishing.
- **Performance Constraints:** Ensure no blocking operations persist on the main thread. Always wrap UI actions via `error_manager.get_single_action_context()`.
