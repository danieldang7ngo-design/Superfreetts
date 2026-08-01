import sys
import json

# pyqt
import aqt.qt


# anki imports
import aqt.qt
import aqt.editor
import aqt.gui_hooks
import aqt.sound
import aqt.utils
import anki.hooks

from typing import List, Tuple

# addon imports
from . import constants
# from . import constants_events removed
from . import stats
from . import config_models
from . import errors
from . import component_batch
from . import component_workflow
from . import component_realtime
from . import component_presetmappingrules
from . import component_services
from . import component_preferences
from . import component_settings
# from . import component_easy removed
# from . import component_choose_easy_advanced removed
from . import text_utils
from . import ttsplayer
from . import logging_utils
from . import gui_utils
from . import stats
from . import i18n
logger = logging_utils.get_child_logger(__name__)


class ConfigurationDialog(aqt.qt.QDialog):
    def __init__(self, hypertts):
        super(aqt.qt.QDialog, self).__init__()
        # lưu tham chiếu để tra ngôn ngữ giao diện
        self.hypertts = hypertts
        # Ensure all services are instantiated when configuration dialog opens
        self.hypertts.service_manager.instantiate_all_services()
        # Cho phép thu nhỏ/phóng to cửa sổ cấu hình (min/max buttons trên title bar)
        # Giúp user có thể mở rộng ra full màn hình khi cần xem nhiều services hơn
        self.setWindowFlag(aqt.qt.Qt.WindowType.WindowMinMaxButtonsHint, True)
        self.setStyleSheet(gui_utils.get_dynamic_stylesheet())
        self.configuration = component_services.ServicesPage(hypertts, self)
        self.configuration.load_model(hypertts.get_configuration())

    def setupUi(self):
        lang = self.hypertts.get_ui_language()
        self.setMinimumSize(500, 300)
        self.setWindowTitle(i18n.get_text("dialog_services_title", lang))
        self.main_layout = aqt.qt.QVBoxLayout(self)
        self.configuration.draw(self.main_layout)
        self.resize(500, 700)

    def close(self):
        self.accept()

class PreferencesDialog(aqt.qt.QDialog):
    def __init__(self, hypertts):
        super(aqt.qt.QDialog, self).__init__()
        self.hypertts = hypertts
        # Cho phép thu nhỏ/phóng to cho màn hình Preferences
        self.setWindowFlag(aqt.qt.Qt.WindowType.WindowMinMaxButtonsHint, True)
        self.setStyleSheet(gui_utils.get_dynamic_stylesheet())
        self.preferences = component_preferences.PreferencesPage(hypertts, self)
        self.preferences.load_model(hypertts.get_preferences())

    def setupUi(self):
        lang = self.hypertts.get_ui_language()
        self.setWindowTitle(i18n.get_text("dialog_preferences_title", lang))
        self.main_layout = aqt.qt.QVBoxLayout(self)
        self.preferences.draw(self.main_layout)
        self.resize(450, 500)

    def close(self):
        self.accept()

class DialogBase(aqt.qt.QDialog):
    def __init__(self):
        super(aqt.qt.QDialog, self).__init__()


class RealtimeDialog(DialogBase):
    def __init__(self, hypertts, card_ord):
        super(DialogBase, self).__init__()
        self.hypertts = hypertts
        # Cho phép thu nhỏ/phóng to cho dialog Realtime TTS
        self.setWindowFlag(aqt.qt.Qt.WindowType.WindowMinMaxButtonsHint, True)
        self.setStyleSheet(gui_utils.get_dynamic_stylesheet())
        self.realtime_component = component_realtime.ComponentRealtime(hypertts, self, card_ord)

    def setupUi(self):
        lang = self.hypertts.get_ui_language()
        self.setWindowTitle(i18n.get_text("dialog_realtime_title", lang))
        self.main_layout = aqt.qt.QVBoxLayout(self)
        self.realtime_component.draw(self.main_layout)

    def configure_note(self, note):
        self.realtime_component.configure_note(note)
        self.setupUi()
        self.realtime_component.load_existing_preset()

    def close(self):
        self.accept()        

def launch_configuration_dialog(hypertts):
    """
    DEPRECATED: Redirects to unified settings dialog (Services tab).
    Kept for backward compatibility with legacy entry points.
    Use launch_unified_dialog() for new code.
    """
    logger.info('launch_configuration_dialog (deprecated alias, redirecting to unified dialog)')
    launch_unified_dialog(hypertts, initial_tab=0)

def launch_services_configuration(hypertts):
    """
    DEPRECATED: Redirects to unified settings dialog (Services tab).
    Super Free TTS Lite compatibility wrapper.
    """
    logger.info('launch_services_configuration (deprecated alias, redirecting to unified dialog)')
    launch_unified_dialog(hypertts, initial_tab=0)

def launch_preferences_dialog(hypertts):
    """
    DEPRECATED: Redirects to unified settings dialog (Preferences tab).
    Kept for backward compatibility with legacy entry points.
    Use launch_unified_dialog() for new code.
    """
    logger.info('launch_preferences_dialog (deprecated alias, redirecting to unified dialog)')
    launch_unified_dialog(hypertts, initial_tab=1)        

def launch_unified_dialog(hypertts, initial_tab=0):
    """
    Launch unified Super Free TTS settings dialog (Services + Preferences in one dialog).
    P0 Phase implementation: new entry point for all settings.
    
    Args:
        hypertts: SuperFreeTTS instance
        initial_tab: Which tab to open initially (0=Services, 1=Preferences, 2=Donation, 3=About)
    """
    with hypertts.error_manager.get_single_action_context('Launching Unified Settings Dialog'):
        logger.info(f'launch_unified_dialog, initial_tab={initial_tab}')
        dialog = component_settings.SettingsDialog(hypertts, initial_tab=initial_tab, parent=aqt.mw)
        dialog.exec()

def launch_realtime_dialog_browser(hypertts, note_id_list):
    with hypertts.error_manager.get_single_action_context('Launching Super Free TTS Realtime Dialog from Browser'):
        if len(note_id_list) != 1:
            aqt.utils.showCritical(constants.GUI_TEXT_REALTIME_SINGLE_NOTE)
            return

        note = hypertts.anki_utils.get_note_by_id(note_id_list[0])
        note_model = note.note_type()
        templates = note_model['tmpls']
        card_ord = 0 # default
        if len(templates) > 1:
            # ask user to choose a template
            card_template_names = [x['name'] for x in templates]
            chosen_row = aqt.utils.chooseList(constants.TITLE_PREFIX + constants.GUI_TEXT_REALTIME_CHOOSE_TEMPLATE, card_template_names)
            logger.info(f'user chose row {chosen_row}')
            card_ord = chosen_row

        dialog = RealtimeDialog(hypertts, card_ord)
        dialog.configure_note(note)
        dialog.exec()

def remove_realtime_tts_tag(hypertts, browser, note_id_list):
    with hypertts.error_manager.get_single_action_context('Removing TTS Tag'):
        if len(note_id_list) != 1:
            aqt.utils.showCritical(constants.GUI_TEXT_REALTIME_SINGLE_NOTE)
            return

        note = hypertts.anki_utils.get_note_by_id(note_id_list[0])
        note_model = note.note_type()
        templates = note_model['tmpls']
        card_ord = 0 # default
        if len(templates) > 1:
            # ask user to choose a template
            card_template_names = [x['name'] for x in templates]
            chosen_row = aqt.utils.chooseList(constants.TITLE_PREFIX + constants.GUI_TEXT_REALTIME_CHOOSE_TEMPLATE, card_template_names)
            logger.info(f'user chose row {chosen_row}')
            card_ord = chosen_row

        hypertts.remove_tts_tags(note, card_ord)
        hypertts.anki_utils.info_message(constants.GUI_TEXT_REALTIME_REMOVED_TAG, browser)



def update_menu_language(hypertts):
    """Update the text of the menu items based on current UI language."""
    global ankivn_menu, action_unified_settings
    lang = hypertts.get_ui_language()
    if ankivn_menu:
        ankivn_menu.setTitle("AnkiVN")
    if action_unified_settings:
        action_unified_settings.setText(i18n.get_text("unified_settings_title", lang))
        action_unified_settings.setIcon(aqt.qt.QIcon(gui_utils.get_graphics_path(constants.GRAPHICS_ICON_HEADPHONES)))

def init(hypertts):
    gui_utils.install_global_wheel_filter()

    def browerMenusInit(browser: aqt.browser.Browser):
        lang = hypertts.get_ui_language()
        
        def get_launch_dialog_browser_new_fn(hypertts, browser):
            def launch():
                with hypertts.error_manager.get_single_action_context('Opening Super Free TTS Dialog from Browser'):
                    component_batch.create_component_batch_browser_new_preset(hypertts, browser.selectedNotes(), hypertts.get_next_preset_name())
                    # browser.model.reset() is deprecated and redundant when using CollectionOp
            return launch

        def get_launch_dialog_browser_existing_fn(hypertts, browser, preset_id: str):
            def launch():
                with hypertts.error_manager.get_single_action_context('Opening Super Free TTS Dialog from Browser'):
                    component_batch.create_component_batch_browser_existing_preset(hypertts, browser.selectedNotes(), preset_id)
                    # browser.model.reset() is deprecated and redundant when using CollectionOp
            return launch            

        def get_launch_realtime_dialog_browser_fn(hypertts, browser):
            def launch():
                with hypertts.error_manager.get_single_action_context('Adding Realtime TTS'):
                    launch_realtime_dialog_browser(hypertts, browser.selectedNotes())
            return launch

        def get_remove_realtime_tts_tag_fn(hypertts, browser):
            def launch():
                with hypertts.error_manager.get_single_action_context('Removing Realtime TTS'):
                    remove_realtime_tts_tag(hypertts, browser, browser.selectedNotes())
            return launch

        def get_launch_workflow_browser_fn(hypertts, browser):
            def launch():
                with hypertts.error_manager.get_single_action_context('Running Workflow from Browser'):
                    component_workflow.create_workflow_dialog_browser(hypertts, browser.selectedNotes())
            return launch

        def get_run_saved_workflow_browser_fn(hypertts, browser, workflow_id: str):
            def launch():
                with hypertts.error_manager.get_single_action_context('Quick Running Workflow from Browser'):
                    component_workflow.create_workflow_dialog_browser(
                        hypertts,
                        browser.selectedNotes(),
                        workflow_id=workflow_id,
                    )
            return launch

        # Prevent duplicate menus in the same browser window
        existing_menu = browser.form.menubar.findChild(aqt.qt.QMenu, "sf_browser_menu")
        if existing_menu:
            return

        menu = aqt.qt.QMenu(constants.ADDON_NAME, browser.form.menubar)
        menu.setObjectName("sf_browser_menu")
        browser.form.menubar.addMenu(menu)

        action = aqt.qt.QAction(i18n.get_text("menu_add_audio_collection", lang), browser)
        action.triggered.connect(get_launch_dialog_browser_new_fn(hypertts, browser))
        menu.addAction(action)

        # add a menu entry for each preset
        preset_list = hypertts.get_preset_list()
        if preset_list:
            quick_apply_menu = menu.addMenu(i18n.get_text("menu_quick_apply_preset", lang))
            for preset_info in preset_list:
                action = aqt.qt.QAction(preset_info.name, browser)
                action.triggered.connect(get_launch_dialog_browser_existing_fn(hypertts, browser, preset_info.id))
                quick_apply_menu.addAction(action)

        workflow_action_title = i18n.get_text("menu_workflow", lang)
        action = aqt.qt.QAction(workflow_action_title, browser)
        action.triggered.connect(get_launch_workflow_browser_fn(hypertts, browser))
        menu.addAction(action)

        workflow_list = hypertts.get_workflow_list()
        if workflow_list:
            workflow_menu_title = i18n.get_text("menu_workflow_quick_run", lang)
            quick_workflow_menu = menu.addMenu(workflow_menu_title)
            for workflow_info in workflow_list:
                action = aqt.qt.QAction(workflow_info.name, browser)
                action.triggered.connect(get_run_saved_workflow_browser_fn(hypertts, browser, workflow_info.id))
                quick_workflow_menu.addAction(action)

        menu.addSeparator()

        action = aqt.qt.QAction(i18n.get_text("menu_add_audio_realtime", lang), browser)
        action.triggered.connect(get_launch_realtime_dialog_browser_fn(hypertts, browser))
        menu.addAction(action)

        action = aqt.qt.QAction(i18n.get_text("menu_remove_audio_realtime", lang), browser)
        action.triggered.connect(get_remove_realtime_tts_tag_fn(hypertts, browser))
        menu.addAction(action)

    def run_superfreetts_settings(editor):
        with hypertts.error_manager.get_single_action_context('Opening Preset Mapping Rules'):
            logger.info(f'clicked superfreetts settings, editor: {editor}')
            editor_context = hypertts.get_editor_context(editor)
            deck_note_type = hypertts.get_editor_deck_note_type(editor)
            component_presetmappingrules.create_dialog(hypertts, deck_note_type, editor_context)

    def run_superfreetts_preview(editor):
        with hypertts.error_manager.get_single_action_context('Previewing Audio'):
            editor_context = hypertts.get_editor_context(editor)
            mapping_rules = hypertts.load_mapping_rules()
            if len(mapping_rules.rules) > 0:
                hypertts.preview_all_mapping_rules(editor_context, mapping_rules)
            else:
                hypertts.preview_with_quick_preset_picker(editor_context)

    def run_superfreetts_apply(editor):
        with hypertts.error_manager.get_single_action_context('Generating Audio'):
            editor_context = hypertts.get_editor_context(editor)
            hypertts.apply_all_mapping_rules(editor_context)

    def setup_editor_buttons(buttons, editor):
        with hypertts.error_manager.get_single_action_context('Setting up Super Free TTS editor buttons'):
            preferences = hypertts.get_preferences()

            add_audio_shortcut = ''
            if preferences.keyboard_shortcuts.shortcut_editor_add_audio != None:
                add_audio_shortcut = str(preferences.keyboard_shortcuts.shortcut_editor_add_audio)
            preview_audio_shortcut = ''
            if preferences.keyboard_shortcuts.shortcut_editor_preview_audio != None:
                preview_audio_shortcut = str(preferences.keyboard_shortcuts.shortcut_editor_preview_audio)

            new_button = editor.addButton(gui_utils.get_graphics_path(constants.GRAPHICS_ICON_SPEAKER),
                'superfreetts_add_audio',
                run_superfreetts_apply,
                tip = i18n.get_text("editor_button_add_audio_tip", hypertts.get_ui_language()).format(add_audio_shortcut),
                keys = preferences.keyboard_shortcuts.shortcut_editor_add_audio,
                disables=False)
            buttons.append(new_button)

            new_button = editor.addButton(gui_utils.get_graphics_path(constants.GRAPHICS_ICON_PLAY),
                'superfreetts_preview_audio',
                run_superfreetts_preview,
                tip = i18n.get_text("editor_button_preview_audio_tip", hypertts.get_ui_language()).format(preview_audio_shortcut),
                keys = preferences.keyboard_shortcuts.shortcut_editor_preview_audio,
                disables=False)
            buttons.append(new_button)

            new_button = editor.addButton(gui_utils.get_graphics_path(constants.GRAPHICS_ICON_SETTINGS),
                'superfreetts_settings',
                run_superfreetts_settings,
                tip = i18n.get_text("editor_button_settings_tip", hypertts.get_ui_language()),
                disables=False)
            buttons.append(new_button)        

            return buttons

    # Clean up legacy Anki Tools menu items if they exist from previous reloads
    existing_actions = aqt.mw.form.menuTools.actions()
    for action in existing_actions:
        # Catch and remove any previous tool actions including the pesky extra About button
        if action.objectName() in ["sf_action_services", "sf_action_preferences", "sf_action_about"] or \
           "Super Free TTS" in action.text():
            aqt.mw.form.menuTools.removeAction(action)

    # Create AnkiVN top-level menu
    global ankivn_menu, action_unified_settings
    
    ankivn_menu = None
    action_unified_settings = None
    
    # Check if menu already exists (from previous addon load)
    menubar_actions = aqt.mw.form.menubar.actions()
    for action in menubar_actions:
        if action.objectName() == "sf_ankivn_menu":
            ankivn_menu = action.menu()
            break
    
    # Create AnkiVN menu if not found
    if ankivn_menu is None:
        ankivn_menu = aqt.qt.QMenu("AnkiVN", aqt.mw)
        ankivn_menu.setObjectName("sf_ankivn_menu")
        ankivn_menu_action = ankivn_menu.menuAction()
        ankivn_menu_action.setObjectName("sf_ankivn_menu")
        
        # Try to insert before Help menu
        help_action = None
        for action in menubar_actions:
            if action.text().lower() == "help":
                help_action = action
                break
        
        if help_action:
            aqt.mw.form.menubar.insertMenu(help_action, ankivn_menu)
        else:
            aqt.mw.form.menubar.addMenu(ankivn_menu)
    
    # Check if unified settings action exists in AnkiVN menu
    for action in ankivn_menu.actions():
        if action.objectName() == "sf_action_unified_settings":
            action_unified_settings = action
            break
    
    # Create unified settings action if not found
    if action_unified_settings is None:
        action_unified_settings = aqt.qt.QAction("", aqt.mw)
        action_unified_settings.setObjectName("sf_action_unified_settings")
        action_unified_settings.triggered.connect(lambda: launch_unified_dialog(hypertts, initial_tab=0))
        ankivn_menu.addAction(action_unified_settings)

    # Initial update
    update_menu_language(hypertts)

    # Update on profile load
    aqt.gui_hooks.profile_did_open.append(lambda: update_menu_language(hypertts)) 

    # browser menus
    aqt.gui_hooks.browser_menus_did_init.append(browerMenusInit)

    # editor buttons
    aqt.gui_hooks.editor_did_init_buttons.append(setup_editor_buttons)

    # register TTS player
    aqt.sound.av_player.players.append(ttsplayer.AnkiSuperFreeTTSPlayer(aqt.mw.taskman, hypertts))

    
