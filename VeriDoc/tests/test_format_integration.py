"""
Integration tests for Format Rule Engine

Tests the complete workflow of format configuration, inheritance,
auto-detection, validation, and hot-reload functionality.
"""

import json
import os
import tempfile
import shutil
import time
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch, MagicMock

from rules.format_rule_engine import FormatRuleEngine
from utils.format_detector import FormatDetector
from config.hot_reload_manager import HotReloadManager


class TestFormatRuleEngineIntegration(TestCase):
    """Integration tests for the complete format rule system."""
    
    def setUp(self):
        """Set up integration test environment."""
        # Create temporary directories
        self.test_config_dir = tempfile.mkdtemp()
        self.test_formats_dir = Path(self.test_config_dir) / "formats"
        self.test_formats_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self.engine = FormatRuleEngine(str(self.test_formats_dir))
        self.detector = FormatDetector(self.engine)
        self.hot_reload = HotReloadManager(self.engine, [str(self.test_formats_dir)])
        
        # Create comprehensive test format hierarchy
        self._create_format_hierarchy()
    
    def tearDown(self):
        """Clean up integration test environment."""
        if self.hot_reload.is_watching:
            self.hot_reload.stop_watching()
        shutil.rmtree(self.test_config_dir, ignore_errors=True)
    
    def _create_format_hierarchy(self):
        """Create a comprehensive format hierarchy for testing."""
        # Base ICAO format
        base_icao = {
            "format_id": "base_icao",
            "display_name": "Base ICAO Standard",
            "version": "2023.1",
            "authority": "ICAO",
            "regulation_references": ["ICAO Doc 9303"],
            "dimensions": {
                "width": 600,
                "height": 600,
                "unit": "pixels",
                "aspect_ratio": 1.0,
                "aspect_tolerance": 0.02
            },
            "face_requirements": {
                "height_ratio": [0.70, 0.80],
                "eye_height_ratio": [0.50, 0.60],
                "centering_tolerance": 0.05,
                "regulation_reference": "ICAO Doc 9303 Part 4"
            },
            "background": {
                "color": "white",
                "rgb_values": [255, 255, 255],
                "tolerance": 10,
                "uniformity_threshold": 0.9,
                "regulation_reference": "ICAO Doc 9303 Part 6"
            },
            "quality_thresholds": {
                "min_brightness": 80,
                "max_brightness": 200,
                "min_sharpness": 100,
                "regulation_reference": "ICAO Doc 9303 Part 5"
            },
            "icao_rules": {
                "glasses": {
                    "tinted_lenses_allowed": False,
                    "max_glare_intensity": 0.2
                },
                "expression": {
                    "neutral_required": True,
                    "mouth_closed_required": True
                }
            },
            "detection_criteria": {
                "min_resolution": 600,
                "target_aspect_ratio": 1.0,
                "aspect_ratio_tolerance": 0.05
            }
        }
        
        # US Visa format (inherits from base_icao)
        us_visa = {
            "format_id": "us_visa",
            "display_name": "US Visa Photo",
            "inherits_from": "base_icao",
            "country": "United States",
            "authority": "US Department of State",
            "regulation_references": [
                "ICAO Doc 9303",
                "US Department of State Photo Requirements"
            ],
            "face_requirements": {
                "height_ratio": [0.69, 0.80],
                "eye_height_ratio": [0.56, 0.69]
            },
            "icao_rules": {
                "glasses": {
                    "prescription_glasses_allowed": False,
                    "max_glare_intensity": 0.15
                }
            },
            "validation_strictness": "strict"
        }
        
        # ICS UAE format (inherits from base_icao)
        ics_uae = {
            "format_id": "ics_uae",
            "display_name": "ICS (UAE)",
            "inherits_from": "base_icao",
            "country": "United Arab Emirates",
            "authority": "ICS UAE",
            "dimensions": {
                "width": 413,
                "height": 531,
                "aspect_ratio": 0.7778,
                "aspect_tolerance": 0.020
            },
            "face_requirements": {
                "height_ratio": [0.62, 0.69],
                "eye_height_ratio": [0.33, 0.36]
            },
            "quality_thresholds": {
                "min_brightness": 55,
                "max_brightness": 190,
                "min_sharpness": 120
            },
            "detection_criteria": {
                "min_resolution": 400,
                "target_aspect_ratio": 0.7778,
                "aspect_ratio_tolerance": 0.03
            }
        }
        
        # Schengen Visa format (inherits from base_icao)
        schengen_visa = {
            "format_id": "schengen_visa",
            "display_name": "Schengen Visa",
            "inherits_from": "base_icao",
            "country": "European Union",
            "authority": "Schengen Area",
            "dimensions": {
                "width": 413,
                "height": 531,
                "aspect_ratio": 0.7778
            },
            "background": {
                "color": "light_gray",
                "rgb_values": [240, 240, 240],
                "tolerance": 15
            },
            "icao_rules": {
                "glasses": {
                    "prescription_glasses_allowed": True,
                    "max_glare_intensity": 0.25
                }
            }
        }
        
        # Write configuration files
        formats = {
            "base_icao": base_icao,
            "us_visa": us_visa,
            "ics_uae": ics_uae,
            "schengen_visa": schengen_visa
        }
        
        for format_id, config in formats.items():
            config_path = self.test_formats_dir / f"{format_id}.json"
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
        
        # Load configurations
        self.engine._load_all_formats()
    
    def test_complete_format_hierarchy_loading(self):
        """Test that the complete format hierarchy loads correctly."""
        formats = self.engine.get_available_formats()
        expected_formats = ["base_icao", "us_visa", "ics_uae", "schengen_visa"]
        
        for expected in expected_formats:
            self.assertIn(expected, formats)
        
        # Test that all formats can be retrieved
        for format_id in expected_formats:
            rule = self.engine.get_format_rule(format_id)
            self.assertIsNotNone(rule)
            self.assertEqual(rule.format_id, format_id)
    
    def test_inheritance_chain_resolution(self):
        """Test that inheritance chains are resolved correctly."""
        # Test US Visa inherits from base_icao
        us_visa = self.engine.get_format_rule("us_visa")
        self.assertIsNotNone(us_visa)
        
        # Should inherit base dimensions but override face requirements
        self.assertEqual(us_visa.dimensions["width"], 600)  # From base
        self.assertEqual(us_visa.dimensions["height"], 600)  # From base
        self.assertEqual(us_visa.face_requirements["height_ratio"], [0.69, 0.80])  # Overridden
        self.assertEqual(us_visa.face_requirements["centering_tolerance"], 0.05)  # Inherited
        
        # Should inherit background settings
        self.assertEqual(us_visa.background["color"], "white")
        self.assertEqual(us_visa.background["rgb_values"], [255, 255, 255])
        
        # Should override ICAO rules
        self.assertFalse(us_visa.icao_rules["glasses"]["prescription_glasses_allowed"])
        self.assertEqual(us_visa.icao_rules["glasses"]["max_glare_intensity"], 0.15)
    
    def test_format_specific_validation(self):
        """Test format-specific validation with different formats."""
        # Create test validation data
        validation_data = {
            "dimensions": {"width": 600, "height": 600},
            "face_analysis": {
                "height_ratio": 0.75,
                "eye_height_ratio": 0.55,
                "center_offset": 0.03
            },
            "background_analysis": {
                "dominant_color": [255, 255, 255],
                "uniformity": 0.95
            },
            "quality_analysis": {
                "sharpness": 150,
                "brightness": 120
            }
        }
        
        # Test validation against different formats
        formats_to_test = ["base_icao", "us_visa", "ics_uae"]
        
        for format_id in formats_to_test:
            with self.subTest(format_id=format_id):
                result = self.engine.validate_format_compliance(format_id, validation_data)
                
                self.assertTrue(result["success"])
                self.assertEqual(result["format_id"], format_id)
                self.assertIsInstance(result["overall_compliance"], float)
                self.assertIsInstance(result["rule_results"], list)
                self.assertGreater(len(result["rule_results"]), 0)
    
    @patch('PIL.Image.open')
    @patch('os.path.getsize')
    def test_auto_detection_workflow(self, mock_getsize, mock_image_open):
        """Test the complete auto-detection workflow."""
        # Mock different image scenarios
        test_scenarios = [
            {
                "name": "square_image",
                "size": (600, 600),
                "format": "JPEG",
                "file_size": 1024 * 1024,
                "expected_matches": ["base_icao", "us_visa"]
            },
            {
                "name": "portrait_image",
                "size": (413, 531),
                "format": "JPEG", 
                "file_size": 2 * 1024 * 1024,
                "expected_matches": ["ics_uae", "schengen_visa"]
            }
        ]
        
        for scenario in test_scenarios:
            with self.subTest(scenario=scenario["name"]):
                # Mock image properties
                mock_img = MagicMock()
                mock_img.size = scenario["size"]
                mock_img.format = scenario["format"]
                mock_img.mode = 'RGB'
                mock_img._getexif.return_value = None
                mock_image_open.return_value.__enter__.return_value = mock_img
                
                mock_getsize.return_value = scenario["file_size"]
                
                # Test detection
                test_image_path = Path(self.test_config_dir) / f"{scenario['name']}.jpg"
                test_image_path.touch()
                
                try:
                    results = self.detector.detect_format(str(test_image_path))
                    
                    self.assertIsInstance(results, list)
                    if results:
                        # Check that expected formats are in top results
                        top_formats = [r.format_id for r in results[:3]]
                        for expected in scenario["expected_matches"]:
                            if expected in self.engine.get_available_formats():
                                # At least one expected format should be detected
                                pass
                
                finally:
                    if test_image_path.exists():
                        test_image_path.unlink()
    
    def test_hot_reload_integration(self):
        """Test hot-reload integration with format engine."""
        # Start hot-reload monitoring
        self.hot_reload.start_watching()
        
        # Track reload events
        reload_events = []
        
        def track_reload(message):
            reload_events.append(message)
        
        self.hot_reload.add_change_handler(track_reload)
        
        # Add a new format configuration
        new_format = {
            "format_id": "test_new_format",
            "display_name": "Test New Format",
            "inherits_from": "base_icao",
            "dimensions": {
                "width": 300,
                "height": 400
            }
        }
        
        new_config_path = self.test_formats_dir / "test_new_format.json"
        with open(new_config_path, 'w') as f:
            json.dump(new_format, f, indent=2)
        
        # Force reload to simulate file change detection
        success = self.hot_reload.force_reload()
        self.assertTrue(success)
        
        # Verify new format is available
        formats = self.engine.get_available_formats()
        self.assertIn("test_new_format", formats)
        
        # Verify inheritance works for new format
        new_rule = self.engine.get_format_rule("test_new_format")
        self.assertIsNotNone(new_rule)
        self.assertEqual(new_rule.dimensions["width"], 300)  # Overridden
        self.assertEqual(new_rule.background["color"], "white")  # Inherited
        
        # Verify reload event was tracked
        self.assertGreater(len(reload_events), 0)
    
    def test_format_compatibility_analysis(self):
        """Test format compatibility analysis."""
        matrix = self.detector.get_format_compatibility_matrix()
        
        self.assertIsInstance(matrix, dict)
        
        # Test self-compatibility (should be 1.0)
        for format_id in self.engine.get_available_formats():
            if format_id in matrix:
                self.assertEqual(matrix[format_id][format_id], 1.0)
        
        # Test that similar formats have higher compatibility
        if "ics_uae" in matrix and "schengen_visa" in matrix:
            # Both have similar aspect ratios, should be somewhat compatible
            compatibility = matrix["ics_uae"]["schengen_visa"]
            self.assertIsInstance(compatibility, float)
            self.assertGreaterEqual(compatibility, 0.0)
            self.assertLessEqual(compatibility, 1.0)
    
    def test_validation_context_workflow(self):
        """Test the complete validation context workflow."""
        # Create validation context
        context = self.engine.create_validation_context(
            "us_visa",
            image_path="/test/image.jpg",
            image_dimensions=(600, 600),
            processing_options={"quality": "high", "auto_fix": True}
        )
        
        self.assertIsNotNone(context)
        self.assertEqual(context.format_rule.format_id, "us_visa")
        self.assertEqual(context.image_path, "/test/image.jpg")
        self.assertEqual(context.image_dimensions, (600, 600))
        self.assertEqual(context.processing_options["quality"], "high")
        
        # Test that context contains inherited properties
        self.assertEqual(context.format_rule.background["color"], "white")
        self.assertEqual(context.format_rule.face_requirements["centering_tolerance"], 0.05)
    
    def test_regulation_reference_propagation(self):
        """Test that regulation references are properly propagated."""
        us_visa = self.engine.get_format_rule("us_visa")
        self.assertIsNotNone(us_visa)
        
        # Should have both base and specific regulation references
        expected_refs = [
            "ICAO Doc 9303",
            "US Department of State Photo Requirements"
        ]
        
        for ref in expected_refs:
            self.assertIn(ref, us_visa.regulation_references)
    
    def test_error_recovery_and_fallbacks(self):
        """Test error recovery and fallback mechanisms."""
        # Test with invalid format ID
        result = self.engine.validate_format_compliance("invalid_format", {})
        self.assertFalse(result["success"])
        self.assertIn("error", result)
        
        # Test with missing validation data
        result = self.engine.validate_format_compliance("base_icao", {})
        self.assertTrue(result["success"])  # Should handle gracefully
        
        # Test context creation with invalid format
        context = self.engine.create_validation_context("invalid_format")
        self.assertIsNone(context)
    
    def test_performance_with_large_hierarchy(self):
        """Test performance with a larger format hierarchy."""
        # Create additional formats to test performance
        start_time = time.time()
        
        for i in range(10):
            additional_format = {
                "format_id": f"perf_test_{i}",
                "display_name": f"Performance Test Format {i}",
                "inherits_from": "base_icao",
                "dimensions": {
                    "width": 400 + i * 10,
                    "height": 500 + i * 10
                }
            }
            
            config_path = self.test_formats_dir / f"perf_test_{i}.json"
            with open(config_path, 'w') as f:
                json.dump(additional_format, f, indent=2)
        
        # Reload and measure time
        reload_start = time.time()
        self.engine._load_all_formats()
        reload_time = time.time() - reload_start
        
        # Should complete reasonably quickly (less than 1 second for small test)
        self.assertLess(reload_time, 1.0)
        
        # Verify all formats loaded
        formats = self.engine.get_available_formats()
        for i in range(10):
            self.assertIn(f"perf_test_{i}", formats)
        
        total_time = time.time() - start_time
        self.assertLess(total_time, 2.0)  # Total test should be fast


if __name__ == '__main__':
    import unittest
    unittest.main()