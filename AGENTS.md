# AGENTS.md — Super Free TTS

Anki addon for free TTS (EdgeTTS, Piper, Kokoro, MMS). Repo root = addon
install dir at `%APPDATA%\Anki2\addons21\351217314`. Everything here is live
user data — be careful with git.

## Architecture

- **Entry point:** `__init__.py` → `superfreetts_addon/__init__.py` → `SuperFreeTTS`
- **Orchestrator:** `superfreetts_addon/superfreetts.py` wires config, realtime, batch, audio, editor modules
- **Services** live in `superfreetts_addon/services/`, lazily instantiated via `ServiceManager`
- **Config model** in `config_models.py` (dataclass + databind.json), serialized to Anki config keys `configuration`, `preferences`, `presets`, `mapping_rules`
- **Version:** `superfreetts_addon/version.py` (`ANKI_SUPER_FREE_TTS_VERSION`)
- **3 UI locales:** en, vi, ko (in `i18n.py`)

## EdgeTTS worker cap

| Context | Cap | Mechanism |
| --- | --- | --- |
| Source (repo default) | **3** | `EDGETTS_MAX_WORKERS = 3` in `batch_constants.py` |
| Local override | 20 | `_local_override.py` (`EDGETTS_MAX_WORKERS = 20`) — gitignored |
| `config.json` default | 20 | Runtime clamped to `EDGETTS_MAX_WORKERS` in `service_edgetts.py:202` |

`MAX_WORKER_THREADS = 20` is the *CPU-bound* cap for Piper/Kokoro/MMS. Don't
touch it for EdgeTTS. The 4 code points if changing worker logic:
`batch_constants.py`, `service_edgetts.py`, `superfreetts.py`, `config.json`.

Toggle at root: `python set_edge_workers_20.py` (interactive, creates/removes
`_local_override.py`).

## Testing

```powershell
pytest                              # all tests (runs mock_anki first)
pytest -m unit                      # unit tests only
pytest -m integration               # tests using filesystem/threads
pytest tests/test_edgetts_direct.py # single test file
```

Tests mock Anki via `tests/mock_anki.py` + `tests/conftest.py`. No real Anki
needed.

## Build `.ankiaddon`

```powershell
python build_share.py               # produces SuperFreeTTS.ankiaddon
```

Resets `config.json` to clean defaults (worker 3, no user data). Does NOT patch
code — source defaults to 3; `_local_override.py` is excluded via `.gitignore`
and `EXCLUDE_FILE_NAMES`.

## Release workflow

Follow `UPDATE_WORKFLOW.md`: bump `version.py` → add `release_notes.py` entry
(en/vi/ko) → update `CHANGELOG.md` (en/vi, +ko when relevant) → verify
`python -m py_compile` on touched files.

## Never commit

`meta.json`, `user_files/`, `cache/`, `__pycache__/`, `dist/`,
`*.ankiaddon`, `_local_override.py`, `set_edge_workers_*.py`,
`superfreetts-work.index`, `*superfreetts-mirror.git*`, `*.log`.

`meta.json` contains user UUID + all presets (voice settings). It's gitignored
but was once pushed to `origin/main` — use `git filter-repo` + force-push if
removing from history.

## Git rules

- Default branch: `main`. Push to `origin/main`.
- Never `git add .` or `git add -A` without checking status first.
- No force-push or history rewrite without explicit user request.

## Debug logging

```powershell
$env:HYPER_TTS_DEBUG_LOGGING = "enable"   # debug to console
$env:HYPER_TTS_DEBUG_LOGGING = "file"     # debug to file
$env:HYPER_TTS_DEBUG_LOGFILE = "path.log"
```


<!-- headroom:rtk-instructions -->
# RTK (Rust Token Killer) - Token-Optimized Commands

When running shell commands, **always prefix with `rtk`**. This reduces context
usage by 60-90% with zero behavior change. If rtk has no filter for a command,
it passes through unchanged — so it is always safe to use.

## Key Commands
```bash
# Git (59-80% savings)
rtk git status          rtk git diff            rtk git log

# Files & Search (60-75% savings)
rtk ls <path>           rtk read <file>         rtk grep <pattern>
rtk find <pattern>      rtk diff <file>

# Test (90-99% savings) — shows failures only
rtk pytest tests/       rtk cargo test          rtk test <cmd>

# Build & Lint (80-90% savings) — shows errors only
rtk tsc                 rtk lint                rtk cargo build
rtk prettier --check    rtk mypy                rtk ruff check

# Analysis (70-90% savings)
rtk err <cmd>           rtk log <file>          rtk json <file>
rtk summary <cmd>       rtk deps                rtk env

# GitHub (26-87% savings)
rtk gh pr view <n>      rtk gh run list         rtk gh issue list

# Infrastructure (85% savings)
rtk docker ps           rtk kubectl get         rtk docker logs <c>

# Package managers (70-90% savings)
rtk pip list            rtk pnpm install        rtk npm run <script>
```

## Rules
- In command chains, prefix each segment: `rtk git add . && rtk git commit -m "msg"`
- For debugging, use raw command without rtk prefix
- `rtk proxy <cmd>` runs command without filtering but tracks usage
<!-- /headroom:rtk-instructions -->
