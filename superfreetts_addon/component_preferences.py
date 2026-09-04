import aqt.qt
from typing import Any

from . import component_common
from . import component_shortcuts
from . import component_troubleshooting
from . import config_models
from . import gui_utils
from . import logging_utils
from . import i18n

logger = logging_utils.get_child_logger(__name__)


class PreferencesPage(component_common.ConfigComponentBase):
    def __init__(self, hypertts: Any, dialog: Any) -> None:
        self.hypertts = hypertts
        self.dialog = dialog
        self.model = config_models.Preferences()
        self.shortcuts = component_shortcuts.ShortcutsSection(self.hypertts, self.dialog, self.shortcuts_updated)
        self.troubleshooting = component_troubleshooting.TroubleshootingSection(
            self.hypertts, self.dialog, self.error_handling_updated
        )

        self.save_button = aqt.qt.QPushButton()
        self.cancel_button = aqt.qt.QPushButton()

        self.language_combobox = aqt.qt.QComboBox()
        self.theme_combobox = aqt.qt.QComboBox()
        self.cache_retention_checkbox = aqt.qt.QCheckBox()
        self.cache_retention_spinbox = aqt.qt.QSpinBox()
        self.cache_retention_spinbox.setMinimum(1)
        self.cache_retention_spinbox.setMaximum(365)
        self.cache_helper_label = aqt.qt.QLabel()
        self.cache_helper_label.setWordWrap(True)
        self.audio_format_combobox = aqt.qt.QComboBox()
        self.audio_helper_label = aqt.qt.QLabel()
        self.audio_helper_label.setWordWrap(True)

    def load_model(self, model):
        logger.info("load_model")
        self.model = model
        self.shortcuts.load_model(self.model.keyboard_shortcuts)
        self.troubleshooting.load_model(self.model.error_handling)

        self._sync_language_combobox_value()

        lang = self.hypertts.get_ui_language()
        self.theme_combobox.clear()
        self.theme_combobox.addItem(i18n.get_text("preferences_option_theme_vibrant", lang), "vibrant")
        self.theme_combobox.addItem(i18n.get_text("preferences_option_theme_ollama", lang), "ollama")
        self.theme_combobox.addItem(i18n.get_text("preferences_option_theme_apple", lang), "apple")
        self.theme_combobox.addItem(i18n.get_text("preferences_option_theme_nintendo", lang), "nintendo")
        self.theme_combobox.addItem(i18n.get_text("preferences_option_theme_binance", lang), "binance")
        self.theme_combobox.addItem(i18n.get_text("preferences_option_theme_clay", lang), "clay")
        self.theme_combobox.addItem(i18n.get_text("preferences_option_theme_claude", lang), "claude")
        self._sync_theme_combobox_value()

        self.cache_retention_checkbox.setChecked(self.model.cache_enabled)
        self.cache_retention_spinbox.setValue(self.model.cache_retention_days)
        self.cache_retention_spinbox.setEnabled(self.model.cache_enabled)

        format_values = ["mp3", "wav", "ogg"]
        current_format = getattr(self.model, "audio_format", "mp3") or "mp3"
        self.audio_format_combobox.setCurrentIndex(format_values.index(current_format) if current_format in format_values else 0)

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

    def _create_section_card(self, title_text, description_text=None):
        card = aqt.qt.QFrame()
        card.setProperty("cssClass", "vibrantCard")

        card_layout = aqt.qt.QVBoxLayout(card)
        card_layout.setContentsMargins(16, 14, 16, 16)
        card_layout.setSpacing(10)

        header = aqt.qt.QLabel(title_text)
        header.setObjectName("vibrantCardHeader")
        card_layout.addWidget(header)

        description = None
        if description_text:
            description = aqt.qt.QLabel(description_text)
            description.setWordWrap(True)
            description.setProperty("cssClass", "helperText")
            card_layout.addWidget(description)

        return card, card_layout, header, description

    def draw(self, layout, show_action_buttons=True):
        lang = self.hypertts.get_ui_language()

        scroll_area = aqt.qt.QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(aqt.qt.QFrame.Shape.NoFrame)
        scroll_area.setHorizontalScrollBarPolicy(aqt.qt.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        content_widget = aqt.qt.QWidget()
        main_vlayout = aqt.qt.QVBoxLayout(content_widget)
        main_vlayout.setContentsMargins(12, 12, 12, 8)
        main_vlayout.setSpacing(14)

        self.general_card, general_layout, self.general_header_label, self.general_description_label = self._create_section_card(
            i18n.get_text("preferences_group_general_title", lang),
            i18n.get_text("preferences_group_general_desc", lang),
        )

        self.language_label = aqt.qt.QLabel(i18n.get_text("preferences_label_interface_language", lang))
        general_layout.addWidget(self.language_label)
        self.language_combobox.clear()
        for language in i18n.SUPPORTED_LANGUAGES:
            self.language_combobox.addItem(self._get_language_option_text(language, lang), language)
        self.language_combobox.setMinimumHeight(34)
        self._sync_language_combobox_value()
        general_layout.addWidget(self.language_combobox)

        self.theme_label = aqt.qt.QLabel(i18n.get_text("preferences_label_theme", lang))
        general_layout.addWidget(self.theme_label)
        theme_row = aqt.qt.QHBoxLayout()
        theme_row.setSpacing(10)
        self.theme_combobox.clear()
        self.theme_combobox.addItem(i18n.get_text("preferences_option_theme_vibrant", lang), "vibrant")
        self.theme_combobox.addItem(i18n.get_text("preferences_option_theme_ollama", lang), "ollama")
        self.theme_combobox.addItem(i18n.get_text("preferences_option_theme_apple", lang), "apple")
        self.theme_combobox.addItem(i18n.get_text("preferences_option_theme_nintendo", lang), "nintendo")
        self.theme_combobox.addItem(i18n.get_text("preferences_option_theme_binance", lang), "binance")
        self.theme_combobox.addItem(i18n.get_text("preferences_option_theme_clay", lang), "clay")
        self.theme_combobox.addItem(i18n.get_text("preferences_option_theme_claude", lang), "claude")
        self.theme_combobox.setMinimumHeight(34)
        self.theme_combobox.setMinimumWidth(220)
        self._sync_theme_combobox_value()
        theme_row.addWidget(self.theme_combobox)
        theme_row.addStretch()
        general_layout.addLayout(theme_row)
        self.theme_helper_label = aqt.qt.QLabel(i18n.get_text("preferences_theme_helper", lang))
        self.theme_helper_label.setProperty("cssClass", "helperText")
        self.theme_helper_label.setWordWrap(True)
        general_layout.addWidget(self.theme_helper_label)

        self.format_label = aqt.qt.QLabel(i18n.get_text("pref_audio_format_desc", lang))
        general_layout.addWidget(self.format_label)
        format_row = aqt.qt.QHBoxLayout()
        format_row.setSpacing(10)
        self.audio_format_combobox.clear()
        self.audio_format_combobox.addItems(["mp3", "wav", "ogg"])
        self.audio_format_combobox.setMinimumHeight(30)
        self.audio_format_combobox.setFixedWidth(120)
        format_row.addWidget(self.audio_format_combobox)
        format_row.addStretch()
        general_layout.addLayout(format_row)
        self.audio_helper_label.setProperty("cssClass", "helperText")
        general_layout.addWidget(self.audio_helper_label)

        self.cache_label = aqt.qt.QLabel(i18n.get_text("preferences_cache_label", lang))
        general_layout.addWidget(self.cache_label)
        cache_row = aqt.qt.QHBoxLayout()
        cache_row.setSpacing(10)
        self.cache_retention_checkbox.setMinimumHeight(24)
        cache_row.addWidget(self.cache_retention_checkbox)
        self.cache_retention_spinbox.setMinimumHeight(30)
        cache_row.addWidget(self.cache_retention_spinbox)
        cache_row.addStretch()
        general_layout.addLayout(cache_row)
        self.cache_helper_label.setProperty("cssClass", "helperText")
        general_layout.addWidget(self.cache_helper_label)
        main_vlayout.addWidget(self.general_card)

        self.shortcuts_card, shortcuts_layout, self.shortcuts_header_label, self.shortcuts_description_label = self._create_section_card(
            i18n.get_text("preferences_group_shortcuts_title", lang),
            i18n.get_text("preferences_group_shortcuts_desc", lang),
        )
        shortcuts_layout.addWidget(self.shortcuts.draw())
        main_vlayout.addWidget(self.shortcuts_card)

        self.troubleshooting_card, troubleshooting_layout, self.troubleshooting_header_label, self.troubleshooting_description_label = self._create_section_card(
            i18n.get_text("preferences_group_troubleshooting_title", lang),
            i18n.get_text("preferences_group_troubleshooting_desc", lang),
        )
        troubleshooting_layout.addWidget(self.troubleshooting.draw())
        main_vlayout.addWidget(self.troubleshooting_card)

        main_vlayout.addStretch()
        scroll_area.setWidget(content_widget)
        layout.addWidget(scroll_area)

        self.update_ui_labels(lang)

        self.save_button.setEnabled(False)
        gui_utils.configure_primary_button(self.save_button, min_height=40, min_width=100, font_size=11)
        gui_utils.configure_secondary_button(self.cancel_button, min_height=40, min_width=100, font_size=11)

        self.language_combobox.currentIndexChanged.connect(self.language_changed)
        self.theme_combobox.currentIndexChanged.connect(self.theme_changed)
        self.cache_retention_checkbox.stateChanged.connect(self.cache_enabled_changed)
        self.cache_retention_spinbox.valueChanged.connect(self.cache_retention_changed)
        self.audio_format_combobox.currentIndexChanged.connect(self.audio_format_changed)

        if show_action_buttons:
            footer = aqt.qt.QHBoxLayout()
            logo_footer = aqt.qt.QWidget()
            logo_footer.setLayout(gui_utils.get_superfreetts_label_header(self.hypertts.superfreetts_pro_enabled()))
            footer.addWidget(logo_footer)
            footer.addStretch()
            footer.addWidget(self.save_button)
            footer.addWidget(self.cancel_button)
            self.save_button.pressed.connect(self.save_button_pressed)
            self.cancel_button.pressed.connect(self.cancel_button_pressed)
            layout.addLayout(footer)

    def language_changed(self, index: int) -> None:
        data_lang = self.language_combobox.itemData(index) or "en"
        self.model.ui_language = data_lang
        self.update_ui_labels(data_lang)
        self.model_part_updated_common()

    def theme_changed(self, index: int) -> None:
        data_theme = self.theme_combobox.itemData(index) or "vibrant"
        self.model.ui_theme = data_theme
        # Preview the theme immediately on the open settings dialog.
        try:
            gui_utils.set_active_theme(data_theme)
            dialog = getattr(self, "dialog", None)
            if dialog is not None and hasattr(dialog, "refresh_stylesheet"):
                dialog.refresh_stylesheet()
        except Exception as e:
            logger.warning(f"[THEME] Error during live preview: {e}")
        self.model_part_updated_common()

    def _sync_theme_combobox_value(self) -> None:
        current_theme = getattr(self.model, "ui_theme", "vibrant") or "vibrant"
        theme_values = ["vibrant", "ollama", "apple", "nintendo", "binance", "clay", "claude"]
        if current_theme not in theme_values:
            current_theme = "vibrant"
        target_index = theme_values.index(current_theme)
        if self.theme_combobox.count() <= target_index:
            return
        self.theme_combobox.blockSignals(True)
        self.theme_combobox.setCurrentIndex(target_index)
        self.theme_combobox.blockSignals(False)

    def _get_language_option_text(self, language: str, display_lang: str) -> str:
        return i18n.get_text(f"preferences_option_language_{language.replace('-', '_')}", display_lang)

    def update_ui_labels(self, lang: str):
        self.general_header_label.setText(i18n.get_text("preferences_group_general_title", lang))
        if self.general_description_label is not None:
            self.general_description_label.setText(i18n.get_text("preferences_group_general_desc", lang))
        self.language_label.setText(i18n.get_text("preferences_label_interface_language", lang))
        self.language_combobox.setToolTip(i18n.get_text("preferences_language_tooltip", lang))

        self.language_combobox.blockSignals(True)
        for index, language in enumerate(i18n.SUPPORTED_LANGUAGES):
            if index < self.language_combobox.count():
                self.language_combobox.setItemText(index, self._get_language_option_text(language, lang))
        self.language_combobox.blockSignals(False)
        self._sync_language_combobox_value()

        self.theme_label.setText(i18n.get_text("preferences_label_theme", lang))
        if hasattr(self, "theme_combobox") and self.theme_combobox.count() >= 7:
            self.theme_combobox.blockSignals(True)
            self.theme_combobox.setItemText(0, i18n.get_text("preferences_option_theme_vibrant", lang))
            self.theme_combobox.setItemText(1, i18n.get_text("preferences_option_theme_ollama", lang))
            self.theme_combobox.setItemText(2, i18n.get_text("preferences_option_theme_apple", lang))
            self.theme_combobox.setItemText(3, i18n.get_text("preferences_option_theme_nintendo", lang))
            self.theme_combobox.setItemText(4, i18n.get_text("preferences_option_theme_binance", lang))
            self.theme_combobox.setItemText(5, i18n.get_text("preferences_option_theme_clay", lang))
            self.theme_combobox.setItemText(6, i18n.get_text("preferences_option_theme_claude", lang))
            self.theme_combobox.blockSignals(False)
        if hasattr(self, "theme_helper_label"):
            self.theme_helper_label.setText(i18n.get_text("preferences_theme_helper", lang))

        self.format_label.setText(i18n.get_text("pref_audio_format_desc", lang))
        self.audio_helper_label.setText(i18n.get_text("preferences_audio_format_helper", lang))

        self.cache_label.setText(i18n.get_text("preferences_cache_label", lang))
        self.cache_retention_checkbox.setText(i18n.get_text("preferences_cache_enable", lang))
        self.cache_retention_checkbox.setToolTip(i18n.get_text("preferences_cache_tooltip", lang))
        self.cache_helper_label.setText(i18n.get_text("preferences_cache_helper", lang))

        self.shortcuts_header_label.setText(i18n.get_text("preferences_group_shortcuts_title", lang))
        if self.shortcuts_description_label is not None:
            self.shortcuts_description_label.setText(i18n.get_text("preferences_group_shortcuts_desc", lang))
        self.troubleshooting_header_label.setText(i18n.get_text("preferences_group_troubleshooting_title", lang))
        if self.troubleshooting_description_label is not None:
            self.troubleshooting_description_label.setText(i18n.get_text("preferences_group_troubleshooting_desc", lang))
        self.shortcuts.update_ui_labels(lang)
        self.troubleshooting.update_ui_labels(lang)

        self.save_button.setText(i18n.get_text("button_apply", lang))
        self.cancel_button.setText(i18n.get_text("button_cancel", lang))

    def _sync_language_combobox_value(self) -> None:
        current_lang = getattr(self.model, "ui_language", "en") or "en"
        language_values = i18n.SUPPORTED_LANGUAGES
        target_index = language_values.index(current_lang) if current_lang in language_values else 0
        if self.language_combobox.count() <= target_index:
            return
        self.language_combobox.blockSignals(True)
        self.language_combobox.setCurrentIndex(target_index)
        self.language_combobox.blockSignals(False)

    def cache_enabled_changed(self, state: int) -> None:
        enabled = (state == aqt.qt.Qt.CheckState.Checked.value)
        self.model.cache_enabled = enabled
        self.cache_retention_spinbox.setEnabled(enabled)
        self.model_part_updated_common()

    def cache_retention_changed(self, value: int) -> None:
        self.model.cache_retention_days = value
        self.model_part_updated_common()

    def audio_format_changed(self, index: int) -> None:
        format_values = ["mp3", "wav", "ogg"]
        if 0 <= index < len(format_values):
            self.model.audio_format = format_values[index]
        self.model_part_updated_common()

    def save_button_pressed(self) -> None:
        with self.hypertts.error_manager.get_single_action_context("Saving Preferences"):
            self.hypertts.save_preferences(self.model)
            self.dialog.close()

    def cancel_button_pressed(self) -> None:
        self.dialog.close()


ComponentPreferences = PreferencesPage
