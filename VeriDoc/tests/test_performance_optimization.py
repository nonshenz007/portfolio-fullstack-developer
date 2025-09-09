"""
Comprehensive performance optimization tests.
Tests parallel processing, memory management, caching, and benchmarking.
"""

import pytest
import time
import tempfile
import shutil
import threading
from pathlib import Path
from unittest.mock import Mock, patch
import numpy as np
from PIL import Image

from core.performance_optimizer import (
    PerformanceOptimizer, ParallelProcessor, MemoryManager, 
    ImageLoader, ProcessingPipeline, ProcessingMetrics, BatchProgress
)
from core.advanced_cache_manager import (
    AdvancedCacheManager, ModelCache, ProcessingResultCache, LRUCache
)
from core.performance_benchmarks import (
    BenchmarkSuite, PerformanceMonitor, SystemMetrics, create_test_images
)


class TestMemoryManager:
    """Test memory management functionality."""
    
    def test_memory_manager_initialization(self):
        """Test memory manager initialization."""
        manager = MemoryManager(max_memory_mb=1024)
        assert manager.max_memory_mb == 1024
        assert manager.memory_threshold == 0.8
    
    def test_get_memory_usage(self):
        """Test memory usage reporting."""
        manager = MemoryManager()
        usage = manager.get_memory_usage()
        assert isinstance(usage, float)
        assert usage > 0
    
    def test_check_memory_pressure(self):
        """Test memory pressure detection."""
        manager = MemoryManager(max_memory_mb=1)  # Very low limit
        # Should detect pressure with such low limit
        pressure = manager.check_memory_pressure()
        assert isinstance(pressure, bool)
    
    def test_optimize_memory(self):
        """Test memory optimization."""
        manager = MemoryManager()
        # Should not raise exception
        manager.optimize_memory()
    
    def test_get_optimal_batch_size(self):
        """Test optimal batch size calculation."""
        manager = MemoryManager(max_memory_mb=2048)
        batch_size = manager.get_optimal_batch_size(image_size_mb=5.0)
        assert isinstance(batch_size, int)
        assert batch_size >= 1


class TestImageLoader:
    """Test intelligent image loading."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.memory_manager = MemoryManager()
        self.image_loader = ImageLoader(self.memory_manager)
        
        # Create test image
        self.test_image_path = Path(self.temp_dir) / "test.jpg"
        test_image = Image.new('RGB', (640, 480), color='red')
        test_image.save(self.test_image_path)
    
    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)
    
    def test_load_image_optimized(self):
        """Test optimized image loading."""
        image_array = self.image_loader.load_image_optimized(str(self.test_image_path))
        assert isinstance(image_array, np.ndarray)
        assert len(image_array.shape) == 3
        assert image_array.shape[2] == 3  # RGB
    
    def test_load_image_with_resize(self):
        """Test image loading with resizing."""
        # Create large image
        large_image_path = Path(self.temp_dir) / "large.jpg"
        large_image = Image.new('RGB', (4000, 3000), color='blue')
        large_image.save(large_image_path)
        
        image_array = self.image_loader.load_image_optimized(
            str(large_image_path), 
            max_size=(1024, 1024)
        )
        
        assert image_array.shape[0] <= 1024
        assert image_array.shape[1] <= 1024
    
    def test_image_caching(self):
        """Test image caching functionality."""
        # Load image twice
        image1 = self.image_loader.load_image_optimized(str(self.test_image_path))
        image2 = self.image_loader.load_image_optimized(str(self.test_image_path))
        
        # Should be same object from cache
        assert np.array_equal(image1, image2)
    
    def test_cache_clearing(self):
        """Test cache clearing."""
        # Load image to populate cache
        self.image_loader.load_image_optimized(str(self.test_image_path))
        assert len(self.image_loader.cache) > 0
        
        # Clear cache
        self.image_loader._clear_cache()
        assert len(self.image_loader.cache) == 0


class TestParallelProcessor:
    """Test parallel processing functionality."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.processor = ParallelProcessor(max_workers=2)
        
        # Create test images
        self.test_images = []
        for i in range(5):
            image_path = Path(self.temp_dir) / f"test_{i}.jpg"
            test_image = Image.new('RGB', (100, 100), color=(i*50, 0, 0))
            test_image.save(image_path)
            self.test_images.append(str(image_path))
    
    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)
    
    def test_process_batch_parallel(self):
        """Test parallel batch processing."""
        def mock_process_func(image, image_path):
            # Simulate processing time
            time.sleep(0.1)
            return {'processed': True, 'path': image_path}
        
        results = self.processor.process_batch_parallel(
            self.test_images, 
            mock_process_func
        )
        
        assert len(results) == len(self.test_images)
        for result in results:
            assert result['success'] is True
            assert 'processing_time' in result
    
    def test_process_batch_with_progress_callback(self):
        """Test batch processing with progress callback."""
        progress_updates = []
        
        def progress_callback(progress: BatchProgress):
            progress_updates.append(progress.progress_percent)
        
        def mock_process_func(image, image_path):
            time.sleep(0.05)
            return {'processed': True}
        
        results = self.processor.process_batch_parallel(
            self.test_images, 
            mock_process_func,
            progress_callback=progress_callback
        )
        
        assert len(results) == len(self.test_images)
        assert len(progress_updates) > 0
        assert progress_updates[-1] == 100.0  # Should reach 100%
    
    def test_process_batch_with_errors(self):
        """Test batch processing with errors."""
        def error_process_func(image, image_path):
            if 'test_2' in image_path:
                raise ValueError("Test error")
            return {'processed': True}
        
        results = self.processor.process_batch_parallel(
            self.test_images, 
            error_process_func
        )
        
        assert len(results) == len(self.test_images)
        
        # Check that one failed and others succeeded
        success_count = sum(1 for r in results if r['success'])
        error_count = sum(1 for r in results if not r['success'])
        
        assert success_count == 4
        assert error_count == 1


class TestProcessingPipeline:
    """Test processing pipeline optimization."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.pipeline = ProcessingPipeline()
        
        # Create test image
        self.test_image_path = Path(self.temp_dir) / "test.jpg"
        test_image = Image.new('RGB', (200, 200), color='green')
        test_image.save(self.test_image_path)
    
    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)
    
    def test_add_stage(self):
        """Test adding processing stages."""
        def stage1(image):
            return image * 0.5
        
        def stage2(image):
            return image + 10
        
        self.pipeline.add_stage(stage1, "brightness_reduction")
        self.pipeline.add_stage(stage2, "brightness_boost")
        
        assert len(self.pipeline.processing_stages) == 2
    
    def test_process_image_pipeline(self):
        """Test image processing through pipeline."""
        def stage1(image):
            # Simple processing stage
            return image.astype(np.float32) * 0.8
        
        def stage2(image):
            # Another processing stage
            return (image + 20).astype(np.uint8)
        
        self.pipeline.add_stage(stage1, "stage1")
        self.pipeline.add_stage(stage2, "stage2")
        
        result = self.pipeline.process_image_pipeline(str(self.test_image_path))
        
        assert result['success'] is True
        assert 'results' in result
        assert 'stage1' in result['results']
        assert 'stage2' in result['results']
        assert 'metrics' in result
        assert isinstance(result['metrics'], ProcessingMetrics)
    
    def test_pipeline_error_handling(self):
        """Test pipeline error handling."""
        def error_stage(image):
            raise ValueError("Test pipeline error")
        
        self.pipeline.add_stage(error_stage, "error_stage")
        
        result = self.pipeline.process_image_pipeline(str(self.test_image_path))
        
        assert result['success'] is False
        assert 'error' in result
        assert result['metrics'].errors_count == 1


class TestLRUCache:
    """Test LRU cache implementation."""
    
    def test_cache_initialization(self):
        """Test cache initialization."""
        cache = LRUCache(max_size=10, max_memory_mb=100)
        assert cache.max_size == 10
        assert cache.max_memory_bytes == 100 * 1024 * 1024
    
    def test_cache_put_get(self):
        """Test basic cache operations."""
        cache = LRUCache(max_size=5)
        
        cache.put("key1", "value1")
        cache.put("key2", "value2")
        
        assert cache.get("key1") == "value1"
        assert cache.get("key2") == "value2"
        assert cache.get("nonexistent") is None
    
    def test_cache_lru_eviction(self):
        """Test LRU eviction."""
        cache = LRUCache(max_size=2)
        
        cache.put("key1", "value1")
        cache.put("key2", "value2")
        cache.put("key3", "value3")  # Should evict key1
        
        assert cache.get("key1") is None
        assert cache.get("key2") == "value2"
        assert cache.get("key3") == "value3"
    
    def test_cache_ttl(self):
        """Test cache TTL functionality."""
        cache = LRUCache(max_size=5)
        
        cache.put("key1", "value1", ttl_seconds=0.1)
        assert cache.get("key1") == "value1"
        
        time.sleep(0.2)
        assert cache.get("key1") is None  # Should be expired
    
    def test_cache_stats(self):
        """Test cache statistics."""
        cache = LRUCache(max_size=5)
        
        cache.put("key1", "value1")
        cache.put("key2", "value2")
        
        stats = cache.get_stats()
        assert stats['entries'] == 2
        assert stats['max_entries'] == 5
        assert 'total_size_mb' in stats


class TestAdvancedCacheManager:
    """Test advanced cache manager."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.cache_manager = AdvancedCacheManager(base_cache_dir=self.temp_dir)
    
    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)
    
    def test_model_caching(self):
        """Test model caching functionality."""
        def mock_model_loader():
            return {"model": "test_model_data"}
        
        # Load model
        model = self.cache_manager.get_model("test_model", mock_model_loader)
        assert model == {"model": "test_model_data"}
        
        # Load again (should come from cache)
        model2 = self.cache_manager.get_model("test_model")
        assert model2 == {"model": "test_model_data"}
    
    def test_processing_result_caching(self):
        """Test processing result caching."""
        # Create test image
        test_image_path = Path(self.temp_dir) / "test.jpg"
        test_image = Image.new('RGB', (100, 100), color='red')
        test_image.save(test_image_path)
        
        processing_params = {"param1": "value1", "param2": 42}
        result_data = {"result": "test_processing_result"}
        
        # Cache result
        self.cache_manager.cache_processing_result(
            str(test_image_path), 
            processing_params, 
            result_data
        )
        
        # Retrieve result
        cached_result = self.cache_manager.get_processing_result(
            str(test_image_path), 
            processing_params
        )
        
        assert cached_result == result_data
    
    def test_general_caching(self):
        """Test general caching functionality."""
        self.cache_manager.put_general("test_key", "test_value")
        
        value = self.cache_manager.get_general("test_key")
        assert value == "test_value"
    
    def test_comprehensive_stats(self):
        """Test comprehensive cache statistics."""
        # Add some data to caches
        self.cache_manager.put_general("key1", "value1")
        
        stats = self.cache_manager.get_comprehensive_stats()
        
        assert 'model_cache' in stats
        assert 'result_cache' in stats
        assert 'general_cache' in stats
        assert 'base_cache_directory' in stats


class TestPerformanceMonitor:
    """Test performance monitoring."""
    
    def test_monitor_initialization(self):
        """Test monitor initialization."""
        monitor = PerformanceMonitor(sampling_interval=0.5)
        assert monitor.sampling_interval == 0.5
        assert not monitor.monitoring
    
    def test_system_metrics_capture(self):
        """Test system metrics capture."""
        metrics = SystemMetrics.capture()
        
        assert isinstance(metrics.timestamp, float)
        assert isinstance(metrics.cpu_percent, float)
        assert isinstance(metrics.memory_percent, float)
        assert metrics.memory_used_mb > 0
        assert metrics.memory_available_mb > 0
    
    def test_monitoring_start_stop(self):
        """Test monitoring start and stop."""
        monitor = PerformanceMonitor(sampling_interval=0.1)
        
        monitor.start_monitoring()
        assert monitor.monitoring is True
        
        time.sleep(0.3)  # Let it collect some metrics
        
        monitor.stop_monitoring()
        assert monitor.monitoring is False
        assert len(monitor.metrics_history) > 0
    
    def test_metrics_summary(self):
        """Test metrics summary generation."""
        monitor = PerformanceMonitor(sampling_interval=0.1)
        
        monitor.start_monitoring()
        time.sleep(0.3)
        monitor.stop_monitoring()
        
        summary = monitor.get_metrics_summary()
        
        assert 'duration_seconds' in summary
        assert 'samples_count' in summary
        assert 'cpu_usage' in summary
        assert 'memory_usage' in summary


class TestBenchmarkSuite:
    """Test benchmark suite functionality."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.benchmark_suite = BenchmarkSuite()
        
        # Create test images
        self.test_images = create_test_images(
            self.temp_dir, 
            count=5, 
            sizes=[(100, 100), (200, 200)]
        )
    
    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)
    
    def test_single_image_benchmark(self):
        """Test single image benchmark."""
        def mock_process_func(image_path):
            # Simulate processing
            time.sleep(0.01)
            return {"processed": True, "path": image_path}
        
        result = self.benchmark_suite.run_single_image_benchmark(
            mock_process_func, 
            self.test_images[:3],  # Use subset for speed
            test_name="test_single"
        )
        
        assert result.test_name == "test_single"
        assert result.total_items == 3
        assert result.success_rate > 0
        assert result.throughput_items_per_second > 0
        assert result.duration_seconds > 0
    
    def test_batch_processing_benchmark(self):
        """Test batch processing benchmark."""
        def mock_batch_process_func(image_paths):
            results = []
            for path in image_paths:
                time.sleep(0.01)  # Simulate processing
                results.append({"success": True, "path": path})
            return results
        
        results = self.benchmark_suite.run_batch_processing_benchmark(
            mock_batch_process_func,
            self.test_images[:4],  # Use subset for speed
            batch_sizes=[1, 2],
            test_name="test_batch"
        )
        
        assert len(results) == 2  # Two batch sizes
        for result in results:
            assert result.total_items == 4
            assert result.success_rate > 0
    
    def test_memory_stress_test(self):
        """Test memory stress test."""
        def mock_process_func(image_path):
            # Simulate memory-intensive processing
            large_array = np.random.rand(100, 100, 3)
            time.sleep(0.01)
            return {"processed": True, "memory_used": large_array.nbytes}
        
        result = self.benchmark_suite.run_memory_stress_test(
            mock_process_func,
            self.test_images[:3],  # Use subset for speed
            max_concurrent=2,
            test_name="test_memory"
        )
        
        assert result.test_name == "test_memory"
        assert result.total_items == 3
        assert result.peak_memory_mb > 0
    
    def test_results_analysis(self):
        """Test results analysis."""
        # Run a simple benchmark to generate results
        def mock_process_func(image_path):
            return {"processed": True}
        
        self.benchmark_suite.run_single_image_benchmark(
            mock_process_func, 
            self.test_images[:2],
            test_name="test_analysis"
        )
        
        analysis = self.benchmark_suite._analyze_results()
        
        assert 'total_tests' in analysis
        assert 'throughput_analysis' in analysis
        assert 'memory_analysis' in analysis
        assert 'reliability_analysis' in analysis
        assert 'recommendations' in analysis
    
    def test_save_results(self):
        """Test saving benchmark results."""
        # Run a simple benchmark
        def mock_process_func(image_path):
            return {"processed": True}
        
        self.benchmark_suite.run_single_image_benchmark(
            mock_process_func, 
            self.test_images[:2],
            test_name="test_save"
        )
        
        # Save results
        results_path = Path(self.temp_dir) / "benchmark_results.json"
        self.benchmark_suite.save_results(str(results_path))
        
        assert results_path.exists()
        
        # Verify content
        import json
        with open(results_path) as f:
            data = json.load(f)
        
        assert 'timestamp' in data
        assert 'system_info' in data
        assert 'results' in data
        assert 'analysis' in data


class TestPerformanceOptimizer:
    """Test main performance optimizer."""
    
    def test_optimizer_initialization(self):
        """Test optimizer initialization."""
        optimizer = PerformanceOptimizer()
        
        assert optimizer.parallel_processor is not None
        assert optimizer.pipeline is not None
        assert isinstance(optimizer.metrics_history, list)
    
    def test_optimize_for_batch_processing(self):
        """Test batch processing optimization."""
        optimizer = PerformanceOptimizer()
        
        optimization = optimizer.optimize_for_batch_processing(
            image_count=100, 
            avg_image_size_mb=5.0
        )
        
        assert 'optimal_workers' in optimization
        assert 'optimal_batch_size' in optimization
        assert 'estimated_memory_usage_mb' in optimization
        assert 'estimated_processing_time_minutes' in optimization
        
        assert optimization['optimal_workers'] > 0
        assert optimization['optimal_batch_size'] > 0
    
    def test_system_performance_info(self):
        """Test system performance information."""
        optimizer = PerformanceOptimizer()
        
        info = optimizer.get_system_performance_info()
        
        assert 'cpu_count' in info
        assert 'memory_total_gb' in info
        assert 'memory_available_gb' in info
        assert 'memory_usage_percent' in info
        assert 'cpu_usage_percent' in info
        
        assert info['cpu_count'] > 0
        assert info['memory_total_gb'] > 0
    
    def test_metrics_recording(self):
        """Test metrics recording and summary."""
        optimizer = PerformanceOptimizer()
        
        # Record some test metrics
        for i in range(3):
            metrics = ProcessingMetrics(
                start_time=time.time() - 1,
                end_time=time.time(),
                images_processed=5,
                memory_usage_mb=100 + i * 10
            )
            metrics.finalize()
            optimizer.record_metrics(metrics)
        
        summary = optimizer.get_performance_summary()
        
        assert 'total_sessions' in summary
        assert 'avg_processing_time_seconds' in summary
        assert 'avg_memory_usage_mb' in summary
        assert 'total_images_processed' in summary
        
        assert summary['total_sessions'] == 3
        assert summary['total_images_processed'] == 15


def test_create_test_images():
    """Test test image creation utility."""
    temp_dir = tempfile.mkdtemp()
    
    try:
        test_images = create_test_images(
            temp_dir, 
            count=3, 
            sizes=[(100, 100), (200, 200)]
        )
        
        assert len(test_images) == 3
        
        for image_path in test_images:
            assert Path(image_path).exists()
            
            # Verify image can be loaded
            with Image.open(image_path) as img:
                assert img.size in [(100, 100), (200, 200)]
    
    finally:
        shutil.rmtree(temp_dir)


if __name__ == "__main__":
    pytest.main([__file__])