"""
Edge Case Testing for Error Handling and Recovery
Tests system behavior under edge cases, error conditions, and recovery scenarios.
"""

import pytest
import numpy as np
import cv2
import tempfile
import threading
import time
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from typing import List, Dict, Any
import psutil
import os

from core.processing_controller import ProcessingController
from core.config_manager import ConfigManager
from ai.ai_engine import AIEngine
from validation.icao_validator import ICAOValidator
from quality.quality_engine import QualityEngine
from autofix.autofix_engine import AutoFixEngine
from utils.error_handler import ProcessingErrorHandler


class EdgeCaseImageGenerator:
    """Generate edge case images for testing"""
    
    @staticmethod
    def create_corrupted_image():
        """Create corrupted image data"""
        # Random bytes that don't form a valid image
        return np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
    
    @staticmethod
    def create_extreme_size_images():
        """Create extremely large and small images"""
        return {
            'tiny': np.ones((1, 1, 3), dtype=np.uint8) * 128,
            'very_small': np.ones((10, 10, 3), dtype=np.uint8) * 128,
            'very_large': np.ones((8000, 6000, 3), dtype=np.uint8) * 128,
            'extreme_aspect_ratio': np.ones((100, 5000, 3), dtype=np.uint8) * 128
        }
    
    @staticmethod
    def create_unusual_format_images():
        """Create images with unusual formats"""
        return {
            'grayscale': np.ones((400, 400), dtype=np.uint8) * 128,
            'rgba': np.ones((400, 400, 4), dtype=np.uint8) * 128,
            'float32': np.ones((400, 400, 3), dtype=np.float32) * 0.5,
            'uint16': np.ones((400, 400, 3), dtype=np.uint16) * 32768
        }
    
    @staticmethod
    def create_problematic_content_images():
        """Create images with problematic content"""
        base_img = np.ones((600, 480, 3), dtype=np.uint8) * 255
        
        return {
            'all_black': np.zeros((600, 480, 3), dtype=np.uint8),
            'all_white': np.ones((600, 480, 3), dtype=np.uint8) * 255,
            'single_color': np.ones((600, 480, 3), dtype=np.uint8) * [100, 150, 200],
            'high_contrast': np.tile(np.array([[[0, 0, 0], [255, 255, 255]]], dtype=np.uint8), (300, 240, 1)),
            'extreme_noise': np.random.randint(0, 255, (600, 480, 3), dtype=np.uint8),
            'geometric_patterns': base_img  # Will be modified below
        }


class TestFileHandlingEdgeCases:
    """Test edge cases in file handling"""
    
    def test_nonexistent_file_handling(self):
        """Test handling of nonexistent files"""
        with patch('ai.yolov8_detector.YOLO'), \
             patch('ai.mediapipe_analyzer.mp.solutions.face_mesh.FaceMesh'), \
             patch('ai.background_segmenter.onnxruntime.InferenceSession'):
            
            config_manager = ConfigManager()
            controller = ProcessingController(config_manager)
            
            # Test nonexistent file
            result = controller.process_image('/nonexistent/path/image.jpg', 'ICAO', {})
            
            assert result is not None
            assert result.success is False
            assert 'file not found' in result.error_message.lower() or 'not exist' in result.error_message.lower()
    
    def test_corrupted_file_handling(self):
        """Test handling of corrupted image files"""
        with patch('ai.yolov8_detector.YOLO'), \
             patch('ai.mediapipe_analyzer.mp.solutions.face_mesh.FaceMesh'), \
             patch('ai.background_segmenter.onnxruntime.InferenceSession'):
            
            config_manager = ConfigManager()
            controller = ProcessingController(config_manager)
            
            # Create corrupted file
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
                temp_file.write(b'This is not a valid image file')
                temp_file.flush()
                
                result = controller.process_image(temp_file.name, 'ICAO', {})
                
                assert result is not None
                assert result.success is False
                assert 'corrupt' in result.error_message.lower() or 'invalid' in result.error_message.lower()
    
    def test_permission_denied_handling(self):
        """Test handling of permission denied errors"""
        with patch('ai.yolov8_detector.YOLO'), \
             patch('ai.mediapipe_analyzer.mp.solutions.face_mesh.FaceMesh'), \
             patch('ai.background_segmenter.onnxruntime.InferenceSession'):
            
            config_manager = ConfigManager()
            controller = ProcessingController(config_manager)
            
            # Create file and remove read permissions (Unix-like systems)
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
                # Create valid image
                test_img = np.ones((100, 100, 3), dtype=np.uint8) * 128
                cv2.imwrite(temp_file.name, test_img)
                
                try:
                    # Remove read permissions
                    os.chmod(temp_file.name, 0o000)
                    
                    result = controller.process_image(temp_file.name, 'ICAO', {})
                    
                    assert result is not None
                    assert result.success is False
                    
                finally:
                    # Restore permissions for cleanup
                    os.chmod(temp_file.name, 0o644)
    
    def test_disk_space_handling(self):
        """Test handling of insufficient disk space"""
        with patch('ai.yolov8_detector.YOLO'), \
             patch('ai.mediapipe_analyzer.mp.solutions.face_mesh.FaceMesh'), \
             patch('ai.background_segmenter.onnxruntime.InferenceSession'):
            
            config_manager = ConfigManager()
            controller = ProcessingController(config_manager)
            
            # Mock disk space check to simulate full disk
            with patch('shutil.disk_usage') as mock_disk_usage:
                mock_disk_usage.return_value = (1000, 0, 0)  # total, used, free
                
                test_img = np.ones((100, 100, 3), dtype=np.uint8) * 128
                
                with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
                    cv2.imwrite(temp_file.name, test_img)
                    
                    # Mock export to fail due to disk space
                    with patch.object(controller, '_save_processed_image') as mock_save:
                        mock_save.side_effect = OSError("No space left on device")
                        
                        result = controller.process_image(temp_file.name, 'ICAO', {})
                        
                        # Should handle gracefully
                        assert result is not None


class TestImageFormatEdgeCases:
    """Test edge cases with different image formats"""
    
    def test_extreme_image_sizes(self):
        """Test handling of extremely large and small images"""
        with patch('ai.yolov8_detector.YOLO'), \
             patch('ai.mediapipe_analyzer.mp.solutions.face_mesh.FaceMesh'), \
             patch('ai.background_segmenter.onnxruntime.InferenceSession'):
            
            config_manager = ConfigManager()
            controller = ProcessingController(config_manager)
            
            # Mock AI responses
            controller.ai_engine.detect_faces = Mock(return_value=[])
            
            extreme_images = EdgeCaseImageGenerator.create_extreme_size_images()
            
            for size_name, image in extreme_images.items():
                with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
                    try:
                        cv2.imwrite(temp_file.name, image)
                        result = controller.process_image(temp_file.name, 'ICAO', {})
                        
                        # Should handle gracefully, either process or fail gracefully
                        assert result is not None
                        
                        if size_name in ['tiny', 'very_small']:
                            # Very small images should fail with appropriate message
                            assert result.success is False
                            assert 'size' in result.error_message.lower() or 'dimension' in result.error_message.lower()
                        
                    except Exception as e:
                        # Should not raise unhandled exceptions
                        pytest.fail(f"Unhandled exception for {size_name}: {e}")
    
    def test_unusual_image_formats(self):
        """Test handling of unusual image formats"""
        with patch('ai.yolov8_detector.YOLO'), \
             patch('ai.mediapipe_analyzer.mp.solutions.face_mesh.FaceMesh'), \
             patch('ai.background_segmenter.onnxruntime.InferenceSession'):
            
            config_manager = ConfigManager()
            controller = ProcessingController(config_manager)
            
            # Mock AI responses
            controller.ai_engine.detect_faces = Mock(return_value=[])
            
            unusual_images = EdgeCaseImageGenerator.create_unusual_format_images()
            
            for format_name, image in unusual_images.items():
                with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
                    try:
                        # Convert to uint8 BGR for OpenCV
                        if image.dtype != np.uint8:
                            if image.dtype == np.float32:
                                image = (image * 255).astype(np.uint8)
                            elif image.dtype == np.uint16:
                                image = (image / 256).astype(np.uint8)
                        
                        if len(image.shape) == 2:  # Grayscale
                            image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
                        elif image.shape[2] == 4:  # RGBA
                            image = cv2.cvtColor(image, cv2.COLOR_RGBA2BGR)
                        
                        cv2.imwrite(temp_file.name, image)
                        result = controller.process_image(temp_file.name, 'ICAO', {})
                        
                        # Should handle gracefully
                        assert result is not None
                        
                    except Exception as e:
                        # Should not raise unhandled exceptions
                        pytest.fail(f"Unhandled exception for {format_name}: {e}")
    
    def test_problematic_image_content(self):
        """Test handling of problematic image content"""
        with patch('ai.yolov8_detector.YOLO'), \
             patch('ai.mediapipe_analyzer.mp.solutions.face_mesh.FaceMesh'), \
             patch('ai.background_segmenter.onnxruntime.InferenceSession'):
            
            config_manager = ConfigManager()
            controller = ProcessingController(config_manager)
            
            # Mock AI responses
            controller.ai_engine.detect_faces = Mock(return_value=[])
            
            problematic_images = EdgeCaseImageGenerator.create_problematic_content_images()
            
            for content_name, image in problematic_images.items():
                with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
                    cv2.imwrite(temp_file.name, image)
                    
                    result = controller.process_image(temp_file.name, 'ICAO', {})
                    
                    # Should handle gracefully
                    assert result is not None
                    
                    if content_name in ['all_black', 'all_white', 'extreme_noise']:
                        # These should likely fail validation but not crash
                        if result.success:
                            assert result.validation_result.overall_compliance < 50


class TestAIModelEdgeCases:
    """Test edge cases in AI model behavior"""
    
    def test_face_detection_failures(self):
        """Test handling of face detection failures"""
        with patch('ai.yolov8_detector.YOLO') as mock_yolo:
            # Test model loading failure
            mock_yolo.side_effect = Exception("Model loading failed")
            
            with pytest.raises(Exception):
                detector = YOLOv8FaceDetector()
            
            # Test detection failure
            mock_yolo.side_effect = None
            mock_yolo.return_value.side_effect = Exception("Detection failed")
            
            detector = YOLOv8FaceDetector()
            
            test_image = np.ones((400, 400, 3), dtype=np.uint8) * 128
            
            # Should handle detection failure gracefully
            with pytest.raises(Exception):
                faces = detector.detect_faces(test_image)
    
    def test_mediapipe_failures(self):
        """Test handling of MediaPipe failures"""
        with patch('ai.mediapipe_analyzer.mp.solutions.face_mesh.FaceMesh') as mock_mp:
            # Test initialization failure
            mock_mp.side_effect = Exception("MediaPipe initialization failed")
            
            with pytest.raises(Exception):
                analyzer = MediaPipeAnalyzer()
            
            # Test analysis failure
            mock_mp.side_effect = None
            mock_face_mesh = Mock()
            mock_face_mesh.process.side_effect = Exception("Analysis failed")
            mock_mp.return_value = mock_face_mesh
            
            analyzer = MediaPipeAnalyzer()
            test_image = np.ones((400, 400, 3), dtype=np.uint8) * 128
            
            # Should handle analysis failure gracefully
            with pytest.raises(Exception):
                result = analyzer.analyze_face_landmarks(test_image, Mock())
    
    def test_model_memory_exhaustion(self):
        """Test handling of model memory exhaustion"""
        with patch('ai.yolov8_detector.YOLO'), \
             patch('ai.mediapipe_analyzer.mp.solutions.face_mesh.FaceMesh'), \
             patch('ai.background_segmenter.onnxruntime.InferenceSession'):
            
            config_manager = ConfigManager()
            controller = ProcessingController(config_manager)
            
            # Mock memory error during AI processing
            controller.ai_engine.detect_faces = Mock(side_effect=MemoryError("Out of memory"))
            
            test_image = np.ones((400, 400, 3), dtype=np.uint8) * 128
            
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
                cv2.imwrite(temp_file.name, test_image)
                
                result = controller.process_image(temp_file.name, 'ICAO', {})
                
                # Should handle memory error gracefully
                assert result is not None
                assert result.success is False
                assert 'memory' in result.error_message.lower()


class TestConcurrencyEdgeCases:
    """Test edge cases in concurrent processing"""
    
    def test_race_condition_handling(self):
        """Test handling of race conditions"""
        with patch('ai.yolov8_detector.YOLO'), \
             patch('ai.mediapipe_analyzer.mp.solutions.face_mesh.FaceMesh'), \
             patch('ai.background_segmenter.onnxruntime.InferenceSession'):
            
            config_manager = ConfigManager()
            controller = ProcessingController(config_manager)
            
            # Mock AI responses with delays to create race conditions
            def delayed_detect(*args, **kwargs):
                time.sleep(0.1)
                return [Mock(confidence=0.95)]
            
            controller.ai_engine.detect_faces = delayed_detect
            controller.ai_engine.analyze_face_landmarks = Mock(return_value=Mock())
            controller.ai_engine.assess_image_quality = Mock(return_value=Mock())
            
            # Create test image
            test_image = np.ones((400, 400, 3), dtype=np.uint8) * 128
            
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
                cv2.imwrite(temp_file.name, test_image)
                
                results = []
                threads = []
                
                def process_concurrent(result_list):
                    try:
                        result = controller.process_image(temp_file.name, 'ICAO', {})
                        result_list.append(result)
                    except Exception as e:
                        result_list.append(e)
                
                # Start multiple concurrent processes
                for _ in range(5):
                    thread = threading.Thread(target=process_concurrent, args=(results,))
                    threads.append(thread)
                    thread.start()
                
                # Wait for all threads
                for thread in threads:
                    thread.join()
                
                # Check results
                assert len(results) == 5
                
                # Should not have unhandled exceptions
                for result in results:
                    assert not isinstance(result, Exception), f"Unhandled exception: {result}"
    
    def test_resource_contention(self):
        """Test handling of resource contention"""
        with patch('ai.yolov8_detector.YOLO'), \
             patch('ai.mediapipe_analyzer.mp.solutions.face_mesh.FaceMesh'), \
             patch('ai.background_segmenter.onnxruntime.InferenceSession'):
            
            config_manager = ConfigManager()
            
            # Create multiple controllers to simulate resource contention
            controllers = [ProcessingController(config_manager) for _ in range(3)]
            
            for controller in controllers:
                controller.ai_engine.detect_faces = Mock(return_value=[Mock(confidence=0.95)])
                controller.ai_engine.analyze_face_landmarks = Mock(return_value=Mock())
                controller.ai_engine.assess_image_quality = Mock(return_value=Mock())
            
            # Create test images
            test_images = []
            for i in range(3):
                with tempfile.NamedTemporaryFile(suffix=f'_{i}.jpg', delete=False) as temp_file:
                    test_image = np.ones((400, 400, 3), dtype=np.uint8) * (128 + i * 10)
                    cv2.imwrite(temp_file.name, test_image)
                    test_images.append(temp_file.name)
            
            results = []
            threads = []
            
            def process_with_controller(controller, image_path, result_list):
                try:
                    result = controller.process_image(image_path, 'ICAO', {})
                    result_list.append(result)
                except Exception as e:
                    result_list.append(e)
            
            # Start concurrent processing with different controllers
            for controller, image_path in zip(controllers, test_images):
                thread = threading.Thread(
                    target=process_with_controller,
                    args=(controller, image_path, results)
                )
                threads.append(thread)
                thread.start()
            
            # Wait for completion
            for thread in threads:
                thread.join()
            
            # Verify results
            assert len(results) == 3
            for result in results:
                assert not isinstance(result, Exception)
                assert result.success is True


class TestMemoryEdgeCases:
    """Test edge cases related to memory management"""
    
    def test_memory_leak_prevention(self):
        """Test prevention of memory leaks"""
        with patch('ai.yolov8_detector.YOLO'), \
             patch('ai.mediapipe_analyzer.mp.solutions.face_mesh.FaceMesh'), \
             patch('ai.background_segmenter.onnxruntime.InferenceSession'):
            
            config_manager = ConfigManager()
            controller = ProcessingController(config_manager)
            
            # Mock AI responses
            controller.ai_engine.detect_faces = Mock(return_value=[Mock(confidence=0.95)])
            controller.ai_engine.analyze_face_landmarks = Mock(return_value=Mock())
            controller.ai_engine.assess_image_quality = Mock(return_value=Mock())
            
            # Create test image
            test_image = np.ones((1000, 1000, 3), dtype=np.uint8) * 128
            
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
                cv2.imwrite(temp_file.name, test_image)
                
                # Measure initial memory
                process = psutil.Process()
                initial_memory = process.memory_info().rss / 1024 / 1024  # MB
                
                # Process image multiple times
                for i in range(10):
                    result = controller.process_image(temp_file.name, 'ICAO', {})
                    assert result.success is True
                    
                    # Force garbage collection
                    import gc
                    gc.collect()
                
                # Measure final memory
                final_memory = process.memory_info().rss / 1024 / 1024  # MB
                memory_increase = final_memory - initial_memory
                
                # Memory increase should be minimal
                assert memory_increase < 100  # Less than 100MB increase
    
    def test_large_image_memory_handling(self):
        """Test memory handling with very large images"""
        with patch('ai.yolov8_detector.YOLO'), \
             patch('ai.mediapipe_analyzer.mp.solutions.face_mesh.FaceMesh'), \
             patch('ai.background_segmenter.onnxruntime.InferenceSession'):
            
            config_manager = ConfigManager()
            controller = ProcessingController(config_manager)
            
            # Mock AI responses
            controller.ai_engine.detect_faces = Mock(return_value=[Mock(confidence=0.95)])
            controller.ai_engine.analyze_face_landmarks = Mock(return_value=Mock())
            controller.ai_engine.assess_image_quality = Mock(return_value=Mock())
            
            # Create very large image (simulated)
            # Use smaller image but mock large dimensions
            test_image = np.ones((400, 400, 3), dtype=np.uint8) * 128
            
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
                cv2.imwrite(temp_file.name, test_image)
                
                # Mock image loading to simulate large image
                with patch('cv2.imread') as mock_imread:
                    # Simulate 50MP image
                    large_image = np.ones((7000, 7000, 3), dtype=np.uint8) * 128
                    mock_imread.return_value = large_image
                    
                    try:
                        result = controller.process_image(temp_file.name, 'ICAO', {})
                        
                        # Should either process successfully or fail gracefully
                        assert result is not None
                        
                        if not result.success:
                            assert 'memory' in result.error_message.lower() or 'size' in result.error_message.lower()
                    
                    except MemoryError:
                        # Acceptable to raise MemoryError for extremely large images
                        pass


class TestConfigurationEdgeCases:
    """Test edge cases in configuration handling"""
    
    def test_missing_configuration_files(self):
        """Test handling of missing configuration files"""
        with patch('pathlib.Path.exists', return_value=False):
            # Should handle missing config gracefully
            config_manager = ConfigManager()
            config = config_manager.get_config()
            
            # Should provide default configuration
            assert config is not None
    
    def test_corrupted_configuration_files(self):
        """Test handling of corrupted configuration files"""
        with patch('builtins.open', mock_open_corrupted_json()):
            # Should handle corrupted config gracefully
            config_manager = ConfigManager()
            config = config_manager.get_config()
            
            # Should provide default configuration
            assert config is not None
    
    def test_invalid_configuration_values(self):
        """Test handling of invalid configuration values"""
        invalid_config = {
            'ai_models': {
                'yolov8_face': '/nonexistent/model.pt',
                'confidence_threshold': 'invalid_value'  # Should be float
            },
            'processing': {
                'max_image_size': -1,  # Invalid negative value
                'quality_threshold': 2.0  # Invalid value > 1.0
            }
        }
        
        with patch.object(ConfigManager, 'load_config', return_value=invalid_config):
            config_manager = ConfigManager()
            
            # Should validate and correct invalid values
            config = config_manager.get_config()
            
            assert config['processing']['max_image_size'] > 0
            assert 0 <= config['processing']['quality_threshold'] <= 1.0


class TestErrorRecoveryMechanisms:
    """Test error recovery mechanisms"""
    
    def test_automatic_retry_mechanism(self):
        """Test automatic retry on transient failures"""
        with patch('ai.yolov8_detector.YOLO'), \
             patch('ai.mediapipe_analyzer.mp.solutions.face_mesh.FaceMesh'), \
             patch('ai.background_segmenter.onnxruntime.InferenceSession'):
            
            config_manager = ConfigManager()
            controller = ProcessingController(config_manager)
            
            # Mock transient failure followed by success
            call_count = 0
            def failing_detect(*args, **kwargs):
                nonlocal call_count
                call_count += 1
                if call_count == 1:
                    raise Exception("Transient failure")
                return [Mock(confidence=0.95)]
            
            controller.ai_engine.detect_faces = failing_detect
            controller.ai_engine.analyze_face_landmarks = Mock(return_value=Mock())
            controller.ai_engine.assess_image_quality = Mock(return_value=Mock())
            
            test_image = np.ones((400, 400, 3), dtype=np.uint8) * 128
            
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
                cv2.imwrite(temp_file.name, test_image)
                
                # Should retry and succeed
                result = controller.process_image(temp_file.name, 'ICAO', {'retry_on_failure': True})
                
                assert result is not None
                assert call_count >= 2  # Should have retried
    
    def test_graceful_degradation(self):
        """Test graceful degradation when components fail"""
        with patch('ai.yolov8_detector.YOLO'), \
             patch('ai.mediapipe_analyzer.mp.solutions.face_mesh.FaceMesh'), \
             patch('ai.background_segmenter.onnxruntime.InferenceSession'):
            
            config_manager = ConfigManager()
            controller = ProcessingController(config_manager)
            
            # Mock face detection success but landmark analysis failure
            controller.ai_engine.detect_faces = Mock(return_value=[Mock(confidence=0.95)])
            controller.ai_engine.analyze_face_landmarks = Mock(side_effect=Exception("Landmark analysis failed"))
            controller.ai_engine.assess_image_quality = Mock(return_value=Mock())
            
            test_image = np.ones((400, 400, 3), dtype=np.uint8) * 128
            
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
                cv2.imwrite(temp_file.name, test_image)
                
                result = controller.process_image(temp_file.name, 'ICAO', {'allow_partial_processing': True})
                
                # Should provide partial results
                assert result is not None
                # May succeed with limited functionality or fail gracefully
    
    def test_error_context_preservation(self):
        """Test preservation of error context for debugging"""
        with patch('ai.yolov8_detector.YOLO'), \
             patch('ai.mediapipe_analyzer.mp.solutions.face_mesh.FaceMesh'), \
             patch('ai.background_segmenter.onnxruntime.InferenceSession'):
            
            config_manager = ConfigManager()
            controller = ProcessingController(config_manager)
            
            # Mock specific error
            controller.ai_engine.detect_faces = Mock(side_effect=ValueError("Invalid input dimensions"))
            
            test_image = np.ones((400, 400, 3), dtype=np.uint8) * 128
            
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
                cv2.imwrite(temp_file.name, test_image)
                
                result = controller.process_image(temp_file.name, 'ICAO', {})
                
                # Should preserve error context
                assert result is not None
                assert result.success is False
                assert 'dimensions' in result.error_message.lower()
                
                # Should include debugging information
                if hasattr(result, 'debug_info'):
                    assert result.debug_info is not None


def mock_open_corrupted_json():
    """Helper function to mock corrupted JSON file"""
    from unittest.mock import mock_open
    return mock_open(read_data='{"invalid": json content}')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])