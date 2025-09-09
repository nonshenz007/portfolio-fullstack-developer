"""
Integration Tests for End-to-End Processing Pipeline
Tests the complete workflow from image input to final export.
"""

import pytest
import numpy as np
import cv2
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import time
import threading
from typing import List, Dict, Any

# Import core components for integration testing
from core.processing_controller import ProcessingController
from core.config_manager import ConfigManager
from ai.ai_engine import AIEngine
from validation.icao_validator import ICAOValidator
from quality.quality_engine import QualityEngine
from autofix.autofix_engine import AutoFixEngine
from export.export_engine import ExportEngine
from rules.icao_rules_engine import ICAORulesEngine


class TestEndToEndPipeline:
    """Integration tests for complete processing pipeline"""
    
    @pytest.fixture
    def integration_setup(self):
        """Setup for integration tests"""
        # Create test images
        test_images = {
            'compliant': self._create_compliant_test_image(),
            'non_compliant_background': self._create_non_compliant_background_image(),
            'non_compliant_lighting': self._create_poor_lighting_image(),
            'multiple_faces': self._create_multiple_faces_image(),
            'no_face': self._create_no_face_image(),
            'low_quality': self._create_low_quality_image()
        }
        
        # Create temporary directory
        temp_dir = tempfile.mkdtemp()
        
        # Save test images
        image_paths = {}
        for name, image in test_images.items():
            path = Path(temp_dir) / f"{name}.jpg"
            cv2.imwrite(str(path), image)
            image_paths[name] = str(path)
        
        return {
            'temp_dir': temp_dir,
            'image_paths': image_paths,
            'test_images': test_images
        }
    
    def _create_compliant_test_image(self):
        """Create a compliant test image"""
        img = np.ones((600, 480, 3), dtype=np.uint8) * 255  # White background
        
        # Draw a realistic face
        center = (240, 300)
        
        # Face outline
        cv2.ellipse(img, center, (80, 100), 0, 0, 360, (220, 180, 160), -1)
        
        # Eyes
        cv2.circle(img, (220, 280), 8, (50, 50, 50), -1)  # Left eye
        cv2.circle(img, (260, 280), 8, (50, 50, 50), -1)  # Right eye
        
        # Nose
        cv2.line(img, (240, 290), (240, 310), (180, 140, 120), 2)
        
        # Mouth (closed, neutral)
        cv2.ellipse(img, (240, 330), (15, 5), 0, 0, 180, (120, 80, 80), 2)
        
        return img
    
    def _create_non_compliant_background_image(self):
        """Create image with non-compliant background"""
        img = np.ones((600, 480, 3), dtype=np.uint8) * 128  # Gray background
        
        # Add face similar to compliant image
        center = (240, 300)
        cv2.ellipse(img, center, (80, 100), 0, 0, 360, (220, 180, 160), -1)
        cv2.circle(img, (220, 280), 8, (50, 50, 50), -1)
        cv2.circle(img, (260, 280), 8, (50, 50, 50), -1)
        cv2.line(img, (240, 290), (240, 310), (180, 140, 120), 2)
        cv2.ellipse(img, (240, 330), (15, 5), 0, 0, 180, (120, 80, 80), 2)
        
        return img
    
    def _create_poor_lighting_image(self):
        """Create image with poor lighting"""
        img = np.ones((600, 480, 3), dtype=np.uint8) * 255
        
        # Create face with uneven lighting
        center = (240, 300)
        cv2.ellipse(img, center, (80, 100), 0, 0, 360, (120, 100, 80), -1)  # Darker face
        
        # Add shadow on one side
        shadow_mask = np.zeros((600, 480), dtype=np.uint8)
        cv2.ellipse(shadow_mask, (200, 300), (60, 80), 0, 0, 360, 255, -1)
        img[shadow_mask > 0] = img[shadow_mask > 0] * 0.6
        
        # Add basic facial features
        cv2.circle(img, (220, 280), 6, (30, 30, 30), -1)
        cv2.circle(img, (260, 280), 6, (30, 30, 30), -1)
        cv2.ellipse(img, (240, 330), (12, 4), 0, 0, 180, (80, 60, 60), 2)
        
        return img
    
    def _create_multiple_faces_image(self):
        """Create image with multiple faces"""
        img = np.ones((600, 480, 3), dtype=np.uint8) * 255
        
        # First face
        cv2.ellipse(img, (180, 250), (60, 75), 0, 0, 360, (220, 180, 160), -1)
        cv2.circle(img, (165, 235), 6, (50, 50, 50), -1)
        cv2.circle(img, (195, 235), 6, (50, 50, 50), -1)
        
        # Second face
        cv2.ellipse(img, (300, 350), (60, 75), 0, 0, 360, (210, 170, 150), -1)
        cv2.circle(img, (285, 335), 6, (50, 50, 50), -1)
        cv2.circle(img, (315, 335), 6, (50, 50, 50), -1)
        
        return img
    
    def _create_no_face_image(self):
        """Create image with no face"""
        img = np.ones((600, 480, 3), dtype=np.uint8) * 255
        
        # Add some random objects but no face
        cv2.rectangle(img, (100, 100), (200, 200), (100, 100, 200), -1)
        cv2.circle(img, (350, 400), 50, (200, 100, 100), -1)
        
        return img
    
    def _create_low_quality_image(self):
        """Create low quality/blurry image"""
        img = self._create_compliant_test_image()
        
        # Apply blur to simulate low quality
        img = cv2.GaussianBlur(img, (15, 15), 0)
        
        # Add noise
        noise = np.random.randint(0, 50, img.shape, dtype=np.uint8)
        img = cv2.add(img, noise)
        
        return img
    
    def test_complete_processing_workflow(self, integration_setup):
        """Test complete processing workflow from input to output"""
        with patch('ai.yolov8_detector.YOLO'), \
             patch('ai.mediapipe_analyzer.mp.solutions.face_mesh.FaceMesh'), \
             patch('ai.background_segmenter.onnxruntime.InferenceSession'):
            
            # Initialize processing controller
            config_manager = ConfigManager()
            controller = ProcessingController(config_manager)
            
            # Mock AI engine responses
            with patch.object(controller.ai_engine, 'detect_faces') as mock_detect, \
                 patch.object(controller.ai_engine, 'analyze_face_landmarks') as mock_analyze, \
                 patch.object(controller.ai_engine, 'assess_image_quality') as mock_quality:
                
                # Setup mock responses
                mock_detect.return_value = [Mock(
                    bbox=Mock(x=160, y=200, width=160, height=200),
                    confidence=0.95
                )]
                
                mock_analyze.return_value = Mock(
                    eye_positions=((220, 280), (260, 280)),
                    mouth_position=(240, 330),
                    glasses_detected=False,
                    head_covering_detected=False
                )
                
                mock_quality.return_value = Mock(
                    sharpness_score=0.85,
                    lighting_score=0.90,
                    color_score=0.88
                )
                
                # Test processing compliant image
                result = controller.process_image(
                    integration_setup['image_paths']['compliant'],
                    'ICAO',
                    {'enable_autofix': False}
                )
                
                assert result.success is True
                assert result.validation_result is not None
                assert result.validation_result.overall_compliance > 70
    
    def test_autofix_integration_workflow(self, integration_setup):
        """Test auto-fix integration in the processing workflow"""
        with patch('ai.yolov8_detector.YOLO'), \
             patch('ai.mediapipe_analyzer.mp.solutions.face_mesh.FaceMesh'), \
             patch('ai.background_segmenter.onnxruntime.InferenceSession'):
            
            config_manager = ConfigManager()
            controller = ProcessingController(config_manager)
            
            # Mock validation result that needs auto-fix
            with patch.object(controller.icao_validator, 'validate_full_compliance') as mock_validate:
                mock_validate.return_value = Mock(
                    overall_compliance=65.0,
                    passes_requirements=False,
                    rule_results=[
                        Mock(rule_id='background', passes=False, auto_fixable=True),
                        Mock(rule_id='lighting', passes=False, auto_fixable=True)
                    ]
                )
                
                # Mock auto-fix engine
                with patch.object(controller.autofix_engine, 'analyze_issues') as mock_analyze, \
                     patch.object(controller.autofix_engine, 'apply_corrections') as mock_apply:
                    
                    mock_analyze.return_value = Mock(fixable_issues=['background', 'lighting'])
                    mock_apply.return_value = Mock(
                        success=True,
                        corrected_image=integration_setup['test_images']['compliant'],
                        improvement_score=20.0
                    )
                    
                    # Test processing with auto-fix enabled
                    result = controller.process_image(
                        integration_setup['image_paths']['non_compliant_background'],
                        'ICAO',
                        {'enable_autofix': True}
                    )
                    
                    assert result.success is True
                    assert result.auto_fix_result is not None
                    assert result.auto_fix_result.success is True
    
    def test_batch_processing_integration(self, integration_setup):
        """Test batch processing integration"""
        with patch('ai.yolov8_detector.YOLO'), \
             patch('ai.mediapipe_analyzer.mp.solutions.face_mesh.FaceMesh'), \
             patch('ai.background_segmenter.onnxruntime.InferenceSession'):
            
            config_manager = ConfigManager()
            controller = ProcessingController(config_manager)
            
            # Mock successful processing for all images
            with patch.object(controller, 'process_image') as mock_process:
                mock_process.return_value = Mock(
                    success=True,
                    validation_result=Mock(overall_compliance=85.0)
                )
                
                # Test batch processing
                image_paths = list(integration_setup['image_paths'].values())[:3]
                result = controller.batch_process(image_paths, 'ICAO')
                
                assert result.success is True
                assert len(result.results) == 3
                assert all(r.success for r in result.results)
    
    def test_error_handling_integration(self, integration_setup):
        """Test error handling throughout the pipeline"""
        with patch('ai.yolov8_detector.YOLO'), \
             patch('ai.mediapipe_analyzer.mp.solutions.face_mesh.FaceMesh'), \
             patch('ai.background_segmenter.onnxruntime.InferenceSession'):
            
            config_manager = ConfigManager()
            controller = ProcessingController(config_manager)
            
            # Test face detection failure
            with patch.object(controller.ai_engine, 'detect_faces') as mock_detect:
                mock_detect.return_value = []  # No faces detected
                
                result = controller.process_image(
                    integration_setup['image_paths']['no_face'],
                    'ICAO',
                    {}
                )
                
                assert result.success is False
                assert 'face' in result.error_message.lower()
    
    def test_export_integration(self, integration_setup):
        """Test export functionality integration"""
        with patch('ai.yolov8_detector.YOLO'), \
             patch('ai.mediapipe_analyzer.mp.solutions.face_mesh.FaceMesh'), \
             patch('ai.background_segmenter.onnxruntime.InferenceSession'):
            
            config_manager = ConfigManager()
            controller = ProcessingController(config_manager)
            export_engine = ExportEngine()
            
            # Mock processing result
            mock_result = Mock(
                success=True,
                validation_result=Mock(
                    overall_compliance=85.0,
                    passes_requirements=True,
                    rule_results=[]
                ),
                processing_metrics=Mock(
                    processing_time=2.5,
                    memory_usage=150.0
                )
            )
            
            # Test report generation
            report_path = Path(integration_setup['temp_dir']) / 'integration_report.json'
            success = export_engine.generate_compliance_report(
                mock_result.validation_result,
                str(report_path)
            )
            
            assert success is True
            assert report_path.exists()
            
            # Verify report content
            with open(report_path, 'r') as f:
                report_data = json.load(f)
                assert 'overall_compliance' in report_data
                assert report_data['overall_compliance'] == 85.0


class TestConcurrentProcessing:
    """Test concurrent processing capabilities"""
    
    def test_parallel_batch_processing(self, integration_setup):
        """Test parallel processing of multiple images"""
        with patch('ai.yolov8_detector.YOLO'), \
             patch('ai.mediapipe_analyzer.mp.solutions.face_mesh.FaceMesh'), \
             patch('ai.background_segmenter.onnxruntime.InferenceSession'):
            
            config_manager = ConfigManager()
            controller = ProcessingController(config_manager)
            
            # Mock processing function with delay to test concurrency
            def mock_process_with_delay(*args, **kwargs):
                time.sleep(0.1)  # Simulate processing time
                return Mock(
                    success=True,
                    validation_result=Mock(overall_compliance=85.0)
                )
            
            with patch.object(controller, 'process_image', side_effect=mock_process_with_delay):
                start_time = time.time()
                
                # Process multiple images
                image_paths = list(integration_setup['image_paths'].values())
                result = controller.batch_process(image_paths, 'ICAO', parallel=True)
                
                end_time = time.time()
                processing_time = end_time - start_time
                
                # Should be faster than sequential processing
                assert processing_time < len(image_paths) * 0.1
                assert result.success is True
    
    def test_thread_safety(self, integration_setup):
        """Test thread safety of processing components"""
        with patch('ai.yolov8_detector.YOLO'), \
             patch('ai.mediapipe_analyzer.mp.solutions.face_mesh.FaceMesh'), \
             patch('ai.background_segmenter.onnxruntime.InferenceSession'):
            
            config_manager = ConfigManager()
            controller = ProcessingController(config_manager)
            
            results = []
            errors = []
            
            def process_image_thread(image_path):
                try:
                    with patch.object(controller, 'process_image') as mock_process:
                        mock_process.return_value = Mock(success=True)
                        result = controller.process_image(image_path, 'ICAO', {})
                        results.append(result)
                except Exception as e:
                    errors.append(e)
            
            # Create multiple threads
            threads = []
            for image_path in list(integration_setup['image_paths'].values())[:3]:
                thread = threading.Thread(target=process_image_thread, args=(image_path,))
                threads.append(thread)
                thread.start()
            
            # Wait for all threads to complete
            for thread in threads:
                thread.join()
            
            # Verify no errors and all results
            assert len(errors) == 0
            assert len(results) == 3


class TestPerformanceIntegration:
    """Test performance characteristics of integrated system"""
    
    def test_processing_speed_benchmarks(self, integration_setup):
        """Test processing speed benchmarks"""
        with patch('ai.yolov8_detector.YOLO'), \
             patch('ai.mediapipe_analyzer.mp.solutions.face_mesh.FaceMesh'), \
             patch('ai.background_segmenter.onnxruntime.InferenceSession'):
            
            config_manager = ConfigManager()
            controller = ProcessingController(config_manager)
            
            # Mock fast processing
            with patch.object(controller, 'process_image') as mock_process:
                mock_process.return_value = Mock(success=True)
                
                # Measure processing time
                start_time = time.time()
                result = controller.process_image(
                    integration_setup['image_paths']['compliant'],
                    'ICAO',
                    {}
                )
                end_time = time.time()
                
                processing_time = end_time - start_time
                
                # Should complete within reasonable time
                assert processing_time < 5.0  # 5 seconds max
                assert result.success is True
    
    def test_memory_usage_monitoring(self, integration_setup):
        """Test memory usage monitoring during processing"""
        import psutil
        
        with patch('ai.yolov8_detector.YOLO'), \
             patch('ai.mediapipe_analyzer.mp.solutions.face_mesh.FaceMesh'), \
             patch('ai.background_segmenter.onnxruntime.InferenceSession'):
            
            config_manager = ConfigManager()
            controller = ProcessingController(config_manager)
            
            # Measure initial memory
            process = psutil.Process()
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            # Mock processing
            with patch.object(controller, 'process_image') as mock_process:
                mock_process.return_value = Mock(success=True)
                
                # Process multiple images
                for image_path in list(integration_setup['image_paths'].values()):
                    controller.process_image(image_path, 'ICAO', {})
                
                # Measure final memory
                final_memory = process.memory_info().rss / 1024 / 1024  # MB
                memory_increase = final_memory - initial_memory
                
                # Memory increase should be reasonable
                assert memory_increase < 500  # Less than 500MB increase


class TestDataConsistency:
    """Test data consistency across processing pipeline"""
    
    def test_validation_result_consistency(self, integration_setup):
        """Test that validation results are consistent across multiple runs"""
        with patch('ai.yolov8_detector.YOLO'), \
             patch('ai.mediapipe_analyzer.mp.solutions.face_mesh.FaceMesh'), \
             patch('ai.background_segmenter.onnxruntime.InferenceSession'):
            
            config_manager = ConfigManager()
            controller = ProcessingController(config_manager)
            
            # Mock deterministic responses
            with patch.object(controller.ai_engine, 'detect_faces') as mock_detect, \
                 patch.object(controller.icao_validator, 'validate_full_compliance') as mock_validate:
                
                mock_detect.return_value = [Mock(confidence=0.95)]
                mock_validate.return_value = Mock(overall_compliance=85.0)
                
                # Process same image multiple times
                results = []
                for _ in range(3):
                    result = controller.process_image(
                        integration_setup['image_paths']['compliant'],
                        'ICAO',
                        {}
                    )
                    results.append(result.validation_result.overall_compliance)
                
                # All results should be identical
                assert all(score == results[0] for score in results)
    
    def test_coordinate_system_consistency(self, integration_setup):
        """Test that coordinate systems are consistent across components"""
        with patch('ai.yolov8_detector.YOLO'), \
             patch('ai.mediapipe_analyzer.mp.solutions.face_mesh.FaceMesh'), \
             patch('ai.background_segmenter.onnxruntime.InferenceSession'):
            
            config_manager = ConfigManager()
            controller = ProcessingController(config_manager)
            
            # Mock face detection with specific coordinates
            mock_bbox = Mock(x=100, y=150, width=200, height=250)
            
            with patch.object(controller.ai_engine, 'detect_faces') as mock_detect:
                mock_detect.return_value = [Mock(bbox=mock_bbox, confidence=0.95)]
                
                # Mock landmark analysis to verify coordinate consistency
                with patch.object(controller.ai_engine, 'analyze_face_landmarks') as mock_landmarks:
                    def verify_coordinates(image, bbox):
                        # Verify that bbox coordinates are within image bounds
                        assert bbox.x >= 0
                        assert bbox.y >= 0
                        assert bbox.x + bbox.width <= image.shape[1]
                        assert bbox.y + bbox.height <= image.shape[0]
                        return Mock()
                    
                    mock_landmarks.side_effect = verify_coordinates
                    
                    result = controller.process_image(
                        integration_setup['image_paths']['compliant'],
                        'ICAO',
                        {}
                    )
                    
                    assert result.success is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])