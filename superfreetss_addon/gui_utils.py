import sys
import os
import aqt
import aqt.qt

from . import version
from . import constants
from . import errors


class NonAliasedImage(aqt.qt.QWidget):
    def __init__(self, pixmap):
        aqt.qt.QWidget.__init__(self)
        self._pixmap = pixmap
        # self.setMinimumSize(self._pixmap.width(), self._pixmap.height())
        self.setFixedWidth(self._pixmap.width())
        self.setFixedHeight(self._pixmap.height())

    def paintEvent(self,event):
        painter = aqt.qt.QPainter(self)
        painter.setRenderHint(aqt.qt.QPainter.RenderHint.SmoothPixmapTransform)
        painter.setRenderHint(aqt.qt.QPainter.RenderHint.Antialiasing)
        painter.drawPixmap(self.rect(), self._pixmap)

def get_graphic(graphic_name):
    return NonAliasedImage(aqt.qt.QPixmap(get_graphics_path(graphic_name)))

def get_header_label(text):
    header = aqt.qt.QLabel()
    header.setText(text)
    font = aqt.qt.QFont()
    font.setBold(True)
    font.setWeight(75)  
    font.setPointSize(20)
    header.setFont(font)
    return header

def get_medium_label(text):
    label = aqt.qt.QLabel()
    label.setText(text)
    font = aqt.qt.QFont()
    label_font_size = 12
    font.setBold(True)
    font.setPointSize(label_font_size)
    label.setFont(font)
    return label

def get_service_header_label(text):
    header = aqt.qt.QLabel()
    header.setText(text)
    font = aqt.qt.QFont()
    font.setBold(True)
    font.setWeight(70)
    font.setPointSize(12)
    header.setFont(font)
    return header

def get_small_cta_label(text):
    label = aqt.qt.QLabel()
    label.setText(text)
    font = aqt.qt.QFont()
    label_font_size = 8
    font.setItalic(True)
    font.setPointSize(label_font_size)
    label.setFont(font)
    return label

def get_large_button_font():
    font2 = aqt.qt.QFont()
    font2.setPointSize(14)
    return font2        

def get_large_checkbox_font():
    font2 = aqt.qt.QFont()
    font2.setPointSize(12)
    return font2

def get_large_combobox_font():
    font2 = aqt.qt.QFont()
    font2.setPointSize(10)
    return font2

def get_version_font():
    font2 = aqt.qt.QFont()
    font2.setPointSize(10)
    font2.setItalic(True)
    return font2        

def process_label_text(text):
    return text.replace('\n', '<br/>')


def get_graphics_path(filename):
    current_dir = os.path.dirname(__file__)
    root_dir = os.path.join(current_dir, os.pardir)
    
    is_dark = aqt.theme.is_dark() if hasattr(aqt, 'theme') and hasattr(aqt.theme, 'is_dark') else False
    
    full_path = os.path.join(root_dir, 'graphics', filename)
    
    if is_dark:
        # Check if a dark version exists (e.g., logo_dark.svg)
        base, ext = os.path.splitext(filename)
        dark_filename = f"{base}_dark{ext}"
        dark_path = os.path.join(root_dir, 'graphics', dark_filename)
        if os.path.exists(dark_path):
            full_path = dark_path
    
    # Check if the file exists
    if not os.path.exists(full_path):
        raise errors.MissingGraphicsFile(filename)
    
    return full_path

def configure_primary_button(button, min_height=32, min_width=100, font_size=9):
    """Configure a button with modern Slate 900 styling - Compact version"""
    elegant_style = f"""
        QPushButton {{
            background-color: {constants.COLOR_PRIMARY};
            border: 1px solid {constants.COLOR_PRIMARY_LIGHT};
            border-radius: 6px;
            color: white;
            padding: 4px 16px;
        }}
        QPushButton:hover {{
            background-color: {constants.COLOR_PRIMARY_HOVER};
            border-color: {constants.COLOR_PRIMARY_HOVER};
        }}
        QPushButton:pressed {{
            background-color: {constants.COLOR_PRIMARY_PRESSED};
        }}
        QPushButton:disabled {{
            background-color: {constants.COLOR_PRIMARY_DISABLED};
            border: none;
            color: #F1F5F9;
        }}
    """
    button.setStyleSheet(elegant_style)
    button.setMinimumHeight(min_height)
    button.setMinimumWidth(min_width)
    font_large = aqt.qt.QFont()
    font_large.setBold(True)
    font_large.setPointSize(font_size)
    button.setFont(font_large)

# Backward compat alias
configure_purple_button = configure_primary_button

def configure_secondary_button(button, min_height=30, min_width=80, font_size=9):
    """Configure a secondary outlined button for less prominent actions - Compact version"""
    secondary_style = """
        QPushButton {
            background-color: transparent;
            border: 1px solid #E2E8F0;
            border-radius: 6px;
            color: palette(text);
            padding: 4px 12px;
        }
        QPushButton:hover {
            background-color: palette(alternate-base);
            border-color: #64748B;
        }
        QPushButton:pressed {
            background-color: palette(midlight);
        }
    """
    button.setStyleSheet(secondary_style)
    button.setMinimumHeight(min_height)
    button.setMinimumWidth(min_width)
    font_btn = aqt.qt.QFont()
    font_btn.setPointSize(font_size)
    button.setFont(font_btn)

def get_vocab_ai_url(url_path, utm_campaign, distinct_id=None):
    """Generate a vocab.ai URL with UTM parameters
    
    Args:
        url_path: Path after the domain (e.g., 'tips/hypertts-adding-audio')
        utm_campaign: Campaign name for UTM tracking
        distinct_id: Optional distinct ID for tracking
    
    Returns:
        Complete URL with UTM parameters
    """
    base_url = f"https://www.vocab.ai/{url_path}"
    utm_params = "utm_source=superfreetss&utm_medium=addon"
    utm_params += f"&utm_campaign={utm_campaign}"
    
    if distinct_id is not None:
        utm_params += f"&distinct_id={distinct_id}"
    
    return f"{base_url}?{utm_params}"

def get_status_badge(text, bg_color=None, text_color=None):
    """Return a compact rounded QLabel suitable for 'Free', 'Recommended', etc."""
    label = aqt.qt.QLabel(text)
    # Slate/Emerald modern badges
    bg = bg_color or "#D1FAE5"  # Emerald 100
    fg = text_color or "#065F46" # Emerald 800
    label.setStyleSheet(f"""
        QLabel {{
            background-color: {bg};
            color: {fg};
            border-radius: 10px;
            padding: 2px 12px;
            font-size: 11px;
            font-weight: bold;
            border: 1px solid #A7F3D0;
        }}
    """)
    label.setFixedHeight(22)
    return label

def get_superfreetss_label_header(superfreetss_pro_enabled, variant='adaptive'):
    hlayout = aqt.qt.QHBoxLayout()

    # Determine text color based on variant
    if variant == 'white':
        text_color = 'white'
    # Use the new SVG logo instead of text
    logo_widget = get_graphic(constants.GRAPHICS_LITE_BANNER)

    version_label = aqt.qt.QLabel('v' + version.ANKI_SUPER_FREE_TTS_VERSION)
    version_label.setFont(get_version_font())
    
    # Adaptive text color for version label
    is_dark = aqt.theme.is_dark() if hasattr(aqt, 'theme') and hasattr(aqt.theme, 'is_dark') else False
    text_color = "#F8FAFC" if is_dark else "#0F172A"
    version_label.setStyleSheet(f'color: {text_color}; background: transparent; border: none;')

    hlayout.addStretch()
    hlayout.addWidget(logo_widget)
    hlayout.addWidget(version_label)
    return hlayout
