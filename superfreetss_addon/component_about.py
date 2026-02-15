import aqt.qt
import webbrowser
from . import component_common
from . import constants
from . import gui_utils
from . import version
from . import i18n
from . import logging_utils

logger = logging_utils.get_child_logger(__name__)

class AboutComponent(component_common.ConfigComponentBase):
    def __init__(self, hypertts):
        self.hypertts = hypertts

    def get_model(self):
        return None

    def load_model(self, model):
        pass

    def draw(self, layout):
        lang = self.hypertts.get_ui_language()
        
        # Main container with some padding
        container = aqt.qt.QWidget()
        vlayout = aqt.qt.QVBoxLayout(container)
        vlayout.setContentsMargins(0, 0, 0, 0)
        vlayout.setSpacing(20)

        # 1. Information Card
        info_card = aqt.qt.QFrame()
        info_card.setStyleSheet("""
            QFrame {
                background-color: palette(window);
                border: 1px solid palette(mid);
                border-radius: 12px;
            }
            QLabel { border: none; }
        """)
        info_layout = aqt.qt.QVBoxLayout(info_card)
        info_layout.setContentsMargins(24, 24, 24, 24)
        info_layout.setSpacing(16)

        # Title
        title_label = aqt.qt.QLabel(i18n.get_text("about_header_title", lang))
        title_font = title_label.font()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        info_layout.addWidget(title_label)

        # Description
        desc_label = aqt.qt.QLabel(i18n.get_text("about_description", lang))
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: palette(text); line-height: 1.5;")
        info_layout.addWidget(desc_label)

        # Grid for details
        details_grid = aqt.qt.QGridLayout()
        details_grid.setSpacing(12)
        
        def add_row(row, label, value, is_link=False, link_text=None):
            lbl = aqt.qt.QLabel(label)
            lbl.setStyleSheet("color: palette(text); font-weight: bold;")
            
            if is_link:
                display_text = link_text if link_text else value
                val = aqt.qt.QLabel(f'<a href="{value}" style="color: {constants.COLOR_ACCENT}; text-decoration: none;">{display_text}</a>')
                val.setOpenExternalLinks(True)
            else:
                val = aqt.qt.QLabel(value)
                val.setStyleSheet("color: palette(text);")
            
            details_grid.addWidget(lbl, row, 0)
            details_grid.addWidget(val, row, 1)

        add_row(0, i18n.get_text("about_version", lang), version.ANKI_SUPER_FREE_TTS_VERSION)
        # Author name is now a green link to Facebook
        add_row(1, i18n.get_text("about_author", lang), "https://facebook.com/dangngooooo", is_link=True, link_text="Daniel from AnkiVN")
        # Added Honorable Contributor
        add_row(2, i18n.get_text("about_contributor", lang), "https://www.facebook.com/tui.la.phuc747", is_link=True, link_text="Lê Hoàng Phúc")
        add_row(3, i18n.get_text("about_website", lang), "https://ankivn.com", is_link=True, link_text="AnkiVN")

        info_layout.addLayout(details_grid)
        vlayout.addWidget(info_card)

        # 3. Footer / Support
        footer_label = aqt.qt.QLabel("SuperFreeTTS is documentation-driven and build for the community.")
        footer_label.setAlignment(aqt.qt.Qt.AlignmentFlag.AlignCenter)
        footer_label.setStyleSheet("color: palette(disabled); font-size: 10px; font-style: italic;")
        vlayout.addWidget(footer_label)

        vlayout.addStretch()
        layout.addWidget(container)
