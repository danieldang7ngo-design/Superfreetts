Superfreetts – Product Roadmap
==============================

## Giới thiệu & cách đọc roadmap

Roadmap này mô tả lộ trình phát triển của add-on Superfreetts cho Anki theo từng giai đoạn rõ ràng, có thứ tự ưu tiên và tiêu chí hoàn thành cụ thể.  
Mỗi **Phase** (giai đoạn) tập trung vào một chủ đề chính (ổn định, UX, hiệu suất, tính năng nâng cao, cộng đồng) và liệt kê các hạng mục cần làm với ưu tiên tương đối (High/Medium/Low).

Khi triển khai thực tế, có thể đánh dấu thêm trạng thái cho từng hạng mục: **Planned**, **In Progress**, **Done**.

## Tầm nhìn (Vision)

Superfreetts hướng tới việc trở thành add-on TTS:

- Giúp người dùng Anki tạo audio từ text **miễn phí**, ổn định và dễ dùng, không phụ thuộc dịch vụ trả phí.
- Hỗ trợ nhiều giọng đọc và ngôn ngữ (EdgeTTS) với cấu hình đơn giản, dễ hiểu.
- Tích hợp mượt vào workflow tạo/sửa thẻ, không làm chậm hoặc treo Anki ngay cả khi xử lý nhiều thẻ.

## Mục tiêu sản phẩm (Product Goals)

- **Stability & Reliability**
  - Hạn chế tối đa crash hoặc treo Anki khi generate nhiều audio liên tiếp.
  - Xử lý tốt hàng đợi (queue) lớn mà vẫn giữ UI phản hồi được.
- **UX & Productivity**
  - Giảm số thao tác cần thiết để tạo audio cho nhiều thẻ.
  - Người dùng luôn biết add-on đang làm gì (progress, thông báo rõ ràng).
- **Extensibility**
  - Cấu trúc mã dễ mở rộng thêm tính năng (preset, tùy biến tên file, tích hợp công cụ khác).
  - Có tài liệu và guideline đủ rõ để contributor mới tham gia nhanh chóng.

## Phạm vi & nguyên tắc (Scope & Principles)

- Tập trung chính vào EdgeTTS làm engine TTS (không cố ôm quá nhiều engine khác cùng lúc).
- Ưu tiên trải nghiệm ổn định, dễ hiểu hơn là quá nhiều tuỳ chọn phức tạp.
- Hạn chế tối đa phụ thuộc vào dịch vụ trả phí, cấu hình khó.
- Thiết kế đơn giản, rõ ràng, ưu tiên code dễ bảo trì hơn là “hack nhanh”.

## Tóm tắt các giai đoạn (Roadmap Summary)

| Phase | Chủ đề chính                 | Trạng thái   | Ghi chú ngắn                      |
|------|------------------------------|-------------|-----------------------------------|
| **P0** | **Unified Settings + AnkiVN Menu** | **✅ Done** | **PRIORITY: Gộp Config+Pref, menu top-level** |
| 1    | Ổn định & dọn dẹp            | ✅ Done     | Đa luồng, crash, cấu trúc, log    |
| 2    | UX & cấu hình                | In Progress | UI config, speed/pitch, preview   |
| 3    | Hiệu suất & cache            | Planned     | Queue lớn, IO, cache text        |
| 4    | Tính năng nâng cao           | Planned     | Preset, naming, folder            |
| 5    | Test, tài liệu & cộng đồng   | Planned     | Test, docs, guideline, issue flow |

---

## Phase P0 – Unified Settings UI & AnkiVN Menu Integration ✅ COMPLETED

**[TOP PRIORITY - COMPLETED]**

- **Mục tiêu chính** ✅
  - ✅ Gộp Configuration dialog + Preferences dialog thành một thống nhất "Super Free TTS Settings" với 2 tab: Services & Preferences.
  - ✅ Đưa entry point chính từ Tools menu vào menu top-level mới "AnkiVN" (ngang hàng với Tools, Edit, File).
  - ✅ Đảm bảo cả hai cấu hình (Services + Preferences) có thể được chỉnh sửa và lưu trong một phiên thao tác.

- **Các hạng mục chính** ✅
  - [Priority: Critical] ✅ Tạo unified settings dialog với QTabWidget (Services tab + Preferences tab)
    - ✅ Tái sử dụng component hiện có từ `component_configuration.py` và `component_preferences.py`
    - ✅ Thực hiện save flow thống nhất: save Configuration → save Preferences → reconfigure ServiceManager
  - [Priority: Critical] ✅ Tạo menu AnkiVN top-level trên main menubar
    - ✅ Insert trước Help menu nếu khả dụng, else append cuối cùng
    - ✅ Thêm action "Super Free TTS" mở unified dialog
  - [Priority: High] ✅ Cập nhật i18n keys cho unified title, tab labels
    - ✅ Giữ key cũ cho backward-compatibility
  - [Priority: Medium] ✅ Giữ backward-compatible wrapper: Tools menu actions redirect tới unified dialog
  - [Priority: Medium] ✅ Fallback mechanism nếu top-level insert API fail ở bản Anki cũ

- **Definition of Done** ✅
  - ✅ Main menu bar hiển thị menu "AnkiVN" ngang hàng Tools
  - ✅ Click "AnkiVN" → "Super Free TTS" mở 1 dialog duy nhất với 2 tab rõ ràng
  - ✅ Chỉnh sửa Services (enable/config) + Preferences (language/cache/…) trong cùng phiên, click Save → cả hai lưu được
  - ✅ Không duplicate menu sau addon reload (objectName pattern)
  - ✅ Browser menu và editor buttons không bị ảnh hưởng
  - ✅ Tài liệu (ROADMAP, PROJECT_DOCUMENTATION) được cập nhật phản ánh entry point mới

**Implementation Summary:**
- Created `component_unified_settings.py` (133 lines) – UnifiedSettingsDialog class consolidating Services + Preferences
- Added AnkiVN top-level menu to main menubar with insert-before-Help logic
- Wired `Super Free TTS` action to launch_unified_dialog(hypertts, initial_tab=0)
- Added 3 i18n keys (EN/VI): unified_settings_title, tab_services, tab_preferences
- Updated legacy entry points (launch_configuration_dialog, launch_preferences_dialog) to redirect to unified dialog
- Updated PROJECT_DOCUMENTATION.md with new menu navigation and component documentation
- All files syntax-verified with Pylance (no errors)
- Commits: 1f72823 (Steps 1-3) + bc6e5a7 (Steps 4-5)

---

## Phase 1 – Core Stability & Cleanup ✅ COMPLETED

- **Mục tiêu chính** ✅
  - ✅ Hạn chế tối đa việc treo hoặc crash Anki khi sử dụng Superfreetts.
  - ✅ Chuẩn hoá cấu trúc dự án và logging để dễ debug và bảo trì.

- **Các hạng mục chính** ✅
  - [Priority: High] ✅ Cố định đa luồng (multithreading) khi generate nhiều audio liên tiếp.
    - ✅ Recreate executor khi worker config thay đổi, tránh dùng pool cũ/stale.
    - ✅ Chuẩn hóa key service config `MmsTTS` để map đúng vào pool `MMS`.
  - [Priority: High] ✅ Giảm lỗi treo UI Anki khi hàng đợi audio lớn.
    - ✅ Bỏ `sleep(0.1)` trong refresh status để không block UI.
    - ✅ Hủy pending futures khi user stop batch để giảm backlog CPU/RAM.
    - ✅ Sửa progress unique task (không tăng sai theo số note duplicate).
  - [Priority: Medium] ✅ Chuẩn hóa/giảm nhiễu logging để ổn định runtime.
    - ✅ Tắt `FORCE_DEBUG_MODE` mặc định trong production.
    - ✅ Loại bỏ warning log quá nặng ở `detect_service` (chuyển sang fast path).

- **Definition of Done** ✅
  - ✅ Luồng batch chạy ổn định hơn khi số lượng note lớn và khi user hủy tác vụ giữa chừng.
  
  - ✅ Cấu hình worker mới có hiệu lực ngay sau reconfigure.
  - ✅ Logging giảm overhead, không spam warning trong loop lớn.

## Phase 2 – UX & Configuration Experience 🚧 IN PROGRESS

**Progress updates (completed in current implementation):**
- ✅ Reduced settings open jitter by lazy-rendering non-active tabs in unified settings.
- ✅ Added unsaved-change confirmation + save success toast in unified settings dialog.
- ✅ Added per-service readiness badges, smarter services search index, and debounced search filtering.
- ✅ Added inline validation hints for required key/token fields and file/folder paths.
- ✅ Added top-level services summary line (Ready / Needs setup / Disabled).
- ✅ Improved settings visual rhythm: consistent margins/spacing and clearer tab hierarchy across Services + Preferences.

- **Mục tiêu chính**
  - Giúp người dùng cấu hình và sử dụng add-on một cách trực quan, ít phải đoán.
  - Cung cấp feedback rõ ràng về trạng thái xử lý (đang chạy, xong, lỗi).

- **Các hạng mục chính**
  - [Priority: High] Thiết kế lại cửa sổ cấu hình:
    - Gom nhóm các tùy chọn quan trọng (ngôn ngữ, giọng, tốc độ đọc) ở trên cùng.
    - Giải thích ngắn gọn từng option bằng tiếng Việt hoặc tiếng Anh dễ hiểu.
  - [Priority: High] Thêm điều khiển tốc độ và cao độ giọng đọc:
    - Thanh trượt (slider) cho `speed` (chậm ↔ nhanh) với giá trị mặc định an toàn.
    - Thanh trượt (hoặc input số đơn giản) cho `pitch` (trầm ↔ cao).
    - Nút xem trước (preview) để nghe nhanh 1 câu mẫu với speed/pitch đã chọn.
  - [Priority: Medium] Thêm trạng thái tiến trình khi generate audio:
    - Thanh tiến trình đơn giản hoặc label đếm số file đã xử lý.
    - Thông báo khi hoàn tất hoặc khi có lỗi.
  - [Priority: Medium] Cải thiện thông báo lỗi: câu chữ dễ hiểu, gợi ý cách tự xử lý (vd: kiểm tra mạng, kiểm tra cấu hình).

- **Definition of Done**
  - Người dùng mới có thể tự cấu hình và tạo audio lần đầu mà không cần đọc thêm tài liệu dài.
  - Có thể nhìn thấy rõ add-on đang ở trạng thái nào khi đang generate (đang chạy / xong / lỗi).
  - Speed/pitch có thể chỉnh và nghe thử, tránh phải vào/ra nhiều lần để thử nghiệm.

## Phase 3 – Performance & Caching

- **Mục tiêu chính**
  - Tối ưu hiệu suất cho các trường hợp generate audio số lượng lớn, tránh gọi TTS thừa.

- **Các hạng mục chính**
  - [Priority: High] Cache kết quả TTS cho cùng một đoạn text (tránh gọi API nhiều lần cho cùng nội dung).
  - [Priority: Medium] Tùy chọn giới hạn số luồng chạy song song để tránh quá tải CPU/mạng.
  - [Priority: Medium] Tối ưu việc ghi file audio (giảm số lần mở/đóng file, quản lý đường dẫn hợp lý).

- **Definition of Done**
  - Khi generate lại audio cho cùng một nội dung text, số lần gọi EdgeTTS giảm rõ rệt (nếu bật cache).
  - Trên máy cấu hình trung bình, generate bộ thẻ lớn không làm Anki lag nặng kéo dài.

## Phase 4 – Advanced Features

- **Mục tiêu chính**
  - Thêm các tính năng nâng cao phục vụ người dùng “power user” nhưng vẫn giữ đơn giản cho người mới.

- **Các hạng mục chính**
  - [Priority: High] Hỗ trợ preset cấu hình:
    - Lưu nhiều bộ thiết lập giọng đọc (Preset A/B/C) để đổi nhanh theo deck hoặc loại thẻ.
  - [Priority: Medium] Cho phép chọn thư mục lưu audio tuỳ chỉnh (nếu người dùng muốn quản lý file ngoài).
  - [Priority: Low] Tùy chọn thêm prefix/suffix vào tên file audio để dễ nhận diện.

- **Definition of Done**
  - Người dùng có thể tạo, lưu và chuyển đổi giữa nhiều preset cấu hình.
  - Có tuỳ chọn (không bắt buộc) cho phép điều chỉnh vị trí lưu file và cách đặt tên.

## Phase 5 – Quality, Testing & Community

- **Mục tiêu chính**
  - Đảm bảo chất lượng dài hạn và tạo môi trường dễ đóng góp.

- **Các hạng mục chính**
  - [Priority: High] Bổ sung bộ test tự động trong thư mục `tests/` cho các chức năng cốt lõi.
  - [Priority: Medium] Ghi lại các case lỗi phổ biến và cách xử lý trong tài liệu.
  - [Priority: Medium] Cập nhật `PROJECT_DOCUMENTATION.md` và `README.md` cho phù hợp tính năng mới.
  - [Priority: Low] Chuẩn hoá guideline đóng góp và template issue/pull request.

- **Definition of Done**
  - Có một tập test cơ bản chạy được, giúp bắt lỗi regression cho các tính năng chính.
  - Người dùng và contributor có thể tìm được hướng dẫn xử lý lỗi phổ biến.
  - Người mới muốn đóng góp có thể dựa vào guideline để mở PR đầu tiên.

## Roadmap kỹ thuật (Technical Roadmap mini)

- Chuẩn hoá API nội bộ cho việc gọi EdgeTTS (module riêng, dễ mock/test).
- Thiết kế module queue xử lý task TTS (quản lý trạng thái, retry, huỷ task nếu cần).
- Định nghĩa rõ lớp chịu trách nhiệm logging, tránh log rải rác khó kiểm soát.
- Thiết kế cấu trúc test đơn giản cho các phần: gọi TTS, xử lý queue, xử lý config.

## Dành cho contributor

- Đọc thêm:
  - `PROJECT_DOCUMENTATION.md` để hiểu kiến trúc và luồng xử lý.
  - `README.md` để nắm tổng quan cài đặt và sử dụng.
- Nếu bạn mới bắt đầu đóng góp:
  - Ưu tiên chọn các hạng mục Priority = Medium trong Phase 1 hoặc Phase 2.
  - Mở issue trước khi làm các thay đổi lớn để trao đổi hướng tiếp cận.
- Khi gửi pull request:
  - Cố gắng thêm/giữ test liên quan (nếu có).
  - Cập nhật tài liệu nếu thay đổi hành vi user-facing (UI, config, tuỳ chọn mới).

## Ý tưởng tương lai — Workflow / Queue Preset (chạy nhiều preset cùng lúc)

> Ghi chú để review sau: thêm vào roadmap như một hướng mở rộng cho power user.

Ý tưởng tạo **Workflow / Queue Preset (chạy nhiều preset cùng lúc)** là một tính năng xuất sắc và đánh trúng “nỗi đau” (pain-point) của nhóm người dùng Anki nâng cao (Power Users).

### Tại sao tính năng này sẽ rất giá trị?

1. **Học đa giọng (Multi-Accent):** Người học ngoại ngữ thường muốn nghe cả giọng Anh-Mỹ và Anh-Anh cho cùng một từ. Hiện tại họ phải chạy batch 2 lần. Nếu có Queue, họ chỉ cần 1 click.
2. **Thẻ đa ngôn ngữ (Bilingual Flashcards):** Thẻ có mặt trước tiếng Anh (cần giọng US), mặt sau giải nghĩa tiếng Pháp/Việt (cần giọng khác). Chạy 2 preset cùng lúc sẽ tự động hóa hoàn toàn quy trình tạo thẻ.
3. **Mô phỏng hội thoại (Male/Female):** Tạo 2 trường audio riêng biệt với giọng Nam và Nữ xen kẽ để luyện nghe.

### Đánh giá tính khả thi trên codebase hiện tại

Cơ sở hạ tầng của hệ thống đã sẵn sàng. Đang có `batch_executor.py` chạy tác vụ ngầm bằng Threading và `batch_state_manager.py` quản lý trạng thái rất tốt.

### Gợi ý 2 hướng triển khai (từ dễ đến khó)

**Hướng 1: Multi-Select Presets trong Batch UI (thực dụng, code nhanh)**

- **Giao diện:** Trong cửa sổ Batch Generation, thay vì dùng Dropdown (`QComboBox`) chỉ cho phép chọn 1 Preset, dùng một danh sách **checkbox** (`QListWidget` thiết lập `ItemIsUserCheckable`). Người dùng có thể tick chọn nhiều Preset cần chạy.
- **Logic:** `BatchExecutor` hiện tại nhận 1 cấu hình. Sửa lại để nhận một `List[Preset]`. Khi duyệt qua từng thẻ (Note) trong Anki, vòng lặp con chạy qua danh sách Preset này để tạo tuần tự từng file audio rồi gán vào các Target Field tương ứng.

**Hướng 2: Khái niệm “Workflow / Pipeline” riêng biệt (chuyên nghiệp hơn)**

- **Giao diện:** Trong màn hình Settings chính, tạo khu vực “Workflows”. Người dùng tạo Workflow mới (ví dụ: “Luyện nghe TOEIC”) và add nhiều Preset (Preset 1: từ vựng giọng UK; Preset 2: câu ví dụ giọng US).
- **Logic:** Ở giao diện Batch, người dùng chọn Workflow. Khác Hướng 1: có thể thiết lập **Delay** (nghỉ 1 giây giữa các audio) nếu muốn nối (concatenate) 2 preset vào chung 1 file audio thay vì xuất ra 2 trường khác nhau.

### Điểm nghẽn kỹ thuật (edge cases) cần lường trước

1. **Xung đột Target Field (ghi đè):** Nếu chạy 2 Preset nhưng cả hai đều lưu vào trường “Audio”, file sau sẽ đè file trước. Cần **pre-check** trước khi chạy: nếu `preset1.target_field == preset2.target_field` → cảnh báo rõ, không cho bấm Start.
2. **Tính toán Progress Bar:** Thanh tiến trình trong `batch_progress_ui.py` cần tính lại: **Tổng tác vụ = Số thẻ (Notes) × Số preset được chọn**.
3. **Rate limit API:** Nếu 2 preset dùng chung một cloud engine (ví dụ EdgeTTS) cùng lúc, tốc độ request nhân đôi, dễ bị server block IP. Cân nhắc xử lý **tuần tự** (xong preset 1 cho thẻ A → mới chạy preset 2 cho thẻ A) thay vì bất đồng bộ ồ ạt.

### Gợi ý ưu tiên

Ưu tiên **Hướng 1** trước vì không cần thay đổi cấu trúc data model trong `config.json`, chỉ cần đổi UI cửa sổ Batch và vòng lặp trong `BatchExecutor`. Ước lượng triển khai: khoảng 1–2 ngày code.

