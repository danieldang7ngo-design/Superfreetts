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
from . import i18n
from . import logging_utils

logger = logging_utils.get_child_logger(__name__)


class UnifiedSettingsDialog(aqt.qt.QDialog):
    """
    One unified dialog for Services Configuration + Preferences.
    Uses QTabWidget to separate the two sections.
    """
    
    def __init__(self, hypertts, parent=None):
        super().__init__(parent)
        self.hypertts = hypertts
        self.setWindowFlag(aqt.qt.Qt.WindowType.WindowMinMaxButtonsHint, True)
        self.setStyleSheet(self._get_stylesheet())
        
        # Create components (will lazily create UI when loaded into layout)
        self.config_component = component_configuration.Configuration(hypertts, self)
        self.config_component.load_model(hypertts.get_configuration())
        
        self.prefs_component = component_preferences.ComponentPreferences(hypertts, self)
        self.prefs_component.load_model(hypertts.get_preferences())
        
        self.setupUi()
        self.connectSignals()
    
    def _get_stylesheet(self):
        """Return stylesheet for unified dialog (reuse from constants if available)."""
        from . import constants
        return constants.STYLESHEET_DIALOG
    
    def setupUi(self):
        """Build dialog layout with tabbed interface."""
        lang = self.hypertts.get_ui_language()
        self.setWindowTitle(i18n.get_text("unified_settings_title", lang))
        self.setMinimumSize(500, 400)
        
        # Main layout
        main_layout = aqt.qt.QVBoxLayout(self)
        
        # Tab widget
        self.tabs = aqt.qt.QTabWidget()
        
        # Tab 1: Services (Configuration)
        services_container = aqt.qt.QWidget()
        services_layout = aqt.qt.QVBoxLayout(services_container)
        self.config_component.draw(services_layout)
        self.tabs.addTab(services_container, i18n.get_text("tab_services", lang))
        
        # Tab 2: Preferences
        prefs_container = aqt.qt.QWidget()
        prefs_layout = aqt.qt.QVBoxLayout(prefs_container)
        self.prefs_component.draw(prefs_layout)
        self.tabs.addTab(prefs_container, i18n.get_text("tab_preferences", lang))
        
        main_layout.addWidget(self.tabs)
        
        # Button layout
        button_layout = aqt.qt.QHBoxLayout()
        
        save_button = aqt.qt.QPushButton(i18n.get_text("button_save", lang))
        cancel_button = aqt.qt.QPushButton(i18n.get_text("button_cancel", lang))
        
        save_button.clicked.connect(self.save_and_close)
        cancel_button.clicked.connect(self.cancel)
        
        button_layout.addStretch()
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        
        main_layout.addLayout(button_layout)
        
        self.setLayout(main_layout)
        self.resize(550, 600)
    
    def connectSignals(self):
        """Hook language change to update tab/dialog labels."""
        pass  # Will be wired via profile_did_open hook in gui.py if needed
    
    def save_and_close(self):
        """
        Save both Configuration and Preferences to disk and reconfigure services.
        """
        try:
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
            
            # Reconfigure service manager once after both saves
            self.hypertts.service_manager.configure(config)
            logger.info("Service manager reconfigured.")
            
            self.accept()
        except Exception as e:
            logger.error(f"Error saving settings: {e}", exc_info=True)
            self.hypertts.anki_utils.critical_message(
                f"Error saving settings:\n{str(e)}", 
                self
            )
    
    def cancel(self):
        """Close without saving."""
        self.reject()
    
    def close(self):
        """Override close to ensure rejection if user closes via window button."""
        self.reject()
