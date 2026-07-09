# Changelog

## 26.7.2 - 2026-07-09

### English

- Fixed batch preview showing only 1 note per page during preview (must_continue=False causing break after first note).
- Fixed batch preview dataChanged range using widened loaded_note_ids instead of exact page rows, causing cached empty values for unloaded rows.
- Changed batch preview to load all pages sequentially on dialog open instead of 2-3 visible pages on scroll.
- Added viewport repaint after each page load to force table UI refresh.
- Added notes-loaded callback so the Generate button stays disabled until all notes are fully loaded; re-disabled on settings change until reload completes.
- Updated status label to show "Loading X of Y notes" during preview page loading, then "Loaded X of Y notes" when done.
- Separated EdgeTTS TimeoutError from connectivity errors; timeouts no longer trigger 60s global connectivity backoff and are retried like other errors.
- Increased EdgeTTS per-request timeout from 30s to 180s for Vietnamese/diacritic text.
- Increased EdgeTTS retry backoff from 3s to 5s and connectivity backoff from 15s to 60s.
- Added retry delay jitter and connectivity-failure-aware retry delay extension to EdgeTTS.
- Connectivity failures in EdgeTTS no longer return immediately but retry like other errors.
- Connectivity check no longer double-marks failure on repeated checks.
- Added `backup_guard` module to suppress Anki's "Creating backup" dialog and periodic backup timer during batch generate/apply phases.
- Moved undo entry creation inside each apply chunk (instead of one undo entry spanning all chunks), matching `col.update_notes()` read/write pattern.
- Added `backup_guard.disable_backups()`/`restore_backups()` calls during generate and apply phases.
- Optimized `get_all_fields_from_notes` to chunk SQL queries (500 per batch) instead of one `get_note_by_id` call per note.
- Updated default offline TTS engine workers (Piper, Kokoro, etc.) from 1 to CPU-count-based default.
- Removed `timeout` parameter from executor shutdown calls.
- Show total note count in progress bar label during deduped generation: "{completed}/{unique} unique • {total} notes".
- Pre-populate note_status_map during generation for notes missed by lazy loading.
- Fill missing dedup keys with error when submit thread fails or is cancelled.
- Created `set_edge_workers_20.py` helper script.
- Added regression tests for EdgeTTS sequence mode and Vietnamese batch behavior.
- Enabled debug logging by default for troubleshooting.

### Tiếng Việt

- Sửa lỗi batch preview chỉ hiển thị 1 note mỗi trang trong giai đoạn xem trước.
- Sửa lỗi dataChanged dùng loaded_note_ids bị mở rộng thay vì hàng chính xác của trang, khiến các hàng chưa tải bị cache giá trị rỗng.
- Đổi batch preview sang tải tuần tự tất cả các trang khi mở hộp thoại thay vì chỉ tải 2-3 trang khi cuộn.
- Thêm viewport.update() sau mỗi lần tải trang để buộc refresh bảng.
- Thêm callback tải xong để nút Generate bị vô hiệu hóa cho đến khi tất cả notes được tải đầy đủ.
- Cập nhật nhãn trạng thái hiển thị "Đang tải X của Y notes" và "Đã tải X của Y notes".
- Tách TimeoutError khỏi lỗi kết nối EdgeTTS; timeout không còn kích hoạt backoff 60s toàn cục nữa.
- Tăng timeout mỗi request EdgeTTS từ 30s lên 180s cho text tiếng Việt có dấu.
- Tăng retry backoff EdgeTTS từ 3s lên 5s và connectivity backoff từ 15s lên 60s.
- Thêm jitter cho retry delay và mở rộng retry delay khi có lỗi kết nối.
- Lỗi kết nối EdgeTTS không còn trả về ngay lập tức mà được retry như các lỗi khác.
- Thêm module backup_guard để chặn hộp thoại "Creating backup" và timer backup định kỳ.
- Di chuyển undo entry vào từng chunk apply thay vì một undo entry cho toàn bộ chuỗi apply.
- Tối ưu get_all_fields_from_notes bằng chunk SQL (500 note mỗi batch).
- Cập nhật worker mặc định cho engine TTS ngoại tuyến từ 1 lên dựa trên số CPU.
- Hiển thị tổng số notes trong nhãn progress bar khi generation có dedup.
- Tạo script helper set_edge_workers_20.py.

### English

- Updated addon versioning to 26.7.1 using the AMD-style release format: year.month.release, so 26.7.1 means the first release in July 2026.
- Added Anki collection path handling so database access follows the active profile path.
- Added note-loading helpers and lazy note list scaffolding for smoother handling of large note sets.
- Verified the packaged addon includes the new DB helper and related modules in the built archive.

### Tiếng Việt

- Cập nhật số phiên bản addon thành 26.7.1 theo quy ước phát hành kiểu AMD.
- Thêm xử lý đường dẫn collection của Anki để truy cập DB theo profile đang hoạt động.
- Thêm helper tải note và khung danh sách note lười để xử lý lượng note lớn mượt hơn.

### 🇰🇷 한국어

* AMD 스타일 릴리스 규칙에 따라 애드온 버전을 26.7.1로 업데이트했습니다.
* 활성 프로필 경로를 따르도록 Anki collection 경로 처리를 추가했습니다.
* 대량 노트 처리에 더 부드럽게 대응하도록 노트 로딩 헬퍼와 지연 로딩 리스트 스캐폴딩을 추가했습니다.

### 🇨🇳 简体中文

* 按照 AMD 风格的版本规则，将插件版本更新为 26.7.1。
* 新增 Anki collection 路径处理，数据库访问将遵循当前活跃配置文件路径。
* 新增笔记加载辅助逻辑与懒加载笔记列表骨架，以更顺畅地处理大量笔记。

### 🇹🇼 繁體中文

* 依照 AMD 風格的版本規則，將外掛版本更新為 26.7.1。
* 新增 Anki collection 路徑處理，資料庫存取將遵循目前使用中的設定檔路徑。
* 新增筆記載入輔助邏輯與延遲載入筆記清單骨架，以更順暢處理大量筆記。

### 🇯🇵 日本語

* AMD 形式のバージョン体系に合わせて、アドオンのバージョンを 26.7.1 に更新しました。
* Anki の collection パスを利用するようにし、現在のアクティブプロファイルに合わせて DB へアクセスするようにしました。
* 大量ノートをより滑らかに扱えるよう、ノート読み込みヘルパーと遅延読み込みリストの土台を追加しました。

### 🇸🇪 Svenska

* Uppdaterade tilläggsversionen till 26.7.1 enligt AMD-liknande versionsschema.
* Lade till hantering av Anki collection-sökväg så att databasanvändning följer den aktiva profilen.
* Lade till hjälpfunktioner för att ladda anteckningar och en lat liststruktur för smidigare hantering av stora anteckningsmängder.

## 1.4 - 2026-07-05

### English

- Refactored `superfreetts.py` God Class into dedicated modules for better separation of concerns.
- Added Supertonic TTS support and worker fixes.
- Fixed UI workflow issues and resolved `NameError` in `batch_orchestrator.py`.
- Added automated test suite and GitHub Actions CI.
- Synced addon code and dependencies.

### Tiếng Việt

- Tái cấu trúc `superfreetts.py` God Class thành các module riêng để phân tách chức năng tốt hơn.
- Hỗ trợ Supertonic TTS và sửa worker.
- Sửa lỗi UI workflow và `NameError` trong `batch_orchestrator.py`.
- Thêm bộ test tự động và GitHub Actions CI.
- Đồng bộ hóa mã nguồn và các dependency của addon.

### 🇰🇷 한국어

* 유지보수성과 관심사 분리를 개선하기 위해 `superfreetts.py`의 God Class를 전용 모듈로 리팩터링했습니다.
* Supertonic TTS 지원 및 워커 관련 문제를 추가 및 수정했습니다.
* UI 워크플로 문제를 수정하고 `batch_orchestrator.py`의 `NameError`를 해결했습니다.
* 자동화된 테스트 스위트와 GitHub Actions CI를 추가했습니다.
* 애드온 코드와 의존성을 동기화했습니다.

### 🇨🇳 简体中文

* 重构了 `superfreetts.py` 中的 God Class，将其拆分为多个独立模块，以提升关注点分离和可维护性。
* 新增 Supertonic TTS 支持，并修复了 Worker 相关问题。
* 修复了 UI 工作流程问题，并解决了 `batch_orchestrator.py` 中的 `NameError`。
* 新增自动化测试套件和 GitHub Actions CI。
* 同步了插件代码及依赖项。

### 🇹🇼 繁體中文

* 重構 `superfreetts.py` 中的 God Class，將其拆分為多個獨立模組，以改善關注點分離與可維護性。
* 新增 Supertonic TTS 支援，並修正 Worker 相關問題。
* 修正 UI 工作流程問題，並解決 `batch_orchestrator.py` 中的 `NameError`。
* 新增自動化測試套件與 GitHub Actions CI。
* 同步外掛程式程式碼與相依性。

### 🇯🇵 日本語

* 関心の分離と保守性を向上させるため、`superfreetts.py` の God Class を専用モジュールへリファクタリングしました。
* Supertonic TTS のサポートを追加し、ワーカー関連の問題を修正しました。
* UI ワークフローの問題を修正し、`batch_orchestrator.py` の `NameError` を解消しました。
* 自動テストスイートと GitHub Actions CI を追加しました。
* アドオンのコードと依存関係を同期しました。

### 🇸🇪 Svenska

* Refaktorerade God Class i `superfreetts.py` till dedikerade moduler för bättre ansvarsfördelning och enklare underhåll.
* Lade till stöd för Supertonic TTS och åtgärdade problem relaterade till workers.
* Åtgärdade problem i användargränssnittets arbetsflöde och löste ett `NameError` i `batch_orchestrator.py`.
* Lade till ett automatiserat testpaket samt GitHub Actions CI.
* Synkroniserade tilläggets kod och beroenden.

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
