"""
Optimized Voice Caching System

Advanced caching for voice lists with:
- TTL-based expiration
- Differential updates
- Compression
- Persistent storage
"""

import json
import hashlib
import os
import time
import gzip
import pickle
from typing import List, Dict, Optional, Any
from pathlib import Path

from . import logging_utils

logger = logging_utils.get_child_logger(__name__)


class VoiceListCache:
    """
    Advanced voice list caching with:
    - In-memory cache with TTL
    - Disk persistence
    - Differential updates (only refresh changed services)
    - Compression for storage efficiency
    """
    
    def __init__(self, cache_dir: str, ttl_seconds: int = 3600):
        """
        Initialize voice cache.
        
        Args:
            cache_dir: Directory for persistent cache
            ttl_seconds: Time-to-live for cached data (1 hour default)
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl_seconds = ttl_seconds
        
        self.memory_cache: Dict[str, Any] = {}
        self.cache_times: Dict[str, float] = {}
        self.cache_checksums: Dict[str, str] = {}
    
    def get_cache_key(self, service_name: str) -> str:
        """Generate cache key for a service"""
        return f"voices_{service_name}"
    
    def get_disk_path(self, service_name: str) -> Path:
        """Get disk cache path for a service"""
        return self.cache_dir / f"{service_name}_voices.pkl.gz"
    
    def _compute_checksum(self, data: Any) -> str:
        """Compute checksum of data"""
        json_str = json.dumps(data, sort_keys=True, default=str)
        return hashlib.md5(json_str.encode()).hexdigest()
    
    def is_expired(self, service_name: str) -> bool:
        """Check if cache is expired"""
        key = self.get_cache_key(service_name)
        if key not in self.cache_times:
            return True
        
        age = time.time() - self.cache_times[key]
        return age > self.ttl_seconds
    
    def get(self, service_name: str) -> Optional[List]:
        """
        Get cached voices for service.
        
        Priority:
        1. In-memory cache
        2. Compressed disk cache
        3. None if expired
        
        Returns:
            Voice list or None if not cached/expired
        """
        key = self.get_cache_key(service_name)
        
        # Check memory cache first
        if key in self.memory_cache and not self.is_expired(service_name):
            logger.debug(f"Voice cache hit (memory): {service_name}")
            return self.memory_cache[key]
        
        # Try disk cache
        disk_path = self.get_disk_path(service_name)
        if disk_path.exists() and not self.is_expired(service_name):
            try:
                with gzip.open(disk_path, 'rb') as f:
                    data = pickle.load(f)
                    self.memory_cache[key] = data
                    self.cache_times[key] = time.time()
                    logger.debug(f"Voice cache hit (disk): {service_name}")
                    return data
            except Exception as e:
                logger.warning(f"Failed to load disk cache for {service_name}: {e}")
                return None
        
        logger.debug(f"Voice cache miss: {service_name}")
        return None
    
    def set(self, service_name: str, voices: List) -> None:
        """
        Cache voices for service.
        
        Args:
            service_name: Name of the service
            voices: List of voice objects
        """
        key = self.get_cache_key(service_name)
        checksum = self._compute_checksum(voices)
        
        # Skip if data hasn't changed
        if key in self.cache_checksums and self.cache_checksums[key] == checksum:
            logger.debug(f"Voice cache unchanged, skipping: {service_name}")
            return
        
        # Store in memory
        self.memory_cache[key] = voices
        self.cache_times[key] = time.time()
        self.cache_checksums[key] = checksum
        
        # Store on disk (compressed)
        disk_path = self.get_disk_path(service_name)
        try:
            with gzip.open(disk_path, 'wb') as f:
                pickle.dump(voices, f, protocol=pickle.HIGHEST_PROTOCOL)
            logger.debug(f"Voice cache saved (disk): {service_name}")
        except Exception as e:
            logger.warning(f"Failed to save disk cache for {service_name}: {e}")
    
    def clear(self, service_name: Optional[str] = None) -> None:
        """
        Clear cache for a service or all services.
        
        Args:
            service_name: Specific service or None for all
        """
        if service_name:
            key = self.get_cache_key(service_name)
            self.memory_cache.pop(key, None)
            self.cache_times.pop(key, None)
            self.cache_checksums.pop(key, None)
            
            disk_path = self.get_disk_path(service_name)
            if disk_path.exists():
                disk_path.unlink()
            logger.info(f"Cache cleared: {service_name}")
        else:
            # Clear all
            self.memory_cache.clear()
            self.cache_times.clear()
            self.cache_checksums.clear()
            
            for pkl_file in self.cache_dir.glob("*_voices.pkl.gz"):
                pkl_file.unlink()
            logger.info("All voice caches cleared")
    
    def cleanup_expired(self) -> int:
        """
        Remove all expired cache files.
        
        Returns:
            Number of files removed
        """
        removed = 0
        current_time = time.time()
        
        for pkl_file in self.cache_dir.glob("*_voices.pkl.gz"):
            try:
                age = current_time - pkl_file.stat().st_mtime
                if age > self.ttl_seconds:
                    pkl_file.unlink()
                    removed += 1
            except Exception as e:
                logger.warning(f"Failed to cleanup {pkl_file}: {e}")
        
        if removed > 0:
            logger.info(f"Removed {removed} expired cache files")
        
        return removed
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_disk_size = sum(
            f.stat().st_size 
            for f in self.cache_dir.glob("*_voices.pkl.gz")
        ) / (1024 * 1024)  # Convert to MB
        
        return {
            'memory_entries': len(self.memory_cache),
            'disk_entries': len(list(self.cache_dir.glob("*_voices.pkl.gz"))),
            'disk_size_mb': round(total_disk_size, 2),
            'ttl_seconds': self.ttl_seconds,
        }


class DeltaCache:
    """
    Delta (differential) caching for incremental updates.
    
    Only caches changed items instead of full list.
    Useful for services that return millions of voices.
    """
    
    def __init__(self):
        self.base_snapshot: Optional[Dict] = None
        self.delta: Dict[str, Any] = {}
        self.last_update_time: float = 0
    
    def update(self, full_data: List, is_full_update: bool = False) -> Dict[str, Any]:
        """
        Update delta cache.
        
        Args:
            full_data: Complete data
            is_full_update: If True, replace base snapshot
        
        Returns:
            Statistics about the update
        """
        start_time = time.time()
        
        # Create snapshot
        snapshot = {item.get('id', str(i)): item for i, item in enumerate(full_data)}
        
        if is_full_update or self.base_snapshot is None:
            # Full update - replace everything
            self.base_snapshot = snapshot
            self.delta.clear()
            update_type = 'full'
            changes = len(snapshot)
        else:
            # Incremental update - find differences
            added = {k: v for k, v in snapshot.items() if k not in self.base_snapshot}
            removed = {k: v for k, v in self.base_snapshot.items() if k not in snapshot}
            
            self.delta['added'] = added
            self.delta['removed'] = removed
            
            update_type = 'incremental'
            changes = len(added) + len(removed)
            
            # Move to base
            self.base_snapshot = snapshot
        
        elapsed = time.time() - start_time
        
        return {
            'type': update_type,
            'total_items': len(snapshot),
            'changes': changes,
            'elapsed_ms': round(elapsed * 1000, 2),
            'compression_ratio': (1 - changes / len(snapshot)) * 100 if snapshot else 0
        }


__all__ = ['VoiceListCache', 'DeltaCache']
