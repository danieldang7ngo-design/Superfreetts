# Đánh giá sản phẩm & Kế hoạch cải thiện chi tiết — SuperFreeTTS

> Ngày: 2026-10-23 · Nhánh `fix/resource-management` · HEAD `28c9ad3` · Version `26.10.2`
> Căn cứ: đọc trực tiếp mã nguồn + `git log/status` + chạy `pytest` (408 passed, 1 skipped)
> + đối chiếu toàn bộ tài liệu `AI_Documents/` (kiểm toán 2026-10-22, HANDOFF 1–3,
> triển-khai-cổng-1/2). Báo cáo này **chỉ đánh giá và lập kế hoạch, không sửa code**.

---

## A. Đánh giá sản phẩm hiện tại

### A.1. Sản phẩm này là gì

SuperFreeTTS là add-on Anki (mã `351217314`), fork từ HyperTTS, chỉ giữ engine TTS
**miễn phí**: EdgeTTS, Piper, Kokoro, MMS, Supertonic, GoogleTranslate, Windows SAPI,
macOS TTS, eSpeak-ng + 6 service từ điển. Ba chế độ chính: Easy Mode (1 note),
Collection Mode (batch nhiều note), Realtime Mode (`{{tts ...}}` phát khi review).

### A.2. Điểm mạnh (đã kiểm chứng, không phải suy đoán)

| Lĩnh vực | Đánh giá |
|---|---|
| **Vòng đời process** | Tốt nhất trong các mặt. Benchmark 4 engine: cleanup idle, `stop_all()`, đóng/mở profile, chạy tiếp 5 request đều đạt; **0 process mồ côi**. Tree RSS khi idle giảm về 42–58 MB. |
| **Chất lượng benchmark** | 500/500 item × 4 engine × 2 mode = 4.000 WAV, 0 lỗi, hash âm thanh phân biệt 500/500; nguồn dữ liệu JSON/CSV được đối chiếu lại. |
| **Chất lượng code/CI** | Test suite 408 test (6,4s), coverage gate 70% cho 5 module critical, Ruff + Bandit xanh, build+verify `.ankiaddon` 83,98 MB. Facade God Class đã được tách (Phase 6). |
| **Độ bền batch (đã sửa)** | Checkpoint theo note ID đã gắn vào Batch Preview (A+B), apply idempotent chống trùng `[sound:...]`, deadline IPC + kill/retry, ngân sách thread (Cổng 1). |
| **Định dạng âm thanh (đã sửa)** | Chính sách "native format + convert có điều kiện" qua `audio_transcode.py`; contract `.mp3` chứa WAV đã được sửa; OGG đã nghỉ hưu (decision 1+3). |
| **Tài liệu** | AGENTS/REFERENCE/handoff/kiểm toán rất chặt; quy tắc rõ (CRLF, EdgeTTS cap 3, undo-entry, không machine-translate). |

### A.3. Điểm yếu & rủi ro còn lại (đã đối chiếu với code thật)

| # | Mức | Vấn đề | Trạng thái code hiện tại |
|---|---|---|---|
| 1 | **P0** | **RAM Kokoro không khớp thực tế.** Ước tính `2400 MB`/worker; thực đo 1 runner Kokoro = **3.933 MB**, 2 runner = 4.662 MB. Nay đã chặn `KOKORO_MAX_AUTO_WORKERS = 2` (đã sửa chặn lỗ hổng 6-worker). | Đã chặn ở `tts_orchestrator.py:43`; **nhưng con số 2400 MB vẫn chưa có PSS thật**, cần đo lại. |
| 2 | **P0/P1** | **IPC local engine chưa có timeout đầy đủ.** `acquire()` semaphore và `stdout.readline()` ở MMS/Kokoro/Supertonic vẫn có thể chờ vô hạn nếu runner treo. Batch chỉ có stall detector 180s toàn cục. | Cổng 1 đã thêm deadline IPC + kill/retry cho **request đầu process mới**; nhưng steady-state + `acquire(timeout=...)` chưa chắc phủ hết — **cần xác minh mã hiện tại**. |
| 3 | **P1** | **Cleanup cache chạy đồng bộ trên main thread.** Đã sửa phần xoá nhầm log/usage (giờ filter `is_cache_audio_filename`), nhưng vẫn gọi trong `__init__` (`superfreetts.py:119`), chặn khởi động Anki khi `user_files` có hàng nghìn file. | `superfreetts.py:116-119` vẫn đồng bộ — **còn trong Cổng 2**. |
| 4 | **P1** | **`voicelist.py` 2,5 MB / 46.865 dòng, nạp eager khi Anki khởi động** qua `service.py:9` (`from .services import voicelist`). Làm chậm startup + tiêu RAM. | Chưa sửa — **còn trong Phase 6 roadmap**. |
| 5 | **P1** | **Code chết `Unified/MultiEngineExecutor.execute()` + `_execute_single_task()`** vẫn còn caller nội bộ + ~10 test, chỉ deprecated; `batch_state_manager.py` đã xoá. | Còn ở `batch_executor.py:473,663` — **cần refactor riêng**. |
| 6 | **P2** | Piper spawn binary mỗi request (nạp lại model 63 MB); MMS rò temp WAV khi lỗi; `fsync` từng file cache; cold-start sau 180s idle. | Chưa đo → chưa đổi default (đúng chủ trương). |
| 7 | — | **Nợ kiểm chứng trên máy thật**: tất cả phép đo worker×thread, RAM Kokoro PSS, crash `kill -9`, convert 500 WAV→MP3, SIGSTOP runner. | Bị chặn do môi trường dev không có máy thật. |
| 8 | — | Test coverage cao nhưng **chưa có end-to-end Anki thật** (playback, import media, profile switch giữa batch, macOS/Windows RAM). | Hạn chế ghi rõ ở kiểm toán §7. |

**Nhận định tổng:** Đây là một sản phẩm **trưởng thành và được duy trì rất có kỷ luật**.
Mọi lỗ hổng P0/P1 nghiêm trọng được phát hiện trong kiểm toán 2026-10-22 (RAM Kokoro,
sai định dạng file, checkpoint hỏng, cleanup xoá nhầm) **đã được sửa ở code** trong
Cổng 1 + A+B. Phần còn lại phần lớn là (1) nợ **đo đạc trên máy thật** để chốt con số
an toàn, (2) 3 việc nhỏ thuộc Cổng 2/Phase 6, và (3) nợ kỹ thuật VOICELIST + code chết.

---

## B. Kế hoạch cải thiện chi tiết theo từng khía cạnh

Ưu tiên theo rủi ro. Mỗi mục có: cần làm → cách làm → tiêu chí đạt → đánh đổi.

### Khía cạnh 1 — An toàn RAM & bộ cấp phát concurrency (P0)

Vấn đề gốc: RAM Kokoro ước tính sai (2400 MB so với thực đo 3,9–4,7 GB), thread×worker
chưa ghép đúng (có thể tới 8 worker × 8 thread = 64 thread / 16 CPU). Đã chặn auto ở 2
worker, nhưng con số vẫn chưa có PSS.

- [ ] **1.1 Đo RAM Kokoro bằng PSS/USS** (không dùng tree RSS): `grep VmRSS /proc/<pid>/status`
  + `cat /proc/<pid>/smaps_rollup`, ở 3 trạng thái idle / đang load / 2 runner; xác định
  torch hay onnxruntime, model có load 2 lần không.
- [ ] **1.2 Chỉ sau khi có PSS mới sửa** `RAM_PER_PROCESS_MB_ESTIMATE['KokoroTTS']` và
  (nếu cần) `KOKORO_MAX_AUTO_WORKERS`; pin bằng test `test_ram_aware_concurrency.py` /
  `test_thread_budget.py`.
- [ ] **1.3 Ghép ngân sách song song** `Σ(workers × threads) ≤ get_total_cpu_count()`;
  bảo đảm dùng logical CPU thật, không nhầm `get_cpu_threads()` (policy cap = 8).
- [ ] **1.4 Ghi log** `peak_tree_rss` thật cạnh `estimated_mb`; kiểm tra lại available RAM
  trước khi tăng pool (không chỉ lúc khởi động); cảnh báo rõ khi manual override vượt budget.
- **Tiêu chí đạt:** ma trận Kokoro 1/2/4/6 worker trên máy 16 GB → không OOM, peak ≤ 70%
  RAM khả dụng, estimate sai ≤ 25% so với peak thực.
- **Đánh đổi:** giữ Kokoro 1–2 worker chậm hơn ~10,7% so với 2 worker nhưng tránh OOM —
  đúng cho default; chỉ mở thêm khi đo đủ trên máy ≥ 32 GB.

### Khía cạnh 2 — Độ ổn định IPC & khả năng phục hồi runner (P1)

- [ ] **2.1 Xác minh phạm vi deadline IPC hiện tại** (Cổng 1 mới thêm): deadline chỉ áp
  cho request đầu process mới; rà xem steady-state `stdout.readline()` và
  `DynamicSemaphore.acquire()` đã có timeout chưa. Nếu chưa, thêm `acquire(timeout=...)`
  + deadline theo request (60s single / 120s chunk), watchdog reader + kill/reap + release
  permit + retry 1 lần process mới.
- [ ] **2.2 Test `SIGSTOP` runner giữa request** → request lỗi trong deadline, kill+retry,
  batch tiếp tục, **không rò permit**.
- [ ] **2.3 MMS rò temp WAV:** đưa cleanup vào `finally` / `TemporaryDirectory` cho cả chunk.
- **Tiêu chí đạt:** một runner treo không khóa pool; batch/realtime tự phục hồi, không
  cần restart Anki.
- **Đánh đổi:** kill process mất cache model trong RAM (request sau chậm hơn), nhưng treo
  vô hạn tệ hơn; tách deadline cold-start khỏi steady-state để không giết request hợp lệ.

### Khía cạnh 3 — Khởi động & phản hồi UI (P1, giao thoa Cổng 2 + Phase 6)

- [ ] **3.1 Cleanup cache chạy nền:** chuyển `cleanup_user_files()` ra thread nền sau khi
  mở profile, có lock với lúc ghi cache; đo startup với 10k file trước/sau.
- [ ] **3.2 `voicelist.py` 2,5 MB:** đo thời gian import khi khởi động → chuyển data ra
  ngoài source hoặc lazy-load/compress (không import eager ở `service.py:9`).
- [ ] **3.3 Xoá code chết `execute()` + `_execute_single_task()`:** viết lại 2 caller nội
  bộ (`batch_executor.py:473,663`) + ~10 test sang `_execute_unique_tasks_unified`, mỗi
  bước một commit + test.
- **Tiêu chí đạt:** thời gian khởi động Anki không tăng khi `user_files` lớn; startup
  không import dữ liệu voice nặng; grep `execute(` chỉ còn đường đang chạy.
- **Đánh đổi:** background cleanup cần lock để tránh tranh chấp; giữ file cache cũ lâu hơn
  thì ít rủi ro race — dùng tuổi tối thiểu lớn (≥ 24h).

### Khía cạnh 4 — Hiệu năng batch có đo lường (P2)

- [ ] **4.1 Ma trận worker × thread**: mỗi engine × worker {1,2,4,8} × thread {1,4,8},
  100–500 item → bảng mean/P95/peak PSS vào `superfreetts_data/benchmark/`.
- [ ] **4.2 Piper persistent**: đo 500 item spawn vs persistent; **chỉ** đổi nếu mean giảm
  ≥ 15–20% và không tăng rủi ro treo.
- [ ] **4.3 `fsync`**: đo 500 file SSD/HDD có/không fsync; chỉ bỏ nếu chênh > 5%.
- [ ] **4.4 Cold start sau 180s idle**: đo request đầu từng engine; nếu realtime hay hết
  20s timeout → tăng idle TTL hoặc prewarm có kiểm soát.
- [ ] **4.5 Chi phí convert 500 WAV→MP3**: nếu chậm bất thường → chỉ convert khi user thực
  sự chọn định dạng khác (đã đúng chủ trương hiện tại).
- **Tiêu chí đạt:** có bảng số, chọn default bằng bằng chứng; **không công bố "nhanh hơn
  X%"** khi chưa đo.

### Khía cạnh 5 — Độ tin cậy end-to-end (đang thiếu hoàn toàn)

- [ ] **5.1 Crash `kill -9` giữa apply** (bắt buộc trước khi coi A+B hoàn tất): batch 200
  note, kill ở note 50–100, mở lại → thấy "Tiếp tục: bỏ qua N note", áp tiếp, không mất
  audio, không 2 `[sound:...]` giống nhau.
- [ ] **5.2 End-to-end**: 500 note trên máy 8 GB + 16 GB; batch + realtime; đóng/mở profile;
  verify playback + import media. 0 OOM, 0 process mồ côi, 0 note thiếu audio.
- [ ] **5.3 Đa nền tảng**: macOS (QtWebEngine GPU workaround — Phase 7) và Windows smoke test
  vẫn còn chờ xác minh trên máy thật.

### Khía cạnh 6 — Chất lượng, i18n & tài liệu

- [ ] **6.1 Locale `ko`**: đã sửa đúng chính sách native-format; nếu có người Hàn rà câu chữ
  thì nhờ review, **không machine-translate** (AGENTS.md §6).
- [ ] **6.2 CHANGELOG/release notes 26.10.2**: đã cập nhật en + vi (6 bullets); các locale
  khác giữ fallback tiếng Anh.
- [ ] **6.3 Cập nhật tài liệu khi hoàn tất từng mục** (`handoff` mới + `trien-khai`); giữ
  Roadmap chỉ chứa việc còn mở (đã đúng format hiện tại).

---

## C. Thứ tự thực hiện đề xuất (roadmap hành động)

| Ưu tiên | Việc | Vì sao trước |
|---|---|---|
| **1** | Test tay crash `kill -9` (5.1) | Chốt A+B — tính năng checkpoint/resume vừa ship |
| **2** | Đo RAM Kokoro PSS (1.1→1.2) | Chốt con số an toàn cho P0, tránh OOM |
| **3** | Xác minh + phủ timeout IPC (2.1→2.3) | Đây là lỗ hổng vận hành còn lại, mang rủi ro treo |
| **4** | Cleanup nền + voicelist + xoá code chết (3.1→3.3) | Việc nhỏ làm được ngay, không cần máy thật |
| **5** | Ma trận worker×thread + P2 (4.x) | Chỉ sau khi có máy thật; chốt default bằng dữ liệu |
| **6** | End-to-end + đa nền tảng (5.2→5.3) | Kiểm chứng cuối trước khi release |

**Điều kiện release an toàn** (kế thừa kiểm toán §9, đã bớt do Cổng 1+A+B đã sửa):
(1) RAM Kokoro có số PSS thật + cap đúng; (2) IPC timeout phủ đầy đủ + test SIGSTOP;
(3) cleanup nền + không xoá nhầm; (4) crash-resume Preview test tay đạt.

---

## D. Gates (copy/paste — giữ nguyên từ handoff)

```bash
python -m pytest tests/ -q --tb=short                       # 408 passed, 1 skipped
.venv/bin/python -m pytest tests/ -q --cov=superfreetts_addon --cov-report=json:coverage.json
python scripts/check_critical_coverage.py coverage.json
.venv/bin/python -m ruff check superfreetts_addon tests scripts
.venv/bin/python -m bandit -r superfreetts_addon -ll
python -m pytest tests/test_version_consistency.py -q --tb=short
python build_share.py && python scripts/verify_package.py
```
