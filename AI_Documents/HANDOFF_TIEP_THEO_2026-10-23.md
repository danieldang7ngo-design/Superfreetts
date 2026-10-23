# HANDOFF — Việc tiếp theo sau Cổng 0 (2026-10-23)

> Tài liệu này thay thế phần "việc cần làm tiếp" của `HANDOFF_RESOURCE_MANAGEMENT.md`
> và dựa trên báo cáo `bao-cao-kiem-toan-superfreetts-2026-10-22.md` cùng ghi chú
> `trien-khai-cong-0-2026-10-23.md`.

- **Ngày bàn giao:** 2026-10-23
- **Nhánh:** `fix/resource-management`
- **HEAD:** `69b668c` (docs) — commit code cuối: `b30c676`
- **Phiên bản:** `26.10.2` — **giữ nguyên**, chưa push, chưa tag/release
- **Môi trường đã xác minh:** Linux x86_64, Python 3.14.8, 16 logical CPU, ~15,4 GB RAM
- **Trạng thái:** Cổng 0 đã xong và có test. Cổng 1–2 chưa làm.

---

## 1. Trạng thái hiện tại

### 1.1. Cổng 0 đã xong

| Commit | Nội dung |
|---|---|
| `cfda747` | Kokoro auto ≤ 2 worker; estimate Kokoro 2.400 MB, Supertonic 700 MB |
| `f91fbe4` | Default WAV; bỏ OGG khỏi UI; tên file theo magic bytes; xoá cache sai đuôi |
| `b30c676` | Cảnh báo format chỉ log một lần mỗi trường hợp |
| `917bd91` | Cleanup chỉ xoá cache audio; MMS dọn temp WAV trong `finally` |
| `69b668c` | Tài liệu: báo cáo kiểm toán + ghi chú triển khai Cổng 0 |

Hành vi đã thay đổi (đừng "sửa lại" mà không đọc commit):

- `audio_format` mặc định là **`wav`**; UI chỉ còn `wav`/`mp3`; preference `ogg` cũ
  hoặc voice option `format=ogg`/`pcm` → WAV kèm cảnh báo.
- File âm thanh được đặt tên theo **byte thực tế** (`detect_audio_format`), không theo
  format yêu cầu. Cache hit dò `.mp3`/`.wav`/`.ogg` cho cùng hash.
- Kokoro auto-scale bị chặn ở **2** (`KOKORO_MAX_AUTO_WORKERS`), áp cả khi không đo
  được RAM; override `concurrency_workers` vẫn được tôn trọng.
- `cleanup_user_files()` chỉ xoá `superfreetts-<sha224>.(mp3|wav|ogg)`.

### 1.2. Kiểm chứng đã chạy

```bash
python -m pytest tests/ -q                                   # 377 passed, 1 skipped
python -m pytest tests/ -q --cov=superfreetts_addon \
  --cov-report=json:coverage.json && \
  python scripts/check_critical_coverage.py coverage.json    # OK, audio_file_store 90,3%
.venv/bin/python -m ruff check superfreetts_addon tests scripts   # OK
.venv/bin/python -m bandit -r superfreetts_addon -ll              # Medium 0 / High 0
python build_share.py && python scripts/verify_package.py         # OK, 83,97 MB
```

### 1.3. Còn nguyên sau Cổng 0

- **P1-2** IPC không timeout, semaphore chờ vô hạn.
- **P1-3** checkpoint chỉ lưu cuối batch; resume trộn index; `execute()` chết `O(n²)`.
- **P1-5** chưa có ngân sách thread `Σ workers × threads`; chưa có ma trận đo.
- **P2** Piper spawn mỗi request, `fsync` từng file, EdgeTTS `+=`, cold start, code chết,
  locale helper, EdgeTTS luôn MP3 khi default WAV.

---

## 2. Quy tắc làm việc trong repo này

Đọc `AI_Documents/AGENTS.md` trước. Các điểm dễ làm hỏng:

1. **File nguồn dùng CRLF** (`superfreetts_addon/*.py`, `locales/*.json`, service).
   Nếu ghi bằng `write_text()`/`Path.write_text()` mặc định, cả file thành LF và diff
   phình lên hàng nghìn dòng. Sau khi sửa, kiểm tra:
   ```bash
   git -c core.whitespace=cr-at-eol diff --check
   file -b superfreetts_addon/audio_file_store.py   # phải ghi "with CRLF line terminators"
   ```
   Nếu lỡ mất CRLF: `data.replace(b'\r\n', b'\n').replace(b'\n', b'\r\n')`.
2. **Không push, không đổi version, không tag/release** nếu chưa được duyệt.
3. **EdgeTTS hard cap = 3** (`batch_constants.EDGETTS_MAX_WORKERS`) — bất biến.
4. Mọi `add_custom_undo_entry` phải `merge_undo_entries` trên **mọi** nhánh thoát
   (xem `component_batch_preview.py`, `_apply_chunk_failed`).
5. Không commit `meta.json`, `user_files/`, `coverage.json`, `*.ankiaddon`, `dist/`.
6. Không thêm `psutil` hay binary biên dịch sẵn; không dọn `external/` trong phạm vi này.
7. Test dùng `tests/mock_anki.py`; chạy `python -m pytest`, không cần Anki thật.

---

## 3. Cổng 1 — Ổn định batch/realtime (làm theo thứ tự)

### 3.1. P1-2 — Deadline IPC + kill/restart runner (ưu tiên cao nhất)

**Hiện trạng**

| Điểm | Vị trí |
|---|---|
| `DynamicSemaphore.acquire()` chờ vô hạn trên `Condition` | `services/service_mms.py:24-28` |
| `SherpaProcessPool.get_process()` gọi `acquire()` không timeout | `services/service_mms.py:109-112` |
| `stdout.readline()` không timeout | MMS `:517`, `:609`; Kokoro `service_kokoro.py:279`, `:347`; Supertonic `service_supertonic.py:346`, `:383`; Piper `service_piper.py:346`, `:474` |
| Piper chỉ có timeout 30 s cho **binary** bên trong runner | `services/piper_runner.py:160-172` |
| Stall detector toàn cục 180 s, chỉ kích hoạt khi **không future nào xong** | `batch_orchestrator.py:696-753`, `batch_constants.py:62` |
| Realtime timeout 20 s chỉ bỏ future, không kill runner | `ttsplayer.py:190-208` |

Hệ quả: một runner treo giữ worker + permit; các future khác vẫn xong nên stall
detector **không** phát hiện; pool cạn dần; người dùng phải restart Anki.

**Thiết kế đề xuất**

1. Thêm `acquire(timeout=...)` cho `DynamicSemaphore` (dùng
   `Condition.wait(timeout)` + trả `False` khi hết hạn). `get_process()` trả lỗi
   "engine busy" thay vì treo.
2. Bọc mỗi lời gọi `readline()` bằng watchdog: reader thread + `queue.Queue.get(timeout)`,
   hoặc `select`/`poll` trên POSIX + thread trên Windows. Deadline khởi điểm:
   **60 s single**, **120 s chunk batch** (P95 hiện tại 1,6–29,9 s); tách deadline
   "first request sau idle" (cold start Kokoro/Supertonic ~10 s cho 3 request).
3. Khi hết hạn: `kill()` + `wait()` + đóng pipe, đánh dấu process `is_healthy = False`,
   release permit, rồi **retry 1 lần** với process mới. Nếu vẫn lỗi → trả lỗi cho đúng
   các note trong chunk.
4. Với batch: timeout theo **chunk** (5 item), ghi lỗi cho từng note; không chỉ dựa vào
   stall toàn cục. Giữ stall detector như lưới an toàn cuối.
5. Metric/log: thời gian chờ process, số lần timeout, số lần restart runner
   (`[IPC] timeout engine=... waited=...s action=kill+retry`).

**Test/acceptance**

- Unit: fake process có `stdout.readline` treo → call trả lỗi trong deadline; permit
  được release; process bị kill; retry dùng process mới.
- Tích hợp tay: `SIGSTOP` runner giữa request → request kết thúc trong deadline, batch
  tiếp tục, không rò semaphore; sau đó `SIGCONT`/kill dọn sạch.
- Không được giết request hợp lệ khi cold start: test riêng first-request sau 180 s idle.

**Rủi ro/đánh đổi**

- Kill process làm mất model trong RAM → request sau chậm hơn (Kokoro ~10 s cold start).
- Deadline quá thấp giết request hợp lệ trên máy yếu; nên đọc từ hằng số, không hard-code
  rải rác, và log khi timeout để tinh chỉnh.

**Ước lượng:** M–L (3 file service + pool + test).

---

### 3.2. P1-3 — Checkpoint theo chunk/note ID, bỏ executor chết

**Hiện trạng**

- Đường active `process_batch_audio()` chỉ lưu checkpoint **sau khi đã apply xong toàn bộ**
  note: `batch_orchestrator.py:539-550`. Không lưu trong `except`, `finally`, khi hủy,
  hay sau từng chunk.
- Resume: `completed_indices` là index của danh sách **gốc**; sau khi lọc,
  `note_id_list` chỉ còn pending (`:347-364`), nhưng lúc lưu lại duyệt
  `range(len(results))` và append index của danh sách **đã lọc** (`:546-550`).
  → resume lần hai bị lệch tập note.
- Nếu checkpoint đã hoàn tất: code xoá checkpoint nhưng **không return**, batch chạy lại
  từ đầu (`:354-357`).
- `UnifiedBatchExecutor.execute()` (`batch_executor.py:343`) và
  `MultiEngineExecutor.execute()` (`:552`) có lưu sau từng item nhưng **không được gọi**
  (`_execute_unique_tasks_unified()` mới là đường chạy). Chúng còn tạo
  `[t['note_id'] for t in tasks]` mỗi vòng → `O(n²)` CPU/I-O.

**Thiết kế đề xuất**

1. Lưu checkpoint **theo chunk** (5 item) hoặc mỗi 50 note, sau khi generation và sau khi
   apply; lưu tối thiểu `{note_id: status}` với status `generated` / `applied`.
2. Chỉ lưu **tập note ID ổn định**, không lưu hai list index; ghi atomic
   (`write temp + os.replace`) và giữ file nhỏ.
3. Resume theo `note_id`; nếu crash giữa apply, kiểm tra note đã có sound tag trước khi
   ghi lại (idempotent). Chọn rõ at-least-once hay exactly-once và ghi vào tài liệu.
4. Xoá hoặc đánh dấu deprecated `UnifiedBatchExecutor.execute()` /
   `MultiEngineExecutor.execute()`; thêm test import để không ai dùng lại.
5. Khi checkpoint báo hoàn tất: xoá rồi **return** ngay.

**Test/acceptance**

- Kill tiến trình ở 25/50/75% rồi resume: không mất note, không apply trùng, đúng tập ID.
- Hủy batch giữa chừng: checkpoint tồn tại và resume đúng.
- Batch 10.000 note: số lần ghi ~200 file nhỏ, không nghẽn UI.

**Ước lượng:** M.

---

### 3.3. P1-5 — Ngân sách thread + ma trận worker × thread

**Hiện trạng**

- `get_cpu_threads()` trả `min(cpu_count - 1, 8)` (`system_utils.py:104-115`);
  `get_max_workers()` trả toàn bộ logical CPU (`:119-125`).
- `build_engine_config()` cấp worker theo RAM nhưng **không** kiểm tra
  `Σ workers × num_threads`.
- Service mặc định `num_threads = 1` (`service_kokoro.py:197`, `service_mms.py:387`,
  `service_piper.py:107`); benchmark dùng 2 worker × 8 thread cho Kokoro/MMS/Supertonic.
- Hệ quả: có thể 8 worker × 8 thread = 64 thread trên 16 CPU.

**Thiết kế đề xuất**

1. Định nghĩa `total_threads = Σ workers × threads`; đảm bảo
   `total_threads ≤ get_total_cpu_count()` (dùng logical CPU thật, **không** dùng
   `get_cpu_threads()` làm tổng ngân sách). Vượt → cảnh báo, chỉ tự hạ khi auto.
2. Chọn default theo profile (ví dụ 16 GB/16 CPU): Kokoro 1×8 hoặc 2×8; Piper 4×1;
   MMS/Supertonic 2×4 — nhưng **chỉ chốt sau khi đo**.
3. Chạy ma trận tối thiểu: mỗi engine × worker {1,2,4,8} × thread {1,4,8}, 100–500 item,
   đo mean/P95/peak tree RSS. Ghi kết quả vào `superfreetts_data/benchmark/`.
4. Chỉ công bố "batch nhanh hơn X%" kèm cấu hình worker/thread + RAM.

**Test/acceptance**

- Unit: cấu hình 8×8 trên 16 CPU → có cảnh báo/hạ; 2×8 → hợp lệ.
- Bảng đo có số; default có bằng chứng, không suy đoán.

**Phụ thuộc:** nên làm sau P1-2 (timeout) để đo batch không bị treo giả.

**Ước lượng:** M (chủ yếu là đo).

---

## 4. Cổng 2 — P2 và các việc nhỏ

| Việc | Vị trí / hiện trạng | Cách làm & ngưỡng quyết định |
|---|---|---|
| **Piper spawn binary mỗi request** | `piper_runner.py:152` `subprocess.Popen` mỗi task; model 63 MB nạp lại | Đo persistent/in-process ONNX trên 500 item. Chỉ đổi nếu mean giảm ≥15–20% và không tăng rủi ro treo. |
| **`fsync` từng file cache** | `audio_file_store.py:277` | Đo batch 500 file có/không `fsync` trên SSD và HDD. Nếu chênh >5% và cache tái sinh được, cân nhắc bỏ (atomic rename vẫn đủ cho hầu hết trường hợp). |
| **EdgeTTS `data += chunk`** | `service_edgetts.py:354` | Đổi sang `bytearray`/list + `b"".join()`; đo text dài. Rủi ro thấp. |
| **Cold start sau idle 180 s** | pool idle `service_mms.py:50`; warmup 3 request: Piper 3,4 s, MMS 4,1 s, Kokoro 10,4 s, Supertonic 10,0 s | Đo request đầu sau 180 s idle cho từng engine; nếu realtime hay bị 20 s timeout → tăng idle TTL hoặc prewarm có kiểm soát (nhớ RAM Kokoro 3,9 GB). |
| **Code chết** | `batch_state_manager.py` không dùng runtime; `resource_manager` chủ yếu còn helper RSS; `execute()` chết; `_execute_single_task` trả `None` | Xoá hoặc đánh dấu deprecated sau khi P1-3 xong; giữ helper RSS; thêm test import. |
| **Locale helper format** | `ko.json:141` còn câu cũ nhắc OGG/mp3; `sv.json:130` câu chung; `ja`/`zh-CN`/`zh-TW` **thiếu key** → fallback tiếng Anh (đã đúng) | Nhờ người review dịch `ko`; không machine-translate (AGENTS §6). `sv` có thể giữ. |
| **EdgeTTS luôn MP3 khi default WAV** | `service_edgetts.py:351-357`; `AudioFileStore` lưu `.mp3` đúng nội dung | Quyết định: chấp nhận (khuyến nghị, không có decoder MP3→WAV đóng gói) hoặc thêm transcode nếu sau này đóng gói decoder. Ghi rõ trong UI/helper. |
| **Cleanup vẫn chạy đồng bộ trên main thread** | `superfreetts.py:119` gọi trong `__init__` | Chuyển sang background sau khi profile mở, có lock với ghi cache; đo thời gian khởi động với 10k file trước/sau. |

---

## 5. Ma trận kiểm chứng (rút từ báo cáo §6)

| Test | Cách chạy | Tiêu chí đạt |
|---|---|---|
| **RAM Kokoro** | 1/2/4 worker × 100/500 item, đo peak tree RSS, có collection 1 GB | Không OOM/swap; peak ≤70% RAM khả dụng; auto ≤2; estimate sai ≤25% |
| **Format** | 5 engine × {mp3,wav} × {single,batch}; đọc magic bytes | 100% file đúng format; không còn `.ogg`; file EdgeTTS là `.mp3` đúng nội dung |
| **Timeout IPC** | `SIGSTOP` runner giữa request | Kết thúc trong deadline; kill/replace runner; không rò permit; batch tiếp tục |
| **Checkpoint** | Kill ở 25/50/75%; resume | Không mất/trùng note; đúng tập ID; resume nhanh |
| **Cleanup** | Tạo cache cũ + usage_log + log + checkpoint; khởi động | Chỉ cache bị xoá; dữ liệu người dùng còn; startup không chặn UI |
| **End-to-end** | 500 note trên máy 8 GB và 16 GB; batch + realtime; đóng/mở profile | 0 OOM, 0 process mồ côi, 0 note thiếu audio |
| **Hiệu năng** | worker {1,2,4,8} × thread {1,4,8} | Bảng mean/P95/RSS; default có bằng chứng |

Lệnh nhanh:

```bash
# Phân bổ worker hiện tại (không cần Anki)
python3 - <<'PY'
import importlib.util
spec = importlib.util.spec_from_file_location('su', 'superfreetts_addon/system_utils.py')
su = importlib.util.module_from_spec(spec); spec.loader.exec_module(su)
avail = su.get_available_ram_mb()
print('available_mb =', avail)
PY

# Gates đầy đủ
python -m pytest tests/ -q --tb=short
python -m pytest tests/ -q --cov=superfreetts_addon --cov-report=json:coverage.json
python scripts/check_critical_coverage.py coverage.json
.venv/bin/python -m ruff check superfreetts_addon tests scripts
.venv/bin/python -m bandit -r superfreetts_addon -ll
python build_share.py && python scripts/verify_package.py
```

---

## 6. Quyết định cần người dùng chốt trước khi code tiếp

1. **Transcode hay "byte thực tế thắng"?** Hiện tại không transcode: EdgeTTS ra `.mp3`,
   local engine ra `.wav`. Nếu muốn mọi file đúng preference, cần đóng gói encoder/decoder
   (ffmpeg) — ảnh hưởng dung lượng gói và CPU batch.
2. **Ngân sách thread:** dùng logical CPU thật hay giữ policy cap 8? Có tự hạ worker khi
   vượt hay chỉ cảnh báo?
3. **Kokoro estimate:** giữ 2.400 MB hay nâng 4.000 MB (worst-case 1 runner) sau khi đo
   1/2/4 worker trên máy thật?
4. **OGG:** có mở lại khi có encoder không, hay bỏ hẳn khỏi code/UI?
5. **Số version kế tiếp + mục CHANGELOG** cho các thay đổi Cổng 0 (hiện chưa ghi
   CHANGELOG vì chưa chốt version).

---

## 7. Bẫy kỹ thuật đã gặp (đừng lặp lại)

- Hash cache **gồm `audio_format`**; đổi field này sẽ làm mất cache toàn bộ người dùng.
  Nếu muốn cache độc lập format, phải có migration rõ ràng.
- `get_cached_file()` dò nhiều extension: đừng "tối ưu" bằng cách chỉ thử extension yêu
  cầu, nếu không file do engine khác format sẽ bị regenerate mỗi lần.
- `write_audio_file_atomic()` trả `AudioFileResult` với tên theo **byte thực tế**; mọi nơi
  dùng `audio_filename` (note updater, batch cache) phải lấy từ kết quả này, không tự
  ghép tên.
- Cleanup chạy trong `__init__` sau `UsageTracker`; nếu chuyển sang background phải giữ
  lock với lúc ghi cache và không xoá file đang được batch dùng.
- Checkpoint nằm ở `user_files/batch_state/` (thư mục con) — vì vậy cleanup cấp 1 không
  đụng tới, nhưng đừng đổi sang quét đệ quy.
- `build_share.py` ghi đè `config.json` trong staging (Edge worker=3, xoá preset); không
  sửa `config.json` repo để "thử" default.
- `tests/test_version_consistency.py` kiểm tra chéo **bốn** chỗ: `manifest.json`,
  `superfreetts_addon/version.py`, `release_notes.RELEASE_NOTES[0]` và `CHANGELOG.md`.
  Đổi version phải sửa đủ cả bốn, nếu không test fail.

---

## 8. Checklist bàn giao cho phiên tiếp theo

- [ ] Đọc `AI_Documents/AGENTS.md`, báo cáo kiểm toán và ghi chú Cổng 0.
- [ ] `git status` sạch, `git log --oneline -6` khớp mục 1.1.
- [ ] Chạy lại 377 test + gates trước khi sửa (baseline).
- [ ] Chốt 5 quyết định ở mục 6.
- [ ] P1-2: thêm deadline + `acquire(timeout)` + kill/retry + test `SIGSTOP`.
- [ ] P1-3: checkpoint theo chunk/note ID; xoá `execute()` chết; test kill 25/50/75%.
- [ ] P1-5: ngân sách thread + ma trận đo; cập nhật default có bằng chứng.
- [ ] P2: chọn việc có số đo trước (Piper persistent, fsync, EdgeTTS bytearray).
- [ ] Cập nhật `CHANGELOG.md` + version khi được duyệt; build/verify lại.
- [ ] Không push/release nếu chưa có approval rõ ràng.
