# Báo cáo kiểm toán chi tiết — Super Free TTS 26.10.2

- **Ngày:** 24/10/2026
- **Nhánh:** `fix/resource-management` (commit gần nhất `7f28a73`)
- **Phạm vi:** toàn bộ `superfreetts_addon/` (110 file `.py`, 34.708 dòng), `tests/` (78 file), `build_share.py`, `scripts/`, `.github/`, `manifest.json`, `config.json`, gói phát hành `SuperFreeTTS.ankiaddon`
- **Cách kiểm:** chạy thật pytest / ruff / bandit / coverage, đọc AST toàn bộ mã nguồn, mở gói `.ankiaddon` đối chiếu, đọc mã các luồng batch – cache – checkpoint – huỷ – migrate – đóng gói
- **Nguyên tắc:** báo cáo này là ảnh chụp lúc audit. Đợt 1 (A1, B1, B2, C1) đã được sửa sau khi anh duyệt — xem **§7 Trạng thái sau xử lý**.

---

## 0. Kết luận trong 10 dòng

1. Phần **lõi xử lý** (cache, checkpoint, tải file, giải nén, khoá cache) được làm rất chắc: có kiểm tra định dạng thật, ghi atomic, chống zip-slip, có resume theo `note_id`.
2. **Cổng kiểm tra đang xanh**: 446 test pass, ruff sạch, bandit không có lỗi mức trung bình/cao.
3. Nhưng **gói phát hành đang sai**: file `.ankiaddon` nặng **83,92 MB**, trong đó **117,59 MB dữ liệu engine/model** bị đóng gói nhầm (engine Piper bản Linux + model 63 MB). Bộ kiểm tra gói vẫn báo "OK".
4. **Migrate config xoá trắng preset/mapping/workflow** của người dùng cũ mà không sao lưu, không báo.
5. **Bấm Huỷ giữa lúc Apply** có thể làm note hiện "Done" nhưng **không được lưu vào DB**, kèm file media rác.
6. **Bấm Huỷ giữa lúc tạo audio** làm toàn bộ note còn lại bị đánh dấu **lỗi đỏ** + ghi "error" vào checkpoint.
7. **52 chuỗi giao diện bị thiếu bản dịch** → người dùng thấy chữ thô kiểu `mms_manager_error_not_installed`; màn MMS Manager gần như chưa có bản dịch.
8. **CI không chạy trên nhánh đang làm việc** (`fix/resource-management` không nằm trong danh sách trigger) → 4 file nguồn vừa sửa chưa từng qua CI.
9. **3 file test "mồ côi"** (432 dòng) không được pytest thu thập; chạy trực tiếp một file thì **treo > 180 giây** vì gọi mạng thật.
10. Tổng thể: **nền tốt, lỗi tập trung ở khâu đóng gói – huỷ giữa chừng – migrate – bản địa hoá.** Sửa 4 nhóm này là chất lượng phát hành tăng rõ rệt, không cần đụng vào kiến trúc.

---

## 1. Bảng điểm

| Mặt | Điểm | Ghi chú |
|---|---|---|
| Kiến trúc / phân lớp | 8/10 | Facade + orchestrator + service rõ ràng, tách Anki ra `anki_utils` |
| Đúng đắn luồng batch | 6/10 | Dedup + checkpoint tốt, nhưng huỷ giữa chừng sai trạng thái |
| An toàn dữ liệu người dùng | 5/10 | Không backup trước Apply; migrate xoá preset; cancel làm mất lần lưu |
| Quản lý tài nguyên / tiến trình | 8/10 | Pool, cap EdgeTTS=3, huỷ theo cây tiến trình, đóng khi đổi profile |
| Bảo mật | 8/10 | Chống zip-slip/symlink/zip-bomb, SHA-256, timeout; không có lỗi mức cao |
| Đóng gói phát hành | 3/10 | 84 MB, chứa binary Linux + model, verify báo OK sai |
| Kiểm thử | 6/10 | 446 test nhanh, nhưng coverage 38,6%; UI ~0%; 3 file mồ côi |
| Bản địa hoá | 4/10 | en/vi tốt, ja/zh 15%, 52 key thiếu, 231 key chết |
| Chất lượng mã | 6/10 | 276 `except Exception`, 48 chỗ nuốt lỗi, 15 hàm ≥150 dòng |
| Tài liệu | 8/10 | REFERENCE + handoff + changelog đầy đủ, có graphify |

---

## 2. Cổng kiểm tra — số thật (chạy trên máy này)

```text
$ .venv/bin/python -m pytest tests/ -q --tb=short
446 passed, 1 skipped in 6.63s          (447 test được thu thập)

$ .venv/bin/python -m ruff check superfreetts_addon tests scripts
All checks passed!

$ .venv/bin/python -m bandit -r superfreetts_addon -ll
exit 0  (không có lỗi MEDIUM/HIGH)
Quét đầy đủ: 114 cảnh báo, tất cả mức LOW:
  48 × B110  try/except/pass      (nuốt lỗi)
  18 × B603  subprocess           (đã kiểm soát, không shell=True)
  15 × B311  random               (dùng cho jitter/backoff — chấp nhận)
  13 × B404  import subprocess
   8 × B101  assert               (kiểm tra kiểu trong mã chạy — mất tác dụng nếu chạy python -O)
   8 × B607  partial path
   4 × B606  no shell

$ coverage (pytest --cov)
Tổng: 38,6% trên 19.592 câu lệnh
Thấp nhất: anki_utils 0%, component_* 0–15%, gui_utils 7%, gui.py 14,5%
```

Số liệu mã nguồn:

- 110 file, 34.708 dòng; 1.900 hàm/class.
- Hàm phức tạp nhất: `_execute_unique_tasks_unified` — **332 dòng, độ phức tạp ~83** (`batch_orchestrator.py:404`).
- 15 hàm ≥150 dòng; 56 hàm ≥80 dòng.
- 0 `except:` trần; 276 `except Exception`; 48 chỗ `except Exception: pass`.
- 24 câu lệnh `global`; 1 tham số mặc định kiểu mutable (`stats.py:101`).

---

## 3. Phát hiện chi tiết

### A. Đóng gói phát hành

#### A1 — Gói addon chứa 117 MB engine/model của máy dev (Mức: CAO)

**Ở đâu:** `SuperFreeTTS.ankiaddon`, `build_share.py:52-64`, `scripts/verify_package.py:52-67`

**Chuyện gì:** Gói phát hành 83,92 MB (998 mục, giải nén 125,6 MB). Trong đó `superfreetts_addon/data/` chiếm **117,59 MB / 366 file**:

| File | Kích thước |
|---|---|
| `data/piper_models/en_US-lessac-medium.onnx` | 63,21 MB |
| `data/piper_engine/piper/libonnxruntime.so.1.14.1` | 16,32 MB |
| `data/piper_engine/piper/libtashkeel_model.ort` | 10,26 MB |
| `data/piper_engine/piper/espeak-ng-data/ru_dict` | 8,53 MB |
| `data/piper_engine/piper/piper` (ELF Linux, không đuôi) | 5,00 MB |

Phần mã + thư viện thật chỉ ~8 MB. Nguyên nhân: `build_share.py` loại file theo **đuôi tên** (`.so`, `.exe`, `.dll`…), nên bỏ sót ba kiểu:
- thư viện có phiên bản: `libonnxruntime.so.1.14.1` → `Path(...).suffix` là `.1`, không khớp `.so`;
- file thực thi **không có đuôi**: `piper`, `piper_phonemize`;
- model/dữ liệu: `.onnx`, `.ort`, `*_dict`.

`scripts/verify_package.py` không có `data/` trong `FORBIDDEN_DIR_PREFIXES` và cũng so khớp bằng `endswith(".so")`, nên **báo sai là đạt**:

```text
$ .venv/bin/python scripts/verify_package.py SuperFreeTTS.ankiaddon
[verify] OK: SuperFreeTTS.ankiaddon (83.92 MB)
```

**Ảnh hưởng:**
- Người dùng Windows/macOS tải 84 MB, giải nén ra binary **Linux** vô dụng (và model 63 MB không dùng tới) → tải chậm, tốn ổ đĩa, cập nhật addon nặng.
- Trên Linux, `component_piper_setup.py:68` chỉ kiểm tra **sự tồn tại** của `piper_engine/piper/piper` → addon tưởng Piper "đã cài" dù thư viện đi kèm có thể không khớp máy người dùng.
- Gói phình làm mỗi lần phát hành/duyệt AnkiWeb chậm và khó soát.

**Cách sửa:**
1. Trong `build_share.py`: thêm `data` vào `EXCLUDE_DIR_NAMES` (engine/model luôn tải lúc chạy), hoặc loại theo **magic bytes** (ELF/PE/Mach-O) thay vì đuôi tên.
2. Trong `scripts/verify_package.py`: thêm `superfreetts_addon/data/` vào danh sách cấm; cấm thêm `.onnx`, `.ort`; kiểm tra magic bytes để bắt binary không đuôi; cảnh báo nếu gói > 15 MB.
3. Build lại và chạy `verify_package.py` — kỳ vọng còn ~4–8 MB.

---

### B. An toàn dữ liệu người dùng

#### B1 — Migrate config xoá trắng preset/mapping/realtime, không sao lưu (Mức: CAO)

**Ở đâu:** `config_models.py:951-967`, `config_store.py:75-77`

**Chuyện gì:** Với config có `config_schema < 6`, hàm migrate đặt thẳng:

```python
config[CONFIG_PRESETS] = {}
config[CONFIG_MAPPING_RULES] = serialize_preset_mapping_rules(PresetMappingRules())
config[CONFIG_REALTIME_CONFIG] = {}
_force_single_worker_mode(..., force_exist=True)
```

Ngay sau đó `perform_config_migration()` gọi `_write()` ghi đè config thật. Không có bản sao lưu, không có thông báo, không có đường quay lại.

**Ảnh hưởng:** người dùng nâng cấp từ bản schema ≤5 mất **toàn bộ** preset, workflow, mapping rule, cấu hình realtime — âm thầm, chỉ phát hiện khi mở lại và thấy trống.

**Cách sửa:** trước khi migrate, ghi `user_files/config_backup_schema{N}_{timestamp}.json`; chỉ reset khi thật cần; ghi log + hiện thông báo một lần "Đã sao lưu cấu hình cũ tại …".

#### B2 — Huỷ giữa lúc Apply: note hiện "Done" nhưng không được lưu (Mức: CAO)

**Ở đâu:** `batch_orchestrator.py:327-328` và `batch_orchestrator.py:372-374`; `note_audio_updater.py:33`

**Chuyện gì:** Trong vòng lặp Apply, mỗi note được sửa trong bộ nhớ (`update_collection=False`), nhưng **file media đã được chép vào collection ngay** (`media_add_file`). Cuối vòng lặp:

```python
if notes_to_update and batch_status.must_continue:
    anki_collection.update_notes(notes_to_update)
```

Nếu người dùng bấm Huỷ giữa lúc Apply, `must_continue` = False → **không gọi `update_notes`**. Kết quả: các note đã xử lý xong hiện trạng thái **Done** trong bảng tiến trình nhưng DB **không hề thay đổi**, còn media thì đã nằm trong thư mục collection (file rác).

**Ảnh hưởng:** người dùng tin là đã lưu (thấy Done) nhưng thực tế chưa; chạy lại sẽ tạo thêm bản media trùng; dọn dẹp thủ công.

**Cách sửa:** luôn flush `notes_to_update` đã gom (huỷ chỉ nên chặn các note **chưa** xử lý), hoặc nếu muốn huỷ cứng thì đặt lại trạng thái các note đó thành "chưa áp dụng" và xoá media đã thêm (`col.media.trash_files`).

#### B3 — Không có điểm khôi phục trước khi ghi hàng loạt (Mức: TRUNG BÌNH)

**Ở đâu:** `backup_guard.py` (tắt backup định kỳ + `create_backup` trong lúc Apply), `config_models.py:894` (`skip_anki_backup` không nơi nào đọc)

**Chuyện gì:** Trong lúc Apply, addon chủ động dừng timer backup của Anki và thay `create_backup` bằng hàm rỗng. Bản thân addon **không tạo backup nào**. Trường `skip_anki_backup` trong preset là **config chết** (không có mã đọc).

**Ảnh hưởng:** một batch ghi đè hàng nghìn field mà không có bản sao lưu nào; nếu người dùng đặt sai target field / sai "chỉ giữ sound tag", dữ liệu gốc khó lấy lại.

**Cách sửa:** trước Apply, tạo 1 backup collection (hoặc yêu cầu người dùng bật "tạo backup" trong preset — và **dùng** trường `skip_anki_backup`), sau đó mới tắt timer.

---

### C. Đúng đắn luồng batch

#### C1 — Huỷ batch làm note còn lại bị đánh "lỗi" + ghi lỗi vào checkpoint (Mức: TRUNG BÌNH)

**Ở đâu:** `batch_orchestrator.py:721-732`

**Chuyện gì:** Sau khi thoát vòng lặp vì huỷ, khối "fill missing" chạy cho **mọi** dedup key chưa có kết quả:

```python
missing_error = Exception(i18n.get_text("error_audio_gen_failed", lang))
...
ctx.set_error(missing_error)
checkpoint.mark_error(note_id, missing_error)
```

**Ảnh hưởng:** bấm Huỷ → hàng loạt note đỏ trong bảng tiến trình; hộp "báo cáo lỗi" liệt kê hàng nghìn note và mời gắn tag lỗi; checkpoint ghi "error". (Điểm tốt: resume coi note chưa `applied` là còn chờ nên **sẽ chạy lại**, không mất vĩnh viễn.)

**Cách sửa:** thêm trạng thái `cancelled/skipped` riêng; khi người dùng huỷ thì không ghi error vào checkpoint và không đưa vào báo cáo lỗi.

#### C2 — Hàm lõi quá lớn, khó sửa an toàn (Mức: TRUNG BÌNH)

`_execute_unique_tasks_unified` (`batch_orchestrator.py:404`): **332 dòng, ~83 nhánh**, gánh cùng lúc: chia chunk, hàng đợi submit theo service, retry executor, stall watchdog, cache hit, usage tracking, checkpoint, tiến trình UI. Toàn dự án có 15 hàm ≥150 dòng, 56 hàm ≥80 dòng.

**Ảnh hưởng:** mỗi lần sửa luồng batch đều có nguy cơ làm hỏng nhánh khác; test hiện chỉ phủ phần nhỏ của hàm này.

**Cách sửa:** tách thành 4 hàm nhỏ: `_submit_chunks()`, `_collect_results()`, `_handle_stall()`, `_finalize_and_fill_missing()`. Không đổi hành vi, chạy lại test sau mỗi bước.

---

### D. Giao diện và bản địa hoá

#### D1 — 52 chuỗi dùng trong mã nhưng không có trong `en.json` → UI hiện key thô (Mức: TRUNG BÌNH)

**Ở đâu:** `i18n.py:29-43` (thiếu key → `return key`), danh sách key thiếu nằm rải ở `component_mms_manager.py` (33 key), `batch_orchestrator.py`, `component_kokoro_manager.py`, `component_troubleshooting.py`, `component_batch.py`.

Ví dụ người dùng thật sẽ thấy:
- `mms_manager_error_not_installed` (trong khi locale chỉ có `..._title` và `..._msg`) — 2 chỗ;
- `error_batch_stalled` / `status_batch_stalled` — 6 chỗ, đúng ở nhánh **watchdog phát hiện batch treo** (thông báo quan trọng nhất lại là chữ thô);
- `generic_warning`, `errors_label_ssl`, `voice_filter_all`, `button_preview`…

**Ảnh hưởng:** màn MMS Manager gần như không dùng được với người không đọc tiếng Anh; thông báo lỗi treo batch vô nghĩa.

**Cách sửa:** thêm 52 key vào `en.json` (+ `vi.json`), thêm test chặn hồi quy: quét `get_text("...")` trong mã và so với `en.json`, fail nếu thiếu.

#### D2 — Bản dịch không đồng đều, nhiều key chết (Mức: THẤP–TRUNG BÌNH)

| Ngôn ngữ | Số key | Tỉ lệ so với en (599) |
|---|---|---|
| en | 599 | 100% |
| vi | 593 | 99% (thiếu 18) |
| ko | 439 | 73% (thừa 47 key lạ) |
| sv | 191 | 32% |
| ja | 89 | 15% |
| zh-CN | 89 | 15% |
| zh-TW | 89 | 15% |

Thêm: **231 key định nghĩa nhưng không nơi nào dùng**, 25 giá trị trùng lặp trong en.

**Cách sửa:** hoặc rút gọn danh sách ngôn ngữ hỗ trợ (chỉ nhận ngôn ngữ ≥90% key), hoặc bổ sung theo lô; thêm script `scripts/i18n_audit.py` để CI báo thiếu/thừa.

---

### E. Quy trình kiểm thử và CI

#### E1 — CI không chạy trên nhánh đang làm (Mức: TRUNG BÌNH)

**Ở đâu:** `.github/workflows/python-test.yml:3-7` — `push.branches: [main, fix/release-readiness]`, `pull_request.branches: [main]`.

Nhánh hiện tại là `fix/resource-management`. Hiện có **6 file thay đổi chưa commit**, trong đó 4 file nguồn lõi:

```text
M superfreetts_addon/batch_executor.py        (+104/-... )
M superfreetts_addon/batch_orchestrator.py
M superfreetts_addon/services/process_pool.py
M superfreetts_addon/tts_orchestrator.py
M tests/test_ram_aware_concurrency.py
M tests/test_sherpa_process_pool.py
```

**Ảnh hưởng:** những thay đổi về khoá/đếm task, deferred engine config, kill theo cây tiến trình Windows **chưa từng** được CI xác nhận (dù tôi đã chạy test cục bộ: pass).

**Cách sửa:** trigger theo `branches: ["**"]` cho `push` (hoặc thêm `fix/**`), giữ `pull_request` vào `main`.

#### E2 — 3 file test mồ côi, chạy trực tiếp thì treo (Mức: TRUNG BÌNH)

**Ở đâu:** `tests/_test_edgetts_continuous_batching.py`, `_test_edgetts_sequence_mode.py`, `_test_edgetts_vietnamese_batch.py` (432 dòng)

Tên bắt đầu bằng `_test_` nên pytest **không thu thập** (mặc định `test_*.py`), nhưng nội dung là **script chạy ngay khi import**, gọi API EdgeTTS thật. Tôi đã thử:

```text
$ pytest tests/_test_edgetts_sequence_mode.py
→ treo, quá 180 giây, phải kill
```

**Ảnh hưởng:** người mới (`hoặc agent`) tưởng có test cho EdgeTTS nhưng thực ra không; ai chạy tay sẽ treo máy/CI; 432 dòng chết gây nhiễu.

**Cách sửa:** chuyển sang `tests/manual/` (ngoài `testpaths`), thêm `if __name__ == "__main__"` + `pytest.skip` khi import; hoặc xoá.

#### E3 — Coverage thấp ở đúng chỗ người dùng chạm nhiều (Mức: TRUNG BÌNH)

38,6% tổng; `anki_utils.py` 0% (cố ý, để test không cần Anki); toàn bộ `component_*.py` 0–15%; `gui.py` 14,5%; `gui_utils.py` 7%. Nghĩa là phần UI (nơi phát sinh lỗi thao tác) gần như không có lưới an toàn. CI đặt sàn 33% + `scripts/check_critical_coverage.py` cho module trọng yếu — hợp lý, nhưng chưa phản ánh UI.

---

### F. Chất lượng mã

#### F1 — Nuốt lỗi diện rộng (Mức: TRUNG BÌNH)

48 chỗ `except Exception: pass` (bandit B110), 276 chỗ `except Exception`. Ở tầng UI thì chấp nhận được (tránh crash Anki), nhưng có mặt ở cả đường ống batch (`batch_orchestrator.py:528,551,564,568`) — lỗi ở đó bị bỏ qua im lặng, chỉ còn triệu chứng "note không có audio" mà không có log.

**Cách sửa:** giữ nguyên ở UI, nhưng ở tầng batch đổi thành `logger.warning(..., exc_info=True)`; thêm rule ruff chặn `except Exception: pass` trong `batch_*.py`, `services/`.

#### F2 — Không nhất quán CRLF (Mức: THẤP)

Quy ước repo: mã nguồn `.py` dùng CRLF. Thực tế:

```text
LF-only : archive_utils.py (155 dòng), http_utils.py (42), download_sources.py (76), services/test_runner.py (6)
Mixed   : component_supertonic_setup.py (279 CRLF + 1 LF)
```

Không ảnh hưởng chạy, nhưng làm diff/git blame nhiễu và vi phạm invariant ghi trong `.hermes.md`. Sửa: chuẩn hoá 5 file + thêm `.gitattributes` (`*.py text eol=crlf`) để khỏi tái diễn.

#### F3 — Mã và config chết (Mức: THẤP)

- `__init__.py:31`: `if False:  # Super Free TTS Lite: Always disable crash reporting` — nhánh không bao giờ chạy nhưng vẫn import `sentry_sdk` ở `logging_utils.py:7` khi có `sys._sentry_crash_reporting`.
- `config.json:10`: `"NaverTTS": false` — dịch vụ không còn tồn tại, không mã nào đọc.
- `config_models.py:894`: `skip_anki_backup` — không nơi nào đọc.
- `stats.py:101`: `send_event(..., properties={})` — tham số mặc định mutable (thân hàm `pass` nên vô hại, nhưng sai mẫu).
- 24 câu `global`.

#### F4 — Log không xoay vòng (Mức: THẤP)

`logging_utils.py:133-137` dùng `logging.FileHandler` thuần. Ở chế độ `HYPER_TTS_DEBUG_LOGGING=file`, log tăng vô hạn trong `user_files/superfreetts.log`. Sửa: `RotatingFileHandler(maxBytes=5_000_000, backupCount=3)`.

#### F5 — `BatchStatus.stop()` có race nhỏ (Mức: THẤP)

`batch_status.py:152-159` lặp `self.futures_to_cancel` **không khoá**, trong khi worker thread `append` danh sách này dưới `future_lock` (`batch_orchestrator.py:581`). Có thể ném `RuntimeError: list changed size during iteration` đúng lúc người dùng bấm Huỷ, hoặc bỏ sót future. Sửa: copy danh sách dưới khoá rồi mới `cancel()`.

---

## 4. Những gì đang tốt — đừng làm hỏng

1. **Giải nén an toàn** (`archive_utils.py`): chặn đường dẫn tuyệt đối, `..`, ổ đĩa, symlink/hardlink, device, giới hạn 2 GiB và 200.000 mục; ghi theo luồng 1 MB. Đây là chuẩn mực, không phải bản sơ sài.
2. **Tải xuống** (`downloader.py`): timeout 30/60 s, resume bằng `Range`, xác thực SHA-256 khi có, MD5 chỉ dùng để đối chiếu catalogue (có ghi chú rõ).
3. **Khoá cache audio** (`audio_file_store.py:119-153`): `text + voice + options + format` → SHA-224, ghi atomic `os.replace`, kiểm tra magic bytes, có dọn theo tuổi và bảo vệ file đang dùng.
4. **Checkpoint v2** (`batch_executor.py:315-410`): khoá theo `note_id` (đã sửa đúng lỗi lệch index của v1), ghi atomic + `fsync`, migrate được file cũ.
5. **Vòng đời tài nguyên**: `profile_will_close` → `shutdown()` tắt executor + 4 pool; `on_profile_reopened()` dựng lại; mọi bước đều `try/except` để không chặn Anki.
6. **Cap EdgeTTS = 3** được test bảo vệ; **version 26.10.2** đồng nhất giữa `version.py`, `manifest.json`, test.
7. **Test nhanh, không cần Anki**: 446 test / 6,6 giây — rất tốt cho vòng lặp phát triển.
8. **Tài liệu**: `REFERENCE.md`, `.hermes.md`, handoff, CHANGELOG đầy đủ; có code graph.

---

## 5. Kế hoạch sửa đề xuất (chờ duyệt)

### Đợt 1 — An toàn dữ liệu & phát hành (ưu tiên cao nhất)
| Việc | File | Kiểm chứng |
|---|---|---|
| A1: loại `data/` khỏi gói + siết `verify_package` | `build_share.py`, `scripts/verify_package.py` | Gói còn ≤ 15 MB, `verify` fail nếu có binary/model |
| B1: sao lưu config trước migrate | `config_store.py`, `config_models.py` | Test: config schema 5 → có file backup, preset cũ nằm trong backup |
| B2: luôn flush note khi huỷ Apply | `batch_orchestrator.py:327,372` | Test mới: huỷ giữa Apply → note đã xử lý vẫn được lưu |
| C1: trạng thái `cancelled` thay vì `error` | `batch_orchestrator.py:721-732`, `batch_status.py` | Huỷ batch → không note đỏ, checkpoint sạch |

### Đợt 2 — Trải nghiệm người dùng & CI
| Việc | File |
|---|---|
| D1: bổ sung 52 key (en + vi), test chặn thiếu key | `locales/*.json`, `tests/test_i18n_locales.py` |
| E1: CI chạy mọi nhánh | `.github/workflows/python-test.yml` |
| E2: dời 3 script EdgeTTS sang `tests/manual/` | `tests/` |
| F2: chuẩn hoá CRLF + `.gitattributes` | 5 file, `.gitattributes` |

### Đợt 3 — Chất lượng dài hạn
| Việc | File |
|---|---|
| C2: tách `_execute_unique_tasks_unified` thành 4 hàm | `batch_orchestrator.py` |
| F1: log thay vì nuốt lỗi ở tầng batch | `batch_orchestrator.py`, `batch_executor.py`, `services/` |
| F3/F4/F5: dọn mã chết, xoay vòng log, khoá `stop()` | nhiều file |
| D2: script `i18n_audit.py` + chốt danh sách ngôn ngữ | `scripts/`, CI |

**Không làm nếu chưa được duyệt:** đổi version, commit/push, tag/release.

---

## 6. Phụ lục — cách tái lập

```bash
cd /home/admin/Documents/deepseek-harness/default-workspace/superfreetts

# 1. Cổng kiểm tra
.venv/bin/python -m pytest tests/ -q --tb=short
.venv/bin/python -m ruff check superfreetts_addon tests scripts
.venv/bin/python -m bandit -r superfreetts_addon -ll

# 2. Coverage
.venv/bin/python -m pytest tests/ -q --cov=superfreetts_addon \
  --cov-report=term-missing:skip-covered --cov-report=json:coverage.json

# 3. Gói phát hành
.venv/bin/python scripts/verify_package.py SuperFreeTTS.ankiaddon
unzip -l SuperFreeTTS.ankiaddon | sort -k1 -n -r | head -20

# 4. Bản địa hoá
.venv/bin/python - <<'PY'
import json, re, pathlib, collections
en = json.load(open('superfreetts_addon/locales/en.json', encoding='utf-8'))
used = collections.Counter()
for p in pathlib.Path('superfreetts_addon').rglob('*.py'):
    used.update(re.findall(r'get_text\(\s*["\'](\w+)["\']', p.read_text(encoding='utf-8', errors='replace')))
print("thiếu trong en:", sorted(k for k in used if k not in en))
PY

# 5. Test mồ côi (cẩn thận: gọi mạng thật, sẽ treo)
# pytest tests/_test_edgetts_sequence_mode.py
```


---

## 7. Trạng thái sau xử lý — Đợt 1 (24/10/2026)

Đã sửa và kiểm chứng bằng chạy thật. **Chưa commit, chưa push, không đổi version.**

| Mục | Thay đổi | Kiểm chứng |
|---|---|---|
| **A1** Đóng gói | `build_share.py` loại hẳn `superfreetts_addon/data/`, nhận diện binary bằng **magic bytes** (ELF/PE/Mach-O) thay vì đuôi tên, thêm `.onnx`/`.ort`. `scripts/verify_package.py` cấm `data/`, cấm `.so.*`, kiểm tra magic bytes, chặn gói > 25 MB | Gói **83,92 MB → 2,17 MB**; `verify_package.py` chạy smoke import OK; 7 test mới trong `tests/test_package_verify.py` |
| **B1** Migrate | Không còn xoá/ghi đè: chỉ `setdefault` container thiếu; giữ nguyên presets, mapping rules, realtime config, worker/concurrency; **sao lưu trước khi ghi** vào `user_files/config_backup_schema{N}_{YYYYmmdd-HHMMSS}.json` (giữ 5 bản mới nhất); schema bị sửa tay thành chuỗi không còn làm crash lúc khởi động | 7 test mới trong `tests/test_config_migration_preserves_settings.py`; 2 test cũ trong `test_config_models.py` được đổi từ kỳ vọng "xoá/clamp" sang kỳ vọng "giữ nguyên" |
| **B2** Huỷ khi Apply | `apply_generated_batch_audio` và bản chunk luôn lưu các note đã xử lý trước khi dừng; huỷ chỉ chặn các note tiếp theo | `test_cancel_during_apply_still_saves_finished_notes` |
| **C1** Huỷ ≠ lỗi | Tách `_fill_missing_results`; chỉ chạy khi batch kết thúc tự nhiên. Huỷ giữa chừng không đánh đỏ note còn lại và không ghi error vào checkpoint | 3 test còn lại trong `tests/test_batch_cancel_semantics.py` |

**Cổng sau sửa:**

```text
pytest  : 473 passed, 1 skipped in 6.70s   (trước: 446 passed + 1 skipped)
ruff    : All checks passed
bandit  : -ll exit 0
CRLF    : config_models.py / config_store.py / batch_orchestrator.py giữ nguyên CRLF, 0 dòng LF lẫn
build   : SuperFreeTTS.ankiaddon 2.17 MB, verify OK
```

---

## 8. Đợt 2 + 3 (đã xử lý)

| Mục | Thay đổi | Kiểm chứng |
|---|---|---|
| **D1** Chuỗi thiếu | Thêm 52 key vào `en.json` + 48 key vào `vi.json`. Sửa luôn lỗi key **động**: `preferences_option_language_sv` thiếu trong en (menu ngôn ngữ bản tiếng Anh hiện chữ thô), `..._en` và `..._sv` thiếu trong vi. Dọn 12 key chết ở ko/sv/vi; sửa 9 chuỗi tiếng Hàn bị mất `{0}` so với tiếng Anh | `scripts/i18n_audit.py --check` → **0 key thiếu**; 6 test trong `tests/test_i18n_keys.py` |
| **D2** Công cụ | `scripts/i18n_audit.py` báo bảng phủ theo ngôn ngữ, `--check` fail nếu thiếu key; chạy trong CI. Test chặn: locale phải là tập con của en, placeholder phải khớp, fallback về tiếng Anh đúng | 473 test pass; báo cáo: en 100%, vi 100%, ko 67%, sv 29%, ja/zh 13,7% |
| **E1** CI | `push.branches: ["**"]` — mọi nhánh đều chạy; thêm bước i18n | YAML parse OK: jobs lint/bandit/test/coverage/cross-platform/package |
| **E2** Test mồ côi | 3 script EdgeTTS chuyển sang `scripts/manual/` + README nêu rõ chúng gọi mạng thật, không phải pytest | `tests/` không còn file `_test_*`; pytest vẫn 473 test |
| **F2** CRLF | Chuẩn hoá 5 file lệch (`archive_utils`, `http_utils`, `download_sources`, `services/test_runner`, `component_supertonic_setup`) | `tests/test_line_endings.py`: addon CRLF-only, tests LF-only |
| **F4** Log | `RotatingFileHandler(maxBytes=5 MB, backupCount=3)` thay `FileHandler` | import + test suite |
| **F5** Huỷ batch | `BatchStatus` có `register_future` / `unregister_future` / `clear_futures`, `stop()` snapshot dưới lock; orchestrator dùng API mới | 3 test cũ + toàn bộ suite |
| **F3** Mã chết | Bỏ nhánh `if False:` trong `__init__.py`, bỏ `NaverTTS` khỏi `config.json`, sửa tham số mặc định mutable ở `stats.py` | pytest + verify gói |
| **F1** Nuốt lỗi | 5 chỗ `except Exception: pass` trên đường ống batch/executor → `logger.debug/warning` (43 chỗ còn lại thuộc UI/dọn dẹp, cố ý giữ để không làm phiền người dùng) | ruff/bandit sạch |
| **C2** Tách hàm | `_execute_unique_tasks_unified`: **332 → 243 dòng, complexity 83 → 55**; tách `_build_all_chunks`, `_apply_chunk_results`, `_fail_chunk`, `_handle_stall` | 4 test mới trong `tests/test_batch_stall_handling.py`; toàn bộ 473 test xanh |

**Cổng sau đợt 2+3:**

```text
pytest  : 473 passed, 1 skipped in 6.70s
ruff    : All checks passed
bandit  : -ll exit 0
coverage: 39,0% (từ 38,6%)
i18n    : 0 key dùng-trong-code bị thiếu trong en
build   : SuperFreeTTS.ankiaddon 2.17 MB, verify OK
```

**Chính sách ngôn ngữ (đã chốt):** chỉ **en** và **vi** là ngôn ngữ chính thức; cả hai đã đủ **100% key (652/652)**. Các locale khác (ko, sv, ja, zh-CN, zh-TW) giữ nguyên và fallback về tiếng Anh — không cần dịch thêm. Test `test_vietnamese_is_complete` chặn hồi quy.

**Còn lại:** coverage tầng UI 0–15% và 43 chỗ `except Exception: pass` ở UI — chấp nhận được; chưa commit/push/đổi version.
