"""Smoke-test every service and subprocess-runner module's import path."""

import importlib
import pkgutil

import pytest

from superfreetts_addon import services as services_package


_RUNNER_MODULES = (
    "kokoro_runner",
    "piper_runner",
    "sherpa_runner_v2",
    "supertonic_runner",
    "runner_base",
    "test_runner",
)


@pytest.mark.unit
def test_all_service_modules_import_cleanly():
    failures = []
    for module_info in pkgutil.iter_modules(services_package.__path__):
        if not module_info.name.startswith("service_"):
            continue
        full_name = f"{services_package.__name__}.{module_info.name}"
        try:
            importlib.import_module(full_name)
        except Exception as exc:  # pragma: no cover - failure path only
            failures.append(f"{full_name}: {type(exc).__name__}: {exc}")

    assert not failures, "Service modules failed to import:\n" + "\n".join(failures)


@pytest.mark.unit
def test_runner_modules_import_without_loading_runtime_dependencies():
    failures = []
    for module_name in _RUNNER_MODULES:
        full_name = f"{services_package.__name__}.{module_name}"
        try:
            importlib.import_module(full_name)
        except Exception as exc:  # pragma: no cover - failure path only
            failures.append(f"{full_name}: {type(exc).__name__}: {exc}")

    assert not failures, "Runner modules failed to import:\n" + "\n".join(failures)
