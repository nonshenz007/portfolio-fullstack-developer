"""
Integration tests for the FormatValidator class.

This module provides comprehensive tests for the complete validation pipeline
including dimension validation, face positioning, background compliance,
and quality checks.
"""

import unittest
import numpy as np
import cv2
from PIL import Image, ImageDraw
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock

from validation.format_validator import (
    FormatValidator, ComplianceResult, ValidationReport,
    DimensionResult, PositionResult, BackgroundResult
)
from config.config_manager import ConfigManager
from detection.data_models import Point
from detection.face_detector import FaceMetrics


class TestFormatValidator(unittest.TestCase):
    """Test cases for FormatValidator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create mock config manager with test rules
        self.mock_config = Mock(spec=ConfigManager)
        
        # Patch external dependencies
        self.face_detector_patcher = patch('validation.format_validator.FaceDetector')
        self.bg_processor_patcher = patch('validation.format_validator.BackgroundProcessor')
        
        self.mock_face_detector_class = self.face_detector_patcher.start()
        self.mock_bg_processor_class = self.bg_processor_patcher.start()
        
        self.mock_face_detector = Mock()
        self.mock_bg_processor = Mock()
        
        self.mock_face_detector_class.return_value = self.mock_face_detector
        self.mock_bg_processor_class.return_value = self.mock_bg_processor
        self.test_rules = {
            'ICS-UAE': {
                'display_name': 'ICS (UAE)',
                'dimensions': {
                    'width': 945,
                    'height': 1417,
                    'unit': 'pixels'
                },
                'face_requirements': {
                    'height_ratio': [0.70, 0.80],
                    'eye_height_ratio': [0.50, 0.60],
                    'centering_tolerance': 0.05
                },
                'background': {
                    'color': 'white',
                    'rgb_values': [255, 255, 255],
                    'tolerance': 10
                },
                'quality_thresholds': {
                    'min_brightness': 50,
                    'max_brightness': 200,
                    'min_sharpness': 100,
                    'max_blur_variance': 50
                }
            },
            'US-Visa': {
                'display_name': 'US Visa',
                'dimensions': {
                    'width': 600,
                    'height': 600,
                    'unit': 'pixels'
                },
                'face_requirements': {
                    'height_ratio': [0.69, 0.80],
                    'eye_height_ratio': [0.56, 0.69],
                    'centering_tolerance': 0.05
                },
                'background': {
                    'color': 'white',
                    'rgb_values': [255, 255, 255],
                    'tolerance': 8
                },
                'quality_thresholds': {
                    'min_brightness': 60,
                    'max_brightness': 190,
                    'min_sharpness': 120,
                    'max_blur_variance': 40
                }
            }
        }
        # Mock the methods that FormatValidator actually uses
        self.mock_config.get_available_formats.return_value = list(self.test_rules.keys())
        
        def mock_get_format_rules(format_name):
            if format_name in self.test_rules:
                rule_data = self.test_rules[format_name]
                from config.config_manager import FormatRule
                return FormatRule(
                    display_name=rule_data['display_name'],
                    dimensions=rule_data['dimensions'],
                    face_requirements=rule_data['face_requirements'],
                    background=rule_data['background'],
                    file_specs=rule_data.get('file_specs', {}),
                    quality_thresholds=rule_data.get('quality_thresholds', {})
                )
            return None
        
        self.mock_config.get_format_rules.side_effect = mock_get_format_rules
        
        # Create validator instance
        self.validator = FormatValidator(self.mock_config)
    
    def tearDown(self):
        """Clean up patches."""
        self.face_detector_patcher.stop()
        self.bg_processor_patcher.stop()
    
    def create_test_image(self, width: int = 945, height: int = 1417, 
                         bg_color: tuple = (255, 255, 255)) -> Image.Image:
        """Create a test image with specified dimensions and background."""
        image = Image.new('RGB', (width, height), bg_color)
        
        # Add a simple face-like shape for testing
        draw = ImageDraw.Draw(image)
        face_width = width // 4
        face_height = height // 3
        face_x = (width - face_width) // 2
        face_y = height // 3
        
        # Draw face oval
        draw.ellipse([face_x, face_y, face_x + face_width, face_y + face_height], 
                    fill=(220, 180, 140))
        
        # Draw eyes
        eye_y = face_y + face_height // 3
        left_eye_x = face_x + face_width // 4
        right_eye_x = face_x + 3 * face_width // 4
        eye_size = 10
        
        draw.ellipse([left_eye_x - eye_size, eye_y - eye_size, 
                     left_eye_x + eye_size, eye_y + eye_size], fill=(0, 0, 0))
        draw.ellipse([right_eye_x - eye_size, eye_y - eye_size, 
                     right_eye_x + eye_size, eye_y + eye_size], fill=(0, 0, 0))
        
        return image
    
    def create_mock_face_metrics(self, face_detected: bool = True, 
                               face_height_ratio: float = 0.75,
                               eye_height_ratio: float = 0.55,
                               centering_offset: float = 0.02) -> FaceMetrics:
        """Create mock face metrics for testing."""
        return FaceMetrics(
            face_detected=face_detected,
            face_bounds=(100, 200, 200, 300),
            eye_positions=(Point(150, 250), Point(250, 250)),
            face_height_ratio=face_height_ratio,
            eye_height_ratio=eye_height_ratio,
            centering_offset=centering_offset,
            confidence_score=0.95
        )
    
    def test_init_with_config_manager(self):
        """Test FormatValidator initialization with config manager."""
        validator = FormatValidator(self.mock_config)
        self.assertEqual(validator.config_manager, self.mock_config)
        self.assertIsNotNone(validator.quality_checker)
        self.assertIsNotNone(validator.face_detector)
        self.assertIsNotNone(validator.background_processor)
        # Check that format rules were converted correctly
        self.assertEqual(len(validator.format_rules), 2)
        self.assertIn('ICS-UAE', validator.format_rules)
        self.assertIn('US-Visa', validator.format_rules)
    
    @patch('validation.format_validator.ConfigManager')
    def test_init_without_config_manager(self, mock_config_class):
        """Test FormatValidator initialization without config manager."""
        mock_instance = Mock()
        mock_instance.get_available_formats.return_value = []
        mock_instance.get_format_rules.return_value = None
        mock_config_class.return_value = mock_instance
        
        validator = FormatValidator()
        self.assertIsNotNone(validator.config_manager)
        mock_config_class.assert_called_once()
    
    def test_check_dimensions_pass(self):
        """Test dimension validation with correct dimensions."""
        image = self.create_test_image(945, 1417)
        format_rules = self.test_rules['ICS-UAE']
        
        result = self.validator.check_dimensions(image, format_rules)
        
        self.assertTrue(result.passes)
        self.assertEqual(result.actual_dimensions, (945, 1417))
        self.assertEqual(result.required_dimensions, (945, 1417))
        self.assertAlmostEqual(result.dimension_ratio, 1.0, places=2)
        self.assertEqual(len(result.suggestions), 0)
    
    def test_check_dimensions_fail_too_small(self):
        """Test dimension validation with image too small."""
        image = self.create_test_image(800, 1200)
        format_rules = self.test_rules['ICS-UAE']
        
        result = self.validator.check_dimensions(image, format_rules)
        
        self.assertFalse(result.passes)
        self.assertEqual(result.actual_dimensions, (800, 1200))
        self.assertEqual(result.required_dimensions, (945, 1417))
        self.assertLess(result.dimension_ratio, 1.0)
        self.assertGreater(len(result.suggestions), 0)
        self.assertIn("too small", result.suggestions[0])
    
    def test_check_dimensions_fail_too_large(self):
        """Test dimension validation with image too large."""
        image = self.create_test_image(1200, 1800)
        format_rules = self.test_rules['ICS-UAE']
        
        result = self.validator.check_dimensions(image, format_rules)
        
        self.assertFalse(result.passes)
        self.assertEqual(result.actual_dimensions, (1200, 1800))
        self.assertEqual(result.required_dimensions, (945, 1417))
        self.assertGreater(len(result.suggestions), 0)
        self.assertIn("too large", result.suggestions[0])
    
    def test_validate_face_positioning_pass(self):
        """Test face positioning validation with correct positioning."""
        # Setup mock face detector
        mock_face_metrics = self.create_mock_face_metrics()
        mock_landmarks = Mock()
        self.mock_face_detector.detect_face_landmarks.return_value = mock_landmarks
        self.mock_face_detector.calculate_face_metrics.return_value = mock_face_metrics
        
        image = np.array(self.create_test_image())
        format_rules = self.test_rules['ICS-UAE']
        
        result = self.validator.validate_face_positioning(image, format_rules)
        
        self.assertTrue(result.passes)
        self.assertTrue(result.face_detected)
        self.assertEqual(result.face_height_ratio, 0.75)
        self.assertEqual(result.eye_height_ratio, 0.55)
        self.assertEqual(result.centering_offset, 0.02)
        self.assertEqual(len(result.suggestions), 0)
    
    def test_validate_face_positioning_no_face(self):
        """Test face positioning validation with no face detected."""
        # Setup mock face detector
        mock_face_metrics = self.create_mock_face_metrics(face_detected=False)
        mock_landmarks = Mock()
        self.mock_face_detector.detect_face_landmarks.return_value = mock_landmarks
        self.mock_face_detector.calculate_face_metrics.return_value = mock_face_metrics
        
        image = np.array(self.create_test_image())
        format_rules = self.test_rules['ICS-UAE']
        
        result = self.validator.validate_face_positioning(image, format_rules)
        
        self.assertFalse(result.passes)
        self.assertFalse(result.face_detected)
        self.assertGreater(len(result.suggestions), 0)
        self.assertIn("No face detected", result.suggestions[0])
    
    def test_validate_face_positioning_face_too_small(self):
        """Test face positioning validation with face too small."""
        # Setup mock face detector
        mock_face_metrics = self.create_mock_face_metrics(face_height_ratio=0.60)  # Below 0.70 minimum
        mock_landmarks = Mock()
        self.mock_face_detector.detect_face_landmarks.return_value = mock_landmarks
        self.mock_face_detector.calculate_face_metrics.return_value = mock_face_metrics
        
        image = np.array(self.create_test_image())
        format_rules = self.test_rules['ICS-UAE']
        
        result = self.validator.validate_face_positioning(image, format_rules)
        
        self.assertFalse(result.passes)
        self.assertTrue(result.face_detected)
        self.assertGreater(len(result.suggestions), 0)
        self.assertIn("too small", result.suggestions[0])
    
    def test_check_background_compliance_pass(self):
        """Test background compliance validation with correct white background."""
        image = np.array(self.create_test_image(bg_color=(255, 255, 255)))
        format_rules = self.test_rules['ICS-UAE']
        
        result = self.validator.check_background_compliance(image, format_rules)
        
        self.assertTrue(result.passes)
        self.assertEqual(result.required_background_color, (255, 255, 255))
        self.assertLessEqual(result.color_difference, 10)  # Within tolerance
        self.assertTrue(result.uniform_background)
    
    def test_check_background_compliance_fail_wrong_color(self):
        """Test background compliance validation with wrong background color."""
        image = np.array(self.create_test_image(bg_color=(200, 200, 200)))  # Gray instead of white
        format_rules = self.test_rules['ICS-UAE']
        
        result = self.validator.check_background_compliance(image, format_rules)
        
        self.assertFalse(result.passes)
        self.assertEqual(result.required_background_color, (255, 255, 255))
        self.assertGreater(result.color_difference, 10)  # Outside tolerance
        self.assertGreater(len(result.suggestions), 0)
        self.assertIn("doesn't match", result.suggestions[0])
    
    def test_validate_compliance_complete_pass(self):
        """Test complete compliance validation with all checks passing."""
        # Setup mock face detector
        mock_face_metrics = self.create_mock_face_metrics()
        mock_landmarks = Mock()
        self.mock_face_detector.detect_face_landmarks.return_value = mock_landmarks
        self.mock_face_detector.calculate_face_metrics.return_value = mock_face_metrics
        
        # Mock quality checker to return passing results
        with patch.object(self.validator.quality_checker, 'check_brightness') as mock_brightness, \
             patch.object(self.validator.quality_checker, 'detect_blur') as mock_blur, \
             patch.object(self.validator.quality_checker, 'validate_contrast') as mock_contrast, \
             patch.object(self.validator.quality_checker, 'check_color_accuracy') as mock_color, \
             patch.object(self.validator.quality_checker, 'generate_quality_score') as mock_score:
            
            # Mock all quality checks to pass
            from validation.quality_checker import BrightnessResult, BlurResult, ContrastResult, ColorResult, QualityScore
            
            mock_brightness.return_value = BrightnessResult(
                average_brightness=120, brightness_distribution={}, passes_threshold=True,
                min_threshold=50, max_threshold=200, suggestions=[]
            )
            mock_blur.return_value = BlurResult(
                laplacian_variance=150, is_sharp=True, sharpness_score=150,
                threshold=100, suggestions=[]
            )
            mock_contrast.return_value = ContrastResult(
                contrast_score=40, histogram_spread=150, passes_threshold=True, suggestions=[]
            )
            mock_color.return_value = ColorResult(
                color_balance={}, saturation_level=50, color_cast_detected=False,
                dominant_colors=[], suggestions=[]
            )
            mock_score.return_value = QualityScore(
                overall_score=95, brightness_score=100, sharpness_score=100,
                contrast_score=90, color_score=100, passes_all_checks=True,
                failed_checks=[], recommendations=[]
            )
            
            # Create compliant test image
            image = self.create_test_image(945, 1417, (255, 255, 255))
            
            result = self.validator.validate_compliance(image, 'ICS-UAE')
            
            self.assertIsInstance(result, ComplianceResult)
            self.assertTrue(result.passes)
            self.assertEqual(result.format_name, 'ICS-UAE')
            self.assertGreater(result.overall_score, 80)  # High score for passing all checks
            self.assertGreater(result.processing_time, 0)
            
            # Check individual results
            self.assertTrue(result.dimension_result.passes)
            self.assertTrue(result.position_result.passes)
            self.assertTrue(result.background_result.passes)
            self.assertTrue(result.quality_result.passes_all_checks)
    
    def test_validate_compliance_complete_fail(self):
        """Test complete compliance validation with multiple failures."""
        # Setup mock face detector
        mock_face_metrics = self.create_mock_face_metrics(face_detected=False)
        mock_landmarks = Mock()
        self.mock_face_detector.detect_face_landmarks.return_value = mock_landmarks
        self.mock_face_detector.calculate_face_metrics.return_value = mock_face_metrics
        
        # Create non-compliant test image (wrong dimensions, wrong background)
        image = self.create_test_image(500, 500, (200, 200, 200))
        
        result = self.validator.validate_compliance(image, 'ICS-UAE')
        
        self.assertIsInstance(result, ComplianceResult)
        self.assertFalse(result.passes)
        self.assertEqual(result.format_name, 'ICS-UAE')
        self.assertLess(result.overall_score, 50)  # Low score for failing checks
        self.assertGreater(len(result.issues), 0)
        
        # Check individual results
        self.assertFalse(result.dimension_result.passes)
        self.assertFalse(result.position_result.passes)
        self.assertFalse(result.background_result.passes)
    
    def test_validate_compliance_with_file_path(self):
        """Test compliance validation using file path input."""
        # Create temporary test image file
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
            image = self.create_test_image()
            image.save(tmp_file.name, 'JPEG')
            tmp_path = tmp_file.name
        
        try:
            # Setup mock face detector
            mock_face_metrics = self.create_mock_face_metrics()
            mock_landmarks = Mock()
            self.mock_face_detector.detect_face_landmarks.return_value = mock_landmarks
            self.mock_face_detector.calculate_face_metrics.return_value = mock_face_metrics
            
            result = self.validator.validate_compliance(tmp_path, 'ICS-UAE')
            
            self.assertIsInstance(result, ComplianceResult)
            self.assertEqual(result.format_name, 'ICS-UAE')
        finally:
            os.unlink(tmp_path)
    
    def test_validate_compliance_invalid_format(self):
        """Test compliance validation with invalid format name."""
        image = self.create_test_image()
        
        with self.assertRaises(ValueError) as context:
            self.validator.validate_compliance(image, 'INVALID-FORMAT')
        
        self.assertIn("Unknown format", str(context.exception))
    
    def test_validate_compliance_invalid_image_path(self):
        """Test compliance validation with non-existent file path."""
        with self.assertRaises(FileNotFoundError):
            self.validator.validate_compliance('/nonexistent/path.jpg', 'ICS-UAE')
    
    def test_generate_validation_report(self):
        """Test validation report generation."""
        # Setup mock face detector
        mock_face_metrics = self.create_mock_face_metrics()
        mock_landmarks = Mock()
        self.mock_face_detector.detect_face_landmarks.return_value = mock_landmarks
        self.mock_face_detector.calculate_face_metrics.return_value = mock_face_metrics
        
        image = self.create_test_image()
        compliance_result = self.validator.validate_compliance(image, 'ICS-UAE')
        
        report = self.validator.generate_validation_report(compliance_result, '/test/path.jpg')
        
        self.assertIsInstance(report, ValidationReport)
        self.assertEqual(report.format_name, 'ICS-UAE')
        self.assertEqual(report.overall_pass, compliance_result.passes)
        self.assertEqual(report.compliance_score, compliance_result.overall_score)
        self.assertEqual(report.image_path, '/test/path.jpg')
        self.assertIsNotNone(report.timestamp)
        self.assertIsInstance(report.suggestions, list)
    
    def test_multiple_format_validation(self):
        """Test validation against multiple formats."""
        # Setup mock face detector
        mock_face_metrics = self.create_mock_face_metrics()
        mock_landmarks = Mock()
        self.mock_face_detector.detect_face_landmarks.return_value = mock_landmarks
        self.mock_face_detector.calculate_face_metrics.return_value = mock_face_metrics
        
        # Test ICS-UAE format
        ics_image = self.create_test_image(945, 1417)
        ics_result = self.validator.validate_compliance(ics_image, 'ICS-UAE')
        self.assertEqual(ics_result.format_name, 'ICS-UAE')
        
        # Test US-Visa format
        us_image = self.create_test_image(600, 600)
        us_result = self.validator.validate_compliance(us_image, 'US-Visa')
        self.assertEqual(us_result.format_name, 'US-Visa')
        
        # Both should have different dimension requirements
        self.assertNotEqual(
            ics_result.dimension_result.required_dimensions,
            us_result.dimension_result.required_dimensions
        )


class TestValidationDataClasses(unittest.TestCase):
    """Test cases for validation data classes."""
    
    def test_dimension_result_creation(self):
        """Test DimensionResult data class creation."""
        result = DimensionResult(
            passes=True,
            actual_dimensions=(945, 1417),
            required_dimensions=(945, 1417),
            dimension_ratio=1.0,
            suggestions=[]
        )
        
        self.assertTrue(result.passes)
        self.assertEqual(result.actual_dimensions, (945, 1417))
        self.assertEqual(result.required_dimensions, (945, 1417))
        self.assertEqual(result.dimension_ratio, 1.0)
        self.assertEqual(result.suggestions, [])
    
    def test_position_result_creation(self):
        """Test PositionResult data class creation."""
        result = PositionResult(
            passes=True,
            face_detected=True,
            face_height_ratio=0.75,
            eye_height_ratio=0.55,
            centering_offset=0.02,
            required_face_height_range=(0.70, 0.80),
            required_eye_height_range=(0.50, 0.60),
            centering_tolerance=0.05,
            suggestions=[]
        )
        
        self.assertTrue(result.passes)
        self.assertTrue(result.face_detected)
        self.assertEqual(result.face_height_ratio, 0.75)
        self.assertEqual(result.eye_height_ratio, 0.55)
        self.assertEqual(result.centering_offset, 0.02)
    
    def test_background_result_creation(self):
        """Test BackgroundResult data class creation."""
        result = BackgroundResult(
            passes=True,
            background_color_detected=(255, 255, 255),
            required_background_color=(255, 255, 255),
            color_difference=0.0,
            tolerance=10,
            uniform_background=True,
            suggestions=[]
        )
        
        self.assertTrue(result.passes)
        self.assertEqual(result.background_color_detected, (255, 255, 255))
        self.assertEqual(result.required_background_color, (255, 255, 255))
        self.assertEqual(result.color_difference, 0.0)
        self.assertTrue(result.uniform_background)


if __name__ == '__main__':
    unittest.main()