# SuperFreeTTS — Architecture

Deep system design. Read `AGENTS.md` first for rules/tasks/folder map — this
file only covers structure and data flow that doesn't fit there.

## 1. Layers

```
┌─────────────────────────────────────────────────────────────────┐
│  Anki UI (Qt / WebView) — Browser menu, Editor buttons, Player   │
└────────────────────────┬────────────────────────────────────────┘
┌────────────────────────▼────────────────────────────────────────┐
│  gui.py, component_batch.py, component_settings.py, ...          │
│                    GUI / Dialog Layer                            │
└────────────────────────┬────────────────────────────────────────┘
┌────────────────────────▼────────────────────────────────────────┐
│              SuperFreeTTS (superfreetts.py) — Facade              │
└──┬──────────┬───────────┬────────────────┬───────────┬──────────┘
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

1. **Presentation** — Qt widgets, dialogs, menus, editor/reviewer hooks.
2. **Facade** — `SuperFreeTTS`, single entry point, wires everything, exposes
   high-level actions to GUI.
3. **Domain** — batch scheduling, text processing, voice selection/fallback,
   realtime routing.
4. **Infrastructure** — service management, disk cache, Anki DB ops, process
   pools, thread pools.

## 2. Data Flows

### 2.1 Batch Audio Generation

```
component_batch.py (Qt Dialog)
  → SuperFreeTTS.process_batch_audio()
    → BatchOrchestrator.process_batch_audio()
      ├─ Phase 1 Preparing: extract field text (source_text_resolver),
      │    clean (text_utils: strip HTML/brackets), resolve voice
      │    (audio_generator), build task structs
      ├─ Phase 2 Deduplicating: group by (text+voice+format)
      ├─ Phase 3 Generating: submit unique tasks to MultiEngineExecutor
      │    → check audio_file_store (disk cache)
      │    → miss: ServiceManager → service.get_tts_audio_batch()
      │    → write atomically to audio_file_store
      └─ Phase 4 Saving: write [sound:...] tags to fields, add media via
           anki_utils, commit all notes in one Anki transaction
```

### 2.2 Editor "Add Audio"

```
Speaker icon click → EditorManager.apply_all_mapping_rules()
  → AudioGenerator.process_note_audio()
    ├─ resolve field text, select voice
    ├─ check audio_file_store, miss → ServiceManager.get_tts_audio()
    ├─ write [sound:...] tag to note
    → editor refresh (main thread) + play via anki_utils.play_sound()
```

### 2.3 Realtime Card Review

```
Card renders {{tts superfreetts_preset=X ...}}
  → AnkiSuperFreeTTSPlayer.play_tts_tag() (registered player hook)
    → RealtimeManager.get_audio_filename_tts_tag()
      ├─ parse preset name from tag
      ├─ fetch preset config from ConfigStore
      ├─ AudioGenerator.get_audio_file() (cache or generate)
      → Anki plays returned file
```

## 3. Concurrency Model

- **Thread isolation**: batch ops and TTS calls run via
  `AnkiUtils.run_in_background()`, results dispatched back to main thread.
- **Per-engine executors**: `MultiEngineExecutor` routes to separate thread
  pools by service name. EdgeTTS pool runs `asyncio.run()` +
  `asyncio.gather()` internally, capped at `EDGETTS_MAX_WORKERS` (see
  `AGENTS.md` §2 rule 4). Local neural engines (Piper/Kokoro/MMS) run in a
  persistent IPC subprocess pool (`SherpaProcessPool`, JSON over stdin/stdout).
- **Bounded queues**: `BoundedThreadPoolExecutor` uses a semaphore to cap
  queue size, preventing memory blowup on large batches.
- **Resource monitoring**: `SimpleResourceMonitor` tracks RAM during batch
  runs, triggers `gc.collect()` when thresholds are crossed.


