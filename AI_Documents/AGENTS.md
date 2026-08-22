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

Addon root is `src/superfreetts/` (AADT layout — see git `e1d2d24`). All runnable
addon code, `manifest.json`, `__init__.py`, `graphics/` and vendored `external/`
live there. Repo root additionally holds `tests/`, `build_share.py` and docs.

| Path | What's inside |
|---|---|
| `src/superfreetts/__init__.py` | Entry point. Anki loads this first. |
| `src/superfreetts/manifest.json` | Addon metadata (AnkiWeb listing info). |
| `src/superfreetts/superfreetts_addon/__init__.py` | Starts the `SuperFreeTTS` class. |
| `src/superfreetts/superfreetts_addon/superfreetts.py` | Central facade. Wires config, audio, batch, realtime, editor modules. |
| `src/superfreetts/superfreetts_addon/batch_orchestrator.py` | Batch pipeline: prepare → dedup → generate → save. |
| `src/superfreetts/superfreetts_addon/batch_executor.py` | `MultiEngineExecutor` — per-engine thread pools. |
| `src/superfreetts/superfreetts_addon/servicemanager.py` | Lazy-loads TTS engines (keeps Anki startup fast). |
| `src/superfreetts/superfreetts_addon/audio_generator.py` | Single-note audio generation, voice fallback logic. |
| `src/superfreetts/superfreetts_addon/audio_file_store.py` | Disk cache, content-addressed by SHA-224 hash. |
| `src/superfreetts/superfreetts_addon/realtime_manager.py` | `{{tts ...}}` tag handling for live review playback. |
| `src/superfreetts/superfreetts_addon/editor_manager.py` | TTS actions inside the note editor. |
| `src/superfreetts/superfreetts_addon/config_store.py` + `config_models.py` | Config read/write, migrations, data shape. |
| `src/superfreetts/superfreetts_addon/services/service_*.py` | One file per TTS engine, extends `ServiceBase`. |
| `src/superfreetts/superfreetts_addon/gui.py` + `component_*.py` | UI windows (Settings, Batch, Easy Mode, note list). |
| `src/superfreetts/superfreetts_addon/i18n.py` | UI text, multiple locales (see §6). |
| `src/superfreetts/graphics/` | Banners + UI icons. Icons are Lucide (ISC), stroke-based SVGs: editor buttons `icon_speaker`, `icon_play`, `icon_settings`; toggles `icon_chevron_down`/`icon_chevron_right`; menu `icon_headphones`. `NOTICE` holds attribution. Add any new icon as a static Lucide SVG here (no runtime dep). |
| `tests/` | Automated tests. `mock_anki.py` fakes Anki, no real install needed. |
| `build_share.py` | Packages `src/superfreetts/` into `.ankiaddon` for release (see §3). |
| `ANKIWEB_DESCRIPTION_EN.html` | English store listing / description for AnkiWeb (item 351217314). |
| `ANKIWEB_DESCRIPTION_EN.txt` | Plain text version of AnkiWeb store listing. |

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
    4 code points touch worker logic if you ever change it: `batch_constants.py`
     (`EDGETTS_MAX_WORKERS`), `tts_orchestrator.py` (`build_engine_config()`
     default + clamp at line ~78), `service_edgetts.py` (runtime clamp at line
     ~313), `config.json`.
5. **No blocking calls on the main thread.** Any slow op (network, file write,
   TTS generation) runs in a background thread, never directly in a
   button-click handler. Wrap UI actions via `error_manager.get_single_action_context()`.
6. **New TTS engine must declare `service_fee = constants.ServiceFee.free`.**
   `ServiceManager` skips anything else automatically.
7. **Every new constant needs a matching attribute in `constants.py`.** When
   referencing `constants.SOME_NAME`, verify it's defined — or define it.
   Same for any import: `grep -rn "pprint\."` before using `pprint.pformat`
   to check the import exists in that file.

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

**Build the `.ankiaddon` — canonical way is via the AADT toolkit**
(`aadt`) which produces `dist/SuperFreeTTS-<version>.ankiaddon`. On this machine
the binary lives at `$env:USERPROFILE\.local\bin\aadt.exe` and is invoked with a
specific version tag + `-d local`:
```powershell
$aadt = "$env:USERPROFILE\.local\bin\aadt.exe"
& $aadt build 26.8.15 -d local      # builds the specific git tag 26.8.15
# "dev" source variant (working tree incl. uncommitted changes) is NOT used here;
# we always build from the exact released git tag so the .ankiaddon equals the tag.
```
AADT reads `addon.json` (`module_name: superfreetts`, `ankiweb_id: 351217314`),
packages `src/superfreetts/` from the tag and writes `dist/SuperFreeTTS-<version>.ankiaddon`.
Build `local` (debug) vs `ankiweb` (release) — see the AADT README.
The `.ankiaddon` is a ZIP; `manifest.json` inside must carry `"version": "<tag>"`
and `"package": "superfreetts"`. Confirm it matches after a build.

A legacy `python build_share.py` script also exists; it packages the same
`src/superfreetts/` source into `SuperFreeTTS.ankiaddon` at the repo root and
resets `config.json` to clean defaults (worker=3, no user data). Prefer `aadt`.
Both skip user data (`meta.json`, `user_files/`, `cache/`; and `dist/`).

### Releasing a new version — full pipeline (used by this project)

Sequence that has been used for each release (26.8.12 → 26.8.15):

1. **Bump version in 2 places** so `version.py` == `pyproject.toml`:
   - `superfreetts_addon/version.py` → `ANKI_SUPER_FREE_TTS_VERSION='26.8.15'`
   - `pyproject.toml` → `version = "26.8.15"`
2. **Changelog** (multi-language): add a top `## <version> - YYYY-MM-DD` block in
   `CHANGELOG.md` (English + at least Vietnamese), and a new
   `ReleaseNoteEntry(version="26.8.15", ...)` at the TOP of `RELEASE_NOTES` in
   `release_notes.py` with title + bullets per locale (en, vi, ko, zh-CN, zh-TW, ja, sv).
3. **Compile + test all changed files before committing**:
   ```
   python -m py_compile <changed files...>
   python -m pytest tests/ -q --tb=short     # expect ~270 passed, 1 skipped
   ```
   Keep `tests/` green on every release.
4. **Commit** only the intended files (never `git add .` blindly — see Golden Rules):
   ```
   git add CHANGELOG.md pyproject.toml tests/ src/superfreetts/...
   git commit -m "feat: ..."
   ```
5. **Tag + build**:
   ```
   git tag 26.8.15
   & "$env:USERPROFILE\.local\bin\aadt.exe" build 26.8.15 -d local
   # -> dist/SuperFreeTTS-26.8.15.ankiaddon
   ```
6. **Install into Anki** — because the addon loads `.pyd`/`.pyc`, always rename
   the live folder aside (avoid locked-file errors) then extract the ZIP:
   ```powershell
   Get-Process -Name anki -ErrorAction SilentlyContinue | Stop-Process -Force
   $target = "$env:APPDATA\Anki2\addons21\superfreetts"
   $old    = "$env:APPDATA\Anki2\addons21\_superfreetts_old$N"   # bump N each time
   if (Test-Path $target) { Rename-Item $target $old }           # keep old aside
   Add-Type -AssemblyName System.IO.Compression.FileSystem
   [System.IO.Compression.ZipFile]::ExtractToDirectory((Resolve-Path dist\SuperFreeTTS-<ver>.ankiaddon), $target)
   # disable the backup so Anki won't load it later:
   Remove-Item "$old\__init__.py","$old\manifest.json" -ErrorAction SilentlyContinue
   ```
7. **Push** branch + the new tag to GitHub:
   ```
   git push origin aadt-restructure     # branch we develop on
   git push origin 26.8.15              # new version tag
   ```
   Note: PowerShell renders git's stderr as "RemoteException" — that is normal;
   verify success via `git log`/`git ls-remote --tags` instead of exit code alone.

`dist/build` and `dist/staging` are transient AADT work dirs. They are safe to
delete any time (AADT regenerates them); keep only the `.ankiaddon` files in `dist/`.

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

### Dirty-button indicator (Anki Sync-style)

When the current Batch preset / Workflow config changes (source field, target,
voice selection, text-processing, rename, duplicate, new preset) and is left
unsaved, the **Generate Audio** button (Batch) and **Run** button (Workflow) flip
to the active theme's warning (`amber`) color to signal the audio would be out of
date and regeneration is expected. Once saved (or the config is clean) the button
returns to its normal color. Implementation:

- `gui_utils.set_button_dirty(button, dirty, normal_style, dirty_style)` swaps the
  button's `cssClass` between `btnPastel{dirty}` and `btnPastel{normal}`. Colors come
  from the active theme's stylesheet (`btnPastelAmber` is defined in every theme), so
  the warning tone adapts per-theme — never hard-code a hex here.
- Batch (`component_batch.ComponentBatch`): `update_save_profile_button_state()` also
  calls `update_apply_button_dirty_style()`, which recolors `apply_button` when
  `model_changed` and `notes_loaded` are both true (re-enabling it so the user can
  regenerate). Editor mode is skipped.
- Workflow (`component_workflow.WorkflowDialog`): `refresh_button_states()` recolors
  `run_button` when `model_changed` and the workflow has items.
- Tooltips (`batch_tooltip_generate_dirty`, `workflow_tooltip_generate_all`,
  `workflow_tooltip_generate_dirty`) exist in all 7 locales.

If you add new buttons that should reflect a "changed, needs re-running" state, reuse
`set_button_dirty` rather than inline `setStyleSheet` so theming stays consistent.

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

## 9. UI Themes (current state, v26.8.15)

- **7 themes**, selectable in Settings → Preferences → "Choose interface theme":
  `vibrant` (default), `ollama`, `apple`, `nintendo`, `binance`, `clay`, `claude`.
  Source of truth `gui_utils.VALID_THEMES`; each has a `_build_<theme>_stylesheet(dark)`
  + a light/dark token block. `get_dynamic_stylesheet()` dispatches on the active theme
  and appends `_build_services_extra_css()` (theme-aware Services tab widgets).
- **Live preview:** picking a theme in Preferences re-applies the stylesheet on the open
  Settings dialog instantly (`SettingsDialog.refresh_stylesheet()` + `unpolish/polish`);
  pressing **Apply** persists it. `gui_utils.set_active_theme(theme)`.
- **Services tab theming:** section headers (`sectionToggle`), Setup buttons
  (`setupAction`), separators (`serviceSeparator`), status badges (`statusBadgeReady /
  statusBadgeSetup / statusBadgeDisabled / statusBadgeFree / statusBadgeRecommended`)
  are styled via `cssClass` selectors from the `_SERVICES_TOKENS` palette — never hard-code
  theme hexes in `component_services.py`.
- **Tests:** `tests/test_themes_smoke.py` builds every theme light+dark and asserts the
  Services selectors are present.

## 10. First-run Language Detection (v26.8.15)

- Addon no longer defaults blindly to a hardcoded language. On **first install**,
  `config_store.ensure_ui_language(True)` is called from `__init__.py` (when
  `first_install`), which reads Anki's own interface language via
  `anki.lang.current_lang` (`detect_anki_language()`) and stores it as `ui_language`
  if it's one of the 7 supported locales; otherwise it falls back to `en`.
- The shipped `config.json` now defaults `preferences.ui_language` to `"en"` (neutral);
  the detected Anki language overrides it on a fresh install.
- `component_welcome.WelcomeDialog` has a language `QComboBox` at the top: switching it
  re-renders the whole dialog live and saving it writes the chosen `ui_language`
  (`hypertts.save_preferences`). Note `i18n.get_text()` falls back to English for any
  key a locale lacks (e.g. `welcome_button_start` missing in ja/sv/zh-*).
- Tests: `tests/test_ui_language.py` (detection + first-run only).

## 11. Gotchas & Pitfalls (learned in practice)

### i18n / locales
1. When inserting multiple keys into a locale JSON with a script, keys can land on a
   single line (still valid JSON, ugly). Normalize with
   `json.dump(data, f, ensure_ascii=False, indent=2, newline="\n")`.
2. A new key must be added to **all 7 locale files** (en, vi, ko, ja, zh-CN, zh-TW, sv).
   `i18n.get_text()` silently falls back to English for any locale missing the key
   (e.g. `welcome_button_start` is missing in ja/sv/zh-*), so a "working" key can hide a
   missing translation.

### theme / gui
3. All **7 theme builders must keep the same shared token variable names**
   (`tab_bg_selected`, `tab_text_selected`, `btn_hover_sec`, `hairline`, `svc_enabled_bg`,
   `svc_disabled_bg`, ...). The Services block (`_SERVICES_TOKENS`) and
   `tests/test_themes_smoke.py` depend on them. Rename one → breaks many.
4. Never hard-code colors/`setStyleSheet` in `component_services.py` — use the themed
   `cssClass` selectors (`sectionToggle`, `setupAction`, `serviceSeparator`,
   `statusBadge*`). Past this rule caused broken dark themes (white search box, blue
   summary, purple gradient header).
5. `is_night_mode()` returns a `MagicMock` under tests — coerce with `bool(dark)` before
   using it as a dict key (e.g. `_SERVICES_TOKENS[theme][bool(dark)]`), else `KeyError`.
6. `get_status_badge()` accepts `css_class` (preferred) with `bg_color`/`text_color`
   kept as a fallback — old callers still work, but migrate to `css_class` over time.

### config
7. **Two places read `ui_language`**: legacy `anki_utils.get_ui_language()` and modern
   `config_store.get_ui_language()`. Keep both in sync.
8. The shipped `config.json` has its own `preferences.ui_language` default which
   overrides `config_models`' `"en"` default. Changing the default means editing **both**.
9. First-run detection: `first_install` is only known when `user_uuid` is null, and
   `user_uuid` is written before `ConfigStore` reads config. Pass the `first_install`
   flag explicitly into `config_store.ensure_ui_language()` — do not re-derive it inside.

### build / release
10. Verify `manifest.json` inside the `.ankiaddon` carries `"version" == tag` and
    `"package" == "superfreetts"` after every build.
11. `dist/build` and `dist/staging` are transient AADT work dirs — safe to delete;
    only the `.ankiaddon` files in `dist/` matter.

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