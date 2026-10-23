# TRIỂN KHAI CỔNG 1 — 2026-10-23

> Ghi chú này đi kèm `HANDOFF_TIEP_THEO_2026-10-23.md`. Nó ghi lại **đã làm gì**,
> **hành vi nào đã thay đổi** và **còn gì chưa làm** sau khi xử lý Cổng 1
> (P1-2, P1-3 và phần kiểm thử đơn vị của P1-5). Số liệu dưới đây đo trên máy
> Linux 16 CPU ngày 2026-10-23.

- **Nhánh:** `fix/resource-management` (không push, không đổi version, không tag)
- **Phiên bản:** vẫn `26.10.2`
- **Test:** 420 passed, 1 skipped (trước Cổng 1: 377 passed, 1 skipped)
- **Gói:** `SuperFreeTTS.ankiaddon` 83,98 MB, `scripts/verify_package.py` OK

---

## 1. P1-2 — Deadline IPC, kill/retry runner

### 1.1. Thay đổi cấu trúc

- **Mới:** `superfreetts_addon/services/process_pool.py`
  - `DynamicSemaphore.acquire(timeout=...)` → trả `False` khi hết hạn (trước đây
    chờ vô hạn trên `Condition`).
  - `SherpaProcessPool` chuyển từ `service_mms.py` sang đây (vẫn re-export ở
    `service_mms.py` để các engine và `tts_orchestrator` không phải sửa import).
  - `start_stdout_reader()`: mỗi runner có một reader thread đọc `stdout` vào
    `queue.Queue`. Nhờ vậy lời gọi đọc không còn nằm trong `readline()` chặn.
  - `read_response()`: chờ tối đa deadline; hết hạn → `terminate()` + `wait()` +
    đóng 3 pipe + `is_healthy = False`, log
    `[IPC] timeout engine=... waited=...s action=kill+retry`, rồi raise
    `IpcTimeoutError`.
  - `EngineBusyError`: không lấy được permit trong deadline → lỗi "engine busy"
    thay vì treo.
  - `request_timeout()`: request đầu tiên trên một process mới dùng deadline
    cold-start; các request sau dùng deadline single/chunk.
- **Sửa:** `service_mms.py`, `service_kokoro.py`, `service_piper.py`,
  `service_supertonic.py` — cả 8 chỗ `process.stdout.readline()` đều đi qua
  `read_response()`, và `IpcTimeoutError` nằm trong nhóm lỗi được **retry 1 lần**.
  `EngineBusyError` là lỗi cuối (không retry), trả lỗi ngay cho note/chunk.

### 1.2. Hằng số (trong `batch_constants.py`)

| Hằng số | Giá trị | Ý nghĩa |
|---|---|---|
| `IPC_SINGLE_REQUEST_TIMEOUT_SECONDS` | 60 s | một request realtime/đơn lẻ |
| `IPC_BATCH_REQUEST_TIMEOUT_SECONDS` | 120 s | một chunk batch (5 item), trùng `TASK_TIMEOUT_SECONDS` |
| `IPC_COLD_START_TIMEOUT_SECONDS` | 150 s | request **đầu tiên** trên runner vừa spawn (Kokoro/Supertonic nạp model ~10 s) |
| `IPC_ACQUIRE_TIMEOUT_SECONDS` | 300 s | chờ permit tối đa; quá hạn → `EngineBusyError` |

### 1.3. Hành vi mới (đừng "sửa lại")

- Runner treo → request kết thúc trong deadline, process bị kill và **retry đúng
  một lần** với process mới; permit luôn được trả ở `finally` của mỗi service.
- Process bị timeout không được quay lại pool (`is_healthy = False`).
- Stream đã đóng (`ipc_stdout_eof`) → `read_response` trả `b""` ngay, không chờ
  hết deadline. Đây là điều kiện để retry dùng process mới thay vì treo thêm
  120–150 s.
- Request đầu tiên của process dùng deadline cold-start; các request sau dùng
  deadline thường. Không áp cold-start cho mọi request (sẽ che giấu treo thật).

### 1.4. Kiểm chứng

`tests/test_ipc_deadline.py` (18 test):

- Semaphore hết hạn trả `False`; `set_max` đánh thức waiter.
- `get_process` khi pool cạn → `EngineBusyError`, **không** trả nhầm permit của
  người khác; spawn lỗi → permit được trả.
- `read_response` với **subprocess thật bị treo** → `IpcTimeoutError` trong
  <5 s, process bị kill, pipe đóng.
- Process chết giữa hai request → lần đọc sau trả EOF ngay (không chờ deadline).
- MMS single/batch với runner treo → lỗi trong deadline, mỗi lần thử đều kill và
  trả permit; `EngineBusyError` không bị retry (chỉ gọi pool 1 lần).
- Test "wiring guard": cả 4 engine không còn `process.stdout.readline()` và mỗi
  file có đúng 2 lời gọi `read_response(...)`.

**Chưa chạy:** bài test `SIGSTOP` thủ công với engine thật (Kokoro/MMS/Supertonic)
vì môi trường này không cài model. Cách chạy khi có engine:

```bash
pgrep -af "kokoro_runner.py"       # tìm PID runner đang chạy
kill -STOP <pid>                   # treo giữa request
# kỳ vọng: log [IPC] timeout ... action=kill+retry, request lỗi trong 60/120 s,
# process bị kill, batch tiếp tục, không rò permit
kill -CONT <pid> 2>/dev/null || true
```

---

## 2. P1-3 — Checkpoint theo note ID

### 2.1. Định dạng v2

`batch_executor.CheckpointManager` lưu:

```json
{
  "version": 2,
  "batch_name": "...",
  "note_ids": [123, 456],
  "statuses": {"123": "applied", "456": "generated"},
  "errors": {"456": "..."},
  "timestamp": "..."
}
```

- Chỉ lưu **tập note ID ổn định** + trạng thái, không còn hai list index.
- Ghi **atomic**: temp file + `flush` + `fsync` + `os.replace`; lỗi giữa chừng
  giữ nguyên file cũ.
- File v1 cũ (`note_id_list` + `completed_indices`) được **migrate khi load**:
  index được ánh xạ sang note ID, không mất tiến độ của người dùng.

### 2.2. `BatchCheckpoint`

- `load_existing()` nạp trạng thái, bỏ qua note không thuộc batch; **giữ lại ID**
  mà lần chạy trước đã lưu để không apply trùng.
- `pending_note_ids()` = note chưa `applied`.
- `mark_generated()` / `mark_applied()` / `mark_error()`.
- `applied` không bao giờ bị hạ về `generated`.
- Flush theo `CHECKPOINT_FLUSH_EVERY = 50` (ghi chú), `mark_applied` flush ngay.
- `remove()` tắt luôn writer để `finally` không tạo lại file.

**Chính sách resume: at-least-once.** Note `applied` được bỏ qua; note
`generated` sinh lại (trúng cache content-addressed) rồi apply lại. Để apply lại
thật sự idempotent, `note_audio_updater.update_note_with_audio()` giờ **không
thêm `[sound:...]` trùng** khi note đã trỏ đúng file audio đó (trước đây chạy lại
batch ở chế độ `text_and_sound_tag` sẽ nhân đôi tag). Không mất note; xấu nhất là
apply trùng một note sau crash giữa lúc ghi note và lúc flush checkpoint.

### 2.3. Luồng batch (`batch_orchestrator.process_batch_audio`)

- Nếu checkpoint **đã apply đủ** → xoá file và **return** (trước đây xoá
  checkpoint nhưng vẫn chạy lại toàn bộ batch).
- Resume: `note_id_list = pending` theo **note ID**, không theo index.
- Generation: mỗi chunk xong → `mark_generated` (flush theo nhịp 50); lỗi/stall
  được ghi vào checkpoint.
- Apply: commit `anki_collection.update_notes()` theo từng chunk
  `CHECKPOINT_APPLY_COMMIT_EVERY = 50` rồi `mark_applied` ngay, thay vì một
  transaction khổng lồ ở cuối. Crash giữa apply chỉ mất tối đa 50 note (apply
  lại, không mất dữ liệu).
- Huỷ batch: `finally` flush checkpoint → lần sau resume đúng.
- Preview (`generate_prepared_batch_audio`) dùng `NullCheckpoint` (không ghi file
  vì không apply).

### 2.4. Kiểm chứng

`tests/test_batch_checkpoint.py` (15 test):

- Lưu/đọc/xoá; ghi atomic (giả lập `os.replace` lỗi → file cũ nguyên vẹn).
- Migrate file v1 `completed_indices` → statuses theo note ID.
- **Kill ở 25/50/75%**: resume nhiều lần vẫn đúng tập note, không note nào bị
  apply hai lần, không index nào bị lệch.
- Resume với danh sách đã lọc vẫn nhớ các note đã apply trước đó.
- Flush theo nhịp 50; `mark_applied` flush ngay; không hạ cấp `applied`.
- Lỗi lưu theo note ID và còn sau khi reload.
- Orchestrator: checkpoint đủ → **không** generate lại, không đụng note, xoá
  checkpoint; resume chỉ generate/apply note pending; huỷ giữa chừng → còn
  checkpoint, resume đủ note.

Test cũ dùng `mock_open` cho API checkpoint cũ đã bị xoá khỏi
`tests/test_batch_executor_unified.py` (được thay bằng bộ test trên).

### 2.5. Phát hiện quan trọng: đường batch đang chạy trong UI

Khi kiểm tra người gọi, `process_batch_audio()` **không còn caller runtime**:

```bash
grep -rn "\.process_batch_audio(" --include=*.py superfreetts_addon   # chỉ facade
grep -rn "generate_prepared_batch_audio\|prepare_batch_audio_generation" \
  --include=*.py superfreetts_addon   # component_batch_preview.py, component_workflow.py
```

Đường UI thật sự chạy là `component_batch_preview.py`
(`prepare_batch_audio_generation` → `generate_prepared_batch_audio`) rồi
`_run_next_apply_chunk()` — apply theo chunk **25 note**, mỗi chunk một QueryOp.
Đường này **không dùng checkpoint**; sau crash, audio đã nằm trong cache
content-addressed nên sinh lại rất nhanh, và apply lại đã idempotent nhờ guard
trên.

Hệ quả:

- P1-3 đã sửa đúng **kho checkpoint** (`CheckpointManager`/`BatchCheckpoint`) và
  đúng logic resume của `process_batch_audio`, nhưng phần resume đó **chưa được
  UI dùng**. Giá trị người dùng thấy hiện tại chủ yếu là: không còn index lệch,
  không còn batch chạy lại khi checkpoint báo xong, apply idempotent.
- Muốn resume thật trong UI cần một việc riêng: lưu checkpoint + sound filename
  trong `component_batch_preview`, và thêm nút/flow "tiếp tục batch" khi mở lại.
  Hoặc ngược lại, quyết định xoá `process_batch_audio()` nếu không còn kế hoạch
  dùng (đã deprecated `execute()` chết tương tự).

---

## 3. P1-5 — Ngân sách thread (phần code + unit test)

- `system_utils.compute_thread_budget(worker_counts, thread_counts, cpu_count)`
  tính `Σ workers × threads`, trả `cpu_count`, `total_threads`, `over_budget`
  và bảng chi tiết từng pool.
- Ngân sách dùng **logical CPU thật** (`get_total_cpu_count()`), **không** dùng
  `get_cpu_threads()` (chỉ là số worker mặc định, cap 8).
- `TTSOrchestrator._enforce_thread_budget()`:
  - chỉ tính các pool **đang bật** (engine tắt vẫn có pool 1 worker nhưng không
    chạy, không chiếm ngân sách — cùng quy tắc với bộ chia RAM);
  - vượt ngân sách → cảnh báo `[THREAD-CAP]` và **tự hạ** worker của các pool
    auto, ưu tiên pool có tích lớn nhất;
  - `concurrency_workers` do người dùng đặt **không bị hạ**, chỉ cảnh báo.
- EdgeTTS không nằm trong ngân sách CPU (network-bound).

`tests/test_thread_budget.py` (9 test): 8×8 trên 16 CPU → vượt/ bị hạ; 2×8 → hợp
lệ; EdgeTTS bị loại; giá trị rác quy về 1; override thủ công được giữ + cảnh
báo; `num_threads` đọc đúng từ cấu hình service.

**Chưa làm:** ma trận đo worker × thread (mục 3.3 của handoff) vì cần engine +
model thật. Vì vậy **default worker/thread giữ nguyên**, chưa có số đo để công bố
"nhanh hơn X%". Khi có máy đích:

```bash
# ví dụ khung đo, chạy với engine đã cài; ghi kết quả vào
# superfreetts_data/benchmark/<engine>-<workers>x<threads>.json
python -m tests.manual_verify_services   # hoặc script đo riêng
```

---

## 4. Gates đã chạy

```text
python -m pytest tests/ -q                                   420 passed, 1 skipped (6,4 s)
python -m pytest tests/ -q --cov=superfreetts_addon \
  --cov-report=json:coverage.json && \
  python scripts/check_critical_coverage.py coverage.json     OK
      config_models 71,1% · batch_executor 77,2% ·
      component_text_processing 96,7% · audio_file_store 90,3% ·
      voice_cache 91,8%
.venv/bin/python -m ruff check superfreetts_addon tests scripts   OK
.venv/bin/python -m bandit -r superfreetts_addon -ll              Medium 0 / High 0
python build_share.py && python scripts/verify_package.py         OK, 83,98 MB
```

---

## 5. Rủi ro / đánh đổi cần biết

- **Kill runner làm mất model trong RAM**: request kế tiếp phải cold start
  (Kokoro ~10 s). Đây là đánh đổi đã chấp nhận để không treo vĩnh viễn.
- **Deadline 60/120/150 s** có thể thấp với máy rất yếu: tất cả nằm ở
  `batch_constants.py`, log `[IPC] timeout` để tinh chỉnh; không hard-code rải rác.
- **Commit theo chunk 50 note** làm tăng số transaction Anki (10.000 note →
  200 lần `update_notes` thay vì 1). Chưa đo ảnh hưởng thời gian; nếu chậm, tăng
  `CHECKPOINT_APPLY_COMMIT_EVERY` (đổi lại: crash có thể mất tiến độ nhiều hơn).
- **Ngân sách thread** có thể hạ concurrency so với trước trên máy nhỏ bật nhiều
  engine. Người dùng vẫn override được bằng `concurrency_workers`/`num_threads`.
- **Code chết**: `UnifiedBatchExecutor.execute()` / `MultiEngineExecutor.execute()`
  đã đánh dấu deprecated (docstring) và sửa sang checkpoint v2; `batch_state_manager.py`
  đánh dấu deprecated. Chưa xoá — cần một quyết định riêng vì còn test import.
- **Realtime 20 s** (`ttsplayer.py`) vẫn chỉ bỏ future; runner giờ bị deadline
  IPC kill trong ≤60 s nên permit được trả, nhưng player không chủ động kill.

---

## 6. Việc tiếp theo

1. Chốt 5 quyết định ở `HANDOFF_TIEP_THEO_2026-10-23.md` §6 (transcode, ngân sách
   thread, Kokoro estimate, OGG, version/CHANGELOG).
2. Đo ma trận worker × thread trên máy thật, cập nhật default có bằng chứng.
3. Chạy `SIGSTOP` thủ công với từng engine đã cài (mục 1.4).
4. Cổng 2: chọn việc có số đo trước (Piper persistent, `fsync`, EdgeTTS
   `bytearray`), rồi cold start, code chết, locale `ko`.
5. Xoá hẳn `batch_state_manager.py` + 2 `execute()` chết khi có quyết định.
6. Quyết định cho `process_batch_audio()` (mục 2.5): hoặc nối checkpoint vào
   `component_batch_preview` + thêm flow resume khi mở lại batch, hoặc xoá
   đường chết này và giữ `CheckpointManager` cho workflow.
