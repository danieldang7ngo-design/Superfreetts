import sys
import aqt.qt

from . import component_common
from . import config_models
from . import constants
from . import gui_utils
from . import logging_utils
from . import i18n
logger = logging_utils.get_child_logger(__name__)


class TroubleshootingSection(component_common.ConfigComponentBase):

    def __init__(self, hypertts, dialog, model_change_callback):
        self.hypertts = hypertts
        self.dialog = dialog
        self.model = config_models.ErrorHandling()
        self.model_change_callback = model_change_callback
        self.propagate_model_change = True

        self.realtime_tts_errors_dialog_type = aqt.qt.QComboBox()
        # populate combo box with constants.ErrorDialogType
        for error_dialog_type in constants.ErrorDialogType:
            self.realtime_tts_errors_dialog_type.addItem(error_dialog_type.name, error_dialog_type)

        self.disable_ssl_verification = aqt.qt.QCheckBox()
        self.debug_mode = aqt.qt.QCheckBox()
        self.ssl_helper = aqt.qt.QLabel()
        self.ssl_helper.setWordWrap(True)
        self.debug_helper = aqt.qt.QLabel()
        self.debug_helper.setWordWrap(True)

    def get_model(self):
        return self.model

    def load_model(self, model):
        self.model = model
        self.propagate_model_change = False
        self.realtime_tts_errors_dialog_type.setCurrentText(self.model.realtime_tts_errors_dialog_type.name)
        self.disable_ssl_verification.setChecked(self.model.disable_ssl_verification)
        self.debug_mode.setChecked(self.model.debug_mode)
        self.propagate_model_change = True

    def notify_model_update(self):
        if self.propagate_model_change == True:
            self.model_change_callback(self.model)

    def draw(self):
        layout_widget = aqt.qt.QWidget()
        layout = aqt.qt.QVBoxLayout(layout_widget)

        # editor add audio
        # ================

        # Realtime TTS Errors group
        lang = self.hypertts.get_ui_language()
        self.realtime_groupbox = aqt.qt.QGroupBox(i18n.get_text("errors_group_realtime", lang))
        realtime_vlayout = aqt.qt.QVBoxLayout()

        self.realtime_tts_error_dialog = aqt.qt.QLabel(i18n.get_text("errors_label_realtime", lang))
        self.realtime_tts_error_dialog.setWordWrap(True)
        realtime_vlayout.addWidget(self.realtime_tts_error_dialog)
        realtime_vlayout.addWidget(self.realtime_tts_errors_dialog_type)

        self.realtime_groupbox.setLayout(realtime_vlayout)
        layout.addWidget(self.realtime_groupbox)

        # Network Connection group
        self.network_groupbox = aqt.qt.QGroupBox(i18n.get_text("error_handling_group_network", lang))
        network_vlayout = aqt.qt.QVBoxLayout()
        self.ssl_description = aqt.qt.QLabel(i18n.get_text("errors_label_ssl", lang))
        self.ssl_description.setWordWrap(True)
        network_vlayout.addWidget(self.ssl_description)
        network_vlayout.addWidget(self.disable_ssl_verification)
        self.ssl_helper.setProperty("cssClass", "helperText")
        network_vlayout.addWidget(self.ssl_helper)
        self.network_groupbox.setLayout(network_vlayout)
        layout.addWidget(self.network_groupbox)

        # Developer Tools group
        self.developer_groupbox = aqt.qt.QGroupBox(i18n.get_text("error_handling_group_developer", lang))
        developer_vlayout = aqt.qt.QVBoxLayout()
        developer_vlayout.addWidget(self.debug_mode)
        self.debug_helper.setProperty("cssClass", "helperText")
        developer_vlayout.addWidget(self.debug_helper)
        self.developer_groupbox.setLayout(developer_vlayout)
        layout.addWidget(self.developer_groupbox)

        layout.addStretch()

        # wire events
        self.realtime_tts_errors_dialog_type.currentIndexChanged.connect(self.realtime_tts_errors_dialog_type_changed)
        self.disable_ssl_verification.stateChanged.connect(self.disable_ssl_verification_changed)
        self.debug_mode.stateChanged.connect(self.debug_mode_changed)

        return layout_widget

    def update_ui_labels(self, lang: str):
        self.realtime_groupbox.setTitle(i18n.get_text("errors_group_realtime", lang))
        self.realtime_tts_error_dialog.setText(i18n.get_text("errors_label_realtime", lang))
        self.network_groupbox.setTitle(i18n.get_text("error_handling_group_network", lang))
        self.ssl_description.setText(i18n.get_text("errors_label_ssl", lang))
        self.disable_ssl_verification.setText(i18n.get_text("error_handling_disable_ssl_label", lang))
        self.disable_ssl_verification.setToolTip(i18n.get_text("error_handling_disable_ssl_tooltip", lang))
        self.ssl_helper.setText(i18n.get_text("preferences_ssl_warning", lang))
        self.developer_groupbox.setTitle(i18n.get_text("error_handling_group_developer", lang))
        self.debug_mode.setText(i18n.get_text("error_handling_debug_mode_label", lang))
        self.debug_mode.setToolTip(i18n.get_text("error_handling_debug_mode_tooltip", lang))
        self.debug_helper.setText(i18n.get_text("preferences_debug_helper", lang))

    def realtime_tts_errors_dialog_type_changed(self, index):
        logger.info(f'realtime_tts_errors_dialog_type_changed {index}')
        self.model.realtime_tts_errors_dialog_type = self.realtime_tts_errors_dialog_type.itemData(index)
        self.notify_model_update()

    def disable_ssl_verification_changed(self, state):
        logger.info(f'disable_ssl_verification_changed {state}')
        self.model.disable_ssl_verification = bool(state)
        self.notify_model_update()

    def debug_mode_changed(self, state):
        logger.info(f'debug_mode_changed {state}')
        self.model.debug_mode = bool(state)
        self.notify_model_update()


ErrorHandling = TroubleshootingSection

