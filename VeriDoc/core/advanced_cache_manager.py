"""
Advanced caching system for AI models and processing results.
Provides intelligent caching with memory management and persistence.
"""

import os
import pickle
import hashlib
import time
import threading
from typing import Any, Dict, Optional, Tuple, List
from dataclasses import dataclass, field
from pathlib import Path
import json
import numpy as np
from PIL import Image
import logging

import logging

logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """Cache entry with metadata."""
    key: str
    data: Any
    timestamp: float
    access_count: int = 0
    last_accessed: float = field(default_factory=time.time)
    size_bytes: int = 0
    ttl_seconds: Optional[float] = None
    
    def is_expired(self) -> bool:
        """Check if cache entry is expired."""
        if self.ttl_seconds is None:
            return False
        return time.time() - self.timestamp > self.ttl_seconds
    
    def touch(self):
        """Update access information."""
        self.access_count += 1
        self.last_accessed = time.time()


class LRUCache:
    """Least Recently Used cache implementation."""
    
    def __init__(self, max_size: int = 100, max_memory_mb: int = 512):
        self.max_size = max_size
        self.max_memory_bytes = max_memory_mb * 1024 * 1024
        self.cache: Dict[str, CacheEntry] = {}
        self.access_order: List[str] = []
        self._lock = threading.RLock()
        
    def get(self, key: str) -> Optional[Any]:
        """Get item from cache."""
        with self._lock:
            if key not in self.cache:
                return None
            
            entry = self.cache[key]
            
            # Check expiration
            if entry.is_expired():
                self._remove_entry(key)
                return None
            
            # Update access info
            entry.touch()
            
            # Move to end of access order
            if key in self.access_order:
                self.access_order.remove(key)
            self.access_order.append(key)
            
            return entry.data
    
    def put(self, key: str, data: Any, ttl_seconds: Optional[float] = None):
        """Put item in cache."""
        with self._lock:
            # Calculate size
            size_bytes = self._calculate_size(data)
            
            # Remove existing entry if present
            if key in self.cache:
                self._remove_entry(key)
            
            # Create new entry
            entry = CacheEntry(
                key=key,
                data=data,
                timestamp=time.time(),
                size_bytes=size_bytes,
                ttl_seconds=ttl_seconds
            )
            
            # Ensure we have space
            self._ensure_space(size_bytes)
            
            # Add to cache
            self.cache[key] = entry
            self.access_order.append(key)
            
            logger.debug(f"Cached item {key} ({size_bytes} bytes)")
    
    def remove(self, key: str) -> bool:
        """Remove item from cache."""
        with self._lock:
            if key in self.cache:
                self._remove_entry(key)
                return True
            return False
    
    def clear(self):
        """Clear all cache entries."""
        with self._lock:
            self.cache.clear()
            self.access_order.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self._lock:
            total_size = sum(entry.size_bytes for entry in self.cache.values())
            return {
                'entries': len(self.cache),
                'max_entries': self.max_size,
                'total_size_mb': total_size / 1024 / 1024,
                'max_size_mb': self.max_memory_bytes / 1024 / 1024,
                'utilization_percent': (total_size / self.max_memory_bytes) * 100 if self.max_memory_bytes > 0 else 0
            }
    
    def _remove_entry(self, key: str):
        """Remove entry from cache."""
        if key in self.cache:
            del self.cache[key]
        if key in self.access_order:
            self.access_order.remove(key)
    
    def _ensure_space(self, required_bytes: int):
        """Ensure enough space for new entry."""
        # Remove expired entries first
        self._cleanup_expired()
        
        # Calculate current size
        current_size = sum(entry.size_bytes for entry in self.cache.values())
        
        # Remove LRU entries if needed
        while (len(self.cache) >= self.max_size or 
               current_size + required_bytes > self.max_memory_bytes) and self.access_order:
            
            lru_key = self.access_order[0]
            lru_entry = self.cache.get(lru_key)
            if lru_entry:
                current_size -= lru_entry.size_bytes
            self._remove_entry(lru_key)
    
    def _cleanup_expired(self):
        """Remove expired entries."""
        expired_keys = [key for key, entry in self.cache.items() if entry.is_expired()]
        for key in expired_keys:
            self._remove_entry(key)
    
    def _calculate_size(self, data: Any) -> int:
        """Calculate approximate size of data."""
        try:
            if isinstance(data, np.ndarray):
                return data.nbytes
            elif isinstance(data, (str, bytes)):
                return len(data)
            elif isinstance(data, dict):
                return len(str(data))  # Rough estimate
            else:
                return len(pickle.dumps(data))
        except:
            return 1024  # Default 1KB estimate


class PersistentCache:
    """Persistent cache that survives application restarts."""
    
    def __init__(self, cache_dir: str = "temp/cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.index_file = self.cache_dir / "cache_index.json"
        self.index = self._load_index()
        self._lock = threading.RLock()
        
    def get(self, key: str) -> Optional[Any]:
        """Get item from persistent cache."""
        with self._lock:
            if key not in self.index:
                return None
            
            entry_info = self.index[key]
            
            # Check expiration
            if entry_info.get('ttl_seconds') and time.time() - entry_info['timestamp'] > entry_info['ttl_seconds']:
                self.remove(key)
                return None
            
            # Load data
            try:
                cache_file = self.cache_dir / f"{key}.cache"
                if cache_file.exists():
                    with open(cache_file, 'rb') as f:
                        data = pickle.load(f)
                    
                    # Update access info
                    entry_info['access_count'] = entry_info.get('access_count', 0) + 1
                    entry_info['last_accessed'] = time.time()
                    self._save_index()
                    
                    return data
                else:
                    # File missing, remove from index
                    self.remove(key)
                    return None
                    
            except Exception as e:
                logger.error(f"Failed to load cached data for {key}: {e}")
                self.remove(key)
                return None
    
    def put(self, key: str, data: Any, ttl_seconds: Optional[float] = None):
        """Put item in persistent cache."""
        with self._lock:
            try:
                # Save data to file
                cache_file = self.cache_dir / f"{key}.cache"
                with open(cache_file, 'wb') as f:
                    pickle.dump(data, f)
                
                # Update index
                self.index[key] = {
                    'timestamp': time.time(),
                    'ttl_seconds': ttl_seconds,
                    'access_count': 0,
                    'last_accessed': time.time(),
                    'file_size': cache_file.stat().st_size
                }
                
                self._save_index()
                logger.debug(f"Persistently cached item {key}")
                
            except Exception as e:
                logger.error(f"Failed to cache data for {key}: {e}")
    
    def remove(self, key: str) -> bool:
        """Remove item from persistent cache."""
        with self._lock:
            if key not in self.index:
                return False
            
            try:
                # Remove file
                cache_file = self.cache_dir / f"{key}.cache"
                if cache_file.exists():
                    cache_file.unlink()
                
                # Remove from index
                del self.index[key]
                self._save_index()
                
                return True
                
            except Exception as e:
                logger.error(f"Failed to remove cached data for {key}: {e}")
                return False
    
    def clear(self):
        """Clear all cached data."""
        with self._lock:
            try:
                # Remove all cache files
                for cache_file in self.cache_dir.glob("*.cache"):
                    cache_file.unlink()
                
                # Clear index
                self.index.clear()
                self._save_index()
                
            except Exception as e:
                logger.error(f"Failed to clear cache: {e}")
    
    def cleanup_expired(self):
        """Remove expired cache entries."""
        with self._lock:
            current_time = time.time()
            expired_keys = []
            
            for key, entry_info in self.index.items():
                if entry_info.get('ttl_seconds') and current_time - entry_info['timestamp'] > entry_info['ttl_seconds']:
                    expired_keys.append(key)
            
            for key in expired_keys:
                self.remove(key)
            
            if expired_keys:
                logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self._lock:
            total_size = sum(entry.get('file_size', 0) for entry in self.index.values())
            return {
                'entries': len(self.index),
                'total_size_mb': total_size / 1024 / 1024,
                'cache_directory': str(self.cache_dir)
            }
    
    def _load_index(self) -> Dict[str, Any]:
        """Load cache index from file."""
        try:
            if self.index_file.exists():
                with open(self.index_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load cache index: {e}")
        return {}
    
    def _save_index(self):
        """Save cache index to file."""
        try:
            with open(self.index_file, 'w') as f:
                json.dump(self.index, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save cache index: {e}")


class ModelCache:
    """Specialized cache for AI models."""
    
    def __init__(self, cache_dir: str = "temp/models"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.memory_cache = LRUCache(max_size=5, max_memory_mb=1024)  # Keep 5 models in memory
        self.persistent_cache = PersistentCache(str(self.cache_dir))
        self._lock = threading.RLock()
        
    def get_model(self, model_key: str, loader_func: Optional[callable] = None) -> Optional[Any]:
        """Get model from cache or load if not cached."""
        with self._lock:
            # Try memory cache first
            model = self.memory_cache.get(model_key)
            if model is not None:
                logger.debug(f"Model {model_key} loaded from memory cache")
                return model
            
            # Try persistent cache
            model = self.persistent_cache.get(model_key)
            if model is not None:
                # Put back in memory cache
                self.memory_cache.put(model_key, model)
                logger.debug(f"Model {model_key} loaded from persistent cache")
                return model
            
            # Load model if loader provided
            if loader_func:
                try:
                    logger.info(f"Loading model {model_key}")
                    model = loader_func()
                    
                    # Cache the model
                    self.memory_cache.put(model_key, model)
                    self.persistent_cache.put(model_key, model, ttl_seconds=7*24*3600)  # 7 days TTL
                    
                    logger.info(f"Model {model_key} loaded and cached")
                    return model
                    
                except Exception as e:
                    logger.error(f"Failed to load model {model_key}: {e}")
                    return None
            
            return None
    
    def preload_models(self, model_configs: Dict[str, callable]):
        """Preload multiple models."""
        for model_key, loader_func in model_configs.items():
            if not self.memory_cache.get(model_key):
                self.get_model(model_key, loader_func)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get model cache statistics."""
        memory_stats = self.memory_cache.get_stats()
        persistent_stats = self.persistent_cache.get_stats()
        
        return {
            'memory_cache': memory_stats,
            'persistent_cache': persistent_stats
        }


class ProcessingResultCache:
    """Cache for processing results to avoid recomputation."""
    
    def __init__(self, cache_dir: str = "temp/results"):
        self.cache = PersistentCache(cache_dir)
        self._lock = threading.RLock()
        
    def get_result_key(self, image_path: str, processing_params: Dict[str, Any]) -> str:
        """Generate cache key for processing result."""
        # Include file modification time and processing parameters
        try:
            file_stat = os.stat(image_path)
            key_data = {
                'path': image_path,
                'mtime': file_stat.st_mtime,
                'size': file_stat.st_size,
                'params': processing_params
            }
            key_string = json.dumps(key_data, sort_keys=True)
            return hashlib.md5(key_string.encode()).hexdigest()
        except:
            # Fallback to simple hash
            key_string = f"{image_path}_{hash(str(processing_params))}"
            return hashlib.md5(key_string.encode()).hexdigest()
    
    def get_cached_result(self, image_path: str, processing_params: Dict[str, Any]) -> Optional[Any]:
        """Get cached processing result."""
        with self._lock:
            key = self.get_result_key(image_path, processing_params)
            return self.cache.get(key)
    
    def cache_result(self, image_path: str, processing_params: Dict[str, Any], result: Any, ttl_hours: int = 24):
        """Cache processing result."""
        with self._lock:
            key = self.get_result_key(image_path, processing_params)
            self.cache.put(key, result, ttl_seconds=ttl_hours * 3600)
    
    def invalidate_image_cache(self, image_path: str):
        """Invalidate all cached results for an image."""
        with self._lock:
            # This is a simplified approach - in practice, you might want to track keys by image
            # For now, we'll rely on the file modification time check in get_result_key
            pass
    
    def cleanup_old_results(self):
        """Clean up old cached results."""
        self.cache.cleanup_expired()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get result cache statistics."""
        return self.cache.get_stats()


class AdvancedCacheManager:
    """Main cache manager coordinating all caching systems."""
    
    def __init__(self, base_cache_dir: str = "temp/cache"):
        self.base_cache_dir = Path(base_cache_dir)
        self.base_cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize specialized caches
        self.model_cache = ModelCache(str(self.base_cache_dir / "models"))
        self.result_cache = ProcessingResultCache(str(self.base_cache_dir / "results"))
        self.general_cache = LRUCache(max_size=200, max_memory_mb=256)
        
        # Start cleanup thread
        self._start_cleanup_thread()
    
    def get_model(self, model_key: str, loader_func: Optional[callable] = None) -> Optional[Any]:
        """Get model from cache."""
        return self.model_cache.get_model(model_key, loader_func)
    
    def get_processing_result(self, image_path: str, processing_params: Dict[str, Any]) -> Optional[Any]:
        """Get cached processing result."""
        return self.result_cache.get_cached_result(image_path, processing_params)
    
    def cache_processing_result(self, image_path: str, processing_params: Dict[str, Any], result: Any):
        """Cache processing result."""
        self.result_cache.cache_result(image_path, processing_params, result)
    
    def get_general(self, key: str) -> Optional[Any]:
        """Get item from general cache."""
        return self.general_cache.get(key)
    
    def put_general(self, key: str, data: Any, ttl_seconds: Optional[float] = None):
        """Put item in general cache."""
        self.general_cache.put(key, data, ttl_seconds)
    
    def clear_all_caches(self):
        """Clear all caches."""
        self.model_cache.memory_cache.clear()
        self.model_cache.persistent_cache.clear()
        self.result_cache.cache.clear()
        self.general_cache.clear()
    
    def get_comprehensive_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics."""
        return {
            'model_cache': self.model_cache.get_stats(),
            'result_cache': self.result_cache.get_stats(),
            'general_cache': self.general_cache.get_stats(),
            'base_cache_directory': str(self.base_cache_dir)
        }
    
    def _start_cleanup_thread(self):
        """Start background cleanup thread."""
        def cleanup_worker():
            while True:
                try:
                    time.sleep(3600)  # Run every hour
                    self.result_cache.cleanup_old_results()
                    self.model_cache.persistent_cache.cleanup_expired()
                except Exception as e:
                    logger.error(f"Cache cleanup error: {e}")
        
        cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
        cleanup_thread.start()