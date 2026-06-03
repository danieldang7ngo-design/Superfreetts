# Changelog

## 1.3.4 - 2026-06-03

### English

- Updated Workflow to generate audio for all presets first, then wait before writing sound tags to notes.
- Added `Apply Selected Preset` so a generated workflow preset can be applied one at a time.
- Added `Apply All` so all generated workflow preset results can be applied in one pass.
- Marked generated workflow presets as ready to apply in the Workflow list.
- Added a headphone icon to the AnkiVN menu entry: `🎧 Super Free TTS Settings`.
- Localized EdgeTTS Advanced Settings labels in the Services settings page.
- Split locale dictionaries into separate JSON files under `superfreetts_addon/locales/` so future translations do not bloat `i18n.py`.
- Added UI language options for Simplified Chinese, Traditional Chinese (Taiwan), and Japanese.

### Tiếng Việt

- Cập nhật Workflow để tạo audio cho toàn bộ preset trước, rồi chờ trước khi ghi sound tag vào note.
- Thêm `Apply Selected Preset` để áp dụng từng preset workflow đã tạo.
- Thêm `Apply All` để áp dụng toàn bộ kết quả workflow đã tạo trong một lượt.
- Hiển thị preset workflow đã tạo ở trạng thái sẵn sàng áp dụng trong danh sách Workflow.
- Thêm icon tai nghe cho menu AnkiVN: `🎧 Super Free TTS Settings`.
- Bổ sung bản dịch cho nhãn Cài đặt nâng cao của EdgeTTS trong trang Services.
- Tách dictionary ngôn ngữ thành từng file JSON riêng trong `superfreetts_addon/locales/` để sau này thêm ngôn ngữ mới không làm `i18n.py` phình to.
- Bổ sung tùy chọn ngôn ngữ giao diện cho tiếng Trung Giản thể, tiếng Trung Phồn thể (Đài Loan) và tiếng Nhật.

### Korean

- 워크플로가 모든 프리셋의 오디오를 먼저 생성한 뒤 노트에 sound tag를 쓰기 전에 대기하도록 업데이트했습니다.
- 생성된 워크플로 프리셋을 하나씩 적용할 수 있도록 `Apply Selected Preset`을 추가했습니다.
- 생성된 워크플로 프리셋 결과를 한 번에 적용할 수 있도록 `Apply All`을 추가했습니다.
- 워크플로 목록에서 생성 완료된 프리셋을 적용 준비 상태로 표시합니다.
- AnkiVN 메뉴 항목에 헤드폰 아이콘을 추가했습니다: `🎧 Super Free TTS Settings`.
- Services 설정 페이지의 EdgeTTS 고급 설정 라벨을 현지화했습니다.
- 향후 번역이 `i18n.py`를 비대하게 만들지 않도록 locale dictionary를 `superfreetts_addon/locales/`의 언어별 JSON 파일로 분리했습니다.
- 중국어 간체, 중국어 번체(대만), 일본어 UI 언어 옵션을 추가했습니다.

### 简体中文

- Workflow 现在会先为所有预设生成音频，然后等待写入 sound tag 到笔记。
- 新增 `Apply Selected Preset`，可逐个应用已生成的 workflow 预设。
- 新增 `Apply All`，可一次性应用所有已生成的 workflow 预设结果。
- 已生成的 workflow 预设会在 Workflow 列表中标记为可应用。
- AnkiVN 菜单项现在显示耳机图标：`🎧 Super Free TTS Settings`。
- Services 设置页中的 EdgeTTS 高级设置标签已本地化。
- Locale dictionary 已拆分为 `superfreetts_addon/locales/` 下的独立 JSON 文件，避免 `i18n.py` 后续膨胀。
- 新增简体中文、繁体中文（台湾）和日语的界面语言选项。

### 繁體中文（台灣）

- Workflow 現在會先為所有預設生成音訊，然後等待將 sound tag 寫入筆記。
- 新增 `Apply Selected Preset`，可逐個套用已生成的 workflow 預設。
- 新增 `Apply All`，可一次套用所有已生成的 workflow 預設結果。
- 已生成的 workflow 預設會在 Workflow 清單中標記為可套用。
- AnkiVN 選單項目現在顯示耳機圖示：`🎧 Super Free TTS Settings`。
- Services 設定頁中的 EdgeTTS 進階設定標籤已在地化。
- Locale dictionary 已拆分為 `superfreetts_addon/locales/` 下的獨立 JSON 檔案，避免 `i18n.py` 之後過度膨脹。
- 新增簡體中文、繁體中文（台灣）和日文的介面語言選項。

### Japanese

- Workflow はすべてのプリセットの音声を先に生成し、sound tag をノートへ書き込む前に待機するようになりました。
- 生成済みの workflow プリセットを個別に適用できる `Apply Selected Preset` を追加しました。
- 生成済みの workflow プリセット結果を一括で適用できる `Apply All` を追加しました。
- 生成済みの workflow プリセットは Workflow リストで適用準備完了として表示されます。
- AnkiVN メニュー項目にヘッドホンアイコンを追加しました：`🎧 Super Free TTS Settings`。
- Services 設定ページの EdgeTTS 詳細設定ラベルをローカライズしました。
- Locale dictionary を `superfreetts_addon/locales/` 配下の言語別 JSON ファイルに分割し、今後 `i18n.py` が肥大化しないようにしました。
- 簡体字中国語、繁体字中国語（台湾）、日本語の UI 言語オプションを追加しました。

## 1.3.3 - 2026-05-22

### English

- Reduced duplicate TTS calls in large batches by caching processed text and deduplicating audio requests by processed text, voice, voice options, and output format.
- Improved audio file caching and writes with stable request hashes, non-empty disk cache checks, and atomic writes for generated audio files.
- Split source text resolution, audio file storage, and note audio updates out of `superfreetss.py` so the core batch path is easier to test and refactor.
- Added regression coverage for text/source resolution, audio file storage, batch cache/dedup behavior, note updates, text processing, and psutil integration.
- Kept the current user workflow and UI behavior unchanged.

### Tiếng Việt

- Giảm gọi TTS trùng lặp trong batch lớn bằng cache processed text và dedup request audio theo processed text, voice, voice options và định dạng đầu ra.
- Cải thiện cache/ghi file audio với hash request ổn định, chỉ dùng disk cache khi file tồn tại và không rỗng, và ghi file theo cơ chế atomic.
- Tách xử lý source text, lưu file audio, và cập nhật sound tag của note ra khỏi `superfreetss.py` để core batch dễ test và dễ refactor tiếp.
- Bổ sung regression test cho resolver text/source, audio file store, batch cache/dedup, note updater, text processing và psutil.
- Giữ nguyên workflow và hành vi UI hiện tại.

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

### Tiếng Việt

- Đổi file audio tạo mới sang prefix `superfreetts-<hash>`.
- Giữ nguyên các file audio cache cũ `superfreetss-*`; chúng vẫn hợp lệ.

## 1.2 - 2026-04-29

### English

- Improved EdgeTTS stability with retry, empty-audio detection, Unicode text cleanup, and clearer no-audio/rate-limit logging.
- Reworked EdgeTTS generation to run in ordered waves of up to three requests, keeping progress easier to follow from top to bottom.
- Added Advanced EdgeTTS controls for retry attempts, request jitter, wave start stagger, retry backoff, and concurrency.
- Fixed Priority voice selection so it now falls back to a second voice if the first voice fails, and similarly if more voices are configured.
- Added the new `Sequence` voice selection mode, which cycles through selected voices in order and loops back to the first voice.
- Added direct EdgeTTS verification scripts, including `tests/verify_edgetts.py`.
- Added a local `async_timeout` compatibility shim so the bundled `aiohttp` imports correctly under the integrated Python 3.10 runtime.

### Tiếng Việt

- Cải thiện độ ổn định của EdgeTTS với retry, kiểm tra audio rỗng, làm sạch Unicode và log rõ hơn khi bị no-audio/rate-limit.
- Đổi EdgeTTS sang cơ chế wave tối đa 3 request theo thứ tự từ trên xuống, giúp tiến trình dễ theo dõi hơn.
- Thêm các tùy chọn Advanced cho EdgeTTS: retry attempts, request jitter, wave start stagger, retry backoff và concurrency.
- Thêm mode chọn giọng mới `Sequence`, dùng giọng theo thứ tự đã chọn và quay lại giọng đầu khi hết danh sách.
- Thêm script kiểm tra EdgeTTS trực tiếp, gồm `tests/verify_edgetts.py`.
- Thêm shim `async_timeout` cục bộ để `aiohttp` bundled import được với Python 3.10 tích hợp.

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

- Thiết kế lại tab `About` với hero layout mới, các info card dễ quét và khu vực liên kết ngoài riêng biệt.
- Thêm liên kết GitHub vào tab `About` và chuyển footer sang dùng text từ i18n.
- Cập nhật style badge phiên bản trong `About` và bỏ viền ở khu `Open Links` để bố cục gọn hơn.

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
