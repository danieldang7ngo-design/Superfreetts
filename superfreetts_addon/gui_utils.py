import os
from string import Template

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


def get_status_badge(text, bg_color=None, text_color=None, css_class=None):
    """Return a compact rounded QLabel suitable for 'Free', 'Recommended', etc.

    Prefer ``css_class`` (a themed selector defined in the active theme's
    stylesheet) over raw ``bg_color``/``text_color`` so the badge follows the
    selected UI theme. The raw colors remain as a fallback for callers that do
    not pass a css_class.
    """
    label = aqt.qt.QLabel(text)
    if css_class is not None:
        label.setProperty("cssClass", css_class)
    else:
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
    return _build_theme_stylesheet(_active_theme, dark) + _build_services_extra_css(_active_theme, dark)

# ── Services tab theme palette ───────────────────────────────────────────────
# Colors mirror the per-theme palettes below so the
# Services tab (section headers, setup action, separators, status badges) stays
# consistent with the active theme in both light and dark mode.
_SERVICES_TOKENS = {
    "vibrant": {
        False: dict(radius=12, radius_sm=10,
                    sec_bg="#6366F1", sec_text="#FFFFFF", sec_hover="rgba(255, 255, 255, 255)",
                    setup_bg="#6366F1", setup_text="#FFFFFF", setup_border="#6366F1", setup_hover="#4338CA",
                    hairline="#E2E8F0",
                    ready_bg="#D1FAE5", ready_text="#064E3B",
                    disabled_bg="#FFE4E6", disabled_text="#881337",
                    free_bg="rgba(255, 255, 255, 180)", free_text="#0F172A",
                    rec_bg="#6366F1", rec_text="#FFFFFF"),
        True: dict(radius=12, radius_sm=10,
                   sec_bg="#00E1D9", sec_text="#0F172A", sec_hover="rgba(51, 65, 85, 255)",
                   setup_bg="#00E1D9", setup_text="#0F172A", setup_border="#00E1D9", setup_hover="#7C3AED",
                   hairline="#334155",
                   ready_bg="#064E3B", ready_text="#D1FAE5",
                   disabled_bg="#4C0519", disabled_text="#FFE4E6",
                   free_bg="rgba(30, 41, 59, 200)", free_text="#F8FAFC",
                   rec_bg="#00E1D9", rec_text="#0F172A"),
    },
    "ollama": {
        False: dict(radius=9999, radius_sm=9999,
                    sec_bg="#000000", sec_text="#ffffff", sec_hover="#fafafa",
                    setup_bg="#000000", setup_text="#ffffff", setup_border="#000000", setup_hover="#090909",
                    hairline="#e5e5e5",
                    ready_bg="#ffffff", ready_text="#000000",
                    disabled_bg="#fafafa", disabled_text="#a3a3a3",
                    free_bg="#ffffff", free_text="#000000",
                    rec_bg="#000000", rec_text="#ffffff"),
        True: dict(radius=9999, radius_sm=9999,
                   sec_bg="#ffffff", sec_text="#000000", sec_hover="#1f1f1f",
                   setup_bg="#ffffff", setup_text="#000000", setup_border="#ffffff", setup_hover="#e5e5e5",
                   hairline="#2a2a2a",
                   ready_bg="#171717", ready_text="#ffffff",
                   disabled_bg="#0a0a0a", disabled_text="#737373",
                   free_bg="#171717", free_text="#ffffff",
                   rec_bg="#ffffff", rec_text="#000000"),
    },
    "nintendo": {
        False: dict(radius=6, radius_sm=6,
                    sec_bg="#e60012", sec_text="#ffffff", sec_hover="#3d4f97",
                    setup_bg="#e60012", setup_text="#ffffff", setup_border="#e60012", setup_hover="#e48600",
                    hairline="#5a5f8c",
                    ready_bg="#e7edf7", ready_text="#21242e",
                    disabled_bg="#dedede", disabled_text="#60619c",
                    free_bg="#21242e", free_text="#ffffff",
                    rec_bg="#e60012", rec_text="#ffffff"),
        True: dict(radius=6, radius_sm=6,
                   sec_bg="#e60012", sec_text="#ffffff", sec_hover="#3d4f97",
                   setup_bg="#e60012", setup_text="#ffffff", setup_border="#e60012", setup_hover="#e48600",
                   hairline="#4a5380",
                   ready_bg="#333c54", ready_text="#ffffff",
                   disabled_bg="#21242e", disabled_text="#9aa3c4",
                   free_bg="#21242e", free_text="#ffffff",
                   rec_bg="#e60012", rec_text="#ffffff"),
    },
    "apple": {
        False: dict(radius=11, radius_sm=11,
                    sec_bg="#0066cc", sec_text="#ffffff", sec_hover="#f5f5f7",
                    setup_bg="#0066cc", setup_text="#ffffff", setup_border="#0066cc", setup_hover="#0071e3",
                    hairline="#e0e0e0",
                    ready_bg="#f5f5f7", ready_text="#1d1d1f",
                    disabled_bg="#fafafc", disabled_text="#7a7a7a",
                    free_bg="#ffffff", free_text="#1d1d1f",
                    rec_bg="#0066cc", rec_text="#ffffff"),
        True: dict(radius=11, radius_sm=11,
                   sec_bg="#2997ff", sec_text="#000000", sec_hover="#333333",
                   setup_bg="#2997ff", setup_text="#000000", setup_border="#2997ff", setup_hover="#2997ff",
                   hairline="#333333",
                   ready_bg="#2a2a2c", ready_text="#ffffff",
                   disabled_bg="#1d1d1f", disabled_text="#7a7a7a",
                   free_bg="#1d1d1f", free_text="#ffffff",
                   rec_bg="#2997ff", rec_text="#000000"),
    },
    "binance": {
        False: dict(radius=8, radius_sm=8,
                    sec_bg="#fcd535", sec_text="#181a20", sec_hover="#f0f0f0",
                    setup_bg="#fcd535", setup_text="#181a20", setup_border="#fcd535", setup_hover="#f0b90b",
                    hairline="#eaecef",
                    ready_bg="#fafafa", ready_text="#181a20",
                    disabled_bg="#f5f5f5", disabled_text="#707a8a",
                    free_bg="#fafafa", free_text="#181a20",
                    rec_bg="#fcd535", rec_text="#181a20"),
        True: dict(radius=8, radius_sm=8,
                   sec_bg="#fcd535", sec_text="#181a20", sec_hover="#3b424b",
                   setup_bg="#fcd535", setup_text="#181a20", setup_border="#fcd535", setup_hover="#f0b90b",
                   hairline="#2b3139",
                   ready_bg="#1e2329", ready_text="#eaecef",
                   disabled_bg="#15171c", disabled_text="#707a8a",
                   free_bg="#2b3139", free_text="#eaecef",
                   rec_bg="#fcd535", rec_text="#181a20"),
    },
    "clay": {
        False: dict(radius=12, radius_sm=10,
                    sec_bg="#ff4d8b", sec_text="#ffffff", sec_hover="#faf5e8",
                    setup_bg="#ff4d8b", setup_text="#ffffff", setup_border="#ff4d8b", setup_hover="#e84175",
                    hairline="#e5e5e5",
                    ready_bg="#faf5e8", ready_text="#0a0a0a",
                    disabled_bg="#f5f0e0", disabled_text="#9a9a9a",
                    free_bg="#ffffff", free_text="#0a0a0a",
                    rec_bg="#ff4d8b", rec_text="#ffffff"),
        True: dict(radius=12, radius_sm=10,
                   sec_bg="#ff4d8b", sec_text="#ffffff", sec_hover="#223333",
                   setup_bg="#ff4d8b", setup_text="#ffffff", setup_border="#ff4d8b", setup_hover="#e84175",
                   hairline="#2a3a3a",
                   ready_bg="#223333", ready_text="#f5f0e0",
                   disabled_bg="#142222", disabled_text="#7a7a7a",
                   free_bg="#1a2a2a", free_text="#f5f0e0",
                   rec_bg="#ff4d8b", rec_text="#ffffff"),
    },
    "claude": {
        False: dict(radius=14, radius_sm=12,
                    sec_bg="#cc785c", sec_text="#ffffff", sec_hover="#f5f0e8",
                    setup_bg="#cc785c", setup_text="#ffffff", setup_border="#cc785c", setup_hover="#a9583e",
                    hairline="#e6dfd8",
                    ready_bg="#f5f0e8", ready_text="#141413",
                    disabled_bg="#efe9eb", disabled_text="#8e8b82",
                    free_bg="#ffffff", free_text="#141413",
                    rec_bg="#cc785c", rec_text="#ffffff"),
        True: dict(radius=14, radius_sm=12,
                   sec_bg="#cc785c", sec_text="#ffffff", sec_hover="#252320",
                   setup_bg="#cc785c", setup_text="#ffffff", setup_border="#cc785c", setup_hover="#d98a6f",
                   hairline="#33302c",
                   ready_bg="#2b2926", ready_text="#faf9f5",
                   disabled_bg="#1f1e1b", disabled_text="#7a776f",
                   free_bg="#252320", free_text="#faf9f5",
                   rec_bg="#cc785c", rec_text="#ffffff"),
    },
}


def _build_services_extra_css(theme: str, dark: bool) -> str:
    """Theme-aware QSS for the Services tab widgets.

    These widgets (section headers, setup/manage action, separators and status
    badges) are styled in component_services.py via cssClass selectors so they
    follow the active theme in both light and dark mode.
    """
    palette = _SERVICES_TOKENS.get(theme, _SERVICES_TOKENS["vibrant"])[bool(dark)]
    return f'''
        /* Services tab — category section header */
        QToolButton[cssClass="sectionToggle"] {{
            text-align: left;
            font-weight: bold;
            font-size: 14px;
            border: none;
            border-radius: {palette['radius']}px;
            padding: 10px 14px;
            background: {palette['sec_bg']};
            color: {palette['sec_text']};
        }}
        QToolButton[cssClass="sectionToggle"]:hover {{
            background: {palette['sec_hover']};
        }}
        /* Services tab — setup / manage action */
        QPushButton[cssClass="setupAction"] {{
            background: {palette['setup_bg']};
            color: {palette['setup_text']};
            border: 1px solid {palette['setup_border']};
            border-radius: {palette['radius_sm']}px;
            padding: 2px 10px;
            font-weight: 700;
        }}
        QPushButton[cssClass="setupAction"]:hover {{
            background: {palette['setup_hover']};
        }}
        /* Services tab — separators */
        QFrame[cssClass="serviceSeparator"] {{
            border: none;
            border-bottom: 1px solid {palette['hairline']};
        }}
        /* Services tab — status badges */
        QLabel[cssClass="statusBadgeReady"] {{
            background: {palette['ready_bg']};
            color: {palette['ready_text']};
            border-radius: 10px;
            padding: 2px 10px;
            font-size: 10px;
            font-weight: 600;
        }}
        QLabel[cssClass="statusBadgeSetup"] {{
            background: {palette['setup_bg']};
            color: {palette['setup_text']};
            border-radius: 10px;
            padding: 2px 10px;
            font-size: 10px;
            font-weight: 600;
        }}
        QLabel[cssClass="statusBadgeDisabled"] {{
            background: {palette['disabled_bg']};
            color: {palette['disabled_text']};
            border-radius: 10px;
            padding: 2px 10px;
            font-size: 10px;
            font-weight: 600;
        }}
        QLabel[cssClass="statusBadgeFree"] {{
            background: {palette['free_bg']};
            color: {palette['free_text']};
            border-radius: 10px;
            padding: 2px 10px;
            font-size: 10px;
            font-weight: 600;
        }}
        QLabel[cssClass="statusBadgeRecommended"] {{
            background: {palette['rec_bg']};
            color: {palette['rec_text']};
            border-radius: 10px;
            padding: 2px 10px;
            font-size: 10px;
            font-weight: 600;
        }}
    '''



# ── Theme engine ─────────────────────────────────────────────────────────────
# Every theme is a palette (colours, per mode) plus a metrics table (radii,
# padding, font weights).  One shared QSS skeleton renders all of them, so a
# rule only has to be written once and can never drift between themes.
#
#   vibrant  indigo accents on tinted cards - the default look
#   ollama   monochrome, hairline cards, pill-shaped inputs
#   nintendo hard red accent, small radii, chunky weights
#   apple    Apple HIG greys, Action Blue CTA, generous 18px radii
#   binance  dark trading-terminal surfaces with the yellow accent
#   clay     warm paper canvas with a pink brand accent
#   claude   cream canvas + coral CTAs (Anthropic design system)
#
# Colours are keyed by role, not by widget: ``card`` feeds the card, group box
# and combo popup; ``primary`` feeds the selected tab, TOC and primary CTA.

_THEME_METRICS: dict[str, dict[str, str]] = {
    "vibrant": dict(
        radius_card="16px", radius_sidebar="16px", radius_group="16px", radius_service="16px",
        radius_pane="16px", radius_tab="14px", radius_chip="12px", radius_toc="14px",
        radius_toggle="12px", radius_input="10px", radius_scroll="16px", radius_scroll_inner="16px",
        radius_button="12px", card_margin="6px", group_margin="24px", group_padding="18px",
        group_title_left="14px", group_title_padding="4px 10px", pad_tab="12px 20px", tab_margin="8px",
        pad_chip="6px 16px", pad_toc="14px 16px", pad_toggle="10px 18px", toggle_margin="6px",
        pad_input="10px 14px", pad_button="10px 18px", w_group_title="800", w_tab="bold",
        w_tab_selected="800", w_chip="800", w_toc="600", w_toc_active="800",
        w_toggle="bold", w_button="bold", w_primary="800",
    ),
    "ollama": dict(
        radius_card="12px", radius_sidebar="12px", radius_group="12px", radius_service="12px",
        radius_pane="12px", radius_tab="9999px", radius_chip="9999px", radius_toc="9999px",
        radius_toggle="9999px", radius_input="9999px", radius_scroll="12px", radius_scroll_inner="12px",
        radius_button="9999px", card_margin="6px", group_margin="24px", group_padding="18px",
        group_title_left="14px", group_title_padding="4px 10px", pad_tab="12px 20px", tab_margin="8px",
        pad_chip="6px 16px", pad_toc="14px 16px", pad_toggle="10px 18px", toggle_margin="6px",
        pad_input="10px 16px", pad_button="10px 20px", w_group_title="600", w_tab="500",
        w_tab_selected="600", w_chip="600", w_toc="500", w_toc_active="600",
        w_toggle="500", w_button="500", w_primary="600",
    ),
    "nintendo": dict(
        radius_card="10px", radius_sidebar="6px", radius_group="10px", radius_service="6px",
        radius_pane="6px", radius_tab="4px", radius_chip="9999px", radius_toc="4px",
        radius_toggle="6px", radius_input="6px", radius_scroll="10px", radius_scroll_inner="10px",
        radius_button="6px", card_margin="6px", group_margin="24px", group_padding="18px",
        group_title_left="14px", group_title_padding="4px 10px", pad_tab="12px 18px", tab_margin="6px",
        pad_chip="6px 16px", pad_toc="14px 16px", pad_toggle="10px 18px", toggle_margin="6px",
        pad_input="10px 16px", pad_button="10px 20px", w_group_title="700", w_tab="700",
        w_tab_selected="800", w_chip="700", w_toc="600", w_toc_active="800",
        w_toggle="600", w_button="600", w_primary="800",
    ),
    "apple": dict(
        radius_card="18px", radius_sidebar="18px", radius_group="18px", radius_service="14px",
        radius_pane="18px", radius_tab="11px", radius_chip="9999px", radius_toc="11px",
        radius_toggle="9999px", radius_input="11px", radius_scroll="18px", radius_scroll_inner="18px",
        radius_button="9999px", card_margin="6px", group_margin="24px", group_padding="18px",
        group_title_left="14px", group_title_padding="4px 10px", pad_tab="12px 20px", tab_margin="8px",
        pad_chip="6px 16px", pad_toc="14px 16px", pad_toggle="10px 18px", toggle_margin="6px",
        pad_input="10px 16px", pad_button="10px 20px", w_group_title="600", w_tab="500",
        w_tab_selected="600", w_chip="600", w_toc="500", w_toc_active="600",
        w_toggle="500", w_button="500", w_primary="600",
    ),
    "binance": dict(
        radius_card="10px", radius_sidebar="10px", radius_group="10px", radius_service="8px",
        radius_pane="10px", radius_tab="9999px", radius_chip="9999px", radius_toc="9999px",
        radius_toggle="9999px", radius_input="8px", radius_scroll="10px", radius_scroll_inner="10px",
        radius_button="9999px", card_margin="6px", group_margin="24px", group_padding="18px",
        group_title_left="14px", group_title_padding="4px 10px", pad_tab="12px 20px", tab_margin="8px",
        pad_chip="6px 16px", pad_toc="14px 16px", pad_toggle="10px 18px", toggle_margin="6px",
        pad_input="10px 16px", pad_button="10px 20px", w_group_title="600", w_tab="500",
        w_tab_selected="700", w_chip="600", w_toc="500", w_toc_active="700",
        w_toggle="500", w_button="500", w_primary="700",
    ),
    "clay": dict(
        radius_card="18px", radius_sidebar="18px", radius_group="18px", radius_service="12px",
        radius_pane="18px", radius_tab="9999px", radius_chip="9999px", radius_toc="9999px",
        radius_toggle="9999px", radius_input="12px", radius_scroll="18px", radius_scroll_inner="18px",
        radius_button="9999px", card_margin="6px", group_margin="24px", group_padding="18px",
        group_title_left="14px", group_title_padding="4px 10px", pad_tab="12px 20px", tab_margin="8px",
        pad_chip="6px 16px", pad_toc="14px 16px", pad_toggle="10px 18px", toggle_margin="6px",
        pad_input="10px 16px", pad_button="10px 20px", w_group_title="700", w_tab="500",
        w_tab_selected="700", w_chip="600", w_toc="500", w_toc_active="700",
        w_toggle="500", w_button="500", w_primary="700",
    ),
    "claude": dict(
        radius_card="14px", radius_sidebar="14px", radius_group="14px", radius_service="10px",
        radius_pane="14px", radius_tab="9999px", radius_chip="9999px", radius_toc="9999px",
        radius_toggle="9999px", radius_input="10px", radius_scroll="14px", radius_scroll_inner="14px",
        radius_button="9999px", card_margin="6px", group_margin="24px", group_padding="18px",
        group_title_left="14px", group_title_padding="4px 10px", pad_tab="12px 20px", tab_margin="8px",
        pad_chip="6px 16px", pad_toc="14px 16px", pad_toggle="10px 18px", toggle_margin="6px",
        pad_input="10px 16px", pad_button="10px 20px", w_group_title="600", w_tab="500",
        w_tab_selected="700", w_chip="600", w_toc="500", w_toc_active="700",
        w_toggle="500", w_button="500", w_primary="700",
    ),
}

_THEME_TOKENS: dict[str, dict[bool, dict[str, str]]] = {
    "vibrant": {
        False: dict(
            canvas="#EEF2FF", canvas_soft="#F8FAFC", card="#FFFFFF", card_alt="#FFFFFF",
            group_bg="#FFFFFF", ink="#0F172A", mute="#475569", toc_text="#475569",
            tab_hover_bg="rgba(255, 255, 255, 255)", toc_hover_bg="#E2E8F0", tab_bg_unselected="rgba(255, 255, 255, 120)", tab_text_unselected="#334155",
            primary="#6366F1", tab_text_selected="#FFFFFF", input_bg="#F8FAFC", input_focus="#FFFFFF",
            selection_bg="#6366F1", on_primary="", btn_bg_secondary="rgba(255, 255, 255, 180)", btn_text_sec="#0F172A",
            btn_hover_sec="rgba(255, 255, 255, 255)", btn_bg_primary="#4F46E5", btn_text_pri="#FFFFFF", btn_hover_pri="#4338CA",
            svc_enabled_bg="#D1FAE5", svc_enabled_text="#064E3B", svc_disabled_bg="#FFE4E6", svc_disabled_text="#881337",
            pastel_bg="#D1FAE5", pastel_fg="#064E3B", b_card="border: none;", b_sidebar="",
            b_group="border: none;", b_service="border: none;", b_pane="border: 1px solid transparent;", b_chip="border: none;",
            b_toggle="border: none;", b_input="border: none;", b_focus="", b_combo="border: none;",
            b_button="border: none;", b_primary="", b_primary_hover="", sel_color="",
            hairline="#000000",
        ),
        True: dict(
            canvas="#0B1120", canvas_soft="#0B1120", card="#1E293B", card_alt="#0F172A",
            group_bg="#1E293B", ink="#F8FAFC", mute="#94A3B8", toc_text="#94A3B8",
            tab_hover_bg="rgba(51, 65, 85, 255)", toc_hover_bg="#1E293B", tab_bg_unselected="rgba(15, 23, 42, 150)", tab_text_unselected="#E2E8F0",
            primary="#00E1D9", tab_text_selected="#0F172A", input_bg="#0B1120", input_focus="#1E293B",
            selection_bg="#00E1D9", on_primary="", btn_bg_secondary="rgba(30, 41, 59, 200)", btn_text_sec="#F8FAFC",
            btn_hover_sec="rgba(51, 65, 85, 255)", btn_bg_primary="#8B5CF6", btn_text_pri="#FFFFFF", btn_hover_pri="#7C3AED",
            svc_enabled_bg="#064E3B", svc_enabled_text="#D1FAE5", svc_disabled_bg="#4C0519", svc_disabled_text="#FFE4E6",
            pastel_bg="#064E3B", pastel_fg="#6EE7B7", b_card="border: none;", b_sidebar="",
            b_group="border: none;", b_service="border: none;", b_pane="border: 1px solid transparent;", b_chip="border: none;",
            b_toggle="border: none;", b_input="border: none;", b_focus="", b_combo="border: none;",
            b_button="border: none;", b_primary="", b_primary_hover="", sel_color="",
            hairline="#000000",
        ),
    },
    "ollama": {
        False: dict(
            canvas="#ffffff", canvas_soft="#ffffff", card="#ffffff", card_alt="#fafafa",
            group_bg="#ffffff", ink="#000000", mute="#737373", toc_text="#525252",
            tab_hover_bg="#fafafa", toc_hover_bg="#fafafa", tab_bg_unselected="rgba(0, 0, 0, 0)", tab_text_unselected="#525252",
            primary="#000000", tab_text_selected="#ffffff", input_bg="#fafafa", input_focus="#ffffff",
            selection_bg="#000000", on_primary="#ffffff", btn_bg_secondary="#ffffff", btn_text_sec="#000000",
            btn_hover_sec="#fafafa", btn_bg_primary="#000000", btn_text_pri="#ffffff", btn_hover_pri="#090909",
            svc_enabled_bg="#ffffff", svc_enabled_text="#000000", svc_disabled_bg="#fafafa", svc_disabled_text="#a3a3a3",
            pastel_bg="#fafafa", pastel_fg="#000000", b_card="border: 1px solid {hairline};", b_sidebar="border: 1px solid {hairline};",
            b_group="border: 1px solid {hairline};", b_service="border: 1px solid {hairline};", b_pane="border: 1px solid {hairline};", b_chip="border: 1px solid {hairline};",
            b_toggle="border: 1px solid #d4d4d4;", b_input="border: 1px solid {hairline};", b_focus="border: 1px solid {primary};", b_combo="border: 1px solid {hairline};",
            b_button="border: 1px solid #d4d4d4;", b_primary="border: 1px solid {primary};", b_primary_hover="border: 1px solid #090909;", sel_color="selection-color: #ffffff;",
            hairline="#e5e5e5",
        ),
        True: dict(
            canvas="#0a0a0a", canvas_soft="#0a0a0a", card="#171717", card_alt="#171717",
            group_bg="#171717", ink="#ffffff", mute="#a3a3a3", toc_text="#d4d4d4",
            tab_hover_bg="#171717", toc_hover_bg="#171717", tab_bg_unselected="rgba(255, 255, 255, 0)", tab_text_unselected="#a3a3a3",
            primary="#ffffff", tab_text_selected="#000000", input_bg="#171717", input_focus="#0a0a0a",
            selection_bg="#ffffff", on_primary="#000000", btn_bg_secondary="#171717", btn_text_sec="#ffffff",
            btn_hover_sec="#1f1f1f", btn_bg_primary="#ffffff", btn_text_pri="#000000", btn_hover_pri="#e5e5e5",
            svc_enabled_bg="#171717", svc_enabled_text="#ffffff", svc_disabled_bg="#0a0a0a", svc_disabled_text="#737373",
            pastel_bg="#171717", pastel_fg="#ffffff", b_card="border: 1px solid {hairline};", b_sidebar="border: 1px solid {hairline};",
            b_group="border: 1px solid {hairline};", b_service="border: 1px solid {hairline};", b_pane="border: 1px solid {hairline};", b_chip="border: 1px solid {hairline};",
            b_toggle="border: 1px solid #404040;", b_input="border: 1px solid {hairline};", b_focus="border: 1px solid {primary};", b_combo="border: 1px solid {hairline};",
            b_button="border: 1px solid #404040;", b_primary="border: 1px solid {primary};", b_primary_hover="border: 1px solid #e5e5e5;", sel_color="selection-color: #000000;",
            hairline="#2a2a2a",
        ),
    },
    "nintendo": {
        False: dict(
            canvas="#7a8aba", canvas_soft="#9fbee7", card="#ffffff", card_alt="#dedede",
            group_bg="#ffffff", ink="#21242e", mute="#60619c", toc_text="#3d4f97",
            tab_hover_bg="#9fbee7", toc_hover_bg="#9fbee7", tab_bg_unselected="rgba(0, 0, 0, 0)", tab_text_unselected="#ffffffe0",
            primary="#e60012", tab_text_selected="#ffffff", input_bg="#ffffff", input_focus="#ffffff",
            selection_bg="#e60012", on_primary="#ffffff", btn_bg_secondary="#21242e", btn_text_sec="#ffffff",
            btn_hover_sec="#3d4f97", btn_bg_primary="#ecab37", btn_text_pri="#21242e", btn_hover_pri="#e48600",
            svc_enabled_bg="#e7edf7", svc_enabled_text="#21242e", svc_disabled_bg="#dedede", svc_disabled_text="#60619c",
            pastel_bg="#9fbee7", pastel_fg="#21242e", b_card="border: 1px solid {hairline};", b_sidebar="border: 1px solid {hairline};",
            b_group="border: 1px solid {hairline};", b_service="border: 1px solid {hairline};", b_pane="border: 1px solid {hairline};", b_chip="border: 1px solid {hairline};",
            b_toggle="border: 1px solid {hairline};", b_input="border: 1px solid {hairline};", b_focus="border: 1px solid {primary};", b_combo="border: 1px solid {hairline};",
            b_button="border: 1px solid {hairline};", b_primary="border: 1px solid #ecab37;", b_primary_hover="border: 1px solid #e48600;", sel_color="selection-color: #ffffff;",
            hairline="#5a5f8c",
        ),
        True: dict(
            canvas="#20242f", canvas_soft="#2a3247", card="#2a3247", card_alt="#333c54",
            group_bg="#2a3247", ink="#f2f4fa", mute="#9aa3c4", toc_text="#b8c4f0",
            tab_hover_bg="#333c54", toc_hover_bg="#333c54", tab_bg_unselected="rgba(255, 255, 255, 0)", tab_text_unselected="#cfd6ff",
            primary="#e60012", tab_text_selected="#ffffff", input_bg="#262b3b", input_focus="#2a3247",
            selection_bg="#e60012", on_primary="#ffffff", btn_bg_secondary="#21242e", btn_text_sec="#ffffff",
            btn_hover_sec="#3d4f97", btn_bg_primary="#ecab37", btn_text_pri="#21242e", btn_hover_pri="#e48600",
            svc_enabled_bg="#333c54", svc_enabled_text="#ffffff", svc_disabled_bg="#21242e", svc_disabled_text="#9aa3c4",
            pastel_bg="#333c54", pastel_fg="#ffffff", b_card="border: 1px solid {hairline};", b_sidebar="border: 1px solid {hairline};",
            b_group="border: 1px solid {hairline};", b_service="border: 1px solid {hairline};", b_pane="border: 1px solid {hairline};", b_chip="border: 1px solid {hairline};",
            b_toggle="border: 1px solid {hairline};", b_input="border: 1px solid {hairline};", b_focus="border: 1px solid {primary};", b_combo="border: 1px solid {hairline};",
            b_button="border: 1px solid {hairline};", b_primary="border: 1px solid #ecab37;", b_primary_hover="border: 1px solid #e48600;", sel_color="selection-color: #ffffff;",
            hairline="#4a5380",
        ),
    },
    "apple": {
        False: dict(
            canvas="#f5f5f7", canvas_soft="#ffffff", card="#ffffff", card_alt="#ffffff",
            group_bg="#fafafc", ink="#1d1d1f", mute="#7a7a7a", toc_text="#333333",
            tab_hover_bg="#f5f5f7", toc_hover_bg="#f5f5f7", tab_bg_unselected="rgba(0, 0, 0, 0)", tab_text_unselected="#333333",
            primary="#0066cc", tab_text_selected="#ffffff", input_bg="#ffffff", input_focus="#ffffff",
            selection_bg="#0066cc", on_primary="#ffffff", btn_bg_secondary="#ffffff", btn_text_sec="#1d1d1f",
            btn_hover_sec="#f5f5f7", btn_bg_primary="#0066cc", btn_text_pri="#ffffff", btn_hover_pri="#0071e3",
            svc_enabled_bg="#f5f5f7", svc_enabled_text="#1d1d1f", svc_disabled_bg="#fafafc", svc_disabled_text="#7a7a7a",
            pastel_bg="#f5f5f7", pastel_fg="#1d1d1f", b_card="border: 1px solid {hairline};", b_sidebar="border: 1px solid {hairline};",
            b_group="border: 1px solid {hairline};", b_service="border: 1px solid {hairline};", b_pane="border: 1px solid {hairline};", b_chip="border: 1px solid {hairline};",
            b_toggle="border: 1px solid #d2d2d7;", b_input="border: 1px solid {hairline};", b_focus="border: 1px solid {primary};", b_combo="border: 1px solid {hairline};",
            b_button="border: 1px solid #d2d2d7;", b_primary="border: 1px solid {primary};", b_primary_hover="border: 1px solid #0071e3;", sel_color="selection-color: #ffffff;",
            hairline="#e0e0e0",
        ),
        True: dict(
            canvas="#1d1d1f", canvas_soft="#000000", card="#1d1d1f", card_alt="#000000",
            group_bg="#1d1d1f", ink="#ffffff", mute="#7a7a7a", toc_text="#e0e0e0",
            tab_hover_bg="#2a2a2c", toc_hover_bg="#2a2a2c", tab_bg_unselected="rgba(255, 255, 255, 0)", tab_text_unselected="#a1a1a6",
            primary="#2997ff", tab_text_selected="#000000", input_bg="#1d1d1f", input_focus="#1d1d1f",
            selection_bg="#2997ff", on_primary="#000000", btn_bg_secondary="#1d1d1f", btn_text_sec="#ffffff",
            btn_hover_sec="#333333", btn_bg_primary="#2997ff", btn_text_pri="#000000", btn_hover_pri="#2997ff",
            svc_enabled_bg="#2a2a2c", svc_enabled_text="#ffffff", svc_disabled_bg="#1d1d1f", svc_disabled_text="#7a7a7a",
            pastel_bg="#2a2a2c", pastel_fg="#ffffff", b_card="border: 1px solid {hairline};", b_sidebar="border: 1px solid {hairline};",
            b_group="border: 1px solid {hairline};", b_service="border: 1px solid {hairline};", b_pane="border: 1px solid {hairline};", b_chip="border: 1px solid {hairline};",
            b_toggle="border: 1px solid #48484a;", b_input="border: 1px solid {hairline};", b_focus="border: 1px solid {primary};", b_combo="border: 1px solid {hairline};",
            b_button="border: 1px solid #48484a;", b_primary="border: 1px solid {primary};", b_primary_hover="border: 1px solid {primary};", sel_color="selection-color: #000000;",
            hairline="#333333",
        ),
    },
    "binance": {
        False: dict(
            canvas="#ffffff", canvas_soft="#ffffff", card="#ffffff", card_alt="#fafafa",
            group_bg="#ffffff", ink="#181a20", mute="#707a8a", toc_text="#707a8a",
            tab_hover_bg="#f5f5f5", toc_hover_bg="#f5f5f5", tab_bg_unselected="rgba(0, 0, 0, 0)", tab_text_unselected="#707a8a",
            primary="#fcd535", tab_text_selected="#181a20", input_bg="#fafafa", input_focus="#ffffff",
            selection_bg="#fcd535", on_primary="#181a20", btn_bg_secondary="#fafafa", btn_text_sec="#181a20",
            btn_hover_sec="#f0f0f0", btn_bg_primary="#fcd535", btn_text_pri="#181a20", btn_hover_pri="#f0b90b",
            svc_enabled_bg="#fafafa", svc_enabled_text="#181a20", svc_disabled_bg="#f5f5f5", svc_disabled_text="#707a8a",
            pastel_bg="#fafafa", pastel_fg="#181a20", b_card="border: 1px solid {hairline};", b_sidebar="border: 1px solid {hairline};",
            b_group="border: 1px solid {hairline};", b_service="border: 1px solid {hairline};", b_pane="border: 1px solid {hairline};", b_chip="border: 1px solid {hairline};",
            b_toggle="border: 1px solid {hairline};", b_input="border: 1px solid {hairline};", b_focus="border: 1px solid {primary};", b_combo="border: 1px solid {hairline};",
            b_button="border: 1px solid {hairline};", b_primary="border: 1px solid {primary};", b_primary_hover="border: 1px solid #f0b90b;", sel_color="selection-color: #181a20;",
            hairline="#eaecef",
        ),
        True: dict(
            canvas="#0b0e11", canvas_soft="#0b0e11", card="#1e2329", card_alt="#2b3139",
            group_bg="#1e2329", ink="#eaecef", mute="#707a8a", toc_text="#707a8a",
            tab_hover_bg="#1e2329", toc_hover_bg="#1e2329", tab_bg_unselected="rgba(255, 255, 255, 0)", tab_text_unselected="#848e9c",
            primary="#fcd535", tab_text_selected="#181a20", input_bg="#181a20", input_focus="#1e2329",
            selection_bg="#fcd535", on_primary="#181a20", btn_bg_secondary="#2b3139", btn_text_sec="#eaecef",
            btn_hover_sec="#3b424b", btn_bg_primary="#fcd535", btn_text_pri="#181a20", btn_hover_pri="#f0b90b",
            svc_enabled_bg="#1e2329", svc_enabled_text="#eaecef", svc_disabled_bg="#15171c", svc_disabled_text="#707a8a",
            pastel_bg="#1e2329", pastel_fg="#eaecef", b_card="border: 1px solid {hairline};", b_sidebar="border: 1px solid {hairline};",
            b_group="border: 1px solid {hairline};", b_service="border: 1px solid {hairline};", b_pane="border: 1px solid {hairline};", b_chip="border: 1px solid {hairline};",
            b_toggle="border: 1px solid {hairline};", b_input="border: 1px solid {hairline};", b_focus="border: 1px solid {primary};", b_combo="border: 1px solid {hairline};",
            b_button="border: 1px solid {hairline};", b_primary="border: 1px solid {primary};", b_primary_hover="border: 1px solid #f0b90b;", sel_color="selection-color: #181a20;",
            hairline="#2b3139",
        ),
    },
    "clay": {
        False: dict(
            canvas="#fffaf0", canvas_soft="#faf5e8", card="#f5f0e0", card_alt="#ebe6d6",
            group_bg="#f5f0e0", ink="#0a0a0a", mute="#6a6a6a", toc_text="#6a6a6a",
            tab_hover_bg="#faf5e8", toc_hover_bg="#faf5e8", tab_bg_unselected="rgba(0, 0, 0, 0)", tab_text_unselected="#6a6a6a",
            primary="#ff4d8b", tab_text_selected="#ffffff", input_bg="#ffffff", input_focus="#ffffff",
            selection_bg="#ff4d8b", on_primary="#ffffff", btn_bg_secondary="#ffffff", btn_text_sec="#0a0a0a",
            btn_hover_sec="#faf5e8", btn_bg_primary="#0a0a0a", btn_text_pri="#ffffff", btn_hover_pri="#1f1f1f",
            svc_enabled_bg="#faf5e8", svc_enabled_text="#0a0a0a", svc_disabled_bg="#f5f0e0", svc_disabled_text="#9a9a9a",
            pastel_bg="#f5f0e0", pastel_fg="#0a0a0a", b_card="border: 1px solid {hairline};", b_sidebar="border: 1px solid {hairline};",
            b_group="border: 1px solid {hairline};", b_service="border: 1px solid {hairline};", b_pane="border: 1px solid {hairline};", b_chip="border: 1px solid {hairline};",
            b_toggle="border: 1px solid {hairline};", b_input="border: 1px solid {hairline};", b_focus="border: 1px solid {primary};", b_combo="border: 1px solid {hairline};",
            b_button="border: 1px solid {hairline};", b_primary="border: 1px solid {ink};", b_primary_hover="border: 1px solid #1f1f1f;", sel_color="selection-color: #ffffff;",
            hairline="#e5e5e5",
        ),
        True: dict(
            canvas="#0a1a1a", canvas_soft="#142222", card="#1a2a2a", card_alt="#223333",
            group_bg="#1a2a2a", ink="#f5f0e0", mute="#9a9a9a", toc_text="#9a9a9a",
            tab_hover_bg="#1a2a2a", toc_hover_bg="#1a2a2a", tab_bg_unselected="rgba(255, 255, 255, 0)", tab_text_unselected="#a0b0a0",
            primary="#ff4d8b", tab_text_selected="#ffffff", input_bg="#1a2a2a", input_focus="#223333",
            selection_bg="#ff4d8b", on_primary="#ffffff", btn_bg_secondary="#1a2a2a", btn_text_sec="#f5f0e0",
            btn_hover_sec="#223333", btn_bg_primary="#ff4d8b", btn_text_pri="#ffffff", btn_hover_pri="#e84175",
            svc_enabled_bg="#223333", svc_enabled_text="#f5f0e0", svc_disabled_bg="#142222", svc_disabled_text="#7a7a7a",
            pastel_bg="#223333", pastel_fg="#f5f0e0", b_card="border: 1px solid {hairline};", b_sidebar="border: 1px solid {hairline};",
            b_group="border: 1px solid {hairline};", b_service="border: 1px solid {hairline};", b_pane="border: 1px solid {hairline};", b_chip="border: 1px solid {hairline};",
            b_toggle="border: 1px solid {hairline};", b_input="border: 1px solid {hairline};", b_focus="border: 1px solid {primary};", b_combo="border: 1px solid {hairline};",
            b_button="border: 1px solid {hairline};", b_primary="border: 1px solid {primary};", b_primary_hover="border: 1px solid #e84175;", sel_color="selection-color: #ffffff;",
            hairline="#2a3a3a",
        ),
    },
    "claude": {
        False: dict(
            canvas="#faf9f5", canvas_soft="#f5f0e8", card="#efe9de", card_alt="#e8e0d2",
            group_bg="#efe9de", ink="#141413", mute="#6c6a64", toc_text="#6c6a64",
            tab_hover_bg="#f5f0e8", toc_hover_bg="#f5f0e8", tab_bg_unselected="rgba(0, 0, 0, 0)", tab_text_unselected="#6c6a64",
            primary="#cc785c", tab_text_selected="#ffffff", input_bg="#ffffff", input_focus="#ffffff",
            selection_bg="#cc785c", on_primary="#ffffff", btn_bg_secondary="#ffffff", btn_text_sec="#141413",
            btn_hover_sec="#f5f0e8", btn_bg_primary="#cc785c", btn_text_pri="#ffffff", btn_hover_pri="#a9583e",
            svc_enabled_bg="#f5f0e8", svc_enabled_text="#141413", svc_disabled_bg="#efe9de", svc_disabled_text="#8e8b82",
            pastel_bg="#efe9de", pastel_fg="#141413", b_card="border: 1px solid {hairline};", b_sidebar="border: 1px solid {hairline};",
            b_group="border: 1px solid {hairline};", b_service="border: 1px solid {hairline};", b_pane="border: 1px solid {hairline};", b_chip="border: 1px solid {hairline};",
            b_toggle="border: 1px solid {hairline};", b_input="border: 1px solid {hairline};", b_focus="border: 1px solid {primary};", b_combo="border: 1px solid {hairline};",
            b_button="border: 1px solid {hairline};", b_primary="border: 1px solid {primary};", b_primary_hover="border: 1px solid #a9583e;", sel_color="selection-color: #ffffff;",
            hairline="#e6dfd8",
        ),
        True: dict(
            canvas="#181715", canvas_soft="#1f1e1b", card="#252320", card_alt="#2b2926",
            group_bg="#252320", ink="#faf9f5", mute="#9a978f", toc_text="#9a978f",
            tab_hover_bg="#252320", toc_hover_bg="#252320", tab_bg_unselected="rgba(255, 255, 255, 0)", tab_text_unselected="#a5a199",
            primary="#cc785c", tab_text_selected="#ffffff", input_bg="#252320", input_focus="#2b2926",
            selection_bg="#cc785c", on_primary="#141413", btn_bg_secondary="#252320", btn_text_sec="#faf9f5",
            btn_hover_sec="#2b2926", btn_bg_primary="#cc785c", btn_text_pri="#141413", btn_hover_pri="#d98a6f",
            svc_enabled_bg="#2b2926", svc_enabled_text="#faf9f5", svc_disabled_bg="#1f1e1b", svc_disabled_text="#7a776f",
            pastel_bg="#2b2926", pastel_fg="#faf9f5", b_card="border: 1px solid {hairline};", b_sidebar="border: 1px solid {hairline};",
            b_group="border: 1px solid {hairline};", b_service="border: 1px solid {hairline};", b_pane="border: 1px solid {hairline};", b_chip="border: 1px solid {hairline};",
            b_toggle="border: 1px solid {hairline};", b_input="border: 1px solid {hairline};", b_focus="border: 1px solid #d98a6f;", b_combo="border: 1px solid {hairline};",
            b_button="border: 1px solid {hairline};", b_primary="border: 1px solid {primary};", b_primary_hover="border: 1px solid #d98a6f;", sel_color="selection-color: #141413;",
            hairline="#33302c",
        ),
    },
}

_VIBRANT_PASTELS: dict[bool, dict[str, tuple[str, str]]] = {
    False: {
        "Emerald": ("#D1FAE5", "#064E3B"),
        "Blue": ("#DBEAFE", "#1E3A8A"),
        "Rose": ("#FCE7F3", "#831843"),
        "Amber": ("#FEF3C7", "#78350F"),
        "Purple": ("#EDE9FE", "#4C1D95"),
    },
    True: {
        "Emerald": ("#064E3B", "#6EE7B7"),
        "Blue": ("#1E3A8A", "#93C5FD"),
        "Rose": ("#831843", "#F9A8D4"),
        "Amber": ("#78350F", "#FCD34D"),
        "Purple": ("#4C1D95", "#C4B5FD"),
    },
}

_THEME_TEMPLATE = Template(r"""
        QDialog {
            background: $canvas;
        }

        QLabel {
            color: $ink;
        }
        QLabel[cssClass="helperText"] {
            color: $mute;
            font-size: 11px;
        }

        QFrame[cssClass="vibrantCard"] {
            background: $card;
            $b_card
            border-radius: $radius_card;
            margin-top: $card_margin;
        }

        QWidget[cssClass="sidebarPanel"] {
            background: $card_alt;
            $b_sidebar
            border-radius: $radius_sidebar;
        }

        QGroupBox {
            background: $group_bg;
            $b_group
            border-radius: $radius_group;
            margin-top: $group_margin;
            padding: $group_padding;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top left;
            left: $group_title_left;
            padding: $group_title_padding;
            color: $ink;
            font-weight: $w_group_title;
        }

        QFrame[cssClass="serviceCard"] {
            border-radius: $radius_service;
            $b_service
        }
        QFrame[cssClass="serviceCard"][cardState="enabled"] {
            background: $svc_enabled_bg;
        }
        QFrame[cssClass="serviceCard"][cardState="enabled"] QLabel {
            color: $svc_enabled_text;
        }
        QFrame[cssClass="serviceCard"][cardState="disabled"] {
            background: $svc_disabled_bg;
        }
        QFrame[cssClass="serviceCard"][cardState="disabled"] QLabel {
            color: $svc_disabled_text;
        }

        QCheckBox, QRadioButton {
            color: $ink;
            spacing: 8px;
            background: transparent;
        }

        QTabWidget::pane {
            $b_pane
            background: $canvas_soft;
            border-radius: $radius_pane;
        }
        QTabBar::tab {
            background: $tab_bg_unselected;
            color: $tab_text_unselected;
            padding: $pad_tab;
            margin-right: $tab_margin;
            border-radius: $radius_tab;
            font-size: 13px;
            font-weight: $w_tab;
        }
        QTabBar::tab:selected {
            background: $primary;
            color: $tab_text_selected;
            font-size: 13px;
            font-weight: $w_tab_selected;
        }
        QTabBar::tab:hover:!selected {
            background: $tab_hover_bg;
        }

$pastel_block

        QPushButton[cssClass="tocButtonInactive"] {
            text-align: left;
            padding: $pad_toc;
            border: none;
            font-weight: $w_toc;
            font-size: 13px;
            border-radius: $radius_toc;
            color: $toc_text;
            background: transparent;
        }
        QPushButton[cssClass="tocButtonInactive"]:hover {
            background: $toc_hover_bg!important;
            color: $ink!important;
        }
        QPushButton[cssClass="tocButtonActive"] {
            text-align: left;
            padding: $pad_toc;
            border: none;
            font-weight: $w_toc_active;
            font-size: 13px;
            border-radius: $radius_toc;
            color: $tab_text_selected;
            background: $primary;
        }
        QPushButton[cssClass="tocButtonActive"]:hover {
            background: $primary!important;
            color: $tab_text_selected!important;
        }
        QToolButton[cssClass="collapsibleToggle"] {
            text-align: left;
            padding: $pad_toggle;
            border-radius: $radius_toggle;
            background: $btn_bg_secondary;
            $b_toggle
            color: $btn_text_sec;
            font-weight: $w_toggle;
            margin-top: $toggle_margin;
        }
        QToolButton[cssClass="collapsibleToggle"]:hover {
            background: $btn_hover_sec;
        }

        QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {
            padding: $pad_input;
            $b_input
            border-radius: $radius_input;
            background: $input_bg;
            color: $ink;
        }
        QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus {
            background: $input_focus;
            $b_focus
        }
        QComboBox QAbstractItemView {
            background: $card;
            $b_combo
            color: $ink;
            selection-background-color: $selection_bg;
            $sel_color
        }

        QScrollArea {
            background: transparent;
            border: none;
            border-radius: $radius_scroll;
        }
        QScrollArea > QWidget > QWidget {
            background: transparent;
            border-radius: $radius_scroll_inner;
        }

        QPushButton {
            padding: $pad_button;
            border-radius: $radius_button;
            background: $btn_bg_secondary;
            $b_button
            color: $btn_text_sec;
            font-weight: $w_button;
        }
        QPushButton:hover {
            background: $btn_hover_sec;
        }
        QPushButton[cssClass="primaryButton"] {
            background: $btn_bg_primary;
            color: $btn_text_pri;
            $b_primary
            font-weight: $w_primary;
        }
        QPushButton[cssClass="primaryButton"]:hover {
            background: $btn_hover_pri;
            $b_primary_hover
        }
    """)

# Flat "chip" buttons: the six non-vibrant themes render every pastel class as
# the same neutral chip.  Vibrant keeps five distinct pastel colours and is
# rendered by _build_vibrant_pastel_block() instead.
_PASTEL_CHIP_TEMPLATE = Template(r"""        QPushButton[cssClass="btnPastelEmerald"],
        QPushButton[cssClass="btnPastelBlue"],
        QPushButton[cssClass="btnPastelRose"],
        QPushButton[cssClass="btnPastelAmber"],
        QPushButton[cssClass="btnPastelPurple"] {
            padding: $pad_chip;
            border-radius: $radius_chip;
            $b_chip
            background: $pastel_bg;
            color: $pastel_fg;
            font-weight: $w_chip;
        }
        QPushButton[cssClass="btnPastelEmerald"]:hover,
        QPushButton[cssClass="btnPastelBlue"]:hover,
        QPushButton[cssClass="btnPastelRose"]:hover,
        QPushButton[cssClass="btnPastelAmber"]:hover,
        QPushButton[cssClass="btnPastelPurple"]:hover {
            background: $btn_hover_sec;
        }""")

_VIBRANT_PASTEL_TEMPLATE = Template(r"""        QPushButton[cssClass="btnPastel$name"] {
            padding: $pad_chip;
            border-radius: $radius_chip;
            $b_chip
            background: $bg;
            color: $fg;
            font-weight: $w_chip;
        }
        QPushButton[cssClass="btnPastel$name"]:hover {
            background: $fg;
            color: $bg;
        }""")


def _theme_tokens(theme: str, dark: bool) -> dict[str, str]:
    """Merge one theme's palette with its metrics and resolve token references.

    Colour values may reference another token (``border: 1px solid {hairline}``)
    so a theme states its hairline colour once instead of on every rule.
    """
    table = dict(_THEME_TOKENS[theme][bool(dark)])
    table.update(_THEME_METRICS[theme])
    for key, value in table.items():
        if "{" in value:
            table[key] = value.format(**table)
    return table


def _build_vibrant_pastel_block(dark: bool, tokens: dict[str, str]) -> str:
    """Vibrant's five pastel button classes invert their colours on hover."""
    blocks = []
    for name, (bg, fg) in _VIBRANT_PASTELS[bool(dark)].items():
        blocks.append(
            _VIBRANT_PASTEL_TEMPLATE.substitute(dict(tokens, name=name, bg=bg, fg=fg))
        )
    return "\n".join(blocks)


def _build_theme_stylesheet(theme: str, dark: bool) -> str:
    """Render the shared QSS skeleton for ``theme`` in light or dark mode."""
    tokens = _theme_tokens(theme, dark)
    if theme == "vibrant":
        tokens["pastel_block"] = _build_vibrant_pastel_block(dark, tokens)
    else:
        tokens["pastel_block"] = _PASTEL_CHIP_TEMPLATE.substitute(tokens)
    return _THEME_TEMPLATE.substitute(tokens)


def _build_vibrant_stylesheet(dark: bool) -> str:
    """Vibrant: indigo accents on tinted cards - the add-on's default look."""
    return _build_theme_stylesheet("vibrant", dark)


def _build_ollama_stylesheet(dark: bool) -> str:
    """Ollama: monochrome, hairline-bordered cards with pill inputs."""
    return _build_theme_stylesheet("ollama", dark)


def _build_nintendo_stylesheet(dark: bool) -> str:
    """Nintendo: hard red accent, small radii, chunky weights."""
    return _build_theme_stylesheet("nintendo", dark)


def _build_apple_stylesheet(dark: bool) -> str:
    """Apple: Apple HIG greys, Action Blue CTA, generous 18px radii."""
    return _build_theme_stylesheet("apple", dark)


def _build_binance_stylesheet(dark: bool) -> str:
    """Binance: dark trading-terminal surfaces with the yellow accent."""
    return _build_theme_stylesheet("binance", dark)


def _build_clay_stylesheet(dark: bool) -> str:
    """Clay: warm paper canvas with a pink brand accent."""
    return _build_theme_stylesheet("clay", dark)


def _build_claude_stylesheet(dark: bool) -> str:
    """Claude: warm cream canvas and coral CTAs from the Anthropic design system."""
    return _build_theme_stylesheet("claude", dark)
