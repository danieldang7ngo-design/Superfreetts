import os
from . import constants
from . import batch_constants
from . import system_utils
from . import batch_executor
from . import config_models
from . import logging_utils

logger = logging_utils.get_child_logger(__name__)

class TTSOrchestrator:
    def __init__(self, superfreetts):
        self.stts = superfreetts
        self.anki_utils = superfreetts.anki_utils
        self.service_manager = superfreetts.service_manager
        self.config_store = superfreetts.config_store
        self.executor = None

    def build_engine_config(self, service_config_map: dict) -> dict:
        cpu_default = max(2, system_utils.get_max_workers())
        defaults = {
            'PiperTTS': cpu_default,
            'KokoroTTS': cpu_default,
            'EdgeTTS': batch_constants.EDGETTS_MAX_WORKERS,
            'MmsTTS': cpu_default,
            'SupertonicTTS': cpu_default,
        }
        service_pool_map = {
            'PiperTTS': 'Piper',
            'KokoroTTS': 'Kokoro',
            'EdgeTTS': 'EdgeTTS',
            'MmsTTS': 'MMS',
            'SupertonicTTS': 'Supertonic',
        }
        engine_config = {}
        for service_name, pool_name in service_pool_map.items():
            service_config = service_config_map.get(service_name, {})
            concurrency = service_config.get('concurrency_workers') or defaults.get(service_name, 1)
            
            max_cap = batch_constants.EDGETTS_MAX_WORKERS if service_name == 'EdgeTTS' else system_utils.get_max_workers()
            if concurrency > max_cap:
                logger.warning(f'Service {service_name} concurrency_workers ({concurrency}) exceeds max ({max_cap}), capping')
                concurrency = max_cap
            engine_config[pool_name] = max(1, concurrency)
            
            self.auto_scale_pool(pool_name, engine_config[pool_name])
        return engine_config

    def auto_scale_pool(self, pool_name: str, concurrency: int) -> None:
        try:
            if pool_name == 'Piper':
                from .services import service_piper
                service_piper._piper_pool.update_max_processes(concurrency)
            elif pool_name == 'Kokoro':
                from .services import service_kokoro
                service_kokoro._kokoro_pool.update_max_processes(concurrency)
            elif pool_name == 'MMS':
                from .services import service_mms
                service_mms._sherpa_pool.update_max_processes(concurrency)
            elif pool_name == 'Supertonic':
                from .services import service_supertonic
                service_supertonic._supertonic_pool.update_max_processes(concurrency)
        except Exception as pool_err:
            logger.warning(f"Failed to auto-scale pool for {pool_name}: {pool_err}")

    def reconfigure_service_manager(self):
        configuration = self.stts.get_configuration()
        preferences = self.stts.get_preferences()
        disable_ssl_verification = preferences.error_handling.disable_ssl_verification
        services_enabled = self.service_manager.configure(configuration, disable_ssl_verification)
        self.service_manager.clear_voice_list_cache()
        logger.debug(f'reconfigure_service_manager, services_enabled: {services_enabled}')
        try:
            service_config_map = configuration.get_service_config()
            engine_config = self.build_engine_config(service_config_map)
            self.executor = batch_executor.get_multi_engine_executor(engine_config=engine_config)
            logger.info(f'[RECONFIG] Batch executor updated with new settings: {engine_config}')
        except Exception as e:
            logger.warning(f'[RECONFIG] Failed to update batch executor: {e}')
            self.executor = batch_executor.get_batch_executor(max_workers=1)
        if services_enabled:
            self.anki_utils.broadcast_services_configured()

    def apply_logging_preferences(self):
        try:
            prefs = config_models.deserialize_preferences(
                self.anki_utils.get_config().get(constants.CONFIG_PREFERENCES, {})
            )
            if prefs.error_handling.debug_mode:
                log_dir = self.anki_utils.get_user_files_dir()
                if not os.path.isdir(log_dir):
                    os.makedirs(log_dir, exist_ok=True)
                log_path = os.path.join(log_dir, 'superfreetts.log')
                logging_utils.configure_file_logging(log_path)
            else:
                logging_utils.configure_silent()
        except Exception:
            logging_utils.configure_silent()