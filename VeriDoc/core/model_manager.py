"""
AI Model Management System

Handles downloading, caching, and loading of AI models including YOLOv8 face detection models.
Ensures offline operation by managing local model cache.
"""

import os
import hashlib
import json
import logging
from pathlib import Path
from typing import Dict, Optional, List
from urllib.parse import urlparse
import requests
from tqdm import tqdm

logger = logging.getLogger(__name__)


class ModelManager:
    """Manages AI model downloading, caching, and loading for offline operation."""
    
    def __init__(self, cache_dir: str = "models"):
        """
        Initialize model manager with cache directory.
        
        Args:
            cache_dir: Directory to store cached models
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.models_config_path = self.cache_dir / "models_config.json"
        self.models_config = self._load_models_config()
        
    def _load_models_config(self) -> Dict:
        """Load models configuration from cache or create default."""
        default_config = {
            "models": {
                "yolov8n-face": {
                    "url": "https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n-face.pt",
                    "filename": "yolov8n-face.pt",
                    "sha256": "",
                    "description": "YOLOv8 Nano Face Detection Model",
                    "size_mb": 6.2
                },
                "yolov8s-face": {
                    "url": "https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8s-face.pt", 
                    "filename": "yolov8s-face.pt",
                    "sha256": "",
                    "description": "YOLOv8 Small Face Detection Model",
                    "size_mb": 22.5
                },
                "mediapipe-face-mesh": {
                    "url": "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task",
                    "filename": "face_landmarker.task",
                    "sha256": "",
                    "description": "MediaPipe Face Mesh Model",
                    "size_mb": 2.8
                }
            },
            "last_updated": None,
            "cache_version": "1.0"
        }
        
        if self.models_config_path.exists():
            try:
                with open(self.models_config_path, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                logger.warning("Invalid models config, using defaults")
                
        return default_config
    
    def _save_models_config(self):
        """Save models configuration to cache."""
        with open(self.models_config_path, 'w') as f:
            json.dump(self.models_config, f, indent=2)
    
    def _calculate_file_hash(self, filepath: Path) -> str:
        """Calculate SHA256 hash of a file."""
        sha256_hash = hashlib.sha256()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()
    
    def _download_file(self, url: str, filepath: Path, expected_size: Optional[float] = None) -> bool:
        """
        Download file with progress bar.
        
        Args:
            url: URL to download from
            filepath: Local path to save file
            expected_size: Expected file size in MB for progress tracking
            
        Returns:
            True if download successful, False otherwise
        """
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            if total_size == 0 and expected_size:
                total_size = int(expected_size * 1024 * 1024)
            
            with open(filepath, 'wb') as f:
                with tqdm(
                    desc=f"Downloading {filepath.name}",
                    total=total_size,
                    unit='B',
                    unit_scale=True,
                    unit_divisor=1024,
                ) as pbar:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            pbar.update(len(chunk))
            
            logger.info(f"Successfully downloaded {filepath.name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to download {url}: {e}")
            if filepath.exists():
                filepath.unlink()
            return False
    
    def is_model_cached(self, model_name: str) -> bool:
        """
        Check if model is already cached locally.
        
        Args:
            model_name: Name of the model to check
            
        Returns:
            True if model is cached and valid, False otherwise
        """
        if model_name not in self.models_config["models"]:
            return False
            
        model_info = self.models_config["models"][model_name]
        model_path = self.cache_dir / model_info["filename"]
        
        if not model_path.exists():
            return False
            
        # Verify file integrity if hash is available
        if model_info.get("sha256"):
            file_hash = self._calculate_file_hash(model_path)
            if file_hash != model_info["sha256"]:
                logger.warning(f"Hash mismatch for {model_name}, will re-download")
                return False
                
        return True
    
    def download_model(self, model_name: str, force_download: bool = False) -> bool:
        """
        Download and cache a model.
        
        Args:
            model_name: Name of the model to download
            force_download: Force re-download even if cached
            
        Returns:
            True if model is available (cached or downloaded), False otherwise
        """
        if model_name not in self.models_config["models"]:
            logger.error(f"Unknown model: {model_name}")
            return False
            
        if not force_download and self.is_model_cached(model_name):
            logger.info(f"Model {model_name} already cached")
            return True
            
        model_info = self.models_config["models"][model_name]
        model_path = self.cache_dir / model_info["filename"]
        
        logger.info(f"Downloading {model_name} ({model_info['size_mb']} MB)...")
        
        success = self._download_file(
            model_info["url"], 
            model_path, 
            model_info["size_mb"]
        )
        
        if success and model_info.get("sha256"):
            # Verify downloaded file
            file_hash = self._calculate_file_hash(model_path)
            if file_hash != model_info["sha256"]:
                logger.error(f"Downloaded file hash mismatch for {model_name}")
                model_path.unlink()
                return False
                
        return success
    
    def get_model_path(self, model_name: str) -> Optional[Path]:
        """
        Get local path to cached model.
        
        Args:
            model_name: Name of the model
            
        Returns:
            Path to model file if available, None otherwise
        """
        if not self.is_model_cached(model_name):
            return None
            
        model_info = self.models_config["models"][model_name]
        return self.cache_dir / model_info["filename"]
    
    def download_all_models(self, force_download: bool = False) -> Dict[str, bool]:
        """
        Download all configured models.
        
        Args:
            force_download: Force re-download even if cached
            
        Returns:
            Dictionary mapping model names to download success status
        """
        results = {}
        for model_name in self.models_config["models"]:
            results[model_name] = self.download_model(model_name, force_download)
            
        return results
    
    def list_available_models(self) -> List[str]:
        """Get list of available model names."""
        return list(self.models_config["models"].keys())
    
    def get_model_info(self, model_name: str) -> Optional[Dict]:
        """Get information about a model."""
        return self.models_config["models"].get(model_name)
    
    def cleanup_cache(self, keep_models: Optional[List[str]] = None):
        """
        Clean up model cache, optionally keeping specified models.
        
        Args:
            keep_models: List of model names to keep, None to keep all
        """
        if keep_models is None:
            keep_models = list(self.models_config["models"].keys())
            
        for file_path in self.cache_dir.iterdir():
            if file_path.is_file() and file_path.name != "models_config.json":
                # Check if this file belongs to a model we want to keep
                should_keep = False
                for model_name in keep_models:
                    if model_name in self.models_config["models"]:
                        model_filename = self.models_config["models"][model_name]["filename"]
                        if file_path.name == model_filename:
                            should_keep = True
                            break
                            
                if not should_keep:
                    logger.info(f"Removing cached file: {file_path.name}")
                    file_path.unlink()


def ensure_models_available(required_models: List[str] = None) -> bool:
    """
    Ensure required models are available, downloading if necessary.
    
    Args:
        required_models: List of required model names, defaults to essential models
        
    Returns:
        True if all required models are available, False otherwise
    """
    if required_models is None:
        required_models = ["yolov8n-face", "mediapipe-face-mesh"]
        
    model_manager = ModelManager()
    
    all_available = True
    for model_name in required_models:
        if not model_manager.is_model_cached(model_name):
            logger.info(f"Downloading required model: {model_name}")
            if not model_manager.download_model(model_name):
                logger.error(f"Failed to download required model: {model_name}")
                all_available = False
                
    return all_available


if __name__ == "__main__":
    # Test model manager
    logging.basicConfig(level=logging.INFO)
    
    manager = ModelManager()
    print("Available models:", manager.list_available_models())
    
    # Download essential models
    essential_models = ["yolov8n-face", "mediapipe-face-mesh"]
    results = {}
    for model in essential_models:
        results[model] = manager.download_model(model)
        
    print("Download results:", results)