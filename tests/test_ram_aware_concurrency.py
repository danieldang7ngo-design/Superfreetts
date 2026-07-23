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

    def test_high_core_count_low_ram_caps_heavy_engines(self):
        """Simulates the user-reported scenario: a many-core machine but
        constrained available RAM, no manual concurrency_workers override.
        Piper (light, 200MB/proc) should get a higher default than
        Supertonic/Kokoro/MMS (heavy, 500MB/proc estimate)."""
        orch = self._make_orchestrator()
        with patch.object(system_utils, 'get_max_workers', return_value=10), \
             patch.object(system_utils, 'get_available_ram_mb', return_value=3000), \
             patch.object(orch, 'auto_scale_pool'):
            engine_config = orch.build_engine_config(service_config_map={})

        # 3000MB available * 0.5 budget = 1500MB budget
        # Piper: 1500 // 200 = 7 (below cpu_default=10 -> capped)
        # Kokoro/MMS/Supertonic: 1500 // 500 = 3 (below cpu_default=10 -> capped)
        assert engine_config['Piper'] == 7
        assert engine_config['Kokoro'] == 3
        assert engine_config['MMS'] == 3
        assert engine_config['Supertonic'] == 3
        # EdgeTTS is network-based, unaffected by RAM capping, unchanged behavior
        from superfreetts_addon import batch_constants
        assert engine_config['EdgeTTS'] == batch_constants.EDGETTS_MAX_WORKERS

    def test_manual_concurrency_workers_override_is_not_ram_capped(self):
        """A user who explicitly sets concurrency_workers must keep full
        control - the RAM cap only applies to the computed default, per
        Phase 2 step 3 of the fix plan (must not break existing override
        behavior)."""
        orch = self._make_orchestrator()
        with patch.object(system_utils, 'get_max_workers', return_value=10), \
             patch.object(system_utils, 'get_available_ram_mb', return_value=3000), \
             patch.object(orch, 'auto_scale_pool'):
            engine_config = orch.build_engine_config(
                service_config_map={'SupertonicTTS': {'concurrency_workers': 9}}
            )

        # Explicit user value (9) must survive even though the RAM-derived
        # default for Supertonic would have been 3 in this scenario.
        assert engine_config['Supertonic'] == 9

    def test_no_psutil_falls_back_to_old_cpu_only_behavior(self):
        """When available RAM can't be measured at all, behavior must be
        identical to the pre-fix code (pure cpu_default), not a crash and
        not a fabricated cap."""
        orch = self._make_orchestrator()
        with patch.object(system_utils, 'get_max_workers', return_value=8), \
             patch.object(system_utils, 'get_available_ram_mb', return_value=None), \
             patch.object(orch, 'auto_scale_pool'):
            engine_config = orch.build_engine_config(service_config_map={})

        assert engine_config['Piper'] == 8
        assert engine_config['Kokoro'] == 8
        assert engine_config['MMS'] == 8
        assert engine_config['Supertonic'] == 8
