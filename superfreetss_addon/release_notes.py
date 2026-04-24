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
    return sorted(entries, key=lambda entry: version_key(entry.version))
