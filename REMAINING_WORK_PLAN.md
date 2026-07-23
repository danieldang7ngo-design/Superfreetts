# Plan bàn giao — Phần việc còn lại (Phase 7): Viết báo cáo & kiểm định cuối

Repo: `https://github.com/danieldang7ngo-design/Superfreetts` (đã clone sẵn tại thư mục làm việc hiện tại)
Đối tượng đọc: AI Agent **lần đầu** tiếp nhận task này — không có ký ức về các phiên làm việc trước. Mọi thông tin cần thiết đều được liệt kê trong file này; agent không cần và không nên giả định thêm gì ngoài những gì ghi ở đây và những gì tự đọc được từ code.

---

## 0. QUY TẮC BẮT BUỘC — CHỐNG HALLUCINATE

1. **Không sửa file mà chưa `view`/đọc nội dung thật của nó trong phiên hiện tại.** Đừng tin tưởng mù quáng bất kỳ mô tả nào trong file này — nếu code thực tế khác với mô tả, **code thật luôn thắng**, hãy cập nhật lại nhận định của bạn.
2. **Mọi khẳng định "đã sửa X" phải được xác minh lại bằng `git diff`** trên file tương ứng trước khi đưa vào báo cáo, không suy diễn từ file này.
3. **Không tự tái hiện crash macOS thật trên máy Linux.** Không có máy macOS trong môi trường này. Task ở phase này KHÔNG yêu cầu thêm code mới — chỉ xác minh, dọn dẹp, và viết báo cáo trung thực về những gì đã làm và chưa làm được.
4. **Không tự bịa số liệu hiệu năng/RAM/thời gian.** Nếu cần số liệu, phải đo bằng script thật (đã có sẵn các pattern đo trong `tests/test_ram_aware_concurrency.py` và `tests/test_edgetts_background_loop.py`) hoặc trích dẫn rõ nguồn (ví dụ: "theo báo cáo của người dùng, chưa được agent đo lại").
5. Nếu phát hiện điều gì trong file này sai/lỗi thời so với code hiện tại, **phải sửa lại nhận định theo code thật** và ghi chú rõ trong báo cáo cuối rằng file hướng dẫn này có điểm không khớp.

---

## 1. TRẠNG THÁI HIỆN TẠI CỦA REPO (đã xác minh — agent nên tự `git diff`/`git status` lại để xác nhận, không tin suông)

Chạy các lệnh sau để tự xác nhận trạng thái mô tả dưới đây là đúng:

```bash
git status
git diff --stat
python3 -m pytest -q
```

Tại thời điểm bàn giao, kỳ vọng thấy:
- 8 file đã sửa (`modified`): `superfreetts_addon/component_kokoro_manager.py`, `superfreetts_addon/engine_manager.py`, `superfreetts_addon/mms_engine_manager.py`, `superfreetts_addon/services/service_edgetts.py`, `superfreetts_addon/services/service_macos.py`, `superfreetts_addon/system_utils.py`, `superfreetts_addon/tts_orchestrator.py`, `superfreetts_addon/ttsplayer.py`.
- 6 file mới (`untracked`): `INVESTIGATION_NOTES.md`, `tests/test_ram_aware_concurrency.py`, `tests/test_ttsplayer_realtime_timeout.py`, `tests/test_edgetts_background_loop.py`, `tests/test_macos_concurrency_gate.py`, `tests/test_engine_manager_platform_guard.py`.
- `python3 -m pytest -q` (cần chạy `pip install -q --break-system-packages -r requirements-dev.txt` trước nếu môi trường chưa có pytest) → kỳ vọng **226 passed, 1 skipped** (skip đó là `tests/test_mms_active.py`, có sẵn từ trước, không liên quan gì tới các thay đổi này).

**Nếu số liệu thực tế khác với trên (ví dụ số test fail, số file thay đổi khác) — đó là dấu hiệu code đã đổi kể từ lúc file này được viết, hoặc có sai sót ở bước trước. Dừng lại, điều tra chênh lệch, và phản ánh đúng thực tế trong báo cáo, đừng cố ép khớp.**

### Tóm tắt 5 bug đã được sửa (agent PHẢI tự `git diff <file>` để xác nhận lại từng cái trước khi liệt kê vào báo cáo — bảng dưới đây chỉ là điểm xuất phát tham khảo):

| # | Bug (root cause) | File đã sửa | Tóm tắt cách sửa |
|---|---|---|---|
| 2.6 | Concurrency của pool Piper/Kokoro/MMS/Supertonic auto-scale theo số nhân CPU, không xét RAM khả dụng → có thể ăn >5GB RAM | `system_utils.py`, `tts_orchestrator.py` | Thêm `get_available_ram_mb()` + `compute_ram_aware_concurrency()`, cap giá trị mặc định theo RAM, vẫn tôn trọng override thủ công của người dùng |
| 2.2 | `ttsplayer.py::_play()` không kiểm tra `_terminate_flag` của Anki → 1 request treo chặn cả hàng đợi phát âm thanh realtime | `ttsplayer.py` | Bọc lời gọi generate bằng `ThreadPoolExecutor` + timeout 20s (`REALTIME_GENERATE_TIMEOUT_SECONDS`); đây là "approach b" (timeout) chứ không phải cancellation triệt để — xem comment trong code để biết trade-off |
| 2.1 | `service_edgetts.py::run_async_safe()` tạo mới 1 event loop + 1 thread cho MỌI request không cache | `service_edgetts.py` | Dùng 1 event loop nền singleton chạy trong daemon thread, submit qua `asyncio.run_coroutine_threadsafe()`; có fallback an toàn nếu loop nền không khởi động được |
| 2.4 | `service_macos.py::get_tts_audio()` (say + ffmpeg) không giới hạn số subprocess chạy đồng thời | `service_macos.py` | Thêm gate y hệt pattern `_get_request_gate()` đã có sẵn trong `service_edgetts.py`, expose qua `advanced_configuration_options()` |
| 2.3 | Engine local (Kokoro/MMS) hardcode bootstrap Python kiểu Windows (`python.exe`) | `engine_manager.py`, `mms_engine_manager.py`, `component_kokoro_manager.py` | **Đã đính chính so với kế hoạch gốc:** `get_tts_audio()` của Kokoro/MMS hoá ra đã tự fail an toàn từ trước (`errors.RequestError`) — không cần sửa. Chỉ thêm guard `platform.system() != "Windows"` ở các hàm **cài đặt** (`ensure_installed`, `start_installation`) để fail nhanh, không tải file zip vô ích |

**Chưa làm, không thuộc phạm vi đã thống nhất (không tự ý mở rộng):**
- Không hỗ trợ đầy đủ Kokoro/MMS chạy thật trên macOS (cần bootstrap Python riêng cho macOS — là việc kiến trúc lớn, ngoài phạm vi "sửa crash").
- Không implement cancellation triệt để cho 2.2 (chỉ dùng timeout — xem "approach a" vs "approach b" trong comment code `ttsplayer.py`).

---

## 2. VIỆC CẦN LÀM TRONG PHASE NÀY

### Bước 1 — Review lại toàn bộ diff một lượt (bắt buộc trước khi viết báo cáo)

```bash
git diff superfreetts_addon/system_utils.py
git diff superfreetts_addon/tts_orchestrator.py
git diff superfreetts_addon/ttsplayer.py
git diff superfreetts_addon/services/service_edgetts.py
git diff superfreetts_addon/services/service_macos.py
git diff superfreetts_addon/engine_manager.py
git diff superfreetts_addon/mms_engine_manager.py
git diff superfreetts_addon/component_kokoro_manager.py
```

Với mỗi diff, tự hỏi:
- Thay đổi này có khớp với mô tả ở bảng mục 1 không?
- Có comment giải thích rõ ràng "vì sao" ngay tại chỗ sửa không (không chỉ "cái gì")?
- Có thay đổi nào ngoài phạm vi bug đang sửa không (dọn dẹp lan man) — nếu có, ghi chú lại, không tự ý revert trừ khi chắc chắn đó là lỗi.

### Bước 2 — Chạy lại toàn bộ test suite, xác nhận sạch

```bash
pip install -q --break-system-packages -r requirements-dev.txt   # nếu chưa cài
python3 -m pytest -q
```

Nếu có test fail: dừng lại, đọc traceback, xác định fail đó có PHẢI do 1 trong 5 thay đổi ở mục 1 gây ra hay không (dùng `git stash` rồi chạy lại test trên code gốc để so sánh nếu cần chắc chắn). Không được viết báo cáo "hoàn tất" nếu có test fail chưa giải thích được.

### Bước 3 — Kiểm tra không có rác/tác dụng phụ ngoài ý muốn

```bash
git status --porcelain
```

Chỉ nên thấy đúng 8 file `modified` + 6 file mới liệt kê ở mục 1. Nếu thấy thêm bất kỳ file/thư mục lạ nào khác (ví dụ thư mục runtime rỗng do lúc chạy test vô tình tạo ra), kiểm tra xem nó có nằm trong `.gitignore` không (`cat .gitignore`); nếu không nằm trong gitignore và là thư mục rỗng không cần thiết, xoá nó đi (`rmdir`), không xoá nếu không chắc chắn.

### Bước 4 — Viết `FIX_REPORT.md` ở thư mục gốc repo

Nội dung bắt buộc phải có:

1. **Tóm tắt tổng quan** (2-3 câu): đã sửa 5 root cause liên quan tới tràn RAM/crash trên macOS của addon Superfreetts, dựa trên `superfreetts_macos_crash_fix_plan.md`.
2. **Bảng chi tiết từng bug đã sửa** — với MỖI bug, bắt buộc có:
   - File + số dòng cụ thể (lấy từ `git diff`, không copy từ file plan cũ vì số dòng có thể lệch).
   - Trước/sau (đoạn code cũ vs mới, ngắn gọn).
   - Test đã viết để chứng minh (tên file test + lệnh chạy `pytest tests/xxx.py -v`).
   - Mức độ tin cậy: bug này đã **verify được bằng test tự động trên Linux** hay **chỉ có thể verify hành vi tổng thể trên máy macOS thật**.
3. **Phần đính chính quan trọng** (không được bỏ qua): giải thích rõ bug 2.3 hoá ra ít nghiêm trọng hơn giả định ban đầu — vì `get_tts_audio()` của Kokoro/MMS đã tự fail an toàn từ trước; chỉ luồng cài đặt (installer) là cần sửa. Đây là ví dụ cụ thể cho thấy việc luôn xác minh lại bằng code thật (thay vì tin vào giả định ban đầu) đã thay đổi phạm vi công việc — nên nêu rõ để người đọc hiểu quy trình làm việc đã cẩn trọng.
4. **Danh sách việc CHƯA làm / nằm ngoài phạm vi**, và lý do (theo mục 1 phần "Chưa làm").
5. **Phần bắt buộc: kịch bản kiểm định thủ công cần người dùng có máy macOS thật thực hiện lại**, cụ thể từng bước, ví dụ:
   - Cài addon đã sửa vào Anki trên macOS.
   - Bật EdgeTTS làm dịch vụ realtime, ôn tập nhanh (giữ phím Space hoặc dùng auto-advance) khoảng 100+ thẻ liên tục trong điều kiện mạng yếu/chập chờn (ví dụ bật/tắt Wi-Fi giữa chừng).
   - Theo dõi Activity Monitor: RAM và số thread của tiến trình Anki có tăng không kiểm soát không, ứng dụng có bị treo/crash không.
   - Lặp lại tương tự với 1 batch generation lớn dùng nhiều voice Supertonic/Piper cùng lúc, so sánh RAM đỉnh trước/sau khi có bản vá (nếu người dùng có bản build cũ để so sánh).
   - Ghi chú: **không dùng ngôn từ khẳng định tuyệt đối** kiểu "đã fix hoàn toàn crash" — dùng ngôn từ đúng mức độ chắc chắn, ví dụ: "đã sửa các lỗi logic cụ thể đã xác minh qua đọc code + test tự động; cần xác nhận thêm trên macOS thật để đảm bảo không còn nguyên nhân nào khác chưa được phát hiện".
6. **Gợi ý cải tiến tiếp theo (không bắt buộc làm ngay)**: nếu muốn giải quyết root cause 2.2 triệt để hơn (thay vì chỉ dùng timeout), cần implement "approach a" (cancellation xuyên suốt qua toàn bộ chuỗi service) — đây là việc lớn hơn, nên tách thành task riêng nếu người dùng muốn.

### Bước 5 — Bàn giao

Liệt kê rõ trong tin nhắn cuối cùng gửi cho người dùng (không phải trong file `FIX_REPORT.md`):
- Đường dẫn tới `FIX_REPORT.md`.
- 1 câu tóm tắt số bug đã sửa thật (không phải tất cả bug trong plan gốc đều "sửa nguyên văn" — có 1 bug được đính chính phạm vi nhỏ hơn dự kiến).
- Nhắc rằng phần xác nhận cuối cùng ("hết crash trên macOS chưa") vẫn cần người dùng tự test trên máy macOS thật.

---

## 3. THAM CHIẾU NHANH — CÁC FILE LIÊN QUAN

| Việc | File |
|---|---|
| Đọc lại toàn bộ root cause đã xác minh (Phase 1 cũ) | `INVESTIGATION_NOTES.md` |
| Đọc lại plan gốc đầy đủ (bao gồm cả các phase đã hoàn thành) | `superfreetts_macos_crash_fix_plan.md` (nếu không tìm thấy trong repo, đây là file đã được cung cấp riêng cho người dùng ở phiên trước — không bắt buộc phải có để hoàn thành Phase 7, file hiện tại đã đủ thông tin) |
| Test cho từng bug | `tests/test_ram_aware_concurrency.py` (2.6), `tests/test_ttsplayer_realtime_timeout.py` (2.2), `tests/test_edgetts_background_loop.py` (2.1), `tests/test_macos_concurrency_gate.py` (2.4), `tests/test_engine_manager_platform_guard.py` (2.3) |
