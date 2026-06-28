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
        lang = self.hypertts.get_ui_language()
        accent = constants.COLOR_ACCENT

        self.setWindowTitle(i18n.get_text("welcome_dialog_title", lang))
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

        # Header
        header_label = QLabel(i18n.get_text("welcome_header", lang))
        header_label.setStyleSheet(
            f"font-size: 24px; font-weight: bold; color: {self.color_header}; margin-bottom: 20px;"
        )
        header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.content_layout.addWidget(header_label)

        # Description
        author_url = "https://facebook.com/dangngooooo"
        contributor_url = "https://www.facebook.com/tui.la.phuc747"
        site_url = "https://ankivn.com"

        welcome_text = f"""
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
        
        desc_label = QLabel(welcome_text)
        desc_label.setWordWrap(True)
        self.content_layout.addWidget(desc_label)

        # Promo section (Semi-transparent card)
        promo_text = i18n.get_text("welcome_addons_promo", lang)
        promo_card = QLabel(
            f'<div style="padding: 10px; color: {self.color_promo}; line-height: 1.5; font-size: 13px;">'
            f'{html.escape(promo_text)}'
            f'</div>'
        )
        promo_card.setWordWrap(True)
        self.content_layout.addWidget(promo_card)

        self.content_layout.addStretch()

        # Footer info
        footer_html = f"""
        <div style="color: {self.color_footer}; font-size: 12px; line-height: 1.6;">
            <b>{html.escape(i18n.get_text("about_version", lang))}</b> {html.escape(version.ANKI_SUPER_FREE_TTS_VERSION)}<br/>
            <b>{html.escape(i18n.get_text("about_author", lang))}</b> <a href="{author_url}" style="color: {accent}; text-decoration: none;">Paul from AnkiVN</a> | 
            <b>Contributor:</b> <a href="{contributor_url}" style="color: {accent}; text-decoration: none;">Hoàng Phúc</a><br/>
            <b>{html.escape(i18n.get_text("about_website", lang))}</b> <a href="{site_url}" style="color: {accent}; text-decoration: none;">AnkiVN.com</a>
        </div>
        """
        footer_label = QLabel(footer_html)
        footer_label.setOpenExternalLinks(True)
        self.content_layout.addWidget(footer_label)

        # Checkbox & Button section
        bottom_layout = QHBoxLayout()
        self.cb_dont_show = QCheckBox(i18n.get_text("welcome_dont_show_again", lang))
        self.cb_dont_show.setStyleSheet(f"color: {self.color_checkbox}; font-size: 11px;")
        bottom_layout.addWidget(self.cb_dont_show)

        bottom_layout.addStretch()

        self.btn_start = QPushButton("Bắt đầu / Get Started")
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
        super().accept()
