"""
Pytest configuration and fixtures for Super Free TTS testing.
"""

import sys
# Mock Anki/AQT before anything else
from . import mock_anki
mock_anki.mock_all()

import os
import pytest
from unittest.mock import Mock, patch

# Add parent directory to path for imports
addon_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, addon_dir)
sys.path.insert(0, os.path.join(addon_dir, 'external'))


class MockAnkiUtils:
    """Mock Anki utilities for testing"""
    
    def __init__(self):
        self.profile_folder = "/tmp/anki_test"
        self.collection = None
        self.user_uuid = "test-uuid-12345"
    
    def get_uuid(self):
        return self.user_uuid
    
    def get_config(self):
        return {
            'service_config': {},
            'batch_concurrency': 2
        }
        
    def write_config(self, config):
        pass
        
    def get_preferences(self):
        from superfreetts_addon import config_models
        return config_models.Preferences()
    
    def get_media_folder(self):
        return "/tmp/anki_test/media"
    
    def collection_is_open(self):
        return True


class MockServiceManager:
    """Mock service manager for testing"""
    
    def __init__(self):
        self.services = {}
        self._initialized = False
    
    def ensure_initialized(self):
        self._initialized = True
    
    def get_service(self, service_name):
        return self.services.get(service_name)
    
    def full_voice_list(self):
        return []


@pytest.fixture
def mock_anki_utils():
    """Provide mock Anki utilities"""
    return MockAnkiUtils()


@pytest.fixture
def mock_service_manager():
    """Provide mock service manager"""
    return MockServiceManager()


@pytest.fixture
def mock_config():
    """Provide mock configuration"""
    return {
        'user_uuid': 'test-uuid',
        'batch_configs': [],
        'enabled_services': {},
        'preferences': {
            'batch_concurrency': 2,
            'language': 'en'
        }
    }


@pytest.fixture
def temp_media_folder(tmp_path):
    """Create temporary media folder for tests"""
    media_dir = tmp_path / "media"
    media_dir.mkdir()
    return media_dir


@pytest.fixture
def mock_anki_collection():
    """Mock Anki collection"""
    collection = MagicMock()
    collection.db = MagicMock()
    collection.models = MagicMock()
    collection.decks = MagicMock()
    collection.sched = MagicMock()
    return collection


@pytest.fixture
def mock_logger(monkeypatch):
    """Mock logger to capture log output"""
    logger = MagicMock()
    return logger


# Markers for test organization
def pytest_configure(config):
    """Register custom markers"""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "service: mark test as a service test"
    )
