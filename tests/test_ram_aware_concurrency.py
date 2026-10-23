"""
Unit tests for root cause 2.6 fix: local engine process-pool concurrency
must be capped by available RAM, not just CPU core count.

See superfreetts_macos_crash_fix_plan.md, section 2.6 / Phase 2.

These tests are pure-Python logic tests (no subprocess, no psutil real
system calls needed - psutil.virtual_memory is mocked) so they run
identically on Linux (this dev environment) and would run the same way on
macOS; they do not attempt to reproduce a real macOS crash (out of scope
per rule 0.6 in the fix plan).
"""

import sys
import os
from unittest.mock import patch, MagicMock

import pytest

addon_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, addon_dir)
sys.path.insert(0, os.path.join(addon_dir, 'external'))

from superfreetts_addon import system_utils
from superfreetts_addon import tts_orchestrator
from superfreetts_addon import batch_executor


@pytest.mark.unit
class TestComputeRamAwareConcurrency:
    """Direct tests of system_utils.compute_ram_aware_concurrency()."""

    def test_no_ram_estimate_returns_cpu_default_unchanged(self):
        """If caller passes no per-process RAM estimate, behavior must be
        identical to the old CPU-only logic (no fabricated cap)."""
        result = system_utils.compute_ram_aware_concurrency(cpu_default=10, ram_per_process_mb=None)
        assert result == 10

    def test_psutil_unavailable_falls_back_to_cpu_default(self):
        """If available RAM can't be measured, must NOT guess a number -
        falls back to the pre-existing CPU-only value."""
        with patch.object(system_utils, 'get_available_ram_mb', return_value=None):
            result = system_utils.compute_ram_aware_concurrency(cpu_default=10, ram_per_process_mb=500)
            assert result == 10

    def test_low_ram_caps_below_cpu_default(self):
        """Reproduces the reported scenario: many CPU cores, heavy
        per-process footprint, limited available RAM -> concurrency must
        be capped below cpu_default."""
        # 2000MB available, 50% budget = 1000MB budget, 500MB/process -> cap at 2
        with patch.object(system_utils, 'get_available_ram_mb', return_value=2000):
            result = system_utils.compute_ram_aware_concurrency(
                cpu_default=10, ram_per_process_mb=500, ram_budget_ratio=0.5
            )
            assert result == 2
            assert result < 10

    def test_plenty_of_ram_does_not_exceed_cpu_default(self):
        """RAM cap must never make concurrency go ABOVE the CPU-derived
        default - only ever equal or below it."""
        with patch.object(system_utils, 'get_available_ram_mb', return_value=100_000):
            result = system_utils.compute_ram_aware_concurrency(
                cpu_default=10, ram_per_process_mb=500, ram_budget_ratio=0.5
            )
            assert result == 10

    def test_never_returns_less_than_one(self):
        """Even in a pathological low-RAM scenario, must return >= 1
        so the app never ends up with a pool of size 0."""
        with patch.object(system_utils, 'get_available_ram_mb', return_value=10):
            result = system_utils.compute_ram_aware_concurrency(
                cpu_default=10, ram_per_process_mb=500, ram_budget_ratio=0.5
            )
            assert result >= 1

    def test_zero_or_negative_estimate_is_treated_as_unknown(self):
        result = system_utils.compute_ram_aware_concurrency(cpu_default=6, ram_per_process_mb=0)
        assert result == 6
        result = system_utils.compute_ram_aware_concurrency(cpu_default=6, ram_per_process_mb=-5)
        assert result == 6


@pytest.mark.unit
class TestBuildEngineConfigRamAware:
    """Tests build_engine_config() end-to-end with a mocked TTSOrchestrator,
    verifying the reported real-world scenario no longer produces an
    unbounded CPU-sized pool for heavy local engines."""

    def _make_orchestrator(self):
        # TTSOrchestrator.__init__ only stores references from `superfreetts`,
        # none of which build_engine_config() touches - a MagicMock stand-in
        # is sufficient and avoids depending on unrelated app wiring.
        return tts_orchestrator.TTSOrchestrator(MagicMock())

    def test_high_core_count_low_ram_caps_light_engine(self):
        """Simulates the user-reported scenario: a many-core machine but
        constrained available RAM, with Piper enabled.  One shared 1500MB
        budget at 200MB/process gives 7 Piper workers (CPU default 10)."""
        orch = self._make_orchestrator()
        with patch.object(system_utils, 'get_cpu_threads', return_value=10), \
             patch.object(system_utils, 'get_max_workers', return_value=10), \
             patch.object(system_utils, 'get_available_ram_mb', return_value=3000), \
             patch.object(orch, 'auto_scale_pool'):
            engine_config = orch.build_engine_config(
                service_config_map={},
                enabled_services={'PiperTTS'},
            )

        assert engine_config['Piper'] == 7
        # Disabled local engines do not spend the shared budget.
        assert engine_config['Kokoro'] == 1
        assert engine_config['MMS'] == 1
        assert engine_config['Supertonic'] == 1
        # EdgeTTS is network-based, unaffected by RAM capping, unchanged behavior
        from superfreetts_addon import batch_constants
        assert engine_config['EdgeTTS'] == batch_constants.EDGETTS_MAX_WORKERS

    def test_all_enabled_local_engines_share_one_budget(self):
        """Four enabled local engines must not each receive a separate
        50%-of-RAM budget.  With 20000MB available the shared budget is
        10000MB; the measured per-engine estimates (Piper 200MB,
        Kokoro 2400MB, MMS 500MB, Supertonic 700MB) fit 5/2/4/3 workers,
        which totals 9900MB - not four independent 10000MB budgets."""
        orch = self._make_orchestrator()
        with patch.object(system_utils, 'get_cpu_threads', return_value=8), \
             patch.object(system_utils, 'get_max_workers', return_value=16), \
             patch.object(system_utils, 'get_available_ram_mb', return_value=20000), \
             patch.object(orch, 'auto_scale_pool'):
            engine_config = orch.build_engine_config(
                service_config_map={},
                enabled_services={'PiperTTS', 'KokoroTTS', 'MmsTTS', 'SupertonicTTS'},
            )

        assert engine_config['Piper'] == 5
        assert engine_config['Kokoro'] == 2
        assert engine_config['MMS'] == 4
        assert engine_config['Supertonic'] == 3
        estimated_mb = (
            engine_config['Piper'] * tts_orchestrator.RAM_PER_PROCESS_MB_ESTIMATE['PiperTTS']
            + engine_config['Kokoro'] * tts_orchestrator.RAM_PER_PROCESS_MB_ESTIMATE['KokoroTTS']
            + engine_config['MMS'] * tts_orchestrator.RAM_PER_PROCESS_MB_ESTIMATE['MmsTTS']
            + engine_config['Supertonic'] * tts_orchestrator.RAM_PER_PROCESS_MB_ESTIMATE['SupertonicTTS']
        )
        assert estimated_mb <= 20000 * 0.5

    def test_manual_concurrency_workers_override_is_not_ram_capped(self):
        """A user who explicitly sets concurrency_workers must keep full
        control - the RAM cap only applies to the computed default, per
        Phase 2 step 3 of the fix plan (must not break existing override
        behavior)."""
        orch = self._make_orchestrator()
        with patch.object(system_utils, 'get_cpu_threads', return_value=10), \
             patch.object(system_utils, 'get_max_workers', return_value=10), \
             patch.object(system_utils, 'get_available_ram_mb', return_value=3000), \
             patch.object(orch, 'auto_scale_pool'):
            engine_config = orch.build_engine_config(
                service_config_map={'SupertonicTTS': {'concurrency_workers': 9}},
                enabled_services={'SupertonicTTS'},
            )

        # Explicit user value (9) must survive even though the RAM-derived
        # default for Supertonic would have been 3 in this scenario.
        assert engine_config['Supertonic'] == 9

    def test_enabled_services_are_read_from_configuration(self):
        stts = MagicMock()
        stts.get_configuration.return_value.get_service_enabled_map.return_value = {
            'PiperTTS': True,
            'KokoroTTS': False,
        }
        orch = tts_orchestrator.TTSOrchestrator(stts)
        with patch.object(system_utils, 'get_cpu_threads', return_value=8), \
             patch.object(system_utils, 'get_max_workers', return_value=8), \
             patch.object(system_utils, 'get_available_ram_mb', return_value=3000), \
             patch.object(orch, 'auto_scale_pool'):
            engine_config = orch.build_engine_config(service_config_map={})

        assert engine_config['Piper'] == 7
        assert engine_config['Kokoro'] == 1

    def test_no_psutil_falls_back_to_cpu_only_except_kokoro_safety_cap(self):
        """When available RAM can't be measured at all, pools fall back to
        the CPU-derived default instead of a fabricated RAM cap.  The one
        exception is the measured-memory safety ceiling for Kokoro, which
        must hold even when RAM is unknown."""
        orch = self._make_orchestrator()
        with patch.object(system_utils, 'get_cpu_threads', return_value=8), \
             patch.object(system_utils, 'get_max_workers', return_value=8), \
             patch.object(system_utils, 'get_total_cpu_count', return_value=32), \
             patch.object(system_utils, 'get_available_ram_mb', return_value=None), \
             patch.object(orch, 'auto_scale_pool'):
            engine_config = orch.build_engine_config(
                service_config_map={},
                enabled_services={'PiperTTS', 'KokoroTTS', 'MmsTTS', 'SupertonicTTS'},
            )

        assert engine_config['Piper'] == 8
        assert engine_config['Kokoro'] == tts_orchestrator.KOKORO_MAX_AUTO_WORKERS
        assert engine_config['MMS'] == 8
        assert engine_config['Supertonic'] == 8

    def test_kokoro_auto_workers_are_hard_capped_with_plenty_of_ram(self):
        """Even on a huge machine the automatic Kokoro pool must stay at or
        below KOKORO_MAX_AUTO_WORKERS: one measured runner peaked at ~3.9GB,
        so 8 auto workers would be ~31GB."""
        orch = self._make_orchestrator()
        with patch.object(system_utils, 'get_cpu_threads', return_value=16), \
             patch.object(system_utils, 'get_max_workers', return_value=16), \
             patch.object(system_utils, 'get_available_ram_mb', return_value=65536), \
             patch.object(orch, 'auto_scale_pool'):
            engine_config = orch.build_engine_config(
                service_config_map={},
                enabled_services={'KokoroTTS'},
            )

        assert engine_config['Kokoro'] == tts_orchestrator.KOKORO_MAX_AUTO_WORKERS

    def test_kokoro_manual_override_bypasses_the_auto_cap(self):
        """An explicit concurrency_workers value remains the user's call."""
        orch = self._make_orchestrator()
        with patch.object(system_utils, 'get_cpu_threads', return_value=16), \
             patch.object(system_utils, 'get_max_workers', return_value=16), \
             patch.object(system_utils, 'get_available_ram_mb', return_value=65536), \
             patch.object(orch, 'auto_scale_pool'):
            engine_config = orch.build_engine_config(
                service_config_map={'KokoroTTS': {'concurrency_workers': 4}},
                enabled_services={'KokoroTTS'},
            )

        assert engine_config['Kokoro'] == 4


@pytest.mark.unit
class TestPreBatchRamRefresh:
    """The batch pipeline re-evaluates RAM before spawning runners."""

    def _make_orchestrator(self):
        stts = MagicMock()
        stts.get_configuration.return_value.get_service_config.return_value = {}
        stts.get_configuration.return_value.get_service_enabled_map.return_value = {
            'PiperTTS': True,
        }
        return tts_orchestrator.TTSOrchestrator(stts), stts

    def test_rebuilds_executor_when_current_ram_changes_worker_count(self):
        orch, stts = self._make_orchestrator()
        old_executor = MagicMock(engine_config={'Piper': 8, 'default': 8})
        orch.executor = old_executor
        stts.executor = old_executor
        new_executor = MagicMock(engine_config={'Piper': 2, 'default': 2})

        with patch.object(orch, 'build_engine_config', return_value={'Piper': 2, 'default': 2}), \
             patch.object(batch_executor, 'get_multi_engine_executor', return_value=new_executor):
            result = orch.refresh_engine_pools_for_current_ram()

        assert result == {'Piper': 2, 'default': 2}
        assert orch.executor is new_executor
        assert stts.executor is new_executor

    def test_keeps_executor_when_config_is_unchanged(self):
        orch, stts = self._make_orchestrator()
        executor = MagicMock(engine_config={'Piper': 2, 'default': 2})
        orch.executor = executor
        stts.executor = executor

        with patch.object(orch, 'build_engine_config', return_value={'Piper': 2, 'default': 2}), \
             patch.object(batch_executor, 'get_multi_engine_executor') as get_executor:
            result = orch.refresh_engine_pools_for_current_ram()

        assert result == {'Piper': 2, 'default': 2}
        get_executor.assert_not_called()
        assert orch.executor is executor

    def test_refresh_failure_is_non_fatal(self):
        orch, _ = self._make_orchestrator()
        with patch.object(orch, 'build_engine_config', side_effect=RuntimeError('boom')):
            assert orch.refresh_engine_pools_for_current_ram() is None
