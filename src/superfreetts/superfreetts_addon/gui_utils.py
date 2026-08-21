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

VALID_THEMES = ("vibrant", "ollama", "apple", "nintendo", "binance", "clay", "claude")


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
    if _active_theme == "nintendo":
        return _build_nintendo_stylesheet(dark)
    if _active_theme == "binance":
        return _build_binance_stylesheet(dark)
    if _active_theme == "clay":
        return _build_clay_stylesheet(dark)
    if _active_theme == "claude":
        return _build_claude_stylesheet(dark)
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


def _build_nintendo_stylesheet(dark: bool) -> str:
    """Returns a stylesheet adhering to the Nintendo.com (2001) design system.

    A Y2K 'console chrome' aesthetic: periwinkle metallic canvas, beveled
    panels, carbon-navy ink, and a warm Nintendo accent set (red #e60012,
    signal orange #f68d1f, amber #ecab37, nav-gold #e48600). Panels use small
    (2-10px) radii — buttons lean slightly rounded, cards subtle. Contrast
    light and dark variants.
    """
    # ── Light Mode Tokens ──
    primary = "#e60012"        # Nintendo Red
    signal = "#f68d1f"         # Signal Orange
    amber = "#ecab37"          # Amber
    nav_gold = "#e48600"
    on_primary = "#ffffff"

    canvas = "#7a8aba"          # Periwinkle metallic
    canvas_soft = "#9fbee7"     # Pale Sky
    card = "#ffffff"            # content surface
    card_alt = "#dedede"        # Platinum
    chrome = "#3d4f97"          # Chrome Indigo
    chrome_muted = "#60619c"    # Muted Indigo
    hairline = "#5a5f8c"

    ink = "#21242e"             # Carbon Navy
    ink_soft = "#3d4f97"
    body = "#21242e"
    mute = "#60619c"

    tab_bg_unselected = "rgba(0, 0, 0, 0)"
    tab_bg_selected = "#e60012"
    tab_text_unselected = "#ffffffe0" if not dark else "#cfd6ff"
    tab_text_selected = "#ffffff"
    toc_hover_bg = "#9fbee7"

    input_bg = "#ffffff"
    input_focus = "#ffffff"
    selection_bg = "#e60012"

    btn_bg_secondary = "#21242e"
    btn_text_sec = "#ffffff"
    btn_hover_sec = "#3d4f97"
    btn_border_sec = "#5a5f8c"

    btn_bg_primary = "#ecab37"
    btn_text_pri = "#21242e"
    btn_hover_pri = "#e48600"

    svc_enabled_bg = "#e7edf7"
    svc_enabled_text = "#21242e"
    svc_disabled_bg = "#dedede"
    svc_disabled_text = "#60619c"

    pastel_bg = "#9fbee7"
    pastel_fg = "#21242e"

    if dark:
        canvas = "#20242f"          # darker than carbon, night console
        canvas_soft = "#2a3247"
        card = "#2a3247"
        card_alt = "#333c54"
        chrome = "#3d4f97"
        chrome_muted = "#60619c"
        hairline = "#4a5380"

        ink = "#f2f4fa"
        ink_soft = "#b8c4f0"
        body = "#e6e9f2"
        mute = "#9aa3c4"

        tab_bg_unselected = "rgba(255, 255, 255, 0)"
        tab_bg_selected = "#e60012"
        tab_text_unselected = "#cfd6ff"
        tab_text_selected = "#ffffff"
        toc_hover_bg = "#333c54"

        input_bg = "#262b3b"
        input_focus = "#2a3247"
        selection_bg = "#e60012"

        btn_bg_secondary = "#21242e"
        btn_text_sec = "#ffffff"
        btn_hover_sec = "#3d4f97"
        btn_border_sec = "#4a5380"

        btn_bg_primary = "#ecab37"
        btn_text_pri = "#21242e"
        btn_hover_pri = "#e48600"

        svc_enabled_bg = "#333c54"
        svc_enabled_text = "#ffffff"
        svc_disabled_bg = "#21242e"
        svc_disabled_text = "#9aa3c4"

        pastel_bg = "#333c54"
        pastel_fg = "#ffffff"

    return f'''
        QDialog {{
            background: {canvas};
        }}

        QLabel {{
            color: {ink};
        }}
        QLabel[cssClass="helperText"] {{
            color: {mute};
            font-size: 11px;
        }}

        /* Cards: beveled panel, small radius */
        QFrame[cssClass="vibrantCard"] {{
            background: {card};
            border: 1px solid {hairline};
            border-radius: 10px;
            margin-top: 6px;
        }}

        QWidget[cssClass="sidebarPanel"] {{
            background: {card_alt};
            border: 1px solid {hairline};
            border-radius: 6px;
        }}

        QGroupBox {{
            background: {card};
            border: 1px solid {hairline};
            border-radius: 10px;
            margin-top: 24px;
            padding: 18px;
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top left;
            left: 14px;
            padding: 4px 10px;
            color: {ink};
            font-weight: 700;
        }}

        /* Service cards */
        QFrame[cssClass="serviceCard"] {{
            border-radius: 6px;
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
            background: {canvas_soft};
            border-radius: 6px;
        }}
        QTabBar::tab {{
            background: {tab_bg_unselected};
            color: {tab_text_unselected};
            padding: 12px 18px;
            margin-right: 6px;
            border-radius: 4px;
            font-size: 13px;
            font-weight: 700;
        }}
        QTabBar::tab:selected {{
            background: {tab_bg_selected};
            color: {tab_text_selected};
            font-size: 13px;
            font-weight: 800;
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
            font-weight: 700;
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
            font-weight: 600;
            font-size: 13px;
            border-radius: 4px;
            color: {ink_soft};
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
            font-weight: 800;
            font-size: 13px;
            border-radius: 4px;
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
            border-radius: 6px;
            background: {btn_bg_secondary};
            border: 1px solid {btn_border_sec};
            color: {btn_text_sec};
            font-weight: 600;
            margin-top: 6px;
        }}
        QToolButton[cssClass="collapsibleToggle"]:hover {{
            background: {btn_hover_sec};
        }}

        /* Inputs */
        QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {{
            padding: 10px 16px;
            border: 1px solid {hairline};
            border-radius: 6px;
            background: {input_bg};
            color: {ink};
        }}
        QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus {{
            background: {input_focus};
            border: 1px solid {primary};
        }}
        QComboBox QAbstractItemView {{
            background: {card};
            border: 1px solid {hairline};
            color: {ink};
            selection-background-color: {selection_bg};
            selection-color: {on_primary};
        }}

        /* ScrollArea */
        QScrollArea {{
            background: transparent;
            border: none;
            border-radius: 10px;
        }}
        QScrollArea > QWidget > QWidget {{
            background: transparent;
            border-radius: 10px;
        }}

        /* Buttons (general fallbacks) */
        QPushButton {{
            padding: 10px 20px;
            border-radius: 6px;
            background: {btn_bg_secondary};
            border: 1px solid {btn_border_sec};
            color: {btn_text_sec};
            font-weight: 600;
        }}
        QPushButton:hover {{
            background: {btn_hover_sec};
        }}
        /* Primary Button Class — amber/gold pill */
        QPushButton[cssClass="primaryButton"] {{
            background: {btn_bg_primary};
            color: {btn_text_pri};
            border: 1px solid {btn_bg_primary};
            font-weight: 800;
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


def _build_binance_stylesheet(dark: bool) -> str:
    """Returns a stylesheet adhering to the Binance design system.

    A confident financial-platform look: deep near-black canvas, Binance
    Yellow (#fcd535) driving every primary CTA, and gray-blue hairlines.
    Defaults to dark; light mode uses the same yellow CTAs on white.
    """
    # â”€â”€ Tokens (dark-first by default) â”€â”€
    primary = "#fcd535"        # Binance Yellow
    primary_active = "#f0b90b"
    on_primary = "#181a20"

    ink = "#eaecef"
    body = "#eaecef"
    mute = "#707a8a"
    mute_strong = "#929aa5"
    hairline = "#2b3139"

    canvas = "#0b0e11"
    card = "#1e2329"
    card_alt = "#2b3139"
    selection_bg = "#fcd535"

    tab_bg_unselected = "rgba(255, 255, 255, 0)"
    tab_bg_selected = "#fcd535"
    tab_text_unselected = "#848e9c"
    tab_text_selected = "#181a20"
    toc_hover_bg = "#1e2329"

    input_bg = "#181a20"
    input_focus = "#1e2329"

    btn_bg_secondary = "#2b3139"
    btn_text_sec = "#eaecef"
    btn_hover_sec = "#3b424b"
    btn_border_sec = "#2b3139"

    btn_bg_primary = "#fcd535"
    btn_text_pri = "#181a20"
    btn_hover_pri = "#f0b90b"

    svc_enabled_bg = "#1e2329"
    svc_enabled_text = "#eaecef"
    svc_disabled_bg = "#15171c"
    svc_disabled_text = "#707a8a"

    pastel_bg = "#1e2329"
    pastel_fg = "#eaecef"

    if not dark:
        canvas = "#ffffff"
        card = "#ffffff"
        card_alt = "#fafafa"
        ink = "#181a20"
        body = "#181a20"
        mute = "#707a8a"
        mute_strong = "#929aa5"
        hairline = "#eaecef"

        tab_bg_unselected = "rgba(0, 0, 0, 0)"
        tab_bg_selected = "#fcd535"
        tab_text_unselected = "#707a8a"
        tab_text_selected = "#181a20"
        toc_hover_bg = "#f5f5f5"

        input_bg = "#fafafa"
        input_focus = "#ffffff"

        btn_bg_secondary = "#fafafa"
        btn_text_sec = "#181a20"
        btn_hover_sec = "#f0f0f0"
        btn_border_sec = "#eaecef"

        btn_bg_primary = "#fcd535"
        btn_text_pri = "#181a20"
        btn_hover_pri = "#f0b90b"

        svc_enabled_bg = "#fafafa"
        svc_enabled_text = "#181a20"
        svc_disabled_bg = "#f5f5f5"
        svc_disabled_text = "#707a8a"

        pastel_bg = "#fafafa"
        pastel_fg = "#181a20"

    return f'''
        QDialog {{
            background: {canvas};
        }}

        QLabel {{
            color: {ink};
        }}
        QLabel[cssClass="helperText"] {{
            color: {mute};
            font-size: 11px;
        }}

        QFrame[cssClass="vibrantCard"] {{
            background: {card};
            border: 1px solid {hairline};
            border-radius: 10px;
            margin-top: 6px;
        }}

        QWidget[cssClass="sidebarPanel"] {{
            background: {card_alt};
            border: 1px solid {hairline};
            border-radius: 10px;
        }}

        QGroupBox {{
            background: {card};
            border: 1px solid {hairline};
            border-radius: 10px;
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

        QFrame[cssClass="serviceCard"] {{
            border-radius: 8px;
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

        QCheckBox, QRadioButton {{
            color: {ink};
            spacing: 8px;
            background: transparent;
        }}

        QTabWidget::pane {{
            border: 1px solid {hairline};
            background: {canvas};
            border-radius: 10px;
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
            font-weight: 700;
        }}
        QTabBar::tab:hover:!selected {{
            background: {toc_hover_bg};
        }}

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

        QPushButton[cssClass="tocButtonInactive"] {{
            text-align: left;
            padding: 14px 16px;
            border: none;
            font-weight: 500;
            font-size: 13px;
            border-radius: 9999px;
            color: {mute};
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
            font-weight: 700;
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

        QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {{
            padding: 10px 16px;
            border: 1px solid {hairline};
            border-radius: 8px;
            background: {input_bg};
            color: {ink};
        }}
        QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus {{
            background: {input_focus};
            border: 1px solid {primary};
        }}
        QComboBox QAbstractItemView {{
            background: {card};
            border: 1px solid {hairline};
            color: {ink};
            selection-background-color: {selection_bg};
            selection-color: {on_primary};
        }}

        QScrollArea {{
            background: transparent;
            border: none;
            border-radius: 10px;
        }}
        QScrollArea > QWidget > QWidget {{
            background: transparent;
            border-radius: 10px;
        }}

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
        QPushButton[cssClass="primaryButton"] {{
            background: {btn_bg_primary};
            color: {btn_text_pri};
            border: 1px solid {btn_bg_primary};
            font-weight: 700;
        }}
        QPushButton[cssClass="primaryButton"]:hover {{
            background: {btn_hover_pri};
            border: 1px solid {btn_hover_pri};
        }}
    '''


def _build_clay_stylesheet(dark: bool) -> str:
    """Returns a stylesheet adhering to the Clay.com design system.

    A vibrant 'claymation' look on a warm cream canvas (#fffaf0), dark-navy
    primary CTAs, and saturated single-color accents (pink #ff4d8b, teal,
    lavender). Soft rounded surfaces, playful yet clean.
    """
    # â”€â”€ Light Mode Tokens â”€â”€
    canvas = "#fffaf0"
    canvas_soft = "#faf5e8"
    card = "#f5f0e0"
    card_alt = "#ebe6d6"
    hairline = "#e5e5e5"

    ink = "#0a0a0a"
    body = "#3a3a3a"
    body_strong = "#1a1a1a"
    mute = "#6a6a6a"
    mute_soft = "#9a9a9a"

    primary = "#0a0a0a"
    on_primary = "#ffffff"

    brand_pink = "#ff4d8b"
    brand_teal = "#1a3a3a"
    brand_lavender = "#b8a4ed"

    tab_bg_unselected = "rgba(0, 0, 0, 0)"
    tab_bg_selected = "#ff4d8b"
    tab_text_unselected = "#6a6a6a"
    tab_text_selected = "#ffffff"
    toc_hover_bg = "#faf5e8"

    input_bg = "#ffffff"
    input_focus = "#ffffff"
    selection_bg = "#ff4d8b"

    btn_bg_secondary = "#ffffff"
    btn_text_sec = "#0a0a0a"
    btn_hover_sec = "#faf5e8"
    btn_border_sec = "#e5e5e5"

    btn_bg_primary = "#0a0a0a"
    btn_text_pri = "#ffffff"
    btn_hover_pri = "#1f1f1f"

    svc_enabled_bg = "#faf5e8"
    svc_enabled_text = "#0a0a0a"
    svc_disabled_bg = "#f5f0e0"
    svc_disabled_text = "#9a9a9a"

    pastel_bg = "#f5f0e0"
    pastel_fg = "#0a0a0a"

    if dark:
        canvas = "#0a1a1a"
        canvas_soft = "#142222"
        card = "#1a2a2a"
        card_alt = "#223333"
        hairline = "#2a3a3a"

        ink = "#f5f0e0"
        body = "#cfc7b0"
        body_strong = "#ffffff"
        mute = "#9a9a9a"
        mute_soft = "#7a7a7a"

        primary = "#ff4d8b"
        on_primary = "#ffffff"

        tab_bg_unselected = "rgba(255, 255, 255, 0)"
        tab_bg_selected = "#ff4d8b"
        tab_text_unselected = "#a0b0a0"
        tab_text_selected = "#ffffff"
        toc_hover_bg = "#1a2a2a"

        input_bg = "#1a2a2a"
        input_focus = "#223333"
        selection_bg = "#ff4d8b"

        btn_bg_secondary = "#1a2a2a"
        btn_text_sec = "#f5f0e0"
        btn_hover_sec = "#223333"
        btn_border_sec = "#2a3a3a"

        btn_bg_primary = "#ff4d8b"
        btn_text_pri = "#ffffff"
        btn_hover_pri = "#e84175"

        svc_enabled_bg = "#223333"
        svc_enabled_text = "#f5f0e0"
        svc_disabled_bg = "#142222"
        svc_disabled_text = "#7a7a7a"

        pastel_bg = "#223333"
        pastel_fg = "#f5f0e0"

    return f'''
        QDialog {{
            background: {canvas};
        }}

        QLabel {{
            color: {ink};
        }}
        QLabel[cssClass="helperText"] {{
            color: {mute};
            font-size: 11px;
        }}

        QFrame[cssClass="vibrantCard"] {{
            background: {card};
            border: 1px solid {hairline};
            border-radius: 18px;
            margin-top: 6px;
        }}

        QWidget[cssClass="sidebarPanel"] {{
            background: {card_alt};
            border: 1px solid {hairline};
            border-radius: 18px;
        }}

        QGroupBox {{
            background: {card};
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
            font-weight: 700;
        }}

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

        QCheckBox, QRadioButton {{
            color: {ink};
            spacing: 8px;
            background: transparent;
        }}

        QTabWidget::pane {{
            border: 1px solid {hairline};
            background: {canvas_soft};
            border-radius: 18px;
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
            font-weight: 700;
        }}
        QTabBar::tab:hover:!selected {{
            background: {toc_hover_bg};
        }}

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

        QPushButton[cssClass="tocButtonInactive"] {{
            text-align: left;
            padding: 14px 16px;
            border: none;
            font-weight: 500;
            font-size: 13px;
            border-radius: 9999px;
            color: {mute};
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
            font-weight: 700;
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

        QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {{
            padding: 10px 16px;
            border: 1px solid {hairline};
            border-radius: 12px;
            background: {input_bg};
            color: {ink};
        }}
        QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus {{
            background: {input_focus};
            border: 1px solid {brand_pink};
        }}
        QComboBox QAbstractItemView {{
            background: {card};
            border: 1px solid {hairline};
            color: {ink};
            selection-background-color: {selection_bg};
            selection-color: #ffffff;
        }}

        QScrollArea {{
            background: transparent;
            border: none;
            border-radius: 18px;
        }}
        QScrollArea > QWidget > QWidget {{
            background: transparent;
            border-radius: 18px;
        }}

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
        QPushButton[cssClass="primaryButton"] {{
            background: {btn_bg_primary};
            color: {btn_text_pri};
            border: 1px solid {btn_bg_primary};
            font-weight: 700;
        }}
        QPushButton[cssClass="primaryButton"]:hover {{
            background: {btn_hover_pri};
            border: 1px solid {btn_hover_pri};
        }}
    '''


def _build_claude_stylesheet(dark: bool) -> str:
    """Returns a stylesheet adhering to the Anthropic Claude design system.

    A warm-canvas editorial look: cream canvas (#faf9f5), warm coral CTAs
    (#cc785c), and dark-navy product surfaces. Serif-friendly, humanist,
    deliberately warm compared to the usual cool AI blue/slate.
    """
    # â”€â”€ Light Mode Tokens â”€â”€
    canvas = "#faf9f5"
    canvas_soft = "#f5f0e8"
    card = "#efe9de"
    card_alt = "#e8e0d2"
    hairline = "#e6dfd8"

    ink = "#141413"
    body = "#3d3d3a"
    body_strong = "#252523"
    mute = "#6c6a64"
    mute_soft = "#8e8b82"

    primary = "#cc785c"        # warm coral
    primary_active = "#a9583e"
    on_primary = "#ffffff"

    accent_teal = "#5db8a6"
    accent_amber = "#e8a55a"

    tab_bg_unselected = "rgba(0, 0, 0, 0)"
    tab_bg_selected = "#cc785c"
    tab_text_unselected = "#6c6a64"
    tab_text_selected = "#ffffff"
    toc_hover_bg = "#f5f0e8"

    input_bg = "#ffffff"
    input_focus = "#ffffff"
    selection_bg = "#cc785c"

    btn_bg_secondary = "#ffffff"
    btn_text_sec = "#141413"
    btn_hover_sec = "#f5f0e8"
    btn_border_sec = "#e6dfd8"

    btn_bg_primary = "#cc785c"
    btn_text_pri = "#ffffff"
    btn_hover_pri = "#a9583e"

    svc_enabled_bg = "#f5f0e8"
    svc_enabled_text = "#141413"
    svc_disabled_bg = "#efe9de"
    svc_disabled_text = "#8e8b82"

    pastel_bg = "#efe9de"
    pastel_fg = "#141413"

    if dark:
        canvas = "#181715"
        canvas_soft = "#1f1e1b"
        card = "#252320"
        card_alt = "#2b2926"
        hairline = "#33302c"

        ink = "#faf9f5"
        body = "#c8c4bb"
        body_strong = "#ffffff"
        mute = "#9a978f"
        mute_soft = "#7a776f"

        primary = "#d98a6f"
        primary_active = "#cc785c"
        on_primary = "#141413"

        tab_bg_unselected = "rgba(255, 255, 255, 0)"
        tab_bg_selected = "#cc785c"
        tab_text_unselected = "#a5a199"
        tab_text_selected = "#ffffff"
        toc_hover_bg = "#252320"

        input_bg = "#252320"
        input_focus = "#2b2926"
        selection_bg = "#cc785c"

        btn_bg_secondary = "#252320"
        btn_text_sec = "#faf9f5"
        btn_hover_sec = "#2b2926"
        btn_border_sec = "#33302c"

        btn_bg_primary = "#cc785c"
        btn_text_pri = "#141413"
        btn_hover_pri = "#d98a6f"

        svc_enabled_bg = "#2b2926"
        svc_enabled_text = "#faf9f5"
        svc_disabled_bg = "#1f1e1b"
        svc_disabled_text = "#7a776f"

        pastel_bg = "#2b2926"
        pastel_fg = "#faf9f5"

    return f'''
        QDialog {{
            background: {canvas};
        }}

        QLabel {{
            color: {ink};
        }}
        QLabel[cssClass="helperText"] {{
            color: {mute};
            font-size: 11px;
        }}

        QFrame[cssClass="vibrantCard"] {{
            background: {card};
            border: 1px solid {hairline};
            border-radius: 14px;
            margin-top: 6px;
        }}

        QWidget[cssClass="sidebarPanel"] {{
            background: {card_alt};
            border: 1px solid {hairline};
            border-radius: 14px;
        }}

        QGroupBox {{
            background: {card};
            border: 1px solid {hairline};
            border-radius: 14px;
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

        QFrame[cssClass="serviceCard"] {{
            border-radius: 10px;
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

        QCheckBox, QRadioButton {{
            color: {ink};
            spacing: 8px;
            background: transparent;
        }}

        QTabWidget::pane {{
            border: 1px solid {hairline};
            background: {canvas_soft};
            border-radius: 14px;
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
            font-weight: 700;
        }}
        QTabBar::tab:hover:!selected {{
            background: {toc_hover_bg};
        }}

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

        QPushButton[cssClass="tocButtonInactive"] {{
            text-align: left;
            padding: 14px 16px;
            border: none;
            font-weight: 500;
            font-size: 13px;
            border-radius: 9999px;
            color: {mute};
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
            font-weight: 700;
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

        QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {{
            padding: 10px 16px;
            border: 1px solid {hairline};
            border-radius: 10px;
            background: {input_bg};
            color: {ink};
        }}
        QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus {{
            background: {input_focus};
            border: 1px solid {primary};
        }}
        QComboBox QAbstractItemView {{
            background: {card};
            border: 1px solid {hairline};
            color: {ink};
            selection-background-color: {selection_bg};
            selection-color: {on_primary};
        }}

        QScrollArea {{
            background: transparent;
            border: none;
            border-radius: 14px;
        }}
        QScrollArea > QWidget > QWidget {{
            background: transparent;
            border-radius: 14px;
        }}

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
        QPushButton[cssClass="primaryButton"] {{
            background: {btn_bg_primary};
            color: {btn_text_pri};
            border: 1px solid {btn_bg_primary};
            font-weight: 700;
        }}
        QPushButton[cssClass="primaryButton"]:hover {{
            background: {btn_hover_pri};
            border: 1px solid {btn_hover_pri};
        }}
    '''

