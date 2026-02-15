import sys
import json

# pyqt
import aqt.qt
import pprint

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
from . import constants_events
from . import stats
from . import config_models
from . import errors
from . import component_batch
from . import component_realtime
from . import component_presetmappingrules
from . import component_configuration
from . import component_preferences
from . import component_easy
from . import component_choose_easy_advanced
from . import component_services_configuration
from . import component_trialsignup
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
        # Cho phép thu nhỏ/phóng to cửa sổ cấu hình (min/max buttons trên title bar)
        # Giúp user có thể mở rộng ra full màn hình khi cần xem nhiều services hơn
        self.setWindowFlag(aqt.qt.Qt.WindowType.WindowMinMaxButtonsHint, True)
        self.setStyleSheet(constants.STYLESHEET_DIALOG)
        self.configuration = component_configuration.Configuration(hypertts, self)
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
        self.setStyleSheet(constants.STYLESHEET_DIALOG)
        self.preferences = component_preferences.ComponentPreferences(hypertts, self)
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
        self.setStyleSheet(constants.STYLESHEET_DIALOG)
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
    with hypertts.error_manager.get_single_action_context('Launching Configuration Dialog'):
        logger.info('launch_configuration_dialog')
        dialog = ConfigurationDialog(hypertts)
        dialog.setupUi()
        dialog.exec()

def launch_services_configuration(hypertts):
    # Super Free TTS Lite: Skip trial signup, go straight to configuration
    launch_configuration_dialog(hypertts)

def launch_preferences_dialog(hypertts):
    with hypertts.error_manager.get_single_action_context('Launching Preferences Dialog'):
        logger.info('launch_preferences_dialog')
        dialog = PreferencesDialog(hypertts)
        dialog.setupUi()
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



# Global references to menu actions for dynamic updates
action_services = None
action_preferences = None

def update_menu_language(hypertts):
    """Update the text of the menu items based on current UI language."""
    global action_services, action_preferences
    lang = hypertts.get_ui_language()
    if action_services:
        action_services.setText(i18n.get_text("menu_services_configuration", lang))
    if action_preferences:
        action_preferences.setText(i18n.get_text("menu_preferences", lang))

def init(hypertts):

    def browerMenusInit(browser: aqt.browser.Browser):
        
        def get_launch_dialog_browser_new_fn(hypertts, browser):
            def launch():
                with hypertts.error_manager.get_single_action_context('Opening Super Free TTS Dialog from Browser'):
                    component_batch.create_component_batch_browser_new_preset(hypertts, browser.selectedNotes(), hypertts.get_next_preset_name())
                    # required to make sound tags appear
                    browser.model.reset()
            return launch

        def get_launch_dialog_browser_existing_fn(hypertts, browser, preset_id: str):
            def launch():
                with hypertts.error_manager.get_single_action_context('Opening Super Free TTS Dialog from Browser'):
                    component_batch.create_component_batch_browser_existing_preset(hypertts, browser.selectedNotes(), preset_id)
                    # required to make sound tags appear
                    browser.model.reset()
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

        # Prevent duplicate menus in the same browser window
        existing_menu = browser.form.menubar.findChild(aqt.qt.QMenu, "sf_browser_menu")
        if existing_menu:
            return

        menu = aqt.qt.QMenu(constants.ADDON_NAME, browser.form.menubar)
        menu.setObjectName("sf_browser_menu")
        browser.form.menubar.addMenu(menu)

        action = aqt.qt.QAction(f'Add Audio (Collection)...', browser)
        action.triggered.connect(get_launch_dialog_browser_new_fn(hypertts, browser))
        menu.addAction(action)

        # add a menu entry for each preset
        for preset_info in hypertts.get_preset_list():
            action = aqt.qt.QAction(f'Add Audio (Collection): {preset_info.name}...', browser)
            action.triggered.connect(get_launch_dialog_browser_existing_fn(hypertts, browser, preset_info.id))
            menu.addAction(action)

        menu.addSeparator()

        action = aqt.qt.QAction(f'Add Audio (Realtime)...', browser)
        action.triggered.connect(get_launch_realtime_dialog_browser_fn(hypertts, browser))
        menu.addAction(action)

        action = aqt.qt.QAction(f'Remove Audio (Realtime) / TTS Tag...', browser)
        action.triggered.connect(get_remove_realtime_tts_tag_fn(hypertts, browser))
        menu.addAction(action)

    def run_superfreetss_settings(editor):
        with hypertts.error_manager.get_single_action_context('Opening Preset Mapping Rules'):
            logger.info(f'clicked superfreetss settings, editor: {editor}')
            editor_context = hypertts.get_editor_context(editor)
            deck_note_type = hypertts.get_editor_deck_note_type(editor)
            component_presetmappingrules.create_dialog(hypertts, deck_note_type, editor_context)

    def run_superfreetss_preview(editor):
        with hypertts.error_manager.get_single_action_context('Previewing Audio'):
            if component_choose_easy_advanced.ensure_easy_advanced_choice_made(hypertts):
                editor_context = hypertts.get_editor_context(editor)
                if hypertts.load_mapping_rules().use_easy_mode:
                    logger.debug('use easy mode')
                    deck_note_type: config_models.DeckNoteType = hypertts.get_editor_deck_note_type(editor)
                    component_easy.create_dialog_editor(hypertts, deck_note_type, editor_context)
                else:
                    hypertts.preview_all_mapping_rules(editor_context)

    def run_superfreetss_apply(editor):
        with hypertts.error_manager.get_single_action_context('Generating Audio'):
            if component_choose_easy_advanced.ensure_easy_advanced_choice_made(hypertts):
                editor_context = hypertts.get_editor_context(editor)
                if hypertts.load_mapping_rules().use_easy_mode:
                    logger.debug('use easy mode')
                    deck_note_type: config_models.DeckNoteType = hypertts.get_editor_deck_note_type(editor)
                    component_easy.create_dialog_editor(hypertts, deck_note_type, editor_context)
                else:
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
                'superfreetss_add_audio',
                run_superfreetss_apply,
                tip = f'Super Free TTS: Add Audio to your note (based on your preset rules) {add_audio_shortcut}',
                keys = preferences.keyboard_shortcuts.shortcut_editor_add_audio,
                disables=False)
            buttons.append(new_button)

            new_button = editor.addButton(gui_utils.get_graphics_path(constants.GRAPHICS_ICON_PLAY),
                'superfreetss_preview_audio',
                run_superfreetss_preview,
                tip = f'Super Free TTS: Preview Audio (Hear the audio before adding it) {preview_audio_shortcut}',
                keys = preferences.keyboard_shortcuts.shortcut_editor_preview_audio,
                disables=False)
            buttons.append(new_button)

            new_button = editor.addButton(gui_utils.get_graphics_path(constants.GRAPHICS_ICON_SETTINGS),
                'superfreetss_settings',
                run_superfreetss_settings,
                tip = 'Super Free TTS: Configure Preset Rules for this Note (do this before being able to add audio)',
                disables=False)
            buttons.append(new_button)        

            return buttons

    # anki tools menu
    global action_services, action_preferences
    
    # Robust Check for existing actions using objectName
    # This survives addon reloads where globals are reset but menu items stay
    existing_actions = aqt.mw.form.menuTools.actions()
    
    # Try to find existing actions in the actual menu
    for action in existing_actions:
        if action.objectName() == "sf_action_services":
            action_services = action
        if action.objectName() == "sf_action_preferences":
            action_preferences = action

    # Create and add if not found
    if action_services is None:
        action_services = aqt.qt.QAction("", aqt.mw)
        action_services.setObjectName("sf_action_services")
        action_services.triggered.connect(lambda: launch_configuration_dialog(hypertts))
        aqt.mw.form.menuTools.addAction(action_services)
    
    if action_preferences is None:
        action_preferences = aqt.qt.QAction("", aqt.mw)
        action_preferences.setObjectName("sf_action_preferences")
        action_preferences.triggered.connect(lambda: launch_preferences_dialog(hypertts))
        aqt.mw.form.menuTools.addAction(action_preferences)

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

    # 


    def should_show_welcome_message(hypertts):
        configuration = hypertts.get_configuration()
        if configuration.display_introduction_message:
            if configuration.trial_registration_step in [config_models.TrialRegistrationStep.new_install, config_models.TrialRegistrationStep.pending_add_audio]:
                return True
        return False

    def on_deck_browser_will_render_content(deck_browser, content):
        # initialize stats
        if hasattr(sys, '_superfreetss_stats_global'):
            # load required data
            sys._superfreetss_stats_global.init_load()

        if should_show_welcome_message(hypertts):
            configuration = hypertts.get_configuration()
            trial_step = configuration.trial_registration_step
            
            # Check if night mode is enabled
            night_mode = hypertts.anki_utils.night_mode_enabled()
            
            # Set colors based on night mode
            bg_color = "#2f2f31" if night_mode else "white"
            border_color = "#555555" if night_mode else "#cccccc"
            text_color = "#ffffff" if night_mode else "#000000"
            
            # Determine which buttons to show based on trial registration step
            show_configure_services = trial_step == config_models.TrialRegistrationStep.new_install
            show_add_audio = trial_step == config_models.TrialRegistrationStep.pending_add_audio
            
            # Set initial visibility styles
            configure_services_style = "" if show_configure_services else "display: none;"
            add_audio_style = "" if show_add_audio else "display: none;"
            
            # Generate button content - only non-large variant
            configure_services_content = f"""
                <p id="superfreetss-important-text"><b class="important-gradient-text">Important</b>: you have to configure services before adding audio.</p>
                <button class="superfreetss-welcome-button">
                    <div><b style="font-size: 1.2em;">Configure Services</b></div>
                    <div style="font-size: 0.8em;">Click here before adding audio</div>
                </button>
            """
            add_audio_content = f"""
                <p>It looks like you haven't added audio yet.</p>
                <button class="superfreetss-welcome-button">
                    <div><b style="font-size: 1.2em;">Adding Audio</b></div>
                    <div style="font-size: 0.8em;">Click to learn how to add audio</div>
                </button>
            """
            
            welcome_html = f"""
            <div id="superfreetss-welcome-message" style="margin: 1em 2em; padding: 1em; background-color: {bg_color}; border: 1px solid {border_color}; border-radius: 15px; color: {text_color};">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <h3 style="margin: 0; text-align: center; flex-grow: 1;">Super Free TTS - Add Audio to your Flashcards</h3>
                    <button id="superfreetss-welcome-close" style="background: none; border: none; cursor: pointer; font-size: 1.2em; color: {text_color};">× Close</button>
                </div>
                <div style="text-align: center; margin-top: 10px;">
                    <div id="superfreetss-configure-services" style="{configure_services_style}">
                        {configure_services_content}
                    </div>
                    <div id="superfreetss-how-to-add-audio" style="{add_audio_style}">
                        {add_audio_content}
                    </div>
                </div>
            </div>
            """
            
            
            welcome_html += f"""
            <style>
                .superfreetss-welcome-button {{
                    cursor: pointer;
                }}
                
                #superfreetss-configure-services button,
                #superfreetss-how-to-add-audio button {{
                    background-color: {constants.COLOR_PRIMARY};
                    border: none;
                    border-radius: 6px;
                    color: white;
                    padding: 12px 24px;
                    font-weight: bold;
                    letter-spacing: 0.5px;
                    transition: background-color 0.2s ease;
                }}
                
                #superfreetss-configure-services button:hover,
                #superfreetss-how-to-add-audio button:hover {{
                    background-color: {constants.COLOR_PRIMARY_HOVER};
                }}
                
                #superfreetss-configure-services button:active,
                #superfreetss-how-to-add-audio button:active {{
                    background-color: {constants.COLOR_PRIMARY_PRESSED};
                }}
                
                .gradient-text {{
                    color: {constants.COLOR_ACCENT};
                    font-weight: bold;
                }}
                
                .important-gradient-text {{
                    color: #C62828;
                    font-weight: bold;
                }}
            </style>
            <script>
                (function() {{
                    function hideConfigureServicesShowAddAudio() {{
                        document.getElementById('superfreetss-configure-services').style.display = 'none';
                        var importantText = document.getElementById('superfreetss-important-text');
                        if (importantText) {{
                            importantText.style.display = 'none';
                        }}
                        document.getElementById('superfreetss-how-to-add-audio').style.display = '';
                    }}
                    
                    function closeWelcomeMessage() {{
                        document.getElementById('superfreetss-welcome-message').style.display = 'none';
                        pycmd('superfreetss:welcome_closed');
                    }}
                    
                    document.getElementById('superfreetss-welcome-close').addEventListener('click', function() {{
                        closeWelcomeMessage();
                    }});
                    
                    var configureServicesDiv = document.getElementById('superfreetss-configure-services');
                    if (configureServicesDiv) {{
                        configureServicesDiv.addEventListener('click', function() {{
                            pycmd('superfreetss:configure_services');
                        }});
                    }}
                    
                    var addAudioDiv = document.getElementById('superfreetss-how-to-add-audio');
                    if (addAudioDiv) {{
                        addAudioDiv.addEventListener('click', function() {{
                            pycmd('superfreetss:how_to_add_audio');
                        }});
                    }}
                    
                    // Make functions available globally if needed
                    window.superFreeTTSWelcome = {{
                        hideConfigureServicesShowAddAudio: hideConfigureServicesShowAddAudio,
                        closeWelcomeMessage: closeWelcomeMessage
                    }};
                }})();
            </script>
            """
            content.stats += welcome_html
            logger.debug('deck browser will render content, added welcome message')
    
    aqt.gui_hooks.deck_browser_will_render_content.append(on_deck_browser_will_render_content)
    
    def on_bridge_cmd(handled, cmd, context):
        if cmd.startswith('superfreetss:welcome_closed'):
            configuration = hypertts.get_configuration()
            configuration.display_introduction_message = False
            hypertts.save_configuration(configuration)
            return (True, None)
        elif cmd.startswith('superfreetss:configure_services'):
            stats.event_global(constants_events.Event.click_welcome_configure_services)
            launch_services_configuration(hypertts)
            return (True, None)
        elif cmd.startswith('superfreetss:how_to_add_audio'):
            stats.event_global(constants_events.Event.click_welcome_add_audio)
            configuration = hypertts.get_configuration()
            user_uuid = configuration.user_uuid
            help_url = gui_utils.get_vocab_ai_url('tips/hypertts-adding-audio', 'deckbrowser_welcome', user_uuid)
            aqt.utils.openLink(help_url)
            logger.info(f'opening url: {help_url}')
            return (True, None)
        return handled
    
    aqt.gui_hooks.webview_did_receive_js_message.append(on_bridge_cmd)
    
