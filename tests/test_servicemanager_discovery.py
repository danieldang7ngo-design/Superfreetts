"""Discovery/import recovery tests for ``ServiceManager`` (audit 2.4 and 2.5).

``init_services()`` used to mark service discovery as complete even when a
service module failed to import, so a transient failure (file lock, engine DLL
still unloading, half-written engine directory) hid that service for the rest
of the Anki session.  These tests pin the recovery contract:

* a module that fails once and imports cleanly later shows up on the next
  ``init_services()`` call;
* a permanently broken module is retried at most
  ``_service_import_max_retries`` times and then given up on;
* an unexpected exception during discovery is never cached as "done";
* discovery reads ``name``/``service_fee`` without running the (expensive)
  service constructors.
"""

import importlib
import pathlib
import sys
import textwrap
import uuid
from unittest.mock import patch

import pytest

from superfreetts_addon import constants, servicemanager


_SERVICE_TEMPLATE = """
from superfreetts_addon import constants
from superfreetts_addon import service


class {class_name}(service.ServiceBase):
    def __init__(self):
        {class_name}.instances += 1
        super().__init__()

    instances = 0

    @property
    def service_type(self):
        return constants.ServiceType.tts

    @property
    def service_fee(self):
        return constants.ServiceFee.free

    def voice_list(self):
        return []

    def get_tts_audio(self, source_text, tts_voice, options):
        return None
"""

_FAILING_SOURCE = """
import pathlib

_COUNTER = pathlib.Path(__file__).with_name("import_attempts.txt")
with _COUNTER.open("a", encoding="utf-8") as handle:
    handle.write("x")

raise RuntimeError("transient service import failure")
"""


def _make_package(tmp_path, module_name, source):
    """Write a throwaway service package and put it on ``sys.path``."""
    package_name = f"sftts_discovery_{uuid.uuid4().hex[:8]}"
    package_dir = tmp_path / package_name
    services_dir = package_dir / "services"
    services_dir.mkdir(parents=True)
    (package_dir / "__init__.py").write_text("", encoding="utf-8")
    (services_dir / "__init__.py").write_text("", encoding="utf-8")
    (services_dir / f"{module_name}.py").write_text(textwrap.dedent(source), encoding="utf-8")

    sys.path.insert(0, str(tmp_path))
    importlib.invalidate_caches()
    return package_name, services_dir


def _cleanup_package(package_name, tmp_path):
    for name in list(sys.modules):
        if name == package_name or name.startswith(f"{package_name}."):
            del sys.modules[name]
    try:
        sys.path.remove(str(tmp_path))
    except ValueError:
        pass
    importlib.invalidate_caches()


def _attempts(services_dir):
    counter = pathlib.Path(services_dir) / "import_attempts.txt"
    if not counter.exists():
        return 0
    return len(counter.read_text(encoding="utf-8"))


@pytest.mark.unit
def test_transient_import_failure_recovers_on_next_init_services(tmp_path):
    package_name, services_dir = _make_package(tmp_path, "service_flaky", _FAILING_SOURCE)
    try:
        manager = servicemanager.ServiceManager(
            str(services_dir), f"{package_name}.services", allow_test_services=False
        )

        manager.init_services()

        assert "_RecoveredService" not in manager._service_classes
        assert manager._services_discovered is False
        assert manager._failed_service_modules == {"service_flaky": 1}

        # The module is fixed (e.g. the engine binary finished unpacking).
        (services_dir / "service_flaky.py").write_text(
            textwrap.dedent(_SERVICE_TEMPLATE.format(class_name="_RecoveredService")),
            encoding="utf-8",
        )
        importlib.invalidate_caches()

        manager.init_services()

        assert "_RecoveredService" in manager._service_classes
        assert manager.service_exists("_RecoveredService")
        assert manager._services_discovered is True
        assert manager._failed_service_modules == {}
        # Only the first (failing) import touched the counter file.
        assert _attempts(services_dir) == 1
    finally:
        _cleanup_package(package_name, tmp_path)


@pytest.mark.unit
def test_permanently_failing_module_stops_after_retry_limit(tmp_path):
    package_name, services_dir = _make_package(tmp_path, "service_broken", _FAILING_SOURCE)
    try:
        manager = servicemanager.ServiceManager(
            str(services_dir), f"{package_name}.services", allow_test_services=False
        )

        for _ in range(5):
            manager.init_services()

        # Three attempts, then the manager gives up instead of spinning forever.
        assert manager._service_import_max_retries == 3
        assert _attempts(services_dir) == 3
        assert manager._failed_service_modules == {"service_broken": 3}
        assert manager._services_discovered is True
    finally:
        _cleanup_package(package_name, tmp_path)


@pytest.mark.unit
def test_exception_during_discovery_is_not_cached_as_discovered(tmp_path):
    package_name, services_dir = _make_package(
        tmp_path,
        "service_ok",
        _SERVICE_TEMPLATE.format(class_name="_FineService"),
    )
    try:
        manager = servicemanager.ServiceManager(
            str(services_dir), f"{package_name}.services", allow_test_services=False
        )

        with patch.object(manager, "_cache_service_classes", side_effect=RuntimeError("boom")):
            with pytest.raises(RuntimeError):
                manager.init_services()

        assert manager._services_discovered is False
    finally:
        _cleanup_package(package_name, tmp_path)


@pytest.mark.unit
def test_discovery_reads_name_and_fee_without_calling_init(tmp_path):
    package_name, services_dir = _make_package(
        tmp_path,
        "service_probe",
        _SERVICE_TEMPLATE.format(class_name="_ProbeService"),
    )
    try:
        module = importlib.import_module(f"{package_name}.services.service_probe")
        manager = servicemanager.ServiceManager(
            str(services_dir), f"{package_name}.services", allow_test_services=False
        )

        manager.init_services()

        assert "_ProbeService" in manager._service_classes
        # Cached from class-level/probe reads: the constructor never ran.
        assert module._ProbeService.instances == 0
    finally:
        _cleanup_package(package_name, tmp_path)


@pytest.mark.unit
def test_class_level_service_fee_is_used_without_an_instance(tmp_path):
    class _PlainClassFeeService:
        # Deliberately a plain class attribute (not a property) plus a
        # constructor that explodes: the class-level read must be enough.
        name = "_PlainClassFeeService"
        service_fee = constants.ServiceFee.free

        def __init__(self):
            raise AssertionError("must not be instantiated")

        def test_service(self):
            return False

        def voice_list(self):
            return []

        def get_tts_audio(self, source_text, voice, options):
            return None

    manager = servicemanager.ServiceManager(str(tmp_path), "pkg.services", allow_test_services=False)

    name, service_fee, is_test_service = manager._describe_service_class(_PlainClassFeeService)

    assert name == "_PlainClassFeeService"
    assert service_fee == constants.ServiceFee.free
    assert is_test_service is False
