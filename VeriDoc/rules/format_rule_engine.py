"""
Format Rule Engine for VeriDoc

This module provides format configuration management, inheritance,
validation, and auto-detection capabilities.
"""

import json
import os
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class ValidationStrictness(Enum):
    """Validation strictness levels."""
    RELAXED = "relaxed"
    STANDARD = "standard"
    STRICT = "strict"


@dataclass
class ValidationContext:
    """Context for validation operations."""
    image_path: str
    format_id: str
    strictness: ValidationStrictness = ValidationStrictness.STANDARD
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class FormatMatchResult:
    """Result of format matching operation."""
    matched: bool
    format_id: Optional[str] = None
    confidence: float = 0.0
    matched_criteria: List[str] = None
    validation_errors: List[str] = None
    
    def __post_init__(self):
        if self.matched_criteria is None:
            self.matched_criteria = []
        if self.validation_errors is None:
            self.validation_errors = []


class FormatRule:
    """Represents a format rule configuration."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize format rule from configuration."""
        self.config = config
        self.format_id = config.get('format_id', '')
        self.display_name = config.get('display_name', '')
        self.inherits_from = config.get('inherits_from')
        self.dimensions = config.get('dimensions', {})
        self.face_requirements = config.get('face_requirements', {})
        self.background = config.get('background', {})
        self.quality_thresholds = config.get('quality_thresholds', {})
        self.detection_criteria = config.get('detection_criteria', {})
        self.validation_strictness = ValidationStrictness(
            config.get('validation_strictness', 'standard')
        )
        self.auto_fix_enabled = config.get('auto_fix_enabled', False)
    
    def validate(self, context: ValidationContext) -> List[str]:
        """Validate against this format rule."""
        errors = []
        # Basic validation logic - can be expanded
        if not self.format_id:
            errors.append("Format ID is required")
        return errors


class FormatRuleEngine:
    """Engine for managing and applying format rules."""
    
    def __init__(self, config_dir: Optional[str] = None):
        """Initialize the format rule engine."""
        self.config_dir = Path(config_dir) if config_dir else Path("config/formats")
        self.formats: Dict[str, FormatRule] = {}
        self.load_formats()
    
    def load_formats(self):
        """Load all format configurations from the config directory."""
        if not self.config_dir.exists():
            logger.warning(f"Config directory {self.config_dir} does not exist")
            return
        
        for config_file in self.config_dir.glob("*.json"):
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
                format_rule = FormatRule(config)
                self.formats[format_rule.format_id] = format_rule
                logger.info(f"Loaded format: {format_rule.format_id}")
            except Exception as e:
                logger.error(f"Failed to load format from {config_file}: {e}")
    
    def get_format(self, format_id: str) -> Optional[FormatRule]:
        """Get a format rule by ID."""
        return self.formats.get(format_id)
    
    def list_formats(self) -> List[str]:
        """List all available format IDs."""
        return list(self.formats.keys())
    
    def validate_format(self, format_id: str, context: ValidationContext) -> List[str]:
        """Validate an image against a specific format."""
        format_rule = self.get_format(format_id)
        if not format_rule:
            return [f"Format '{format_id}' not found"]
        
        return format_rule.validate(context)
    
    def auto_detect_format(self, image_path: str) -> FormatMatchResult:
        """Auto-detect the format of an image."""
        # Basic implementation - can be enhanced with actual image analysis
        for format_id, format_rule in self.formats.items():
            # Simple detection based on format criteria
            if self._matches_format_criteria(image_path, format_rule):
                return FormatMatchResult(
                    matched=True,
                    format_id=format_id,
                    confidence=0.8,
                    matched_criteria=["basic_match"]
                )
        
        return FormatMatchResult(matched=False)
    
    def _matches_format_criteria(self, image_path: str, format_rule: FormatRule) -> bool:
        """Check if image matches format criteria."""
        # Basic implementation - always returns True for now
        # This should be enhanced with actual image analysis
        return True
    
    def reload_configuration(self):
        """Reload all format configurations."""
        logger.info("Reloading format configurations...")
        self.formats.clear()
        self.load_formats()
        logger.info(f"Reloaded {len(self.formats)} formats")
