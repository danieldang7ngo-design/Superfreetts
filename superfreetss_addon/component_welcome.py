"""
Hộp thoại chào mừng khi cài addon lần đầu (display_introduction_message).
Nội dung bổ sung từ màn About + quảng bá AnkiVN / cộng đồng làm addon.
"""
import html

import aqt.qt

from . import constants
from . import i18n
from . import logging_utils
from . import version

logger = logging_utils.get_child_logger(__name__)


class WelcomeDialog(aqt.qt.QDialog):
    def __init__(self, hypertts, parent=None):
        super().__init__(parent)
        self.hypertts = hypertts
        lang = self.hypertts.get_ui_language()
        accent = constants.COLOR_ACCENT

        self.setWindowTitle("Welcome to Super Free TTS")
        # Nội dung dài hơn (About + link) nên tăng kích thước cửa sổ
        self.setFixedSize(540, 560)
        self.setWindowFlags(
            self.windowFlags() & ~aqt.qt.Qt.WindowType.WindowContextHelpButtonHint
        )

        layout = aqt.qt.QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)

        # Dùng cùng thông tin About + link như component_about (Facebook / AnkiVN)
        author_url = "https://facebook.com/dangngooooo"
        contributor_url = "https://www.facebook.com/tui.la.phuc747"
        site_url = "https://ankivn.com"

        welcome_html = f"""
        <h2 style="color: #2c3e50; text-align: center;">Welcome to Super Free TTS! 🎉</h2>
        <p style="font-size: 14px; margin-top: 10px;">
            Cảm ơn bạn đã cài đặt <b>Super Free TTS</b> — trợ lý TTS miễn phí cho Anki.
        </p>
        <p style="font-size: 13px; color: #1E3A5F; line-height: 1.45;">
            {html.escape(i18n.get_text("about_description", lang))}
        </p>
        <ul style="font-size: 13px; margin-top: 8px;">
            <li>Hỗ trợ đa dạng các engine như EdgeTTS, Kokoro, Piper, MMS...</li>
            <li>Hoạt động Offline (với các local engine) bảo vệ quyền riêng tư.</li>
            <li>Tạo audio hàng loạt (Batch) hoặc tạo ngay khi thêm thẻ (Realtime).</li>
        </ul>
        <p style="font-size: 13px; margin-top: 10px;">
            Để bắt đầu, hãy bôi đen văn bản trong trình chỉnh sửa thẻ hoặc cấu hình trong menu
            <i>Tools -&gt; Super Free TTS</i>.
        </p>
        <p style="font-size: 12px; margin-top: 12px; padding: 10px; background-color: #FFF4C8;
           border-radius: 10px; color: #1E3A5F; line-height: 1.5;">
            {html.escape(i18n.get_text("welcome_addons_promo", lang))}
        </p>
        <p style="font-size: 12px; margin-top: 8px;">
            <b>{html.escape(i18n.get_text("about_version", lang))}</b>
            {html.escape(version.ANKI_SUPER_FREE_TTS_VERSION)}<br/>
            <b>{html.escape(i18n.get_text("about_author", lang))}</b>
            <a href="{author_url}" style="color: {accent}; text-decoration: none;">Daniel from AnkiVN</a><br/>
            <b>{html.escape(i18n.get_text("about_contributor", lang))}</b>
            <a href="{contributor_url}" style="color: {accent}; text-decoration: none;">Lê Hoàng Phúc</a><br/>
            <b>{html.escape(i18n.get_text("about_website", lang))}</b>
            <a href="{site_url}" style="color: {accent}; text-decoration: none;">AnkiVN</a>
        </p>
        <p style="font-size: 10px; font-style: italic; color: #2C5B87; text-align: center; margin-top: 6px;">
            {html.escape(i18n.get_text("about_footer", lang))}
        </p>
        """

        label_msg = aqt.qt.QLabel(welcome_html)
        label_msg.setWordWrap(True)
        label_msg.setOpenExternalLinks(True)
        layout.addWidget(label_msg)

        layout.addStretch()

        cb_layout = aqt.qt.QHBoxLayout()
        self.cb_dont_show = aqt.qt.QCheckBox(
            "Don't show this again (Không hiển thị lại)"
        )
        self.cb_dont_show.setChecked(False)
        cb_layout.addWidget(self.cb_dont_show)
        layout.addLayout(cb_layout)

        btn_layout = aqt.qt.QHBoxLayout()
        btn_layout.addStretch()
        self.btn_start = aqt.qt.QPushButton("Get Started / Bắt đầu")
        self.btn_start.setMinimumWidth(150)
        self.btn_start.setFixedHeight(35)
        self.btn_start.setStyleSheet(
            "font-weight: bold; background-color: #3498db; color: white; border-radius: 5px;"
        )
        self.btn_start.clicked.connect(self.accept)
        btn_layout.addWidget(self.btn_start)
        btn_layout.addStretch()

        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def accept(self):
        if self.cb_dont_show.isChecked():
            try:
                config = self.hypertts.get_configuration()
                config.display_introduction_message = False
                self.hypertts.save_configuration(config)
                logger.info(
                    "User selected 'Don't show again'. Welcome popup disabled."
                )
            except Exception as e:
                logger.error(f"Failed to save welcome popup state: {e}")

        super().accept()
