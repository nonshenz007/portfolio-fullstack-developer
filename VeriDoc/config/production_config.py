"""
Production Configuration System for VeriDoc

This module provides a production-ready configuration management system
with centralized settings, validation, and runtime configuration updates.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, field
from enum import Enum
import hashlib
import time

from core.error_handler import get_error_handler, ErrorCategory, ErrorSeverity


class ConfigEnvironment(Enum):
    """Configuration environments."""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


@dataclass
class ProcessingThresholds:
    """Centralized processing thresholds and magic numbers."""

    # Face detection thresholds
    face_confidence_min: float = 0.85
    face_size_ratio_min: float = 0.15
    face_rotation_max_deg: float = 15.0
    eye_distance_min_px: float = 30

    # Image quality thresholds
    brightness_min: int = 55
    brightness_max: int = 190
    sharpness_min: float = 120.0
    blur_variance_max: float = 45.0

    # Background thresholds
    background_uniformity_sigma_max: float = 4.0
    background_tolerance: int = 8

    # Output specifications
    output_width_px: int = 413
    output_height_px: int = 531
    output_dpi: int = 300
    output_jpeg_quality: int = 92
    output_max_kb: int = 200

    # Processing limits
    max_batch_size: int = 100
    processing_timeout_sec: int = 300
    memory_limit_mb: int = 1024

    # Auto-fix settings
    auto_fix_enabled: bool = True
    auto_fix_max_attempts: int = 3
    auto_fix_confidence_threshold: float = 0.8


@dataclass
class SecuritySettings:
    """Security-related configuration."""

    # Encryption settings
    encryption_algorithm: str = "AES-256-GCM"
    key_rotation_days: int = 90
    secure_delete_passes: int = 3

    # Audit settings
    audit_enabled: bool = True
    audit_retention_days: int = 365
    audit_compression: bool = True

    # Access control
    session_timeout_minutes: int = 30
    max_login_attempts: int = 3
    lockout_duration_minutes: int = 15

    # Network security
    allowed_hosts: List[str] = field(default_factory=lambda: ["localhost", "127.0.0.1"])
    ssl_verify: bool = True


@dataclass
class PerformanceSettings:
    """Performance optimization settings."""

    # Threading and concurrency
    max_worker_threads: int = 4
    thread_pool_size: int = 8
    queue_size_limit: int = 1000

    # Caching
    cache_enabled: bool = True
    cache_max_size_mb: int = 512
    cache_ttl_seconds: int = 3600

    # Memory management
    memory_cleanup_interval_sec: int = 60
    garbage_collection_threshold: int = 1000

    # I/O optimization
    batch_write_size: int = 10
    file_buffer_size_kb: int = 64


@dataclass
class LoggingSettings:
    """Logging and monitoring configuration."""

    # Log levels
    console_level: str = "INFO"
    file_level: str = "DEBUG"
    audit_level: str = "INFO"

    # Log files
    max_log_size_mb: int = 10
    log_retention_days: int = 30
    log_rotation_count: int = 5

    # Performance monitoring
    performance_monitoring_enabled: bool = True
    metrics_collection_interval_sec: int = 60
    slow_operation_threshold_sec: float = 5.0


@dataclass
class ProductionConfig:
    """Main production configuration container."""

    # Environment
    environment: ConfigEnvironment = ConfigEnvironment.DEVELOPMENT

    # Core directories
    config_dir: str = "config"
    models_dir: str = "models"
    output_dir: str = "output"
    logs_dir: str = "logs"
    temp_dir: str = "temp"
    cache_dir: str = ".cache"

    # Component settings
    processing: ProcessingThresholds = field(default_factory=ProcessingThresholds)
    security: SecuritySettings = field(default_factory=SecuritySettings)
    performance: PerformanceSettings = field(default_factory=PerformanceSettings)
    logging: LoggingSettings = field(default_factory=LoggingSettings)

    # Feature flags
    features: Dict[str, bool] = field(default_factory=lambda: {
        "ai_face_detection": True,
        "auto_background_fix": True,
        "batch_processing": True,
        "real_time_validation": True,
        "audit_logging": True,
        "performance_monitoring": True,
        "hot_reload": True,
        "advanced_export": True
    })

    # Integration settings
    integrations: Dict[str, Any] = field(default_factory=dict)

    # Metadata
    version: str = "1.0.0"
    config_hash: str = ""
    last_updated: float = field(default_factory=time.time)

    def __post_init__(self):
        """Validate configuration after initialization."""
        self._validate_config()
        self._update_hash()

    def _validate_config(self):
        """Validate configuration values."""
        error_handler = get_error_handler()

        # Validate processing thresholds
        if not 0 < self.processing.face_confidence_min <= 1:
            error_handler.handle_error(
                error_handler.create_error(
                    "Invalid face confidence threshold",
                    ErrorCategory.CONFIGURATION,
                    ErrorSeverity.HIGH,
                    "CONFIG_INVALID_FACE_CONFIDENCE"
                )
            )

        # Validate output specifications
        if self.processing.output_width_px <= 0 or self.processing.output_height_px <= 0:
            error_handler.handle_error(
                error_handler.create_error(
                    "Invalid output dimensions",
                    ErrorCategory.CONFIGURATION,
                    ErrorSeverity.HIGH,
                    "CONFIG_INVALID_OUTPUT_DIMENSIONS"
                )
            )

        # Validate security settings
        if self.security.session_timeout_minutes <= 0:
            error_handler.handle_error(
                error_handler.create_error(
                    "Invalid session timeout",
                    ErrorCategory.CONFIGURATION,
                    ErrorSeverity.MEDIUM,
                    "CONFIG_INVALID_SESSION_TIMEOUT"
                )
            )

    def _update_hash(self):
        """Update configuration hash for change detection."""
        config_str = json.dumps(self.to_dict(), sort_keys=True, default=str)
        self.config_hash = hashlib.md5(config_str.encode()).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "environment": self.environment.value,
            "config_dir": self.config_dir,
            "models_dir": self.models_dir,
            "output_dir": self.output_dir,
            "logs_dir": self.logs_dir,
            "temp_dir": self.temp_dir,
            "cache_dir": self.cache_dir,
            "processing": {
                "face_confidence_min": self.processing.face_confidence_min,
                "face_size_ratio_min": self.processing.face_size_ratio_min,
                "face_rotation_max_deg": self.processing.face_rotation_max_deg,
                "eye_distance_min_px": self.processing.eye_distance_min_px,
                "brightness_min": self.processing.brightness_min,
                "brightness_max": self.processing.brightness_max,
                "sharpness_min": self.processing.sharpness_min,
                "blur_variance_max": self.processing.blur_variance_max,
                "background_uniformity_sigma_max": self.processing.background_uniformity_sigma_max,
                "background_tolerance": self.processing.background_tolerance,
                "output_width_px": self.processing.output_width_px,
                "output_height_px": self.processing.output_height_px,
                "output_dpi": self.processing.output_dpi,
                "output_jpeg_quality": self.processing.output_jpeg_quality,
                "output_max_kb": self.processing.output_max_kb,
                "max_batch_size": self.processing.max_batch_size,
                "processing_timeout_sec": self.processing.processing_timeout_sec,
                "memory_limit_mb": self.processing.memory_limit_mb,
                "auto_fix_enabled": self.processing.auto_fix_enabled,
                "auto_fix_max_attempts": self.processing.auto_fix_max_attempts,
                "auto_fix_confidence_threshold": self.processing.auto_fix_confidence_threshold
            },
            "security": {
                "encryption_algorithm": self.security.encryption_algorithm,
                "key_rotation_days": self.security.key_rotation_days,
                "secure_delete_passes": self.security.secure_delete_passes,
                "audit_enabled": self.security.audit_enabled,
                "audit_retention_days": self.security.audit_retention_days,
                "audit_compression": self.security.audit_compression,
                "session_timeout_minutes": self.security.session_timeout_minutes,
                "max_login_attempts": self.security.max_login_attempts,
                "lockout_duration_minutes": self.security.lockout_duration_minutes,
                "allowed_hosts": self.security.allowed_hosts,
                "ssl_verify": self.security.ssl_verify
            },
            "performance": {
                "max_worker_threads": self.performance.max_worker_threads,
                "thread_pool_size": self.performance.thread_pool_size,
                "queue_size_limit": self.performance.queue_size_limit,
                "cache_enabled": self.performance.cache_enabled,
                "cache_max_size_mb": self.performance.cache_max_size_mb,
                "cache_ttl_seconds": self.performance.cache_ttl_seconds,
                "memory_cleanup_interval_sec": self.performance.memory_cleanup_interval_sec,
                "garbage_collection_threshold": self.performance.garbage_collection_threshold,
                "batch_write_size": self.performance.batch_write_size,
                "file_buffer_size_kb": self.performance.file_buffer_size_kb
            },
            "logging": {
                "console_level": self.logging.console_level,
                "file_level": self.logging.file_level,
                "audit_level": self.logging.audit_level,
                "max_log_size_mb": self.logging.max_log_size_mb,
                "log_retention_days": self.logging.log_retention_days,
                "log_rotation_count": self.logging.log_rotation_count,
                "performance_monitoring_enabled": self.logging.performance_monitoring_enabled,
                "metrics_collection_interval_sec": self.logging.metrics_collection_interval_sec,
                "slow_operation_threshold_sec": self.logging.slow_operation_threshold_sec
            },
            "features": self.features,
            "integrations": self.integrations,
            "version": self.version,
            "config_hash": self.config_hash,
            "last_updated": self.last_updated
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProductionConfig':
        """Create configuration from dictionary."""
        # Handle nested dataclasses
        processing_data = data.get("processing", {})
        security_data = data.get("security", {})
        performance_data = data.get("performance", {})
        logging_data = data.get("logging", {})

        processing = ProcessingThresholds(**processing_data)
        security = SecuritySettings(**security_data)
        performance = PerformanceSettings(**performance_data)
        logging_config = LoggingSettings(**logging_data)

        return cls(
            environment=ConfigEnvironment(data.get("environment", "development")),
            config_dir=data.get("config_dir", "config"),
            models_dir=data.get("models_dir", "models"),
            output_dir=data.get("output_dir", "output"),
            logs_dir=data.get("logs_dir", "logs"),
            temp_dir=data.get("temp_dir", "temp"),
            cache_dir=data.get("cache_dir", ".cache"),
            processing=processing,
            security=security,
            performance=performance,
            logging=logging_config,
            features=data.get("features", {}),
            integrations=data.get("integrations", {}),
            version=data.get("version", "1.0.0")
        )

    def save_to_file(self, file_path: Union[str, Path]) -> bool:
        """Save configuration to JSON file."""
        try:
            file_path = Path(file_path)
            file_path.parent.mkdir(parents=True, exist_ok=True)

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.to_dict(), f, indent=2, default=str)

            return True
        except Exception as e:
            error_handler = get_error_handler()
            error_handler.handle_error(
                error_handler.create_error(
                    f"Failed to save configuration: {e}",
                    ErrorCategory.CONFIGURATION,
                    ErrorSeverity.HIGH,
                    "CONFIG_SAVE_FAILED"
                )
            )
            return False

    @classmethod
    def load_from_file(cls, file_path: Union[str, Path]) -> Optional['ProductionConfig']:
        """Load configuration from JSON file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            return cls.from_dict(data)
        except Exception as e:
            error_handler = get_error_handler()
            error_handler.handle_error(
                error_handler.create_error(
                    f"Failed to load configuration: {e}",
                    ErrorCategory.CONFIGURATION,
                    ErrorSeverity.HIGH,
                    "CONFIG_LOAD_FAILED"
                )
            )
            return None


class ProductionConfigManager:
    """Manager for production configuration with hot-reloading."""

    def __init__(self, config_file: Union[str, Path] = None):
        self.logger = logging.getLogger(__name__)
        self.config_file = Path(config_file or "config/production_config.json")
        self.config: Optional[ProductionConfig] = None
        self.config_watchers: List[callable] = []
        self.last_hash = ""

        # Load initial configuration
        self.load_config()

    def load_config(self) -> bool:
        """Load configuration from file or create default."""
        if self.config_file.exists():
            config = ProductionConfig.load_from_file(self.config_file)
            if config:
                self.config = config
                self.last_hash = config.config_hash
                self.logger.info(f"Loaded configuration from {self.config_file}")
                return True
        else:
            # Create default configuration
            self.config = ProductionConfig()
            self.save_config()
            self.logger.info(f"Created default configuration at {self.config_file}")
            return True

        return False

    def save_config(self) -> bool:
        """Save current configuration to file."""
        if self.config:
            success = self.config.save_to_file(self.config_file)
            if success:
                self.logger.info(f"Saved configuration to {self.config_file}")
            return success
        return False

    def reload_config(self) -> bool:
        """Reload configuration from file if changed."""
        if not self.config_file.exists():
            return False

        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            current_hash = hashlib.md5(json.dumps(data, sort_keys=True, default=str).encode()).hexdigest()

            if current_hash != self.last_hash:
                new_config = ProductionConfig.from_dict(data)
                if new_config:
                    self.config = new_config
                    self.last_hash = current_hash

                    # Notify watchers
                    for watcher in self.config_watchers:
                        try:
                            watcher(self.config)
                        except Exception as e:
                            self.logger.error(f"Config watcher failed: {e}")

                    self.logger.info("Configuration reloaded successfully")
                    return True

        except Exception as e:
            error_handler = get_error_handler()
            error_handler.handle_error(
                error_handler.create_error(
                    f"Failed to reload configuration: {e}",
                    ErrorCategory.CONFIGURATION,
                    ErrorSeverity.MEDIUM,
                    "CONFIG_RELOAD_FAILED"
                )
            )

        return False

    def add_watcher(self, callback: callable):
        """Add a configuration change watcher."""
        self.config_watchers.append(callback)

    def get_config(self) -> ProductionConfig:
        """Get current configuration."""
        return self.config

    def update_config(self, updates: Dict[str, Any]) -> bool:
        """Update configuration with new values."""
        if not self.config:
            return False

        try:
            # Apply updates to config
            for key, value in updates.items():
                if hasattr(self.config, key):
                    setattr(self.config, key, value)
                else:
                    # Handle nested updates
                    if key == "processing" and isinstance(value, dict):
                        for p_key, p_value in value.items():
                            if hasattr(self.config.processing, p_key):
                                setattr(self.config.processing, p_key, p_value)
                    elif key == "security" and isinstance(value, dict):
                        for s_key, s_value in value.items():
                            if hasattr(self.config.security, s_key):
                                setattr(self.config.security, s_key, s_value)
                    elif key == "performance" and isinstance(value, dict):
                        for perf_key, perf_value in value.items():
                            if hasattr(self.config.performance, perf_key):
                                setattr(self.config.performance, perf_key, perf_value)

            # Validate and save
            self.config._validate_config()
            self.config._update_hash()
            return self.save_config()

        except Exception as e:
            error_handler = get_error_handler()
            error_handler.handle_error(
                error_handler.create_error(
                    f"Failed to update configuration: {e}",
                    ErrorCategory.CONFIGURATION,
                    ErrorSeverity.MEDIUM,
                    "CONFIG_UPDATE_FAILED"
                )
            )
            return False


# Global configuration manager instance
_config_manager: Optional[ProductionConfigManager] = None


def get_config_manager() -> ProductionConfigManager:
    """Get the global configuration manager instance."""
    global _config_manager
    if _config_manager is None:
        _config_manager = ProductionConfigManager()
    return _config_manager


def get_config() -> ProductionConfig:
    """Get current production configuration."""
    return get_config_manager().get_config()
