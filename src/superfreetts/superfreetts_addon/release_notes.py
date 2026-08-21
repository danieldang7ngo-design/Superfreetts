from dataclasses import dataclass
import re
from typing import Dict, List, Optional, Tuple


@dataclass(frozen=True)
class ReleaseNoteEntry:
    version: str
    title: Dict[str, str]
    bullets: Dict[str, List[str]]


RELEASE_NOTES: List[ReleaseNoteEntry] = [
    ReleaseNoteEntry(
        version="26.8.11",
        title={
            "en": "New Apple UI theme option",
            "vi": "Thêm tùy chọn giao diện Apple",
            "ko": "새 Apple UI 테마 옵션",
            "zh-CN": "新增 Apple 界面主题选项",
            "zh-TW": "新增 Apple 介面主題選項",
            "ja": "新しい Apple UI テーマオプション",
            "sv": "Nytt Apple-tema UI-alternativ",
        },
        bullets={
            "en": [
                "Added a third UI theme: Apple (inspired by apple.com) — clean SF Pro feel with an Action Blue (#0066cc) accent and soft rounded cards.",
                "Choose between Vibrant Blocks, Ollama, and Apple in Preferences. All themes follow Anki's light/dark mode.",
            ],
            "vi": [
                "Thêm giao diện thứ ba: Apple (lấy cảm hứng từ apple.com) — phong cách SF Pro gọn gàng, điểm nhấn Action Blue (#0066cc) và card bo tròn mềm mại.",
                "Chọn giữa Vibrant Blocks, Ollama và Apple trong Tùy chọn. Mọi giao diện đều tự động theo chế độ sáng/tối của Anki.",
            ],
            "ko": [
                "세 번째 UI 테마 추가: Apple(apple.com에서 영감) — 깔끔한 SF Pro 느낌과 Action Blue(#0066cc) 포인트, 부드러운 둥근 카드.",
                "환경 설정에서 Vibrant Blocks, Ollama, Apple 중 선택할 수 있습니다. 모든 테마는 Anki의 라이트/다크 모드를 따릅니다.",
            ],
            "zh-CN": [
                "新增第三个界面主题：Apple（灵感来自 apple.com）—— 简洁的 SF Pro 风格，配以 Action Blue（#0066cc）强调色和柔和圆角卡片。",
                "可在偏好设置中选择 Vibrant Blocks、Ollama 和 Apple。所有主题都会跟随 Anki 的浅色/深色模式。",
            ],
            "zh-TW": [
                "新增第三個介面主題：Apple（靈感來自 apple.com）—— 簡潔的 SF Pro 風格，搭配 Action Blue（#0066cc）強調色與柔和圓角卡片。",
                "可在偏好設定中選擇 Vibrant Blocks、Ollama 和 Apple。所有主題都會跟隨 Anki 的淺色/深色模式。",
            ],
            "ja": [
                "3つ目のUIテーマを追加: Apple（apple.com から着想）— すっきりしたSF Pro風、Action Blue（#0066cc）のアクセントと柔らかな角丸カード。",
                "環境設定で Vibrant Blocks、Ollama、Apple から選択できます。すべてのテーマは Anki のライト/ダークモードに追従します。",
            ],
            "sv": [
                "Lade till ett tredje UI-tema: Apple (inspirerat av apple.com) — ren SF Pro-känsla med en Action Blue (#0066cc) accent och mjuka rundade kort.",
                "Välj mellan Vibrant Blocks, Ollama och Apple i Inställningar. Alla teman följer Ankis ljust/mörkt läge.",
            ],
        },
    ),
    ReleaseNoteEntry(
        version="26.8.10",
        title={
            "en": "New Ollama (minimal) UI theme option",
            "vi": "Thêm tùy chọn giao diện Ollama (tối giản)",
            "ko": "새 Ollama(미니멀) UI 테마 옵션",
            "zh-CN": "新增 Ollama（极简）界面主题选项",
            "zh-TW": "新增 Ollama（極簡）介面主題選項",
            "ja": "新しい Ollama（ミニマル）UI テーマオプション",
            "sv": "Ny Ollama-tema (minimal) UI-alternativ",
        },
        bullets={
            "en": [
                "Added an interface theme selector in Preferences: choose between the default Vibrant Blocks theme and a new Ollama theme (flat paper-white design with pill-shaped buttons, inspired by ollama.com).",
                "The Ollama theme follows Anki's light/dark mode automatically.",
            ],
            "vi": [
                "Thêm bộ chọn giao diện trong Tùy chọn: chọn giữa giao diện mặc định Vibrant Blocks và giao diện Ollama mới (nền trắng phẳng, nút hình viên thuốc, lấy cảm hứng từ ollama.com).",
                "Giao diện Ollama tự động theo chế độ sáng/tối của Anki.",
            ],
            "ko": [
                "환경 설정에 인터페이스 테마 선택기 추가: 기본 Vibrant Blocks 테마와 새로운 Ollama 테마(평면 흰색 디자인, 알약 모양 버튼, ollama.com에서 영감) 중에서 선택할 수 있습니다.",
                "Ollama 테마는 Anki의 라이트/다크 모드를 자동으로 따릅니다.",
            ],
            "zh-CN": [
                "在偏好设置中新增界面主题选择器：可在默认的 Vibrant Blocks 主题与全新的 Ollama 主题（扁平白底、药丸形按钮，灵感来自 ollama.com）之间选择。",
                "Ollama 主题会自动跟随 Anki 的浅色/深色模式。",
            ],
            "zh-TW": [
                "在偏好設定中新增介面主題選擇器：可在預設的 Vibrant Blocks 主題與全新的 Ollama 主題（扁平白底、藥丸形按鈕，靈感來自 ollama.com）之間選擇。",
                "Ollama 主題會自動跟隨 Anki 的淺色/深色模式。",
            ],
            "ja": [
                "環境設定にインターフェーステーマ選択を追加: デフォルトの Vibrant Blocks テーマと新しい Ollama テーマ（フラットな白背景、ピル型ボタン、ollama.com から着想）を選択できます。",
                "Ollama テーマは Anki のライト/ダークモードに自動追従します。",
            ],
            "sv": [
                "Lade till en temaväljare i Inställningar: välj mellan standardtemat Vibrant Blocks och ett nytt Ollama-tema (platt vit design med pillerformade knappar, inspirerat av ollama.com).",
                "Ollama-temat följer automatiskt Ankis ljust/mörkt läge.",
            ],
        },
    ),
    ReleaseNoteEntry(
        version="26.8.9",
        title={
            "en": "Local-only Usage dashboard and startup crash fix",
            "vi": "Bảng thống kê sử dụng cục bộ và sửa lỗi crash khi khởi động",
            "ko": "로컬 전용 사용량 대시보드 및 시작 충돌 수정",
            "zh-CN": "仅本地使用情况仪表盘与启动崩溃修复",
            "zh-TW": "僅本機使用情況儀表板與啟動崩潰修復",
            "ja": "ローカルのみの使用状況ダッシュボードと起動クラッシュの修正",
            "sv": "Lokal användningsinstrumentpanel och startkraschfix",
        },
        bullets={
            "en": [
                "New Usage tab in Settings: see how many audio files, notes, characters and realtime plays you have created — plus generation time, per-engine breakdown, monthly activity and recent sessions.",
                "Money saved estimate: the dashboard estimates how much you saved versus a paid TTS plan ($5/month for 250,000 characters).",
                "100% private: all usage stats are stored only on your computer (user_files/usage_log.json) and are never sent anywhere. No telemetry.",
                "Fixed startup crash on Anki 25.09+: replaced the removed profile_did_close hook with profile_will_close so the addon loads correctly.",
            ],
            "vi": [
                "Tab Usage mới trong Cài đặt: xem bạn đã tạo bao nhiêu tệp âm thanh, ghi chú, ký tự và lượt phát realtime — kèm thời gian tạo, phân theo engine, hoạt động theo tháng và phiên gần đây.",
                "Ước tính tiền đã tiết kiệm: bảng điều khiển ước tính số tiền bạn tiết kiệm so với gói TTS trả phí ($5/tháng cho 250.000 ký tự).",
                "100% riêng tư: mọi thống kê chỉ lưu trên máy bạn (user_files/usage_log.json) và không gửi đi bất cứ đâu. Không telemetry.",
                "Sửa lỗi crash khi khởi động trên Anki 25.09+: thay hook profile_did_close đã bị loại bỏ bằng profile_will_close để addon tải chính xác.",
            ],
            "ko": [
                "설정에 새 사용량 탭: 생성한 오디오 파일, 노트, 문자, 실시간 재생 횟수와 생성 시간, 엔진별 분류, 월별 활동, 최근 세션을 확인할 수 있습니다.",
                "절약 금액 추정: 유료 TTS 요금제($5/월, 250,000자) 대비 절약한 금액을 추정합니다.",
                "100% 프라이빗: 모든 사용 통계는 컴퓨터에만 저장되며(user_files/usage_log.json) 어디로도 전송되지 않습니다. 텔레메트리 없음.",
                "Anki 25.09+에서의 시작 충돌 수정: 제거된 profile_did_close 훅을 profile_will_close로 교체하여 애드온이 올바르게 로드됩니다.",
            ],
            "zh-CN": [
                "设置中新增使用情况选项卡：查看已生成的音频文件数、笔记数、字符数和实时播放次数——以及生成时间、按引擎分类、每月活动和最近会话。",
                "节省金额估算：仪表盘会估算您相对于付费 TTS 套餐（每月 5 美元/250,000 字符）节省的金额。",
                "100% 隐私：所有使用统计仅存储在您的计算机上（user_files/usage_log.json），绝不会发送到任何地方。无遥测。",
                "修复 Anki 25.09+ 上的启动崩溃：将已移除的 profile_did_close 挂钩替换为 profile_will_close，确保插件正确加载。",
            ],
            "zh-TW": [
                "設定中新增使用情況索引標籤：查看已產生的音訊檔數、筆記數、字元數和即時播放次數——以及產生時間、依引擎分類、每月活動和最近工作階段。",
                "節省金額估算：儀表板會估算您相對於付費 TTS 方案（每月 5 美元/250,000 字元）節省的金額。",
                "100% 隱私：所有使用統計僅儲存在您的電腦上（user_files/usage_log.json），絕不會傳送到任何地方。無遙測。",
                "修復 Anki 25.09+ 上的啟動崩潰：將已移除的 profile_did_close 掛鉤替換為 profile_will_close，確保外掛正確載入。",
            ],
            "ja": [
                "設定に新しい使用状況タブ: 作成した音声ファイル数、ノート数、文字数、リアルタイム再生回数に加え、生成時間、エンジン別の内訳、月ごとのアクティビティ、最近のセッションを確認できます。",
                "節約額の見積もり: 有料TTSプラン（月額5ドル/250,000文字）と比較した節約額を推定します。",
                "100%プライベート: すべての使用統計はお使いのコンピューターにのみ保存され（user_files/usage_log.json）、どこにも送信されません。テレメトリーはありません。",
                "Anki 25.09+ での起動クラッシュを修正: 削除された profile_did_close フックを profile_will_close に置き換え、アドオンが正しく読み込まれるようにしました。",
            ],
            "sv": [
                "Ny flik Användning i Inställningar: se hur många ljudfiler, anteckningar, tecken och realtidsspelningar du har skapat — plus genereringstid, uppdelning per motor, månatlig aktivitet och senaste sessioner.",
                "Besparingsuppskattning: instrumentpanelen uppskattar hur mycket du sparat jämfört med en betald TTS-plan ($5/månad för 250 000 tecken).",
                "100% privat: alla användningsstatistik lagras bara på din dator (user_files/usage_log.json) och skickas aldrig någonstans. Ingen telemetri.",
                "Fixade startkrasch på Anki 25.09+: ersatte den borttagna profile_did_close-kroken med profile_will_close så att tillägget laddas korrekt.",
            ],
        },
    ),
    ReleaseNoteEntry(
        version="26.7.5",
        title={
            "en": "macOS RAM and stability fixes, unsaved preset audio preview support",
            "vi": "Khắc phục lỗi RAM và crash trên macOS, hỗ trợ nghe thử âm thanh khi chưa lưu preset",
            "ko": "macOS RAM 및 안정성 수정, 미저장 프리셋 오디오 미리보기 지원",
            "zh-CN": "macOS 内存与稳定性修复，支持未保存预设的音频预览",
            "zh-TW": "macOS 記憶體與穩定性修復，支援未儲存預設的音訊預覽",
            "ja": "macOSのメモリおよび安定性の修正、未保存プリセットの音声プレビュー対応",
            "sv": "macOS-minnes- och stabilitetsfixar, stöd för förhandsgranskning av osparade förinställningar",
        },
        bullets={
            "en": [
                "Fixed macOS RAM overload & crashes: Implemented RAM-aware concurrency limits for neural process pools, bounded realtime playback timeout (20s), reused EdgeTTS background event loop, and added semaphore gating for macOS `say` subprocesses.",
                "Platform guards: Prevented Windows-only Python installers (Kokoro/MMS) from downloading on macOS/Linux with clear warning dialogs.",
                "Unsaved preset preview: Enabled instant audio preview using current in-memory UI options without requiring a saved preset name or existing mapping rules.",
            ],
            "vi": [
                "Sửa lỗi tràn RAM & crash trên macOS: Giới hạn số tiến trình đồng thời theo dung lượng RAM khả dụng (Piper, Kokoro, MMS, Supertonic), thêm timeout 20s cho realtime playback, tái sử dụng event loop EdgeTTS và giới hạn subprocess `say`.",
                "Cảnh báo nền tảng: Bổ sung guard phát hiện hệ điều hành, thông báo rõ ràng trên macOS/Linux khi cố cài đặt engine Windows-only (Kokoro/MMS).",
                "Nghe thử chưa cần lưu: Hỗ trợ nghe thử âm thanh trực tiếp từ các tuỳ chọn đang chọn trên UI ngay cả khi chưa lưu Preset hoặc chưa có Mapping Rules.",
            ],
            "ko": [
                "macOS RAM 과부하 및 크래시 수정: 신경망 프로세스 풀에 RAM 인지 동시성 제한 구현, 실시간 재생 제한 시간(20초) 설정, EdgeTTS 백그라운드 이벤트 루프 재사용 및 macOS `say` 서브프로세스 제한 적용.",
                "플랫폼 가드: macOS/Linux에서 Windows 전용 Python 설치 프로그램(Kokoro/MMS) 다운로드를 방지하고 명확한 경고 대화상자 표시.",
                "미저장 프리셋 미리보기: 저장된 프리셋 이름이나 기존 매핑 규칙 없이도 현재 UI 설정으로 즉시 오디오 미리보기 지원.",
            ],
            "zh-CN": [
                "修复 macOS 内存过载与崩溃：为神经引擎进程池增加内存感知并发限制，设置实时播放超时（20秒），复用 EdgeTTS 后台事件循环，并限制 macOS `say` 子进程并发。",
                "平台保护：在 macOS/Linux 上阻止下载 Windows 专用 Python 安装程序（Kokoro/MMS），并弹出清晰警告。",
                "未保存预设预览：支持直接根据当前 UI 选项进行实时音频预览，无需事先保存预设名称或配置映射规则。",
            ],
            "zh-TW": [
                "修復 macOS 記憶體過載與崩潰：為神經引擎處理程序池增加記憶體感知並發限制，設定即時播放超時（20秒），複用 EdgeTTS 後台事件循環，並限制 macOS `say` 子處理程序並發。",
                "平台保護：在 macOS/Linux 上阻止下載 Windows 專用 Python 安裝程式（Kokoro/MMS），並彈出清晰警告。",
                "未儲存預設預覽：支援直接根據當前 UI 選項進行即時音訊預覽，無需事先儲存預設名稱或設定對應規則。",
            ],
            "ja": [
                "macOSのメモリ過負荷とクラッシュの修正：ニューラルエンジンのプロセスプールにメモリ認識並行制限を導入、リアルタイム再生タイムアウト（20秒）を設定、EdgeTTSバックグラウンドイベントループを再利用、macOS `say`サブプロセスの並行数を制限。",
                "プラットフォームガード：macOS/LinuxでWindows専用のPythonインストーラー（Kokoro/MMS）のダウンロードをブロックし、明確な警告を表示。",
                "未保存プリセットのプレビュー：保存されたプリセット名やマッピングルールがなくても、現在のUI設定で即座に音声プレビューが可能に。",
            ],
            "sv": [
                "Fixat macOS-minnesöverbelastning och krascher: Implementerade minnesmedvetna konkurrensbegränsningar för neurala processpooler, tidsgräns för realtidsuppspelning (20s), återanvändning av EdgeTTS händelseslinga och semaforspärr för macOS `say`-underprocesser.",
                "Plattformsspärrar: Förhindrade nedladdning av Windows-exklusiva Python-installerare (Kokoro/MMS) på macOS/Linux med tydliga varningsdialoger.",
                "Förhandsgranskning av osparade förinställningar: Aktiverade omedelbar förhandsgranskning av ljud med aktuella UI-inställningar utan krav på sparad förinställning eller befintliga regler.",
            ],
        },
    ),
    ReleaseNoteEntry(
        version="26.7.4",

        title={
            "en": "Batch mode optimization for small runs, refactored service management, and UI improvements",
            "vi": "Tối ưu hóa chế độ lô nhỏ, tái cấu trúc quản lý dịch vụ và cải thiện giao diện",
            "ko": "소규모 배치 모드 최적화, 서비스 관리 리팩토링 및 UI 개선",
            "zh-CN": "小批量模式优化、服务管理重构及界面改进",
            "zh-TW": "小批次模式優化、服務管理重構及介面改進",
            "ja": "小規模バッチの最適化、サービス管理のリファクタリング、UI改善",
            "sv": "Optimerat batchläge för små körningar, refaktorerad tjänstehantering och UI-förbättringar",
        },
        bullets={
            "en": [
                "Optimized batch mode: Skip upfront voice pre-loading for batches under 1,000 notes, speeding up batch startup for small sets.",
                "Refactored service management: Merged service management component and removed legacy service component and unused code files.",
                "Voice selection preview: Automatically update sample text in voice selection widget when batch configuration or selected voice changes.",
                "Improved code quality: Cleaned up bare except blocks and unused functions across all service drivers for better reliability.",
                "Workflow UI adjustments: Removed unused autorun mode and improved button state handling in workflow dialog.",
            ],
            "vi": [
                "Tối ưu hóa chế độ lô (batch): Bỏ qua việc tải trước danh sách giọng nói cho các lô dưới 1.000 ghi chú, giúp tăng tốc độ bắt đầu cho lô nhỏ.",
                "Tái cấu trúc quản lý dịch vụ: Hợp nhất giao diện quản lý dịch vụ, loại bỏ thành phần cũ và các tệp mã nguồn không sử dụng.",
                "Xem trước lựa chọn giọng nói: Tự động cập nhật văn bản mẫu trong cửa sổ chọn giọng khi cấu hình lô hoặc giọng nói thay đổi.",
                "Cải thiện chất lượng mã: Dọn dẹp các khối ngoại lệ không rõ ràng (bare except) và các hàm không dùng đến trong các trình điều khiển dịch vụ.",
                "Điều chỉnh giao diện quy trình làm việc (workflow): Loại bỏ chế độ tự động chạy (autorun) không sử dụng và cải thiện trạng thái nút bấm.",
            ],
            "ko": [
                "배치 모드 최적화: 1,000개 미만의 배치에 대해 음성 목록 사전 로드를 건너뛰어 소규모 배치의 시작 속도를 향상했습니다.",
                "서비스 관리 리팩토링: 서비스 관리 컴포넌트를 병합하고 기존 레거시 컴포넌트와 미사용 코드 파일을 제거했습니다.",
                "음성 선택 미리보기: 배치 구성 또는 선택한 음성이 변경될 때 음성 선택 위젯의 샘플 텍스트를 자동으로 업데이트합니다.",
                "코드 품질 개선: 안정성 향상을 위해 모든 서비스 드라이버에서 불완전한 예외 처리(bare except)와 미사용 함수를 정리했습니다.",
                "워크플로 UI 조정: 미사용 자동 실행(autorun) 모드를 제거하고 버튼 상태 처리를 개선했습니다.",
            ],
            "zh-CN": [
                "优化批量模式：针对 1,000 条以下的批量操作跳过前置语音预加载，加快小批量的启动速度。",
                "重构服务管理：合并服务管理组件，移除旧版服务组件及未使用的代码文件。",
                "语音选择预览：当批量配置或所选语音发生变化时，自动更新语音选择控件中的示例文本。",
                "改善代码质量：清理所有服务驱动程序中不规范的异常捕获（bare except）和未使用函数，提升稳定性。",
                "工作流界面调整：移除未使用的工作流自动运行（autorun）模式，优化按钮状态处理。",
            ],
            "zh-TW": [
                "優化批次模式：針對 1,000 條以下的批次操作跳過前置語音預載，加快小批次的啟動速度。",
                "重構服務管理：合併服務管理元件，移除舊版服務元件及未使用的程式碼檔案。",
                "語音選擇預覽：當批次設定或所選語音發生變化時，自動更新語音選擇控制項中的範例文字。",
                "改善程式碼品質：清理所有服務驅動程式中不規範的異常擷取（bare except）和未使用函式，提升穩定性。",
                "工作流介面調整：移除未使用的工作流自動執行（autorun）模式，優化按鈕狀態處理。",
            ],
            "ja": [
                "バッチモードの最適化：1,000件未満のバッチ処理において音声リストの事前ロードをスキップし、小規模バッチの起動を高速化。",
                "サービス管理のリファクタリング：サービス管理コンポーネントを統合し、レガシーコンポーネントおよび未使用のコードファイルを削除。",
                "音声選択プレビュー：バッチ設定や選択音声の変更時に、音声選択ウィジェットのサンプルテキストを自動更新。",
                "コード品質の向上：安定性向上のため、すべてのサービスドライバーで裸の例外処理（bare except）および未使用の関数をクリーンアップ。",
                "ワークフローUIの調整：未使用の自動実行（autorun）モードの削除と、ボタンの状態制御の改善。",
            ],
            "sv": [
                "Optimerat batchläge: Hoppa över förhandsladdning av röstlista för batcher under 1 000 anteckningar, vilket snabvar upp batchstart för små set.",
                "Refaktorerat tjänstehantering: Slog samman gränssnittet för tjänstehantering och tog bort föråldrade komponenter samt oanvända filer.",
                "Förhandsvisning av röstval: Uppdatera automatiskt exempeltext i röstvalswidgeten när batchkonfiguration eller vald röst ändras.",
                "Förbättrad kodkvalitet: Rensade upp osäkra undantagsblock (bare except) och oanvända funktioner i alla tjänstedrivrutiner för bättre stabilitet.",
                "Arbetsflödesjusteringar: Tog bort oanvänt autokörningsläge (autorun) och förbättrade knappstatusar i arbetsflödesdialogen.",
            ],
        },
    ),
    ReleaseNoteEntry(
        version="26.7.3",
        title={
            "en": "Critical bug fixes: Kokoro uninstall kills Anki, semaphore deadlock, silent error suppression",
            "vi": "Sửa lỗi nghiêm trọng: gỡ Kokoro giết Anki, deadlock semaphore, nuốt lỗi im lặng",
            "ko": "심각한 버그 수정: Kokoro 제거 시 Anki 종료, 세마포어 데드락, 무음 오류 억제",
            "zh-CN": "关键错误修复：Kokoro卸载杀死Anki、信号量死锁、静默错误抑制",
            "zh-TW": "關鍵錯誤修復：Kokoro解除安裝殺死Anki、信號量死鎖、靜默錯誤抑制",
            "ja": "重大バグ修正：KokoroアンインストールによるAnki強制終了、セマフォデッドロック、サイレントエラー抑止",
            "sv": "Kritiska buggfixar: Kokoro-avinstallation dödar Anki, semaforlåsning, tyst felsuppression",
        },
        bullets={
            "en": [
                "Fixed Kokoro uninstall killing Anki itself (taskkill /F /IM python.exe /T replaced with PowerShell path-filtered kill).",
                "Fixed semaphore deadlock in SherpaProcessPool (threading.Semaphore replaced with DynamicSemaphore supporting runtime max adjustment).",
                "Fixed silent error suppression: 7 except: pass sites in Kokoro manager now log warnings.",
                "Fixed bare except: in MMS safe_terminate, macOS safe_terminate, and system_utils CPU detection.",
                "Added fix plan for remaining 11 issues in AI_Documents/Plan.md.",
            ],
            "vi": [
                "Sửa lỗi gỡ Kokoro giết chết Anki (thay taskkill /F /IM python.exe /T bằng PowerShell lọc đường dẫn).",
                "Sửa lỗi deadlock semaphore trong SherpaProcessPool (thay threading.Semaphore bằng DynamicSemaphore hỗ trợ điều chỉnh max runtime).",
                "Sửa lỗi im lặng nuốt lỗi: 7 chỗ except: pass trong Kokoro manager giờ ghi log warning.",
                "Sửa except: bare trong MMS safe_terminate, macOS safe_terminate và system_utils CPU detection.",
                "Thêm kế hoạch sửa cho 11 vấn đề còn lại trong AI_Documents/Plan.md.",
            ],
            "ko": [
                "Kokoro 제거 시 Anki 자체를 종료하던 버그 수정 (taskkill /F /IM python.exe /T를 PowerShell 경로 필터로 대체).",
                "SherpaProcessPool의 세마포어 데드락 수정 (threading.Semaphore를 런타임 최대값 조정을 지원하는 DynamicSemaphore로 대체).",
                "무음 오류 억제 수정: Kokoro 관리자의 7개 except: pass 위치가 이제 경고를 로깅합니다.",
                "MMS safe_terminate, macOS safe_terminate 및 system_utils CPU 감지의 bare except: 수정.",
                "남은 11개 문제에 대한 수정 계획을 AI_Documents/Plan.md에 추가.",
            ],
            "zh-CN": [
                "修复了 Kokoro 卸载会杀死 Anki 本身的问题（将 taskkill /F /IM python.exe /T 替换为 PowerShell 路径过滤）。",
                "修复了 SherpaProcessPool 中的信号量死锁（将 threading.Semaphore 替换为支持运行时最大并发调整的 DynamicSemaphore）。",
                "修复了静默错误抑制：Kokoro 管理器中的 7 个 except: pass 位置现在记录警告日志。",
                "修复了 MMS safe_terminate、macOS safe_terminate 和 system_utils CPU 检测中的裸 except:。",
                "将剩余 11 个问题的修复计划添加到 AI_Documents/Plan.md。",
            ],
            "zh-TW": [
                "修復了 Kokoro 解除安裝會殺死 Anki 本身的問題（將 taskkill /F /IM python.exe /T 替換為 PowerShell 路徑過濾）。",
                "修復了 SherpaProcessPool 中的信號量死鎖（將 threading.Semaphore 替換為支援執行時最大調整的 DynamicSemaphore）。",
                "修復了靜默錯誤抑制：Kokoro 管理器中的 7 個 except: pass 現在記錄警告日誌。",
                "修復了 MMS safe_terminate、macOS safe_terminate 和 system_utils CPU 檢測中的裸 except:。",
                "將剩餘 11 個問題的修復計劃添加到 AI_Documents/Plan.md。",
            ],
            "ja": [
                "Kokoro アンインストール時に Anki 自体を強制終了していた問題を修正（taskkill /F /IM python.exe /T を PowerShell のパスフィルターに置き換え）。",
                "SherpaProcessPool のセマフォデッドロックを修正（threading.Semaphore を実行時に最大値を調整できる DynamicSemaphore に置き換え）。",
                "サイレントエラー抑止を修正：Kokoro マネージャーの 7 箇所の except: pass が警告をログ出力するように。",
                "MMS safe_terminate、macOS safe_terminate、system_utils CPU 検出の裸の except: を修正。",
                "残りの 11 の問題の修正計画を AI_Documents/Plan.md に追加。",
            ],
            "sv": [
                "Fixade att Kokoro-avinstallation dödade Anki själv (taskkill /F /IM python.exe /T ersatt med PowerShell-sökvägsfiltrering).",
                "Fixade semaforlåsning i SherpaProcessPool (threading.Semaphore ersatt med DynamicSemaphore som stöder runtime max-justering).",
                "Fixade tyst felsuppression: 7 except: pass-platser i Kokoro-hanteraren loggar nu varningar.",
                "Fixade bar except: i MMS safe_terminate, macOS safe_terminate och system_utils CPU-detektering.",
                "Lade till fixplan för återstående 11 problem i AI_Documents/Plan.md.",
            ],
        },
    ),
    ReleaseNoteEntry(
        version="26.7.2",
        title={
            "en": "Batch preview loading, EdgeTTS timeout separation, and backup guard",
            "vi": "Tải batch preview, tách timeout EdgeTTS, và backup guard",
            "ko": "배치 미리보기 로딩, EdgeTTS 타임아웃 분리, 백업 가드",
            "zh-CN": "批量预览加载、EdgeTTS超时分离和备份守卫",
            "zh-TW": "批量預覽載入、EdgeTTS超時分離和備份守衛",
            "ja": "バッチプレビュー読み込み、EdgeTTS タイムアウト分離、バックアップガード",
            "sv": "Batch-förhandsvisning laddning, EdgeTTS timeout-separation och backup-skydd",
        },
        bullets={
            "en": [
                "Fixed batch preview showing only 1 note per page during preview (must_continue=False causing break after first note).",
                "Fixed batch preview dataChanged range using widened loaded_note_ids instead of exact page rows.",
                "Changed batch preview to load all pages sequentially on dialog open instead of on scroll.",
                "Generate button now disabled until all notes fully loaded; re-disabled on settings change.",
                "Status label shows 'Loading X of Y notes' during preview page loading.",
                "Separated EdgeTTS TimeoutError from connectivity errors; timeouts no longer trigger 60s global backoff.",
                "Increased EdgeTTS per-request timeout from 30s to 180s for Vietnamese/diacritic text.",
                "Increased EdgeTTS retry backoff 3s->5s and connectivity backoff 15s->60s; added jitter.",
                "Connectivity failures in EdgeTTS now retry instead of returning immediately.",
                "Added backup_guard module to suppress Anki's backup dialog and periodic backup timer.",
                "Moved undo entry inside each apply chunk instead of one undo for the whole chain.",
                "Optimized get_all_fields_from_notes to chunk SQL queries (500 per batch).",
                "Updated offline TTS engine default workers from 1 to CPU-count-based.",
                "Show total note count in progress bar during deduped generation.",
            ],
            "vi": [
                "Sửa lỗi batch preview chỉ hiển thị 1 note mỗi trang do must_continue=False.",
                "Sửa lỗi dataChanged dùng loaded_note_ids bị mở rộng thay vì hàng chính xác.",
                "Đổi batch preview sang tải tuần tự tất cả trang khi mở hộp thoại.",
                "Nút Generate bị vô hiệu hóa đến khi tất cả notes được tải xong.",
                "Nhãn trạng thái hiển thị 'Đang tải X của Y notes' khi đang tải.",
                "Tách TimeoutError khỏi lỗi kết nối EdgeTTS; timeout không còn kích hoạt backoff 60s.",
                "Tăng timeout EdgeTTS từ 30s lên 180s cho text tiếng Việt có dấu.",
                "Tăng retry backoff 3s->5s và connectivity backoff 15s->60s; thêm jitter.",
                "Lỗi kết nối EdgeTTS được retry thay vì trả về ngay.",
                "Thêm module backup_guard để chặn hộp thoại backup và timer định kỳ.",
                "Di chuyển undo entry vào từng chunk apply.",
                "Tối ưu get_all_fields_from_notes bằng chunk SQL (500 note/batch).",
                "Cập nhật worker mặc định cho engine TTS ngoại tuyến dựa trên số CPU.",
                "Hiển thị tổng số notes trong progress bar khi generation có dedup.",
            ],
            "ko": [
                "must_continue=False로 인해 미리보기 페이지당 1개 노트만 표시되던 배치 미리보기 버그 수정.",
                "dataChanged 범위가 정확한 페이지 행 대신 확장된 loaded_note_ids를 사용하던 문제 수정.",
                "대화상자 열릴 때 스크롤이 아닌 모든 페이지를 순차적으로 로드하도록 변경.",
                "모든 노트가 로드될 때까지 생성 버튼 비활성화, 설정 변경 시 다시 비활성화.",
                "상태 레이블에 'X/Y 노트 로딩 중' 표시.",
                "EdgeTTS TimeoutError를 연결 오류와 분리, 타임아웃이 더 이상 60s 백오프 트리거하지 않음.",
                "EdgeTTS 요청 타임아웃 30s→180s로 증가 (베트남어/발음 구별 부호).",
                "재시도 백오프 3s→5s, 연결 백오프 15s→60s 증가, 지터 추가.",
                "EdgeTTS 연결 실패 시 즉시 반환 대신 재시도.",
                "Anki 백업 대화상자와 주기적 백업 타이머를 억제하는 backup_guard 모듈 추가.",
                "전체 체인 하나의 실행 취소 대신 각 청크 내부로 실행 취소 이동.",
                "get_all_fields_from_notes SQL 청크(배치당 500개)로 최적화.",
                "오프라인 TTS 엔진 기본 작업자 1→CPU 수 기반으로 업데이트.",
                "중복 제거 생성 중 진행률 표시줄에 총 노트 수 표시.",
            ],
            "zh-CN": [
                "修复了预览期间每页仅显示1条笔记的批量预览错误（must_continue=False导致第一条后中断）。",
                "修复了dataChanged范围使用扩展的loaded_note_ids而非精确页面行的问题。",
                "批量预览在对话框打开时改为顺序加载所有页面，而非滚动时加载。",
                "生成按钮在所有笔记完全加载前保持禁用，设置更改后重新禁用。",
                "状态标签在预览加载期间显示'正在加载 X/Y 条笔记'。",
                "将EdgeTTS TimeoutError与连接错误分离；超时不再触发60秒全局退避。",
                "EdgeTTS每次请求超时从30秒增加到180秒（越南语/变音符号文本）。",
                "重试退避从3秒增加到5秒，连接退避从15秒增加到60秒；添加抖动。",
                "EdgeTTS连接失败现在会重试而非立即返回。",
                "添加backup_guard模块以抑制Anki的备份对话框和定期备份计时器。",
                "将撤销条目移入每个应用块内，而非整个链使用一个撤销条目。",
                "优化get_all_fields_from_notes为SQL分块查询（每批500条）。",
                "离线TTS引擎的默认工作线程从1更新为基于CPU数量。",
                "在去重生成期间，进度条显示笔记总数。",
            ],
            "zh-TW": [
                "修復了預覽期間每頁僅顯示1條筆記的批量預覽錯誤。",
                "修復了dataChanged範圍使用擴展的loaded_note_ids而非精確頁面行的問題。",
                "批量預覽在對話框開啟時改為順序載入所有頁面，而非滾動時載入。",
                "產生按鈕在所有筆記完全載入前保持禁用，設定變更後重新禁用。",
                "狀態標籤在預覽載入期間顯示'正在載入 X/Y 條筆記'。",
                "將EdgeTTS TimeoutError與連線錯誤分離；逾時不再觸發60秒全域退避。",
                "EdgeTTS每次請求逾時從30秒增加到180秒。",
                "新增backup_guard模組以抑制Anki的備份對話框和定期備份計時器。",
                "將復原條目移入每個應用區塊內。",
            ],
            "ja": [
                "プレビュー中に1ページに1ノートしか表示されなかったバッチプレビューのバグを修正。",
                "dataChanged範囲が拡張されたloaded_note_idsを使用していた問題を修正。",
                "ダイアログを開いたときにスクロールではなく全ページを順次読み込むように変更。",
                "すべてのノートが読み込まれるまで生成ボタンを無効にし、設定変更時に再び無効化。",
                "ステータスラベルに'X/Y ノートを読み込み中'と表示。",
                "EdgeTTS TimeoutErrorを接続エラーから分離。タイムアウトが60秒のグローバルバックオフをトリガーしない。",
                "EdgeTTSのリクエストタイムアウトを30秒から180秒に増加。",
                "backup_guardモジュールを追加してAnkiのバックアップダイアログと定期バックアップタイマーを抑制。",
                "各適用チャンク内に元に戻すエントリを移動。",
            ],
            "sv": [
                "Fixade batch-preview som endast visade 1 anteckning per sida under förhandsvisning.",
                "Fixade dataChanged-intervall som använde utökade loaded_note_ids istället för exakta sidrader.",
                "Batch-preview laddar nu alla sidor sekventiellt när dialogrutan öppnas istället för vid scrollning.",
                "Generera-knappen inaktiveras tills alla anteckningar har laddats; återinaktiveras vid inställningsändring.",
                "Statusetiketten visar 'Laddar X av Y anteckningar' under förhandsvisning.",
                "Separerade EdgeTTS TimeoutError från anslutningsfel; timeout utlöser inte längre 60s global backoff.",
                "EdgeTTS timeout per förfrågan ökad från 30s till 180s för vietnamesisk/diakritisk text.",
                "Lade till backup_guard-modul för att dämpa Ankis backup-dialog och periodisk backup-timer.",
                "Flyttade ångra-post inuti varje appliceringsbit istället för en ångra-post för hela kedjan.",
            ],
        },
    ),
    ReleaseNoteEntry(
        version="26.7.1",
        title={
            "en": "Anki addon update",
            "vi": "Cập nhật addon Anki",
            "ko": "Anki 애드온 업데이트",
            "zh-CN": "Anki 插件更新",
            "zh-TW": "Anki 外掛更新",
            "ja": "Anki アドオン更新",
            "sv": "Anki-tilläggsuppdatering",
        },
        bullets={
            "en": [
                "Updated addon versioning to 26.7.1 using the AMD-style release format: year.month.release, so 26.7.1 means the first release in July 2026.",
                "Added Anki collection path handling so DB access follows the active profile path.",
                "Added note-loading helpers and lazy note list scaffolding for smoother large-note handling.",
                "Verified the packaged addon includes the new DB helper and related modules in the built archive.",
            ],
            "vi": [
                "Cập nhật phiên bản addon lên 26.7.1 theo định dạng phát hành kiểu AMD: năm.tháng.bản-phát-hành, nên 26.7.1 là bản phát hành đầu tiên vào tháng 7 năm 2026.",
                "Thêm xử lý đường dẫn collection của Anki để truy cập cơ sở dữ liệu theo đúng profile đang hoạt động.",
                "Thêm helper tải note và khung danh sách note lười để xử lý số lượng note lớn mượt hơn.",
                "Đã xác minh gói addon đã đóng gồm helper DB mới và các module liên quan trong file .ankiaddon đã build.",
            ],
            "ko": [
                "AMD 스타일 릴리스 형식인 연도.월.배포번호에 따라 애드온 버전을 26.7.1로 업데이트했습니다. 따라서 26.7.1은 2026년 7월의 첫 번째 릴리스입니다.",
                "활성 프로필 경로를 따라 DB 접근이 이루어지도록 Anki collection 경로 처리를 추가했습니다.",
                "대량 노트 처리에 더 부드럽게 대응하도록 노트 로딩 헬퍼와 지연 로딩 리스트 구조를 추가했습니다.",
                "빌드된 .ankiaddon 패키지에 새 DB 헬퍼와 관련 모듈이 포함되도록 확인했습니다.",
            ],
            "zh-CN": [
                "按照 AMD 风格的版本格式更新插件版本为 26.7.1：年.月.发布序号，因此 26.7.1 表示 2026 年 7 月的第 1 个版本。",
                "新增 Anki collection 路径处理，让数据库访问跟随当前活跃配置文件路径。",
                "新增笔记加载辅助逻辑与懒加载笔记列表骨架，以更顺畅地处理大量笔记。",
                "已确认生成的 .ankiaddon 包含新的 DB helper 及相关模块。",
            ],
            "zh-TW": [
                "依照 AMD 風格的版本格式更新外掛版本為 26.7.1：年.月.發布序號，因此 26.7.1 表示 2026 年 7 月的第 1 個版本。",
                "新增 Anki collection 路徑處理，讓資料庫存取跟隨目前使用中的設定檔路徑。",
                "新增筆記載入輔助邏輯與延遲載入筆記清單骨架，以更順暢處理大量筆記。",
                "已確認產生的 .ankiaddon 套件包含新的 DB helper 與相關模組。",
            ],
            "ja": [
                "AMD 形式のリリース規則に合わせて、アドオンのバージョンを 26.7.1 に更新しました。年.月.リリース番号の形式で、26.7.1 は 2026 年 7 月の第 1 リリースを意味します。",
                "Anki の collection パスを基準にして、現在のアクティブプロファイルに合わせて DB へアクセスする処理を追加しました。",
                "大量ノートをより滑らかに扱えるよう、ノート読み込みヘルパーと遅延読み込みリストの土台を追加しました。",
                "生成した .ankiaddon パッケージに、新しい DB helper と関連モジュールが含まれることを確認しました。",
            ],
            "sv": [
                "Uppdaterade tilläggsversionen till 26.7.1 enligt AMD-stilens releaseformat: år.månad.release, så betyder 26.7.1 den första releasen i juli 2026.",
                "Lade till hantering av Anki collection-sökväg så att databasanvändning följer den aktiva profilen.",
                "Lade till hjälpfunktioner för att ladda anteckningar och en lat liststruktur för smidigare hantering av stora anteckningsmängder.",
                "Verifierade att den packade .ankiaddon-filen innehåller den nya DB-hjälparen och de relaterade modulerna.",
            ],
        },
    ),
    ReleaseNoteEntry(
        version="1.4",
        title={
            "en": "Core refactor and sync",
            "vi": "Tái cấu trúc module lõi và đồng bộ",
            "ko": "핵심 모듈 리팩터링 및 동기화",
            "zh-CN": "核心模块重构与同步",
            "zh-TW": "核心模組重構與同步",
            "ja": "コアモジュールのリファクタリングと同期",
            "sv": "Kärnmodul refaktorering och synkronisering",
        },
        bullets={
            "en": [
                "Refactored superfreetts.py God Class into dedicated modules for better separation of concerns.",
                "Added Supertonic TTS support and worker fixes.",
                "Fixed UI workflow issues and resolved NameError in batch_orchestrator.py.",
                "Added automated test suite and GitHub Actions CI.",
                "Synced addon code and dependencies.",
            ],
            "vi": [
                "Tái cấu trúc superfreetts.py God Class thành các module riêng để phân tách chức năng tốt hơn.",
                "Hỗ trợ Supertonic TTS và sửa worker.",
                "Sửa lỗi UI workflow và NameError trong batch_orchestrator.py.",
                "Thêm bộ test tự động và GitHub Actions CI.",
                "Đồng bộ hóa mã nguồn và các dependency của addon.",
            ],
            "ko": [
                "관심사 분리를 개선하기 위해 superfreetts.py God Class를 전용 모듈로 리팩터링했습니다.",
                "Supertonic TTS 지원 및 worker 수정을 추가했습니다.",
                "UI 워크플로 문제를 수정하고 batch_orchestrator.py의 NameError를 해결했습니다.",
                "자동화된 테스트 스위트와 GitHub Actions CI를 추가했습니다.",
                "애드온 코드와 종속성을 동기화했습니다.",
            ],
            "zh-CN": [
                "重构了 superfreetts.py God Class 为专用模块，以实现更好的关注点分离。",
                "添加了 Supertonic TTS 支持和 worker 修复。",
                "修复了 UI workflow 问题，并解决了 batch_orchestrator.py 中的 NameError。",
                "添加了自动化测试套件和 GitHub Actions CI。",
                "同步了插件代码和依赖项。",
            ],
            "zh-TW": [
                "重構了 superfreetts.py God Class 為專用模組，以實現更好的關注點分離。",
                "新增了 Supertonic TTS 支援和 worker 修復。",
                "修復了 UI workflow 問題，並解決了 batch_orchestrator.py 中的 NameError。",
                "新增了自動化測試套件和 GitHub Actions CI。",
                "同步了插件程式碼和相依性。",
            ],
            "ja": [
                "関心の分離と保守性を向上させるため、`superfreetts.py` の God Class を専用モジュールへリファクタリングしました。",
                "Supertonic TTS のサポートを追加し、ワーカー関連の問題を修正しました。",
                "UI ワークフローの問題を修正し、`batch_orchestrator.py` の `NameError` を解消しました。",
                "自動テストスイートと GitHub Actions CI を追加しました。",
                "アドオンのコードと依存関係を同期しました。",
            ],
            "sv": [
                "Refaktorerade God Class i `superfreetts.py` till dedikerade moduler för bättre ansvarsfördelning och enklare underhåll.",
                "Lade till stöd för Supertonic TTS och åtgärdade problem relaterade till workers.",
                "Åtgärdade problem i användargränssnittets arbetsflöde och löste ett `NameError` i `batch_orchestrator.py`.",
                "Lade till ett automatiserat testpaket samt GitHub Actions CI.",
                "Synkroniserade tilläggets kod och beroenden.",
            ],
        },
    ),
    ReleaseNoteEntry(
        version="1.3.4",
        title={
            "en": "Workflow generate-first apply controls",
            "vi": "Workflow tạo trước rồi áp dụng",
            "ko": "워크플로 먼저 생성 후 적용",
            "zh-CN": "Workflow 先生成后应用控制",
            "zh-TW": "Workflow 先生成後套用控制",
            "ja": "Workflow の先生成・後適用コントロール",
        },
        bullets={
            "en": [
                "Workflow now generates audio for all presets first, then waits before writing sound tags to notes.",
                "Added Apply Selected Preset so a generated workflow preset can be applied one at a time.",
                "Added Apply All so all generated workflow preset results can be applied in one pass.",
                "Generated workflow presets are marked as ready to apply in the Workflow list.",
                "The AnkiVN menu entry now shows a headphone icon: 🎧 Super Free TTS Settings.",
                "EdgeTTS Advanced Settings labels are now localized in the Services settings page.",
                "Locale dictionaries are now split into separate JSON files under superfreetts_addon/locales/.",
            ],
            "vi": [
                "Workflow bây giờ tạo audio cho toàn bộ preset trước, rồi chờ trước khi ghi sound tag vào note.",
                "Thêm Apply Selected Preset để áp dụng từng preset workflow đã tạo.",
                "Thêm Apply All để áp dụng toàn bộ kết quả workflow đã tạo trong một lượt.",
                "Preset workflow đã tạo sẽ được đánh dấu sẵn sàng áp dụng trong danh sách Workflow.",
                "Menu AnkiVN bây giờ có icon tai nghe: 🎧 Super Free TTS Settings.",
                "Nhãn Cài đặt nâng cao của EdgeTTS trong trang Services bây giờ đã có bản dịch.",
                "Dictionary ngôn ngữ bây giờ đã được tách thành từng file JSON riêng trong superfreetts_addon/locales/.",
            ],
            "ko": [
                "워크플로가 모든 프리셋의 오디오를 먼저 생성한 뒤 노트에 sound tag를 쓰기 전에 대기합니다.",
                "생성된 워크플로 프리셋을 하나씩 적용할 수 있도록 Apply Selected Preset을 추가했습니다.",
                "생성된 모든 워크플로 프리셋 결과를 한 번에 적용할 수 있도록 Apply All을 추가했습니다.",
                "생성 완료된 워크플로 프리셋은 워크플로 목록에서 적용 준비 상태로 표시됩니다.",
                "AnkiVN 메뉴 항목에 헤드폰 아이콘을 추가했습니다: 🎧 Super Free TTS Settings.",
                "Services 설정 페이지의 EdgeTTS 고급 설정 라벨을 현지화했습니다.",
                "Locale dictionary를 superfreetts_addon/locales/ 아래의 언어별 JSON 파일로 분리했습니다.",
            ],
            "zh-CN": [
                "Workflow 现在会先为所有预设生成音频，然后等待应用到笔记。",
                "新增 Apply Selected Preset，可逐个应用已生成的 workflow 预设。",
                "新增 Apply All，可一次性应用所有已生成的 workflow 预设结果。",
                "已生成的 workflow 预设会在 Workflow 列表中标记为可应用。",
                "AnkiVN 菜单项现在显示耳机图标：🎧 Super Free TTS Settings。",
                "Services 设置页中的 EdgeTTS 高级设置标签已本地化。",
                "Locale dictionary 已拆分为 superfreetts_addon/locales/ 下的独立 JSON 文件。",
                "新增简体中文、繁体中文（台湾）和日语的界面语言选项。",
            ],
            "zh-TW": [
                "Workflow 現在會先為所有預設生成音訊，然後等待套用到筆記。",
                "新增 Apply Selected Preset，可逐個套用已生成的 workflow 預設。",
                "新增 Apply All，可一次套用所有已生成的 workflow 預設結果。",
                "已生成的 workflow 預設會在 Workflow 清單中標記為可套用。",
                "AnkiVN 選單項目現在顯示耳機圖示：🎧 Super Free TTS Settings。",
                "Services 設定頁中的 EdgeTTS 進階設定標籤已在地化。",
                "Locale dictionary 已拆分為 superfreetts_addon/locales/ 下的獨立 JSON 檔案。",
                "新增簡體中文、繁體中文（台灣）和日文的介面語言選項。",
            ],
            "ja": [
                "Workflow はすべてのプリセットの音声を先に生成し、ノートへ書き込む前に待機するようになりました。",
                "生成済みの workflow プリセットを個別に適用できる Apply Selected Preset を追加しました。",
                "生成済みの workflow プリセット結果を一括で適用できる Apply All を追加しました。",
                "生成済みの workflow プリセットは Workflow リストで適用準備完了として表示されます。",
                "AnkiVN メニュー項目にヘッドホンアイコンを追加しました：🎧 Super Free TTS Settings。",
                "Services 設定ページの EdgeTTS 詳細設定ラベルをローカライズしました。",
                "Locale dictionary を superfreetts_addon/locales/ 配下の言語別 JSON ファイルに分割しました。",
                "簡体字中国語、繁体字中国語（台湾）、日本語の UI 言語オプションを追加しました。",
            ],
        },
    ),
    ReleaseNoteEntry(
        version="1.3.3",
        title={
            "en": "Batch cache, audio IO, and core cleanup",
            "vi": "Cache batch, ghi audio và dọn core",
            "ko": "배치 캐시, 오디오 입출력 및 핵심 코드 정리"
        },
        bullets={
            "en": [
                "Reduced duplicate TTS calls in large batches by caching processed text and deduplicating audio requests by processed text, voice, voice options, and output format.",
                "Improved audio file caching and writes with stable request hashes, non-empty disk cache checks, and atomic writes for generated audio files.",
                "Split source text resolution, audio file storage, and note audio updates out of superfreetss.py so the core batch path is easier to test and refactor.",
                "Added regression coverage for text/source resolution, audio file storage, batch cache/dedup behavior, note updates, text processing, and psutil integration.",
                "The current workflow and UI behavior remain unchanged.",
            ],
            "vi": [
                "Giảm gọi TTS trùng lặp trong batch lớn bằng cache processed text và dedup request audio theo processed text, voice, voice options và định dạng đầu ra.",
                "Cải thiện cache/ghi file audio với hash request ổn định, chỉ dùng disk cache khi file tồn tại và không rỗng, và ghi file theo cơ chế atomic.",
                "Tách xử lý source text, lưu file audio, và cập nhật sound tag của note ra khỏi superfreetss.py để core batch dễ test và dễ refactor tiếp.",
                "Bổ sung regression test cho resolver text/source, audio file store, batch cache/dedup, note updater, text processing và psutil.",
                "Workflow và hành vi UI hiện tại không thay đổi.",
            ],
            "ko": [
                "처리된 텍스트를 캐싱하고 처리된 텍스트, 음성, 음성 옵션 및 출력 형식을 기준으로 오디오 요청을 중복 제거하여 대규모 배치에서 중복 TTS 호출을 줄였습니다.",
                "안정적인 요청 해시, 비어 있지 않은 디스크 캐시 확인 및 생성된 오디오 파일에 대한 원자적 쓰기를 통해 오디오 파일 캐싱 및 저장을 개선했습니다.",
                "핵심 배치 경로를 더 쉽게 테스트하고 리팩터링할 수 있도록 원본 텍스트 해석, 오디오 파일 저장 및 노트 오디오 업데이트 로직을 superfreetss.py에서 분리했습니다.",
                "텍스트/원본 해석, 오디오 파일 저장, 배치 캐시/중복 제거 동작, 노트 업데이트, 텍스트 처리 및 psutil 통합에 대한 회귀 테스트 커버리지를 추가했습니다.",
                "현재 워크플로우와 UI 동작은 변경되지 않았습니다."
            ],
        },
    ),
    ReleaseNoteEntry(
        version="1.3.2",
        title={
            "en": "Settings cleanup",
            "vi": "Dọn dẹp Cài đặt",
            "ko": "설정 정리",
        },
        bullets={
            "en": [
                "Streamlined the Settings layout and cleaned up the release-note wording shown to users.",
                "The Generate then Apply workflow remains unchanged: audio is generated first, then notes are updated only after Apply Generated Audio.",
            ],
            "vi": [
                "Tinh gọn bố cục Cài đặt và làm sạch cách diễn đạt của phần ghi chú phát hành hiển thị cho người dùng.",
                "Workflow Tạo rồi Áp dụng vẫn giữ nguyên: âm thanh được tạo trước, sau đó note chỉ được cập nhật khi bấm Áp dụng âm thanh đã tạo.",
            ],
            "ko": [
                "설정 레이아웃을 정리하고 사용자에게 보이는 릴리스 노트 문구를 다듬었습니다.",
                "Generate 후 Apply 흐름은 그대로 유지됩니다. 오디오는 먼저 생성되고, Apply Generated Audio를 누른 뒤에만 노트가 업데이트됩니다.",
            ],
        },
    ),
    ReleaseNoteEntry(
        version="1.3.0",
        title={
            "en": "EdgeTTS stability update",
            "vi": "Cập nhật ổn định EdgeTTS",
            "ko": "EdgeTTS 안정성 업데이트",
        },
        bullets={
            "en": [
                "Public addon builds now use a safer EdgeTTS concurrency cap.",
                "The Generate then Apply workflow remains unchanged: audio is generated first, then notes are updated only after Apply Generated Audio.",
            ],
            "vi": [
                "Bản addon phát hành cho người dùng hiện dùng mức giới hạn EdgeTTS an toàn hơn.",
                "Workflow Tạo rồi Áp dụng vẫn giữ nguyên: âm thanh được tạo trước, sau đó note chỉ được cập nhật khi bấm Áp dụng âm thanh đã tạo.",
            ],
            "ko": [
                "공개 배포용 애드온은 EdgeTTS 동시 실행 수를 더 안전한 값으로 제한합니다.",
                "Generate 후 Apply 흐름은 그대로 유지됩니다. 오디오는 먼저 생성되고, Apply Generated Audio를 누른 뒤에만 노트가 업데이트됩니다.",
            ],
        },
    ),
    ReleaseNoteEntry(
        version="1.2.2",
        title={
            "en": "Generate first, apply when ready",
            "vi": "Tạo âm thanh trước, sẵn sàng thì áp dụng",
            "ko": "먼저 생성하고 준비되면 적용",
        },
        bullets={
            "en": [
                "Generate Audio now creates audio files first and does not update notes immediately.",
                "After generation finishes, use Apply Generated Audio to write sound tags to notes.",
                "Anki backup is triggered before applying generated audio to the collection.",
                "Large EdgeTTS batches now show active progress updates and use safer per-request timeouts.",
            ],
            "vi": [
                "Generate Audio bây giờ chỉ tạo file âm thanh trước và chưa cập nhật note ngay.",
                "Sau khi tạo xong, bấm Apply Generated Audio để ghi sound tag vào note.",
                "Addon sẽ gọi backup của Anki trước khi áp dụng âm thanh đã tạo vào collection.",
                "Batch EdgeTTS lớn bây giờ hiển thị tiến trình đang chạy và có timeout an toàn hơn cho từng request.",
            ],
            "ko": [
                "Generate Audio는 이제 먼저 오디오 파일만 생성하고 노트를 즉시 업데이트하지 않습니다.",
                "생성이 끝난 뒤 Apply Generated Audio로 노트에 sound tag를 기록합니다.",
                "생성된 오디오를 컬렉션에 적용하기 전에 Anki 백업을 먼저 실행합니다.",
                "큰 EdgeTTS 배치에서 실행 중인 진행 상황을 표시하고 요청별 timeout을 더 안전하게 적용합니다.",
            ],
        },
    ),
    ReleaseNoteEntry(
        version="1.2.1",
        title={
            "en": "Audio filename prefix cleanup",
            "vi": "Sửa tiền tố tên file audio",
            "ko": "오디오 파일 이름 접두사 정리",
        },
        bullets={
            "en": [
                "Newly generated audio files now use the superfreetts-<hash> filename prefix.",
                "Existing superfreetss-* cached audio files remain valid and are not renamed.",
            ],
            "vi": [
                "File audio tạo mới bây giờ dùng tiền tố tên file `superfreetts-<hash>`.",
                "Các file audio cache cũ `superfreetss-*` vẫn giữ nguyên và vẫn hợp lệ.",
            ],
            "ko": [
                "새로 생성되는 오디오 파일은 이제 superfreetts-<hash> 파일 이름 접두사를 사용합니다.",
                "기존 superfreetss-* 캐시 오디오 파일은 이름을 바꾸지 않으며 계속 유효합니다.",
            ],
        },
    ),
    ReleaseNoteEntry(
        version="1.2",
        title={
            "en": "EdgeTTS stability, ordered concurrency, and Sequence voices",
            "vi": "EdgeTTS ổn định hơn, chạy đúng thứ tự và thêm chế độ Sequence",
            "ko": "EdgeTTS 안정성, 순차 실행, Sequence 음성 모드",
        },
        bullets={
            "en": [
                "Improved EdgeTTS generation with retry, empty-audio detection, Unicode cleanup, and clearer no-audio/rate-limit logging.",
                "Changed EdgeTTS batch scheduling to run ordered waves of up to three requests so progress follows the note order more predictably.",
                "Added Advanced EdgeTTS controls for retry attempts, request jitter, wave start stagger, and retry backoff.",
                "Added the Sequence voice selection mode, which cycles through selected voices in order and loops back to the first voice.",
                "Fixed Priority voice selection so it now falls back to a second voice if the first voice fails, and similarly if more voices are configured.",
                "Added runnable EdgeTTS verification scripts, including a combined verify_edgetts smoke test.",
                "Added workflow function so you can now generate with multiple presets at the same time ",
            ],
            "vi": [
                "Cải thiện EdgeTTS với retry, kiểm tra audio rỗng, làm sạch Unicode và log rõ hơn khi bị no-audio/rate-limit.",
                "Đổi batch EdgeTTS sang wave tối đa 3 request theo thứ tự note để tiến trình dễ theo dõi hơn.",
                "Thêm các tùy chọn Advanced cho EdgeTTS: số lần retry, request jitter, wave start stagger và retry backoff.",
                "Thêm chế độ chọn giọng Sequence, tự động xoay vòng các giọng theo thứ tự đã chọn.",
                "Sửa Priority voice selection để bây giờ sẽ fallback sang giọng thứ hai nếu giọng đầu lỗi, và tương tự nếu có nhiều giọng hơn.",
                "Thêm bộ kiểm tra EdgeTTS có thể chạy trực tiếp, gồm smoke test verify_edgetts.",
                "Thêm cơ chế workflow nên bây giờ bạn có thể tạo âm thanh với nhiều presets cùng lúc.",
            ],
            "ko": [
                "EdgeTTS 재시도 동작, 빈 오디오 처리, 유니코드 정리, 그리고 더 명확한 rate-limit 로그를 개선했습니다.",
                "EdgeTTS 생성을 최대 3개의 요청으로 구성된 순차적 웨이브로 변경하여 진행 상황을 더 쉽게 추적할 수 있게 했습니다.",
                "재시도 횟수, 지터, 웨이브 시작 간격, 재시도 백오프를 위한 고급 EdgeTTS 제어 기능을 추가했습니다.",
                "선택된 음성을 순서대로 순환하는 Sequence 음성 선택 모드를 추가했습니다.",
                "Priority 음성 선택을 수정하여 첫 번째 음성이 실패할 경우 두 번째 음성으로 자동으로 대체되며, 더 많은 음성이 구성되어 있으면 동일하게 동작합니다.",
                "실행 가능한 EdgeTTS 스모크 검증 스크립트를 추가했습니다.",
                "워크플로우 기능이 추가되어 이제 여러 프리셋을 동시에 사용해 생성할 수 있습니다.",
            ],
        },
    ),
    ReleaseNoteEntry(
        version="1.1.2",
        title={
            "en": "Korean UI language and release note coverage",
            "vi": "Bổ sung ngôn ngữ giao diện tiếng Hàn và cập nhật thông báo",
            "ko": "한국어 UI 언어 및 업데이트 안내 확장",
        },
        bullets={
            "en": [
                "Added Korean (ko) as a supported UI language and expanded the language picker in Preferences.",
                "Localized the main Settings dialogs, About tab, Workflow, Failure Report, and common browser/editor controls for Korean.",
                "Fixed the Preferences language combobox so it restores the saved language correctly after reopening Settings.",
                "Updated the addon version and release note flow so Korean users see localized update text.",
            ],
            "vi": [
                "Bổ sung tiếng Hàn (ko) như một ngôn ngữ giao diện được hỗ trợ và mở rộng bộ chọn ngôn ngữ trong Preferences.",
                "Dịch các hộp thoại Settings chính, tab About, Workflow, Failure Report và các điều khiển chung trong browser/editor sang tiếng Hàn.",
                "Sửa combobox ngôn ngữ trong Preferences để nó khôi phục đúng ngôn ngữ đã lưu khi mở lại Settings.",
                "Cập nhật version addon và luồng release notes để người dùng tiếng Hàn thấy nội dung cập nhật đã được bản địa hóa.",
            ],
            "ko": [
                "Korean(ko)을 지원되는 UI 언어로 추가하고 Preferences의 언어 선택 목록을 확장했습니다.",
                "주요 Settings 대화상자, About 탭, Workflow, Failure Report, 그리고 브라우저/에디터 공용 컨트롤을 한국어로 현지화했습니다.",
                "Preferences 언어 콤보박스가 Settings를 다시 열 때 저장된 언어를 정확히 복원하도록 수정했습니다.",
                "애드온 버전과 release notes 흐름을 업데이트해 한국어 사용자가 현지화된 업데이트 문구를 보게 했습니다.",
            ],
        },
    ),
    ReleaseNoteEntry(
        version="1.1.1",
        title={
            "en": "Settings refactor and Preferences translation fixes",
            "vi": "Tái cấu trúc Settings và sửa bản dịch Preferences",
            "ko": "Settings 리팩터링과 Preferences 번역 수정",
        },
        bullets={
            "en": [
                "Refactored the Settings window into modular components: Settings, Services, Preferences, and Troubleshooting.",
                "Split the previous unified settings implementation into dedicated modules and updated the main UI wiring accordingly.",
                "Fixed incorrect Preferences translations where English could show Vietnamese or mojibake text.",
                "Added the missing Vietnamese translations for the new Preferences sections and helper text.",
            ],
            "vi": [
                "Tái cấu trúc cửa sổ Settings thành các component riêng: Settings, Services, Preferences và Troubleshooting.",
                "Tách phần cài đặt hợp nhất trước đây thành các module chuyên biệt và cập nhật lại phần nối UI chính cho phù hợp.",
                "Sửa lỗi bản dịch trong Preferences khiến giao diện tiếng Anh có thể hiển thị tiếng Việt hoặc chuỗi lỗi mã hóa.",
                "Bổ sung các bản dịch tiếng Việt còn thiếu cho các section mới trong Preferences và các helper text liên quan.",
            ],
            "ko": [
                "Settings 창을 Settings, Services, Preferences, Troubleshooting으로 분리된 모듈 구조로 리팩터링했습니다.",
                "기존의 통합 Settings 구현을 전용 모듈로 나누고 메인 UI 연결을 정리했습니다.",
                "Preferences에서 영어로 보이거나 깨진 문자로 나타나던 번역 문제를 수정했습니다.",
                "새 Preferences 섹션과 helper text에 필요한 베트남어 번역을 추가했습니다.",
            ],
        },
    ),
    ReleaseNoteEntry(
        version="1.1.0",
        title={
            "en": "Generate Audio Files refresh and startup announcements",
            "vi": "Làm mới Generate Audio Files và thông báo khi cập nhật",
        },
        bullets={
            "en": [
                "Renamed the batch dialog to Generate Audio Files so the window title matches the Browser menu.",
                "Added Workflow to the Super Free TTS Browser menu for running multi-preset flows from selected notes.",
                "Added a New preset button and simplified the preset toolbar by removing the unused Open flow.",
                "Changed the main batch action label to Generate Audio and cleaned up the preset switching logic.",
                "Removed the editor-only selected text option from batch mode to avoid confusion when many notes are selected.",
                "New installs now see Welcome, while existing users see a localized What's New popup after addon updates.",
            ],
            "vi": [
                "Đổi tên hộp thoại batch thành Generate Audio Files để title của sổ khớp với menu trong Browser.",
                "Thêm Workflow vào menu Super Free TTS trong Browser để chạy luồng nhiều preset trên các note đang chọn.",
                "Thêm nút New cho preset và đơn giản hóa thanh preset bằng cách bỏ luồng Open không còn cần thiết.",
                "Đổi nhãn nút chạy batch thành Generate Audio và làm gọn logic chuyển preset.",
                "Ẩn tùy chọn chọn đoạn văn bản khỏi batch mode vì nó chỉ có ý nghĩa trong editor của một note.",
                "Người cài mới sẽ thấy Welcome, còn người cập nhật addon sẽ thấy popup What's New theo ngôn ngữ giao diện.",
            ],
        },
    ),
]


def version_key(version: Optional[str]) -> Tuple[int, ...]:
    if not version:
        return tuple()
    return tuple(int(part) for part in re.findall(r"\d+", version))


def get_release_notes_since(
    last_seen_version: Optional[str],
    current_version: str,
) -> List[ReleaseNoteEntry]:
    current_key = version_key(current_version)
    last_seen_key = version_key(last_seen_version)

    entries = [
        entry
        for entry in RELEASE_NOTES
        if version_key(entry.version) <= current_key
        and (not last_seen_key or version_key(entry.version) > last_seen_key)
    ]
    return sorted(entries, key=lambda entry: version_key(entry.version), reverse=True)
