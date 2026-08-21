import sys
import os
import aqt
import aqt.qt

from . import version
from . import constants
from . import errors


_global_wheel_filter = None


class _NoWheelValueChangeFilter(aqt.qt.QObject):
    def eventFilter(self, obj, event):
        try:
            wheel_event_type = getattr(getattr(aqt.qt.QEvent, "Type", aqt.qt.QEvent), "Wheel")
            if event.type() != wheel_event_type:
                return False

            if isinstance(obj, aqt.qt.QComboBox):
                view = obj.view()
                if view is not None and view.isVisible():
                    return False
                event.ignore()
                return True

            abstract_spinbox = getattr(aqt.qt, "QAbstractSpinBox", None)
            if abstract_spinbox is not None and isinstance(obj, abstract_spinbox):
                event.ignore()
                return True
        except Exception:
            return False
        return False


def install_global_wheel_filter():
    """Prevent mouse-wheel scrolling from accidentally changing combo/spin values."""
    global _global_wheel_filter
    app = aqt.qt.QApplication.instance()
    if app is None or _global_wheel_filter is not None:
        return
    _global_wheel_filter = _NoWheelValueChangeFilter(app)
    app.installEventFilter(_global_wheel_filter)


def make_scroll_area(widget):
    scroll_area = aqt.qt.QScrollArea()
    scroll_area.setWidgetResizable(True)
    scroll_area.setFrameShape(aqt.qt.QFrame.Shape.NoFrame)
    scroll_area.setHorizontalScrollBarPolicy(aqt.qt.Qt.ScrollBarPolicy.ScrollBarAsNeeded)
    scroll_area.setVerticalScrollBarPolicy(aqt.qt.Qt.ScrollBarPolicy.ScrollBarAsNeeded)
    scroll_area.setWidget(widget)
    return scroll_area


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

def get_service_header_label(text):
    header = aqt.qt.QLabel(text)
    font = aqt.qt.QFont()
    font.setWeight(aqt.qt.QFont.Weight.DemiBold)
    font.setPointSize(11)
    header.setFont(font)
    return header


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
    button.setProperty("cssClass", "primaryButton")
    button.setMinimumHeight(min_height)
    button.setMinimumWidth(min_width)
    font_large = aqt.qt.QFont()
    font_large.setBold(True)
    font_large.setPointSize(font_size)
    button.setFont(font_large)

# Backward compat alias
configure_purple_button = configure_primary_button

def configure_secondary_button(button, min_height=30, min_width=80, font_size=9):
    button.setProperty("cssClass", "secondaryButton")
    button.setMinimumHeight(min_height)
    button.setMinimumWidth(min_width)
    font_btn = aqt.qt.QFont()
    font_btn.setPointSize(font_size)
    button.setFont(font_btn)

def configure_pastel_button(button, style_name="emerald", min_height=34, min_width=80, font_size=10, is_primary=False):
    """
    Apply a pastel vibrant block style to a button.
    Available styles: 'emerald', 'blue', 'rose', 'amber', 'purple'.
    """
    css_class = f"btnPastel{style_name.capitalize()}"
    button.setProperty("cssClass", css_class)
    button.setMinimumHeight(min_height)
    button.setMinimumWidth(min_width)
    font_btn = aqt.qt.QFont()
    if is_primary:
        font_btn.setBold(True)
    font_btn.setPointSize(font_size)
    button.setFont(font_btn)
    button.style().unpolish(button)
    button.style().polish(button)


def get_status_badge(text, bg_color=None, text_color=None):
    """Return a compact rounded QLabel suitable for 'Free', 'Recommended', etc."""
    label = aqt.qt.QLabel(text)
    # Use Emerald theme for success/positive badges by default
    bg = bg_color or constants.COLOR_ACCENT_LIGHT
    fg = text_color or constants.COLOR_ACCENT_DARK
    label.setStyleSheet(f"""
        QLabel {{
            background-color: {bg};
            color: {fg};
            border-radius: 10px;
            padding: 2px 10px;
            font-size: 10px;
            font-weight: 600;
        }}
    """)
    label.setFixedHeight(20)
    label.setContentsMargins(0, 0, 0, 0)
    label.setAlignment(aqt.qt.Qt.AlignmentFlag.AlignCenter)
    return label

def get_superfreetts_label_header(superfreetts_pro_enabled, variant='adaptive'):
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

    hlayout.addWidget(logo_widget)
    hlayout.addWidget(version_label)
    hlayout.addStretch()
    return hlayout


def is_night_mode() -> bool:
    """Helper to check if Anki is currently in night mode."""
    if hasattr(aqt, 'theme') and hasattr(aqt.theme, 'theme_manager'):
        return getattr(aqt.theme.theme_manager, 'night_mode', False)
    elif hasattr(aqt, 'theme') and hasattr(aqt.theme, 'is_dark'):
        return aqt.theme.is_dark()
    return False

# Current active UI theme. Set at addon startup and whenever preferences are saved.
_active_theme = "vibrant"

VALID_THEMES = ("vibrant", "ollama", "apple")


def set_active_theme(theme: str) -> None:
    """Set the active UI theme. Invalid values fall back to vibrant."""
    global _active_theme
    _active_theme = theme if theme in VALID_THEMES else "vibrant"


def get_active_theme() -> str:
    return _active_theme


def get_dynamic_stylesheet() -> str:
    """Returns the unified stylesheet for the active theme."""
    dark = is_night_mode()
    if _active_theme == "ollama":
        return _build_ollama_stylesheet(dark)
    if _active_theme == "apple":
        return _build_apple_stylesheet(dark)
    return _build_vibrant_stylesheet(dark)


def _build_vibrant_stylesheet(dark: bool) -> str:
    """Returns a unified stylesheet adhering to Vibrant Blocks (No Borders, Full Gradient)."""

    # Base configuration: Light Mode Tokens (Pastel Vibrant)
    bg_window = "#EEF2FF"           # Indigo 50 (Soft solid, no gradient)
    bg_card = "#FFFFFF"             # Crisp White block
    sidebar_bg = "#FFFFFF"          # Bright sidebar differentiating from window
    
    text_primary = "#0F172A"        # Slate 900
    text_secondary = "#475569"      # Slate 600
    
    tab_bg_unselected = "rgba(255, 255, 255, 120)"
    tab_bg_selected = "#6366F1"     # Indigo 500 (Soft Neon)
    tab_text_unselected = "#334155" # Slate 700
    tab_text_selected = "#FFFFFF"   # White
    
    toc_hover_bg = "#E2E8F0"        # Slate 200
    tab_pane_bg = "#F1F5F9"         # Slate 100 for distinct background
    
    input_bg = "#F8FAFC"            # Slate 50
    input_focus = "#FFFFFF"         # Crisp white for focus bg
    
    btn_bg_secondary = "rgba(255, 255, 255, 180)"
    btn_text_sec = "#0F172A"
    btn_hover_sec = "rgba(255, 255, 255, 255)"
    
    btn_bg_primary = "#4F46E5"      # Indigo 600 (Solid Vibrant)
    btn_text_pri = "#FFFFFF"
    btn_hover_pri = "#4338CA"       # Indigo 700 (Solid Vibrant)
    
    # Service Cards Vibrant Blocks
    svc_enabled_bg = "#D1FAE5"      # Emerald 100 (Bright Pastel Green)
    svc_enabled_text = "#064E3B"    # Emerald 900
    
    svc_disabled_bg = "#FFE4E6"     # Rose 100
    svc_disabled_text = "#881337"   # Rose 900

    # Pastel Vibrant Blocks
    pastel_emerald_bg = "#D1FAE5"    # Emerald 100
    pastel_emerald_fg = "#064E3B"    # Emerald 900
    pastel_blue_bg = "#DBEAFE"       # Blue 100
    pastel_blue_fg = "#1E3A8A"       # Blue 900
    pastel_rose_bg = "#FCE7F3"       # Pink 100
    pastel_rose_fg = "#831843"       # Pink 900
    pastel_amber_bg = "#FEF3C7"      # Amber 100
    pastel_amber_fg = "#78350F"      # Amber 900
    pastel_purple_bg = "#EDE9FE"     # Violet 100
    pastel_purple_fg = "#4C1D95"     # Violet 900


    if dark:
        # Override with Night Mode Tokens (Deep Space Vibrant)
        bg_window = "#0B1120"           # Slate 950 (Very dark, solid)
        bg_card = "#1E293B"             # Slate 800 (Distinct lighter block)
        sidebar_bg = "#0F172A"          # Slate 900 (Subtle sidebar elevation)
        
        text_primary = "#F8FAFC"        # Slate 50
        text_secondary = "#94A3B8"      # Slate 400
        
        tab_bg_unselected = "rgba(15, 23, 42, 150)" # Slate 900 translucent
        tab_bg_selected = "#00E1D9"     # Cyan (Cyberpunk Neon)
        tab_text_unselected = "#E2E8F0" # Slate 200
        tab_text_selected = "#0F172A"   # Slate 900
        
        toc_hover_bg = "#1E293B"        # Slate 800
        tab_pane_bg = "#0B1120"         # Slate 950 for distinct background
        
        input_bg = "#0B1120"            # Slate 950
        input_focus = "#1E293B"         # Slate 800
        
        btn_bg_secondary = "rgba(30, 41, 59, 200)" # Slate 800
        btn_text_sec = "#F8FAFC"
        btn_hover_sec = "rgba(51, 65, 85, 255)" # Slate 700
        
        btn_bg_primary = "#8B5CF6"      # Violet 500 (Solid Vibrant)
        btn_text_pri = "#FFFFFF"
        btn_hover_pri = "#7C3AED"       # Violet 600 (Solid Vibrant)
        
        # High contrast vibrant blocks
        svc_enabled_bg = "#064E3B"      # Emerald 900
        svc_enabled_text = "#D1FAE5"    # Emerald 100
        
        svc_disabled_bg = "#4C0519"     # Rose 900
        svc_disabled_text = "#FFE4E6"   # Rose 100
        
        # Pastel Vibrant Blocks (Dark Variants: neon pastel effect)
        pastel_emerald_bg = "#064E3B"    # Emerald 900
        pastel_emerald_fg = "#6EE7B7"    # Emerald 300
        pastel_blue_bg = "#1E3A8A"       # Blue 900
        pastel_blue_fg = "#93C5FD"       # Blue 300
        pastel_rose_bg = "#831843"       # Pink 900
        pastel_rose_fg = "#F9A8D4"       # Pink 300
        pastel_amber_bg = "#78350F"      # Amber 900
        pastel_amber_fg = "#FCD34D"      # Amber 300
        pastel_purple_bg = "#4C1D95"     # Violet 900
        pastel_purple_fg = "#C4B5FD"     # Violet 300


    return f'''
        QDialog {{
            background: {bg_window};
        }}
        
        QLabel {{
            color: {text_primary};
        }}
        QLabel[cssClass="helperText"] {{
            color: {text_secondary};
            font-size: 11px;
        }}
        
        /* General Blocks / Cards */
        QFrame[cssClass="vibrantCard"] {{
            background: {bg_card};
            border: none;
            border-radius: 16px;
            margin-top: 6px;
        }}
        
        QWidget[cssClass="sidebarPanel"] {{
            background: {sidebar_bg};
            border-radius: 16px;
        }}
        
        /* GroupBox (used heavily in batch ui) - making it look like a vibrant card */
        QGroupBox {{
            background: {bg_card};
            border: none;
            border-radius: 16px;
            margin-top: 24px;
            padding: 18px;
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top left;
            left: 14px;
            padding: 4px 10px;
            color: {text_primary};
            font-weight: 800;
        }}
        
        /* Service Cards used in Configuration */
        QFrame[cssClass="serviceCard"] {{
            border-radius: 16px;
            border: none;
        }}
        QFrame[cssClass="serviceCard"][cardState="enabled"] {{
            background: {svc_enabled_bg};
        }}
        QFrame[cssClass="serviceCard"][cardState="enabled"] QLabel {{
            color: {svc_enabled_text};
        }}
        
        QFrame[cssClass="serviceCard"][cardState="disabled"] {{
            background: {svc_disabled_bg};
        }}
        QFrame[cssClass="serviceCard"][cardState="disabled"] QLabel {{
            color: {svc_disabled_text};
        }}
        
        /* Checkboxes & RadioButtons */
        QCheckBox, QRadioButton {{
            color: {text_primary};
            spacing: 8px;
            background: transparent;
        }}
        
        /* QTabWidget */
        QTabWidget::pane {{
            border: 1px solid transparent;
            background: {input_bg};
            border-radius: 16px;
        }}
        QTabBar::tab {{
            background: {tab_bg_unselected};
            color: {tab_text_unselected};
            padding: 12px 20px;
            margin-right: 8px;
            border-radius: 14px;
            font-size: 13px;
            font-weight: bold;
        }}
        QTabBar::tab:selected {{
            background: {tab_bg_selected};
            color: {tab_text_selected};
            font-size: 13px;
            font-weight: 800;
        }}
        QTabBar::tab:hover:!selected {{
            background: {btn_hover_sec};
        }}
        
        /* Pastel Vibrant Blocks Buttons */
        QPushButton[cssClass="btnPastelEmerald"] {{
            padding: 6px 16px;
            border-radius: 12px;
            border: none;
            background: {pastel_emerald_bg};
            color: {pastel_emerald_fg};
            font-weight: 800;
        }}
        QPushButton[cssClass="btnPastelEmerald"]:hover {{
            background: {pastel_emerald_fg};
            color: {pastel_emerald_bg};
        }}
        
        QPushButton[cssClass="btnPastelBlue"] {{
            padding: 6px 16px;
            border-radius: 12px;
            border: none;
            background: {pastel_blue_bg};
            color: {pastel_blue_fg};
            font-weight: 800;
        }}
        QPushButton[cssClass="btnPastelBlue"]:hover {{
            background: {pastel_blue_fg};
            color: {pastel_blue_bg};
        }}
        
        QPushButton[cssClass="btnPastelRose"] {{
            padding: 6px 16px;
            border-radius: 12px;
            border: none;
            background: {pastel_rose_bg};
            color: {pastel_rose_fg};
            font-weight: 800;
        }}
        QPushButton[cssClass="btnPastelRose"]:hover {{
            background: {pastel_rose_fg};
            color: {pastel_rose_bg};
        }}
        
        QPushButton[cssClass="btnPastelAmber"] {{
            padding: 6px 16px;
            border-radius: 12px;
            border: none;
            background: {pastel_amber_bg};
            color: {pastel_amber_fg};
            font-weight: 800;
        }}
        QPushButton[cssClass="btnPastelAmber"]:hover {{
            background: {pastel_amber_fg};
            color: {pastel_amber_bg};
        }}
        
        QPushButton[cssClass="btnPastelPurple"] {{
            padding: 6px 16px;
            border-radius: 12px;
            border: none;
            background: {pastel_purple_bg};
            color: {pastel_purple_fg};
            font-weight: 800;
        }}
        QPushButton[cssClass="btnPastelPurple"]:hover {{
            background: {pastel_purple_fg};
            color: {pastel_purple_bg};
        }}

        
        /* Sidebar/TOC List mimicking Tabs */
        /* See component_configuration for active TOC buttons */
        QPushButton[cssClass="tocButtonInactive"] {{
            text-align: left; 
            padding: 14px 16px; 
            border: none; 
            font-weight: 600; 
            font-size: 13px;
            border-radius: 14px; 
            color: {text_secondary}; 
            background: transparent; 
        }}
        QPushButton[cssClass="tocButtonInactive"]:hover {{
            background: {toc_hover_bg}!important; 
            color: {text_primary}!important;
        }}
        QPushButton[cssClass="tocButtonActive"] {{
            text-align: left; 
            padding: 14px 16px; 
            border: none; 
            font-weight: 800; 
            font-size: 13px;
            border-radius: 14px; 
            color: {tab_text_selected}; 
            background: {tab_bg_selected}; 
        }}
        QPushButton[cssClass="tocButtonActive"]:hover {{
            background: {tab_bg_selected}!important; 
            color: {tab_text_selected}!important;
        }}
        QToolButton[cssClass="collapsibleToggle"] {{
            text-align: left;
            padding: 10px 18px;
            border-radius: 12px;
            background: {btn_bg_secondary};
            border: none;
            color: {btn_text_sec};
            font-weight: bold;
            margin-top: 6px;
        }}
        QToolButton[cssClass="collapsibleToggle"]:hover {{
            background: {btn_hover_sec};
        }}
        /* Inputs */
        QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {{
            padding: 10px 14px;
            border: none;
            border-radius: 10px;
            background: {input_bg};
            color: {text_primary};
        }}
        QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus {{
            background: {input_focus};
        }}
        QComboBox QAbstractItemView {{
            background: {bg_card};
            border: none;
            color: {text_primary};
            selection-background-color: {tab_bg_selected};
        }}
        
        /* ScrollArea */
        QScrollArea {{
            background: transparent;
            border: none;
            border-radius: 16px;
        }}
        QScrollArea > QWidget > QWidget {{
            background: transparent;
            border-radius: 16px;
        }}

        /* Buttons (General Fallbacks - Secondary) */
        QPushButton {{
            padding: 10px 18px;
            border-radius: 12px;
            background: {btn_bg_secondary};
            border: none;
            color: {btn_text_sec};
            font-weight: bold;
        }}
        QPushButton:hover {{
            background: {btn_hover_sec};
        }}
        /* Primary Button Class */
        QPushButton[cssClass="primaryButton"] {{
            background: {btn_bg_primary};
            color: {btn_text_pri};
            font-weight: 800;
        }}
        QPushButton[cssClass="primaryButton"]:hover {{
            background: {btn_hover_pri};
        }}
    '''


def _build_ollama_stylesheet(dark: bool) -> str:
    """Returns a stylesheet adhering to the Ollama design system.

    Paper-white flat canvas, pill geometry (9999px) for interactive elements,
    12px cards, no gradients, no drop shadows. Black-on-white in light mode;
    inverted to near-black (#171717) in dark mode.
    """
    # ── Light Mode Tokens (paper-white) ──
    canvas = "#ffffff"
    surface_soft = "#fafafa"
    surface_card = "#ffffff"
    surface_dark = "#171717"

    ink = "#000000"            # primary / headings / links
    ink_deep = "#090909"       # pressed
    charcoal = "#525252"       # list / secondary copy
    body = "#737373"           # default prose
    mute = "#a3a3a3"           # captions / utility
    hairline = "#e5e5e5"       # 1px borders
    hairline_strong = "#d4d4d4"

    on_primary = "#ffffff"
    on_dark = "#ffffff"
    on_dark_mute = "rgba(255,255,255,0.7)"

    # Tab / nav accents (monochrome — the only "selected" cue is ink fill)
    tab_bg_unselected = "rgba(0, 0, 0, 0)"
    tab_bg_selected = "#000000"
    tab_text_unselected = "#525252"
    tab_text_selected = "#ffffff"
    toc_hover_bg = "#fafafa"

    input_bg = "#fafafa"
    input_focus = "#ffffff"
    selection_bg = "#000000"

    btn_bg_secondary = "#ffffff"
    btn_text_sec = "#000000"
    btn_hover_sec = "#fafafa"
    btn_border_sec = "#d4d4d4"

    btn_bg_primary = "#000000"
    btn_text_pri = "#ffffff"
    btn_hover_pri = "#090909"

    # Service cards: hairline border, flat white (enabled) vs muted (disabled)
    svc_enabled_bg = "#ffffff"
    svc_enabled_text = "#000000"
    svc_disabled_bg = "#fafafa"
    svc_disabled_text = "#a3a3a3"

    # Pastel classes collapsed to flat neutral "chip" treatments
    pastel_bg = "#fafafa"
    pastel_fg = "#000000"

    if dark:
        canvas = "#0a0a0a"
        surface_soft = "#171717"
        surface_card = "#171717"
        surface_dark = "#171717"

        ink = "#ffffff"
        ink_deep = "#e5e5e5"
        charcoal = "#d4d4d4"
        body = "#a3a3a3"
        mute = "#737373"
        hairline = "#2a2a2a"
        hairline_strong = "#404040"

        on_primary = "#000000"
        on_dark = "#ffffff"
        on_dark_mute = "rgba(255,255,255,0.7)"

        tab_bg_unselected = "rgba(255, 255, 255, 0)"
        tab_bg_selected = "#ffffff"
        tab_text_unselected = "#a3a3a3"
        tab_text_selected = "#000000"
        toc_hover_bg = "#171717"

        input_bg = "#171717"
        input_focus = "#0a0a0a"
        selection_bg = "#ffffff"

        btn_bg_secondary = "#171717"
        btn_text_sec = "#ffffff"
        btn_hover_sec = "#1f1f1f"
        btn_border_sec = "#404040"

        btn_bg_primary = "#ffffff"
        btn_text_pri = "#000000"
        btn_hover_pri = "#e5e5e5"

        svc_enabled_bg = "#171717"
        svc_enabled_text = "#ffffff"
        svc_disabled_bg = "#0a0a0a"
        svc_disabled_text = "#737373"

        pastel_bg = "#171717"
        pastel_fg = "#ffffff"

    return f'''
        QDialog {{
            background: {canvas};
        }}

        QLabel {{
            color: {ink};
        }}
        QLabel[cssClass="helperText"] {{
            color: {body};
            font-size: 11px;
        }}

        /* Cards: 12px rounded, 1px hairline border, no shadow */
        QFrame[cssClass="vibrantCard"] {{
            background: {surface_card};
            border: 1px solid {hairline};
            border-radius: 12px;
            margin-top: 6px;
        }}

        QWidget[cssClass="sidebarPanel"] {{
            background: {surface_soft};
            border: 1px solid {hairline};
            border-radius: 12px;
        }}

        QGroupBox {{
            background: {surface_card};
            border: 1px solid {hairline};
            border-radius: 12px;
            margin-top: 24px;
            padding: 18px;
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top left;
            left: 14px;
            padding: 4px 10px;
            color: {ink};
            font-weight: 600;
        }}

        /* Service cards */
        QFrame[cssClass="serviceCard"] {{
            border-radius: 12px;
            border: 1px solid {hairline};
        }}
        QFrame[cssClass="serviceCard"][cardState="enabled"] {{
            background: {svc_enabled_bg};
        }}
        QFrame[cssClass="serviceCard"][cardState="enabled"] QLabel {{
            color: {svc_enabled_text};
        }}
        QFrame[cssClass="serviceCard"][cardState="disabled"] {{
            background: {svc_disabled_bg};
        }}
        QFrame[cssClass="serviceCard"][cardState="disabled"] QLabel {{
            color: {svc_disabled_text};
        }}

        /* Checkboxes & RadioButtons */
        QCheckBox, QRadioButton {{
            color: {ink};
            spacing: 8px;
            background: transparent;
        }}

        /* Tabs */
        QTabWidget::pane {{
            border: 1px solid {hairline};
            background: {canvas};
            border-radius: 12px;
        }}
        QTabBar::tab {{
            background: {tab_bg_unselected};
            color: {tab_text_unselected};
            padding: 12px 20px;
            margin-right: 8px;
            border-radius: 9999px;
            font-size: 13px;
            font-weight: 500;
        }}
        QTabBar::tab:selected {{
            background: {tab_bg_selected};
            color: {tab_text_selected};
            font-size: 13px;
            font-weight: 600;
        }}
        QTabBar::tab:hover:!selected {{
            background: {toc_hover_bg};
        }}

        /* Pastel Vibrant Blocks buttons → flat neutral chips */
        QPushButton[cssClass="btnPastelEmerald"],
        QPushButton[cssClass="btnPastelBlue"],
        QPushButton[cssClass="btnPastelRose"],
        QPushButton[cssClass="btnPastelAmber"],
        QPushButton[cssClass="btnPastelPurple"] {{
            padding: 6px 16px;
            border-radius: 9999px;
            border: 1px solid {hairline};
            background: {pastel_bg};
            color: {pastel_fg};
            font-weight: 600;
        }}
        QPushButton[cssClass="btnPastelEmerald"]:hover,
        QPushButton[cssClass="btnPastelBlue"]:hover,
        QPushButton[cssClass="btnPastelRose"]:hover,
        QPushButton[cssClass="btnPastelAmber"]:hover,
        QPushButton[cssClass="btnPastelPurple"]:hover {{
            background: {btn_hover_sec};
        }}

        /* Sidebar/TOC list */
        QPushButton[cssClass="tocButtonInactive"] {{
            text-align: left;
            padding: 14px 16px;
            border: none;
            font-weight: 500;
            font-size: 13px;
            border-radius: 9999px;
            color: {charcoal};
            background: transparent;
        }}
        QPushButton[cssClass="tocButtonInactive"]:hover {{
            background: {toc_hover_bg}!important;
            color: {ink}!important;
        }}
        QPushButton[cssClass="tocButtonActive"] {{
            text-align: left;
            padding: 14px 16px;
            border: none;
            font-weight: 600;
            font-size: 13px;
            border-radius: 9999px;
            color: {tab_text_selected};
            background: {tab_bg_selected};
        }}
        QPushButton[cssClass="tocButtonActive"]:hover {{
            background: {tab_bg_selected}!important;
            color: {tab_text_selected}!important;
        }}
        QToolButton[cssClass="collapsibleToggle"] {{
            text-align: left;
            padding: 10px 18px;
            border-radius: 9999px;
            background: {btn_bg_secondary};
            border: 1px solid {btn_border_sec};
            color: {btn_text_sec};
            font-weight: 500;
            margin-top: 6px;
        }}
        QToolButton[cssClass="collapsibleToggle"]:hover {{
            background: {btn_hover_sec};
        }}

        /* Inputs: pill geometry */
        QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {{
            padding: 10px 16px;
            border: 1px solid {hairline};
            border-radius: 9999px;
            background: {input_bg};
            color: {ink};
        }}
        QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus {{
            background: {input_focus};
            border: 1px solid {ink};
        }}
        QComboBox QAbstractItemView {{
            background: {surface_card};
            border: 1px solid {hairline};
            color: {ink};
            selection-background-color: {selection_bg};
            selection-color: {on_primary};
        }}

        /* ScrollArea */
        QScrollArea {{
            background: transparent;
            border: none;
            border-radius: 12px;
        }}
        QScrollArea > QWidget > QWidget {{
            background: transparent;
            border-radius: 12px;
        }}

        /* Buttons (general fallbacks) */
        QPushButton {{
            padding: 10px 20px;
            border-radius: 9999px;
            background: {btn_bg_secondary};
            border: 1px solid {btn_border_sec};
            color: {btn_text_sec};
            font-weight: 500;
        }}
        QPushButton:hover {{
            background: {btn_hover_sec};
        }}
        /* Primary Button Class — black pill */
        QPushButton[cssClass="primaryButton"] {{
            background: {btn_bg_primary};
            color: {btn_text_pri};
            border: 1px solid {btn_bg_primary};
            font-weight: 600;
        }}
        QPushButton[cssClass="primaryButton"]:hover {{
            background: {btn_hover_pri};
            border: 1px solid {btn_hover_pri};
        }}
    '''


def _build_apple_stylesheet(dark: bool) -> str:
    """Returns a stylesheet adhering to the Apple design system.

    Clean, photography-first aesthetic with an SF Pro feel. Canvas is near-white
    (#ffffff / #f5f5f7), ink is near-black (#1d1d1f), and a single Action Blue
    (#0066cc) drives all interactive states. Cards use soft 11-18px radii and a
    hairline border. Dark mode inverts to black canvas with #2997ff primary.
    No decorative gradients, no shadows on chrome.
    """
    # ── Light Mode Tokens ──
    canvas = "#ffffff"
    canvas_parchment = "#f5f5f7"
    surface_pearl = "#fafafc"
    surface_card = "#ffffff"

    ink = "#1d1d1f"
    body = "#1d1d1f"
    body_muted = "#333333"
    ink_muted_48 = "#7a7a7a"
    charcoal = "#333333"
    mute = "#7a7a7a"
    hairline = "#e0e0e0"
    divider_soft = "#f0f0f0"

    primary = "#0066cc"        # Action Blue
    primary_focus = "#0071e3"
    on_primary = "#ffffff"
    link = "#0066cc"

    tab_bg_unselected = "rgba(0, 0, 0, 0)"
    tab_bg_selected = "#0066cc"
    tab_text_unselected = "#333333"
    tab_text_selected = "#ffffff"
    toc_hover_bg = "#f5f5f7"

    input_bg = "#ffffff"
    input_focus = "#ffffff"
    selection_bg = "#0066cc"

    btn_bg_secondary = "#ffffff"
    btn_text_sec = "#1d1d1f"
    btn_hover_sec = "#f5f5f7"
    btn_border_sec = "#d2d2d7"

    btn_bg_primary = "#0066cc"
    btn_text_pri = "#ffffff"
    btn_hover_pri = "#0071e3"

    svc_enabled_bg = "#f5f5f7"
    svc_enabled_text = "#1d1d1f"
    svc_disabled_bg = "#fafafc"
    svc_disabled_text = "#7a7a7a"

    pastel_bg = "#f5f5f7"
    pastel_fg = "#1d1d1f"

    if dark:
        canvas = "#000000"
        canvas_parchment = "#1d1d1f"
        surface_pearl = "#1d1d1f"
        surface_card = "#1d1d1f"

        ink = "#ffffff"
        body = "#ffffff"
        body_muted = "#cccccc"
        ink_muted_48 = "#7a7a7a"
        charcoal = "#e0e0e0"
        mute = "#7a7a7a"
        hairline = "#333333"
        divider_soft = "#2a2a2c"

        primary = "#2997ff"        # Action Blue (on dark)
        primary_focus = "#0071e3"
        on_primary = "#000000"
        link = "#2997ff"

        tab_bg_unselected = "rgba(255, 255, 255, 0)"
        tab_bg_selected = "#2997ff"
        tab_text_unselected = "#a1a1a6"
        tab_text_selected = "#000000"
        toc_hover_bg = "#2a2a2c"

        input_bg = "#1d1d1f"
        input_focus = "#1d1d1f"
        selection_bg = "#2997ff"

        btn_bg_secondary = "#1d1d1f"
        btn_text_sec = "#ffffff"
        btn_hover_sec = "#333333"
        btn_border_sec = "#48484a"

        btn_bg_primary = "#2997ff"
        btn_text_pri = "#000000"
        btn_hover_pri = "#2997ff"

        svc_enabled_bg = "#2a2a2c"
        svc_enabled_text = "#ffffff"
        svc_disabled_bg = "#1d1d1f"
        svc_disabled_text = "#7a7a7a"

        pastel_bg = "#2a2a2c"
        pastel_fg = "#ffffff"

    return f'''
        QDialog {{
            background: {canvas_parchment};
        }}

        QLabel {{
            color: {ink};
        }}
        QLabel[cssClass="helperText"] {{
            color: {ink_muted_48};
            font-size: 11px;
        }}

        /* Cards: 18px rounded, hairline border */
        QFrame[cssClass="vibrantCard"] {{
            background: {surface_card};
            border: 1px solid {hairline};
            border-radius: 18px;
            margin-top: 6px;
        }}

        QWidget[cssClass="sidebarPanel"] {{
            background: {canvas};
            border: 1px solid {hairline};
            border-radius: 18px;
        }}

        QGroupBox {{
            background: {surface_pearl};
            border: 1px solid {hairline};
            border-radius: 18px;
            margin-top: 24px;
            padding: 18px;
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top left;
            left: 14px;
            padding: 4px 10px;
            color: {ink};
            font-weight: 600;
        }}

        /* Service cards */
        QFrame[cssClass="serviceCard"] {{
            border-radius: 14px;
            border: 1px solid {hairline};
        }}
        QFrame[cssClass="serviceCard"][cardState="enabled"] {{
            background: {svc_enabled_bg};
        }}
        QFrame[cssClass="serviceCard"][cardState="enabled"] QLabel {{
            color: {svc_enabled_text};
        }}
        QFrame[cssClass="serviceCard"][cardState="disabled"] {{
            background: {svc_disabled_bg};
        }}
        QFrame[cssClass="serviceCard"][cardState="disabled"] QLabel {{
            color: {svc_disabled_text};
        }}

        /* Checkboxes & RadioButtons */
        QCheckBox, QRadioButton {{
            color: {ink};
            spacing: 8px;
            background: transparent;
        }}

        /* Tabs */
        QTabWidget::pane {{
            border: 1px solid {hairline};
            background: {canvas};
            border-radius: 18px;
        }}
        QTabBar::tab {{
            background: {tab_bg_unselected};
            color: {tab_text_unselected};
            padding: 12px 20px;
            margin-right: 8px;
            border-radius: 11px;
            font-size: 13px;
            font-weight: 500;
        }}
        QTabBar::tab:selected {{
            background: {tab_bg_selected};
            color: {tab_text_selected};
            font-size: 13px;
            font-weight: 600;
        }}
        QTabBar::tab:hover:!selected {{
            background: {toc_hover_bg};
        }}

        /* Pastel classes → flat neutral chips */
        QPushButton[cssClass="btnPastelEmerald"],
        QPushButton[cssClass="btnPastelBlue"],
        QPushButton[cssClass="btnPastelRose"],
        QPushButton[cssClass="btnPastelAmber"],
        QPushButton[cssClass="btnPastelPurple"] {{
            padding: 6px 16px;
            border-radius: 9999px;
            border: 1px solid {hairline};
            background: {pastel_bg};
            color: {pastel_fg};
            font-weight: 600;
        }}
        QPushButton[cssClass="btnPastelEmerald"]:hover,
        QPushButton[cssClass="btnPastelBlue"]:hover,
        QPushButton[cssClass="btnPastelRose"]:hover,
        QPushButton[cssClass="btnPastelAmber"]:hover,
        QPushButton[cssClass="btnPastelPurple"]:hover {{
            background: {btn_hover_sec};
        }}

        /* Sidebar/TOC list — pill-ish */
        QPushButton[cssClass="tocButtonInactive"] {{
            text-align: left;
            padding: 14px 16px;
            border: none;
            font-weight: 500;
            font-size: 13px;
            border-radius: 11px;
            color: {charcoal};
            background: transparent;
        }}
        QPushButton[cssClass="tocButtonInactive"]:hover {{
            background: {toc_hover_bg}!important;
            color: {ink}!important;
        }}
        QPushButton[cssClass="tocButtonActive"] {{
            text-align: left;
            padding: 14px 16px;
            border: none;
            font-weight: 600;
            font-size: 13px;
            border-radius: 11px;
            color: {tab_text_selected};
            background: {tab_bg_selected};
        }}
        QPushButton[cssClass="tocButtonActive"]:hover {{
            background: {tab_bg_selected}!important;
            color: {tab_text_selected}!important;
        }}
        QToolButton[cssClass="collapsibleToggle"] {{
            text-align: left;
            padding: 10px 18px;
            border-radius: 9999px;
            background: {btn_bg_secondary};
            border: 1px solid {btn_border_sec};
            color: {btn_text_sec};
            font-weight: 500;
            margin-top: 6px;
        }}
        QToolButton[cssClass="collapsibleToggle"]:hover {{
            background: {btn_hover_sec};
        }}

        /* Inputs */
        QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {{
            padding: 10px 16px;
            border: 1px solid {hairline};
            border-radius: 11px;
            background: {input_bg};
            color: {ink};
        }}
        QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus {{
            background: {input_focus};
            border: 1px solid {primary};
        }}
        QComboBox QAbstractItemView {{
            background: {surface_card};
            border: 1px solid {hairline};
            color: {ink};
            selection-background-color: {selection_bg};
            selection-color: {on_primary};
        }}

        /* ScrollArea */
        QScrollArea {{
            background: transparent;
            border: none;
            border-radius: 18px;
        }}
        QScrollArea > QWidget > QWidget {{
            background: transparent;
            border-radius: 18px;
        }}

        /* Buttons (general fallbacks) */
        QPushButton {{
            padding: 10px 20px;
            border-radius: 9999px;
            background: {btn_bg_secondary};
            border: 1px solid {btn_border_sec};
            color: {btn_text_sec};
            font-weight: 500;
        }}
        QPushButton:hover {{
            background: {btn_hover_sec};
        }}
        /* Primary Button Class — Action Blue pill */
        QPushButton[cssClass="primaryButton"] {{
            background: {btn_bg_primary};
            color: {btn_text_pri};
            border: 1px solid {btn_bg_primary};
            font-weight: 600;
        }}
        QPushButton[cssClass="primaryButton"]:hover {{
            background: {btn_hover_pri};
            border: 1px solid {btn_hover_pri};
        }}
    '''

