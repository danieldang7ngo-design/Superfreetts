# Báo cáo sản phẩm toàn diện — SuperFreeTTS 26.10.2 (bản sửa sau review 2026-10-24)

> Ngày: 2026-10-24 · Nhánh: `fix/resource-management` (working tree chưa commit: 6 file sửa + 3 file mới) · Phiên bản: 26.10.2 · Người đọc mục tiêu: người không chuyên kỹ thuật (thuật ngữ khó có giải thích trong ngoặc) · Mọi con số đều từ lệnh chạy thật (xem §8), không ước đoán.
> Bản này viết lại toàn bộ sau review độc lập: sửa nguyên nhân gốc F01, loại finding ma F17 (OGG), bám đúng 20 khía cạnh A01–A20 của plan, thêm cột score cho mọi finding.
> Lưu ý: `USER_FEEDBACK.md` là file kịch bản test tổng hợp để thử agent (không phải phản ánh người dùng thật) — F01 đọc theo khung đó, xem D2.

---

## 0. Cách đọc báo cáo

- **Severity (4 mức, kèm bằng chứng file:line):** **critical** = mất/hỏng dữ liệu người dùng, hoặc tính năng chính sai một cách âm thầm (ví dụ: batch ra sai giọng như kịch bản test `USER_FEEDBACK.md`, ghi note không undo); **major** = người dùng thường gặp, có cách vòng quanh nhưng tốn công, hoặc chặn phát hành (ví dụ: i18n ja/zh chỉ 15%, 3 file test không được chạy); **minor** = chỉ ảnh hưởng nhóm nhỏ/khó gặp, gây khó chịu (ví dụ: log phình, dead code); **nit** = vệ sinh code/tài liệu (ví dụ: key config ma, chuỗi chết).
- **Score = Impact(1–5) × Likelihood(1–5) / Effort(1–5)** (Effort 1 = ≤2 giờ, 5 = ≥3 ngày). **P0:** critical hoặc Score ≥ 15 (hoặc plan §5 chỉ định đích danh). **P1:** major và 8 ≤ Score < 15 (hoặc plan §5 chỉ định). **P2:** còn lại.
- **Deviations (lệch plan, nêu rõ lý do):** D1 — F03 (score 6) và F06 (score 3,75), F07 (2,5), F08 (4) có score dưới ngưỡng nhưng vẫn xếp P0/P1 vì plan §5 chỉ định đích danh (F04, F07, F08) hoặc vì ảnh hưởng trực tiếp tới người dùng (F03, F06). D2 — F01 từng là critical khi bug còn sống; code sửa đã commit (f65934a) + test hồi quy pass. `USER_FEEDBACK.md` là file kịch bản test (không phải phản ánh thật) nên Likelihood 3→1, Score 15→5, F01 chuyển P0→P2 (việc hồi quy R21, không chặn release).
- **Quy ước "đã đo / chưa đo":** số nào có lệnh ở §8.1 là "đã đo"; suy luận từ đọc code ghi "(đọc code)"; ước lượng ghi "(ước tính)". Không đo trên Windows/macOS thật, không telemetry, không đọc nội dung `meta.json`/`user_files/` (chỉ `du`/`ls`).

---

## 1. Tóm tắt điều hành

### 1.1 Sản phẩm đang ở đâu (5 câu, không jargon)

1. SuperFreeTTS là tiện ích miễn phí cho phần mềm học từ vựng Anki: tự động đọc to từ vựng và gắn file âm thanh vào thẻ học (giọng lấy từ dịch vụ online miễn phí như EdgeTTS/Google và từ "máy đọc" chạy ngay trên máy như Piper/Kokoro).
2. Sức khỏe hiện tại: test suite **XANH** — 446 passed, 1 skipped / 447 test (6,7 giây); kiểm tra phong cách code (Ruff) sạch; kiểm tra bảo mật (Bandit `-ll`) 0 issue (lưu ý: `-ll` ẩn 114 issue LOW — xem §2.2).
3. Độ bao phủ test toàn dự án **39%** (ngưỡng chặn 33%): đủ sàn nhưng mỏng đúng 2 file từng chứa bug giọng đọc — `batch_orchestrator.py` 42%, `audio_generator.py` 50% (không phải "tập trung đúng chỗ hiểm" như bản trước đã viết).
4. Kịch bản test `USER_FEEDBACK.md` (batch ra từng "khối" cùng giọng — file test tổng hợp, không phải phản ánh thật) mô tả đúng bug cũ đã **có code sửa được commit (f65934a) kèm test hồi quy pass** — còn lại 1 việc kiểm thử hồi quy ở P2 (R21), không chặn release.
5. Khuyến nghị: làm xong 3 việc P0 (chặn rule default trùng, cứu 3 file test mồ côi, sửa CI cho nhánh đang làm) rồi mới đóng gói phát hành; P1/P2 để các bản sau.

### 1.2 Top 7 việc phải làm ngay (có score)

| # | ID | Việc (1 dòng) | Sev | Score | Đợt |
|---|---|---|---|---|---|
| 1 | F02 | Mapping rules: 2 rule `is_default` cùng deck+notetype → rule đầu thắng âm thầm, không cảnh báo | major | 4×4/1 = **16** | P0-R2 |
| 2 | F05 | CI chưa từng chạy trên nhánh `fix/resource-management` (chỉ phủ `main`, `fix/release-readiness`) | major | 3×5/1 = **15** | P0-R4 |
| 3 | F04 | 3 file `tests/_test_edgetts_*.py` không được pytest thu thập (tên file sai quy ước) | major | 3×5/2 = 7,5 (plan §5 chỉ định P0, xem D1) | P0-R3 |
| 4 | F03 | Rule trỏ tới deck/notetype đã xóa: không validate, không UI sửa chữa | major | 3×4/2 = 6 (nâng P1, xem D1) | P1-R8 |
| 5 | F06 | i18n ja/zh-CN/zh-TW chỉ 89/599 key (15%), rớt về tiếng Anh | major | 3×5/4 = 3,75 (giữ P1, xem D1) | P1-R5 |
| 6 | F08 | Coverage lõi mỏng: `anki_utils.py` 0%, `component_voiceselection.py` 7% | major | 4×3/3 = 4 (plan §5 chỉ định P1, xem D1) | P1-R7 |
| 7 | F07 | Gói `.ankiaddon` 88,0 MB (125,6 MB chưa nén), chứa 91 entry tests/dist-info | minor | 2×5/4 = 2,5 (plan §5 chỉ định P1, xem D1) | P1-R6 |

### 1.3 Ba việc KHÔNG nên làm (effort cao, impact thấp)

1. **Viết lại kiến trúc stylesheet `gui_utils.py` (2.602 dòng).** 7 hàm stylesheet dài 282–351 dòng nhưng hoạt động ổn định, không liên quan bug người dùng. Effort ≥3 ngày, impact ~0 → để P2 xa hoặc không làm.
2. **Tự host lại model Piper (63,2 MB) để giảm dung lượng gói.** Model là tài sản của project Piper (xem A16); tự host gây rủi ro license + hỏng đường tải có SHA-256 pin. Thay vào đó: loại entry thừa trong zip (R6).
3. **Bật lại OGG.** OGG đã nghỉ hưu có chủ đích ở 26.10 (không engine nào encode được — `component_preferences.py:14`, `release_notes.py:38`); bật lại là đi ngược quyết định sản phẩm.

---

## 2. Phương pháp & phạm vi

### 2.1 Trạng thái repo khi đo

- Nhánh `fix/resource-management`, HEAD `7f28a73`, version 26.10.2 (`manifest.json`: name "Super Free TTS", author "Phuc", ankiweb_id 351217314).
- Working tree chưa commit: **6 file sửa + 3 file mới** (`git status --short`): `M superfreetts_addon/batch_executor.py`, `batch_orchestrator.py`, `services/process_pool.py`, `tts_orchestrator.py`, `tests/test_ram_aware_concurrency.py`, `tests/test_sherpa_process_pool.py`; `?? .graphifyignore`, `.hermes.md`, `AI_Documents/bao-cao-san-pham-toan-dien-2026-10-24.md`.
- Source `.py` CRLF (4 file lệch: `archive_utils.py`, `download_sources.py`, `http_utils.py`, `services/test_runner.py`; không có `.gitattributes`).
- Fix bug giọng đọc (theo kịch bản test `USER_FEEDBACK.md`) đã commit: `f65934a` (00:19 24/10) + regression test `tests/test_batch_mixed_voice_chunk.py` (202 dòng, pass).

### 2.2 Lệnh đã chạy + thời lượng

| Lệnh | Kết quả | Thời lượng |
|---|---|---|
| `.venv/bin/python -m pytest tests/ -q -p no:randomly` | 446 passed, 1 skipped / 447 | 6,7s |
| `pytest --collect-only` | 447 collected | — |
| `ruff check superfreetts_addon tests scripts` | All checks passed | — |
| `bandit -ll -r superfreetts_addon` | 0 issue (nhưng `-ll` ẩn **114 LOW** — xem nit N3) | — |
| `pytest test_batch_mixed_voice_chunk.py` (test hồi quy F01) | pass | — |
| 6 file test lõi (checkpoint, undo, RAM, IPC, mixed-voice) | 67 passed | 0,8s |
| 5 file (shutdown, thread budget, batch flow, preview, config) | 53 passed | 0,2s |
| 6 file (cleanup, format, config defaults/models, service imports, version) | 62 passed | 0,3s |
| `scripts/vendor_deps.py --check` | exit 0 | — |
| `scripts/verify_package.py` (đọc zip có sẵn, không build) | OK 83,92 MiB | — |
| Repro F01 scratch (Sequence+Random+chunk+dedup, `audit_evidence/F01_repro.txt`) | PASS (chi tiết §3-A06) | — |
| Repro M7 mapping rules (`audit_evidence/M7_repro.txt`) | PASS (chi tiết §3-A02) | — |
| Coverage toàn dự án | TOTAL 39% (19592 stmt, floor 33 qua `check_critical_coverage.py`) | — |

### 2.3 Giới hạn (những gì KHÔNG đo được)

1. Không có Windows/macOS thật: SAPI, `say`, Piper binary, `taskkill` (commit `7f28a73`) chỉ kiểm bằng đọc code + CI matrix → mọi kết luận gắn nhãn "chưa xác minh runtime".
2. Không telemetry: tỉ lệ lỗi thật của user là suy luận từ code (`USER_FEEDBACK.md` là file test, không phải phản ánh thật).
3. Working tree bẩn (6 file): số đo có thể lệch bản release.
4. Scraping 6 từ điển: không gọi mạng thật trong audit.
5. Effort trong score là phỏng đoán của người audit, không phải cam kết.

---

## 3. Audit theo khía cạnh (A01–A20)

> Mỗi mục: Kết luận 1 câu → Bảng finding (ID/severity/score/bằng chứng/tác động 1 câu) → "Đã tốt".

### A01 — Kiến trúc & khả năng bảo trì

**Kết luận:** Facade + orchestrator rõ vai, nhưng còn nợ god-object (stylesheet) và 540 tham chiếu tên di sản `hypertts`.

| ID | Sev | Score | Bằng chứng file:line | Tác động người dùng (1 câu) | Cách kiểm chứng |
|---|---|---|---|---|---|
| F16 | minor | 2×4/4 = 2 | `gui_utils.py` 2.602 dòng (7 hàm stylesheet 282–351 dòng); 56 hàm ≥80 dòng; 7 file >800 dòng (2.602 `gui_utils.py`, 1.271 `release_notes.py` … 815 `component_batch_preview.py`); `component_voiceselection.py` 791 dòng; `grep -c hypertts` = 540; 4 file lệch CRLF, không `.gitattributes` | Code khó sửa, dễ gây bug khi thêm tính năng mới | Script AST đếm hàm ≥80; `wc -l`; `grep` |

**Đã tốt:** phân lớp rõ (GUI → facade `superfreetts.py` 777 dòng → orchestrator/executor → services); `component_services.py:draw_service_options` 286 dòng là UI vẽ options, không phải logic batch; import chéo layer chỉ 3 chỗ, trong đó 1 chỗ ngoài tầng UI (`editor_manager.py:211` import `component_choosepreset`), 2 chỗ trong nội bộ UI (`component_services.py:512`, `component_supertonic_setup.py:14`).

### A02 — Tích hợp note type & mapping rules (trọng tâm user)

**Kết luận:** Engine rule chạy đúng các case cơ bản (đã repro), nhưng có 2 lỗ hổng thật: default trùng thắng âm thầm và rule mồ côi không ai báo.

| ID | Sev | Score | Bằng chứng file:line | Tác động người dùng | Cách kiểm chứng |
|---|---|---|---|---|---|
| F02 | major | 4×4/1 = **16** | `config_models.py:798-805` (`get_default_preset_id` trả rule đầu, không cảnh báo khi 2 rule `is_default=True` cùng model+deck) | Đổi thứ tự rule làm đổi preset, không hiểu vì sao | Repro M7: 2 defaults → `p1` âm thầm |
| F03 | major | 3×4/2 = 6 → P1 (D1) | `config_models.py:758-773` (`rule_applies` trả False gọn, không lỗi); không có validate/repair UI (`component_presetmappingrules.py` 357 dòng không nhánh mồ côi) | Xóa deck/notetype xong preset "mất tích" khó hiểu | Repro M7: `model_id=999` → False, không crash nhưng cũng không báo |

Repro M7 (scratch, `mock_anki.mock_all()`, output thật): two defaults → `p1`; orphan → False; NoteType vs deck 5 → True (đúng chủ ý — NoteType bỏ qua deck); disabled → False; automatic-only ở chế độ manual → True (đúng thiết kế: chỉ lọc `automatic` khi `automated=True`); wrong deck → False.

**Đã tốt:** `rule_applies` phủ đủ 4 điều kiện (enabled, model, deck, automatic); `DeckNoteType` khớp `(model_id, deck_id)`; `editor_manager.py:72` đọc model từ collection có guard; serialize/deserialize round-trip có test (`test_config_models.py` pass).

### A03 — UX & luồng người dùng

**Kết luận:** Luồng batch có báo lỗi/hủy, nhưng first-run bắt user hiểu 3 khái niệm (preset/workflow/mapping rule) và code nuốt lỗi còn nhiều (276 `except Exception`).

| ID | Sev | Score | Bằng chứng file:line | Tác động người dùng | Cách kiểm chứng |
|---|---|---|---|---|---|
| F20 | minor | 2×4/2 = 4 | `grep -c 'except Exception'` = 276; `errors.py` 351 dòng; `gui.py:init` 245 dòng | Lỗi hiện chung chung, khó tự gỡ | `grep -rn 'except Exception' --include='*.py' \| wc -l`; đếm click first-run từ `gui.py:init` |

**Đã tốt:** batch có `BatchProgressUI` + phase DEDUPLICATING, checkpoint resume sau crash (`test_batch_preview_checkpoint.py` 8 test pass), `component_failure_report.py` cho user gửi lỗi.

### A04 — Độ tin cậy & phục hồi sau lỗi

**Kết luận:** Checkpoint resume đã tốt (test xanh cả ma trận kill 25/50/75%), rủi ro tồn dư duy nhất là F01 cần kiểm chứng runtime.

| ID | Sev | Score | Bằng chứng | Tác động | Kiểm chứng |
|---|---|---|---|---|---|
| (F01 bao phủ, không finding riêng) | — | — | `test_batch_checkpoint.py` 15 test + preview 8 test pass; `BatchCheckpoint` resume theo note_id | Crash giữa batch 5.000 thẻ vẫn resume đúng | `pytest tests/test_batch_checkpoint.py tests/test_batch_preview_checkpoint.py -q` |

**Đã tốt:** ghi atomic + flush theo nhịp (`CHECKPOINT_FLUSH_EVERY=50`, `batch_constants.py:91`); kill-resume 3 mức; stop/cancel có test dọn dẹp (`test_shutdown_cleanup.py` pass); 2 commit gần nhất (`7168f13`, `7f28a73`) gia cố pool teardown.

### A05 — Concurrency & tài nguyên

**Kết luận:** Không có finding mới — cap EdgeTTS=3 còn enforce, RAM budget đã đo thật, IPC có deadline; khác biệt duy nhất là working tree 6 file chưa qua CI (bao phủ bởi F05).

**Đã tốt:** `batch_constants.py:44` `EDGETTS_MAX_WORKERS=3` (test-enforced, immutable); `tts_orchestrator.py:18-26` ghi số đo thật Kokoro 3.933/4.662 MB tree, marginal 2.400 MB (đã sửa — bản trước gọi là "ước tính" là sai, xem m10); `test_ram_aware_concurrency.py` + `test_ipc_deadline.py` + `test_thread_budget.py` + `test_macos_concurrency_gate.py` đều pass.

### A06 — Hiệu năng & cache

**Kết luận:** Dedup key đúng (text+voice+format, đã repro), text cache có giới hạn 2048 entry; bug giọng đọc nằm ở tầng gọi service theo chunk (đã fix), không phải ở dedup.

| ID | Sev | Score | Bằng chứng file:line | Tác động người dùng | Cách kiểm chứng |
|---|---|---|---|---|---|
| F01 | major (đã fix, kịch bản test) | 5×1/1 = 5 → P2 (D2) | Root cause cũ: pre-f65934a `_generate_audio_batch_task` dùng voice của item đầu chunk cho cả chunk (`git show f65934a^:...superfreetts.py`); fix: group theo voice `_batch_task_voice_key` (vòng group `superfreetts.py:299-307`, helper `:374-391`); EdgeTTS chunk=3 (`batch_orchestrator.py:476`) → khối ~3 thẻ | Lỗi cũ: batch Sequence/Random ra khối sai giọng — khớp kịch bản test tổng hợp `USER_FEEDBACK.md` (không phải phản ánh thật); fix đã commit, test hồi quy pass | `F01_repro.txt` + `test_batch_mixed_voice_chunk.py` pass |

Repro F01 (output thật): prepare 6 note → F,M,F,M,F,M (explicit `sequence_index`, nhánh counter `audio_generator.py:88-90` không dùng); Random seeded → per-card; chunk hiện tại → 2 service call (3F+3M), mỗi item đúng voice; mô phỏng logic cũ → cả 6 item cùng voice đầu; dedup key cùng text khác voice → khác nhau, cùng voice → bằng nhau. Loại trừ: counter dùng chung (đường batch không đọc `_sequence_runtime_index`), dedup gộp sai voice (key đã chứa voice), `_voice_with_options` memoize (fallback `batch_executor.py:92-93` chỉ chạy khi task thiếu `chosen_voice` — đường batch luôn set ở `batch_orchestrator.py:179`).

**Đã tốt:** `text_processing_cache` = `BoundedLRUDict(2048)` (`superfreetts.py:70`) — có giới hạn; cache retention 30 ngày (`batch_constants.py:105`); `build_request_key` SHA-224 (`audio_file_store.py`).

### A07 — Chất lượng âm thanh & format

**Kết luận:** Không có finding — F17 cũ là finding ma: OGG đã nghỉ hưu có chủ đích ở 26.10, không phải bug.

**Đã tốt (bằng chứng M1):** `component_preferences.py:14-15` ("OGG support was removed in 26.10", `AUDIO_FORMAT_CHOICES=("wav","mp3")`); `release_notes.py:38,52` (cả en + vi); `audio_file_store.py:102-113` đọc cache OGG cũ, không ghi mới; `test_audio_format_contract.py` + `test_audio_transcode.py` pass; retry thật ở `services/service_edgetts.py:311-394` (`_is_connectivity_error` :188), không phải dict UI :164-192 như bản trước đã dẫn.

### A08 — An toàn dữ liệu người dùng

**Kết luận:** Ghi note có undo entry, nhưng chưa có diễn tập backup/restore và giới hạn merge undo đã biết.

| ID | Sev | Score | Bằng chứng file:line | Tác động người dùng | Cách kiểm chứng |
|---|---|---|---|---|---|
| F09 | minor | 3×2/2 = 3 | `anki_utils.py:184,190,234` có `add_custom_undo_entry`, merge ở :199/:239 với warning đã biết (:238-241); `backup_guard.py` tồn tại nhưng không có test diễn tập phục hồi | Crash đúng lúc ghi batch lớn có thể cần restore thủ công | `pytest tests/test_note_audio_updater.py tests/test_realtime_remove_tts_tag.py -q` (pass); R8 diễn tập restore |

**Đã tốt:** áp lại cùng audio không nhân đôi `[sound:]` (test pass); xóa tag không xóa oan text (regex non-greedy fix `39e0851`); `user_files/` chỉ chứa `batch_state/`.

### A09 — Bảo mật & riêng tư

**Kết luận:** Không rò rỉ bất thường; code sentry đã chết hẳn (`if False`); host gọi ra khớp danh sách engine + CDN.

| ID | Sev | Score | Bằng chứng file:line | Tác động người dùng | Cách kiểm chứng |
|---|---|---|---|---|---|
| F13 | minor | 2×2/1 = 4 | `__init__.py:31` `if False:` → `sys._sentry_crash_reporting` không bao giờ set; 9 điểm chạm sentry (`anki_utils.py:24,423,425,434,436`, `logging_utils.py:8,61,83,85` — bản trước ghi 6 là thiếu) thành dead code | Hiểu nhầm "còn telemetry"; code chết gây rối | `grep -rn _sentry_crash_reporting`; Bandit `-ll` 0 issue |

**Đã tốt:** download pin SHA-256 + size (`download_sources.py`); `downloader.py:265-290` verify + MD5 `usedforsecurity=False`; host inventory: github 8, huggingface 6, 6 site từ điển, vocab.ai 2, ankivn 2, facebook 2 (link hỗ trợ) — không host lạ; `vendor_deps --check` exit 0.

### A10 — Packaging / release / versioning / update path

**Kết luận:** Version đồng bộ có test chặn, nhưng gói 88 MB còn 91 entry thừa và manifest thiếu sàn Anki tối thiểu.

| ID | Sev | Score | Bằng chứng file:line | Tác động người dùng | Cách kiểm chứng |
|---|---|---|---|---|---|
| F07 | minor | 2×5/4 = 2,5 → P1 (D1) | File `SuperFreeTTS.ankiaddon` 87.992.735 B = **88,0 MB** thập phân (83,9 MiB — bản trước trộn đơn vị, xem m8); chưa nén 125,6 MB; top: piper model 63,2 MB + libonnxruntime 16,3 MB; 91 entry tests/dist-info trong zip | Tải/cập nhật nặng, tốn dung lượng | Đọc zip (không build): top-10 + total; `verify_package.py` OK |
| F11b | minor (gộp F11) | — | `manifest.json` thiếu `min_point_version` (sàn Anki chưa khai báo) | User Anki cũ cài vào lỗi khó hiểu | Đọc `manifest.json` |

**Đã tốt:** `test_version_consistency.py` pass (manifest == version.py == release_notes[0] == CHANGELOG); `release_notes.py` 1.271 dòng song ngữ; không chạy `build_share.py` trên repo thật (đúng cấm kỵ).

### A11 — Config schema, migration, backward compat

**Kết luận:** Migration đủ mốc (thiếu số 4 là chủ đích — không tồn tại schema 4), còn 1 ghost key NaverTTS trong config mẫu.

| ID | Sev | Score | Bằng chứng file:line | Tác động người dùng | Cách kiểm chứng |
|---|---|---|---|---|---|
| F14 | nit | 1×3/1 = 3 | `config.json:10` `"NaverTTS": false` nhưng không có code Naver nào (`grep -ri naver superfreetts_addon` rỗng); `constants.py:148` SCHEMA 7 với mốc <2,<3,<5,<6,<7 (`config_models.py:883-968`, thiếu 4 = không tồn tại) | Sửa config tay thấy key lạ, hoang mang | `grep -ni naver config.json superfreetts_addon -r` |

**Đã tốt:** default fallback đầy đủ (`config_store.py:54-90`); `test_config_defaults.py` + `test_config_models.py` pass (62-test batch §2.2).

### A12 — Testing & CI / coverage

**Kết luận:** Suite xanh nhưng CI mù trên nhánh đang làm, 3 file test mồ côi, coverage lõi mỏng.

| ID | Sev | Score | Bằng chứng file:line | Tác động người dùng | Cách kiểm chứng |
|---|---|---|---|---|---|
| F04 | major | 3×5/2 = 7,5 → P0 (D1) | `tests/_test_edgetts_{continuous_batching,sequence_mode,vietnamese_batch}.py` — 3 file (bản trước ghi 12 là sai, xem m2); prefix `_test_` nên pytest không collect | Test viết rồi mà không chạy = không bảo vệ gì | `--collect-only` = 447, thiếu 3 file |
| F05 | major | 3×5/1 = **15** | `.github/workflows/python-test.yml:4-5` chỉ chạy push trên `[main, fix/release-readiness]` → nhánh `fix/resource-management` chưa từng chạy CI | Bug lọt lưới đúng nhánh đang sửa | Đọc file yml |
| F08 | major | 4×3/3 = 4 → P1 (D1) | TOTAL 39% (floor 33); `anki_utils.py` 0% (312 stmt), `component_voiceselection.py` 7%, `batch_orchestrator.py` 42%, `audio_generator.py` 50% — đúng 2 file chứa F01 | Sửa code mù, regression không ai bắt | `pytest --cov --cov-report=term` |

**Đã tốt:** 447 test xanh; checkpoint/concurrency/format/version đều có test riêng và pass; `pytest.ini` + `conftest.py` mock Anki sạch.

### A13 — i18n & accessibility

**Kết luận:** Khung 7 ngôn ngữ tốt nhưng ja/zh chỉ 15%, và accessibility chưa ai audit.

| ID | Sev | Score | Bằng chứng file:line | Tác động người dùng | Cách kiểm chứng |
|---|---|---|---|---|---|
| F06 | major | 3×5/4 = 3,75 → P1 (D1) | `locales`: en 599 key; ja/zh-CN/zh-TW **89** (15%); vi 593; ko 439; sv 191; fallback en trong `i18n.py` | User Nhật/Trung thấy nửa Anh nửa mẹ đẻ | Script đếm key vs en (baseline 599) |
| F10 | minor | 2×3/3 = 2 | Không có audit contrast 4.5:1, phím tắt xung đột (`component_shortcuts.py`, stylesheet `gui_utils.py`) | Người khiếm thị/khó dùng chuột gặp rào cản | R9: audit contrast + keyboard |

**Đã tốt:** 7 ngôn ngữ + fallback en (không crash thiếu key); `test_i18n_locales.py` tồn tại; release notes song ngữ đầy đủ.

### A14 — Logging / observability / diagnostics

**Kết luận:** Log đủ để gỡ lỗi nhưng file log chính không xoay vòng và log rule spam mỗi lần batch.

| ID | Sev | Score | Bằng chứng file:line | Tác động người dùng | Cách kiểm chứng |
|---|---|---|---|---|---|
| F19 | minor | 2×4/1 = 8 | `DEFAULT_LOG_FILE` ở `logging_utils.py:17` (bản trước ghi :20 là sai, xem m4); `FileHandler` :135 không rotation (rotation 5 MB chỉ có ở `service_logger.py:19`); `config_models.py:784` log `info` mỗi rule mỗi lần | `superfreetts.log` phình theo năm tháng; log nghìn dòng cho 1 batch | `ls -la user_files/*.log`; đếm dòng log/1 batch |

**Đã tốt:** log vào `user_files/superfreetts.log` (ngoài collection, không dính backup Anki); `[BATCH]`/`[RAM]` markers tra được; `component_usage.py` + `usage_log.json` đo đúng (cache hit ghi nhận); debug qua env.

### A15 — Tài liệu & hỗ trợ người dùng

**Kết luận:** Khung tài liệu tốt (REFERENCE/HANDOFF/UPDATE_WORKFLOW) nhưng số liệu drift sau mỗi lần chạy test.

| ID | Sev | Score | Bằng chứng file:line | Tác động người dùng | Cách kiểm chứng |
|---|---|---|---|---|---|
| F21 | nit | 1×4/1 = 4 | 3 file còn ghi "408 test" (`danh-gia-...:4,25,160`, `HANDOFF_TIEP_THEO_3:33,129`, `trien-khai-cong-2:7`) trong khi thực tế 446 (bản trước + tiêu chí `grep "408 passed"` không khớp text thật `"408 test"` — xem N4) | Đọc tài liệu cũ nghi ngờ số liệu mới | `grep -rnE "408 (test|passed)" AI_Documents` (phải dùng `-E`, xem N1) |

**Đã tốt:** `README.md` 3.894 byte đủ cài → tạo audio đầu tiên; `AGENTS.md`/`REFERENCE.md` còn giá trị; `EDGETTS_CONCURRENCY_TEST.md` lưu benchmark.

### A16 — Licensing & third-party compliance

**Kết luận:** Nghĩa vụ GPL khi phát hành zip chưa được đóng gói đầy đủ: thiếu NOTICE tập hợp, nguồn tương ứng chưa rõ ràng, ToS 6 site scraper chưa đánh giá.

| ID | Sev | Score | Bằng chứng file:line | Tác động người dùng | Cách kiểm chứng |
|---|---|---|---|---|---|
| F22 | major | 4×3/2 = 6 → P1 | `LICENSE` = GPL-3; gói `.ankiaddon` bán kèm espeak-ng (GPLv3), model Piper, binary onnxruntime, 46 dist-info vendored nhưng **không có `THIRD_PARTY_NOTICES`**, không file nguồn tương ứng; author `manifest.json` "Phuc" không nhắc upstream HyperTTS (fork); `constants.py:22-23` còn URL vocab.ai | Phát hành AnkiWeb/zip có thể vi phạm GPL (thiếu NOTICE + nguồn tương ứng); scraper 6 từ điển (cambridge/duden/dwds/oxford/spanishdict/youdao) chưa ai đọc ToS | `ls THIRD_PARTY_NOTICES` (kỳ vọng: chưa có); `vendor_deps --check`; đọc ToS 6 site |

**Đã tốt:** `LICENSE` GPL-3 hiện diện cả repo lẫn `dist/staging`; `download_sources.py` pin SHA-256 + ghi chú MMS dùng revision pin (minh bạch nguồn).

### A17 — Tương thích đa nền tảng & phiên bản Anki

**Kết luận:** Có guard platform trong code và CI matrix, nhưng chưa xác minh runtime Windows/macOS thật và chưa khai báo sàn Anki.

| ID | Sev | Score | Bằng chứng file:line | Tác động người dùng | Cách kiểm chứng |
|---|---|---|---|---|---|
| F11 | minor | 3×3/2 = 4,5 | 27 nhánh `sys.platform`/`platform.system()`; `service_windows.py`/`service_macos.py`/`service_espeakng.py` chỉ đọc code; `manifest.json` thiếu `min_point_version` (gộp từ A10) | Lỗi chỉ nổ trên máy user Win/Mac | R10: ma trận test thật + khai báo sàn |

**Đã tốt:** `test_engine_manager_platform_guard.py`, `test_mms_python_path.py` pass; CI matrix 3.9/3.11/3.13/3.14 + windows/macos (đọc yml).

### A18 — Scale & chi phí vận hành

**Kết luận:** Chưa có số đo batch lớn (10.000 note) và rào cản tải 88 MB chưa định lượng — toàn bộ là "chưa đo", không phải finding lỗi.

| ID | Sev | Score | Bằng chứng | Tác động | Kiểm chứng |
|---|---|---|---|---|---|
| F12 | minor | 2×2/2 = 2 | Không có log batch >1.000 note; retention 30 ngày có (`batch_constants.py:105`); `cleanup` pass (`test_cleanup_user_files.py`) | Không biết batch lớn mất bao lâu/tốn bao nhiêu | R19: script ước lượng 10k note từ code (ghi rõ ước tính) |

**Đã tốt:** dedup log sẵn (`[BATCH] Deduplication found`); retention + cleanup có test; EdgeTTS free-tier: cap 3 worker + retry/backoff (`services/service_edgetts.py:311-394`).

### A19 — Chất lượng 6 service từ điển (scraping)

**Kết luận:** Parse HTML là điểm vỡ tiềm ẩn, test chỉ dừng ở import-smoke, không thấy retry ở 2 service đã grep.

| ID | Sev | Score | Bằng chứng file:line | Tác động người dùng | Cách kiểm chứng |
|---|---|---|---|---|---|
| F18 | minor | 3×3/3 = 3 | `service_cambridge.py` dùng regex/HTML parsing; không thấy `retry`/`backoff`/`429`/`403` trong cambridge/youdao; `test_service_imports.py` chỉ smoke | Đổi giao diện site → tra từ điển hỏng âm thầm | R17: health-check 1 request/service |

**Đã tốt:** 6 service tách file riêng (`service_cambridge/duden/dwds/oxford/spanishdict/youdao.py`); voice list tập trung; timeout có ở mọi service.

### A20 — Product integrity / fork hygiene

**Kết luận:** Không còn upsell nào render được, nhưng chuỗi trial trả phí và URL cũ vẫn ship trong code.

| ID | Sev | Score | Bằng chứng file:line | Tác động người dùng | Cách kiểm chứng |
|---|---|---|---|---|---|
| F15 | nit | 1×2/1 = 2 | `constants.py:471-478` chuỗi "Start Free Trial… 50,000 characters… 7-day trial" (Azure/ElevenLabs/OpenAI) + `constants.py:22-23` URL vocab.ai + `errors.py:120` link tutorial cũ — 0 chỗ dùng ngoài constants (dead string, đã kiểm) | User tò mò đọc code thấy hứa hẹn tính phí, mất tin tưởng bản "Free" | `grep -rnE "NaverTTS\|sentry_sdk\|ENHANCED_TRIAL" superfreetts_addon` (phải `-E`, xem N1); `grep -rn "vocab.ai\|ElevenLabs"` |

**Đã tốt:** 0 chuỗi upsell render được trong UI; `config.json` chỉ còn ghost key NaverTTS (F14); sentry tắt hẳn (F13).

---

## 4. Đối chiếu với tài liệu cũ

### 4.1 Bảng trạng thái các ID audit 2026-10-22

| ID cũ | Nội dung | Trạng thái | Bằng chứng kiểm chứng lại |
|---|---|---|---|
| P0-1 | Kokoro RAM budget | **Đã xong** | Số đo thật trong code `tts_orchestrator.py:18-26`; `test_ram_aware_concurrency.py` pass |
| P1-1 | OGG chưa encode | **Đã xong theo hướng retire có chủ đích** (không phải fix encode) | `component_preferences.py:14-15`, `release_notes.py:38,52` |
| P1-2 | IPC timeout | **Đã xong** | `test_ipc_deadline.py` pass; deadline 60/120/150s trong code |
| P1-3 | Checkpoint không resume | **Đã xong** | 15 + 8 test checkpoint pass; resume theo note_id |
| P1-4 | Cleanup xóa log/usage | **Đã xong** | `test_cleanup_user_files.py` pass |
| P1-5 | Benchmark EdgeTTS | **Một phần** | `EDGETTS_CONCURRENCY_TEST.md` tồn tại; chưa có số batch lớn mới |

### 4.2 Bảng `danh-gia-va-ke-hoach-cai-thien-2026-10-23.md`

| Mục trong tài liệu | Trạng thái |
|---|---|
| A.2 Điểm mạnh (đã kiểm chứng) | Giữ nguyên giá trị, đã dùng làm "Đã tốt" các axis |
| Khía cạnh 1 — An toàn RAM & concurrency (P0) | **Đã xong** (số đo + test xanh) |
| Khía cạnh 2 — Ổn định IPC & runner (P1) | **Đã xong** (deadline + kill-and-retry) |
| Khía cạnh 3 — Khởi động & phản hồi UI (P1) | **Một phần** (F20 còn 276 except) |
| Khía cạnh 4 — Hiệu năng batch có đo lường (P2) | **Còn mở** (F12: chưa có số 10k) |
| Khía cạnh 5 — Độ tin cậy end-to-end (đang thiếu hoàn toàn) | **Còn mở** (F01 cần kiểm chứng runtime — R1) |
| Khía cạnh 6 — Chất lượng, i18n & tài liệu | **Còn mở** (F06, F21) |

### 4.3 Những gì audit cũ KẾT LUẬN SAI hoặc đã lỗi thời

1. **F01 bản trước: sai nguyên nhân gốc (critical).** Bản trước nói batch truyền `sequence_index` tường thuật nên "batch đúng", đổ lỗi cho counter `audio_generator.py:88-91`. Sai 3 điểm: (a) nhánh Random (`:75-81`) không dùng counter; (b) kịch bản ghi preview đơn ĐÚNG — bản trước nói preview sai; (c) đường batch không bao giờ đọc `_sequence_runtime_index` (1 điểm đọc duy nhất ở `:89`, chỉ cho preview đơn). Nguyên nhân thật: pre-f65934a `_generate_audio_batch_task` dùng voice item đầu chunk cho cả chunk + nhiễm cache (chứng minh ở §3-A06). (`USER_FEEDBACK.md` là kịch bản test tổng hợp — xem D2.)
2. **F17 (OGG degrade WAV): finding ma.** OGG đã gỡ có chủ đích ở 26.10 — không phải bug, không có việc sửa.
3. **P1-R1 cũ: "thay ước tính 2400 MB bằng số đo".** `tts_orchestrator.py:20-25` đã ghi số đo; 2400 MB là marginal cost đã đo, không phải ước tính. Việc còn lại duy nhất: đo thêm PSS (RSS ≠ PSS) — chuyển thành R16 (P2).
4. **"Coverage 39% tập trung đúng chỗ hiểm": sai.** Đúng 2 file chứa F01 (`batch_orchestrator` 42%, `audio_generator` 50%) lại mỏng nhất lõi.
5. **Số liệu sai rải rác (13 minor m1–m13):** `superfreetts.py` 777 không phải 477 (477 là statements trong coverage); tổng lõi 3.617 không phải 3.172; 3 file `_test_*` không phải 12; `git status` 6M+3U không phải 5M+2U; `DEFAULT_LOG_FILE` ở `:17` không phải `:20`; `CHECKPOINT_FLUSH_EVERY` ở `batch_constants.py:91`; 9 điểm chạm sentry không phải 6; retry thật ở `:311-394` không phải `:164-192`; 88,0 MB thập phân (83,9 MiB) — bản trước trộn đơn vị; `voiceselection` 791 dòng (không >800) và bỏ sót `release_notes.py` 1.271 dòng; CI chưa chạy nhánh hiện tại (A19 cũ nói "quy trình dev & CI TỐT" mà không đọc yml); 446 passed + 1 skipped = 447 (thống nhất, bỏ cặp "58 vs 23" mâu thuẫn).

---

## 5. Roadmap cải thiện

### 5.1 Đợt P0 — "An toàn để phát hành" (3 việc)

- **R2 (F02+F03). Mục tiêu:** mapping rules không thắng âm thầm. **Việc:** chặn/cảnh báo default thứ 2 cùng (model,deck); UI liệt kê rule mồ côi + nút sửa/xóa; test engine mới (`rule_applies`, `get_default_preset_id`, serialize round-trip). **Nghiệm thu:** §6-R2. (Effort 1–2)
- **R3 (F04). Mục tiêu:** không còn test mồ côi. **Việc:** đổi tên 3 file `_test_edgetts_*` thành `test_*` hợp lệ (hoặc xóa kèm lý do trong báo cáo). **Nghiệm thu:** collect ≥ 447 + số test mới. (Effort 1)
- **R4 (F05). Mục tiêu:** CI chạy trên nhánh đang làm. **Việc:** sửa trigger `on.push.branches` phủ `fix/**` (hoặc `['**']`). **Nghiệm thu:** đọc yml thấy phủ nhánh. (Effort 1)

### 5.2 Đợt P1 — "Ổn định & tin cậy" (8 việc)

- **R5 (F06)** i18n ja/zh-CN/zh-TW: thiếu ≤5% so với en (599 key). (Effort 4)
- **R6 (F07)** Gói ≤ 60 MB: loại 91 entry tests/dist-info, tách model Piper thành tải riêng lần đầu. (Effort 3)
- **R7 (F08)** Coverage lõi: `anki_utils.py` ≥ 40%, `component_voiceselection.py` ≥ 40%, giữ floor 33. (Effort 3)
- **R8 (F03+F09)** Backup/restore: diễn tập phục hồi collection sau crash + tài liệu khôi phục cho user. (Effort 2)
- **R9 (F10)** Accessibility: audit contrast ≥4.5:1 + vận hành bằng bàn phím. (Effort 3)
- **R10 (F11)** Ma trận nền tảng: bảng cái gì đã verify ở đâu (Win/Mac/Linux thật), khai báo `min_point_version`, guards còn thiếu. (Effort 2)
- **R11 (F14+A11)** Ghost keys: xóa `NaverTTS` khỏi `config.json`, audit `service_enabled` chỉ chứa key có implementation + `test_config_defaults`. (Effort 1)
- **R12 (F22)** Licensing: thêm `THIRD_PARTY_NOTICES`, làm rõ nguồn tương ứng GPL, đọc ToS 6 site scraper, ghi công upstream trong manifest/docs. (Effort 2)

### 5.3 Đợt P2 — "Chất lượng & vệ sinh" (8 việc)

- **R13 (F16)** CRLF + `.gitattributes`: 0 file lệch. (Effort 1)
- **R14 (F16)** Tách hàm logic >200 dòng (stylesheet loại trừ, ghi rõ). (Effort 3)
- **R15 (F15)** Fork hygiene: xóa chuỗi upsell chết + URL cũ. (Effort 1)
- **R16 (F21+m10)** Docs drift: 0 claim "408 test"; đo PSS (RSS ≠ PSS) cho Kokoro/Supertonic, ghi cạnh số RSS. (Effort 1)
- **R17 (F18)** Health-check 6 scraper (tối đa 1 request/service, ghi rõ). (Effort 2)
- **R18 (mới)** Incident response/rollback: note phát hành lỗi → rollback AnkiWeb + tắt tính năng. (Effort 1)
- **R19 (F12)** Scale: ước lượng 10k note từ code (ghi rõ ước tính) + khuyến nghị batch size. (Effort 2)
- **R20 (F20)** Error-copy pass: message thân thiện cho lỗi batch thường gặp. (Effort 2)
- **R21 (F01)** Kiểm thử hồi quy giọng theo chunk (kịch bản test, không chặn release). **Việc:** repro 6 note/2 voice Sequence (kỳ vọng A,B,A,B,A,B) + Random per-card trên đường batch; chạy 20 lần + 4 luồng. **Nghiệm thu:** §6-R21. (Effort 1)

P0 3 việc (R2–R4) · P1 8 việc (R5–R12) · P2 9 việc (R13–R21).

### 5.4 Bảng phụ thuộc giữa các việc

| Việc | Phải xong trước | Vì sao |
|---|---|---|
| R2–R3 | R4 | CI phải chạy trên nhánh trước khi tin kết quả verify |
| R7 | R3 | Coverage tính trên tập test đã bao gồm file được cứu |
| R6 | R11 | Dọn key trước khi chốt danh sách đóng gói |
| R8 | R2–R4 | Diễn tập restore chạy sau khi P0 xong |
| R10 | R2–R4 | Ma trận platform chốt sau khi P0 xong |
| R15/R16 | Mọi P0 | Số liệu tài liệu chốt sau khi P0 đổi code/test |
| R19 | — | Ước lượng scale dựa trên chunk/voice-grouping đã fix (f65934a) |

---

## 6. Tiêu chí nghiệm thu có thể kiểm chứng (việc → lệnh → ngưỡng pass)

| Việc | Lệnh nghiệm thu | Ngưỡng pass |
|---|---|---|
| R21 hồi quy giọng theo chunk (kịch bản test) | Script scratch §8.1 + `pytest tests/test_batch_mixed_voice_chunk.py -q` | Sequence A,B,A,B,A,B mọi lần; Random mỗi card 1 voice; batch call tách theo voice (informational, không gate) |
| R2 mapping rules | `pytest tests/test_mapping_rules_engine.py -q` (mới) | 2 defaults → raise/cảnh báo (không còn trả `p1` âm thầm); rule mồ côi → UI báo, không crash |
| R3 test mồ côi | `pytest tests/ -q --collect-only \| tail -1` | ≥ 447 + số test trong 3 file (hoặc file đã xóa kèm lý do) |
| R4 CI nhánh | Đọc `.github/workflows/python-test.yml` | `on.push.branches` phủ `fix/**` hoặc `['**']` |
| R5 i18n | Script đếm key vs `en` (599) | ja/zh-CN/zh-TW thiếu ≤ 5% |
| R6 gói nhẹ | Đọc zip (không build) | ≤ 60 MB, 0 entry `tests/`, 0 `*.dist-info/tests` |
| R7 coverage lõi | `pytest --cov --cov-fail-under=33` | `anki_utils.py` ≥ 40%, `voiceselection` ≥ 40% |
| R8 backup drill | Diễn tập restore theo tài liệu mới | Khôi phục collection đúng 100% note mẫu |
| R9 a11y | Audit contrast + keyboard | 0 cặp chữ/nền < 4.5:1; mọi luồng chính dùng được bằng phím |
| R10 platform | Bảng ma trận + `manifest.json` | Có `min_point_version`; mỗi engine ghi rõ đã verify ở đâu |
| R11 ghost key | `pytest tests/test_config_defaults.py` | `service_enabled` chỉ chứa key có implementation; `grep -ri naver config.json` rỗng |
| R12 licensing | Đọc repo | Có `THIRD_PARTY_NOTICES`; nguồn tương ứng rõ; ToS 6 site đã đọc |
| R13 CRLF | Script đếm + `ls .gitattributes` | 0 file lệch, có `.gitattributes` |
| R14 hàm dài | Script AST (không dùng grep — xem N2) | 0 hàm logic > 200 dòng (stylesheet loại trừ, liệt kê) |
| R15 hygiene | `grep -rnE "vocab.ai\|ElevenLabs" superfreetts_addon` | 0 chuỗi upsell trong code ship |
| R16 docs+PSS | `grep -rnE "408 (test|passed)" AI_Documents` + lệnh đo PSS | 0 claim sai; có số PSS cạnh RSS (informational, không gate) |
| R17 scraper | Health-check 1 req/service | Bảng sống/chết + retry cho service còn sống |
| R18 incident | Đọc note rollback | Có đường rollback AnkiWeb ≤ 1 ngày |
| R19 scale | Script ước lượng | Có số 10k note (ghi rõ ước tính) + batch size khuyến nghị |
| R20 error copy | Đọc code errors | Lỗi batch thường gặp có message 1 câu tiếng Việt đơn giản |

Ghi chú sửa các tiêu chí cũ không đo được (nits N1–N6): `grep "NaverTTS|sentry_sdk..."` → phải là `grep -rnE` (không `-E` thì `|` thành chữ thường → luôn rỗng); `grep "408 passed"` → sai text thật (`"408 test"`); `grep .acquire(` → thay bằng script AST; "review dễ hơn"/"pixel-diff = 0" → bỏ, thay bằng R14/R9 đo được; bandit `-ll` → luôn ghi chú "ẩn 114 LOW"; call-site `choose_voice` → thống nhất: gọi ở `superfreetts.py:409`, định nghĩa ở `:429`; dẫn "xem §2" cho danh sách test → bỏ (không có).

---

## 7. Rủi ro & câu hỏi mở

1. Fix F01 đã commit + test hồi quy pass; `USER_FEEDBACK.md` là kịch bản test nên R21 chỉ là kiểm thử hồi quy (không bắt buộc trước release).
2. Không telemetry: mọi Impact là suy luận từ code (`USER_FEEDBACK.md` là file test, không phải phản ánh thật).
3. Working tree bẩn: số đo có thể lệch bản release.
4. Schema version nhảy số 4, `NaverTTS`, chuỗi trial 50.000 ký tự — để ngỏ cho tác giả, không kết luận bug.
5. Scraping ToS 6 site chưa đọc — R12/R17 bao phủ.
6. Effort trong score là phỏng đoán audit.

---

## 8. Phụ lục

### 8.1 Lệnh tái lập (copy-paste, đúng thứ tự)

```bash
cd /home/admin/Documents/deepseek-harness/default-workspace/superfreetts
git status --short; git branch --show-current; git log --oneline -5
.venv/bin/python -m pytest tests/ -q -p no:randomly 2>&1 | tail -2
.venv/bin/python -m pytest tests/ -q -p no:randomly --cov=superfreetts_addon --cov-report=term 2>&1 | grep -E 'TOTAL|anki_utils|voiceselection|batch_orchestrator|audio_generator'
.venv/bin/python -m ruff check superfreetts_addon tests scripts 2>&1 | tail -2
.venv/bin/python -m bandit -ll -r superfreetts_addon 2>&1 | tail -8   # lưu ý: -ll ẩn 114 LOW
.venv/bin/python /home/admin/.hermes/cache/scratch/audit_fix2/repro_f01.py   # F01: Sequence+Random+chunk+dedup
.venv/bin/python /home/admin/.hermes/cache/scratch/audit_fix2/repro_m7.py    # M7: mapping-rule engine
.venv/bin/python -m pytest tests/test_batch_mixed_voice_chunk.py -q -p no:randomly
grep -rnE "NaverTTS|sentry_sdk|ENHANCED_TRIAL" superfreetts_addon --include='*.py'
```

### 8.2 Số liệu đo được (baseline)

447 collected (446 passed + 1 skipped); coverage TOTAL 39% (floor 33); ruff sạch; bandit `-ll` 0 issue (114 LOW bị ẩn); zip 87.992.735 B = 88,0 MB (125,6 MB chưa nén, 998 file); i18n en 599 / ja·zh 89 / vi 593 / ko 439 / sv 191; lõi: superfreetts 777 + batch_orchestrator 785 + batch_executor 775 + audio_generator 296 + config_models 984 = **3.617** dòng; 56 hàm ≥80 dòng; 540 tham chiếu `hypertts`; 276 `except Exception`; 27 nhánh platform; 4 file lệch CRLF, không `.gitattributes`; working tree 6M+3U.

### 8.3 Danh sách file đã đọc (không có meta.json, không nội dung user_files)

`audio_generator.py`, `batch_orchestrator.py`, `batch_executor.py`, `superfreetts.py`, `config_models.py`, `tts_orchestrator.py`, `component_preferences.py`, `audio_file_store.py`, `release_notes.py`, `anki_utils.py`, `logging_utils.py`, `__init__.py`, `constants.py`, `i18n.py` + `locales/*.json`, `service_edgetts.py`, `service_cambridge.py`, `service_youdao.py`, `component_voiceselection.py`, `component_presetmappingrules.py`, `editor_manager.py`, `manifest.json`, `config.json`, `LICENSE`, `.github/workflows/python-test.yml`, `pytest.ini`, `tests/test_batch_mixed_voice_chunk.py`, `USER_FEEDBACK.md` (kịch bản test tổng hợp), `danh-gia-va-ke-hoach-cai-thien-2026-10-23.md`. Evidence thô: `~/.hermes/cache/scratch/audit_evidence/` (`F01_repro.txt`, `F01_regtest.txt`, `M7_repro.txt`, `S0_*`, `S1_*`).
