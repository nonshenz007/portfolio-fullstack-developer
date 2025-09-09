import unittest
import numpy as np
import cv2
from unittest.mock import Mock, patch, MagicMock
import json
import sys
import os

# Mock mediapipe at the module level to prevent actual import issues
# This is crucial for tests that don't explicitly patch it in each method
sys.modules['mediapipe'] = MagicMock()
sys.modules['mediapipe.solutions'] = MagicMock()
sys.modules['mediapipe.solutions.face_mesh'] = MagicMock()

from detection.data_models import Point, FacialLandmarks
from detection.face_detector import (
    FaceDetector, FacialLandmarks, FaceMetrics, CropBox, 
    ValidationResult
)


class TestFaceDetector(unittest.TestCase):
    """Test cases for FaceDetector class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Patch MediaPipe availability and FaceMesh
        self.mediapipe_patcher = patch('engine.face_detector.MEDIAPIPE_AVAILABLE', True)
        self.mp_patcher = patch('engine.face_detector.mp')
        
        self.mediapipe_patcher.start()
        mock_mp = self.mp_patcher.start()
        
        # Set up the mock structure
        self.mock_face_mesh_instance = Mock()
        mock_mp.solutions.face_mesh.FaceMesh.return_value = self.mock_face_mesh_instance
        
        self.detector = FaceDetector()
        
        # Sample format rules for testing
        self.sample_rules = {
            "dimensions": {
                "width": 600,
                "height": 600
            },
            "face_requirements": {
                "height_ratio": [0.70, 0.80],
                "eye_height_ratio": [0.50, 0.60],
                "centering_tolerance": 0.05
            }
        }
        
        # Create a simple test image (solid color)
        self.test_image = np.ones((400, 300, 3), dtype=np.uint8) * 128
        
        # Mock landmarks for testing
        self.mock_landmarks = self._create_mock_landmarks()
    
    def tearDown(self):
        """Clean up patches."""
        self.mediapipe_patcher.stop()
        self.mp_patcher.stop()
    
    def _create_mock_landmarks(self):
        """Create mock facial landmarks for testing."""
        landmarks = []
        # Create 478 landmarks (MediaPipe FaceMesh standard)
        for i in range(478):
            if i == 468:  # Left eye center
                landmarks.append(Point(x=120, y=150))
            elif i == 473:  # Right eye center
                landmarks.append(Point(x=180, y=150))
            elif i == 1:  # Nose tip
                landmarks.append(Point(x=150, y=180))
            elif i == 175:  # Chin bottom
                landmarks.append(Point(x=150, y=250))
            elif i == 10:  # Forehead top
                landmarks.append(Point(x=150, y=100))
            else:
                # Random points for other landmarks
                landmarks.append(Point(x=150 + (i % 50 - 25), y=150 + (i % 40 - 20)))
        
        return FacialLandmarks(
            landmarks=landmarks,
            face_detected=True,
            confidence_score=0.85,
            image_width=300,
            image_height=400
        )
    
    def test_face_detector_initialization(self):
        """Test FaceDetector initialization."""
        # This test should not be patched, as it tests the actual initialization
        # Temporarily unpatch FaceMesh for this test
        with patch('mediapipe.solutions.face_mesh.FaceMesh') as MockFaceMesh:
            MockFaceMesh.return_value = Mock() # Ensure a mock instance is returned
            detector = FaceDetector()
            self.assertIsNotNone(detector.face_mesh)
            self.assertIsNotNone(detector.mp_face_mesh)
            
            # Check landmark indices are set
            self.assertEqual(detector.LEFT_EYE_CENTER, 468)
            self.assertEqual(detector.RIGHT_EYE_CENTER, 473)
            self.assertEqual(detector.NOSE_TIP, 1)
            self.assertEqual(detector.CHIN_BOTTOM, 175)
            self.assertEqual(detector.FOREHEAD_TOP, 10)
    
    def test_detect_face_landmarks_success(self):
        """Test successful face landmark detection."""
        # Mock MediaPipe results
        mock_landmark = Mock(x=0.5, y=0.4, z=-0.3) # Directly set attributes
        mock_face_landmarks = Mock(landmark=[mock_landmark] * 478)
        mock_results = Mock(multi_face_landmarks=[mock_face_landmarks])
        
        self.mock_face_mesh_instance.process.return_value = mock_results # Set return value on the mocked instance
        
        # Test detection
        result = self.detector.detect_face_landmarks(self.test_image)
        
        self.assertTrue(result.face_detected)
        self.assertEqual(len(result.landmarks), 478)
        self.assertEqual(result.image_width, 300)
        self.assertEqual(result.image_height, 400)
        self.assertGreater(result.confidence_score, 0)
    
    def test_detect_face_landmarks_no_face(self):
        """Test face detection when no face is present."""
        mock_results = Mock(multi_face_landmarks=[]) # Empty list
        self.mock_face_mesh_instance.process.return_value = mock_results # Set return value on the mocked instance
        
        result = self.detector.detect_face_landmarks(self.test_image)
        
        self.assertFalse(result.face_detected)
        self.assertEqual(len(result.landmarks), 0)
        self.assertEqual(result.confidence_score, 0.0)
    
    def test_detect_face_landmarks_invalid_image(self):
        """Test face detection with invalid image input."""
        # Test with None image
        result = self.detector.detect_face_landmarks(None)
        self.assertFalse(result.face_detected)
        
        # Test with empty image
        empty_image = np.array([])
        result = self.detector.detect_face_landmarks(empty_image)
        self.assertFalse(result.face_detected)
    
    def test_calculate_face_metrics_success(self):
        """Test face metrics calculation with valid landmarks."""
        metrics = self.detector.calculate_face_metrics(self.mock_landmarks)
        
        self.assertTrue(metrics.face_detected)
        self.assertEqual(len(metrics.face_bounds), 4)
        self.assertIsInstance(metrics.eye_positions[0], Point)
        self.assertIsInstance(metrics.eye_positions[1], Point)
        self.assertGreater(metrics.face_height_ratio, 0)
        self.assertGreater(metrics.eye_height_ratio, 0)
        self.assertGreaterEqual(metrics.centering_offset, 0)
        self.assertGreater(metrics.confidence_score, 0)
    
    def test_calculate_face_metrics_no_face(self):
        """Test face metrics calculation when no face is detected."""
        no_face_landmarks = FaceLandmarks(
            landmarks=[],
            face_detected=False,
            confidence_score=0.0,
            image_width=300,
            image_height=400
        )
        
        metrics = self.detector.calculate_face_metrics(no_face_landmarks)
        
        self.assertFalse(metrics.face_detected)
        self.assertEqual(metrics.face_bounds, (0, 0, 0, 0))
        self.assertEqual(metrics.face_height_ratio, 0.0)
        self.assertEqual(metrics.eye_height_ratio, 0.0)
        self.assertEqual(metrics.centering_offset, 0.0)
        self.assertEqual(metrics.confidence_score, 0.0)
    
    def test_get_crop_boundaries_with_face(self):
        """Test crop boundary calculation with detected face."""
        crop_box = self.detector.get_crop_boundaries(
            self.test_image, self.mock_landmarks, self.sample_rules
        )
        
        self.assertIsInstance(crop_box, CropBox)
        self.assertGreaterEqual(crop_box.x, 0)
        self.assertGreaterEqual(crop_box.y, 0)
        self.assertGreater(crop_box.width, 0)
        self.assertGreater(crop_box.height, 0)
        
        # Ensure crop doesn't exceed image boundaries
        self.assertLessEqual(crop_box.x + crop_box.width, self.mock_landmarks.image_width)
        self.assertLessEqual(crop_box.y + crop_box.height, self.mock_landmarks.image_height)
    
    def test_get_crop_boundaries_no_face(self):
        """Test crop boundary calculation when no face is detected."""
        no_face_landmarks = FaceLandmarks(
            landmarks=[],
            face_detected=False,
            confidence_score=0.0,
            image_width=300,
            image_height=400
        )
        
        crop_box = self.detector.get_crop_boundaries(
            self.test_image, no_face_landmarks, self.sample_rules
        )
        
        self.assertIsInstance(crop_box, CropBox)
        self.assertGreaterEqual(crop_box.x, 0)
        self.assertGreaterEqual(crop_box.y, 0)
        self.assertGreater(crop_box.width, 0)
        self.assertGreater(crop_box.height, 0)
    
    def test_validate_face_positioning_valid(self):
        """Test face positioning validation with valid metrics."""
        # Create metrics that should pass validation
        valid_metrics = FaceMetrics(
            face_detected=True,
            face_bounds=(50, 50, 200, 300),
            eye_positions=(Point(120, 150), Point(180, 150)),
            face_height_ratio=0.75,  # Within range [0.70, 0.80]
            eye_height_ratio=0.55,   # Within range [0.50, 0.60]
            centering_offset=0.02,   # Within tolerance 0.05
            confidence_score=0.85
        )
        
        result = self.detector.validate_face_positioning(valid_metrics, self.sample_rules)
        
        self.assertIsInstance(result, ValidationResult)
        self.assertTrue(result.is_valid)
        self.assertEqual(len(result.issues), 0)
        self.assertEqual(len(result.suggestions), 0)
        self.assertEqual(result.metrics, valid_metrics)
    
    def test_validate_face_positioning_invalid_ratios(self):
        """Test face positioning validation with invalid ratios."""
        invalid_metrics = FaceMetrics(
            face_detected=True,
            face_bounds=(50, 50, 200, 300),
            eye_positions=(Point(120, 150), Point(180, 150)),
            face_height_ratio=0.60,  # Below range [0.70, 0.80]
            eye_height_ratio=0.70,   # Above range [0.50, 0.60]
            centering_offset=0.10,   # Above tolerance 0.05
            confidence_score=0.85
        )
        
        result = self.detector.validate_face_positioning(invalid_metrics, self.sample_rules)
        
        self.assertFalse(result.is_valid)
        self.assertGreater(len(result.issues), 0)
        self.assertGreater(len(result.suggestions), 0)
        
        # Check specific issues
        issues_text = ' '.join(result.issues)
        self.assertIn("Face too small", issues_text)
        self.assertIn("Eyes positioned too high", issues_text)
        self.assertIn("Face not centered", issues_text)
    
    def test_validate_face_positioning_no_face(self):
        """Test face positioning validation when no face is detected."""
        no_face_metrics = FaceMetrics(
            face_detected=False,
            face_bounds=(0, 0, 0, 0),
            eye_positions=(Point(0, 0), Point(0, 0)),
            face_height_ratio=0.0,
            eye_height_ratio=0.0,
            centering_offset=0.0,
            confidence_score=0.0
        )
        
        result = self.detector.validate_face_positioning(no_face_metrics, self.sample_rules)
        
        self.assertFalse(result.is_valid)
        self.assertIn("No face detected", result.issues[0])
        self.assertIn("clear, front-facing portrait", result.suggestions[0])
    
    def test_validate_face_positioning_low_confidence(self):
        """Test face positioning validation with low confidence score."""
        low_confidence_metrics = FaceMetrics(
            face_detected=True,
            face_bounds=(50, 50, 200, 300),
            eye_positions=(Point(120, 150), Point(180, 150)),
            face_height_ratio=0.75,
            eye_height_ratio=0.55,
            centering_offset=0.02,
            confidence_score=0.5  # Below threshold 0.7
        )
        
        result = self.detector.validate_face_positioning(low_confidence_metrics, self.sample_rules)
        
        self.assertFalse(result.is_valid)
        self.assertIn("Low face detection confidence", result.issues)
        self.assertIn("good lighting", ' '.join(result.suggestions))
    
    def test_face_metrics_calculation_accuracy(self):
        """Test accuracy of face metrics calculations."""
        metrics = self.detector.calculate_face_metrics(self.mock_landmarks)
        
        # Test that face metrics are calculated (values will depend on the outline landmarks)
        # Since we're using random outline landmarks, we just check that reasonable values are returned
        self.assertGreater(metrics.face_height_ratio, 0.0)
        self.assertLess(metrics.face_height_ratio, 1.0)
        
        # Test eye height ratio calculation
        # Left eye y = 150, Right eye y = 150, so average eye y = 150
        # image_height = 400
        # expected_eye_ratio = 150 / 400 = 0.375
        expected_eye_y = 150
        expected_eye_ratio = expected_eye_y / 400
        self.assertAlmostEqual(metrics.eye_height_ratio, expected_eye_ratio, places=1)
        
        # Test centering offset calculation
        # Mock landmarks are centered horizontally (x=150 for nose, forehead, chin)
        # image_width = 300, image_center_x = 150
        # face_x = min(x_coords) and face_width = max(x_coords) - min(x_coords)
        # With the current mock, face_x will be around 125 and face_width around 50
        # face_center_x = 125 + 50/2 = 150
        # expected_offset = abs(150 - 150) / 300 = 0
        face_center_x = metrics.face_bounds[0] + metrics.face_bounds[2] / 2
        image_center_x = 300 / 2  # image width / 2
        expected_offset = abs(face_center_x - image_center_x) / 300
        self.assertAlmostEqual(metrics.centering_offset, expected_offset, places=2) # Increased delta for robustness
    
    def test_crop_boundaries_aspect_ratio_preservation(self):
        """Test that crop boundaries preserve target aspect ratio."""
        # Test with square target format
        square_rules = {
            "dimensions": {"width": 600, "height": 600},
            "face_requirements": {"height_ratio": [0.70, 0.80]}
        }
        
        crop_box = self.detector.get_crop_boundaries(
            self.test_image, self.mock_landmarks, square_rules
        )
        
        # For square format, width should equal height (or close due to constraints)
        aspect_ratio = crop_box.width / crop_box.height
        self.assertAlmostEqual(aspect_ratio, 1.0, delta=0.1)
        
        # Test with rectangular target format
        rect_rules = {
            "dimensions": {"width": 400, "height": 600},
            "face_requirements": {"height_ratio": [0.70, 0.80]}
        }
        
        crop_box = self.detector.get_crop_boundaries(
            self.test_image, self.mock_landmarks, rect_rules
        )
        
        expected_ratio = 400 / 600
        actual_ratio = crop_box.width / crop_box.height
        self.assertAlmostEqual(actual_ratio, expected_ratio, delta=0.1)


class TestDataClasses(unittest.TestCase):
    """Test cases for data classes used in face detection."""
    
    def test_point_creation(self):
        """Test Point dataclass creation and attributes."""
        point = Point(x=10.5, y=20.3)
        self.assertEqual(point.x, 10.5)
        self.assertEqual(point.y, 20.3)
    
    def test_face_landmarks_creation(self):
        """Test FaceLandmarks dataclass creation."""
        landmarks = [Point(x=1, y=2), Point(x=3, y=4)]
        face_landmarks = FaceLandmarks(
            landmarks=landmarks,
            face_detected=True,
            confidence_score=0.9,
            image_width=640,
            image_height=480
        )
        
        self.assertEqual(len(face_landmarks.landmarks), 2)
        self.assertTrue(face_landmarks.face_detected)
        self.assertEqual(face_landmarks.confidence_score, 0.9)
        self.assertEqual(face_landmarks.image_width, 640)
        self.assertEqual(face_landmarks.image_height, 480)
    
    def test_face_metrics_creation(self):
        """Test FaceMetrics dataclass creation."""
        metrics = FaceMetrics(
            face_detected=True,
            face_bounds=(10, 20, 100, 150),
            eye_positions=(Point(30, 40), Point(70, 40)),
            face_height_ratio=0.75,
            eye_height_ratio=0.55,
            centering_offset=0.02,
            confidence_score=0.85
        )
        
        self.assertTrue(metrics.face_detected)
        self.assertEqual(metrics.face_bounds, (10, 20, 100, 150))
        self.assertEqual(metrics.face_height_ratio, 0.75)
        self.assertEqual(metrics.eye_height_ratio, 0.55)
        self.assertEqual(metrics.centering_offset, 0.02)
        self.assertEqual(metrics.confidence_score, 0.85)
    
    def test_crop_box_creation(self):
        """Test CropBox dataclass creation."""
        crop_box = CropBox(x=50, y=60, width=200, height=300)
        
        self.assertEqual(crop_box.x, 50)
        self.assertEqual(crop_box.y, 60)
        self.assertEqual(crop_box.width, 200)
        self.assertEqual(crop_box.height, 300)
    
    def test_validation_result_creation(self):
        """Test ValidationResult dataclass creation."""
        metrics = FaceMetrics(
            face_detected=True,
            face_bounds=(0, 0, 100, 100),
            eye_positions=(Point(25, 25), Point(75, 25)),
            face_height_ratio=0.75,
            eye_height_ratio=0.55,
            centering_offset=0.02,
            confidence_score=0.85
        )
        
        result = ValidationResult(
            is_valid=False,
            issues=["Face too small"],
            suggestions=["Move closer to camera"],
            metrics=metrics
        )
        
        self.assertFalse(result.is_valid)
        self.assertEqual(len(result.issues), 1)
        self.assertEqual(len(result.suggestions), 1)
        self.assertEqual(result.metrics, metrics)


if __name__ == '__main__':
    unittest.main()