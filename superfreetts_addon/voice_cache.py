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
from typing import List, Dict, Optional, Any
from pathlib import Path

from . import constants
from . import languages
from . import logging_utils
from . import voice as voice_module

logger = logging_utils.get_child_logger(__name__)

CACHE_FORMAT_VERSION = 2
CACHE_SUFFIX = "_voices.json.gz"
LEGACY_CACHE_GLOB = "*_voices.pkl.gz"


def _serialize_voice(voice: Any) -> Dict[str, Any]:
    """Convert a TtsVoice_v3 into JSON-safe data.

    Voice lists are deliberately stored as plain JSON.  The old implementation
    used pickle, which turns a cache file into arbitrary code execution if it is
    ever tampered with.
    """
    gender = getattr(voice, "gender", None)
    service_fee = getattr(voice, "service_fee", None)
    audio_languages = getattr(voice, "audio_languages", None) or []
    return {
        "name": getattr(voice, "name", ""),
        "voice_key": getattr(voice, "voice_key", ""),
        "options": getattr(voice, "options", {}),
        "service": getattr(voice, "service", ""),
        "gender": getattr(gender, "name", str(gender)),
        "audio_languages": [
            getattr(language, "name", str(language))
            for language in audio_languages
        ],
        "service_fee": getattr(service_fee, "name", str(service_fee)),
    }


def _deserialize_voice(data: Dict[str, Any]):
    audio_languages = []
    for name in data.get("audio_languages", []):
        try:
            audio_languages.append(languages.AudioLanguage[name])
        except KeyError:
            logger.warning(f"Unknown audio language in voice cache: {name}")
    if not audio_languages:
        audio_languages = [languages.AudioLanguage.en_US]

    try:
        gender = constants.Gender[data.get("gender", "Any")]
    except KeyError:
        gender = constants.Gender.Any
    try:
        service_fee = constants.ServiceFee[data.get("service_fee", "free")]
    except KeyError:
        service_fee = constants.ServiceFee.free

    return voice_module.TtsVoice_v3(
        name=data.get("name", ""),
        voice_key=data.get("voice_key", ""),
        options=data.get("options", {}),
        service=data.get("service", ""),
        gender=gender,
        audio_languages=audio_languages,
        service_fee=service_fee,
    )


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
        return self.cache_dir / f"{service_name}{CACHE_SUFFIX}"
    
    def _compute_checksum(self, data: Any) -> str:
        """Compute checksum of data"""
        json_str = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(json_str.encode()).hexdigest()
    
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
        
        # Try disk cache. A fresh process has no in-memory timestamp, so use
        # the file's mtime rather than treating every disk entry as expired.
        disk_path = self.get_disk_path(service_name)
        if disk_path.exists():
            try:
                age = time.time() - disk_path.stat().st_mtime
                if age <= self.ttl_seconds:
                    with gzip.open(disk_path, "rt", encoding="utf-8") as f:
                        payload = json.load(f)
                    if payload.get("version") != CACHE_FORMAT_VERSION:
                        raise ValueError("unsupported voice-cache version")
                    data = [
                        _deserialize_voice(item)
                        for item in payload.get("voices", [])
                    ]
                    self.memory_cache[key] = data
                    self.cache_times[key] = time.time()
                    self.cache_checksums[key] = self._compute_checksum(payload.get("voices", []))
                    logger.debug(f"Voice cache hit (disk): {service_name}")
                    return data
            except Exception as e:
                logger.warning(f"Failed to load disk cache for {service_name}: {e}")
                try:
                    disk_path.unlink()
                except OSError:
                    pass
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
        serialized_voices = [_serialize_voice(item) for item in voices]
        checksum = self._compute_checksum(serialized_voices)
        
        # Skip if data hasn't changed
        if key in self.cache_checksums and self.cache_checksums[key] == checksum:
            logger.debug(f"Voice cache unchanged, skipping: {service_name}")
            return
        
        # Store in memory
        self.memory_cache[key] = voices
        self.cache_times[key] = time.time()
        self.cache_checksums[key] = checksum
        
        # Store on disk (compressed JSON, written atomically)
        disk_path = self.get_disk_path(service_name)
        temp_path = disk_path.with_name(disk_path.name + ".tmp")
        try:
            payload = {
                "version": CACHE_FORMAT_VERSION,
                "saved_at": time.time(),
                "voices": serialized_voices,
            }
            with gzip.open(temp_path, "wt", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False, separators=(",", ":"))
            os.replace(temp_path, disk_path)
            logger.debug(f"Voice cache saved (disk): {service_name}")
        except Exception as e:
            logger.warning(f"Failed to save disk cache for {service_name}: {e}")
            try:
                temp_path.unlink()
            except OSError:
                pass
    
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
            # Purge any legacy pickle cache for this service as well.
            for legacy_file in self.cache_dir.glob(f"{service_name}_voices.pkl.gz"):
                try:
                    legacy_file.unlink()
                except OSError:
                    pass
            logger.info(f"Cache cleared: {service_name}")
        else:
            # Clear all
            self.memory_cache.clear()
            self.cache_times.clear()
            self.cache_checksums.clear()
            
            for cache_file in self.cache_dir.glob(f"*{CACHE_SUFFIX}"):
                cache_file.unlink()
            for legacy_file in self.cache_dir.glob(LEGACY_CACHE_GLOB):
                try:
                    legacy_file.unlink()
                except OSError:
                    pass
            logger.info("All voice caches cleared")
    
    def cleanup_expired(self) -> int:
        """
        Remove all expired cache files.
        
        Returns:
            Number of files removed
        """
        removed = 0
        current_time = time.time()
        
        for cache_file in self.cache_dir.glob(f"*{CACHE_SUFFIX}"):
            try:
                age = current_time - cache_file.stat().st_mtime
                if age > self.ttl_seconds:
                    cache_file.unlink()
                    removed += 1
            except Exception as e:
                logger.warning(f"Failed to cleanup {cache_file}: {e}")

        # Remove old pickle caches produced by versions <= 26.10.1.
        for legacy_file in self.cache_dir.glob(LEGACY_CACHE_GLOB):
            try:
                legacy_file.unlink()
                removed += 1
            except OSError:
                pass
        
        if removed > 0:
            logger.info(f"Removed {removed} expired cache files")
        
        return removed
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_disk_size = sum(
            f.stat().st_size 
            for f in self.cache_dir.glob(f"*{CACHE_SUFFIX}")
        ) / (1024 * 1024)  # Convert to MB
        
        return {
            'memory_entries': len(self.memory_cache),
            'disk_entries': len(list(self.cache_dir.glob(f"*{CACHE_SUFFIX}"))),
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
