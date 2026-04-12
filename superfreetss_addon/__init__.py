import sys
import os
import traceback
import logging
import uuid
import re
import pprint
import json

enable_stats_error_reporting = False

if hasattr(sys, '_pytest_mode'):
    # called from within a test run
    pass
else:
    # configure imports
    # =================

    # running from within Anki
    import anki
    import anki.hooks
    import aqt
    import aqt.gui_hooks
    import anki.sound

    # need to declare upfront whether we're doing crash reporting
    # ============================================================
    if False: # Super Free TTS Lite: Always disable crash reporting
        sys._sentry_crash_reporting = True

    # setup logger
    # ============

    from . import logging_utils

    if os.environ.get('HYPER_TTS_DEBUG_LOGGING', '') == 'enable':
        # Enable debug mode without calling configure_console_logging()
        # (which tries to wrap stdout, which may be closed during startup)
        # Instead, set FORCE_DEBUG_MODE to enable logging via get_child_logger()
        logging_utils.FORCE_DEBUG_MODE = True
        logging_utils.configure_silent()  # Start in silent mode
    elif os.environ.get('HYPER_TTS_DEBUG_LOGGING', '') == 'file':
        # log everything to file
        logging_utils.configure_file_logging(os.environ['HYPER_TTS_DEBUG_LOGFILE'])
    else:
        # log at info level, but with null handler, so that sentry picks up breadcrumbs and errors
        logging_utils.configure_silent()

    logger = logging_utils.get_child_logger(__name__)

    # anonymous user id
    # =================

    # for new installs
    # - create the user_uuid
    # - enable all help screens
    # for existing installs
    # - default help screens to off

    # get or create user_uuid
    from . import config_models
    from . import constants

    def get_configuration_dict() -> dict:
        """
        return the `configuration` key of the addon config.
        """
        addon_config = aqt.mw.addonManager.getConfig(constants.CONFIG_ADDON_NAME)
        config_configuration = addon_config.get(constants.CONFIG_CONFIGURATION, {})
        return config_configuration

    def generate_user_uuid() -> str:
        """
        Generate a new user UUID.
        """
        return uuid.uuid4().hex

    def get_configuration() -> tuple[config_models.Configuration, bool]:
        """
        Returns the configuration for the addon, in config_models.Configuration type.
        """
        config_dict: dict = get_configuration_dict()
        config: config_models.Configuration = config_models.deserialize_configuration(config_dict)
        first_install = False
        if config.user_uuid == None:
            # first install
            first_install = True
            config.user_uuid = generate_user_uuid()
            # enable welcome messages and features
            config.new_install_settings()

        return config, first_install

    def save_configuration(configuration: config_models.Configuration) -> None:
        """
        Save the configuration to the addon config.
        """
        addon_config = aqt.mw.addonManager.getConfig(constants.CONFIG_ADDON_NAME)
        addon_config[constants.CONFIG_CONFIGURATION] = config_models.serialize_configuration(configuration)
        aqt.mw.addonManager.writeConfig(constants.CONFIG_ADDON_NAME, addon_config)

    configuration, first_install = get_configuration()
    save_configuration(configuration)

    # Sentry crash reporting removed in Lite version


    # addon imports
    # =============

    from . import anki_utils
    from . import servicemanager
    from . import superfreetss
    from . import gui

    # initialize superfreetss
    # =======================
    #
    # Important: To keep Anki startup fast, we avoid instantiating all
    # TTS services here. Service discovery and instantiation are now
    # performed lazily when first needed (configuration dialog, voice
    # selection, or audio generation).

    ankiutils = anki_utils.AnkiUtils()

    def services_dir():
        current_script_path = os.path.realpath(__file__)
        current_script_dir = os.path.dirname(current_script_path)
        return os.path.join(current_script_dir, 'services')

    # Derive the package name for services dynamically
    # This ensures that if the addon is renamed or loaded as a sub-package (e.g. Superfreetts.superfreetss_addon),
    # discovery still works correctly.
    if __package__:
        services_package = f"{__package__}.{constants.DIR_SERVICES}"
    else:
        # Fallback if __package__ is None (unlikely in Anki)
        services_package = f"{constants.DIR_HYPERTTS_ADDON}.{constants.DIR_SERVICES}"

    service_manager = servicemanager.ServiceManager(
        services_dir(),
        services_package,
        False
    )

    hyper_tts = superfreetss.SuperFreeTTS(ankiutils, service_manager)
    aqt.mw.hyper_tts = hyper_tts

    # Configure services based on current configuration.
    # At this point no concrete services may be instantiated yet;
    # ServiceManager stores the configuration and will apply it
    # when services are lazily instantiated.
    with hyper_tts.error_manager.get_single_action_context('Configuring Services'):
        service_manager.configure(hyper_tts.get_configuration())

    # Configure logging based on user preference
    if hyper_tts.get_preferences().error_handling.debug_mode:
        logging_utils.FORCE_DEBUG_MODE = True

    gui.init(hyper_tts)


    # stats
    from . import stats
# from . import constants_events removed
    if not hasattr(sys, '_pytest_mode') and enable_stats_error_reporting:
        if configuration.enable_stats():
            # initialize stats global object
            sys._superfreetss_stats_global = stats.StatsGlobal(ankiutils, 
                                                        configuration.user_uuid,
                                                        {
                                                            'superfreetss_days_since_install': configuration.days_since_install(),
                                                            'superfreetss_trial_registration_step': configuration.trial_registration_step.name,
                                                            'superfreetss_pro': False
                                                        },
                                                        first_install,
                                                        False
                                                        )

    # ---------------------------------------------------------
    # Popup chào mừng (display_introduction_message = True sau first_install)
    # profile_did_open có thể gọi nhiều lần → guard để chỉ hiện 1 lần mỗi session
    # ---------------------------------------------------------
    _welcome_popup_already_shown = False

    def show_welcome_popup():
        global _welcome_popup_already_shown
        if _welcome_popup_already_shown:
            return

        try:
            current_config = hyper_tts.get_configuration()
            # Force show if requested, but respect existing session guard
            if not current_config.display_introduction_message:
                current_config.display_introduction_message = True
                save_configuration(current_config)

            # Gán True trước exec() (modal): lần gọi hook kế tiếp vẫn thấy True trong config
            # nhưng guard session chặn mở dialog thứ hai
            _welcome_popup_already_shown = True

            from . import component_welcome

            welcome_dialog = component_welcome.WelcomeDialog(hyper_tts, aqt.mw)
            welcome_dialog.exec()
        except Exception as e:
            logger.error(f"Failed to show welcome popup: {e}")

    if not hasattr(sys, "_pytest_mode"):
        # Tránh chồng callback sau Tools → Add-ons → Reload (module mới append thêm, handler cũ vẫn nằm trong list)
        _mw = getattr(aqt, "mw", None)
        if _mw is not None:
            _prev = getattr(_mw, "_sftts_welcome_profile_hook", None)
            if _prev is not None:
                try:
                    aqt.gui_hooks.profile_did_open.remove(_prev)
                except ValueError:
                    pass
            _mw._sftts_welcome_profile_hook = show_welcome_popup
        aqt.gui_hooks.profile_did_open.append(show_welcome_popup)
