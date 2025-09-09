"""
Integration tests for ProcessingController.

These tests verify the complete processing workflow including:
- Image loading and validation
- Face detection integration
- ICAO compliance validation
- Error handling and recovery
- Progress tracking
- Batch processing
"""

import pytest
import numpy as np
import cv2
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from core.processing_controller import (
    ProcessingController, ProcessingResult, BatchResult, ValidationResult,
    ProcessingStage, ProcessingProgress
)
from core.config_manager import ConfigManager
from detection.data_models import FaceDetectionResult, FaceMetrics, BoundingBox
from validation.validation_models import ComplianceResult, ValidationIssue, ValidationSeverity


class TestProcessingControllerIntegration:
    """Integration tests for ProcessingController."""
    
    @pytest.fixture
    def temp_image(self):
        """Create a temporary test image."""
        # Create a simple test image (200x200 white background with black rectangle for "face")
        image = np.ones((200, 200, 3), dtype=np.uint8) * 255
        # Add a black rectangle to simulate a face
        cv2.rectangle(image, (75, 50), (125, 150), (0, 0, 0), -1)
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as f:
            cv2.imwrite(f.name, image)
            yield f.name
        
        # Cleanup
        os.unlink(f.name)
    
    @pytest.fixture
    def config_manager(self):
        """Create a test configuration manager."""
        return ConfigManager()
    
    @pytest.fixture
    def controller(self, config_manager):
        """Create a processing controller for testing."""
        return ProcessingController(config_manager)
    
    @pytest.fixture
    def mock_face_detector(self):
        """Create a mock face detector."""
        detector = Mock()
        
        # Mock successful face detection
        face_metrics = FaceMetrics(
            face_height_ratio=0.75,
            eye_height_ratio=0.55,
            face_center_x=0.5,
            face_center_y=0.5,
            eye_distance=50.0,
            face_angle=0.0,
            eyes_open=True,
            mouth_closed=True
        )
        
        detection_result = FaceDetectionResult(
            face_found=True,
            confidence=0.9,
            bounding_box=BoundingBox(x=75, y=50, width=50, height=100),
            landmarks=None,
            face_metrics=face_metrics,
            multiple_faces=False,
            processing_time=0.1
        )
        
        detector.detect_face.return_value = detection_result
        return detector
    
    @pytest.fixture
    def mock_icao_validator(self):
        """Create a mock ICAO validator."""
        validator = Mock()
        
        # Mock successful validation
        compliance_result = ComplianceResult(
            overall_pass=True,
            compliance_score=95.0,
            dimension_check=Mock(passes=True, issues=[]),
            position_check=Mock(passes=True, issues=[]),
            background_check=Mock(passes=True, issues=[]),
            quality_check=Mock(passes=True, issues=[]),
            issues=[],
            format_name="ICS-UAE",
            processing_time=0.2
        )
        
        validator.validate_compliance.return_value = compliance_result
        return validator
    
    def test_process_image_success(self, controller, temp_image, mock_face_detector, mock_icao_validator):
        """Test successful image processing."""
        # Mock the components
        controller._face_detector = mock_face_detector
        controller._icao_validator = mock_icao_validator
        
        # Process the image
        result = controller.process_image(temp_image, "ICS-UAE")
        
        # Verify result
        assert result.success is True
        assert result.face_detected is True
        assert result.compliance_score == 95.0
        assert result.passes_requirements is True
        assert result.processing_time > 0
        assert len(result.processing_stages) >= 0
        
        # Verify components were called
        mock_face_detector.detect_face.assert_called_once()
        mock_icao_validator.validate_compliance.assert_called_once()
    
    def test_process_image_file_not_found(self, controller):
        """Test processing with non-existent file."""
        result = controller.process_image("nonexistent.jpg", "ICS-UAE")
        
        assert result.success is False
        assert "Image file not found" in result.issues
        assert result.face_detected is False
        assert result.compliance_score == 0.0
    
    def test_process_image_invalid_format(self, controller, temp_image):
        """Test processing with invalid format."""
        result = controller.process_image(temp_image, "INVALID-FORMAT")
        
        assert result.success is False
        assert "Unknown format" in result.issues[0]
        assert result.face_detected is False
        assert result.compliance_score == 0.0
    
    def test_process_image_no_face_detected(self, controller, temp_image, mock_icao_validator):
        """Test processing when no face is detected."""
        # Mock face detector to return no face
        mock_face_detector = Mock()
        mock_face_detector.detect_face.return_value = FaceDetectionResult(
            face_found=False,
            confidence=0.0,
            bounding_box=None,
            landmarks=None,
            face_metrics=None,
            error_message="No face detected"
        )
        
        controller._face_detector = mock_face_detector
        controller._icao_validator = mock_icao_validator
        
        result = controller.process_image(temp_image, "ICS-UAE")
        
        assert result.success is False
        assert result.face_detected is False
        assert "No face detected" in result.issues
        assert len(result.suggestions) > 0
    
    def test_process_image_validation_failure(self, controller, temp_image, mock_face_detector):
        """Test processing when validation fails."""
        # Mock validator to return failure
        mock_validator = Mock()
        
        validation_issue = ValidationIssue(
            category="background",
            severity=ValidationSeverity.MAJOR,
            message="Background color incorrect",
            suggestion="Use white background",
            auto_fixable=True
        )
        
        compliance_result = ComplianceResult(
            overall_pass=False,
            compliance_score=45.0,
            dimension_check=Mock(passes=True, issues=[]),
            position_check=Mock(passes=True, issues=[]),
            background_check=Mock(passes=False, issues=[validation_issue]),
            quality_check=Mock(passes=True, issues=[]),
            issues=[validation_issue],
            format_name="ICS-UAE",
            processing_time=0.2
        )
        
        mock_validator.validate_compliance.return_value = compliance_result
        
        controller._face_detector = mock_face_detector
        controller._icao_validator = mock_validator
        
        result = controller.process_image(temp_image, "ICS-UAE")
        
        assert result.success is True  # Processing succeeded even if validation failed
        assert result.face_detected is True
        assert result.passes_requirements is False
        assert result.compliance_score == 45.0
        assert "Background color incorrect" in result.issues
        assert "Use white background" in result.suggestions
    
    def test_progress_tracking(self, controller, temp_image, mock_face_detector, mock_icao_validator):
        """Test progress tracking during processing."""
        progress_updates = []
        
        def progress_callback(progress: ProcessingProgress):
            progress_updates.append(progress)
        
        controller.set_progress_callback(progress_callback)
        controller._face_detector = mock_face_detector
        controller._icao_validator = mock_icao_validator
        
        result = controller.process_image(temp_image, "ICS-UAE")
        
        assert result.success is True
        assert len(progress_updates) > 0
        
        # Check that we got progress updates for different stages
        stages = [update.stage for update in progress_updates]
        assert ProcessingStage.INITIALIZING in stages
        assert ProcessingStage.LOADING_IMAGE in stages
        assert ProcessingStage.DETECTING_FACE in stages
        assert ProcessingStage.VALIDATING_COMPLIANCE in stages
        assert ProcessingStage.COMPLETED in stages
    
    def test_batch_processing_success(self, controller, mock_face_detector, mock_icao_validator):
        """Test successful batch processing."""
        # Create multiple temporary images
        temp_images = []
        for i in range(3):
            image = np.ones((200, 200, 3), dtype=np.uint8) * 255
            cv2.rectangle(image, (75, 50), (125, 150), (0, 0, 0), -1)
            
            with tempfile.NamedTemporaryFile(suffix=f'_test_{i}.jpg', delete=False) as f:
                cv2.imwrite(f.name, image)
                temp_images.append(f.name)
        
        try:
            controller._face_detector = mock_face_detector
            controller._icao_validator = mock_icao_validator
            
            result = controller.batch_process(temp_images, "ICS-UAE")
            
            assert result.total_images == 3
            assert result.successful == 3
            assert result.failed == 0
            assert len(result.results) == 3
            assert result.summary['success_rate'] == 1.0
            assert result.summary['format_used'] == "ICS-UAE"
            
            # Verify all individual results are successful
            for individual_result in result.results:
                assert individual_result.success is True
                assert individual_result.face_detected is True
        
        finally:
            # Cleanup
            for temp_file in temp_images:
                os.unlink(temp_file)
    
    def test_batch_processing_mixed_results(self, controller, mock_face_detector, mock_icao_validator):
        """Test batch processing with mixed success/failure results."""
        # Create temporary images
        temp_images = []
        for i in range(3):
            image = np.ones((200, 200, 3), dtype=np.uint8) * 255
            cv2.rectangle(image, (75, 50), (125, 150), (0, 0, 0), -1)
            
            with tempfile.NamedTemporaryFile(suffix=f'_test_{i}.jpg', delete=False) as f:
                cv2.imwrite(f.name, image)
                temp_images.append(f.name)
        
        # Add a non-existent file to cause failure
        temp_images.append("nonexistent.jpg")
        
        try:
            controller._face_detector = mock_face_detector
            controller._icao_validator = mock_icao_validator
            
            result = controller.batch_process(temp_images, "ICS-UAE")
            
            assert result.total_images == 4
            assert result.successful == 3
            assert result.failed == 1
            assert len(result.results) == 4
            assert result.summary['success_rate'] == 0.75
            
            # Check that the last result (nonexistent file) failed
            assert result.results[-1].success is False
            assert "Image file not found" in result.results[-1].issues
        
        finally:
            # Cleanup existing files
            for temp_file in temp_images[:-1]:  # Skip the nonexistent file
                os.unlink(temp_file)
    
    def test_validate_only(self, controller, temp_image, mock_face_detector, mock_icao_validator):
        """Test validation-only functionality."""
        controller._face_detector = mock_face_detector
        controller._icao_validator = mock_icao_validator
        
        result = controller.validate_only(temp_image, "ICS-UAE")
        
        assert isinstance(result, ValidationResult)
        assert result.success is True
        assert result.face_detected is True
        assert result.compliance_score == 95.0
        assert result.passes_requirements is True
    
    def test_error_handling_and_recovery(self, controller, temp_image):
        """Test error handling and recovery mechanisms."""
        # Mock face detector to raise exception
        mock_face_detector = Mock()
        mock_face_detector.detect_face.side_effect = Exception("Face detection failed")
        
        controller._face_detector = mock_face_detector
        
        result = controller.process_image(temp_image, "ICS-UAE")
        
        assert result.success is False
        assert "Processing error" in result.issues[0]
        assert result.error_message is not None
        assert result.processing_time > 0
    
    def test_statistics_tracking(self, controller, temp_image, mock_face_detector, mock_icao_validator):
        """Test processing statistics tracking."""
        controller._face_detector = mock_face_detector
        controller._icao_validator = mock_icao_validator
        
        # Process some images
        controller.process_image(temp_image, "ICS-UAE")
        controller.process_image("nonexistent.jpg", "ICS-UAE")  # This will fail
        
        stats = controller.get_processing_stats()
        
        assert stats['total_processed'] == 2
        assert stats['successful'] == 1
        assert stats['failed'] == 1
        assert stats['success_rate'] == 0.5
        assert stats['failure_rate'] == 0.5
        assert stats['average_processing_time'] > 0
    
    def test_health_check(self, controller):
        """Test health check functionality."""
        health = controller.health_check()
        
        assert 'overall_healthy' in health
        assert 'components' in health
        assert 'timestamp' in health
        
        # Check that all expected components are included
        expected_components = ['config_manager', 'face_detector', 'icao_validator', 'autofix_engine']
        for component in expected_components:
            assert component in health['components']
            assert 'healthy' in health['components'][component]
            assert 'message' in health['components'][component]
    
    def test_configuration_reload(self, controller):
        """Test configuration reloading."""
        # This should not raise an exception
        controller.reload_configuration()
        
        # Verify that validator is reset (will be reinitialized with new config)
        assert controller._icao_validator is None
    
    def test_format_validation(self, controller):
        """Test format configuration validation."""
        # Test valid format
        assert controller.validate_format_config("ICS-UAE") is True
        
        # Test invalid format
        assert controller.validate_format_config("NONEXISTENT") is False
    
    def test_lazy_loading_components(self, controller):
        """Test that components are lazy-loaded correctly."""
        # Initially, components should be None
        assert controller._face_detector is None
        assert controller._icao_validator is None
        
        # Accessing properties should initialize them
        face_detector = controller.face_detector
        icao_validator = controller.icao_validator
        
        assert face_detector is not None
        assert icao_validator is not None
        
        # Subsequent access should return the same instances
        assert controller.face_detector is face_detector
        assert controller.icao_validator is icao_validator
    
    @patch('cv2.imread')
    def test_image_loading_optimization(self, mock_imread, controller):
        """Test image loading with size optimization."""
        # Create a large mock image
        large_image = np.ones((4000, 3000, 3), dtype=np.uint8) * 255
        mock_imread.return_value = large_image
        
        # Mock the resize function to track if it's called
        with patch('cv2.resize') as mock_resize:
            mock_resize.return_value = np.ones((2000, 1500, 3), dtype=np.uint8) * 255
            
            image = controller._load_image("test.jpg")
            
            # Verify that resize was called for large image
            mock_resize.assert_called_once()
            assert image is not None
    
    def test_auto_fix_placeholder(self, controller, temp_image):
        """Test auto-fix functionality (placeholder until task 5)."""
        result = controller.auto_fix_image(temp_image, ["Background color incorrect"], "ICS-UAE")
        
        # Should return a result indicating auto-fix is not implemented
        assert result.success is False
        assert "Auto-fix engine not available" in result.error_message
        assert result.before_score >= 0
        assert result.after_score >= 0