# TRIỂN KHAI A+B + ĐỊNH DẠNG + OGG — 2026-10-23

> Tiếp nối `trien-khai-cong-1-2026-10-23.md` (Cổng 1) và
> `HANDOFF_TIEP_THEO_2_2026-10-23.md` (5 quyết định, việc ưu tiên A+B).
> Nhánh `fix/resource-management`, version giữ **26.10.2**, không push/tag.

- **Test:** 408 passed, 1 skipped (trước: 420 passed — xoá 3 test `process_batch_audio`,
  xoá 21 test `batch_state_manager`, thêm 5 test preview-checkpoint + 7 test transcode).
- **Gates:** ruff OK, bandit "No issues identified", coverage OK
  (config_models 71,1%, batch_executor 80,5%, component_text_processing 96,7%,
  audio_file_store 90,3%, voice_cache 91,8%), version-consistency OK,
  build+verify OK (83,98 MB).
- **Lưu ý công cụ:** coverage bắt buộc `.venv/bin/python -m pytest` (python hệ
  thống thiếu `pytest-cov`).

---

## 1. A+B — checkpoint vào Batch Preview, xoá máy cũ

### 1.1. B — `BatchPreview` resume được sau crash

- **Mới:** `batch_orchestrator.preview_checkpoint_key(batch_model, note_ids, dedup_map)`
  → `"preview-" + sha1(hex)[:16]`. Khoá **không** dùng `str()` của model hay
  text_processing (địa chỉ bộ nhớ làm resume không bao giờ khớp); chỉ hash
  note_ids + tên preset + target field flags + dedup keys đã sort. Đổi giọng,
  format, target hay text processing → khoá đổi → chạy lại từ đầu (an toàn).
- `generate_prepared_batch_audio(..., checkpoint=None)` và facade
  `superfreetts.py` + `_execute_unique_tasks_unified` nhận checkpoint, truyền
  xuống như đường `process_batch_audio` cũ. `None` → hành vi cũ.
- `component_batch_preview.py`:
  - `self.batch_checkpoint` vòng đời: `None` ở `__init__`/`load_model`/
    `generate_audio_to_cache` → tạo trong `finished_prepare_audio_fn` (sau khi
    có `dedup_map`), dùng ở generate + apply, `remove()` khi xong,
    `flush()` khi huỷ/lỗi.
  - `finished_prepare_audio_fn`: tạo checkpoint, `load_existing()`; nếu có note
    `applied` → log + `"Tiếp tục: bỏ qua N note đã ghi"` + set các note đó
    `Done` để bảng preview hiển thị đúng.
  - `generate_audio_fn` truyền checkpoint vào generate.
  - `_run_next_apply_chunk`: lọc note đã `applied` khỏi chunk (resume ở bước
    apply; generation vẫn chạy lại nhưng trúng cache content-addressed nên gần
    như tức thì). Chunk toàn note đã áp → bỏ qua, sang chunk kế.
  - `_chunk_success(result, chunk_note_ids)`: `mark_applied` **sau** commit
    QueryOp. `_apply_chunk_failed`/`stop_button_pressed`/`batch_operation_failed`:
    `flush()`. `finished_apply_audio_fn`: `remove()` nếu xong, `flush()` nếu huỷ.
- Áp lại cùng audio là idempotent (guard chống trùng `[sound:...]` từ Cổng 1),
  nên resume at-least-once không bao giờ ghi trùng.

### 1.2. A — xoá `process_batch_audio`

- Xoá method trong `batch_orchestrator.py`, facade trong `superfreetts.py`, 3 test
  trong `tests/test_batch_checkpoint.py` (giữ toàn bộ test
  `CheckpointManager`/`BatchCheckpoint`), `grep process_batch_audio` sạch code.
- Đính chính handoff cũ: `Unified/MultiEngineExecutor.execute()` và
  `_execute_single_task()` **chưa xoá** — chúng còn caller nội bộ
  (`batch_executor.py:473,663`) và ~10 test đang dùng, chỉ mới deprecated.
  Xoá thật cần một refactor riêng. Chỉ `batch_state_manager.py` (0 caller
  runtime) đã xoá + test của nó + dòng import trong `test_import.py`
  (thay bằng `audio_transcode`).

### 1.3. Test mới — `tests/test_batch_preview_checkpoint.py` (5 test)

- Key ổn định cùng input; đổi target/dedup/notes → key đổi; 2 object cùng nội
  dung → cùng key (không phụ thuộc địa chỉ bộ nhớ).
- Chunk apply bỏ qua note đã applied, note còn lại vẫn áp, xong xoá file.
- Huỷ giữa chừng → giữ file, `pending_note_ids()` đúng.
- Bài test tay crash `kill -9` (handoff §3.2.5) **chưa chạy** — cần Anki + batch
  thật, để mục "việc còn lại".

---

## 2. Định dạng âm thanh (quyết định 1)

- **Mới:** `superfreetts_addon/audio_transcode.py` —
  `native_format_for(service)` (EdgeTTS MP3, còn lại WAV),
  `convert_wav_to_mp3()` (qua `aqt.sound._encode_mp3`, lỗi → raise để caller
  fallback), `maybe_convert()` (đã đúng format → trả về ngay, **không** gọi
  converter; WAV→MP3 thử convert, lỗi giữ WAV + log một lần; MP3→WAV không hỗ
  trợ giữ MP3 + log một lần), `convert_if_requested()` (đọc preference, chỉ
  convert khi user chọn mp3; pref đọc lỗi/thiếu → wav = không convert).
- 8 đường engine bọc `convert_if_requested`: Piper/Kokoro/MMS/Supertonic ×
  {single, batch}. Logic convert inline của Piper single đã chuyển sang helper
  (giữ nguyên hành vi). EdgeTTS giữ nguyên MP3, có ghi trong helper.
- `write_audio_file_atomic` giữ nguyên (lưu theo byte thật + dò magic bytes) như
  lưới an toàn; `build_request_key`/`resolve_audio_format` không đổi.
- **Test:** `tests/test_audio_transcode.py` (7 test) — native map, không convert
  khi đã đúng (assert không gọi converter), WAV→MP3 thành công/thất bại,
  MP3→WAV giữ nguyên, tôn trọng preference.
- Đính chính contract cũ: test `test_wav_bytes_requested_as_mp3_are_saved_with_wav_extension`
  vẫn đúng ở tầng `AudioFileStore` (service bypass); convert xảy ra ở tầng service.

---

## 3. Bỏ OGG (quyết định 3)

- `services/voicelist.py`: toàn bộ `'values': ['mp3', ...ogg...]` (156 + 2236 + 61
  entries, giọng trả phí đã fork bỏ nhưng file vẫn được nạp) → `['mp3']`.
  `grep ogg_vorbis|ogg_opus` trong voicelist sạch.
- Đã có từ trước, xác minh lại: UI chỉ offered wav/mp3 (`component_preferences`),
  helper locale en/vi/ko mô tả đúng chính sách native-format, `_normalize_format`
  map ogg→WAV + cảnh báo một lần, `get_cached_file` vẫn dò `.ogg` để đọc cache cũ.
- Enum `options.AudioFormat` giữ 2 member ogg để preset/config cũ không crash.

---

## 4. Version + CHANGELOG (quyết định 5)

- Giữ **26.10.2** mọi nơi (`manifest.json`, `version.py`), không tag.
- `release_notes.RELEASE_NOTES[0]` + `CHANGELOG.md ## 26.10.2`: thêm 6 bullets
  **en + vi** (IPC deadline+retry, checkpoint note ID + Preview resume + không
  trùng sound tag, thread budget, native-format + convert có điều kiện, OGG
  retire). Các locale ko/ja/zh-CN/zh-TW/sv giữ nguyên để fallback tiếng Anh —
  không machine-translate (theo AGENTS.md §6; đã có tiền lệ ở handoff §9.5).
- `tests/test_version_consistency.py` xanh.

---

## 5. Cổng 2 nhỏ (làm 2/5)

- ✅ EdgeTTS `data += chunk` → `parts.append` + `b"".join` (`service_edgetts.py`).
- ✅ Xoá `batch_state_manager.py` + test + import (thay bằng `audio_transcode`).
- ⏳ Chưa làm: cleanup cache chạy nền (cần lock + đo startup 10k file), xoá
  `execute()`/`_execute_single_task` (còn caller nội bộ — cần refactor riêng),
  đo `fsync`/Piper-persistent/cold-start/SIGSTOP (cần máy thật, xem §6).

---

## 6. Việc phải làm trên máy thật (giữ nguyên từ handoff 2 §8 + test crash)

| Việc | Cách làm | Tiêu chí |
|---|---|---|
| Crash `kill -9` giữa apply (Preview resume) | Batch 200 note → Tạo audio → Áp; kill -9 khoảng note 50–100; mở lại, Tạo audio, Áp tiếp | Không mất/m trùng audio, không 2 `[sound:...]` giống nhau; thông báo "Tiếp tục: bỏ qua N note" hiện ra |
| Ma trận worker × thread (P1-5) | Mỗi engine × worker {1,2,4,8} × thread {1,4,8}, 100–500 item | Bảng mean/P95, peak PSS; ghi `superfreetts_data/benchmark/` |
| `SIGSTOP` runner giữa request | `kill -STOP <pid kokoro_runner>` | Lỗi trong deadline, kill+retry, batch tiếp tục, không rò permit |
| Đo chi phí convert 500 WAV→MP3 | Batch MP3-pref 500 note Kokoro/MMS | Nếu chậm bất thường → chỉ convert khi user thực sự chọn khác format (đã đúng) |
| RAM Kokoro PSS/USS | `smaps_rollup` khi rảnh/load/2 runner; kiểm tra torch vs onnxruntime, load 2 lần? | Chỉ sửa `RAM_PER_PROCESS_MB_ESTIMATE`/`KOKORO_MAX_AUTO_WORKERS` sau khi có số PSS |

---

## 7. Rủi ro / đánh đổi mới

- Convert WAV→MP3 tốn CPU ở máy user chọn MP3 (default WAV không ảnh hưởng).
  `convert_if_requested` fallback giữ WAV khi encoder thiếu/lỗi nên batch không
  bao giờ mất audio vì convert.
- `preferred_output_format()` đọc `aqt.mw.addonManager.getConfig`; trong test
  (mock) trả về wav → không convert → test cũ của service không vỡ.
- Preview checkpoint key đổi khi preset/target/dedup đổi → resume chạy lại từ
  đầu thay vì skip nhầm (an toàn, tốn thêm thời gian cache-hit).
