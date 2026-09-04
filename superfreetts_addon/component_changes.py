import html

import aqt.qt

from . import component_common
from . import constants
from . import i18n
from . import release_notes


class ChangesPage(component_common.ConfigComponentBase):
    def __init__(self, hypertts):
        self.hypertts = hypertts

    def get_model(self):
        return None

    def load_model(self, model):
        pass

    def draw(self, layout):
        lang = self.hypertts.get_ui_language()

        container = aqt.qt.QWidget()
        container.setStyleSheet(
            f"QWidget {{ background: transparent; color: {constants.COLOR_PRIMARY}; }}"
        )

        page_layout = aqt.qt.QVBoxLayout(container)
        page_layout.setContentsMargins(0, 0, 0, 0)
        page_layout.setSpacing(12)

        header = aqt.qt.QLabel(i18n.get_text("changes_header", lang))
        header_font = header.font()
        header_font.setPointSize(18)
        header_font.setBold(True)
        header.setFont(header_font)
        header.setWordWrap(True)
        header.setStyleSheet(f"color: {constants.COLOR_PRIMARY};")
        page_layout.addWidget(header)

        intro = aqt.qt.QLabel(i18n.get_text("changes_intro", lang))
        intro.setWordWrap(True)
        intro.setStyleSheet(f"color: {constants.COLOR_SECONDARY}; font-size: 12px;")
        page_layout.addWidget(intro)

        browser = aqt.qt.QTextBrowser()
        browser.setOpenExternalLinks(True)
        browser.setStyleSheet(
            f"""
            QTextBrowser {{
                background: white;
                border: 1px solid {constants.COLOR_BORDER};
                border-radius: 12px;
                padding: 14px;
                color: {constants.COLOR_PRIMARY};
            }}
            """
        )
        browser.setHtml(self._build_html(lang))
        page_layout.addWidget(browser, 1)

        layout.addWidget(container)

    def _build_html(self, lang: str) -> str:
        sections = []
        for entry in release_notes.RELEASE_NOTES:
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


ChangesComponent = ChangesPage
