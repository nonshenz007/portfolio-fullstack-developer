"""
Centralized Configuration Management System with Hot-Reload Support

This module implements a thread-safe configuration management system that:
- Loads YAML configuration files from app/config/
- Validates configurations against JSON schemas
- Supports hot-reload using double-read-swap pattern
- Handles SIGHUP signal for configuration reload
- Migrates legacy boolean toggles to realism_profile enum
"""

import os
import signal
import threading
import time
import yaml
import json
import logging
from typing import Dict, Any, Optional, List, Callable
from pathlib import Path
from dataclasses import dataclass
from enum import Enum
import jsonschema
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

logger = logging.getLogger(__name__)


class RealismProfile(Enum):
    """Realism profile enum replacing legacy boolean toggles"""
    BASIC = "basic"
    REALISTIC = "realistic"
    ADVANCED = "advanced"


@dataclass
class ValidationResult:
    """Result of configuration validation"""
    valid: bool
    errors: List[str] = None
    warnings: List[str] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []


class ConfigFileHandler(FileSystemEventHandler):
    """File system event handler for configuration file changes"""
    
    def __init__(self, config_manager: 'ConfigurationManager'):
        self.config_manager = config_manager
        
    def on_modified(self, event):
        if not event.is_directory and event.src_path.endswith('.yaml'):
            config_name = Path(event.src_path).stem
            logger.info(f"Configuration file {config_name} modified, triggering reload")
            self.config_manager.hot_reload_config(config_name)


class ConfigurationManager:
    """
    Thread-safe configuration manager with hot-reload capability
    
    Features:
    - Double-read-swap pattern for zero-downtime reloads
    - JSON Schema validation
    - File system watching for automatic reloads
    - SIGHUP signal handling
    - Migration from boolean toggles to realism_profile enum
    """
    
    def __init__(self, config_dir: str = "app/config"):
        self.config_dir = Path(config_dir)
        self._config_cache: Dict[str, Dict[str, Any]] = {}
        self._config_lock = threading.RLock()
        self._schemas: Dict[str, Dict[str, Any]] = {}
        self._file_watchers: Dict[str, Observer] = {}
        self._reload_callbacks: Dict[str, List[Callable]] = {}
        
        # Ensure config directory exists
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Set up signal handler for SIGHUP
        signal.signal(signal.SIGHUP, self._signal_handler)
        
        # Load schemas
        self._load_schemas()
        
        # Initialize file watchers
        self._setup_file_watchers()
        
        logger.info(f"ConfigurationManager initialized with config_dir: {self.config_dir}")
    
    def _signal_handler(self, signum, frame):
        """Handle SIGHUP signal for configuration reload"""
        logger.info("SIGHUP received, reloading all configurations")
        self.reload_all_configs()
    
    def _load_schemas(self):
        """Load JSON schemas for configuration validation"""
        schema_dir = self.config_dir / "schemas"
        if schema_dir.exists():
            for schema_file in schema_dir.glob("*.json"):
                schema_name = schema_file.stem
                try:
                    with open(schema_file, 'r') as f:
                        self._schemas[schema_name] = json.load(f)
                    logger.info(f"Loaded schema: {schema_name}")
                except Exception as e:
                    logger.error(f"Failed to load schema {schema_name}: {e}")
    
    def _setup_file_watchers(self):
        """Set up file system watchers for automatic reload"""
        if self.config_dir.exists():
            observer = Observer()
            handler = ConfigFileHandler(self)
            observer.schedule(handler, str(self.config_dir), recursive=False)
            observer.start()
            self._file_watchers['main'] = observer
            logger.info("File system watcher set up for configuration directory")
    
    def load_config(self, config_name: str) -> Dict[str, Any]:
        """
        Load configuration with double-read-swap for thread safety
        
        Args:
            config_name: Name of the configuration file (without .yaml extension)
            
        Returns:
            Configuration dictionary
        """
        with self._config_lock:
            # Check cache first
            if config_name in self._config_cache:
                return self._config_cache[config_name].copy()
            
            # Load from file
            config_file = self.config_dir / f"{config_name}.yaml"
            if not config_file.exists():
                logger.warning(f"Configuration file {config_file} not found")
                return {}
            
            try:
                with open(config_file, 'r') as f:
                    config_data = yaml.safe_load(f) or {}
                
                # Validate configuration
                validation_result = self.validate_config(config_data, config_name)
                if not validation_result.valid:
                    logger.error(f"Configuration validation failed for {config_name}: {validation_result.errors}")
                    raise ValueError(f"Invalid configuration: {validation_result.errors}")
                
                # Apply migrations
                config_data = self._apply_migrations(config_data, config_name)
                
                # Cache the configuration
                self._config_cache[config_name] = config_data.copy()
                
                logger.info(f"Loaded configuration: {config_name}")
                return config_data.copy()
                
            except Exception as e:
                logger.error(f"Failed to load configuration {config_name}: {e}")
                raise
    
    def hot_reload_config(self, config_name: str) -> bool:
        """
        Safely reload configuration without disrupting active workers
        
        Args:
            config_name: Name of the configuration to reload
            
        Returns:
            True if reload was successful, False otherwise
        """
        try:
            # Load new configuration
            config_file = self.config_dir / f"{config_name}.yaml"
            if not config_file.exists():
                logger.warning(f"Configuration file {config_file} not found for reload")
                return False
            
            with open(config_file, 'r') as f:
                new_config = yaml.safe_load(f) or {}
            
            # Validate new configuration
            validation_result = self.validate_config(new_config, config_name)
            if not validation_result.valid:
                logger.error(f"Hot reload validation failed for {config_name}: {validation_result.errors}")
                return False
            
            # Apply migrations
            new_config = self._apply_migrations(new_config, config_name)
            
            # Double-read-swap: atomically update cache
            with self._config_lock:
                old_config = self._config_cache.get(config_name, {}).copy()
                self._config_cache[config_name] = new_config.copy()
            
            # Notify callbacks
            self._notify_reload_callbacks(config_name, old_config, new_config)
            
            logger.info(f"Hot reloaded configuration: {config_name}")
            return True
            
        except Exception as e:
            logger.error(f"Hot reload failed for {config_name}: {e}")
            return False
    
    def validate_config(self, config: Dict[str, Any], schema_name: str) -> ValidationResult:
        """
        Validate configuration against JSON schema
        
        Args:
            config: Configuration data to validate
            schema_name: Name of the schema to validate against
            
        Returns:
            ValidationResult with validation status and errors
        """
        result = ValidationResult(valid=True)
        
        # Check for unknown keys if schema exists
        if schema_name in self._schemas:
            schema = self._schemas[schema_name]
            try:
                jsonschema.validate(config, schema)
            except jsonschema.ValidationError as e:
                result.valid = False
                result.errors.append(f"Schema validation error: {e.message}")
            except jsonschema.SchemaError as e:
                result.valid = False
                result.errors.append(f"Schema error: {e.message}")
        else:
            # Basic validation for unknown keys
            self._validate_unknown_keys(config, result)
        
        return result
    
    def _validate_unknown_keys(self, config: Dict[str, Any], result: ValidationResult):
        """Validate for unknown keys when no schema is available"""
        # This is a placeholder - in a real implementation, you'd have
        # a whitelist of known configuration keys
        known_keys = {
            'realism_profile', 'invoice_patterns', 'template_requirements',
            'business_rules', 'tax_tolerances', 'compliance_scoring',
            'risk_levels', 'business_style_expectations'
        }
        
        for key in config.keys():
            if key not in known_keys:
                result.warnings.append(f"Unknown configuration key: {key}")
    
    def get_realism_profile(self, profile_name: str) -> RealismProfile:
        """
        Get realism profile enum from string
        
        Args:
            profile_name: String name of the profile
            
        Returns:
            RealismProfile enum value
        """
        try:
            return RealismProfile(profile_name.lower())
        except ValueError:
            logger.warning(f"Unknown realism profile: {profile_name}, defaulting to REALISTIC")
            return RealismProfile.REALISTIC
    
    def _apply_migrations(self, config: Dict[str, Any], config_name: str) -> Dict[str, Any]:
        """
        Apply configuration migrations (e.g., boolean toggles to realism_profile)
        
        Args:
            config: Configuration data
            config_name: Name of the configuration
            
        Returns:
            Migrated configuration data
        """
        migrated_config = config.copy()
        
        # Migration: Boolean toggles to realism_profile enum
        # Apply to all configs that might have boolean toggles
        migrated_config = self._migrate_boolean_toggles(migrated_config)
        
        return migrated_config
    
    def _migrate_boolean_toggles(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Migrate legacy boolean toggles to realism_profile enum
        
        Args:
            config: Configuration with potential boolean toggles
            
        Returns:
            Configuration with realism_profile enum
        """
        migrated = config.copy()
        
        # Check for legacy boolean toggles and convert to realism_profile
        legacy_toggles = {
            'enable_advanced_features': False,
            'use_realistic_data': True,
            'enable_basic_mode': False
        }
        
        found_toggles = {}
        for toggle, default in legacy_toggles.items():
            if toggle in migrated:
                found_toggles[toggle] = migrated.pop(toggle)
        
        if found_toggles:
            # Determine realism profile based on boolean toggles
            if found_toggles.get('enable_basic_mode', False):
                profile = RealismProfile.BASIC
            elif found_toggles.get('enable_advanced_features', False):
                profile = RealismProfile.ADVANCED
            else:
                profile = RealismProfile.REALISTIC
            
            migrated['realism_profile'] = profile.value
            logger.info(f"Migrated boolean toggles to realism_profile: {profile.value}")
        
        return migrated
    
    def register_reload_callback(self, config_name: str, callback: Callable):
        """
        Register callback to be called when configuration is reloaded
        
        Args:
            config_name: Name of the configuration to watch
            callback: Function to call on reload (old_config, new_config)
        """
        if config_name not in self._reload_callbacks:
            self._reload_callbacks[config_name] = []
        self._reload_callbacks[config_name].append(callback)
    
    def _notify_reload_callbacks(self, config_name: str, old_config: Dict[str, Any], new_config: Dict[str, Any]):
        """Notify registered callbacks about configuration reload"""
        if config_name in self._reload_callbacks:
            for callback in self._reload_callbacks[config_name]:
                try:
                    callback(old_config, new_config)
                except Exception as e:
                    logger.error(f"Error in reload callback for {config_name}: {e}")
    
    def reload_all_configs(self):
        """Reload all cached configurations"""
        with self._config_lock:
            config_names = list(self._config_cache.keys())
        
        for config_name in config_names:
            self.hot_reload_config(config_name)
    
    def get_config_status(self) -> Dict[str, Any]:
        """Get status information about loaded configurations"""
        with self._config_lock:
            return {
                'loaded_configs': list(self._config_cache.keys()),
                'available_schemas': list(self._schemas.keys()),
                'config_dir': str(self.config_dir),
                'watchers_active': len(self._file_watchers) > 0
            }
    
    def shutdown(self):
        """Shutdown the configuration manager and cleanup resources"""
        # Stop file watchers
        for observer in self._file_watchers.values():
            observer.stop()
            observer.join()
        
        logger.info("ConfigurationManager shutdown complete")


# Global configuration manager instance
_config_manager: Optional[ConfigurationManager] = None


def get_config_manager() -> ConfigurationManager:
    """Get the global configuration manager instance"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigurationManager()
    return _config_manager


def load_config(config_name: str) -> Dict[str, Any]:
    """Convenience function to load configuration"""
    return get_config_manager().load_config(config_name)


def reload_config(config_name: str) -> bool:
    """Convenience function to reload configuration"""
    return get_config_manager().hot_reload_config(config_name)