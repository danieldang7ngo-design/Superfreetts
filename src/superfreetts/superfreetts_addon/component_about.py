import aqt.qt
import webbrowser
from . import component_common
from . import constants
from . import gui_utils
from . import version
from . import i18n
from . import logging_utils

logger = logging_utils.get_child_logger(__name__)


class AboutPage(component_common.ConfigComponentBase):
    INFO_ITEMS = (
        {
            "label_key": "about_author",
            "title": "Paul from AnkiVN",
            "description_key": "about_author_role",
            "url": "https://facebook.com/dangngooooo",
        },
        {
            "label_key": "about_contributor",
            "title": "Lê Hoàng Phúc",
            "description_key": "about_contributor_role",
            "url": "https://www.facebook.com/tui.la.phuc747",
        },
        {
            "label_key": "about_website",
            "title": "AnkiVN",
            "description_key": "about_website_role",
            "url": "https://ankivn.com",
        },
        {
            "label_key": "about_github",
            "title": "GitHub",
            "description_key": "about_github_role",
            "url": "https://github.com/danieldang7ngo-design/Superfreetts",
        },
    )

    def __init__(self, hypertts):
        self.hypertts = hypertts

    def get_model(self):
        return None

    def load_model(self, model):
        pass

    def draw(self, layout):
        lang = self.hypertts.get_ui_language()
        dark = gui_utils.is_night_mode()
        palette = self._get_palette(dark)

        container = aqt.qt.QWidget()
        container.setStyleSheet(f"QWidget {{ background: transparent; color: {palette['text_primary']}; }}")

        page_layout = aqt.qt.QVBoxLayout(container)
        page_layout.setContentsMargins(0, 0, 0, 0)
        page_layout.setSpacing(18)

        page_layout.addWidget(self._build_hero_card(lang, palette))
        page_layout.addWidget(self._build_info_section(lang, palette))
        page_layout.addWidget(self._build_action_section(lang, palette))

        footer_label = aqt.qt.QLabel(i18n.get_text("about_footer", lang))
        footer_label.setAlignment(aqt.qt.Qt.AlignmentFlag.AlignCenter)
        footer_label.setWordWrap(True)
        footer_label.setStyleSheet(
            f"color: {palette['text_muted']}; font-size: 11px; padding: 2px 6px 0 6px;"
        )
        page_layout.addWidget(footer_label)
        page_layout.addStretch()

        layout.addWidget(container)

    def _build_hero_card(self, lang, palette):
        card = self._create_card()
        card.setStyleSheet(
            f"""
            QFrame {{
                background-color: {palette['hero_bg']};
                border: 1px solid {palette['hero_border']};
                border-radius: 22px;
            }}
            QLabel {{
                background: transparent;
                border: none;
            }}
            """
        )

        card_layout = aqt.qt.QVBoxLayout(card)
        card_layout.setContentsMargins(24, 24, 24, 24)
        card_layout.setSpacing(14)

        top_row = aqt.qt.QHBoxLayout()
        top_row.setSpacing(12)

        title_label = aqt.qt.QLabel(i18n.get_text("about_header_title", lang))
        title_font = title_label.font()
        title_font.setPointSize(17)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setWordWrap(True)
        title_label.setStyleSheet(f"color: {palette['text_primary']};")
        top_row.addWidget(title_label, 1)

        version_badge = aqt.qt.QLabel(
            f"{i18n.get_text('about_version', lang)} {version.ANKI_SUPER_FREE_TTS_VERSION}"
        )
        version_badge.setAlignment(aqt.qt.Qt.AlignmentFlag.AlignCenter)
        version_badge.setStyleSheet(
            f"""
            background-color: {palette['badge_bg']};
            color: {palette['badge_text']};
            border-radius: 10px;
            padding: 7px 12px;
            font-weight: bold;
            """
        )
        top_row.addWidget(version_badge, 0, aqt.qt.Qt.AlignmentFlag.AlignTop)
        card_layout.addLayout(top_row)

        desc_label = aqt.qt.QLabel(i18n.get_text("about_description", lang))
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet(
            f"color: {palette['text_secondary']}; font-size: 12px; line-height: 1.45;"
        )
        card_layout.addWidget(desc_label)

        return card

    def _build_info_section(self, lang, palette):
        section = aqt.qt.QWidget()
        section_layout = aqt.qt.QVBoxLayout(section)
        section_layout.setContentsMargins(0, 0, 0, 0)
        section_layout.setSpacing(10)

        title = aqt.qt.QLabel(i18n.get_text("about_info_title", lang))
        title_font = title.font()
        title_font.setPointSize(11)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet(f"color: {palette['text_primary']};")
        section_layout.addWidget(title)

        grid = aqt.qt.QGridLayout()
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(12)

        for index, item in enumerate(self.INFO_ITEMS):
            card = self._build_info_card(lang, palette, item)
            grid.addWidget(card, index // 2, index % 2)

        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)
        section_layout.addLayout(grid)
        return section

    def _build_info_card(self, lang, palette, item):
        card = self._create_card()
        card.setStyleSheet(
            f"""
            QFrame {{
                background-color: {palette['card_bg']};
                border: 1px solid {palette['card_border']};
                border-radius: 18px;
            }}
            QLabel {{
                background: transparent;
                border: none;
            }}
            """
        )

        card_layout = aqt.qt.QVBoxLayout(card)
        card_layout.setContentsMargins(18, 16, 18, 16)
        card_layout.setSpacing(8)

        kicker = aqt.qt.QLabel(i18n.get_text(item["label_key"], lang))
        kicker.setStyleSheet(
            f"color: {palette['text_muted']}; font-size: 10px; font-weight: bold; text-transform: uppercase;"
        )
        card_layout.addWidget(kicker)

        title = aqt.qt.QLabel(item["title"])
        title_font = title.font()
        title_font.setPointSize(11)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setWordWrap(True)
        title.setStyleSheet(f"color: {palette['text_primary']};")
        card_layout.addWidget(title)

        description = aqt.qt.QLabel(i18n.get_text(item["description_key"], lang))
        description.setWordWrap(True)
        description.setStyleSheet(f"color: {palette['text_secondary']}; font-size: 11px;")
        card_layout.addWidget(description)

        link = aqt.qt.QLabel(self._build_anchor(item["url"], item["url"], palette["link"]))
        link.setTextFormat(aqt.qt.Qt.TextFormat.RichText)
        link.setTextInteractionFlags(aqt.qt.Qt.TextInteractionFlag.TextBrowserInteraction)
        link.setOpenExternalLinks(True)
        link.setWordWrap(True)
        link.setStyleSheet(f"color: {palette['link']}; font-size: 11px;")
        card_layout.addWidget(link)

        card_layout.addStretch()
        return card

    def _build_action_section(self, lang, palette):
        card = self._create_card()
        card.setStyleSheet(
            f"""
            QFrame {{
                background-color: {palette['card_bg']};
                border: none;
                border-radius: 22px;
            }}
            """
        )

        card_layout = aqt.qt.QVBoxLayout(card)
        card_layout.setContentsMargins(22, 22, 22, 22)
        card_layout.setSpacing(14)

        title = aqt.qt.QLabel(i18n.get_text("about_links_title", lang))
        title_font = title.font()
        title_font.setPointSize(11)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet(f"color: {palette['text_primary']};")
        card_layout.addWidget(title)

        description = aqt.qt.QLabel(i18n.get_text("about_links_description", lang))
        description.setWordWrap(True)
        description.setStyleSheet(f"color: {palette['text_secondary']}; font-size: 11px;")
        card_layout.addWidget(description)

        button_layout = aqt.qt.QGridLayout()
        button_layout.setHorizontalSpacing(10)
        button_layout.setVerticalSpacing(10)

        for index, item in enumerate(self.INFO_ITEMS):
            button = aqt.qt.QPushButton(i18n.get_text(item["label_key"], lang))
            button.setCursor(aqt.qt.Qt.CursorShape.PointingHandCursor)
            button.setMinimumHeight(38)
            button.clicked.connect(lambda _checked=False, url=item["url"]: webbrowser.open(url))
            button.setStyleSheet(
                f"""
                QPushButton {{
                    background-color: {palette['button_bg']};
                    color: {palette['button_text']};
                    border: 1px solid {palette['button_border']};
                    border-radius: 12px;
                    padding: 8px 14px;
                    text-align: left;
                    font-weight: 600;
                }}
                QPushButton:hover {{
                    background-color: {palette['button_hover_bg']};
                    border-color: {palette['button_hover_border']};
                }}
                QPushButton:pressed {{
                    background-color: {palette['button_pressed_bg']};
                }}
                """
            )
            button_layout.addWidget(button, index // 2, index % 2)

        button_layout.setColumnStretch(0, 1)
        button_layout.setColumnStretch(1, 1)
        card_layout.addLayout(button_layout)
        return card

    def _create_card(self):
        card = aqt.qt.QFrame()
        card.setFrameShape(aqt.qt.QFrame.Shape.NoFrame)
        card.setAutoFillBackground(False)
        return card

    def _build_anchor(self, url, text, color):
        return f'<a href="{url}" style="color: {color}; text-decoration: none;">{text}</a>'

    def _get_palette(self, dark):
        if dark:
            return {
                "hero_bg": "#0F172A",
                "hero_border": "#1E293B",
                "card_bg": "#111827",
                "card_border": "#334155",
                "text_primary": "#F8FAFC",
                "text_secondary": "#CBD5E1",
                "text_muted": "#94A3B8",
                "badge_bg": "rgba(16, 185, 129, 0.18)",
                "badge_text": "#A7F3D0",
                "link": "#6EE7B7",
                "button_bg": "rgba(16, 185, 129, 0.12)",
                "button_text": "#ECFDF5",
                "button_border": "rgba(16, 185, 129, 0.28)",
                "button_hover_bg": "rgba(16, 185, 129, 0.22)",
                "button_hover_border": constants.COLOR_ACCENT,
                "button_pressed_bg": "rgba(5, 150, 105, 0.28)",
            }

        return {
            "hero_bg": "#F8FAFC",
            "hero_border": "#DCE7F2",
            "card_bg": "#FFFFFF",
            "card_border": "#E2E8F0",
            "text_primary": "#0F172A",
            "text_secondary": "#475569",
            "text_muted": "#64748B",
            "badge_bg": constants.COLOR_ACCENT_LIGHT,
            "badge_text": constants.COLOR_ACCENT_DARK,
            "link": constants.COLOR_ACCENT_HOVER,
            "button_bg": "#F0FDF4",
            "button_text": "#065F46",
            "button_border": "#A7F3D0",
            "button_hover_bg": "#DCFCE7",
            "button_hover_border": constants.COLOR_ACCENT,
            "button_pressed_bg": "#BBF7D0",
        }


AboutComponent = AboutPage
