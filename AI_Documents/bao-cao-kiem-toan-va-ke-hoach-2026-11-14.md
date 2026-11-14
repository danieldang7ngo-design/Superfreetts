# Báo cáo kiểm toán & kế hoạch cải thiện — SuperFreeTTS 26.10.3

**Nhánh:** `fix/resource-management` · **Commit cuối (HEAD):** `6271884` (28-10-2026, "fix(edgetts): restore synthesis via the api.msedgeservices.com endpoint")
**Thẻ phát hành hiện có:** `26.10.3` → trỏ vào commit `55089d3` (24-10-2026)
**Ngày kiểm toán:** 14-11-2026 · **Máy:** Linux 7.3.3, Python 3.14.9, 16 nhân CPU (Central Processing Unit – bộ xử lý trung tâm), ~9,7 GB (Gigabyte – gigabyte) RAM (Random Access Memory – bộ nhớ truy cập ngẫu nhiên) khả dụng

---

## 0. Thẻ tóm tắt

| Hạng mục | Kết quả |
|---|---|
| 5 cổng bắt buộc (pytest, ruff, bandit, quốc tế hoá (i18n – internationalization), verify_package) | **Đều ĐẠT** — không có lỗi chặn |
| Số phát hiện | 4 mức ưu tiên 0 / ưu tiên 1 (P0/P1 – Priority 0/1, ưu tiên cao), 8 mức ưu tiên 2 (P2 – Priority 2, nợ kỹ thuật lớn), 7 mức ưu tiên 3 (P3 – Priority 3, vệ sinh) |
| Phát hiện nghiêm trọng nhất | **Gói cài trên đĩa và thẻ `26.10.3` không chứa bản sửa dịch vụ chuyển văn bản thành giọng nói của trình duyệt Microsoft Edge (EdgeTTS – Microsoft Edge Text-to-Speech) ngày 28-10** → người dùng cài "26.10.3" vẫn bị lỗi giao thức truyền tải siêu văn bản (HTTP – Hypertext Transfer Protocol) 403 khi tạo giọng |
| Phủ kiểm thử (đo lại) | **50,33 %** dòng · **50,0 %** nhánh (19.321 câu lệnh, 4.348 nhánh) — đo lại 14-11-2026 sau khi bổ sung test (bản kiểm toán gốc: 39,0 % dòng, chưa đo nhánh) |
| Nợ kỹ thuật đo được | 43 chỗ `except: pass`, 277 chỗ `except Exception`, 48 hàm ≥ 90 dòng, ~2.000 dòng bảng kiểu xếp tầng (CSS – Cascading Style Sheets) trùng lặp, 232 khoá dịch thừa, 4 ngôn ngữ dịch dở |
| Đề xuất | 5 đợt việc, ưu tiên đợt 0 (phát hành) trước khi làm bất cứ refactor nào |

---

## 1. Phạm vi, môi trường, phương pháp

**Phạm vi:** toàn bộ `superfreetts_addon/` (110 file Python, 34.908 dòng), `tests/` (82 file, 10.619 dòng), `scripts/`, `build_share.py`, `external/` (thư viện đi kèm), gói `SuperFreeTTS.ankiaddon`, cấu hình tích hợp liên tục (CI – Continuous Integration, chạy tự động trên GitHub), tài liệu `AI_Documents/`, và trạng thái git.

**Phương pháp:** chạy thật 5 cổng; đo lại độ phủ kiểm thử bằng `coverage` (ghi ra thư mục tạm, không ghi vào repo); phân tích cây cú pháp trừu tượng (AST – Abstract Syntax Tree, cách máy đọc cấu trúc mã) để đếm hàm dài, chỗ nuốt lỗi, chỗ thiếu khẳng định trong test; so từng byte các file `.py` trong gói cài với cây nguồn; đối chiếu thẻ git với HEAD; đọc trực tiếp các đoạn mã ở những chỗ rủi ro cao.

**Nguyên tắc:** không sửa một dòng mã nào, không commit, không bump phiên bản. Sau khi kiểm toán, `git status` vẫn chỉ có đúng 2 mục có sẵn từ trước: `.hermes.md` (đã sửa, 23 dòng thêm/13 dòng bớt) và `AI_Documents/bao-cao-hieu-nang-2026-10-24.md` (chưa theo dõi).

---

## 2. Cổng kiểm tra — kết quả thật

| # | Cổng | Lệnh | Kết quả thật | Kết luận |
|---|---|---|---|---|
| 1 | Kiểm thử đơn vị | `.venv/bin/python -m pytest tests/ -q --tb=short` | `493 passed, 1 skipped in 6.92s` (lần 2: 6,73 s; lần có đo phủ: 9,64 s) | ĐẠT |
| 2 | Soi mã tĩnh | `.venv/bin/ruff check superfreetts_addon build_share.py scripts tests` | `All checks passed!` (ruff 0.17.1) | ĐẠT |
| 3 | Quét bảo mật | `.venv/bin/bandit -ll -r superfreetts_addon` | 109 Low · **0 Medium · 0 High** (bandit 1.9.4) | ĐẠT |
| 4 | Dịch thuật (quốc tế hoá (i18n – internationalization)) | `.venv/bin/python scripts/i18n_audit.py --check` | `used but missing in en: 0`; tiếng Anh / tiếng Việt (en/vi – English/Vietnamese) 652 khoá (100 %) | ĐẠT |
| 5 | Gói cài | `.venv/bin/python scripts/verify_package.py SuperFreeTTS.ankiaddon` | `[verify] OK: SuperFreeTTS.ankiaddon (2.18 MB)`; smoke: `edge_cap: 3, requests 2.32.4, edge_tts 7.3.1` | ĐẠT |
| 6 | Sàn phủ kiểm thử | `scripts/check_critical_coverage.py` | 5/5 module trọng yếu ≥ 70 %: config_models 70,2 %, batch_executor 83,7 %, component_text_processing 96,7 %, audio_file_store 91,7 %, voice_cache 91,8 % | ĐẠT |
| 7 | Siêu dữ liệu thư viện đi kèm | `scripts/vendor_deps.py --check` | 5/5 khớp (`requests`, `certifi`, `idna`, `charset-normalizer`, `urllib3`) | ĐẠT |
| 8 | Quy ước xuống dòng đầu dòng và xuống dòng kiểu Windows (CRLF – Carriage Return Line Feed) | `tests/test_line_endings.py` | 34.908 dòng đầu dòng và xuống dòng (CRLF – Carriage Return Line Feed), **0 dòng chỉ xuống dòng (LF – Line Feed)**; `tests/` 0 dòng CRLF | ĐẠT |

**Bài học từ chính các cổng này:** cả 5 cổng đều xanh, nhưng gói cài vẫn sai (xem P0-1). Nghĩa là bộ cổng hiện tại **không kiểm tra được gói có khớp mã nguồn hay không** — đây là lỗ hổng của quy trình, không phải lỗi của từng cổng.

---

## 3. Bản đồ sức khoẻ mã nguồn (số liệu đo được)

| Chỉ số | Giá trị | Ghi chú |
|---|---|---|
| File Python trong add-on / số dòng | 110 / 34.908 | Trung bình 317 dòng/file |
| File kiểm thử / số dòng | 82 / 10.619 | 493 hàm test, tỉ lệ 1 test / 71 dòng mã |
| Phủ kiểm thử tổng | **50,33 %** dòng · **50,0 %** nhánh (19.321 câu lệnh, 4.348 nhánh) | Đo lại 14-11-2026 có `--cov-branch`; số 39,0 % là bản đo cũ chỉ tính dòng |
| Tầng giao diện (`component_*`, `gui.py`, `gui_utils.py`, `batch_progress_ui.py`) | 14.662 dòng = **42 % mã**, phủ **16,2 %** | Lý do chính kéo phủ tổng xuống |
| `anki_utils.py` (ranh giới gọi Anki) | 312 câu lệnh, phủ **94,72 %** dòng · 79,2 % nhánh | Đo lại 14-11-2026; trước đây 0,0 % vì `tests/conftest.py` giả lập toàn bộ `aqt` |
| `except Exception` toàn repo | **277** chỗ | 72 chỗ nằm trong `component_*.py` |
| Nuốt lỗi im lặng | **43** chỗ `except …: pass` (bandit B110) + 17 chỗ `continue`/`return None` = **60** | Tăng từ 43 (báo cáo 24-10) do tính thêm kiểu khác |
| Hàm ≥ 90 dòng | **48** hàm | 7 hàm stylesheet 284–351 dòng |
| File import thẳng `aqt`/`anki` | **49** file, 159 chỗ dùng `mw.` | Vi phạm quy ước "mọi lời gọi Anki qua `anki_utils.py`" |
| Import kiểu `import *` | 7 chỗ | `F403` không nằm trong danh sách luật ruff |
| Khoá dịch định nghĩa nhưng không dùng | **232** / 652 | |
| Ngôn ngữ phủ thấp | tiếng Nhật (ja – Japanese) 13,7 % · tiếng Trung giản thể (zh-CN – Simplified Chinese) 13,7 % · tiếng Trung phồn thể (zh-TW – Traditional Chinese) 13,7 % · tiếng Thụy Điển (sv – Swedish) 29,0 % · tiếng Hàn (ko – Korean) 67,0 % | tiếng Anh / tiếng Việt (en/vi – English/Vietnamese) 100 % |
| Mục trong gói cài | 632 · 2.281.489 byte · 7 file `.py` **lệch** cây nguồn | Xem P0-1 |

**Đo lại độ phủ có nhánh (14-11-2026, sau khi sửa M2/M3):**

```bash
COVERAGE_FILE=/tmp/sftts-cov/.coverage .venv/bin/python -m pytest tests/ -q \
    --cov=superfreetts_addon --cov-branch --cov-report=json:/tmp/sftts-cov/coverage.json
```

| Phạm vi | Câu lệnh | Nhánh | Phủ dòng | Phủ nhánh | Ghi chú |
|---|---:|---:|---:|---:|---|
| Toàn gói `superfreetts_addon` | 19.321 | 4.348 | **50,33 %** | **50,0 %** | Bản kiểm toán gốc ghi 39,0 % (chỉ đo dòng) |
| `component_services.py` | 799 | 214 | **70,09 %** | 55,1 % | Trước: 6,0 % |
| `component_voiceselection.py` | 646 | 182 | **86,96 %** | 75,3 % | Có test cho cả nhánh sửa preset hỏng và nhánh giữ nguyên giọng Piper |
| `anki_utils.py` | 312 | 48 | **94,72 %** | 79,2 % | Trước: 0,0 % |

---

## 4. Phát hiện theo mức ưu tiên

> Cách đọc mức ưu tiên: **ưu tiên 0 (P0 – Priority 0)** = phải sửa trước khi phát hành; **ưu tiên 1 (P1 – Priority 1)** = rủi ro cao với người dùng, sửa trong 1–2 tuần; **ưu tiên 2 (P2 – Priority 2)** = nợ kỹ thuật lớn, cần kế hoạch; **ưu tiên 3 (P3 – Priority 3)** = vệ sinh, gộp vào việc khác.

### P0-1. Gói cài và thẻ phát hành lệch HEAD — bản sửa EdgeTTS ngày 28-10 không có trong gói

**Bằng chứng:**
- `git rev-parse 26.10.3^{commit}` → `55089d3` (24-10). `git log -1` → HEAD `6271884` (28-10).
- `git diff --stat 26.10.3..HEAD` → 9 file, 685 dòng thêm: 4 file `external/edge_tts/*`, `services/service_edgetts.py` (+32/−…), `superfreetts_addon/superfreetts.py`, `superfreetts_addon/batch_orchestrator.py`, và `tests/test_edgetts_endpoint.py` (+321 dòng test mới).
- So từng byte gói `SuperFreeTTS.ankiaddon` (ngày 24-10, 2.281.489 byte) với cây nguồn: **7 file `.py` khác nhau**, gồm `external/edge_tts/constants.py`, `communicate.py`, `drm.py`, `voices.py`, `services/service_edgetts.py`, `batch_orchestrator.py`, `superfreetts.py`.
- Kiểm chuỗi đặc trưng: `external/edge_tts/constants.py` **trong cây nguồn** có `api.msedgeservices` (1 lần); **trong gói cài** có 0 lần.

**Ảnh hưởng:** Microsoft đã chuyển điểm cuối tổng hợp giọng khỏi `wss://speech.platform.bing.com/.../edge/v1`. Bản trong gói vẫn dùng điểm cuối cũ → mọi lần tạo giọng dịch vụ chuyển văn bản thành giọng nói của Microsoft Edge (EdgeTTS – Microsoft Edge Text-to-Speech) trả **giao thức truyền tải siêu văn bản (HTTP – Hypertext Transfer Protocol) 403**, trong khi danh sách giọng vẫn tải được (đúng triệu chứng issue #5). Người dùng tải gói "26.10.3" sẽ gặp lỗi này; bản sửa chỉ tồn tại trên nhánh, chưa vào thẻ, chưa vào gói.

**Vì sao cổng không bắt được:** `scripts/verify_package.py:192-207` chỉ so `manifest.json` với `version.py` (**số phiên bản**), không so nội dung từng file với cây nguồn. Báo cáo 24-10 từng xác nhận "mọi `.py` trong gói giống hệt cây làm việc" — nhưng đó là kiểm tay tại commit `55089d3`, không phải cổng tự động.

**Hướng sửa:** dựng lại gói từ HEAD (`python build_share.py`) rồi phát hành `26.10.4`; thêm bước đối chiếu thuật toán băm an toàn 256-bit (SHA-256 – Secure Hash Algorithm 256-bit, hàm băm một chiều) từng file trong gói với cây nguồn vào `verify_package.py`.

---

### P1-1. `stop_all()` giết tiến trình **trong khi đang giữ khoá** của pool → treo giao diện khi đóng profile

**Bằng chứng:** `services/process_pool.py:455-479`

```
462  with self._lock:
463      processes = list(self._active)
...
471      for proc in processes:
472          self.safe_terminate(proc)      # <-- nằm trong khoá
```

`safe_terminate` → `terminate_process` (`process_pool.py:145-204`): gửi tín hiệu kết thúc (SIGTERM – Signal Terminate) cho cả nhóm tiến trình, `proc.wait(timeout=2.0)`, nếu chưa chết thì gửi tín hiệu buộc dừng (SIGKILL – Signal Kill), `wait(timeout=1.0)` → **tối đa ~3 giây cho mỗi tiến trình**. Với 4 engine (Piper, Kokoro, mô hình đa ngôn ngữ (MMS – Massively Multilingual Speech), Supertonic) là **~12 giây**.

Chuỗi gọi: `gui.py:406-416` đăng ký hook `profile_will_close` → `hypertts.shutdown()` (`superfreetts.py:689-731`) → `pool.stop_all()` cho 4 pool (`superfreetts.py:717-722`). Hook này chạy trên **luồng chính của Qt** (thư viện giao diện) → Anki đứng hình đến khi xong.

Cùng lỗi ở nhánh khác: `process_pool.py:408` — khi gặp tiến trình nhàn rỗi có cờ debug khác, gọi `self.safe_terminate(proc)` **bên trong `with self._lock`**.

**Ảnh hưởng:** người dùng thấy Anki "treo" khi đóng hồ sơ hoặc đổi hồ sơ; nếu một tiến trình con (ví dụ `piper`) không phản hồi tín hiệu kết thúc (SIGTERM – Signal Terminate), thời gian chờ nhân lên theo số tiến trình.

**Hướng sửa:** gom danh sách tiến trình trong khoá, **nhả khoá rồi mới** kết thúc; hoặc đẩy việc kết thúc sang luồng riêng có hàng đợi và đặt trần thời gian tổng (ví dụ 3 giây cho cả lô), phần còn lại để tín hiệu buộc dừng (SIGKILL – Signal Kill) bất đồng bộ.

---

### P1-2. Không có cơ chế chống tiến trình mồ côi khi Anki thoát đột ngột hoặc "tải lại add-on"

**Bằng chứng:**
- Không có `atexit` ở bất kỳ đâu trong `superfreetts_addon/` (đã tìm toàn repo: 0 kết quả).
- Các tiến trình chạy engine (`services/piper_runner.py`, `kokoro_runner.py`, `sherpa_runner_v2.py`, `supertonic_runner.py`) **không có vòng kiểm tra tiến trình cha** (`os.getppid()`, `parent_pid`, `watchdog` — 0 kết quả trong `services/`).
- `shutdown()` chỉ dừng **4 pool được liệt kê cứng** qua biến toàn cục mức module (`superfreetts.py:717-722`: `service_piper._piper_pool`, `service_kokoro._kokoro_pool`, `service_mms._sherpa_pool`, `service_supertonic._supertonic_pool`). Thêm engine mới mà quên thêm vào danh sách này thì tiến trình sẽ sống mãi.
- `subprocess.Popen` dùng `start_new_session=True` trên Linux/macOS (`process_pool.py:550`) → tiến trình con **thoát khỏi nhóm tiến trình của Anki**, nên khi Anki bị kill, hệ điều hành không tự dọn.

**Ảnh hưởng:** Kokoro giữ ~3,9 GB (Gigabyte – gigabyte) bộ nhớ truy cập ngẫu nhiên (RAM – Random Access Memory) đỉnh (số đo trong `AI_Documents/bao-cao-hieu-nang-2026-10-24.md:73`). Sau một lần Anki bị buộc thoát hoặc bấm "Reload add-ons" giữa lúc đang chạy Kokoro, tiến trình đó **vẫn sống**, giữ model trong bộ nhớ truy cập ngẫu nhiên (RAM – Random Access Memory), và bản add-on mới không có tay cầm nào để dừng nó. Người dùng chỉ phát hiện qua trình quản lý tác vụ (Task Manager).

**Hướng sửa:** (a) trong mỗi runner, thêm vòng kiểm tra `os.getppid()` mỗi 5–10 giây, cha chết thì tự thoát; (b) đăng ký `atexit` + xử lý tín hiệu ở phía add-on; (c) thay danh sách cứng bằng một sổ đăng ký pool (`register_pool()` / `stop_all_registered()`).

---

### P1-3. `init_services()` đánh dấu "đã khám phá xong" **sau khi** một module dịch vụ import lỗi

**Bằng chứng:** `servicemanager.py:129-143`

```
129  if self._services_discovered: return
134  try:
135      self.import_services()      # lỗi từng module chỉ bị log (dòng 154-156)
136      self._cache_service_classes()
137      self._services_discovered = True
139  except Exception as e:
140      logger.error(...)
142      self._services_discovered = True   # <-- đánh dấu xong dù đã lỗi
143      raise
```

**Ảnh hưởng:** một lỗi tạm thời khi import (ví dụ file bị khoá bởi trình quét virus trên Windows, hoặc `onnxruntime` nạp chậm) làm mất **vĩnh viễn** dịch vụ đó trong suốt phiên Anki: không có lần thử lại, người dùng chỉ thấy dịch vụ biến mất khỏi danh sách. Lỗi chỉ nằm trong log.

Thêm một điểm liên quan: `_cache_service_classes` (`servicemanager.py:158-188`) **khởi tạo thử mọi lớp dịch vụ** (`subclass()`) chỉ để đọc `.name` và `.service_fee`. Nghĩa là mọi hàm dựng đều chạy trên luồng giao diện lúc khởi động — nếu một dịch vụ mới có hàm dựng nặng, thời gian mở Anki tăng mà không ai thấy trong test (vì test giả lập `aqt`).

**Hướng sửa:** chỉ đặt `_services_discovered = True` khi `import_services()` không ném lỗi; giữ danh sách module lỗi để thử lại; chuyển `name`/`service_fee` thành thuộc tính lớp (class attribute) để không phải khởi tạo đối tượng.

---

### P1-4. Tầng giao diện 14.662 dòng gần như không có kiểm thử; ranh giới Anki phủ 0 %

**Bằng chứng (đo lại, không dùng số cũ):**

| Nhóm | Câu lệnh | Thiếu | Phủ |
|---|---:|---:|---:|
| Tầng giao diện | 8.854 | 7.420 | **16,2 %** |
| `services/*` + runner/giao tiếp liên tiến trình (IPC – Inter-Process Communication) | 2.975 | 1.796 | 39,5–39,8 % |
| Lõi batch | 1.523 | 469 | 69,2 % |
| Cấu hình | 935 | 336 | 64,1 % |

Các file phủ thấp nhất: `anki_utils.py` **0,0 %** (312 câu lệnh), `component_onnx_manager.py` 0,0 %, `component_piper_manager.py` 0,0 %, `utils_hf.py` 0,0 %, `component_services.py` 6,0 %, `component_mms_manager.py` 6,2 %, `gui_utils.py` 7,0 %.

**Ảnh hưởng:** 42 % mã nguồn (toàn bộ hộp thoại, nút, luồng cài engine) chỉ được kiểm bằng tay. Đây là nơi phát sinh phần lớn lỗi người dùng báo. Toàn bộ 493 test chạy trong 6,9 giây — dấu hiệu rõ ràng rằng không có test tích hợp nào chạm vào giao diện thật.

**Điểm cần nói cho công bằng:** đây là lựa chọn kiến trúc có chủ đích (`tests/conftest.py` giả lập `aqt` toàn cục để bộ test không cần Anki). Nhưng hệ quả là **quy ước "mọi lời gọi Anki qua `anki_utils.py`" chỉ còn là quy ước trên giấy**: có 49 file import thẳng `aqt`/`anki`, 159 chỗ dùng `mw.`, 7 chỗ `from aqt.qt import *`. Bộ test không nhìn thấy các chỗ đó vì đã bị giả lập.

---

### P2-1. 277 chỗ `except Exception` và 43 chỗ `except: pass` — lỗi bị nuốt, khó chẩn đoán

**Bằng chứng:** bandit B110 = **43** (khớp chính xác báo cáo 24-10), phân bố: `services/process_pool.py` **15**, `service_logger.py` 4, `component_supertonic_setup.py` 3, còn lại rải ở `component_batch_preview.py`, `component_kokoro_manager.py`, `component_mms_manager.py`, `component_services.py`, `services/piper_runner.py`, `services/runner_base.py`, `services/service_supertonic.py`, `tts_orchestrator.py` (mỗi file 2), `component_piper_manager.py` 1. Ngoài ra 17 chỗ kiểu `except …: continue` / `return None` (ví dụ `system_utils.py:55,277`, `superfreetts.py:426`).

**Ví dụ cụ thể cho thấy cái giá của việc nuốt lỗi:** `process_pool.py:178`

```
176  else:
177      group_signalled = _signal_process_group(proc, signal.SIGTERM)
178  if not group_signalled and os.name != 'nt':
```

Nếu `proc.poll() is not None` (tiến trình đã chết sẵn) thì **không nhánh nào gán** `group_signalled` → dòng 178 ném `UnboundLocalError`, và nó bị `except Exception: pass` ở dòng 190 nuốt mất. Lỗi thật bị che, người đọc mã tưởng luồng chạy bình thường.

**Ảnh hưởng:** khi người dùng báo "batch dừng mà không rõ lý do", log không có manh mối vì đúng chỗ hỏng lại `pass`.

---

### P2-2. Trùng lặp cấu trúc: ~2.000 dòng bảng kiểu xếp tầng (CSS – Cascading Style Sheets) trong `gui_utils.py`

**Bằng chứng:** 7 hàm dựng stylesheet (bảng kiểu Qt (QSS – Qt Style Sheets), chuỗi tạo kiểu dáng cho Qt):

| Hàm | Dòng | Độ dài |
|---|---:|---:|
| `_build_vibrant_stylesheet` | 477 | 351 |
| `_build_apple_stylesheet` | 1434 | 303 |
| `_build_ollama_stylesheet` | 830 | 300 |
| `_build_nintendo_stylesheet` | 1132 | 300 |
| `_build_claude_stylesheet` | 2312 | 290 |
| `_build_clay_stylesheet` | 2023 | 287 |
| `_build_binance_stylesheet` | 1739 | 282 |

Đo độ giống nhau sau khi bỏ màu và số: **0,95–0,99** giữa 6 hàm (ollama/nintendo/apple; binance/clay/claude). Nghĩa là chúng gần như **cùng một bảng kiểu xếp tầng (CSS – Cascading Style Sheets), chỉ khác bảng màu**.

**Ảnh hưởng:** mỗi lần sửa một chi tiết giao diện phải sửa 7 chỗ; rất dễ lệch nhau; không có test nào bảo vệ. Đây là nợ kỹ thuật lớn nhất về khối lượng trong repo.

---

### P2-3. Cổng quốc tế hoá (i18n – internationalization) quá yếu: 4 ngôn ngữ dịch dở vẫn được coi là ĐẠT

**Bằng chứng:** `scripts/i18n_audit.py:59,75-77` chỉ trả mã lỗi 1 khi **tiếng Anh** thiếu khoá đang dùng:

```
59  missing_english = sorted(used - set(english))
75  if args.check and missing_english:
77      return 1
```

Số đo hiện tại: tiếng Nhật (`ja` – Japanese) 89/652 (**13,7 %**), tiếng Trung giản thể (`zh-CN` – Simplified Chinese) 89 (13,7 %), tiếng Trung phồn thể (`zh-TW` – Traditional Chinese) 89 (13,7 %), tiếng Thụy Điển (`sv` – Swedish) 189 (29,0 %), tiếng Hàn (`ko` – Korean) 437 (67,0 %). Đồng thời **232 khoá** trong `en.json` không được mã nguồn dùng tới.

**Ảnh hưởng:** người dùng Nhật/Trung chọn ngôn ngữ của mình nhưng thấy gần như toàn bộ giao diện bằng tiếng Anh — tệ hơn là không có tuỳ chọn đó. Cổng vẫn xanh nên không ai biết.

---

### P2-4. Mã chết và hai kiến trúc song song trong cùng một file

| Vị trí | Dòng | Tình trạng |
|---|---:|---|
| `component_onnx_manager.py` | 270 | **Không file nào import** (0 kết quả tìm toàn repo), phủ 0 %, vẫn được đóng vào gói |
| `batch_executor.py` lớp `UnifiedBatchExecutor` | 537-594 | **Không nơi nào khởi tạo**; chỉ `MultiEngineExecutor` (dòng 596) được dùng qua `get_multi_engine_executor` (dòng 728) |
| `batch_executor.py` `UnifiedCache` | 119-189 | Được khởi tạo với ngân sách 100 megabyte (MB – Megabyte) (`batch_executor.py:654`) nhưng **không nơi nào đọc/ghi**; chính mã cũng ghi chú "legacy UnifiedCache was write-only in the live path" (`batch_orchestrator.py:266`) |
| `resource_manager.ResourceMonitor` (lớp) | 150-241 | Chỉ test dùng; đường chạy thật dùng `SimpleResourceMonitor` (`batch_executor.py:653`) và hàm `resource_manager._get_process_ram_usage_without_psutil` |
| `system_utils.get_total_ram_mb` | 481 | 0 lời gọi |
| `services/test_runner.py` | 6 | In một dòng định dạng đối tượng JavaScript (JSON – JavaScript Object Notation), không được `discover_services()` nhận (chỉ nhận `service_*.py`), vẫn vào gói |
| `set_edge_workers_20.py` | — | Được nhắc trong `batch_constants.py:49` và `build_share.py:71` nhưng **file không tồn tại** |

**Ảnh hưởng:** người đọc mã không biết kiến trúc nào là thật; mọi thay đổi có nguy cơ sửa nhầm nhánh chết. Riêng `resource_manager.ResourceMonitor` còn chứa hai lỗi tiềm ẩn (chia cho `max_ram_mb` không kiểm tra 0 tại `resource_manager.py:232`; sàn 2 worker khi bộ nhớ truy cập ngẫu nhiên (RAM – Random Access Memory) > 70 % tại dòng 236) — hiện **không ảnh hưởng người dùng** vì lớp này không được dùng, nhưng nếu ai đó "hồi sinh" nó thì lỗi thành thật.

---

### P2-5. Vòng gửi việc batch: 100 dòng lồng ngoặc, và **hai chủ sở hữu** cùng một `executor`

**Bằng chứng:** `batch_orchestrator.py:491-568`. Trong đó dòng 527-533 ghi đè thuộc tính của đối tượng điều phối từ một **luồng công nhân**:

```
527  current_executor = getattr(self.hypertts.orchestrator, 'executor', None)
529  rebuilt = batch_executor.get_multi_engine_executor(...)
532  self.hypertts.orchestrator.executor = rebuilt
533  self.hypertts.executor = rebuilt
```

Điều này chỉ tồn tại để vá lỗi "cannot schedule new futures after shutdown". Cơ chế hoãn của `apply_deferred_engine_pools` (`tts_orchestrator.py:374-421`) kiểm tra `busy == 0` rồi mới đổi executor — nhưng giữa lúc kiểm tra và lúc đổi, một luồng khác vẫn có thể gửi việc vào executor cũ. Đây là cuộc đua (race condition) được che bằng cách thử lại, không phải được loại bỏ.

Thêm dấu hiệu giao diện lập trình ứng dụng (API – Application Programming Interface) còn biến động: `apply_deferred_engine_pools` có **4 tên alias** (`tts_orchestrator.py:417-420`).

**Ảnh hưởng:** khó sửa, khó test; mọi thay đổi về số luồng đều có nguy cơ gây "mất việc" hoặc ném `RuntimeError` giữa batch.

---

### P2-6. Bất biến "EdgeTTS tối đa 3 luồng" không thực sự được test bảo vệ

**Bằng chứng:** hằng số bị ghi đè được nếu có module `_local_override` (`batch_constants.py:45-46`):

```
44  EDGETTS_MAX_WORKERS: Final[int] = 3
45  if _local_override is not None:
46      EDGETTS_MAX_WORKERS = int(getattr(_local_override, "EDGETTS_MAX_WORKERS", EDGETTS_MAX_WORKERS))
```

Sáu test liên quan đều so với **chính hằng số đó**, không so với số 3: `tests/test_batch_flow.py:149`, `tests/test_config_defaults.py:15`, `tests/test_ram_aware_concurrency.py:116`, `tests/test_supertonic_service.py:177`, `tests/test_thread_budget.py:144`. Nghĩa là nếu ai đó đặt `_local_override.EDGETTS_MAX_WORKERS = 20`, **cả 6 test vẫn xanh**.

Kèm theo: `Final[int]` bị gán lại ở dòng 46 — khai báo sai kiểu (không có cổng kiểm kiểu tĩnh nên không bị phát hiện). `build_share.py:69` loại `_local_override.py` khỏi gói, nhưng mã vẫn `import` nó lúc chạy → người dùng tự thả file vào thư mục add-on là nâng được giới hạn.

**Ảnh hưởng:** tài liệu dự án (`.hermes.md`) khẳng định "EdgeTTS worker cap = 3, immutable, test-enforced". Thực tế: **có thể thay đổi được**, và test không bắt được. Với dịch vụ miễn phí của Microsoft, vượt 3 luồng dẫn tới bị chặn tốc độ (đúng như báo cáo hiệu năng đã ghi: 6 câu tuần tự bị bóp còn 2,64 s/câu).

---

### P2-7. Không có cổng kiểu tĩnh (type check)

**Bằng chứng:** `pyproject.toml` chỉ cấu hình ruff với 6 nhóm luật (`E9, F821, F811, F401, F541, F841`); không có `mypy`/`pyright` trong `requirements-dev.txt` lẫn trong `.github/workflows/python-test.yml`. Trong khi mã dùng gợi ý kiểu khá dày (`Dict[str, int]`, `Optional[...]`, dataclass).

**Ảnh hưởng:** các lỗi kiểu như `Final` bị gán lại (P2-6), `group_signalled` có thể chưa gán (P2-1), hay `None` lọt vào chỗ cần `int` chỉ bị phát hiện khi chạy thật.

---

### P2-8. Sàn phủ kiểm thử trong tích hợp liên tục (CI – Continuous Integration) quá thấp so với thực tế

**Bằng chứng:** `.github/workflows/python-test.yml` dùng `--cov-fail-under=33` trong khi thực tế 39,0 % → chỉ còn **6 điểm dư địa**. Không có `--cov-branch` nên **không đo phủ nhánh** — với mã nhiều `if/else` phòng thủ như repo này, phủ nhánh thấp hơn phủ dòng đáng kể.

Tích hợp liên tục (CI – Continuous Integration) hiện có 6 job (lint, bandit, test trên Python 3.9/3.11/3.13/3.14, coverage, package, cross-platform Windows/macOS) — về hình thức là tốt; vấn đề nằm ở **ngưỡng**, không ở **phạm vi**.

---

### P3 — Vệ sinh và nhất quán (gộp vào việc khác)

| # | Vấn đề | Bằng chứng |
|---|---|---|
| P3-1 | Tên di sản "HyperTTS" còn 50 chỗ; `HyperTTSError = SuperFreeTTSError` (`errors.py:12`) là alias, 0 chỗ dùng tên mới | `errors.py:8,12`; 50 lần xuất hiện `HyperTTS` |
| P3-2 | 232 khoá dịch thừa trong `en.json` | đo bằng script |
| P3-3 | 7 chỗ `from aqt.qt import *`; ruff không bật `F403` nên không cảnh báo | `component_kokoro_manager.py:10`, `component_mms_manager.py:4`, … |
| P3-4 | Tài liệu trỏ tới file không tồn tại (`set_edge_workers_20.py`) | `batch_constants.py:49`, `build_share.py:71` |
| P3-5 | Rác trong thư mục làm việc: `.coverage`, `coverage.json` (24-10), `dist/`, `SuperFreeTTS.ankiaddon` cũ | đều nằm trong `.gitignore` nhưng vẫn trên đĩa, dễ gây nhầm khi phát hành |
| P3-6 | `update_max_processes` (`process_pool.py:481-487`) hạ trần nhưng **không dọn** tiến trình dư; chỉ tự hết sau 180 giây nhờ bộ dọn nhàn rỗi | `process_pool.py:336-360` |
| P3-7 | Cây làm việc không sạch từ trước khi kiểm toán | `git status`: `M .hermes.md`, `?? AI_Documents/bao-cao-hieu-nang-2026-10-24.md` |

---

## 5. Những điểm đã kiểm và **ĐẠT** (ghi nhận công bằng)

Không phải mọi thứ đều có vấn đề. Các điểm sau đã kiểm kỹ và làm đúng:

1. **Bảo mật giải nén** (`archive_utils.py`): chặn đường dẫn `../`, đường dẫn tuyệt đối, đường dẫn có ổ đĩa, liên kết tượng trưng (symlink), liên kết cứng (hardlink), thiết bị, file mã hoá, và có trần 2 gibibyte (GiB – Gibibyte) / 200.000 mục. Đây là mã chất lượng cao.
2. **Toàn vẹn tải về** (`downloader.py:32,265-300`): thuật toán băm an toàn 256-bit (SHA-256 – Secure Hash Algorithm 256-bit) cho Python embed, Piper, Kokoro; thuật toán băm thông điệp 5 (MD5 – Message Digest Algorithm 5) + kích thước cho giọng Piper; kiểm kích thước; xoá file hỏng khi sai.
3. **Không có thu thập dữ liệu từ xa (telemetry):** `__init__.py:13` đặt `enable_stats_error_reporting = False`; `stats.py:6` ghi rõ "All telemetry and network requests ... have been removed". Định danh duy nhất toàn cục của người dùng (`user_uuid` – Universally Unique Identifier) chỉ lưu cục bộ. **Không có rò rỉ dữ liệu người dùng.**
4. **Không có lỗ hổng thực thi lệnh:** 0 chỗ `shell=True`; `eval`/`exec` chỉ là `dialog.exec()` của Qt (không phải `exec()` của Python); 0 `pickle`.
5. **Mạng có thời gian chờ:** `http_utils.py:20-27` đặt mặc định (5 giây kết nối, 20 giây đọc) và mọi yêu cầu đi qua đây; `nosec B113` là hợp lý vì thời gian chờ được chèn ngay dòng trên.
6. **Truy vấn ngôn ngữ truy vấn có cấu trúc (SQL – Structured Query Language)** dùng `?` cho tham số, chỉ ghép chuỗi cho danh sách `IN (...)` với mã định danh (ID – Identifier) số (`anki_utils.py:141`, `superfreetts.py:537`, đều có `# nosec B608`).
7. **Cache âm thanh** (`audio_file_store.py`): tên theo nội dung thuật toán băm an toàn 224-bit (SHA-224 – Secure Hash Algorithm 224-bit), ghi nguyên tử qua `os.replace`, kiểm magic-byte khi đọc, bộ nhớ đệm ít dùng gần nhất (LRU – Least Recently Used) 4096 mục — 91,7 % phủ.
8. **Di trú cấu hình** (`config_store.py:82-91`): chỉ `setdefault`, có sao lưu trước khi đổi, giữ `CONFIG_BACKUP_KEEP` bản — đúng như báo cáo 24-10; 15 test di trú.
9. **Checkpoint** (`batch_executor.py:315-421`): định dạng v2 theo mã định danh (ID – Identifier) note, ghi nguyên tử, tự chuyển từ v1.
10. **Quy ước đầu dòng và xuống dòng (CRLF – Carriage Return Line Feed)** được giữ tuyệt đối: 34.908 dòng, 0 vi phạm.
11. **Bảo vệ dữ liệu người dùng** trong `backup_guard.py`: vá tạm `mw.col.create_backup` nhưng có đếm lồng nhau, có dấu trong profile, và tự sửa nếu Anki crash giữa lúc vá. Rủi ro kiến trúc (vá thủ công giao diện lập trình ứng dụng (API – Application Programming Interface) của Anki) nhưng cách xử lý là cẩn thận.

---

## 6. Kế hoạch cải thiện chi tiết

> **Đơn vị ước lượng:** "người-ngày" = công của một người làm việc trọn 1 ngày. Mọi bước đều kết thúc bằng việc **chạy lại cổng**, không phải bằng "đã sửa xong".

### Đợt 0 — Phát hành đúng (làm ngay, trước mọi việc khác)

| Bước | Việc | File đụng tới | Tiêu chí nghiệm thu | Ràng buộc | Rủi ro |
|---|---|---|---|---|---|
| 0.1 | Dựng lại gói từ HEAD | không sửa mã; chạy `python build_share.py` | Gói mới có `external/edge_tts/constants.py` chứa `api.msedgeservices`; 632 mục; ~2,18 megabyte (MB – Megabyte) | Không bump phiên bản trong bước này | Ghi đè `SuperFreeTTS.ankiaddon` cũ — cần lưu bản cũ để đối chiếu |
| 0.2 | Thêm cổng "gói khớp mã nguồn" | `scripts/verify_package.py` | Với mỗi file `.py` trong gói, băm thuật toán băm an toàn 256-bit (SHA-256 – Secure Hash Algorithm 256-bit) phải trùng file tương ứng trong cây nguồn; lệch 1 file → mã lỗi 1 | Giữ nguyên các kiểm tra cũ (đường dẫn cấm, phiên bản, smoke import) | Gói dựng trên máy khác có thể khác do xuống dòng — phải áp quy tắc đầu dòng và xuống dòng (CRLF – Carriage Return Line Feed) trước khi băm |
| 0.3 | Chốt phiên bản phát hành | `manifest.json`, `superfreetts_addon/version.py`, `release_notes.py`, `CHANGELOG.md` | 26.10.4 ở cả 4 nơi; `tests/test_version_consistency.py` xanh | Không sửa mã chức năng | Quên một nơi → test nhất quán phiên bản bắt được |
| 0.4 | Gắn thẻ mới cho commit đã có bản sửa | git tag | Thẻ `26.10.4` trỏ vào commit chứa `6271884` (hoặc commit kế tiếp) | Chỉ sau khi người dùng phê duyệt | Thẻ cũ `26.10.3` đã công bố — **không xoá**, ghi rõ trong ghi chú phát hành là bản 26.10.3 có lỗi dịch vụ chuyển văn bản thành giọng nói của Microsoft Edge (EdgeTTS – Microsoft Edge Text-to-Speech) |

**Ước lượng:** 0,5 người-ngày. **Đây là đợt duy nhất nên làm trước khi bất cứ ai tải gói.**

### Đợt 1 — Tài nguyên và tiến trình (đúng chủ đề nhánh hiện tại)

| Bước | Việc | File đụng tới | Tiêu chí nghiệm thu | Ràng buộc | Rủi ro |
|---|---|---|---|---|---|
| 1.1 | Kết thúc tiến trình **ngoài khoá** | `services/process_pool.py:455-479`, `:408` | Test mới: 4 tiến trình giả, `stop_all()` trả về < 200 mili-giây (ms – millisecond) (đo bằng `time.monotonic()`); không lời gọi `terminate_process` nào diễn ra khi đang giữ `self._lock` (kiểm bằng cách tiêm bộ đếm) | Giữ nguyên ngữ nghĩa "dừng cả tiến trình đang chạy lẫn chờ" | Nếu nhả khoá sớm, một luồng khác có thể lấy lại tiến trình đang bị giết → phải đánh dấu `is_healthy = False` **trước** khi nhả khoá |
| 1.2 | Chống tiến trình mồ côi phía runner | `services/runner_base.py`, `piper_runner.py`, `kokoro_runner.py`, `sherpa_runner_v2.py`, `supertonic_runner.py` | Test: khởi động runner, giết tiến trình cha, runner tự thoát trong ≤ 15 giây (`proc.poll() is not None`) | Không thêm thư viện ngoài; chỉ dùng `os.getppid()` + `threading` | Trên Windows `os.getppid()` có thể trả mã định danh tiến trình (PID – Process Identifier) đã tái sử dụng — phải so cả thời điểm khởi tạo hoặc dùng `psutil` **tuỳ chọn** (không bắt buộc) |
| 1.3 | Sổ đăng ký pool thay danh sách cứng | `superfreetts.py:717-722`, `services/process_pool.py` | Thêm một pool giả vào sổ → `shutdown()` dừng nó (test mới); danh sách cứng bị xoá | Giữ 4 pool hiện có hoạt động y hệt | Vòng đời: pool đăng ký mà không bao giờ gỡ → rò rỉ tham chiếu; dùng tham chiếu yếu (`weakref`) |
| 1.4 | `atexit` + xử lý tín hiệu | `superfreetts_addon/__init__.py` | Test: gọi thẳng hàm dọn qua `atexit._run_exitfuncs()` trong môi trường test → mọi pool nhận `stop_all` | Chỉ đăng ký một lần (idempotent) | Anki có thể tải lại add-on; đăng ký nhiều lần gây gọi lặp → dùng cờ |
| 1.5 | Dọn tiến trình dư khi hạ trần | `services/process_pool.py:481-487` | Sau `update_max_processes(2)` với 4 tiến trình nhàn rỗi, còn ≤ 2 tiến trình sống trong ≤ 1 giây | Không giết tiến trình đang bận | Giết nhầm tiến trình vừa được cấp phát → kiểm `proc not in self._active` |
| 1.6 | Sửa `group_signalled` và siết `except` ở `terminate_process` | `services/process_pool.py:145-204` | `group_signalled = False` khởi tạo trước; nhánh đã chết vẫn đóng được pipe; test mới cho `poll() is not None` | Không đổi hành vi kết thúc | Thấp |

**Ước lượng:** 3–4 người-ngày. **Tiêu chí chung của đợt:** số tiến trình còn sống sau `shutdown()` = 0 (đo bằng `psutil` trong test tích hợp, chỉ dùng khi có thư viện).

### Đợt 2 — Xử lý lỗi có thể chẩn đoán

| Bước | Việc | File đụng tới | Tiêu chí nghiệm thu | Ràng buộc | Rủi ro |
|---|---|---|---|---|---|
| 2.1 | Thay `pass` bằng log có ngữ cảnh, **bắt đầu từ `process_pool.py`** (15 chỗ) | `services/process_pool.py` | Bandit B110 của file này = 0; log có tên tiến trình + thao tác | Không đổi luồng điều khiển; chỉ thêm `logger.warning(..., exc_info=True)` | Log nhiều làm chậm batch — dùng mức `debug` cho trường hợp bình thường, `warning` cho bất thường |
| 2.2 | Tiếp `service_logger.py` (4), `runner_base.py` (2), `piper_runner.py` (2) | các file trên | B110 toàn repo ≤ 15 (từ 43) | Giữ nguyên hành vi chịu lỗi (không được để lỗi làm sập batch) | Vô tình biến lỗi không nghiêm trọng thành lỗi chặn |
| 2.3 | Thu hẹp `except Exception` ở tầng dịch vụ | `services/service_*.py`, `tts_orchestrator.py` | Mỗi chỗ bắt đúng loại lỗi (`requests.RequestException`, `OSError`, `subprocess.SubprocessError`, …); nơi buộc phải bắt rộng thì có bình luận giải thích | Không đổi hợp đồng `get_tts_audio()` | Bắt hẹp quá → lỗi mới nổi lên thành sự cố; làm theo từng file, chạy test sau mỗi file |
| 2.4 | `init_services` không đánh dấu xong khi lỗi | `servicemanager.py:129-143` | Test mới: module import lỗi → `_services_discovered` vẫn `False`, lần gọi sau thử lại; dịch vụ còn lại vẫn dùng được | Vẫn phải "chịu lỗi từng module" | Vòng lặp thử lại vô hạn nếu lỗi vĩnh viễn → đếm số lần thử |
| 2.5 | Bỏ khởi tạo đối tượng để đọc tên dịch vụ | `servicemanager.py:158-188`, `service.py` | `name`/`service_fee` là thuộc tính lớp; test: đếm số lần hàm dựng được gọi lúc `init_services` = 0 | Không đổi giao diện lập trình ứng dụng (API – Application Programming Interface) công khai của `ServiceBase` | Dịch vụ nào đặt `name` trong `__init__` sẽ hỏng → rà từng file dịch vụ trước |

**Ước lượng:** 3 người-ngày. **Không được gộp bước 2.3 với bất kỳ refactor nào khác** — mỗi lần chỉ đổi một file.

### Đợt 3 — Kiểm thử tầng giao diện và ranh giới Anki

| Bước | Việc | File đụng tới | Tiêu chí nghiệm thu | Ràng buộc | Rủi ro |
|---|---|---|---|---|---|
| 3.1 | Dựng khung test giao diện không cần Anki | `tests/mock_anki.py`, `tests/conftest.py`, file mới `tests/test_ui_smoke.py` | Dựng được 8 hộp thoại chính trong chế độ giả lập, không ném lỗi; mỗi hộp thoại ≥ 3 khẳng định | Không thêm `pytest-qt` nếu không cần; giữ bộ test chạy < 30 giây | Giả lập Qt quá nông → test chỉ kiểm "không crash", giá trị thấp; phải khẳng định trên **nhãn nút, trạng thái bật/tắt, số dòng bảng** |
| 3.2 | Test cho `component_services.py` (6,0 %) | `tests/test_component_services.py` (mới) | Phủ file ≥ 40 %; kiểm: bật/tắt dịch vụ ghi vào cấu hình; số luồng bị kẹp về 1..3 | Không sửa mã nguồn trong bước này | Hàm `draw_service_options` 286 dòng rất khó dựng cảnh — ưu tiên test các hàm nhỏ gọi từ nó |
| 3.3 | Test cho `component_voiceselection.py` (6,7 %) | file mới (`tests/test_component_voiceselection.py`) | Phủ ≥ 40 %; kiểm: lọc giọng theo ngôn ngữ, sắp xếp, chọn nhiều giọng, sửa luôn lỗi dự phòng (fallback) ở `component_voiceselection.py:120-135` (issue #4) | — | Phụ thuộc danh sách giọng thật → dùng dữ liệu mẫu cố định |
| 3.4 | Test cho `anki_utils.py` (0 %) | `tests/test_anki_utils.py` (mới) | Phủ ≥ 50 % phần logic thuần (đọc/ghi cấu hình, đường dẫn media, ghép danh sách mã định danh (ID – Identifier)); phần gọi `aqt` giữ nguyên không test | Bất biến "bộ test không cần Anki" | Cố test quá sâu sẽ phải giả lập collection thật — dừng ở ranh giới |
| 3.5 | Nâng sàn phủ và bật đo nhánh | `.github/workflows/python-test.yml` | `--cov-fail-under` = **45**; thêm `--cov-branch`; ghi nhận phủ nhánh thực tế vào `AI_Documents/` | Chỉ nâng sau khi 3.1–3.4 xanh | Nâng sàn quá sớm làm tích hợp liên tục (CI – Continuous Integration) đỏ liên tục → nâng theo bậc 39 → 42 → 45 |

**Ước lượng:** 6–8 người-ngày (phần lớn là dựng khung). **Đây là đợt tốn công nhất nhưng đổi lại giá trị lâu dài lớn nhất.**

### Đợt 4 — Gỡ trùng lặp và dọn mã chết

| Bước | Việc | File đụng tới | Tiêu chí nghiệm thu | Ràng buộc | Rủi ro |
|---|---|---|---|---|---|
| 4.1 | Xoá mã chết đã xác nhận | `component_onnx_manager.py`, `batch_executor.py:537-594`, `batch_executor.py:119-189`, `services/test_runner.py`, `resource_manager.py:150-241`, `system_utils.py:481` | `grep` không còn tham chiếu; pytest 493 → vẫn ≥ 470 (bỏ test của mã chết); gói giảm ≥ 25 kilobyte (KB – Kilobyte) | Giữ `resource_manager._get_process_ram_usage_without_psutil` (đang dùng thật) | Xoá nhầm lớp còn được nạp động → kiểm bằng `grep` + chạy `verify_package.py` smoke |
| 4.2 | Gộp 7 hàm stylesheet thành 1 bộ dựng + 7 bảng màu | `gui_utils.py:477-2602` | Số dòng file giảm từ 2.602 xuống ≤ 1.100; 7 giao diện trông **không đổi** (so ảnh chụp trước/sau từng theme) | Không đổi tên theme, không đổi giá trị màu | Đây là thay đổi giao diện — rủi ro thị giác; phải chụp ảnh 7 theme trước khi sửa |
| 4.3 | Tách `draw_service_options` (286 dòng) và `_execute_unique_tasks_unified` (243 dòng) | `component_services.py:300`, `batch_orchestrator.py:408` | Mỗi hàm ≤ 80 dòng; hành vi không đổi (test cũ xanh) | Không đổi hợp đồng | Cần test bảo vệ trước — **phải làm sau đợt 3** |
| 4.4 | Đơn giản hoá vòng gửi việc | `batch_orchestrator.py:491-568`, `tts_orchestrator.py:374-421` | Chỉ còn **một** nơi được gán `executor` (tìm `\.executor =` chỉ ra 1 kết quả ngoài hàm khởi tạo); xoá 3 alias thừa | Phải giữ hành vi "hoãn khi pool bận" | Cao nhất trong đợt — làm sau cùng, có test tải (nhiều chunk, huỷ giữa đường) |

**Ước lượng:** 5–6 người-ngày. Bước 4.2 và 4.4 nên tách thành hai lần phát hành riêng.

### Đợt 5 — Quốc tế hoá (i18n – internationalization), kiểu tĩnh, vệ sinh

| Bước | Việc | File đụng tới | Tiêu chí nghiệm thu | Ràng buộc | Rủi ro |
|---|---|---|---|---|---|
| 5.1 | Siết cổng quốc tế hoá (i18n – internationalization) | `scripts/i18n_audit.py`, `.github/workflows/python-test.yml` | Thêm `--min-coverage` (ví dụ 40 %) và `--strict-locales en,vi`; tích hợp liên tục (CI – Continuous Integration) đỏ nếu một ngôn ngữ **đang bật trong giao diện** tụt dưới ngưỡng | tiếng Anh / tiếng Việt (en/vi – English/Vietnamese) vẫn 100 % | Nếu bật ngưỡng cho cả 7 ngôn ngữ, tích hợp liên tục (CI – Continuous Integration) đỏ ngay → chỉ áp cho ngôn ngữ được chọn làm "chính thức" |
| 5.2 | Quyết định số phận 4 ngôn ngữ dở | `superfreetts_addon/locales/*.json`, `i18n.py` | Hoặc dịch đủ ≥ 90 %, hoặc ẩn khỏi danh sách chọn ngôn ngữ | Không làm mất bản dịch đã có | Người dùng đang chọn tiếng Nhật / tiếng Trung (ja/zh – Japanese/Chinese) sẽ thấy mất tuỳ chọn — ghi vào CHANGELOG |
| 5.3 | Dọn 232 khoá thừa | `locales/en.json` | Số khoá = số khoá dùng + khoá động đã biết (420 + ~14) | Phải rà khoá động bằng tay (`component_preferences.py:260` dùng f-string) | Xoá nhầm khoá động → chữ thô hiện ra; kiểm bằng `i18n_audit` + rà tay 10 vị trí đã biết |
| 5.4 | Thêm mypy ở chế độ dần dần | `pyproject.toml`, tích hợp liên tục (CI – Continuous Integration) | `mypy --ignore-missing-imports` trên 6 module lõi (`batch_executor`, `batch_orchestrator`, `system_utils`, `config_models`, `audio_file_store`, `process_pool`) = 0 lỗi | Không bắt buộc toàn repo (quá lớn) | Gợi ý kiểu hiện tại có thể sai nhiều → chạy thử trước, ghi số lỗi thật vào kế hoạch |
| 5.5 | Bỏ `Final` bị gán lại; ghi rõ bất biến Edge | `batch_constants.py:44-46`, 6 test liên quan | Thêm test so với **số 3 literal**; test riêng cho `_local_override` (nếu có file thì phải log cảnh báo to) | Không phá cơ chế override cho người dùng nâng cao | Nếu bỏ `Final` thì mất tín hiệu cho người đọc → ghi bình luận giải thích |
| 5.6 | Dọn tên di sản HyperTTS | `errors.py:12` + 50 chỗ | Chỉ còn alias tương thích, có `# deprecated`; mã mới dùng `SuperFreeTTSError` | Không đổi tên lớp công khai (tránh phá vỡ) | Thấp |
| 5.7 | Sửa tài liệu trỏ file không tồn tại | `batch_constants.py:49`, `build_share.py:71`, `.hermes.md` | Không còn nhắc `set_edge_workers_20.py`; `.hermes.md` ghi đúng cơ chế override | — | Thấp |

**Ước lượng:** 3–4 người-ngày.

---

## 7. Thứ tự, phụ thuộc, và vì sao thứ tự này

```
Đợt 0 (phát hành)  ──►  Đợt 1 (tài nguyên)  ──►  Đợt 2 (lỗi)
                                   │
                                   └──►  Đợt 3 (test giao diện) ──►  Đợt 4 (gỡ trùng lặp)
                                                                          │
                                                                          └──►  Đợt 5 (i18n/kiểu/vệ sinh)
```

Lý do ràng buộc:
- **Đợt 0 trước tất cả:** đang có một gói cài sai trên đĩa. Mọi việc khác đều vô nghĩa nếu người dùng vẫn tải bản lỗi.
- **Đợt 1 trước đợt 3:** sửa khoá trong `process_pool` làm thay đổi hành vi đóng profile — cần test mới của đợt 1 làm lưới an toàn trước khi viết test giao diện.
- **Đợt 3 trước đợt 4:** không được tách hàm 286 dòng (`draw_service_options`) khi chưa có test bảo vệ. Đây là điều kiện tiên quyết, không phải lời khuyên.
- **Đợt 5 sau cùng:** dọn khoá quốc tế hoá (i18n – internationalization) và đổi tên chỉ an toàn khi giao diện đã có test.

---

## 8. Rủi ro tổng thể và cách giảm

| Rủi ro | Khả năng | Tác động | Cách giảm |
|---|---|---|---|
| Sửa `process_pool` gây treo mới khi đóng profile | Trung bình | Cao (mất dữ liệu batch đang chạy) | Test tải: 4 pool × 2 tiến trình, đóng profile giữa lúc chạy; đo thời gian `shutdown()` < 3 giây |
| Thêm kiểm tra tiến trình cha làm runner tự thoát giữa batch trên Windows | Trung bình | Cao | Chỉ bật kiểm tra khi `os.getppid()` trả giá trị dương và ổn định qua 3 lần đọc; có cờ tắt qua cấu hình |
| Xoá mã chết nhầm thứ còn dùng | Thấp | Trung bình | Trước khi xoá: `grep` toàn repo + chạy `scripts/verify_package.py` (smoke import thật trong trình thông dịch sạch) |
| Gộp stylesheet làm lệch giao diện | Cao | Thấp (thẩm mỹ) | Chụp ảnh 7 theme trước/sau; so từng cặp; giữ nguyên bảng màu từng theme |
| Nâng sàn phủ làm tích hợp liên tục (CI – Continuous Integration) đỏ liên tục | Trung bình | Thấp | Nâng theo bậc 39 → 42 → 45, mỗi bậc một lần phát hành |
| Đợt 4.4 (bỏ hai chủ sở hữu executor) gây mất việc giữa batch | Trung bình | Cao | Làm cuối cùng, có test "gửi 200 chunk, huỷ ở chunk 50, không mất note nào đã xong" |
| Người dùng mất tuỳ chọn ngôn ngữ tiếng Nhật / tiếng Trung (ja/zh – Japanese/Chinese) | Chắc chắn nếu làm 5.2 | Thấp | Ghi rõ trong CHANGELOG; giữ file dịch, chỉ ẩn khỏi danh sách |

**Điều kiện dừng khẩn (rollback):** bất kỳ đợt nào làm `pytest` đỏ quá 2 giờ, hoặc làm `verify_package.py` báo lỗi — quay lại commit đầu đợt, không cố sửa tiếp trong cùng nhánh.

---

## 9. Cách nghiệm thu lại sau mỗi đợt (chạy đúng 7 lệnh)

```bash
.venv/bin/python -m pytest tests/ -q --tb=short
.venv/bin/ruff check superfreetts_addon build_share.py scripts tests
.venv/bin/python scripts/i18n_audit.py --check
.venv/bin/python scripts/verify_package.py SuperFreeTTS.ankiaddon
.venv/bin/bandit -ll -r superfreetts_addon
.venv/bin/python scripts/check_critical_coverage.py coverage.json
.venv/bin/python scripts/vendor_deps.py --check
```

**Bảng ngưỡng cần đạt theo đợt:**

| Chỉ số | Hiện tại | Sau đợt 1 | Sau đợt 3 | Sau đợt 5 |
|---|---:|---:|---:|---:|
| Test đậu | 493 | ≥ 505 | ≥ 545 | ≥ 560 |
| Phủ dòng | 39,0 % | 39,0 % | ≥ 45 % | ≥ 48 % |
| Bandit B110 | 43 | 43 | ≤ 25 | ≤ 15 |
| Bandit High | 0 | 0 | 0 | 0 |
| File `.py` trong gói lệch cây nguồn | **7** | **0** | 0 | 0 |
| Thời gian `shutdown()` (4 pool) | ~12 giây (lý thuyết) | **< 3 giây** | < 3 giây | < 3 giây |
| Số dòng `gui_utils.py` | 2.602 | 2.602 | 2.602 | ≤ 1.100 |
| Ngôn ngữ phủ < 40 % | 4 | 4 | 4 | 0 (dịch đủ hoặc ẩn) |

---

## 10. Phụ lục

### A. Bằng chứng thô đã dùng

- pytest: `493 passed, 1 skipped in 6.92s`; test bị bỏ qua duy nhất: `tests/test_mms_active.py:33` ("English MMS model not found in voice list").
- Bandit: `Total issues (by severity): Low 109, Medium 0, High 0`; phân rã theo mã: B110 **43**, B603 18, B311 15, B404 13, B101 8, B607 8, B606 4.
- Coverage (chạy mới, ghi ra thư mục tạm): `TOTAL 19692 12016 39%`.
- Kích thước: `superfreetts_addon` 34.908 dòng / 110 file; `tests` 10.619 dòng / 82 file.
- Gói: 632 mục, 2.281.489 byte; 7 file `.py` khác cây nguồn; `external/edge_tts/constants.py` trong gói có 0 lần `msedgeservices`, trong cây nguồn có 1 lần.
- Git: HEAD `6271884`; thẻ `26.10.3` → `55089d3`; `git status` có `M .hermes.md` và 1 file chưa theo dõi (đều có từ trước).

### B. 15 chỗ `except: pass` trong `process_pool.py` (ưu tiên sửa đầu tiên)

Dòng 160, 170, 174, 188, 190, 195, 203, 238, 245, 270, 477, 570, 587, 591, 600. Trong đó **dòng 190** đang che lỗi `UnboundLocalError` thật ở dòng 178 (xem P2-1).

### C. Ghi chú phương pháp (để lần sau tái lập đúng)

1. Không đo được thời gian import add-on ngoài Anki vì `import superfreetts_addon.*` cần `anki` trên đường dẫn (`ModuleNotFoundError: No module named 'anki'`). Muốn đo phải dùng bộ giả lập trong `tests/mock_anki.py`. Số đo có giả lập: `superfreetts` 46,6 mili-giây (ms – millisecond), `config_models` 24,5 mili-giây (ms – millisecond) — không phải nút cổ chai.
2. Đếm "nuốt lỗi" phải nêu rõ định nghĩa: bandit B110 = chỉ `except: pass` (43); đếm mở rộng thêm `continue`/`return None` = 60. Trộn hai con số mà không nói rõ sẽ gây tranh cãi vô ích.
3. Độ phủ phải đo lại tại HEAD, không dùng `coverage.json` có sẵn trong repo (file đó từ 24-10). Kết quả trùng nhau (39,0 %) nhưng đó là may, không phải quy tắc.
4. Khi kiểm "mã chết", phải tìm cả nạp động: `services/service_*.py` được nạp bằng `importlib` (`servicemanager.py:145-156`) nên **không** được coi là chết dù không có `import` tĩnh.

---

**Kết luận một câu:** repo ở trạng thái kỹ thuật tốt hơn mức trung bình của add-on Anki (cổng đầy đủ, bảo mật giải nén và tải về nghiêm túc, không thu thập dữ liệu từ xa (telemetry), quy ước đầu dòng và xuống dòng (CRLF – Carriage Return Line Feed) được giữ), nhưng đang có **một lỗi phát hành thật** (gói và thẻ lệch HEAD, dịch vụ chuyển văn bản thành giọng nói của Microsoft Edge (EdgeTTS – Microsoft Edge Text-to-Speech) bị lỗi 403) và **ba điểm rủi ro tài nguyên** (giết tiến trình trong khoá, tiến trình mồ côi, khám phá dịch vụ hỏng không thử lại). Sửa đợt 0 ngay, đợt 1 trong tuần này, phần còn lại theo kế hoạch 5 đợt ở trên.
