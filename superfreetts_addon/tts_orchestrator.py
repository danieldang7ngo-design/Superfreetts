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
# These values were re-based on the 2026-10-22 resource audit
# (AI_Documents/bao-cao-kiem-toan-superfreetts-2026-10-22.md, P0-1):
#   * Kokoro: 3,933 MB tree RSS for one runner, 4,662 MB for two.  The old
#     500 MB figure was a user report, never measured, and let the allocator
#     hand Kokoro 6 workers on a 16 GB host.  2,400 MB/worker is the measured
#     marginal cost of an extra runner, but a single cold runner peaks much
#     higher, so automatic scaling is hard-capped by
#     KOKORO_MAX_AUTO_WORKERS below instead of relying on this number alone.
#   * Supertonic: 687 MB measured for one runner (was 500).
#   * Piper (327 MB tree for two runners) and MMS (450 MB) matched their
#     existing estimates closely enough to keep.
# Manual per-service `concurrency_workers` always overrides this table; it
# only affects the computed default.
RAM_PER_PROCESS_MB_ESTIMATE = {
    'PiperTTS': 200,
    'KokoroTTS': 2400,
    'MmsTTS': 500,
    'SupertonicTTS': 700,
}

# Hard ceiling for the *automatic* Kokoro pool size, independent of measured
# available RAM.  A single Kokoro runner peaked at ~3.9 GB, so the old
# auto-scaled 6-8 workers on a 16 GB machine could exhaust physical RAM.
# This limit only applies when no explicit `concurrency_workers` value is
# configured for KokoroTTS; manual overrides are still honoured and only log
# a warning when they exceed the RAM-safe estimate.
KOKORO_MAX_AUTO_WORKERS = 2

SERVICE_POOL_MAP = {
    'PiperTTS': 'Piper',
    'KokoroTTS': 'Kokoro',
    'EdgeTTS': 'EdgeTTS',
    'MmsTTS': 'MMS',
    'SupertonicTTS': 'Supertonic',
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

        # Safety ceiling for automatic Kokoro scaling (see
        # KOKORO_MAX_AUTO_WORKERS).  Applied to the CPU cap handed to the
        # allocator so it also holds when available RAM cannot be measured;
        # an explicit per-service override bypasses it.
        cpu_caps = {pool: cpu_default for pool in ram_per_pool_mb}
        if 'Kokoro' in enabled_pools and 'Kokoro' not in manual_workers:
            capped_kokoro = min(cpu_caps['Kokoro'], KOKORO_MAX_AUTO_WORKERS)
            if capped_kokoro < cpu_caps['Kokoro']:
                logger.info(
                    f'[RAM-CAP] KokoroTTS automatic concurrency capped to '
                    f'{capped_kokoro} by the measured-memory safety limit '
                    f'(KOKORO_MAX_AUTO_WORKERS={KOKORO_MAX_AUTO_WORKERS}); '
                    f'set concurrency_workers manually to override.'
                )
            cpu_caps['Kokoro'] = capped_kokoro

        allocation, budget_meta = system_utils.allocate_local_engine_workers(
            cpu_caps=cpu_caps,
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

        self._enforce_thread_budget(engine_config, service_config_map, manual_workers, enabled_pools)

        for pool_name, concurrency in engine_config.items():
            self.auto_scale_pool(pool_name, concurrency)

        return engine_config

    def _local_thread_counts(self, service_config_map: dict) -> Dict[str, int]:
        """Read ``num_threads`` per local engine pool (the engine default is 1)."""
        counts = {}
        for service_name, pool_name in SERVICE_POOL_MAP.items():
            if pool_name == 'EdgeTTS' or pool_name in counts:
                continue
            service_config = service_config_map.get(service_name, {}) or {}
            try:
                threads = int(service_config.get('num_threads', 1) or 1)
            except (TypeError, ValueError):
                threads = 1
            counts[pool_name] = max(1, threads)
        return counts

    def _enforce_thread_budget(self, engine_config: dict, service_config_map: dict, manual_workers: Dict[str, int], enabled_pools=None) -> dict:
        """Keep sum(workers x threads) within the real logical CPU count.

        The budget is the machine's logical CPU count, not ``get_cpu_threads()``
        (which is a default worker count capped at 8).  Automatic allocations
        are lowered, largest product first; explicit ``concurrency_workers``
        overrides are preserved and only warned about.
        """
        thread_counts = self._local_thread_counts(service_config_map)
        # Disabled engines keep a 1-worker pool but never run, so they do not
        # consume the budget (same rule as the shared RAM allocator).
        active_pools = set(enabled_pools) if enabled_pools is not None else set(engine_config)
        active_workers = {
            pool: workers for pool, workers in engine_config.items()
            if pool in active_pools or pool in manual_workers
        }
        budget = system_utils.compute_thread_budget(active_workers, thread_counts)

        pool_summary = {pool: info['threads_total'] for pool, info in budget['per_pool'].items()}
        if not budget['over_budget']:
            logger.info(
                f"[THREAD-BUDGET] total_threads={budget['total_threads']} "
                f"logical_cpus={budget['cpu_count']} per_pool={pool_summary}"
            )
            return engine_config

        logger.warning(
            f"[THREAD-CAP] sum(workers x threads)={budget['total_threads']} exceeds "
            f"{budget['cpu_count']} logical CPUs; lowering automatic worker counts. "
            f"Set num_threads/concurrency_workers in Advanced settings to override."
        )

        auto_pools = [
            pool_name for pool_name, info in budget['per_pool'].items()
            if pool_name not in manual_workers and info['workers'] > 1
        ]
        while budget['total_threads'] > budget['cpu_count'] and auto_pools:
            pool_name = max(
                auto_pools,
                key=lambda name: engine_config.get(name, 1) * thread_counts.get(name, 1),
            )
            new_workers = max(1, engine_config.get(pool_name, 1) - 1)
            logger.info(
                f"[THREAD-CAP] {pool_name}: {engine_config.get(pool_name, 1)} -> {new_workers} "
                f"workers (threads={thread_counts.get(pool_name, 1)})"
            )
            engine_config[pool_name] = new_workers
            auto_pools = [name for name in auto_pools if engine_config.get(name, 1) > 1]
            active_workers = {
                pool: workers for pool, workers in engine_config.items()
                if pool in active_pools or pool in manual_workers
            }
            budget = system_utils.compute_thread_budget(active_workers, thread_counts)

        if budget['total_threads'] > budget['cpu_count']:
            manual_detail = ', '.join(
                f"{pool}={engine_config.get(pool, 1)}x{thread_counts.get(pool, 1)}"
                for pool in active_workers
                if pool in manual_workers
            ) or 'none'
            logger.warning(
                f"[THREAD-CAP] still {budget['total_threads']} threads > "
                f"{budget['cpu_count']} logical CPUs after lowering automatic pools; "
                f"manual overrides are kept ({manual_detail}). Lower num_threads or "
                f"concurrency_workers if the machine feels sluggish."
            )

        pool_summary = {pool: info['threads_total'] for pool, info in budget['per_pool'].items()}
        logger.info(
            f"[THREAD-BUDGET] total_threads={budget['total_threads']} "
            f"logical_cpus={budget['cpu_count']} per_pool={pool_summary}"
        )
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