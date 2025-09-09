"""
Unit tests for ICAO Compliance Validator

Tests all ICAO rule implementations with reference images and edge cases.
"""

import unittest
import numpy as np
import cv2
from unittest.mock import Mock, patch, MagicMock
import tempfile
import os
from dataclasses import dataclass

from validation.icao_validator import (
    ICAOValidator, GlassesResult, HeadCoveringResult, ExpressionResult,
    PhotoQualityResult, StyleLightingResult, ComplianceReport
)
from rules.icao_rules_engine import ICAORulesEngine, RuleResult, RuleSeverity
from ai.ai_engine import FaceFeatures, FaceDetection


class TestICAOValidator(unittest.TestCase):
    """Test cases for ICAO Compliance Validator"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create mock components
        self.mock_rules_engine = Mock(spec=ICAORulesEngine)
        self.mock_ai_engine = Mock()
        self.mock_quality_checker = Mock()
        
        # Create test image
        self.test_image = np.zeros((600, 400, 3), dtype=np.uint8)
        self.test_image.fill(255)  # White background
        
        # Add a simple face-like region
        cv2.rectangle(self.test_image, (150, 200), (250, 350), (200, 180, 160), -1)  # Face
        cv2.circle(self.test_image, (180, 250), 5, (50, 50, 50), -1)  # Left eye
        cv2.circle(self.test_image, (220, 250), 5, (50, 50, 50), -1)  # Right eye
        cv2.rectangle(self.test_image, (190, 280), (210, 290), (150, 100, 100), -1)  # Mouth
        
        # Create mock face features
        self.mock_face_features = Mock(spec=FaceFeatures)
        self.mock_face_features.glasses_detected = False
        self.mock_face_features.head_covering_detected = False
        self.mock_face_features.eye_positions = ((180, 250), (220, 250))
        self.mock_face_features.mouth_position = (200, 285)
        self.mock_face_features.mouth_openness = 0.05
        self.mock_face_features.eye_openness = (0.9, 0.9)
        self.mock_face_features.face_orientation = {
            'yaw': 0.0,
            'pitch': 0.0,
            'roll': 0.0
        }
        
        # Create mock face detection
        self.mock_face_detection = Mock(spec=FaceDetection)
        self.mock_face_detection.landmarks = Mock()
        
        # Set up mock rules
        self._setup_mock_rules()
        
        # Create validator instance
        self.validator = ICAOValidator(
            rules_engine=self.mock_rules_engine,
            ai_engine=self.mock_ai_engine,
            quality_checker=self.mock_quality_checker
        )
    
    def _setup_mock_rules(self):
        """Set up mock ICAO rules"""
        # Mock rule definitions
        mock_tinted_rule = Mock()
        mock_tinted_rule.rule_id = "ICAO.3.2.1"
        mock_tinted_rule.parameters = {'allowed': False, 'detection_threshold': 0.3}
        
        mock_heavy_frames_rule = Mock()
        mock_heavy_frames_rule.rule_id = "ICAO.3.2.2"
        mock_heavy_frames_rule.parameters = {'max_frame_width_ratio': 0.15}
        
        mock_glare_rule = Mock()
        mock_glare_rule.rule_id = "ICAO.3.2.3"
        mock_glare_rule.parameters = {'max_glare_intensity': 0.2}
        
        mock_prescription_rule = Mock()
        mock_prescription_rule.rule_id = "ICAO.3.2.4"
        mock_prescription_rule.parameters = {'eye_visibility_requirement': 0.9}
        
        # Set up glasses rules
        self.mock_rules_engine.get_glasses_rules.return_value = {
            'tinted_lenses': mock_tinted_rule,
            'heavy_frames': mock_heavy_frames_rule,
            'glare_reflection': mock_glare_rule,
            'prescription_glasses': mock_prescription_rule
        }
        
        # Mock head covering rules
        mock_religious_rule = Mock()
        mock_religious_rule.rule_id = "ICAO.3.3.1"
        mock_religious_rule.parameters = {'face_visibility_requirement': 0.85}
        
        mock_non_religious_rule = Mock()
        mock_non_religious_rule.rule_id = "ICAO.3.3.2"
        mock_non_religious_rule.parameters = {'allowed': False}
        
        mock_face_coverage_rule = Mock()
        mock_face_coverage_rule.rule_id = "ICAO.3.3.3"
        mock_face_coverage_rule.parameters = {'min_face_visibility': 0.8}
        
        self.mock_rules_engine.get_head_covering_rules.return_value = {
            'religious_exception': mock_religious_rule,
            'non_religious': mock_non_religious_rule,
            'face_coverage': mock_face_coverage_rule
        }
        
        # Mock expression rules
        mock_neutral_rule = Mock()
        mock_neutral_rule.rule_id = "ICAO.4.1.1"
        mock_neutral_rule.parameters = {'mouth_openness_max': 0.1, 'smile_detection_max': 0.2}
        
        mock_gaze_rule = Mock()
        mock_gaze_rule.rule_id = "ICAO.4.1.2"
        mock_gaze_rule.parameters = {'max_gaze_deviation_degrees': 5.0}
        
        mock_eyes_rule = Mock()
        mock_eyes_rule.rule_id = "ICAO.4.1.3"
        mock_eyes_rule.parameters = {'min_eye_openness': 0.7}
        
        self.mock_rules_engine.get_expression_rules.return_value = {
            'neutral_expression': mock_neutral_rule,
            'direct_gaze': mock_gaze_rule,
            'eyes_open': mock_eyes_rule
        }
        
        # Mock quality rules
        mock_sharpness_rule = Mock()
        mock_sharpness_rule.rule_id = "ICAO.5.1.1"
        mock_sharpness_rule.parameters = {'min_laplacian_variance': 100}
        
        mock_lighting_rule = Mock()
        mock_lighting_rule.rule_id = "ICAO.5.2.1"
        mock_lighting_rule.parameters = {'min_brightness': 80, 'max_brightness': 200}
        
        self.mock_rules_engine.get_photo_quality_rules.return_value = {
            'sharpness': mock_sharpness_rule,
            'lighting': mock_lighting_rule
        }
        
        # Mock style rules
        mock_background_rule = Mock()
        mock_background_rule.rule_id = "ICAO.6.1.1"
        mock_background_rule.parameters = {'required_color': 'white', 'color_tolerance': 10}
        
        mock_shadow_rule = Mock()
        mock_shadow_rule.rule_id = "ICAO.6.2.1"
        mock_shadow_rule.parameters = {'max_shadow_intensity': 0.2}
        
        self.mock_rules_engine.get_style_lighting_rules.return_value = {
            'background': mock_background_rule,
            'shadows': mock_shadow_rule
        }
        
        # Mock rule validation results
        def mock_validate_rule(rule_id, measured_value, context=None):
            return RuleResult(
                rule_id=rule_id,
                rule_name="test_rule",
                passes=True,
                measured_value=measured_value,
                required_value="test_required",
                confidence=0.9,
                severity=RuleSeverity.MAJOR,
                regulation_reference="ICAO Test",
                description="Test rule",
                suggestion="Test suggestion"
            )
        
        self.mock_rules_engine.validate_rule_compliance.side_effect = mock_validate_rule
    
    def test_validator_initialization(self):
        """Test ICAO validator initialization"""
        validator = ICAOValidator()
        self.assertIsNotNone(validator.rules_engine)
        self.assertIsNotNone(validator.ai_engine)
        self.assertIsNotNone(validator.quality_checker)
        self.assertIsNotNone(validator.glasses_rules)
        self.assertIsNotNone(validator.expression_rules)
    
    def test_glasses_compliance_no_glasses(self):
        """Test glasses compliance validation when no glasses detected"""
        # Set up mocks
        self.mock_face_features.glasses_detected = False
        
        # Test validation
        result = self.validator.validate_glasses_compliance(self.test_image, self.mock_face_features)
        
        # Assertions
        self.assertIsInstance(result, GlassesResult)
        self.assertFalse(result.glasses_detected)
        self.assertFalse(result.tinted_lenses_detected)
        self.assertFalse(result.heavy_frames_detected)
        self.assertFalse(result.glare_detected)
        self.assertEqual(result.eye_visibility_score, 1.0)
    
    def test_glasses_compliance_with_glasses(self):
        """Test glasses compliance validation with glasses detected"""
        # Set up mocks
        self.mock_face_features.glasses_detected = True
        
        # Test validation
        result = self.validator.validate_glasses_compliance(self.test_image, self.mock_face_features)
        
        # Assertions
        self.assertIsInstance(result, GlassesResult)
        self.assertTrue(result.glasses_detected)
        self.assertIsInstance(result.rule_results, list)
        self.assertIsInstance(result.suggestions, list)
    
    def test_tinted_lenses_detection(self):
        """Test tinted lenses detection"""
        # Set up mocks for tinted lenses
        self.mock_face_features.glasses_detected = True
        
        # Create image with tinted eye regions (darker/more saturated)
        tinted_image = self.test_image.copy()
        # Make eye regions darker to simulate tinted lenses
        cv2.circle(tinted_image, (180, 250), 15, (100, 100, 150), -1)  # Tinted left eye area
        cv2.circle(tinted_image, (220, 250), 15, (100, 100, 150), -1)  # Tinted right eye area
        
        # Test detection
        tinted_detected = self.validator._detect_tinted_lenses(tinted_image, self.mock_face_features)
        
        # Should detect tinted lenses due to color difference
        self.assertTrue(tinted_detected)
    
    def test_heavy_frames_detection(self):
        """Test heavy frames detection"""
        # Set up mocks
        self.mock_face_features.glasses_detected = True
        
        # Create image with heavy frames (high edge density around eyes)
        heavy_frames_image = self.test_image.copy()
        # Add thick black rectangles around eyes to simulate heavy frames
        cv2.rectangle(heavy_frames_image, (160, 235), (200, 265), (0, 0, 0), 3)  # Left frame
        cv2.rectangle(heavy_frames_image, (200, 235), (240, 265), (0, 0, 0), 3)  # Right frame
        
        # Test detection
        heavy_detected = self.validator._detect_heavy_frames(heavy_frames_image, self.mock_face_features)
        
        # Should detect heavy frames due to high edge density
        self.assertTrue(heavy_detected)
    
    def test_glare_detection(self):
        """Test glare detection on glasses"""
        # Set up mocks
        self.mock_face_features.glasses_detected = True
        
        # Create image with glare (bright spots on eye regions)
        glare_image = self.test_image.copy()
        # Add bright spots to simulate glare
        cv2.circle(glare_image, (175, 245), 8, (255, 255, 255), -1)  # Glare on left lens
        cv2.circle(glare_image, (225, 245), 8, (255, 255, 255), -1)  # Glare on right lens
        
        # Test detection
        glare_intensity = self.validator._detect_glasses_glare(glare_image, self.mock_face_features)
        
        # Should detect significant glare
        self.assertGreater(glare_intensity, 0.1)
    
    def test_head_covering_compliance_no_covering(self):
        """Test head covering compliance when no covering detected"""
        # Set up mocks
        self.mock_face_features.head_covering_detected = False
        
        # Test validation
        result = self.validator.validate_head_covering_compliance(self.test_image, self.mock_face_features)
        
        # Assertions
        self.assertIsInstance(result, HeadCoveringResult)
        self.assertFalse(result.head_covering_detected)
        self.assertFalse(result.is_religious_covering)
        self.assertIsInstance(result.required_features_visible, dict)
    
    def test_head_covering_compliance_religious(self):
        """Test head covering compliance with religious covering"""
        # Set up mocks
        self.mock_face_features.head_covering_detected = True
        
        # Mock religious covering classification
        with patch.object(self.validator, '_classify_head_covering_type', return_value=True):
            result = self.validator.validate_head_covering_compliance(self.test_image, self.mock_face_features)
        
        # Assertions
        self.assertIsInstance(result, HeadCoveringResult)
        self.assertTrue(result.head_covering_detected)
        self.assertTrue(result.is_religious_covering)
    
    def test_expression_compliance_neutral(self):
        """Test expression compliance with neutral expression"""
        # Set up mocks for neutral expression
        self.mock_face_features.mouth_openness = 0.05  # Closed mouth
        self.mock_face_features.eye_openness = (0.9, 0.9)  # Open eyes
        
        # Test validation
        result = self.validator.validate_expression_compliance(self.mock_face_features)
        
        # Assertions
        self.assertIsInstance(result, ExpressionResult)
        self.assertTrue(result.neutral_expression)
        self.assertTrue(result.eyes_open)
        self.assertGreater(result.expression_score, 80)  # Should have high score
    
    def test_expression_compliance_smile_detected(self):
        """Test expression compliance with smile detected"""
        # Set up mocks for smile
        self.mock_face_features.mouth_openness = 0.3  # Open mouth (smile)
        
        # Mock smile detection
        with patch.object(self.validator, '_detect_smile', return_value=0.8):
            result = self.validator.validate_expression_compliance(self.mock_face_features)
        
        # Should fail neutral expression requirement
        self.assertFalse(result.neutral_expression)
        self.assertIn("neutral expression", " ".join(result.suggestions).lower())
    
    def test_gaze_deviation_calculation(self):
        """Test gaze deviation calculation"""
        # Test direct gaze (no deviation)
        self.mock_face_features.face_orientation = {'yaw': 0.0, 'pitch': 0.0, 'roll': 0.0}
        
        deviation = self.validator._calculate_gaze_deviation(self.mock_face_features)
        self.assertEqual(deviation, 0.0)
        
        # Test with deviation
        self.mock_face_features.face_orientation = {'yaw': 3.0, 'pitch': 4.0, 'roll': 0.0}
        
        deviation = self.validator._calculate_gaze_deviation(self.mock_face_features)
        self.assertAlmostEqual(deviation, 5.0, places=1)  # sqrt(3^2 + 4^2) = 5
    
    def test_photo_quality_compliance(self):
        """Test photo quality compliance validation"""
        # Set up mock quality results
        mock_brightness_result = Mock()
        mock_brightness_result.passes_threshold = True
        mock_brightness_result.suggestions = []
        
        mock_blur_result = Mock()
        mock_blur_result.laplacian_variance = 150  # Above threshold
        mock_blur_result.suggestions = []
        
        mock_contrast_result = Mock()
        mock_contrast_result.passes_threshold = True
        mock_contrast_result.contrast_score = 40
        mock_contrast_result.suggestions = []
        
        mock_color_result = Mock()
        mock_color_result.color_cast_detected = False
        mock_color_result.suggestions = []
        
        # Set up quality checker mocks
        self.mock_quality_checker.check_brightness.return_value = mock_brightness_result
        self.mock_quality_checker.detect_blur.return_value = mock_blur_result
        self.mock_quality_checker.validate_contrast.return_value = mock_contrast_result
        self.mock_quality_checker.check_color_accuracy.return_value = mock_color_result
        
        # Test validation
        result = self.validator.validate_photo_quality_compliance(self.test_image, Mock())
        
        # Assertions
        self.assertIsInstance(result, PhotoQualityResult)
        self.assertGreater(result.sharpness_score, 100)  # Should exceed minimum
        self.assertEqual(result.lighting_score, 100)  # Should pass
        self.assertGreater(result.overall_quality_score, 80)  # Should have high overall score
    
    def test_style_lighting_compliance(self):
        """Test style and lighting compliance validation"""
        # Test validation
        result = self.validator.validate_style_and_lighting(self.test_image, self.mock_face_features)
        
        # Assertions
        self.assertIsInstance(result, StyleLightingResult)
        self.assertIsInstance(result.background_compliant, bool)
        self.assertIsInstance(result.shadows_acceptable, bool)
        self.assertIsInstance(result.flash_reflections_acceptable, bool)
        self.assertIsInstance(result.lighting_uniformity_score, float)
    
    def test_background_compliance_white(self):
        """Test background compliance with white background"""
        # Create image with white background
        white_bg_image = np.ones((400, 300, 3), dtype=np.uint8) * 255
        
        # Mock background rule
        mock_rule = Mock()
        mock_rule.parameters = {'required_color': 'white', 'color_tolerance': 10}
        
        # Test validation
        compliant = self.validator._validate_background_compliance(white_bg_image, mock_rule)
        
        # Should be compliant
        self.assertTrue(compliant)
    
    def test_background_compliance_non_white(self):
        """Test background compliance with non-white background"""
        # Create image with colored background
        colored_bg_image = np.ones((400, 300, 3), dtype=np.uint8)
        colored_bg_image[:, :] = [100, 150, 200]  # Blue-ish background
        
        # Mock background rule
        mock_rule = Mock()
        mock_rule.parameters = {'required_color': 'white', 'color_tolerance': 10}
        
        # Test validation
        compliant = self.validator._validate_background_compliance(colored_bg_image, mock_rule)
        
        # Should not be compliant
        self.assertFalse(compliant)
    
    def test_shadow_detection(self):
        """Test shadow detection on face and background"""
        # Create image with shadows (high gradient areas)
        shadow_image = self.test_image.copy()
        # Add gradient to simulate shadow
        for i in range(100, 200):
            for j in range(150, 250):
                shadow_image[i, j] = [int(255 * (i - 100) / 100), 
                                    int(255 * (i - 100) / 100), 
                                    int(255 * (i - 100) / 100)]
        
        # Test detection
        shadow_intensity = self.validator._detect_shadows(shadow_image, self.mock_face_features)
        
        # Should detect shadows due to gradient
        self.assertGreater(shadow_intensity, 0.1)
    
    def test_flash_reflection_detection(self):
        """Test flash reflection detection"""
        # Create image with flash reflections (very bright spots)
        flash_image = self.test_image.copy()
        # Add bright spots to simulate flash reflections
        cv2.circle(flash_image, (200, 200), 20, (255, 255, 255), -1)
        cv2.circle(flash_image, (300, 150), 15, (255, 255, 255), -1)
        
        # Test detection
        reflection_intensity = self.validator._detect_flash_reflections(flash_image, self.mock_face_features)
        
        # Should detect reflections
        self.assertGreater(reflection_intensity, 0.05)
    
    def test_red_eye_detection(self):
        """Test red-eye effect detection"""
        # Create image with red-eye effect
        red_eye_image = self.test_image.copy()
        # Make eye regions very red
        cv2.circle(red_eye_image, (180, 250), 8, (0, 0, 255), -1)  # Red left eye
        cv2.circle(red_eye_image, (220, 250), 8, (0, 0, 255), -1)  # Red right eye
        
        # Test detection
        red_eye_detected = self.validator._detect_red_eye(red_eye_image, self.mock_face_features)
        
        # Should detect red-eye
        self.assertTrue(red_eye_detected)
    
    def test_lighting_uniformity_calculation(self):
        """Test lighting uniformity calculation"""
        # Test uniform lighting
        uniform_image = np.ones((400, 300, 3), dtype=np.uint8) * 128
        uniformity = self.validator._calculate_lighting_uniformity(uniform_image, self.mock_face_features)
        self.assertGreater(uniformity, 0.9)  # Should be very uniform
        
        # Test non-uniform lighting
        non_uniform_image = np.ones((400, 300, 3), dtype=np.uint8)
        non_uniform_image[:200, :] = 50   # Dark top half
        non_uniform_image[200:, :] = 200  # Bright bottom half
        uniformity = self.validator._calculate_lighting_uniformity(non_uniform_image, self.mock_face_features)
        self.assertLess(uniformity, 0.5)  # Should be non-uniform
    
    def test_complete_compliance_validation(self):
        """Test complete ICAO compliance validation"""
        # Set up AI engine mocks
        self.mock_ai_engine.detect_faces.return_value = [self.mock_face_detection]
        self.mock_ai_engine.extract_face_features.return_value = self.mock_face_features
        self.mock_ai_engine.assess_image_quality.return_value = Mock()
        
        # Set up quality checker mocks
        self._setup_quality_checker_mocks()
        
        # Test complete validation
        result = self.validator.validate_complete_compliance(self.test_image)
        
        # Assertions
        self.assertIsInstance(result, ComplianceReport)
        self.assertIsInstance(result.overall_passes, bool)
        self.assertIsInstance(result.overall_score, float)
        self.assertIsInstance(result.glasses_result, GlassesResult)
        self.assertIsInstance(result.head_covering_result, HeadCoveringResult)
        self.assertIsInstance(result.expression_result, ExpressionResult)
        self.assertIsInstance(result.photo_quality_result, PhotoQualityResult)
        self.assertIsInstance(result.style_lighting_result, StyleLightingResult)
        self.assertIsInstance(result.all_rule_results, list)
        self.assertGreater(result.processing_time, 0)
    
    def test_no_face_detected_scenario(self):
        """Test validation when no face is detected"""
        # Set up AI engine to return no faces
        self.mock_ai_engine.detect_faces.return_value = []
        
        # Test validation
        result = self.validator.validate_complete_compliance(self.test_image)
        
        # Assertions
        self.assertIsInstance(result, ComplianceReport)
        self.assertFalse(result.overall_passes)
        self.assertEqual(result.overall_score, 0.0)
        self.assertGreater(len(result.critical_violations), 0)
        self.assertEqual(result.critical_violations[0].rule_id, "FACE_DETECTION")
    
    def test_country_variation_setting(self):
        """Test setting country-specific rule variations"""
        # Test setting country variation
        self.validator.validate_complete_compliance(self.test_image, country_variation="us_strict")
        
        # Verify rules engine was called with correct variation
        self.mock_rules_engine.set_country_variation.assert_called_with("us_strict")
    
    def test_rule_severity_categorization(self):
        """Test categorization of rule violations by severity"""
        # Set up mock rule results with different severities
        critical_rule = RuleResult(
            rule_id="CRITICAL.1", rule_name="critical", passes=False,
            measured_value=0, required_value=1, confidence=0.9,
            severity=RuleSeverity.CRITICAL, regulation_reference="Test",
            description="Critical violation", suggestion="Fix critical"
        )
        
        major_rule = RuleResult(
            rule_id="MAJOR.1", rule_name="major", passes=False,
            measured_value=0, required_value=1, confidence=0.8,
            severity=RuleSeverity.MAJOR, regulation_reference="Test",
            description="Major violation", suggestion="Fix major"
        )
        
        minor_rule = RuleResult(
            rule_id="MINOR.1", rule_name="minor", passes=False,
            measured_value=0, required_value=1, confidence=0.7,
            severity=RuleSeverity.MINOR, regulation_reference="Test",
            description="Minor violation", suggestion="Fix minor"
        )
        
        # Mock validation methods to return these results
        with patch.object(self.validator, 'validate_glasses_compliance') as mock_glasses, \
             patch.object(self.validator, 'validate_head_covering_compliance') as mock_head, \
             patch.object(self.validator, 'validate_expression_compliance') as mock_expr, \
             patch.object(self.validator, 'validate_photo_quality_compliance') as mock_quality, \
             patch.object(self.validator, 'validate_style_and_lighting') as mock_style:
            
            # Set up mock returns
            mock_glasses.return_value = GlassesResult(False, False, False, False, False, 0.0, [critical_rule], [])
            mock_head.return_value = HeadCoveringResult(False, False, False, 0.0, {}, [major_rule], [])
            mock_expr.return_value = ExpressionResult(False, False, False, False, False, False, 0.0, [minor_rule], [])
            mock_quality.return_value = PhotoQualityResult(True, 100, 100, 100, 100, 0.0, 100, [], [])
            mock_style.return_value = StyleLightingResult(True, True, True, True, False, 1.0, [], [])
            
            # Set up AI engine mocks
            self.mock_ai_engine.detect_faces.return_value = [self.mock_face_detection]
            self.mock_ai_engine.extract_face_features.return_value = self.mock_face_features
            self.mock_ai_engine.assess_image_quality.return_value = Mock()
            
            # Test validation
            result = self.validator.validate_complete_compliance(self.test_image)
            
            # Verify severity categorization
            self.assertEqual(len(result.critical_violations), 1)
            self.assertEqual(len(result.major_violations), 1)
            self.assertEqual(len(result.minor_violations), 1)
            self.assertEqual(result.critical_violations[0].rule_id, "CRITICAL.1")
            self.assertEqual(result.major_violations[0].rule_id, "MAJOR.1")
            self.assertEqual(result.minor_violations[0].rule_id, "MINOR.1")
    
    def _setup_quality_checker_mocks(self):
        """Set up quality checker mock returns"""
        mock_brightness = Mock()
        mock_brightness.passes_threshold = True
        mock_brightness.suggestions = []
        
        mock_blur = Mock()
        mock_blur.laplacian_variance = 150
        mock_blur.suggestions = []
        
        mock_contrast = Mock()
        mock_contrast.passes_threshold = True
        mock_contrast.contrast_score = 40
        mock_contrast.suggestions = []
        
        mock_color = Mock()
        mock_color.color_cast_detected = False
        mock_color.suggestions = []
        
        self.mock_quality_checker.check_brightness.return_value = mock_brightness
        self.mock_quality_checker.detect_blur.return_value = mock_blur
        self.mock_quality_checker.validate_contrast.return_value = mock_contrast
        self.mock_quality_checker.check_color_accuracy.return_value = mock_color


class TestICAOValidatorIntegration(unittest.TestCase):
    """Integration tests for ICAO Validator with real components"""
    
    def setUp(self):
        """Set up integration test fixtures"""
        # Create real validator with real components
        self.validator = ICAOValidator()
        
        # Create test images
        self.compliant_image = self._create_compliant_test_image()
        self.non_compliant_image = self._create_non_compliant_test_image()
    
    def _create_compliant_test_image(self) -> np.ndarray:
        """Create a test image that should pass ICAO compliance"""
        # Create white background image
        image = np.ones((600, 400, 3), dtype=np.uint8) * 255
        
        # Add realistic face
        face_color = (200, 180, 160)  # Skin tone
        cv2.ellipse(image, (200, 300), (60, 80), 0, 0, 360, face_color, -1)
        
        # Add eyes
        cv2.circle(image, (180, 280), 8, (50, 50, 50), -1)  # Left eye
        cv2.circle(image, (220, 280), 8, (50, 50, 50), -1)  # Right eye
        
        # Add nose
        cv2.ellipse(image, (200, 300), (5, 15), 0, 0, 360, (180, 160, 140), -1)
        
        # Add mouth
        cv2.ellipse(image, (200, 330), (15, 5), 0, 0, 360, (150, 100, 100), -1)
        
        return image
    
    def _create_non_compliant_test_image(self) -> np.ndarray:
        """Create a test image that should fail ICAO compliance"""
        # Create colored background (non-compliant)
        image = np.ones((600, 400, 3), dtype=np.uint8)
        image[:, :] = [100, 150, 200]  # Blue background
        
        # Add face with issues
        face_color = (200, 180, 160)
        cv2.ellipse(image, (200, 300), (60, 80), 15, 0, 360, face_color, -1)  # Tilted face
        
        # Add partially closed eyes (non-compliant)
        cv2.ellipse(image, (180, 280), (8, 3), 0, 0, 360, (50, 50, 50), -1)  # Squinting left eye
        cv2.ellipse(image, (220, 280), (8, 3), 0, 0, 360, (50, 50, 50), -1)  # Squinting right eye
        
        # Add open mouth (non-compliant)
        cv2.ellipse(image, (200, 330), (15, 10), 0, 0, 360, (100, 50, 50), -1)
        
        return image
    
    @unittest.skip("Requires real AI models - enable for full integration testing")
    def test_compliant_image_validation(self):
        """Test validation of compliant image"""
        result = self.validator.validate_complete_compliance(self.compliant_image)
        
        # Should pass most checks (may fail on AI detection due to simple test image)
        self.assertIsInstance(result, ComplianceReport)
        self.assertGreater(result.overall_score, 50)  # Should have reasonable score
    
    @unittest.skip("Requires real AI models - enable for full integration testing")
    def test_non_compliant_image_validation(self):
        """Test validation of non-compliant image"""
        result = self.validator.validate_complete_compliance(self.non_compliant_image)
        
        # Should fail multiple checks
        self.assertIsInstance(result, ComplianceReport)
        self.assertFalse(result.overall_passes)
        self.assertGreater(len(result.all_rule_results), 0)


if __name__ == '__main__':
    unittest.main()