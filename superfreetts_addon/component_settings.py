"""
Settings dialog for Super Free TTS.

Layout:
  - Sidebar navigation: Services, Preferences, Changes, Donation, About
  - Shared Save/Cancel buttons
"""

import aqt.qt

from . import component_about
from . import component_changes
from . import component_donation
from . import component_preferences
from . import component_services
from . import config_models
from . import gui_utils
from . import i18n
from . import logging_utils

logger = logging_utils.get_child_logger(__name__)


class SettingsDialog(aqt.qt.QDialog):
    def __init__(self, hypertts, initial_tab=0, parent=None):
        super().__init__(parent)
        self.hypertts = hypertts
        self.initial_tab = 0 if initial_tab not in (0, 1, 2, 3, 4) else initial_tab
        self._saved_once = False
        self._initial_snapshot = None

        self.setUpdatesEnabled(False)
        self.setWindowFlag(aqt.qt.Qt.WindowType.WindowMinMaxButtonsHint, True)

        self.services_page = component_services.ServicesPage(hypertts, self)
        self.services_page.load_model(hypertts.get_configuration())

        self.preferences_page = component_preferences.PreferencesPage(hypertts, self)
        self.preferences_page.load_model(hypertts.get_preferences())

        self.changes_page = component_changes.ChangesPage(hypertts)
        self.donation_page = component_donation.DonationPage(hypertts)
        self.about_page = component_about.AboutPage(hypertts)

        self._page_buttons = []
        self._page_built = set()

        self.setupUi()
        self.setStyleSheet(self._get_stylesheet())
        self.setUpdatesEnabled(True)
        aqt.qt.QTimer.singleShot(0, self._deferred_snapshot)

    def _get_stylesheet(self):
        from . import gui_utils
        return gui_utils.get_dynamic_stylesheet()

    def _deferred_snapshot(self):
        self._initial_snapshot = self._capture_snapshot()

    def setupUi(self):
        lang = self.hypertts.get_ui_language()
        self.setWindowTitle(i18n.get_text("unified_settings_title", lang))
        self.setMinimumSize(420, 360)
        self.resize(900, 700)

        main_layout = aqt.qt.QVBoxLayout(self)
        main_layout.setContentsMargins(16, 14, 16, 14)
        main_layout.setSpacing(12)

        body_layout = aqt.qt.QHBoxLayout()
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(14)

        sidebar = aqt.qt.QWidget()
        sidebar.setProperty("cssClass", "sidebarPanel")
        sidebar_layout = aqt.qt.QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(8, 18, 8, 8)
        sidebar_layout.setSpacing(8)

        self.btn_services = self._create_sidebar_button(i18n.get_text("tab_services", lang))
        self.btn_preferences = self._create_sidebar_button(i18n.get_text("tab_preferences", lang))
        self.btn_changes = self._create_sidebar_button(i18n.get_text("tab_changes", lang))
        self.btn_donation = self._create_sidebar_button(i18n.get_text("tab_donation", lang))
        self.btn_about = self._create_sidebar_button(i18n.get_text("tab_about", lang))
        self._page_buttons = [
            self.btn_services,
            self.btn_preferences,
            self.btn_changes,
            self.btn_donation,
            self.btn_about,
        ]

        for btn in self._page_buttons:
            sidebar_layout.addWidget(btn)
        sidebar_layout.addStretch()

        sidebar_scroll = aqt.qt.QScrollArea()
        sidebar_scroll.setWidgetResizable(True)
        sidebar_scroll.setFrameShape(aqt.qt.QFrame.Shape.NoFrame)
        sidebar_scroll.setHorizontalScrollBarPolicy(aqt.qt.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        sidebar_scroll.setWidget(sidebar)
        sidebar_scroll.setMinimumWidth(130)
        sidebar_scroll.setMaximumWidth(220)

        body_layout.addWidget(sidebar_scroll)

        self.pages = aqt.qt.QStackedWidget()
        self.services_container = self._build_page_container()
        self.preferences_container = self._build_page_container()
        self.changes_container = self._build_page_container()
        self.donation_container = self._build_page_container()
        self.about_container = self._build_page_container()
        self.pages.addWidget(self.services_container)
        self.pages.addWidget(self.preferences_container)
        self.pages.addWidget(self.changes_container)
        self.pages.addWidget(self.donation_container)
        self.pages.addWidget(self.about_container)
        body_layout.addWidget(self.pages, 1)

        main_layout.addLayout(body_layout, 1)

        button_layout = aqt.qt.QHBoxLayout()
        button_layout.setContentsMargins(0, 6, 0, 0)
        button_layout.setSpacing(8)

        self.save_button = aqt.qt.QPushButton(i18n.get_text("button_save", lang))
        self.cancel_button = aqt.qt.QPushButton(i18n.get_text("button_cancel", lang))
        gui_utils.configure_primary_button(self.save_button, min_height=40, min_width=100, font_size=11)
        gui_utils.configure_secondary_button(self.cancel_button, min_height=40, min_width=100, font_size=11)
        self.save_button.clicked.connect(self.save_and_close)
        self.cancel_button.clicked.connect(self.cancel)
        button_layout.addStretch()
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        main_layout.addLayout(button_layout)

        self.btn_services.clicked.connect(lambda: self.switch_page(0))
        self.btn_preferences.clicked.connect(lambda: self.switch_page(1))
        self.btn_changes.clicked.connect(lambda: self.switch_page(2))
        self.btn_donation.clicked.connect(lambda: self.switch_page(3))
        self.btn_about.clicked.connect(lambda: self.switch_page(4))

        self.switch_page(self.initial_tab)

    def _build_page_container(self):
        container = aqt.qt.QWidget()
        layout = aqt.qt.QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        return container

    def _create_sidebar_button(self, label):
        btn = aqt.qt.QPushButton(label)
        btn.setFlat(True)
        btn.setCursor(aqt.qt.Qt.CursorShape.PointingHandCursor)
        btn.setProperty("cssClass", "tocButtonInactive")
        return btn

    def _mark_active_button(self, active_index):
        for index, btn in enumerate(self._page_buttons):
            btn.setProperty("cssClass", "tocButtonActive" if index == active_index else "tocButtonInactive")
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    def _ensure_page_built(self, index):
        if index in self._page_built:
            return
        if index == 0:
            self.services_page.draw(self.services_container.layout(), show_action_buttons=False)
        elif index == 1:
            self.preferences_page.draw(self.preferences_container.layout(), show_action_buttons=False)
        elif index == 2:
            self.changes_page.draw(self.changes_container.layout())
        elif index == 3:
            self.donation_page.draw(self.donation_container.layout())
        elif index == 4:
            self.about_page.draw(self.about_container.layout())
        self._page_built.add(index)

    def switch_page(self, index):
        self._ensure_page_built(index)
        self.pages.setCurrentIndex(index)
        self._mark_active_button(index)

    def _capture_snapshot(self):
        config = self.services_page.get_model()
        prefs = self.preferences_page.get_model()
        return (
            config_models.serialize_configuration(config),
            config_models.serialize_preferences(prefs),
        )

    def _has_unsaved_changes(self):
        if self._initial_snapshot is None:
            return False
        return self._capture_snapshot() != self._initial_snapshot

    def _confirm_discard_if_needed(self):
        lang = self.hypertts.get_ui_language()
        if not self._has_unsaved_changes():
            return True
        return self.hypertts.anki_utils.ask_user(
            i18n.get_text("unified_settings_discard_changes", lang),
            self,
        )

    def save_and_close(self):
        try:
            lang = self.hypertts.get_ui_language()
            logger.info("Settings dialog: saving configuration and preferences...")

            self.hypertts.save_configuration(self.services_page.get_model())
            self.hypertts.save_preferences(self.preferences_page.get_model())

            self._saved_once = True
            self._initial_snapshot = self._capture_snapshot()
            self.hypertts.anki_utils.tooltip_message(
                i18n.get_text("unified_settings_saved_toast", lang)
            )
            self.accept()
        except Exception as e:
            logger.error(f"Error saving settings: {e}", exc_info=True)
            self.hypertts.anki_utils.critical_message(
                f"Error saving settings:\n{str(e)}",
                self,
            )

    def cancel(self):
        if self._confirm_discard_if_needed():
            self.reject()

    def closeEvent(self, event):
        if self._confirm_discard_if_needed():
            event.accept()
        else:
            event.ignore()


# Backward-compatible alias for older imports.
UnifiedSettingsDialog = SettingsDialog
