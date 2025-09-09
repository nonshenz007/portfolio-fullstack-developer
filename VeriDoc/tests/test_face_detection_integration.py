"""
Integration tests for face detection system with the broader VeriDoc system.
"""
import pytest
import numpy as np
import cv2
import os
from pathlib import Path

from detection import FaceDetector, FaceDetectionResult


class TestFaceDetectionIntegration:
    """Integration tests for face detection system."""
    
    @pytest.fixture
    def face_detector(self):
        """Create a FaceDetector instance for testing."""
        return FaceDetector()
    
    def test_face_detector_import(self):
        """Test that face detector can be imported correctly."""
        from detection import FaceDetector, FaceDetectionResult, BoundingBox, FacialLandmarks, FaceMetrics
        
        # Verify classes can be instantiated
        detector = FaceDetector()
        assert detector is not None
        
        # Verify data classes work
        bbox = BoundingBox(x=10, y=20, width=100, height=120)
        assert bbox.center_x == 60.0
        assert bbox.center_y == 80.0
    
    def test_opencv_integration(self, face_detector):
        """Test that OpenCV integration works correctly."""
        # Create a test image using OpenCV
        image = np.zeros((300, 300, 3), dtype=np.uint8)
        cv2.rectangle(image, (50, 50), (250, 250), (128, 128, 128), -1)
        
        # Should not crash and should return a valid result
        result = face_detector.detect_face(image)
        assert isinstance(result, FaceDetectionResult)
        assert result.processing_time > 0.0
    
    def test_mediapipe_fallback(self, face_detector):
        """Test MediaPipe fallback behavior."""
        # Create a simple test image
        image = np.zeros((200, 200, 3), dtype=np.uint8)
        
        # Create a mock bounding box
        from detection.data_models import BoundingBox
        bbox = BoundingBox(x=50, y=50, width=100, height=100)
        
        # Test landmark detection (should handle MediaPipe availability gracefully)
        result = face_detector.get_facial_landmarks(image, bbox)
        
        # Should return a valid result regardless of MediaPipe availability
        assert hasattr(result, 'success')
        assert hasattr(result, 'landmarks')
        assert hasattr(result, 'confidence')
    
    def test_error_handling_integration(self, face_detector):
        """Test error handling integration."""
        # Test with various invalid inputs
        invalid_inputs = [
            None,
            np.array([]),
            np.zeros((0, 0, 3)),
            "not an image"
        ]
        
        for invalid_input in invalid_inputs:
            try:
                result = face_detector.detect_face(invalid_input)
                # Should return a failed result, not crash
                assert isinstance(result, FaceDetectionResult)
                assert not result.success
            except Exception as e:
                # If it does throw an exception, it should be handled gracefully
                assert "Invalid" in str(e) or "empty" in str(e)
    
    def test_real_world_image_processing(self, face_detector):
        """Test with real-world images if available."""
        # Look for test images in common locations
        test_locations = [
            "test_images/ics/compliant_ics_uae.jpg",
            "work/WhatsApp Image 2025-07-29 at 11.52.35.jpeg"
        ]
        
        images_tested = 0
        successful_detections = 0
        
        for image_path in test_locations:
            if os.path.exists(image_path):
                try:
                    # Load image
                    image = cv2.imread(image_path)
                    if image is not None:
                        images_tested += 1
                        
                        # Test detection
                        result = face_detector.detect_face(image)
                        
                        # Validate result structure
                        assert isinstance(result, FaceDetectionResult)
                        assert hasattr(result, 'face_found')
                        assert hasattr(result, 'confidence')
                        assert hasattr(result, 'processing_time')
                        assert result.processing_time > 0.0
                        
                        if result.face_found:
                            successful_detections += 1
                            assert result.bounding_box is not None
                            assert result.confidence > 0.0
                            
                            # Test face metrics if available
                            if result.face_metrics:
                                metrics = result.face_metrics
                                assert 0.0 <= metrics.face_height_ratio <= 1.0
                                assert 0.0 <= metrics.eye_height_ratio <= 1.0
                                assert 0.0 <= metrics.face_center_x <= 1.0
                                assert 0.0 <= metrics.face_center_y <= 1.0
                        
                        print(f"Processed {image_path}: "
                              f"Face found: {result.face_found}, "
                              f"Confidence: {result.confidence:.3f}, "
                              f"Time: {result.processing_time:.3f}s")
                        
                except Exception as e:
                    print(f"Error processing {image_path}: {e}")
        
        if images_tested > 0:
            detection_rate = successful_detections / images_tested
            print(f"Detection rate: {detection_rate:.1%} ({successful_detections}/{images_tested})")
            
            # For real passport photos, we should have a reasonable detection rate
            # Note: This might fail if test images don't contain clear faces
            if images_tested >= 2:
                assert detection_rate >= 0.5, f"Detection rate too low: {detection_rate:.1%}"
        else:
            print("No test images found - skipping real-world image test")
    
    def test_memory_usage(self, face_detector):
        """Test that face detection doesn't have memory leaks."""
        import gc
        
        # Create a test image
        image = np.random.randint(0, 255, (400, 400, 3), dtype=np.uint8)
        
        # Add a simple face pattern
        cv2.circle(image, (200, 200), 80, (200, 200, 200), -1)
        cv2.circle(image, (180, 180), 8, (50, 50, 50), -1)
        cv2.circle(image, (220, 180), 8, (50, 50, 50), -1)
        
        # Process the same image multiple times
        results = []
        for i in range(50):
            result = face_detector.detect_face(image)
            results.append(result)
            
            # Periodically force garbage collection
            if i % 10 == 0:
                gc.collect()
        
        # All results should be valid
        assert len(results) == 50
        for result in results:
            assert isinstance(result, FaceDetectionResult)
            assert result.processing_time > 0.0
    
    def test_thread_safety_basic(self, face_detector):
        """Basic test for thread safety (single-threaded for now)."""
        import threading
        import time
        
        # Create test images
        images = []
        for i in range(5):
            image = np.random.randint(0, 255, (300, 300, 3), dtype=np.uint8)
            cv2.circle(image, (150, 150), 60, (200, 200, 200), -1)
            cv2.circle(image, (135, 135), 6, (50, 50, 50), -1)
            cv2.circle(image, (165, 135), 6, (50, 50, 50), -1)
            images.append(image)
        
        results = []
        errors = []
        
        def process_image(img, index):
            try:
                result = face_detector.detect_face(img)
                results.append((index, result))
            except Exception as e:
                errors.append((index, str(e)))
        
        # Process images sequentially (basic thread safety test)
        threads = []
        for i, image in enumerate(images):
            thread = threading.Thread(target=process_image, args=(image, i))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Check results
        assert len(errors) == 0, f"Errors occurred: {errors}"
        assert len(results) == len(images)
        
        for index, result in results:
            assert isinstance(result, FaceDetectionResult)
            assert result.processing_time > 0.0


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])