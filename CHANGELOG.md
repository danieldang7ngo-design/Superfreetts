# Changelog

## 1.3.3 - 2026-05-22

### English

- Reduced duplicate TTS calls in large batches by caching processed text and deduplicating audio requests by processed text, voice, voice options, and output format.
- Improved audio file caching and writes with stable request hashes, non-empty disk cache checks, and atomic writes for generated audio files.
- Split source text resolution, audio file storage, and note audio updates out of `superfreetss.py` so the core batch path is easier to test and refactor.
- Added regression coverage for text/source resolution, audio file storage, batch cache/dedup behavior, note updates, text processing, and psutil integration.
- Kept the current user workflow and UI behavior unchanged.

### Tieng Viet

- Giam goi TTS trung lap trong batch lon bang cache processed text va dedup request audio theo processed text, voice, voice options va dinh dang dau ra.
- Cai thien cache/ghi file audio voi hash request on dinh, chi dung disk cache khi file ton tai va khong rong, va ghi file theo co che atomic.
- Tach xu ly source text, luu file audio, va cap nhat sound tag cua note ra khoi `superfreetss.py` de core batch de test va de refactor tiep.
- Bo sung regression test cho resolver text/source, audio file store, batch cache/dedup, note updater, text processing va psutil.
- Giu nguyen workflow va hanh vi UI hien tai.

### Korean

- 대규모 배치 작업에서 처리된 텍스트를 캐싱하고, 처리된 텍스트·음성·음성 옵션·출력 형식을 기준으로 오디오 요청을 중복 제거하여 중복 TTS 호출을 줄였습니다.
- 안정적인 요청 해시, 비어 있지 않은 디스크 캐시 확인, 생성된 오디오 파일의 원자적 쓰기(atomic write)를 통해 오디오 파일 캐싱 및 저장 방식을 개선했습니다.
- 핵심 배치 경로를 더 쉽게 테스트하고 리팩터링할 수 있도록, 원본 텍스트 해석·오디오 파일 저장·노트 오디오 업데이트 로직을 `superfreetss.py`에서 분리했습니다.
- 텍스트/원본 해석, 오디오 파일 저장, 배치 캐시 및 중복 제거 동작, 노트 업데이트, 텍스트 처리, 그리고 psutil 통합에 대한 회귀 테스트 커버리지를 추가했습니다.
- 기존 사용자 워크플로우와 UI 동작은 변경 없이 그대로 유지했습니다.


## 1.3.2 - 2026-05-16

### English

- Streamlined the Settings layout and cleaned up the release-note wording shown to users.
- Kept the Generate then Apply workflow unchanged.

### Tiếng Việt

- Tinh gọn bố cục Cài đặt và làm sạch cách diễn đạt của phần ghi chú phát hành hiển thị cho người dùng.
- Giữ nguyên workflow Tạo rồi Áp dụng.

### Korean

- 설정 레이아웃을 정리하고 사용자에게 보이는 릴리스 노트 문구를 다듬었습니다.
- Generate 후 Apply 흐름은 그대로 유지됩니다.

## 1.3.0 - 2026-05-16

### English

- Adjusted public EdgeTTS concurrency for stability.
- Kept the Generate then Apply workflow: audio is generated first, then notes are updated only after `Apply Generated Audio`.

### Tiếng Việt

- Điều chỉnh mức đồng thời của EdgeTTS bản phát hành để ổn định hơn.
- Giữ workflow Tạo rồi Áp dụng: âm thanh được tạo trước, sau đó note chỉ được cập nhật khi bấm `Apply Generated Audio`.

### Korean

- Public addon builds now use a safer EdgeTTS concurrency cap.
- The Generate then Apply workflow remains unchanged: audio is generated first, then notes are updated only after `Apply Generated Audio`.

## 1.2.2 - 2026-05-16

### English

- Changed Generate Audio so it generates audio files first and waits for the user to click `Apply Generated Audio` before updating notes.
- Added a forced Anki backup step before applying generated audio to the collection.
- Added `Generated` row status so preview results are distinct from notes that have actually been updated.
- Improved large EdgeTTS batch progress with active heartbeat text, safer per-request timeout handling, and one-request EdgeTTS chunking.

### Tiếng Việt

- Đổi Generate Audio để chỉ tạo file âm thanh trước; note chỉ được cập nhật sau khi người dùng bấm `Apply Generated Audio`.
- Thêm bước gọi backup của Anki trước khi áp dụng âm thanh đã tạo vào collection.
- Thêm trạng thái dòng `Generated` để phân biệt kết quả preview với note đã được update thật sự.
- Cải thiện tiến trình batch EdgeTTS lớn với heartbeat đang chạy, timeout an toàn hơn cho từng request, và chunk EdgeTTS mỗi chunk một request.

### Korean

- Generate Audio now creates audio files first; notes are updated only after clicking `Apply Generated Audio`.
- Anki backup is triggered before generated audio is applied to the collection.
- Added `Generated` row status so generated preview results are separate from fully updated notes.
- Improved large EdgeTTS batch progress with active status text, safer per-request timeout handling, and one-request EdgeTTS chunking.

## 1.2.1 - 2026-05-11

### English

- Changed newly generated audio filenames to use the `superfreetts-<hash>` prefix.
- Kept existing `superfreetss-*` cached audio files valid and unchanged.

### Tieng Viet

- Doi file audio tao moi sang prefix `superfreetts-<hash>`.
- Giu nguyen cac file audio cache cu `superfreetss-*`; chung van hop le.

## 1.2 - 2026-04-29

### English

- Improved EdgeTTS stability with retry, empty-audio detection, Unicode text cleanup, and clearer no-audio/rate-limit logging.
- Reworked EdgeTTS generation to run in ordered waves of up to three requests, keeping progress easier to follow from top to bottom.
- Added Advanced EdgeTTS controls for retry attempts, request jitter, wave start stagger, retry backoff, and concurrency.
- Fixed Priority voice selection so it now falls back to a second voice if the first voice fails, and similarly if more voices are configured.
- Added the new `Sequence` voice selection mode, which cycles through selected voices in order and loops back to the first voice.
- Added direct EdgeTTS verification scripts, including `tests/verify_edgetts.py`.
- Added a local `async_timeout` compatibility shim so the bundled `aiohttp` imports correctly under the integrated Python 3.10 runtime.

### Tieng Viet

- Cai thien do on dinh cua EdgeTTS voi retry, kiem tra audio rong, lam sach Unicode va log ro hon khi bi no-audio/rate-limit.
- Doi EdgeTTS sang co che wave toi da 3 request theo thu tu tu tren xuong, giup tien trinh de theo doi hon.
- Them cac tuy chon Advanced cho EdgeTTS: retry attempts, request jitter, wave start stagger, retry backoff va concurrency.
- Them mode chon giong moi `Sequence`, dung giong theo thu tu da chon va quay lai giong dau khi het danh sach.
- Them script kiem tra EdgeTTS truc tiep, gom `tests/verify_edgetts.py`.
- Them shim `async_timeout` cuc bo de `aiohttp` bundled import duoc voi Python 3.10 tich hop.

## 1.1.2 - 2026-04-24

### English

- Added Korean as a supported UI language and expanded the Preferences language picker.
- Localized the main Settings dialogs, About tab, Workflow, Failure Report, and shared browser/editor controls for Korean.
- Fixed the Preferences language combobox so it restores the saved language correctly after reopening Settings.
- Updated the addon version and release notes flow so Korean users see localized update text.
- Added workflow function so you can now generate with multiple presets at the same time

### Tiếng Việt

- Bổ sung tiếng Hàn như một ngôn ngữ giao diện được hỗ trợ và mở rộng bộ chọn ngôn ngữ trong Preferences.
- Dịch các hộp thoại Settings chính, tab About, Workflow, Failure Report và các điều khiển chung trong browser/editor sang tiếng Hàn.
- Sửa combobox ngôn ngữ trong Preferences để nó khôi phục đúng ngôn ngữ đã lưu khi mở lại Settings.
- Cập nhật version addon và luồng release notes để người dùng tiếng Hàn thấy nội dung cập nhật đã được bản địa hóa.
- Thêm cơ chế workflow nên bây giờ bạn có thể tạo âm thanh với nhiều preset cùng lúc. 

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
