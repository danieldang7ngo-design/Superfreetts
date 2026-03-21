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
| **P0** | **Unified Settings + AnkiVN Menu** | **In Progress** | **PRIORITY: Gộp Config+Pref, menu top-level** |
| 1    | Ổn định & dọn dẹp            | Planned     | Đa luồng, crash, cấu trúc, log    |
| 2    | UX & cấu hình                | Planned     | UI config, speed/pitch, preview   |
| 3    | Hiệu suất & cache            | Planned     | Queue lớn, IO, cache text        |
| 4    | Tính năng nâng cao           | Planned     | Preset, naming, folder            |
| 5    | Test, tài liệu & cộng đồng   | Planned     | Test, docs, guideline, issue flow |

---

## Phase P0 – Unified Settings UI & AnkiVN Menu Integration

**[TOP PRIORITY - MUST DO FIRST]**

- **Mục tiêu chính**
  - Gộp Configuration dialog + Preferences dialog thành một thống nhất "Super Free TTS Settings" với 2 tab: Services & Preferences.
  - Đưa entry point chính từ Tools menu vào menu top-level mới "AnkiVN" (ngang hàng với Tools, Edit, File).
  - Đảm bảo cả hai cấu hình (Services + Preferences) có thể được chỉnh sửa và lưu trong một phiên thao tác.

- **Các hạng mục chính**
  - [Priority: Critical] Tạo unified settings dialog với QTabWidget (Services tab + Preferences tab)
    - Tái sử dụng component hiện có từ `component_configuration.py` và `component_preferences.py`
    - Thực hiện save flow thống nhất: save Configuration → save Preferences → reconfigure ServiceManager
  - [Priority: Critical] Tạo menu AnkiVN top-level trên main menubar
    - Insert trước Help menu nếu khả dụng, else append cuối cùng
    - Thêm action "Super Free TTS" mở unified dialog
  - [Priority: High] Cập nhật i18n keys cho unified title, tab labels
    - Giữ key cũ cho backward-compatibility
  - [Priority: Medium] Giữ backward-compatible wrapper: Tools menu actions redirect tới unified dialog (tạm thời)
  - [Priority: Medium] Fallback mechanism nếu top-level insert API fail ở bản Anki cũ

- **Definition of Done**
  - Main menu bar hiển thị menu "AnkiVN" ngang hàng Tools
  - Click "AnkiVN" → "Super Free TTS" mở 1 dialog duy nhất với 2 tab rõ ràng
  - Chỉnh sửa Services (enable/config) + Preferences (language/cache/…) trong cùng phiên, click Save → cả hai lưu được
  - Không duplicate menu sau addon reload
  - Browser menu và editor buttons không bị ảnh hưởng
  - Tài liệu (ROADMAP, PROJECT_DOCUMENTATION, README) được cập nhật phản ánh entry point mới

---

## Phase 1 – Core Stability & Cleanup

- **Mục tiêu chính**
  - Hạn chế tối đa việc treo hoặc crash Anki khi sử dụng Superfreetts.
  - Chuẩn hoá cấu trúc dự án và logging để dễ debug và bảo trì.

- **Các hạng mục chính**
  - [Priority: High] Cố định đa luồng (multithreading) khi generate nhiều audio liên tiếp.
  - [Priority: High] Giảm lỗi treo UI Anki khi hàng đợi audio lớn (quản lý queue và luồng nền hợp lý).
  - [Priority: Medium] Chuẩn hóa cấu trúc thư mục: tách rõ `superfreetss_addon/`, `external/`, `graphics/`, `tests/`.
  - [Priority: Medium] Thêm log thân thiện (file log riêng) để dễ debug mà không làm chậm add-on.

- **Definition of Done**
  - Có thể generate nhiều trăm thẻ liên tiếp trong bài test nội bộ mà không crash Anki.
  - Các lỗi quan trọng (exception) đều được ghi log có thể đọc lại.
  - Cấu trúc thư mục thống nhất với tài liệu (`PROJECT_DOCUMENTATION.md`).

## Phase 2 – UX & Configuration Experience

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

