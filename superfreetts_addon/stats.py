import logging
import functools
import enum

# Stubbed out stats.py for Super Free TTS Lite
# All telemetry and network requests to st.vocab.ai have been removed.

logger = logging.getLogger(__name__)

# Constants and Enums moved from constants_events for compatibility
STATS_DAYS_CUTOFF = 14
FEATURE_FLAG_DEFAULT_VALUE = 'control'

class EventContext(enum.Enum):
    addon = enum.auto()
    services = enum.auto()
    hyperttspro = enum.auto()
    trial_signup = enum.auto()
    generate = enum.auto()
    voice_selection = enum.auto()
    choose_easy_advanced = enum.auto()
    servicemanager = enum.auto()
    services_configuration = enum.auto()

class Event(enum.Enum):
    open = enum.auto()
    close = enum.auto()
    click_cancel = enum.auto()
    click_save = enum.auto()
    click_add = enum.auto()
    click_preview = enum.auto()
    install = enum.auto()
    choose = enum.auto()
    click_disable_all_services = enum.auto()
    click_enable_free_services = enum.auto()
    click_free_trial = enum.auto()
    click_enter_api_key = enum.auto()
    click_remove_api_key = enum.auto()
    click_sign_up = enum.auto()
    click_free_trial_ok = enum.auto()
    click_welcome_configure_services = enum.auto()
    click_welcome_add_audio = enum.auto()
    click_trial_signup = enum.auto()
    trial_signup_error = enum.auto()
    trial_signup_success = enum.auto()
    click_email_verification_status = enum.auto()
    email_verification_success = enum.auto()
    email_verification_failure = enum.auto()
    click_how_to_add_audio = enum.auto()
    get_tts_audio = enum.auto()
    error = enum.auto()

class EventMode(enum.Enum):
    advanced_browser_existing_preset = enum.auto()
    advanced_browser_new_preset = enum.auto()
    advanced_editor_existing_preset = enum.auto()
    advanced_editor_new_preset = enum.auto()
    easy_editor = enum.auto()
    easy_mode = enum.auto()
    advanced_mode = enum.auto()

class StatsGlobal:
    def __init__(self, anki_utils, user_uuid, user_properties, first_install, superfreetts_pro: bool):
        self.init_done = True

    def publish(self, context, event, event_mode, event_properties):
        pass

    def publish_event(self, context, event, event_mode, event_properties):
        pass

    def load_feature_flags(self):
        pass
    
    def report_feature_flags(self):
        pass

    def get_feature_flag_value(self, flag_key: str) -> str:
        return 'control'

    def get_feature_flag_enabled(self, flag_key: str) -> bool:
        return False
    
    def init_load(self):
        pass

class StatsEvent:
    def __init__(self, context, event, event_mode):
        pass
    def __call__(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper

class StatsContext:
    def __init__(self, context):
        self.context = context
    def event(self, event, event_mode = None):
        return StatsEvent(self.context, event, event_mode)
    def send_event(self, event, event_mode = None, properties = {}):
        pass

