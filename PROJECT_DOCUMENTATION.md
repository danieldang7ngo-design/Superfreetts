# Super Free TTS by Daniel from AnkiVN - Tài Liệu Dự Án

> Tài liệu này mô tả chi tiết dự án Super Free TTS. Để xem nhanh tóm tắt kiến trúc và định hướng dành riêng cho AI Agents, vui lòng đọc [AI_SUMMARY.md](./AI_SUMMARY.md).

## 📋 Mục Lục

- [Tổng Quan](#-tổng-quan)
- [Công Nghệ Sử Dụng](#-công-nghệ-sử-dụng)
- [Kiến Trúc Dự Án](#-kiến-trúc-dự-án)
- [Hướng Dẫn Sử Dụng](#-hướng-dẫn-sử-dụng)
- [Hướng Dẫn Phát Triển](#-hướng-dẫn-phát-triển)

---

## 🎯 Tổng Quan

### Dự án là gì?

**Super Free TTS** là một addon (tiện ích mở rộng) **100% MIỄN PHÍ** cho [Anki](https://apps.ankiweb.net/) - ứng dụng học flashcard phổ biến. Addon này giúp người dùng tự động thêm âm thanh text-to-speech (TTS) vào thẻ học của họ.

**Tác giả**: Daniel from AnkiVN

### Giải quyết vấn đề gì?

Khi học ngôn ngữ hoặc bất kỳ môn học nào cần phát âm, việc có âm thanh trên thẻ học rất quan trọng. Tuy nhiên, việc thu âm hoặc tìm file âm thanh cho từng thẻ rất tốn thời gian. Super Free TTS giải quyết vấn đề này bằng cách:

- **Tự động tạo âm thanh** từ văn bản trên thẻ học
- **Hỗ trợ nhiều engine TTS MIỄN PHÍ**: EdgeTTS, Piper (offline), Kokoro (offline), MMS (offline, 1100+ ngôn ngữ), Google Translate, Windows SAPI, macOS TTS, eSpeak-ng
- **Linh hoạt**: Thêm âm thanh từng thẻ hoặc hàng loạt; preset mapping rules; realtime TTS
- **100% Miễn phí**: Chỉ load engine free, không cần API key

### Thông tin

- **Tên addon**: Super Free TTS
- **Tác giả**: Daniel from AnkiVN
- **Phiên bản hiện tại**: 1.0 (trong `version.py`; có thể khác với số hiển thị trong Anki)
- **Thư mục add-on**: Có thể là `Superfreetts` hoặc ID số (vd. 655806401) trong `Anki2/addons21/`
- **Website**: ankivn.com
- **Tương thích Anki**: `min_point_version: 5`, `max_point_version: 241100` (meta.json)

---

## 🛠 Công Nghệ Sử Dụng

### Ngôn ngữ lập trình

- **Python 3.x**: Ngôn ngữ chính của dự án
- **PyQt5/PyQt6**: Framework để tạo giao diện người dùng (UI)
- **HTML/CSS/JavaScript**: Tạo giao diện web trong các dialog của Anki

### Thư viện chính

#### Core Dependencies (trong thư mục `external/`)

1. **aiohttp (3.13.3)**: HTTP client/server bất đồng bộ cho Python
   - Dùng để gọi API các dịch vụ TTS

2. **edge-tts (7.2.7)**: Thư viện Python để sử dụng Microsoft Edge TTS
   - Dịch vụ TTS miễn phí chất lượng cao

3. **gtts**: Google Text-to-Speech
   - Dịch vụ TTS miễn phí từ Google

4. **requests**: HTTP library đơn giản
   - Gọi API các dịch vụ TTS miễn phí

5. **tabulate (0.9.0)**: Tạo bảng dữ liệu đẹp
   - Hiển thị danh sách voices

6. **comtypes** (Windows only): COM interface
   - Tích hợp với Windows SAPI TTS

### Dịch vụ TTS được hỗ trợ (TẤT CẢ MIỄN PHÍ)

Dự án chỉ load **các dịch vụ TTS có `service_fee = free`** (service trả phí như Naver bị bỏ qua khi khởi tạo).

#### Engine TTS chính (thứ tự ưu tiên trong UI)
| Engine | Mô tả | Online/Offline |
|--------|--------|-----------------|
| **EdgeTTS** | Microsoft Edge TTS (⭐ chất lượng cao) | Online |
| **PiperTTS** | Piper (Rhasspy) – giọng đa ngôn ngữ, model .onnx | Offline |
| **KokoroTTS** | Kokoro – giọng tự nhiên, chạy qua engine riêng | Offline |
| **MmsTTS** | MMS (Massively Multilingual Speech) – 1100+ ngôn ngữ | Offline |
| **GoogleTranslate** | Google Translate TTS | Online |
| **Windows** | Windows SAPI (chỉ Windows) | Offline |
| **MacOS** | macOS built-in TTS (chỉ macOS) | Offline |
| **ESpeakNg** | eSpeak-ng, open-source | Offline |

#### Dịch vụ từ điển (pronunciation, `service_type = dictionary`)
- **Cambridge**, **Oxford**, **Duden**, **DWDS**, **Youdao**, **SpanishDict** – tất cả miễn phí.
- **Naver**: trong code là `service_fee = paid` nên **không được load** trong Super Free TTS.

#### File service tương ứng (trong `services/`)
- `service_edgetts.py`, `service_piper.py`, `service_kokoro.py`, `service_mms.py`, `service_googletranslate.py`, `service_windows.py`, `service_macos.py`, `service_espeakng.py`
- Từ điển: `service_cambridge.py`, `service_oxford.py`, `service_duden.py`, `service_dwds.py`, `service_youdao.py`, `service_spanishdict.py`
- `service_naver.py` (paid – bị bỏ qua). `service_onnx_general.py` (OnnxGeneralTTS) hiện bị comment/disabled.

**Runner / helper (không phải ServiceBase):** `piper_runner.py` (Piper qua sherpa_onnx, JSON stdin/stdout), `kokoro_runner.py`, `sherpa_runner.py`/`sherpa_runner_v2.py` – dùng cho inference offline (MMS/Kokoro). Engine Piper chính trong add-on hiện dùng `piper.exe` subprocess trong `service_piper.py`.

---

## 🏗 Kiến Trúc Dự Án

### Cấu trúc thư mục

```
Superfreetts/                       # Thư mục gốc addon (hoặc ID số trong addons21/)
├── __init__.py                     # Entry point, thêm path và import superfreetss_addon
├── meta.json                       # Cấu hình Anki, min/max version, config addon
│
├── superfreetss_addon/             # Code chính
│   ├── __init__.py                 # Setup logging, config, ServiceManager, SuperFreeTTS, gui.init (lazy load services)
│   ├── version.py                  # ANKI_SUPER_FREE_TTS_VERSION (1.0)
│   ├── constants.py                # ServiceType, ServiceFee, BatchMode, enums, CONFIG_ADDON_NAME, DIR_HYPERTTS_ADDON
│   ├── config_models.py            # Configuration, BatchConfig, VoiceSelection, Preferences, v.v.
│   ├── errors.py                   # Custom exceptions, ErrorManager
│   ├── superfreetss.py             # ⭐ CORE – get_audio_file, process_batch_audio, presets, realtime
│   ├── servicemanager.py           # ⭐ Quản lý TTS: lazy init (ensure_initialized), configure, get_tts_audio, full_voice_list, clear_voice_list_cache
│   ├── anki_utils.py               # Tương tác Anki, media, config read/write
│   ├── gui.py                      # Menu (AnkiVN top-level + Tools aliases), actions, dialog entry points
│   ├── service.py                  # ServiceBase abstract: voice_list(), get_tts_audio(), service_fee, configuration_options()
│   ├── voice.py                    # TtsVoice_v3, TtsVoiceId_v3, build_voice_v3, voice_str()
│   ├── languages.py                # Language, AudioLanguage enums (map ngôn ngữ TTS)
│   ├── options.py                  # AudioFormat (mp3, ogg_vorbis, ogg_opus)
│   ├── context.py                  # AudioRequestContext (batch/preview/realtime, batch_uuid)
│   ├── text_utils.py               # Xử lý text (strip HTML, cloze, replace rules)
│   ├── logging_utils.py            # Logger setup
│   ├── stats.py                    # Usage statistics (optional)
│   ├── ttsplayer.py                # Anki TTS tag player (realtime)
│   ├── batch_status.py             # Trạng thái batch (note status, progress)
│   ├── preset_rules_status.py      # Preset mapping rules
│   ├── i18n.py                     # Đa ngôn ngữ UI (en / vi)
│   ├── gui_utils.py                # Helper UI (buttons, font)
│   ├── system_utils.py             # GPU/detect (MMS, Kokoro)
│   ├── cloudlanguagetools.py       # CloudLanguageTools (Super Free TTS: disabled)
│   ├── constants_events.py         # Event names cho stats
│   ├── sentry_utils.py             # Sentry filter (crash reporting)
│   │
│   ├── services/                   # Engine TTS & từ điển
│   │   ├── service_edgetts.py      # EdgeTTS (online)
│   │   ├── service_piper.py        # Piper (offline, .onnx + .onnx.json, data/piper_models)
│   │   ├── service_kokoro.py       # Kokoro (offline, data/kokoro_engine)
│   │   ├── service_mms.py          # MMS (offline, 1100+ ngôn ngữ)
│   │   ├── service_googletranslate.py
│   │   ├── service_windows.py      # Windows SAPI
│   │   ├── service_macos.py
│   │   ├── service_espeakng.py
│   │   ├── service_cambridge.py, service_oxford.py, service_duden.py, service_dwds.py
│   │   ├── service_youdao.py, service_spanishdict.py
│   │   ├── service_naver.py        # Paid – không load trong Super Free TTS
│   │   ├── service_onnx_general.py # OnnxGeneralTTS (hiện disabled)
│   │   ├── voicelist.py            # VOICE_LIST (paid voices, reference)
│   │   ├── piper_runner.py         # Optional Piper runner (sherpa_onnx, stdin JSON)
│   │   ├── kokoro_runner.py        # Kokoro inference
│   │   ├── sherpa_runner.py / sherpa_runner_v2.py  # Sherpa-ONNX (MMS/Kokoro)
│   │   └── __init__.py
│   │
│   ├── data/                       # Dữ liệu add-on (tạo tại runtime nếu cần)
│   │   ├── piper_models/           # Model Piper (.onnx + .onnx.json) – mặc định hoặc config
│   │   ├── piper_engine/           # Piper binary (sau Setup Piper)
│   │   └── kokoro_engine/           # Kokoro Python/env (nếu dùng)
│   │
│   ├── component_*.py              # UI components (nhiều file)
│   │   ├── component_batch.py      # Add Audio (Collection), batch preview
│   │   ├── component_batch_preview.py
│   │   ├── component_easy.py       # Easy mode
│   │   ├── component_unified_settings.py  # ⭐ NEW (P0) – Unified Settings dialog (Services + Preferences in QTabWidget)
│   │   ├── component_configuration.py  # Services Configuration (enable/disable, path Piper/Kokoro/MMS)
│   │   ├── component_services_configuration.py
│   │   ├── component_piper_setup.py    # Setup Piper engine + Manage Voices
│   │   ├── component_piper_manager.py  # Piper: tải giọng từ HuggingFace (voices.json)
│   │   ├── component_kokoro_manager.py # Kokoro: quản lý engine/giọng
│   │   ├── component_mms_manager.py    # MMS: cài đặt ngôn ngữ (1100+)
│   │   ├── component_onnx_manager.py   # ONNX models (nếu bật)
│   │   ├── component_voiceselection.py # Chọn voice (single/random/priority)
│   │   ├── component_voiceselection_easy.py
│   │   ├── component_realtime.py   # Realtime TTS config
│   │   ├── component_realtime_source.py, component_realtime_side.py
│   │   ├── component_presetmappingrules.py, component_mappingrule.py
│   │   ├── component_choosepreset.py, component_choose_easy_advanced.py
│   │   ├── component_source.py, component_source_easy.py
│   │   ├── component_target.py, component_target_easy.py
│   │   ├── component_text_processing.py
│   │   ├── component_label_preview.py
│   │   ├── component_preferences.py   # Preferences (batch_concurrency, cache, UI language)
│   │   ├── component_errorhandling.py
│   │   ├── component_about.py, component_shortcuts.py
│   │   ├── component_common.py
│   │   ├── component_trialsignup.py, component_superfreettpro.py
│   │   └── ...
│   │
│   └── external/                   # (nếu nằm trong addon) Thư viện: aiohttp, edge_tts, requests, ...
│
├── external/                       # Thư viện bên thứ 3 (có thể ở ngoài superfreetss_addon)
│   ├── aiohttp/, edge_tts/, gtts/, requests/, comtypes/, ...
│
├── user_files/                     # Cache âm thanh (hash-based: superfreetss-{hash}.mp3)
├── UPGRADE_IDEAS.md                # Gợi ý nâng cấp (hiện tại: tối ưu load add-on)
└── PROJECT_DOCUMENTATION.md        # Tài liệu này
```

### Luồng hoạt động chính

#### 1. Khởi động Addon (đã tối ưu lazy load)

```
Anki starts
    ↓
__init__.py (root) → sys.path, import superfreetss_addon
    ↓
superfreetss_addon/__init__.py
    ├─→ Setup logging (logging_utils)
    ├─→ get_configuration() / save_configuration() (user_uuid, config)
    ├─→ (Optional) Sentry crash reporting (disabled trong Lite)
    ├─→ Import anki_utils, servicemanager, superfreetss, gui
    ├─→ ServiceManager(services_dir, package_name, allow_test_services=False)
    ├─→ SuperFreeTTS(ankiutils, service_manager)
    ├─→ service_manager.set_config_provider(hyper_tts)
    │   ⚠️ Không gọi init_services() hay configure() tại đây – lazy load
    └─→ gui.init(hyper_tts)  → menus, actions

Lần đầu cần dùng TTS (mở Configuration, Generate, hoặc gọi get_tts_audio / full_voice_list):
    └─→ service_manager.ensure_initialized()
        ├─→ init_services()  → import toàn bộ service_*.py, instantiate (chỉ free)
        ├─→ _initialized = True
        └─→ configure(config_provider.get_configuration())
```

#### 2. Thêm Audio (Collection Mode)

```
User clicks "Add Audio" button in editor
    ↓
gui.py: run_hypertts_apply()
    ↓
component_easy.py hoặc component_batch.py
    ↓
HyperTTS.editor_note_add_audio()
    ├─→ get_source_text() - Lấy text từ note
    ├─→ process_text() - Xử lý text (strip HTML, etc.)
    ├─→ get_audio_file()
    │   ├─→ choose_voice() - Chọn voice
    │   └─→ generate_audio_write_file()
    │       ├─→ servicemanager.get_tts_audio()
    │       │   └─→ service_edgetts.py (hoặc service khác)
    │       └─→ Write to user_files/superfreetss-{hash}.mp3
    ├─→ get_collection_sound_tag() - Tạo [sound:filename.mp3]
    └─→ Update note field với sound tag
```

#### 3. Thêm Audio (Realtime Mode)

```
User configures Realtime TTS
    ↓
component_realtime.py
    ↓
HyperTTS.persist_realtime_config_update_note_type()
    ├─→ Save realtime config
    ├─→ Build TTS tag: {{tts en voices=HyperTTS:Field}}
    └─→ Insert vào card template (qfmt/afmt)
        ↓
When reviewing card
    ↓
Anki calls tts_player
    ↓
ttsplayer.py: AnkiHyperTTSPlayer
    ├─→ Extract TTS tag info
    ├─→ HyperTTS.get_audio_filename_tts_tag()
    └─→ Generate & play audio
```

### Các thành phần chính

#### 1. **HyperTTS Class** (`superfreetss.py`)

Core business logic, xử lý:
- Lấy text từ note (simple/template/advanced template)
- Xử lý text (HTML to text, strip brackets, cloze)
- Tạo audio file (với caching dựa trên hash)
- Quản lý presets, mapping rules
- Cấu hình realtime TTS

**Key methods:**
- `process_note_audio()`: Xử lý 1 note, tạo audio
- `get_audio_file()`: Tạo audio file từ text + voice
- `editor_note_add_audio()`: Thêm audio vào note trong editor
- `save_preset()`, `load_preset()`: Quản lý presets

#### 2. **ServiceManager** (`servicemanager.py`)

Quản lý các dịch vụ TTS, **lazy init** để add-on load nhanh:
- **Lazy load:** Không gọi `init_services()`/`configure()` lúc add-on load; chỉ chạy khi lần đầu cần (mở Configuration/Generate, hoặc `get_tts_audio`/`full_voice_list`).
- Discovery: quét `services/service_*.py`, import module, instantiate class kế thừa `ServiceBase` (bỏ qua `service_fee == paid` và test_service).
- Thứ tự hiển thị: EdgeTTS → PiperTTS → KokoroTTS → MmsTTS → Others.

**Key methods:**
- `set_config_provider(hyper_tts)`: Gán provider để lazy init gọi `get_configuration()` khi cần.
- `ensure_initialized()`: Gọi một lần khi cần; chạy `init_services()` rồi `configure(config)`.
- `init_services()`: `import_services()` + `instantiate_services()` (chỉ free).
- `configure(configuration_model)`: Gán enabled và service_config cho từng service.
- `get_tts_audio()`, `full_voice_list()`, `get_service_voice_list()`, `locate_voice()`, `deserialize_voice()`: Đều gọi `ensure_initialized()` trước khi dùng `self.services`.
- `clear_voice_list_cache()`: Xóa cache `get_service_voice_list` và `locate_voice` (sau khi tải Piper/Kokoro hoặc đổi config).
- `service_exists()`, `get_service()`, `get_all_services()`, `service_configuration_options()`: Cũng đảm bảo đã init.

#### 3. **GUI Components** (`component_*.py`)

Mỗi component là 1 phần UI riêng biệt:

- **component_batch.py**: Dialog "Add Audio (Collection)"
  - Chọn source field, template
  - Chọn target field
  - Chọn voice(s)
  - Preview và apply cho nhiều notes

- **component_easy.py**: Easy mode dialog
  - UI đơn giản hơn cho người dùng mới
  - Tự động chọn field hiện tại
  - Chỉ cần chọn voice và click OK

- **component_realtime.py**: Realtime TTS configuration
  - Cấu hình TTS tag trong card template
  - Chọn field để phát âm
  - Cấu hình cho front/back của card

- **component_presetmappingrules.py**: Preset mapping rules
  - Liên kết preset với Note Type hoặc Deck+Note Type
  - Cho phép auto-apply preset dựa trên rule

- **component_voiceselection.py**: Voice selection UI
  - Chọn voice từ danh sách (filter by language/service)
  - Chọn voice mode: single, random, priority

#### 4. **Services** (`services/service_*.py`)

Mỗi engine kế thừa **`ServiceBase`** (`service.py`), khai báo `service_type` (tts/dictionary), `service_fee` (free/paid), và implement:

- `voice_list() -> List[TtsVoice_v3]`: Trả về danh sách giọng (dùng `voice.build_voice_v3(name, gender, language, service, voice_key, options)`).
- `get_tts_audio(source_text, voice: TtsVoice_v3, options) -> bytes`: Sinh audio từ text.
- `configuration_options() -> dict`: Key → (type, label [, default]) cho UI config (directory, bool, int, …).

**Engine TTS chính:**
- **service_edgetts.py**: Edge TTS (async, `edge_tts`), nhiều giọng/ngôn ngữ.
- **service_piper.py**: Piper (offline). Config: `models_path` (thư mục .onnx + .onnx.json), `debug_logging`. Mặc định: `data/piper_models`, engine từ Setup Piper. Voice list đọc từ file JSON, map `AudioLanguage`, suy giới tính từ dataset/filename.
- **service_kokoro.py**: Kokoro (offline). Config: `engine_path` (python/engine), `num_threads`, `use_gpu`, `debug_logging`. Giọng từ engine.
- **service_mms.py**: MMS (offline). Config: `python_path`, `num_threads`, `use_gpu`, `debug_logging`. Hỗ trợ 1100+ ngôn ngữ, cài qua component_mms_manager.
- **service_googletranslate.py**: Google Translate TTS.
- **service_windows.py** / **service_macos.py** / **service_espeakng.py**: Hệ thống / eSpeak-ng.

**Từ điển:** Cambridge, Oxford, Duden, DWDS, Youdao, SpanishDict (free). Naver (paid – không load).

### Config Models (`config_models.py`)

Định nghĩa cấu trúc dữ liệu cho:

- **Configuration**: Cấu hình chung (user_uuid, service_enabled, service_config, presets, mapping_rules, realtime_config, …).
- **Preferences**: `ui_language` (en/vi), `cache_retention_days`, `cache_enabled`, `batch_concurrency` (số thread batch), `error_handling` (disable_ssl_verification, realtime_tts_errors_dialog_type), keyboard_shortcuts.
- **BatchConfig** (Preset): Source (simple/template/advanced_template), Target (target_field, remove_sound_tag, text_and_sound_tag, insert_location), VoiceSelection, Text processing.
- **VoiceSelection**: Chế độ single / random / priority; danh sách voice (voice_id + options + weight).
- **VoiceWithOptions**: voice + options (vd. format mp3/ogg).
- **MappingRule**: Liên kết preset với deck/note type.
- **RealtimeConfig**: Cấu hình realtime TTS (front/back, source, voice).
- **AudioLanguage / Language**: Enum ngôn ngữ (dùng trong `voice.py` và `languages.py`).

### Voice & Options

- **voice.py**: `TtsVoice_v3` (name, voice_key, service, gender, audio_languages, options, service_fee), `TtsVoiceId_v3` (voice_key, service), `build_voice_v3(name, gender, language, service, voice_key, options)`, `voice_str(voice)` dùng trong combobox.
- **options.py**: `AudioFormat` (mp3, ogg_vorbis, ogg_opus) – dùng khi ghi file cache (`superfreetss-{hash}.mp3`/`.ogg`).

### Error Handling (`errors.py`)

Custom exceptions: `SourceFieldNotFoundError`, `TargetFieldNotFoundError`, `SourceTextEmpty`, `NoVoicesAdded`, `AudioNotFoundError`, `PresetNotFound`, `VoiceNotFound`, `VoiceIdNotFound`, `MissingServiceConfiguration`, `RequestError` (TTS lỗi), …  
**ErrorManager** dùng để wrap action và hiển thị lỗi qua dialog/tooltip.

---

## 📖 Hướng Dẫn Sử Dụng

### Cài đặt

1. **Tải addon**:
   - Copy thư mục này vào `Anki2/addons21/`
   - Hoặc từ AnkiVN (xem hướng dẫn tại ankivn.com)

2. **Restart Anki**

3. **Cấu hình dịch vụ TTS** (lần đầu):
   - Menu: `AnkiVN` → `Super Free TTS Settings` → Click tab "Services"
   - Bật engine cần dùng: EdgeTTS (online, ⭐ khuyên dùng), Piper/Kokoro/MMS (offline cần setup đường dẫn hoặc Setup/Manage), Google Translate, Windows/macOS/eSpeak-ng.
   - **Piper:** Có thể để trống "Piper Models Directory" (dùng mặc định `data/piper_models`) hoặc chọn thư mục chứa file `.onnx` + `.onnx.json`. Dùng "Setup Piper" để cài engine, "Manage Voices" để tải giọng từ HuggingFace.
   - **Kokoro / MMS:** Chỉ định đường dẫn Python/engine nếu cần (xem component_kokoro_manager, component_mms_manager).

### Sử dụng cơ bản

#### 1. Easy Mode (Đơn giản)

Dùng cho người mới, thêm audio vào từng note riêng lẻ:

1. Mở note editor (Add card hoặc Browser)
2. Click nút **speaker icon** (Add Audio)
3. Chọn voice từ dropdown
4. Click "Add Audio"
5. Audio được thêm vào field hiện tại

#### 2. Collection Mode (Nâng cao)

Thêm audio cho nhiều notes cùng lúc:

1. Mở Browser, chọn các notes
2. Menu: `Super Free TTS` → `Add Audio (Collection)...`
3. Configure:
   - **Source**: Field chứa text cần tạo audio
   - **Voice**: Chọn voice TTS
   - **Target**: Field để chèn sound tag
   - **Text Processing**: Tùy chọn xử lý text
4. Preview (nghe thử)
5. Click "Apply" để thêm audio cho tất cả notes

#### 3. Preset Mapping Rules

Tự động apply preset dựa trên Note Type hoặc Deck:

1. Click nút **gear icon** (Settings) trong editor
2. Add rule:
   - Chọn Note Type (hoặc Deck + Note Type)
   - Chọn/tạo preset
3. Save rule
4. Từ giờ, khi click "Add Audio" button, preset sẽ tự động apply

#### 4. Realtime TTS

Audio tự động phát khi review card (không cần thêm vào note):

1. Chọn 1 note trong Browser
2. Menu: `Super Free TTS` → `Add Audio (Realtime)...`
3. Configure:
   - Front side: Field nào sẽ đọc, voice nào
   - Back side: Field nào sẽ đọc, voice nào
4. Apply
5. TTS tag `{{tts ...}}` được thêm vào card template
6. Khi review, audio tự động phát

### Các tính năng nâng cao

#### Text Processing

- **HTML to Text**: Loại bỏ HTML tags
- **Strip Brackets**: Loại bỏ [...]
- **Strip Cloze**: Loại bỏ cloze {{c1::...}}
- **SSML Characters**: Escape ký tự đặc biệt cho SSML
- **Text Replacement**: Thay thế text trước khi tạo audio

#### Voice Selection Modes

- **Single**: Chọn 1 voice cố định
- **Random**: Chọn ngẫu nhiên từ danh sách voices (có thể set weight)
- **Priority**: Thử voice theo thứ tự, fallback nếu không tạo được audio

#### Template Source

Combine nhiều fields:
- **Simple Template**: `{Field1} {Field2}`
- **Advanced Template**: Python code (disabled trong bản Lite vì lý do bảo mật)

---

## 👨‍💻 Hướng Dẫn Phát Triển

### Setup môi trường phát triển

#### 1. Clone/Copy dự án

```bash
# Thư mục addon thường ở đây (Windows):
cd %APPDATA%\Anki2\addons21\655806401

# Hoặc (macOS/Linux):
cd ~/Library/Application Support/Anki2/addons21/655806401
```

#### 2. Dependency management

Dependencies đã được bundle trong thư mục `external/`. Nếu cần thêm dependency:

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

Hoặc log to file:

```bash
$env:HYPER_TTS_DEBUG_LOGGING="file"
$env:HYPER_TTS_DEBUG_LOGFILE="C:\path\to\superfreetss.log"
```

#### 4. Restart Anki và test

```bash
# Anki sẽ load addon từ thư mục này
# Mọi thay đổi code cần restart Anki
```

### Cấu trúc code guidelines

#### 1. Tổ chức code

- **Business logic**: Nên ở `superfreetss.py` hoặc `servicemanager.py`
- **UI logic**: Nên ở các `component_*.py`
- **Utilities**: Nên ở các `*_utils.py`
- **Models**: Nên ở `config_models.py`
- **Constants**: Nên ở `constants.py`

#### 2. Error handling

Luôn sử dụng custom exceptions từ `errors.py`:

```python
# Good
if field not in note:
    raise errors.TargetFieldNotFoundError(field)

# Bad
if field not in note:
    raise Exception(f"Field {field} not found")
```

Wrap user-facing actions với `ErrorManager`:

```python
with superfreetss.error_manager.get_single_action_context('Action Name'):
    # Your code here
```

#### 3. Configuration

Mọi cấu hình cần:
- Định nghĩa model trong `config_models.py`
- Implement `serialize()` và `deserialize()`
- Lưu vào config qua `anki_utils.write_config()`

#### 4. Logging

```python
from . import logging_utils
logger = logging_utils.get_child_logger(__name__)

logger.debug('Debug message')
logger.info('Info message')
logger.error('Error message')
```

### Thêm dịch vụ TTS mới

#### Bước 1: Tạo file service

Tạo `superfreetss_addon/services/service_yourservice.py`. Class **kế thừa `ServiceBase`** và khai báo **`service_fee = constants.ServiceFee.free`** (nếu paid thì add-on sẽ không load).

```python
from typing import List
from superfreetss_addon import service, voice as voice_module, constants, languages

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
        return constants.ServiceFee.free  # bắt buộc free để được load

    def configuration_options(self):
        return {
            'api_key': ('string', 'API Key', ''),
            'debug_logging': ('bool', 'Debug Logging', False),
        }

    def voice_list(self) -> List[voice_module.TtsVoice_v3]:
        # Lấy danh sách từ API hoặc file; mỗi giọng tạo bằng build_voice_v3
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
        # Gọi API / engine, trả về bytes (audio)
        # voice.voice_key, voice.service
        return response_content  # bytes
```

- **`build_voice_v3`** (trong `voice.py`): Tham số `name`, `gender`, `language`, `service`, `voice_key`, `options`. Thiếu `gender` sẽ gây lỗi.
- **Config:** Key trong `configuration_options()` dùng trong UI; giá trị đọc bằng `self.get_configuration_value_optional(key, default)` / `get_configuration_value_mandatory(key)`.

#### Bước 2: Register service

Service **tự động được discovery** nếu file đặt tên `service_*.py` trong `services/`. Không cần đăng ký tay. Nếu muốn thứ tự hiển thị: thêm tên class vào `priority_order` trong `servicemanager.instantiate_services()` (vd. `["EdgeTTS", "PiperTTS", "KokoroTTS", "MmsTTS", "YourServiceTTS"]`).

Test:

```python
# Anki Debug Console (Tools > Debug Console)
from superfreetss_addon.servicemanager import ServiceManager
from superfreetss_addon import constants
import os
path = os.path.join(os.path.dirname(__file__), 'services')  # điều chỉnh path
sm = ServiceManager(path, 'superfreetss_addon.services', False)
sm.set_config_provider(hyper_tts)  # nếu có
sm.ensure_initialized()
voices = sm.full_voice_list()
print([v for v in voices if v.service == 'YourServiceTTS'])
```

### Testing

#### Manual testing

1. Tạo test deck với vài notes
2. Configure service trong UI
3. Test từng workflow:
   - Easy mode
   - Collection mode
   - Realtime mode
   - Preset mapping rules

#### Unit testing (hiện tại chưa có)

Dự án không còn thư mục `test_services/` (đã xóa). Có thể thêm test bằng pytest hoặc unittest; khi chạy test cần set `sys._pytest_mode = True` để add-on không chạy block Anki (vd. Sentry). Test service: instantiate class service, gọi `voice_list()` và `get_tts_audio(source_text, voice, {})` với voice lấy từ `voice_list()[0]`.

### Code review checklist

Trước khi commit code:

- [ ] Code có follow cấu trúc hiện tại không?
- [ ] Có thêm logging phù hợp không?
- [ ] Error handling đúng cách (dùng custom exceptions)?
- [ ] Config được save/load đúng không?
- [ ] UI có responsive và user-friendly không?
- [ ] Code có comments cho phần phức tạp không?
- [ ] Đã test manually các workflow chính chưa?

### Quy tắc cần tuân theo

#### 1. Bảo mật

- **KHÔNG bao giờ** execute Python code do user nhập (Advanced Template đã bị disable)
- **KHÔNG log** API keys hoặc sensitive data
- **Validate** tất cả user input

#### 2. Tương thích Anki

- Addon phải tương thích với:
  - Anki 2.1.50 - 2.1.x (check `meta.json`: `min_point_version: 5, max_point_version: 241100`)
- Sử dụng Anki API đúng cách (qua `anki_utils.py`)

#### 3. Performance

- **Lazy load add-on:** Services **không** được load lúc Anki khởi động. Chỉ khi lần đầu cần (mở Configuration/Generate, hoặc gọi `get_tts_audio`/`full_voice_list`), `ServiceManager.ensure_initialized()` mới chạy `init_services()` và `configure()`. Chi tiết: `UPGRADE_IDEAS.md`.
- **Cache audio files:** `generate_audio_write_file()` dùng hash `(source_text, voice_id, options)` → file `superfreetss-{hash}.mp3`; nếu đã tồn tại thì không gọi TTS lại.
- **Voice list cache:** `get_service_voice_list()` và `locate_voice()` dùng `functools.lru_cache`; sau khi tải Piper/đổi config cần gọi `clear_voice_list_cache()` (đã gọi khi reconfigure và khi đóng Piper Manager/Setup).
- **Batch:** `process_batch_audio()` dùng `ThreadPoolExecutor(max_workers=batch_concurrency)` (Preferences, mặc định 4). Mỗi task gọi `get_audio_file()` → tận dụng cache file.
- **Background processing:** Dùng `anki_utils.run_in_background()` cho thao tác lâu.

#### 4. UI/UX

- **Consistent với Anki**: Dùng PyQt components chuẩn
- **Error messages rõ ràng**: User phải hiểu được lỗi gì
- **Progress indicators**: Cho operations lâu (batch processing)

#### 5. HyperTTS Lite vs Pro

Bản Lite cần disable một số features:

```python
# constants.py
ENABLE_SENTRY_CRASH_REPORTING = True  # Set to False for Lite

# superfreetss.py
def expand_advanced_template(self, note, source_template):
    raise errors.HyperTTSError("Advanced Template (Python) không hỗ trợ trong bản Lite")
```

---

## 📚 Tài Liệu & Tham Khảo

### Tài liệu trong repo

- **UPGRADE_IDEAS.md**: Gợi ý nâng cấp (hiện tại chỉ tối ưu tốc độ load add-on – lazy load services).
- **PROJECT_DOCUMENTATION.md**: Tài liệu này.

### API Documentation

- **Anki Addon API**: https://addon-docs.ankiweb.net/
- **PyQt5**: https://www.riverbankcomputing.com/static/Docs/PyQt5/
- **Edge TTS**: https://github.com/rany2/edge-tts

### Service APIs (Miễn phí)

- **Edge TTS**: https://github.com/rany2/edge-tts
- **gTTS (Google Translate)**: https://github.com/pndurette/gTTS
- **eSpeak-ng**: https://github.com/espeak-ng/espeak-ng

### Anki Resources

- **Anki Manual**: https://docs.ankiweb.net/
- **Addon Development**: https://addon-docs.ankiweb.net/intro.html

---

## 🤝 Đóng Góp

Nếu bạn muốn đóng góp vào dự án:

1. Fork dự án (nếu có repository)
2. Tạo branch mới: `git checkout -b feature/your-feature`
3. Làm theo [Hướng Dẫn Phát Triển](#-hướng-dẫn-phát-triển)
4. Test kỹ các thay đổi
5. Commit với message rõ ràng
6. Tạo Pull Request

### Ý tưởng đóng góp

- Thêm dịch vụ TTS mới
- Improve UI/UX
- Thêm text processing features
- Viết tests
- Improve documentation
- Bug fixes

---

## 🌐 Đa ngôn ngữ giao diện (UI)

Super Free TTS hiện hỗ trợ **2 ngôn ngữ giao diện**: **English** và **Tiếng Việt**.

- **Cách đổi ngôn ngữ giao diện**:
  1. Vào menu `Tools → Super Free TTS: Preferences`  
  2. Ở nhóm **Language / Ngôn ngữ**, chọn:
     - `English` để dùng giao diện tiếng Anh
     - `Tiếng Việt` để dùng giao diện tiếng Việt
  3. Nhấn **Apply** và mở lại các hộp thoại của Super Free TTS (Easy, Collection, Configuration, Realtime, Preset Rules, Voice Selection) để thấy thay đổi.

- **Lưu ý cho developer**:
  - Bảng dịch nằm trong file `[superfreetss_addon/i18n.py](superfreetss_addon/i18n.py)`.
  - Khi thêm text mới ra UI, hãy dùng `i18n.get_text("some_key", lang)` thay vì hard-code chuỗi.
  - Quy ước đặt key:
    - Nút bấm: `button_*` hoặc `easy_button_*`, `batch_button_*`, `voice_button_*`
    - Tiêu đề dialog: `dialog_*_title`
    - Nhóm / groupbox / label: `*_group_*`, `label_*`

---

## 📝 License

Super Free TTS được phát triển bởi **Daniel from AnkiVN**. 100% miễn phí cho cộng đồng Anki Việt Nam.

---

## 📞 Liên Hệ & Hỗ Trợ

- **Website**: https://ankivn.com
- **Tác giả**: Daniel from AnkiVN
- **Issues**: Báo cáo lỗi hoặc đề xuất tính năng qua AnkiVN

---

**Tài liệu cập nhật**: 2026-02-16  
**Phiên bản addon (version.py)**: 1.0  
**Tác giả**: Daniel from AnkiVN  
