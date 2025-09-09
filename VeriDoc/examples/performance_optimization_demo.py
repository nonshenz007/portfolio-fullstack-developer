"""
Performance Optimization Demo

Demonstrates the performance optimization features including:
- Parallel processing for batch operations
- Intelligent memory management
- Advanced caching systems
- Performance benchmarking and metrics
- Processing pipeline optimization
"""

import time
import tempfile
import shutil
from pathlib import Path
import numpy as np
from PIL import Image
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from core.performance_optimizer import (
    PerformanceOptimizer, ParallelProcessor, MemoryManager, 
    ImageLoader, ProcessingPipeline, ProcessingMetrics, BatchProgress
)
from core.advanced_cache_manager import AdvancedCacheManager
from core.performance_benchmarks import (
    BenchmarkSuite, PerformanceMonitor, create_test_images
)


def create_demo_images(output_dir: str, count: int = 20) -> list:
    """Create demo images for testing."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    demo_images = []
    sizes = [(640, 480), (1024, 768), (1920, 1080), (2048, 1536)]
    
    for i in range(count):
        size = sizes[i % len(sizes)]
        
        # Create image with face-like pattern
        image_array = np.random.randint(50, 200, (size[1], size[0], 3), dtype=np.uint8)
        
        # Add a simple "face" pattern (circle in center)
        center_y, center_x = size[1] // 2, size[0] // 2
        y, x = np.ogrid[:size[1], :size[0]]
        mask = (x - center_x) ** 2 + (y - center_y) ** 2 <= (min(size) // 6) ** 2
        image_array[mask] = [180, 150, 120]  # Skin-like color
        
        image = Image.fromarray(image_array)
        image_path = output_path / f"demo_image_{i:03d}_{size[0]}x{size[1]}.jpg"
        image.save(image_path, "JPEG", quality=85)
        
        demo_images.append(str(image_path))
    
    logger.info(f"Created {count} demo images in {output_dir}")
    return demo_images


def demo_memory_management():
    """Demonstrate intelligent memory management."""
    logger.info("=== Memory Management Demo ===")
    
    # Initialize memory manager
    memory_manager = MemoryManager(max_memory_mb=1024)
    
    # Show current memory usage
    current_usage = memory_manager.get_memory_usage()
    logger.info(f"Current memory usage: {current_usage:.1f} MB")
    
    # Check memory pressure
    pressure = memory_manager.check_memory_pressure()
    logger.info(f"Memory pressure detected: {pressure}")
    
    # Get optimal batch size for different image sizes
    for image_size_mb in [1.0, 5.0, 10.0, 20.0]:
        batch_size = memory_manager.get_optimal_batch_size(image_size_mb)
        logger.info(f"Optimal batch size for {image_size_mb}MB images: {batch_size}")
    
    # Demonstrate memory optimization
    logger.info("Performing memory optimization...")
    memory_manager.optimize_memory()
    
    after_usage = memory_manager.get_memory_usage()
    logger.info(f"Memory usage after optimization: {after_usage:.1f} MB")


def demo_intelligent_image_loading(demo_images: list):
    """Demonstrate intelligent image loading with optimization."""
    logger.info("=== Intelligent Image Loading Demo ===")
    
    memory_manager = MemoryManager()
    image_loader = ImageLoader(memory_manager)
    
    # Load images with different optimization settings
    for i, image_path in enumerate(demo_images[:5]):
        logger.info(f"Loading image {i+1}: {Path(image_path).name}")
        
        # Load with default settings
        start_time = time.time()
        image_array = image_loader.load_image_optimized(image_path)
        load_time = time.time() - start_time
        
        logger.info(f"  Loaded in {load_time:.3f}s, shape: {image_array.shape}")
        
        # Load with size limit
        start_time = time.time()
        small_image = image_loader.load_image_optimized(image_path, max_size=(512, 512))
        load_time = time.time() - start_time
        
        logger.info(f"  Resized in {load_time:.3f}s, shape: {small_image.shape}")
    
    # Show cache statistics
    logger.info(f"Images cached: {len(image_loader.cache)}")


def demo_parallel_processing(demo_images: list):
    """Demonstrate parallel batch processing."""
    logger.info("=== Parallel Processing Demo ===")
    
    processor = ParallelProcessor(max_workers=4)
    
    def mock_process_function(image, image_path):
        """Mock processing function that simulates work."""
        # Simulate processing time
        time.sleep(0.1 + np.random.random() * 0.1)
        
        # Simulate some processing results
        return {
            'path': image_path,
            'processed': True,
            'image_shape': image.shape,
            'mean_brightness': float(np.mean(image)),
            'processing_time': 0.1 + np.random.random() * 0.1
        }
    
    # Progress tracking
    progress_updates = []
    
    def progress_callback(progress: BatchProgress):
        progress_updates.append({
            'completed': progress.completed_items,
            'total': progress.total_items,
            'percent': progress.progress_percent,
            'eta': progress.eta_seconds
        })
        logger.info(f"Progress: {progress.completed_items}/{progress.total_items} "
                   f"({progress.progress_percent:.1f}%) - ETA: {progress.eta_seconds:.1f}s")
    
    # Process batch
    logger.info(f"Processing {len(demo_images)} images in parallel...")
    start_time = time.time()
    
    results = processor.process_batch_parallel(
        demo_images,
        mock_process_function,
        progress_callback=progress_callback
    )
    
    total_time = time.time() - start_time
    
    # Analyze results
    successful = sum(1 for r in results if r['success'])
    failed = len(results) - successful
    avg_processing_time = np.mean([r.get('processing_time', 0) for r in results if r['success']])
    
    logger.info(f"Batch processing completed in {total_time:.2f}s")
    logger.info(f"Successful: {successful}, Failed: {failed}")
    logger.info(f"Average processing time per image: {avg_processing_time:.3f}s")
    logger.info(f"Throughput: {successful/total_time:.2f} images/second")


def demo_processing_pipeline(demo_images: list):
    """Demonstrate optimized processing pipeline."""
    logger.info("=== Processing Pipeline Demo ===")
    
    pipeline = ProcessingPipeline()
    
    # Add processing stages
    def stage_blur_detection(image):
        """Simulate blur detection."""
        time.sleep(0.02)  # Simulate processing time
        laplacian_var = np.var(np.array([[1, 1, 1], [1, -8, 1], [1, 1, 1]]))
        return {'blur_score': float(laplacian_var), 'is_sharp': laplacian_var > 100}
    
    def stage_brightness_analysis(image):
        """Simulate brightness analysis."""
        time.sleep(0.03)
        mean_brightness = np.mean(image)
        return {'brightness': float(mean_brightness), 'well_lit': 80 <= mean_brightness <= 180}
    
    def stage_face_detection(image):
        """Simulate face detection."""
        time.sleep(0.05)
        # Mock face detection result
        h, w = image.shape[:2]
        return {
            'faces_detected': 1,
            'primary_face': {
                'bbox': [w//4, h//4, w//2, h//2],
                'confidence': 0.95
            }
        }
    
    def stage_compliance_check(image):
        """Simulate compliance checking."""
        time.sleep(0.04)
        # Mock compliance result
        return {
            'compliance_score': 85.5,
            'passes_icao': True,
            'issues': []
        }
    
    # Add stages to pipeline
    pipeline.add_stage(stage_blur_detection, "blur_detection")
    pipeline.add_stage(stage_brightness_analysis, "brightness_analysis")
    pipeline.add_stage(stage_face_detection, "face_detection")
    pipeline.add_stage(stage_compliance_check, "compliance_check")
    
    # Process images through pipeline
    for i, image_path in enumerate(demo_images[:3]):
        logger.info(f"Processing image {i+1} through pipeline: {Path(image_path).name}")
        
        result = pipeline.process_image_pipeline(image_path)
        
        if result['success']:
            logger.info(f"  Pipeline completed successfully")
            logger.info(f"  Total processing time: {result['metrics'].duration:.3f}s")
            
            for stage_name, stage_result in result['results'].items():
                stage_time = stage_result['processing_time']
                logger.info(f"    {stage_name}: {stage_time:.3f}s")
        else:
            logger.error(f"  Pipeline failed: {result['error']}")


def demo_advanced_caching(demo_images: list):
    """Demonstrate advanced caching system."""
    logger.info("=== Advanced Caching Demo ===")
    
    temp_dir = tempfile.mkdtemp()
    try:
        cache_manager = AdvancedCacheManager(base_cache_dir=temp_dir)
        
        # Demo model caching
        logger.info("Testing model caching...")
        
        def mock_model_loader():
            logger.info("  Loading mock model (expensive operation)...")
            time.sleep(0.5)  # Simulate loading time
            return {"model_type": "face_detector", "version": "1.0", "weights": np.random.rand(100)}
        
        # First load (should call loader)
        start_time = time.time()
        model1 = cache_manager.get_model("face_detector_v1", mock_model_loader)
        load_time1 = time.time() - start_time
        logger.info(f"  First load took {load_time1:.3f}s")
        
        # Second load (should come from cache)
        start_time = time.time()
        model2 = cache_manager.get_model("face_detector_v1")
        load_time2 = time.time() - start_time
        logger.info(f"  Second load took {load_time2:.3f}s (from cache)")
        
        # Demo processing result caching
        logger.info("Testing processing result caching...")
        
        for image_path in demo_images[:3]:
            processing_params = {"format": "ICAO", "quality_threshold": 0.8}
            
            # Check if result is cached
            cached_result = cache_manager.get_processing_result(image_path, processing_params)
            
            if cached_result:
                logger.info(f"  Found cached result for {Path(image_path).name}")
            else:
                logger.info(f"  Processing {Path(image_path).name}...")
                
                # Simulate processing
                time.sleep(0.1)
                result = {
                    'compliance_score': 85.0 + np.random.random() * 10,
                    'passes_icao': True,
                    'processing_time': 0.1
                }
                
                # Cache the result
                cache_manager.cache_processing_result(image_path, processing_params, result)
                logger.info(f"  Result cached for future use")
        
        # Show cache statistics
        stats = cache_manager.get_comprehensive_stats()
        logger.info("Cache Statistics:")
        logger.info(f"  Model cache entries: {stats['model_cache']['memory_cache']['entries']}")
        logger.info(f"  Result cache entries: {stats['result_cache']['entries']}")
        logger.info(f"  General cache entries: {stats['general_cache']['entries']}")
        
    finally:
        shutil.rmtree(temp_dir)


def demo_performance_monitoring():
    """Demonstrate performance monitoring."""
    logger.info("=== Performance Monitoring Demo ===")
    
    monitor = PerformanceMonitor(sampling_interval=0.5)
    
    # Start monitoring
    logger.info("Starting performance monitoring...")
    monitor.start_monitoring()
    
    # Simulate some work
    logger.info("Simulating workload...")
    for i in range(5):
        # Simulate CPU-intensive work
        _ = np.random.rand(1000, 1000).dot(np.random.rand(1000, 1000))
        time.sleep(0.5)
        logger.info(f"  Completed work iteration {i+1}")
    
    # Stop monitoring
    monitor.stop_monitoring()
    
    # Get metrics summary
    summary = monitor.get_metrics_summary()
    logger.info("Performance Summary:")
    logger.info(f"  Duration: {summary['duration_seconds']:.1f}s")
    logger.info(f"  Samples collected: {summary['samples_count']}")
    logger.info(f"  Average CPU usage: {summary['cpu_usage']['avg']:.1f}%")
    logger.info(f"  Peak CPU usage: {summary['cpu_usage']['max']:.1f}%")
    logger.info(f"  Average memory usage: {summary['memory_usage']['avg_percent']:.1f}%")
    logger.info(f"  Peak memory usage: {summary['memory_usage']['peak_used_mb']:.1f} MB")


def demo_performance_benchmarking(demo_images: list):
    """Demonstrate comprehensive performance benchmarking."""
    logger.info("=== Performance Benchmarking Demo ===")
    
    benchmark_suite = BenchmarkSuite()
    
    # Mock processing functions
    def mock_single_process(image_path):
        """Mock single image processing."""
        time.sleep(0.05 + np.random.random() * 0.05)  # Simulate variable processing time
        
        # Simulate occasional failures
        if np.random.random() < 0.1:  # 10% failure rate
            raise ValueError("Mock processing error")
        
        return {
            'compliance_score': 80 + np.random.random() * 20,
            'passes_icao': np.random.random() > 0.2
        }
    
    def mock_batch_process(image_paths):
        """Mock batch processing."""
        results = []
        for path in image_paths:
            try:
                result = mock_single_process(path)
                results.append({'success': True, 'result': result, 'path': path})
            except Exception as e:
                results.append({'success': False, 'error': str(e), 'path': path})
        return results
    
    # Run single image benchmark
    logger.info("Running single image benchmark...")
    single_result = benchmark_suite.run_single_image_benchmark(
        mock_single_process,
        demo_images[:10],  # Use subset for demo
        test_name="demo_single_processing"
    )
    
    logger.info(f"Single Image Results:")
    logger.info(f"  Throughput: {single_result.throughput_items_per_second:.2f} images/sec")
    logger.info(f"  Success rate: {single_result.success_rate:.1%}")
    logger.info(f"  Average memory usage: {single_result.memory_usage_mb:.1f} MB")
    
    # Run batch processing benchmark
    logger.info("Running batch processing benchmark...")
    batch_results = benchmark_suite.run_batch_processing_benchmark(
        mock_batch_process,
        demo_images[:12],  # Use subset for demo
        batch_sizes=[1, 2, 4],
        test_name="demo_batch_processing"
    )
    
    logger.info("Batch Processing Results:")
    for result in batch_results:
        batch_size = result.metadata['batch_size']
        logger.info(f"  Batch size {batch_size}: {result.throughput_items_per_second:.2f} images/sec")
    
    # Run memory stress test
    logger.info("Running memory stress test...")
    stress_result = benchmark_suite.run_memory_stress_test(
        mock_single_process,
        demo_images[:8],  # Use subset for demo
        max_concurrent=4,
        test_name="demo_memory_stress"
    )
    
    logger.info(f"Memory Stress Results:")
    logger.info(f"  Throughput: {stress_result.throughput_items_per_second:.2f} images/sec")
    logger.info(f"  Peak memory: {stress_result.peak_memory_mb:.1f} MB")
    logger.info(f"  Memory increase: {stress_result.metadata['memory_increase_mb']:.1f} MB")
    
    # Generate analysis and recommendations
    analysis = benchmark_suite._analyze_results()
    logger.info("Performance Analysis:")
    logger.info(f"  Average throughput: {analysis['throughput_analysis']['avg_images_per_second']:.2f} images/sec")
    logger.info(f"  Average memory usage: {analysis['memory_analysis']['avg_memory_mb']:.1f} MB")
    logger.info(f"  Average success rate: {analysis['reliability_analysis']['avg_success_rate']:.1%}")
    
    if analysis['recommendations']:
        logger.info("Recommendations:")
        for rec in analysis['recommendations']:
            logger.info(f"  - {rec}")


def demo_performance_optimizer():
    """Demonstrate the main performance optimizer."""
    logger.info("=== Performance Optimizer Demo ===")
    
    optimizer = PerformanceOptimizer()
    
    # Get system performance info
    system_info = optimizer.get_system_performance_info()
    logger.info("System Information:")
    logger.info(f"  CPU cores: {system_info['cpu_count']}")
    logger.info(f"  Total memory: {system_info['memory_total_gb']:.1f} GB")
    logger.info(f"  Available memory: {system_info['memory_available_gb']:.1f} GB")
    logger.info(f"  Current CPU usage: {system_info['cpu_usage_percent']:.1f}%")
    logger.info(f"  Current memory usage: {system_info['memory_usage_percent']:.1f}%")
    
    # Optimize for batch processing
    optimization = optimizer.optimize_for_batch_processing(
        image_count=100,
        avg_image_size_mb=5.0
    )
    
    logger.info("Batch Processing Optimization:")
    logger.info(f"  Optimal workers: {optimization['optimal_workers']}")
    logger.info(f"  Optimal batch size: {optimization['optimal_batch_size']}")
    logger.info(f"  Estimated memory usage: {optimization['estimated_memory_usage_mb']:.1f} MB")
    logger.info(f"  Estimated processing time: {optimization['estimated_processing_time_minutes']:.1f} minutes")
    
    # Record some mock metrics
    for i in range(3):
        metrics = ProcessingMetrics(
            start_time=time.time() - 2,
            images_processed=5,
            memory_usage_mb=200 + i * 50
        )
        metrics.end_time = time.time()
        metrics.finalize()
        optimizer.record_metrics(metrics)
    
    # Get performance summary
    summary = optimizer.get_performance_summary()
    logger.info("Performance Summary:")
    logger.info(f"  Total sessions: {summary['total_sessions']}")
    logger.info(f"  Total images processed: {summary['total_images_processed']}")
    logger.info(f"  Average processing time: {summary['avg_processing_time_seconds']:.3f}s")
    logger.info(f"  Average throughput: {summary['avg_throughput_images_per_second']:.2f} images/sec")
    logger.info(f"  Average memory usage: {summary['avg_memory_usage_mb']:.1f} MB")


def main():
    """Run all performance optimization demos."""
    logger.info("Starting Performance Optimization Demo")
    logger.info("=" * 50)
    
    # Create temporary directory for demo
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Create demo images
        demo_images = create_demo_images(temp_dir, count=15)
        
        # Run all demos
        demo_memory_management()
        print()
        
        demo_intelligent_image_loading(demo_images)
        print()
        
        demo_parallel_processing(demo_images)
        print()
        
        demo_processing_pipeline(demo_images)
        print()
        
        demo_advanced_caching(demo_images)
        print()
        
        demo_performance_monitoring()
        print()
        
        demo_performance_benchmarking(demo_images)
        print()
        
        demo_performance_optimizer()
        
        logger.info("=" * 50)
        logger.info("Performance Optimization Demo completed successfully!")
        
    except Exception as e:
        logger.error(f"Demo failed: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # Clean up
        shutil.rmtree(temp_dir)
        logger.info("Cleanup completed")


if __name__ == "__main__":
    main()