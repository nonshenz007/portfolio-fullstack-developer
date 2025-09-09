"""
Performance optimization system for Veridoc photo processing.
Handles parallel processing, memory management, and pipeline optimization.
"""

import asyncio
import concurrent.futures
import multiprocessing
import threading
import time
import psutil
import gc
from typing import List, Dict, Any, Optional, Callable, Tuple
from dataclasses import dataclass, field
from pathlib import Path
import numpy as np
from PIL import Image
import logging

import logging

logger = logging.getLogger(__name__)


@dataclass
class ProcessingMetrics:
    """Metrics for processing performance tracking."""
    start_time: float
    end_time: Optional[float] = None
    duration: Optional[float] = None
    memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0
    images_processed: int = 0
    errors_count: int = 0
    throughput_images_per_second: float = 0.0
    peak_memory_mb: float = 0.0
    
    def finalize(self):
        """Finalize metrics calculation."""
        if self.end_time:
            self.duration = self.end_time - self.start_time
            if self.duration > 0:
                self.throughput_images_per_second = self.images_processed / self.duration


@dataclass
class BatchProgress:
    """Progress tracking for batch operations."""
    total_items: int
    completed_items: int = 0
    failed_items: int = 0
    current_item: Optional[str] = None
    start_time: float = field(default_factory=time.time)
    estimated_completion_time: Optional[float] = None
    
    @property
    def progress_percent(self) -> float:
        """Calculate progress percentage."""
        if self.total_items == 0:
            return 100.0
        return (self.completed_items / self.total_items) * 100.0
    
    @property
    def eta_seconds(self) -> Optional[float]:
        """Calculate estimated time to completion."""
        if self.completed_items == 0:
            return None
        
        elapsed = time.time() - self.start_time
        rate = self.completed_items / elapsed
        remaining = self.total_items - self.completed_items
        
        if rate > 0:
            return remaining / rate
        return None


class MemoryManager:
    """Intelligent memory management for image processing."""
    
    def __init__(self, max_memory_mb: int = 2048):
        self.max_memory_mb = max_memory_mb
        self.current_memory_mb = 0.0
        self.memory_threshold = 0.8  # 80% of max memory
        self._lock = threading.Lock()
        
    def get_memory_usage(self) -> float:
        """Get current memory usage in MB."""
        process = psutil.Process()
        return process.memory_info().rss / 1024 / 1024
    
    def check_memory_pressure(self) -> bool:
        """Check if memory usage is approaching limits."""
        current = self.get_memory_usage()
        return current > (self.max_memory_mb * self.memory_threshold)
    
    def optimize_memory(self):
        """Perform memory optimization."""
        with self._lock:
            # Force garbage collection
            gc.collect()
            
            # Log memory status
            before = self.get_memory_usage()
            logger.info(f"Memory optimization: {before:.1f}MB before cleanup")
            
            # Additional cleanup can be added here
            after = self.get_memory_usage()
            logger.info(f"Memory optimization: {after:.1f}MB after cleanup, freed {before-after:.1f}MB")
    
    def get_optimal_batch_size(self, image_size_mb: float) -> int:
        """Calculate optimal batch size based on available memory."""
        available_mb = self.max_memory_mb * self.memory_threshold
        current_usage = self.get_memory_usage()
        free_memory = max(available_mb - current_usage, 100)  # Minimum 100MB
        
        # Estimate memory per image (processing overhead ~3x image size)
        memory_per_image = image_size_mb * 3
        optimal_batch = max(1, int(free_memory / memory_per_image))
        
        return min(optimal_batch, multiprocessing.cpu_count() * 2)


class ImageLoader:
    """Intelligent image loading with memory optimization."""
    
    def __init__(self, memory_manager: MemoryManager):
        self.memory_manager = memory_manager
        self.cache = {}
        self.max_cache_size = 50  # Maximum cached images
        
    def load_image_optimized(self, image_path: str, max_size: Tuple[int, int] = (2048, 2048)) -> np.ndarray:
        """Load image with memory optimization."""
        try:
            # Check cache first
            if image_path in self.cache:
                return self.cache[image_path]
            
            # Check memory pressure
            if self.memory_manager.check_memory_pressure():
                self.memory_manager.optimize_memory()
                self._clear_cache()
            
            # Load and optimize image
            with Image.open(image_path) as img:
                # Convert to RGB if needed
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Resize if too large
                if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
                    img.thumbnail(max_size, Image.Resampling.LANCZOS)
                
                # Convert to numpy array
                image_array = np.array(img)
                
                # Cache if space available
                if len(self.cache) < self.max_cache_size:
                    self.cache[image_path] = image_array
                
                return image_array
                
        except Exception as e:
            logger.error(f"Failed to load image {image_path}: {e}")
            raise
    
    def _clear_cache(self):
        """Clear image cache to free memory."""
        self.cache.clear()
        gc.collect()


class ParallelProcessor:
    """Parallel processing system for batch operations."""
    
    def __init__(self, max_workers: Optional[int] = None):
        self.max_workers = max_workers or min(multiprocessing.cpu_count(), 8)
        self.memory_manager = MemoryManager()
        self.image_loader = ImageLoader(self.memory_manager)
        
    def process_batch_parallel(self, 
                             image_paths: List[str], 
                             process_func: Callable,
                             progress_callback: Optional[Callable] = None) -> List[Dict[str, Any]]:
        """Process batch of images in parallel."""
        
        batch_progress = BatchProgress(total_items=len(image_paths))
        results = []
        
        # Determine optimal batch size
        if image_paths:
            sample_size = self._estimate_image_size(image_paths[0])
            batch_size = self.memory_manager.get_optimal_batch_size(sample_size)
        else:
            batch_size = self.max_workers
        
        logger.info(f"Processing {len(image_paths)} images with batch size {batch_size}")
        
        # Process in batches to manage memory
        for i in range(0, len(image_paths), batch_size):
            batch_paths = image_paths[i:i + batch_size]
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=min(len(batch_paths), self.max_workers)) as executor:
                # Submit batch jobs
                future_to_path = {
                    executor.submit(self._process_single_image, path, process_func): path 
                    for path in batch_paths
                }
                
                # Collect results
                for future in concurrent.futures.as_completed(future_to_path):
                    path = future_to_path[future]
                    batch_progress.current_item = path
                    
                    try:
                        result = future.result()
                        results.append(result)
                        batch_progress.completed_items += 1
                    except Exception as e:
                        logger.error(f"Failed to process {path}: {e}")
                        results.append({
                            'path': path,
                            'success': False,
                            'error': str(e)
                        })
                        batch_progress.failed_items += 1
                    
                    # Update progress
                    if progress_callback:
                        progress_callback(batch_progress)
            
            # Memory cleanup between batches
            if self.memory_manager.check_memory_pressure():
                self.memory_manager.optimize_memory()
        
        return results
    
    def _process_single_image(self, image_path: str, process_func: Callable) -> Dict[str, Any]:
        """Process a single image with error handling."""
        start_time = time.time()
        
        try:
            # Load image optimally
            image = self.image_loader.load_image_optimized(image_path)
            
            # Process image
            result = process_func(image, image_path)
            
            processing_time = time.time() - start_time
            
            return {
                'path': image_path,
                'success': True,
                'result': result,
                'processing_time': processing_time
            }
            
        except Exception as e:
            processing_time = time.time() - start_time
            return {
                'path': image_path,
                'success': False,
                'error': str(e),
                'processing_time': processing_time
            }
    
    def _estimate_image_size(self, image_path: str) -> float:
        """Estimate image size in MB."""
        try:
            file_size = Path(image_path).stat().st_size / 1024 / 1024
            return max(file_size, 1.0)  # Minimum 1MB estimate
        except:
            return 5.0  # Default 5MB estimate


class ProcessingPipeline:
    """Optimized processing pipeline for large images."""
    
    def __init__(self):
        self.memory_manager = MemoryManager()
        self.image_loader = ImageLoader(self.memory_manager)
        self.processing_stages = []
        
    def add_stage(self, stage_func: Callable, stage_name: str):
        """Add a processing stage to the pipeline."""
        self.processing_stages.append({
            'func': stage_func,
            'name': stage_name
        })
    
    def process_image_pipeline(self, image_path: str) -> Dict[str, Any]:
        """Process image through optimized pipeline."""
        metrics = ProcessingMetrics(start_time=time.time())
        results = {}
        
        try:
            # Load image optimally
            image = self.image_loader.load_image_optimized(image_path)
            current_image = image
            
            # Process through stages
            for stage in self.processing_stages:
                stage_start = time.time()
                
                # Check memory before each stage
                if self.memory_manager.check_memory_pressure():
                    self.memory_manager.optimize_memory()
                
                # Process stage
                stage_result = stage['func'](current_image)
                
                # Update results
                results[stage['name']] = {
                    'result': stage_result,
                    'processing_time': time.time() - stage_start
                }
                
                # Update image if stage returns new image
                if isinstance(stage_result, np.ndarray):
                    current_image = stage_result
            
            metrics.images_processed = 1
            metrics.end_time = time.time()
            metrics.memory_usage_mb = self.memory_manager.get_memory_usage()
            metrics.finalize()
            
            return {
                'success': True,
                'results': results,
                'metrics': metrics,
                'final_image': current_image
            }
            
        except Exception as e:
            metrics.end_time = time.time()
            metrics.errors_count = 1
            metrics.finalize()
            
            logger.error(f"Pipeline processing failed for {image_path}: {e}")
            return {
                'success': False,
                'error': str(e),
                'metrics': metrics
            }


class PerformanceOptimizer:
    """Main performance optimization coordinator."""
    
    def __init__(self):
        self.parallel_processor = ParallelProcessor()
        self.pipeline = ProcessingPipeline()
        self.metrics_history = []
        
    def optimize_for_batch_processing(self, image_count: int, avg_image_size_mb: float) -> Dict[str, Any]:
        """Optimize system settings for batch processing."""
        
        # Calculate optimal settings
        optimal_workers = min(multiprocessing.cpu_count(), max(2, image_count // 10))
        optimal_batch_size = self.parallel_processor.memory_manager.get_optimal_batch_size(avg_image_size_mb)
        
        # Update processor settings
        self.parallel_processor.max_workers = optimal_workers
        
        return {
            'optimal_workers': optimal_workers,
            'optimal_batch_size': optimal_batch_size,
            'estimated_memory_usage_mb': optimal_batch_size * avg_image_size_mb * 3,
            'estimated_processing_time_minutes': (image_count / optimal_workers) * 0.5  # Rough estimate
        }
    
    def get_system_performance_info(self) -> Dict[str, Any]:
        """Get current system performance information."""
        return {
            'cpu_count': multiprocessing.cpu_count(),
            'memory_total_gb': psutil.virtual_memory().total / 1024 / 1024 / 1024,
            'memory_available_gb': psutil.virtual_memory().available / 1024 / 1024 / 1024,
            'memory_usage_percent': psutil.virtual_memory().percent,
            'cpu_usage_percent': psutil.cpu_percent(interval=1)
        }
    
    def record_metrics(self, metrics: ProcessingMetrics):
        """Record processing metrics for analysis."""
        self.metrics_history.append(metrics)
        
        # Keep only recent metrics (last 1000)
        if len(self.metrics_history) > 1000:
            self.metrics_history = self.metrics_history[-1000:]
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary from recorded metrics."""
        if not self.metrics_history:
            return {'message': 'No metrics recorded yet'}
        
        durations = [m.duration for m in self.metrics_history if m.duration]
        throughputs = [m.throughput_images_per_second for m in self.metrics_history if m.throughput_images_per_second > 0]
        memory_usage = [m.memory_usage_mb for m in self.metrics_history]
        
        return {
            'total_sessions': len(self.metrics_history),
            'avg_processing_time_seconds': np.mean(durations) if durations else 0,
            'avg_throughput_images_per_second': np.mean(throughputs) if throughputs else 0,
            'avg_memory_usage_mb': np.mean(memory_usage) if memory_usage else 0,
            'peak_memory_usage_mb': max(memory_usage) if memory_usage else 0,
            'total_images_processed': sum(m.images_processed for m in self.metrics_history),
            'total_errors': sum(m.errors_count for m in self.metrics_history)
        }