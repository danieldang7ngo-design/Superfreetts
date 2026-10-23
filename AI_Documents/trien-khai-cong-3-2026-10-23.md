# Triển khai công 3 — 2026-10-23

Branch: `fix/resource-management` · Version: `26.10.2` (giữ nguyên) · Không push/tag/release.

## Commit IDs
- Commit A (voicelist lazy + service + test imports): `7a7943efbec087338fa889d7241c7c6057a45725`
- Commit B1 (core batch/resource/superfreetts): `f65934a`
- Commit B2 (runners hardening): `c9e208a`
- Commit C (remove_tts_tag non-greedy): `39e0851`
- Commit D (crash-resume preview tests + docs): `eb306a5`

## Full gate
- `.venv/bin/python -m pytest`: 442 passed, 1 skipped
- coverage critical: config_models 71.1%, batch_executor 84.8%, component_text_processing 96.7%, audio_file_store 91.7%, voice_cache 91.8% (min 70%)
- ruff (superfreetts_addon + tests): All checks passed
- bandit -ll (superfreetts_addon): No issues identified (medium/high)
- version_consistency: passed
- build_share + verify_package: OK (edge_cap 3)

## Ghi chú
- Giữ CRLF cho file `.py` nguồn.
- EdgeTTS cap 3 bất biến (`EDGETTS_MAX_WORKERS=3`).
- Không commit dist/, coverage.json, meta.json, *.ankiaddon, user_files.
