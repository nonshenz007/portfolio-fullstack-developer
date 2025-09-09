"""
Unit tests for Format Rule Engine

Tests format configuration loading, inheritance, validation,
and auto-detection capabilities.
"""

import json
import os
import tempfile
import shutil
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch, MagicMock

from rules.format_rule_engine import FormatRuleEngine, FormatRule, FormatMatchResult, ValidationContext
from utils.format_detector import FormatDetector


class TestFormatRuleEngine(TestCase):
    """Test cases for FormatRuleEngine."""
    
    def setUp(self):
        """Set up test environment."""
        # Create temporary directory for test configurations
        self.test_config_dir = tempfile.mkdtemp()
        self.engine = FormatRuleEngine(self.test_config_dir)
        
        # Create test format configurations
        self._create_test_configurations()
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_config_dir, ignore_errors=True)
    
    def _create_test_configurations(self):
        """Create test format configuration files."""
        # Base format
        base_config = {
            "format_id": "test_base",
            "display_name": "Test Base Format",
            "dimensions": {
                "width": 600,
                "height": 600,
                "aspect_ratio": 1.0
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
            "quality_thresholds": {
                "min_sharpness": 100,
                "min_brightness": 80
            }
        }
        
        # Child format with inheritance
        child_config = {
            "format_id": "test_child",
            "display_name": "Test Child Format",
            "inherits_from": "test_base",
            "dimensions": {
                "width": 400,
                "height": 500
            },
            "quality_thresholds": {
                "min_sharpness": 120
            }
        }
        
        # Standalone format
        standalone_config = {
            "format_id": "test_standalone",
            "display_name": "Test Standalone Format",
            "dimensions": {
                "width": 800,
                "height": 600,
                "aspect_ratio": 1.333
            },
            "detection_criteria": {
                "min_resolution": 600,
                "target_aspect_ratio": 1.333,
                "aspect_ratio_tolerance": 0.05
            }
        }
        
        # Write configuration files
        with open(Path(self.test_config_dir) / "test_base.json", 'w') as f:
            json.dump(base_config, f, indent=2)
        
        with open(Path(self.test_config_dir) / "test_child.json", 'w') as f:
            json.dump(child_config, f, indent=2)
        
        with open(Path(self.test_config_dir) / "test_standalone.json", 'w') as f:
            json.dump(standalone_config, f, indent=2)
        
        # Reload engine to pick up new configurations
        self.engine._load_all_formats()
    
    def test_format_loading(self):
        """Test basic format loading."""
        formats = self.engine.get_available_formats()
        self.assertIn("test_base", formats)
        self.assertIn("test_child", formats)
        self.assertIn("test_standalone", formats)
        
        # Test format retrieval
        base_rule = self.engine.get_format_rule("test_base")
        self.assertIsNotNone(base_rule)
        self.assertEqual(base_rule.format_id, "test_base")
        self.assertEqual(base_rule.display_name, "Test Base Format")
    
    def test_format_inheritance(self):
        """Test format inheritance and rule merging."""
        child_rule = self.engine.get_format_rule("test_child")
        self.assertIsNotNone(child_rule)
        
        # Check that child inherits from base
        self.assertEqual(child_rule.inherits_from, "test_base")
        
        # Check that child overrides work
        self.assertEqual(child_rule.dimensions["width"], 400)
        self.assertEqual(child_rule.dimensions["height"], 500)
        self.assertEqual(child_rule.quality_thresholds["min_sharpness"], 120)
        
        # Check that child inherits non-overridden values
        self.assertEqual(child_rule.face_requirements["height_ratio"], [0.70, 0.80])
        self.assertEqual(child_rule.background["color"], "white")
        self.assertEqual(child_rule.quality_thresholds["min_brightness"], 80)
    
    def test_format_validation(self):
        """Test format-specific validation."""
        validation_data = {
            "dimensions": {"width": 600, "height": 600},
            "face_analysis": {
                "height_ratio": 0.75,
                "center_offset": 0.03
            },
            "background_analysis": {
                "dominant_color": [250, 250, 250],
                "uniformity": 0.95
            },
            "quality_analysis": {
                "sharpness": 150,
                "brightness": 120
            }
        }
        
        result = self.engine.validate_format_compliance("test_base", validation_data)
        
        self.assertTrue(result["success"])
        self.assertEqual(result["format_id"], "test_base")
        self.assertGreater(result["overall_compliance"], 0.8)
        self.assertIsInstance(result["rule_results"], list)
        self.assertGreater(len(result["rule_results"]), 0)
    
    def test_auto_detection(self):
        """Test automatic format detection."""
        # Create a mock image file
        test_image_path = Path(self.test_config_dir) / "test_image.jpg"
        test_image_path.touch()
        
        try:
            # Test detection with dimensions matching test_base
            results = self.engine.auto_detect_format(
                str(test_image_path),
                (600, 600),
                {"filename": "test_image.jpg"}
            )
            
            self.assertIsInstance(results, list)
            if results:
                self.assertIsInstance(results[0], FormatMatchResult)
                self.assertIn(results[0].format_id, ["test_base", "test_child", "test_standalone"])
        
        finally:
            test_image_path.unlink()
    
    def test_configuration_reload(self):
        """Test configuration hot-reload."""
        # Add a new format configuration
        new_config = {
            "format_id": "test_new",
            "display_name": "Test New Format",
            "dimensions": {"width": 300, "height": 400}
        }
        
        new_config_path = Path(self.test_config_dir) / "test_new.json"
        with open(new_config_path, 'w') as f:
            json.dump(new_config, f, indent=2)
        
        # Reload configuration
        success = self.engine.reload_configuration()
        self.assertTrue(success)
        
        # Check that new format is available
        formats = self.engine.get_available_formats()
        self.assertIn("test_new", formats)
        
        new_rule = self.engine.get_format_rule("test_new")
        self.assertIsNotNone(new_rule)
        self.assertEqual(new_rule.display_name, "Test New Format")
    
    def test_validation_context_creation(self):
        """Test validation context creation."""
        context = self.engine.create_validation_context(
            "test_base",
            image_path="/test/image.jpg",
            image_dimensions=(600, 600),
            processing_options={"quality": "high"}
        )
        
        self.assertIsNotNone(context)
        self.assertIsInstance(context, ValidationContext)
        self.assertEqual(context.format_rule.format_id, "test_base")
        self.assertEqual(context.image_path, "/test/image.jpg")
        self.assertEqual(context.image_dimensions, (600, 600))
        self.assertEqual(context.processing_options["quality"], "high")
    
    def test_invalid_format_handling(self):
        """Test handling of invalid format requests."""
        # Test non-existent format
        rule = self.engine.get_format_rule("non_existent")
        self.assertIsNone(rule)
        
        # Test validation with non-existent format
        result = self.engine.validate_format_compliance("non_existent", {})
        self.assertFalse(result["success"])
        self.assertIn("error", result)
        
        # Test context creation with non-existent format
        context = self.engine.create_validation_context("non_existent")
        self.assertIsNone(context)
    
    def test_format_display_names(self):
        """Test format display name mapping."""
        display_names = self.engine.get_format_display_names()
        
        self.assertIsInstance(display_names, dict)
        self.assertEqual(display_names["test_base"], "Test Base Format")
        self.assertEqual(display_names["test_child"], "Test Child Format")
        self.assertEqual(display_names["test_standalone"], "Test Standalone Format")
    
    def test_inheritance_error_handling(self):
        """Test error handling in inheritance resolution."""
        # Create a format with invalid parent
        invalid_config = {
            "format_id": "test_invalid",
            "display_name": "Test Invalid Format",
            "inherits_from": "non_existent_parent",
            "dimensions": {"width": 100, "height": 100}
        }
        
        invalid_path = Path(self.test_config_dir) / "test_invalid.json"
        with open(invalid_path, 'w') as f:
            json.dump(invalid_config, f, indent=2)
        
        # This should handle the error gracefully
        with self.assertLogs(level='ERROR'):
            self.engine._load_all_formats()
    
    def test_circular_inheritance_detection(self):
        """Test detection of circular inheritance."""
        # Create circular inheritance: A -> B -> A
        config_a = {
            "format_id": "circular_a",
            "inherits_from": "circular_b",
            "dimensions": {"width": 100, "height": 100}
        }
        
        config_b = {
            "format_id": "circular_b",
            "inherits_from": "circular_a",
            "dimensions": {"width": 200, "height": 200}
        }
        
        with open(Path(self.test_config_dir) / "circular_a.json", 'w') as f:
            json.dump(config_a, f, indent=2)
        
        with open(Path(self.test_config_dir) / "circular_b.json", 'w') as f:
            json.dump(config_b, f, indent=2)
        
        # This should handle circular inheritance gracefully
        with self.assertLogs(level='ERROR'):
            self.engine._load_all_formats()


class TestFormatDetector(TestCase):
    """Test cases for FormatDetector."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_config_dir = tempfile.mkdtemp()
        self.engine = FormatRuleEngine(self.test_config_dir)
        self.detector = FormatDetector(self.engine)
        
        # Create test image file
        self.test_image_path = Path(self.test_config_dir) / "test_image.jpg"
        self.test_image_path.touch()
        
        # Create basic format configuration
        self._create_test_format()
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_config_dir, ignore_errors=True)
    
    def _create_test_format(self):
        """Create a test format configuration."""
        config = {
            "format_id": "test_format",
            "display_name": "Test Format",
            "dimensions": {
                "width": 600,
                "height": 600,
                "aspect_ratio": 1.0
            },
            "detection_criteria": {
                "min_resolution": 500,
                "target_aspect_ratio": 1.0,
                "aspect_ratio_tolerance": 0.05
            }
        }
        
        with open(Path(self.test_config_dir) / "test_format.json", 'w') as f:
            json.dump(config, f, indent=2)
        
        self.engine._load_all_formats()
    
    @patch('PIL.Image.open')
    @patch('os.path.getsize')
    def test_format_detection(self, mock_getsize, mock_image_open):
        """Test format detection with mocked image."""
        # Mock image properties
        mock_img = MagicMock()
        mock_img.size = (600, 600)
        mock_img.format = 'JPEG'
        mock_img.mode = 'RGB'
        mock_img._getexif.return_value = None
        mock_image_open.return_value.__enter__.return_value = mock_img
        
        # Mock file size
        mock_getsize.return_value = 1024 * 1024  # 1MB
        
        results = self.detector.detect_format(str(self.test_image_path))
        
        self.assertIsInstance(results, list)
        # Should find at least one match with our test format
        if results:
            self.assertIsInstance(results[0], FormatMatchResult)
    
    @patch('PIL.Image.open')
    @patch('os.path.getsize')
    def test_best_format_match(self, mock_getsize, mock_image_open):
        """Test getting the best format match."""
        # Mock image properties
        mock_img = MagicMock()
        mock_img.size = (600, 600)
        mock_img.format = 'JPEG'
        mock_img.mode = 'RGB'
        mock_img._getexif.return_value = None
        mock_image_open.return_value.__enter__.return_value = mock_img
        
        mock_getsize.return_value = 1024 * 1024
        
        result = self.detector.get_best_format_match(str(self.test_image_path))
        
        # Should return the best match or None
        if result:
            self.assertIsInstance(result, FormatMatchResult)
    
    @patch('PIL.Image.open')
    @patch('os.path.getsize')
    def test_format_improvement_suggestions(self, mock_getsize, mock_image_open):
        """Test format improvement suggestions."""
        # Mock image properties
        mock_img = MagicMock()
        mock_img.size = (400, 300)  # Different from target
        mock_img.format = 'PNG'     # Different from target
        mock_img.mode = 'RGB'
        mock_img._getexif.return_value = None
        mock_image_open.return_value.__enter__.return_value = mock_img
        
        mock_getsize.return_value = 5 * 1024 * 1024  # 5MB
        
        suggestions = self.detector.suggest_format_improvements(
            str(self.test_image_path), 
            "test_format"
        )
        
        self.assertIsInstance(suggestions, dict)
        self.assertEqual(suggestions["format_id"], "test_format")
        self.assertIn("improvements", suggestions)
        self.assertIsInstance(suggestions["improvements"], list)
    
    def test_compatibility_matrix(self):
        """Test format compatibility matrix generation."""
        matrix = self.detector.get_format_compatibility_matrix()
        
        self.assertIsInstance(matrix, dict)
        # Should have at least our test format
        if "test_format" in matrix:
            self.assertIn("test_format", matrix["test_format"])
            self.assertEqual(matrix["test_format"]["test_format"], 1.0)


class TestFormatRuleDataStructures(TestCase):
    """Test cases for format rule data structures."""
    
    def test_format_rule_creation(self):
        """Test FormatRule creation and properties."""
        rule = FormatRule(
            format_id="test",
            display_name="Test Format",
            dimensions={"width": 600, "height": 600},
            face_requirements={"height_ratio": [0.7, 0.8]},
            country="Test Country",
            authority="Test Authority"
        )
        
        self.assertEqual(rule.format_id, "test")
        self.assertEqual(rule.display_name, "Test Format")
        self.assertEqual(rule.dimensions["width"], 600)
        self.assertEqual(rule.face_requirements["height_ratio"], [0.7, 0.8])
        self.assertEqual(rule.country, "Test Country")
        self.assertEqual(rule.authority, "Test Authority")
        self.assertEqual(rule.version, "1.0")  # Default value
        self.assertTrue(rule.auto_fix_enabled)  # Default value
    
    def test_format_match_result_creation(self):
        """Test FormatMatchResult creation and properties."""
        result = FormatMatchResult(
            format_id="test",
            confidence=0.85,
            match_reasons=["dimension match", "aspect ratio match"],
            dimension_match=True,
            aspect_ratio_match=True,
            quality_indicators={"sharpness": 0.9}
        )
        
        self.assertEqual(result.format_id, "test")
        self.assertEqual(result.confidence, 0.85)
        self.assertEqual(len(result.match_reasons), 2)
        self.assertTrue(result.dimension_match)
        self.assertTrue(result.aspect_ratio_match)
        self.assertEqual(result.quality_indicators["sharpness"], 0.9)
    
    def test_validation_context_creation(self):
        """Test ValidationContext creation and properties."""
        rule = FormatRule(format_id="test", display_name="Test")
        
        context = ValidationContext(
            format_rule=rule,
            image_path="/test/path.jpg",
            image_dimensions=(600, 600),
            processing_options={"quality": "high"}
        )
        
        self.assertEqual(context.format_rule.format_id, "test")
        self.assertEqual(context.image_path, "/test/path.jpg")
        self.assertEqual(context.image_dimensions, (600, 600))
        self.assertEqual(context.processing_options["quality"], "high")


if __name__ == '__main__':
    import unittest
    unittest.main()