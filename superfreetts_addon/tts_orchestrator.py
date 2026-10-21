import os
from typing import Dict, Set

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

    def _enabled_local_pools(self, enabled_services=None) -> Set[str]:
        """Return local-engine pool names that are currently enabled.

        ``enabled_services`` may be the configuration model's
        ``{service_name: bool}`` map, an explicit collection of service or
        pool names, or None (read from the configuration).  If the value
        cannot be interpreted, default to all local pools so older callers
        keep their previous behaviour instead of accidentally disabling
        everything.
        """
        service_to_pool = {
            'PiperTTS': 'Piper',
            'KokoroTTS': 'Kokoro',
            'MmsTTS': 'MMS',
            'SupertonicTTS': 'Supertonic',
        }

        if enabled_services is None:
            try:
                configuration = self.stts.get_configuration()
                candidate = configuration.get_service_enabled_map()
                if isinstance(candidate, dict):
                    enabled_services = candidate
            except Exception as e:
                logger.debug(f'[RAM] Could not read enabled services: {e}')

        if enabled_services is None:
            return set(service_to_pool.values())

        if isinstance(enabled_services, dict):
            return {
                pool_name
                for service_name, pool_name in service_to_pool.items()
                if enabled_services.get(service_name, False)
            }

        if isinstance(enabled_services, (set, frozenset, list, tuple)):
            enabled = set()
            for item in enabled_services:
                item = str(item)
                if item in service_to_pool:
                    enabled.add(service_to_pool[item])
                elif item in service_to_pool.values():
                    enabled.add(item)
            return enabled

        # Unknown/Mock object: preserve the previous all-local behaviour.
        return set(service_to_pool.values())

    def build_engine_config(
        self,
        service_config_map: dict,
        enabled_services=None,
    ) -> dict:
        cpu_default = max(1, system_utils.get_cpu_threads())
        max_workers = system_utils.get_max_workers()
        available_ram_mb = system_utils.get_available_ram_mb()
        ram_source = system_utils.get_ram_detection_source()
        service_config_map = service_config_map or {}

        service_pool_map = {
            'PiperTTS': 'Piper',
            'KokoroTTS': 'Kokoro',
            'EdgeTTS': 'EdgeTTS',
            'MmsTTS': 'MMS',
            'SupertonicTTS': 'Supertonic',
        }
        ram_per_pool_mb = {
            'Piper': RAM_PER_PROCESS_MB_ESTIMATE['PiperTTS'],
            'Kokoro': RAM_PER_PROCESS_MB_ESTIMATE['KokoroTTS'],
            'MMS': RAM_PER_PROCESS_MB_ESTIMATE['MmsTTS'],
            'Supertonic': RAM_PER_PROCESS_MB_ESTIMATE['SupertonicTTS'],
        }

        enabled_pools = self._enabled_local_pools(enabled_services)

        # Collect user overrides first.  Local overrides are preserved; the
        # only hard limits are the existing max-worker ceiling (warned) and
        # the EdgeTTS network cap handled below.
        manual_workers: Dict[str, int] = {}
        manual_service_by_pool: Dict[str, str] = {}
        for service_name, pool_name in service_pool_map.items():
            if pool_name == 'EdgeTTS':
                continue
            service_config = service_config_map.get(service_name, {}) or {}
            requested_concurrency = service_config.get('concurrency_workers')
            if not requested_concurrency:
                continue
            try:
                requested = int(requested_concurrency)
            except (TypeError, ValueError):
                logger.warning(
                    f'Service {service_name} concurrency_workers='
                    f'{requested_concurrency!r} is not an integer; ignoring it.'
                )
                continue
            if requested <= 0:
                continue
            if requested > max_workers:
                logger.warning(
                    f'Service {service_name} concurrency_workers ({requested}) '
                    f'exceeds max ({max_workers}), capping'
                )
                requested = max_workers
            manual_workers[pool_name] = requested
            manual_service_by_pool[pool_name] = service_name

        allocation, budget_meta = system_utils.allocate_local_engine_workers(
            cpu_caps={pool: cpu_default for pool in ram_per_pool_mb},
            ram_per_process_mb=ram_per_pool_mb,
            enabled_engines=enabled_pools,
            available_ram_mb=available_ram_mb,
            manual_workers=manual_workers,
        )

        defaults = {
            'PiperTTS': allocation.get('Piper', 1),
            'KokoroTTS': allocation.get('Kokoro', 1),
            'EdgeTTS': batch_constants.EDGETTS_MAX_WORKERS,
            'MmsTTS': allocation.get('MMS', 1),
            'SupertonicTTS': allocation.get('Supertonic', 1),
        }

        if available_ram_mb is None:
            logger.warning(
                f'[RAM] source={ram_source} available_mb=unknown '
                f'cpu_default={cpu_default}; local engine pools are NOT RAM-capped. '
                f'Use Advanced settings to set concurrency_workers manually if needed.'
            )
        else:
            logger.info(
                f'[RAM] source={ram_source} available_mb={available_ram_mb} '
                f'budget_mb={budget_meta.get("budget_mb")} '
                f'cpu_default={cpu_default} enabled={sorted(enabled_pools)} '
                f'defaults={defaults} estimated_mb={budget_meta.get("estimated_mb")}'
            )

        for pool_name, workers in allocation.items():
            if (
                pool_name in enabled_pools
                and pool_name not in manual_workers
                and workers < cpu_default
            ):
                service_name = next(
                    name for name, pool in service_pool_map.items()
                    if pool == pool_name
                )
                logger.info(
                    f'[RAM-CAP] {service_name} default concurrency capped to {workers} '
                    f'(cpu_default={cpu_default}) by the shared RAM budget. '
                    f'Set concurrency_workers manually in Advanced settings to override.'
                )

        if available_ram_mb is not None and budget_meta.get('minimum_over_budget'):
            logger.warning(
                f'[RAM-WARN] shared RAM budget is {budget_meta.get("budget_mb")}MB, '
                f'but the one-worker-per-enabled-engine minimum is about '
                f'{budget_meta.get("minimum_estimated_mb")}MB. Keeping 1 worker per '
                f'enabled engine; disable unused local engines or add RAM.'
            )
        elif available_ram_mb is not None and budget_meta.get('over_budget'):
            logger.warning(
                f'[RAM-WARN] manual concurrency overrides are estimated at '
                f'{budget_meta.get("estimated_mb")}MB, exceeding the shared RAM '
                f'budget of {budget_meta.get("budget_mb")}MB. Keeping the user '
                f'overrides.'
            )

        for pool_name, requested in manual_workers.items():
            if pool_name not in enabled_pools:
                continue
            service_name = manual_service_by_pool.get(pool_name, pool_name)
            safe_default = system_utils.compute_ram_aware_concurrency(
                cpu_default,
                ram_per_pool_mb.get(pool_name),
                available_ram_mb=available_ram_mb,
            )
            if requested > safe_default:
                logger.warning(
                    f'[RAM-WARN] {service_name} concurrency_workers={requested} '
                    f'exceeds the RAM-safe estimate of {safe_default} '
                    f'(available_mb={available_ram_mb}). Keeping the user override.'
                )

        engine_config = {}
        for service_name, pool_name in service_pool_map.items():
            if service_name == 'EdgeTTS':
                service_config = service_config_map.get(service_name, {}) or {}
                requested_concurrency = service_config.get('concurrency_workers')
                if requested_concurrency:
                    try:
                        requested = int(requested_concurrency)
                    except (TypeError, ValueError):
                        requested = batch_constants.EDGETTS_MAX_WORKERS
                    if requested > batch_constants.EDGETTS_MAX_WORKERS:
                        logger.warning(
                            f'Service {service_name} concurrency_workers ({requested}) '
                            f'exceeds max ({batch_constants.EDGETTS_MAX_WORKERS}), capping'
                        )
                    concurrency = min(
                        batch_constants.EDGETTS_MAX_WORKERS,
                        max(1, requested),
                    )
                else:
                    concurrency = batch_constants.EDGETTS_MAX_WORKERS
            else:
                concurrency = allocation.get(pool_name, 1)

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
            engine_config = self.build_engine_config(
                service_config_map,
                enabled_services=configuration.get_service_enabled_map(),
            )
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