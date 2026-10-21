# Super Free TTS Anki Add-on
========================

👉 View detailed development roadmap: [_ROADMAP](./_ROADMAP.md)
🤖 For architecture, testing and maintenance notes, see: [`AI_Documents/AGENTS.md`](./AI_Documents/AGENTS.md) and [`AI_Documents/REFERENCE.md`](./AI_Documents/REFERENCE.md)
📦 Release steps: [`UPDATE_WORKFLOW.md`](./UPDATE_WORKFLOW.md) · Change history: [`CHANGELOG.md`](./CHANGELOG.md)

## Introduction

This is the source code for the Super Free TTS add-on for Anki. This folder has been cleaned and does not contain files generated during runtime (logs, tmp, cache, etc.), making it ready to:

- Install into the Anki `addons21` directory.
- Push directly to GitHub as a "clean" source code repository.

## Key Differences from HyperTTS

Super Free TTS is a fork of HyperTTS with a focus on providing high-quality Text-to-Speech using exclusively free resources.

### 1. 100% Free Services
- **Removed Paid Services:** All services requiring API keys or subscriptions have been removed (Alibaba, Amazon, Azure, ElevenLabs, Google Cloud, OpenAI, etc.).
- **Added Free AI Engines:** Integrated powerful free engines including **EdgeTTS** (Microsoft), **Piper TTS**, **Kokoro TTS** (high-quality ONNX), and **MMS TTS** (Meta).

### 2. High-Performance Architecture
- **Multi-threaded Processing:** Features a new `UnifiedBatchExecutor` and `MultiEngineExecutor` for asynchronous, non-blocking audio generation.
- **Service-Specific Concurrency:** Intelligent worker management (e.g., EdgeTTS is capped at 3 workers to prevent IP bans while Piper can run more aggressive threads).
- **Unified Cache & Resource Monitoring:** Shared caching system and RAM tracking to ensure stability during large batches.

### 3. Improved UI/UX
- **Unified Settings:** Merged Configuration and Preferences into a single, intuitive tabbed dialog.
- **Top-Level Menu:** Added an "AnkiVN" menu to the main toolbar for faster access.
- **Simplified Workflow:** "Easy Mode" for quick single-note updates and "Collection Mode" for powerful batch processing.

### 4. Reliability & Recovery
- **Checkpoint System:** Automatically saves progress during batch generation, allowing you to resume if Anki crashes or is closed.

## Main Structure

- `superfreetts_addon/`: Core add-on source code (Python, UI, processing logic).
- `external/`: Vendored pure-Python runtime dependencies (EdgeTTS, HTTP, platform helpers).
- `tests/`: Pytest suite with a mock Anki layer; no real Anki install required.
- `scripts/`: Verification, packaging and vendor-maintenance helpers.
- `AI_Documents/`: Architecture, reference and archived investigation notes.
- `_ROADMAP.md`, `UPDATE_WORKFLOW.md`, `CHANGELOG.md`: Product direction, release checklist and history.

Standard temporary files (like `__pycache__`, `*.pyc`, `*.log`, `*.tmp`, coverage output) are excluded from this repository.

## Installation (Anki)

1. Ensure Anki is closed.
2. Copy this `Superfreetts` folder to:
   - Windows: `C:\Users\<YourUser>\AppData\Roaming\Anki2\addons21\`
3. Restart Anki; the add-on will load automatically.

## Development / Contributing

- Modify source code in the `superfreetts_addon/` directory.
- Run the checks before committing:

```bash
python -m pytest tests/ -q
ruff check superfreetts_addon tests build_share.py scripts
bandit -r superfreetts_addon -ll
```

- The full coverage gate and critical-module gate (70% for config, batch executor,
  text processing, audio storage and voice cache) are documented in
  `.github/workflows/python-test.yml`.
- Vendored dependency versions are pinned in `requirements-vendor.txt`; verify
  them with `python scripts/vendor_deps.py --check`.
- Before packaging, ensure logs, caches and generated files are removed. Build
  with `python build_share.py` and verify with
  `python scripts/verify_package.py SuperFreeTTS.ankiaddon`.

---
Maintained by Paul from AnkiVN.

