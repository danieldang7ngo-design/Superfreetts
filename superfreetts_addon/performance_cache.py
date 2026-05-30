"""
Performance optimization module with caching and memory management.
Improves batch processing speed through intelligent caching.
"""

import hashlib
import threading
from typing import Dict, Optional, Tuple, Any, List
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class CacheEntry:
    """Represents a cached entry with timestamp"""
    def __init__(self, value: Any, ttl_seconds: int = 3600):
        self.value = value
        self.created_at = datetime.now()
        self.ttl_seconds = ttl_seconds
    
    def is_expired(self) -> bool:
        """Check if cache entry has expired"""
        if self.ttl_seconds <= 0:
            return False
        elapsed = (datetime.now() - self.created_at).total_seconds()
        return elapsed > self.ttl_seconds
    
    def get_value(self) -> Optional[Any]:
        """Get value if not expired, else None"""
        if self.is_expired():
            return None
        return self.value


class VoiceListCache:
    """Cache for voice lists to avoid repeated service calls"""
    def __init__(self, ttl_seconds: int = 3600):
        self._cache: Dict[str, CacheEntry] = {}
        self._lock = threading.Lock()
        self.ttl_seconds = ttl_seconds
        self.hits = 0
        self.misses = 0
    
    def get(self, service_name: str) -> Optional[List]:
        """Get cached voice list for service"""
        with self._lock:
            if service_name in self._cache:
                entry = self._cache[service_name]
                value = entry.get_value()
                if value is not None:
                    self.hits += 1
                    return value
                else:
                    # Expired, remove
                    del self._cache[service_name]
                    self.misses += 1
                    return None
            else:
                self.misses += 1
                return None
    
    def set(self, service_name: str, voices: List) -> None:
        """Cache voice list for service"""
        with self._lock:
            self._cache[service_name] = CacheEntry(voices, self.ttl_seconds)
    
    def clear(self, service_name: Optional[str] = None) -> None:
        """Clear cache for specific service or all"""
        with self._lock:
            if service_name:
                self._cache.pop(service_name, None)
            else:
                self._cache.clear()
    
    def get_stats(self) -> Dict[str, int]:
        """Get cache hit/miss statistics"""
        total = max(self.hits + self.misses, 1)
        hit_rate = (self.hits / total) * 100
        return {
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate_percent': hit_rate
        }


class DedupKeyGenerator:
    """Optimized deduplication key generation"""
    
    @staticmethod
    def create_key(processed_text: str, voice_id: str) -> Tuple[str, str]:
        """
        Create optimized dedup key.
        O(1) operation - just tuple creation, no hashing needed.
        
        Args:
            processed_text: The processed TTS text
            voice_id: The voice identifier
            
        Returns:
            Tuple key for deduplication map
        """
        return (processed_text, voice_id)
    
    @staticmethod
    def create_text_hash(text: str, algorithm: str = 'sha256') -> str:
        """
        Create hash of large text for memory optimization.
        Useful for batch operations with very long strings.
        
        Args:
            text: Text to hash
            algorithm: Hash algorithm (sha256, sha1, md5)
            
        Returns:
            Hex digest of text hash
        """
        if algorithm == 'sha256':
            return hashlib.sha256(text.encode()).hexdigest()
        elif algorithm == 'sha1':
            return hashlib.sha1(text.encode()).hexdigest()
        elif algorithm == 'md5':
            return hashlib.md5(text.encode()).hexdigest()
        else:
            raise ValueError(f"Unknown algorithm: {algorithm}")


class BatchMemoryManager:
    """Manages memory usage for large batch operations"""
    
    def __init__(self, chunk_size: int = 1000):
        """
        Initialize memory manager for batch processing.
        
        Args:
            chunk_size: Process notes in chunks to limit memory usage
        """
        self.chunk_size = chunk_size
        self.total_processed = 0
        self.peak_memory_mb = 0
    
    def get_chunks(self, items: List[Any]) -> List[List[Any]]:
        """
        Split items into chunks for progressive processing.
        
        Useful for 10k+ note batches to avoid memory spikes.
        
        Args:
            items: List to chunk
            
        Returns:
            List of chunks
        """
        chunks = []
        for i in range(0, len(items), self.chunk_size):
            chunks.append(items[i:i + self.chunk_size])
        return chunks
    
    def estimate_memory_usage(self, num_items: int, avg_text_size_bytes: int = 100) -> float:
        """
        Estimate memory usage for batch operation.
        
        Args:
            num_items: Number of items in batch
            avg_text_size_bytes: Average text size per item
            
        Returns:
            Estimated memory usage in MB
        """
        # Rough estimate: text + metadata overhead
        bytes_per_item = avg_text_size_bytes + 200  # 200 bytes for dict overhead
        total_bytes = num_items * bytes_per_item
        return total_bytes / (1024 * 1024)  # Convert to MB


class TTLCache:
    """Generic TTL-based in-memory cache with max size eviction."""

    def __init__(self, max_size: int = 100, ttl_seconds: int = 3600):
        self._cache: Dict[Any, CacheEntry] = {}
        self._lock = threading.Lock()
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds

    def get(self, key: Any) -> Optional[Any]:
        with self._lock:
            entry = self._cache.get(key)
            if entry is None:
                return None
            value = entry.get_value()
            if value is None:
                del self._cache[key]
                return None
            return value

    def set(self, key: Any, value: Any) -> None:
        with self._lock:
            # Evict oldest entry when at capacity
            if len(self._cache) >= self.max_size and key not in self._cache:
                oldest_key = next(iter(self._cache))
                del self._cache[oldest_key]
            self._cache[key] = CacheEntry(value, self.ttl_seconds)

    def clear(self) -> None:
        with self._lock:
            self._cache.clear()


# Global cache instances
_voice_list_cache = VoiceListCache(ttl_seconds=3600)  # 1 hour TTL


def get_voice_list_cache() -> VoiceListCache:
    """Get global voice list cache instance"""
    return _voice_list_cache


def clear_all_caches() -> None:
    """Clear all global caches"""
    _voice_list_cache.clear()
    logger.info("All caches cleared")
