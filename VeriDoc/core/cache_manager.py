"""
Cache Management System

Manages processing cache for improved performance and resource optimization.
"""

import os
import pickle
import hashlib
import logging
from pathlib import Path
from typing import Any, Optional, Dict, List
from dataclasses import dataclass
from datetime import datetime, timedelta
import threading
import json

logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """Represents a cache entry with metadata."""
    key: str
    data: Any
    created_at: datetime
    last_accessed: datetime
    access_count: int
    size_bytes: int
    ttl_seconds: Optional[int] = None
    
    def is_expired(self) -> bool:
        """Check if cache entry has expired."""
        if self.ttl_seconds is None:
            return False
        return datetime.now() - self.created_at > timedelta(seconds=self.ttl_seconds)
    
    def is_stale(self, max_age_seconds: int) -> bool:
        """Check if cache entry is stale."""
        return datetime.now() - self.last_accessed > timedelta(seconds=max_age_seconds)


class CacheManager:
    """
    Manages processing cache with LRU eviction, TTL support, and persistence.
    """
    
    def __init__(self, cache_dir: str = "cache", max_memory_mb: int = 512):
        """
        Initialize cache manager.
        
        Args:
            cache_dir: Directory for persistent cache storage
            max_memory_mb: Maximum memory usage for in-memory cache
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        
        self.max_memory_bytes = max_memory_mb * 1024 * 1024
        self.current_memory_bytes = 0
        
        self._memory_cache: Dict[str, CacheEntry] = {}
        self._lock = threading.RLock()
        
        # Cache statistics
        self.stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'disk_reads': 0,
            'disk_writes': 0
        }
        
        # Load persistent cache index
        self._load_cache_index()
    
    def _generate_cache_key(self, *args, **kwargs) -> str:
        """Generate cache key from arguments."""
        key_data = str(args) + str(sorted(kwargs.items()))
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _get_cache_file_path(self, key: str) -> Path:
        """Get file path for persistent cache entry."""
        return self.cache_dir / f"{key}.cache"
    
    def _get_cache_index_path(self) -> Path:
        """Get path to cache index file."""
        return self.cache_dir / "cache_index.json"
    
    def _load_cache_index(self):
        """Load cache index from disk."""
        index_path = self._get_cache_index_path()
        if index_path.exists():
            try:
                with open(index_path, 'r') as f:
                    index_data = json.load(f)
                    
                # Validate and clean up stale entries
                current_time = datetime.now()
                for key, entry_data in index_data.items():
                    cache_file = self._get_cache_file_path(key)
                    if cache_file.exists():
                        created_at = datetime.fromisoformat(entry_data['created_at'])
                        ttl = entry_data.get('ttl_seconds')
                        
                        # Check if entry is expired
                        if ttl and current_time - created_at > timedelta(seconds=ttl):
                            cache_file.unlink()
                            continue
                            
                logger.info(f"Loaded cache index with {len(index_data)} entries")
            except Exception as e:
                logger.warning(f"Failed to load cache index: {e}")
    
    def _save_cache_index(self):
        """Save cache index to disk."""
        try:
            index_data = {}
            
            # Include memory cache entries
            for key, entry in self._memory_cache.items():
                index_data[key] = {
                    'created_at': entry.created_at.isoformat(),
                    'last_accessed': entry.last_accessed.isoformat(),
                    'access_count': entry.access_count,
                    'size_bytes': entry.size_bytes,
                    'ttl_seconds': entry.ttl_seconds,
                    'in_memory': True
                }
            
            # Include disk cache entries
            for cache_file in self.cache_dir.glob("*.cache"):
                key = cache_file.stem
                if key not in index_data:
                    stat = cache_file.stat()
                    index_data[key] = {
                        'created_at': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                        'last_accessed': datetime.fromtimestamp(stat.st_atime).isoformat(),
                        'access_count': 1,
                        'size_bytes': stat.st_size,
                        'ttl_seconds': None,
                        'in_memory': False
                    }
            
            with open(self._get_cache_index_path(), 'w') as f:
                json.dump(index_data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to save cache index: {e}")
    
    def _evict_lru_entries(self, bytes_needed: int):
        """Evict least recently used entries to free memory."""
        if not self._memory_cache:
            return
            
        # Sort by last accessed time (oldest first)
        sorted_entries = sorted(
            self._memory_cache.items(),
            key=lambda x: x[1].last_accessed
        )
        
        bytes_freed = 0
        for key, entry in sorted_entries:
            if bytes_freed >= bytes_needed:
                break
                
            # Move to disk cache if not already there
            self._save_to_disk(key, entry)
            
            # Remove from memory
            del self._memory_cache[key]
            self.current_memory_bytes -= entry.size_bytes
            bytes_freed += entry.size_bytes
            self.stats['evictions'] += 1
            
        logger.debug(f"Evicted {bytes_freed} bytes from memory cache")
    
    def _save_to_disk(self, key: str, entry: CacheEntry):
        """Save cache entry to disk."""
        try:
            cache_file = self._get_cache_file_path(key)
            with open(cache_file, 'wb') as f:
                pickle.dump(entry.data, f)
            self.stats['disk_writes'] += 1
        except Exception as e:
            logger.error(f"Failed to save cache entry to disk: {e}")
    
    def _load_from_disk(self, key: str) -> Optional[Any]:
        """Load cache entry from disk."""
        try:
            cache_file = self._get_cache_file_path(key)
            if cache_file.exists():
                with open(cache_file, 'rb') as f:
                    data = pickle.load(f)
                self.stats['disk_reads'] += 1
                return data
        except Exception as e:
            logger.error(f"Failed to load cache entry from disk: {e}")
        return None
    
    def _calculate_size(self, data: Any) -> int:
        """Estimate size of data in bytes."""
        try:
            return len(pickle.dumps(data))
        except:
            # Fallback estimation
            return len(str(data).encode('utf-8'))
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get cached data by key.
        
        Args:
            key: Cache key
            
        Returns:
            Cached data or None if not found/expired
        """
        with self._lock:
            # Check memory cache first
            if key in self._memory_cache:
                entry = self._memory_cache[key]
                
                # Check if expired
                if entry.is_expired():
                    del self._memory_cache[key]
                    self.current_memory_bytes -= entry.size_bytes
                    self.stats['misses'] += 1
                    return None
                
                # Update access info
                entry.last_accessed = datetime.now()
                entry.access_count += 1
                self.stats['hits'] += 1
                return entry.data
            
            # Check disk cache
            data = self._load_from_disk(key)
            if data is not None:
                # Load into memory cache
                size_bytes = self._calculate_size(data)
                
                # Ensure we have space
                if self.current_memory_bytes + size_bytes > self.max_memory_bytes:
                    self._evict_lru_entries(size_bytes)
                
                entry = CacheEntry(
                    key=key,
                    data=data,
                    created_at=datetime.now(),
                    last_accessed=datetime.now(),
                    access_count=1,
                    size_bytes=size_bytes
                )
                
                self._memory_cache[key] = entry
                self.current_memory_bytes += size_bytes
                self.stats['hits'] += 1
                return data
            
            self.stats['misses'] += 1
            return None
    
    def put(self, key: str, data: Any, ttl_seconds: Optional[int] = None):
        """
        Store data in cache.
        
        Args:
            key: Cache key
            data: Data to cache
            ttl_seconds: Time to live in seconds (None for no expiration)
        """
        with self._lock:
            size_bytes = self._calculate_size(data)
            
            # Remove existing entry if present
            if key in self._memory_cache:
                old_entry = self._memory_cache[key]
                self.current_memory_bytes -= old_entry.size_bytes
            
            # Ensure we have space
            if self.current_memory_bytes + size_bytes > self.max_memory_bytes:
                self._evict_lru_entries(size_bytes)
            
            # Create new entry
            entry = CacheEntry(
                key=key,
                data=data,
                created_at=datetime.now(),
                last_accessed=datetime.now(),
                access_count=0,
                size_bytes=size_bytes,
                ttl_seconds=ttl_seconds
            )
            
            self._memory_cache[key] = entry
            self.current_memory_bytes += size_bytes
    
    def cache_result(self, func_name: str, ttl_seconds: Optional[int] = None):
        """
        Decorator for caching function results.
        
        Args:
            func_name: Name identifier for the function
            ttl_seconds: Time to live for cached results
        """
        def decorator(func):
            def wrapper(*args, **kwargs):
                # Generate cache key
                cache_key = f"{func_name}_{self._generate_cache_key(*args, **kwargs)}"
                
                # Try to get from cache
                result = self.get(cache_key)
                if result is not None:
                    return result
                
                # Execute function and cache result
                result = func(*args, **kwargs)
                self.put(cache_key, result, ttl_seconds)
                return result
            
            return wrapper
        return decorator
    
    def invalidate(self, key: str):
        """Remove entry from cache."""
        with self._lock:
            # Remove from memory
            if key in self._memory_cache:
                entry = self._memory_cache[key]
                self.current_memory_bytes -= entry.size_bytes
                del self._memory_cache[key]
            
            # Remove from disk
            cache_file = self._get_cache_file_path(key)
            if cache_file.exists():
                cache_file.unlink()
    
    def clear(self):
        """Clear all cache entries."""
        with self._lock:
            self._memory_cache.clear()
            self.current_memory_bytes = 0
            
            # Clear disk cache
            for cache_file in self.cache_dir.glob("*.cache"):
                cache_file.unlink()
            
            # Clear index
            index_path = self._get_cache_index_path()
            if index_path.exists():
                index_path.unlink()
    
    def cleanup_expired(self):
        """Remove expired cache entries."""
        with self._lock:
            expired_keys = []
            
            # Check memory cache
            for key, entry in self._memory_cache.items():
                if entry.is_expired():
                    expired_keys.append(key)
            
            # Remove expired entries
            for key in expired_keys:
                entry = self._memory_cache[key]
                self.current_memory_bytes -= entry.size_bytes
                del self._memory_cache[key]
            
            # Check disk cache
            for cache_file in self.cache_dir.glob("*.cache"):
                # This would require loading the entry to check expiration
                # For now, we rely on the index cleanup during load
                pass
            
            logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")
    
    def get_stats(self) -> Dict:
        """Get cache statistics."""
        with self._lock:
            hit_rate = 0
            total_requests = self.stats['hits'] + self.stats['misses']
            if total_requests > 0:
                hit_rate = self.stats['hits'] / total_requests
            
            return {
                **self.stats,
                'hit_rate': hit_rate,
                'memory_usage_mb': self.current_memory_bytes / (1024 * 1024),
                'memory_entries': len(self._memory_cache),
                'disk_entries': len(list(self.cache_dir.glob("*.cache")))
            }
    
    def shutdown(self):
        """Shutdown cache manager and save state."""
        with self._lock:
            self._save_cache_index()
            logger.info("Cache manager shutdown complete")


# Global cache manager instance
_cache_manager = None


def get_cache_manager() -> CacheManager:
    """Get global cache manager instance."""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CacheManager()
    return _cache_manager


if __name__ == "__main__":
    # Test cache manager
    logging.basicConfig(level=logging.INFO)
    
    cache = CacheManager()
    
    # Test basic operations
    cache.put("test_key", {"data": "test_value"})
    result = cache.get("test_key")
    print("Cached result:", result)
    
    # Test decorator
    @cache.cache_result("expensive_function", ttl_seconds=60)
    def expensive_function(x, y):
        print(f"Computing {x} + {y}")
        return x + y
    
    print("First call:", expensive_function(1, 2))
    print("Second call:", expensive_function(1, 2))  # Should be cached
    
    print("Cache stats:", cache.get_stats())