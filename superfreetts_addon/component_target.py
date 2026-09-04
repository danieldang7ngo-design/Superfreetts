from asyncio.proactor_events import constants
import sys
import aqt.qt

from . import component_common
from . import config_models
from . import constants
from . import logging_utils
logger = logging_utils.get_child_logger(__name__)


class BatchTarget(component_common.ConfigComponentBase):
    def __init__(self, hypertts, field_list, model_change_callback):
        self.hypertts = hypertts
        self.field_list = field_list
        self.model_change_callback = model_change_callback

        self.batch_target_model = config_models.BatchTarget()

        # initialize widgets
        self.target_field_combobox = aqt.qt.QComboBox()
        # text and sound
        self.text_sound_group = aqt.qt.QButtonGroup()
        self.radio_button_sound_only = aqt.qt.QRadioButton('Sound Tag only')
        self.radio_button_text_sound = aqt.qt.QRadioButton('Text and Sound Tag')
        self.text_sound_group.addButton(self.radio_button_sound_only)
        self.text_sound_group.addButton(self.radio_button_text_sound)
        # remove sound
        self.remove_sound_group = aqt.qt.QButtonGroup()
        self.radio_button_remove_sound = aqt.qt.QRadioButton('Remove other sound tags')
        self.radio_button_keep_sound = aqt.qt.QRadioButton('Keep other sound tags (append)')
        self.remove_sound_group.addButton(self.radio_button_remove_sound)
        self.remove_sound_group.addButton(self.radio_button_keep_sound)


    def get_model(self):
        return self.batch_target_model

    def load_model(self, model):
        logger.info('load_model')
        self.batch_target_model = model

        self.target_field_combobox.setCurrentText(self.batch_target_model.target_field)

        self.radio_button_text_sound.setChecked(self.batch_target_model.text_and_sound_tag)
        self.radio_button_sound_only.setChecked(not self.batch_target_model.text_and_sound_tag)
        self.radio_button_remove_sound.setChecked(self.batch_target_model.remove_sound_tag)
        self.radio_button_keep_sound.setChecked(not self.batch_target_model.remove_sound_tag)

        # FIX: After setCurrentText(), we must sync the model directly from the combobox text.
        # Using update_field() (which reads currentIndex()) was unsafe because an editable
        # combobox does NOT always update currentIndex() synchronously after setCurrentText().
        # This caused the target_field to fall back to field_list[0] (the first field).
        desired_field = self.batch_target_model.target_field
        if desired_field in self.field_list:
            # Field exists in the list: sync model directly (index-independent)
            self.batch_target_model.target_field = desired_field
            self.notify_model_update()
        else:
            # Field not found in current note type, fall back to first available field
            self.update_field()


    def draw(self): # return scrollarea
        self.scroll_area = aqt.qt.QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.layout_widget = aqt.qt.QWidget()

        self.batch_target_layout = aqt.qt.QVBoxLayout(self.layout_widget)
        
        # target field
        # ============
        groupbox = aqt.qt.QGroupBox('Target Field')
        vlayout = aqt.qt.QVBoxLayout()
        vlayout.addWidget(aqt.qt.QLabel(constants.GUI_TEXT_TARGET_FIELD))
        self.target_field_combobox.addItems(self.field_list)
        self.target_field_combobox.setEditable(True)
        try:
            self.target_field_combobox.setInsertPolicy(aqt.qt.QComboBox.InsertPolicy.NoInsert)
        except AttributeError:
            self.target_field_combobox.setInsertPolicy(aqt.qt.QComboBox.NoInsert)
        
        completer = self.target_field_combobox.completer()
        if completer:
            try:
                completer.setFilterMode(aqt.qt.Qt.MatchFlag.MatchContains)
                completer.setCaseSensitivity(aqt.qt.Qt.CaseSensitivity.CaseInsensitive)
            except AttributeError:
                completer.setFilterMode(aqt.qt.Qt.MatchContains)
                completer.setCaseSensitivity(aqt.qt.Qt.CaseInsensitive)

        # Error label — shown when user types an invalid field name
        self.target_field_error_label = aqt.qt.QLabel()
        self.target_field_error_label.setStyleSheet(
            "color: #C62828; background-color: #FFEBEE; border-radius: 6px; "
            "padding: 4px 8px; font-size: 9pt;"
        )
        self.target_field_error_label.setWordWrap(True)
        self.target_field_error_label.setVisible(False)

        def validate_target_field():
            typed = self.target_field_combobox.currentText().strip()
            if typed and typed not in self.field_list:
                self.target_field_combobox.lineEdit().setStyleSheet(
                    "border: 2px solid #E53935; background-color: #FFF5F5;"
                )
                self.target_field_error_label.setText(
                    f'⚠️ Field "{typed}" not found. Available: ' + ', '.join(self.field_list[:5]) +
                    ('...' if len(self.field_list) > 5 else '')
                )
                self.target_field_error_label.setVisible(True)
            else:
                self.target_field_combobox.lineEdit().setStyleSheet('')
                self.target_field_error_label.setVisible(False)

        self.target_field_combobox.lineEdit().editingFinished.connect(validate_target_field)
        self.target_field_combobox.currentIndexChanged.connect(lambda _: validate_target_field())
        
        vlayout.addWidget(self.target_field_combobox)
        vlayout.addWidget(self.target_field_error_label)
        groupbox.setLayout(vlayout)
        self.batch_target_layout.addWidget(groupbox)


        # text and sound tag
        # ==================
        groupbox = aqt.qt.QGroupBox('Text and Sound Tag Handling')
        vlayout = aqt.qt.QVBoxLayout()
        label = aqt.qt.QLabel(constants.GUI_TEXT_TARGET_TEXT_AND_SOUND)
        label.setWordWrap(True)
        vlayout.addWidget(label)
        self.radio_button_sound_only.setChecked(True)
        vlayout.addWidget(self.radio_button_sound_only)
        vlayout.addWidget(self.radio_button_text_sound)
        groupbox.setLayout(vlayout)
        self.batch_target_layout.addWidget(groupbox)        

        # remove sound tag
        # ================
        groupbox = aqt.qt.QGroupBox('Existing Sound Tag Handling')
        vlayout = aqt.qt.QVBoxLayout()        
        label = aqt.qt.QLabel(constants.GUI_TEXT_TARGET_REMOVE_SOUND_TAG)
        label.setWordWrap(True)
        vlayout.addWidget(label)        
        self.radio_button_remove_sound.setChecked(True)
        vlayout.addWidget(self.radio_button_remove_sound)
        vlayout.addWidget(self.radio_button_keep_sound)
        groupbox.setLayout(vlayout)
        self.batch_target_layout.addWidget(groupbox)                

        self.batch_target_layout.addStretch()

        # connect events
        self.wire_events_base()

        # select default to trigger model update
        self.update_field()

        self.scroll_area.setWidget(self.layout_widget)
        return self.scroll_area

    def wire_events_base(self):
        logger.info('wire events base')
        self.target_field_combobox.currentIndexChanged.connect(lambda x: self.update_field())
        self.radio_button_sound_only.toggled.connect(self.update_text_sound)
        self.radio_button_text_sound.toggled.connect(self.update_text_sound)
        self.radio_button_remove_sound.toggled.connect(self.update_remove_sound)
        self.radio_button_keep_sound.toggled.connect(self.update_remove_sound)

    def update_text_sound(self):
        self.batch_target_model.text_and_sound_tag = self.radio_button_text_sound.isChecked()
        self.notify_model_update()

    def update_remove_sound(self):
        self.batch_target_model.remove_sound_tag = self.radio_button_remove_sound.isChecked()
        self.notify_model_update()

    def update_field(self):
        logger.info('update_field')
        # Prefer currentText() over currentIndex() to handle editable combobox correctly.
        # When setCurrentText() is called, currentIndex() may not be updated synchronously,
        # potentially returning 0 (first field) even when a different field was intended.
        current_text = self.target_field_combobox.currentText().strip()
        if current_text and current_text in self.field_list:
            self.batch_target_model.target_field = current_text
            self.notify_model_update()
            return
        # Fallback: use index-based selection (for fresh draw() with no preset text)
        current_index = self.target_field_combobox.currentIndex()
        if current_index == -1 or current_index >= len(self.field_list) or len(self.field_list) == 0:
            return
        self.batch_target_model.target_field = self.field_list[current_index]
        self.notify_model_update()

    def notify_model_update(self):
        self.model_change_callback(self.batch_target_model)