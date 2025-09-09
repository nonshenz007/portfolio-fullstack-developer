"""
Performance benchmarking and metrics collection system.
Provides comprehensive performance testing and analysis capabilities.
"""

import time
import statistics
import threading
import psutil
import gc
from typing import Dict, List, Any, Optional, Callable, Tuple
from dataclasses import dataclass, field
from pathlib import Path
import json
import numpy as np
from PIL import Image
import logging

from core.performance_optimizer import ProcessingMetrics, MemoryManager

logger = logging.getLogger(__name__)


@dataclass
class BenchmarkResult:
    """Result of a performance benchmark."""
    test_name: str
    duration_seconds: float
    throughput_items_per_second: float
    memory_usage_mb: float
    peak_memory_mb: float
    cpu_usage_percent: float
    success_rate: float
    error_count: int
    total_items: int
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'test_name': self.test_name,
            'duration_seconds': self.duration_seconds,
            'throughput_items_per_second': self.throughput_items_per_second,
            'memory_usage_mb': self.memory_usage_mb,
            'peak_memory_mb': self.peak_memory_mb,
            'cpu_usage_percent': self.cpu_usage_percent,
            'success_rate': self.success_rate,
            'error_count': self.error_count,
            'total_items': self.total_items,
            'metadata': self.metadata
        }


@dataclass
class SystemMetrics:
    """System performance metrics snapshot."""
    timestamp: float
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    memory_available_mb: float
    disk_io_read_mb: float = 0.0
    disk_io_write_mb: float = 0.0
    
    @classmethod
    def capture(cls) -> 'SystemMetrics':
        """Capture current system metrics."""
        memory = psutil.virtual_memory()
        disk_io = psutil.disk_io_counters()
        
        return cls(
            timestamp=time.time(),
            cpu_percent=psutil.cpu_percent(interval=0.1),
            memory_percent=memory.percent,
            memory_used_mb=memory.used / 1024 / 1024,
            memory_available_mb=memory.available / 1024 / 1024,
            disk_io_read_mb=disk_io.read_bytes / 1024 / 1024 if disk_io else 0.0,
            disk_io_write_mb=disk_io.write_bytes / 1024 / 1024 if disk_io else 0.0
        )


class PerformanceMonitor:
    """Real-time performance monitoring."""
    
    def __init__(self, sampling_interval: float = 1.0):
        self.sampling_interval = sampling_interval
        self.metrics_history: List[SystemMetrics] = []
        self.monitoring = False
        self.monitor_thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
        
    def start_monitoring(self):
        """Start performance monitoring."""
        with self._lock:
            if self.monitoring:
                return
            
            self.monitoring = True
            self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.monitor_thread.start()
            logger.info("Performance monitoring started")
    
    def stop_monitoring(self):
        """Stop performance monitoring."""
        with self._lock:
            self.monitoring = False
            if self.monitor_thread:
                self.monitor_thread.join(timeout=2.0)
            logger.info("Performance monitoring stopped")
    
    def get_current_metrics(self) -> SystemMetrics:
        """Get current system metrics."""
        return SystemMetrics.capture()
    
    def get_metrics_summary(self, duration_seconds: Optional[float] = None) -> Dict[str, Any]:
        """Get summary of collected metrics."""
        with self._lock:
            if not self.metrics_history:
                return {'message': 'No metrics collected'}
            
            # Filter by duration if specified
            if duration_seconds:
                cutoff_time = time.time() - duration_seconds
                metrics = [m for m in self.metrics_history if m.timestamp >= cutoff_time]
            else:
                metrics = self.metrics_history
            
            if not metrics:
                return {'message': 'No metrics in specified duration'}
            
            cpu_values = [m.cpu_percent for m in metrics]
            memory_values = [m.memory_percent for m in metrics]
            memory_used_values = [m.memory_used_mb for m in metrics]
            
            return {
                'duration_seconds': metrics[-1].timestamp - metrics[0].timestamp,
                'samples_count': len(metrics),
                'cpu_usage': {
                    'avg': statistics.mean(cpu_values),
                    'max': max(cpu_values),
                    'min': min(cpu_values),
                    'std': statistics.stdev(cpu_values) if len(cpu_values) > 1 else 0
                },
                'memory_usage': {
                    'avg_percent': statistics.mean(memory_values),
                    'max_percent': max(memory_values),
                    'avg_used_mb': statistics.mean(memory_used_values),
                    'peak_used_mb': max(memory_used_values)
                }
            }
    
    def _monitor_loop(self):
        """Main monitoring loop."""
        while self.monitoring:
            try:
                metrics = SystemMetrics.capture()
                
                with self._lock:
                    self.metrics_history.append(metrics)
                    
                    # Keep only recent metrics (last 1000 samples)
                    if len(self.metrics_history) > 1000:
                        self.metrics_history = self.metrics_history[-1000:]
                
                time.sleep(self.sampling_interval)
                
            except Exception as e:
                logger.error(f"Error in performance monitoring: {e}")
                time.sleep(self.sampling_interval)


class BenchmarkSuite:
    """Comprehensive benchmark suite for performance testing."""
    
    def __init__(self):
        self.monitor = PerformanceMonitor()
        self.memory_manager = MemoryManager()
        self.results: List[BenchmarkResult] = []
        
    def run_single_image_benchmark(self, 
                                 process_func: Callable,
                                 test_images: List[str],
                                 test_name: str = "single_image_processing") -> BenchmarkResult:
        """Benchmark single image processing performance."""
        
        logger.info(f"Running single image benchmark: {test_name}")
        
        # Start monitoring
        self.monitor.start_monitoring()
        
        start_time = time.time()
        start_memory = self.memory_manager.get_memory_usage()
        peak_memory = start_memory
        
        success_count = 0
        error_count = 0
        processing_times = []
        
        try:
            for image_path in test_images:
                try:
                    # Monitor memory before processing
                    pre_memory = self.memory_manager.get_memory_usage()
                    
                    # Process image
                    img_start = time.time()
                    result = process_func(image_path)
                    img_duration = time.time() - img_start
                    
                    processing_times.append(img_duration)
                    success_count += 1
                    
                    # Monitor memory after processing
                    post_memory = self.memory_manager.get_memory_usage()
                    peak_memory = max(peak_memory, post_memory)
                    
                except Exception as e:
                    logger.error(f"Error processing {image_path}: {e}")
                    error_count += 1
        
        finally:
            # Stop monitoring
            self.monitor.stop_monitoring()
        
        end_time = time.time()
        total_duration = end_time - start_time
        
        # Get monitoring summary
        monitor_summary = self.monitor.get_metrics_summary(total_duration)
        
        # Calculate results
        total_items = len(test_images)
        success_rate = success_count / total_items if total_items > 0 else 0
        throughput = success_count / total_duration if total_duration > 0 else 0
        
        result = BenchmarkResult(
            test_name=test_name,
            duration_seconds=total_duration,
            throughput_items_per_second=throughput,
            memory_usage_mb=monitor_summary.get('memory_usage', {}).get('avg_used_mb', 0),
            peak_memory_mb=peak_memory,
            cpu_usage_percent=monitor_summary.get('cpu_usage', {}).get('avg', 0),
            success_rate=success_rate,
            error_count=error_count,
            total_items=total_items,
            metadata={
                'avg_processing_time_seconds': statistics.mean(processing_times) if processing_times else 0,
                'max_processing_time_seconds': max(processing_times) if processing_times else 0,
                'min_processing_time_seconds': min(processing_times) if processing_times else 0,
                'monitor_summary': monitor_summary
            }
        )
        
        self.results.append(result)
        logger.info(f"Single image benchmark completed: {throughput:.2f} images/sec")
        
        return result
    
    def run_batch_processing_benchmark(self,
                                     batch_process_func: Callable,
                                     test_images: List[str],
                                     batch_sizes: List[int],
                                     test_name: str = "batch_processing") -> List[BenchmarkResult]:
        """Benchmark batch processing with different batch sizes."""
        
        results = []
        
        for batch_size in batch_sizes:
            logger.info(f"Running batch benchmark with batch size {batch_size}")
            
            # Start monitoring
            self.monitor.start_monitoring()
            
            start_time = time.time()
            start_memory = self.memory_manager.get_memory_usage()
            peak_memory = start_memory
            
            success_count = 0
            error_count = 0
            
            try:
                # Process in batches
                for i in range(0, len(test_images), batch_size):
                    batch = test_images[i:i + batch_size]
                    
                    try:
                        # Monitor memory before batch
                        pre_memory = self.memory_manager.get_memory_usage()
                        
                        # Process batch
                        batch_results = batch_process_func(batch)
                        
                        # Count successes/errors
                        for result in batch_results:
                            if result.get('success', False):
                                success_count += 1
                            else:
                                error_count += 1
                        
                        # Monitor memory after batch
                        post_memory = self.memory_manager.get_memory_usage()
                        peak_memory = max(peak_memory, post_memory)
                        
                    except Exception as e:
                        logger.error(f"Error processing batch: {e}")
                        error_count += len(batch)
            
            finally:
                # Stop monitoring
                self.monitor.stop_monitoring()
            
            end_time = time.time()
            total_duration = end_time - start_time
            
            # Get monitoring summary
            monitor_summary = self.monitor.get_metrics_summary(total_duration)
            
            # Calculate results
            total_items = len(test_images)
            success_rate = success_count / total_items if total_items > 0 else 0
            throughput = success_count / total_duration if total_duration > 0 else 0
            
            result = BenchmarkResult(
                test_name=f"{test_name}_batch_{batch_size}",
                duration_seconds=total_duration,
                throughput_items_per_second=throughput,
                memory_usage_mb=monitor_summary.get('memory_usage', {}).get('avg_used_mb', 0),
                peak_memory_mb=peak_memory,
                cpu_usage_percent=monitor_summary.get('cpu_usage', {}).get('avg', 0),
                success_rate=success_rate,
                error_count=error_count,
                total_items=total_items,
                metadata={
                    'batch_size': batch_size,
                    'monitor_summary': monitor_summary
                }
            )
            
            results.append(result)
            self.results.append(result)
            
            logger.info(f"Batch benchmark (size {batch_size}) completed: {throughput:.2f} images/sec")
        
        return results
    
    def run_memory_stress_test(self,
                              process_func: Callable,
                              test_images: List[str],
                              max_concurrent: int = 10,
                              test_name: str = "memory_stress") -> BenchmarkResult:
        """Run memory stress test with concurrent processing."""
        
        logger.info(f"Running memory stress test with {max_concurrent} concurrent processes")
        
        # Start monitoring
        self.monitor.start_monitoring()
        
        start_time = time.time()
        start_memory = self.memory_manager.get_memory_usage()
        peak_memory = start_memory
        
        success_count = 0
        error_count = 0
        
        try:
            import concurrent.futures
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_concurrent) as executor:
                # Submit all tasks
                futures = [executor.submit(process_func, img_path) for img_path in test_images]
                
                # Collect results
                for future in concurrent.futures.as_completed(futures):
                    try:
                        result = future.result()
                        success_count += 1
                        
                        # Monitor memory
                        current_memory = self.memory_manager.get_memory_usage()
                        peak_memory = max(peak_memory, current_memory)
                        
                    except Exception as e:
                        logger.error(f"Concurrent processing error: {e}")
                        error_count += 1
        
        finally:
            # Stop monitoring
            self.monitor.stop_monitoring()
        
        end_time = time.time()
        total_duration = end_time - start_time
        
        # Get monitoring summary
        monitor_summary = self.monitor.get_metrics_summary(total_duration)
        
        # Calculate results
        total_items = len(test_images)
        success_rate = success_count / total_items if total_items > 0 else 0
        throughput = success_count / total_duration if total_duration > 0 else 0
        
        result = BenchmarkResult(
            test_name=test_name,
            duration_seconds=total_duration,
            throughput_items_per_second=throughput,
            memory_usage_mb=monitor_summary.get('memory_usage', {}).get('avg_used_mb', 0),
            peak_memory_mb=peak_memory,
            cpu_usage_percent=monitor_summary.get('cpu_usage', {}).get('avg', 0),
            success_rate=success_rate,
            error_count=error_count,
            total_items=total_items,
            metadata={
                'max_concurrent': max_concurrent,
                'memory_increase_mb': peak_memory - start_memory,
                'monitor_summary': monitor_summary
            }
        )
        
        self.results.append(result)
        logger.info(f"Memory stress test completed: {throughput:.2f} images/sec, peak memory: {peak_memory:.1f}MB")
        
        return result
    
    def run_comprehensive_benchmark(self,
                                  process_func: Callable,
                                  batch_process_func: Callable,
                                  test_images: List[str]) -> Dict[str, Any]:
        """Run comprehensive benchmark suite."""
        
        logger.info("Starting comprehensive benchmark suite")
        
        # Single image benchmark
        single_result = self.run_single_image_benchmark(process_func, test_images[:10])  # Use subset for speed
        
        # Batch processing benchmarks
        batch_results = self.run_batch_processing_benchmark(
            batch_process_func, 
            test_images[:20],  # Use subset for speed
            batch_sizes=[1, 2, 4, 8]
        )
        
        # Memory stress test
        stress_result = self.run_memory_stress_test(process_func, test_images[:15])  # Use subset for speed
        
        # Analyze results
        analysis = self._analyze_results()
        
        comprehensive_results = {
            'single_image': single_result.to_dict(),
            'batch_processing': [r.to_dict() for r in batch_results],
            'memory_stress': stress_result.to_dict(),
            'analysis': analysis,
            'system_info': self._get_system_info()
        }
        
        logger.info("Comprehensive benchmark suite completed")
        
        return comprehensive_results
    
    def save_results(self, output_path: str):
        """Save benchmark results to file."""
        results_data = {
            'timestamp': time.time(),
            'system_info': self._get_system_info(),
            'results': [r.to_dict() for r in self.results],
            'analysis': self._analyze_results()
        }
        
        with open(output_path, 'w') as f:
            json.dump(results_data, f, indent=2)
        
        logger.info(f"Benchmark results saved to {output_path}")
    
    def _analyze_results(self) -> Dict[str, Any]:
        """Analyze benchmark results."""
        if not self.results:
            return {'message': 'No results to analyze'}
        
        throughputs = [r.throughput_items_per_second for r in self.results]
        memory_usage = [r.memory_usage_mb for r in self.results]
        success_rates = [r.success_rate for r in self.results]
        
        return {
            'total_tests': len(self.results),
            'throughput_analysis': {
                'avg_images_per_second': statistics.mean(throughputs),
                'max_images_per_second': max(throughputs),
                'min_images_per_second': min(throughputs)
            },
            'memory_analysis': {
                'avg_memory_mb': statistics.mean(memory_usage),
                'peak_memory_mb': max(memory_usage),
                'min_memory_mb': min(memory_usage)
            },
            'reliability_analysis': {
                'avg_success_rate': statistics.mean(success_rates),
                'min_success_rate': min(success_rates)
            },
            'recommendations': self._generate_recommendations()
        }
    
    def _generate_recommendations(self) -> List[str]:
        """Generate performance recommendations based on results."""
        recommendations = []
        
        if not self.results:
            return recommendations
        
        # Analyze throughput
        throughputs = [r.throughput_items_per_second for r in self.results]
        avg_throughput = statistics.mean(throughputs)
        
        if avg_throughput < 1.0:
            recommendations.append("Consider optimizing processing algorithms - throughput is below 1 image/second")
        
        # Analyze memory usage
        memory_usage = [r.peak_memory_mb for r in self.results]
        peak_memory = max(memory_usage)
        
        if peak_memory > 2048:  # 2GB
            recommendations.append("High memory usage detected - consider implementing memory optimization")
        
        # Analyze success rates
        success_rates = [r.success_rate for r in self.results]
        min_success_rate = min(success_rates)
        
        if min_success_rate < 0.95:
            recommendations.append("Low success rate detected - improve error handling and robustness")
        
        # Analyze batch performance
        batch_results = [r for r in self.results if 'batch' in r.test_name]
        if len(batch_results) > 1:
            batch_throughputs = [r.throughput_items_per_second for r in batch_results]
            if max(batch_throughputs) > min(batch_throughputs) * 2:
                recommendations.append("Significant batch size performance variation - optimize batch processing")
        
        return recommendations
    
    def _get_system_info(self) -> Dict[str, Any]:
        """Get system information."""
        return {
            'cpu_count': psutil.cpu_count(),
            'memory_total_gb': psutil.virtual_memory().total / 1024 / 1024 / 1024,
            'python_version': f"{psutil.sys.version_info.major}.{psutil.sys.version_info.minor}",
            'platform': psutil.os.name
        }


def create_test_images(output_dir: str, count: int = 20, sizes: List[Tuple[int, int]] = None) -> List[str]:
    """Create test images for benchmarking."""
    if sizes is None:
        sizes = [(640, 480), (1024, 768), (1920, 1080), (2048, 1536)]
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    test_images = []
    
    for i in range(count):
        size = sizes[i % len(sizes)]
        
        # Create random image
        image_array = np.random.randint(0, 255, (size[1], size[0], 3), dtype=np.uint8)
        image = Image.fromarray(image_array)
        
        image_path = output_path / f"test_image_{i:03d}_{size[0]}x{size[1]}.jpg"
        image.save(image_path, "JPEG", quality=85)
        
        test_images.append(str(image_path))
    
    logger.info(f"Created {count} test images in {output_dir}")
    return test_images