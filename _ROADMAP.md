# Superfreetts - Product Roadmap

Roadmap này chỉ giữ phần còn mở. Mục đã ship đi vào `CHANGELOG.md` và chi tiết kỹ thuật dài đi vào `AI_Documents/AGENTS.md` + `AI_Documents/REFERENCE.md`.

## Cách đọc

- `Done`: đã ship, chỉ giữ để tra cứu.
- `Mostly done`: đã ship phần lớn, còn một vài việc nhỏ.
- `In Progress`: còn code, test, hoặc docs thật sự cần làm.
- `Planned`: chỉ dùng cho việc chưa bắt đầu nhưng vẫn có giá trị rõ.

## Đánh giá nhanh

- Roadmap cũ bị trộn giữa feature đã xong, nợ kỹ thuật thật, và brainstorm tương lai.
- Phần còn phù hợp nhất với project hiện tại: UX polish, performance/cache, quality/testing, refactor/performance debt.
- Phần đã ship nên rút gọn: Unified Settings, Workflow, core stability.
- Không giữ các block giải thích dài, câu hỏi điều tra cũ, hoặc release-note text trong roadmap.

## Tình trạng tổng quan

| Phase | Chủ đề chính | Trạng thái | Ghi chú |
| --- | --- | --- | --- |
| 0 | Unified Settings + AnkiVN Menu | Done | Đã ship |
| 1 | Ổn định & dọn dẹp | Done | Đa luồng, crash, log |
| 2 | UX & cấu hình | In Progress | Chỉ còn UX polish thật sự |
| 3 | Hiệu suất & cache | In Progress | Queue lớn, IO, cache text |
| 4 | Tính năng nâng cao | Mostly done | Workflow đã ship; naming/folder còn mở |
| 5 | Test, tài liệu & cộng đồng | Mostly done | CI + regression tests đã ship; còn cập nhật docs |
| 6 | Refactor + Performance Audit | In Progress | Core split + legacy cleanup đã xong; còn timeout hardcode, voicelist, duplicate import |

---

## Current Roadmap

### Phase 2 - UX & Configuration

- ✅ Field Mapping và Voice Selection đã tách riêng; option chính nằm đầu từng tab.
- Giữ Settings nhanh, gọn, dễ quét.
- Polish các luồng speed/pitch/preview và trạng thái generate.
- Cải thiện copy lỗi để người dùng biết nên kiểm tra config, mạng, hoặc engine nào.
- Done khi người mới có thể cấu hình, preview, và generate audio mà không cần đọc tài liệu dài.

### Phase 3 - Performance & Caching

- ✅ Audio cache đã có `AudioFileStore` (SHA-224 content-addressed) + `SmartLRUCache` + `VoiceListCache`.
- ✅ Giới hạn concurrency theo engine: `tts_orchestrator.py::build_engine_config()` RAM-cap + per-engine clamp (`EDGETTS_MAX_WORKERS = 3` cho EdgeTTS).
- ⏳ Cache text (`text_processing_cache` ở `superfreetts.py:81`) vẫn là `{}` dict đơn giản, chưa có eviction/giới hạn kích thước.
- Tối ưu IO khi ghi audio, nhất là các batch nhiều note.
- Done khi duplicate request giảm rõ và batch lớn vẫn giữ Anki phản hồi ổn.

### Phase 4 - Advanced Features

- Workflow / Queue Preset đã ship: dialog, save/load, duplicate, rename, delete, run, Browser menu, Quick Run.
- Việc còn mở: custom output folder nếu thật sự cần quản lý audio ngoài Anki media.
- Việc còn mở: naming policy/prefix-suffix/template nếu `superfreetts-<hash>` chưa đủ.
- Done khi naming/folder được ship hoặc được chủ động deferred.

### Phase 5 - Quality, Testing & Community

- ✅ Thêm GitHub Actions/CI để chạy test tự động: `.github/workflows/python-test.yml`.
- ✅ Mở rộng regression tests cho batch, workflow, config migration, service fallback: ~30 file test mới (test_batch_flow, test_service_manager, test_supertonic_service, test_macos_concurrency_gate, test_ram_aware_concurrency...).
- Còn lại: cập nhật `README.md` / `_PROJECT_DOCUMENTATION.md` khi thay đổi hành vi user-facing (lưu ý: `_PROJECT_DOCUMENTATION.md` đã xoá, docs gộp về `AI_Documents/`).
- Chỉ thêm issue/PR templates khi repo thật sự cần nhận đóng góp ngoài.
- Done khi test suite chạy tự động và cover được các luồng dễ regression nhất.

### Phase 6 - Refactor + Performance Audit

- ✅ Tách `superfreetts.py` God Class: giờ là facade mỏng (~585 dòng), logic tách sang `batch_orchestrator.py`, `editor_manager.py`, `config_store.py`, `audio_generator.py`, `realtime_manager.py`, `tts_orchestrator.py`, `job_pipeline.py`.
- ✅ Dọn legacy fallback: `component_services_legacy.py`, `performance_cache.py`, `cpu_utils.py`, `sherpa_manager.py` đã xoá; 7x `except:pass` trong `component_kokoro_manager.py` đã fix; `threading.Semaphore` → `DynamicSemaphore` trong `service_mms.py`.
- ✅ Tăng test coverage core batch flow: `test_batch_flow.py`, `test_batch_preview_preset_switch.py`, `test_batch_state_manager.py`, `test_batch_executor_routing_and_stop.py`.
- ⏳ **Thay hardcoded batch timeout (`future.result(timeout=25.0)`)** tại `batch_orchestrator.py:742` bằng per-engine timeout config. Hằng số `TASK_TIMEOUT_SECONDS = 120` đã có trong `batch_constants.py` nhưng chưa được dùng ở chỗ này. Còn cả `stall_timeout_seconds = 60.0` hardcode ở `batch_orchestrator.py:678`.
- ⏳ **Giảm gánh nặng `voicelist.py`**: file 2.5MB / 43k dòng, vẫn được `service.py:16` import trực tiếp → nạp ngay khi Anki khởi động. Cần lazy-load/compress hoặc đưa dữ liệu ra ngoài source.
- ⏳ **Xoá import trùng lặp trong `superfreetts.py:83-89`**: khối `from .tts_orchestrator import TTSOrchestrator` / `UIController` / `JobPipeline` được import 2 lần y hệt nhau (vô hại nhưng cần dọn). *Nhắc nhở AI agent: khi đọc/refactor file này, kiểm tra và gộp về 1 khối.*
- Done khi core nhỏ hơn, timeout configurable, `voicelist.py` không còn là file quá lớn trong source, và batch refactor có test bảo vệ.

---

## Completed Archive

- **P0 - Unified Settings + AnkiVN Menu**: gộp Services/Preferences, thêm menu top-level, giữ wrapper backward-compatible.
- **Phase 1 - Core Stability & Cleanup**: ổn định đa luồng, giảm treo UI, giảm log spam, cập nhật executor khi config worker đổi.
- **Workflow / Queue Preset**: đã triển khai CRUD workflow, chạy nhiều preset theo thứ tự trên cùng notes, Browser menu, Quick Run Workflow.

Chi tiết release đã ship nằm trong `CHANGELOG.md`; roadmap này không lặp lại release notes.

---

## Deferred Ideas

- Delay/concatenate audio trong workflow nếu sau này cần pipeline phức tạp hơn.
- Template đặt tên nâng cao hơn `superfreetts-<hash>` nếu prefix/suffix cơ bản không đủ.
- Preset/workflow matching nâng cao theo deck/note type nếu mapping rule hiện tại chưa đủ.

Bất kỳ ý tưởng mới nào chỉ nên vào roadmap khi có use case rõ và code gap thật.
