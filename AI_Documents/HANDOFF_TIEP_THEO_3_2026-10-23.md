# HANDOFF 3 — sau A+B + định dạng + OGG (2026-10-23)

> Kế thừa `HANDOFF_TIEP_THEO_2_2026-10-23.md` (đã thay thế). Đọc thêm
> `trien-khai-cong-2-2026-10-23.md` để biết đợt này đã làm gì và kiểm chứng ra sao.

- **Nhánh:** `fix/resource-management`
- **HEAD:** xem `git log --oneline -5` (code cuối: transcode + OGG + CHANGELOG + docs)
- **Phiên bản:** `26.10.2` — **giữ nguyên**, chưa push, chưa tag/release
- **Môi trường đã xác minh:** Linux x86_64, Python 3.14.8, 16 logical CPU, ~15,4 GB RAM
- **Trạng thái:** A+B xong (mục 1). Định dạng âm thanh xong phần code+test (mục 2,
  chưa đo chi phí convert). OGG xong (mục 3). CHANGELOG/release notes xong en+vi
  (mục 4). Cổng 2 nhỏ làm 2/5 (mục 5). Còn lại: đo đạc + test tay trên máy thật (mục 6).

---

## 0. Đọc gì trước

1. `AI_Documents/AGENTS.md` — quy tắc repo (CRLF .py, EdgeTTS cap 3, undo entry, …).
2. `AI_Documents/trien-khai-cong-1-2026-10-23.md` — Cổng 1 + cập nhật A+B ở §2.5.
3. `AI_Documents/trien-khai-cong-2-2026-10-23.md` — đợt này: A+B, transcode,
   OGG, CHANGELOG, gates, rủi ro.
4. File này — việc còn lại theo thứ tự ưu tiên.

---

## 1. Đang ở đâu (nói gọn)

- **Đã xong:** B (checkpoint trong Batch Preview + 5 test), A (xoá
  `process_batch_audio` + facade + 3 test cũ), helper `audio_transcode` + bọc 8
  đường Piper/Kokoro/MMS/Supertonic + 7 test, voicelist sạch OGG, CHANGELOG +
  release notes 26.10.2 (en+vi, giữ version), EdgeTTS `b"".join`, xoá
  `batch_state_manager.py`.
- **Test:** 408 passed, 1 skipped. **Ruff OK. Bandit: No issues identified.**
  Coverage gate OK. `test_version_consistency` OK. Gói build+verify OK, 83,98 MB.
- **Code chết còn lại (cố ý giữ):** `Unified/MultiEngineExecutor.execute()` +
  `_execute_single_task()` — còn caller nội bộ (`batch_executor.py:473,663`) và
  ~10 test, mới chỉ deprecated. Xoá thật cần refactor riêng, đừng xoá ẩu.
- **Chưa xong:** đo đạc máy thật (mục 6), test tay crash Preview (mục 6),
  Cổng 2 còn lại (mục 5).

---

## 2. Năm quyết định cũ — đối chiếu

| # | Chủ đề | Trạng thái |
|---|---|---|
| 1 | Định dạng: native, giữ lựa chọn convert, đúng format thì không convert | Xong code+test (§2 trien-khai-2); chưa đo chi phí convert 500 file |
| 2 | RAM Kokoro: không tin 2.400 MB/runner, phải đo lại | Chưa làm — cần máy có Kokoro (mục 6) |
| 3 | OGG: bỏ, chỉ giữ MP3/WAV | Xong (mục 3) |
| 4 | A+B: xoá máy cũ + gắn checkpoint vào máy thật | Xong (mục 1) |
| 5 | Giữ 26.10.2, chỉ thêm nội dung release notes/CHANGELOG | Xong en+vi; ko/ja/zh-CN/zh-TW/sv fallback tiếng Anh, không machine-translate |

---

## 3. Việc ưu tiên 1 — test tay crash Preview (bắt buộc trước khi coi A+B hoàn tất)

Handoff 2 §3.2.5, nhắc lại:

1. Batch 200 note, bấm "Tạo audio" rồi "Áp vào note"; `kill -9` Anki khi đang
   áp (khoảng 50–100 note).
2. Mở lại Anki + batch với cùng lựa chọn → bấm "Tạo audio" → phải thấy
   `"Tiếp tục: bỏ qua N note đã ghi"`, bảng preview hiện N note `Done`.
3. Áp tiếp; kiểm tra: không note nào mất audio, không note nào có 2
   `[sound:...]` giống nhau.
4. Đạt thì đánh dấu A+B hoàn tất; lỗi thì log lại (checkpoint key? chunk nào?
   file `preview-*.checkpoint.json` còn không?).

---

## 4. Việc ưu tiên 2 — đo đạc máy thật (không làm được ở máy dev)

| Việc | Cách làm | Tiêu chí |
|---|---|---|
| RAM Kokoro PSS/USS | `grep VmRSS /proc/<pid>/status`, `cat /proc/<pid>/smaps_rollup` (Pss mới đáng tin); so rảnh / load model / 2 runner; torch hay onnxruntime, load 2 lần? import nặng? | Chỉ sửa `RAM_PER_PROCESS_MB_ESTIMATE['KokoroTTS']` + `KOKORO_MAX_AUTO_WORKERS` sau khi có PSS |
| Ma trận worker × thread | Mỗi engine × worker {1,2,4,8} × thread {1,4,8}, 100–500 item | Bảng mean/P95, peak PSS → `superfreetts_data/benchmark/`; chưa có số thì không đổi default, không công bố "nhanh hơn X%" |
| Chi phí convert 500 WAV→MP3 | Batch MP3-pref 500 note Kokoro/MMS | Nếu chậm bất thường mới tính tiếp (hiện tại đúng chính sách: chỉ convert khi user chọn khác format) |
| `SIGSTOP` runner giữa request | `kill -STOP <pid>` (xem trien-khai-cong-1 §1.4) | Lỗi trong deadline, kill+retry, batch tiếp tục, không rò permit |
| Piper spawn mỗi request | 500 item, so spawn vs persistent | Chỉ đổi nếu mean giảm ≥15–20% và không tăng rủi ro treo |
| `fsync` từng file cache | 500 file, SSD và HDD, có/không `fsync` | Chỉ bỏ nếu chênh >5% |
| Cold start sau 180 s idle | Đo request đầu từng engine | Nếu realtime hay timeout 20 s → tăng idle TTL hoặc prewarm có kiểm soát |

---

## 5. Cổng 2 — còn lại

1. **Cleanup cache chạy nền** (`superfreetts.py`, khoảng dòng 119): đang chạy
   trong `__init__` trên luồng chính → chuyển ra nền sau khi mở profile, có
   lock với lúc ghi cache; đo thời gian khởi động với 10k file.
2. **Xoá `execute()` + `_execute_single_task()`**: chỉ làm khi viết lại 2 caller
   nội bộ (`batch_executor.py:473,663`) và ~10 test trong
   `test_batch_flow.py`/`test_batch_executor_unified.py` sang đường
   `_execute_unique_tasks_unified`; mỗi bước một commit + test.
3. **Locale `ko`**: `ko.json` đã đúng chính sách native-format; nếu có người Hàn
   review thì rà câu chữ, **không machine-translate**.

---

## 6. Quy tắc & cạm bẫy (bổ sung cho AGENTS.md)

- **CRLF:** file `.py` nguồn dùng CRLF; sau khi sửa kiểm tra bằng số byte:
  ```bash
  python - <<'PY'
  import pathlib
  d = pathlib.Path('superfreetts_addon/batch_orchestrator.py').read_bytes()
  print(d.count(b'\r\n'), d.count(b'\n'))   # phải bằng nhau
  PY
  ```
  File test (`tests/`) dùng LF — giữ nguyên, đừng "thống nhất".
- **Không push, không tag/release, không đổi version** nếu chưa được duyệt.
- **EdgeTTS cap 3** — bất biến.
- Mọi `add_custom_undo_entry` phải `merge_undo_entries` trên **mọi** nhánh thoát.
- **Coverage cần `.venv/bin/python`** — python hệ thống thiếu `pytest-cov`.
- **Checkpoint:** chỉ note ID, ghi atomic, at-least-once, apply idempotent.
- **IPC deadline:** request đầu process mới dùng deadline cold-start; stream EOF
  trả `b""` ngay.
- **Ngân sách thread:** chỉ tính pool đang bật; override thủ công không bị hạ.
- **`audio_transcode` là đường convert duy nhất:** service trả byte native,
  convert (nếu cần) qua helper; `write_audio_file_atomic` giữ nguyên vai trò
  lưới an toàn (lưu theo byte thật). `preferred_output_format()` lỗi/thiếu
  config → `"wav"` (không convert) để test mock không vỡ.
- Không commit `meta.json`, `user_files/`, `coverage.json`, `*.ankiaddon`, `dist/`.

---

## 7. Gates (copy/paste)

```bash
# test
python -m pytest tests/ -q --tb=short                       # 408 passed, 1 skipped

# coverage (bắt buộc dùng venv)
.venv/bin/python -m pytest tests/ -q --cov=superfreetts_addon \
  --cov-report=json:coverage.json
python scripts/check_critical_coverage.py coverage.json

# lint + bảo mật
.venv/bin/python -m ruff check superfreetts_addon tests scripts
.venv/bin/python -m bandit -r superfreetts_addon -ll

# version + gói
python -m pytest tests/test_version_consistency.py -q --tb=short
python build_share.py && python scripts/verify_package.py
```

---

## 8. Checklist bàn giao

- [ ] `git status` sạch (sau khi commit đợt này); version vẫn `26.10.2`.
- [ ] Baseline 408 test + gates xanh (ghi số vào trien-khai nếu lệch).
- [ ] Test tay crash Preview (mục 3) — bắt buộc.
- [ ] Đo RAM Kokoro PSS + ma trận worker×thread + chi phí convert (mục 4).
- [ ] Cổng 2 còn lại: cleanup cache nền; refactor `execute()`; locale ko review.
- [ ] Cập nhật handoff + `trien-khai-cong-2-2026-10-23.md` khi xong.
- [ ] Không push/release nếu chưa có approval rõ ràng.
