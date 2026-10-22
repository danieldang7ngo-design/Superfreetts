# HANDOFF — Gia cố quản lý tài nguyên và dọn dẹp nền (P0/P1/P2)

- **Ngày bàn giao:** 2026-10-22
- **Nhánh:** `fix/resource-management`
- **Commit:** `004d73b` — `fix: restore runtime after profile switch`
- **Commit nền:** `292668e` — `fix: harden resource management and background cleanup`
- **Base:** `f4ac372`
- **Phiên bản:** `26.10.2` (giữ nguyên, chưa release)
- **Môi trường xác minh:** Linux 7.2.9-2-cachyos x86_64, Python 3.14.8, 16 logical CPU
- **Trạng thái:** code + automated gates đã xong trên Linux. Chưa push, chưa tạo GitHub release, chưa cập nhật AnkiWeb.

---

## 1. Tóm tắt nhanh

Đợt gia cố này xử lý bốn nhóm vấn đề:

1. **P0 — Đo và phân bổ RAM đúng:** thay cách đọc RSS bị kẹt ở peak, sửa GC hysteresis, và dùng **một ngân sách RAM chung** cho tất cả local engine đang bật thay vì cấp 50% RAM riêng cho từng engine.
2. **P1 — Cache/executor an toàn hơn:** khóa `UnifiedCache`, giữ đúng kiểu tuple, bổ sung interface parity cho fallback executor, và cho executor mặc định dùng `get_cpu_threads()` thay vì số core tối đa.
3. **P2 — Chặn realtime quá tải và dọn process khi đóng profile:** giới hạn tối đa 4 generation realtime đang chạy, hủy future khi timeout/shutdown, dừng cả process đang active trong pool, và không warmup Kokoro khi engine đang tắt.
4. **Follow-up review — profile switch không được làm chết runtime:** phát hiện executor bị shutdown vĩnh viễn sau `profile_will_close`, trong khi Anki không reload add-on khi chuyển profile. Đã thêm re-init executor/pool khi `profile_did_open` (xem §4.10).

**Kết quả automated trên Linux:**

- `340 passed, 1 skipped` trong 5.7 giây (tổng 341 test được thu thập).
- `ruff`, `bandit`, coverage critical gate, vendor dependency check và package verification đều đạt.
- Package build ra `SuperFreeTTS.ankiaddon` khoảng **2.22 MiB** (2,328,523 bytes).
- **EdgeTTS vẫn bị chặn cứng ở 3 worker.** Manual override của local engine vẫn được giữ nguyên trong trần `get_max_workers()` và chỉ cảnh báo, không tự ý hạ xuống.

**Việc còn lại quan trọng nhất:** kiểm định thủ công trên **macOS và Windows thật** với model local thật, đo RSS thực tế của từng engine, rồi mới cân nhắc chỉnh các hằng số ước lượng. Hiện chưa có model local trong môi trường Linux này nên chưa thể đo RSS thật của Piper/Kokoro/MMS/Supertonic.

---

## 2. Mục tiêu và phạm vi

### Mục tiêu

- Giảm nguy cơ Anki bị ăn quá nhiều RAM hoặc crash khi batch nhiều thẻ với local engine.
- Không để một allocation spike làm GC chạy lặp lại vô ích.
- Không để các pool local engine chiếm nhiều hơn ngân sách RAM đã định.
- Bảo toàn quyền override của người dùng, nhưng phải cảnh báo rõ nếu override vượt ngưỡng an toàn.
- Dọn sạch executor/process khi đóng profile hoặc khi uninstall engine.
- Không thêm dependency mới, không thêm binary biên dịch sẵn.

### Ngoài phạm vi lần này

- Không đổi version `26.10.2`.
- Không push, không merge, không phát hành GitHub release.
- Không upload/update AnkiWeb.
- Không dọn `external/`.
- Không thêm bản dịch máy.
- Không thiết kế lại UI hay thay đổi kiến trúc engine.

---

## 3. Trạng thái Git và release

| Mục | Giá trị |
|---|---|
| Nhánh làm việc | `fix/resource-management` |
| Commit gần nhất | `004d73b` — `fix: restore runtime after profile switch` |
| Commit trước đó | `292668e` — `fix: harden resource management and background cleanup` |
| Commit cha của đợt chính | `f4ac372` |
| `main` local | `94d24bc` — release `26.10.1` |
| `origin/main` | `94d24bc` — release `26.10.1` |
| Đã push? | **Chưa** |
| Đã release? | **Chưa** |
| Đã cập nhật AnkiWeb? | **Chưa** |
| Version hiện tại | `26.10.2` |

Sau commit `292668e`, bước review P1 đã phát hiện một hồi quy: `profile_will_close` shutdown executor vĩnh viễn, nhưng Anki **không reload add-on** khi người dùng chuyển profile. Commit `004d73b` sửa hồi quy này và thêm test hồi quy (§4.10).

Working tree sạch sau khi commit tài liệu handoff. Các artifact `coverage.json`, `.coverage`, `dist/` và `SuperFreeTTS.ankiaddon` là file generated và đã nằm trong `.gitignore`.

Commit `292668e` thay đổi 19 file: 10 file source và 9 file test. Commit follow-up `004d73b` thay đổi 9 file: 5 file source và 4 file test. Không có thay đổi trong `external/`, `manifest.json`, `version.py`, locales hay release notes.

---

## 4. Những gì đã hoàn thành

### 4.1. P0 — Đọc current RSS thay vì peak RSS

**Vấn đề cũ:** fallback không có `psutil` dùng `resource.getrusage(...).ru_maxrss`. Đây là **peak RSS**, không bao giờ giảm, nên sau một spike RAM thì monitor cứ tưởng process vẫn đang dùng nhiều RAM và kích hoạt GC liên tục.

**Đã sửa trong `resource_manager.py`:**

- Linux: đọc `/proc/self/statm` để lấy resident pages hiện tại.
- macOS: dùng Mach `task_info(MACH_TASK_BASIC_INFO)` qua `ctypes` để lấy `resident_size`.
- Windows: dùng `GetProcessMemoryInfo` để lấy `WorkingSetSize`.
- `ru_maxrss` chỉ còn là **last-resort fallback** khi không đọc được current RSS.
- Thêm `get_process_ram_source()` để log nguồn đo, ví dụ `linux_proc`, `macos_task_info`, `windows_working_set`, `peak_fallback`, `unavailable`.
- Không bắt buộc phải có `psutil`; nếu có thì vẫn dùng `psutil`, nếu không có thì dùng các API hệ điều hành ở trên.

**Test:** `tests/test_resource_manager_current_rss.py` và các test cũ trong `tests/test_ram_aware_concurrency.py`.

---

### 4.2. P0 — Sửa GC hysteresis

**Vấn đề cũ:** baseline GC dựa trên initial/peak RAM. Một spike 300–500 MB có thể làm mọi lần kiểm tra sau đó đều thấy “RAM tăng” và gọi `gc.collect()` lặp lại.

**Đã sửa:**

- `SimpleResourceMonitor` giữ `_last_gc_ram_mb` và `_last_gc_items`.
- `ResourceMonitor` cũng giữ baseline tương tự.
- Sau mỗi lần GC, baseline được cập nhật bằng RSS **hiện tại**, không phải peak.
- Nếu RSS hiện tại thấp hơn baseline (OS đã trả bộ nhớ), baseline được hạ xuống theo giá trị mới.
- Ngưỡng hiện tại:
  - `SimpleResourceMonitor`: tăng hơn **300 MB** kể từ lần GC trước, hoặc mỗi **100 item**.
  - `ResourceMonitor`: tăng hơn **500 MB** kể từ lần GC trước, hoặc mỗi **50 item**.

**Kết quả đo hành vi:**

- Giả lập spike: RSS `26 MB → 386 MB → 26 MB`.
- `ru_maxrss` vẫn là `386 MB` (đúng bản chất peak), nhưng current RSS sau khi giải phóng là `26 MB`.
- `should_gc()` trả `False` sau khi RAM đã giảm và cho các item 2–11.
- `should_gc()` trả `True` trở lại ở item 101 theo interval 100 item.

---

### 4.3. P0 — Một ngân sách RAM chung cho các local engine

**Vấn đề cũ:** `compute_ram_aware_concurrency()` được gọi riêng cho từng engine và mỗi lần đều giả định được dùng 50% RAM khả dụng. Bật 4 local engine có thể khiến tổng “đặt trước” lên tới ~200% RAM.

**Đã thêm `system_utils.allocate_local_engine_workers()`:**

- Chỉ các engine **đang bật** mới tiêu ngân sách.
- Engine tắt nhận placeholder **1 worker** và không tiêu RAM budget.
- Ngân sách chung mặc định = **50% RAM khả dụng**.
- Mỗi engine đang bật được đảm bảo tối thiểu **1 worker**.
- Phần budget còn lại được chia **round-robin**, engine có chi phí RAM/process thấp hơn được ưu tiên tăng trước.
- Không vượt quá CPU cap của từng engine.
- Nếu ngay cả mức tối thiểu 1 worker/engine cũng vượt budget, vẫn giữ 1 worker và trả cờ `minimum_over_budget` để caller cảnh báo. Không tự tắt engine.
- Manual override được giữ nguyên; allocator không tự hạ số người dùng đã đặt. Trần cứng duy nhất là `get_max_workers()` (cap kèm warning); EdgeTTS vẫn bị cap cứng ở 3.
- Nếu không đo được RAM, tự động quay về CPU cap (hành vi cũ), không bịa số RAM.

**Đã sửa `tts_orchestrator.build_engine_config()`:**

- Nhận `enabled_services` để lọc engine đang bật.
- Default local worker dùng `get_cpu_threads()` (16 logical CPU → 8), không dùng `get_max_workers()`.
- EdgeTTS luôn là `min(3, requested)`; nếu user đặt 99 thì log warning và vẫn dùng **3**.
- Manual override local được giữ, nhưng nếu vượt ước lượng an toàn thì log `[RAM-WARN]`.
- Log thêm `[RAM]`, `[RAM-CAP]`, `[RAM-WARN]` để dễ chẩn đoán từ log của Anki.
- `SuperFreeTTS` khởi tạo và `reconfigure_service_manager()` đều truyền map enabled-service vào cấu hình executor.

**File chính:** `superfreetts_addon/system_utils.py`, `superfreetts_addon/tts_orchestrator.py`, `superfreetts_addon/superfreetts.py`.

---

### 4.4. P1 — `UnifiedCache` thread-safe và đúng kiểu tuple

**Đã sửa trong `batch_executor.py`:**

- Thêm `threading.RLock()` bảo vệ `get()`, `put()`, `clear()` và `stats()`.
- Ở size-based mode, value được lưu dạng `(value, size_bytes)` và `get()` unwrap đúng.
- Khi size mode tắt, **không unwrap** tuple tùy ý nữa. Trước đây cache có thể trả sai giá trị nếu caller cache một tuple hợp lệ.
- Việc xóa entry cũ và trừ `current_size` được thực hiện nhất quán khi ghi đè key.

**Test:** `tests/test_batch_executor_unified.py` (bao gồm test cache đồng thời và tuple value).

---

### 4.5. P1 — Fallback executor có interface tương đương

**Đã sửa:**

- `UnifiedBatchExecutor.get_executor(service_name=None)` trả về pool duy nhất; tham số `service_name` chỉ để tương thích interface.
- `UnifiedBatchExecutor.detect_service(task)` dùng chung logic `_detect_service_from_task()`.
- `MultiEngineExecutor` mặc định dùng `get_cpu_threads()` và có thêm pool `MMS` trong cấu hình mặc định.

**Mục đích:** batch flow có thể chạy với `MultiEngineExecutor` hoặc fallback `UnifiedBatchExecutor` mà không bị lỗi do thiếu method/khác chữ ký.

---

### 4.6. P2 — Giới hạn realtime generation

**Đã sửa trong `ttsplayer.py`:**

- Hằng số `MAX_REALTIME_IN_FLIGHT = 4`.
- Mỗi lần `_play()` phải lấy slot trước khi submit.
- Nếu đã có 4 generation đang chạy, `_play()` trả `None` ngay và log warning, không xếp thêm việc.
- Timeout generation vẫn là **20 giây** (`REALTIME_GENERATE_TIMEOUT_SECONDS`).
- Khi timeout: `future.cancel()` (best effort), trả `None`, và slot chỉ được giải phóng khi future thực sự kết thúc.
- Slot được giải phóng qua `add_done_callback`.
- `shutdown()` đặt `_executor_shutdown = True`, shutdown executor và cố gắng `cancel_futures=True`; các lần `_play()` sau đó bị từ chối ngay.
- Exception thật (không phải timeout) vẫn propagate như hành vi cũ, không bị nuốt.

**File test:** `tests/test_ttsplayer_realtime_timeout.py`.

---

### 4.7. P2 — `SherpaProcessPool` dọn cả process đang active

**Đã sửa trong `services/service_mms.py`:**

- Pool theo dõi process đang được thuê trong `_active`.
- `release_process()` chuyển process khỏe mạnh về idle pool, hoặc terminate process lỗi.
- `stop_all()` lấy **cả active lẫn idle**, terminate toàn bộ, đóng stdin/stdout/stderr, xóa `_pool`/`_active`, đưa `_total_spawned` về 0, và hủy cleanup timer.
- Các bộ đếm được clamp `max(0, ...)` để tránh âm khi cleanup lặp.

**Trước đây:** chỉ process trong idle pool bị dừng; process đang chạy có thể sống sót sau khi đóng profile và giữ model/RAM/pipe.

**Test:** `tests/test_sherpa_process_pool.py`.

---

### 4.8. P2 — Dọn executor và pool khi đóng profile

**Đã sửa trong `superfreetts.py` và `gui.py`:**

- `SuperFreeTTS.shutdown()`:
  - flush usage tracker;
  - shutdown batch executor với `wait=False`;
  - gọi `stop_all()` cho cả bốn pool: Piper, Kokoro, MMS, Supertonic.
- Hook `profile_will_close` trong `gui.py` gọi:
  - `tts_player.shutdown()` (dừng realtime executor);
  - `hypertts.shutdown()` (dừng batch executor + local pools).
- Mỗi bước đều có `try/except` riêng để một subsystem lỗi không chặn các bước cleanup còn lại.

**Test:** `tests/test_shutdown_cleanup.py`.

---

### 4.9. P2 — Kokoro warmup và uninstall đúng pool

**Đã sửa trong `services/service_kokoro.py`:**

- Warmup được chuyển khỏi `__init__` sang `configure()`.
- Chỉ warmup khi `self.enabled` là `True`.
- Có `_warmup_lock` + `_warmup_started` để tránh tạo nhiều thread warmup.
- Trong `_low_priority_warmup()` vẫn kiểm tra lại `self.enabled` sau thời gian chờ, phòng trường hợp user tắt engine trong lúc chờ.
- Khi uninstall Kokoro, `component_kokoro_manager.py` gọi `_kokoro_pool.stop_all()` thay vì dừng nhầm pool MMS.

**Test:** `tests/test_kokoro_warmup_gating.py`, `tests/test_kokoro_uninstall_error.py`.

---

### 4.10. Follow-up — Khôi phục runtime khi chuyển profile

**Vấn đề phát hiện khi review P1:** `profile_will_close` gọi `shutdown()` và đánh dấu executor/player đã tắt. Tuy nhiên Anki **không reload add-on** khi người dùng Close Profile rồi mở lại (hoặc chuyển sang profile khác); chỉ có hook `profile_did_open` chạy lại. Vì vậy sau lần đóng profile đầu tiên:

- `MultiEngineExecutor` / `UnifiedBatchExecutor` đã shutdown nhưng vẫn là singleton → batch tiếp theo lỗi `cannot schedule new futures after shutdown`.
- `AnkiSuperFreeTTSPlayer` giữ `_executor_shutdown=True` → realtime TTS từ chối mọi thẻ cho đến khi khởi động lại Anki.
- `SherpaProcessPool.stop_all()` hủy cleanup timer nhưng không bật lại → process idle của Piper/Kokoro/MMS/Supertonic không bao giờ hết hạn sau khi mở lại profile.

**Đã sửa trong commit `004d73b`:**

- `SuperFreeTTS` thêm cờ `_shutdown` và `on_profile_reopened()`; chỉ re-init khi profile thực sự được mở lại, không chạy lại ở lần mở đầu tiên.
- `gui.py` đăng ký `profile_did_open` để gọi `hypertts.on_profile_reopened()` và `tts_player.restart()`.
- `batch_executor.get_multi_engine_executor()` / `get_batch_executor()` tự tạo instance mới nếu instance cũ đã shutdown.
- `ttsplayer.restart()` tạo `ThreadPoolExecutor` mới; thêm generation counter để callback của executor cũ không trừ nhầm slot in-flight của executor mới. `_play()` cũng xử lý `CancelledError` khi future bị hủy lúc shutdown.
- `SherpaProcessPool` thêm `_cleanup_enabled` + `_ensure_cleanup_timer()`; cleanup timer được bật lại lazily ở `get_process()` sau khi pool được dùng lại.

**Test:** `tests/test_shutdown_cleanup.py` (3 test reopen), `tests/test_batch_flow.py` (2 test singleton recreate), `tests/test_ttsplayer_realtime_timeout.py` (1 test restart), `tests/test_sherpa_process_pool.py` (1 test timer restart).

**Chưa xác minh thủ công:** hành vi Close Profile → mở lại trên Anki thật (macOS/Windows) vẫn nằm trong checklist §9.

---

## 5. File đã thay đổi trong commit `292668e`

### Source

| File | Nội dung chính |
|---|---|
| `superfreetts_addon/resource_manager.py` | Current RSS cho Linux/macOS/Windows, peak fallback, source diagnostics, GC baseline |
| `superfreetts_addon/system_utils.py` | RAM detection, shared allocator, CPU helper |
| `superfreetts_addon/tts_orchestrator.py` | Enabled-engine filtering, shared budget, Edge cap, manual warnings, logging |
| `superfreetts_addon/batch_executor.py` | Cache lock/tuple fix, GC hysteresis, fallback executor parity, CPU-aware defaults |
| `superfreetts_addon/ttsplayer.py` | Realtime in-flight cap, timeout, shutdown |
| `superfreetts_addon/services/service_mms.py` | Active process tracking, `stop_all()` cleanup |
| `superfreetts_addon/services/service_kokoro.py` | Warmup gating, one-start guard, enabled re-check |
| `superfreetts_addon/superfreetts.py` | Shutdown wiring, enabled-service map vào orchestrator |
| `superfreetts_addon/gui.py` | Profile-close shutdown hook |
| `superfreetts_addon/component_kokoro_manager.py` | Uninstall dừng đúng `_kokoro_pool` |

### Test

- Mới: `tests/test_resource_manager_current_rss.py`
- Mới: `tests/test_sherpa_process_pool.py`
- Mới: `tests/test_shutdown_cleanup.py`
- Mới: `tests/test_kokoro_warmup_gating.py`
- Cập nhật: `tests/test_system_utils_ram.py`
- Cập nhật: `tests/test_ram_aware_concurrency.py`
- Cập nhật: `tests/test_batch_executor_unified.py`
- Cập nhật: `tests/test_ttsplayer_realtime_timeout.py`
- Cập nhật: `tests/test_kokoro_uninstall_error.py`

### Follow-up commit `004d73b`

Source:

- `superfreetts_addon/superfreetts.py` — cờ `_shutdown`, `on_profile_reopened()`, flush an toàn.
- `superfreetts_addon/gui.py` — re-init khi `profile_did_open`.
- `superfreetts_addon/batch_executor.py` — singleton tự tạo lại sau shutdown.
- `superfreetts_addon/ttsplayer.py` — `restart()`, generation counter, xử lý cancel.
- `superfreetts_addon/services/service_mms.py` — cleanup timer tự bật lại sau `stop_all()`.

Test:

- Cập nhật: `tests/test_shutdown_cleanup.py`
- Cập nhật: `tests/test_batch_flow.py`
- Cập nhật: `tests/test_ttsplayer_realtime_timeout.py`
- Cập nhật: `tests/test_sherpa_process_pool.py`

---

## 6. Kết quả đo trên Linux

> RAM khả dụng thay đổi theo thời điểm. Các kịch bản phân bổ dưới đây được chạy với `available_ram_mb = 6,880 MB` (budget 3,440 MB) để tái lập; một lần đo độc lập khác thấy 7,213 MB. Host có 16 logical CPU, tổng RAM 15,358 MB; `get_cpu_threads()` trả 8, `get_max_workers()` trả 16.

### 6.1. Import footprint

| Chỉ số | Giá trị |
|---|---:|
| RSS sau import | 26,872 kB (~26 MB) |
| Threads | 1 |
| File descriptors | 4 |
| Nguồn RSS của process | `linux_proc` |

### 6.2. Phân bổ worker theo engine

| Kịch bản | Kết quả | Ghi chú |
|---|---|---|
| Chỉ EdgeTTS | Edge 3; local 1 mỗi engine | Edge luôn bị cap 3 |
| Chỉ Piper | Piper 8 | Chạm CPU cap, budget dư |
| Chỉ Kokoro | Kokoro 6 | 6 × 500 MB = 3,000 MB |
| Piper + Kokoro | Piper 7, Kokoro 4 | Ước tính ~3,400 MB |
| Cả 4 local engine | 2 mỗi engine | Ước tính ~3,400 MB |
| Cả 4 local, RAM khả dụng 3,000 MB | 1 mỗi engine | Budget 1,500 MB < mức tối thiểu 1,700 MB → warning |
| Kokoro manual = 10 | Kokoro 10 | Giữ override, log `[RAM-WARN]` |
| Edge manual = 99 | Edge 3 | Cap cứng + warning |
| Không đo được RAM | Piper 8, Kokoro 8; local tắt = 1 | Quay về CPU cap |

Các giá trị RAM/process vẫn là **ước tính**, không phải benchmark model thật:

| Engine | Ước tính |
|---|---:|
| Piper | 200 MB/process |
| Kokoro | 500 MB/process |
| MMS | 500 MB/process |
| Supertonic | 500 MB/process |

Các ước tính này lấy từ báo cáo người dùng và được chọn thiên về an toàn. Chưa có model local trong môi trường hiện tại để đo RSS thực tế.

---

## 7. Automated gates đã chạy

### 7.1. Test suite

```bash
python -m pytest tests/ -q --tb=short
```

Kết quả mới nhất:

```text
340 passed, 1 skipped in 5.74s
```

Test skip:

```text
tests/test_mms_active.py:33: English MMS model not found in voice list
```

Đây là skip do môi trường không có model MMS tiếng Anh, không phải regression.

### 7.2. Lint và security

```bash
ruff check superfreetts_addon tests scripts
bandit -r superfreetts_addon -ll
```

- `ruff`: pass.
- `bandit`: không có finding mức medium/high.

### 7.3. Coverage critical gate

```bash
python -m pytest tests/ -q \
  --cov=superfreetts_addon \
  --cov-report=json:coverage.json
python scripts/check_critical_coverage.py coverage.json
```

Kết quả:

| Module | Coverage |
|---|---:|
| `batch_executor.py` | 77.2% |
| `config_models.py` | 71.1% |
| `component_text_processing.py` | 96.7% |
| `audio_file_store.py` | 89.7% |
| `voice_cache.py` | 91.8% |

Critical gate: **pass**.

### 7.4. Vendor dependencies

```bash
python scripts/vendor_deps.py --check
```

Kết quả: pass cho chuỗi dependency `requests`. Không thêm `psutil` và không thêm binary biên dịch sẵn.

### 7.5. Package build và verify

```bash
python build_share.py
python scripts/verify_package.py
```

Kết quả:

- `SuperFreeTTS.ankiaddon`: **2,328,523 bytes** (~2.22 MiB).
- `verify_package.py`: pass.
- Package smoke:
  - `ram_mb=10853`
  - `ram_source=linux_meminfo`
  - `edge_cap=3`
  - `requests=2.32.4`
  - `aiohttp=3.13.3`
  - `edge_tts=7.3.1`

Lưu ý: artifact `.ankiaddon`, `coverage.json`, `.coverage` và `dist/` là generated, đã được gitignore; không nằm trong commit.

---

## 8. Những gì chưa thể xác minh / còn hạn chế

| Hạng mục | Trạng thái | Lý do |
|---|---|---|
| RSS thật của Piper/Kokoro/MMS/Supertonic | **Chưa đo** | Không có model local trong môi trường Linux |
| Anki peak RAM / swap / crash trên macOS thật | **Chưa kiểm định** | Không có máy macOS |
| Anki peak RAM / swap / crash trên Windows thật | **Chưa kiểm định** | Chưa chạy test thủ công trên Windows |
| Hành vi thực tế của `task_info` macOS | Mới test logic/unit | Cần chạy trên macOS thật |
| Hành vi thực tế của `GetProcessMemoryInfo` Windows | Mới test logic/unit | Cần chạy trên Windows thật |
| Timeout realtime 20 giây | Giá trị conservative, chưa benchmark mạng thật | Cần theo dõi log khi mạng chậm |
| `MAX_REALTIME_IN_FLIGHT = 4` | Giá trị conservative | Có thể chỉnh nếu thực tế quá chặt |
| Close Profile → mở lại trong cùng phiên Anki | Mới test unit | Cần xác minh trên Anki thật rằng executor, realtime và local pool đều dùng lại được |
| Dừng process đang chạy giữa một call Python | Không thể interrupt an toàn trong cùng process | Chỉ dừng được process con của pool; call đang chạy trong process chính vẫn có thể hoàn tất |
| Manual override vượt budget | **Được giữ nguyên có chủ đích** | Chỉ cảnh báo, không tự hạ mà không báo; riêng trần `get_max_workers()` và Edge hard-cap 3 vẫn áp dụng kèm warning |

### Rủi ro cần theo dõi

1. Nếu ước tính RAM/process quá thấp, budget có thể vẫn cho phép quá nhiều worker. Cần đo thật để cập nhật bảng `RAM_PER_PROCESS_MB_ESTIMATE`.
2. Nếu ước tính quá cao, engine có thể bị giảm worker quá mức. Người dùng vẫn có thể override thủ công.
3. Trên macOS/Windows, API đọc RSS có thể trả giá trị khác `psutil`; cần đối chiếu log `get_process_ram_source()` và Activity Monitor/Task Manager.
4. Realtime timeout không hủy được call đang chạy; nó chỉ ngăn call đó chặn playback và giới hạn số call bị bỏ bằng 4.
5. Việc đóng profile gọi cleanup với `wait=False`; process con được terminate, nhưng không nên kỳ vọng mọi thread Python đang chạy dở sẽ dừng ngay lập tức.

---

## 9. Việc cần làm tiếp theo

### Ưu tiên P0 — Kiểm định thực tế trước khi release

- [ ] **macOS thật:** mở Anki, đo RSS nền, bật Piper/Kokoro/MMS/Supertonic, chạy batch ~500 thẻ, ghi lại peak RSS, swap và số process con.
- [ ] **Windows thật:** lặp lại quy trình tương tự bằng Task Manager/Resource Monitor.
- [ ] Kiểm tra log có các dòng `[RAM]`, `[RAM-CAP]`, `[RAM-WARN]` và nguồn đo đúng (`macos_task_info` / `windows_working_set`).
- [ ] Đo RSS thật của từng local engine (1 process, model thật), cập nhật `RAM_PER_PROCESS_MB_ESTIMATE` nếu số liệu khác đáng kể.
- [ ] Chạy realtime 100+ thẻ với EdgeTTS, bao gồm tình huống mạng chậm/ngắt; xác nhận UI không treo và số generation in-flight không vượt 4.
- [ ] **Chuyển profile:** trong Anki, Close Profile rồi mở lại cùng profile **không thoát app**; chạy batch local và realtime, xác nhận executor hoạt động lại, không có process mồ côi, và idle process vẫn được dọn sau 180 giây.
- [ ] Đóng profile khi batch đang chạy; xác nhận không còn process Piper/Kokoro/MMS/Supertonic hoặc runner Python mồ côi.
- [ ] Test Kokoro đang tắt: restart Anki, xác nhận không có process warmup. Sau đó bật Kokoro và xác nhận warmup chạy đúng một lần.
- [ ] Test uninstall Kokoro khi đang có process chạy; xác nhận process bị dừng và file không còn bị khóa.
- [ ] Test manual override: Kokoro = 10 phải được giữ nguyên kèm warning; Edge = 99 phải bị hạ về 3 kèm warning.

### Ưu tiên P1 — Trước khi merge/release

- [x] Review lại commit `292668e` và diff của 19 file. Review phát hiện hồi quy profile switch; đã sửa trong `004d73b` kèm test.
- [ ] Chạy lại toàn bộ gate trên môi trường đích (ít nhất Linux + một máy Windows/macOS).
- [ ] Cập nhật handoff/CHANGELOG nếu có thay đổi số liệu hoặc hành vi sau kiểm định.
- [ ] Chỉ sau khi có kết quả thực tế mới cân nhắc tinh chỉnh timeout, in-flight cap hoặc RAM estimate.

### Ưu tiên P2 — Release (chỉ khi được duyệt rõ ràng)

- [ ] Push nhánh `fix/resource-management`.
- [ ] Tạo PR/merge theo quy trình.
- [ ] Build lại package từ commit cuối cùng.
- [ ] Verify package.
- [ ] Tạo GitHub release/tag nếu được duyệt.
- [ ] Upload AnkiWeb nếu được duyệt.
- [ ] Giữ nguyên version `26.10.2` cho đến khi release được duyệt.

> **Không tự động làm các bước release.** Handoff này không phải là approval để push, publish GitHub release hay cập nhật AnkiWeb.

---

## 10. Checklist kiểm định thủ công chi tiết

### A. Batch local engine trên macOS/Windows

1. Mở Anki, ghi lại RSS nền của tiến trình Anki và số process con.
2. Bật 4 local engine: Piper, Kokoro, MMS, Supertonic.
3. Chạy batch khoảng 500 thẻ.
4. Theo dõi:
   - RSS hiện tại và peak;
   - số process con;
   - swap;
   - thời gian phản hồi UI.
5. Mở log, tìm:
   - `[RAM] source=... available_mb=... budget_mb=...`;
   - `[RAM-CAP] ...`;
   - `[RAM-WARN] ...`.
6. Kỳ vọng:
   - không OOM/crash;
   - số process không vượt quá allocation;
   - budget chung không bị vượt quá mức hợp lý;
   - không có dấu hiệu GC chạy liên tục sau một spike.

### B. Realtime EdgeTTS

1. Bật EdgeTTS cho realtime.
2. Ôn tập 100+ thẻ liên tục.
3. Giữa chừng tắt Wi-Fi trong 10–30 giây rồi bật lại.
4. Kỳ vọng:
   - UI không bị treo vĩnh viễn;
   - request lỗi/timeout không chặn các thẻ sau;
   - log không cho thấy hàng đợi generation tăng vô hạn;
   - số generation in-flight tối đa là 4.

### C. Đóng profile / shutdown

1. Bắt đầu batch lớn hoặc làm ấm local pool.
2. Đóng profile Anki ngay khi process đang chạy.
3. Kiểm tra Activity Monitor (macOS) hoặc Task Manager (Windows):
   - không còn process con TTS mồ côi;
   - không còn runner Python của Kokoro/MMS/Piper/Supertonic.
4. Mở lại Anki, xác nhận không bị lỗi file lock/process cũ.

### D. Kokoro

1. Tắt Kokoro trong settings, restart Anki.
2. Xác nhận không có process Kokoro warmup.
3. Bật Kokoro, restart hoặc mở settings; xác nhận warmup chạy đúng một lần.
4. Trong lúc Kokoro đang chạy, thử uninstall engine.
5. Kỳ vọng: process bị dừng, uninstall không báo lỗi file đang bị khóa.

### E. Manual override

1. Đặt `concurrency_workers = 10` cho Kokoro.
2. Khởi động batch.
3. Kỳ vọng: Kokoro dùng 10 worker, log có `[RAM-WARN]`, không bị tự hạ.
4. Đặt `concurrency_workers = 99` cho EdgeTTS.
5. Kỳ vọng: Edge dùng 3 worker, log có warning cap.

### F. Chuyển profile không restart Anki

1. Mở Anki, chạy thử một batch nhỏ hoặc realtime để chắc executor đang hoạt động.
2. Vào File → Close Profile (hoặc chuyển sang profile khác).
3. Mở lại profile vừa đóng, **không thoát Anki**.
4. Chạy lại batch local và realtime.
5. Kỳ vọng:
   - batch không lỗi `cannot schedule new futures after shutdown`;
   - realtime TTS vẫn phát được;
   - log có `[SHUTDOWN] Profile reopened; recreating executors` và `restarted realtime TTS executor after profile reopen`;
   - sau 180 giây idle, process local engine vẫn được dọn bình thường.

---

## 11. Lệnh để tiếp tục

```bash
cd /home/admin/Documents/deepseek-harness/default-workspace/superfreetts

git status
git log --oneline -5
git show --stat 292668e
git show --stat 004d73b

python -m pytest tests/ -q --tb=short

ruff check superfreetts_addon tests scripts
bandit -r superfreetts_addon -ll

python build_share.py
python scripts/verify_package.py
```

Kiểm tra diff trước khi commit (file nguồn dùng CRLF):

```bash
git -c core.whitespace=cr-at-eol diff --check
```

---

## 12. Ghi chú bàn giao

- **Không push** nhánh này nếu chưa có approval.
- **Không đổi version** `26.10.2` nếu chưa có release approval.
- **Không dọn `external/`** trong phạm vi task này.
- **Không thêm** `psutil` hoặc binary biên dịch sẵn.
- **EdgeTTS hard cap = 3** là invariant, không được nâng trong committed source.
- Manual override local được giữ nguyên có chủ đích; chỉ cảnh báo, không tự hạ mà không báo. Ngoại lệ có chủ đích: trần `get_max_workers()` và EdgeTTS hard cap 3, cả hai đều log warning.
- Commit `004d73b` khôi phục executor/pool sau khi chuyển profile; khi sửa tiếp phần shutdown/reopen, giữ nguyên hành vi: lần mở profile đầu tiên không re-init, chỉ re-init sau khi `shutdown()` đã chạy.
- Tài liệu này được đặt tại `AI_Documents/HANDOFF_RESOURCE_MANAGEMENT.md`.
