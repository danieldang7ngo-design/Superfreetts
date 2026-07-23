import os
from . import constants
from . import batch_constants
from . import system_utils
from . import batch_executor
from . import config_models
from . import logging_utils

logger = logging_utils.get_child_logger(__name__)

# Best-effort per-process RAM estimates (MB) used only to cap the *default*
# (CPU-core-derived) concurrency for local engine process pools - see root
# cause 2.6 in superfreetts_macos_crash_fix_plan.md.
#
# IMPORTANT - these numbers are NOT an agent-measured benchmark. They come
# from a user-reported real-world observation (Piper ~100-200MB/process,
# Kokoro/MMS/Supertonic ~300-500MB/process) and were not independently
# verified with psutil against the actual bundled models in this
# environment (no local engine models are installed here to measure). They
# are deliberately picked toward the upper/conservative end of the reported
# range. If these turn out to be inaccurate for a given model/voice, the
# existing per-service `concurrency_workers` config field always overrides
# this estimate-driven default - this table only affects the fallback.
RAM_PER_PROCESS_MB_ESTIMATE = {
    'PiperTTS': 200,
    'KokoroTTS': 500,
    'MmsTTS': 500,
    'SupertonicTTS': 500,
}

class TTSOrchestrator:
    def __init__(self, superfreetts):
        self.stts = superfreetts
        self.anki_utils = superfreetts.anki_utils
        self.service_manager = superfreetts.service_manager
        self.config_store = superfreetts.config_store
        self.executor = None

    def build_engine_config(self, service_config_map: dict) -> dict:
        cpu_default = max(2, system_utils.get_max_workers())
        # Root cause 2.6 fix: local engine defaults used to be cpu_default
        # unconditionally, meaning pool size scaled with CPU core count with
        # no regard for how much RAM each process actually needs. Cap each
        # engine's default by available RAM too; compute_ram_aware_concurrency
        # falls back to plain cpu_default if RAM can't be measured (no
        # psutil) or no estimate exists for a given engine, so this is a
        # strict subset of the old behavior, never more permissive.
        ram_capped_default = {
            engine: system_utils.compute_ram_aware_concurrency(cpu_default, ram_estimate)
            for engine, ram_estimate in RAM_PER_PROCESS_MB_ESTIMATE.items()
        }
        defaults = {
            'PiperTTS': ram_capped_default.get('PiperTTS', cpu_default),
            'KokoroTTS': ram_capped_default.get('KokoroTTS', cpu_default),
            'EdgeTTS': batch_constants.EDGETTS_MAX_WORKERS,
            'MmsTTS': ram_capped_default.get('MmsTTS', cpu_default),
            'SupertonicTTS': ram_capped_default.get('SupertonicTTS', cpu_default),
        }
        for engine_name, ram_value in ram_capped_default.items():
            if ram_value < cpu_default:
                logger.info(
                    f'[RAM-CAP] {engine_name} default concurrency capped to {ram_value} '
                    f'(cpu_default={cpu_default}) based on available RAM. '
                    f'Set concurrency_workers manually in Advanced settings to override.'
                )
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