import aqt.qt
from . import config_models
from . import constants
from . import logging_utils
from . import constants_events
from . import gui_utils
from . import i18n
from .constants_events import Event, EventMode
from . import stats

logger = logging_utils.get_test_child_logger(__name__)

sc = stats.StatsContext(constants_events.EventContext.choose_easy_advanced)

# ── Card styling ──────────────────────────────────────────────────────
_CARD_BASE = f"""
    QFrame {{
        border: 2px solid palette(mid);
        border-radius: 10px;
        padding: 16px 20px;
        background-color: palette(window);
    }}
"""
_CARD_SELECTED = f"""
    QFrame {{
        border: 2px solid {constants.COLOR_ACCENT_TEAL};
        border-radius: 10px;
        padding: 16px 20px;
        background-color: palette(alternate-base);
    }}
"""


def _apply_card_style(frame: aqt.qt.QFrame, selected: bool):
    """Programmatic card highlight — avoids broken QSS property selectors."""
    frame.setStyleSheet(_CARD_SELECTED if selected else _CARD_BASE)


class ChooseEasyAdvancedDialog(aqt.qt.QDialog):
    """Dialog for choosing between Easy and Advanced modes"""
    def __init__(self, lang: str = "en"):
        super(aqt.qt.QDialog, self).__init__()
        self.lang = lang
        self.setStyleSheet(constants.STYLESHEET_DIALOG)
        self.chosen_mode = None
        self.setupUi()

    def setupUi(self):
        self.setWindowTitle(constants.TITLE_PREFIX + 'Choose Mode')
        self.setMinimumWidth(420)
        root = aqt.qt.QVBoxLayout()
        root.setSpacing(16)
        root.setContentsMargins(24, 24, 24, 20)

        # ── Title ──
        title = aqt.qt.QLabel(i18n.get_text("choose_mode_title", self.lang))
        title_font = title.font()
        title_font.setPointSize(15)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(aqt.qt.Qt.AlignmentFlag.AlignCenter)
        root.addWidget(title)

        subtitle = aqt.qt.QLabel(i18n.get_text("choose_mode_subtitle", self.lang))
        subtitle.setAlignment(aqt.qt.Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("color: palette(dark);")
        root.addWidget(subtitle)

        root.addSpacing(4)

        # ── Button group for mutual exclusion ──
        self.button_group = aqt.qt.QButtonGroup(self)

        # ── Easy mode card ──
        self.easy_frame = self._build_card(
            radio_text=i18n.get_text("choose_mode_easy_title", self.lang),
            description=i18n.get_text("choose_mode_easy_desc", self.lang),
            checked=True,
        )
        self.easy_radio = self.easy_frame.findChild(aqt.qt.QRadioButton)
        self.button_group.addButton(self.easy_radio)
        root.addWidget(self.easy_frame)

        # ── Advanced mode card ──
        self.advanced_frame = self._build_card(
            radio_text=i18n.get_text("choose_mode_advanced_title", self.lang),
            description=i18n.get_text("choose_mode_advanced_desc", self.lang),
            checked=False,
        )
        self.advanced_radio = self.advanced_frame.findChild(aqt.qt.QRadioButton)
        self.button_group.addButton(self.advanced_radio)
        root.addWidget(self.advanced_frame)

        # Wire up selection highlight
        self.easy_radio.toggled.connect(self._on_selection_changed)
        self._on_selection_changed()   # apply initial highlight

        root.addSpacing(4)

        # ── Footer note ──
        footer = aqt.qt.QLabel(i18n.get_text("choose_mode_footer", self.lang))
        footer.setWordWrap(True)
        footer.setAlignment(aqt.qt.Qt.AlignmentFlag.AlignCenter)
        footer.setStyleSheet("color: palette(dark); font-size: 11px; font-style: italic;")
        root.addWidget(footer)

        # ── OK / Cancel ──
        root.addStretch()
        self.button_box = aqt.qt.QDialogButtonBox(
            aqt.qt.QDialogButtonBox.StandardButton.Ok |
            aqt.qt.QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        root.addWidget(self.button_box)

        self.setLayout(root)

    # ── helpers ───────────────────────────────────────────────────────
    def _build_card(self, radio_text: str, description: str, checked: bool) -> aqt.qt.QFrame:
        frame = aqt.qt.QFrame()
        frame.setCursor(aqt.qt.Qt.CursorShape.PointingHandCursor)
        layout = aqt.qt.QHBoxLayout()
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(12)

        # Radio
        radio = aqt.qt.QRadioButton(radio_text)
        radio_font = radio.font()
        radio_font.setPointSize(12)
        radio_font.setBold(True)
        radio.setFont(radio_font)
        radio.setChecked(checked)
        layout.addWidget(radio, 0, aqt.qt.Qt.AlignmentFlag.AlignTop)

        # Description
        desc = aqt.qt.QLabel(description)
        desc.setWordWrap(True)
        desc.setStyleSheet("border: none; background: transparent; color: palette(text);")
        layout.addWidget(desc, 1)

        frame.setLayout(layout)

        # Click anywhere on card → toggle radio
        def card_click(event, r=radio):
            r.setChecked(True)
        frame.mousePressEvent = card_click

        return frame

    def _on_selection_changed(self):
        _apply_card_style(self.easy_frame, self.easy_radio.isChecked())
        _apply_card_style(self.advanced_frame, self.advanced_radio.isChecked())

    def accept(self):
        logger.debug('accept')
        if self.easy_radio.isChecked():
            self.chosen_mode = config_models.EasyAdvancedMode.EASY
        else:
            self.chosen_mode = config_models.EasyAdvancedMode.ADVANCED
        logger.debug(f'User selected mode: {self.chosen_mode}')
        super().accept()

@sc.event(Event.open)
def show_easy_advanced_dialog(hypertts) -> config_models.EasyAdvancedMode:
    """Show dialog to choose between Easy and Advanced modes
    Returns:
        EasyAdvancedMode enum value, or None if user cancelled
    """
    lang = hypertts.get_ui_language()
    dialog = ChooseEasyAdvancedDialog(lang=lang)
    hypertts.anki_utils.wait_for_dialog_input(dialog, constants.DIALOG_ID_CHDOOSE_EASY_ADVANCED)
    return dialog.chosen_mode

def ensure_easy_advanced_choice_made(hypertts) -> bool:
    """Ensure user has made a choice between Easy and Advanced modes.
    If not, show the dialog and save their choice."""

    # return True if we can proceed to the next step    

    configuration = hypertts.get_configuration()
    if configuration.user_choice_easy_advanced:
        return True  # can proceed to the next step

    logger.debug('user hasnt chosen easy/advanced mode yet')
    # User hasn't chosen yet, show dialog
    choice = show_easy_advanced_dialog(hypertts)
    if choice is not None:
        # Save their choice
        configuration.user_choice_easy_advanced = True
        hypertts.save_configuration(configuration)
        
        # Update mapping rules based on their choice
        mapping_rules = hypertts.load_mapping_rules()
        mapping_rules.use_easy_mode = (choice == config_models.EasyAdvancedMode.EASY)
        hypertts.save_mapping_rules(mapping_rules)

        if mapping_rules.use_easy_mode:
            sc.send_event(Event.choose, EventMode.easy_mode)
        else:
            sc.send_event(Event.choose, EventMode.advanced_mode)
        
        return True
                
    return False