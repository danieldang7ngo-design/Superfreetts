"""
Unit tests for servicemanager.ServiceManager.

Strategy:
- Bypass real service file scanning by injecting FakeService classes directly
  into ServiceManager._service_classes and setting _services_discovered=True.
- For discovery tests, create a real temporary directory with dummy service_*.py files.
- No Anki runtime needed: mock_anki.mock_all() is called by conftest.py at import time.
"""

import os
import sys
import pytest
from unittest.mock import MagicMock, patch

from superfreetts_addon.servicemanager import ServiceManager
from superfreetts_addon.service import ServiceBase
from superfreetts_addon import constants


# ─────────────────────────────────────────────────────────────
# Local fake services (defined here to not pollute global state
# between test files — each class is unique)
# ─────────────────────────────────────────────────────────────

class _FreeTestServiceA(ServiceBase):
    """Minimal free service for injection into ServiceManager."""

    @property
    def service_type(self):
        return constants.ServiceType.tts

    @property
    def service_fee(self):
        return constants.ServiceFee.free

    def voice_list(self):
        return []

    def get_tts_audio(self, source_text, voice, options):
        return b"fake-audio"

    def configuration_options(self):
        return {"workers": 2}


class _FreeTestServiceB(ServiceBase):
    """Second minimal free service."""

    @property
    def service_type(self):
        return constants.ServiceType.tts

    @property
    def service_fee(self):
        return constants.ServiceFee.free

    def voice_list(self):
        return []

    def get_tts_audio(self, source_text, voice, options):
        return b"fake-audio-b"

    def configuration_options(self):
        return {}


class _PaidTestService(ServiceBase):
    """Paid service — should be excluded from ServiceManager."""

    @property
    def service_type(self):
        return constants.ServiceType.tts

    @property
    def service_fee(self):
        return constants.ServiceFee.paid

    def voice_list(self):
        return []

    def get_tts_audio(self, source_text, voice, options):
        return b""

    def configuration_options(self):
        return {}


class _IsTestService(ServiceBase):
    """Service that identifies itself as a test service."""

    @property
    def service_type(self):
        return constants.ServiceType.tts

    @property
    def service_fee(self):
        return constants.ServiceFee.free

    def test_service(self):
        return True  # marks itself as test

    def voice_list(self):
        return []

    def get_tts_audio(self, source_text, voice, options):
        return b""

    def configuration_options(self):
        return {}


# ─────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────

def _make_sm(tmp_path, allow_test=False, classes=None):
    """
    Create a ServiceManager with a fake services directory.
    Optionally inject service classes directly to bypass file scanning.
    """
    services_dir = tmp_path / "services"
    services_dir.mkdir()

    sm = ServiceManager(
        services_directory=str(services_dir),
        package_name="superfreetts_addon.services",
        allow_test_services=allow_test,
    )

    if classes is not None:
        # Inject classes directly, mark as discovered to skip real import
        for cls in classes:
            instance = cls()
            sm._service_classes[instance.name] = cls
        sm._services_discovered = True

    return sm


@pytest.fixture()
def sm_with_two_services(tmp_path):
    """ServiceManager pre-loaded with two free services."""
    return _make_sm(tmp_path, classes=[_FreeTestServiceA, _FreeTestServiceB])


@pytest.fixture()
def sm_empty(tmp_path):
    """ServiceManager with no services injected (empty)."""
    return _make_sm(tmp_path, classes=[])


# ─────────────────────────────────────────────────────────────
# Service Discovery (file system scanning)
# ─────────────────────────────────────────────────────────────

class TestServiceDiscovery:

    def test_discover_services_finds_service_py_files(self, tmp_path):
        """discover_services() returns modules for every service_*.py file."""
        services_dir = tmp_path / "services"
        services_dir.mkdir()
        (services_dir / "service_alpha.py").write_text("# stub")
        (services_dir / "service_beta.py").write_text("# stub")

        sm = ServiceManager(str(services_dir), "pkg", False)
        found = sm.discover_services()

        assert "service_alpha" in found
        assert "service_beta" in found

    def test_discover_services_empty_dir_returns_empty(self, tmp_path):
        """discover_services() on an empty directory returns []."""
        services_dir = tmp_path / "empty_services"
        services_dir.mkdir()

        sm = ServiceManager(str(services_dir), "pkg", False)
        assert sm.discover_services() == []

    def test_discover_services_nonexistent_dir_returns_empty(self, tmp_path):
        """discover_services() when directory doesn't exist returns []."""
        sm = ServiceManager(str(tmp_path / "does_not_exist"), "pkg", False)
        assert sm.discover_services() == []

    def test_discover_ignores_non_service_files(self, tmp_path):
        """discover_services() ignores files that don't start with service_."""
        services_dir = tmp_path / "services"
        services_dir.mkdir()
        (services_dir / "utils.py").write_text("# utility")
        (services_dir / "service_real.py").write_text("# real service")
        (services_dir / "__init__.py").write_text("")

        sm = ServiceManager(str(services_dir), "pkg", False)
        found = sm.discover_services()

        assert "service_real" in found
        assert "utils" not in found
        assert "__init__" not in found

    def test_discover_services_no_duplicates(self, tmp_path):
        """discover_services() does not return duplicate module names."""
        services_dir = tmp_path / "services"
        services_dir.mkdir()
        (services_dir / "service_dup.py").write_text("# stub")

        sm = ServiceManager(str(services_dir), "pkg", False)
        found = sm.discover_services()
        assert found.count("service_dup") == 1


# ─────────────────────────────────────────────────────────────
# Service Class Caching (_cache_service_classes)
# ─────────────────────────────────────────────────────────────

class TestServiceClassCaching:

    def test_cache_service_classes_includes_free_services(self, tmp_path):
        """_cache_service_classes caches free services."""
        sm = _make_sm(tmp_path)

        # Temporarily ensure our fake classes are subclasses visible to __subclasses__
        with patch.object(ServiceBase, "__subclasses__", return_value=[_FreeTestServiceA]):
            sm._cache_service_classes()

        assert "_FreeTestServiceA" in sm._service_classes

    def test_cache_skips_paid_services(self, tmp_path):
        """_cache_service_classes excludes paid services."""
        sm = _make_sm(tmp_path)

        with patch.object(ServiceBase, "__subclasses__",
                          return_value=[_FreeTestServiceA, _PaidTestService]):
            sm._cache_service_classes()

        assert "_FreeTestServiceA" in sm._service_classes
        assert "_PaidTestService" not in sm._service_classes

    def test_cache_skips_test_services_when_not_allowed(self, tmp_path):
        """_cache_service_classes excludes test services when allow_test_services=False."""
        sm = _make_sm(tmp_path, allow_test=False)

        with patch.object(ServiceBase, "__subclasses__",
                          return_value=[_FreeTestServiceA, _IsTestService]):
            sm._cache_service_classes()

        assert "_FreeTestServiceA" in sm._service_classes
        assert "_IsTestService" not in sm._service_classes

    def test_cache_includes_test_services_when_allowed(self, tmp_path):
        """_cache_service_classes keeps test services when allow_test_services=True."""
        sm = _make_sm(tmp_path, allow_test=True)

        with patch.object(ServiceBase, "__subclasses__",
                          return_value=[_IsTestService]):
            sm._cache_service_classes()

        assert "_IsTestService" in sm._service_classes


# ─────────────────────────────────────────────────────────────
# Service Instantiation
# ─────────────────────────────────────────────────────────────

class TestServiceInstantiation:

    def test_instantiate_all_services_populates_services(self, sm_with_two_services):
        """After instantiate_all_services(), self.services is populated."""
        sm_with_two_services.instantiate_all_services()
        assert len(sm_with_two_services.services) == 2

    def test_instantiate_all_services_is_idempotent(self, sm_with_two_services):
        """Calling instantiate_all_services() twice doesn't double-instantiate."""
        sm_with_two_services.instantiate_all_services()
        count_first = len(sm_with_two_services.services)
        sm_with_two_services.instantiate_all_services()
        count_second = len(sm_with_two_services.services)
        assert count_first == count_second

    def test_instantiate_service_lazy_loads_single_service(self, tmp_path):
        """instantiate_service_lazy() loads exactly the requested service."""
        sm = _make_sm(tmp_path, classes=[_FreeTestServiceA, _FreeTestServiceB])

        sm.instantiate_service_lazy("_FreeTestServiceA")

        assert "_FreeTestServiceA" in sm.services
        assert "_FreeTestServiceB" not in sm.services  # not loaded yet

    def test_instantiate_service_lazy_noop_if_already_loaded(self, tmp_path):
        """instantiate_service_lazy() on an already-loaded service is a no-op."""
        sm = _make_sm(tmp_path, classes=[_FreeTestServiceA])
        sm.instantiate_all_services()

        original_instance = sm.services["_FreeTestServiceA"]
        sm.instantiate_service_lazy("_FreeTestServiceA")

        assert sm.services["_FreeTestServiceA"] is original_instance


# ─────────────────────────────────────────────────────────────
# Service Access
# ─────────────────────────────────────────────────────────────

class TestServiceAccess:

    def test_get_service_returns_instance(self, sm_with_two_services):
        """get_service() returns the instantiated service object."""
        sm_with_two_services.instantiate_all_services()
        svc = sm_with_two_services.get_service("_FreeTestServiceA")
        assert svc is not None
        assert isinstance(svc, _FreeTestServiceA)

    def test_get_service_unknown_returns_none(self, sm_with_two_services):
        """get_service() for an unknown name returns None (no raise)."""
        sm_with_two_services.instantiate_all_services()
        result = sm_with_two_services.get_service("NonExistentService")
        assert result is None

    def test_service_exists_true_after_instantiation(self, sm_with_two_services):
        """service_exists() returns True for an instantiated service."""
        sm_with_two_services.instantiate_all_services()
        assert sm_with_two_services.service_exists("_FreeTestServiceA") is True

    def test_service_exists_false_for_unknown(self, sm_empty):
        """service_exists() returns False for a service not in self.services."""
        sm_empty.instantiate_all_services()
        assert sm_empty.service_exists("NonExistentService") is False

    def test_get_all_services_returns_list(self, sm_with_two_services):
        """get_all_services() returns a list with all instantiated services."""
        sm_with_two_services.instantiate_all_services()
        all_svcs = sm_with_two_services.get_all_services()
        assert isinstance(all_svcs, list)
        assert len(all_svcs) == 2

    def test_get_all_services_empty(self, sm_empty):
        """get_all_services() returns empty list when no services."""
        sm_empty.instantiate_all_services()
        assert sm_empty.get_all_services() == []


# ─────────────────────────────────────────────────────────────
# Service Configuration
# ─────────────────────────────────────────────────────────────

def _make_config_model(enabled_map, service_config=None):
    """Build a minimal mock configuration model."""
    model = MagicMock()
    model.get_service_enabled_map.return_value = dict(enabled_map)
    model.get_service_config.return_value = service_config or {}
    model.set_service_enabled_map = MagicMock()
    model.set_service_config = MagicMock()
    return model


class TestServiceConfiguration:

    def test_configure_sets_service_enabled_flag(self, sm_with_two_services):
        """configure() applies the enabled state from the configuration model."""
        sm_with_two_services.instantiate_all_services()

        config = _make_config_model({"_FreeTestServiceA": True, "_FreeTestServiceB": False})
        sm_with_two_services.configure(config)

        assert sm_with_two_services.services["_FreeTestServiceA"].enabled is True
        assert sm_with_two_services.services["_FreeTestServiceB"].enabled is False

    def test_configure_calls_service_configure_with_dict(self, sm_with_two_services):
        """configure() passes per-service config dict to service.configure()."""
        sm_with_two_services.instantiate_all_services()

        service_cfg = {"_FreeTestServiceA": {"key": "value"}}
        config = _make_config_model(
            {"_FreeTestServiceA": True, "_FreeTestServiceB": False},
            service_config=service_cfg,
        )
        sm_with_two_services.configure(config)

        svc = sm_with_two_services.services["_FreeTestServiceA"]
        assert svc._config == {"key": "value"}

    def test_service_configuration_options_delegates_to_service(self, sm_with_two_services):
        """service_configuration_options() returns what the service reports."""
        sm_with_two_services.instantiate_all_services()
        opts = sm_with_two_services.service_configuration_options("_FreeTestServiceA")
        # _FreeTestServiceA.configuration_options() returns {"workers": 2}
        assert opts == {"workers": 2}

    def test_service_configuration_options_unknown_returns_empty(self, sm_empty):
        """service_configuration_options() for missing service returns {}."""
        sm_empty.instantiate_all_services()
        result = sm_empty.service_configuration_options("GhostService")
        assert result == {}

    def test_remove_non_existent_services_cleans_enabled_map(self, sm_with_two_services):
        """remove_non_existent_services removes stale entries from enabled map."""
        sm_with_two_services.instantiate_all_services()

        # Config references a service that doesn't exist in sm
        enabled_map = {
            "_FreeTestServiceA": True,
            "StaleService": True,   # not in sm.services
        }
        config = _make_config_model(enabled_map)
        sm_with_two_services.remove_non_existent_services(config)

        updated_map = config.get_service_enabled_map()
        assert "StaleService" not in updated_map
        assert "_FreeTestServiceA" in updated_map
