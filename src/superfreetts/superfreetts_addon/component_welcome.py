import html
import random
import time

import aqt.qt
from aqt.qt import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QCheckBox,
    QComboBox,
    QTimer,
    QPainter,
    QColor,
    QPen,
    Qt,
    QBrush,
    QRadialGradient,
)

try:
    from aqt.theme import theme_manager
except ImportError:
    theme_manager = None

from . import constants
from . import i18n
from . import logging_utils
from . import version

logger = logging_utils.get_child_logger(__name__)


class SnowFlake:
    def __init__(self, width, height, is_dark=True):
        self.width = width
        self.height = height
        self.is_dark = is_dark
        if not self.is_dark:
            colors = [QColor("#3b82f6"), QColor("#ef4444"), QColor("#10b981"), QColor("#f59e0b"), QColor("#8b5cf6"), QColor("#ec4899")]
            self.color = random.choice(colors)
            self.color.setAlpha(180)
        else:
            self.color = QColor(255, 255, 255, 200)

        self.reset()
        # Randomize initial Y position to fill the screen
        self.y = random.uniform(0, height)

    def reset(self):
        self.x = random.uniform(0, self.width)
        self.y = random.uniform(-20, 0)
        self.size = random.uniform(2, 6)
        self.speed = random.uniform(0.5, 2.0)
        self.amplitude = random.uniform(0.5, 1.5)
        self.angle = random.uniform(0, 2 * 3.14159)
        self.rotation = random.uniform(0, 360)
        self.rot_speed = random.uniform(-5, 5)

    def update(self):
        self.y += self.speed
        self.angle += 0.02
        self.rotation += self.rot_speed
        self.x += self.amplitude * (random.uniform(-1, 1) + 0.5)  # Slight drift
        if self.y > self.height:
            self.reset()


class WelcomeDialog(QDialog):
    def __init__(self, hypertts, parent=None):
        super().__init__(parent)
        self.hypertts = hypertts
        self.lang = self.hypertts.get_ui_language()
        accent = constants.COLOR_ACCENT

        self.setWindowTitle("")
        self.setMinimumSize(360, 420)
        self.resize(560, 620)
        self.setWindowFlags(
            self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint
        )

        # Check theme
        if theme_manager:
            self.is_dark = theme_manager.night_mode
        else:
            self.is_dark = True
            
        # Colors dependent on theme
        if self.is_dark:
            self.bg_color = QColor("#1e293b")  # Slate 800
            self.color_header = "white"
            self.color_desc = "#e2e8f0"
            self.color_promo = "#fef3c7"
            self.color_footer = "#94a3b8"
            self.color_checkbox = "#cbd5e1"
        else:
            self.bg_color = QColor("#f8fafc")  # Slate 50
            self.color_header = "#0f172a"
            self.color_desc = "#334155"
            self.color_promo = "#b45309"
            self.color_footer = "#64748b"
            self.color_checkbox = "#475569"

        # Particles
        self.particles = [SnowFlake(560, 620, self.is_dark) for _ in range(50)]

        # Timer for animation
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(33)  # ~30 FPS

        # Main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        # Content container (transparent background to show snow)
        self.content_widget = aqt.qt.QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(30, 40, 30, 30)
        self.main_layout.addWidget(self.content_widget)

        # Language selector row (stays fixed; only text below re-renders)
        lang_row = QHBoxLayout()
        self.lang_caption = QLabel("")
        self.lang_caption.setStyleSheet(
            f"color: {self.color_footer}; font-size: 13px; font-weight: bold;"
        )
        lang_row.addWidget(self.lang_caption)
        self.language_combobox = QComboBox()
        self.language_combobox.setMinimumHeight(30)
        lang_row.addWidget(self.language_combobox)
        lang_row.addStretch()
        self.content_layout.addLayout(lang_row)

        # Header
        self.header_label = QLabel()
        self.header_label.setStyleSheet(
            f"font-size: 24px; font-weight: bold; color: {self.color_header}; margin-bottom: 20px;"
        )
        self.header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.content_layout.addWidget(self.header_label)

        # Description
        self.desc_label = QLabel()
        self.desc_label.setWordWrap(True)
        self.content_layout.addWidget(self.desc_label)

        # Promo section (Semi-transparent card)
        self.promo_card = QLabel()
        self.promo_card.setWordWrap(True)
        self.content_layout.addWidget(self.promo_card)

        self.content_layout.addStretch()

        # Footer info
        self.footer_label = QLabel()
        self.footer_label.setOpenExternalLinks(True)
        self.content_layout.addWidget(self.footer_label)

        # Checkbox & Button section
        bottom_layout = QHBoxLayout()
        self.cb_dont_show = QCheckBox("")
        self.cb_dont_show.setStyleSheet(f"color: {self.color_checkbox}; font-size: 11px;")
        bottom_layout.addWidget(self.cb_dont_show)

        bottom_layout.addStretch()

        self.btn_start = QPushButton("")
        self.btn_start.setMinimumWidth(160)
        self.btn_start.setFixedHeight(40)
        self.btn_start.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_start.setStyleSheet(f"""
            QPushButton {{
                background-color: {accent};
                color: white;
                border-radius: 0px;
                font-weight: bold;
                font-size: 14px;
                border: 1px solid transparent;
                outline: none;
            }}
            QPushButton:hover {{
                background-color: {constants.COLOR_ACCENT_HOVER};
                border-radius: 0px;
                border: 1px solid transparent;
            }}
        """)
        self.btn_start.clicked.connect(self.accept)
        bottom_layout.addWidget(self.btn_start)
        
        self.content_layout.addLayout(bottom_layout)

        # Populate + update language-dependent texts
        self._populate_languages()
        self.language_combobox.currentIndexChanged.connect(self._on_language_changed)
        self._apply_language()

    # ------------------------------------------------------------------
    # Language handling
    # ------------------------------------------------------------------

    @staticmethod
    def _lang_display(language: str, display_lang: str) -> str:
        return i18n.get_text(f"preferences_option_language_{language.replace('-', '_')}", display_lang)

    def _populate_languages(self) -> None:
        self.language_combobox.blockSignals(True)
        self.language_combobox.clear()
        for language in i18n.SUPPORTED_LANGUAGES:
            self.language_combobox.addItem(self._lang_display(language, self.lang), language)
        index = i18n.SUPPORTED_LANGUAGES.index(self.lang) if self.lang in i18n.SUPPORTED_LANGUAGES else 0
        if self.language_combobox.count() > index:
            self.language_combobox.setCurrentIndex(index)
        self.language_combobox.blockSignals(False)

    def _on_language_changed(self, index: int) -> None:
        data = self.language_combobox.itemData(index) or "en"
        if data == self.lang:
            return
        self.lang = data
        # Re-display language names in the newly selected language.
        self.language_combobox.blockSignals(True)
        for i, language in enumerate(i18n.SUPPORTED_LANGUAGES):
            if i < self.language_combobox.count():
                self.language_combobox.setItemText(i, self._lang_display(language, self.lang))
        self.language_combobox.blockSignals(False)
        self._apply_language()

    def _build_welcome_html(self, lang: str) -> str:
        return f"""
        <div style="color: {self.color_desc}; font-size: 14px; line-height: 1.6;">
            <p>{i18n.get_text("welcome_thanks", lang)}</p>
            <p>{html.escape(i18n.get_text("about_description", lang))}</p>
            <ul style="margin-top: 10px; margin-bottom: 10px; padding-left: 20px;">
                <li>{html.escape(i18n.get_text("welcome_list_engines", lang))}</li>
                <li>{html.escape(i18n.get_text("welcome_list_offline", lang))}</li>
                <li>{html.escape(i18n.get_text("welcome_list_batch", lang))}</li>
            </ul>
            <p>{i18n.get_text("welcome_instruction", lang)}</p>
        </div>
        """

    def _build_promo_html(self, lang: str) -> str:
        return (
            f'<div style="padding: 10px; color: {self.color_promo}; line-height: 1.5; font-size: 13px;">'
            f'{html.escape(i18n.get_text("welcome_addons_promo", lang))}'
            f'</div>'
        )

    def _build_footer_html(self, lang: str) -> str:
        accent = constants.COLOR_ACCENT
        author_url = "https://facebook.com/dangngooooo"
        contributor_url = "https://www.facebook.com/tui.la.phuc747"
        site_url = "https://ankivn.com"
        return f"""
        <div style="color: {self.color_footer}; font-size: 12px; line-height: 1.6;">
            <b>{html.escape(i18n.get_text("about_version", lang))}</b> {html.escape(version.ANKI_SUPER_FREE_TTS_VERSION)}<br/>
            <b>{html.escape(i18n.get_text("about_author", lang))}</b> <a href="{author_url}" style="color: {accent}; text-decoration: none;">Paul from AnkiVN</a> |
            <b>Contributor:</b> <a href="{contributor_url}" style="color: {accent}; text-decoration: none;">Hoàng Phúc</a><br/>
            <b>{html.escape(i18n.get_text("about_website", lang))}</b> <a href="{site_url}" style="color: {accent}; text-decoration: none;">AnkiVN.com</a>
        </div>
        """

    def _apply_language(self) -> None:
        lang = self.lang
        self.setWindowTitle(i18n.get_text("welcome_dialog_title", lang))
        self.lang_caption.setText(i18n.get_text("preferences_label_interface_language", lang))
        self.header_label.setText(i18n.get_text("welcome_header", lang))
        self.desc_label.setText(self._build_welcome_html(lang))
        self.promo_card.setText(self._build_promo_html(lang))
        self.footer_label.setText(self._build_footer_html(lang))
        self.cb_dont_show.setText(i18n.get_text("welcome_dont_show_again", lang))
        self.btn_start.setText(i18n.get_text("welcome_button_start", lang))

    def update_animation(self):
        for p in self.particles:
            p.update()
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw background
        painter.fillRect(self.rect(), self.bg_color)

        # Draw snow or confetti
        painter.setPen(Qt.PenStyle.NoPen)
        for p in self.particles:
            if self.is_dark:
                # Snow style for dark mode
                gradient = QRadialGradient(p.x, p.y, p.size)
                gradient.setColorAt(0, p.color) # Core
                gradient.setColorAt(1, QColor(255, 255, 255, 0))   # Edge
                painter.setBrush(QBrush(gradient))
                painter.drawEllipse(aqt.qt.QPointF(p.x, p.y), p.size, p.size)
            else:
                # Confetti style for light mode
                painter.setBrush(QBrush(p.color))
                painter.save()
                painter.translate(p.x, p.y)
                painter.rotate(p.rotation)
                # Small rectangles for confetti
                painter.drawRect(aqt.qt.QRectF(-p.size, -p.size/2, p.size*2, p.size))
                painter.restore()

    def accept(self):
        if self.cb_dont_show.isChecked():
            try:
                config = self.hypertts.get_configuration()
                config.display_introduction_message = False
                self.hypertts.save_configuration(config)
                logger.info("Welcome popup disabled by user.")
            except Exception as e:
                logger.error(f"Failed to save welcome popup state: {e}")

        # Persist the language chosen in the first-run language picker.
        if getattr(self, "lang", None):
            try:
                prefs = self.hypertts.get_preferences()
                if getattr(prefs, "ui_language", "en") != self.lang:
                    prefs.ui_language = self.lang
                    self.hypertts.save_preferences(prefs)
                    logger.info(f"[LANG] Welcome dialog chose UI language '{self.lang}'")
            except Exception as e:
                logger.error(f"Failed to save welcome language: {e}")

        super().accept()
