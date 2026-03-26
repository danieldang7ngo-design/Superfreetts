import sys
import aqt.qt
from typing import Any

from . import component_common
from . import component_shortcuts
from . import component_errorhandling
from . import config_models
from . import constants
from . import errors
from . import gui_utils
from . import logging_utils
from . import i18n
logger = logging_utils.get_child_logger(__name__)

class ComponentPreferences(component_common.ConfigComponentBase):
    def __init__(self, hypertts: Any, dialog: Any) -> None:
        """
        Initialize preferences component.
        
        Args:
            hypertts: Main HyperTTS instance
            dialog: Parent dialog widget
        """
        self.hypertts = hypertts
        self.dialog = dialog
        self.model = config_models.Preferences()
        self.shortcuts = component_shortcuts.Shortcuts(self.hypertts, self.dialog, self.shortcuts_updated)
        self.error_handling = component_errorhandling.ErrorHandling(self.hypertts, self.dialog, self.error_handling_updated)

        # Nút lưu / hủy
        self.save_button = aqt.qt.QPushButton()
        self.cancel_button = aqt.qt.QPushButton()

        # Chọn ngôn ngữ giao diện
        self.language_combobox = aqt.qt.QComboBox()

        # Cache retention setting
        self.cache_retention_checkbox = aqt.qt.QCheckBox()
        self.cache_retention_checkbox.setToolTip("")
        self.cache_retention_spinbox = aqt.qt.QSpinBox()
        self.cache_retention_spinbox.setMinimum(1)
        self.cache_retention_spinbox.setMaximum(365)
        self.cache_helper_label = aqt.qt.QLabel()
        self.cache_helper_label.setWordWrap(True)

        self.batch_concurrency_spinbox = aqt.qt.QSpinBox()
        self.batch_concurrency_spinbox.setMinimum(1)
        self.batch_concurrency_spinbox.setMaximum(16)
        self.batch_concurrency_spinbox.setToolTip("Number of concurrent threads for batch processing. Keep at 4 for auto-detect CPU cores, or set custom value (1-20)")
        self.perf_helper_label = aqt.qt.QLabel()
        self.perf_helper_label.setWordWrap(True)
        
        # Note: Per-service concurrency workers are now configured in each service's Advanced settings

        # UI layout for preferences
        
        # Sherpa Max Processes
        self.sherpa_max_processes_spinbox = aqt.qt.QSpinBox()
        self.sherpa_max_processes_spinbox.setMinimum(1)
        self.sherpa_max_processes_spinbox.setMaximum(16)

    def load_model(self, model):
        logger.info('load_model')
        self.model = model
        self.shortcuts.load_model(self.model.keyboard_shortcuts)
        self.error_handling.load_model(self.model.error_handling)
        # thiết lập ngôn ngữ ban đầu cho combobox
        current_lang = getattr(self.model, "ui_language", "en") or "en"
        # ánh xạ giá trị nội bộ -> index
        language_values = ["en", "vi"]
        if current_lang in language_values:
            self.language_combobox.setCurrentIndex(language_values.index(current_lang))
        else:
            self.language_combobox.setCurrentIndex(0)

        # load cache retention days
        self.cache_retention_checkbox.setChecked(self.model.cache_enabled)
        self.cache_retention_spinbox.setValue(self.model.cache_retention_days)
        self.cache_retention_spinbox.setEnabled(self.model.cache_enabled)
        # load batch concurrency
        self.batch_concurrency_spinbox.setValue(self.model.batch_concurrency)
        
        self.sherpa_max_processes_spinbox.setValue(self.model.sherpa_max_processes)

    def get_model(self):
        return self.model

    def shortcuts_updated(self, model):
        self.model.keyboard_shortcuts = model
        self.model_part_updated_common()

    def error_handling_updated(self, model):
        self.model.error_handling = model
        self.model_part_updated_common()

    def model_part_updated_common(self):
        self.save_button.setEnabled(True)
        self.save_button.setStyleSheet(self.hypertts.anki_utils.get_green_stylesheet())        

    def draw(self, layout, show_action_buttons=True):
        lang = self.hypertts.get_ui_language()
        vlayout = aqt.qt.QVBoxLayout()
        vlayout.setContentsMargins(16, 12, 16, 8)
        vlayout.setSpacing(10)

        groupbox_style = (
            "QGroupBox { margin-top: 10px; padding-top: 14px; padding-left: 8px; padding-right: 8px; padding-bottom: 8px; font-weight: 700; border: none; border-radius: 14px; background-color: #EEF4FB; color: #123A63; }"
            "QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 6px; color: #123A63; }"
        )

        # nhóm chọn ngôn ngữ giao diện
        self.language_groupbox = aqt.qt.QGroupBox(i18n.get_text("preferences_group_language_title", lang))
        self.language_groupbox.setStyleSheet(groupbox_style)
        language_layout = aqt.qt.QVBoxLayout()
        language_layout.setContentsMargins(10, 10, 10, 8)
        language_layout.setSpacing(8)
        self.language_label = aqt.qt.QLabel(i18n.get_text("preferences_label_interface_language", lang))
        language_layout.addWidget(self.language_label)

        # đổ dữ liệu cho combobox ngôn ngữ
        self.language_combobox.clear()
        self.language_combobox.addItem(i18n.get_text("preferences_option_language_en", lang), "en")
        self.language_combobox.addItem(i18n.get_text("preferences_option_language_vi", lang), "vi")
        self.language_combobox.setToolTip(i18n.get_text("preferences_language_tooltip", lang))
        self.language_combobox.setMinimumHeight(32)
        language_layout.addWidget(self.language_combobox)
        self.language_groupbox.setLayout(language_layout)
        vlayout.addWidget(self.language_groupbox)

        # Cache Management Group
        self.cache_groupbox = aqt.qt.QGroupBox(i18n.get_text("preferences_group_cache_title", lang))
        self.cache_groupbox.setStyleSheet(groupbox_style)
        cache_layout = aqt.qt.QVBoxLayout()
        cache_layout.setContentsMargins(10, 10, 10, 8)
        cache_layout.setSpacing(8)
        self.cache_label = aqt.qt.QLabel(i18n.get_text("preferences_cache_label", lang))
        self.cache_label.setMinimumHeight(24)
        
        h_cache_layout = aqt.qt.QHBoxLayout()
        self.cache_retention_checkbox.setMinimumHeight(24)
        h_cache_layout.addWidget(self.cache_retention_checkbox)
        h_cache_layout.addWidget(self.cache_label)
        self.cache_retention_spinbox.setMinimumHeight(30)
        h_cache_layout.addWidget(self.cache_retention_spinbox)
        h_cache_layout.addStretch()
        
        cache_layout.addLayout(h_cache_layout)
        self.cache_helper_label.setStyleSheet("color: palette(mid);")
        cache_layout.addWidget(self.cache_helper_label)
        self.cache_groupbox.setLayout(cache_layout)
        vlayout.addWidget(self.cache_groupbox)

        # Performance Group
        self.perf_groupbox = aqt.qt.QGroupBox(i18n.get_text("preferences_group_performance_title", lang))
        self.perf_groupbox.setStyleSheet(groupbox_style)
        perf_layout = aqt.qt.QVBoxLayout()
        perf_layout.setContentsMargins(10, 10, 10, 8)
        perf_layout.setSpacing(12)
        self.perf_label = aqt.qt.QLabel(i18n.get_text("preferences_batch_concurrency_label", lang))
        self.perf_label.setMinimumHeight(24)
        self.perf_label.setMinimumWidth(220)
        self.perf_label.setWordWrap(False)
        
        h_perf_layout = aqt.qt.QHBoxLayout()
        h_perf_layout.setContentsMargins(0, 0, 0, 0)
        h_perf_layout.setSpacing(12)
        h_perf_layout.addWidget(self.perf_label)
        self.batch_concurrency_spinbox.setMinimumHeight(30)
        self.batch_concurrency_spinbox.setFixedWidth(72)
        h_perf_layout.addWidget(self.batch_concurrency_spinbox)
        h_perf_layout.addStretch()

        perf_layout.addLayout(h_perf_layout)

        # Pool limit
        h_sherpa_pool_layout = aqt.qt.QHBoxLayout()
        h_sherpa_pool_layout.setContentsMargins(0, 0, 0, 0)
        h_sherpa_pool_layout.setSpacing(12)
        self.sherpa_pool_label = aqt.qt.QLabel(i18n.get_text("pref_label_sherpa_max_processes", lang))
        self.sherpa_pool_label.setMinimumHeight(24)
        self.sherpa_pool_label.setMinimumWidth(220)
        self.sherpa_pool_label.setWordWrap(False)
        h_sherpa_pool_layout.addWidget(self.sherpa_pool_label)
        self.sherpa_max_processes_spinbox.setMinimumHeight(30)
        self.sherpa_max_processes_spinbox.setFixedWidth(72)
        h_sherpa_pool_layout.addWidget(self.sherpa_max_processes_spinbox)
        h_sherpa_pool_layout.addStretch()
        perf_layout.addLayout(h_sherpa_pool_layout)
        self.perf_helper_label.setStyleSheet("color: palette(mid);")
        perf_layout.addWidget(self.perf_helper_label)

        self.perf_groupbox.setLayout(perf_layout)
        vlayout.addWidget(self.perf_groupbox)

        vlayout.addStretch()
        layout.addLayout(vlayout)

        # preferences tabs
        # ====================

        self.tabs = aqt.qt.QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setStyleSheet(
            "QTabWidget::pane { border: none; background: #F8FBFF; border-radius: 12px; }"
            "QTabBar::tab { padding: 8px 14px; border: none; border-radius: 10px; background: #DCEBFA; color: #244166; }"
            "QTabBar::tab:selected { font-weight: 700; background: #FFF4C8; color: #133B5C; }"
        )
        self.tabs.addTab(self.shortcuts.draw(), i18n.get_text("preferences_tab_shortcuts", lang))
        self.tabs.addTab(self.error_handling.draw(), i18n.get_text("preferences_tab_error_handling", lang))
        vlayout.addSpacing(4)
        layout.addWidget(self.tabs)
 
        # Finally, set initial label text
        self.update_ui_labels(lang)

        # configure bottom action buttons (standalone dialogs only)
        self.save_button.setEnabled(False)
        gui_utils.configure_primary_button(self.save_button, min_height=40, min_width=100, font_size=11)
        gui_utils.configure_secondary_button(self.cancel_button, min_height=40, min_width=100, font_size=11)

        # sự kiện thay đổi ngôn ngữ
        self.language_combobox.currentIndexChanged.connect(self.language_changed)
        self.cache_retention_checkbox.stateChanged.connect(self.cache_enabled_changed)
        self.cache_retention_spinbox.valueChanged.connect(self.cache_retention_changed)
        self.batch_concurrency_spinbox.valueChanged.connect(self.batch_concurrency_changed)
        self.sherpa_max_processes_spinbox.valueChanged.connect(self.sherpa_max_processes_changed)
        
        if show_action_buttons:
            hlayout = aqt.qt.QHBoxLayout()
            logo_footer = aqt.qt.QWidget()
            logo_footer.setLayout(gui_utils.get_superfreetss_label_header(self.hypertts.superfreetss_pro_enabled()))
            hlayout.addWidget(logo_footer)
            hlayout.addStretch()
            hlayout.addWidget(self.save_button)
            hlayout.addWidget(self.cancel_button)
            self.save_button.pressed.connect(self.save_button_pressed)
            self.cancel_button.pressed.connect(self.cancel_button_pressed)
            layout.addLayout(hlayout)

    def language_changed(self, index: int) -> None:
        """
        Handle language change event.
        
        Args:
            index: Index of selected language in combobox
            
        Returns:
            None
        """
        data_lang = self.language_combobox.itemData(index)
        if data_lang is None:
            # fallback an toàn
            data_lang = "en"
        self.model.ui_language = data_lang
        self.update_ui_labels(data_lang)
        self.model_part_updated_common()

    def update_ui_labels(self, lang: str):
        self.language_groupbox.setTitle(i18n.get_text("preferences_group_language_title", lang))
        self.language_label.setText(i18n.get_text("preferences_label_interface_language", lang))
        self.language_combobox.setToolTip(i18n.get_text("preferences_language_tooltip", lang))
        
        # update dropdown items
        self.language_combobox.blockSignals(True)
        self.language_combobox.setItemText(0, i18n.get_text("preferences_option_language_en", lang))
        self.language_combobox.setItemText(1, i18n.get_text("preferences_option_language_vi", lang))
        self.language_combobox.blockSignals(False)

        self.cache_groupbox.setTitle(i18n.get_text("preferences_group_cache_title", lang))
        self.cache_label.setText(i18n.get_text("preferences_cache_label", lang))
        self.cache_retention_checkbox.setText(i18n.get_text("preferences_cache_enable", lang))
        self.cache_retention_checkbox.setToolTip(i18n.get_text("preferences_cache_tooltip", lang))
        self.cache_helper_label.setText(i18n.get_text("preferences_cache_helper", lang))
        
        self.perf_groupbox.setTitle(i18n.get_text("preferences_group_performance_title", lang))
        self.perf_label.setText(i18n.get_text("preferences_batch_concurrency_label", lang))
        self.batch_concurrency_spinbox.setToolTip(i18n.get_text("preferences_batch_concurrency_tooltip", lang))
        self.perf_helper_label.setText(i18n.get_text("preferences_performance_helper", lang))
        
        self.sherpa_pool_label.setText(i18n.get_text("pref_label_sherpa_max_processes", lang))
        self.sherpa_max_processes_spinbox.setToolTip(i18n.get_text("pref_tooltip_sherpa_max_processes", lang))
        
        self.tabs.setTabText(0, i18n.get_text("preferences_tab_shortcuts", lang))
        self.tabs.setTabText(1, i18n.get_text("preferences_tab_error_handling", lang))
        
        self.shortcuts.update_ui_labels(lang)
        self.error_handling.update_ui_labels(lang)
        
        self.save_button.setText(i18n.get_text("button_apply", lang))
        self.cancel_button.setText(i18n.get_text("button_cancel", lang))

    def cache_enabled_changed(self, state: int) -> None:
        """
        Handle cache enable/disable checkbox change.
        
        Args:
            state: Qt CheckState value
            
        Returns:
            None
        """
        enabled = (state == aqt.qt.Qt.CheckState.Checked.value)
        self.model.cache_enabled = enabled
        self.cache_retention_spinbox.setEnabled(enabled)
        self.model_part_updated_common()

    def cache_retention_changed(self, value: int) -> None:
        """
        Handle cache retention days spinbox change.
        
        Args:
            value: Number of days to retain cache files
            
        Returns:
            None
        """
        self.model.cache_retention_days = value
        self.model_part_updated_common()

    def batch_concurrency_changed(self, value: int) -> None:
        """
        Handle batch concurrency threads spinbox change.
        
        Args:
            value: Number of concurrent threads to use
            
        Returns:
            None
        """
        self.model.batch_concurrency = value
        self.model_part_updated_common()

    def sherpa_max_processes_changed(self, value: int) -> None:
        """Handle Sherpa max processes spinbox change."""
        self.model.sherpa_max_processes = value
        self.model_part_updated_common()

    def save_button_pressed(self) -> None:
        """Handle save button click."""
        with self.hypertts.error_manager.get_single_action_context('Saving Preferences'):
            self.hypertts.save_preferences(self.model)
            self.dialog.close()

    def cancel_button_pressed(self) -> None:
        """Handle cancel button click."""
        self.dialog.close()    