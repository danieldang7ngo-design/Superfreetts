Superfreetts Anki Add-on
========================

👉 Xem lộ trình phát triển chi tiết: [ROADMAP](./ROADMAP.md)
🤖 Để nắm bắt nhanh cấu trúc dự án (đặc biệt cho AI), xem: [AI SUMMARY](./AI_SUMMARY.md)

## Giới thiệu

Đây là mã nguồn add-on Superfreetts cho Anki. Thư mục này đã được làm sạch, không chứa
file sinh ra trong quá trình chạy (log, tmp, cache, v.v.) để sẵn sàng:

- Cài đặt vào thư mục `addons21` của Anki
- Đẩy thẳng lên GitHub như một bản mã nguồn "clean"

## Cấu trúc chính

- `superfreetss_addon/`: Mã nguồn chính của add-on (Python, UI, logic xử lý)
- `PROJECT_DOCUMENTATION.md`: Tài liệu thiết kế / mô tả chi tiết chức năng bên trong add-on
- `README.md`: Tệp mô tả ngắn gọn cho GitHub và người dùng

Có thể còn một số thư mục/tệp khác tùy theo phiên bản add-on, nhưng sẽ không bao gồm:

- `__pycache__/`
- File `*.pyc`, `*.pyo`
- File log tạm (`*.log`), file tạm (`*.tmp`) hoặc file backup (`*.bak`, `*~`)

## Cài đặt (Anki)

1. Đảm bảo Anki đã đóng.
2. Sao chép thư mục `Superfreetts` này vào:
   - Windows: `C:\\Users\\<TênUser>\\AppData\\Roaming\\Anki2\\addons21\\`
3. Mở lại Anki, add-on sẽ tự động được nạp.

## Phát triển / Đóng góp

- Sửa mã nguồn trong thư mục `superfreetss_addon/`.
- Khi debug hoặc chạy test, có thể sinh ra các file log/tạm; trước khi đóng gói/commit,
  hãy xóa chúng để giữ repo sạch.

Đề xuất khi phát triển:

- Không commit các file log, cache, file tạm.
- Nếu thêm test, để chúng trong thư mục `tests/` (nếu có), có thể giữ lại trên GitHub
  nhưng không cần copy vào bản phát hành đưa vào `addons21` khi phân phối cho người dùng.

