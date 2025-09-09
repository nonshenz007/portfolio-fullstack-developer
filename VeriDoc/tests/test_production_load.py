"""
Production Load Testing and Performance Validation

This module validates processing speed and memory usage under production loads,
ensuring the system can handle real-world usage scenarios efficiently.
"""

import pytest
import numpy as np
import cv2
import time
import threading
import multiprocessing
import psutil
import json
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import logging

from core.processing_controller import ProcessingController
from core.config_manager import ConfigManager
from ai.ai_engine import AIEngine
from validation.icao_validator import ICAOValidator
from rules.icao_rules_engine import ICAORulesEngine
from autofix.autofix_engine import AutoFixEngine


@dataclass
class LoadTestMetrics:
    """Metrics for load testing evaluation"""
    total_images_processed: int
    total_processing_time: float
    average_processing_time: float
    peak_memory_usage_mb: float
    average_memory_usage_mb: float
    cpu_usage_percent: float
    throughput_images_per_second: float
    error_rate: float
    success_rate: float
    
    @property
    def performance_score(self) -> float:
        """Calculate overall performance score"""
        # Higher throughput and lower memory usage = better score
        throughput_score = min(self.throughput_images_per_second / 10.0, 1.0)  # Target: 10 images/sec
        memory_score = max(0, 1.0 - (self.peak_memory_usage_mb / 2000.0))  # Target: <2GB peak
        success_score = self.success_rate
        
        return (throughput_score * 0.4) + (memory_score * 0.3) + (success_score * 0.3)


@dataclass
class LoadTestScenario:
    """Load test scenario definition"""
    name: str
    description: str
    num_images: int
    concurrent_workers: int
    image_sizes: List[Tuple[int, int]]
    processing_options: Dict[str, Any]
    expected_throughput: float
    max_memory_mb: float
    max_processing_time: float


class ProductionLoadTester:
    """Production load testing and performance validation system"""
    
    def __init__(self):
        self.config_manager = ConfigManager()
        self.processing_controller = ProcessingController(self.config_manager)
        self.ai_engine = AIEngine()
        self.icao_validator = ICAOValidator(ICAORulesEngine())
        self.autofix_engine = AutoFixEngine(self.ai_engine)
        
        self.logger = logging.getLogger(__name__)
        
        # Load test scenarios
        self.test_scenarios = self._define_load_test_scenarios()
        
        # Performance monitoring
        self.performance_history = []
        self.system_monitor = SystemMonitor()
    
    def _define_load_test_scenarios(self) -> List[LoadTestScenario]:
        """Define load test scenarios for different usage patterns"""
        return [
            LoadTestScenario(
                name="single_user_batch",
                description="Single user processing a batch of photos",
                num_images=50,
                concurrent_workers=1,
                image_sizes=[(480, 600), (960, 1200)],
                processing_options={"validate_only": False, "auto_fix": True},
                expected_throughput=2.0,  # 2 images per second
                max_memory_mb=1000,
                max_processing_time=3.0
            ),
            LoadTestScenario(
                name="multi_user_concurrent",
                description="Multiple users processing photos simultaneously",
                num_images=100,
                concurrent_workers=4,
                image_sizes=[(480, 600), (720, 900), (960, 1200)],
                processing_options={"validate_only": False, "auto_fix": True},
                expected_throughput=6.0,  # 6 images per second total
                max_memory_mb=2000,
                max_processing_time=5.0
            ),
            LoadTestScenario(
                name="high_volume_validation",
                description="High volume validation-only processing",
                num_images=200,
                concurrent_workers=6,
                image_sizes=[(480, 600)],
                processing_options={"validate_only": True, "auto_fix": False},
                expected_throughput=15.0,  # 15 images per second (validation only)
                max_memory_mb=1500,
                max_processing_time=1.0
            ),
            LoadTestScenario(
                name="large_image_processing",
                description="Processing large high-resolution images",
                num_images=30,
                concurrent_workers=2,
                image_sizes=[(1920, 2400), (2400, 3000)],
                processing_options={"validate_only": False, "auto_fix": True},
                expected_throughput=0.5,  # 0.5 images per second (large images)
                max_memory_mb=3000,
                max_processing_time=10.0
            ),
            LoadTestScenario(
                name="stress_test_maximum",
                description="Maximum stress test with many concurrent workers",
                num_images=500,
                concurrent_workers=8,
                image_sizes=[(480, 600), (720, 900), (960, 1200), (1440, 1800)],
                processing_options={"validate_only": False, "auto_fix": True},
                expected_throughput=10.0,  # 10 images per second
                max_memory_mb=4000,
                max_processing_time=8.0
            ),
            LoadTestScenario(
                name="memory_intensive",
                description="Memory-intensive processing with complex auto-fix",
                num_images=100,
                concurrent_workers=3,
                image_sizes=[(1440, 1800), (1920, 2400)],
                processing_options={
                    "validate_only": False, 
                    "auto_fix": True,
                    "background_removal": True,
                    "lighting_correction": True,
                    "geometry_correction": True
                },
                expected_throughput=1.0,  # 1 image per second
                max_memory_mb=2500,
                max_processing_time=6.0
            ),
            LoadTestScenario(
                name="sustained_load",
                description="Sustained load over extended period",
                num_images=1000,
                concurrent_workers=4,
                image_sizes=[(720, 900), (960, 1200)],
                processing_options={"validate_only": False, "auto_fix": True},
                expected_throughput=4.0,  # 4 images per second
                max_memory_mb=2000,
                max_processing_time=4.0
            )
        ]
    
    def run_production_load_tests(self) -> Dict[str, Any]:
        """Run comprehensive production load tests"""
        self.logger.info("🚀 Starting production load testing...")
        
        test_results = {}
        overall_metrics = {
            'total_images_processed': 0,
            'total_test_time': 0,
            'peak_memory_usage': 0,
            'average_throughput': 0,
            'success_rate': 0
        }
        
        for scenario in self.test_scenarios:
            self.logger.info(f"  Running scenario: {scenario.name}")
            
            # Run load test scenario
            scenario_results = self._run_load_test_scenario(scenario)
            test_results[scenario.name] = scenario_results
            
            # Update overall metrics
            overall_metrics['total_images_processed'] += scenario_results.total_images_processed
            overall_metrics['total_test_time'] += scenario_results.total_processing_time
            overall_metrics['peak_memory_usage'] = max(
                overall_metrics['peak_memory_usage'], 
                scenario_results.peak_memory_usage_mb
            )
            
            # Log scenario results
            self.logger.info(f"    ✅ Processed {scenario_results.total_images_processed} images")
            self.logger.info(f"    📊 Throughput: {scenario_results.throughput_images_per_second:.2f} img/sec")
            self.logger.info(f"    💾 Peak Memory: {scenario_results.peak_memory_usage_mb:.1f} MB")
            self.logger.info(f"    ✓ Success Rate: {scenario_results.success_rate:.1%}")
            
            # Brief pause between scenarios
            time.sleep(2)
        
        # Calculate overall metrics
        if overall_metrics['total_test_time'] > 0:
            overall_metrics['average_throughput'] = (
                overall_metrics['total_images_processed'] / overall_metrics['total_test_time']
            )
        
        overall_metrics['success_rate'] = np.mean([
            result.success_rate for result in test_results.values()
        ])
        
        # Generate comprehensive report
        report = self._generate_load_test_report(test_results, overall_metrics)
        
        # Save results
        self._save_load_test_results(report)
        
        self.logger.info("✅ Production load testing complete")
        
        return report
    
    def _run_load_test_scenario(self, scenario: LoadTestScenario) -> LoadTestMetrics:
        """Run a specific load test scenario"""
        # Generate test images
        test_images = self._generate_test_images(scenario.num_images, scenario.image_sizes)
        
        # Start system monitoring
        self.system_monitor.start_monitoring()
        
        # Track processing metrics
        processing_times = []
        memory_usage = []
        errors = 0
        successes = 0
        
        start_time = time.time()
        
        if scenario.concurrent_workers == 1:
            # Sequential processing
            for i, test_image in enumerate(test_images):
                try:
                    process_start = time.time()
                    
                    # Process image
                    result = self.processing_controller.process_image(
                        test_image,
                        format_name="ICAO",
                        options=scenario.processing_options
                    )
                    
                    process_time = time.time() - process_start
                    processing_times.append(process_time)
                    
                    # Track memory usage
                    current_memory = psutil.Process().memory_info().rss / 1024 / 1024
                    memory_usage.append(current_memory)
                    
                    if result.success:
                        successes += 1
                    else:
                        errors += 1
                        
                except Exception as e:
                    self.logger.warning(f"Error processing image {i}: {str(e)}")
                    errors += 1
        
        else:
            # Concurrent processing
            with ThreadPoolExecutor(max_workers=scenario.concurrent_workers) as executor:
                # Submit all tasks
                futures = []
                for i, test_image in enumerate(test_images):
                    future = executor.submit(
                        self._process_image_with_timing,
                        test_image,
                        scenario.processing_options,
                        i
                    )
                    futures.append(future)
                
                # Collect results
                for future in futures:
                    try:
                        result = future.result(timeout=scenario.max_processing_time + 5)
                        if result['success']:
                            processing_times.append(result['processing_time'])
                            memory_usage.append(result['memory_usage'])
                            successes += 1
                        else:
                            errors += 1
                    except Exception as e:
                        self.logger.warning(f"Error in concurrent processing: {str(e)}")
                        errors += 1
        
        total_time = time.time() - start_time
        
        # Stop system monitoring
        system_metrics = self.system_monitor.stop_monitoring()
        
        # Calculate metrics
        total_processed = successes + errors
        avg_processing_time = np.mean(processing_times) if processing_times else 0
        peak_memory = max(memory_usage) if memory_usage else 0
        avg_memory = np.mean(memory_usage) if memory_usage else 0
        throughput = total_processed / total_time if total_time > 0 else 0
        error_rate = errors / total_processed if total_processed > 0 else 0
        success_rate = successes / total_processed if total_processed > 0 else 0
        
        return LoadTestMetrics(
            total_images_processed=total_processed,
            total_processing_time=total_time,
            average_processing_time=avg_processing_time,
            peak_memory_usage_mb=peak_memory,
            average_memory_usage_mb=avg_memory,
            cpu_usage_percent=system_metrics.get('avg_cpu_usage', 0),
            throughput_images_per_second=throughput,
            error_rate=error_rate,
            success_rate=success_rate
        )
    
    def _process_image_with_timing(self, image: np.ndarray, options: Dict[str, Any], 
                                 image_id: int) -> Dict[str, Any]:
        """Process image with timing and memory tracking"""
        start_time = time.time()
        memory_before = psutil.Process().memory_info().rss / 1024 / 1024
        
        try:
            result = self.processing_controller.process_image(
                image,
                format_name="ICAO",
                options=options
            )
            
            processing_time = time.time() - start_time
            memory_after = psutil.Process().memory_info().rss / 1024 / 1024
            
            return {
                'success': result.success,
                'processing_time': processing_time,
                'memory_usage': memory_after,
                'memory_delta': memory_after - memory_before,
                'image_id': image_id
            }
            
        except Exception as e:
            processing_time = time.time() - start_time
            memory_after = psutil.Process().memory_info().rss / 1024 / 1024
            
            return {
                'success': False,
                'processing_time': processing_time,
                'memory_usage': memory_after,
                'memory_delta': memory_after - memory_before,
                'error': str(e),
                'image_id': image_id
            }
    
    def _generate_test_images(self, num_images: int, sizes: List[Tuple[int, int]]) -> List[np.ndarray]:
        """Generate test images for load testing"""
        images = []
        
        for i in range(num_images):
            # Select size for this image
            size = sizes[i % len(sizes)]
            width, height = size
            
            # Create realistic test image
            image = self._create_realistic_test_image(width, height, i)
            images.append(image)
        
        return images
    
    def _create_realistic_test_image(self, width: int, height: int, seed: int) -> np.ndarray:
        """Create realistic test image with face and background"""
        np.random.seed(seed)
        
        # Create background with slight variation
        bg_color = np.random.randint(240, 255, 3)
        image = np.full((height, width, 3), bg_color, dtype=np.uint8)
        
        # Add some background texture
        noise = np.random.normal(0, 5, (height, width, 3)).astype(np.int16)
        image = np.clip(image.astype(np.int16) + noise, 0, 255).astype(np.uint8)
        
        # Add face
        face_center = (width // 2, height // 2)
        face_radius = min(width, height) // 8
        
        # Face (skin tone with variation)
        skin_base = np.array([220, 180, 140])
        skin_variation = np.random.randint(-20, 20, 3)
        skin_color = np.clip(skin_base + skin_variation, 0, 255)
        
        cv2.circle(image, face_center, face_radius, skin_color.tolist(), -1)
        
        # Eyes
        eye_y = face_center[1] - face_radius // 3
        eye_offset = face_radius // 3
        eye_color = [50, 50, 50]
        eye_size = max(2, face_radius // 10)
        
        cv2.circle(image, (face_center[0] - eye_offset, eye_y), eye_size, eye_color, -1)
        cv2.circle(image, (face_center[0] + eye_offset, eye_y), eye_size, eye_color, -1)
        
        # Mouth
        mouth_y = face_center[1] + face_radius // 3
        mouth_width = face_radius // 4
        mouth_height = max(2, face_radius // 15)
        mouth_color = [100, 50, 50]
        
        cv2.ellipse(image, (face_center[0], mouth_y), (mouth_width, mouth_height), 
                   0, 0, 180, mouth_color, 2)
        
        # Add some random variations to make images more realistic
        if seed % 3 == 0:
            # Add slight blur
            image = cv2.GaussianBlur(image, (3, 3), 0.5)
        elif seed % 3 == 1:
            # Add slight brightness variation
            brightness_factor = np.random.uniform(0.9, 1.1)
            image = cv2.convertScaleAbs(image, alpha=brightness_factor, beta=0)
        
        return image
    
    def _generate_load_test_report(self, test_results: Dict[str, LoadTestMetrics], 
                                 overall_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive load test report"""
        # Calculate performance grades
        performance_grades = {}
        for scenario_name, metrics in test_results.items():
            scenario = next(s for s in self.test_scenarios if s.name == scenario_name)
            
            # Grade based on meeting expectations
            throughput_grade = "A" if metrics.throughput_images_per_second >= scenario.expected_throughput else \
                              "B" if metrics.throughput_images_per_second >= scenario.expected_throughput * 0.8 else \
                              "C" if metrics.throughput_images_per_second >= scenario.expected_throughput * 0.6 else "D"
            
            memory_grade = "A" if metrics.peak_memory_usage_mb <= scenario.max_memory_mb else \
                          "B" if metrics.peak_memory_usage_mb <= scenario.max_memory_mb * 1.2 else \
                          "C" if metrics.peak_memory_usage_mb <= scenario.max_memory_mb * 1.5 else "D"
            
            time_grade = "A" if metrics.average_processing_time <= scenario.max_processing_time else \
                        "B" if metrics.average_processing_time <= scenario.max_processing_time * 1.2 else \
                        "C" if metrics.average_processing_time <= scenario.max_processing_time * 1.5 else "D"
            
            success_grade = "A" if metrics.success_rate >= 0.95 else \
                           "B" if metrics.success_rate >= 0.90 else \
                           "C" if metrics.success_rate >= 0.85 else "D"
            
            performance_grades[scenario_name] = {
                'throughput': throughput_grade,
                'memory': memory_grade,
                'processing_time': time_grade,
                'success_rate': success_grade,
                'overall_score': metrics.performance_score
            }
        
        # System recommendations
        recommendations = self._generate_performance_recommendations(test_results)
        
        return {
            'test_summary': {
                'total_scenarios': len(test_results),
                'total_images_processed': overall_metrics['total_images_processed'],
                'total_test_duration': overall_metrics['total_test_time'],
                'average_throughput': overall_metrics['average_throughput'],
                'peak_memory_usage': overall_metrics['peak_memory_usage'],
                'overall_success_rate': overall_metrics['success_rate']
            },
            'scenario_results': {
                name: asdict(metrics) for name, metrics in test_results.items()
            },
            'performance_grades': performance_grades,
            'recommendations': recommendations,
            'system_info': {
                'cpu_count': multiprocessing.cpu_count(),
                'total_memory_gb': psutil.virtual_memory().total / (1024**3),
                'python_version': f"{psutil.sys.version_info.major}.{psutil.sys.version_info.minor}",
                'test_timestamp': time.time()
            }
        }
    
    def _generate_performance_recommendations(self, test_results: Dict[str, LoadTestMetrics]) -> List[str]:
        """Generate performance optimization recommendations"""
        recommendations = []
        
        # Analyze throughput
        avg_throughput = np.mean([metrics.throughput_images_per_second for metrics in test_results.values()])
        if avg_throughput < 2.0:
            recommendations.append(
                "Consider optimizing AI model inference speed or implementing model quantization"
            )
        
        # Analyze memory usage
        peak_memory = max([metrics.peak_memory_usage_mb for metrics in test_results.values()])
        if peak_memory > 2000:
            recommendations.append(
                "High memory usage detected. Consider implementing image streaming or batch size optimization"
            )
        
        # Analyze processing times
        avg_processing_time = np.mean([metrics.average_processing_time for metrics in test_results.values()])
        if avg_processing_time > 5.0:
            recommendations.append(
                "Processing times are high. Consider GPU acceleration or algorithm optimization"
            )
        
        # Analyze error rates
        avg_error_rate = np.mean([metrics.error_rate for metrics in test_results.values()])
        if avg_error_rate > 0.05:
            recommendations.append(
                "Error rate is above 5%. Review error handling and input validation"
            )
        
        # Concurrent processing analysis
        concurrent_scenarios = [name for name, scenario in 
                              zip(test_results.keys(), self.test_scenarios) 
                              if scenario.concurrent_workers > 1]
        
        if concurrent_scenarios:
            concurrent_performance = [test_results[name].performance_score 
                                    for name in concurrent_scenarios]
            if np.mean(concurrent_performance) < 0.7:
                recommendations.append(
                    "Concurrent processing performance is suboptimal. Consider thread pool optimization"
                )
        
        if not recommendations:
            recommendations.append("System performance meets all requirements. No optimizations needed.")
        
        return recommendations
    
    def _save_load_test_results(self, report: Dict[str, Any]):
        """Save load test results to file"""
        results_path = Path("test_results/production_load_test_report.json")
        results_path.parent.mkdir(exist_ok=True)
        
        with open(results_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Also save a summary CSV for easy analysis
        summary_path = Path("test_results/load_test_summary.csv")
        with open(summary_path, 'w') as f:
            f.write("Scenario,Images,Workers,Throughput,Peak_Memory_MB,Avg_Time_Sec,Success_Rate,Performance_Score\n")
            
            for scenario_name, metrics in report['scenario_results'].items():
                scenario = next(s for s in self.test_scenarios if s.name == scenario_name)
                f.write(f"{scenario_name},{metrics['total_images_processed']},{scenario.concurrent_workers},"
                       f"{metrics['throughput_images_per_second']:.2f},{metrics['peak_memory_usage_mb']:.1f},"
                       f"{metrics['average_processing_time']:.3f},{metrics['success_rate']:.3f},"
                       f"{metrics['performance_score']:.3f}\n")
        
        self.logger.info(f"📄 Load test results saved to: {results_path}")
        self.logger.info(f"📊 Summary CSV saved to: {summary_path}")


class SystemMonitor:
    """System resource monitoring during load tests"""
    
    def __init__(self):
        self.monitoring = False
        self.metrics = {
            'cpu_usage': [],
            'memory_usage': [],
            'timestamps': []
        }
        self.monitor_thread = None
    
    def start_monitoring(self):
        """Start system monitoring"""
        self.monitoring = True
        self.metrics = {'cpu_usage': [], 'memory_usage': [], 'timestamps': []}
        self.monitor_thread = threading.Thread(target=self._monitor_system)
        self.monitor_thread.start()
    
    def stop_monitoring(self) -> Dict[str, float]:
        """Stop monitoring and return metrics"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join()
        
        if not self.metrics['cpu_usage']:
            return {'avg_cpu_usage': 0, 'peak_memory_usage': 0}
        
        return {
            'avg_cpu_usage': np.mean(self.metrics['cpu_usage']),
            'peak_cpu_usage': np.max(self.metrics['cpu_usage']),
            'avg_memory_usage': np.mean(self.metrics['memory_usage']),
            'peak_memory_usage': np.max(self.metrics['memory_usage'])
        }
    
    def _monitor_system(self):
        """Monitor system resources"""
        while self.monitoring:
            try:
                cpu_percent = psutil.cpu_percent(interval=0.1)
                memory_info = psutil.virtual_memory()
                
                self.metrics['cpu_usage'].append(cpu_percent)
                self.metrics['memory_usage'].append(memory_info.percent)
                self.metrics['timestamps'].append(time.time())
                
                time.sleep(0.5)  # Monitor every 0.5 seconds
            except Exception:
                break


@pytest.fixture
def load_tester():
    """Fixture for production load tester"""
    return ProductionLoadTester()


class TestProductionLoad:
    """Test suite for production load validation"""
    
    def test_single_user_performance(self, load_tester):
        """Test single user batch processing performance"""
        scenario = next(s for s in load_tester.test_scenarios if s.name == "single_user_batch")
        metrics = load_tester._run_load_test_scenario(scenario)
        
        # Assert performance requirements
        assert metrics.throughput_images_per_second >= scenario.expected_throughput * 0.8, \
            f"Throughput {metrics.throughput_images_per_second:.2f} below threshold"
        
        assert metrics.peak_memory_usage_mb <= scenario.max_memory_mb * 1.2, \
            f"Memory usage {metrics.peak_memory_usage_mb:.1f}MB exceeds threshold"
        
        assert metrics.success_rate >= 0.95, \
            f"Success rate {metrics.success_rate:.1%} below threshold"
        
        print(f"✅ Single user performance: {metrics.throughput_images_per_second:.2f} img/sec")
    
    def test_concurrent_processing(self, load_tester):
        """Test concurrent multi-user processing"""
        scenario = next(s for s in load_tester.test_scenarios if s.name == "multi_user_concurrent")
        metrics = load_tester._run_load_test_scenario(scenario)
        
        # Assert concurrent performance requirements
        assert metrics.throughput_images_per_second >= scenario.expected_throughput * 0.7, \
            f"Concurrent throughput {metrics.throughput_images_per_second:.2f} below threshold"
        
        assert metrics.error_rate <= 0.05, \
            f"Error rate {metrics.error_rate:.1%} too high for concurrent processing"
        
        print(f"✅ Concurrent performance: {metrics.throughput_images_per_second:.2f} img/sec with {scenario.concurrent_workers} workers")
    
    def test_memory_efficiency(self, load_tester):
        """Test memory efficiency under load"""
        scenario = next(s for s in load_tester.test_scenarios if s.name == "memory_intensive")
        metrics = load_tester._run_load_test_scenario(scenario)
        
        # Assert memory efficiency
        assert metrics.peak_memory_usage_mb <= scenario.max_memory_mb, \
            f"Peak memory {metrics.peak_memory_usage_mb:.1f}MB exceeds limit {scenario.max_memory_mb}MB"
        
        # Check for memory leaks (average should be much lower than peak)
        memory_efficiency = metrics.average_memory_usage_mb / metrics.peak_memory_usage_mb
        assert memory_efficiency >= 0.6, \
            f"Memory efficiency {memory_efficiency:.1%} suggests potential memory leaks"
        
        print(f"✅ Memory efficiency: Peak {metrics.peak_memory_usage_mb:.1f}MB, Avg {metrics.average_memory_usage_mb:.1f}MB")
    
    def test_sustained_load(self, load_tester):
        """Test sustained load processing"""
        scenario = next(s for s in load_tester.test_scenarios if s.name == "sustained_load")
        metrics = load_tester._run_load_test_scenario(scenario)
        
        # Assert sustained performance
        assert metrics.throughput_images_per_second >= scenario.expected_throughput * 0.8, \
            f"Sustained throughput {metrics.throughput_images_per_second:.2f} below threshold"
        
        assert metrics.success_rate >= 0.90, \
            f"Success rate {metrics.success_rate:.1%} degraded under sustained load"
        
        print(f"✅ Sustained load: {metrics.total_images_processed} images in {metrics.total_processing_time:.1f}s")
    
    def test_comprehensive_load_suite(self, load_tester):
        """Run comprehensive load test suite"""
        report = load_tester.run_production_load_tests()
        
        # Assert overall system performance
        assert report['test_summary']['overall_success_rate'] >= 0.90, \
            f"Overall success rate {report['test_summary']['overall_success_rate']:.1%} below threshold"
        
        assert report['test_summary']['average_throughput'] >= 1.0, \
            f"Average throughput {report['test_summary']['average_throughput']:.2f} below minimum"
        
        # Check that no scenario completely failed
        failed_scenarios = [
            name for name, grades in report['performance_grades'].items()
            if grades['overall_score'] < 0.3
        ]
        
        assert len(failed_scenarios) == 0, \
            f"Scenarios failed completely: {failed_scenarios}"
        
        print(f"✅ Comprehensive load test: {report['test_summary']['total_images_processed']} images processed")
        print(f"📊 Average throughput: {report['test_summary']['average_throughput']:.2f} img/sec")
        print(f"💾 Peak memory: {report['test_summary']['peak_memory_usage']:.1f}MB")


if __name__ == "__main__":
    # Run load tests when executed directly
    tester = ProductionLoadTester()
    
    print("🚀 Starting production load testing...")
    report = tester.run_production_load_tests()
    
    print("\n" + "="*60)
    print("PRODUCTION LOAD TESTING COMPLETE")
    print("="*60)
    print(f"Total Images Processed: {report['test_summary']['total_images_processed']}")
    print(f"Average Throughput: {report['test_summary']['average_throughput']:.2f} images/sec")
    print(f"Peak Memory Usage: {report['test_summary']['peak_memory_usage']:.1f} MB")
    print(f"Overall Success Rate: {report['test_summary']['overall_success_rate']:.1%}")
    
    print("\nPerformance Grades:")
    for scenario, grades in report['performance_grades'].items():
        print(f"  {scenario}: Overall Score {grades['overall_score']:.2f}")
    
    print("\nRecommendations:")
    for rec in report['recommendations']:
        print(f"  • {rec}")