"""
Integration tests for batch_executor — focusing on MultiEngineExecutor routing logic,
detect_service(), get_executor(), and singleton lifecycle.

Strategy:
- All helpers are local to avoid polluting the session-level ServiceBase subclass list.
"""

from unittest.mock import MagicMock

from superfreetts_addon.batch_executor import (
    MultiEngineExecutor,
    BoundedThreadPoolExecutor,
    get_multi_engine_executor,
    get_batch_executor,
    reset_multi_engine_executor,
)
from superfreetts_addon import batch_constants
from superfreetts_addon.voice import TtsVoice_v3, TtsVoiceId_v3
from superfreetts_addon import constants
from superfreetts_addon.languages import AudioLanguage


# ─────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────

def _make_voice(service_name: str) -> TtsVoice_v3:
    """Create a minimal TtsVoice_v3 tagged with the given service."""
    TtsVoiceId_v3({"id": "test_voice"}, service_name)
    return TtsVoice_v3(
        name="TestVoice",
        voice_key={"id": "test_voice"},
        options={},
        service=service_name,
        gender=constants.Gender.Male,
        audio_languages=[AudioLanguage.en_US],
        service_fee=constants.ServiceFee.free,
    )


def _make_task(note_id: int, text: str = "hello", service_name: str = "EdgeTTS") -> dict:
    """Build a minimal task dict matching the shape batch_executor expects."""
    voice = _make_voice(service_name)
    return {
        "note_id": note_id,
        "processed_text": text,
        "batch": MagicMock(),
        "audio_request_context": MagicMock(),
        "chosen_voice": voice,
    }


# ─────────────────────────────────────────────────────────────
# detect_service
# ─────────────────────────────────────────────────────────────

class TestDetectService:

    def setup_method(self):
        self.executor = MultiEngineExecutor()

    def teardown_method(self):
        self.executor.shutdown(wait=False)

    def test_detect_service_from_chosen_voice(self):
        """detect_service() reads service name from task['chosen_voice'].voice_id.service."""
        task = _make_task(1, service_name="EdgeTTS")
        assert self.executor.detect_service(task) == "EdgeTTS"

    def test_detect_service_piper(self):
        """detect_service() works for PiperTTS tasks."""
        task = _make_task(1, service_name="PiperTTS")
        assert self.executor.detect_service(task) == "PiperTTS"

    def test_detect_service_no_voice_returns_default(self):
        """detect_service() returns 'default' when chosen_voice is absent and
        there is no batch voice_selection either."""
        # A completely bare task with no voice info at all
        task = {
            "note_id": 99,
            "processed_text": "text",
        }
        result = self.executor.detect_service(task)
        assert result == "default"

    def test_detect_service_none_chosen_voice_returns_default(self):
        """detect_service() returns 'default' when chosen_voice is None and no batch key."""
        # Without a 'batch' key, detect_service cannot follow any voice_selection fallback
        task = {
            "note_id": 2,
            "processed_text": "text",
            "chosen_voice": None,
        }
        result = self.executor.detect_service(task)
        assert result == "default"


# ─────────────────────────────────────────────────────────────
# get_executor / normalization
# ─────────────────────────────────────────────────────────────

class TestGetExecutor:

    def setup_method(self):
        self.executor = MultiEngineExecutor(engine_config={
            "EdgeTTS": 2,
            "Piper": 1,
            "Kokoro": 1,
            "default": 1,
        })

    def teardown_method(self):
        self.executor.shutdown(wait=False)

    def test_get_executor_edgetts_uses_edgetts_pool(self):
        """EdgeTTS service maps to the named EdgeTTS executor pool."""
        pool = self.executor.get_executor("EdgeTTS")
        assert pool is self.executor.executors["EdgeTTS"]

    def test_get_executor_piperts_normalizes_to_piper(self):
        """PiperTTS is stripped to 'Piper' when looking up the executor pool."""
        pool = self.executor.get_executor("PiperTTS")
        assert pool is self.executor.executors["Piper"]

    def test_get_executor_kokorotts_normalizes_to_kokoro(self):
        """KokoroTTS is stripped to 'Kokoro' when looking up the executor pool."""
        pool = self.executor.get_executor("KokoroTTS")
        assert pool is self.executor.executors["Kokoro"]

    def test_get_executor_unknown_uses_default(self):
        """Unknown service name falls back to the default executor pool."""
        pool = self.executor.get_executor("SomeUnknownTTS")
        assert pool is self.executor.default_executor


# ─────────────────────────────────────────────────────────────
# MultiEngineExecutor initialisation
# ─────────────────────────────────────────────────────────────

class TestMultiEngineExecutorInit:

    def test_default_config_respects_edgetts_cap(self):
        """Default engine_config uses EDGETTS_MAX_WORKERS for EdgeTTS."""
        executor = MultiEngineExecutor()
        try:
            edgetts_pool = executor.executors.get("EdgeTTS")
            assert edgetts_pool is not None
            assert edgetts_pool._max_workers == batch_constants.EDGETTS_MAX_WORKERS
        finally:
            executor.shutdown(wait=False)

    def test_custom_engine_config_is_applied(self):
        """Custom engine_config overrides default worker counts."""
        executor = MultiEngineExecutor(engine_config={"EdgeTTS": 5, "default": 2})
        try:
            assert executor.executors["EdgeTTS"]._max_workers == 5
        finally:
            executor.shutdown(wait=False)

    def test_per_engine_executors_are_bounded_thread_pools(self):
        """Each named executor is a BoundedThreadPoolExecutor instance."""
        executor = MultiEngineExecutor(engine_config={"EdgeTTS": 1, "default": 1})
        try:
            for name, pool in executor.executors.items():
                assert isinstance(pool, BoundedThreadPoolExecutor), \
                    f"Expected BoundedThreadPoolExecutor for {name}, got {type(pool)}"
        finally:
            executor.shutdown(wait=False)


# ─────────────────────────────────────────────────────────────
# Singleton helpers
# ─────────────────────────────────────────────────────────────

class TestMultiEngineExecutorSingleton:

    def setup_method(self):
        reset_multi_engine_executor()

    def teardown_method(self):
        reset_multi_engine_executor()

    def test_get_returns_same_instance(self):
        """get_multi_engine_executor() returns the same object on repeated calls."""
        a = get_multi_engine_executor()
        b = get_multi_engine_executor()
        assert a is b

    def test_reset_clears_singleton(self):
        """reset_multi_engine_executor() causes next get to return a new instance."""
        a = get_multi_engine_executor()
        reset_multi_engine_executor()
        b = get_multi_engine_executor()
        assert a is not b

    def test_custom_config_triggers_new_executor(self):
        """Passing a different engine_config creates a new executor."""
        a = get_multi_engine_executor(engine_config={"EdgeTTS": 1})
        b = get_multi_engine_executor(engine_config={"EdgeTTS": 5})
        assert a is not b

    def test_shutdown_executor_is_recreated(self):
        """A profile close shuts the singleton down; the next call must not
        return the dead executor (Anki reuses add-on modules across profile
        switches)."""
        a = get_multi_engine_executor(engine_config={"EdgeTTS": 1})
        a.shutdown(wait=False)

        b = get_multi_engine_executor(engine_config={"EdgeTTS": 1})

        assert b is not a
        assert b._shutdown is False


class TestUnifiedExecutorSingleton:

    def teardown_method(self):
        import superfreetts_addon.batch_executor as batch_executor_module
        batch_executor_module._executor = None

    def test_shutdown_executor_is_recreated(self):
        a = get_batch_executor()
        a.shutdown(wait=False)

        b = get_batch_executor()

        assert b is not a
        assert b._shutdown is False
