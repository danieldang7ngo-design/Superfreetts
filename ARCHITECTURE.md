# SuperFreeTTS — Architecture

Anki addon for free TTS (EdgeTTS, Piper, Kokoro, MMS, and more).  
Addon install dir: `%APPDATA%\Anki2\addons21\351217314`

---

## 1. High-Level Architecture

SuperFreeTTS follows a layered architecture to separate GUI presentation, business logic, configuration management, and the underlying TTS engines.

```
┌─────────────────────────────────────────────────────────────────┐
│  Anki UI (Qt / WebView)                                         │
│  Browser menu, Editor buttons, Card review player               │
└────────────────────────┬────────────────────────────────────────┘
                         │ hooks / callbacks
┌────────────────────────▼────────────────────────────────────────┐
│  gui.py, component_batch, component_settings, etc.              │
│                    GUI / Dialog Layer                            │
└────────────────────────┬────────────────────────────────────────┘
                         │ method calls
┌────────────────────────▼────────────────────────────────────────┐
│              SuperFreeTTS  (superfreetts.py)                     │
│              Central Facade / Orchestrator                       │
└──┬──────────┬───────────┬────────────────┬───────────┬──────────┘
   │          │           │                │           │
   ▼          ▼           ▼                ▼           ▼
Config    Batch       Audio           Realtime    Editor
Store   Orchestrator Generator        Manager    Manager
   │          │           │
   ▼          ▼           ▼
config_   batch_      audio_file_
models   executor     store
              │
              ▼
       ServiceManager
              │
    ┌─────────┼──────────┐
    ▼         ▼          ▼
EdgeTTS   PiperTTS   Kokoro/MMS/etc.
```

The codebase is organized into four layers:

1. **Presentation Layer**: Handles Qt widgets, dialogs, menus, and hooks into Anki's editor and card reviewer.
2. **Facade Layer**: `SuperFreeTTS` acts as the single entry point. It wires all components together and delegates requests.
3. **Domain Layer**: Implements core business logic such as batch scheduling, text processing, voice selection, priority fallback, and realtime audio routing.
4. **Infrastructure Layer**: Provides service management, audio cache lookup, Anki database operations, process pool scheduling, and thread pools.

---

## 2. Module Responsibilities

### Facade & Orchestration
* **`superfreetts.py` (`SuperFreeTTS`)**: The primary orchestrator. Initialized during profile load, it instantiates and references all other managers. It exposes high-level actions to the GUI layer.
* **`anki_utils.py` (`AnkiUtils`)**: Wraps all Anki-specific APIs (media addition, note retrieval/updating, thread scheduling, undo actions, GUI messages) to isolate domain code and make unit testing possible without a running Anki instance.

### Domain Managers
* **`config_store.py` (`ConfigStore`)**: Single point of entry for reading/writing configuration (presets, preferences, mapping rules, realtime configurations) from/to Anki's profile configuration. Handles database migration.
* **`batch_orchestrator.py` (`BatchOrchestrator`)**: Coordinates the batch generation pipeline (Loading -> Preparing -> Deduplicating -> Generating -> Saving) in a background thread.
* **`audio_generator.py` (`AudioGenerator`)**: Handles audio generation for a single note. Performs voice selection (single, random, priority fallback, sequence) and requests audio from the ServiceManager.
* **`realtime_manager.py` (`RealtimeManager`)**: Manages the `{{tts}}` template tags. Renders ephemeral cards to extract tags and handles playback routing.
* **`editor_manager.py` (`EditorManager`)**: Bridges the Anki editor panel with TTS actions. Handles the mapping rules execution when the user triggers actions inside the note editor.

### Infrastructure & Services
* **`servicemanager.py` (`ServiceManager`)**: Responsible for service discovery, lazy instantiation of expensive local neural TTS engines, and caching voice lists.
* **`audio_file_store.py` (`AudioFileStore`)**: A content-addressed cache store on disk. It hashes voice and text properties using SHA-224 to locate or write audio files in the `user_files/` folder.
* **`batch_executor.py`**: Manages thread pools (`BoundedThreadPoolExecutor`), in-memory caches, memory monitoring/garbage collection, and checkpoint management for crash recovery.
* **`services/`**: Concrete adapters for external and local engines. Local Python/executable subprocesses (like Piper, Kokoro, MMS) are managed via a persistent IPC process pool (`SherpaProcessPool`).

---

## 3. Data Flows

### 3.1 Batch Audio Generation Flow

```
[User Action in Browser]
       │
       ▼
[component_batch.py (Qt Dialog)]
       │
       ▼
[SuperFreeTTS.process_batch_audio()]
       │
       ▼
[BatchOrchestrator.process_batch_audio()]
       │
       ├─► [Phase 1: Preparing]
       │     For each note:
       │       Extract field text via source_text_resolver
       │       Clean text via text_utils (HTML strip, bracket removal)
       │       Resolve voice selection via audio_generator
       │       Build task data structure
       │
       ├─► [Phase 2: Deduplicating]
       │     Group duplicate tasks by (text + voice + format) to avoid redundant generation
       │
       ├─► [Phase 3: Generating]
       │     Submit unique tasks to MultiEngineExecutor
       │       Look up file in audio_file_store (Disk Cache)
       │       If cache miss, route to ServiceManager -> service.get_tts_audio_batch()
       │       Write generated audio atomically to audio_file_store
       │
       └─► [Phase 4: Saving]
             Write [sound:filename.mp3] tags to target fields
             Add media files to Anki's media collection via anki_utils
             Commit changes in a single Anki transaction
```

### 3.2 Note Editor "Add Audio" Flow

```
[User Clicks Speaker Icon in Editor]
       │
       ▼
[EditorManager.apply_all_mapping_rules()]
       │
       ▼
[AudioGenerator.process_note_audio()]
       │
       ├─► Resolve field text and select voice
       ├─► check audio_file_store (Disk Cache)
       ├─► If cache miss, call ServiceManager.get_tts_audio()
       ├─► Write sound tag [sound:...] to note
       │
       ▼
[Editor Refresh & Audio Playback]
       ├─► Update editor fields on main thread
       └─► Play generated audio file via anki_utils.play_sound()
```

### 3.3 Realtime Card Review Flow

```
[Anki renders review card containing {{tts superfreetts_preset=MyPreset ...}}]
       │
       ▼
[AnkiSuperFreeTTSPlayer.play_tts_tag()]  (Registered player hook)
       │
       ▼
[RealtimeManager.get_audio_filename_tts_tag()]
       │
       ├─► Parse preset name from TTS tag extra arguments
       ├─► Fetch preset config from ConfigStore
       ├─► Call AudioGenerator.get_audio_file() (Generates or returns cached file)
       │
       ▼
[Anki plays returned audio file]
```

---

## 4. Concurrency Model

SuperFreeTTS isolates slow I/O and CPU-intensive operations from Anki's main thread to keep the user interface responsive.

* **Thread Isolation**: Batch operations and TTS calls are run in background threads using `AnkiUtils.run_in_background()`. Results are dispatched back to Anki's main thread.
* **Per-Engine Executors**: The `MultiEngineExecutor` routes tasks to separate thread pools based on the service name:
  * **EdgeTTS**: Managed via `BoundedThreadPoolExecutor` with a pool cap of `EDGETTS_MAX_WORKERS` (default = 3). Work is executed concurrently using `asyncio.run()` with `asyncio.gather()`.
  * **Local neural engines (Piper, Kokoro, MMS)**: Sub-processes run within a persistent IPC pool (`SherpaProcessPool`). Threads submit requests to the pool and wait for response data over stdin/stdout.
* **Bounded Queues**: `BoundedThreadPoolExecutor` uses a semaphore to limit queue size. This prevents memory saturation when generating thousands of items.
* **Resource Monitoring**: `SimpleResourceMonitor` tracks RAM usage during batch runs. It triggers explicit Python garbage collection (`gc.collect()`) when memory boundaries are crossed.

---

## 5. Configuration & Persistence

All addon configuration is stored within Anki's native profile config using five main keys:

1. **`configuration`**: Global settings mapping service names to their status (enabled/disabled) and parameters (API keys, endpoints, options).
2. **`preferences`**: UI language, default audio format, debug mode, log settings, and cache cleanup intervals.
3. **`presets`**: User-defined configurations (source fields, target fields, text cleaning, voice configurations) identified by UUIDs.
4. **`mapping_rules`**: A list of rule definitions mapping note types or decks to preset UUIDs for automatic audio assignment in the editor.
5. **`realtime_config`**: Configurations for card reviewer playback, defining presets separately for the front and back card templates.

### Migration
The schema version is tracked via `CONFIG_SCHEMA_VERSION = 7`. On startup, `config_models.migrate_configuration()` detects older formats and migrates them before instantiating the main application.
