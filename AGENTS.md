# AGENTS.md — SuperFreeTTS

This repository contains an Anki add-on for free TTS engines. For deeper project context, see [AI_Documents/AGENTS.md](AI_Documents/AGENTS.md) and [README.md](README.md).

## Working conventions

- Keep changes scoped to the add-on source under [superfreetts_addon/](superfreetts_addon/) and tests under [tests/](tests/).
- Prefer the existing virtual environment at [.venv/](.venv/) for Python commands; avoid installing packages globally.
- Verify behavior with targeted pytest runs before claiming completion.
- Avoid touching generated user data, logs, or runtime artifacts under [user_files/](user_files/) unless the task explicitly requires it.

## Sandbox / agent execution

- When the editor runs agents in a sandbox, keep execution isolated and read-only unless a change is required.
- Prefer small, verifiable edits and avoid full UI launches or network-heavy actions unless explicitly requested.
- If a task needs external services or Anki, use the smallest reproducible test path and report the limitation clearly.
