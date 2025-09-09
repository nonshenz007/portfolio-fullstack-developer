"""
Comprehensive unit tests for error handling and diagnostics system.
Tests error recovery strategies, performance monitoring, and diagnostic capabilities.
"""

import unittest
import time
import tempfile
import shutil
import numpy as np
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Import the modules to test
from utils.error_handler import (
    ProcessingErrorHandler, ErrorSeverity, ProcessingStage, 
    ErrorContext, RecoveryStrategy, ProcessingMetrics
)
from utils.diagnostics import SystemDiagnostics, SystemHealth, ProcessingProfile
from utils.performance_monitor import PerformanceMonitor, ResourceMetrics, PerformanceAlert


class TestProcessingErrorHandler(unittest.TestCase):
    """Test cases for ProcessingErrorHandler."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.error_handler = ProcessingErrorHandler(
            debug_mode=True,
            save_debug_artifacts=True,
            debug_output_dir=str(Path(self.temp_dir) / "debug")
        )
    
    def tearDown(self):
        """Clean up test environment."""
        self.error_handler.cleanup()
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_error_handler_initialization(self):
        """Test error handler initialization."""
        self.assertTrue(self.error_handler.debug_mode)
        self.assertTrue(self.error_handler.save_debug_artifacts)
        self.assertEqual(len(self.error_handler.error_history), 0)
        self.assertEqual(len(self.error_handler.confidence_scores), 0)
        self.assertIsNotNone(self.error_handler.logger)
    
    def test_error_severity_classification(self):
        """Test error severity classification."""
        # Test critical errors
        memory_error = MemoryError("Out of memory")
        severity = self.error_handler._classify_error_severity(
            memory_error, ProcessingStage.FACE_DETECTION
        )
        self.assertEqual(severity, ErrorSeverity.CRITICAL)
        
        # Test major errors
        runtime_error = RuntimeError("Processing failed")
        severity = self.error_handler._classify_error_severity(
            runtime_error, ProcessingStage.FACE_DETECTION
        )
        self.assertEqual(severity, ErrorSeverity.MAJOR)
        
        # Test warning errors
        user_warning = UserWarning("Deprecated function")
        severity = self.error_handler._classify_error_severity(
            user_warning, ProcessingStage.IMAGE_LOADING
        )
        self.assertEqual(severity, ErrorSeverity.WARNING)
    
    def test_handle_error_basic(self):
        """Test basic error handling."""
        test_error = ValueError("Test error")
        context = {
            'image_path': 'test.jpg',
            'image_dimensions': (640, 480),
            'processing_params': {'param1': 'value1'}
        }
        
        success, result = self.error_handler.handle_error(
            test_error, ProcessingStage.FACE_DETECTION, context
        )
        
        # Check that error was recorded
        self.assertEqual(len(self.error_handler.error_history), 1)
        error_record = self.error_handler.error_history[0]
        self.assertEqual(error_record.stage, ProcessingStage.FACE_DETECTION)
        self.assertEqual(error_record.message, "Test error")
        self.assertEqual(error_record.exception_type, "ValueError")
    
    def test_face_detection_recovery(self):
        """Test face detection error recovery."""
        # Create test image
        test_image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        
        error_context = ErrorContext(
            error_id="test_error",
            timestamp=time.time(),
            stage=ProcessingStage.FACE_DETECTION,
            severity=ErrorSeverity.MAJOR,
            message="no_face_detected",
            exception_type="ValueError",
            stack_trace="test stack trace"
        )
        
        context = {'image_path': 'test.jpg'}
        
        # Test recovery function
        result = self.error_handler._recover_face_detection(
            error_context, context, test_image
        )
        
        self.assertIsNotNone(result)
        self.assertEqual(result.shape, test_image.shape)
    
    def test_memory_recovery(self):
        """Test memory optimization recovery."""
        error_context = ErrorContext(
            error_id="test_memory_error",
            timestamp=time.time(),
            stage=ProcessingStage.IMAGE_LOADING,
            severity=ErrorSeverity.CRITICAL,
            message="memory_error",
            exception_type="MemoryError",
            stack_trace="test stack trace"
        )
        
        # Create large test image
        large_image = np.random.randint(0, 255, (2000, 2000, 3), dtype=np.uint8)
        context = {'image_path': 'large_test.jpg'}
        
        result = self.error_handler._recover_memory_issues(
            error_context, context, large_image
        )
        
        self.assertIsNotNone(result)
        # Should be smaller than original
        self.assertLess(result.size, large_image.size)
    
    def test_confidence_scoring(self):
        """Test confidence score calculation."""
        # Test with good results
        good_results = {
            'face_detection_confidence': 0.9,
            'validation_consistency': 0.85
        }
        confidence = self.error_handler.calculate_confidence_score(good_results, error_count=0)
        self.assertGreater(confidence, 0.7)
        
        # Test with errors
        confidence_with_errors = self.error_handler.calculate_confidence_score(
            good_results, error_count=3
        )
        self.assertLess(confidence_with_errors, confidence)
        
        # Test with poor results
        poor_results = {
            'face_detection_confidence': 0.3,
            'validation_consistency': 0.4
        }
        poor_confidence = self.error_handler.calculate_confidence_score(poor_results, error_count=0)
        self.assertLess(poor_confidence, 0.5)
    
    def test_manual_review_flagging(self):
        """Test manual review flagging logic."""
        # Test low confidence
        self.assertTrue(self.error_handler.should_require_manual_review(0.5))
        
        # Test high confidence
        self.assertFalse(self.error_handler.should_require_manual_review(0.9))
        
        # Add critical error and test
        critical_error = ErrorContext(
            error_id="critical_test",
            timestamp=time.time(),
            stage=ProcessingStage.FACE_DETECTION,
            severity=ErrorSeverity.CRITICAL,
            message="Critical error",
            exception_type="SystemError",
            stack_trace="test"
        )
        self.error_handler.error_history.append(critical_error)
        
        # Should require manual review even with high confidence
        self.assertTrue(self.error_handler.should_require_manual_review(0.9))
    
    def test_debug_artifact_saving(self):
        """Test debug artifact saving."""
        test_image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        
        error_context = ErrorContext(
            error_id="debug_test",
            timestamp=time.time(),
            stage=ProcessingStage.FACE_DETECTION,
            severity=ErrorSeverity.MAJOR,
            message="Test debug error",
            exception_type="ValueError",
            stack_trace="test stack trace"
        )
        
        context = {'test_param': 'test_value'}
        
        # Save debug artifact
        self.error_handler._save_debug_artifact(error_context, test_image, context)
        
        # Check that files were created
        debug_dir = Path(self.error_handler.debug_output_dir) / error_context.error_id
        self.assertTrue(debug_dir.exists())
        self.assertTrue((debug_dir / "error_image.jpg").exists())
        self.assertTrue((debug_dir / "error_context.json").exists())
        self.assertTrue((debug_dir / "processing_context.json").exists())
    
    def test_diagnostic_report_generation(self):
        """Test diagnostic report generation."""
        # Add some test data
        test_error = ErrorContext(
            error_id="report_test",
            timestamp=time.time(),
            stage=ProcessingStage.ICAO_VALIDATION,
            severity=ErrorSeverity.MAJOR,
            message="Test error for report",
            exception_type="ValueError",
            stack_trace="test"
        )
        self.error_handler.error_history.append(test_error)
        self.error_handler.confidence_scores.extend([0.8, 0.7, 0.9])
        
        # Generate report
        report = self.error_handler.generate_diagnostic_report()
        
        self.assertIn('timestamp', report)
        self.assertIn('system_info', report)
        self.assertIn('error_statistics', report)
        self.assertIn('average_confidence', report)
        self.assertIn('recent_errors', report)
        
        self.assertAlmostEqual(report['average_confidence'], 0.8, places=1)
        self.assertEqual(len(report['recent_errors']), 1)


class TestSystemDiagnostics(unittest.TestCase):
    """Test cases for SystemDiagnostics."""
    
    def setUp(self):
        """Set up test environment."""
        self.diagnostics = SystemDiagnostics(
            monitoring_interval=0.1,  # Fast for testing
            max_history_size=10
        )
    
    def tearDown(self):
        """Clean up test environment."""
        self.diagnostics.cleanup()
    
    def test_diagnostics_initialization(self):
        """Test diagnostics initialization."""
        self.assertEqual(self.diagnostics.monitoring_interval, 0.1)
        self.assertEqual(self.diagnostics.max_history_size, 10)
        self.assertEqual(len(self.diagnostics.health_history), 0)
        self.assertIsNotNone(self.diagnostics.logger)
    
    def test_system_health_collection(self):
        """Test system health metrics collection."""
        health = self.diagnostics._collect_system_health()
        
        self.assertIsInstance(health, SystemHealth)
        self.assertGreaterEqual(health.cpu_usage, 0)
        self.assertGreaterEqual(health.memory_usage, 0)
        self.assertGreaterEqual(health.disk_usage, 0)
        self.assertIsInstance(health.gpu_available, bool)
        self.assertIsInstance(health.network_status, bool)
        self.assertGreater(health.timestamp, 0)
    
    def test_debug_session_management(self):
        """Test debug session creation and management."""
        # Start session
        session_id = self.diagnostics.start_debug_session("test_session")
        self.assertEqual(session_id, "test_session")
        self.assertEqual(self.diagnostics.current_session, "test_session")
        self.assertIn("test_session", self.diagnostics.debug_sessions)
        
        # End session
        session = self.diagnostics.end_debug_session("test_session")
        self.assertIsNotNone(session)
        self.assertIsNotNone(session.end_time)
        self.assertIsNone(self.diagnostics.current_session)
    
    def test_operation_profiling(self):
        """Test operation performance profiling."""
        # Start profiling
        operation_id = self.diagnostics.start_operation_profiling("test_operation")
        self.assertIn(operation_id, self.diagnostics.active_operations)
        
        # Simulate some work
        time.sleep(0.1)
        
        # End profiling
        profile = self.diagnostics.end_operation_profiling(
            operation_id, 
            success=True,
            input_size=(640, 480),
            output_size=(640, 480)
        )
        
        self.assertIsInstance(profile, ProcessingProfile)
        self.assertEqual(profile.operation_name, "test_operation")
        self.assertTrue(profile.success)
        self.assertGreater(profile.duration, 0.05)  # Should be at least 0.05s
        self.assertEqual(profile.input_size, (640, 480))
    
    def test_debug_artifact_saving(self):
        """Test debug artifact saving."""
        # Start session
        session_id = self.diagnostics.start_debug_session()
        
        # Save JSON artifact
        test_data = {"test": "data", "number": 42}
        json_path = self.diagnostics.save_debug_artifact("test_data", test_data, "json")
        self.assertTrue(Path(json_path).exists())
        
        # Save numpy artifact
        test_array = np.array([1, 2, 3, 4, 5])
        npy_path = self.diagnostics.save_debug_artifact("test_array", test_array, "npy")
        self.assertTrue(Path(npy_path).exists())
        
        # Check session recorded artifacts
        session = self.diagnostics.debug_sessions[session_id]
        self.assertEqual(len(session.artifacts_saved), 2)
    
    def test_performance_summary(self):
        """Test performance summary generation."""
        # Add some test profiles
        for i in range(5):
            operation_id = self.diagnostics.start_operation_profiling(f"test_op_{i}")
            time.sleep(0.01)
            self.diagnostics.end_operation_profiling(
                operation_id, 
                success=i < 4,  # One failure
                input_size=(100, 100)
            )
        
        summary = self.diagnostics.get_performance_summary("test_op_0")
        
        self.assertIn("total_operations", summary)
        self.assertIn("success_rate", summary)
        self.assertIn("duration_stats", summary)
        self.assertEqual(summary["total_operations"], 1)
        self.assertEqual(summary["success_rate"], 1.0)
        
        # Test all operations summary
        all_summary = self.diagnostics.get_performance_summary()
        self.assertEqual(all_summary["total_operations"], 5)
        self.assertEqual(all_summary["success_rate"], 0.8)  # 4/5 success
    
    def test_system_health_summary(self):
        """Test system health summary generation."""
        # Add some test health records
        for i in range(3):
            health = SystemHealth(
                cpu_usage=50.0 + i * 10,
                memory_usage=60.0 + i * 5,
                disk_usage=30.0,
                gpu_available=True,
                gpu_memory=70.0,
                temperature=45.0,
                load_average=[1.0, 1.1, 1.2],
                network_status=True,
                timestamp=time.time() + i
            )
            self.diagnostics.health_history.append(health)
        
        summary = self.diagnostics.get_system_health_summary()
        
        self.assertIn("record_count", summary)
        self.assertIn("cpu_usage", summary)
        self.assertIn("memory_usage", summary)
        self.assertEqual(summary["record_count"], 3)
        self.assertEqual(summary["cpu_usage"]["mean"], 60.0)  # (50+60+70)/3


class TestPerformanceMonitor(unittest.TestCase):
    """Test cases for PerformanceMonitor."""
    
    def setUp(self):
        """Set up test environment."""
        self.monitor = PerformanceMonitor(
            monitoring_interval=0.1,  # Fast for testing
            history_size=10,
            enable_auto_optimization=False  # Disable for testing
        )
    
    def tearDown(self):
        """Clean up test environment."""
        self.monitor.cleanup()
    
    def test_monitor_initialization(self):
        """Test performance monitor initialization."""
        self.assertEqual(self.monitor.monitoring_interval, 0.1)
        self.assertEqual(self.monitor.history_size, 10)
        self.assertFalse(self.monitor.enable_auto_optimization)
        self.assertIsNotNone(self.monitor.baseline_metrics)
    
    def test_metrics_collection(self):
        """Test resource metrics collection."""
        metrics = self.monitor._collect_metrics()
        
        self.assertIsInstance(metrics, ResourceMetrics)
        self.assertGreater(metrics.timestamp, 0)
        self.assertGreaterEqual(metrics.cpu_percent, 0)
        self.assertGreaterEqual(metrics.memory_percent, 0)
        self.assertGreater(metrics.memory_available_mb, 0)
        self.assertGreaterEqual(metrics.process_count, 1)
        self.assertGreaterEqual(metrics.thread_count, 1)
    
    def test_performance_alerts(self):
        """Test performance alert generation."""
        # Create metrics that should trigger alerts
        high_cpu_metrics = ResourceMetrics(
            timestamp=time.time(),
            cpu_percent=95.0,  # Above critical threshold
            memory_percent=50.0,
            memory_used_mb=1000.0,
            memory_available_mb=1000.0,
            disk_io_read_mb=0.0,
            disk_io_write_mb=0.0,
            network_sent_mb=0.0,
            network_recv_mb=0.0,
            process_count=100,
            thread_count=10
        )
        
        # Check alerts before
        alerts_before = len(self.monitor.alerts_history)
        
        # Trigger alert check
        self.monitor._check_performance_alerts(high_cpu_metrics)
        
        # Should have generated alert
        self.assertGreater(len(self.monitor.alerts_history), alerts_before)
        
        # Check alert details
        latest_alert = self.monitor.alerts_history[-1]
        self.assertEqual(latest_alert.alert_type, 'cpu_usage')
        self.assertEqual(latest_alert.severity, 'high')  # 95% triggers 'high' not 'critical'
        self.assertEqual(latest_alert.current_value, 95.0)
    
    def test_memory_optimization(self):
        """Test memory optimization."""
        result = self.monitor._optimize_memory()
        
        self.assertIsInstance(result.optimization_type, str)
        self.assertIsInstance(result.success, bool)
        self.assertGreaterEqual(result.memory_freed_mb, 0)
        self.assertGreaterEqual(result.time_taken, 0)
        self.assertIn('objects_collected', result.details)
    
    def test_cache_optimization(self):
        """Test cache optimization."""
        # Create some temporary files to clean up
        temp_dir = Path("temp")
        temp_dir.mkdir(exist_ok=True)
        
        # Create old file (simulate with modified time)
        old_file = temp_dir / "old_temp_file.txt"
        old_file.write_text("test content")
        
        result = self.monitor._optimize_cache()
        
        self.assertEqual(result.optimization_type, 'cache_cleanup')
        self.assertIsInstance(result.success, bool)
        self.assertGreaterEqual(result.time_taken, 0)
    
    def test_performance_context(self):
        """Test performance context manager."""
        with self.monitor.performance_context("test_operation"):
            time.sleep(0.05)  # Simulate work
        
        # Context manager should log performance info
        # This is mainly testing that it doesn't crash
        self.assertTrue(True)  # If we get here, context manager worked
    
    def test_performance_summary(self):
        """Test performance summary generation."""
        # Add some test metrics
        for i in range(3):
            metrics = ResourceMetrics(
                timestamp=time.time() + i,
                cpu_percent=50.0 + i * 10,
                memory_percent=60.0 + i * 5,
                memory_used_mb=1000.0 + i * 100,
                memory_available_mb=2000.0 - i * 100,
                disk_io_read_mb=1.0,
                disk_io_write_mb=2.0,
                network_sent_mb=0.5,
                network_recv_mb=1.5,
                process_count=100,
                thread_count=10
            )
            self.monitor.metrics_history.append(metrics)
        
        summary = self.monitor.get_performance_summary()
        
        self.assertIn("time_range", summary)
        self.assertIn("cpu_usage", summary)
        self.assertIn("memory_usage", summary)
        self.assertIn("baseline_comparison", summary)
        
        # Check calculated values
        self.assertEqual(summary["cpu_usage"]["average"], 60.0)  # (50+60+70)/3
        self.assertEqual(summary["memory_usage"]["average"], 65.0)  # (60+65+70)/3
    
    def test_forced_optimization(self):
        """Test forced optimization execution."""
        result = self.monitor.force_optimization('memory_cleanup')
        
        self.assertEqual(result.optimization_type, 'memory_cleanup')
        self.assertIsInstance(result.success, bool)
        self.assertGreaterEqual(result.time_taken, 0)
        
        # Test invalid optimization type
        with self.assertRaises(ValueError):
            self.monitor.force_optimization('invalid_optimization')
    
    def test_recent_alerts(self):
        """Test recent alerts retrieval."""
        # Add some test alerts
        for i in range(5):
            alert = PerformanceAlert(
                timestamp=time.time() + i,
                alert_type='test_alert',
                severity='medium',
                message=f'Test alert {i}',
                current_value=50.0 + i,
                threshold_value=60.0,
                suggested_action='Test action'
            )
            self.monitor.alerts_history.append(alert)
        
        recent_alerts = self.monitor.get_recent_alerts(3)
        
        self.assertEqual(len(recent_alerts), 3)
        self.assertEqual(recent_alerts[-1].message, 'Test alert 4')  # Most recent


class TestErrorRecoveryIntegration(unittest.TestCase):
    """Integration tests for error recovery scenarios."""
    
    def setUp(self):
        """Set up integration test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.error_handler = ProcessingErrorHandler(
            debug_mode=True,
            debug_output_dir=str(Path(self.temp_dir) / "debug")
        )
        self.diagnostics = SystemDiagnostics(monitoring_interval=0.1)
        self.performance_monitor = PerformanceMonitor(
            monitoring_interval=0.1,
            enable_auto_optimization=True
        )
    
    def tearDown(self):
        """Clean up integration test environment."""
        self.error_handler.cleanup()
        self.diagnostics.cleanup()
        self.performance_monitor.cleanup()
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_end_to_end_error_handling(self):
        """Test complete error handling workflow."""
        # Start monitoring and debug session
        self.performance_monitor.start_monitoring()
        session_id = self.diagnostics.start_debug_session("integration_test")
        
        # Simulate processing with error
        test_image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        test_error = RuntimeError("Simulated processing error")
        
        context = {
            'image_path': 'integration_test.jpg',
            'image_dimensions': test_image.shape[:2],
            'processing_params': {'test_param': 'test_value'}
        }
        
        # Handle error
        success, result = self.error_handler.handle_error(
            test_error, ProcessingStage.FACE_DETECTION, context, test_image
        )
        
        # Verify error was handled
        self.assertEqual(len(self.error_handler.error_history), 1)
        
        # Calculate confidence
        processing_results = {'face_detection_confidence': 0.6}
        confidence = self.error_handler.calculate_confidence_score(
            processing_results, error_count=1
        )
        self.assertLess(confidence, 1.0)
        
        # Check if manual review is needed
        needs_review = self.error_handler.should_require_manual_review(confidence)
        
        # End session and get diagnostics
        session = self.diagnostics.end_debug_session(session_id)
        diagnostic_report = self.error_handler.generate_diagnostic_report()
        performance_summary = self.performance_monitor.get_performance_summary()
        
        # Verify integration worked
        self.assertIsNotNone(session)
        self.assertIn('error_statistics', diagnostic_report)
        self.assertIn('cpu_usage', performance_summary)
        
        # Stop monitoring
        self.performance_monitor.stop_monitoring()
    
    def test_resource_optimization_under_load(self):
        """Test resource optimization during high load simulation."""
        self.performance_monitor.start_monitoring()
        
        # Simulate high memory usage
        large_arrays = []
        try:
            # Create memory pressure
            for i in range(10):
                large_arrays.append(np.random.rand(1000, 1000))
            
            # Force optimization
            result = self.performance_monitor.force_optimization('memory_cleanup')
            self.assertTrue(result.success)
            
        finally:
            # Clean up
            del large_arrays
            self.performance_monitor.stop_monitoring()
    
    def test_concurrent_error_handling(self):
        """Test error handling under concurrent conditions."""
        import threading
        
        errors_handled = []
        
        def simulate_error(error_id):
            error = ValueError(f"Concurrent error {error_id}")
            context = {'error_id': error_id}
            success, result = self.error_handler.handle_error(
                error, ProcessingStage.ICAO_VALIDATION, context
            )
            errors_handled.append((error_id, success))
        
        # Create multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=simulate_error, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads
        for thread in threads:
            thread.join()
        
        # Verify all errors were handled
        self.assertEqual(len(errors_handled), 5)
        self.assertEqual(len(self.error_handler.error_history), 5)


if __name__ == '__main__':
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_suite.addTest(unittest.makeSuite(TestProcessingErrorHandler))
    test_suite.addTest(unittest.makeSuite(TestSystemDiagnostics))
    test_suite.addTest(unittest.makeSuite(TestPerformanceMonitor))
    test_suite.addTest(unittest.makeSuite(TestErrorRecoveryIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Exit with appropriate code
    exit(0 if result.wasSuccessful() else 1)