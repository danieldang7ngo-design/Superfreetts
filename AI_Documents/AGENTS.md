# AGENTS.md — SuperFreeTTS

Anki add-on, free TTS engines only (EdgeTTS, Piper, Kokoro, MMS, Supertonic,
GoogleTranslate, Windows SAPI, macOS TTS, eSpeak-ng, also 6 dictionary services).
Forked from HyperTTS, paid services stripped. Anki addon ID: `351217314`.
Everything here is live user data — careful with git.

Read `AGENTS.md` first. Reach for `REFERENCE.md` only when:
- Need architecture diagram / data flow
- Need vendored deps list
- Running tests (skip-list, full command)
- Need file location of a class (API Index or Module Index)
- Need list of UI components
Otherwise AGENTS.md covers 90% of tasks.

## 1. Folder Map

| Path | What's inside |
|---|---|
| `__init__.py` | Entry point. Anki loads this first. |
| `superfreetts_addon/__init__.py` | Starts the `SuperFreeTTS` class. |
| `superfreetts_addon/superfreetts.py` | Central facade. Wires config, audio, batch, realtime, editor modules. |
| `superfreetts_addon/batch_orchestrator.py` | Batch pipeline: prepare → dedup → generate → save. |
| `superfreetts_addon/batch_executor.py` | `MultiEngineExecutor` — per-engine thread pools. |
| `superfreetts_addon/servicemanager.py` | Lazy-loads TTS engines (keeps Anki startup fast). |
| `superfreetts_addon/audio_generator.py` | Single-note audio generation, voice fallback logic. |
| `superfreetts_addon/audio_file_store.py` | Disk cache, content-addressed by SHA-224 hash. |
| `superfreetts_addon/realtime_manager.py` | `{{tts ...}}` tag handling for live review playback. |
| `superfreetts_addon/editor_manager.py` | TTS actions inside the note editor. |
| `superfreetts_addon/config_store.py` + `config_models.py` | Config read/write, migrations, data shape. |
| `superfreetts_addon/services/service_*.py` | One file per TTS engine, extends `ServiceBase`. |
| `superfreetts_addon/gui.py` + `component_*.py` | UI windows (Settings, Batch, Easy Mode, note list). |
| `superfreetts_addon/i18n.py` | UI text, multiple locales (see §6). |
| `tools/notes_db.py` | Resolves Anki collection path, paged note fetch/count for lazy-loading UI. |
| `tests/` | Automated tests. `mock_anki.py` fakes Anki, no real install needed. |
| `build_share.py` | Packages everything into `.ankiaddon` for release. |

## 2. Golden Rules

1. **Never commit:** `meta.json`, `user_files/`, `cache/`, `__pycache__/`, `dist/`,
   `*.ankiaddon`, `_local_override.py`, `set_edge_workers_*.py`, `*.log`,
   `superfreetts-work.index`, `*superfreetts-mirror.git*`. Real user data or
   generated junk. `meta.json` holds user UUID + all voice presets — gitignored
   now, but was once pushed to `origin/main`; use `git filter-repo` + force-push
   if it needs removing from history.
2. **Never `git add .` / `git add -A`** without checking `git status` first.
3. **Never force-push or rewrite history** unless the user explicitly asks.
   Default branch `main`, push to `origin/main`.
4. **EdgeTTS worker cap is 3**, source of truth `EDGETTS_MAX_WORKERS = 3` in
   `batch_constants.py`. Never raise this in committed source — Microsoft bans
   IPs that burst EdgeTTS requests. `MAX_WORKER_THREADS = 20` is a *separate*
   cap, for CPU-bound engines (Piper/Kokoro/MMS) only — fine to use, not EdgeTTS.
   4 code points touch worker logic if you ever change it: `batch_constants.py`,
    `service_edgetts.py` (runtime clamp at line ~251), `superfreetts.py`,
   `config.json`.
5. **No blocking calls on the main thread.** Any slow op (network, file write,
   TTS generation) runs in a background thread, never directly in a
   button-click handler. Wrap UI actions via `error_manager.get_single_action_context()`.
6. **New TTS engine must declare `service_fee = constants.ServiceFee.free`.**
   `ServiceManager` skips anything else automatically.

## 3. Common Tasks

**Add a new free TTS engine:**
1. Create `superfreetts_addon/services/service_yourengine.py`, inherit `ServiceBase`.
2. Set `service_fee = constants.ServiceFee.free`.
3. Done — `ServiceManager` auto-discovers it, no manual registration.

**Change EdgeTTS worker count locally (never in committed source):**
```
python set_edge_workers_20.py
```
Creates gitignored `_local_override.py`. Don't edit `batch_constants.py` directly.

**Tests:**
```
python -m pytest tests/ -v --tb=short       # all (~200, 2s)
python -m pytest tests/test_batch_flow.py   # single file
```
`rtk pytest` swallows stdout on Windows — use `python -m pytest` directly.
See `REFERENCE.md §5` for skip-list and details.

**Build the `.ankiaddon`:**
```
python build_share.py
```
Resets `config.json` to clean defaults (worker=3, no user data). Includes
`tools/` package so DB helper modules ship too. Doesn't patch code.

**Debug logging:**
```powershell
$env:HYPER_TTS_DEBUG_LOGGING = "enable"   # console
$env:HYPER_TTS_DEBUG_LOGGING = "file"     # file
$env:HYPER_TTS_DEBUG_LOGFILE = "path.log"
```

**Release a new version:** bump `superfreetts_addon/version.py` → add entry to
`release_notes.py` (per-locale) → update `CHANGELOG.md` → run
`python -m py_compile` on changed files. Full steps: `UPDATE_WORKFLOW.md`.

## 4. Audio Generation — How It Works

1. User triggers generate (Easy Mode = one note, Collection Mode = batch).
2. `get_source_text()` pulls text from the note field.
3. Text cleaned: HTML tags, cloze markers, brackets stripped.
4. `get_audio_file()` hashes `(text, voice_id, options)` with SHA-224 →
   checks `user_files/` for `superfreetts-{hash}.mp3`. Hit → reuse, no network
   call. Miss → queued to `MultiEngineExecutor`, which runs it on a per-engine
   background thread pool (max 3 threads for EdgeTTS).
5. Finished audio attaches to the note.

Batch mode specifically runs 4 phases: Preparing → Deduplicating → Generating
→ Saving (writes sound tags + commits notes in one Anki transaction).

## 5. UI Modes

- **Easy Mode** — single note, simple flow, for beginners.
- **Collection Mode** — batch, many notes, checkpoint/resume if Anki crashes mid-run.
- **Realtime Mode** — no file saved; inserts `{{tts ...}}` tag, plays live during
  review via `ttsplayer.py` → `RealtimeManager`.

## 6. i18n

UI text lives in `i18n.py`. 7 locales: en, vi, ko, ja, zh-CN, zh-TW, sv.

## 7. Known UI Bug Pattern

`QLabel` with `wordWrap=True` inside a `QVBoxLayout` can overlap other widgets
unless you call `setMinimumHeight()` on it.

## 8. Config Persistence

Five keys in Anki's profile config: `configuration` (per-service settings),
`preferences` (language, format, debug, cache TTL), `presets` (UUID-keyed
voice configs), `mapping_rules` (deck/note-type → preset), `realtime_config`
(front/back card playback presets). Schema version tracked as
`CONFIG_SCHEMA_VERSION = 7`; `config_models.migrate_configuration()` upgrades
old formats on startup.

<!-- headroom:rtk-instructions -->
## RTK (Rust Token Killer) — prefix shell commands

`rtk <cmd>` cuts context usage 60-90%, zero behavior change. Safe always — if
rtk has no filter for a command it passes through unchanged.

```bash
rtk git status / diff / log
rtk ls <path>  rtk read <file>  rtk grep <pattern>  rtk find <pattern>
rtk pytest tests/     # failures only
rtk tsc / lint / mypy / ruff check   # errors only
rtk gh pr view <n>  rtk gh run list
rtk docker ps  rtk kubectl get
rtk pip list  rtk pnpm install  rtk npm run <script>
```
Chain commands with `rtk` on each segment: `rtk git add . && rtk git commit -m "msg"`.
Debugging → use raw command, no rtk prefix. `rtk proxy <cmd>` = unfiltered but tracked.
<!-- /headroom:rtk-instructions -->

## Undo entries (Apply flow)

Any `aqt.mw.col.add_custom_undo_entry(...)` MUST be merged
(`merge_undo_entries`) on every exit path — success AND failure — before
the calling method returns. An unmerged entry blocks all other undoable
collection ops (Batch, Workflow, everything) until Anki restarts. If you
add a new `.failure(...)` handler to any `QueryOp` between an open undo
entry and its merge, that handler must merge the entry first. See
`component_batch_preview.py`, `_apply_chunk_failed`, for the pattern.