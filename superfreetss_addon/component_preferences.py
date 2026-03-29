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
        
        self.batch_concurrency_help_label = aqt.qt.QLabel()
        self.batch_concurrency_help_label.setWordWrap(True)
        
        # Note: Per-service concurrency workers are now configured in each service's Advanced settings

        # UI layout for preferences
        
        # Audio output format
        self.audio_format_combobox = aqt.qt.QComboBox()

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

        # load audio format
        format_values = ["mp3", "wav", "ogg"]
        current_format = getattr(self.model, 'audio_format', 'mp3') or 'mp3'
        if current_format in format_values:
            self.audio_format_combobox.setCurrentIndex(format_values.index(current_format))
        else:
            self.audio_format_combobox.setCurrentIndex(0)

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
        self.save_button.setProperty("cssClass", "primaryButton")
        self.save_button.style().unpolish(self.save_button)
        self.save_button.style().polish(self.save_button)

    def _create_vibrant_card(self, title_text):
        """Helper to create a high-contrast card with a bold header."""
        card = aqt.qt.QFrame()
        card.setProperty("cssClass", "vibrantCard")
        
        card_layout = aqt.qt.QVBoxLayout(card)
        card_layout.setContentsMargins(16, 14, 16, 16)
        card_layout.setSpacing(10)
        
        header = aqt.qt.QLabel(title_text)
        header.setObjectName("vibrantCardHeader")
        
        card_layout.addWidget(header)
        return card, card_layout

    def draw(self, layout, show_action_buttons=True):
        lang = self.hypertts.get_ui_language()

        scroll_area = aqt.qt.QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(aqt.qt.QFrame.Shape.NoFrame)
        try:
            scroll_area.setHorizontalScrollBarPolicy(aqt.qt.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        except AttributeError:
            scroll_area.setHorizontalScrollBarPolicy(aqt.qt.Qt.ScrollBarAlwaysOff)

        content_widget = aqt.qt.QWidget()
        main_vlayout = aqt.qt.QVBoxLayout(content_widget)
        main_vlayout.setContentsMargins(12, 12, 12, 8)
        main_vlayout.setSpacing(14)

        # 1. Language Card
        self.language_card, lang_card_layout = self._create_vibrant_card(i18n.get_text("preferences_group_language_title", lang))
        
        self.language_label = aqt.qt.QLabel(i18n.get_text("preferences_label_interface_language", lang))
        lang_card_layout.addWidget(self.language_label)

        self.language_combobox.clear()
        self.language_combobox.addItem(i18n.get_text("preferences_option_language_en", lang), "en")
        self.language_combobox.addItem(i18n.get_text("preferences_option_language_vi", lang), "vi")
        self.language_combobox.setMinimumHeight(34)
        lang_card_layout.addWidget(self.language_combobox)
        
        main_vlayout.addWidget(self.language_card)

        # 2. Cache Card
        self.cache_card, cache_card_layout = self._create_vibrant_card(i18n.get_text("preferences_group_cache_title", lang))
        
        h_cache_row = aqt.qt.QHBoxLayout()
        h_cache_row.setSpacing(10)
        self.cache_retention_checkbox.setMinimumHeight(24)
        h_cache_row.addWidget(self.cache_retention_checkbox)
        
        self.cache_label = aqt.qt.QLabel(i18n.get_text("preferences_cache_label", lang))
        h_cache_row.addWidget(self.cache_label)
        
        self.cache_retention_spinbox.setMinimumHeight(30)
        h_cache_row.addWidget(self.cache_retention_spinbox)
        h_cache_row.addStretch()
        
        cache_card_layout.addLayout(h_cache_row)
        self.cache_helper_label.setProperty("cssClass", "helperText")
        cache_card_layout.addWidget(self.cache_helper_label)
        
        main_vlayout.addWidget(self.cache_card)

        # 2b. Audio Format Card
        self.format_card, format_card_layout = self._create_vibrant_card(i18n.get_text("pref_audio_format", lang))
        
        h_format_row = aqt.qt.QHBoxLayout()
        h_format_row.setSpacing(10)
        self.format_label = aqt.qt.QLabel(i18n.get_text("pref_audio_format_desc", lang))
        h_format_row.addWidget(self.format_label)

        self.audio_format_combobox.clear()
        self.audio_format_combobox.addItems(["mp3", "wav", "ogg"])
        self.audio_format_combobox.setMinimumHeight(30)
        self.audio_format_combobox.setFixedWidth(120)
        h_format_row.addWidget(self.audio_format_combobox)
        h_format_row.addStretch()
        format_card_layout.addLayout(h_format_row)

        main_vlayout.addWidget(self.format_card)

        # 3. Performance Card
        self.perf_card, perf_card_layout = self._create_vibrant_card(i18n.get_text("preferences_group_performance_title", lang))
        
        # Batch Concurrency Sub-section
        batch_vlayout = aqt.qt.QVBoxLayout()
        batch_vlayout.setSpacing(4)
        
        h_batch = aqt.qt.QHBoxLayout()
        self.perf_label = aqt.qt.QLabel(i18n.get_text("preferences_batch_concurrency_label", lang))
        h_batch.addWidget(self.perf_label)
        self.batch_concurrency_spinbox.setFixedWidth(72)
        h_batch.addWidget(self.batch_concurrency_spinbox)
        h_batch.addStretch()
        
        self.batch_concurrency_help_label.setProperty("cssClass", "helperText")
        batch_vlayout.addLayout(h_batch)
        batch_vlayout.addWidget(self.batch_concurrency_help_label)
        
        perf_card_layout.addLayout(batch_vlayout)
        
        main_vlayout.addWidget(self.perf_card)

        # tabs
        # ====================

        self.tabs = aqt.qt.QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.addTab(self.shortcuts.draw(), i18n.get_text("preferences_tab_shortcuts", lang))
        self.tabs.addTab(self.error_handling.draw(), i18n.get_text("preferences_tab_error_handling", lang))
        main_vlayout.addSpacing(4)
        main_vlayout.addWidget(self.tabs)
        
        scroll_area.setWidget(content_widget)
        layout.addWidget(scroll_area)
 
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
        self.audio_format_combobox.currentIndexChanged.connect(self.audio_format_changed)
        
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
        self.language_card.findChild(aqt.qt.QLabel).setText(i18n.get_text("preferences_group_language_title", lang))
        self.language_label.setText(i18n.get_text("preferences_label_interface_language", lang))
        self.language_combobox.setToolTip(i18n.get_text("preferences_language_tooltip", lang))
        
        # update dropdown items
        self.language_combobox.blockSignals(True)
        self.language_combobox.setItemText(0, i18n.get_text("preferences_option_language_en", lang))
        self.language_combobox.setItemText(1, i18n.get_text("preferences_option_language_vi", lang))
        self.language_combobox.blockSignals(False)

        self.cache_card.findChild(aqt.qt.QLabel).setText(i18n.get_text("preferences_group_cache_title", lang))
        self.cache_label.setText(i18n.get_text("preferences_cache_label", lang))
        self.cache_retention_checkbox.setText(i18n.get_text("preferences_cache_enable", lang))
        self.cache_retention_checkbox.setToolTip(i18n.get_text("preferences_cache_tooltip", lang))
        self.cache_helper_label.setText(i18n.get_text("preferences_cache_helper", lang))
        
        self.perf_card.findChild(aqt.qt.QLabel).setText(i18n.get_text("preferences_group_performance_title", lang))
        self.perf_label.setText(i18n.get_text("preferences_batch_concurrency_label", lang))
        self.batch_concurrency_spinbox.setToolTip(i18n.get_text("preferences_batch_concurrency_tooltip", lang))
        self.batch_concurrency_help_label.setText(i18n.get_text("preferences_batch_concurrency_help", lang))
        
        self.format_card.findChild(aqt.qt.QLabel).setText(i18n.get_text("pref_audio_format", lang))
        self.format_label.setText(i18n.get_text("pref_audio_format_desc", lang))
        
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

    def audio_format_changed(self, index: int) -> None:
        """Handle audio format combobox change."""
        format_values = ["mp3", "wav", "ogg"]
        if 0 <= index < len(format_values):
            self.model.audio_format = format_values[index]
        self.model_part_updated_common()

    def save_button_pressed(self) -> None:
        """Handle save button click."""
        with self.hypertts.error_manager.get_single_action_context('Saving Preferences'):
            self.hypertts.save_preferences(self.model)
            self.dialog.close()

    def cancel_button_pressed(self) -> None:
        """Handle cancel button click."""
        self.dialog.close()    