# Super Free TTS by Daniel from AnkiVN - Tài Liệu Dự Án

> Tài liệu này giúp bất kỳ ai (bao gồm cả AI Agents) có thể nhanh chóng hiểu và tham gia phát triển dự án Super Free TTS.

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
- **Hỗ trợ nhiều dịch vụ TTS MIỄN PHÍ**: EdgeTTS (Microsoft), Google Translate, Windows SAPI, macOS TTS, eSpeak-ng
- **Linh hoạt**: Có thể thêm âm thanh cho từng thẻ riêng lẻ hoặc hàng loạt thẻ
- **100% Miễn phí**: Không có dịch vụ trả phí, không cần API key

### Thông tin

- **Tên addon**: Super Free TTS
- **Tác giả**: Daniel from AnkiVN
- **Phiên bản hiện tại**: 2.11.1
- **ID cài đặt**: 655806401 (thư mục cài đặt trên máy)
- **Website**: ankivn.com

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

Dự án chỉ hỗ trợ **các dịch vụ TTS miễn phí**:

#### Dịch vụ TTS miễn phí chính
- **EdgeTTS**: Microsoft Edge TTS (⭐ Khuyên dùng - chất lượng cao, miễn phí)
- **Google Translate TTS**: Google Translate (miễn phí)
- **Windows SAPI**: Windows Speech API (chỉ Windows)
- **macOS TTS**: macOS built-in TTS (chỉ macOS)
- **eSpeak-ng**: Open-source TTS

#### Dịch vụ từ điển miễn phí (pronunciation)
- **Cambridge Dictionary**: Từ điển Cambridge (miễn phí)
- **Oxford Dictionary**: Từ điển Oxford (miễn phí)
- **Duden**: Từ điển tiếng Đức (miễn phí)
- **DWDS**: Từ điển tiếng Đức (miễn phí)
- **Naver**: Từ điển tiếng Hàn (miễn phí)
- **Youdao**: Từ điển tiếng Trung (miễn phí)
- **SpanishDict**: Từ điển tiếng Tây Ban Nha (miễn phí)

---

## 🏗 Kiến Trúc Dự Án

### Cấu trúc thư mục

```
655806401/                          # Thư mục gốc addon
├── __init__.py                     # Entry point, khởi tạo addon
├── manifest.json                   # Metadata addon
├── meta.json                       # Cấu hình Anki và trạng thái addon
├── config.json                     # Cấu hình mặc định
│
├── superfreetss_addon/             # Thư mục chứa code chính (Super Free TTS)
│   ├── __init__.py                 # Khởi tạo addon, setup logging, error reporting
│   ├── version.py                  # Phiên bản addon (2.11.1)
│   ├── constants.py                # Constants, enums, text UI
│   ├── config_models.py            # Data models cho cấu hình
│   ├── errors.py                   # Custom exception classes
│   │
│   ├── superfreetss.py             # ⭐ CORE - Logic nghiệp vụ chính
│   ├── servicemanager.py           # Quản lý các dịch vụ TTS
│   ├── anki_utils.py               # Utilities tương tác với Anki
│   ├── gui.py                      # ⭐ Khởi tạo giao diện, menu, buttons
│   │
│   ├── services/                   # Các dịch vụ TTS miễn phí
│   │   ├── service_edgetts.py      # ⭐ EdgeTTS (khuyên dùng)
│   │   ├── service_googletranslate.py  # Google Translate TTS
│   │   ├── service_windows.py      # Windows SAPI
│   │   ├── service_macos.py        # macOS TTS
│   │   ├── service_espeakng.py     # eSpeak-ng
│   │   ├── service_cambridge.py    # Cambridge Dictionary
│   │   ├── service_oxford.py       # Oxford Dictionary
│   │   └── voicelist.py            # Database voices
│   │
│   ├── component_*.py              # UI components (13 files)
│   │   ├── component_batch.py      # Dialog thêm audio hàng loạt
│   │   ├── component_easy.py       # Dialog easy mode
│   │   ├── component_realtime.py   # Dialog realtime TTS
│   │   ├── component_configuration.py
│   │   └── ... (9 components khác)
│   │
│   ├── text_utils.py               # Xử lý text (strip HTML, cloze, etc.)
│   ├── voice.py                    # Voice models
│   ├── logging_utils.py            # Logging configuration
│   ├── stats.py                    # Usage statistics
│   └── ttsplayer.py                # Anki TTS player integration
│
├── external/                       # Thư viện bên thứ 3 (49 packages)
│   ├── aiohttp/
│   ├── edge_tts/
│   ├── gtts/
│   └── ...
│
├── graphics/                       # Hình ảnh UI
│   ├── superfreetss_banner.png
│   ├── icon_play.png
│   ├── icon_settings.png
│   └── icon_speaker.png
│
└── user_files/                     # Cache file âm thanh đã tạo
    └── superfreetss-*.mp3          # Audio files (hash-based naming)
```

### Luồng hoạt động chính

#### 1. Khởi động Addon

```
Anki starts
    ↓
__init__.py (root)
    ↓
sys.path.insert(external/) & sys.path.insert(addon_dir/)
    ↓
import superfreetts_addon
    ↓
superfreetts_addon/__init__.py
    ├─→ Setup logging
    ├─→ Get/create user_uuid
    ├─→ Initialize servicemanager
    ├─→ Initialize HyperTTS core class (trong `superfreetts.py`)
    └─→ gui.init() - Setup UI, menus, buttons
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

Quản lý các dịch vụ TTS:
- Load tất cả services từ thư mục `services/`
- Lấy danh sách voices từ mỗi service
- Gọi API TTS để lấy audio data
- Kiểm tra service có enabled không

**Key methods:**
- `init_services()`: Load tất cả service modules
- `get_tts_audio()`: Gọi service để lấy audio
- `get_voice_list()`: Lấy danh sách voices từ service
- `configure()`: Cấu hình services

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

Mỗi service implement interface chung:

```python
class Service:
    def get_tts_audio(self, source_text, voice, options)
    def get_voice_list(self)
    def configuration_options(self)
```

**Ví dụ: service_edgetts.py** (⭐ Khuyên dùng)
- Sử dụng thư viện `edge_tts`
- Miễn phí, không cần API key
- Hỗ trợ nhiều ngôn ngữ, voices chất lượng cao

**Ví dụ: service_googletranslate.py**
- Sử dụng thư viện `gtts`
- Miễn phí, không cần API key
- Hỗ trợ nhiều ngôn ngữ

### Config Models (`config_models.py`)

Định nghĩa cấu trúc dữ liệu cho:

- **Configuration**: Cấu hình chung (user_uuid, service configs)
- **BatchConfig** (Preset): Cấu hình 1 preset
  - Source (field/template)
  - Target (field, text+sound)
  - Voice selection
  - Text processing
- **VoiceSelection**: Chọn voice (single/random/priority)
- **MappingRule**: Rule liên kết preset với deck/note type
- **RealtimeConfig**: Cấu hình realtime TTS cho front/back

### Error Handling (`errors.py`)

Custom exceptions:
- `SourceFieldNotFoundError`
- `TargetFieldNotFoundError`
- `SourceTextEmpty`
- `NoVoicesAdded`
- `AudioNotFoundError`
- `PresetNotFound`
- ... và nhiều exceptions khác

**ErrorManager** class hiển thị lỗi cho user qua dialog hoặc tooltip.

---

## 📖 Hướng Dẫn Sử Dụng

### Cài đặt

1. **Tải addon**:
   - Copy thư mục này vào `Anki2/addons21/`
   - Hoặc từ AnkiVN (xem hướng dẫn tại ankivn.com)

2. **Restart Anki**

3. **Cấu hình dịch vụ TTS** (lần đầu):
   - Menu: `Tools` → `Super Free TTS: Services Configuration`
   - Enable EdgeTTS (⭐ Khuyên dùng - chất lượng cao nhất)

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

Tạo `superfreetss_addon/services/service_yourservice.py`:

```python
import requests
from typing import List

def get_tts_audio(source_text, voice, options):
    """
    Gọi API TTS service, trả về audio data (bytes)
    
    Args:
        source_text (str): Text cần convert
        voice (dict): Voice info {service, voice_key, name, ...}
        options (dict): Options (rate, pitch, ...)
    
    Returns:
        bytes: Audio data
    """
    # Implement API call here
    response = requests.post('https://api.yourservice.com/tts', {
        'text': source_text,
        'voice': voice['voice_key'],
        # ...
    })
    return response.content

def get_voice_list():
    """
    Lấy danh sách voices từ service
    
    Returns:
        List[dict]: Danh sách voices
    """
    # Implement API call
    return [
        {
            'voice_key': 'en-US-JennyNeural',
            'name': 'Jenny (US English)',
            'service': 'YourService',
            'language_code': 'en-US',
            'gender': 'Female',
            # ...
        },
        # ...
    ]

def configuration_options():
    """
    Return configuration UI for this service
    
    Returns:
        List[dict]: UI configuration elements
    """
    return [
        {
            'key': 'api_key',
            'type': 'text',
            'label': 'API Key',
            'default': ''
        }
    ]
```

#### Bước 2: Register service

Service tự động được load nếu đặt trong thư mục `services/`.

Test voice list:

```python
# Trong Anki debug console (Tools > Debug Console)
from superfreetss_addon import servicemanager
sm = servicemanager.ServiceManager(...)
voices = sm.get_voice_list()
print([v for v in voices if v['service'] == 'YourService'])
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

Dự án có thư mục `test_services/` nhưng chưa có test framework setup.

Để thêm tests:

```python
# superfreetss_addon/test_services/test_service_yourservice.py
import sys
sys._pytest_mode = True  # Enable test mode

def test_get_voice_list():
    from ..services import service_yourservice
    voices = service_yourservice.get_voice_list()
    assert len(voices) > 0
    assert voices[0]['service'] == 'YourService'

def test_get_tts_audio():
    from ..services import service_yourservice
    audio = service_yourservice.get_tts_audio(
        'Hello world',
        {'voice_key': 'en-US-JennyNeural'},
        {}
    )
    assert isinstance(audio, bytes)
    assert len(audio) > 0
```

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

- **Cache audio files**: Dùng hash để tránh tạo lại audio giống nhau
- **Background processing**: Dùng `anki_utils.run_in_background()` cho operations lâu
- **Lazy loading**: Chỉ load voices khi cần

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

## 📚 Tài Liệu Tham Khảo

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

**Tài liệu được tạo**: 2026-02-03  
**Phiên bản addon**: 2.11.1  
**Tác giả**: Daniel from AnkiVN
