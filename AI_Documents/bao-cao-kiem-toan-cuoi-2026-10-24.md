# Báo cáo kiểm toán cuối — SuperFreeTTS 26.10.3 (24-10-2026)

Ngày chạy: 24-10-2026, khoảng 21:04–21:09 (+07). Nhánh `fix/resource-management`, HEAD `55089d3`.

## 0. Kết luận trong 10 dòng

1. **Kết luận: PASS** — phát hành được, không phát hiện điểm chặn (blocker).
2. Phiên bản 26.10.3, nhất quán ở cả 5 nơi (version.py, manifest.json, TARGET_VERSION, RELEASE_NOTES[0], đầu CHANGELOG).
3. HEAD `55089d3`, cây làm việc sạch (chỉ còn hai file báo cáo chưa theo dõi, không có file nào bị sửa).
4. Kiểm thử: 474 đậu, 1 bỏ qua, 0 lỗi. Ruff sạch. Bandit: 109 Low, 0 Medium, 0 High.
5. i18n: tiếng Anh và tiếng Việt đủ 652/652 khóa, không thiếu khóa nào đang dùng.
6. Gói phát hành dựng lại: 632 mục, file 2.281.489 byte (~2,18 MB), sha256 `f96e524b...9c548aa3`.
7. Trong gói: không có dữ liệu giọng/model, không file nhị phân, không đường dẫn nguy hiểm, mọi file `.py` giống hệt mã nguồn.
8. 5 lỗi của đợt kiểm toán 26.10.2 đều đã đóng (di trú, hủy batch, ghi lỗi sai khi huỷ, gói 117 MB, khóa thiếu).
9. Còn lại chỉ là nợ kỹ thuật đã biết và được chấp nhận (hàm dài, phủ UI thấp, `except: pass` mức Low).
10. Không bump version, không sửa mã nguồn trong lần kiểm toán này; commit báo cáo, push và thẻ `26.10.3` làm sau khi PASS + review, theo phê duyệt (xem §8).

## 1. Bảng điểm (18 tiêu chí)

| # | Tiêu chí | Kết quả thật | Ngưỡng | Kết luận |
|---|---|---|---|---|
| 1 | pytest | 474 passed, 1 skipped, 0 failed, exit 0 | 474 passed, 1 skipped, 0 failed | PASS |
| 2 | ruff (4 mục tiêu) | "All checks passed", exit 0 | exit 0 | PASS |
| 3 | bandit `-ll` | 109 Low, 0 Medium, 0 High | 0 Medium, 0 High | PASS |
| 4 | `except:` trần | bandit E722 = 0; grep thô ra 15 dòng nhưng toàn là chú thích/chuỗi (0 câu lệnh thật) | 0 | PASS |
| 5 | B110 nuốt lỗi | 43 vị trí; đếm AST `except Exception: pass` = 43, khớp nhau | khớp nhau, đã ghi nhận | PASS |
| 6 | tham số mặc định khả biến | 0 | 0 | PASS |
| 7 | phủ kiểm thử tổng | 39,0 % (7671/19660) | ≥ 39,0 % (sàn CI 33 %) | PASS |
| 8 | `check_critical_coverage.py` | exit 0, 5/5 module ≥ 70 % | exit 0 | PASS |
| 9 | i18n audit | exit 0; en 652/652, vi 652/652, used-but-missing 0 | như bên trái | PASS |
| 10 | khóa động (dynamic families) | thiếu 0 ở en, thiếu 0 ở vi, wrapper literal thiếu 0 | 0 | PASS |
| 11 | dung lượng gói | file 2.281.489 byte (~2,18 MB); chưa nén 8,04 MB | file < 5 MiB; chưa nén < 15 MB | PASS |
| 12 | số mục trong gói | 632 mục | 600–700 | PASS |
| 13 | rò rỉ gói | 0 mục `data/`/`user_files/`/`cache/`; 0 `.pyc/.so/.onnx/.ort`; 0 magic nhị phân; 0 đường dẫn xấu | 0 | PASS |
| 14 | gói khớp mã nguồn | mọi `.py` trong gói giống hệt từng byte với cây làm việc | 100 % | PASS |
| 15 | `verify_package.py` | exit 0, "OK" | exit 0 "OK" | PASS |
| 16 | phiên bản | 26.10.3 ở cả 5 nơi, trùng nhau | trùng nhau | PASS |
| 17 | CRLF | 110/110 file `.py` có CRLF, 0 vi phạm | 110/110 | PASS |
| 18 | trạng thái git | HEAD `55089d3`, không file nào bị sửa, không commit mới | như bên trái | PASS |

## 2. Cổng kiểm tra — output thật

pytest (dòng cuối):

```
TOTAL                                                      19660  11989    39%
8 files skipped due to complete coverage.
Coverage JSON written to file dist/audit/cov.json
======================== 474 passed, 1 skipped in 9.73s ========================
```

ruff:

```
All checks passed!
```

bandit `-ll` (phần kết quả):

```
Test results:
	No issues identified.
Run metrics:
	Total issues (by severity):
		Undefined: 0
		Low: 109
		Medium: 0
		High: 0
```

i18n_audit `--check` (toàn bộ):

```
locale    keys  missing  extra  coverage
en         652        0      0    100.0%
ja          89      563      0     13.7%
ko         437      215      0     67.0%
sv         189      463      0     29.0%
vi         652        0      0    100.0%
zh-CN       89      563      0     13.7%
zh-TW       89      563      0     13.7%

keys used in code : 420
keys defined in en: 652
used but missing in en: 0
```

verify_package.py:

```
[verify] smoke: {"ram_mb": 6330, "ram_source": "linux_meminfo", "edge_cap": 3, "requests": "2.32.4", "charset_normalizer": "3.4.2", "aiohttp": "3.13.3", "edge_tts": "7.3.1", "servicemanager_loaded": true}
[verify] OK: /home/admin/Documents/deepseek-harness/default-workspace/superfreetts/SuperFreeTTS.ankiaddon (2.18 MB)
```

## 3. Phát hiện chi tiết

Không có blocker. Các phát hiện dưới đây đều không chặn phát hành (chính sách hiện tại đã chấp nhận).

### 3.1. Tình trạng 5 lỗi từ đợt kiểm toán 26.10.2 — tất cả đã đóng

- **B1 — di trú xóa cài đặt người dùng → đã đóng.** `config_models.py:939-948`: bước di trú schema < 6 chỉ `setdefault` (tạo thùng chứa còn thiếu), không xóa preset/quy tắc. `config_store.py:80-91`: trước khi viết lại có sao lưu cấu hình cũ (`backup_config_before_migration`, `config_store.py:102-126`), giữ `CONFIG_BACKUP_KEEP` bản mới nhất; điều kiện là `0 < previous_version < CONFIG_SCHEMA_VERSION` (`config_store.py:85-89`) — nếu chuỗi schema hỏng thì `previous_version = 0` (`:81-84`), không có bản sao lưu, nhưng dữ liệu vẫn an toàn vì bước di trú chỉ `setdefault`. Kiểm thử di trú: 15/15 đậu.
- **B2 — hủy batch không lưu phần đã xong → đã đóng.** `batch_orchestrator.py:327-332`: khi hủy, các note đã xử lý vẫn được `update_notes()` lưu, chỉ dừng các note tiếp theo. Kiểm thử hủy/treo: 6/6 đậu.
- **C1 — hủy batch đánh dấu nhầm thành lỗi → đã đóng.** Các vòng lặp kiểm tra `batch_status.must_continue` (`batch_orchestrator.py:143,224,304,351,419,494,501,559,573`) chỉ `break`, không ghi lỗi cho các note chưa làm. Kiểm thử checkpoint/hủy: 25/25 đậu.
- **A1 — gói 117 MB kèm dữ liệu → đã đóng.** Gói hiện tại 0 mục dưới `superfreetts_addon/data/`, chưa nén 8,04 MB, file ~2,18 MB. Engine và model giọng chỉ tải khi người dùng dùng tới.
- **D1 — 52 khóa i18n thiếu → đã đóng.** `used but missing in en: 0`; en và vi đủ 652/652.

### 3.2. B110 — 43 vị trí `except ...: pass` (mức Low, không chặn)

Bandit B110 = 43, đếm AST `except Exception: pass` = 43, khớp nhau. Tập trung ở: `services/process_pool.py` (15 vị trí: 160,170,174,188,190,195,203,238,245,270,477,570,587,591,600), `service_logger.py` (4: 40,85,111,137), `services/service_supertonic.py` (2: 176,201), `component_supertonic_setup.py` (3: 169,173,260), `component_kokoro_manager.py` (2: 112,336), `component_mms_manager.py` (2: 330,343), `component_batch_preview.py` (2: 623,763), `component_services.py` (2: 74,82), `downloader.py:326`, `services/piper_runner.py` (2: 197,201), `services/runner_base.py` (2: 23,38), `services/service_espeakng.py:30`, `services/service_mms.py:284`, `services/supertonic_runner.py:174`, `tts_orchestrator.py` (2: 365,408), `component_piper_manager.py:248`. Ảnh hưởng: lỗi ở các chỗ này bị lặng lẽ bỏ qua, khó chẩn đoán khi sự cố. Hướng sửa (đợt sau, không làm trong bản này): thay `pass` bằng ghi log warning kèm ngữ cảnh, bắt đầu từ `process_pool.py` và `service_logger.py`.

### 3.3. Hàm phức tạp / quá dài (ứng viên tái cấu trúc, không chặn)

8 hàm độ phức tạp ≥ 30, 14 hàm dài > 150 dòng. Nặng nhất: `component_services.py:300 draw_service_options` (phức tạp 56, 286 dòng), `batch_orchestrator.py:408 _execute_unique_tasks_unified` (phức tạp 54, 243 dòng — đã đọc kỹ, logic đúng: kiểm tra cache trước khi gom nhóm engine, hủy thì dừng gọn), `gui.py:196 init` (245 dòng), `services/kokoro_runner.py:23 main` (197 dòng), `component_services.py:822 draw` (187 dòng), `tts_orchestrator.py:114 build_engine_config` (183 dòng), `component_voiceselection.py:236 draw` (179 dòng). 7 hàm stylesheet trong `gui_utils.py` dài 282–351 dòng nhưng chỉ là chuỗi giao diện, rủi ro thấp (nguồn: `dist/audit/ast-structural.txt`). Ảnh hưởng người dùng: không trực tiếp; chỉ làm việc sửa lỗi sau này khó hơn. Hướng sửa: tách nhỏ dần ở các bản sau.

### 3.4. Phủ kiểm thử thấp ở module giao diện (đã biết, không chặn)

Phủ tổng 39,0 %. Các module giao diện gần như chưa có kiểm thử: `component_services.py` 6,0 %, `component_voiceselection.py` 6,7 %, `gui_utils.py` 7,0 %, `component_workflow.py` 11,5 %, `gui.py` 14,5 %. 5 module then chốt đều ≥ 70 % (config_models 70,2 %, batch_executor 83,7 %, component_text_processing 96,7 %, audio_file_store 91,7 %, voice_cache 91,8 %). Ảnh hưởng: lỗi giao diện khó bị kiểm thử bắt. Hướng sửa: bổ sung kiểm thử cho `component_services.py` và `component_voiceselection.py` ở bản sau.

### 3.5. Khóa i18n thừa và ngôn ngữ phủ thấp (không chặn)

en định nghĩa 652 khóa nhưng mã nguồn chỉ dùng 420 → 232 khóa định nghĩa mà chưa dùng (khóa cũ hoặc dự phòng). Các ngôn ngữ khác phủ thấp: ja 13,7 %, zh-CN/zh-TW 13,7 %, sv 29,0 %, ko 67,0 %. Chính sách: chỉ en + vi là chính thức, các ngôn ngữ khác tự rớt về tiếng Anh. Ảnh hưởng: không, người dùng không bao giờ thấy chữ thô (used-but-missing = 0). Hướng sửa: dọn 232 khóa thừa và bổ sung bản dịch ở bản sau.

## 4. Gói phát hành

- Mục: 632. Chưa nén 8,04 MiB; nén 2,19 MiB (2,28 MB thập phân); file 2.281.489 byte (2,18 MiB).
- Theo thư mục (chưa nén): external 5,72 MB; superfreetts_addon 2,17 MB; graphics 0,11 MB; LICENSE 0,04 MB; còn lại không đáng kể.
- 10 file lớn nhất: `superfreetts_addon/mms_languages.json` (486.810), `external/comtypes/gen/_C866..._0_5_4.py` (410.338), `external/certifi/cacert.pem` (288.447), `external/idna/uts46data.py` (247.970), `external/typing_extensions.py` (161.652), `external/dateutil/zoneinfo/dateutil-zoneinfo.tar.gz` (156.400), `external/click/core.py` (117.795), `superfreetts_addon/release_notes.py` (116.143), `external/attr/_make.py` (107.503), `graphics/donation_qr_v6.png` (103.409).
- 0 mục `data/`, 0 `user_files/`, 0 `cache/`, 0 `.pyc/.so/.onnx/.ort`, 0 magic nhị phân, 0 đường dẫn xấu.
- Mọi `.py` trong gói giống hệt từng byte với cây làm việc (461 file); 7 file `locales/*.json` cũng giống hệt; `config.json` trong gói cũng giống hệt bản trong cây (817 byte) — lần build này không sửa nội dung nào.
- sha256 trước khi dựng lại: `f4f75631...c10b916e`. Sau khi dựng lại: `f96e524bcdafaa02a038812a2e4fd3034aa8724021faa049e74b82ab9c548aa3`. Hai bản khác nhau vì zip ghi lại thời điểm nén, nên **không tái lập byte-for-byte** — bản chuẩn để phát hành là bản mới nhất `SuperFreeTTS.ankiaddon` tại thời điểm báo cáo, đối chiếu bằng sha256 ở trên (2.281.489 byte).

## 5. i18n

| Ngôn ngữ | Khóa | Phủ |
|---|---|---|
| en | 652 | 100,0 % |
| vi | 652 | 100,0 % |
| ko | 437 | 67,0 % |
| sv | 189 | 29,0 % |
| ja / zh-CN / zh-TW | 89 | 13,7 % |

Khóa động (14 khóa họ ghép từ mã): giới tính giọng (3), phí dịch vụ, loại dịch vụ, tùy chọn ngôn ngữ giao diện — thiếu 0 ở en, thiếu 0 ở vi. 1 vị trí dùng f-string trong `get_text` (`component_preferences.py:260`) đã kiểm tra, khóa sinh ra đều tồn tại. 3 khóa chữ dùng qua hàm bọc (`add_info_row`, `_text`) đều tồn tại. Không có khóa `service_option_*`/`service_description_*` nào trỏ tới dịch vụ không tồn tại.

Ngoài khóa dựng bằng f-string, còn 10 vị trí `get_text` nhận khóa qua biến/nối chuỗi mà script quét không thấy — đã mở từng chỗ kiểm tra bằng tay và xác nhận vẫn đúng danh sách cũ, không phát sinh chỗ mới: `voice.py:238`, `component_services.py:55,684,687,693`, `component_about.py:181,196,246`, `component_donation.py:67`, `component_failure_report.py:28`, `component_workflow.py:60`.

## 6. Điểm nóng hành vi — cả 5 đều đạt

1. **Di trú cấu hình** (`config_store.py:80-91`, `config_models.py:867-964`): không ghi đè lựa chọn người dùng; schema hỏng không làm sập khởi động. Kiểm thử di trú 15/15 đậu.
2. **Hủy batch** (`batch_orchestrator.py:304-332`): dừng note tiếp theo, lưu note đã xong, không đánh dấu lỗi sai. Kiểm thử hủy/treo 6/6 đậu.
3. **Checkpoint** (`batch_executor.py:315-384`): định dạng v2 theo note ID, ghi nguyên tử (file tạm + `os.replace`), tự chuyển đổi file v1 cũ. Kiểm thử checkpoint 25/25 đậu.
4. **Cache âm thanh** (`audio_file_store.py:231-238,309-346`): khóa = chữ + giọng + tùy chọn + định dạng (SHA-224); ghi nguyên tử; đọc có kiểm tra magic-byte (`audio_file_store.py:251`) và LRU 4096 mục đã xác thực (`:160`); sai định dạng tự sửa phần mở rộng. Kiểm thử cache 53/53 đậu.
5. **Dọn dẹp khi đóng** (`superfreetts.py:680-723`, `process_pool.py:455-479`, `gui.py:406-431`): đóng executor, dừng cả tiến trình đang chạy lẫn chờ, hủy timer dọn dẹp; hook `profile_will_close`/`profile_did_open` đã đấu dây; cấu hình engine hoãn lại được áp khi pool rảnh qua `apply_deferred_engine_pools` (`tts_orchestrator.py:374`, gọi ở `batch_orchestrator.py:497,537`, có kiểm thử `tests/test_ram_aware_concurrency.py:307-326`); giới hạn EdgeTTS = 3 (`batch_constants.py:44`, ép ở `service_edgetts.py:313`, `tts_orchestrator.py:274-285`). Kiểm thử shutdown/pool 25/25 đậu.

## 7. Còn lại / cần quyết định

Những việc sau cần người dùng phê duyệt rõ ràng, không được tự ý làm:

1. **Gắn thẻ git** — repo đặt tên thẻ trơn không có tiền tố `v` (`26.10.2`, `26.10.1`, …), nên lệnh đúng là `git tag -a 26.10.3 -m "Release 26.10.3"` và `git push origin 26.10.3`. **Đã được duyệt và thực hiện — xem §8.**
2. **Commit/đẩy báo cáo này** (`AI_Documents/bao-cao-kiem-toan-cuoi-2026-10-24.md`). **Đã được duyệt và thực hiện — xem §8.** File `AI_Documents/bao-cao-hieu-nang-2026-10-24.md` (báo cáo hiệu năng có từ trước) vẫn để nguyên chưa theo dõi, không đưa vào commit này.
3. **Xuất bản gói** ở bất cứ đâu (GitHub release, AnkiWeb, link chia sẻ) — **vẫn chưa làm**, cần anh/chị tự đăng. Khi đăng phải kèm sha256 và số byte để người dùng đối chiếu: `f96e524bcdafaa02a038812a2e4fd3034aa8724021faa049e74b82ab9c548aa3`, 2.281.489 byte.
4. **Mọi sửa mã nguồn** (không có, vì không blocker): nếu có sẽ chỉ là đề xuất + phác thảo sửa + cổng ảnh hưởng + có cần bump 26.10.4 không.
5. **Ghi đè `SuperFreeTTS.ankiaddon`** là thao tác ghi duy nhất được phép trong đợt này (đã làm). Ngoài `dist/audit/` và báo cáo này, không ghi gì khác.

Nợ kỹ thuật không chặn cho bản sau: 43 vị trí B110 (bắt đầu từ `process_pool.py`), tách nhỏ `draw_service_options` và `_execute_unique_tasks_unified`, kiểm thử cho module giao diện, dọn 232 khóa i18n thừa, bổ sung dịch ko/sv/ja/zh.

Không bump version, không sửa mã nguồn, không đổi gói trong lần kiểm toán này. Việc commit báo cáo, push nhánh và gắn thẻ `26.10.3` được thực hiện sau khi kiểm toán PASS và sau bước review độc lập, theo phê duyệt của người dùng (xem §8).

## 8. Nhật ký ship (24-10-2026, 21:14–21:16 +07)

Thực hiện sau khi kiểm toán PASS và review độc lập kết luận `APPROVE-WITH-NITS` (5 điểm minor + nit trong báo cáo đã sửa, không có critical/major, không đụng tới mã nguồn hay gói).

| Việc | Kết quả |
|---|---|
| Commit báo cáo | `850436a` — "docs: final audit report for 26.10.3 (PASS, 18/18 gates)" |
| Push nhánh | `fix/resource-management` → `origin`, `55089d3..850436a`, remote HEAD = `850436a` |
| Thẻ phát hành | `26.10.3` (annotated, "Release 26.10.3") trỏ vào commit `55089d3` — đúng commit "release: 26.10.3" |
| Push thẻ | remote `refs/tags/26.10.3` = `172859d8e847e8bdedb3a5d05f0dc69e4c3e329d`, deref = `55089d3882e3ab6a3929dfecff2150d0b97e51f5` |
| Gói phát hành | `SuperFreeTTS.ankiaddon`, 2.281.489 byte, sha256 `f96e524bcdafaa02a038812a2e4fd3034aa8724021faa049e74b82ab9c548aa3` |
| Còn lại | Chỉ còn việc đăng gói lên nơi phát hành (AnkiWeb/GitHub release) — người dùng tự làm, kèm sha256 và số byte ở trên. |
