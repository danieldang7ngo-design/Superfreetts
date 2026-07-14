import sys
import aqt.qt
import copy


from typing import List, Optional

from . import component_common
from . import component_source
from . import component_target
from . import component_voiceselection
from . import component_text_processing
from . import component_batch_preview
from . import component_label_preview
from . import config_models
from . import constants
# from . import constants_events removed
from .stats import Event, EventMode
from . import stats
from . import errors
from . import gui_utils
from . import logging_utils
from . import i18n
logger = logging_utils.get_child_logger(__name__)

sc = stats.StatsContext(stats.EventContext.generate)

class ComponentBatch(component_common.ConfigComponentBase):
    MIN_WIDTH_COMPONENT = 420
    MIN_HEIGHT = 250

    def __init__(self, hypertts, dialog):
        self.hypertts = hypertts
        self.dialog = dialog
        self.batch_model = config_models.BatchConfig(self.hypertts.anki_utils)
        self.model_changed = False
        self.note = None
        self.last_saved_preset_id = None
        self.editor_new_preset_id = None

        lang = self.hypertts.get_ui_language()

        # create certain widgets upfront
        self.profile_name_combobox = aqt.qt.QComboBox()
        self.profile_name_combobox.setMinimumWidth(150)
        self.profile_name_combobox.setMaximumWidth(250)
        self.combobox_suspend_events = False
        self.profile_name_combobox.currentIndexChanged.connect(self.profile_combobox_changed)
        self.show_settings_button = aqt.qt.QPushButton(i18n.get_text("batch_button_hide_settings", lang))
        self.preview_sound_button = aqt.qt.QPushButton(i18n.get_text("batch_button_preview_sound", lang))
        self.apply_button = aqt.qt.QPushButton(i18n.get_text("batch_button_generate_audio", lang))
        self.cancel_button = aqt.qt.QPushButton(i18n.get_text("button_cancel", lang))
        self.profile_new_button = aqt.qt.QPushButton(i18n.get_text("button_new", lang))
        self.profile_new_button.setToolTip(i18n.get_text("batch_tooltip_new_preset", lang))
        gui_utils.configure_pastel_button(self.profile_new_button, style_name="blue", font_size=10)

        self.profile_duplicate_button = aqt.qt.QPushButton(i18n.get_text("button_duplicate", lang))
        self.profile_duplicate_button.setToolTip(i18n.get_text("batch_tooltip_duplicate_preset", lang))
        gui_utils.configure_pastel_button(self.profile_duplicate_button, style_name="purple", font_size=10)

        self.profile_save_button = aqt.qt.QPushButton(i18n.get_text("button_save", lang))
        self.profile_save_button.setToolTip(i18n.get_text("batch_tooltip_save_preset", lang))
        gui_utils.configure_pastel_button(self.profile_save_button, style_name="emerald", font_size=10)

        self.profile_rename_button = aqt.qt.QPushButton(i18n.get_text("button_rename", lang))
        self.profile_rename_button.setToolTip(i18n.get_text("batch_tooltip_rename_preset", lang))
        gui_utils.configure_pastel_button(self.profile_rename_button, style_name="amber", font_size=10)

        self.profile_delete_button = aqt.qt.QPushButton(i18n.get_text("button_delete", lang))
        self.profile_delete_button.setToolTip(i18n.get_text("batch_tooltip_delete_preset", lang))
        gui_utils.configure_pastel_button(self.profile_delete_button, style_name="rose", font_size=10)

        self.profile_save_and_close_button = aqt.qt.QPushButton(i18n.get_text("button_save_and_close", lang))
        self.profile_save_and_close_button.setToolTip(i18n.get_text("batch_tooltip_save_and_close", lang))
        gui_utils.configure_pastel_button(self.profile_save_and_close_button, style_name="emerald", is_primary=True)



    def configure_browser(self, note_id_list):
        self.note_id_list = note_id_list
        field_list = self.hypertts.get_all_fields_from_notes(note_id_list)
        if len(field_list) == 0:
            raise Exception(i18n.get_text("error_no_fields_found", self.hypertts.get_ui_language()).format(len(note_id_list)))
        self.source = component_source.BatchSource(
            self.hypertts,
            field_list,
            self.source_model_updated,
            show_use_selection=False,
        )
        self.target = component_target.BatchTarget(self.hypertts, field_list, self.target_model_updated)
        self.voice_selection = component_voiceselection.VoiceSelection(self.hypertts, self.dialog, self.voice_selection_model_updated)
        self.text_processing = component_text_processing.TextProcessing(self.hypertts, self.text_processing_model_updated)
        self.preview = component_batch_preview.BatchPreview(self.hypertts, self.dialog, self.note_id_list, 
            self.sample_selected, self.apply_notes_batch_start, self.apply_notes_batch_end,
            notes_loaded_callback=self._on_all_notes_loaded)
        self.editor_mode = False
        self.show_settings = True

    def configure_editor(self, editor_context: config_models.EditorContext):
        self.editor_context = editor_context
        self.note = editor_context.note
        self.editor = editor_context.editor
        self.add_mode = editor_context.add_mode
        field_list = list(self.note.keys())
        self.source = component_source.BatchSource(
            self.hypertts,
            field_list,
            self.source_model_updated,
            show_use_selection=True,
        )
        self.target = component_target.BatchTarget(self.hypertts, field_list, self.target_model_updated)
        self.voice_selection = component_voiceselection.VoiceSelection(self.hypertts, self.dialog, self.voice_selection_model_updated)
        self.text_processing = component_text_processing.TextProcessing(self.hypertts, self.text_processing_model_updated)
        self.preview = component_label_preview.LabelPreview(self.hypertts, self.note)
        self.editor_mode = True

    def update_profile_dropdown(self, name, preset_id=None):
        self.combobox_suspend_events = True
        self.profile_name_combobox.clear()
        presets = self.hypertts.get_preset_list()
        for p in presets:
            self.profile_name_combobox.addItem(p.name, p.id)
            
        if preset_id:
            idx = self.profile_name_combobox.findData(preset_id)
            if idx >= 0:
                self.profile_name_combobox.setCurrentIndex(idx)
                self.profile_name_combobox.setItemText(idx, name)
            else:
                self.profile_name_combobox.addItem(name, preset_id)
                self.profile_name_combobox.setCurrentIndex(self.profile_name_combobox.count() - 1)
        else:
            self.profile_name_combobox.addItem(name, "UNSAVED_NEW_PRESET")
            self.profile_name_combobox.setCurrentIndex(self.profile_name_combobox.count() - 1)
            
        self.combobox_suspend_events = False

    def profile_combobox_changed(self, index):
        if getattr(self, 'combobox_suspend_events', False) or index < 0:
            return
        preset_id = self.profile_name_combobox.itemData(index)
        if preset_id == "UNSAVED_NEW_PRESET":
            return
             
        if hasattr(self, 'batch_model') and preset_id != getattr(self.batch_model, 'uuid', None):
            self.save_profile_if_changed()
            self.load_preset(preset_id)

    def build_new_preset_model(self, preset_name=None):
        if preset_name == None:
            preset_name = self.hypertts.get_next_preset_name()

        field_list = self.source.field_list
        source_field = field_list[0]
        target_field = field_list[0]

        voice_list = getattr(self.voice_selection, 'voice_list', None)
        if voice_list == None or len(voice_list) == 0:
            voice_list = self.hypertts.service_manager.full_voice_list()
        if len(voice_list) == 0:
            raise errors.NoVoicesAvailable()

        model = config_models.BatchConfig(self.hypertts.anki_utils)
        model.name = preset_name
        model.set_source(config_models.BatchSource(
            mode=constants.BatchMode.simple,
            source_field=source_field,
            use_selection=False,
        ))
        model.set_target(config_models.BatchTarget(target_field=target_field))

        voice_selection = config_models.VoiceSelectionSingle()
        voice_selection.set_voice(config_models.VoiceWithOptions(voice_list[0].voice_id, {}))
        model.set_voice_selection(voice_selection)
        model.set_text_processing(config_models.TextProcessing())
        return model

    def new_preset(self, preset_name = None):
        """start with a new preset"""
        self.batch_model = self.build_new_preset_model(preset_name)
        if hasattr(self, 'tabs'):
            self.load_model(self.batch_model)
        else:
            self.update_profile_dropdown(self.batch_model.name, getattr(self.batch_model, 'uuid', None))
        self.model_changed = True
        self.update_save_profile_button_state()
        self.disable_delete_profile_button()

    def new_preset_after_delete(self):
        """new preset after user deleted the existing one"""
        # note: don't create new model, just reset the uuid, otherwise members of BatchConfig won't be initialized
        new_preset_name = self.hypertts.get_next_preset_name()
        self.batch_model.reset_uuid(self.hypertts.anki_utils)
        self.batch_model.name = new_preset_name
        self.update_profile_dropdown(new_preset_name, getattr(self.batch_model, 'uuid', None))
        self.model_changed = True
        self.update_save_profile_button_state()
        self.disable_delete_profile_button()

    def load_preset(self, preset_id):
        model = self.hypertts.load_preset(preset_id)
        self.load_model(model)
        self.enable_delete_profile_button()
        self.focus_apply_button()

    def load_model(self, model):
        logger.info('load_model')
        self.batch_model = model
        # disseminate to all components
        self.update_profile_dropdown(model.name, getattr(model, 'uuid', None))
        self.source.load_model(model.source)
        self.target.load_model(model.target)
        self.voice_selection.load_model(model.voice_selection)
        self.text_processing.load_model(model.text_processing)
        self.preview.load_model(self.batch_model)
        self.reset_apply_button_idle()
        


        self.model_changed = False
        self.update_save_profile_button_state()

        logger.debug('load_model')

    def reset_apply_button_idle(self):
        lang = self.hypertts.get_ui_language()
        if self.editor_mode:
            self.apply_button.setText(i18n.get_text("batch_button_apply_to_note", lang))
        else:
            self.apply_button.setText(i18n.get_text("batch_button_generate_audio", lang))

    def _on_all_notes_loaded(self):
        self.apply_button.setEnabled(True)

    def get_model(self):
        return self.batch_model

    def source_model_updated(self, model):
        logger.info(f'source_model_updated: {model}')
        self.batch_model.set_source(model)
        self.model_part_updated_common()

    def target_model_updated(self, model):
        logger.info('target_model_updated')
        self.batch_model.set_target(model)
        self.model_part_updated_common()

    def voice_selection_model_updated(self, model):
        logger.info('voice_selection_model_updated')
        self.batch_model.set_voice_selection(model)
        self.model_changed = True
        self.update_save_profile_button_state()
        if self.note != None and self.batch_model.source != None and self.batch_model.text_processing != None:
            try:
                source_text, processed_text = self.hypertts.get_source_processed_text(self.note, self.batch_model.source, self.batch_model.text_processing)
                self.voice_selection.sample_text_selected(processed_text)
            except Exception as e:
                logger.warning(f'could not set sample text: {e}')


    def text_processing_model_updated(self, model):
        logger.info('text_processing_model_updated')
        self.batch_model.text_processing = model
        self.model_part_updated_common()



    def model_part_updated_common(self):
        self.preview.load_model(self.batch_model)
        self.apply_button.setEnabled(False)
        self.model_changed = True
        # are we in editor mode ? if so, set the sample text on the voice component
        if self.note != None:
            if self.batch_model.source != None and self.batch_model.text_processing != None:
                try:
                    source_text, processed_text = self.hypertts.get_source_processed_text(self.note, self.batch_model.source, self.batch_model.text_processing)
                    self.voice_selection.sample_text_selected(processed_text)
                except Exception as e:
                    logger.warning(f'could not set sample text: {e}')
        self.update_save_profile_button_state()

    def update_save_profile_button_state(self):
        if self.model_changed:
            self.enable_save_profile_button()
        else:
            self.disable_save_profile_button()

    def enable_save_profile_button(self):
        logger.info('enable_save_profile_button')
        self.profile_save_button.setEnabled(True)
        self.profile_save_button.setProperty("cssClass", "btnPastelEmerald")
        self.profile_save_button.style().unpolish(self.profile_save_button)
        self.profile_save_button.style().polish(self.profile_save_button)

    def disable_save_profile_button(self):
        logger.info('disable_save_profile_button')
        self.profile_save_button.setEnabled(False)
        self.profile_save_button.setProperty("cssClass", "")
        self.profile_save_button.style().unpolish(self.profile_save_button)
        self.profile_save_button.style().polish(self.profile_save_button)

    def enable_delete_profile_button(self):
        self.profile_delete_button.setEnabled(True)

    def disable_delete_profile_button(self):
        self.profile_delete_button.setEnabled(False)

    def focus_apply_button(self):
        self.apply_button.setFocus()

    def sample_selected(self, note_id, text):
        self.voice_selection.sample_text_selected(text)
        self.note = self.hypertts.anki_utils.get_note_by_id(note_id)
        self.preview_sound_button.setEnabled(True)
        lang = self.hypertts.get_ui_language()
        self.preview_sound_button.setText(i18n.get_text("batch_button_preview_sound", lang))

    def _create_collapsible_toggle(self, text):
        button = aqt.qt.QToolButton()
        button.setText(text)
        button.setArrowType(aqt.qt.Qt.ArrowType.RightArrow)
        button.setToolButtonStyle(aqt.qt.Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        button.setProperty("cssClass", "collapsibleToggle")
        button.setSizePolicy(aqt.qt.QSizePolicy.Policy.Expanding, aqt.qt.QSizePolicy.Policy.Fixed)
        return button

    def _set_collapsible_toggle_open(self, button, visible):
        arrow_type = aqt.qt.Qt.ArrowType.DownArrow if visible else aqt.qt.Qt.ArrowType.RightArrow
        button.setArrowType(arrow_type)

    def _build_field_mapping_tab(self):
        """Build a merged Source + Target tab with collapsible advanced sections."""
        lang = self.hypertts.get_ui_language()
        scroll_area = aqt.qt.QScrollArea()
        scroll_area.setWidgetResizable(True)
        container = aqt.qt.QWidget()
        main_layout = aqt.qt.QVBoxLayout(container)

        # === Source Field (simple dropdown — always visible) ===
        source_group = aqt.qt.QGroupBox(i18n.get_text("batch_group_source_field", lang))
        source_vlayout = aqt.qt.QVBoxLayout()
        source_vlayout.addWidget(aqt.qt.QLabel(i18n.get_text("batch_label_select_source", lang)))

        # Draw the full source component (creates all widgets + wires events)
        self.source.draw()
        # Re-use the source widgets from the source component.
        source_vlayout.addWidget(self.source.source_field_combobox)
        source_vlayout.addWidget(self.source.source_field_error_label)
        if self.source.show_use_selection:
            source_vlayout.addWidget(self.source.use_selection_checkbox)
        source_group.setLayout(source_vlayout)
        main_layout.addWidget(source_group)

        # === Target Field (simple dropdown — always visible) ===
        target_group = aqt.qt.QGroupBox(i18n.get_text("batch_group_target_field", lang))
        target_vlayout = aqt.qt.QVBoxLayout()
        target_vlayout.addWidget(aqt.qt.QLabel(i18n.get_text("batch_label_select_target", lang)))

        # Draw the full target component (creates all widgets + wires events)
        self.target.draw()
        target_vlayout.addWidget(self.target.target_field_combobox)
        target_vlayout.addWidget(self.target.target_field_error_label)
        target_group.setLayout(target_vlayout)
        main_layout.addWidget(target_group)

        self.text_processing_toggle = self._create_collapsible_toggle(i18n.get_text("tp_section_title", lang))
        main_layout.addWidget(self.text_processing_toggle)

        self.text_processing_section = aqt.qt.QWidget()
        text_processing_layout = aqt.qt.QVBoxLayout(self.text_processing_section)
        text_processing_layout.setContentsMargins(10, 5, 10, 5)
        text_processing_layout.addWidget(self.text_processing.draw(embedded=True))
        self.text_processing_section.setVisible(False)
        main_layout.addWidget(self.text_processing_section)

        def toggle_text_processing():
            visible = not self.text_processing_section.isVisible()
            self.text_processing_section.setVisible(visible)
            self._set_collapsible_toggle_open(self.text_processing_toggle, visible)
        self.text_processing_toggle.pressed.connect(toggle_text_processing)

        # === Sound Tag Options (collapsible) ===
        self.sound_tag_toggle = self._create_collapsible_toggle(i18n.get_text("batch_toggle_sound_tag", lang))
        main_layout.addWidget(self.sound_tag_toggle)

        self.sound_tag_section = aqt.qt.QWidget()
        sound_tag_layout = aqt.qt.QVBoxLayout(self.sound_tag_section)
        sound_tag_layout.setContentsMargins(10, 5, 10, 5)

        # Text and Sound Tag group
        ts_group = aqt.qt.QGroupBox(i18n.get_text("batch_group_sound_tag_handling", lang))
        ts_vlayout = aqt.qt.QVBoxLayout()
        ts_label = aqt.qt.QLabel(constants.GUI_TEXT_TARGET_TEXT_AND_SOUND)
        ts_label.setWordWrap(True)
        ts_vlayout.addWidget(ts_label)
        ts_vlayout.addWidget(self.target.radio_button_sound_only)
        ts_vlayout.addWidget(self.target.radio_button_text_sound)
        ts_group.setLayout(ts_vlayout)
        sound_tag_layout.addWidget(ts_group)

        # Existing Sound Tag group
        es_group = aqt.qt.QGroupBox(i18n.get_text("batch_group_existing_sound_tag", lang))
        es_vlayout = aqt.qt.QVBoxLayout()
        es_label = aqt.qt.QLabel(constants.GUI_TEXT_TARGET_REMOVE_SOUND_TAG)
        es_label.setWordWrap(True)
        es_vlayout.addWidget(es_label)
        es_vlayout.addWidget(self.target.radio_button_remove_sound)
        es_vlayout.addWidget(self.target.radio_button_keep_sound)
        es_group.setLayout(es_vlayout)
        sound_tag_layout.addWidget(es_group)

        self.sound_tag_section.setVisible(False)
        main_layout.addWidget(self.sound_tag_section)

        def toggle_sound_tag():
            visible = not self.sound_tag_section.isVisible()
            self.sound_tag_section.setVisible(visible)
            self._set_collapsible_toggle_open(self.sound_tag_toggle, visible)
        self.sound_tag_toggle.pressed.connect(toggle_sound_tag)

        # === Advanced Source Mode (collapsible) ===
        self.source_mode_toggle = self._create_collapsible_toggle(i18n.get_text("batch_toggle_advanced_source", lang))
        main_layout.addWidget(self.source_mode_toggle)

        self.source_mode_section = aqt.qt.QWidget()
        source_mode_layout = aqt.qt.QVBoxLayout(self.source_mode_section)
        source_mode_layout.setContentsMargins(10, 5, 10, 5)

        # Source Mode selector
        mode_group = aqt.qt.QGroupBox(i18n.get_text("batch_group_source_mode", lang))
        mode_vlayout = aqt.qt.QVBoxLayout()
        mode_label = aqt.qt.QLabel(gui_utils.process_label_text(constants.GUI_TEXT_SOURCE_MODE))
        mode_label.setWordWrap(True)
        mode_vlayout.addWidget(mode_label)
        mode_vlayout.addWidget(self.source.batch_mode_combobox)
        mode_group.setLayout(mode_vlayout)
        source_mode_layout.addWidget(mode_group)

        # Source Config Stack (Template/Advanced Template)
        config_group = aqt.qt.QGroupBox('Source Configuration')
        config_vlayout = aqt.qt.QVBoxLayout()
        config_vlayout.addWidget(self.source.source_config_stack)
        config_group.setLayout(config_vlayout)
        source_mode_layout.addWidget(config_group)

        self.source_mode_section.setVisible(False)
        main_layout.addWidget(self.source_mode_section)

        def toggle_source_mode():
            visible = not self.source_mode_section.isVisible()
            self.source_mode_section.setVisible(visible)
            self._set_collapsible_toggle_open(self.source_mode_toggle, visible)
        self.source_mode_toggle.pressed.connect(toggle_source_mode)

        main_layout.addStretch()

        scroll_area.setWidget(container)
        return scroll_area

    def draw(self, layout):
        lang = self.hypertts.get_ui_language()
        self.content_widget = aqt.qt.QWidget()
        self.vlayout = aqt.qt.QVBoxLayout(self.content_widget)
        self.vlayout.setContentsMargins(6, 6, 6, 6)
        self.vlayout.setSpacing(10)

        # profile management
        # ==================

        top_layout = aqt.qt.QVBoxLayout()
        profile_row = aqt.qt.QHBoxLayout()
        profile_row.addWidget(aqt.qt.QLabel(i18n.get_text("batch_button_preset", lang)))

        font = aqt.qt.QFont()
        font.setBold(True)
        self.profile_name_combobox.setFont(font)

        profile_row.addWidget(self.profile_name_combobox, 1)
        # logo header
        profile_row.addLayout(gui_utils.get_superfreetts_label_header(self.hypertts.superfreetts_pro_enabled()))
        top_layout.addLayout(profile_row)

        preset_actions_row = aqt.qt.QHBoxLayout()
        for button in [
            self.profile_new_button,
            self.profile_save_button,
            self.profile_duplicate_button,
            self.profile_rename_button,
            self.profile_delete_button,
        ]:
            preset_actions_row.addWidget(button)
        preset_actions_row.addStretch()
        top_layout.addLayout(preset_actions_row)
        self.vlayout.addLayout(top_layout)

        self.profile_new_button.pressed.connect(self.new_profile_button_pressed)
        self.profile_save_button.pressed.connect(self.save_profile_button_pressed)
        self.profile_delete_button.pressed.connect(self.delete_profile_button_pressed)
        self.profile_rename_button.pressed.connect(self.rename_profile_button_pressed)
        self.profile_duplicate_button.pressed.connect(self.duplicate_profile_button_pressed)

        # preset settings tabs
        # ====================

        self.tabs = aqt.qt.QTabWidget()

        # Tab 1: Field Mapping (left, default active)
        self.field_mapping_widget = self._build_field_mapping_tab()
        self.tabs.addTab(self.field_mapping_widget, i18n.get_text("tab_field_mapping", lang))

        # Tab 2: Voice Selection (right)
        self.tabs.addTab(self.voice_selection.draw(), i18n.get_text("tab_voice_selection", lang))

        if self.editor_mode == False:
            self.splitter = aqt.qt.QSplitter(aqt.qt.Qt.Orientation.Horizontal)
            self.splitter.addWidget(self.tabs)

            self.preview_widget = aqt.qt.QWidget()
            self.preview_widget.setLayout(self.preview.draw())
            self.splitter.addWidget(self.preview_widget)

            # UI Fix: Prevent accidental collapsing of the results tab and ensure smooth resizing
            self.splitter.setChildrenCollapsible(False)
            self.splitter.setCollapsible(0, True)   # Settings can be hidden via button
            self.splitter.setCollapsible(1, False)  # Results preview should stay visible
            self.tabs.setMinimumWidth(240)
            self.preview_widget.setMinimumWidth(240)
            self.splitter.setStretchFactor(0, 1)
            self.splitter.setStretchFactor(1, 1)

            self.vlayout.addWidget(self.splitter, 1) # splitter is what should stretch
        else:
            self.vlayout.addWidget(self.tabs, 1) # the tabs should stretch
            self.preview_widget = aqt.qt.QWidget()
            self.preview_widget.setLayout(self.preview.draw())            
            self.vlayout.addWidget(self.preview_widget)


        # setup bottom buttons
        # ====================

        hlayout = aqt.qt.QHBoxLayout()
        hlayout.setSpacing(6)
        hlayout.setContentsMargins(0, 5, 0, 5)
        hlayout.addStretch()

        # show settings button
        if not self.editor_mode:
            self.show_settings_button.setText(i18n.get_text("batch_button_hide_settings", lang))
            gui_utils.configure_secondary_button(self.show_settings_button)
            hlayout.addWidget(self.show_settings_button)
            
        # preview button
        if not self.editor_mode:
            self.preview_sound_button.setText(i18n.get_text("batch_button_select_note_to_preview", lang))
            self.preview_sound_button.setEnabled(False)
        else:
            self.preview_sound_button.setText(i18n.get_text("button_preview", lang))
        gui_utils.configure_pastel_button(self.preview_sound_button, style_name="blue", font_size=10)
        hlayout.addWidget(self.preview_sound_button)
        
        # apply button
        if self.editor_mode:
            apply_text = i18n.get_text("batch_button_apply_to_note", lang)
        else:
            apply_text = i18n.get_text("batch_button_generate_audio", lang)
        self.apply_button.setText(apply_text)
        self.apply_button.setEnabled(False)
        if self.editor_mode == False:
            gui_utils.configure_pastel_button(self.apply_button, style_name="emerald", is_primary=True, font_size=11)
        hlayout.addWidget(self.apply_button)

        # save and close
        if self.editor_mode == True:
            self.profile_save_and_close_button.setText(i18n.get_text("button_save_and_close_simple", lang))
            hlayout.addWidget(self.profile_save_and_close_button)

        # cancel button
        self.cancel_button.setText(i18n.get_text("button_cancel", lang))
        gui_utils.configure_secondary_button(self.cancel_button, min_width=70)
        hlayout.addWidget(self.cancel_button)
        self.vlayout.addLayout(hlayout)

        self.show_settings_button.pressed.connect(self.show_settings_button_pressed)
        self.preview_sound_button.pressed.connect(self.sound_preview_button_pressed)
        self.apply_button.pressed.connect(self.apply_button_pressed)
        self.cancel_button.pressed.connect(self.cancel_button_pressed)
        self.profile_save_and_close_button.pressed.connect(self.profile_save_and_close_button_pressed)

        self.cancel_button.setFocus()

        layout.addWidget(gui_utils.make_scroll_area(self.content_widget), 1)

    def get_min_size(self):
        return self.MIN_HEIGHT

    def no_settings_editor(self):
        # when launched from the editor
        self.dialog.setMinimumSize(self.MIN_WIDTH_COMPONENT, self.get_min_size())

    def collapse_settings(self):
        # when we have already loaded a batch
        # We use a very small value instead of exactly 0 to ensure predictable splitter state if needed,
        # but QSplitter generally handles 0 fine when collapsible is True.
        self.splitter.setSizes([0, 1000]) 
        # Note: dialog minimum size remains respected
        self.show_settings = False
        lang = self.hypertts.get_ui_language()
        self.show_settings_button.setText(i18n.get_text("batch_button_show_settings", lang))

    def display_settings(self):
        # when configuring a new batch
        # Use a balanced size distribution
        self.splitter.setSizes([500, 500])
        self.show_settings = True
        lang = self.hypertts.get_ui_language()
        self.show_settings_button.setText(i18n.get_text("batch_button_hide_settings", lang))

    def new_profile_button_pressed(self):
        self.save_profile_if_changed()
        self.new_preset()
        if not self.editor_mode and not self.show_settings:
            self.display_settings()
        self.tabs.setCurrentIndex(0)

    def duplicate_profile_button_pressed(self):
        with self.hypertts.error_manager.get_single_action_context('Duplicating Profile'):
            duplicate_model = copy.deepcopy(self.get_model())
            duplicate_model.reset_uuid(self.hypertts.anki_utils)
            duplicate_model.name = f'{duplicate_model.name} (copy)'
            self.load_model(duplicate_model)
            self.model_changed = True
            self.update_save_profile_button_state()
            self.disable_delete_profile_button()


    def save_profile(self):
        with self.hypertts.error_manager.get_single_action_context('Saving Preset'):
            self.hypertts.save_preset(self.get_model())
            self.model_changed = False
            self.last_saved_preset_id = self.get_model().uuid
            self.update_save_profile_button_state()
            self.enable_delete_profile_button()

    def save_profile_if_changed(self):
        if self.model_changed:
            # does the user want to save the profile ?
            lang = self.hypertts.get_ui_language()
            proceed = self.hypertts.anki_utils.ask_user(i18n.get_text("dialog_save_changes", lang), self.dialog)
            if proceed:
                self.save_profile()

    def save_profile_button_pressed(self):
        self.save_profile()

    def rename_profile_button_pressed(self):
        current_profile_name = self.batch_model.name
        lang = self.hypertts.get_ui_language()
        new_profile_name, result = self.hypertts.anki_utils.ask_user_get_text(
            i18n.get_text("dialog_enter_new_name", lang), self.dialog, current_profile_name, i18n.get_text("dialog_rename_title", lang))
        if result == 1:
            # user pressed ok, rename profile
            self.batch_model.name = new_profile_name
            # reflect new name
            self.update_profile_dropdown(new_profile_name, getattr(self.batch_model, 'uuid', None))
            # enable save button
            self.model_changed = True
            self.update_save_profile_button_state()

    def delete_profile_button_pressed(self):
        profile_name = self.batch_model.name
        preset_id = self.batch_model.uuid
        lang = self.hypertts.get_ui_language()
        proceed = self.hypertts.anki_utils.ask_user(i18n.get_text("dialog_delete_confirm", lang).format(profile_name), self.dialog)
        if proceed == True:
            with self.hypertts.error_manager.get_single_action_context('Deleting Preset'):
                self.hypertts.delete_preset(preset_id)
                self.new_preset_after_delete()

    def show_settings_button_pressed(self):
        if self.show_settings:
            self.collapse_settings()
        else:
            self.display_settings()

    def toggle_advanced(self):
        if not hasattr(self, 'text_processing_tab_index'):
            return
        self.advanced_visible = not self.advanced_visible
        self.tabs.setTabVisible(self.text_processing_tab_index, self.advanced_visible)
        lang = self.hypertts.get_ui_language()
        
        if self.advanced_visible:
            self.advanced_toggle_button.setText(i18n.get_text("batch_advanced_toggle_on", lang))
            self.advanced_toggle_button.setToolTip(i18n.get_text("batch_tooltip_hide_advanced", lang))
            self.advanced_toggle_button.setProperty("cssClass", "primaryButton")
            self.advanced_toggle_button.style().unpolish(self.advanced_toggle_button)
            self.advanced_toggle_button.style().polish(self.advanced_toggle_button)
        else:
            self.advanced_toggle_button.setText(i18n.get_text("batch_advanced_toggle_off", lang))
            self.advanced_toggle_button.setToolTip(i18n.get_text("batch_tooltip_show_advanced", lang))
            self.advanced_toggle_button.setProperty("cssClass", "secondaryButton")
            self.advanced_toggle_button.style().unpolish(self.advanced_toggle_button)
            self.advanced_toggle_button.style().polish(self.advanced_toggle_button)

    @sc.event(Event.click_preview)
    def sound_preview_button_pressed(self):
        # Determine selected note status on main thread. If generated audio exists, play it.
        note_status = None
        try:
            note_status = self.preview.get_selected_note_status()
        except Exception:
            note_status = None

        lang = self.hypertts.get_ui_language()
        # if selected and error -> tooltip, do nothing
        if note_status is not None and note_status.status == constants.BatchNoteStatus.Error:
            self.hypertts.anki_utils.tooltip_message(i18n.get_text("batch_button_select_note_to_preview", lang))
            return

        # if selected and cached sound exists -> play cached file
        if note_status is not None and note_status.sound_file:
            # compose full path from user_files dir
            user_files_dir = self.hypertts.anki_utils.get_user_files_dir()
            full_path = None
            try:
                import os
                full_path = os.path.join(user_files_dir, note_status.sound_file)
            except Exception:
                full_path = None
            if full_path:
                # show playing state then play
                self.preview_sound_button.setText(i18n.get_text("easy_button_previewing", lang))
                self.preview_sound_button.setEnabled(False)
                self.hypertts.anki_utils.play_sound(full_path)
                self.hypertts.anki_utils.run_on_main(self.finish_sound_preview)
                return

        # fallback: generate+play in background (existing behavior)
        self.disable_bottom_buttons()
        self.preview_sound_button.setText(i18n.get_text("easy_button_previewing", lang))
        self.hypertts.anki_utils.run_in_background(self.sound_preview_task, self.sound_preview_task_done)

    def profile_save_and_close_button_pressed(self):
        self.save_profile()
        self.editor_new_preset_id = self.last_saved_preset_id
        self.dialog.close()

    @sc.event(Event.click_add)
    def apply_button_pressed(self):
        with self.hypertts.error_manager.get_single_action_context('Applying Audio to Notes'):
            self.get_model().validate()
            logger.info('apply_button_pressed')
            if self.editor_mode:
                self.disable_bottom_buttons()
                self.apply_button.setText(i18n.get_text("easy_button_adding_audio", self.hypertts.get_ui_language()))
                self.hypertts.anki_utils.run_in_background(self.apply_note_editor_task, self.apply_note_editor_task_done)
            else:
                self.disable_bottom_buttons()
                if self.preview.has_pending_generated_audio():
                    self.apply_button.setText(i18n.get_text("batch_button_applying_audio", self.hypertts.get_ui_language()))
                    self.preview.apply_generated_audio_to_notes()
                else:
                    self.apply_button.setText(i18n.get_text("batch_button_generating_audio", self.hypertts.get_ui_language()))
                    self.preview.generate_audio_to_cache()

    @sc.event(Event.click_cancel)
    def cancel_button_pressed(self):
        self.dialog.close()

    def apply_note_editor_task(self):
        logger.debug('apply_note_editor_task')
        self.hypertts.editor_note_add_audio(self.batch_model, self.editor_context)
        return True

    def apply_note_editor_task_done(self, result):
        logger.debug('apply_note_editor_task_done')
        with self.hypertts.error_manager.get_single_action_context('Adding Audio to Note'):
            result = result.result()
            self.dialog.close()
        self.hypertts.anki_utils.run_on_main(self.finish_apply_note_editor)
    
    def finish_apply_note_editor(self):
        self.enable_bottom_buttons()
        lang = self.hypertts.get_ui_language()
        self.apply_button.setText(i18n.get_text("batch_button_apply_to_note", lang))

    def sound_preview_task(self):
        if self.note == None:
            raise errors.NoNotesSelectedPreview()
        self.hypertts.preview_note_audio(self.batch_model, self.note, None)
        return True

    def sound_preview_task_done(self, result):
        with self.hypertts.error_manager.get_single_action_context('Playing Sound Preview'):
            result = result.result()
        self.hypertts.anki_utils.run_on_main(self.finish_sound_preview)

    def finish_sound_preview(self):
        self.enable_bottom_buttons()
        lang = self.hypertts.get_ui_language()
        self.preview_sound_button.setText(i18n.get_text("batch_button_preview_sound", lang))

    def disable_bottom_buttons(self):
        self.preview_sound_button.setEnabled(False)
        self.apply_button.setEnabled(False)
        self.cancel_button.setEnabled(False)

    def enable_bottom_buttons(self):
        self.preview_sound_button.setEnabled(True)
        self.apply_button.setEnabled(True)
        self.cancel_button.setEnabled(True)

    def apply_notes_batch_start(self):
        lang = self.hypertts.get_ui_language()
        if self.preview.is_applying_generated_audio():
            self.apply_button.setText(i18n.get_text("batch_button_applying_audio", lang))
        else:
            self.apply_button.setText(i18n.get_text("batch_button_generating_audio", lang))
        self.apply_button.setEnabled(False)
        self.preview_sound_button.setEnabled(False)
        self.cancel_button.setEnabled(False)

    def batch_interrupted_button_setup(self):
        self.enable_bottom_buttons()
        lang = self.hypertts.get_ui_language()
        self.apply_button.setText(i18n.get_text("batch_button_generate_audio", lang))

    def batch_completed_button_setup(self):
        lang = self.hypertts.get_ui_language()
        self.cancel_button.setText(i18n.get_text("button_close", lang))
        # Keep cancel button as secondary, maybe emphasize it's done?
        # Actually standard secondary is fine for "Close"
        self.cancel_button.setEnabled(True)
        self.apply_button.setStyleSheet(None)
        self.apply_button.setText(i18n.get_text("batch_button_done", lang))

    def batch_ready_to_apply_button_setup(self):
        lang = self.hypertts.get_ui_language()
        self.cancel_button.setText(i18n.get_text("button_close", lang))
        self.cancel_button.setEnabled(True)
        self.preview_sound_button.setEnabled(True)
        self.apply_button.setEnabled(True)
        self.apply_button.setStyleSheet(None)
        self.apply_button.setText(i18n.get_text("batch_button_apply_generated_audio", lang))

    def apply_notes_batch_end(self, completed):
        if completed:
            if self.preview.has_pending_generated_audio():
                self.hypertts.anki_utils.run_on_main(self.batch_ready_to_apply_button_setup)
            else:
                self.hypertts.anki_utils.run_on_main(self.batch_completed_button_setup)
        else:
            self.hypertts.anki_utils.run_on_main(self.batch_interrupted_button_setup)

        

# factory and setup functions for ComponentBatch: only use those to create a ComponentBatch
# =========================================================================================

class BatchDialog(aqt.qt.QDialog):
    def __init__(self, hypertts):
        super(aqt.qt.QDialog, self).__init__()
        self.hypertts = hypertts
        # Cho phép dialog Collection Mode thu nhỏ/phóng to
        self.setWindowFlag(aqt.qt.Qt.WindowType.WindowMinMaxButtonsHint, True)
        self.setStyleSheet(gui_utils.get_dynamic_stylesheet())
        lang = self.hypertts.get_ui_language()
        self.setWindowTitle(i18n.get_text("dialog_collection_title", lang))
        self.main_layout = aqt.qt.QVBoxLayout(self)        

    def configure_browser_existing_preset(self, note_id_list, preset_id: str):
        self.batch_component = ComponentBatch(self.hypertts, self)
        self.batch_component.configure_browser(note_id_list)
        self.batch_component.draw(self.main_layout)
        self.batch_component.load_preset(preset_id)
        self.batch_component.collapse_settings()           

    def configure_browser_from_model(self, note_id_list, batch_model):
        self.batch_component = ComponentBatch(self.hypertts, self)
        self.batch_component.configure_browser(note_id_list)
        self.batch_component.draw(self.main_layout)
        self.batch_component.load_model(copy.deepcopy(batch_model))
        self.batch_component.collapse_settings()

    def configure_browser_new_preset(self, note_id_list, new_preset_name: str):
        self.batch_component = ComponentBatch(self.hypertts, self)
        self.batch_component.configure_browser(note_id_list)
        self.batch_component.new_preset(new_preset_name)
        self.batch_component.draw(self.main_layout)
        self.batch_component.display_settings()

    def configure_editor_new_preset(self, editor_context: config_models.EditorContext):
        batch_component = ComponentBatch(self.hypertts, self)
        batch_component.configure_editor(editor_context)
        new_preset_name = self.hypertts.get_next_preset_name()
        batch_component.new_preset(new_preset_name)
        batch_component.draw(self.main_layout)
        batch_component.no_settings_editor()
        self.batch_component = batch_component

    def configure_editor_existing_preset(self, editor_context: config_models.EditorContext, preset_id: str):
        batch_component = ComponentBatch(self.hypertts, self)
        batch_component.configure_editor(editor_context)
        batch_component.draw(self.main_layout)
        batch_component.load_preset(preset_id)
        batch_component.no_settings_editor()
        self.batch_component = batch_component        

    def verify_profile_saved(self):
        self.batch_component.save_profile_if_changed()

    def closeEvent(self, evnt):
        self.verify_profile_saved()
        super(aqt.qt.QDialog, self).closeEvent(evnt)

    @sc.event(Event.close)
    def close(self):
        self.verify_profile_saved()
        self.closed = True
        self.accept()

@sc.event(Event.open, EventMode.advanced_browser_existing_preset)
def create_component_batch_browser_existing_preset(hypertts, note_id_list, preset_id: str) -> ComponentBatch:
    if len(note_id_list) == 0:
        raise errors.NoNotesSelected()
    dialog = BatchDialog(hypertts)
    dialog.configure_browser_existing_preset(note_id_list, preset_id)
    hypertts.anki_utils.wait_for_dialog_input(dialog, constants.DIALOG_ID_BATCH)


def open_batch_dialog_for_model(hypertts, note_id_list, batch_model) -> ComponentBatch:
    if len(note_id_list) == 0:
        raise errors.NoNotesSelected()
    dialog = BatchDialog(hypertts)
    dialog.configure_browser_from_model(note_id_list, batch_model)
    hypertts.anki_utils.wait_for_dialog_input(dialog, constants.DIALOG_ID_BATCH)

@sc.event(Event.open, EventMode.advanced_browser_new_preset)
def create_component_batch_browser_new_preset(hypertts, note_id_list, new_preset_name: str) -> ComponentBatch:
    if len(note_id_list) == 0:
        raise errors.NoNotesSelected()    
    dialog = BatchDialog(hypertts)
    dialog.configure_browser_new_preset(note_id_list, new_preset_name)
    hypertts.anki_utils.wait_for_dialog_input(dialog, constants.DIALOG_ID_BATCH)

@sc.event(Event.open, EventMode.advanced_editor_existing_preset)
def create_dialog_editor_existing_preset(hypertts, editor_context: config_models.EditorContext, preset_id: str):
    dialog = BatchDialog(hypertts)
    dialog.configure_editor_existing_preset(editor_context, preset_id)
    hypertts.anki_utils.wait_for_dialog_input(dialog, constants.DIALOG_ID_BATCH)    

@sc.event(Event.open, EventMode.advanced_editor_new_preset)
def create_dialog_editor_new_preset(hypertts, editor_context: config_models.EditorContext):
    """get a new preset_id from the editor, and return the new preset_id"""
    dialog = BatchDialog(hypertts)
    dialog.configure_editor_new_preset(editor_context)
    hypertts.anki_utils.wait_for_dialog_input(dialog, constants.DIALOG_ID_BATCH)
    return dialog.batch_component.editor_new_preset_id
