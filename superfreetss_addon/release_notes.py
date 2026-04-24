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
        version="1.1.1",
        title={
            "en": "Settings refactor and Preferences translation fixes",
            "vi": "Tái cấu trúc Settings và sửa bản dịch Preferences",
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
                "Đổi tên hộp thoại batch thành Generate Audio Files để title cửa sổ khớp với menu trong Browser.",
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
