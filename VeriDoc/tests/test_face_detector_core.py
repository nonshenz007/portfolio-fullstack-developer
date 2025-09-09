"""
Comprehensive unit tests for the core face detection system.
"""
import pytest
import numpy as np
import cv2
import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

from detection import (
    FaceDetector, 
    FaceDetectionResult, 
    BoundingBox, 
    FacialLandmarks, 
    FaceMetrics
)


class TestFaceDetector:
    """Test cases for the FaceDetector class."""
    
    @pytest.fixture
    def face_detector(self):
        """Create a FaceDetector instance for testing."""
        return FaceDetector()
    
    @pytest.fixture
    def sample_image(self):
        """Create a sample test image with a simple face-like pattern."""
        # Create a 400x400 BGR image
        image = np.zeros((400, 400, 3), dtype=np.uint8)
        
        # Draw a simple face-like pattern
        # Face outline (circle)
        cv2.circle(image, (200, 200), 80, (200, 200, 200), -1)
        
        # Eyes (dark circles)
        cv2.circle(image, (180, 180), 8, (50, 50, 50), -1)
        cv2.circle(image, (220, 180), 8, (50, 50, 50), -1)
        
        # Nose (small triangle)
        pts = np.array([[200, 190], [195, 210], [205, 210]], np.int32)
        cv2.fillPoly(image, [pts], (100, 100, 100))
        
        # Mouth (horizontal line)
        cv2.line(image, (185, 230), (215, 230), (50, 50, 50), 2)
        
        return image
    
    @pytest.fixture
    def no_face_image(self):
        """Create an image without any face."""
        # Create a simple landscape image
        image = np.zeros((400, 400, 3), dtype=np.uint8)
        
        # Add some random patterns that shouldn't be detected as faces
        cv2.rectangle(image, (50, 50), (150, 150), (100, 150, 200), -1)
        cv2.rectangle(image, (250, 250), (350, 350), (200, 100, 150), -1)
        
        return image
    
    @pytest.fixture
    def multiple_faces_image(self):
        """Create an image with multiple face-like patterns."""
        image = np.zeros((400, 600, 3), dtype=np.uint8)
        
        # First face
        cv2.circle(image, (150, 200), 60, (200, 200, 200), -1)
        cv2.circle(image, (135, 185), 6, (50, 50, 50), -1)
        cv2.circle(image, (165, 185), 6, (50, 50, 50), -1)
        
        # Second face (larger)
        cv2.circle(image, (450, 200), 80, (200, 200, 200), -1)
        cv2.circle(image, (430, 180), 8, (50, 50, 50), -1)
        cv2.circle(image, (470, 180), 8, (50, 50, 50), -1)
        
        return image
    
    def test_face_detector_initialization(self, face_detector):
        """Test that FaceDetector initializes correctly."""
        assert face_detector is not None
        assert face_detector.face_cascade is not None
        assert not face_detector.face_cascade.empty()
    
    def test_detect_face_success(self, face_detector, sample_image):
        """Test successful face detection."""
        result = face_detector.detect_face(sample_image)
        
        assert isinstance(result, FaceDetectionResult)
        assert result.success
        assert result.face_found
        assert result.confidence > 0.0
        assert result.bounding_box is not None
        assert result.processing_time > 0.0
        assert result.error_message is None
    
    def test_detect_face_no_face(self, face_detector, no_face_image):
        """Test face detection when no face is present."""
        result = face_detector.detect_face(no_face_image)
        
        assert isinstance(result, FaceDetectionResult)
        assert not result.face_found
        assert result.confidence == 0.0
        assert result.bounding_box is None
        assert result.processing_time > 0.0
        assert "No face detected" in result.error_message
    
    def test_detect_face_multiple_faces(self, face_detector, multiple_faces_image):
        """Test face detection with multiple faces."""
        result = face_detector.detect_face(multiple_faces_image)
        
        assert isinstance(result, FaceDetectionResult)
        # Should detect at least one face and select the largest
        if result.face_found:
            assert result.multiple_faces
            assert result.bounding_box is not None
            assert result.confidence > 0.0
    
    def test_detect_face_invalid_image(self, face_detector):
        """Test face detection with invalid image input."""
        # Test with None
        result = face_detector.detect_face(None)
        assert not result.success
        assert "Invalid or empty image" in result.error_message
        
        # Test with empty array
        empty_image = np.array([])
        result = face_detector.detect_face(empty_image)
        assert not result.success
        assert "Invalid or empty image" in result.error_message
    
    def test_bounding_box_properties(self):
        """Test BoundingBox properties and methods."""
        bbox = BoundingBox(x=100, y=150, width=200, height=250)
        
        assert bbox.center_x == 200.0  # 100 + 200/2
        assert bbox.center_y == 275.0  # 150 + 250/2
        assert bbox.area == 50000  # 200 * 250
    
    def test_facial_landmarks_properties(self):
        """Test FacialLandmarks properties and methods."""
        landmarks = FacialLandmarks(
            left_eye=(100, 120),
            right_eye=(140, 120),
            nose_tip=(120, 140),
            mouth_left=(110, 160),
            mouth_right=(130, 160),
            chin=(120, 180)
        )
        
        assert landmarks.eye_center == (120.0, 120.0)
        assert landmarks.eye_distance == 40.0  # Distance between (100,120) and (140,120)
    
    def test_face_metrics_methods(self):
        """Test FaceMetrics methods."""
        # Test perfectly centered face
        centered_metrics = FaceMetrics(
            face_height_ratio=0.7,
            eye_height_ratio=0.5,
            face_center_x=0.5,
            face_center_y=0.5,
            eye_distance=100.0,
            face_angle=2.0,
            eyes_open=True,
            mouth_closed=True
        )
        
        # Test centering check
        assert centered_metrics.is_centered(tolerance=0.1)
        assert centered_metrics.is_centered(tolerance=0.01)  # Perfectly centered
        
        # Test off-center face
        off_center_metrics = FaceMetrics(
            face_height_ratio=0.7,
            eye_height_ratio=0.5,
            face_center_x=0.6,  # Off center
            face_center_y=0.4,  # Off center
            eye_distance=100.0,
            face_angle=2.0,
            eyes_open=True,
            mouth_closed=True
        )
        
        assert off_center_metrics.is_centered(tolerance=0.15)  # Within loose tolerance
        assert not off_center_metrics.is_centered(tolerance=0.05)  # Outside strict tolerance
        
        # Test straightness check
        assert centered_metrics.is_straight(max_angle=5.0)
        assert not centered_metrics.is_straight(max_angle=1.0)
    
    def test_is_face_suitable(self, face_detector):
        """Test face suitability checking."""
        # Good face metrics
        good_metrics = FaceMetrics(
            face_height_ratio=0.6,
            eye_height_ratio=0.5,
            face_center_x=0.5,
            face_center_y=0.5,
            eye_distance=100.0,
            face_angle=2.0,
            eyes_open=True,
            mouth_closed=True
        )
        assert face_detector.is_face_suitable(good_metrics)
        
        # Face too small
        small_face_metrics = FaceMetrics(
            face_height_ratio=0.2,  # Too small
            eye_height_ratio=0.5,
            face_center_x=0.5,
            face_center_y=0.5,
            eye_distance=50.0,
            face_angle=2.0,
            eyes_open=True,
            mouth_closed=True
        )
        assert not face_detector.is_face_suitable(small_face_metrics)
        
        # Face too tilted
        tilted_face_metrics = FaceMetrics(
            face_height_ratio=0.6,
            eye_height_ratio=0.5,
            face_center_x=0.5,
            face_center_y=0.5,
            eye_distance=100.0,
            face_angle=20.0,  # Too tilted
            eyes_open=True,
            mouth_closed=True
        )
        assert not face_detector.is_face_suitable(tilted_face_metrics)
    
    def test_enhance_image_for_detection(self, face_detector, sample_image):
        """Test image enhancement for better detection."""
        enhanced = face_detector.enhance_image_for_detection(sample_image)
        
        assert enhanced is not None
        assert enhanced.shape == sample_image.shape
        assert enhanced.dtype == sample_image.dtype
    
    def test_calculate_face_metrics_with_landmarks(self, face_detector):
        """Test face metrics calculation with landmarks."""
        landmarks = FacialLandmarks(
            left_eye=(180, 180),
            right_eye=(220, 180),
            nose_tip=(200, 200),
            mouth_left=(185, 220),
            mouth_right=(215, 220),
            chin=(200, 240)
        )
        
        bbox = BoundingBox(x=160, y=160, width=80, height=100)
        image_shape = (400, 400, 3)
        
        metrics = face_detector.calculate_face_metrics(landmarks, bbox, image_shape)
        
        assert isinstance(metrics, FaceMetrics)
        assert 0.0 <= metrics.face_height_ratio <= 1.0
        assert 0.0 <= metrics.eye_height_ratio <= 1.0
        assert 0.0 <= metrics.face_center_x <= 1.0
        assert 0.0 <= metrics.face_center_y <= 1.0
        assert metrics.eye_distance > 0.0
        assert isinstance(metrics.face_angle, float)
        assert isinstance(metrics.eyes_open, bool)
        assert isinstance(metrics.mouth_closed, bool)
    
    @patch('detection.face_detector.MEDIAPIPE_AVAILABLE', False)
    def test_mediapipe_unavailable(self, face_detector, sample_image):
        """Test behavior when MediaPipe is not available."""
        bbox = BoundingBox(x=160, y=160, width=80, height=100)
        result = face_detector.get_facial_landmarks(sample_image, bbox)
        
        assert not result.success
        assert "MediaPipe not available" in result.error_message
    
    def test_processing_time_measurement(self, face_detector, sample_image):
        """Test that processing time is measured correctly."""
        result = face_detector.detect_face(sample_image)
        
        assert result.processing_time > 0.0
        assert result.processing_time < 10.0  # Should be reasonably fast
    
    def test_confidence_scoring(self, face_detector, sample_image):
        """Test confidence scoring logic."""
        result = face_detector.detect_face(sample_image)
        
        if result.face_found:
            assert 0.0 <= result.confidence <= 1.0
            # Confidence should be reasonable for a detected face
            assert result.confidence >= 0.5


class TestFaceDetectionWithRealImages:
    """Test face detection with real images if available."""
    
    @pytest.fixture
    def face_detector(self):
        """Create a FaceDetector instance for testing."""
        return FaceDetector()
    
    def test_detect_face_real_image(self, face_detector):
        """Test face detection with real test images if available."""
        test_image_paths = [
            "test_images/ics/compliant_ics_uae.jpg",
            "work/WhatsApp Image 2025-07-29 at 11.52.35.jpeg"
        ]
        
        for image_path in test_image_paths:
            if os.path.exists(image_path):
                # Load the image
                image = cv2.imread(image_path)
                if image is not None:
                    result = face_detector.detect_face(image)
                    
                    # Basic checks
                    assert isinstance(result, FaceDetectionResult)
                    assert result.processing_time > 0.0
                    
                    # If face is detected, validate the result
                    if result.face_found:
                        assert result.confidence > 0.0
                        assert result.bounding_box is not None
                        assert result.bounding_box.width > 0
                        assert result.bounding_box.height > 0
                        
                        print(f"✓ Face detected in {image_path}")
                        print(f"  Confidence: {result.confidence:.3f}")
                        print(f"  Bounding box: {result.bounding_box.x}, {result.bounding_box.y}, "
                              f"{result.bounding_box.width}, {result.bounding_box.height}")
                        print(f"  Processing time: {result.processing_time:.3f}s")
                    else:
                        print(f"✗ No face detected in {image_path}")
                        print(f"  Error: {result.error_message}")


class TestFaceDetectionPerformance:
    """Performance tests for face detection."""
    
    @pytest.fixture
    def face_detector(self):
        """Create a FaceDetector instance for testing."""
        return FaceDetector()
    
    def test_detection_speed(self, face_detector):
        """Test that face detection meets speed requirements."""
        # Create a reasonably sized test image
        image = np.random.randint(0, 255, (600, 600, 3), dtype=np.uint8)
        
        # Add a simple face pattern
        cv2.circle(image, (300, 300), 100, (200, 200, 200), -1)
        cv2.circle(image, (270, 270), 10, (50, 50, 50), -1)
        cv2.circle(image, (330, 270), 10, (50, 50, 50), -1)
        
        # Test detection speed
        result = face_detector.detect_face(image)
        
        # Should complete within reasonable time (5 seconds as per requirements)
        assert result.processing_time < 5.0
        print(f"Detection time: {result.processing_time:.3f}s")
    
    def test_batch_detection_performance(self, face_detector):
        """Test performance with multiple images."""
        images = []
        
        # Create 10 test images
        for i in range(10):
            image = np.random.randint(0, 255, (400, 400, 3), dtype=np.uint8)
            # Add face pattern to some images
            if i % 2 == 0:
                cv2.circle(image, (200, 200), 60, (200, 200, 200), -1)
                cv2.circle(image, (185, 185), 6, (50, 50, 50), -1)
                cv2.circle(image, (215, 185), 6, (50, 50, 50), -1)
            images.append(image)
        
        # Test batch processing
        import time
        start_time = time.time()
        
        results = []
        for image in images:
            result = face_detector.detect_face(image)
            results.append(result)
        
        total_time = time.time() - start_time
        avg_time = total_time / len(images)
        
        print(f"Batch processing: {len(images)} images in {total_time:.3f}s")
        print(f"Average time per image: {avg_time:.3f}s")
        
        # Each image should process reasonably quickly
        assert avg_time < 2.0
        
        # Check that we got results for all images
        assert len(results) == len(images)
        for result in results:
            assert isinstance(result, FaceDetectionResult)


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])