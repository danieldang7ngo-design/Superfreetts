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

class TestSimpleResourceMonitor:
    def test_ram_tracking(self):
        monitor = batch_executor.SimpleResourceMonitor()
        ram = monitor._get_ram_usage()
        assert ram >= 0
        status = monitor.get_status()
        assert "RAM:" in status
        
    def test_gc_heuristic(self):
        monitor = batch_executor.SimpleResourceMonitor()
        # Mock initial RAM to simulate growth
        monitor.initial_ram_mb = 100
        with patch.object(monitor, '_get_ram_usage', return_value=500):
            assert monitor.should_gc(0) is True # 400MB growth
            
        assert monitor.should_gc(100) is True # Every 100 items

class TestCheckpointManager:
    def test_save_load_remove(self):
        with patch('os.makedirs'):
            manager = batch_executor.CheckpointManager(state_dir='/tmp/test_checkpoints')
            batch_name = "test_batch"
            
            # Use mock_open for cleaner file mocking
            from unittest.mock import mock_open
            
            m = mock_open()
            with patch('builtins.open', m):
                manager.save(batch_name, [1, 2], [10, 20], {"1": "error"})
                m.assert_called()
                
            with patch('os.path.exists', return_value=True):
                with patch('builtins.open', mock_open(read_data='{"completed_indices": [1, 2]}')):
                    data = manager.load(batch_name)
                    assert data['completed_indices'] == [1, 2]
            
            with patch('os.path.exists', return_value=True):
                with patch('os.remove') as mock_remove:
                    manager.remove(batch_name)
                    mock_remove.assert_called_once()

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

class TestUnifiedBatchExecutor:
    def test_execute_basic(self):
        executor = batch_executor.UnifiedBatchExecutor(max_workers=1)
        
        # Mock task
        task = {
            'note_id': 123,
            'processed_text': 'hello',
            'batch': MagicMock(),
            'audio_request_context': MagicMock(),
            'chosen_voice': MagicMock()
        }
        
        # We need to mock _execute_single_task to return a result
        # because the base implementation in batch_executor.py returns None
        with patch.object(executor, '_execute_single_task', return_value=(123, 'hello', 'hello', 'f.mp3', '/p/f.mp3', False)):
            on_progress = MagicMock()
            results = executor.execute([task], on_progress=on_progress, enable_checkpoint=False)
            
            assert len(results) == 1
            assert results[0][0] == 123
            on_progress.assert_called_once()
            assert executor.items_processed == 1

class TestBoundedThreadPoolExecutor:
    def test_concurrency_limit(self):
        executor = batch_executor.BoundedThreadPoolExecutor(max_workers=2, max_waiting_tasks=1)
        
        results = []
        def slow_task():
            time.sleep(0.5)
            results.append(True)
            return True
            
        # Submit 2 active + 1 waiting = 3 total
        f1 = executor.submit(slow_task)
        f2 = executor.submit(slow_task)
        f3 = executor.submit(slow_task)
        
        # 4th submission should block (using a timeout for the test)
        start_time = time.time()
        
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
