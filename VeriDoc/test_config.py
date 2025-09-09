"""
Unit tests for Veridoc Universal configuration system.
Tests ConfigManager functionality including loading, validation, and error handling.
"""

import unittest
import json
import os
import tempfile
import shutil
from unittest.mock import patch, mock_open
from config.config_manager import ConfigManager, ValidationResult, FormatRule
from config.defaults import get_default_config


class TestConfigManager(unittest.TestCase):
    """Test cases for ConfigManager class"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.test_config_path = os.path.join(self.test_dir, "test_rules.json")
        
        # Valid test configuration
        self.valid_config = {
            "formats": {
                "TEST-FORMAT": {
                    "display_name": "Test Format",
                    "dimensions": {
                        "width": 600,
                        "height": 600,
                        "unit": "pixels"
                    },
                    "face_requirements": {
                        "height_ratio": [0.70, 0.80],
                        "centering_tolerance": 0.05
                    },
                    "background": {
                        "color": "white",
                        "rgb_values": [255, 255, 255],
                        "tolerance": 10
                    },
                    "file_specs": {
                        "format": "JPEG",
                        "max_size_mb": 2,
                        "quality": 90
                    }
                }
            },
            "global_settings": {
                "temp_directory": "temp/saved/",
                "export_directory": "export/",
                "log_file": "logs/test_log.csv"
            }
        }
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.test_dir)
    
    def _write_config_file(self, config_data):
        """Helper to write config data to test file"""
        with open(self.test_config_path, 'w') as f:
            json.dump(config_data, f)
    
    def test_load_valid_configuration(self):
        """Test loading a valid configuration file"""
        self._write_config_file(self.valid_config)
        
        config_manager = ConfigManager(self.test_config_path)
        
        # Verify configuration loaded
        self.assertEqual(len(config_manager.get_available_formats()), 1)
        self.assertIn("TEST-FORMAT", config_manager.get_available_formats())
        
        # Verify format rule parsing
        format_rule = config_manager.get_format_rules("TEST-FORMAT")
        self.assertIsNotNone(format_rule)
        self.assertEqual(format_rule.display_name, "Test Format")
        self.assertEqual(format_rule.dimensions["width"], 600)
    
    def test_load_missing_configuration_file(self):
        """Test behavior when configuration file is missing"""
        non_existent_path = os.path.join(self.test_dir, "missing.json")
        
        config_manager = ConfigManager(non_existent_path)
        
        # Should fall back to defaults
        available_formats = config_manager.get_available_formats()
        self.assertGreater(len(available_formats), 0)
        self.assertIn("ICS-UAE", available_formats)
    
    def test_load_corrupted_configuration_file(self):
        """Test behavior when configuration file is corrupted"""
        with open(self.test_config_path, 'w') as f:
            f.write("{ invalid json content")
        
        config_manager = ConfigManager(self.test_config_path)
        
        # Should fall back to defaults
        available_formats = config_manager.get_available_formats()
        self.assertGreater(len(available_formats), 0)
        self.assertIn("ICS-UAE", available_formats)
    
    def test_validate_valid_configuration(self):
        """Test validation of valid configuration"""
        config_manager = ConfigManager()
        result = config_manager.validate_config(self.valid_config)
        
        self.assertTrue(result.is_valid)
        self.assertEqual(len(result.errors), 0)
    
    def test_validate_missing_formats_section(self):
        """Test validation when formats section is missing"""
        invalid_config = {"global_settings": {}}
        
        config_manager = ConfigManager()
        result = config_manager.validate_config(invalid_config)
        
        self.assertFalse(result.is_valid)
        self.assertIn("Missing 'formats' section", str(result.errors))
    
    def test_validate_missing_format_fields(self):
        """Test validation when format is missing required fields"""
        invalid_config = {
            "formats": {
                "INVALID-FORMAT": {
                    "display_name": "Invalid Format"
                    # Missing required sections
                }
            }
        }
        
        config_manager = ConfigManager()
        result = config_manager.validate_config(invalid_config)
        
        self.assertFalse(result.is_valid)
        self.assertTrue(any("missing required section" in error for error in result.errors))
    
    def test_validate_missing_dimension_fields(self):
        """Test validation when dimensions are incomplete"""
        invalid_config = {
            "formats": {
                "INVALID-FORMAT": {
                    "display_name": "Invalid Format",
                    "dimensions": {
                        "width": 600
                        # Missing height and unit
                    },
                    "face_requirements": {},
                    "background": {"color": "white", "rgb_values": [255, 255, 255]},
                    "file_specs": {}
                }
            }
        }
        
        config_manager = ConfigManager()
        result = config_manager.validate_config(invalid_config)
        
        self.assertFalse(result.is_valid)
        self.assertTrue(any("dimensions missing" in error for error in result.errors))
    
    def test_validate_missing_background_fields(self):
        """Test validation when background fields are missing"""
        invalid_config = {
            "formats": {
                "INVALID-FORMAT": {
                    "display_name": "Invalid Format",
                    "dimensions": {"width": 600, "height": 600, "unit": "pixels"},
                    "face_requirements": {},
                    "background": {
                        "color": "white"
                        # Missing rgb_values
                    },
                    "file_specs": {}
                }
            }
        }
        
        config_manager = ConfigManager()
        result = config_manager.validate_config(invalid_config)
        
        self.assertFalse(result.is_valid)
        self.assertTrue(any("background missing" in error for error in result.errors))
    
    def test_get_format_rules_existing(self):
        """Test getting format rules for existing format"""
        self._write_config_file(self.valid_config)
        config_manager = ConfigManager(self.test_config_path)
        
        format_rule = config_manager.get_format_rules("TEST-FORMAT")
        
        self.assertIsNotNone(format_rule)
        self.assertIsInstance(format_rule, FormatRule)
        self.assertEqual(format_rule.display_name, "Test Format")
    
    def test_get_format_rules_non_existing(self):
        """Test getting format rules for non-existing format"""
        self._write_config_file(self.valid_config)
        config_manager = ConfigManager(self.test_config_path)
        
        format_rule = config_manager.get_format_rules("NON-EXISTENT")
        
        self.assertIsNone(format_rule)
    
    def test_get_available_formats(self):
        """Test getting list of available formats"""
        self._write_config_file(self.valid_config)
        config_manager = ConfigManager(self.test_config_path)
        
        formats = config_manager.get_available_formats()
        
        self.assertIsInstance(formats, list)
        self.assertEqual(len(formats), 1)
        self.assertIn("TEST-FORMAT", formats)
    
    def test_get_global_setting_existing(self):
        """Test getting existing global setting"""
        self._write_config_file(self.valid_config)
        config_manager = ConfigManager(self.test_config_path)
        
        temp_dir = config_manager.get_global_setting("temp_directory")
        
        self.assertEqual(temp_dir, "temp/saved/")
    
    def test_get_global_setting_non_existing_with_default(self):
        """Test getting non-existing global setting with default"""
        self._write_config_file(self.valid_config)
        config_manager = ConfigManager(self.test_config_path)
        
        setting = config_manager.get_global_setting("non_existent", "default_value")
        
        self.assertEqual(setting, "default_value")
    
    def test_get_format_display_names(self):
        """Test getting format display names mapping"""
        self._write_config_file(self.valid_config)
        config_manager = ConfigManager(self.test_config_path)
        
        display_names = config_manager.get_format_display_names()
        
        self.assertIsInstance(display_names, dict)
        self.assertEqual(display_names["TEST-FORMAT"], "Test Format")
    
    def test_reload_configuration(self):
        """Test configuration reloading"""
        # Start with valid config
        self._write_config_file(self.valid_config)
        config_manager = ConfigManager(self.test_config_path)
        
        initial_formats = config_manager.get_available_formats()
        self.assertEqual(len(initial_formats), 1)
        
        # Update config file
        updated_config = self.valid_config.copy()
        updated_config["formats"]["NEW-FORMAT"] = updated_config["formats"]["TEST-FORMAT"].copy()
        updated_config["formats"]["NEW-FORMAT"]["display_name"] = "New Format"
        
        self._write_config_file(updated_config)
        
        # Reload and verify
        success = config_manager.reload_configuration()
        self.assertTrue(success)
        
        updated_formats = config_manager.get_available_formats()
        self.assertEqual(len(updated_formats), 2)
        self.assertIn("NEW-FORMAT", updated_formats)
    
    def test_default_configuration_completeness(self):
        """Test that default configuration contains all required formats"""
        default_config = get_default_config()
        
        # Verify all 5 government formats are present
        expected_formats = ["ICS-UAE", "India-Passport", "US-Visa", "Schengen-Visa", "Canada-PR"]
        formats = default_config.get("formats", {})
        
        for expected_format in expected_formats:
            self.assertIn(expected_format, formats)
            
            # Verify each format has required sections
            format_data = formats[expected_format]
            required_sections = ["display_name", "dimensions", "face_requirements", "background", "file_specs"]
            
            for section in required_sections:
                self.assertIn(section, format_data, f"Format {expected_format} missing {section}")
    
    def test_default_configuration_validation(self):
        """Test that default configuration passes validation"""
        config_manager = ConfigManager()
        default_config = get_default_config()
        
        result = config_manager.validate_config(default_config)
        
        self.assertTrue(result.is_valid, f"Default config validation failed: {result.errors}")
        self.assertEqual(len(result.errors), 0)


class TestValidationResult(unittest.TestCase):
    """Test cases for ValidationResult dataclass"""
    
    def test_validation_result_creation(self):
        """Test ValidationResult creation and attributes"""
        result = ValidationResult(
            is_valid=True,
            errors=["error1", "error2"],
            warnings=["warning1"]
        )
        
        self.assertTrue(result.is_valid)
        self.assertEqual(len(result.errors), 2)
        self.assertEqual(len(result.warnings), 1)
        self.assertIn("error1", result.errors)
        self.assertIn("warning1", result.warnings)


class TestFormatRule(unittest.TestCase):
    """Test cases for FormatRule dataclass"""
    
    def test_format_rule_creation(self):
        """Test FormatRule creation and attributes"""
        rule = FormatRule(
            display_name="Test Format",
            dimensions={"width": 600, "height": 600},
            face_requirements={"height_ratio": [0.7, 0.8]},
            background={"color": "white"},
            file_specs={"format": "JPEG"},
            quality_thresholds={"min_brightness": 50}
        )
        
        self.assertEqual(rule.display_name, "Test Format")
        self.assertEqual(rule.dimensions["width"], 600)
        self.assertEqual(rule.face_requirements["height_ratio"], [0.7, 0.8])
        self.assertEqual(rule.background["color"], "white")
        self.assertEqual(rule.file_specs["format"], "JPEG")
        self.assertEqual(rule.quality_thresholds["min_brightness"], 50)
    
    def test_format_rule_optional_quality_thresholds(self):
        """Test FormatRule with optional quality_thresholds"""
        rule = FormatRule(
            display_name="Test Format",
            dimensions={},
            face_requirements={},
            background={},
            file_specs={}
        )
        
        self.assertIsNone(rule.quality_thresholds)


if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2)