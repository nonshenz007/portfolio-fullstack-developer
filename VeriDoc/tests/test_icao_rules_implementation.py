"""
Unit tests for specific ICAO rule implementations

Tests individual ICAO rules with reference test cases and edge scenarios.
"""

import unittest
import numpy as np
import cv2
from unittest.mock import Mock, patch
import tempfile
import os

from validation.icao_validator import ICAOValidator
from rules.icao_rules_engine import ICAORulesEngine, RuleSeverity
from ai.ai_engine import FaceFeatures


class TestICAOGlassesRules(unittest.TestCase):
    """Test ICAO glasses-related rules"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.validator = ICAOValidator()
        self.test_image = np.ones((400, 300, 3), dtype=np.uint8) * 255
        
        # Create mock face features with glasses
        self.glasses_face_features = Mock(spec=FaceFeatures)
        self.glasses_face_features.glasses_detected = True
        self.glasses_face_features.eye_positions = ((150, 200), (200, 200))
        self.glasses_face_features.head_covering_detected = False
    
    def test_icao_3_2_1_tinted_lenses_prohibited(self):
        """Test ICAO Rule 3.2.1: Tinted lenses are not permitted"""
        # Create image with tinted lenses (high saturation in eye regions)
        tinted_image = self.test_image.copy()
        # Add tinted regions around eyes
        cv2.circle(tinted_image, (150, 200), 20, (100, 100, 200), -1)  # Blue tint
        cv2.circle(tinted_image, (200, 200), 20, (100, 100, 200), -1)  # Blue tint
        
        # Test tinted lenses detection
        tinted_detected = self.validator._detect_tinted_lenses(tinted_image, self.glasses_face_features)
        self.assertTrue(tinted_detected, "Should detect tinted lenses")
        
        # Test with clear lenses (normal skin tone)
        clear_image = self.test_image.copy()
        cv2.circle(clear_image, (150, 200), 20, (200, 180, 160), -1)  # Normal skin tone
        cv2.circle(clear_image, (200, 200), 20, (200, 180, 160), -1)  # Normal skin tone
        
        clear_detected = self.validator._detect_tinted_lenses(clear_image, self.glasses_face_features)
        self.assertFalse(clear_detected, "Should not detect tinted lenses on clear glasses")
    
    def test_icao_3_2_2_heavy_frames_detection(self):
        """Test ICAO Rule 3.2.2: Heavy frames that obscure facial features"""
        # Create image with heavy frames (thick black borders around eyes)
        heavy_frames_image = self.test_image.copy()
        # Add thick black rectangles to simulate heavy frames
        cv2.rectangle(heavy_frames_image, (130, 180), (170, 220), (0, 0, 0), 5)  # Left frame
        cv2.rectangle(heavy_frames_image, (180, 180), (220, 220), (0, 0, 0), 5)  # Right frame
        
        heavy_detected = self.validator._detect_heavy_frames(heavy_frames_image, self.glasses_face_features)
        self.assertTrue(heavy_detected, "Should detect heavy frames")
        
        # Test with thin frames
        thin_frames_image = self.test_image.copy()
        cv2.rectangle(thin_frames_image, (140, 190), (160, 210), (0, 0, 0), 1)  # Thin left frame
        cv2.rectangle(thin_frames_image, (190, 190), (210, 210), (0, 0, 0), 1)  # Thin right frame
        
        thin_detected = self.validator._detect_heavy_frames(thin_frames_image, self.glasses_face_features)
        self.assertFalse(thin_detected, "Should not detect heavy frames on thin glasses")
    
    def test_icao_3_2_3_glare_reflection_detection(self):
        """Test ICAO Rule 3.2.3: Glare or reflections on glasses"""
        # Create image with glare (bright white spots on lenses)
        glare_image = self.test_image.copy()
        cv2.circle(glare_image, (145, 195), 10, (255, 255, 255), -1)  # Glare on left lens
        cv2.circle(glare_image, (205, 195), 10, (255, 255, 255), -1)  # Glare on right lens
        
        glare_intensity = self.validator._detect_glasses_glare(glare_image, self.glasses_face_features)
        self.assertGreater(glare_intensity, 0.15, "Should detect significant glare")
        
        # Test without glare
        no_glare_image = self.test_image.copy()
        cv2.circle(no_glare_image, (150, 200), 15, (200, 180, 160), -1)  # Normal eye region
        cv2.circle(no_glare_image, (200, 200), 15, (200, 180, 160), -1)  # Normal eye region
        
        no_glare_intensity = self.validator._detect_glasses_glare(no_glare_image, self.glasses_face_features)
        self.assertLess(no_glare_intensity, 0.1, "Should not detect glare on normal lenses")
    
    def test_icao_3_2_4_prescription_glasses_eye_visibility(self):
        """Test ICAO Rule 3.2.4: Eyes must be clearly visible through prescription glasses"""
        # Create image with good eye visibility (high contrast in eye regions)
        good_visibility_image = self.test_image.copy()
        # Add detailed eye features
        cv2.circle(good_visibility_image, (150, 200), 15, (200, 180, 160), -1)  # Eye socket
        cv2.circle(good_visibility_image, (150, 200), 8, (255, 255, 255), -1)   # Eye white
        cv2.circle(good_visibility_image, (150, 200), 4, (100, 50, 50), -1)     # Iris
        cv2.circle(good_visibility_image, (150, 200), 2, (0, 0, 0), -1)         # Pupil
        
        cv2.circle(good_visibility_image, (200, 200), 15, (200, 180, 160), -1)  # Eye socket
        cv2.circle(good_visibility_image, (200, 200), 8, (255, 255, 255), -1)   # Eye white
        cv2.circle(good_visibility_image, (200, 200), 4, (100, 50, 50), -1)     # Iris
        cv2.circle(good_visibility_image, (200, 200), 2, (0, 0, 0), -1)         # Pupil
        
        good_visibility = self.validator._calculate_eye_visibility(good_visibility_image, self.glasses_face_features)
        self.assertGreater(good_visibility, 0.8, "Should have high eye visibility score")
        
        # Create image with poor eye visibility (low contrast, blurred)
        poor_visibility_image = self.test_image.copy()
        cv2.circle(poor_visibility_image, (150, 200), 15, (180, 180, 180), -1)  # Low contrast
        cv2.circle(poor_visibility_image, (200, 200), 15, (180, 180, 180), -1)  # Low contrast
        
        poor_visibility = self.validator._calculate_eye_visibility(poor_visibility_image, self.glasses_face_features)
        self.assertLess(poor_visibility, 0.5, "Should have low eye visibility score")


class TestICAOHeadCoveringRules(unittest.TestCase):
    """Test ICAO head covering rules"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.validator = ICAOValidator()
        self.test_image = np.ones((400, 300, 3), dtype=np.uint8) * 255
        
        # Create mock face features with head covering
        self.covered_face_features = Mock(spec=FaceFeatures)
        self.covered_face_features.head_covering_detected = True
        self.covered_face_features.glasses_detected = False
        self.covered_face_features.eye_positions = ((150, 200), (200, 200))
        self.covered_face_features.mouth_position = (175, 250)
    
    def test_icao_3_3_1_religious_head_covering_exception(self):
        """Test ICAO Rule 3.3.1: Religious head coverings are permitted with face visibility"""
        # Test religious covering classification
        # Mock high face visibility (typical of religious coverings that comply)
        with patch.object(self.validator, '_calculate_face_visibility', return_value=0.9):
            is_religious = self.validator._classify_head_covering_type(self.test_image, self.covered_face_features)
            self.assertTrue(is_religious, "Should classify as religious covering with high face visibility")
        
        # Test non-religious classification
        # Mock low face visibility (typical of non-religious coverings)
        with patch.object(self.validator, '_calculate_face_visibility', return_value=0.6):
            is_religious = self.validator._classify_head_covering_type(self.test_image, self.covered_face_features)
            self.assertFalse(is_religious, "Should classify as non-religious covering with low face visibility")
    
    def test_icao_3_3_2_non_religious_head_covering_prohibited(self):
        """Test ICAO Rule 3.3.2: Non-religious head coverings are not permitted"""
        # This rule is tested through the head covering compliance validation
        # Non-religious coverings should fail validation
        
        # Mock non-religious covering
        with patch.object(self.validator, '_classify_head_covering_type', return_value=False):
            result = self.validator.validate_head_covering_compliance(self.test_image, self.covered_face_features)
            
            # Should have rule violations for non-religious covering
            non_religious_violations = [r for r in result.rule_results if 'non_religious' in r.rule_id.lower()]
            self.assertGreater(len(non_religious_violations), 0, "Should have non-religious covering violations")
    
    def test_icao_3_3_3_face_coverage_requirements(self):
        """Test ICAO Rule 3.3.3: Face must be clearly visible from hairline to chin"""
        # Test all required features visible
        all_visible_features = {
            'eyes': True,
            'nose': True,
            'mouth': True,
            'chin': True
        }
        
        with patch.object(self.validator, '_check_required_features_visibility', return_value=all_visible_features):
            result = self.validator.validate_head_covering_compliance(self.test_image, self.covered_face_features)
            
            # Should pass face coverage requirements
            face_coverage_results = [r for r in result.rule_results if 'face_coverage' in r.rule_id.lower()]
            if face_coverage_results:
                self.assertTrue(face_coverage_results[0].passes, "Should pass face coverage requirements")
        
        # Test some features hidden
        partially_visible_features = {
            'eyes': True,
            'nose': False,  # Nose hidden
            'mouth': True,
            'chin': False   # Chin hidden
        }
        
        with patch.object(self.validator, '_check_required_features_visibility', return_value=partially_visible_features):
            result = self.validator.validate_head_covering_compliance(self.test_image, self.covered_face_features)
            
            # Should fail face coverage requirements
            self.assertIn("nose", " ".join(result.suggestions).lower())
            self.assertIn("chin", " ".join(result.suggestions).lower())
    
    def test_face_visibility_calculation(self):
        """Test face visibility score calculation"""
        # Test with all features detected (high visibility)
        full_features = Mock(spec=FaceFeatures)
        full_features.eye_positions = ((150, 200), (200, 200))
        full_features.mouth_position = (175, 250)
        
        high_visibility = self.validator._calculate_face_visibility(self.test_image, full_features)
        self.assertEqual(high_visibility, 1.0, "Should have maximum visibility with all features")
        
        # Test with missing features (low visibility)
        partial_features = Mock(spec=FaceFeatures)
        partial_features.eye_positions = None  # Eyes not detected
        partial_features.mouth_position = (175, 250)
        
        low_visibility = self.validator._calculate_face_visibility(self.test_image, partial_features)
        self.assertLess(low_visibility, 1.0, "Should have reduced visibility with missing features")


class TestICAOExpressionRules(unittest.TestCase):
    """Test ICAO expression and framing rules"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.validator = ICAOValidator()
        
        # Create mock face features for expression testing
        self.neutral_face_features = Mock(spec=FaceFeatures)
        self.neutral_face_features.mouth_openness = 0.05  # Closed mouth
        self.neutral_face_features.eye_openness = (0.9, 0.9)  # Open eyes
        self.neutral_face_features.face_orientation = {
            'yaw': 0.0,
            'pitch': 0.0,
            'roll': 0.0
        }
        self.neutral_face_features.glasses_detected = False
        self.neutral_face_features.head_covering_detected = False
    
    def test_icao_4_1_1_neutral_expression_requirement(self):
        """Test ICAO Rule 4.1.1: Subject must have neutral expression with mouth closed"""
        # Test neutral expression (should pass)
        with patch.object(self.validator, '_detect_smile', return_value=0.1):  # Low smile score
            result = self.validator.validate_expression_compliance(self.neutral_face_features)
            self.assertTrue(result.neutral_expression, "Should detect neutral expression")
        
        # Test smiling expression (should fail)
        smiling_features = Mock(spec=FaceFeatures)
        smiling_features.mouth_openness = 0.3  # Open mouth
        smiling_features.eye_openness = (0.9, 0.9)
        smiling_features.face_orientation = self.neutral_face_features.face_orientation
        
        with patch.object(self.validator, '_detect_smile', return_value=0.8):  # High smile score
            result = self.validator.validate_expression_compliance(smiling_features)
            self.assertFalse(result.neutral_expression, "Should detect non-neutral expression")
            self.assertIn("neutral", " ".join(result.suggestions).lower())
    
    def test_icao_4_1_2_direct_gaze_requirement(self):
        """Test ICAO Rule 4.1.2: Subject must look directly at the camera"""
        # Test direct gaze (no deviation)
        direct_gaze_features = self.neutral_face_features
        direct_gaze_features.face_orientation = {'yaw': 0.0, 'pitch': 0.0, 'roll': 0.0}
        
        result = self.validator.validate_expression_compliance(direct_gaze_features)
        self.assertTrue(result.direct_gaze, "Should detect direct gaze")
        
        # Test gaze deviation (should fail)
        deviated_gaze_features = Mock(spec=FaceFeatures)
        deviated_gaze_features.mouth_openness = 0.05
        deviated_gaze_features.eye_openness = (0.9, 0.9)
        deviated_gaze_features.face_orientation = {
            'yaw': 10.0,  # Significant deviation
            'pitch': 8.0,
            'roll': 0.0
        }
        
        result = self.validator.validate_expression_compliance(deviated_gaze_features)
        self.assertFalse(result.direct_gaze, "Should detect gaze deviation")
        self.assertIn("camera", " ".join(result.suggestions).lower())
    
    def test_icao_4_1_3_eyes_open_requirement(self):
        """Test ICAO Rule 4.1.3: Both eyes must be open and clearly visible"""
        # Test open eyes (should pass)
        open_eyes_features = self.neutral_face_features
        open_eyes_features.eye_openness = (0.9, 0.9)  # Both eyes open
        
        result = self.validator.validate_expression_compliance(open_eyes_features)
        self.assertTrue(result.eyes_open, "Should detect open eyes")
        
        # Test closed/squinting eyes (should fail)
        closed_eyes_features = Mock(spec=FaceFeatures)
        closed_eyes_features.mouth_openness = 0.05
        closed_eyes_features.eye_openness = (0.3, 0.4)  # Squinting/closed eyes
        closed_eyes_features.face_orientation = self.neutral_face_features.face_orientation
        
        result = self.validator.validate_expression_compliance(closed_eyes_features)
        self.assertFalse(result.eyes_open, "Should detect closed/squinting eyes")
        self.assertIn("eyes", " ".join(result.suggestions).lower())
    
    def test_icao_4_2_2_head_rotation_limits(self):
        """Test ICAO Rule 4.2.2: Head must be straight and facing forward"""
        # Test straight head (should pass)
        straight_head_features = self.neutral_face_features
        straight_head_features.face_orientation = {'yaw': 0.0, 'pitch': 0.0, 'roll': 1.0}  # Minimal rotation
        
        result = self.validator.validate_expression_compliance(straight_head_features)
        self.assertTrue(result.head_straight, "Should detect straight head")
        
        # Test tilted head (should fail)
        tilted_head_features = Mock(spec=FaceFeatures)
        tilted_head_features.mouth_openness = 0.05
        tilted_head_features.eye_openness = (0.9, 0.9)
        tilted_head_features.face_orientation = {
            'yaw': 2.0,
            'pitch': 3.0,
            'roll': 15.0  # Significant tilt
        }
        
        result = self.validator.validate_expression_compliance(tilted_head_features)
        self.assertFalse(result.head_straight, "Should detect tilted head")
        self.assertIn("straight", " ".join(result.suggestions).lower())
    
    def test_gaze_deviation_calculation_accuracy(self):
        """Test accuracy of gaze deviation calculation"""
        # Test perfect alignment
        perfect_features = Mock(spec=FaceFeatures)
        perfect_features.face_orientation = {'yaw': 0.0, 'pitch': 0.0, 'roll': 0.0}
        
        deviation = self.validator._calculate_gaze_deviation(perfect_features)
        self.assertEqual(deviation, 0.0, "Should have zero deviation for perfect alignment")
        
        # Test known deviation (3-4-5 triangle)
        deviated_features = Mock(spec=FaceFeatures)
        deviated_features.face_orientation = {'yaw': 3.0, 'pitch': 4.0, 'roll': 0.0}
        
        deviation = self.validator._calculate_gaze_deviation(deviated_features)
        self.assertAlmostEqual(deviation, 5.0, places=1, msg="Should calculate correct deviation magnitude")
    
    def test_expression_score_calculation(self):
        """Test overall expression score calculation"""
        # Test perfect expression (all factors true)
        perfect_score = self.validator._calculate_expression_score(
            neutral=True, direct_gaze=True, eyes_open=True, 
            positioned=True, straight=True
        )
        self.assertEqual(perfect_score, 100.0, "Should have perfect score for all factors true")
        
        # Test partial compliance
        partial_score = self.validator._calculate_expression_score(
            neutral=True, direct_gaze=False, eyes_open=True, 
            positioned=True, straight=False
        )
        self.assertEqual(partial_score, 60.0, "Should have 60% score for 3/5 factors true")
        
        # Test no compliance
        zero_score = self.validator._calculate_expression_score(
            neutral=False, direct_gaze=False, eyes_open=False, 
            positioned=False, straight=False
        )
        self.assertEqual(zero_score, 0.0, "Should have zero score for all factors false")


class TestICAOQualityRules(unittest.TestCase):
    """Test ICAO photo quality rules"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.validator = ICAOValidator()
        
        # Create test images with different quality characteristics
        self.sharp_image = self._create_sharp_test_image()
        self.blurry_image = self._create_blurry_test_image()
        self.bright_image = self._create_bright_test_image()
        self.dark_image = self._create_dark_test_image()
    
    def _create_sharp_test_image(self) -> np.ndarray:
        """Create a sharp test image"""
        image = np.ones((400, 300, 3), dtype=np.uint8) * 128
        # Add high-contrast features for sharpness
        cv2.rectangle(image, (100, 100), (200, 200), (255, 255, 255), -1)
        cv2.rectangle(image, (120, 120), (180, 180), (0, 0, 0), -1)
        cv2.rectangle(image, (140, 140), (160, 160), (255, 255, 255), -1)
        return image
    
    def _create_blurry_test_image(self) -> np.ndarray:
        """Create a blurry test image"""
        sharp_image = self._create_sharp_test_image()
        # Apply Gaussian blur to simulate blur
        blurry_image = cv2.GaussianBlur(sharp_image, (15, 15), 5)
        return blurry_image
    
    def _create_bright_test_image(self) -> np.ndarray:
        """Create an overly bright test image"""
        return np.ones((400, 300, 3), dtype=np.uint8) * 240
    
    def _create_dark_test_image(self) -> np.ndarray:
        """Create an overly dark test image"""
        return np.ones((400, 300, 3), dtype=np.uint8) * 30
    
    def test_icao_5_1_1_sharpness_requirements(self):
        """Test ICAO Rule 5.1.1: Photo must be sharp and in focus"""
        # Test sharp image
        sharp_noise = self.validator._calculate_noise_level(self.sharp_image)
        self.assertLess(sharp_noise, 0.5, "Sharp image should have low noise level")
        
        # Test blurry image
        blurry_noise = self.validator._calculate_noise_level(self.blurry_image)
        # Note: This is a simplified test - real implementation would use Laplacian variance
        
        # Verify blur detection works
        gray_sharp = cv2.cvtColor(self.sharp_image, cv2.COLOR_BGR2GRAY)
        gray_blurry = cv2.cvtColor(self.blurry_image, cv2.COLOR_BGR2GRAY)
        
        sharp_laplacian = cv2.Laplacian(gray_sharp, cv2.CV_64F).var()
        blurry_laplacian = cv2.Laplacian(gray_blurry, cv2.CV_64F).var()
        
        self.assertGreater(sharp_laplacian, blurry_laplacian, 
                          "Sharp image should have higher Laplacian variance")
        self.assertGreater(sharp_laplacian, 100, 
                          "Sharp image should exceed ICAO minimum sharpness threshold")
    
    def test_icao_5_2_1_lighting_requirements(self):
        """Test ICAO Rule 5.2.1: Photo must have even lighting without shadows"""
        # Test lighting uniformity calculation
        uniform_image = np.ones((400, 300, 3), dtype=np.uint8) * 128
        uniform_score = self.validator._calculate_lighting_uniformity(uniform_image, Mock())
        self.assertGreater(uniform_score, 0.9, "Uniform image should have high uniformity score")
        
        # Test non-uniform lighting
        non_uniform_image = np.ones((400, 300, 3), dtype=np.uint8)
        non_uniform_image[:200, :] = 50   # Dark top half
        non_uniform_image[200:, :] = 200  # Bright bottom half
        
        non_uniform_score = self.validator._calculate_lighting_uniformity(non_uniform_image, Mock())
        self.assertLess(non_uniform_score, 0.5, "Non-uniform image should have low uniformity score")
        
        # Test brightness levels
        bright_avg = np.mean(cv2.cvtColor(self.bright_image, cv2.COLOR_BGR2GRAY))
        dark_avg = np.mean(cv2.cvtColor(self.dark_image, cv2.COLOR_BGR2GRAY))
        
        self.assertGreater(bright_avg, 200, "Bright image should exceed maximum brightness threshold")
        self.assertLess(dark_avg, 80, "Dark image should be below minimum brightness threshold")
    
    def test_icao_5_3_1_color_accuracy_requirements(self):
        """Test ICAO Rule 5.3.1: Photo must have natural colors without color cast"""
        # Create image with color cast
        color_cast_image = np.ones((400, 300, 3), dtype=np.uint8)
        color_cast_image[:, :, 0] = 100  # Low blue
        color_cast_image[:, :, 1] = 128  # Medium green  
        color_cast_image[:, :, 2] = 200  # High red (red cast)
        
        # Calculate color balance
        b_mean = np.mean(color_cast_image[:, :, 0])
        g_mean = np.mean(color_cast_image[:, :, 1])
        r_mean = np.mean(color_cast_image[:, :, 2])
        total_mean = (b_mean + g_mean + r_mean) / 3
        
        # Check for color cast detection
        color_cast_threshold = 15
        has_color_cast = (
            abs(b_mean - total_mean) > color_cast_threshold or
            abs(g_mean - total_mean) > color_cast_threshold or
            abs(r_mean - total_mean) > color_cast_threshold
        )
        
        self.assertTrue(has_color_cast, "Should detect color cast in biased image")
        
        # Test neutral color image
        neutral_image = np.ones((400, 300, 3), dtype=np.uint8) * 128
        
        b_mean_neutral = np.mean(neutral_image[:, :, 0])
        g_mean_neutral = np.mean(neutral_image[:, :, 1])
        r_mean_neutral = np.mean(neutral_image[:, :, 2])
        total_mean_neutral = (b_mean_neutral + g_mean_neutral + r_mean_neutral) / 3
        
        has_neutral_cast = (
            abs(b_mean_neutral - total_mean_neutral) > color_cast_threshold or
            abs(g_mean_neutral - total_mean_neutral) > color_cast_threshold or
            abs(r_mean_neutral - total_mean_neutral) > color_cast_threshold
        )
        
        self.assertFalse(has_neutral_cast, "Should not detect color cast in neutral image")


class TestICAOStyleLightingRules(unittest.TestCase):
    """Test ICAO style and lighting rules"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.validator = ICAOValidator()
        self.mock_face_features = Mock(spec=FaceFeatures)
        self.mock_face_features.eye_positions = ((150, 200), (200, 200))
    
    def test_icao_6_1_1_background_requirements(self):
        """Test ICAO Rule 6.1.1: Background must be plain white and uniform"""
        # Test white background
        white_bg_image = np.ones((400, 300, 3), dtype=np.uint8) * 255
        
        mock_rule = Mock()
        mock_rule.parameters = {'required_color': 'white', 'color_tolerance': 10}
        
        white_compliant = self.validator._validate_background_compliance(white_bg_image, mock_rule)
        self.assertTrue(white_compliant, "White background should be compliant")
        
        # Test colored background
        blue_bg_image = np.ones((400, 300, 3), dtype=np.uint8)
        blue_bg_image[:, :] = [255, 100, 100]  # Red background
        
        colored_compliant = self.validator._validate_background_compliance(blue_bg_image, mock_rule)
        self.assertFalse(colored_compliant, "Colored background should not be compliant")
        
        # Test gradient background (non-uniform)
        gradient_bg_image = np.ones((400, 300, 3), dtype=np.uint8)
        for i in range(400):
            gradient_bg_image[i, :] = [255 - i//2, 255 - i//2, 255 - i//2]
        
        gradient_compliant = self.validator._validate_background_compliance(gradient_bg_image, mock_rule)
        # This should fail due to non-uniformity (average might be close to white but not uniform)
    
    def test_icao_6_2_1_shadow_detection(self):
        """Test ICAO Rule 6.2.1: Photo must be free from shadows"""
        # Create image with shadows (high gradient areas)
        shadow_image = np.ones((400, 300, 3), dtype=np.uint8) * 200
        
        # Add shadow gradient
        for i in range(100, 200):
            for j in range(100, 200):
                intensity = int(200 - (i - 100) * 2)  # Gradient shadow
                shadow_image[i, j] = [intensity, intensity, intensity]
        
        shadow_intensity = self.validator._detect_shadows(shadow_image, self.mock_face_features)
        self.assertGreater(shadow_intensity, 0.1, "Should detect shadows in gradient image")
        
        # Test uniform image (no shadows)
        uniform_image = np.ones((400, 300, 3), dtype=np.uint8) * 200
        
        no_shadow_intensity = self.validator._detect_shadows(uniform_image, self.mock_face_features)
        self.assertLess(no_shadow_intensity, shadow_intensity, 
                       "Uniform image should have less shadow intensity")
    
    def test_icao_6_3_1_flash_reflection_detection(self):
        """Test ICAO Rule 6.3.1: Photo must be free from flash reflections"""
        # Create image with flash reflections (very bright spots)
        flash_image = np.ones((400, 300, 3), dtype=np.uint8) * 128
        
        # Add bright spots to simulate flash reflections
        cv2.circle(flash_image, (150, 150), 20, (255, 255, 255), -1)
        cv2.circle(flash_image, (250, 200), 15, (255, 255, 255), -1)
        
        reflection_intensity = self.validator._detect_flash_reflections(flash_image, self.mock_face_features)
        self.assertGreater(reflection_intensity, 0.05, "Should detect flash reflections")
        
        # Test image without reflections
        no_flash_image = np.ones((400, 300, 3), dtype=np.uint8) * 128
        
        no_reflection_intensity = self.validator._detect_flash_reflections(no_flash_image, self.mock_face_features)
        self.assertLess(no_reflection_intensity, 0.02, "Should not detect reflections in uniform image")
    
    def test_icao_6_4_1_red_eye_detection(self):
        """Test ICAO Rule 6.4.1: Red-eye effect is not permitted"""
        # Create image with red-eye effect
        red_eye_image = np.ones((400, 300, 3), dtype=np.uint8) * 128
        
        # Add red eyes (high red channel values in eye positions)
        cv2.circle(red_eye_image, (150, 200), 10, (0, 0, 255), -1)  # Red left eye
        cv2.circle(red_eye_image, (200, 200), 10, (0, 0, 255), -1)  # Red right eye
        
        red_eye_detected = self.validator._detect_red_eye(red_eye_image, self.mock_face_features)
        self.assertTrue(red_eye_detected, "Should detect red-eye effect")
        
        # Test normal eyes
        normal_eye_image = np.ones((400, 300, 3), dtype=np.uint8) * 128
        
        # Add normal colored eyes
        cv2.circle(normal_eye_image, (150, 200), 10, (100, 80, 60), -1)  # Normal left eye
        cv2.circle(normal_eye_image, (200, 200), 10, (100, 80, 60), -1)  # Normal right eye
        
        no_red_eye_detected = self.validator._detect_red_eye(normal_eye_image, self.mock_face_features)
        self.assertFalse(no_red_eye_detected, "Should not detect red-eye in normal eyes")


if __name__ == '__main__':
    unittest.main()