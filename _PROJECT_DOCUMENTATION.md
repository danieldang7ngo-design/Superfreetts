# Super Free TTS by Paul from AnkiVN - Tài Li?u D? Án

> Tài li?u này mô t? chi ti?t d? án Super Free TTS. Ð? xem nhanh tóm t?t ki?n trúc và d?nh hu?ng dành riêng cho AI Agents, vui lòng d?c [AI_SUMMARY.md](./AI_SUMMARY.md).

## ?? M?c L?c

- [T?ng Quan](#-t?ng-quan)
- [Công Ngh? S? D?ng](#-công-ngh?-s?-d?ng)
- [Ki?n Trúc D? Án](#-ki?n-trúc-d?-án)
- [Hu?ng D?n S? D?ng](#-hu?ng-d?n-s?-d?ng)
- [Hu?ng D?n Phát Tri?n](#-hu?ng-d?n-phát-tri?n)

---

## ?? T?ng Quan

### D? án là gì?

**Super Free TTS** là m?t addon (ti?n ích m? r?ng) **100% MI?N PHÍ** cho [Anki](https://apps.ankiweb.net/) - ?ng d?ng h?c flashcard ph? bi?n. Addon này du?c **fork t? d? án HyperTTS** và ti?p t?c phát tri?n d? ph?c v? c?ng d?ng.

**Tác gi?**: Paul from AnkiVN

### Gi?i quy?t v?n d? gì?

Khi h?c ngôn ng? ho?c b?t k? môn h?c nào c?n phát âm, vi?c có âm thanh trên th? h?c r?t quan tr?ng. Tuy nhiên, vi?c thu âm ho?c tìm file âm thanh cho t?ng th? r?t t?n th?i gian. Super Free TTS gi?i quy?t v?n d? này b?ng cách:

- **T? d?ng t?o âm thanh** t? van b?n trên th? h?c
- **H? tr? nhi?u engine TTS MI?N PHÍ**: EdgeTTS, Piper (offline), Kokoro (offline), MMS (offline, 1100+ ngôn ng?), Google Translate, Windows SAPI, macOS TTS, eSpeak-ng
- **Linh ho?t**: Thêm âm thanh t?ng th? ho?c hàng lo?t; preset mapping rules; realtime TTS
- **100% Mi?n phí**: Ch? load engine free, không c?n API key

### Thông tin

- **Tên addon**: Super Free TTS
- **Tác gi?**: Paul from AnkiVN
- **Phiên b?n hi?n t?i**: 1.0 (trong `version.py`)
- **Website**: ankivn.com
- **Tuong thích Anki**: `min_point_version: 5`, `max_point_version: 241100` (meta.json)

---

## ?? Công Ngh? S? D?ng

### Ngôn ng? l?p trình

- **Python 3.x**: Ngôn ng? chính c?a d? án
- **PyQt5/PyQt6**: Framework d? t?o giao di?n ngu?i dùng (UI)
- **HTML/CSS/JavaScript**: T?o giao di?n web trong các dialog c?a Anki

### Thu vi?n chính

#### Core Dependencies (trong thu m?c `external/`)

1. **aiohttp (3.13.3)**: HTTP client/server b?t d?ng b? cho Python
   - Dùng d? g?i API các d?ch v? TTS

2. **edge-tts (7.2.7)**: Thu vi?n Python d? s? d?ng Microsoft Edge TTS
   - D?ch v? TTS mi?n phí ch?t lu?ng cao

3. **gtts**: Google Text-to-Speech
   - D?ch v? TTS mi?n phí t? Google

4. **requests**: HTTP library don gi?n
   - G?i API các d?ch v? TTS mi?n phí

5. **tabulate (0.9.0)**: T?o b?ng d? li?u d?p
   - Hi?n th? danh sách voices

6. **comtypes** (Windows only): COM interface
   - Tích h?p v?i Windows SAPI TTS

### D?ch v? TTS du?c h? tr? (T?T C? MI?N PHÍ)

D? án ch? load **các d?ch v? TTS có `service_fee = free`** (service tr? phí nhu Naver b? b? qua khi kh?i t?o).

#### Engine TTS chính (th? t? uu tiên trong UI)
| Engine | Mô t? | Online/Offline |
|--------|--------|-----------------|
| **EdgeTTS** | Microsoft Edge TTS (? ch?t lu?ng cao) | Online |
| **PiperTTS** | Piper (Rhasspy) – gi?ng da ngôn ng?, model .onnx | Offline |
| **KokoroTTS** | Kokoro – gi?ng t? nhiên, ch?y qua engine riêng | Offline |
| **MmsTTS** | MMS (Massively Multilingual Speech) – 1100+ ngôn ng? | Offline |
| **GoogleTranslate** | Google Translate TTS | Online |
| **Windows** | Windows SAPI (ch? Windows) | Offline |
| **MacOS** | macOS built-in TTS (ch? macOS) | Offline |
| **ESpeakNg** | eSpeak-ng, open-source | Offline |

#### D?ch v? t? di?n (pronunciation, `service_type = dictionary`)
- **Cambridge**, **Oxford**, **Duden**, **DWDS**, **Youdao**, **SpanishDict** – t?t c? mi?n phí.
- **Naver**: trong code là `service_fee = paid` nên **không du?c load** trong Super Free TTS.

#### File service tuong ?ng (trong `services/`)
- `service_edgetts.py`, `service_piper.py`, `service_kokoro.py`, `service_mms.py`, `service_googletranslate.py`, `service_windows.py`, `service_macos.py`, `service_espeakng.py`
- T? di?n: `service_cambridge.py`, `service_oxford.py`, `service_duden.py`, `service_dwds.py`, `service_youdao.py`, `service_spanishdict.py`
- `service_naver.py` (paid – b? b? qua). `service_onnx_general.py` (OnnxGeneralTTS) hi?n b? comment/disabled.

**Runner / helper (không ph?i ServiceBase):** `piper_runner.py` (Piper qua sherpa_onnx, JSON stdin/stdout), `kokoro_runner.py`, `sherpa_runner.py`/`sherpa_runner_v2.py` – dùng cho inference offline (MMS/Kokoro). Engine Piper chính trong add-on hi?n dùng `piper.exe` subprocess trong `service_piper.py`.

---

## ?? Ki?n Trúc D? Án

### C?u trúc thu m?c

```
Superfreetts/                       # Thu m?c g?c addon (ho?c ID s? trong addons21/)
+-- __init__.py                     # Entry point, thêm path và import superfreetts_addon
+-- meta.json                       # C?u hình Anki, min/max version, config addon
¦
+-- superfreetts_addon/             # Code chính
¦   +-- __init__.py                 # Setup logging, config, ServiceManager, SuperFreeTTS, gui.init
¦   +-- superfreetts.py             # ? CORE – SuperFreeTTS class: text extraction, process_batch_audio, presets
¦   +-- batch_executor.py           # ? ASYNC – UnifiedBatchExecutor & MultiEngineExecutor (Producer-Consumer pattern)
¦   +-- cpu_utils.py                # CPU info & concurrency validation
¦   +-- performance_tracker.py      # Tracking batch performance & latency
¦   +-- batch_progress_ui.py        # UI for batch progress and status
¦   +-- servicemanager.py           # TTS Service Management (lazy loading)
¦   +-- anki_utils.py               # Anki API interaction
¦   +-- gui.py                      # Menu and main UI actions
¦   +-- ...
¦   +-- cloudlanguagetools.py       # CloudLanguageTools (Super Free TTS: disabled)
¦   +-- constants_events.py         # Event names cho stats
¦   +-- sentry_utils.py             # Sentry filter (crash reporting)
¦   ¦
¦   +-- services/                   # Engine TTS & t? di?n
¦   ¦   +-- service_edgetts.py      # EdgeTTS (online)
¦   ¦   +-- service_piper.py        # Piper (offline, .onnx + .onnx.json, data/piper_models)
¦   ¦   +-- service_kokoro.py       # Kokoro (offline, data/kokoro_engine)
¦   ¦   +-- service_mms.py          # MMS (offline, 1100+ ngôn ng?)
¦   ¦   +-- service_googletranslate.py
¦   ¦   +-- service_windows.py      # Windows SAPI
¦   ¦   +-- service_macos.py
¦   ¦   +-- service_espeakng.py
¦   ¦   +-- service_cambridge.py, service_oxford.py, service_duden.py, service_dwds.py
¦   ¦   +-- service_youdao.py, service_spanishdict.py
¦   ¦   +-- service_naver.py        # Paid – không load trong Super Free TTS
¦   ¦   +-- service_onnx_general.py # OnnxGeneralTTS (hi?n disabled)
¦   ¦   +-- voicelist.py            # VOICE_LIST (paid voices, reference)
¦   ¦   +-- piper_runner.py         # Optional Piper runner (sherpa_onnx, stdin JSON)
¦   ¦   +-- kokoro_runner.py        # Kokoro inference
¦   ¦   +-- sherpa_runner.py / sherpa_runner_v2.py  # Sherpa-ONNX (MMS/Kokoro)
¦   ¦   +-- __init__.py
¦   ¦
¦   +-- data/                       # D? li?u add-on (t?o t?i runtime n?u c?n)
¦   ¦   +-- piper_models/           # Model Piper (.onnx + .onnx.json) – m?c d?nh ho?c config
¦   ¦   +-- piper_engine/           # Piper binary (sau Setup Piper)
¦   ¦   +-- kokoro_engine/           # Kokoro Python/env (n?u dùng)
¦   ¦
¦   +-- component_*.py              # UI components (nhi?u file)
¦   ¦   +-- component_batch.py      # Add Audio (Collection), batch preview
¦   ¦   +-- component_batch_preview.py
¦   ¦   +-- component_easy.py       # Easy mode
¦   ¦   +-- component_unified_settings.py  # ? NEW (P0) – Unified Settings dialog (Services + Preferences in QTabWidget)
¦   ¦   +-- component_configuration.py  # Services Configuration (enable/disable, path Piper/Kokoro/MMS)
¦   ¦   +-- component_services_configuration.py
¦   ¦   +-- component_piper_setup.py    # Setup Piper engine + Manage Voices
¦   ¦   +-- component_piper_manager.py  # Piper: t?i gi?ng t? HuggingFace (voices.json)
¦   ¦   +-- component_kokoro_manager.py # Kokoro: qu?n lý engine/gi?ng
¦   ¦   +-- component_mms_manager.py    # MMS: cài d?t ngôn ng? (1100+)
¦   ¦   +-- component_onnx_manager.py   # ONNX models (n?u b?t)
¦   ¦   +-- component_voiceselection.py # Ch?n voice (single/random/priority)
¦   ¦   +-- component_voiceselection_easy.py
¦   ¦   +-- component_realtime.py   # Realtime TTS config
¦   ¦   +-- component_realtime_source.py, component_realtime_side.py
¦   ¦   +-- component_presetmappingrules.py, component_mappingrule.py
¦   ¦   +-- component_choosepreset.py, component_choose_easy_advanced.py
¦   ¦   +-- component_source.py, component_source_easy.py
¦   ¦   +-- component_target.py, component_target_easy.py
¦   ¦   +-- component_text_processing.py
¦   ¦   +-- component_label_preview.py
¦   ¦   +-- component_preferences.py   # Preferences (batch_concurrency, cache, UI language)
¦   ¦   +-- component_errorhandling.py
¦   ¦   +-- component_about.py, component_shortcuts.py
¦   ¦   +-- component_common.py
¦   ¦   +-- component_trialsignup.py, component_superfreettpro.py
¦   ¦   +-- ...
¦   ¦
¦   +-- external/                   # (n?u n?m trong addon) Thu vi?n: aiohttp, edge_tts, requests, ...
¦
+-- external/                       # Thu vi?n bên th? 3 (có th? ? ngoài superfreetts_addon)
¦   +-- aiohttp/, edge_tts/, gtts/, requests/, comtypes/, ...
¦
+-- user_files/                     # Cache âm thanh (hash-based: superfreetts-{hash}.mp3)
+-- UPGRADE_IDEAS.md                # G?i ý nâng c?p (hi?n t?i: t?i uu load add-on)
+-- PROJECT_DOCUMENTATION.md        # Tài li?u này
```

### Lu?ng ho?t d?ng chính

#### 1. Kh?i d?ng Addon (dã t?i uu lazy load)

```
Anki starts
    ?
__init__.py (root) ? sys.path, import superfreetts_addon
    ?
superfreetts_addon/__init__.py
    +-? Setup logging (logging_utils)
    +-? get_configuration() / save_configuration() (user_uuid, config)
    +-? (Optional) Sentry crash reporting (disabled trong Lite)
    +-? Import anki_utils, servicemanager, superfreetts, gui
    +-? ServiceManager(services_dir, package_name, allow_test_services=False)
    +-? SuperFreeTTS(ankiutils, service_manager)
    +-? service_manager.set_config_provider(hyper_tts)
    ¦   ?? Không g?i init_services() hay configure() t?i dây – lazy load
    +-? gui.init(hyper_tts)  ? menus, actions

L?n d?u c?n dùng TTS (m? Configuration, Generate, ho?c g?i get_tts_audio / full_voice_list):
    +-? service_manager.ensure_initialized()
        +-? init_services()  ? import toàn b? service_*.py, instantiate (ch? free)
        +-? _initialized = True
        +-? configure(config_provider.get_configuration())
```

#### 2. Thêm Audio (Collection Mode)

```
User clicks "Add Audio" button in editor
    ?
gui.py: run_hypertts_apply()
    ?
component_easy.py ho?c component_batch.py
    ?
HyperTTS.editor_note_add_audio()
    +-? get_source_text() - L?y text t? note
    +-? process_text() - X? lý text (strip HTML, etc.)
    +-? get_audio_file()
    ¦   +-? choose_voice() - Ch?n voice
    ¦   +-? generate_audio_write_file()
    ¦       +-? servicemanager.get_tts_audio()
    ¦       ¦   +-? service_edgetts.py (ho?c service khác)
    ¦       +-? Write to user_files/superfreetts-{hash}.mp3
    +-? get_collection_sound_tag() - T?o [sound:filename.mp3]
    +-? Update note field v?i sound tag
```

#### 3. Thêm Audio (Realtime Mode)

```
User configures Realtime TTS
    ?
component_realtime.py
    ?
HyperTTS.persist_realtime_config_update_note_type()
    +-? Save realtime config
    +-? Build TTS tag: {{tts en voices=HyperTTS:Field}}
    +-? Insert vào card template (qfmt/afmt)
        ?
When reviewing card
    ?
Anki calls tts_player
    ?
ttsplayer.py: AnkiHyperTTSPlayer
    +-? Extract TTS tag info
    +-? HyperTTS.get_audio_filename_tts_tag()
    +-? Generate & play audio
```

### Các thành ph?n chính

#### 1. **HyperTTS Class** (`superfreetts.py`)

Core business logic, x? lý:
- L?y text t? note (simple/template/advanced template)
- X? lý text (HTML to text, strip brackets, cloze)
- T?o audio file (v?i caching d?a trên hash)
- Qu?n lý presets, mapping rules
- C?u hình realtime TTS

**Key methods:**
- `process_note_audio()`: X? lý 1 note, t?o audio
- `get_audio_file()`: T?o audio file t? text + voice
- `editor_note_add_audio()`: Thêm audio vào note trong editor
- `save_preset()`, `load_preset()`: Qu?n lý presets

#### 2. **ServiceManager** (`servicemanager.py`)

Qu?n lý các d?ch v? TTS, **lazy init** d? add-on load nhanh:
- **Lazy load:** Không g?i `init_services()`/`configure()` lúc add-on load; ch? ch?y khi l?n d?u c?n (m? Configuration/Generate, ho?c `get_tts_audio`/`full_voice_list`).
- Discovery: quét `services/service_*.py`, import module, instantiate class k? th?a `ServiceBase` (b? qua `service_fee == paid` và test_service).
- Th? t? hi?n th?: EdgeTTS ? PiperTTS ? KokoroTTS ? MmsTTS ? Others.

**Key methods:**
- `set_config_provider(hyper_tts)`: Gán provider d? lazy init g?i `get_configuration()` khi c?n.
- `ensure_initialized()`: G?i m?t l?n khi c?n; ch?y `init_services()` r?i `configure(config)`.
- `init_services()`: `import_services()` + `instantiate_services()` (ch? free).
- `configure(configuration_model)`: Gán enabled và service_config cho t?ng service.
- `get_tts_audio()`, `full_voice_list()`, `get_service_voice_list()`, `locate_voice()`, `deserialize_voice()`: Ð?u g?i `ensure_initialized()` tru?c khi dùng `self.services`.
- `clear_voice_list_cache()`: Xóa cache `get_service_voice_list` và `locate_voice` (sau khi t?i Piper/Kokoro ho?c d?i config).
- `service_exists()`, `get_service()`, `get_all_services()`, `service_configuration_options()`: Cung d?m b?o dã init.

#### 3. **GUI Components** (`component_*.py`)

M?i component là 1 ph?n UI riêng bi?t:

- **component_batch.py**: Dialog "Add Audio (Collection)"
  - Ch?n source field, template
  - Ch?n target field
  - Ch?n voice(s)
  - Preview và apply cho nhi?u notes

- **component_easy.py**: Easy mode dialog
  - UI don gi?n hon cho ngu?i dùng m?i
  - T? d?ng ch?n field hi?n t?i
  - Ch? c?n ch?n voice và click OK

- **component_realtime.py**: Realtime TTS configuration
  - C?u hình TTS tag trong card template
  - Ch?n field d? phát âm
  - C?u hình cho front/back c?a card

- **component_presetmappingrules.py**: Preset mapping rules
  - Liên k?t preset v?i Note Type ho?c Deck+Note Type
  - Cho phép auto-apply preset d?a trên rule

- **component_voiceselection.py**: Voice selection UI
  - Ch?n voice t? danh sách (filter by language/service)
  - Ch?n voice mode: single, random, priority

#### 4. **Services** (`services/service_*.py`)

M?i engine k? th?a **`ServiceBase`** (`service.py`), khai báo `service_type` (tts/dictionary), `service_fee` (free/paid), và implement:

- `voice_list() -> List[TtsVoice_v3]`: Tr? v? danh sách gi?ng (dùng `voice.build_voice_v3(name, gender, language, service, voice_key, options)`).
- `get_tts_audio(source_text, voice: TtsVoice_v3, options) -> bytes`: Sinh audio t? text.
- `configuration_options() -> dict`: Key ? (type, label [, default]) cho UI config (directory, bool, int, …).

**Engine TTS chính:**
- **service_edgetts.py**: Edge TTS (async, `edge_tts`), nhi?u gi?ng/ngôn ng?.
- **service_piper.py**: Piper (offline). Config: `models_path` (thu m?c .onnx + .onnx.json), `debug_logging`. M?c d?nh: `data/piper_models`, engine t? Setup Piper. Voice list d?c t? file JSON, map `AudioLanguage`, suy gi?i tính t? dataset/filename.
- **service_kokoro.py**: Kokoro (offline). Config: `engine_path` (python/engine), `num_threads`, `use_gpu`, `debug_logging`. Gi?ng t? engine.
- **service_mms.py**: MMS (offline). Config: `python_path`, `num_threads`, `use_gpu`, `debug_logging`. H? tr? 1100+ ngôn ng?, cài qua component_mms_manager.
- **service_googletranslate.py**: Google Translate TTS.
- **service_windows.py** / **service_macos.py** / **service_espeakng.py**: H? th?ng / eSpeak-ng.

**T? di?n:** Cambridge, Oxford, Duden, DWDS, Youdao, SpanishDict (free). Naver (paid – không load).

### Config Models (`config_models.py`)

Ð?nh nghia c?u trúc d? li?u cho:

- **Configuration**: C?u hình chung (user_uuid, service_enabled, service_config, presets, mapping_rules, realtime_config, …).
- **Preferences**: `ui_language` (en/vi), `cache_retention_days`, `cache_enabled`, `batch_concurrency` (s? thread batch), `error_handling` (disable_ssl_verification, realtime_tts_errors_dialog_type), keyboard_shortcuts.
- **BatchConfig** (Preset): Source (simple/template/advanced_template), Target (target_field, remove_sound_tag, text_and_sound_tag, insert_location), VoiceSelection, Text processing.
- **VoiceSelection**: Ch? d? single / random / priority; danh sách voice (voice_id + options + weight).
- **VoiceWithOptions**: voice + options (vd. format mp3/ogg).
- **MappingRule**: Liên k?t preset v?i deck/note type.
- **RealtimeConfig**: C?u hình realtime TTS (front/back, source, voice).
- **AudioLanguage / Language**: Enum ngôn ng? (dùng trong `voice.py` và `languages.py`).

### Voice & Options

- **voice.py**: `TtsVoice_v3` (name, voice_key, service, gender, audio_languages, options, service_fee), `TtsVoiceId_v3` (voice_key, service), `build_voice_v3(name, gender, language, service, voice_key, options)`, `voice_str(voice)` dùng trong combobox.
- **options.py**: `AudioFormat` (mp3, ogg_vorbis, ogg_opus) – dùng khi ghi file cache (`superfreetts-{hash}.mp3`/`.ogg`).

### Error Handling (`errors.py`)

Custom exceptions: `SourceFieldNotFoundError`, `TargetFieldNotFoundError`, `SourceTextEmpty`, `NoVoicesAdded`, `AudioNotFoundError`, `PresetNotFound`, `VoiceNotFound`, `VoiceIdNotFound`, `MissingServiceConfiguration`, `RequestError` (TTS l?i), …  
**ErrorManager** dùng d? wrap action và hi?n th? l?i qua dialog/tooltip.

---

## ?? Hu?ng D?n S? D?ng

### Cài d?t

1. **T?i addon**:
   - Copy thu m?c này vào `Anki2/addons21/`
   - Ho?c t? AnkiVN (xem hu?ng d?n t?i ankivn.com)

2. **Restart Anki**

3. **C?u hình d?ch v? TTS** (l?n d?u):
   - Menu: `AnkiVN` ? `Super Free TTS Settings` ? Click tab "Services"
   - B?t engine c?n dùng: EdgeTTS (online, ? khuyên dùng), Piper/Kokoro/MMS (offline c?n setup du?ng d?n ho?c Setup/Manage), Google Translate, Windows/macOS/eSpeak-ng.
   - **Piper:** Có th? d? tr?ng "Piper Models Directory" (dùng m?c d?nh `data/piper_models`) ho?c ch?n thu m?c ch?a file `.onnx` + `.onnx.json`. Dùng "Setup Piper" d? cài engine, "Manage Voices" d? t?i gi?ng t? HuggingFace.
   - **Kokoro / MMS:** Ch? d?nh du?ng d?n Python/engine n?u c?n (xem component_kokoro_manager, component_mms_manager).

### S? d?ng co b?n

#### 1. Easy Mode (Ðon gi?n)

Dùng cho ngu?i m?i, thêm audio vào t?ng note riêng l?:

1. M? note editor (Add card ho?c Browser)
2. Click nút **speaker icon** (Add Audio)
3. Ch?n voice t? dropdown
4. Click "Add Audio"
5. Audio du?c thêm vào field hi?n t?i

#### 2. Collection Mode (Nâng cao)

Thêm audio cho nhi?u notes cùng lúc:

1. M? Browser, ch?n các notes
2. Menu: `Super Free TTS` ? `Add Audio (Collection)...`
3. Configure:
   - **Source**: Field ch?a text c?n t?o audio
   - **Voice**: Ch?n voice TTS
   - **Target**: Field d? chèn sound tag
   - **Text Processing**: Tùy ch?n x? lý text
4. Preview (nghe th?)
5. Click "Apply" d? thêm audio cho t?t c? notes

#### 3. Preset Mapping Rules

T? d?ng apply preset d?a trên Note Type ho?c Deck:

1. Click nút **gear icon** (Settings) trong editor
2. Add rule:
   - Ch?n Note Type (ho?c Deck + Note Type)
   - Ch?n/t?o preset
3. Save rule
4. T? gi?, khi click "Add Audio" button, preset s? t? d?ng apply

#### 4. Realtime TTS

Audio t? d?ng phát khi review card (không c?n thêm vào note):

1. Ch?n 1 note trong Browser
2. Menu: `Super Free TTS` ? `Add Audio (Realtime)...`
3. Configure:
   - Front side: Field nào s? d?c, voice nào
   - Back side: Field nào s? d?c, voice nào
4. Apply
5. TTS tag `{{tts ...}}` du?c thêm vào card template
6. Khi review, audio t? d?ng phát

### Các tính nang nâng cao

#### Text Processing

- **HTML to Text**: Lo?i b? HTML tags
- **Strip Brackets**: Lo?i b? [...]
- **Strip Cloze**: Lo?i b? cloze {{c1::...}}
- **SSML Characters**: Escape ký t? d?c bi?t cho SSML
- **Text Replacement**: Thay th? text tru?c khi t?o audio

#### Voice Selection Modes

- **Single**: Ch?n 1 voice c? d?nh
- **Random**: Ch?n ng?u nhiên t? danh sách voices (có th? set weight)
- **Priority**: Th? voice theo th? t?, fallback n?u không t?o du?c audio

#### Template Source

Combine nhi?u fields:
- **Simple Template**: `{Field1} {Field2}`
- **Advanced Template**: Python code (disabled trong b?n Lite vì lý do b?o m?t)

---

## ????? Hu?ng D?n Phát Tri?n

### Setup môi tru?ng phát tri?n

#### 1. Clone/Copy d? án

```bash
# Thu m?c addon thu?ng ? dây (Windows):
cd %APPDATA%\Anki2\addons21\655806401

# Ho?c (macOS/Linux):
cd ~/Library/Application Support/Anki2/addons21/655806401
```

#### 2. Dependency management

Dependencies dã du?c bundle trong thu m?c `external/`. N?u c?n thêm dependency:

```bash
pip install <package> -t external/
```

#### 3. Enable debug logging

Set environment variable:

```bash
# Windows (PowerShell)
$env:HYPER_TTS_DEBUG_LOGGING="enable"

# macOS/Linux
export HYPER_TTS_DEBUG_LOGGING="enable"
```

Ho?c log to file:

```bash
$env:HYPER_TTS_DEBUG_LOGGING="file"
$env:HYPER_TTS_DEBUG_LOGFILE="C:\path\to\superfreetts.log"
```

#### 4. Restart Anki và test

```bash
# Anki s? load addon t? thu m?c này
# M?i thay d?i code c?n restart Anki
```

### C?u trúc code guidelines

#### 1. T? ch?c code

- **Business logic**: Nên ? `superfreetts.py` ho?c `servicemanager.py`
- **UI logic**: Nên ? các `component_*.py`
- **Utilities**: Nên ? các `*_utils.py`
- **Models**: Nên ? `config_models.py`
- **Constants**: Nên ? `constants.py`

#### 2. Error handling

Luôn s? d?ng custom exceptions t? `errors.py`:

```python
# Good
if field not in note:
    raise errors.TargetFieldNotFoundError(field)

# Bad
if field not in note:
    raise Exception(f"Field {field} not found")
```

Wrap user-facing actions v?i `ErrorManager`:

```python
with superfreetts.error_manager.get_single_action_context('Action Name'):
    # Your code here
```

#### 3. Configuration

M?i c?u hình c?n:
- Ð?nh nghia model trong `config_models.py`
- Implement `serialize()` và `deserialize()`
- Luu vào config qua `anki_utils.write_config()`

#### 4. Logging

```python
from . import logging_utils
logger = logging_utils.get_child_logger(__name__)

logger.debug('Debug message')
logger.info('Info message')
logger.error('Error message')
```

### Thêm d?ch v? TTS m?i

#### Bu?c 1: T?o file service

T?o `superfreetts_addon/services/service_yourservice.py`. Class **k? th?a `ServiceBase`** và khai báo **`service_fee = constants.ServiceFee.free`** (n?u paid thì add-on s? không load).

```python
from typing import List
from superfreetts_addon import service, voice as voice_module, constants, languages

class YourServiceTTS(service.ServiceBase):
    def __init__(self):
        service.ServiceBase.__init__(self)

    @property
    def name(self):
        return "YourServiceTTS"

    @property
    def service_type(self):
        return constants.ServiceType.tts

    @property
    def service_fee(self):
        return constants.ServiceFee.free  # b?t bu?c free d? du?c load

    def configuration_options(self):
        return {
            'api_key': ('string', 'API Key', ''),
            'debug_logging': ('bool', 'Debug Logging', False),
        }

    def voice_list(self) -> List[voice_module.TtsVoice_v3]:
        # L?y danh sách t? API ho?c file; m?i gi?ng t?o b?ng build_voice_v3
        voices = []
        # ... fetch list ...
        voices.append(voice_module.build_voice_v3(
            name="Display Name",
            gender=constants.Gender.Female,
            language=languages.AudioLanguage.en_US,
            service=self,
            voice_key="voice_id",
            options={}
        ))
        return voices

    def get_tts_audio(self, source_text, voice: voice_module.TtsVoice_v3, options):
        # G?i API / engine, tr? v? bytes (audio)
        # voice.voice_key, voice.service
        return response_content  # bytes
```

- **`build_voice_v3`** (trong `voice.py`): Tham s? `name`, `gender`, `language`, `service`, `voice_key`, `options`. Thi?u `gender` s? gây l?i.
- **Config:** Key trong `configuration_options()` dùng trong UI; giá tr? d?c b?ng `self.get_configuration_value_optional(key, default)` / `get_configuration_value_mandatory(key)`.

#### Bu?c 2: Register service

Service **t? d?ng du?c discovery** n?u file d?t tên `service_*.py` trong `services/`. Không c?n dang ký tay. N?u mu?n th? t? hi?n th?: thêm tên class vào `priority_order` trong `servicemanager.instantiate_services()` (vd. `["EdgeTTS", "PiperTTS", "KokoroTTS", "MmsTTS", "YourServiceTTS"]`).

Test:

```python
# Anki Debug Console (Tools > Debug Console)
from superfreetts_addon.servicemanager import ServiceManager
from superfreetts_addon import constants
import os
path = os.path.join(os.path.dirname(__file__), 'services')  # di?u ch?nh path
sm = ServiceManager(path, 'superfreetts_addon.services', False)
sm.set_config_provider(hyper_tts)  # n?u có
sm.ensure_initialized()
voices = sm.full_voice_list()
print([v for v in voices if v.service == 'YourServiceTTS'])
```

### Testing

#### Manual testing

1. T?o test deck v?i vài notes
2. Configure service trong UI
3. Test t?ng workflow:
   - Easy mode
   - Collection mode
   - Realtime mode
   - Preset mapping rules

#### Unit testing (hi?n t?i chua có)

D? án không còn thu m?c `test_services/` (dã xóa). Có th? thêm test b?ng pytest ho?c unittest; khi ch?y test c?n set `sys._pytest_mode = True` d? add-on không ch?y block Anki (vd. Sentry). Test service: instantiate class service, g?i `voice_list()` và `get_tts_audio(source_text, voice, {})` v?i voice l?y t? `voice_list()[0]`.

### Code review checklist

Tru?c khi commit code:

- [ ] Code có follow c?u trúc hi?n t?i không?
- [ ] Có thêm logging phù h?p không?
- [ ] Error handling dúng cách (dùng custom exceptions)?
- [ ] Config du?c save/load dúng không?
- [ ] UI có responsive và user-friendly không?
- [ ] Code có comments cho ph?n ph?c t?p không?
- [ ] Ðã test manually các workflow chính chua?

### Quy t?c c?n tuân theo

#### 1. B?o m?t

- **KHÔNG bao gi?** execute Python code do user nh?p (Advanced Template dã b? disable)
- **KHÔNG log** API keys ho?c sensitive data
- **Validate** t?t c? user input

#### 2. Tuong thích Anki

- Addon ph?i tuong thích v?i:
  - Anki 2.1.50 - 2.1.x (check `meta.json`: `min_point_version: 5, max_point_version: 241100`)
- S? d?ng Anki API dúng cách (qua `anki_utils.py`)

#### 3. Performance

- **Lazy load add-on:** Services **không** du?c load lúc Anki kh?i d?ng. Ch? khi l?n d?u c?n (m? Configuration/Generate, ho?c g?i `get_tts_audio`/`full_voice_list`), `ServiceManager.ensure_initialized()` m?i ch?y `init_services()` và `configure()`.
- **New Executor Architecture:** S? d?ng `MultiEngineExecutor` (`batch_executor.py`) v?i các pool riêng bi?t cho t?ng engine.
- **Concurrency Capping:** 
    - **EdgeTTS**: Ðu?c gi?i h?n c?ng ? **3 workers** d? tránh b? Microsoft rate-limit.
    - **Offline Engines**: S? d?ng `BoundedThreadPoolExecutor` d? gi?i h?n hàng ch? và qu?n lý tài nguyên (RAM/CPU). Ð? xu?t 4-8 workers cho CPU Ryzen 7.
- **Interleaved Batching:** Áp d?ng mô hình producer-consumer d? b?t d?u t?o audio ngay khi có yêu c?u, không d?i n?p xong toàn b? danh sách, giúp gi?m dáng k? d? tr? kh?i d?ng (startup latency).
- **Cache audio files:** `generate_audio_write_file()` dùng hash `(source_text, voice_id, options)` ? file `superfreetts-{hash}.mp3`; n?u dã t?n t?i thì không g?i TTS l?i.
- **Voice list cache:** `get_service_voice_list()` và `locate_voice()` dùng `functools.lru_cache`.

#### 4. UI/UX

- **Consistent v?i Anki**: Dùng PyQt components chu?n
- **Error messages rõ ràng**: User ph?i hi?u du?c l?i gì
- **Progress indicators**: Cho operations lâu (batch processing)

#### 5. HyperTTS Lite vs Pro

B?n Lite c?n disable m?t s? features:

```python
# constants.py
ENABLE_SENTRY_CRASH_REPORTING = True  # Set to False for Lite

# superfreetts.py
def expand_advanced_template(self, note, source_template):
    raise errors.HyperTTSError("Advanced Template (Python) không h? tr? trong b?n Lite")
```

---

## ?? Tài Li?u & Tham Kh?o

### Tài li?u trong repo

- **UPGRADE_IDEAS.md**: G?i ý nâng c?p (hi?n t?i ch? t?i uu t?c d? load add-on – lazy load services).
- **PROJECT_DOCUMENTATION.md**: Tài li?u này.

### API Documentation

- **Anki Addon API**: https://addon-docs.ankiweb.net/
- **PyQt5**: https://www.riverbankcomputing.com/static/Docs/PyQt5/
- **Edge TTS**: https://github.com/rany2/edge-tts

### Service APIs (Mi?n phí)

- **Edge TTS**: https://github.com/rany2/edge-tts
- **gTTS (Google Translate)**: https://github.com/pndurette/gTTS
- **eSpeak-ng**: https://github.com/espeak-ng/espeak-ng

### Anki Resources

- **Anki Manual**: https://docs.ankiweb.net/
- **Addon Development**: https://addon-docs.ankiweb.net/intro.html

---

## ?? Ðóng Góp

N?u b?n mu?n dóng góp vào d? án:

1. Fork d? án (n?u có repository)
2. T?o branch m?i: `git checkout -b feature/your-feature`
3. Làm theo [Hu?ng D?n Phát Tri?n](#-hu?ng-d?n-phát-tri?n)
4. Test k? các thay d?i
5. Commit v?i message rõ ràng
6. T?o Pull Request

### Ý tu?ng dóng góp

- Thêm d?ch v? TTS m?i
- Improve UI/UX
- Thêm text processing features
- Vi?t tests
- Improve documentation
- Bug fixes

---

## ?? Ða ngôn ng? giao di?n (UI)

Super Free TTS hi?n h? tr? **2 ngôn ng? giao di?n**: **English** và **Ti?ng Vi?t**.

- **Cách d?i ngôn ng? giao di?n**:
  1. Vào menu `Tools ? Super Free TTS: Preferences`  
  2. ? nhóm **Language / Ngôn ng?**, ch?n:
     - `English` d? dùng giao di?n ti?ng Anh
     - `Ti?ng Vi?t` d? dùng giao di?n ti?ng Vi?t
  3. Nh?n **Apply** và m? l?i các h?p tho?i c?a Super Free TTS (Easy, Collection, Configuration, Realtime, Preset Rules, Voice Selection) d? th?y thay d?i.

- **Luu ý cho developer**:
  - B?ng d?ch n?m trong file `[superfreetts_addon/i18n.py](superfreetts_addon/i18n.py)`.
  - Khi thêm text m?i ra UI, hãy dùng `i18n.get_text("some_key", lang)` thay vì hard-code chu?i.
  - Quy u?c d?t key:
    - Nút b?m: `button_*` ho?c `easy_button_*`, `batch_button_*`, `voice_button_*`
    - Tiêu d? dialog: `dialog_*_title`
    - Nhóm / groupbox / label: `*_group_*`, `label_*`

---

## ?? License

Super Free TTS du?c phát tri?n b?i **Paul from AnkiVN**. 100% mi?n phí cho c?ng d?ng Anki Vi?t Nam.

---

## ?? Liên H? & H? Tr?

- **Website**: https://ankivn.com
- **Tác gi?**: Paul from AnkiVN
- **Issues**: Báo cáo l?i ho?c d? xu?t tính nang qua AnkiVN

---

**Tài li?u c?p nh?t**: 2026-04-11  
**Phiên b?n addon (version.py)**: 1.0  
**Tác gi?**: Paul from AnkiVN  
