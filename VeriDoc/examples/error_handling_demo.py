"""
Demonstration of the comprehensive error handling and diagnostics system.
Shows how to use error recovery, performance monitoring, and diagnostics.
"""

import time
import numpy as np
import logging
from pathlib import Path

# Import error handling components
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.error_handler import ProcessingErrorHandler, ProcessingStage, ErrorSeverity
from utils.diagnostics import SystemDiagnostics
from utils.performance_monitor import PerformanceMonitor
from utils.error_integration import IntegratedErrorHandler, ErrorHandlingConfig, with_error_handling


def setup_logging():
    """Setup logging for the demo."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def demo_basic_error_handling():
    """Demonstrate basic error handling capabilities."""
    print("\n=== Basic Error Handling Demo ===")
    
    # Initialize error handler
    error_handler = ProcessingErrorHandler(
        debug_mode=True,
        save_debug_artifacts=True,
        debug_output_dir="temp/demo_debug"
    )
    
    try:
        # Simulate various types of errors
        test_image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        
        # Test face detection error
        face_detection_error = ValueError("No face detected in image")
        context = {
            'image_path': 'demo_image.jpg',
            'image_dimensions': test_image.shape[:2],
            'processing_params': {'confidence_threshold': 0.5}
        }
        
        print("Handling face detection error...")
        success, result = error_handler.handle_error(
            face_detection_error, 
            ProcessingStage.FACE_DETECTION, 
            context, 
            test_image
        )
        print(f"Recovery successful: {success}")
        if result is not None:
            print(f"Enhanced image shape: {result.shape}")
        
        # Test memory error
        memory_error = MemoryError("Insufficient memory for processing")
        print("\nHandling memory error...")
        success, result = error_handler.handle_error(
            memory_error,
            ProcessingStage.IMAGE_LOADING,
            context,
            test_image
        )
        print(f"Memory recovery successful: {success}")
        
        # Calculate confidence score
        processing_results = {
            'face_detection_confidence': 0.7,
            'validation_consistency': 0.8
        }
        confidence = error_handler.calculate_confidence_score(processing_results, error_count=2)
        print(f"\nConfidence score: {confidence:.2f}")
        
        # Check if manual review is needed
        needs_review = error_handler.should_require_manual_review(confidence)
        print(f"Needs manual review: {needs_review}")
        
        # Generate diagnostic report
        report = error_handler.generate_diagnostic_report()
        print(f"\nDiagnostic report generated with {len(report['recent_errors'])} errors")
        
    finally:
        error_handler.cleanup()


def demo_performance_monitoring():
    """Demonstrate performance monitoring capabilities."""
    print("\n=== Performance Monitoring Demo ===")
    
    # Initialize performance monitor
    monitor = PerformanceMonitor(
        monitoring_interval=1.0,
        enable_auto_optimization=True
    )
    
    try:
        # Start monitoring
        monitor.start_monitoring()
        print("Performance monitoring started")
        
        # Simulate some processing work
        print("Simulating processing work...")
        
        with monitor.performance_context("image_processing"):
            # Simulate CPU-intensive work
            large_array = np.random.rand(1000, 1000)
            result = np.dot(large_array, large_array.T)
            time.sleep(1)
        
        with monitor.performance_context("validation"):
            # Simulate validation work
            time.sleep(0.5)
            validation_result = np.mean(result)
        
        # Get performance summary
        summary = monitor.get_performance_summary()
        print(f"\nPerformance Summary:")
        print(f"CPU Usage - Current: {summary['cpu_usage']['current']:.1f}%, "
              f"Average: {summary['cpu_usage']['average']:.1f}%")
        print(f"Memory Usage - Current: {summary['memory_usage']['current']:.1f}%, "
              f"Available: {summary['memory_usage']['available_mb']:.0f}MB")
        
        # Force optimization
        print("\nForcing memory optimization...")
        opt_result = monitor.force_optimization('memory_cleanup')
        print(f"Optimization successful: {opt_result.success}")
        print(f"Memory freed: {opt_result.memory_freed_mb:.1f}MB")
        
        # Get recent alerts
        alerts = monitor.get_recent_alerts(5)
        print(f"\nRecent alerts: {len(alerts)}")
        for alert in alerts:
            print(f"  - {alert.alert_type}: {alert.message}")
        
    finally:
        monitor.cleanup()


def demo_system_diagnostics():
    """Demonstrate system diagnostics capabilities."""
    print("\n=== System Diagnostics Demo ===")
    
    # Initialize diagnostics
    diagnostics = SystemDiagnostics(monitoring_interval=0.5)
    
    try:
        # Start monitoring
        diagnostics.start_monitoring()
        print("System diagnostics started")
        
        # Start debug session
        session_id = diagnostics.start_debug_session("demo_session")
        print(f"Debug session started: {session_id}")
        
        # Simulate operations with profiling
        operations = ["face_detection", "validation", "auto_fix"]
        
        for op_name in operations:
            print(f"Profiling operation: {op_name}")
            
            # Start profiling
            op_id = diagnostics.start_operation_profiling(op_name)
            
            # Simulate work
            if op_name == "face_detection":
                time.sleep(0.3)
                # Simulate successful operation
                profile = diagnostics.end_operation_profiling(
                    op_id, success=True, input_size=(640, 480)
                )
            elif op_name == "validation":
                time.sleep(0.2)
                profile = diagnostics.end_operation_profiling(
                    op_id, success=True, input_size=(640, 480)
                )
            else:  # auto_fix
                time.sleep(0.4)
                # Simulate failed operation
                profile = diagnostics.end_operation_profiling(
                    op_id, success=False, error_message="Auto-fix failed"
                )
            
            print(f"  Duration: {profile.duration:.2f}s, Success: {profile.success}")
        
        # Save debug artifacts
        test_data = {"operation": "demo", "timestamp": time.time()}
        artifact_path = diagnostics.save_debug_artifact("demo_data", test_data, "json")
        print(f"Debug artifact saved: {artifact_path}")
        
        # Get performance summary
        perf_summary = diagnostics.get_performance_summary()
        print(f"\nPerformance Summary:")
        print(f"Total operations: {perf_summary['total_operations']}")
        print(f"Success rate: {perf_summary['success_rate']:.2f}")
        print(f"Average duration: {perf_summary['duration_stats']['mean']:.2f}s")
        
        # Get system health summary
        health_summary = diagnostics.get_system_health_summary()
        print(f"\nSystem Health Summary:")
        if 'cpu_usage' in health_summary:
            print(f"CPU usage: {health_summary['cpu_usage']['current']:.1f}%")
            print(f"Memory usage: {health_summary['memory_usage']['current']:.1f}%")
        else:
            print("Health data not yet available")
        
        # End debug session
        session = diagnostics.end_debug_session(session_id)
        print(f"\nDebug session ended: {session.session_id}")
        print(f"Operations recorded: {len(session.operations)}")
        print(f"Artifacts saved: {len(session.artifacts_saved)}")
        
        # Export session
        export_path = diagnostics.export_debug_session(session_id)
        print(f"Session exported to: {export_path}")
        
    finally:
        diagnostics.cleanup()


def demo_integrated_error_handling():
    """Demonstrate integrated error handling system."""
    print("\n=== Integrated Error Handling Demo ===")
    
    # Configure integrated handler
    config = ErrorHandlingConfig(
        debug_mode=True,
        save_debug_artifacts=True,
        enable_performance_monitoring=True,
        enable_auto_optimization=True,
        confidence_threshold=0.7
    )
    
    # Initialize integrated handler
    integrated_handler = IntegratedErrorHandler(config)
    
    try:
        # Start a processing operation
        operation_id = integrated_handler.start_processing_operation(
            "demo_image_processing",
            {"input_format": "jpg", "target_format": "icao"}
        )
        print(f"Started operation: {operation_id}")
        
        # Simulate processing with some warnings and errors
        integrated_handler.add_processing_warning(
            operation_id,
            "Image quality is below optimal threshold",
            ProcessingStage.QUALITY_ASSESSMENT,
            {"quality_score": 0.6}
        )
        
        # Simulate an error during face detection
        face_error = RuntimeError("Face detection model failed to load")
        test_image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        
        success, result = integrated_handler.handle_processing_error(
            operation_id,
            face_error,
            ProcessingStage.FACE_DETECTION,
            {"model_path": "models/face_detector.onnx"},
            test_image
        )
        print(f"Error recovery successful: {success}")
        
        # Add another warning
        integrated_handler.add_processing_warning(
            operation_id,
            "Auto-fix applied with reduced quality",
            ProcessingStage.AUTO_FIX,
            {"quality_reduction": 0.1}
        )
        
        # Complete the operation
        report = integrated_handler.complete_processing_operation(
            operation_id,
            success=True,
            result_data={"output_path": "demo_output.jpg", "compliance_score": 0.85},
            input_size=(640, 480),
            output_size=(640, 480)
        )
        
        print(f"\nOperation completed:")
        print(f"  Success: {report['success']}")
        print(f"  Duration: {report['duration']:.2f}s")
        print(f"  Confidence: {report['confidence_score']:.2f}")
        print(f"  Needs manual review: {report['needs_manual_review']}")
        print(f"  Errors: {report['error_count']}, Warnings: {report['warning_count']}")
        
        # Get system status
        status = integrated_handler.get_system_status()
        print(f"\nSystem Status:")
        print(f"  Active operations: {status['active_operations']}")
        print(f"  Total errors: {status['error_handler_status']['total_errors']}")
        print(f"  Manual review flags: {status['error_handler_status']['manual_review_flags']}")
        
        # Force system optimization
        print("\nForcing system optimization...")
        opt_results = integrated_handler.force_system_optimization()
        for opt_type, result in opt_results.items():
            if 'error' not in result:
                print(f"  {opt_type}: {result['memory_freed_mb']:.1f}MB freed")
            else:
                print(f"  {opt_type}: Error - {result['error']}")
        
        # Export comprehensive report
        report_path = integrated_handler.export_comprehensive_report(
            include_debug_data=True
        )
        print(f"\nComprehensive report exported to: {report_path}")
        
    finally:
        integrated_handler.cleanup()


def demo_decorator_usage():
    """Demonstrate decorator usage for automatic error handling."""
    print("\n=== Decorator Usage Demo ===")
    
    # Initialize integrated handler
    config = ErrorHandlingConfig(debug_mode=True)
    integrated_handler = IntegratedErrorHandler(config)
    
    try:
        # Define functions with error handling decorators
        @with_error_handling(integrated_handler, "face_detection", ProcessingStage.FACE_DETECTION)
        def detect_face(image):
            """Simulate face detection with potential errors."""
            if np.random.random() < 0.3:  # 30% chance of error
                raise ValueError("No face detected")
            
            # Simulate processing time
            time.sleep(0.2)
            return {"face_bbox": [100, 100, 200, 200], "confidence": 0.85}
        
        @with_error_handling(integrated_handler, "validation", ProcessingStage.ICAO_VALIDATION)
        def validate_compliance(image, face_data):
            """Simulate compliance validation."""
            if np.random.random() < 0.2:  # 20% chance of error
                raise RuntimeError("Validation engine error")
            
            time.sleep(0.1)
            return {"compliance_score": 0.9, "passes": True}
        
        # Test the decorated functions
        test_image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        
        print("Testing decorated functions...")
        
        # Run multiple iterations to demonstrate error handling
        for i in range(5):
            print(f"\nIteration {i + 1}:")
            
            try:
                # Face detection
                face_result = detect_face(test_image)
                print(f"  Face detection: Success - {face_result['confidence']}")
                
                # Validation
                validation_result = validate_compliance(test_image, face_result)
                print(f"  Validation: Success - {validation_result['compliance_score']}")
                
            except Exception as e:
                print(f"  Error: {e}")
        
        # Get final system status
        status = integrated_handler.get_system_status()
        print(f"\nFinal system status:")
        print(f"  Total errors handled: {status['error_handler_status']['total_errors']}")
        
    finally:
        integrated_handler.cleanup()


def main():
    """Run all error handling demos."""
    print("Veridoc Error Handling and Diagnostics System Demo")
    print("=" * 60)
    
    # Setup logging
    setup_logging()
    
    # Create output directories
    Path("temp/demo_debug").mkdir(parents=True, exist_ok=True)
    Path("logs").mkdir(exist_ok=True)
    
    try:
        # Run demos
        demo_basic_error_handling()
        demo_performance_monitoring()
        demo_system_diagnostics()
        demo_integrated_error_handling()
        demo_decorator_usage()
        
        print("\n" + "=" * 60)
        print("All demos completed successfully!")
        print("Check the 'logs' and 'temp/demo_debug' directories for output files.")
        
    except Exception as e:
        print(f"\nDemo failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()