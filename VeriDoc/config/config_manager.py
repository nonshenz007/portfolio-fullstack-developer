"""
Enhanced configuration manager for VeriDoc Universal.

Provides both legacy API compatibility and new format rule engine integration:
- ConfigManager.get_available_formats() -> list[str]
- ConfigManager.get_format_rules(format_name) -> FormatRule
- ConfigManager.get_global_setting(key, default=None)
- Integration with Format Rule Engine for advanced capabilities

If external JSON rules are missing, falls back to sane defaults from
config/defaults.py so the app can run out-of-the-box.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional
import json
import logging

from .defaults import get_default_config

# Import format rule engine components if available
try:
    from rules.format_rule_engine import FormatRuleEngine
    from utils.format_detector import FormatDetector
    from config.hot_reload_manager import setup_hot_reload
    FORMAT_ENGINE_AVAILABLE = True
except ImportError:
    FORMAT_ENGINE_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class FormatRule:
    """Dataclass representing a single photo format rule set."""

    display_name: str
    dimensions: Dict[str, Any]
    face_requirements: Dict[str, Any]
    background: Dict[str, Any]
    file_specs: Dict[str, Any]
    quality_thresholds: Optional[Dict[str, Any]] = None


@dataclass
class ValidationResult:
    """Simple configuration validation result used by tests."""
    is_valid: bool
    errors: List[str]
    warnings: List[str]


class ConfigManager:
    """Enhanced configuration manager that supports both legacy and modern format engines.

    Looks for config/rules.json and optionally overlays with
    config/ics_rules.json. Falls back to in-repo defaults if files
    are not present.
    
    If the new Format Rule Engine is available, provides enhanced capabilities
    including inheritance, hot-reload, and auto-detection.
    """

    def __init__(
        self,
        rules_path: Optional[str] = None,
        ics_overlay_path: Optional[str] = None,
        enable_format_engine: bool = True,
        enable_hot_reload: bool = False,
    ) -> None:
        base_dir = Path(__file__).resolve().parent
        project_root = base_dir.parent

        rules_file = Path(rules_path) if rules_path else (project_root / "config" / "rules.json")
        # Allow passing a directory; resolve to rules.json inside it
        try:
            if rules_path and rules_file.is_dir():
                rules_file = rules_file / "rules.json"
        except Exception:
            pass
        ics_file = (
            Path(ics_overlay_path)
            if ics_overlay_path
            else (project_root / "config" / "ics_rules.json")
        )

        # Choose loading strategy
        config: Dict[str, Any]
        if rules_path:
            # When an explicit path is provided, treat it as authoritative
            # and do NOT merge defaults (unit tests expect single-format files)
            try:
                if rules_file.exists():
                    with rules_file.open("r", encoding="utf-8") as f:
                        external = json.load(f)
                    config = external if isinstance(external, dict) else get_default_config()
                else:
                    config = get_default_config()
            except Exception:
                config = get_default_config()
        else:
            # Default behavior for application runtime: start with defaults and
            # overlay repo config/rules.json if present
            config = get_default_config()
            try:
                if rules_file.exists():
                    with rules_file.open("r", encoding="utf-8") as f:
                        external = json.load(f)
                    for k, v in external.items():
                        if isinstance(v, dict) and isinstance(config.get(k), dict):
                            config[k].update(v)
                        else:
                            config[k] = v
            except Exception:
                pass

        # Optionally overlay ICS constraint tweaks if present
        try:
            if ics_file.exists():
                with ics_file.open("r", encoding="utf-8") as f:
                    ics_overlay = json.load(f)
                for section in ("formats", "global_settings"):
                    if section in ics_overlay and isinstance(ics_overlay[section], dict):
                        if section not in config:
                            config[section] = {}
                        for key, val in ics_overlay[section].items():
                            if (
                                isinstance(val, dict)
                                and isinstance(config[section].get(key), dict)
                            ):
                                config[section][key].update(val)
                            else:
                                config[section][key] = val
        except Exception:
            pass

        self._config: Dict[str, Any] = config
        self._rules_file = rules_file
        self._explicit_path = bool(rules_path)
        
        # Initialize format rule engine if available and enabled
        self._format_engine: Optional[FormatRuleEngine] = None
        self._format_detector: Optional[FormatDetector] = None
        self._hot_reload_manager = None
        
        if FORMAT_ENGINE_AVAILABLE and enable_format_engine:
            try:
                # Set up format engine with formats directory
                formats_dir = base_dir / "formats"
                if formats_dir.exists():
                    self._format_engine = FormatRuleEngine(str(formats_dir))
                    self._format_detector = FormatDetector(self._format_engine)
                    
                    if enable_hot_reload:
                        self._hot_reload_manager = setup_hot_reload(
                            self._format_engine, 
                            [str(formats_dir)],
                            auto_start=True
                        )
                        logger.info("Format rule engine with hot-reload enabled")
                    else:
                        logger.info("Format rule engine enabled")
                else:
                    logger.info("Format rule engine available but no formats directory found")
            except Exception as e:
                logger.warning(f"Failed to initialize format rule engine: {e}")
        
        # Build display name maps for round-trip normalization
        self._key_to_display: Dict[str, str] = {}
        self._display_to_key: Dict[str, str] = {}
        try:
            for key, data in self._config.get("formats", {}).items():
                if not isinstance(data, dict):
                    continue
                display = data.get("display_name", key)
                self._key_to_display[key] = display
                self._display_to_key[self._normalize_format_name(display)] = key
                # Common synonyms
                self._display_to_key[self._normalize_format_name(key)] = key
                syns = [
                    display.replace("-", " "),
                    display.replace(" ", "-"),
                    display.replace("Visa", "-Visa"),
                    display.replace("Passport", "-Passport"),
                ]
                for s in syns:
                    self._display_to_key[self._normalize_format_name(s)] = key
        except Exception:
            pass

    # Public API -------------------------------------------------------------
    def get_available_formats(self) -> List[str]:
        formats = self._config.get("formats", {})
        return list(formats.keys())

    def get_format_rules(self, format_name: str) -> Optional[FormatRule]:
        formats = self._config.get("formats", {})
        data = formats.get(format_name)
        if not isinstance(data, dict):
            return None
        return FormatRule(
            display_name=data.get("display_name", format_name),
            dimensions=data.get("dimensions", {}),
            face_requirements=data.get("face_requirements", {}),
            background=data.get("background", {}),
            file_specs=data.get("file_specs", {}),
            quality_thresholds=data.get("quality_thresholds", {}),
        )

    def get_global_setting(self, key: str, default: Any = None) -> Any:
        settings = self._config.get("global_settings", {})
        if key == "global_settings":
            return settings if settings else default
        return settings.get(key, default)

    # Convenience for UI components that want a concrete rules file for a format
    def get_format_file_path(self, format_key: str) -> str:
        """Return a best-effort path to a rules JSON for a given format.

        Falls back to `config/icao_rules.json` when a format-specific JSON is
        not available in the repository.
        """
        from pathlib import Path
        root = Path(__file__).resolve().parents[1]  # project root
        cfg = root / "config"
        # Known mappings
        mapping = {
            "ICS-UAE": cfg / "ics_rules.json",
        }
        path = mapping.get(format_key, cfg / "icao_rules.json")
        return str(path if path.exists() else (cfg / "icao_rules.json"))

    # --- Additional helpers required by unit tests ---
    def validate_config(self, config: Dict[str, Any]) -> ValidationResult:
        """Validate a configuration dictionary for required structure."""
        errors: List[str] = []
        warnings: List[str] = []

        formats = config.get("formats")
        if not isinstance(formats, dict) or not formats:
            errors.append("Missing 'formats' section or it is not a dict")
            return ValidationResult(False, errors, warnings)

        required_format_sections = [
            "display_name",
            "dimensions",
            "face_requirements",
            "background",
            "file_specs",
        ]
        for name, data in formats.items():
            if not isinstance(data, dict):
                errors.append(f"Format {name} is not an object")
                continue
            # required sections
            for section in required_format_sections:
                if section not in data:
                    errors.append(f"Format {name} missing required section: {section}")
            # dimensions minimal fields
            dims = data.get("dimensions", {})
            if not isinstance(dims, dict) or not all(k in dims for k in ("width", "height")):
                errors.append(f"Format {name} dimensions missing width/height")
            # background minimal fields
            bg = data.get("background", {})
            if not isinstance(bg, dict) or "rgb_values" not in bg:
                errors.append(f"Format {name} background missing rgb_values")

        return ValidationResult(len(errors) == 0, errors, warnings)

    def get_format_display_names(self) -> Dict[str, str]:
        """Return mapping of format keys to display names."""
        out: Dict[str, str] = {}
        for key, data in self._config.get("formats", {}).items():
            if isinstance(data, dict):
                out[key] = data.get("display_name", key)
        return out

    # New API for canonical key normalization -------------------------------
    def get_display_name_map(self) -> Dict[str, str]:
        """Return mapping of canonical keys to display names (UI consumption)."""
        # Ensure it's up to date in case of reload
        if not self._key_to_display:
            self._key_to_display = self.get_format_display_names()
        return dict(self._key_to_display)

    def get_canonical_key(self, name_or_key: str) -> str:
        """Resolve any display name or synonym to a canonical format key.

        The resolution is case-insensitive and tolerant to spaces vs hyphens.
        Returns the input string if no mapping is found.
        """
        if not isinstance(name_or_key, str):
            return name_or_key
        # Direct key hit
        if name_or_key in self._config.get("formats", {}):
            return name_or_key
        # Normalize and resolve
        normalized = self._normalize_format_name(name_or_key)
        key = self._display_to_key.get(normalized)
        if key:
            return key
        # Last resort: try matching display names directly
        for k, disp in self._key_to_display.items():
            if self._normalize_format_name(disp) == normalized:
                return k
        return name_or_key

    @staticmethod
    def _normalize_format_name(name: str) -> str:
        try:
            n = name.strip().lower()
            for ch in [" ", "_", "."]:
                n = n.replace(ch, "-")
            while "--" in n:
                n = n.replace("--", "-")
            return n
        except Exception:
            return str(name)

    def reload_configuration(self) -> bool:
        """Reload the base rules.json into the current config in-place.

        Returns True on success, False on failure. Defaults are always kept
        as a base and then overlaid with the reloaded file (same behavior as __init__).
        """
        try:
            if self._explicit_path:
                # Authoritative file mode
                if self._rules_file and self._rules_file.exists():
                    with self._rules_file.open("r", encoding="utf-8") as f:
                        external = json.load(f)
                    self._config = external if isinstance(external, dict) else get_default_config()
                else:
                    self._config = get_default_config()
            else:
                base = get_default_config()
                if self._rules_file and self._rules_file.exists():
                    with self._rules_file.open("r", encoding="utf-8") as f:
                        external = json.load(f)
                    for k, v in external.items():
                        if isinstance(v, dict) and isinstance(base.get(k), dict):
                            base[k].update(v)
                        else:
                            base[k] = v
                self._config = base
            
            # Also reload format engine if available
            if self._format_engine:
                self._format_engine.reload_configuration()
            
            return True
        except Exception:
            return False
    
    # New Format Rule Engine Integration Methods
    
    def has_format_engine(self) -> bool:
        """Check if the format rule engine is available and enabled."""
        return self._format_engine is not None
    
    def get_format_engine(self) -> Optional[FormatRuleEngine]:
        """Get the format rule engine instance."""
        return self._format_engine
    
    def get_format_detector(self) -> Optional[FormatDetector]:
        """Get the format detector instance."""
        return self._format_detector
    
    def auto_detect_format(self, image_path: str, confidence_threshold: float = 0.3) -> List[Dict[str, Any]]:
        """
        Auto-detect the best format for an image using the format engine.
        
        Args:
            image_path: Path to the image file
            confidence_threshold: Minimum confidence for results
            
        Returns:
            List of format match results
        """
        if not self._format_detector:
            return []
        
        try:
            results = self._format_detector.detect_format(image_path, confidence_threshold)
            return [
                {
                    'format_id': r.format_id,
                    'confidence': r.confidence,
                    'match_reasons': r.match_reasons,
                    'dimension_match': r.dimension_match,
                    'aspect_ratio_match': r.aspect_ratio_match,
                    'quality_indicators': r.quality_indicators
                }
                for r in results
            ]
        except Exception as e:
            logger.error(f"Error in auto-detection: {e}")
            return []
    
    def validate_format_compliance(self, format_id: str, validation_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate image data against format-specific rules using the format engine.
        
        Args:
            format_id: Format to validate against
            validation_data: Image analysis data
            
        Returns:
            Validation result with compliance status and details
        """
        if not self._format_engine:
            return {'success': False, 'error': 'Format engine not available'}
        
        try:
            return self._format_engine.validate_format_compliance(format_id, validation_data)
        except Exception as e:
            logger.error(f"Error in format validation: {e}")
            return {'success': False, 'error': str(e)}
    
    def suggest_format_improvements(self, image_path: str, target_format: str) -> Dict[str, Any]:
        """
        Suggest improvements for an image to meet format requirements.
        
        Args:
            image_path: Path to the image file
            target_format: Target format ID
            
        Returns:
            Dictionary with improvement suggestions
        """
        if not self._format_detector:
            return {'error': 'Format detector not available'}
        
        try:
            return self._format_detector.suggest_format_improvements(image_path, target_format)
        except Exception as e:
            logger.error(f"Error suggesting improvements: {e}")
            return {'error': str(e)}
    
    def get_format_compatibility_matrix(self) -> Dict[str, Dict[str, float]]:
        """
        Get compatibility matrix between different formats.
        
        Returns:
            Dictionary mapping format pairs to compatibility scores
        """
        if not self._format_detector:
            return {}
        
        try:
            return self._format_detector.get_format_compatibility_matrix()
        except Exception as e:
            logger.error(f"Error generating compatibility matrix: {e}")
            return {}
    
    def enable_hot_reload(self) -> bool:
        """
        Enable hot-reload functionality for format configurations.
        
        Returns:
            True if hot-reload was enabled successfully
        """
        if not self._format_engine:
            return False
        
        if self._hot_reload_manager:
            return True  # Already enabled
        
        try:
            formats_dir = Path(__file__).resolve().parent / "formats"
            if formats_dir.exists():
                self._hot_reload_manager = setup_hot_reload(
                    self._format_engine,
                    [str(formats_dir)],
                    auto_start=True
                )
                logger.info("Hot-reload enabled for format configurations")
                return True
            else:
                logger.warning("Cannot enable hot-reload: formats directory not found")
                return False
        except Exception as e:
            logger.error(f"Failed to enable hot-reload: {e}")
            return False
    
    def disable_hot_reload(self) -> bool:
        """
        Disable hot-reload functionality.
        
        Returns:
            True if hot-reload was disabled successfully
        """
        if self._hot_reload_manager:
            try:
                self._hot_reload_manager.stop_watching()
                self._hot_reload_manager = None
                logger.info("Hot-reload disabled")
                return True
            except Exception as e:
                logger.error(f"Failed to disable hot-reload: {e}")
                return False
        return True
    
    def get_hot_reload_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about hot-reload operations.
        
        Returns:
            Dictionary with reload statistics
        """
        if self._hot_reload_manager:
            return self._hot_reload_manager.get_reload_statistics()
        return {'error': 'Hot-reload not enabled'}
    
    def __del__(self):
        """Cleanup when ConfigManager is destroyed."""
        if self._hot_reload_manager:
            try:
                self._hot_reload_manager.stop_watching()
            except:
                pass

