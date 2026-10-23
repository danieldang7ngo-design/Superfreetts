# Triển khai Cổng 0 — sau báo cáo kiểm toán 2026-10-22

- **Ngày:** 2026-10-23
- **Nhánh:** `fix/resource-management`
- **Cơ sở:** `AI_Documents/bao-cao-kiem-toan-superfreetts-2026-10-22.md`, §5 "Cổng 0"
- **Phạm vi:** chỉ bốn việc chặn release; không đổi version `26.10.2`, không push, không release.

## 1. Commit

| Commit | Nội dung |
|---|---|
| `cfda747` | Chặn Kokoro auto >2 worker + estimate RAM theo số đo |
| `f91fbe4` | Hợp đồng format: phần mở rộng khớp byte thực tế, default WAV, bỏ OGG |
| `917bd91` | Cleanup chỉ xoá cache audio; MMS luôn dọn temp WAV trong `finally` |

## 2. Việc 1 — Kokoro (P0-1)

- `RAM_PER_PROCESS_MB_ESTIMATE['KokoroTTS']`: **500 → 2.400 MB** (mức marginal đo được của runner thứ hai: 4.662 MB cho 2 runner).
- `SupertonicTTS`: **500 → 700 MB** (đo được 687 MB cho 1 runner). Piper 200 và MMS 500 giữ nguyên vì sát số đo (327 MB cho 2 runner Piper, 450 MB MMS).
- Thêm `KOKORO_MAX_AUTO_WORKERS = 2`: trần cứng cho **auto-scale**, áp cả khi không đo được RAM. Override `concurrency_workers` thủ công vẫn được tôn trọng và chỉ cảnh báo như trước.
- Hệ quả trên máy 16 GB: Kokoro auto = **1 worker** (ngân sách 50% vẫn chỉ đủ một runner 2,4 GB); trên máy ≥32 GB auto tối đa 2.
- Log mới: `[RAM-CAP] KokoroTTS automatic concurrency capped to 2 ...`.

## 3. Việc 2 — Hợp đồng format (P1-1)

- Default `audio_format` = **`wav`** (`config_models.Preferences`, `deserialize_preferences`).
- UI chỉ còn **WAV / MP3**; OGG bị ẩn. Mọi preference `ogg` cũ hoặc voice option `format=ogg`/`pcm` được map về WAV kèm cảnh báo, không tạo file `.ogg` không hợp lệ.
- `AudioFileStore`:
  - `detect_audio_format()` nhận `RIFF....WAVE`, `OggS`, `ID3`, frame sync MPEG; trả `None` nếu không nhận ra.
  - Khi ghi, tên file lấy theo **byte thực tế**, không theo format yêu cầu → hết cảnh WAV nằm trong `.mp3`.
  - Cache hit dò các extension đã biết cho cùng hash, và **xoá** entry cũ có nội dung không khớp đuôi (file do bản cũ tạo) để regenerate.
  - Voice option `format` lạ (`flac`, ...) không còn làm `KeyError`.
- Giới hạn đã biết: **EdgeTTS luôn trả MP3** (không có decoder/encoder đóng gói), nên khi chọn WAV thì file của EdgeTTS vẫn là `.mp3` — đúng nội dung, chỉ khác định dạng yêu cầu. Piper single vẫn chuyển WAV→MP3 khi preference là `mp3`.
- Helper text đã cập nhật cho `en` và `vi`. Năm locale còn lại vẫn còn câu cũ nhắc OGG — cần người review dịch, không machine-translate.

## 4. Việc 3 — Cleanup (P1-4)

- `cleanup_user_files()` chỉ xoá file khớp `^superfreetts-[0-9a-f]{56}\.(mp3|wav|ogg)$`.
- `usage_log.json`, `superfreetts.log`, backup config, `batch_state/` và mọi thư mục con được giữ nguyên; log ghi rõ `deleted N old cache files, kept M non-cache files`.
- Cleanup vẫn chạy đồng bộ lúc mở profile (Cổng 1 mới chuyển sang background).

## 5. Việc 4 — MMS temp (P2)

- Toàn bộ vòng tạo/đọc temp WAV nằm trong `try/finally`; temp được xoá cả khi `readline` lỗi, JSON hỏng, pipe gãy hoặc retry lần 2.

## 6. Kiểm chứng

| Kiểm tra | Kết quả |
|---|---|
| `python -m pytest tests/ -q` | **377 passed, 1 skipped** (trước: 340 passed) |
| Coverage gate (`scripts/check_critical_coverage.py`) | **OK**, `audio_file_store.py` 90,3% |
| `ruff check superfreetts_addon tests scripts` | OK |
| `bandit -r superfreetts_addon -ll` | Medium 0 / High 0 (theo mức severity) |
| `python build_share.py` + `scripts/verify_package.py` | OK, 83,97 MB, smoke import pass |

Test mới: `tests/test_audio_format_contract.py`, `tests/test_cleanup_user_files.py`, `tests/test_mms_temp_cleanup.py`; cập nhật `test_audio_file_store.py`, `test_ram_aware_concurrency.py`, `test_system_utils_ram.py`.

## 7. Việc còn lại (Cổng 1–2)

1. Deadline + kill/restart runner cho MMS/Kokoro/Supertonic; `acquire(timeout=...)` cho semaphore (P1-2).
2. Checkpoint theo chunk/note ID, bỏ hai hàm `execute()` chết (P1-3).
3. Ma trận worker × thread, chốt default theo profile RAM/CPU (P1-5); hiện chưa ghép ngân sách thread.
4. Piper persistent, đo `fsync` và EdgeTTS `bytearray` (P2).
5. Đo lại Kokoro 1/2/4 worker trên máy thật để xác nhận estimate 2.400 MB; đo cold start sau 180 giây idle.

## 8. Ghi chú

- Không đổi `manifest.json` / `version.py`; chưa cập nhật `CHANGELOG.md` vì chưa chốt số version kế tiếp.
- `SuperFreeTTS.ankiaddon` được build lại cục bộ để verify, không commit (gitignored).
- Không push, không tạo tag/release.
