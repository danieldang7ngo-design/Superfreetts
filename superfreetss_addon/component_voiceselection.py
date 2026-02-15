import sys
import aqt.qt
import copy

from . import constants
from . import options
from . import component_common
from . import config_models
from . import gui_utils
from . import errors
from . import voice as voice_module
from . import constants_events
from .constants_events import Event, EventMode
from . import stats
from . import logging_utils
from . import i18n
logger = logging_utils.get_child_logger(__name__)

sc = stats.StatsContext(constants_events.EventContext.voice_selection)

class VoiceSelection(component_common.ConfigComponentBase):
    def __init__(self, hypertts, dialog, model_change_callback):
        self.hypertts = hypertts
        self.dialog = dialog
        self.model_change_callback = model_change_callback
        self.enable_model_change_callback = True

        # initialize widgets

        self.audio_languages_combobox = aqt.qt.QComboBox()
        self.languages_combobox = aqt.qt.QComboBox()
        self.services_combobox = aqt.qt.QComboBox()
        self.genders_combobox = aqt.qt.QComboBox()
        self.voices_combobox = aqt.qt.QComboBox()

        for combobox in [
            self.audio_languages_combobox,
            self.languages_combobox,
            self.services_combobox,
            self.genders_combobox,
            self.voices_combobox]:
            combobox.view().setVerticalScrollBarPolicy(aqt.qt.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
            # Allow comboboxes to shrink and expand reasonably
            combobox.setSizePolicy(aqt.qt.QSizePolicy.Policy.Expanding, aqt.qt.QSizePolicy.Policy.Fixed)
            combobox.setMinimumWidth(100)
            combobox.setMaximumWidth(450)
        self.voices_combobox.setFont(gui_utils.get_large_combobox_font())
        self.voices_combobox.setFixedHeight(45)

        self.play_sample_button = aqt.qt.QPushButton('Play Sample')
        self.reset_filters_button = aqt.qt.QPushButton('Reset Filters')

        # Guard to prevent infinite recursion during dynamic updates
        self._is_updating_filters = False


    def get_voices(self):
        self.voice_list = self.hypertts.service_manager.full_voice_list()

        languages = set()
        audio_languages = set()
        services = set()
        genders = set()

        for voice in self.voice_list:
            # with ttsvoice v3, voices can support multiple languages
            for audio_language in voice.audio_languages:
                audio_languages.add(audio_language)
                languages.add(audio_language.lang)
            services.add(voice.service)
            genders.add(voice.gender)

        def get_name(entry):
            return entry.name
        def get_language_name(entry):
            return entry.lang_name
        def get_audio_language_name(entry):
            return entry.audio_lang_name

        self.audio_languages = sorted(list(audio_languages), key=get_audio_language_name)
        self.languages = sorted(list(languages), key=get_language_name)
        self.services = sorted(list(services))
        self.genders = sorted(list(genders), key=get_name)

        self.set_default_selection_model()

    def get_model(self):
        return self.voice_selection_model

    def load_model(self, model):
        # don't report changes back to parent dialog as we adjust widgets
        self.enable_model_change_callback = False
        logger.info(f'load_model, model: {model}')
        # self.voice_selection_model = model

        if model.selection_mode == constants.VoiceSelectionMode.single:
            logger.info(f'options: {model.voice.options}')
            # single voice
            self.radio_button_single.setChecked(True)
            # here we need to select the correct voice, based on what the user has saved in their preset (single voice)
            # we have access to the voice_id, but we need to locate the proper voice
            voice_id = model.voice.voice_id
            voice = self.hypertts.service_manager.locate_voice(voice_id)
            voice_index = self.voice_list.index(voice)
            self.voices_combobox.setCurrentIndex(voice_index)
            # self.voice_options_layout
            #self.voice_options_widgets[widget_name]
            logger.info(f'options: {model.voice.options}')
            for key, value in model.voice.options.items():
                widget_name = f'voice_option_{key}'
                logger.info(f'setting value of {key} to {value}')
                voice_option_widget = self.voice_options_widgets[widget_name]
                setCurrentTextFn = getattr(voice_option_widget, 'setCurrentText', None)
                if callable(setCurrentTextFn):
                    # qcombobox detected
                    voice_option_widget.setCurrentText(value)
                else:
                    # check if it's a QLineEdit (has setText method)
                    setTextFn = getattr(voice_option_widget, 'setText', None)
                    if callable(setTextFn):
                        # QLineEdit detected
                        voice_option_widget.setText(value)
                    else:
                        # slider
                        self.voice_options_widgets[widget_name].setValue(value)
        elif model.selection_mode == constants.VoiceSelectionMode.random:
            self.radio_button_random.setChecked(True)
            self.voice_selection_model = model
            self.redraw_selected_voices()
        elif model.selection_mode == constants.VoiceSelectionMode.priority:
            self.radio_button_priority.setChecked(True)
            self.voice_selection_model = model
            self.redraw_selected_voices()

        self.enable_model_change_callback = True

    def sample_text_selected(self, text):
        logger.debug(f'sample_text_selected: {text}')
        self.sample_text = text
        lang = self.hypertts.get_ui_language()
        self.play_sample_button.setText(i18n.get_text("voice_button_play_sample", lang))
        self.play_sample_button.setEnabled(True)


    def notify_model_update(self):
        if self.enable_model_change_callback:
            self.model_change_callback(self.voice_selection_model)

    def set_default_selection_model(self):
        self.voice_selection_model = config_models.VoiceSelectionSingle() # default
        # pick first voice
        if len(self.voice_list) == 0:
            raise errors.NoVoicesAvailable()
        voice_id = self.voice_list[0].voice_id
        self.voice_selection_model.set_voice(config_models.VoiceWithOptions(voice_id, {}))

    def populate_combobox(self, combobox, items):
        combobox.addItem(constants.LABEL_FILTER_ALL)
        combobox.insertSeparator(1)
        combobox.addItems(items)

    def draw(self): # return scrollarea
        # filters:
        # - language
        # - locale
        # - service
        # - gender

        # 1. get full voice list
        # 2. iterate over the list, gather attributes
        # 3. populate filters
        # 4. draw all voices

        lang = self.hypertts.get_ui_language()

        self.scroll_area = aqt.qt.QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.layout_widget = aqt.qt.QWidget()

        self.voices_layout = aqt.qt.QVBoxLayout(self.layout_widget)
        self.voices_layout.setContentsMargins(12, 12, 12, 12)
        self.voices_layout.setSpacing(16)

        self.get_voices()

        self.populate_combobox(self.audio_languages_combobox, [audio_lang.audio_lang_name for audio_lang in self.audio_languages])
        self.populate_combobox(self.languages_combobox, [language.lang_name for language in self.languages])
        self.populate_combobox(self.services_combobox, self.services)
        self.populate_combobox(self.genders_combobox, [gender.name for gender in self.genders])

        # ── Modern Filter Bar ──
        self.groupbox_voice_filters = aqt.qt.QGroupBox(i18n.get_text("voice_filters_group_title", lang))
        
        # Grid layout for filters, 2 columns of (Label + Combo) pairs
        gridlayout = aqt.qt.QGridLayout()
        gridlayout.setSpacing(10)
        gridlayout.setContentsMargins(16, 20, 16, 16)

        # Row 0
        gridlayout.addWidget(aqt.qt.QLabel(i18n.get_text("voice_label_language", lang)), 0, 0)
        gridlayout.addWidget(self.languages_combobox, 0, 1)
        gridlayout.addWidget(aqt.qt.QLabel(i18n.get_text("voice_label_locale", lang)), 0, 2)
        gridlayout.addWidget(self.audio_languages_combobox, 0, 3)

        # Row 1
        gridlayout.addWidget(aqt.qt.QLabel(i18n.get_text("voice_label_service", lang)), 1, 0)
        gridlayout.addWidget(self.services_combobox, 1, 1)
        gridlayout.addWidget(aqt.qt.QLabel(i18n.get_text("voice_label_gender", lang)), 1, 2)
        gridlayout.addWidget(self.genders_combobox, 1, 3)

        # Centered Reset button
        reset_layout = aqt.qt.QHBoxLayout()
        reset_layout.addStretch()
        self.reset_filters_button.setText(i18n.get_text("voice_button_reset_filters", lang))
        gui_utils.configure_secondary_button(self.reset_filters_button, min_width=140)
        reset_layout.addWidget(self.reset_filters_button)
        reset_layout.addStretch()
        gridlayout.addLayout(reset_layout, 2, 0, 1, 4)

        self.groupbox_voice_filters.setLayout(gridlayout)
        self.voices_layout.addWidget(self.groupbox_voice_filters)

        # ── Voice Selection Card ──
        self.groupbox_voice = aqt.qt.QGroupBox(i18n.get_text("voice_group_voice", lang))
        vlayout = aqt.qt.QVBoxLayout()
        vlayout.setSpacing(12)
        vlayout.setContentsMargins(16, 20, 16, 16)
        
        vlayout.addWidget(self.voices_combobox)

        self.play_sample_button.setText(i18n.get_text("voice_button_play_sample_wait", lang))
        gui_utils.configure_secondary_button(self.play_sample_button)
        vlayout.addWidget(self.play_sample_button)

        self.voice_options_layout = aqt.qt.QGridLayout()
        self.voice_options_layout.setSpacing(8)
        vlayout.addLayout(self.voice_options_layout)

        # Piper Warning Label (Hidden by default)
        self.piper_warning_label = aqt.qt.QLabel()
        self.piper_warning_label.setStyleSheet("color: #C62828; font-weight: bold; background-color: #FFEBEE; padding: 10px; border-radius: 8px;")
        self.piper_warning_label.setWordWrap(True)
        self.piper_warning_label.setVisible(False)
        vlayout.addWidget(self.piper_warning_label)

        self.groupbox_voice.setLayout(vlayout)
        self.voices_layout.addWidget(self.groupbox_voice)


        # voice selection mode groupbox
        # =============================
        groupbox = aqt.qt.QGroupBox(i18n.get_text("voice_group_selection_mode", lang))
        vlayout = aqt.qt.QVBoxLayout()
        mode_group = aqt.qt.QButtonGroup()
        self.radio_button_single = aqt.qt.QRadioButton(i18n.get_text("voice_radio_single", lang))
        self.radio_button_random = aqt.qt.QRadioButton(i18n.get_text("voice_radio_random", lang))
        self.radio_button_priority = aqt.qt.QRadioButton(i18n.get_text("voice_radio_priority", lang))
        mode_group.addButton(self.radio_button_single)
        mode_group.addButton(self.radio_button_random)
        mode_group.addButton(self.radio_button_priority)
        #self.voices_layout.addWidget(mode_group)
        vlayout.addWidget(self.radio_button_single)
        vlayout.addWidget(self.radio_button_random)
        vlayout.addWidget(self.radio_button_priority)

        groupbox.setLayout(vlayout)
        self.voices_layout.addWidget(groupbox)   
        # finished voice selection mode

        # voice list groupbox, should be in a widget stack
        # ================================================

        self.voice_list_display_stack = aqt.qt.QStackedWidget()
        no_voice_list_stack = aqt.qt.QWidget()
        voice_list_stack = aqt.qt.QWidget()

        self.voicelist_groupbox = aqt.qt.QGroupBox(i18n.get_text("voice_group_voice_list", lang))
        vlayout = aqt.qt.QVBoxLayout(voice_list_stack)

        # buttons
        # -------

        self.add_voice_button = aqt.qt.QPushButton(i18n.get_text("voice_button_add_voice", lang))
        vlayout.addWidget(self.add_voice_button)

        # voice list grid
        # ---------------

        self.voice_list_grid_layout = aqt.qt.QGridLayout()
        vlayout.addLayout(self.voice_list_grid_layout)

        # finalize stack setup
        self.voice_list_display_stack.addWidget(no_voice_list_stack)
        self.voice_list_display_stack.addWidget(voice_list_stack)
        self.voices_layout.addWidget(self.voice_list_display_stack, 1)

        # -------------------------
        # finished voice list setup



        # set some defaults
        # =================
        self.radio_button_single.setChecked(True)
        # self.voicelist_groupbox.setVisible(False)
        self.voice_list_display_stack.setCurrentIndex(0)

        # wire all events
        # ===============

        self.audio_languages_combobox.currentIndexChanged.connect(self.filter_and_draw_voices)
        self.languages_combobox.currentIndexChanged.connect(self.filter_and_draw_voices)
        self.services_combobox.currentIndexChanged.connect(self.filter_and_draw_voices)
        self.genders_combobox.currentIndexChanged.connect(self.filter_and_draw_voices)

        self.voices_combobox.currentIndexChanged.connect(self.voice_selected)

        self.play_sample_button.setEnabled(False)
        self.play_sample_button.setText(i18n.get_text("voice_button_play_sample_wait", lang))
        self.play_sample_button.pressed.connect(self.play_sample)

        self.reset_filters_button.pressed.connect(self.reset_filters)

        self.radio_button_single.toggled.connect(self.voice_selection_mode_change)
        self.radio_button_random.toggled.connect(self.voice_selection_mode_change)
        self.radio_button_priority.toggled.connect(self.voice_selection_mode_change)

        self.add_voice_button.pressed.connect(self.add_voice)
        gui_utils.configure_primary_button(self.add_voice_button)

        self.filter_and_draw_voices()

        self.scroll_area.setWidget(self.layout_widget)
        return self.scroll_area

    def voice_selection_mode_change(self):
        if self.radio_button_single.isChecked():
            self.voice_list_display_stack.setCurrentIndex(0)
            self.voice_selection_model = config_models.VoiceSelectionSingle()
        elif self.radio_button_random.isChecked():
            self.voice_list_display_stack.setCurrentIndex(1)
            self.voice_selection_model = config_models.VoiceSelectionRandom()
        elif self.radio_button_priority.isChecked():
            self.voice_list_display_stack.setCurrentIndex(1)
            self.voice_selection_model = config_models.VoiceSelectionPriority()
        self.redraw_selected_voices()
        self.notify_model_update()

    def reset_filters(self):
        self.audio_languages_combobox.setCurrentIndex(0)
        self.languages_combobox.setCurrentIndex(0)
        self.services_combobox.setCurrentIndex(0)
        self.genders_combobox.setCurrentIndex(0)

    def get_selected_voice(self):
        if len(self.filtered_voice_list) == 0:
            # most likely user configured filters in a way that no voices match
            raise errors.NoVoiceSelected()
        current_index = self.voices_combobox.currentIndex()
        if current_index >= len(self.filtered_voice_list):
            logger.error(f'filtered_voice_list: {self.filtered_voice_list} current_index: {current_index}')
            raise errors.NoVoiceSelected()
        selected_voice = self.filtered_voice_list[current_index]
        return selected_voice


    def play_sample(self):
        with self.hypertts.error_manager.get_single_action_context('Playing Voice Sample'):
            logger.info('play_sample')
            selected_voice = self.get_selected_voice()
            # get options
            options = self.current_voice_options
            logger.debug(f'play_sample, sample_text: {self.sample_text}')
            self.hypertts.play_sound(self.sample_text, selected_voice.voice_id, options)

    def add_voice(self):
        with self.hypertts.error_manager.get_single_action_context('Adding Voice'):
            selected_voice = self.get_selected_voice()
            options = copy.copy(self.current_voice_options)

            if self.radio_button_random.isChecked():
                self.voice_selection_model.add_voice(config_models.VoiceWithOptionsRandom(selected_voice.voice_id, options))
            elif self.radio_button_priority.isChecked():
                self.voice_selection_model.add_voice(config_models.VoiceWithOptionsPriority(selected_voice.voice_id, options))

            self.redraw_selected_voices()
            
            self.notify_model_update()


    def voice_selected(self, current_index):
        # clear the options layout
        self.voice_options_widgets = {}
        for i in reversed(range(self.voice_options_layout.count())): 
            self.voice_options_layout.itemAt(i).widget().setParent(None)

        # clear the current voice options
        self.current_voice_options = {}

        if len(self.filtered_voice_list) == 0:
            # if we are in the single voice mode, clear current voice
            if self.voice_selection_model.selection_mode == constants.VoiceSelectionMode.single:
                self.voice_selection_model.set_voice(None)
                self.notify_model_update()
            return

        voice = self.filtered_voice_list[current_index]
        logger.info(f'voice_selected: {voice} options: {voice.options}')

        def get_set_option_lambda(voice, key):
            def set_value(value):
                self.current_voice_options[key] = value
                logger.info(f'set option {key} to {value}')
                if self.voice_selection_model.selection_mode == constants.VoiceSelectionMode.single:
                    self.voice_selection_model.set_voice(config_models.VoiceWithOptions(voice.voice_id, self.current_voice_options))
                    self.notify_model_update()
            return set_value

        # populate voice options layout
        row = 0
        for key, value in voice.options.items():
            widget_name = f'voice_option_{key}'
            option_type = options.ParameterType[value['type']]
            if option_type == options.ParameterType.number or option_type == options.ParameterType.number_int:
                # create a spinner
                if option_type == options.ParameterType.number:
                    widget = aqt.qt.QDoubleSpinBox()
                elif option_type == options.ParameterType.number_int:
                    widget = aqt.qt.QSpinBox()
                widget.setObjectName(widget_name)
                # logger.info(f'objec name: {widget_name}')
                widget.setRange(value['min'], value['max'])
                widget.setValue(value['default'])
                widget.valueChanged.connect(get_set_option_lambda(voice, key))
                label_text = f"""{key} ({value['min']} to {value['max']})"""
                label = aqt.qt.QLabel(label_text)
                self.voice_options_layout.addWidget(label, row, 0, 1, 1)
                self.voice_options_layout.addWidget(widget, row, 1, 1, 1)
                self.voice_options_widgets[widget_name] = widget
            elif option_type == options.ParameterType.list:
                # create a combobox
                widget = aqt.qt.QComboBox()
                widget.setObjectName(widget_name)
                widget.addItems(value['values'])
                widget.setCurrentText(value['default'])
                widget.currentTextChanged.connect(get_set_option_lambda(voice, key))
                label_text = f"""{key}"""
                label = aqt.qt.QLabel(label_text)
                self.voice_options_layout.addWidget(label, row, 0, 1, 1)
                self.voice_options_layout.addWidget(widget, row, 1, 1, 1)
                self.voice_options_widgets[widget_name] = widget
            elif option_type == options.ParameterType.text:
                # create a text input field
                widget = aqt.qt.QLineEdit()
                widget.setObjectName(widget_name)
                widget.setText(value.get('default', ''))
                widget.textChanged.connect(get_set_option_lambda(voice, key))
                label_text = f"""{key}"""
                label = aqt.qt.QLabel(label_text)
                self.voice_options_layout.addWidget(label, row, 0, 1, 1)
                self.voice_options_layout.addWidget(widget, row, 1, 1, 1)
                self.voice_options_widgets[widget_name] = widget
            else:
                raise Exception(f"voice option type not supported: {value['type']}")
            row += 1

        # ── Piper JP/KR Clarification ──
        if voice.service == 'Piper':
            is_jp_kr = any(l.lang_code in ['ja', 'jpn', 'ko', 'kor'] for l in voice.languages)
            if is_jp_kr:
                self.piper_warning_label.setText("Note: Official Piper releases currently have limited/no support for Japanese/Korean. These voices may be experimental or unavailable.")
                self.piper_warning_label.setVisible(True)
            else:
                self.piper_warning_label.setVisible(False)
        else:
            self.piper_warning_label.setVisible(False)

        # if we are in the single voice mode, set the mode on the voice selection model
        if self.voice_selection_model.selection_mode == constants.VoiceSelectionMode.single:
            self.voice_selection_model.set_voice(config_models.VoiceWithOptions(voice.voice_id, self.current_voice_options))
            self.notify_model_update()

    def filter_and_draw_voices(self, _=None):
        logger.info('filter_and_draw_voices')
        voice_list = self.voice_list
        logger.debug(f'initial voice count: {len(voice_list)}')
        
        # check filtering by audio language
        if self.audio_languages_combobox.currentIndex() > 1:
            audio_language_name = self.audio_languages_combobox.currentText()
            voice_list = [voice for voice in voice_list if any(al.audio_lang_name == audio_language_name for al in voice.audio_languages)]
            
        # check filtering by language
        if self.languages_combobox.currentIndex() > 1:
            language_name = self.languages_combobox.currentText()
            voice_list = [voice for voice in voice_list if any(l.lang_name == language_name for l in voice.languages)]
            
        # check filtering by service
        if self.services_combobox.currentIndex() > 1:
            service = self.services_combobox.currentText()
            voice_list = [voice for voice in voice_list if voice.service == service] 
            
        # check filtering by gender
        if self.genders_combobox.currentIndex() > 1:
            gender_name = self.genders_combobox.currentText()
            voice_list = [voice for voice in voice_list if voice.gender.name == gender_name]
            
        def voice_sort_key(voice):
            return str(voice)
            
        # sort
        voice_list.sort(key=voice_sort_key)
        self.filtered_voice_list = voice_list
        self.draw_all_voices(self.filtered_voice_list)

    def draw_all_voices(self, voice_list):
        self.voices_combobox.clear()
        self.voices_combobox.addItems([str(voice) for voice in voice_list])
        logger.debug(f'voices_combobox has {self.voices_combobox.count()} items')

    def clear_voice_list_grid_layout(self):
        for i in reversed(range(self.voice_list_grid_layout.count())): 
            self.voice_list_grid_layout.itemAt(i).widget().setParent(None)        

    def redraw_selected_voices(self):
        # clear all voices from the grid
        self.clear_voice_list_grid_layout()

        if isinstance(self.voice_selection_model, config_models.VoiceSelectionSingle):
            return

        def get_remove_lambda(selection_model, voice_with_options_random, redraw_fn, notify_model_update_fn):
            def remove():
                # remove this entry (locate by equality)
                selection_model.voice_list.remove(voice_with_options_random)
                redraw_fn()
                notify_model_update_fn()
            return remove

        def get_move_up_lambda(selection_model, voice_with_options_priority, redraw_fn, notify_model_update_fn):
            def up():
                selection_model.move_up_voice(voice_with_options_priority)
                redraw_fn()
                notify_model_update_fn()
            return up

        def get_move_down_lambda(selection_model, voice_with_options_priority, redraw_fn, notify_model_update_fn):
            def down():
                selection_model.move_down_voice(voice_with_options_priority)
                redraw_fn()
                notify_model_update_fn()
            return down
        
        # draw all voices
        lang = self.hypertts.get_ui_language()
        row = 0
        for voice_entry in self.voice_selection_model.voice_list:
            column_index = 0
            # need to convert the voice with options entry to a string to show the user
            voice_id = voice_entry.voice_id
            assert isinstance(voice_id, voice_module.TtsVoiceId_v3), f"Expected voice_id to be TtsVoiceId_v3, got {type(voice_id).__name__}"
            # need to locate the voice for this voice_id
            voice = self.hypertts.service_manager.locate_voice(voice_id)
            # generate the string representation
            voice_with_options_str = voice_module.generate_voice_with_options_str(voice, voice_entry.options)
            self.voice_list_grid_layout.addWidget(aqt.qt.QLabel(voice_with_options_str), row, column_index, 1, 1)
            column_index += 1
            if isinstance(self.voice_selection_model, config_models.VoiceSelectionRandom):
                # add weight widget
                weight_widget = aqt.qt.QSpinBox()
                weight_widget.setValue(voice_entry.random_weight)
                def get_change_random_weight_lambda(voice_entry, notify_model_update_fn):
                    def set_random_weight(value):
                        voice_entry.random_weight = value
                        notify_model_update_fn()
                    return set_random_weight
                weight_widget.valueChanged.connect(get_change_random_weight_lambda(voice_entry, self.notify_model_update))
                self.voice_list_grid_layout.addWidget(weight_widget, row, column_index, 1, 1)
                column_index += 1
            # add remove button
            remove_button = aqt.qt.QPushButton(i18n.get_text("voice_button_remove_voice", lang))
            remove_button.setObjectName(f'remove_voice_row_{row}')
            self.voice_list_grid_layout.addWidget(remove_button, row, column_index, 1, 1)
            column_index += 1
            remove_button.pressed.connect(get_remove_lambda(self.voice_selection_model, voice_entry, self.redraw_selected_voices, self.notify_model_update))
            # add up/down buttons
            if isinstance(self.voice_selection_model, config_models.VoiceSelectionPriority):
                # add weight widget
                up_button = aqt.qt.QPushButton(i18n.get_text("voice_button_move_up", lang))
                down_button = aqt.qt.QPushButton(i18n.get_text("voice_button_move_down", lang))
                up_button.pressed.connect(get_move_up_lambda(self.voice_selection_model, voice_entry, self.redraw_selected_voices, self.notify_model_update))
                down_button.pressed.connect(get_move_down_lambda(self.voice_selection_model, voice_entry, self.redraw_selected_voices, self.notify_model_update))

                self.voice_list_grid_layout.addWidget(up_button, row, column_index, 1, 1)
                column_index += 1
                self.voice_list_grid_layout.addWidget(down_button, row, column_index, 1, 1)
                column_index += 1

            row += 1

    def serialize(self):
        return self.voice_selection_model.serialize()
