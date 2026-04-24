# Changelog

## 1.1.2 - 2026-04-24

### English

- Added Korean as a supported UI language and expanded the Preferences language picker.
- Localized the main Settings dialogs, About tab, Workflow, Failure Report, and shared browser/editor controls for Korean.
- Fixed the Preferences language combobox so it restores the saved language correctly after reopening Settings.
- Updated the addon version and release notes flow so Korean users see localized update text.

### Tiếng Việt

- Bổ sung tiếng Hàn như một ngôn ngữ giao diện được hỗ trợ và mở rộng bộ chọn ngôn ngữ trong Preferences.
- Dịch các hộp thoại Settings chính, tab About, Workflow, Failure Report và các điều khiển chung trong browser/editor sang tiếng Hàn.
- Sửa combobox ngôn ngữ trong Preferences để nó khôi phục đúng ngôn ngữ đã lưu khi mở lại Settings.
- Cập nhật version addon và luồng release notes để người dùng tiếng Hàn thấy nội dung cập nhật đã được bản địa hóa.

## 1.1.1 - 2026-04-24

### English

- Refactored the Settings window into modular components: `Settings`, `Services`, `Preferences`, and `Troubleshooting`.
- Split the previous unified settings implementation into dedicated modules and updated the main UI wiring accordingly.
- Fixed incorrect `Preferences` translations where English could show Vietnamese or mojibake text.
- Added the missing Vietnamese translations for the new `Preferences` sections and helper text.
- Redesigned the `About` tab with a new hero layout, scan-friendly info cards, and a dedicated external links section.
- Added a GitHub link to the `About` tab and moved the footer text to i18n resources.
- Updated the `About` version badge styling and removed the border from the `Open Links` section for a cleaner layout.

### Tiếng Việt

- Tái cấu trúc cửa sổ `Settings` thành các component riêng: `Settings`, `Services`, `Preferences` và `Troubleshooting`.
- Tách phần cài đặt hợp nhất trước đây thành các module chuyên biệt và cập nhật lại phần nối UI chính cho phù hợp.
- Sửa lỗi bản dịch trong `Preferences` khiến giao diện tiếng Anh có thể hiển thị tiếng Việt hoặc chuỗi lỗi mã hóa.
- Bổ sung các bản dịch tiếng Việt còn thiếu cho các section mới trong `Preferences` và các helper text liên quan.

- Thiáº¿t káº¿ láº¡i tab `About` vá»›i hero layout má»›i, cÃ¡c info card dá»… quÃ©t vÃ  khu vá»±c liÃªn káº¿t ngoÃ i riÃªng biá»‡t.
- ThÃªm liÃªn káº¿t GitHub vÃ o tab `About` vÃ  chuyá»ƒn footer sang dÃ¹ng text tá»« i18n.
- Cáº­p nháº­t style badge phiÃªn báº£n trong `About` vÃ  bá» viá»n á»Ÿ khu `Open Links` Ä‘á»ƒ bÃ´ cá»¥c gá»n hÆ¡n.

## 1.1.0 - 2026-04-22

### English

- Renamed the batch dialog to `Generate Audio Files` so the window title matches the Browser menu.
- Added `Workflow` to the `Super Free TTS` menu in the Browser for running multi-preset flows from selected notes.
- Added a `New` preset button and removed the unused `Open` flow from the preset toolbar.
- Updated the main batch action label to `Generate Audio` and cleaned up preset switching behavior.
- Hid the editor-only selected-text option from batch mode to avoid confusion when many notes are selected.
- Added localized startup announcements: new installs see `Welcome`, while existing users see `What's New` after updates.

### Tiếng Việt

- Đổi tên hộp thoại batch thành `Generate Audio Files` để title cửa sổ khớp với menu trong Browser.
- Thêm `Workflow` vào menu `Super Free TTS` trong Browser để chạy luồng nhiều preset trên các note đang chọn.
- Thêm nút `New` cho preset và bỏ luồng `Open` không còn cần thiết trong thanh preset.
- Đổi nhãn nút chạy batch thành `Generate Audio` và làm gọn hành vi chuyển preset.
- Ẩn tùy chọn chọn đoạn văn bản khỏi batch mode vì tính năng này chỉ phù hợp với editor của một note.
- Thêm popup thông báo khởi động theo ngôn ngữ: cài mới sẽ thấy `Welcome`, còn người cập nhật addon sẽ thấy `What's New`.
