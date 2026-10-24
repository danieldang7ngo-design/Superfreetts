# Manual network scripts

These scripts call the real EdgeTTS service and run at import time — they are
**not** pytest tests and are deliberately outside `testpaths`.

They used to live in `tests/` as `_test_*.py`. pytest's default
`python_files = test_*.py` never collected them, but running one directly
blocked for minutes on the network (a 180s timeout was observed), which looked
like a broken suite.

Run them explicitly from the repository root when you want a live check:

```bash
python scripts/manual/_test_edgetts_sequence_mode.py
```
