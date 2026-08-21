# Changelog

## 26.8.12 - 2026-08-22

### English

- Added four more UI themes: Nintendo 2001 (retro console chrome), Binance (dark trading with yellow CTAs), Clay (warm claymation), and Claude (warm cream-coral editorial).
- The theme selector now offers seven choices: Vibrant Blocks, Ollama, Apple, Nintendo 2001, Binance, Clay, and Claude.

### Tiếng Việt

- Thêm bốn giao diện UI nữa: Nintendo 2001 (console retro), Binance (giao diện trading tối với nút vàng), Clay (phong cách claymation ấm áp) và Claude (biên tập kem ấm với cam san hô).
- Bộ chọn giao diện giờ có bảy lựa chọn: Vibrant Blocks, Ollama, Apple, Nintendo 2001, Binance, Clay và Claude.

## 26.8.11 - 2026-08-22

### English

- New UI theme: Apple (inspired by apple.com) — clean SF Pro feel, Action Blue (#0066cc) accent, soft rounded cards.
- Theme selector now offers three choices: Vibrant Blocks, Ollama, and Apple.

### Tiếng Việt

- Giao diện mới: Apple (lấy cảm hứng từ apple.com) — phong cách SF Pro gọn gàng, điểm nhấn Action Blue (#0066cc), card bo tròn mềm mại.
- Bộ chọn giao diện giờ có ba lựa chọn: Vibrant Blocks, Ollama và Apple.

## 26.8.10 - 2026-08-22

### English

- UI Theme Selector: Added an interface theme choice in Preferences — the default "Vibrant Blocks" theme or a new "Ollama" theme (flat paper-white design with pill-shaped buttons, inspired by ollama.com).
- The Ollama theme automatically follows Anki's light/dark mode.

### Tiếng Việt

- Bộ chọn giao diện: Thêm tùy chọn giao diện trong Tùy chọn — giao diện mặc định "Vibrant Blocks" hoặc giao diện "Ollama" mới (nền trắng phẳng, nút hình viên thuốc, lấy cảm hứng từ ollama.com).
- Giao diện Ollama tự động theo chế độ sáng/tối của Anki.

## 26.8.9 - 2026-08-09

### English

- Usage Dashboard: Added a local-only Usage tab in Settings that shows what you have created with Super Free TTS — audio files generated, notes updated, characters synthesized, realtime plays, generation time, per-engine breakdown, monthly activity and recent sessions.
- Money Saved estimate: The dashboard estimates how much you saved versus a paid TTS plan ($5/month for 250,000 characters), computed locally.
- 100% private: All usage statistics are stored on your computer only (user_files/usage_log.json) and are never sent anywhere. No telemetry.

### Tiếng Việt

- Bảng thống kê sử dụng (Usage): Thêm tab Usage trong Cài đặt, chỉ hiển thị trên máy bạn, liệt kê những gì bạn đã tạo bằng Super Free TTS — số tệp âm thanh, ghi chú đã cập nhật, ký tự đã tổng hợp, lượt phát realtime, thời gian tạo, phân theo engine, hoạt động theo tháng và phiên gần đây.
- Ước tính tiền đã tiết kiệm: Bảng điều khiển ước tính số tiền bạn tiết kiệm so với gói TTS trả phí ($5/tháng cho 250.000 ký tự), tính toán cục bộ.
- 100% riêng tư: Mọi thống kê chỉ lưu trên máy bạn (user_files/usage_log.json) và không gửi đi bất cứ đâu. Không telemetry.

## 26.7.5 - 2026-07-23

### English

- macOS RAM & Crash Fixes: Implemented RAM-aware concurrency limits for neural process pools (Piper, Kokoro, MMS, Supertonic), 20s timeout for realtime audio playback, EdgeTTS background event loop reuse, and semaphore gating for macOS `say` subprocesses.
- Platform Guards: Added fail-fast checks on macOS/Linux for Windows-only Python embeddable installers (Kokoro/MMS) with user-friendly warning dialogs.
- Unsaved Preset Audio Preview: Enabled instant audio preview using current in-memory UI selections without requiring a saved preset name or pre-configured mapping rules.

### Tiếng Việt

- Khắc phục lỗi RAM & Crash trên macOS: Giới hạn số tiến trình đồng thời theo RAM khả dụng (Piper, Kokoro, MMS, Supertonic), bổ sung timeout 20s cho realtime playback, tái sử dụng event loop EdgeTTS và giới hạn subprocess `say`.
- Cảnh báo nền tảng: Bổ sung guard phát hiện hệ điều hành, thông báo rõ ràng trên macOS/Linux khi cố cài đặt engine Windows-only (Kokoro/MMS).
- Nghe thử chưa cần lưu: Hỗ trợ nghe thử âm thanh trực tiếp từ các tuỳ chọn đang chọn trên UI ngay cả khi chưa lưu Preset hoặc chưa có Mapping Rules.

### 🇰🇷 한국어

- macOS RAM 및 크래시 수정: 신경망 프로세스 풀에 RAM 인지 동시성 제한 구현, 실시간 재생 제한 시간(20초) 설정, EdgeTTS 백그라운드 이벤트 루프 재사용 및 macOS `say` 서브프로세스 제한 적용.
- 플랫폼 가드: macOS/Linux에서 Windows 전용 Python 설치 프로그램(Kokoro/MMS) 다운로드를 방지하고 명확한 경고 대화상자 표시.
- 미저장 프리셋 미리보기: 저장된 프리셋 이름이나 기존 매핑 규칙 없이도 현재 UI 설정으로 즉시 오디오 미리보기 지원.

### 🇨🇳 简体中文

- 修复 macOS 内存过载与崩溃：为神经引擎进程池增加内存感知并发限制，设置实时播放超时（20秒），复用 EdgeTTS 后台事件循环，并限制 macOS `say` 子进程并发。
- 平台保护：在 macOS/Linux 上阻止下载 Windows 专用 Python 安装程序（Kokoro/MMS），并弹出清晰警告。
- 未保存预设预览：支持直接根据当前 UI 选项进行实时音频预览，无需事先保存预设名称或配置映射规则。

### 🇹🇼 繁體中文

- 修復 macOS 記憶體過載與崩潰：為神經引擎處理程序池增加記憶體感知並發限制，設定即時播放超時（20秒），複用 EdgeTTS 後台事件循環，並限制 macOS `say` 子處理程序並發。
- 平台保護：在 macOS/Linux 上阻止下載 Windows 專用 Python 安裝程式（Kokoro/MMS），並彈出清晰警告。
- 未儲存預設預覽：支援直接根據當前 UI 選項進行即時音訊預覽，無需事先儲存預設名稱或設定對應規則。

### 🇯🇵 日本語

- macOSのメモリ過負荷とクラッシュの修正：ニューラルエンジンのプロセスプールにメモリ認識並行制限を導入、リアルタイム再生タイムアウト（20秒）を設定、EdgeTTSバックグラウンドイベントループを再利用、macOS `say`サブプロセスの並行数を制限。
- プラットフォームガード：macOS/LinuxでWindows専用のPythonインストーラー（Kokoro/MMS）のダウンロードをブロックし、明確な警告を表示。
- 未保存プリセットのプレビュー：保存されたプリセット名やマッピングルールがなくても、現在のUI設定で即座に音声プレビューが可能に。

### 🇸🇪 Svenska

- macOS-minnes- och stabilitetsfixar: Implementerade minnesmedvetna konkurrensbegränsningar för neurala processpooler, tidsgräns för realtidsuppspelning (20s), återanvändning av EdgeTTS händelseslinga och semaforspärr för macOS `say`-underprocesser.
- Plattformsspärrar: Förhindrade nedladdning av Windows-exklusiva Python-installerare (Kokoro/MMS) på macOS/Linux med tydliga varningsdialoger.
- Förhandsgranskning av osparade förinställningar: Aktiverade omedelbar förhandsgranskning av ljud med aktuella UI-inställningar utan krav på sparad förinställning eller befintliga regler.

## 26.7.4 - 2026-07-12

### English

- Optimized batch mode: Skip upfront voice pre-loading for batches under 1,000 notes, speeding up batch startup for small sets.
- Refactored service management: Merged service management component and removed legacy service component and unused code files.
- Voice selection preview: Automatically update sample text in voice selection widget when batch configuration or selected voice changes.
- Improved code quality: Cleaned up bare except blocks and unused functions across all service drivers for better reliability.
- Workflow UI adjustments: Removed unused autorun mode and improved button state handling in workflow dialog.

### Tiếng Việt

- Tối ưu hóa chế độ lô (batch): Bỏ qua việc tải trước danh sách giọng nói cho các lô dưới 1.000 ghi chú, giúp tăng tốc độ bắt đầu cho lô nhỏ.
- Tái cấu trúc quản lý dịch vụ: Hợp nhất giao diện quản lý dịch vụ, loại bỏ thành phần cũ và các tệp mã nguồn không sử dụng.
- Xem trước lựa chọn giọng nói: Tự động cập nhật văn bản mẫu trong cửa sổ chọn giọng khi cấu hình lô hoặc giọng nói thay đổi.
- Cải thiện chất lượng mã: Dọn dẹp các khối ngoại lệ không rõ ràng (bare except) và các hàm không dùng đến trong các trình điều khiển dịch vụ.
- Điều chỉnh giao diện quy trình làm việc (workflow): Loại bỏ chế độ tự động chạy (autorun) không sử dụng và cải thiện trạng thái nút bấm.

### 🇰🇷 한국어

- 배치 모드 최적화: 1,000개 미만의 배치에 대해 음성 목록 사전 로드를 건너뛰어 소규모 배치의 시작 속도를 향상했습니다.
- 서비스 관리 리팩토링: 서비스 관리 컴포넌트를 병합하고 기존 레거시 컴포넌트와 미사용 코드 파일을 제거했습니다.
- 음성 선택 미리보기: 배치 구성 또는 선택한 음성이 변경될 때 음성 선택 위젯의 샘플 텍스트를 자동으로 업데이트합니다.
- 코드 품질 개선: 안정성 향상을 위해 모든 서비스 드라이버에서 불완전한 예외 처리(bare except)와 미사용 함수를 정리했습니다.
- 워크플로 UI 조정: 미사용 자동 실행(autorun) 모드를 제거하고 버튼 상태 처리를 개선했습니다.

### 🇨🇳 简体中文

- 优化批量模式：针对 1,000 条以下的批量操作跳过前置语音预加载，加快小批量的启动速度。
- 重构服务管理：合并服务管理组件，移除旧版服务组件及未使用的代码文件。
- 语音选择预览：当批量配置或所选语音发生变化时，自动更新语音选择控件中的示例文本。
- 改善代码质量：清理所有服务驱动程序中不规范的异常捕获（bare except）和未使用函数，提升稳定性。
- 工作流界面调整：移除未使用的工作流自动运行（autorun）模式，优化按钮状态处理。

### 🇹🇼 繁體中文

- 優化批次模式：針對 1,000 條以下的批次操作跳過前置語音預載，加快小批次的啟動速度。
- 重構服務管理：合併服務管理元件，移除舊版服務元件及未使用的程式碼檔案。
- 語音選擇預覽：當批次設定或所選語音發生變化時，自動更新語音選擇控制項中的範例文字。
- 改善程式碼品質：清理所有服務驅動程式中不規範的異常擷取（bare except）和未使用函式，提升穩定性。
- 工作流介面調整：移除未使用的工作流自動執行（autorun）模式，優化按鈕狀態處理。

### 🇯🇵 日本語

- バッチモードの最適化：1,000件未満のバッチ処理において音声リストの事前ロードをスキップし、小規模バッチの起動を高速化。
- サービス管理のリファクタリング：サービス管理コンポーネントを統合し、レガシーコンポーネントおよび未使用のコードファイルを削除。
- 音声選択プレビュー：バッチ設定や選択音声의変更時に、音声選択ウィジェットのサンプルテキストを自動更新。
- コード品質の向上：安定性向上のため、すべてのサービスドライバーで裸の例外処理（bare except）および未使用の関数をクリーンアップ。
- ワークフローUIの調整：未使用の自動実行（autorun）モードの削除と、ボタンの状態制御の改善。

### 🇸🇪 Svenska

- Optimerat batchläge: Hoppa över förhandsladdning av röstlista för batcher under 1 000 anteckningar, vilket snabbar upp batchstart för små set.
- Refaktorerat tjänstehantering: Slog samman gränssnittet för tjänstehantering och tog bort föråldrade komponenter samt oanvända filer.
- Förhandsvisning av röstval: Uppdatera automatiskt exempeltext i röstvalswidgeten när batchkonfiguration eller vald röst ändras.
- Förbättrad kodkvalitet: Rensade upp osäkra undantagsblock (bare except) och oanvända funktioner i alla tjänstedrivrutiner för bättre stabilitet.
- Arbetsflödesjusteringar: Tog bort oanvänt autokörningsläge (autorun) och förbättrade knappstatusar i arbetsflödesdialogen.

## 26.7.3 - 2026-07-09

### English

- Fixed Kokoro uninstall killing Anki itself (`taskkill /F /IM python.exe /T` replaced with PowerShell path-filtered kill).
- Fixed semaphore deadlock in SherpaProcessPool (`threading.Semaphore` replaced with `DynamicSemaphore` supporting runtime max adjustment).
- Fixed silent error suppression: 7 `except: pass` sites in Kokoro manager now log warnings.
- Fixed bare `except:` in MMS safe_terminate, macOS safe_terminate, and system_utils CPU detection.
- Added fix plan for remaining 11 issues in `AI_Documents/Plan.md`.

### Tiếng Việt

- Sửa lỗi gỡ Kokoro giết chết Anki (thay `taskkill /F /IM python.exe /T` bằng PowerShell lọc đường dẫn).
- Sửa lỗi deadlock semaphore trong SherpaProcessPool (thay `threading.Semaphore` bằng `DynamicSemaphore` hỗ trợ điều chỉnh max runtime).
- Sửa lỗi im lặng nuốt lỗi: 7 chỗ `except: pass` trong Kokoro manager giờ ghi log warning.
- Sửa `except:` bare trong MMS safe_terminate, macOS safe_terminate và system_utils CPU detection.
- Thêm kế hoạch sửa cho 11 vấn đề còn lại trong `AI_Documents/Plan.md`.

### 🇰🇷 한국어

- Kokoro 제거 시 Anki 자체를 종료하던 버그 수정 (`taskkill /F /IM python.exe /T`를 PowerShell 경로 필터로 대체).
- SherpaProcessPool의 세마포어 데드락 수정 (`threading.Semaphore`를 런타임 최대값 조정을 지원하는 `DynamicSemaphore`로 대체).
- 무음 오류 억제 수정: Kokoro 관리자의 7개 `except: pass` 위치가 이제 경고를 로깅합니다.
- MMS safe_terminate, macOS safe_terminate 및 system_utils CPU 감지의 bare `except:` 수정.
- 남은 11개 문제에 대한 수정 계획을 `AI_Documents/Plan.md`에 추가.

### 🇨🇳 简体中文

- 修复了 Kokoro 卸载会杀死 Anki 本身的问题（将 `taskkill /F /IM python.exe /T` 替换为 PowerShell 路径过滤）。
- 修复了 SherpaProcessPool 中的信号量死锁（将 `threading.Semaphore` 替换为支持运行时最大并发调整的 `DynamicSemaphore`）。
- 修复了静默错误抑制：Kokoro 管理器中的 7 个 `except: pass` 位置现在记录警告日志。
- 修复了 MMS safe_terminate、macOS safe_terminate 和 system_utils CPU 检测中的裸 `except:`。
- 将剩余 11 个问题的修复计划添加到 `AI_Documents/Plan.md`。

### 🇹🇼 繁體中文

- 修復了 Kokoro 解除安裝會殺死 Anki 本身的問題（將 `taskkill /F /IM python.exe /T` 替換為 PowerShell 路徑過濾）。
- 修復了 SherpaProcessPool 中的信號量死鎖（將 `threading.Semaphore` 替換為支援執行時最大調整的 `DynamicSemaphore`）。
- 修復了靜默錯誤抑制：Kokoro 管理器中的 7 個 `except: pass` 現在記錄警告日誌。
- 修復了 MMS safe_terminate、macOS safe_terminate 和 system_utils CPU 檢測中的裸 `except:`。
- 將剩餘 11 個問題的修復計劃添加到 `AI_Documents/Plan.md`。

### 🇯🇵 日本語

- Kokoro アンインストール時に Anki 自体を強制終了していた問題を修正（`taskkill /F /IM python.exe /T` を PowerShell のパスフィルターに置き換え）。
- SherpaProcessPool のセマフォデッドロックを修正（`threading.Semaphore` を実行時に最大値を調整できる `DynamicSemaphore` に置き換え）。
- サイレントエラー抑止を修正：Kokoro マネージャーの 7 箇所の `except: pass` が警告をログ出力するように。
- MMS safe_terminate、macOS safe_terminate、system_utils CPU 検出の裸の `except:` を修正。
- 残りの 11 の問題の修正計画を `AI_Documents/Plan.md` に追加。

### 🇸🇪 Svenska

- Fixade att Kokoro-avinstallation dödade Anki själv (`taskkill /F /IM python.exe /T` ersatt med PowerShell-sökvägsfiltrering).
- Fixade semaforlåsning i SherpaProcessPool (`threading.Semaphore` ersatt med `DynamicSemaphore` som stöder runtime max-justering).
- Fixade tyst felsuppression: 7 `except: pass`-platser i Kokoro-hanteraren loggar nu varningar.
- Fixade bar `except:` i MMS safe_terminate, macOS safe_terminate och system_utils CPU-detektering.
- Lade till fixplan för återstående 11 problem i `AI_Documents/Plan.md`.

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

### 🇰🇷 한국어

- must_continue=False로 인해 미리보기 페이지당 1개 노트만 표시되던 배치 미리보기 버그 수정.
- dataChanged 범위가 정확한 페이지 행 대신 확장된 loaded_note_ids를 사용하던 문제 수정.
- 대화상자 열릴 때 스크롤이 아닌 모든 페이지를 순차적으로 로드하도록 변경.
- 모든 노트가 로드될 때까지 생성 버튼 비활성화, 설정 변경 시 다시 비활성화.
- 상태 레이블에 'X/Y 노트 로딩 중' 표시.
- EdgeTTS TimeoutError를 연결 오류와 분리, 타임아웃이 더 이상 60s 백오프 트리거하지 않음.
- EdgeTTS 요청 타임아웃 30s→180s로 증가 (베트남어/발음 구별 부호).
- 재시도 백오프 3s→5s, 연결 백오프 15s→60s 증가, 지터 추가.
- EdgeTTS 연결 실패 시 즉시 반환 대신 재시도.
- Anki 백업 대화상자와 주기적 백업 타이머를 억제하는 backup_guard 모듈 추가.
- 전체 체인 하나의 실행 취소 대신 각 청크 내부로 실행 취소 이동.
- get_all_fields_from_notes SQL 청크(배치당 500개)로 최적화.
- 오프라인 TTS 엔진 기본 작업자 1→CPU 수 기반으로 업데이트.
- 중복 제거 생성 중 진행률 표시줄에 총 노트 수 표시.

### 🇨🇳 简体中文

- 修复了预览期间每页仅显示1条笔记的批量预览错误（must_continue=False导致第一条后中断）。
- 修复了dataChanged范围使用扩展的loaded_note_ids而非精确页面行的问题。
- 批量预览在对话框打开时改为顺序加载所有页面，而非滚动时加载。
- 生成按钮在所有笔记完全加载前保持禁用，设置更改后重新禁用。
- 状态标签在预览加载期间显示'正在加载 X/Y 条笔记'。
- 将EdgeTTS TimeoutError与连接错误分离；超时不再触发60秒全局退避。
- EdgeTTS每次请求超时从30秒增加到180秒（越南语/变音符号文本）。
- 重试退避从3秒增加到5秒，连接退避从15秒增加到60秒；添加抖动。
- EdgeTTS连接失败现在会重试而非立即返回。
- 添加backup_guard模块以抑制Anki的备份对话框和定期备份计时器。
- 将撤销条目移入每个应用块内，而非整个链使用一个撤销条目。
- 优化get_all_fields_from_notes为SQL分块查询（每批500条）。
- 离线TTS引擎的默认工作线程从1更新为基于CPU数量。
- 在去重生成期间，进度条显示笔记总数。

### 🇹🇼 繁體中文

- 修復了預覽期間每頁僅顯示1條筆記的批量預覽錯誤。
- 修復了dataChanged範圍使用擴展的loaded_note_ids而非精確頁面行的問題。
- 批量預覽在對話框開啟時改為順序載入所有頁面，而非滾動時載入。
- 產生按鈕在所有筆記完全載入前保持禁用，設定變更後重新禁用。
- 狀態標籤在預覽載入期間顯示'正在載入 X/Y 條筆記'。
- 將EdgeTTS TimeoutError與連線錯誤分離；逾時不再觸發60秒全域退避。
- EdgeTTS每次請求逾時從30秒增加到180秒。
- 新增backup_guard模組以抑制Anki的備份對話框和定期備份計時器。
- 將復原條目移入每個應用區塊內。

### 🇯🇵 日本語

- プレビュー中に1ページに1ノートしか表示されなかったバッチプレビューのバグを修正。
- dataChanged範囲が拡張されたloaded_note_idsを使用していた問題を修正。
- ダイアログを開いたときにスクロールではなく全ページを順次読み込むように変更。
- すべてのノートが読み込まれるまで生成ボタンを無効にし、設定変更時に再び無効化。
- ステータスラベルに'X/Y ノートを読み込み中'と表示。
- EdgeTTS TimeoutErrorを接続エラーから分離。タイムアウトが60秒のグローバルバックオフをトリガーしない。
- EdgeTTSのリクエストタイムアウトを30秒から180秒に増加。
- backup_guardモジュールを追加してAnkiのバックアップダイアログと定期バックアップタイマーを抑制。
- 各適用チャンク内に元に戻すエントリを移動。

### 🇸🇪 Svenska

- Fixade batch-preview som endast visade 1 anteckning per sida under förhandsvisning.
- Fixade dataChanged-intervall som använde utökade loaded_note_ids istället för exakta sidrader.
- Batch-preview laddar nu alla sidor sekventiellt när dialogrutan öppnas istället för vid scrollning.
- Generera-knappen inaktiveras tills alla anteckningar har laddats; återinaktiveras vid inställningsändring.
- Statusetiketten visar 'Laddar X av Y anteckningar' under förhandsvisning.
- Separerade EdgeTTS TimeoutError från anslutningsfel; timeout utlöser inte längre 60s global backoff.
- EdgeTTS timeout per förfrågan ökad från 30s till 180s för vietnamesisk/diakritisk text.
- Lade till backup_guard-modul för att dämpa Ankis backup-dialog och periodisk backup-timer.
- Flyttade ångra-post inuti varje appliceringsbit istället för en ångra-post för hela kedjan.

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
