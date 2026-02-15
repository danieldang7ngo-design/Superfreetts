import enum
import os
import os.path

ENV_VAR_ANKI_LANGUAGE_TOOLS_BASE_URL = 'ANKI_LANGUAGE_TOOLS_BASE_URL'

ENABLE_SENTRY_CRASH_REPORTING = False

LOGGER_NAME = 'superfreetss'
LOGGER_NAME_TEST = 'test_superfreetss'

CLIENT_NAME='anki-super-free-tts'

# requests related constants
RequestTimeout = 20 # 20 seconds max
RequestTimeoutShort = 3

CLOUDLANGUAGETOOLS_API_BASE_URL = 'https://cloudlanguagetools-api.vocab.ai'
VOCABAI_API_BASE_URL = 'https://app.vocab.ai/languagetools-api/v4'

class ServiceType(enum.Enum):
    dictionary = ("Dictionary, contains recordings of words.")
    tts = ("Text To Speech, can generate audio for full sentences.")
    def __init__(self, description):
        self.description = description

class ServiceFee(enum.Enum):
    free = enum.auto()
    paid = enum.auto()

class AudioRequestReason(enum.Enum):
    preview = enum.auto()
    batch = enum.auto()
    realtime = enum.auto()
    editor_browser = enum.auto()
    editor_add = enum.auto()

# what triggered this request (batch / on the fly / editor)
class RequestMode(enum.Enum):
    batch = enum.auto()
    dynamic = enum.auto()
    edit = enum.auto()

# batch modes
class BatchMode(enum.Enum):
    simple = enum.auto()
    template = enum.auto()
    advanced_template = enum.auto()

class TemplateFormatVersion(enum.Enum):
    v1 = enum.auto()

class VoiceSelectionMode(enum.Enum):
    single = enum.auto() # a single voice is selected
    random = enum.auto() # a random voice is selected, with optional weights
    priority = enum.auto() # the first voice is selected, and if audio is not found, move to the second one

class BatchNoteStatus(enum.Enum):
    Waiting = enum.auto()
    Processing = enum.auto()
    Done = enum.auto()
    Error = enum.auto()
    OK = enum.auto()

class TextReplacementRuleType(enum.Enum):
    Simple = enum.auto()
    Regex = enum.auto()

class RealtimeSourceType(enum.Enum):
    AnkiTTSTag = enum.auto()

class AnkiTTSFieldType(enum.Enum):
    Regular = enum.auto()
    Cloze = enum.auto()
    ClozeOnly = enum.auto()

class AnkiCardSide(enum.Enum):
    Front = enum.auto()
    Back = enum.auto()

class MappingRuleType(enum.Enum):
    NoteType = enum.auto()
    DeckNoteType = enum.auto()

DIR_HYPERTTS_ADDON = 'superfreetss_addon'
DIR_SERVICES = 'services'

ANKIWEB_ADDON_ID = '111623432'

def _get_addon_name():
    # specifically for Super Free TTS, the core logic is in superfreetss_addon subfolder.
    # The parent of superfreetss_addon is the actual addon directory name used by Anki.
    current_dir = os.path.dirname(__file__)
    parent_dir = os.path.dirname(current_dir)
    addon_folder = os.path.basename(parent_dir)
    
    if ANKIWEB_ADDON_ID in __file__:
        return ANKIWEB_ADDON_ID
    
    # Fallback to the detected folder name (e.g. 'super free tts' or 'anki-super-free-tts')
    return addon_folder

CONFIG_ADDON_NAME = _get_addon_name()


CONFIG_SCHEMA = 'config_schema'
CONFIG_SCHEMA_VERSION = 4
# deprecated, use CONFIG_PRESETS
CONFIG_BATCH_CONFIG = 'batch_config'
# this is the new config category, contains dict of uuids
CONFIG_PRESETS = 'presets'
CONFIG_DEFAULT_PRESETS = 'default_presets'
CONFIG_MAPPING_RULES = 'mapping_rules'
CONFIG_REALTIME_CONFIG = 'realtime_config'
CONFIG_CONFIGURATION = 'configuration'
CONFIG_PREFERENCES = 'preferences'
CONFIG_KEYBOARD_SHORTCUTS = 'keyboard_shortcuts'
CONFIG_LAST_USED_BATCH = 'last_used_batch'
CONFIG_USE_SELECTION = 'use_selection' # whether to use the selected portion of the field

ADDON_NAME = 'Super Free TTS'
MENU_PREFIX = ADDON_NAME + ':'
TITLE_PREFIX = ADDON_NAME + ': '

GUI_EASY_DIALOG_TITLE = TITLE_PREFIX + 'Add Audio (Easy)'
GUI_COLLECTION_DIALOG_TITLE = TITLE_PREFIX + 'Add Audio (Collection)'
GUI_REALTIME_DIALOG_TITLE = TITLE_PREFIX + 'Add Audio (Realtime)'
GUI_CONFIGURATION_DIALOG_TITLE = TITLE_PREFIX + 'Configuration'
GUI_PREFERENCES_DIALOG_TITLE = TITLE_PREFIX + 'Preferences'
GUI_CHOOSE_PRESET_DIALOG_TITLE = TITLE_PREFIX + 'Choose Preset'
GUI_PRESET_MAPPING_RULES_DIALOG_TITLE = TITLE_PREFIX + 'Preset Rules'

DIALOG_ID_CHOOSE_PRESET = 'choose_preset'
DIALOG_ID_BATCH = 'batch'
DIALOG_ID_PRESET_MAPPING_RULES = 'preset_mapping_rules'
DIALOG_ID_EASY = 'easy'
DIALOG_ID_CHDOOSE_EASY_ADVANCED = 'choose_easy_advanced'
DIALOG_ID_SERVICES_CONFIGURATION = 'services_configuration'
DIALOG_ID_TRIAL_SIGNUP = 'trial_signup'

TTS_TAG_VOICE = 'SuperFreeTTS'
TTS_TAG_HYPERTTS_PRESET = 'superfreetss_preset'

PYCMD_ADD_AUDIO = 'addaudio'
PYCMD_PREVIEW_AUDIO = 'previewaudio'

PYCMD_ADD_AUDIO_PREFIX = f'superfreetss:{PYCMD_ADD_AUDIO}:'
PYCMD_PREVIEW_AUDIO_PREFIX = f'superfreetss:{PYCMD_PREVIEW_AUDIO}:'

UNDO_ENTRY_NAME = ADDON_NAME + ': Add Audio to Notes'
UNDO_ENTRY_ADD_TTS_TAG = ADDON_NAME + ': Configure Realtime TTS Tag'

GREEN_COLOR_REGULAR = '#69F0AE'
RED_COLOR_REGULAR = '#FFCDD2'

# ── Primary palette (Elegant Monochrome) ──
# ── Modern Swiss/Slate Design System ──
COLOR_PRIMARY = '#0F172A'              # Slate 900 (Deep Dark)
COLOR_PRIMARY_LIGHT = '#1E293B'        # Slate 800
COLOR_PRIMARY_HOVER = '#334155'        # Slate 700
COLOR_PRIMARY_PRESSED = '#020617'      # Slate 950
COLOR_PRIMARY_DISABLED = '#94A3B8'     # Slate 400

COLOR_ACCENT = '#10B981'               # Emerald 500 (Clean Success)
COLOR_ACCENT_HOVER = '#059669'         # Emerald 600
COLOR_ACCENT_TEAL = '#10B981'          # Consistent with Emerald
COLOR_SECONDARY = '#64748B'            # Slate 500 (Muted Text)
COLOR_SURFACE_LIGHT = '#F8FAFC'        # Slate 50 (Paper)

# Backwards compat aliases
COLOR_GRADIENT_PURPLE_START = COLOR_PRIMARY
COLOR_GRADIENT_PURPLE_HOVER_END = COLOR_PRIMARY_HOVER
COLOR_GRADIENT_PURPLE_PRESSED_START = COLOR_PRIMARY_PRESSED

GREEN_STYLESHEET = f'background-color: {COLOR_ACCENT}; color: white; border-radius: 6px; padding: 8px 16px; font-weight: bold; border: none;'
RED_STYLESHEET = f'background-color: transparent; color: {COLOR_SECONDARY}; border: 1px solid #E2E8F0; border-radius: 6px; padding: 6px 12px;'

GREEN_STYLESHEET_NIGHTMODE = f'background-color: {COLOR_ACCENT}; color: white; border-radius: 6px; padding: 8px 16px; font-weight: bold; border: none;'
RED_STYLESHEET_NIGHTMODE = f'background-color: transparent; color: #CBD5E1; border: 1px solid #475569; border-radius: 6px; padding: 6px 12px;'



# Global QSS Stylesheet for dialogs
STYLESHEET_DIALOG = """
    QDialog {
        background-color: palette(window);
    }

    /* ── Group boxes ── */
    QGroupBox {
        font-weight: bold;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        margin-top: 16px;
        padding: 24px 16px 16px 16px;
        background-color: palette(alternate-base);
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 16px;
        padding: 0 10px;
        color: """ + COLOR_SECONDARY + """;
    }

    /* ── Tabs ── */
    QTabWidget::pane {
        border: 1px solid #E2E8F0;
        border-radius: 10px;
    }
    QTabBar::tab {
        padding: 10px 24px;
        margin-right: 4px;
        border-top-left-radius: 8px;
        border-top-right-radius: 8px;
        background-color: palette(button);
        color: palette(button-text);
    }
    QTabBar::tab:selected {
        font-weight: bold;
        background-color: palette(window);
        border-bottom-color: transparent;
    }

    /* ── Input controls ── */
    QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {
        padding: 8px 12px;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        background-color: palette(base);
    }
    QLineEdit:focus, QComboBox:focus {
        border: 2px solid """ + COLOR_ACCENT + """;
    }

    /* ── Buttons ── */
    QPushButton {
        padding: 10px 20px;
        border-radius: 8px;
        font-weight: bold;
    }

    /* ── Scroll area ── */
    QScrollArea {
        border: none;
        background-color: transparent;
    }

    /* ── Checkboxes ── */
    QCheckBox {
        spacing: 10px;
    }
    QCheckBox::indicator {
        width: 20px;
        height: 20px;
        border: 1px solid #CBD5E1;
        border-radius: 6px;
        background-color: palette(base);
    }
    QCheckBox::indicator:checked {
        background-color: """ + COLOR_ACCENT + """;
        border: 1px solid """ + COLOR_ACCENT + """;
    }
"""

LABEL_FILTER_ALL = 'All'

BATCH_CONFIG_NEW = 'New Preset'

GUI_TEXT_UNKNOWN_PRESET = 'Unknown Preset'

GUI_TEXT_MAPPING_RULES = ("""<i>Here, you can configure presets specific to this note or deck."""
""" You will be able to preview or add audio with a single click of the play/preview buttons on the Anki note editor."""
""" You can associate a preset with the Note Type (the preset applies to all notes of that type)"""
""" or with the Deck And Note Type (the preset only applies to this note type + deck combination)"""
)

GUI_TEXT_SOURCE_MODE = """Choose a source mode:
<b>Simple:</b> your text comes from a single field. In most cases, choose this option.
<b>Template:</b> text from different fields can be combined together.
<b>Advanced Template:</b> fields can be combined in complex ways using Python."""

GUI_TEXT_SOURCE_FIELD_NAME = """Source Field:"""
GUI_TEXT_SOURCE_USE_SELECTION = """If text is selected, use selection instead of the full field."""
GUI_TEXT_SOURCE_SIMPLE_TEMPLATE = """Enter template using syntax {Field1} {Field2}:"""
GUI_TEXT_SOURCE_ADVANCED_TEMPLATE = """Enter template using Python syntax (advanced users only):
a simple example:
field_1 = template_fields['Field 1']
field_2 = template_fields['Field 2']
result = f'{field_1} {field_2}'
"""


GUI_TEXT_SOURCE_MODE_REALTIME = """Choose a source mode:
<b>AnkiTTSTag:</b> Configure Realtime Audio using Anki {{tts}} tag. You can choose a single field""" \
""" containing the source text. Will use Super Free TTS when reviewing on desktop and fallback to other voices on iOS AnkiMobile."""

GUI_TEXT_SOURCE_FIELD_TYPE_REALTIME = """Field Type:
<b>Regular:</b> the field should be pronounced in its entirety.
<b>Cloze:</b> only use this for cloze fields. The audio on the front will contain everything except for the hidden word"""\
""" (which you have to guess), and the audio on the back will contain everything.
<b>ClozeOnly:</b> only use this for cloze fields. Only the hidden word will be pronounced, and nothing else."""\
"""It only makes to use this on the back side."""


GUI_TEXT_EASY_SOURCE_SELECTION_NO_TEXT = '<i>(no selected text)</i>'
GUI_TEXT_EASY_SOURCE_CLIPBOARD_NO_TEXT = '<i>(no clipboard text)</i>'
GUI_TEXT_EASY_SOURCE_FIELD_EMPTY = 'empty'

GUI_TEXT_EASY_SOURCE_FIELD = """<i>The sound will be generated using this text. You can edit it.</i>"""
GUI_TEXT_EASY_VOICE_SELECTION = """<i>Choose a voice. You can filter by Language and Service.</i>"""
GUI_TEXT_EASY_TARGET = """<i>Decide where the sound tag will be placed.</i>"""
GUI_TEXT_EASY_BUTTON_MORE_SETTINGS = 'More Settings...'
GUI_TEXT_EASY_BUTTON_HIDE_MORE_SETTINGS = 'Hide Settings...'

GUI_TEXT_EASY_MODE_LABEL_PRESET_MAPPING_RULES = '<i>Enable to use a simplified, easier interface when adding audio to a single note in the Anki editor.</i>'
 
GUI_TEXT_CHOICE_EASY_ADVANCED_EXPLANATION = """Please choose how you want to add audio in the Anki editor."""
GUI_TEXT_CHOICE_EASY_MODE = """Simple interface for adding audio manually. Just choose the field \
and the voice to add audio. Similar to AwesomeTTS. Choose this if you want something simple."""
GUI_TEXT_CHOICE_ADVANCED_MODE = """Full interface with all settings, allows you to add sound manually \
or automatically. You can setup presets for different note types or decks. Choose this if you \
don't mind configuring settings and setup presets."""
GUI_TEXT_CHOICE_EASY_ADVANCED_BOTTOM = """<i>You can change this setting later by clicking the gear button on the editor button bar (Configure preset rules)</i>"""

GUI_TEXT_TARGET_FIELD = """Sound tags will be inserted in this field"""

GUI_TEXT_TARGET_TEXT_AND_SOUND = """<i>Should the target field only contain the sound tag, or should
it contain both text and sound tag.</i>"""
GUI_TEXT_TARGET_REMOVE_SOUND_TAG = """<i>If the target field already contains a sound tag, should it get  removed?</i>"""

GUI_TEXT_BATCH_COMPLETED = """<b>Finished adding Audio to notes</b>. You can undo this operation in menu Edit, 
Undo Super Free TTS: Add Audio to Notes. You may close this dialog.
"""

GUI_TEXT_SUPERFREETSS_PRO = """Super Free TTS is a powerful, free TTS tool for Anki. Premium AI voices (OpenAI, Google Cloud, Azure) are also available via a Pro trial."""

GUI_TEXT_BUTTON_TRIAL = """"""
GUI_TEXT_BUTTON_API_KEY = """"""
GUI_TEXT_BUTTON_BUY = """"""

BUY_PLAN_URL = """"""

GUI_TEXT_SUPERFREETSS_PRO_TRIAL = """"""
GUI_TEXT_SUPERFREETSS_PRO_BUY_PLAN = """"""
GUI_TEXT_SUPERFREETSS_PRO_ENTER_API_KEY = """"""

GUI_TEXT_SUPERFREETSS_PRO_ENABLED = """"""
GUI_TEXT_SUPERFREETSS_PRO_TRIAL_ENTER_EMAIL = """<i>Enter your email and choose a password to get instant access to premium TTS services such as Azure, Google, ElevenLabs, OpenAI, Amazon, Forvo. 7 day trial limited to 50k characters.</i>"""

GUI_TEXT_SUPERFREETSS_PRO_TRIAL_VERIFY_EMAIL = """<i>You have to verify your email before proceeding</i>"""

GUI_TEXT_SUPERFREETSS_PRO_TRIAL_CONFIRM_EMAIL = """<b>IMPORTANT</b>: You must confirm your email address before you can use the service. """\
"""The email subject should be <b>Please Confirm Your Email Address</b> and sender: <b>Vocab.Ai</b>."""

GUI_TEXT_SUPERFREETSS_PRO_TRIAL_VERIFICATION_DESCRIPTION = """Please check your email (subject: <b>Please Confirm Your Email Address</b>"""\
""" sender: <b>Vocab.Ai</b>) and click the verification link. You must verify your email before you can use Super Free TTS Pro services. Once you've clicked the link, press the <b>Check Status</b> button below to continue."""

GUI_TEXT_SUPERFREETSS_PRO_TRIAL_VERIFICATION_INITIAL_STATUS = """If you don't see the email, please check your spam folder. Once you've clicked the verify link, press the <b>Check Status</b> button below."""

GUI_TEXT_SUPERFREETSS_PRO_TRIAL_VERIFIED_TITLE = """Email Verified Successfully!"""
GUI_TEXT_SUPERFREETSS_PRO_TRIAL_VERIFIED_DESCRIPTION = """<b>Congratulations!</b> Your email has been verified and you can now use Super Free TTS Pro services. You can close this dialog and start adding audio to your notes. Check out the tutorial below to learn how to add audio."""

# Trial signup screen variant constants
GUI_TEXT_SUPERFREETSS_PRO_TRIAL_ALTERNATE_TITLE = """Add realistic audio to your cards in 30 seconds"""
GUI_TEXT_SUPERFREETSS_PRO_TRIAL_ALTERNATE_BENEFITS = """<p style="margin-top: 10px; margin-bottom: 15px;">
✓ 1200+ lifelike voices in 60+ languages<br/>
✓ Works inside Anki with one click<br/>
✓ Keep everything you create, even after the trial
</p>"""
GUI_TEXT_SUPERFREETSS_PRO_TRIAL_ALTERNATE_BUTTON = """Start Adding Audio"""
GUI_TEXT_SUPERFREETSS_PRO_TRIAL_ALTERNATE_PRIVACY = """<p style="text-align: center; color: palette(dark); font-size: small; margin-top: 10px;">Free 7-day trial, limited to 50k characters. No obligation to subscribe. Your info is private.</p>"""

GUI_TEXT_REALTIME_SINGLE_NOTE = """Please select a single note to add Realtime Audio"""
GUI_TEXT_REALTIME_CHOOSE_TEMPLATE = """Choose card template"""
GUI_TEXT_REALTIME_REMOVED_TAG = """Removed TTS Tag. Realtime audio will not play anymore."""

GUI_TEXT_SHORTCUTS_ANKI_RESTART = """Note: You'll need to restart Anki after modifying these shortcuts."""

GUI_TEXT_SHORTCUTS_EDITOR_ADD_AUDIO = """Add Audio to note using the selected preset"""
GUI_TEXT_SHORTCUTS_EDITOR_PREVIEW_AUDIO = """Preview Audio for a note using the selected preset"""

GUI_TEXT_ERROR_HANDLING_REALTIME_TTS = """How to display errors during Realtime TTS"""

# Enhanced variants for trial incentive experiment
GUI_TEXT_SERVICES_CONFIG_ENHANCED_TITLE = """Get Started with Super Free TTS - Choose Your Path"""
GUI_TEXT_SERVICES_CONFIG_ENHANCED_DESCRIPTION = """Ready to add amazing audio to your flashcards? Pick the option that works best for you."""
GUI_TEXT_SERVICES_CONFIG_ENHANCED_TRIAL_TITLE = """Start Free Trial (Recommended & Simplest)"""
GUI_TEXT_SERVICES_CONFIG_ENHANCED_TRIAL_RECOMMENDED = """Most popular choice - Get the best quality audio for free!"""
GUI_TEXT_SERVICES_CONFIG_ENHANCED_TRIAL_DESCRIPTION = """<p><strong>Get instant access to premium voices in just 2 clicks:</strong></p><ul><li><strong>Premium AI voices:</strong> Azure, ElevenLabs, OpenAI, Google, Amazon</li><li><strong>Studio-quality audio</strong> - sounds natural and professional</li><li><strong>50,000 characters included</strong> (enough for ~1,250 flashcards)</li><li><strong>No setup required</strong> - works immediately after signup (7-day trial)</li></ul>"""
GUI_TEXT_SERVICES_CONFIG_ENHANCED_MANUAL_TITLE = """Manual Setup (For Advanced Users)"""
GUI_TEXT_SERVICES_CONFIG_ENHANCED_MANUAL_RECOMMENDED = """Choose this if you prefer to configure everything yourself."""
GUI_TEXT_SERVICES_CONFIG_ENHANCED_MANUAL_DESCRIPTION = """<ul><li>Free services (Google Translate, Windows SAPI, MacOS)</li><li>Use your own API keys with cloud services</li><li>Full control over configuration</li><li><em>Note: Requires technical setup and may have limited voice options</em></li></ul>"""

GRAPHICS_PRO_BANNER = 'superfreetss_banner.svg'
GRAPHICS_LITE_BANNER = 'superfreetss_banner.svg'
GRAPHICS_SERVICE_COMPATIBLE = 'superfreetss_service_compatible_banner.svg'
GRAPHICS_SERVICE_ENABLED = 'superfreetss_service_enabled_banner.svg'

GRAPHICS_ICON_SPEAKER = 'icon_speaker.svg'
GRAPHICS_ICON_PLAY = 'icon_play.svg'
GRAPHICS_ICON_SETTINGS = 'icon_settings.svg'

TEXT_PROCESSING_DEFAULT_HTMLTOTEXTLINE = True
TEXT_PROCESSING_DEFAULT_STRIP_BRACKETS = False
TEXT_PROCESSING_DEFAULT_STRIP_CLOZE = False
TEXT_PROCESSING_DEFAULT_SSML_CHARACTERS = True
TEXT_PROCESSING_DEFAULT_REPLACE_AFTER = True
TEXT_PROCESSING_DEFAULT_IGNORE_CASE = False

# prevent message boxes from getting too big
MESSAGE_TEXT_MAX_LENGTH = 500

class ReplaceType(enum.Enum):
    simple = enum.auto()
    regex = enum.auto()

class Gender(enum.Enum):
    Male = enum.auto()
    Female = enum.auto()
    Any = enum.auto()

class ErrorDialogType(str, enum.Enum):
    Dialog = 'Dialog'
    Tooltip = 'Tooltip'
    Nothing = 'Nothing'

# Security: REQUEST_TRIAL_PAYLOAD removed and replaced by native implementation.
