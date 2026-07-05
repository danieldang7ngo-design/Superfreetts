# Giải Thích Thư Mục External

Thư mục `external/` chứa các **thư viện Python bên thứ 3** (dependencies) mà addon cần để hoạt động. Đây là cách "bundle" (đóng gói) các thư viện vào addon để không phụ thuộc vào Python của hệ thống.

## Tại sao cần thư mục này?

Anki chạy Python riêng, nhưng không có tất cả thư viện. Nên addon phải tự mang theo các thư viện cần thiết.

---

## Các Thư Viện Quan Trọng (Đang Dùng)

### 🎯 **Cho EdgeTTS** (Dịch vụ TTS chính)
- **edge_tts/** - Thư viện gọi Microsoft Edge TTS API
- **edge_playback/** - Phát audio từ Edge TTS
- **aiohttp/** - HTTP client bất đồng bộ (gọi API Edge TTS)
- **aiosignal/** - Signals cho async
- **aiohappyeyeballs/** - DNS resolver nhanh cho aiohttp
- **frozenlist/** - Data structure cho aiohttp
- **multidict/** - Dictionary đặc biệt cho HTTP headers
- **propcache/** - Cache properties
- **yarl/** - Parse URL cho aiohttp
- **attrs/** - Tạo classes dễ dàng
- **psutil/** - Theo dõi tài nguyên hệ thống (RAM/CPU)

### 🎯 **Cho Google Translate TTS**
- **gtts/** - Google Text-to-Speech library
- **click/** - Command line interface (gtts dùng)

### 🎯 **Cho Windows SAPI**
- **comtypes/** - COM interface để gọi Windows API

### 🎯 **Cho eSpeak-ng**
- **espeakng/** - Wrapper cho eSpeak-ng TTS engine

### **Cho Supertonic**
- **Không vendor trong external/** - Supertonic SDK và model được cài vào shared embedded Python runtime bằng setup dialog.
- **Model cache** - Lưu trong `data/supertonic_cache` theo profile Anki, không đóng gói vào `.ankiaddon`.
- **License lưu ý** - Supertonic model/license upstream cần được review trước khi phát hành public.
- **Tích hợp mới**: Supertonic hiện là một engine TTS offline được hỗ trợ.

### 🎯 **HTTP & Network**
- **requests/** - HTTP library đơn giản (gọi API các dịch vụ)
- **urllib3/** - HTTP client low-level (requests dùng)
- **certifi/** - SSL certificates
- **charset_normalizer/** - Detect encoding
- **idna/** - Xử lý domain names quốc tế

### 🎯 **Utilities**
- **tabulate/** - Tạo bảng đẹp (hiển thị danh sách voices)
- **dateutil/** - Xử lý date/time
- **cachetools/** - Cache data
- **machineid/** - Lấy ID máy tính
- **six.py** - Tương thích Python 2/3
- **typing_extensions.py** - Type hints mở rộng
- **PyYAML**: Dùng để đọc/ghi file config YAML (nếu có).

### 🎯 **Data Processing**
- **databind/** - Serialize/deserialize data
- **typeapi/** - Type introspection
- **nr/** - Utilities package (nr.stream, nr.date)
- **deprecated/** - Đánh dấu code deprecated
- **wrapt/** - Decorators

---

Những thư viện này đã được xóa hoặc làm sạch để giảm dung lượng addon:

### ❌ Đã xóa / Đã làm sạch
- **__pycache__/** - Đã xóa sạch toàn bộ project
- **.pytest_cache/** - Đã xóa sạch
- **Files rác (log, tmp)** - Đã dọn dẹp hoàn toàn

---

## Cách Hoạt Động

Khi addon khởi động:

```python
# Trong __init__.py (root)
import sys
import os

addon_dir = os.path.dirname(os.path.realpath(__file__))
external_dir = os.path.join(addon_dir, 'external')

# Thêm external/ vào Python path
sys.path.insert(0, external_dir)

# Bây giờ có thể import các thư viện
import edge_tts  # Từ external/edge_tts/
import gtts      # Từ external/gtts/
import aiohttp   # Từ external/aiohttp/
```

---

## Kích Thước

Các thư viện này chiếm khá nhiều dung lượng:
- **aiohttp** và dependencies: ~5-10 MB
- **edge_tts**: ~1-2 MB
- **gtts**: ~500 KB
- **comtypes**: ~2-3 MB
- **requests** và urllib3: ~2-3 MB
- Tổng cộng: **~15-20 MB**

---

## Có Thể Tối Ưu Không?

Có thể giảm kích thước bằng cách:

1. **Xóa các file không cần:**
   - `*.dist-info/` folders (metadata)
   - `__pycache__/` folders
   - Test files

2. **Nhưng cẩn thận:** Một số thư viện phụ thuộc lẫn nhau, xóa nhầm sẽ lỗi!

---

## Tóm Tắt

**Thư mục `external/` = "Kho thư viện riêng của addon"**

- ✅ **Cần thiết** để addon hoạt động độc lập
- ✅ **Chứa 40+ thư viện** Python
- ✅ **Chiếm ~15-20 MB** dung lượng
- ✅ **Quan trọng nhất:** edge_tts, gtts, aiohttp, requests, comtypes

**Không nên xóa bừa bãi!** Chỉ xóa khi chắc chắn không service nào dùng.
