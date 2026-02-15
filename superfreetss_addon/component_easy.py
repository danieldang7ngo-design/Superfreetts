import sys
import aqt.qt
import copy

from . import component_common
from . import component_target_easy
from . import component_voiceselection_easy
from . import component_source_easy
from . import config_models
from . import constants
from . import constants_events
from .constants_events import Event, EventMode
from . import stats
from . import gui_utils
from . import logging_utils
from . import errors
from . import i18n

logger = logging_utils.get_child_logger(__name__)

# The ComponentEasy component allows the user to generate audio for a single note. It's invoked from the Anki
# editor for a single note.

# todo:
# OK add load_model logic for ComponentEasy, and test
# add audio at cursor location
#  note: this will require calling self._editor.addMedia(path), like AwesomeTTS used to do
#  https://github.com/AwesomeTTS/awesometts-anki-addon/blob/90826a8d79794b1e813f5286202f932ca09e6363/awesometts/gui/generator.py#L798C17-L798C45
# OK properly strip html when getting source text
# OK need to make sure HTML entities are not replaced when displaying text to user
# OK clear clipboard when user moves away from clipboard source radio button
# OK save profile as default profile for DeckNoteType when applying audio
# OK integrate with the editor buttons / preset mapping rules
# OK preview button should disable while preview is running
# OK bug: adding to same field overwrites the text
# OK bug: if existing sound tag, it's not stripped when displaying to the user
# potential issues:
#  - what if the user didn't select a source field in the editor ? we need to set the target field (write a test)

sc = stats.StatsContext(constants_events.EventContext.generate)

class ComponentEasy(component_common.ComponentBase):
    BUTTON_TEXT_PREVIEW_AUDIO = 'Preview Audio'
    BUTTON_TEXT_PREVIEWING = 'Playing Preview...'
    BUTTON_TEXT_ADD_AUDIO = 'Add Audio'
    BUTTON_TEXT_ADDING_AUDIO = 'Adding Audio...'

    def __init__(self, hypertts, dialog, deck_note_type: config_models.DeckNoteType, editor_context: config_models.EditorContext):
        self.hypertts = hypertts
        self.dialog = dialog
        self.deck_note_type = deck_note_type
        self.editor_context = editor_context
        self.original_width = None
        self.batch_model = None

        # initialize source component
        self.source = component_source_easy.ComponentEasySource(hypertts, editor_context, self.model_update_source)
        source_field = editor_context.current_field
        field_list = field_list = list(editor_context.note.keys())

        # initialize sub-components
        self.target = component_target_easy.BatchTargetEasy(hypertts, field_list, self.model_update_target)
        self.voice_selection = component_voiceselection_easy.VoiceSelectionEasy(hypertts, dialog, self.model_update_voice_selection)
        
        # configure the model
        self.batch_model = config_models.BatchConfig(self.hypertts.anki_utils)
        self.set_model_defaults()


    def set_model_defaults(self):
        # this will get overwritten if we load a model
        self.batch_model.name = self.hypertts.get_default_easy_preset_name(self.deck_note_type)
        # set dummy source, will not get used
        self.batch_model.source = config_models.BatchSource(
            mode=constants.BatchMode.simple,
            source_field=self.editor_context.current_field
        )
        # default text processing
        self.batch_model.text_processing = config_models.TextProcessing()

    def load_preset(self, preset_id):
        model = self.hypertts.load_preset(preset_id)
        self.load_model(model)

    def load_model(self, model):
        logger.info('load_model')
        self.batch_model = model
        # disseminate to all components
        # check the current_field in editor context. If it's different from the preset, don't load
        # target / source, because the user is trying to load from a different field
        if self.editor_context.current_field != None and self.editor_context.current_field != model.source.source_field:
            logger.warning(f'Current field {self.editor_context.current_field} does not match model source field {model.source.source_field}. Not loading source/target.')
        else:
            self.source.load_model(model.source)
            self.target.load_model(model.target)
        self.voice_selection.load_model(model.voice_selection)

    def get_model(self):
        logger.debug('get_model')
        # do some adjustments on the model
        
        # If we have selected text, set the target field to the current field
        if self.batch_model.target.same_field:
            # we want to insert into "same field". this requires some manipulation because the target field
            # is not necessarily set on the model
            if self.source.selection_radio.isChecked() and self.editor_context.current_field:
                # user is generating from a selection
                self.batch_model.target.target_field = self.editor_context.current_field
                logger.debug(f'get_model: selection active, set target field to {self.batch_model.target.target_field}')
            else:
                # not generating from a selection
                # if same field, we need to set the target field to the source field
                self.batch_model.target.target_field = self.batch_model.source.source_field
                # also, the only thing that makes sense is text_and_sound_tag=True
                self.batch_model.target.text_and_sound_tag = True
                logger.debug(f'get_model: same field selected, set target field to {self.batch_model.target.target_field}')
        
        logger.debug(f'get_model: returning model {repr(self.batch_model)}')

        return self.batch_model

    def draw(self, layout):
        lang = self.hypertts.get_ui_language()

        # thiết lập text theo ngôn ngữ hiện tại
        self.BUTTON_TEXT_PREVIEW_AUDIO = i18n.get_text("easy_button_preview_audio", lang)
        self.BUTTON_TEXT_PREVIEWING = i18n.get_text("easy_button_previewing", lang)
        self.BUTTON_TEXT_ADD_AUDIO = i18n.get_text("easy_button_add_audio", lang)
        self.BUTTON_TEXT_ADDING_AUDIO = i18n.get_text("easy_button_adding_audio", lang)
        # Add header with logo at the top
        header_layout = aqt.qt.QHBoxLayout()
        header_layout.addStretch()
        header_layout.addLayout(gui_utils.get_superfreetss_label_header(self.hypertts.superfreetss_pro_enabled()))
        layout.addLayout(header_layout)

        # Main Vertical Content Layout
        self.main_content_layout = aqt.qt.QVBoxLayout()
        
        # ① Source Text
        source_group = aqt.qt.QGroupBox("① Source Text")
        source_layout = aqt.qt.QVBoxLayout()
        source_layout.addWidget(self.source.draw())
        source_group.setLayout(source_layout)
        self.main_content_layout.addWidget(source_group)
        
        # ② Voice Selection
        voice_group = aqt.qt.QGroupBox("② Voice Selection")
        voice_layout = aqt.qt.QVBoxLayout()
        # voice_description_label = aqt.qt.QLabel(constants.GUI_TEXT_EASY_VOICE_SELECTION)
        # voice_layout.addWidget(voice_description_label) 
        # (Optional: Description might be redundant with wizard number, but keeping it simple)
        voice_layout.addWidget(self.voice_selection.draw())
        voice_group.setLayout(voice_layout)
        self.main_content_layout.addWidget(voice_group)

        # ③ Target Field (Hidden by default, toggled via 'More Settings')
        self.target_widget = aqt.qt.QWidget()
        target_layout = aqt.qt.QVBoxLayout(self.target_widget)
        target_layout.setContentsMargins(0, 0, 0, 0)
        
        target_group = aqt.qt.QGroupBox("③ Target Field")
        target_group_layout = aqt.qt.QVBoxLayout()
        target_description_label = aqt.qt.QLabel(constants.GUI_TEXT_EASY_TARGET)
        target_group_layout.addWidget(target_description_label)
        target_group_layout.addWidget(self.target.draw())
        target_group.setLayout(target_group_layout)
        
        target_layout.addWidget(target_group)
        self.main_content_layout.addWidget(self.target_widget)
        self.target_widget.hide() # Collapsed default

        layout.addLayout(self.main_content_layout)

        # Buttons
        button_layout = aqt.qt.QHBoxLayout()
        button_layout.addStretch()
        
        self.toggle_settings_button = aqt.qt.QPushButton(i18n.get_text("easy_button_more_settings", lang))
        # get shortcuts from preferences
        preferences = self.hypertts.get_preferences()
        preview_shortcut = preferences.keyboard_shortcuts.shortcut_editor_preview_audio
        add_shortcut = preferences.keyboard_shortcuts.shortcut_editor_add_audio

        self.preview_sound_button = aqt.qt.QPushButton(self.BUTTON_TEXT_PREVIEW_AUDIO)
        if preview_shortcut is not None:
            self.preview_sound_button.setShortcut(preview_shortcut)
            self.preview_sound_button.setToolTip(f'Preview the audio that will be generated ({preview_shortcut})')
        else:
            self.preview_sound_button.setToolTip('Preview the audio that will be generated')
            
        self.add_audio_button = aqt.qt.QPushButton(self.BUTTON_TEXT_ADD_AUDIO)
        if add_shortcut is not None:
            self.add_audio_button.setShortcut(add_shortcut)
            self.add_audio_button.setToolTip(f'Add the audio to your note ({add_shortcut})')
        else:
            self.add_audio_button.setToolTip('Add the audio to your note')
            
        self.add_audio_button.setStyleSheet(self.hypertts.anki_utils.get_green_stylesheet())
        self.cancel_button = aqt.qt.QPushButton(i18n.get_text("button_cancel", lang))
        self.cancel_button.setStyleSheet(self.hypertts.anki_utils.get_red_stylesheet())

        button_layout.addWidget(self.toggle_settings_button)
        button_layout.addWidget(self.preview_sound_button)
        button_layout.addWidget(self.add_audio_button)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)

        # Wire events
        self.preview_sound_button.pressed.connect(self.preview_button_pressed)
        self.add_audio_button.pressed.connect(self.add_audio_button_pressed)
        self.cancel_button.pressed.connect(self.cancel_button_pressed)
        self.toggle_settings_button.pressed.connect(self.toggle_settings)


    def model_update_source(self, model):
        logger.debug(f'model_update_source: {model}')
        self.batch_model.source = model

    def model_update_target(self, model):
        logger.debug(f'model_update_target: {model}')
        self.batch_model.target = model

    def model_update_voice_selection(self, model):
        logger.debug(f'model_update_voice_selection: {model}')
        self.batch_model.voice_selection = model

    def get_source_text(self):
        return self.source.get_current_text()

    # preview audio handling
    # ======================

    @sc.event(Event.click_preview)
    def preview_button_pressed(self):
        self.preview_sound_button.setText(self.BUTTON_TEXT_PREVIEWING)
        self.preview_sound_button.setEnabled(False)
        self.hypertts.anki_utils.run_in_background(self.sound_preview_task, self.sound_preview_task_done)

    def sound_preview_task(self):
        # get text
        self.hypertts.preview_note_audio(self.get_model(), self.editor_context.note, self.get_source_text())
        return True

    def sound_preview_task_done(self, result):
        with self.hypertts.error_manager.get_single_action_context('Playing Sound Preview'):
            result = result.result()
        self.hypertts.anki_utils.run_on_main(self.finish_sound_preview)

    def finish_sound_preview(self):
        self.preview_sound_button.setText(self.BUTTON_TEXT_PREVIEW_AUDIO)
        self.preview_sound_button.setEnabled(True)

    # add audio handling
    # ==================

    @sc.event(Event.click_add)
    def add_audio_button_pressed(self):
        self.add_audio_button.setText(self.BUTTON_TEXT_ADDING_AUDIO)
        self.add_audio_button.setEnabled(False)
        self.hypertts.anki_utils.run_in_background(self.add_audio_task, self.add_audio_task_done)

    def add_audio_task(self):
        logger.debug('add_audio_task')
        self.hypertts.editor_note_add_audio(self.get_model(), self.editor_context, text_input=self.get_source_text())
        return True

    def add_audio_task_done(self, result):
        logger.debug('add_audio_task_done')
        with self.hypertts.error_manager.get_single_action_context('Adding Audio to Note'):
            result = result.result()
            # save default profile
            self.hypertts.save_default_preset(self.deck_note_type, self.get_model())
            self.dialog.close()
        self.hypertts.anki_utils.run_on_main(self.finish_add_audio)
    
    def finish_add_audio(self):
        self.add_audio_button.setText(self.BUTTON_TEXT_ADD_AUDIO)
        self.add_audio_button.setEnabled(True)

    @sc.event(Event.click_cancel)
    def cancel_button_pressed(self):
        self.dialog.close()

    def toggle_settings(self):
        if self.target_widget.isVisible():
            self.target_widget.hide()
            lang = self.hypertts.get_ui_language()
            self.toggle_settings_button.setText(i18n.get_text("easy_button_more_settings", lang))
            if self.original_width is not None:
                 # Logic for width adjustment might be less relevant in vertical layout, but keeping it safe
                self.dialog.adjustSize()
        else:
            self.target_widget.show()
            lang = self.hypertts.get_ui_language()
            self.toggle_settings_button.setText(i18n.get_text("easy_button_hide_settings", lang))
            self.dialog.adjustSize()

class EasyDialog(aqt.qt.QDialog):
    def __init__(self, hypertts):
        super(aqt.qt.QDialog, self).__init__()
        self.hypertts = hypertts
        # Cho phép dialog Easy Mode thu nhỏ/phóng to theo ý người dùng
        self.setWindowFlag(aqt.qt.Qt.WindowType.WindowMinMaxButtonsHint, True)
        self.setStyleSheet(constants.STYLESHEET_DIALOG)
        lang = self.hypertts.get_ui_language()
        self.setWindowTitle(i18n.get_text("dialog_easy_title", lang))
        self.main_layout = aqt.qt.QVBoxLayout(self)

    def configure(self, deck_note_type: config_models.DeckNoteType, editor_context: config_models.EditorContext):
        easy_component = ComponentEasy(self.hypertts, self, deck_note_type, editor_context)
        layout = aqt.qt.QVBoxLayout()
        easy_component.draw(self.main_layout)
        self.easy_component = easy_component
        # Set initial size
        self.adjustSize()

    def load_preset(self, preset_id:str):
        self.easy_component.load_preset(preset_id)

    def pick_default_voice(self):
        self.easy_component.voice_selection.pick_default_voice()

    def close(self):
        self.closed = True
        self.accept()


def create_dialog_editor_new_preset(hypertts, deck_note_type: config_models.DeckNoteType, editor_context: config_models.EditorContext):
    dialog = EasyDialog(hypertts)
    dialog.configure(deck_note_type, editor_context)
    hypertts.anki_utils.wait_for_dialog_input(dialog, constants.DIALOG_ID_EASY)

def create_dialog_editor_existing_preset(hypertts, 
        deck_note_type: config_models.DeckNoteType, 
        editor_context: config_models.EditorContext,
        preset_id: str):
    logger.debug(f'create_dialog_editor_existing_preset: {preset_id}')
    dialog = EasyDialog(hypertts)
    dialog.configure(deck_note_type, editor_context)
    dialog.load_preset(preset_id)
    hypertts.anki_utils.wait_for_dialog_input(dialog, constants.DIALOG_ID_EASY)    

@sc.event(Event.open, EventMode.easy_editor)
def create_dialog_editor(hypertts, deck_note_type: config_models.DeckNoteType, editor_context: config_models.EditorContext):
    dialog = EasyDialog(hypertts)
    dialog.configure(deck_note_type, editor_context)
    # load preset if one exists
    preset_id: str = hypertts.get_default_preset_id(deck_note_type)
    if preset_id != None:
        logger.info(f'loading preset_id {preset_id}')
        dialog.load_preset(preset_id)
    else:
        # no voice selected, pick a default voice
        logger.info('no preset_id found, using default voice')
        dialog.pick_default_voice()
    hypertts.anki_utils.wait_for_dialog_input(dialog, constants.DIALOG_ID_EASY)
