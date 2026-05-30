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
        version="1.3.3",
        title={
            "en": "Batch cache, audio IO, and core cleanup",
            "vi": "Cache batch, ghi audio, va don core",
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
                "Giam goi TTS trung lap trong batch lon bang cache processed text va dedup request audio theo processed text, voice, voice options va dinh dang dau ra.",
                "Cai thien cache/ghi file audio voi hash request on dinh, chi dung disk cache khi file ton tai va khong rong, va ghi file theo co che atomic.",
                "Tach xu ly source text, luu file audio, va cap nhat sound tag cua note ra khoi superfreetss.py de core batch de test va de refactor tiep.",
                "Bo sung regression test cho resolver text/source, audio file store, batch cache/dedup, note updater, text processing va psutil.",
                "Workflow va hanh vi UI hien tai khong thay doi.",
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
