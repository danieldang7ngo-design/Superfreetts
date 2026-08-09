import html

import aqt.qt

from . import constants
from . import i18n
from . import logging_utils
from . import version

logger = logging_utils.get_child_logger(__name__)


class ReleaseNotesDialog(aqt.qt.QDialog):
    def __init__(self, hypertts, release_entries, current_version, parent=None):
        super().__init__(parent)
        self.hypertts = hypertts
        self.release_entries = release_entries
        self.current_version = current_version
        lang = self.hypertts.get_ui_language()

        self.setWindowTitle(i18n.get_text("release_notes_window_title", lang))
        self.setMinimumSize(420, 360)
        self.resize(680, 560)
        self.setWindowFlags(
            self.windowFlags() & ~aqt.qt.Qt.WindowType.WindowContextHelpButtonHint
        )
        self.setStyleSheet(
            f"""
            QDialog {{
                background-color: {constants.COLOR_SURFACE_LIGHT};
            }}
            QLabel#Header {{
                color: {constants.COLOR_PRIMARY};
                font-size: 22px;
                font-weight: bold;
            }}
            QLabel#Intro {{
                color: {constants.COLOR_SECONDARY};
                font-size: 12px;
            }}
            QTextBrowser {{
                background: white;
                border: 1px solid {constants.COLOR_BORDER};
                border-radius: 12px;
                padding: 14px;
                color: {constants.COLOR_PRIMARY};
            }}
            QPushButton#Primary {{
                background-color: {constants.COLOR_ACCENT};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 18px;
                font-weight: bold;
            }}
            QPushButton#Primary:hover {{
                background-color: {constants.COLOR_ACCENT_HOVER};
            }}
            """
        )

        layout = aqt.qt.QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(14)

        header = aqt.qt.QLabel(i18n.get_text("release_notes_header", lang))
        header.setObjectName("Header")
        layout.addWidget(header)

        intro = aqt.qt.QLabel(
            i18n.get_text("release_notes_intro", lang).format(current_version)
        )
        intro.setObjectName("Intro")
        intro.setWordWrap(True)
        layout.addWidget(intro)

        browser = aqt.qt.QTextBrowser()
        browser.setOpenExternalLinks(True)
        browser.setHtml(self._build_html(lang))
        layout.addWidget(browser, 1)

        footer = aqt.qt.QLabel(
            i18n.get_text("release_notes_footer", lang).format(
                version.ANKI_SUPER_FREE_TTS_VERSION
            )
        )
        footer.setObjectName("Intro")
        footer.setWordWrap(True)
        layout.addWidget(footer)

        button_row = aqt.qt.QHBoxLayout()
        button_row.addStretch()
        close_button = aqt.qt.QPushButton(
            i18n.get_text("release_notes_button_close", lang)
        )
        close_button.setObjectName("Primary")
        close_button.clicked.connect(self.accept)
        button_row.addWidget(close_button)
        layout.addLayout(button_row)

    def _build_html(self, lang: str) -> str:
        sections = []
        for entry in self.release_entries:
            title = entry.title.get(lang) or entry.title.get("en") or entry.version
            bullets = entry.bullets.get(lang) or entry.bullets.get("en") or []
            bullet_html = "".join(f"<li>{html.escape(item)}</li>" for item in bullets)
            sections.append(
                f"""
                <div style="margin-bottom: 18px;">
                    <div style="font-size: 18px; font-weight: bold; color: {constants.COLOR_PRIMARY};">
                        v{html.escape(entry.version)} - {html.escape(title)}
                    </div>
                    <ul style="margin-top: 8px; line-height: 1.7;">
                        {bullet_html}
                    </ul>
                </div>
                """
            )

        return f"""
        <html>
            <body style="font-family: Segoe UI, Arial, sans-serif;">
                {''.join(sections)}
            </body>
        </html>
        """
