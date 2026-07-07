# `external/` — Vendored Dependencies

Anki bundles its own Python, missing most libraries the addon needs. `external/`
vendors them so the addon works standalone — no reliance on system Python.

## Load mechanism

```python
# root __init__.py
addon_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, os.path.join(addon_dir, 'external'))
import edge_tts, gtts, aiohttp  # now resolve from external/
```

## What's in there, by engine

| Engine | Vendored libs |
|---|---|
| EdgeTTS | `edge_tts`, `edge_playback`, `aiohttp` + deps (`aiosignal`, `aiohappyeyeballs`, `frozenlist`, `multidict`, `propcache`, `yarl`, `attrs`), `psutil` |
| Google Translate TTS | `gtts`, `click` |
| Windows SAPI | `comtypes` |
| eSpeak-ng | `espeakng` |
| Supertonic | **Not vendored.** SDK + model install into the shared embedded Python runtime via the setup dialog. Model cache lives in `data/supertonic_cache` (per Anki profile), not packaged into `.ankiaddon`. Model/license needs review before public release. |

Shared/general: `requests`, `urllib3`, `certifi`, `charset_normalizer`, `idna`
(HTTP); `tabulate`, `dateutil`, `cachetools`, `machineid`, `six`,
`typing_extensions`, `PyYAML` (utilities); `databind`, `typeapi`, `nr`,
`deprecated`, `wrapt` (data/serialization).

Already cleaned from the repo: `__pycache__/`, `.pytest_cache/`, log/tmp files.

## Size

~15-20 MB total. Biggest: aiohttp+deps (~5-10 MB), comtypes (~2-3 MB),
requests+urllib3 (~2-3 MB), edge_tts (~1-2 MB), gtts (~500 KB).

## Trimming further

Safe: strip `*.dist-info/` metadata, `__pycache__/`, test files.
Unsafe: don't remove individual libs blind — many are interdependent
(aiohttp's sub-deps especially); breaking one breaks EdgeTTS entirely.
