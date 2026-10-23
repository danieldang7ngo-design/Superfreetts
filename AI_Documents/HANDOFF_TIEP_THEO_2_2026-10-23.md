# HANDOFF 2 — sau Cổng 1 (2026-10-23)

> Kế thừa `HANDOFF_TIEP_THEO_2026-10-23.md` (đã thay thế). Đọc thêm
> `trien-khai-cong-1-2026-10-23.md` để biết Cổng 1 đã làm gì và kiểm chứng ra sao.

- **Nhánh:** `fix/resource-management`
- **HEAD:** `55bdce9` + commit handoff này (docs) — code cuối: `a7de221`
- **Phiên bản:** `26.10.2` — **giữ nguyên**, chưa push, chưa tag/release
- **Môi trường đã xác minh:** Linux x86_64, Python 3.14.8, 16 logical CPU, ~15,4 GB RAM
- **Trạng thái:** Cổng 1 xong (P1-2, P1-3, phần unit-test của P1-5). Cổng 2 chưa
  làm. Người dùng đã chốt 5 quyết định — việc tiếp theo là **A+B** (mục 3).

---

## 0. Đọc gì trước

1. `AI_Documents/AGENTS.md` — quy tắc repo (CRLF, EdgeTTS cap 3, undo entry, …).
2. `AI_Documents/trien-khai-cong-1-2026-10-23.md` — Cổng 1: deadline IPC,
   checkpoint v2, ngân sách thread, các gate đã chạy, và **phát hiện §2.5**.
3. File này — việc còn lại, theo thứ tự ưu tiên.

---

## 1. Đang ở đâu (nói gọn)

- **Đã xong:** P1-2 (deadline IPC + kill/retry), P1-3 (checkpoint theo note ID),
  phần code + unit test của P1-5 (ngân sách thread).
- **Test:** 420 passed, 1 skipped. **Ruff OK. Bandit Medium 0 / High 0.**
  Coverage gate OK (`batch_executor` 80,7%). Gói build+verify OK, 83,98 MB.
- **Chưa xong:** A+B (mục 3), định dạng âm thanh (mục 4), điều tra RAM Kokoro
  (mục 5), bỏ OGG (mục 6), CHANGELOG (mục 7), các phép đo trên máy thật (mục 8),
  Cổng 2 nhỏ (mục 9).
- **Code chết đang chờ xoá:** `process_batch_audio()`, `batch_state_manager.py`,
  `UnifiedBatchExecutor.execute()`, `MultiEngineExecutor.execute()`,
  `_execute_single_task()`.

---

## 2. Năm quyết định người dùng đã chốt (2026-10-23)

| # | Chủ đề | Quyết định | Hệ quả cho code |
|---|---|---|---|
| 1 | Định dạng âm thanh | Lưu đúng định dạng engine xuất ra; **vẫn giữ lựa chọn convert**; nếu engine đã ra đúng định dạng người dùng chọn thì **không convert lại** | Mục 4 |
| 2 | RAM Kokoro | Không tin con số 2.400 MB/runner; phải kiểm tra lại cách đo | Mục 5 |
| 3 | OGG | Bỏ; chỉ giữ định dạng phổ thông (MP3, WAV) | Mục 6 |
| 4 | Đường batch cũ | **A + B**: xoá "máy cũ" `process_batch_audio()` **và** gắn sổ tiến độ (checkpoint) vào "máy thật" (`component_batch_preview`) | Mục 3 |
| 5 | Version/CHANGELOG | Giữ **26.10.2**, không tăng; chỉ **thêm nội dung** vào release notes/CHANGELOG | Mục 7 |

---

## 3. Việc ưu tiên 1 — A+B: xoá máy cũ, gắn sổ tiến độ vào máy thật

### 3.1. Nhắc lại cho dễ hiểu

- **Máy cũ** = `BatchOrchestrator.process_batch_audio()`. Làm hết mọi thứ trong
  một lần, có sổ tiến độ, nhưng **không có nút nào trên giao diện gọi nó**.
- **Máy thật** = cửa sổ Batch Preview (`component_batch_preview.py`). Người dùng
  bấm "Tạo audio" → "Áp vào note" (25 note mỗi lần). **Không có sổ tiến độ.**
- Việc cần làm: **chuyển sổ tiến độ sang máy thật**, rồi **xoá máy cũ**.

**Thứ tự khuyến nghị: làm B trước (gắn checkpoint vào preview), sau đó A (xoá).**
Làm B trước để `BatchCheckpoint` không có lúc nào bị bỏ không.

### 3.2. B — gắn checkpoint vào Batch Preview

Những gì đã có sẵn, **không cần viết lại**:

- `batch_executor.CheckpointManager` (ghi atomic, migrate v1).
- `batch_executor.BatchCheckpoint` (`load_existing`, `pending_note_ids`,
  `mark_generated`, `mark_applied`, `mark_error`, `flush`, `remove`).
- `_execute_unique_tasks_unified(..., checkpoint=None)` đã nhận checkpoint.

Các bước sửa:

1. **`batch_orchestrator.generate_prepared_batch_audio(prepared_batch,
   batch_status, checkpoint=None)`** — thêm tham số tuỳ chọn và truyền xuống
   `_execute_unique_tasks_unified(..., checkpoint)`. Không đổi hành vi khi
   `checkpoint is None` (workflow vẫn chạy như cũ).
2. **`component_batch_preview.py`**:
   - Thêm `self.batch_checkpoint = None` trong `__init__`.
   - **Khoá checkpoint phải ổn định giữa các lần chạy.** Đừng dùng
     `str(batch_model)`, `str(batch_model.text_processing)` hay
     `str(batch_model.voice_selection)`: `TextProcessing` không có `__str__`
     nên in ra địa chỉ bộ nhớ (`<... object at 0x...>`) → mỗi lần mở là một khoá
     khác, resume không bao giờ khớp.
   - Cách đúng: tạo checkpoint **sau khi prepare** (trong
     `finished_prepare_audio_fn`, nơi đã có `prepared_batch['dedup_map']`), khoá
     dựa trên dữ liệu đã chuẩn hoá:
     ```python
     def preview_checkpoint_key(batch_model, note_ids, dedup_map):
         # dedup key = hash(text + voice + options + format); đổi giọng, đổi
         # định dạng hay đổi text processing đều làm key đổi, nên không skip nhầm.
         target = batch_model.target
         fingerprint = "|".join([
             ",".join(str(n) for n in note_ids),
             str(getattr(batch_model, "name", "") or ""),
             str(getattr(target, "target_field", "")),
             str(getattr(target, "text_and_sound_tag", "")),
             str(getattr(target, "remove_sound_tag", "")),
             "|".join(sorted(str(k) for k in dedup_map.keys())),
         ])
         return "preview-" + hashlib.sha1(fingerprint.encode("utf-8")).hexdigest()[:16]
     ```
     `CheckpointManager._get_path()` tự lọc ký tự lạ nên tên này an toàn.
   - `finished_prepare_audio_fn()`: tạo
     `BatchCheckpoint(hypertts.executor.checkpoint, key, note_id_list)`, gọi
     `load_existing()`; nếu có note đã `applied`:
     - log + `batch_status.set_status_message("Tiếp tục: bỏ qua N note đã ghi")`;
     - set các note đó sang `BatchNoteStatus.Done` để bảng preview hiển thị đúng;
     - giữ `self.batch_checkpoint` cho bước generate/apply.
   - `generate_audio_fn()` → `generate_prepared_batch_audio(prepared, status,
     self.batch_checkpoint)`.
   - `_run_next_apply_chunk()`: lấy `chunk_note_ids = [row[0] for row in chunk]`,
     **lọc các note đã applied** khỏi chunk (resume), rồi truyền danh sách ID
     vào `_chunk_success(result, chunk_note_ids)`.
   - `_chunk_success()`: `self.batch_checkpoint.mark_applied(chunk_note_ids)`
     (hàm này flush ngay) rồi mới gọi chunk kế tiếp.
     Chỉ mark **sau** khi `apply_generated_batch_audio_chunk()` đã
     `update_notes()` thành công (nó nằm trong `QueryOp`, `_chunk_success` là
     sau commit).
   - `_apply_chunk_failed()`: `self.batch_checkpoint.flush()` rồi xử lý lỗi như
     cũ — giữ file để lần sau resume.
   - `stop_button_pressed()`: `self.batch_checkpoint.flush()` — huỷ thì giữ tiến
     độ, không xoá.
   - `finished_apply_audio_fn()`: `self.batch_checkpoint.remove()` khi xong.
   - Không cần thêm nút "Tiếp tục": thông báo resume hiện ra khi người dùng bấm
     "Tạo audio" (sau bước prepare). Nếu muốn gợi ý sớm hơn, quét thư mục
     checkpoint trong `load_model()` và hiện câu chung (đừng thử tính lại khoá
     khi chưa prepare).
3. **Resume hoạt động thế nào (thiết kế đã chọn):** mở lại batch → bấm "Tạo
   audio" → engine sinh lại nhưng **trúng cache audio gần như tức thì** → bước
   apply bỏ qua các note đã `applied`. Nhờ vậy không phải lưu tên file audio
   trong checkpoint, và không bao giờ ghi trùng (đã có guard chống trùng
   `[sound:...]`).
4. **Test cần thêm:**
   - Unit cho `preview_checkpoint_key`: cùng đầu vào → cùng khoá; đổi
     giọng/định dạng/target field → khoá khác; **không phụ thuộc địa chỉ bộ nhớ**
     (gọi 2 lần trên 2 object khác nhau, cùng nội dung → cùng khoá).
   - Unit: checkpoint có 2 note `applied` → chunk apply lọc đúng, note còn lại
     vẫn được áp; xong thì file checkpoint bị xoá.
   - Unit: huỷ giữa chừng → file còn, `pending_note_ids()` đúng.
   - Có thể tái dùng cách dựng component trong
     `tests/test_batch_preview_preset_switch.py` (mock Anki/Qt).
5. **Test tay (bắt buộc trước khi coi là xong):**
   - Batch 200 note, bấm "Tạo audio" rồi "Áp vào note"; `kill -9` Anki khi đang
     áp (khoảng 50–100 note).
   - Mở lại Anki + batch với cùng lựa chọn → thấy gợi ý tiếp tục; bấm Tạo audio
     → áp tiếp; kiểm tra: không note nào mất audio, không note nào có 2
     `[sound:...]` giống nhau.
6. **Rủi ro:** khoá phụ thuộc `dedup_map` — nếu bước prepare không tạo lại đúng
   danh sách (ví dụ người dùng đổi text processing), khoá đổi và resume bắt đầu
   lại từ đầu. Đó là hành vi **an toàn** (thà làm lại còn hơn skip nhầm).

### 3.3. A — xoá máy cũ

1. `superfreetts_addon/batch_orchestrator.py`: xoá hàm `process_batch_audio`.
   **Giữ** `apply_generated_batch_audio()` và `apply_generated_batch_audio_chunk()`
   (workflow + preview còn dùng).
2. `superfreetts_addon/superfreetts.py`: xoá facade `process_batch_audio`
   (khoảng dòng 201–202).
3. `tests/test_batch_checkpoint.py`: xoá 3 test gọi `process_batch_audio`
   (`test_completed_checkpoint_returns_without_regenerating`,
   `test_resume_generates_and_applies_only_pending_notes`,
   `test_cancelled_batch_keeps_checkpoint_for_resume`). **Giữ** toàn bộ test
   `CheckpointManager`/`BatchCheckpoint` (đó là phần dùng cho B).
4. Chạy `ruff` để xoá import thừa; `grep -rn "process_batch_audio"` chỉ còn
   trong tài liệu là đạt.
5. Cập nhật `AI_Documents/trien-khai-cong-1-2026-10-23.md` §2.5: ghi "đã xoá
   theo quyết định A+B, checkpoint đã chuyển sang preview".

### 3.4. Tiêu chí hoàn thành A+B

- [ ] Preview resume đúng sau crash giữa lúc áp note (test tay ở 3.2.5).
- [ ] `grep process_batch_audio` không còn trong code.
- [ ] 420+ test xanh, ruff/bandit/build xanh.
- [ ] Không có `[sound:...]` trùng sau khi resume.

---

## 4. Định dạng âm thanh (quyết định 1)

**Nguyên tắc:** engine ra gì lưu nấy; chỉ convert khi người dùng chọn khác định
dạng gốc **và** có bộ chuyển; không convert khi đã đúng định dạng.

Hiện trạng cần biết:

- `audio_file_store.AudioFileStore.resolve_audio_format()` quyết định định dạng
  theo preference/voice options; `build_request_key()` **hash cả `audio_format`**;
  `write_audio_file_atomic()` đặt tên file theo **byte thực tế**
  (`detect_audio_format`) — đừng phá hai điều này.
- EdgeTTS: luôn trả MP3 (`service_edgetts.py`), không có decode MP3→WAV.
- Piper: runner trả WAV; `service_piper.py` tự convert WAV→MP3 bằng
  `aqt.sound._encode_mp3` khi preference là mp3.
- Kokoro / MMS / Supertonic: trả WAV, **chưa** có convert sang MP3.

Việc cần làm:

1. Tạo một helper chung (ví dụ `superfreetts_addon/audio_transcode.py` hoặc thêm
   vào `audio_file_store.py`): `native_format_for(engine)`,
   `convert_audio(audio_bytes, target_format)`; WAV→MP3 dùng
   `aqt.sound._encode_mp3` (Anki đã có), MP3→WAV **không hỗ trợ** (thiếu decoder
   đóng gói) → giữ MP3 + log một lần.
2. Chuyển logic convert của Piper sang helper chung; bật convert WAV→MP3 cho
   Kokoro/MMS/Supertonic khi preference = mp3.
3. `resolve_audio_format()`: nếu preference trùng định dạng gốc của engine thì
   trả đúng định dạng đó, **không** yêu cầu convert. Nếu convert thất bại/không
   hỗ trợ, khoá cache phải phản ánh **định dạng thật** (đừng để key nói wav mà
   file là mp3).
4. Ghi rõ trong UI/helper: EdgeTTS luôn MP3; muốn WAV cần bộ giải mã (chưa có).
5. Test: 5 engine × {mp3, wav} × {single, batch}; đọc magic bytes; trường hợp
   "đã đúng định dạng" không được gọi convert (mock và assert không gọi).
6. Đo nhanh chi phí convert 500 file WAV→MP3 (có thể ảnh hưởng thời gian batch).

**Rủi ro:** convert thêm CPU vào batch; nếu chậm, chỉ convert khi người dùng
thực sự chọn định dạng khác (đúng như quyết định).

---

## 5. RAM Kokoro (quyết định 2)

Người dùng nghi ngờ 2.400 MB/runner là quá cao ("một TTS không thể tốn nhiều RAM
vậy"). Số cũ đến từ "tree RSS" — **RSS cộng cả trang dùng chung** của thư viện
(MKL/OpenMP/torch) cho từng process, nên có thể phóng đại.

Việc cần làm (trên máy có Kokoro đã cài):

1. Đo **PSS/USS** thay vì RSS cây:
   ```bash
   pgrep -af kokoro_runner.py
   grep -E "VmRSS|RssAnon|RssFile|RssShmem" /proc/<pid>/status
   cat /proc/<pid>/smaps_rollup     # Pss là con số đáng tin cho "RAM thật"
   ```
2. So sánh: 1 runner rảnh, 1 runner đang load model, 2 runner cùng chạy.
3. Kiểm tra runner dùng gì: PyTorch CPU hay onnxruntime; có load model 2 lần
   không; import nặng nào (torch, numpy…) đang chiếm phần lớn.
4. Chỉ sau khi có số PSS mới sửa:
   - `tts_orchestrator.RAM_PER_PROCESS_MB_ESTIMATE['KokoroTTS']`
   - `KOKORO_MAX_AUTO_WORKERS` (hiện 2)
5. Thêm test pin số mới trong `tests/test_ram_aware_concurrency.py` /
   `tests/test_thread_budget.py`.

**Không hạ cap khi chưa đo** — máy 8 GB có thể OOM thật.

---

## 6. Bỏ OGG (quyết định 3)

Giữ tương thích, chỉ bỏ phần tạo mới:

1. `options.AudioFormat`: bỏ `ogg_opus`/`ogg_vorbis` khỏi đường tạo mới; giữ
   `_normalize_format()` trong `audio_file_store.py` map mọi giá trị ogg →
   WAV (kèm cảnh báo một lần) để config/voice option cũ không lỗi.
2. `get_cached_file()` vẫn dò `.ogg` để **đọc cache cũ** — đừng xoá file người
   dùng đang dùng; chỉ không sinh `.ogg` mới.
3. `services/voicelist.py` còn `ogg_vorbis` trong option của vài voice cũ
   (khoảng dòng 604+): kiểm tra xem file này còn được nạp không; nếu còn, đổi
   danh sách giá trị sang `['mp3']`.
4. Locale: rà các câu nhắc OGG (`locales/*.json`); **không dịch máy** — câu
   tiếng Hàn cần người review, các ngôn ngữ khác có thể chỉnh theo bản tiếng Anh.
5. Test: không sinh `.ogg`; file `.ogg` cũ vẫn tìm thấy qua cache; preference
   `ogg` cũ → WAV + cảnh báo một lần.

---

## 7. Version + CHANGELOG (quyết định 5)

- **Không** đổi `manifest.json` / `version.py` (giữ `26.10.2`).
- Thêm bullet vào `release_notes.RELEASE_NOTES[0]` cho cả 7 ngôn ngữ và mục
  `## 26.10.2` trong `CHANGELOG.md` (English + Tiếng Việt).
- Chạy `tests/test_version_consistency.py` để chắc 4 nơi vẫn khớp.
- Nội dung dự kiến: deadline IPC + retry; checkpoint theo note ID (sau khi A+B
  xong); ngân sách thread; không nhân đôi `[sound:...]`; chính sách định dạng;
  bỏ OGG; (nếu có) số RAM Kokoro mới.

---

## 8. Việc phải làm trên máy thật (không làm được ở máy dev này)

| Việc | Cách làm | Tiêu chí |
|---|---|---|
| Ma trận worker × thread (P1-5) | Mỗi engine × worker {1,2,4,8} × thread {1,4,8}, 100–500 item | Bảng mean/P95, peak PSS; ghi `superfreetts_data/benchmark/` |
| `SIGSTOP` runner giữa request | Xem `trien-khai-cong-1-2026-10-23.md` §1.4 | Request lỗi trong deadline, kill + retry, batch tiếp tục, không rò permit |
| Piper spawn mỗi request | 500 item, so spawn vs persistent | Chỉ đổi nếu mean giảm ≥15–20% và không tăng rủi ro treo |
| `fsync` từng file cache | 500 file, SSD và HDD, có/không `fsync` | Chỉ bỏ nếu chênh >5% |
| Cold start sau 180 s idle | Đo request đầu cho từng engine | Nếu realtime hay timeout 20 s → tăng idle TTL hoặc prewarm có kiểm soát |

Chưa có số đo thì **không đổi default** và **không công bố "nhanh hơn X%"**.

---

## 9. Cổng 2 — việc nhỏ làm được ngay (không cần đo)

1. **EdgeTTS `data += chunk`** (`service_edgetts.py`, khoảng dòng 354) → dùng
   `bytearray`/list + `b"".join()`.
2. **Cleanup cache chạy nền** (`superfreetts.py`, khoảng dòng 119): đang chạy
   trong `__init__` trên luồng chính → chuyển ra nền sau khi mở profile, có
   lock với lúc ghi cache; đo thời gian khởi động với 10k file.
3. **Xoá code chết** (sau khi A+B xong): `batch_state_manager.py` +
   `UnifiedBatchExecutor.execute()` + `MultiEngineExecutor.execute()` +
   `_execute_single_task()`; xoá test tương ứng (`tests/test_batch_state_manager.py`,
   phần `TestMultiEngineBatchFlow` trong `tests/test_batch_flow.py`,
   `tests/test_import.py` bỏ import `batch_state_manager`).
4. **EdgeTTS luôn MP3**: đã chốt giữ MP3; ghi rõ trong helper/UI (mục 4).
5. **Locale `ko`**: nhờ người Hàn review; không machine-translate.

---

## 10. Quy tắc & cạm bẫy (bổ sung cho AGENTS.md)

- **CRLF:** file `.py` nguồn dùng CRLF; sau khi sửa phải kiểm tra bằng số byte:
  ```bash
  python - <<'PY'
  import pathlib
  d = pathlib.Path('superfreetts_addon/batch_orchestrator.py').read_bytes()
  print(d.count(b'\r\n'), d.count(b'\n'))   # phải bằng nhau
  PY
  ```
  `file -b` có thể báo sai (file `system_utils.py` bị nhận là "Generic INItialization").
- **Không push, không tag/release, không đổi version** nếu chưa được duyệt.
- **EdgeTTS cap 3** — bất biến.
- Mọi `add_custom_undo_entry` phải `merge_undo_entries` trên **mọi** nhánh thoát.
- **Coverage cần `.venv/bin/python`** — python hệ thống thiếu `pytest-cov`, chạy
  `python -m pytest --cov` sẽ báo `unrecognized arguments`.
- **Checkpoint:** chỉ dùng note ID, không dùng index; ghi atomic; at-least-once;
  apply idempotent (guard chống trùng `[sound:...]` đã có).
- **IPC deadline:** request đầu của process mới dùng deadline cold-start; stream
  đã EOF phải trả `b""` ngay (test `tests/test_ipc_deadline.py`).
- **Ngân sách thread:** chỉ tính pool đang bật; override thủ công không bị hạ.
- Không commit `meta.json`, `user_files/`, `coverage.json`, `*.ankiaddon`, `dist/`.

---

## 11. Gates (copy/paste)

```bash
# test
python -m pytest tests/ -q --tb=short                       # 420 passed, 1 skipped

# coverage (bắt buộc dùng venv)
.venv/bin/python -m pytest tests/ -q --cov=superfreetts_addon \
  --cov-report=json:coverage.json
python scripts/check_critical_coverage.py coverage.json

# lint + bảo mật
.venv/bin/python -m ruff check superfreetts_addon tests scripts
.venv/bin/python -m bandit -r superfreetts_addon -ll

# gói
python build_share.py && python scripts/verify_package.py
```

---

## 12. Checklist bàn giao

- [ ] `git status` sạch; `git log --oneline -8` khớp mục "Đang ở đâu".
- [ ] Chạy baseline 420 test + gates trước khi sửa.
- [ ] B: gắn checkpoint vào `component_batch_preview` + test + test tay crash.
- [ ] A: xoá `process_batch_audio` + facade + test cũ; `grep` sạch.
- [ ] Định dạng âm thanh theo mục 4.
- [ ] Bỏ OGG theo mục 6.
- [ ] CHANGELOG/release notes 26.10.2 theo mục 7.
- [ ] Điều tra RAM Kokoro theo mục 5 (cần máy thật; nếu chưa có thì ghi lại).
- [ ] Cổng 2 nhỏ (mục 9) — làm dần, mỗi việc một commit + test.
- [ ] Cập nhật handoff + `trien-khai-cong-1-2026-10-23.md` khi xong.
- [ ] Không push/release nếu chưa có approval rõ ràng.
