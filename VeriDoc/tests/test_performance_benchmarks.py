"""
Performance Benchmarks for Processing Speed and Memory Usage
Tests system performance characteristics and resource utilization.
"""

import pytest
import numpy as np
import cv2
import time
import psutil
import threading
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch
from typing import List, Dict, Tuple
import statistics
import json

from core.processing_controller import ProcessingController
from core.config_manager import ConfigManager
from ai.ai_engine import AIEngine
from validation.icao_validator import ICAOValidator
from quality.quality_engine import QualityEngine
from autofix.autofix_engine import AutoFixEngine


class PerformanceMonitor:
    """Monitor system performance during testing"""
    
    def __init__(self):
        self.process = psutil.Process()
        self.measurements = []
    
    def start_monitoring(self, interval=0.1):
        """Start monitoring system resources"""
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, args=(interval,))
        self.monitor_thread.start()
    
    def stop_monitoring(self):
        """Stop monitoring and return measurements"""
        self.monitoring = False
        if hasattr(self, 'monitor_thread'):
            self.monitor_thread.join()
        return self.measurements
    
    def _monitor_loop(self, interval):
        """Monitor loop for resource tracking"""
        while self.monitoring:
            try:
                memory_mb = self.process.memory_info().rss / 1024 / 1024
                cpu_percent = self.process.cpu_percent()
                
                self.measurements.append({
                    'timestamp': time.time(),
                    'memory_mb': memory_mb,
                    'cpu_percent': cpu_percent
                })
                
                time.sleep(interval)
            except Exception:
                break
    
    def get_peak_memory(self):
        """Get peak memory usage"""
        if not self.measurements:
            return 0
        return max(m['memory_mb'] for m in self.measurements)
    
    def get_average_cpu(self):
        """Get average CPU usage"""
        if not self.measurements:
            return 0
        return statistics.mean(m['cpu_percent'] for m in self.measurements)


class BenchmarkImageGenerator:
    """Generate test images of various sizes and complexities"""
    
    @staticmethod
    def create_test_images():
        """Create test images for benchmarking"""
        images = {}
        
        # Small image (passport photo size)
        images['small'] = np.random.randint(0, 255, (531, 413, 3), dtype=np.uint8)
        
        # Medium image (2MP)
        images['medium'] = np.random.randint(0, 255, (1200, 1600, 3), dtype=np.uint8)
        
        # Large image (8MP)
        images['large'] = np.random.randint(0, 255, (2400, 3200, 3), dtype=np.uint8)
        
        # Very large image (20MP)
        images['very_large'] = np.random.randint(0, 255, (3600, 5400, 3), dtype=np.uint8)
        
        # Add realistic face features to each image
        for name, img in images.items():
            height, width = img.shape[:2]
            center_x, center_y = width // 2, height // 2
            
            # Scale face size based on image size
            face_size = min(width, height) // 4
            
            # Draw face
            cv2.ellipse(img, (center_x, center_y), (face_size//2, int(face_size*0.6)), 
                       0, 0, 360, (220, 180, 160), -1)
            
            # Eyes
            eye_offset = face_size // 6
            cv2.circle(img, (center_x - eye_offset, center_y - face_size//6), 
                      face_size//20, (50, 50, 50), -1)
            cv2.circle(img, (center_x + eye_offset, center_y - face_size//6), 
                      face_size//20, (50, 50, 50), -1)
            
            # Mouth
            cv2.ellipse(img, (center_x, center_y + face_size//4), 
                       (face_size//8, face_size//16), 0, 0, 180, (120, 80, 80), 2)
        
        return images


class TestProcessingSpeedBenchmarks:
    """Test processing speed benchmarks"""
    
    @pytest.fixture
    def benchmark_images(self):
        """Generate benchmark images"""
        return BenchmarkImageGenerator.create_test_images()
    
    @pytest.fixture
    def performance_controller(self):
        """Setup performance-optimized controller"""
        with patch('ai.yolov8_detector.YOLO'), \
             patch('ai.mediapipe_analyzer.mp.solutions.face_mesh.FaceMesh'), \
             patch('ai.background_segmenter.onnxruntime.InferenceSession'):
            
            config_manager = ConfigManager()
            controller = ProcessingController(config_manager)
            
            # Mock fast AI responses
            controller.ai_engine.detect_faces = Mock(return_value=[
                Mock(bbox=Mock(x=100, y=100, width=200, height=250), confidence=0.95)
            ])
            
            controller.ai_engine.analyze_face_landmarks = Mock(return_value=Mock(
                eye_positions=((150, 150), (250, 150)),
                mouth_position=(200, 200),
                glasses_detected=False
            ))
            
            controller.ai_engine.assess_image_quality = Mock(return_value=Mock(
                sharpness_score=0.85,
                lighting_score=0.90
            ))
            
            return controller
    
    def test_single_image_processing_speed(self, benchmark_images, performance_controller):
        """Test single image processing speed across different image sizes"""
        controller = performance_controller
        results = {}
        
        for size_name, image in benchmark_images.items():
            # Create temporary image file
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
                cv2.imwrite(temp_file.name, image)
                
                # Measure processing time
                start_time = time.time()
                result = controller.process_image(temp_file.name, 'ICAO', {})
                end_time = time.time()
                
                processing_time = end_time - start_time
                results[size_name] = {
                    'processing_time': processing_time,
                    'image_size': image.shape,
                    'megapixels': (image.shape[0] * image.shape[1]) / 1_000_000,
                    'success': result.success if result else False
                }
        
        # Verify performance requirements
        assert results['small']['processing_time'] < 3.0  # Under 3 seconds for small images
        assert results['medium']['processing_time'] < 5.0  # Under 5 seconds for medium images
        assert results['large']['processing_time'] < 10.0  # Under 10 seconds for large images
        
        # Verify processing scales reasonably with image size
        small_time = results['small']['processing_time']
        large_time = results['large']['processing_time']
        
        # Large image shouldn't take more than 5x longer than small image
        assert large_time / small_time < 5.0
        
        return results
    
    def test_batch_processing_speed(self, benchmark_images, performance_controller):
        """Test batch processing speed and parallelization"""
        controller = performance_controller
        
        # Create multiple test images
        image_paths = []
        for i in range(5):
            with tempfile.NamedTemporaryFile(suffix=f'_{i}.jpg', delete=False) as temp_file:
                cv2.imwrite(temp_file.name, benchmark_images['medium'])
                image_paths.append(temp_file.name)
        
        # Test sequential processing
        start_time = time.time()
        sequential_results = []
        for path in image_paths:
            result = controller.process_image(path, 'ICAO', {})
            sequential_results.append(result)
        sequential_time = time.time() - start_time
        
        # Test batch processing (should be faster due to optimizations)
        start_time = time.time()
        batch_result = controller.batch_process(image_paths, 'ICAO')
        batch_time = time.time() - start_time
        
        # Batch processing should be more efficient
        assert batch_time < sequential_time * 0.8  # At least 20% faster
        assert batch_result.success is True
        assert len(batch_result.results) == 5
    
    def test_ai_component_performance(self, benchmark_images):
        """Test individual AI component performance"""
        with patch('ai.yolov8_detector.YOLO'), \
             patch('ai.mediapipe_analyzer.mp.solutions.face_mesh.FaceMesh'), \
             patch('ai.background_segmenter.onnxruntime.InferenceSession'):
            
            ai_engine = AIEngine()
            medium_image = benchmark_images['medium']
            
            # Test face detection speed
            start_time = time.time()
            faces = ai_engine.detect_faces(medium_image)
            face_detection_time = time.time() - start_time
            
            # Test landmark analysis speed
            if faces:
                start_time = time.time()
                landmarks = ai_engine.analyze_face_landmarks(medium_image, faces[0].bbox)
                landmark_time = time.time() - start_time
            else:
                landmark_time = 0
            
            # Test quality assessment speed
            start_time = time.time()
            quality = ai_engine.assess_image_quality(medium_image)
            quality_time = time.time() - start_time
            
            # Verify AI component performance
            assert face_detection_time < 2.0  # Face detection under 2 seconds
            assert landmark_time < 1.0        # Landmark analysis under 1 second
            assert quality_time < 1.0         # Quality assessment under 1 second
            
            return {
                'face_detection_time': face_detection_time,
                'landmark_time': landmark_time,
                'quality_time': quality_time
            }
    
    def test_validation_performance(self, benchmark_images):
        """Test validation engine performance"""
        with patch('rules.icao_rules_engine.ICAORulesEngine'):
            validator = ICAOValidator()
            quality_engine = QualityEngine()
            
            medium_image = benchmark_images['medium']
            
            # Mock face features
            mock_features = Mock(
                glasses_detected=False,
                head_covering_detected=False,
                mouth_openness=0.05,
                smile_intensity=0.1
            )
            
            # Test quality assessment speed
            start_time = time.time()
            quality_metrics = quality_engine.generate_quality_score([
                Mock(sharpness_score=0.85),
                Mock(lighting_score=0.90),
                Mock(color_score=0.88)
            ])
            quality_assessment_time = time.time() - start_time
            
            # Test ICAO validation speed
            start_time = time.time()
            with patch.object(validator, '_extract_face_features', return_value=mock_features), \
                 patch.object(validator, '_assess_image_quality', return_value=quality_metrics):
                
                validation_result = validator.validate_full_compliance(
                    medium_image, mock_features, quality_metrics
                )
            validation_time = time.time() - start_time
            
            # Verify validation performance
            assert quality_assessment_time < 1.0  # Quality assessment under 1 second
            assert validation_time < 0.5          # ICAO validation under 0.5 seconds
            
            return {
                'quality_assessment_time': quality_assessment_time,
                'validation_time': validation_time
            }


class TestMemoryUsageBenchmarks:
    """Test memory usage benchmarks"""
    
    def test_memory_usage_single_image(self, benchmark_images):
        """Test memory usage for single image processing"""
        with patch('ai.yolov8_detector.YOLO'), \
             patch('ai.mediapipe_analyzer.mp.solutions.face_mesh.FaceMesh'), \
             patch('ai.background_segmenter.onnxruntime.InferenceSession'):
            
            monitor = PerformanceMonitor()
            config_manager = ConfigManager()
            controller = ProcessingController(config_manager)
            
            # Mock AI responses to focus on memory usage
            controller.ai_engine.detect_faces = Mock(return_value=[Mock(confidence=0.95)])
            controller.ai_engine.analyze_face_landmarks = Mock(return_value=Mock())
            controller.ai_engine.assess_image_quality = Mock(return_value=Mock())
            
            results = {}
            
            for size_name, image in benchmark_images.items():
                # Measure baseline memory
                baseline_memory = monitor.process.memory_info().rss / 1024 / 1024
                
                # Start monitoring
                monitor.start_monitoring()
                
                # Process image
                with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
                    cv2.imwrite(temp_file.name, image)
                    result = controller.process_image(temp_file.name, 'ICAO', {})
                
                # Stop monitoring
                measurements = monitor.stop_monitoring()
                peak_memory = monitor.get_peak_memory()
                
                memory_increase = peak_memory - baseline_memory
                
                results[size_name] = {
                    'baseline_memory': baseline_memory,
                    'peak_memory': peak_memory,
                    'memory_increase': memory_increase,
                    'image_size_mb': (image.nbytes / 1024 / 1024),
                    'megapixels': (image.shape[0] * image.shape[1]) / 1_000_000
                }
                
                # Reset monitor for next test
                monitor = PerformanceMonitor()
            
            # Verify memory usage is reasonable
            assert results['small']['memory_increase'] < 100   # Less than 100MB for small images
            assert results['medium']['memory_increase'] < 300  # Less than 300MB for medium images
            assert results['large']['memory_increase'] < 800   # Less than 800MB for large images
            
            return results
    
    def test_memory_usage_batch_processing(self, benchmark_images):
        """Test memory usage during batch processing"""
        with patch('ai.yolov8_detector.YOLO'), \
             patch('ai.mediapipe_analyzer.mp.solutions.face_mesh.FaceMesh'), \
             patch('ai.background_segmenter.onnxruntime.InferenceSession'):
            
            monitor = PerformanceMonitor()
            config_manager = ConfigManager()
            controller = ProcessingController(config_manager)
            
            # Mock AI responses
            controller.ai_engine.detect_faces = Mock(return_value=[Mock(confidence=0.95)])
            controller.ai_engine.analyze_face_landmarks = Mock(return_value=Mock())
            controller.ai_engine.assess_image_quality = Mock(return_value=Mock())
            
            # Create batch of medium-sized images
            image_paths = []
            for i in range(10):
                with tempfile.NamedTemporaryFile(suffix=f'_batch_{i}.jpg', delete=False) as temp_file:
                    cv2.imwrite(temp_file.name, benchmark_images['medium'])
                    image_paths.append(temp_file.name)
            
            # Measure baseline memory
            baseline_memory = monitor.process.memory_info().rss / 1024 / 1024
            
            # Start monitoring
            monitor.start_monitoring()
            
            # Process batch
            result = controller.batch_process(image_paths, 'ICAO')
            
            # Stop monitoring
            measurements = monitor.stop_monitoring()
            peak_memory = monitor.get_peak_memory()
            
            memory_increase = peak_memory - baseline_memory
            
            # Verify batch processing doesn't use excessive memory
            # Should not use more than 2x the memory of processing images sequentially
            single_image_memory = 300  # Estimated from previous test
            max_expected_memory = single_image_memory * 2  # Allow for some overhead
            
            assert memory_increase < max_expected_memory
            assert result.success is True
            
            return {
                'baseline_memory': baseline_memory,
                'peak_memory': peak_memory,
                'memory_increase': memory_increase,
                'images_processed': len(image_paths)
            }
    
    def test_memory_leak_detection(self, benchmark_images):
        """Test for memory leaks during repeated processing"""
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
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
                cv2.imwrite(temp_file.name, benchmark_images['medium'])
                test_image_path = temp_file.name
            
            memory_measurements = []
            
            # Process same image multiple times
            for i in range(20):
                # Measure memory before processing
                memory_before = psutil.Process().memory_info().rss / 1024 / 1024
                
                # Process image
                result = controller.process_image(test_image_path, 'ICAO', {})
                
                # Measure memory after processing
                memory_after = psutil.Process().memory_info().rss / 1024 / 1024
                
                memory_measurements.append({
                    'iteration': i,
                    'memory_before': memory_before,
                    'memory_after': memory_after,
                    'memory_increase': memory_after - memory_before
                })
                
                # Force garbage collection
                import gc
                gc.collect()
            
            # Analyze memory trend
            initial_memory = memory_measurements[0]['memory_after']
            final_memory = memory_measurements[-1]['memory_after']
            memory_growth = final_memory - initial_memory
            
            # Memory growth should be minimal (less than 50MB over 20 iterations)
            assert memory_growth < 50
            
            # Average memory increase per iteration should be small
            avg_increase = statistics.mean(m['memory_increase'] for m in memory_measurements)
            assert avg_increase < 5  # Less than 5MB average increase per iteration
            
            return {
                'initial_memory': initial_memory,
                'final_memory': final_memory,
                'memory_growth': memory_growth,
                'avg_increase_per_iteration': avg_increase,
                'measurements': memory_measurements
            }


class TestScalabilityBenchmarks:
    """Test system scalability under load"""
    
    def test_concurrent_processing_performance(self, benchmark_images):
        """Test performance under concurrent processing load"""
        with patch('ai.yolov8_detector.YOLO'), \
             patch('ai.mediapipe_analyzer.mp.solutions.face_mesh.FaceMesh'), \
             patch('ai.background_segmenter.onnxruntime.InferenceSession'):
            
            config_manager = ConfigManager()
            
            # Create multiple controllers to simulate concurrent users
            controllers = []
            for _ in range(3):
                controller = ProcessingController(config_manager)
                controller.ai_engine.detect_faces = Mock(return_value=[Mock(confidence=0.95)])
                controller.ai_engine.analyze_face_landmarks = Mock(return_value=Mock())
                controller.ai_engine.assess_image_quality = Mock(return_value=Mock())
                controllers.append(controller)
            
            # Create test images
            image_paths = []
            for i in range(3):
                with tempfile.NamedTemporaryFile(suffix=f'_concurrent_{i}.jpg', delete=False) as temp_file:
                    cv2.imwrite(temp_file.name, benchmark_images['medium'])
                    image_paths.append(temp_file.name)
            
            results = []
            threads = []
            
            def process_concurrent(controller, image_path, result_list):
                start_time = time.time()
                result = controller.process_image(image_path, 'ICAO', {})
                end_time = time.time()
                result_list.append({
                    'success': result.success if result else False,
                    'processing_time': end_time - start_time
                })
            
            # Start concurrent processing
            start_time = time.time()
            for i, (controller, image_path) in enumerate(zip(controllers, image_paths)):
                thread = threading.Thread(
                    target=process_concurrent,
                    args=(controller, image_path, results)
                )
                threads.append(thread)
                thread.start()
            
            # Wait for all threads to complete
            for thread in threads:
                thread.join()
            
            total_time = time.time() - start_time
            
            # Verify concurrent processing
            assert len(results) == 3
            assert all(r['success'] for r in results)
            
            # Concurrent processing should not take much longer than single processing
            max_individual_time = max(r['processing_time'] for r in results)
            assert total_time < max_individual_time * 1.5  # Allow 50% overhead
            
            return {
                'total_time': total_time,
                'individual_times': [r['processing_time'] for r in results],
                'max_individual_time': max_individual_time,
                'concurrent_efficiency': max_individual_time / total_time
            }
    
    def test_large_batch_scalability(self, benchmark_images):
        """Test scalability with large batch sizes"""
        with patch('ai.yolov8_detector.YOLO'), \
             patch('ai.mediapipe_analyzer.mp.solutions.face_mesh.FaceMesh'), \
             patch('ai.background_segmenter.onnxruntime.InferenceSession'):
            
            config_manager = ConfigManager()
            controller = ProcessingController(config_manager)
            
            # Mock AI responses
            controller.ai_engine.detect_faces = Mock(return_value=[Mock(confidence=0.95)])
            controller.ai_engine.analyze_face_landmarks = Mock(return_value=Mock())
            controller.ai_engine.assess_image_quality = Mock(return_value=Mock())
            
            batch_sizes = [10, 25, 50, 100]
            results = {}
            
            for batch_size in batch_sizes:
                # Create batch of images
                image_paths = []
                for i in range(batch_size):
                    with tempfile.NamedTemporaryFile(suffix=f'_batch_{batch_size}_{i}.jpg', delete=False) as temp_file:
                        cv2.imwrite(temp_file.name, benchmark_images['small'])  # Use small images for speed
                        image_paths.append(temp_file.name)
                
                # Measure batch processing time
                start_time = time.time()
                result = controller.batch_process(image_paths, 'ICAO')
                end_time = time.time()
                
                processing_time = end_time - start_time
                time_per_image = processing_time / batch_size
                
                results[batch_size] = {
                    'total_time': processing_time,
                    'time_per_image': time_per_image,
                    'success': result.success if result else False,
                    'throughput': batch_size / processing_time  # Images per second
                }
            
            # Verify scalability
            # Time per image should not increase significantly with batch size
            small_batch_time_per_image = results[10]['time_per_image']
            large_batch_time_per_image = results[100]['time_per_image']
            
            # Large batch should not be more than 2x slower per image
            assert large_batch_time_per_image < small_batch_time_per_image * 2
            
            # Throughput should improve with larger batches
            assert results[100]['throughput'] > results[10]['throughput']
            
            return results


class TestPerformanceReporting:
    """Test performance reporting and metrics collection"""
    
    def test_performance_metrics_collection(self, benchmark_images):
        """Test collection of detailed performance metrics"""
        with patch('ai.yolov8_detector.YOLO'), \
             patch('ai.mediapipe_analyzer.mp.solutions.face_mesh.FaceMesh'), \
             patch('ai.background_segmenter.onnxruntime.InferenceSession'):
            
            config_manager = ConfigManager()
            controller = ProcessingController(config_manager)
            
            # Mock AI responses with timing
            def mock_detect_with_timing(*args, **kwargs):
                time.sleep(0.1)  # Simulate processing time
                return [Mock(confidence=0.95)]
            
            controller.ai_engine.detect_faces = mock_detect_with_timing
            controller.ai_engine.analyze_face_landmarks = Mock(return_value=Mock())
            controller.ai_engine.assess_image_quality = Mock(return_value=Mock())
            
            # Process image and collect metrics
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
                cv2.imwrite(temp_file.name, benchmark_images['medium'])
                
                result = controller.process_image(temp_file.name, 'ICAO', {})
                metrics = controller.get_processing_metrics()
            
            # Verify metrics collection
            assert metrics is not None
            assert hasattr(metrics, 'total_processing_time')
            assert hasattr(metrics, 'face_detection_time')
            assert hasattr(metrics, 'validation_time')
            assert hasattr(metrics, 'memory_usage')
            
            # Verify metrics are reasonable
            assert metrics.total_processing_time > 0
            assert metrics.face_detection_time > 0
            assert metrics.memory_usage > 0
            
            return metrics
    
    def test_benchmark_report_generation(self):
        """Test generation of comprehensive benchmark reports"""
        # Mock benchmark results
        benchmark_data = {
            'processing_speed': {
                'small_image': 1.2,
                'medium_image': 2.8,
                'large_image': 6.5
            },
            'memory_usage': {
                'small_image': 85,
                'medium_image': 180,
                'large_image': 420
            },
            'batch_processing': {
                'batch_10': {'time': 15.2, 'throughput': 0.66},
                'batch_50': {'time': 68.5, 'throughput': 0.73},
                'batch_100': {'time': 125.8, 'throughput': 0.79}
            }
        }
        
        # Generate report
        report = self._generate_benchmark_report(benchmark_data)
        
        assert 'summary' in report
        assert 'detailed_results' in report
        assert 'performance_analysis' in report
        assert 'recommendations' in report
        
        # Verify report content
        summary = report['summary']
        assert 'avg_processing_time' in summary
        assert 'peak_memory_usage' in summary
        assert 'max_throughput' in summary
        
        return report
    
    def _generate_benchmark_report(self, benchmark_data):
        """Generate benchmark report from test data"""
        # Calculate summary statistics
        processing_times = list(benchmark_data['processing_speed'].values())
        memory_usage = list(benchmark_data['memory_usage'].values())
        throughputs = [batch['throughput'] for batch in benchmark_data['batch_processing'].values()]
        
        summary = {
            'avg_processing_time': statistics.mean(processing_times),
            'max_processing_time': max(processing_times),
            'peak_memory_usage': max(memory_usage),
            'max_throughput': max(throughputs)
        }
        
        # Performance analysis
        analysis = {
            'processing_speed_trend': 'Linear scaling with image size',
            'memory_efficiency': 'Good - memory usage scales reasonably',
            'batch_performance': 'Excellent - throughput improves with batch size'
        }
        
        # Recommendations
        recommendations = [
            'Use batch processing for multiple images',
            'Consider image resizing for very large images',
            'Monitor memory usage for large batches'
        ]
        
        return {
            'summary': summary,
            'detailed_results': benchmark_data,
            'performance_analysis': analysis,
            'recommendations': recommendations
        }


if __name__ == "__main__":
    pytest.main([__file__, "-v"])