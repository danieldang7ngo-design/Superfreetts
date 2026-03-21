"""
Unified Settings Dialog for Super Free TTS
Consolidates Configuration (Services) + Preferences into one resizable dialog with tabs.

Structure:
  - UnifiedSettingsDialog (QDialog)
    - Tab 1: Services (from component_configuration)
    - Tab 2: Preferences (from component_preferences)
    - Shared Save/Cancel buttons
"""

import aqt.qt
from . import component_configuration
from . import component_preferences
from . import config_models
from . import i18n
from . import logging_utils

logger = logging_utils.get_child_logger(__name__)


class UnifiedSettingsDialog(aqt.qt.QDialog):
    """
    One unified dialog for Services Configuration + Preferences.
    Uses QTabWidget to separate the two sections.
    """
    
    def __init__(self, hypertts, initial_tab=0, parent=None):
        super().__init__(parent)
        self.hypertts = hypertts
        self.initial_tab = 0 if initial_tab not in (0, 1) else initial_tab
        self._saved_once = False
        self.setWindowFlag(aqt.qt.Qt.WindowType.WindowMinMaxButtonsHint, True)
        self.setStyleSheet(self._get_stylesheet())
        
        # Create components (will lazily create UI when loaded into layout)
        self.config_component = component_configuration.Configuration(hypertts, self)
        self.config_component.load_model(hypertts.get_configuration())
        
        self.prefs_component = component_preferences.ComponentPreferences(hypertts, self)
        self.prefs_component.load_model(hypertts.get_preferences())
        
        self._services_built = False
        self._preferences_built = False
        self.setupUi()
        self.connectSignals()
        self._initial_snapshot = self._capture_snapshot()
    
    def _get_stylesheet(self):
        """Return stylesheet for unified dialog (reuse from constants if available)."""
        from . import constants
        return constants.STYLESHEET_DIALOG
    
    def setupUi(self):
        """Build dialog layout with tabbed interface."""
        lang = self.hypertts.get_ui_language()
        self.setWindowTitle(i18n.get_text("unified_settings_title", lang))
        self.setMinimumSize(500, 400)

        # Reduce visible relayout/flicker while composing heavy UI.
        self.setUpdatesEnabled(False)

        # Main layout
        main_layout = aqt.qt.QVBoxLayout(self)
        main_layout.setContentsMargins(16, 14, 16, 14)
        main_layout.setSpacing(12)
        
        # Tab widget
        self.tabs = aqt.qt.QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setStyleSheet(
            "QTabBar::tab { padding: 8px 14px; }"
            "QTabBar::tab:selected { font-weight: 600; }"
        )

        # Tab containers are created immediately, but content is lazy-built on demand.
        self.services_container = aqt.qt.QWidget()
        self.services_layout = aqt.qt.QVBoxLayout(self.services_container)
        self.services_layout.setContentsMargins(0, 2, 0, 0)
        self.services_layout.setSpacing(0)
        self.tabs.addTab(self.services_container, i18n.get_text("tab_services", lang))

        self.prefs_container = aqt.qt.QWidget()
        self.prefs_layout = aqt.qt.QVBoxLayout(self.prefs_container)
        self.prefs_layout.setContentsMargins(0, 2, 0, 0)
        self.prefs_layout.setSpacing(0)
        self.tabs.addTab(self.prefs_container, i18n.get_text("tab_preferences", lang))

        # Build only the initial tab to keep open-time responsive.
        if self.initial_tab == 0:
            self._build_services_tab()
        else:
            self._build_preferences_tab()

        self.tabs.setCurrentIndex(self.initial_tab)
        
        main_layout.addWidget(self.tabs)
        
        # Button layout
        button_layout = aqt.qt.QHBoxLayout()
        button_layout.setContentsMargins(0, 6, 0, 0)
        button_layout.setSpacing(8)
        
        save_button = aqt.qt.QPushButton(i18n.get_text("button_save", lang))
        cancel_button = aqt.qt.QPushButton(i18n.get_text("button_cancel", lang))
        
        save_button.clicked.connect(self.save_and_close)
        cancel_button.clicked.connect(self.cancel)
        
        button_layout.addStretch()
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        
        main_layout.addLayout(button_layout)

        self.setUpdatesEnabled(True)
        self.resize(550, 600)

    def _build_services_tab(self):
        if self._services_built:
            return
        self.config_component.draw(self.services_layout, show_action_buttons=False)
        self._services_built = True

    def _build_preferences_tab(self):
        if self._preferences_built:
            return
        self.prefs_component.draw(self.prefs_layout, show_action_buttons=False)
        self._preferences_built = True
    
    def connectSignals(self):
        """Hook language change to update tab/dialog labels."""
        self.tabs.currentChanged.connect(self._on_tab_changed)

    def _on_tab_changed(self, index):
        # Lazy-build the non-initial tab only when user actually visits it.
        if index == 0:
            self._build_services_tab()
        elif index == 1:
            self._build_preferences_tab()

    def _capture_snapshot(self):
        """Capture current config/preferences snapshot for dirty-checking."""
        config = self.config_component.get_model() if hasattr(self.config_component, 'get_model') else self.config_component.model
        prefs = self.prefs_component.get_model() if hasattr(self.prefs_component, 'get_model') else self.prefs_component.model
        return (
            config_models.serialize_configuration(config),
            config_models.serialize_preferences(prefs),
        )

    def _has_unsaved_changes(self):
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
        """
        Save both Configuration and Preferences to disk and reconfigure services.
        """
        try:
            lang = self.hypertts.get_ui_language()
            logger.info("Unified settings: saving configuration and preferences...")
            
            # Get updated models from components
            config = self.config_component.get_model() if hasattr(self.config_component, 'get_model') else self.config_component.model
            prefs = self.prefs_component.get_model() if hasattr(self.prefs_component, 'get_model') else self.prefs_component.model
            
            # Save configuration (Services)
            self.hypertts.save_configuration(config)
            logger.info("Configuration saved.")
            
            # Save preferences
            self.hypertts.save_preferences(prefs)
            logger.info("Preferences saved.")

            # save_preferences() already triggers service manager reconfigure.
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
                self
            )
    
    def cancel(self):
        """Close without saving."""
        if self._confirm_discard_if_needed():
            self.reject()
    
    def closeEvent(self, event):
        """Intercept window-close to protect unsaved changes."""
        if self._confirm_discard_if_needed():
            event.accept()
        else:
            event.ignore()
