import pytest

@pytest.mark.unit
def test_imports(anki_mock):
    """Smoke test to verify all major modules can be imported without error under mock Anki"""
    from superfreetts_addon.services import service_edgetts
    from superfreetts_addon import superfreetts
    from superfreetts_addon import config_models
    from superfreetts_addon import text_utils
    from superfreetts_addon import audio_file_store
    from superfreetts_addon import source_text_resolver
    from superfreetts_addon import servicemanager
    from superfreetts_addon import batch_executor
    from superfreetts_addon import batch_state_manager
    from superfreetts_addon import batch_status
    
    assert service_edgetts is not None
    assert superfreetts is not None
    assert config_models is not None
    assert text_utils is not None
    assert audio_file_store is not None
    assert source_text_resolver is not None
    assert servicemanager is not None
    assert batch_executor is not None
    assert batch_state_manager is not None
    assert batch_status is not None
