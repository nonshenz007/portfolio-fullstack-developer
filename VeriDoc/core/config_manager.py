"""
Configuration Manager for VeriDoc Core

Provides simple, reliable configuration management for format rules and system settings.
"""

import json
import yaml
import os
from typing import Dict, Any, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class ConfigManager:
    """Simple configuration manager for VeriDoc format rules and settings."""
    
    def __init__(self, config_dir: str = "config"):
        """
        Initialize configuration manager.
        
        Args:
            config_dir: Directory containing configuration files
        """
        self.config_dir = Path(config_dir)
        self.formats: Dict[str, Any] = {}
        self.settings: Dict[str, Any] = {}
        self._load_configurations()
    
    def _load_configurations(self):
        """Load all configuration files."""
        try:
            # Load format rules
            formats_file = self.config_dir / "formats.json"
            if formats_file.exists():
                with open(formats_file, 'r') as f:
                    self.formats = json.load(f)
                logger.info(f"Loaded {len(self.formats.get('formats', {}))} format configurations")
            else:
                logger.warning(f"Format configuration file not found: {formats_file}")
                self._create_default_formats()
            
            # Load general settings
            settings_file = self.config_dir / "settings.yaml"
            if settings_file.exists():
                with open(settings_file, 'r') as f:
                    self.settings = yaml.safe_load(f)
                logger.info("Loaded system settings")
            else:
                logger.info("No settings file found, using defaults")
                self._create_default_settings()
                
        except Exception as e:
            logger.error(f"Error loading configurations: {e}")
            self._create_default_configurations()
    
    def _create_default_formats(self):
        """Create default format configurations."""
        self.formats = {
            "formats": {
                "ICS-UAE": {
                    "display_name": "ICS UAE Visa",
                    "dimensions": {
                        "width": 413,
                        "height": 531,
                        "dpi": 300,
                        "tolerance": 0.05
                    },
                    "face_requirements": {
                        "face_height_ratio": [0.70, 0.80],
                        "eye_height_ratio": [0.50, 0.60],
                        "centering_tolerance": 0.05,
                        "max_face_angle": 5.0
                    },
                    "background": {
                        "required_color": [255, 255, 255],
                        "tolerance": 15,
                        "uniformity_threshold": 0.9
                    },
                    "quality": {
                        "min_sharpness": 100,
                        "min_brightness": 80,
                        "max_brightness": 200,
                        "max_noise": 0.1
                    }
                },
                "US-Visa": {
                    "display_name": "US Visa Photo",
                    "dimensions": {
                        "width": 600,
                        "height": 600,
                        "dpi": 300,
                        "tolerance": 0.02
                    },
                    "face_requirements": {
                        "face_height_ratio": [0.69, 0.80],
                        "eye_height_ratio": [0.56, 0.69],
                        "centering_tolerance": 0.03,
                        "max_face_angle": 3.0
                    },
                    "background": {
                        "required_color": [255, 255, 255],
                        "tolerance": 10,
                        "uniformity_threshold": 0.95
                    },
                    "quality": {
                        "min_sharpness": 120,
                        "min_brightness": 100,
                        "max_brightness": 180,
                        "max_noise": 0.08
                    }
                }
            }
        }
        self._save_formats()
    
    def _create_default_settings(self):
        """Create default system settings."""
        self.settings = {
            "processing": {
                "max_image_size": 2000,
                "cache_enabled": True,
                "parallel_processing": False,
                "timeout_seconds": 30
            },
            "logging": {
                "level": "INFO",
                "file_enabled": True,
                "console_enabled": True
            },
            "ui": {
                "theme": "default",
                "show_debug_info": False,
                "auto_save_results": True
            }
        }
        self._save_settings()
    
    def _create_default_configurations(self):
        """Create all default configurations."""
        self._create_default_formats()
        self._create_default_settings()
    
    def _save_formats(self):
        """Save format configurations to file."""
        try:
            os.makedirs(self.config_dir, exist_ok=True)
            formats_file = self.config_dir / "formats.json"
            with open(formats_file, 'w') as f:
                json.dump(self.formats, f, indent=2)
            logger.info(f"Saved format configurations to {formats_file}")
        except Exception as e:
            logger.error(f"Error saving format configurations: {e}")
    
    def _save_settings(self):
        """Save system settings to file."""
        try:
            os.makedirs(self.config_dir, exist_ok=True)
            settings_file = self.config_dir / "settings.yaml"
            with open(settings_file, 'w') as f:
                yaml.dump(self.settings, f, default_flow_style=False)
            logger.info(f"Saved system settings to {settings_file}")
        except Exception as e:
            logger.error(f"Error saving system settings: {e}")
    
    def get_format_config(self, format_name: str) -> Optional[Dict[str, Any]]:
        """
        Get configuration for a specific format.
        
        Args:
            format_name: Name of the format (e.g., 'ICS-UAE', 'US-Visa')
            
        Returns:
            Format configuration dictionary or None if not found
        """
        return self.formats.get("formats", {}).get(format_name)
    
    def get_available_formats(self) -> Dict[str, str]:
        """
        Get list of available formats with display names.
        
        Returns:
            Dictionary mapping format names to display names
        """
        formats = {}
        for name, config in self.formats.get("formats", {}).items():
            formats[name] = config.get("display_name", name)
        return formats
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """
        Get a system setting value.
        
        Args:
            key: Setting key (supports dot notation like 'processing.max_image_size')
            default: Default value if setting not found
            
        Returns:
            Setting value or default
        """
        keys = key.split('.')
        value = self.settings
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def validate_format_config(self, format_name: str) -> bool:
        """
        Validate that a format configuration is complete and valid.
        
        Args:
            format_name: Name of the format to validate
            
        Returns:
            True if configuration is valid, False otherwise
        """
        config = self.get_format_config(format_name)
        if not config:
            return False
        
        required_sections = ['dimensions', 'face_requirements', 'background', 'quality']
        for section in required_sections:
            if section not in config:
                logger.error(f"Format {format_name} missing required section: {section}")
                return False
        
        # Validate dimensions
        dims = config['dimensions']
        required_dim_keys = ['width', 'height', 'dpi']
        for key in required_dim_keys:
            if key not in dims:
                logger.error(f"Format {format_name} dimensions missing: {key}")
                return False
        
        logger.info(f"Format {format_name} configuration is valid")
        return True
    
    def reload_configurations(self):
        """Reload all configuration files from disk."""
        logger.info("Reloading configurations...")
        self._load_configurations()