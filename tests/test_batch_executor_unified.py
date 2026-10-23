import sys
import os
import time
import pytest
import threading
from unittest.mock import MagicMock, patch

# Setup mock environment
import tests.mock_anki as mock_anki
mock_anki.mock_all()

# Add paths
addon_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, addon_dir)
sys.path.insert(0, os.path.join(addon_dir, 'external'))

from superfreetts_addon import batch_executor

class TestUnifiedCache:
    def test_basic_get_set(self):
        cache = batch_executor.UnifiedCache(max_size_mb=1)
        cache.put("key1", "value1", size_bytes=10)
        assert cache.get("key1") == "value1"
        assert cache.get("miss") is None
        
    def test_lru_eviction(self):
        cache = batch_executor.UnifiedCache(max_size_mb=0)
        cache.max_size_bytes = 100
        
        cache.put("k1", "v1" * 20, size_bytes=40)
        cache.put("k2", "v2" * 20, size_bytes=40)
        cache.put("k3", "v3" * 20, size_bytes=40)  # Should evict k1
        
        assert cache.get("k1") is None
        assert cache.get("k2") == "v2" * 20
        assert cache.get("k3") == "v3" * 20

    def test_tuple_value_survives_entry_mode(self):
        cache = batch_executor.UnifiedCache(max_size_mb=0)
        value = ("source", "file.mp3", "/tmp/file.mp3")
        cache.put("key", value)
        assert cache.get("key") == value

    def test_concurrent_get_put_clear(self):
        cache = batch_executor.UnifiedCache(max_size_mb=0)
        cache.max_entries = 200
        errors = []

        def worker(worker_id):
            try:
                for i in range(2000):
                    key = f"{worker_id}-{i % 50}"
                    value = (worker_id, i)
                    cache.put(key, value)
                    result = cache.get(key)
                    if result is not None and not isinstance(result, tuple):
                        errors.append(f"bad value type: {type(result)!r}")
                    if i % 500 == 0:
                        cache.stats()
            except Exception as exc:
                errors.append(repr(exc))

        threads = [threading.Thread(target=worker, args=(i,)) for i in range(8)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        assert errors == []
        assert cache.stats()["entries"] <= 200

class TestBoundedLRUDict:
    def test_evicts_oldest_entry(self):
        cache = batch_executor.BoundedLRUDict(max_entries=2)
        cache["a"] = 1
        cache["b"] = 2
        cache["a"]  # refresh a
        cache["c"] = 3

        assert "a" in cache
        assert "b" not in cache
        assert cache["c"] == 3
        assert len(cache) == 2

    def test_get_and_clear(self):
        cache = batch_executor.BoundedLRUDict(max_entries=2)
        cache["a"] = 1

        assert cache.get("a") == 1
        assert cache.get("missing", "fallback") == "fallback"

        cache.clear()
        assert len(cache) == 0


class TestSimpleResourceMonitor:
    def test_ram_tracking(self):
        monitor = batch_executor.SimpleResourceMonitor()
        ram = monitor._get_ram_usage()
        assert ram >= 0
        status = monitor.get_status()
        assert "RAM:" in status
        
    def test_gc_heuristic(self):
        monitor = batch_executor.SimpleResourceMonitor()
        # Mock the GC baseline to simulate growth
        monitor._last_gc_ram_mb = 100
        with patch.object(monitor, '_get_ram_usage', return_value=500):
            assert monitor.should_gc(0) is True # 400MB growth
            
        assert monitor.should_gc(100) is True # Every 100 items since last GC

    def test_gc_hysteresis_resets_baseline_after_collection(self):
        monitor = batch_executor.SimpleResourceMonitor()
        monitor._last_gc_ram_mb = 100
        monitor._last_gc_items = 0

        with patch.object(monitor, '_get_ram_usage', return_value=500), \
             patch.object(batch_executor.gc, 'collect') as collect:
            monitor.maybe_gc(1)
            assert collect.call_count == 1
            assert monitor._last_gc_ram_mb == 500

            # The old implementation kept comparing against the initial
            # 100MB and collected on every following chunk.  After reset,
            # no growth means no collection.
            monitor.maybe_gc(2)
            assert collect.call_count == 1

    def test_gc_item_interval_is_relative_to_last_collection(self):
        monitor = batch_executor.SimpleResourceMonitor()
        monitor._last_gc_ram_mb = 500
        monitor._last_gc_items = 100

        with patch.object(monitor, '_get_ram_usage', return_value=500), \
             patch.object(batch_executor.gc, 'collect') as collect:
            monitor.maybe_gc(199)
            assert collect.call_count == 0
            monitor.maybe_gc(200)
            assert collect.call_count == 1
            assert monitor._last_gc_items == 200

class TestMultiEngineExecutor:
    def test_executor_selection(self):
        config = {'Piper': 2, 'Kokoro': 1, 'default': 4}
        executor = batch_executor.MultiEngineExecutor(engine_config=config)
        
        # PiperTTS -> Piper
        exec_piper = executor.get_executor('PiperTTS')
        assert exec_piper._max_workers == 2
        
        # MmsTTS -> MMS (should fallback to default 4 since not in config but MMS exists)
        # Wait, the code maps MmsTTS to MMS. Let's check config.
        exec_mms = executor.get_executor('MmsTTS')
        assert exec_mms._max_workers == 4 # fallback to default
        
        # EdgeTTS -> EdgeTTS
        exec_edge = executor.get_executor('EdgeTTS')
        assert exec_edge._max_workers == 4 # fallback to default since not in config
        
    def test_engine_detection(self):
        executor = batch_executor.MultiEngineExecutor()
        
        # Mock task with chosen_voice
        voice = MagicMock()
        voice.voice_id.service = "PiperTTS"
        task = {'chosen_voice': voice}
        
        assert executor.detect_service(task) == "PiperTTS"
        
        # Fallback
        assert executor.detect_service({}) == "default"

    def test_default_local_pools_use_cpu_threads_not_logical_cores(self):
        from superfreetts_addon import system_utils
        with patch.object(system_utils, 'get_cpu_threads', return_value=8), \
             patch.object(system_utils, 'get_max_workers', return_value=32):
            executor = batch_executor.MultiEngineExecutor()
            try:
                assert executor.executors["Piper"]._max_workers == 8
                assert executor.executors["Kokoro"]._max_workers == 8
                assert executor.executors["MMS"]._max_workers == 8
                assert executor.executors["Supertonic"]._max_workers == 8
                assert executor.executors["EdgeTTS"]._max_workers == 3
            finally:
                executor.shutdown(wait=False)

class TestUnifiedBatchExecutor:
    def test_get_executor_fallback_surface(self):
        from types import SimpleNamespace

        executor = batch_executor.UnifiedBatchExecutor(max_workers=1)
        try:
            assert executor.get_executor() is executor.executor
            assert executor.get_executor("PiperTTS") is executor.executor
            voice = SimpleNamespace(
                voice_id=SimpleNamespace(service="PiperTTS"),
            )
            assert executor.detect_service({"chosen_voice": voice}) == "PiperTTS"
            future = executor.get_executor().submit(lambda: 42)
            assert future.result(timeout=2) == 42
        finally:
            executor.shutdown()

class TestBoundedThreadPoolExecutor:
    def test_concurrency_limit(self):
        executor = batch_executor.BoundedThreadPoolExecutor(max_workers=2, max_waiting_tasks=1)
        
        results = []
        def slow_task():
            time.sleep(0.5)
            results.append(True)
            return True
            
        # Submit 2 active + 1 waiting = 3 total
        executor.submit(slow_task)
        executor.submit(slow_task)
        executor.submit(slow_task)
        
        # 4th submission should block (using a timeout for the test)
        time.time()
        
        def attempt_4th():
            executor.submit(slow_task)
            
        t = threading.Thread(target=attempt_4th)
        t.start()
        time.sleep(0.1)
        assert t.is_alive() # Still blocked
        
        time.sleep(1.0) # wait for tasks to complete
        assert not t.is_alive() # Unblocked now
        executor.shutdown()

if __name__ == "__main__":
    pytest.main([__file__])
