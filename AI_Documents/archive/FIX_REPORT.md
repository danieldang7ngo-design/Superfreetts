# FIX_REPORT.md — macOS RAM/Crash Fixes for Superfreetts Add-on

**Ngày hoàn thành:** 2026-07-23
**Commit gốc khi làm việc:** `ef57c69`
**Môi trường xác minh:** Windows (Python 3.14.6, pytest 9.1.1) — xem mục 6 để biết phần cần xác nhận thêm trên macOS thật.

---

## 1. Tóm tắt tổng quan

Đã xác định và sửa 5 root cause gây tràn RAM và crash của add-on Superfreetts trên macOS, dựa trên quá trình điều tra trong `INVESTIGATION_NOTES.md`. Các sửa đổi tập trung vào: giới hạn concurrency theo RAM khả dụng (Piper/Kokoro/MMS/Supertonic), bổ sung timeout cho realtime TTS playback, tái sử dụng event loop cho EdgeTTS, thêm gate cho subprocess macOS `say`, và thêm guard fail-fast cho installer của engine Windows-only. Tất cả thay đổi được bao phủ bởi 27 test tự động mới; kết quả toàn bộ suite: **226 passed, 1 skipped**.

---

## 2. Bảng chi tiết từng bug đã sửa

### Bug 2.6 — RAM-aware concurrency cho local engine pools

| Thuộc tính | Chi tiết |
|---|---|
| **Root cause** | `build_engine_config()` trong `tts_orchestrator.py` đặt số worker của process pool (Piper/Kokoro/MMS/Supertonic) bằng số CPU core, không xét RAM/process → trên Mac nhiều core có thể spawn >5GB RAM |
| **Files đã sửa** | `superfreetts_addon/system_utils.py` — dòng 8-9: thêm import psutil; dòng 43-108: thêm `get_available_ram_mb()` và `compute_ram_aware_concurrency()` |
| | `superfreetts_addon/tts_orchestrator.py` — dòng 11-30: thêm `RAM_PER_PROCESS_MB_ESTIMATE`; dòng 41-68: thay `cpu_default` bằng `ram_capped_default` |
| **Trước** | `'PiperTTS': cpu_default` — pool size = CPU core count |
| **Sau** | `'PiperTTS': ram_capped_default.get('PiperTTS', cpu_default)` — cap bởi `min(cpu_default, floor(available_ram*0.5 / ram_per_process_mb))` |
| **Fallback** | psutil không có / call thất bại → trả về `cpu_default` y hệt hành vi cũ |
| **Test** | `tests/test_ram_aware_concurrency.py` (9 cases): `pytest tests/test_ram_aware_concurrency.py -v` |
| **Mức tin cậy** | ✅ Xác minh logic qua test tự động trên Windows; ⚠️ RAM đỉnh thực tế cần đo trên macOS thật với model thật |

> **Lưu ý:** Các giá trị trong `RAM_PER_PROCESS_MB_ESTIMATE` (Piper: 200 MB, Kokoro/MMS/Supertonic: 500 MB) **không phải do agent đo benchmark**. Chúng dựa trên báo cáo của người dùng và được chọn thiên về phía thận trọng (conservative). Người dùng luôn có thể override qua field `concurrency_workers` trong Advanced settings.

---

### Bug 2.2 — Timeout cho realtime TTS generation trong `ttsplayer.py`

| Thuộc tính | Chi tiết |
|---|---|
| **Root cause** | `_play()` override hoàn toàn `TTSProcessPlayer` nhưng không check `_terminate_flag` của Anki → 1 request treo chặn toàn bộ hàng đợi phát âm thanh realtime |
| **File đã sửa** | `superfreetts_addon/ttsplayer.py` — dòng 9: thêm `import concurrent.futures`; dòng 24-51: thêm `REALTIME_GENERATE_TIMEOUT_SECONDS=20` + comment giải thích trade-off; dòng 57-64: thêm `_generate_executor`; dòng 96-108: bọc call bằng executor + timeout |
| **Trước** | `audio_filename = self.hypertts.get_audio_filename_tts_tag(tag)` — blocking call trực tiếp |
| **Sau** | `future = self._generate_executor.submit(...); audio_filename = future.result(timeout=20)` — nếu >20s: log warning, return None, call tiếp tục chạy nền và bị discard |
| **Test** | `tests/test_ttsplayer_realtime_timeout.py` (4 cases): `pytest tests/test_ttsplayer_realtime_timeout.py -v` |
| **Mức tin cậy** | ✅ Logic timeout xác minh qua test; ⚠️ đây là "approach b" (timeout, không phải cancellation triệt để) — call vẫn chạy nền sau khi timeout |

---

### Bug 2.1 — Tái sử dụng event loop singleton cho EdgeTTS

| Thuộc tính | Chi tiết |
|---|---|
| **Root cause** | `run_async_safe()` trong `service_edgetts.py` tạo mới `ThreadPoolExecutor` + event loop (qua `asyncio.run()`) cho MỌI request không cache → lãng phí CPU/RAM, thêm thread không cần thiết |
| **File đã sửa** | `superfreetts_addon/services/service_edgetts.py` — dòng 35-37: thêm 3 biến singleton `_background_loop/thread/lock`; dòng 40-78: thêm hàm `_get_background_loop()`; dòng 126-135: thay thế logic trong `run_async_safe()` |
| **Trước** | `with ThreadPoolExecutor(max_workers=1) as ex: return ex.submit(asyncio.run, coro).result()` |
| **Sau** | `return asyncio.run_coroutine_threadsafe(coro, background_loop).result()` — submit vào loop singleton daemon thread |
| **Fallback** | Loop không khởi động trong 10s → log warning + dùng lại old per-call approach |
| **Test** | `tests/test_edgetts_background_loop.py` (6 cases): `pytest tests/test_edgetts_background_loop.py -v` |
| **Mức tin cậy** | ✅ Logic singleton + fallback xác minh qua test tự động |

---

### Bug 2.4 — Concurrency gate cho subprocess `say` + ffmpeg trên macOS

| Thuộc tính | Chi tiết |
|---|---|
| **Root cause** | `get_tts_audio()` trong `service_macos.py` spawn 2 subprocess (`say` + `_encode_mp3`) mỗi call không có giới hạn concurrency — khác với `service_edgetts.py` đã có gate |
| **File đã sửa** | `superfreetts_addon/services/service_macos.py` — dòng 8: `import threading`; dòng 20-43: thêm `DEFAULT/MAX_MACOS_CONCURRENCY_WORKERS` + `_get_request_gate()`; dòng 468-485: thêm `advanced_configuration_options()` + `_get_int_config()`; dòng 585-599: bọc subprocess calls bằng `BoundedSemaphore` |
| **Trước** | `subprocess.check_call(arg_list); aqt.sound._encode_mp3(...)` — không giới hạn concurrency |
| **Sau** | `request_gate.acquire(); try: subprocess.check_call(...); _encode_mp3(...); finally: request_gate.release()` — mặc định max 2, configurable |
| **Test** | `tests/test_macos_concurrency_gate.py` (4 cases): `pytest tests/test_macos_concurrency_gate.py -v` |
| **Mức tin cậy** | ✅ Gate logic xác minh qua test; ⚠️ hiệu quả trên macOS thật cần kiểm định thủ công |

---

### Bug 2.3 — Platform guard fail-fast cho installer Windows-only (Kokoro/MMS/Engine)

| Thuộc tính | Chi tiết |
|---|---|
| **Root cause** | `ensure_installed()` / `start_installation()` tải Python Embeddable Distribution (Windows-only PE) và cố chạy pip qua nó trên mọi OS → lãng phí băng thông, fail muộn với lỗi khó hiểu |
| **Files đã sửa** | `superfreetts_addon/engine_manager.py` — dòng 7: `import platform`; dòng 44-57: guard `if platform.system() != "Windows": return False` |
| | `superfreetts_addon/mms_engine_manager.py` — dòng 8: `import platform`; dòng 75-88: guard tương tự + ghi log service |
| | `superfreetts_addon/component_kokoro_manager.py` — dòng 9: `import platform`; dòng 106-115: guard trong `start_installation()` với `showWarning()` cho người dùng |
| **Test** | `tests/test_engine_manager_platform_guard.py` (4 cases): `pytest tests/test_engine_manager_platform_guard.py -v` |
| **Mức tin cậy** | ✅ Guard logic xác minh qua test |

---

## 3. Đính chính quan trọng về phạm vi Bug 2.3

**Bug 2.3 hoá ra ít nghiêm trọng hơn giả định ban đầu.**

Giả định ban đầu: `get_tts_audio()` của Kokoro/MMS sẽ crash hoặc gây lỗi khó hiểu trên macOS do cố dùng Python binary Windows-only.

**Thực tế sau khi đọc code:** `get_tts_audio()` đã tự `raise errors.RequestError(...)` ngay đầu hàm nếu engine chưa sẵn sàng — fail an toàn từ trước, không crash Anki. Vấn đề thực sự chỉ ở luồng **cài đặt** (`ensure_installed`, `start_installation`): người dùng macOS có thể bấm "Install" và chờ download vô ích rồi nhận lỗi muộn.

Phạm vi sửa được thu hẹp có chủ đích: chỉ guard ở hàm installer, không sửa `get_tts_audio()` (đã an toàn). Đây là ví dụ cụ thể cho thấy đọc code thật trước khi sửa thay đổi phạm vi công việc — và lý do quy tắc "không sửa file chưa đọc" được đặt ở đầu plan.

---

## 4. Danh sách việc CHƯA làm / nằm ngoài phạm vi

| Việc | Lý do |
|---|---|
| Hỗ trợ đầy đủ Kokoro/MMS trên macOS | Cần bootstrap Python riêng cho macOS — kiến trúc lớn, ngoài phạm vi "sửa crash" đã thống nhất |
| Cancellation triệt để cho Bug 2.2 ("approach a") | Yêu cầu threading cancellation signal qua toàn bộ chuỗi service — thay đổi lớn, nên tách thành task riêng |
| Đo benchmark RAM thực tế | Không có model thật trong môi trường để đo; giá trị trong `RAM_PER_PROCESS_MB_ESTIMATE` là ước tính từ báo cáo người dùng |
| Kiểm định crash trên macOS thật | Không có máy macOS trong môi trường làm việc — xem mục 6 |

---

## 5. Gợi ý cải tiến tiếp theo

**Implement "approach a" cho Bug 2.2 (cancellation triệt để):**
Timeout 20s giải quyết triệu chứng nhưng không giải phóng tài nguyên của call đã bị abandon. Giải pháp sạch hơn là threading `CancellationToken` qua: `ttsplayer._play()` → `HyperTTS.get_audio_filename_tts_tag()` → từng service's `get_tts_audio()`. Nên tách thành task riêng với scoping discussion.

**Đo RAM per-process thực tế:**
Sau khi có macOS + model cài đặt, chạy script đo RSS qua psutil trước/sau khi spawn 1 process Piper/Kokoro, cập nhật `RAM_PER_PROCESS_MB_ESTIMATE` với giá trị thực để RAM-cap (Bug 2.6 fix) chính xác hơn.

---

## 6. Kịch bản kiểm định thủ công cần thực hiện trên máy macOS thật

> **Ngôn từ chính xác:** Các thay đổi đã được xác minh qua đọc code + test tự động trên Windows. Phần dưới mô tả những gì cần kiểm tra thêm trên macOS thật để đảm bảo không còn nguyên nhân crash nào khác chưa được phát hiện — không phải khẳng định tuyệt đối "đã fix hoàn toàn".

### 6.1. Cài đặt bản vá

Trong Anki trên macOS: `Tools → Add-ons → thư mục add-on Superfreetts`, copy/replace các file đã sửa. Khởi động lại Anki.

### 6.2. EdgeTTS realtime (Bug 2.1 + 2.2)

1. Bật EdgeTTS làm dịch vụ realtime trong cài đặt Superfreetts.
2. Ôn tập nhanh qua **100+ thẻ liên tục** (Space hoặc auto-advance).
3. Theo dõi **Activity Monitor → tab Memory**:
   - Cột **Memory** của tiến trình `anki`: có tăng liên tục không kiểm soát không?
   - Cột **Threads**: có tăng theo số thẻ không?
4. Thử điều kiện mạng chập chờn (bật/tắt Wi-Fi giữa chừng): Anki có frozen UI không, hay tự tiếp tục sau ~20 giây?
5. **Kỳ vọng sau bản vá:** không có UI freeze vĩnh viễn; nếu 1 request EdgeTTS mất >20s, Anki tự bỏ qua và tiếp tục.

### 6.3. Batch generation với local engine (Bug 2.6)

1. Tạo batch ~500 thẻ dùng Piper/Supertonic.
2. Theo dõi Activity Monitor: RAM đỉnh của `anki`, số process con.
3. Kiểm tra Superfreetts log: tìm dòng `[RAM-CAP]` để xác nhận RAM capping đang hoạt động.
4. So sánh RAM đỉnh trước/sau bản vá nếu có bản build cũ.

### 6.4. macOS say gate (Bug 2.4)

1. Bật macOS TTS (`say`) làm dịch vụ trong Superfreetts.
2. Chạy batch generation.
3. Trong Activity Monitor: số process `say` chạy đồng thời không nên vượt quá giá trị `concurrency_workers` (mặc định: 2).

### 6.5. Installer guard (Bug 2.3)

1. Vào cài đặt Superfreetts → thử cài Kokoro engine.
2. **Kỳ vọng:** hiện ngay dialog cảnh báo "Kokoro's built-in installer currently only supports Windows..." thay vì bắt đầu download.

---

## 7. Kết quả test suite

```
Platform: Windows (Python 3.14.6, pytest 9.1.1)
226 passed, 1 skipped (test_mms_active.py — pre-existing skip, không liên quan)
Thời gian: 5.07s
```

| File test mới | Bug | Số test |
|---|---|---|
| `tests/test_ram_aware_concurrency.py` | 2.6 | 9 |
| `tests/test_ttsplayer_realtime_timeout.py` | 2.2 | 4 |
| `tests/test_edgetts_background_loop.py` | 2.1 | 6 |
| `tests/test_macos_concurrency_gate.py` | 2.4 | 4 |
| `tests/test_engine_manager_platform_guard.py` | 2.3 | 4 |
| **Tổng** | | **27 test mới** |
