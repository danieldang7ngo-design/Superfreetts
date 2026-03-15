Superfreetts Roadmap
=====================

## Mục tiêu tổng thể

Add-on Superfreetts giúp người dùng Anki tạo audio từ text **miễn phí**, ổn định và dễ dùng, hỗ trợ nhiều giọng đọc (EdgeTTS) và tối ưu cho workflow học thẻ nhanh.

## Giai đoạn 1 – Ổn định & dọn dẹp

- Cố định đa luồng (multithreading) khi generate nhiều audio liên tiếp.
- Giảm lỗi treo UI Anki khi hàng đợi audio lớn.
- Chuẩn hóa cấu trúc thư mục: tách rõ `superfreetss_addon/`, `external/`, `graphics/`, `tests/`.
- Thêm log thân thiện (file log riêng) để dễ debug, không làm chậm add-on.

## Giai đoạn 2 – UX/UI thân thiện hơn

- Thiết kế lại cửa sổ cấu hình:
  - Gom nhóm các tùy chọn quan trọng (ngôn ngữ, giọng, tốc độ đọc) ở trên cùng.
  - Giải thích ngắn gọn từng option bằng tiếng Việt.
- Thêm trạng thái tiến trình khi generate audio:
  - Thanh tiến trình đơn giản hoặc label đếm số file đã xử lý.
  - Thông báo khi hoàn tất hoặc khi có lỗi.
- Cải thiện thông báo lỗi: câu chữ dễ hiểu, gợi ý cách tự xử lý.

## Giai đoạn 3 – Tối ưu hiệu suất

- Cache kết quả TTS cho cùng một đoạn text (tránh gọi API nhiều lần).
- Tùy chọn giới hạn số luồng chạy song song để tránh quá tải CPU.
- Tối ưu việc ghi file audio (giảm số lần mở/đóng file).

## Giai đoạn 4 – Nâng cao tính năng

- Hỗ trợ preset cấu hình:
  - Lưu nhiều bộ thiết lập giọng đọc (Preset A/B/C) để đổi nhanh theo deck.
- Cho phép chọn thư mục lưu audio tùy chỉnh (nếu người dùng muốn quản lý ngoài).
- Tùy chọn thêm prefix/suffix vào tên file audio để dễ nhận diện.

## Giai đoạn 5 – Chất lượng & cộng đồng

- Bổ sung bộ test tự động trong thư mục `tests/`.
- Ghi lại các case lỗi phổ biến và cách xử lý trong tài liệu.
- Viết hướng dẫn chi tiết hơn trong `PROJECT_DOCUMENTATION.md` và `README.md`.

## Góp ý & đóng góp

- Người dùng có thể mở issue/pull request trên GitHub để:
  - Đề xuất tính năng mới.
  - Báo lỗi cụ thể (kèm log, phiên bản Anki).
  - Gửi patch cải thiện hiệu suất hoặc UX.

