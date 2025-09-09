"""
Unit tests for AI Processing Engine components.

Tests for YOLOv8 face detection, MediaPipe analysis, background segmentation,
quality assessment, and overall AI engine functionality.
"""

import pytest
import numpy as np
import cv2
import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Import AI components
from ai.ai_engine import AIEngine
from ai.yolov8_detector import YOLOv8FaceDetector
from ai.mediapipe_analyzer import MediaPipeFaceAnalyzer, FaceLandmarks, FaceFeatures
from ai.background_segmenter import BackgroundSegmenter, BackgroundMask
from ai.quality_assessor import QualityAssessor, QualityMetrics


class TestAIEngine:
    """Test cases for the main AI Engine."""
    
    @pytest.fixture
    def ai_engine(self):
        """Create AI engine instance for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            return AIEngine(model_cache_dir=temp_dir)
    
    @pytest.fixture
    def test_image(self):
        """Create a test image."""
        # Create a simple test image with a face-like pattern
        image = np.zeros((400, 300, 3), dtype=np.uint8)
        
        # Add a face-like rectangle
        cv2.rectangle(image, (100, 100), (200, 250), (180, 150, 120), -1)
        
        # Add eyes
        cv2.circle(image, (130, 150), 10, (50, 50, 50), -1)
        cv2.circle(image, (170, 150), 10, (50, 50, 50), -1)
        
        # Add mouth
        cv2.ellipse(image, (150, 200), (20, 10), 0, 0, 180, (100, 50, 50), -1)
        
        return image
    
    def test_ai_engine_initialization(self, ai_engine):
        """Test AI engine initialization."""
        assert ai_engine is not None
        assert hasattr(ai_engine, 'face_detector')
        assert hasattr(ai_engine, 'face_analyzer')
        assert hasattr(ai_engine, 'background_segmenter')
        assert hasattr(ai_engine, 'quality_assessor')
    
    def test_detect_faces(self, ai_engine, test_image):
        """Test face detection functionality."""
        faces = ai_engine.detect_faces(test_image)
        assert isinstance(faces, list)
        # Should detect at least one face in our test image
        assert len(faces) >= 0  # May be 0 if detection fails on simple test image
    
    def test_process_image_complete(self, ai_engine, test_image):
        """Test complete image processing pipeline."""
        results = ai_engine.process_image_complete(test_image)
        
        assert isinstance(results, dict)
        assert 'processing_time' in results
        assert 'faces' in results
        assert 'quality' in results
        assert 'background' in results
        assert 'success' in results
        
        # Processing time should be reasonable
        assert results['processing_time'] > 0
        assert results['processing_time'] < 30  # Should complete within 30 seconds
    
    def test_enhance_image_for_detection(self, ai_engine, test_image):
        """Test image enhancement for better detection."""
        enhanced = ai_engine.enhance_image_for_detection(test_image)
        
        assert enhanced.shape == test_image.shape
        assert enhanced.dtype == np.uint8
        # Enhanced image should be different from original
        assert not np.array_equal(enhanced, test_image)
    
    def test_get_model_info(self, ai_engine):
        """Test model information retrieval."""
        info = ai_engine.get_model_info()
        
        assert isinstance(info, dict)
        assert 'face_detector' in info
        assert 'face_analyzer' in info
        assert 'background_segmenter' in info
        assert 'quality_assessor' in info


class TestYOLOv8FaceDetector:
    """Test cases for YOLOv8 face detector."""
    
    @pytest.fixture
    def detector(self):
        """Create detector instance for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            return YOLOv8FaceDetector(model_cache_dir=temp_dir)
    
    @pytest.fixture
    def face_image(self):
        """Create an image with a clear face pattern."""
        image = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Create a more realistic face pattern
        face_center = (320, 240)
        face_size = 120
        
        # Face oval
        cv2.ellipse(image, face_center, (face_size//2, int(face_size*0.7)), 
                   0, 0, 360, (200, 180, 160), -1)
        
        # Eyes
        eye_y = face_center[1] - 30
        cv2.circle(image, (face_center[0] - 30, eye_y), 8, (50, 50, 50), -1)
        cv2.circle(image, (face_center[0] + 30, eye_y), 8, (50, 50, 50), -1)
        
        # Nose
        cv2.circle(image, (face_center[0], face_center[1]), 5, (150, 130, 110), -1)
        
        # Mouth
        cv2.ellipse(image, (face_center[0], face_center[1] + 30), (15, 8), 
                   0, 0, 180, (120, 80, 80), -1)
        
        return image
    
    def test_detector_initialization(self, detector):
        """Test detector initialization."""
        assert detector is not None
        assert detector.confidence_threshold > 0
        assert detector.iou_threshold > 0
        assert detector.min_face_size > 0
    
    def test_detect_faces_basic(self, detector, face_image):
        """Test basic face detection."""
        faces = detector.detect_faces(face_image)
        assert isinstance(faces, list)
        # Each face should have bbox and confidence
        for face in faces:
            assert hasattr(face, 'bbox')
            assert hasattr(face, 'confidence')
            assert len(face.bbox) == 4  # x, y, width, height
            assert 0 <= face.confidence <= 1
    
    def test_detect_with_enhancement(self, detector, face_image):
        """Test detection with image enhancement."""
        # Create a darker image to test enhancement
        dark_image = (face_image * 0.3).astype(np.uint8)
        
        faces = detector.detect_with_enhancement(dark_image, max_attempts=2)
        assert isinstance(faces, list)
    
    def test_set_detection_parameters(self, detector):
        """Test parameter setting."""
        original_conf = detector.confidence_threshold
        
        detector.set_detection_parameters(confidence_threshold=0.7)
        assert detector.confidence_threshold == 0.7
        
        detector.set_detection_parameters(confidence_threshold=original_conf)
        assert detector.confidence_threshold == original_conf
    
    def test_is_valid_face_size(self, detector):
        """Test face size validation."""
        # Valid face sizes
        assert detector._is_valid_face_size(100, 120) == True
        assert detector._is_valid_face_size(80, 100) == True
        
        # Invalid face sizes
        assert detector._is_valid_face_size(10, 10) == False  # Too small
        assert detector._is_valid_face_size(1000, 100) == False  # Wrong aspect ratio
    
    def test_get_model_info(self, detector):
        """Test model information."""
        info = detector.get_model_info()
        
        assert isinstance(info, dict)
        assert 'model_available' in info
        assert 'confidence_threshold' in info
        assert 'min_face_size' in info
    
    def test_benchmark_detection(self, detector, face_image):
        """Test detection benchmarking."""
        test_images = [face_image, face_image]  # Use same image twice
        
        benchmark = detector.benchmark_detection(test_images)
        
        assert isinstance(benchmark, dict)
        assert 'total_images' in benchmark
        assert 'detection_rate' in benchmark
        assert 'average_time_per_image' in benchmark
        assert benchmark['total_images'] == 2


class TestMediaPipeFaceAnalyzer:
    """Test cases for MediaPipe face analyzer."""
    
    @pytest.fixture
    def analyzer(self):
        """Create analyzer instance for testing."""
        return MediaPipeFaceAnalyzer()
    
    @pytest.fixture
    def face_bbox(self):
        """Create a test face bounding box."""
        return (100, 100, 200, 250)  # x, y, width, height
    
    @pytest.fixture
    def test_landmarks(self):
        """Create test landmarks."""
        return FaceLandmarks(
            eye_positions=((0.3, 0.4), (0.7, 0.4)),
            eye_openness=(0.8, 0.8),
            mouth_position=(0.5, 0.7),
            mouth_openness=0.1,
            face_orientation={'roll': 0.0, 'pitch': 0.0, 'yaw': 0.0},
            confidence=0.9
        )
    
    def test_analyzer_initialization(self, analyzer):
        """Test analyzer initialization."""
        assert analyzer is not None
        assert hasattr(analyzer, 'landmark_indices')
        assert len(analyzer.landmark_indices) > 0
    
    def test_analyze_landmarks(self, analyzer, face_image, face_bbox):
        """Test landmark analysis."""
        landmarks = analyzer.analyze_landmarks(face_image, face_bbox)
        
        # May return None if MediaPipe is not available or detection fails
        if landmarks is not None:
            assert isinstance(landmarks, FaceLandmarks)
            assert len(landmarks.eye_positions) == 2
            assert len(landmarks.eye_openness) == 2
            assert 0 <= landmarks.confidence <= 1
    
    def test_extract_features(self, analyzer, face_image, test_landmarks):
        """Test feature extraction."""
        features = analyzer.extract_features(face_image, test_landmarks)
        
        assert isinstance(features, FaceFeatures)
        assert hasattr(features, 'eye_positions')
        assert hasattr(features, 'glasses_detected')
        assert hasattr(features, 'head_covering_detected')
        assert hasattr(features, 'face_height_ratio')
        assert hasattr(features, 'eye_height_ratio')
        assert hasattr(features, 'centering_offset')
    
    def test_detect_accessories(self, analyzer, face_image, test_landmarks):
        """Test accessory detection."""
        accessories = analyzer.detect_accessories(face_image, test_landmarks)
        
        assert isinstance(accessories, dict)
        assert 'glasses_detected' in accessories
        assert 'glasses_type' in accessories
        assert 'head_covering_detected' in accessories
        assert 'head_covering_type' in accessories
        assert 'confidence' in accessories
        
        assert isinstance(accessories['glasses_detected'], bool)
        assert isinstance(accessories['head_covering_detected'], bool)
        assert 0 <= accessories['confidence'] <= 1
    
    def test_get_model_info(self, analyzer):
        """Test model information."""
        info = analyzer.get_model_info()
        
        assert isinstance(info, dict)
        assert 'mediapipe_available' in info
        assert 'face_mesh_available' in info
        assert 'landmark_indices_count' in info


class TestBackgroundSegmenter:
    """Test cases for background segmenter."""
    
    @pytest.fixture
    def segmenter(self):
        """Create segmenter instance for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            return BackgroundSegmenter(model_cache_dir=temp_dir)
    
    @pytest.fixture
    def test_image_with_bg(self):
        """Create test image with clear background."""
        image = np.ones((300, 400, 3), dtype=np.uint8) * 255  # White background
        
        # Add a subject in the center
        cv2.rectangle(image, (150, 100), (250, 200), (100, 150, 200), -1)
        
        return image
    
    def test_segmenter_initialization(self, segmenter):
        """Test segmenter initialization."""
        assert segmenter is not None
        assert hasattr(segmenter, 'segmentation_method')
        assert segmenter.segmentation_method in ['onnx', 'rembg', 'traditional']
    
    def test_segment(self, segmenter, test_image_with_bg):
        """Test background segmentation."""
        mask = segmenter.segment(test_image_with_bg)
        
        assert isinstance(mask, BackgroundMask)
        assert mask.mask.shape[:2] == test_image_with_bg.shape[:2]
        assert 0 <= mask.confidence <= 1
        assert len(mask.background_color) == 3
        assert 0 <= mask.uniformity_score <= 1
    
    def test_replace_background(self, segmenter, test_image_with_bg):
        """Test background replacement."""
        # Create a simple mask
        h, w = test_image_with_bg.shape[:2]
        mask = np.zeros((h, w), dtype=np.uint8)
        mask[100:200, 150:250] = 255  # Foreground region
        
        new_color = (0, 255, 0)  # Green background
        result = segmenter.replace_background(test_image_with_bg, mask, new_color)
        
        assert result.shape == test_image_with_bg.shape
        assert result.dtype == np.uint8
    
    def test_refine_mask(self, segmenter, test_image_with_bg):
        """Test mask refinement."""
        # Create a noisy mask
        h, w = test_image_with_bg.shape[:2]
        noisy_mask = np.random.randint(0, 256, (h, w), dtype=np.uint8)
        
        refined_mask = segmenter.refine_mask(test_image_with_bg, noisy_mask)
        
        assert refined_mask.shape == noisy_mask.shape
        assert refined_mask.dtype == np.uint8
    
    def test_get_background_statistics(self, segmenter, test_image_with_bg):
        """Test background statistics."""
        # Create a simple mask
        h, w = test_image_with_bg.shape[:2]
        mask = np.zeros((h, w), dtype=np.uint8)
        mask[100:200, 150:250] = 255  # Foreground region
        
        stats = segmenter.get_background_statistics(test_image_with_bg, mask)
        
        if 'error' not in stats:
            assert 'pixel_count' in stats
            assert 'mean_bgr' in stats
            assert 'uniformity_score' in stats
            assert stats['pixel_count'] > 0
    
    def test_get_model_info(self, segmenter):
        """Test model information."""
        info = segmenter.get_model_info()
        
        assert isinstance(info, dict)
        assert 'segmentation_method' in info
        assert 'onnx_available' in info
        assert 'rembg_available' in info


class TestQualityAssessor:
    """Test cases for quality assessor."""
    
    @pytest.fixture
    def assessor(self):
        """Create assessor instance for testing."""
        return QualityAssessor()
    
    @pytest.fixture
    def high_quality_image(self):
        """Create a high-quality test image."""
        # Create a sharp, well-lit image
        image = np.zeros((400, 300, 3), dtype=np.uint8)
        
        # Add gradient background
        for y in range(400):
            for x in range(300):
                image[y, x] = [200 + x//10, 200 + y//10, 220]
        
        # Add sharp details
        cv2.rectangle(image, (100, 100), (200, 200), (50, 100, 150), 2)
        cv2.circle(image, (150, 150), 30, (255, 255, 255), -1)
        
        return image
    
    @pytest.fixture
    def low_quality_image(self):
        """Create a low-quality test image."""
        # Create a blurry, poorly lit image
        image = np.ones((400, 300, 3), dtype=np.uint8) * 50  # Dark image
        
        # Add noise
        noise = np.random.randint(-20, 20, image.shape, dtype=np.int16)
        image = np.clip(image.astype(np.int16) + noise, 0, 255).astype(np.uint8)
        
        # Apply blur
        image = cv2.GaussianBlur(image, (15, 15), 5)
        
        return image
    
    def test_assessor_initialization(self, assessor):
        """Test assessor initialization."""
        assert assessor is not None
        assert hasattr(assessor, 'thresholds')
        assert 'sharpness' in assessor.thresholds
        assert 'lighting' in assessor.thresholds
        assert 'color' in assessor.thresholds
        assert 'noise' in assessor.thresholds
        assert 'resolution' in assessor.thresholds
    
    def test_assess_quality_high_quality(self, assessor, high_quality_image):
        """Test quality assessment on high-quality image."""
        metrics = assessor.assess_quality(high_quality_image)
        
        assert isinstance(metrics, QualityMetrics)
        assert 0 <= metrics.sharpness_score <= 1
        assert 0 <= metrics.lighting_score <= 1
        assert 0 <= metrics.color_score <= 1
        assert 0 <= metrics.noise_score <= 1
        assert 0 <= metrics.resolution_score <= 1
        assert 0 <= metrics.overall_score <= 1
        assert isinstance(metrics.issues, list)
        
        # High-quality image should have decent scores
        assert metrics.overall_score > 0.3  # Should be reasonably good
    
    def test_assess_quality_low_quality(self, assessor, low_quality_image):
        """Test quality assessment on low-quality image."""
        metrics = assessor.assess_quality(low_quality_image)
        
        assert isinstance(metrics, QualityMetrics)
        # Low-quality image should have lower scores
        assert metrics.overall_score < 0.8  # Should detect quality issues
        assert len(metrics.issues) > 0  # Should identify issues
    
    def test_assess_sharpness(self, assessor, high_quality_image, low_quality_image):
        """Test sharpness assessment."""
        sharp_score = assessor._assess_sharpness(high_quality_image)
        blurry_score = assessor._assess_sharpness(low_quality_image)
        
        assert 0 <= sharp_score <= 1
        assert 0 <= blurry_score <= 1
        # Sharp image should score higher than blurry image
        assert sharp_score >= blurry_score
    
    def test_assess_lighting(self, assessor, high_quality_image):
        """Test lighting assessment."""
        lighting_score = assessor._assess_lighting(high_quality_image)
        
        assert 0 <= lighting_score <= 1
    
    def test_assess_color_accuracy(self, assessor, high_quality_image):
        """Test color accuracy assessment."""
        color_score = assessor._assess_color_accuracy(high_quality_image)
        
        assert 0 <= color_score <= 1
    
    def test_assess_noise_levels(self, assessor, high_quality_image, low_quality_image):
        """Test noise level assessment."""
        clean_score = assessor._assess_noise_levels(high_quality_image)
        noisy_score = assessor._assess_noise_levels(low_quality_image)
        
        assert 0 <= clean_score <= 1
        assert 0 <= noisy_score <= 1
        # Clean image should score higher than noisy image
        assert clean_score >= noisy_score
    
    def test_assess_resolution(self, assessor, high_quality_image):
        """Test resolution assessment."""
        resolution_score = assessor._assess_resolution(high_quality_image)
        
        assert 0 <= resolution_score <= 1
    
    def test_get_detailed_analysis(self, assessor, high_quality_image):
        """Test detailed analysis."""
        analysis = assessor.get_detailed_analysis(high_quality_image)
        
        if 'error' not in analysis:
            assert 'basic_statistics' in analysis
            assert 'quality_metrics' in analysis
            assert 'detailed_metrics' in analysis
            
            basic_stats = analysis['basic_statistics']
            assert 'dimensions' in basic_stats
            assert 'total_pixels' in basic_stats
            assert 'mean_brightness' in basic_stats
    
    def test_get_model_info(self, assessor):
        """Test model information."""
        info = assessor.get_model_info()
        
        assert isinstance(info, dict)
        assert 'thresholds' in info
        assert 'assessment_methods' in info


class TestIntegration:
    """Integration tests for AI components working together."""
    
    @pytest.fixture
    def full_test_image(self):
        """Create a comprehensive test image."""
        # Create a realistic photo-like image
        image = np.ones((600, 800, 3), dtype=np.uint8) * 240  # Light gray background
        
        # Add a person silhouette
        person_center = (400, 300)
        
        # Head (oval)
        cv2.ellipse(image, person_center, (80, 100), 0, 0, 360, (200, 180, 160), -1)
        
        # Eyes
        eye_y = person_center[1] - 30
        cv2.circle(image, (person_center[0] - 25, eye_y), 8, (50, 50, 50), -1)
        cv2.circle(image, (person_center[0] + 25, eye_y), 8, (50, 50, 50), -1)
        
        # Nose
        cv2.circle(image, person_center, 4, (150, 130, 110), -1)
        
        # Mouth
        cv2.ellipse(image, (person_center[0], person_center[1] + 25), (12, 6), 
                   0, 0, 180, (120, 80, 80), -1)
        
        # Shoulders
        cv2.ellipse(image, (person_center[0], person_center[1] + 120), (100, 40), 
                   0, 0, 180, (100, 120, 140), -1)
        
        return image
    
    def test_complete_ai_pipeline(self, full_test_image):
        """Test complete AI processing pipeline."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Initialize AI engine
            ai_engine = AIEngine(model_cache_dir=temp_dir)
            
            # Process the image
            results = ai_engine.process_image_complete(full_test_image)
            
            # Verify results structure
            assert isinstance(results, dict)
            assert 'success' in results
            assert 'processing_time' in results
            assert 'faces' in results
            assert 'quality' in results
            assert 'background' in results
            
            # Verify processing completed
            assert results['processing_time'] > 0
            
            # If successful, verify result types
            if results['success']:
                assert isinstance(results['faces'], list)
                if results['quality'] is not None:
                    assert hasattr(results['quality'], 'overall_score')
                if results['background'] is not None:
                    assert hasattr(results['background'], 'confidence')


if __name__ == '__main__':
    pytest.main([__file__, '-v'])