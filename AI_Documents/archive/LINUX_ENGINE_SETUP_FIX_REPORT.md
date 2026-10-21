# LINUX_ENGINE_SETUP_FIX_REPORT.md — Linux Engine Setup Fixes for Superfreetts

**Ngày hoàn thành:** 2026-09-06
**Môi trường xác minh:** Arch Linux (Python 3.14.7, no root/sudo), Anki addon 351217314.
**Phạm vi:** Sửa lỗi cài đặt & chạy các local engine (Piper, Supertonic, ESpeakNG, Kokoro, MMS) trên Linux.

---

## 1. Tóm tắt

Các local TTS engine không chạy được trên Linux vì (a) các installer/runner đa số được viết cho Windows, (b) một số binary model không được add-on bundle sẵn, (c) vòng đời download cài đặt làm treo UI. Tất cả các lỗi dưới đây được fix trong code add-on và xác minh end-to-end (runner sinh ra file WAV hợp lệ) trên máy thật.

---

## 2. Chi tiết từng lỗi

### 2.1 Piper — giao diện cài đặt treo khi tải engine

| | |
|---|---|
| **Lỗi** | Setup dialog đứng yên (freeze) suốt lúc tải `piper.tar.gz`; không có % hay tốc độ nào hiển thị |
| **Nguyên nhân** | `component_piper_setup.py` dùng `urllib.request.urlretrieve(piper_url, archive_path)` — blocking, không callback progress |
| **Fix** | Thay bằng `TurboDownloader` + `progress_callback` cập nhật `progress_bar` (cap 70%) và `status_label` (%, MB/s) qua `mw.taskman.run_on_main` |

File: `superfreetts_addon/component_piper_setup.py`

### 2.2 Piper — âm thanh không ra (silent failure)

| | |
|---|---|
| **Lỗi** | Piper process chạy nhưng không sinh ra audio / bị bỏ qua cờ |
| **Nguyên nhân** | Runner dùng `--data_dir` — cờ này **không tồn tại** trong piper 1.2.0 (bị bỏ qua âm thầm); cờ đúng là `--espeak_data` |
| **Fix** | Đổi thành `--espeak_data` trong `generate_single()` |

File: `superfreetts_addon/services/piper_runner.py`

### 2.3 Supertonic — installer treo như "chết" ở bước đầu

| | |
|---|---|
| **Lỗi** | Setup log đứng im hàng phút khi tạo venv / pip install / download model; nhiều khi treo vô hạn |
| **Nguyên nhân** | `_run_command()` dùng `subprocess.run` capture stdout+stderr rồi mới log — không có tiến trình thời gian thực, **không có timeout** |
| **Fix** | Chuyển sang `Popen`, stream từng dòng stdout vào log realtime; thêm `timeout=1800`s (kill process nếu quá hạn); toast lỗi lấy từ output đã stream. Error message giờ luôn cho biết bước nào chết |

File: `superfreetts_addon/component_supertonic_setup.py`

### 2.4 Supertonic — model rơi ra ngoài profile cache

| | |
|---|---|
| **Lỗi** | Model supertonic tải vào `~/.cache/supertonic-3` thay vì `SUPERTONIC_CACHE_DIR` → không portable, xoá khi gỡ addon không sạch |
| **Nguyên nhân** | supertonic ≥ 1.3 **không có tham số `cache_dir`** trong `TTS()`; nó đọc `$SUPERTONIC_CACHE_DIR` (mặc định `~/.cache/<model>`) |
| **Fix** | Set `os.environ["SUPERTONIC_CACHE_DIR"] = cache_path` ở cả `supertonic_runner._set_cache_env()` lẫn script `_download_model()` (bên cạnh `HF_HOME`/`HUGGINGFACE_HUB_CACHE`/`TORCH_HOME` đã có) |

Files: `superfreetts_addon/services/supertonic_runner.py`, `superfreetts_addon/component_supertonic_setup.py`

### 2.5 ESpeakNG — không có danh sách giọng / lỗi không tìm thấy binary

| | |
|---|---|
| **Lỗi** | `voice_list` trả rỗng, synthesis báo lỗi trên Linux |
| **Nguyên nhân** | Service giả định lệnh `espeak-ng` có sẵn trên PATH (không bundle binary, macOS/Linux không có sẵn). Binary espeak-ng thật ra **nằm sẵn trong thư mục Piper engine** nhưng service không biết đến; binary này còn cần `LD_LIBRARY_PATH` trỏ vào thư mục của nó và `--path=<piper>/espeak-ng-data` (default nội bộ `/usr/share/espeak-ng-data` không tồn tại) |
| **Fix** | Thêm `_find_espeak_ng_engine()` (ưu tiên binary bundled trong `PIPER_ENGINE_DIR/piper`, fallback `espeak-ng` trên PATH) và `_run_espeak_ng()` (inject `LD_LIBRARY_PATH` + `--path=...`). Thay 2 call `subprocess.run(['espeak-ng', ...])` bằng `_run_espeak_ng(...)` |

File: `superfreetts_addon/services/service_espeakng.py`

### 2.6 MMS — runner chạy bằng Python hệ thống, thiếu `sherpa_onnx`

| | |
|---|---|
| **Lỗi** | MMS dừng với lỗi import `sherpa_onnx` / không synth được trên Linux |
| **Nguyên nhân** | `MmsEngineManager.get_python_exe()` trên non-Windows trả về `python3` hệ thống (bootstrap embeddable python chỉ tồn tại trên Windows); cấu hình `engine_path` (của service MmsTTS) **không bao giờ được dùng** trên Linux |
| **Fix** | Thêm `MmsTTS._get_python_exe()`: ưu tiên tham số config `engine_path` (hỗ trợ cả path file lẫn thư mục venv **trên mọi OS**), fallback `MmsEngineManager.get_python_exe()`. Áp dụng cho cả `get_tts_audio()` lẫn `get_tts_audio_batch()` |

File: `superfreetts_addon/services/service_mms.py`

---

## 3. Ghi chú cài đặt Linux (ngoài code)

- **Kokoro / MMS**: installer có sẵn trong addon chỉ được build cho Windows. Trên Linux phải tự dựng venv (pip install `kokoro-onnx` / `sherpa-onnx`) và tải model theo URL sẵn có trong addon vào `<DATA>/kokoro_engine/models` và `<DATA>/mms_models/<lang>/`, rồi set `engine_path` trỏ đến venv python trong config của addon.
- **Kokoro path quirk Linux**: vì dùng venv, `kokoro_runner.py` tính `models_dir = dirname(sys.executable)/models` (= `<venv>/bin/models`); bắt buộc có symlink `<venv>/bin/models -> <kokoro_engine>/models`.
- **Piper**: binary Linux từ tarball chạy native (cần `--espeak_data`); giọng nói là người dùng tự quản lý (không tự tải).