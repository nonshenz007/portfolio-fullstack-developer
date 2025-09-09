"""
Integration module for comprehensive error handling and diagnostics.
Provides unified interface for error handling, diagnostics, and performance monitoring.
"""

import time
import threading
import logging
from typing import Dict, List, Optional, Any, Tuple, Callable
from dataclasses import dataclass
from pathlib import Path
import numpy as np

from core.error_handler import get_error_handler, ErrorCategory, ErrorSeverity
from .diagnostics import SystemDiagnostics, profile_operation, save_debug_image
from .performance_monitor import PerformanceMonitor, monitor_performance


@dataclass
class ErrorHandlingConfig:
    """Configuration for integrated error handling system."""
    debug_mode: bool = False
    save_debug_artifacts: bool = False
    enable_performance_monitoring: bool = True
    enable_auto_optimization: bool = True
    monitoring_interval: float = 5.0
    debug_output_dir: str = "temp/debug"
    max_history_size: int = 1000
    confidence_threshold: float = 0.7
    auto_review_threshold: float = 0.5


class IntegratedErrorHandler:
    """
    Unified error handling system that integrates error recovery,
    diagnostics, and performance monitoring.
    """
    
    def __init__(self, config: Optional[ErrorHandlingConfig] = None):
        """
        Initialize integrated error handling system.
        
        Args:
            config: Configuration for error handling system
        """
        self.config = config or ErrorHandlingConfig()
        
        # Initialize components using core error handler
        self.error_handler = get_error_handler()
        
        self.diagnostics = SystemDiagnostics(
            monitoring_interval=self.config.monitoring_interval,
            max_history_size=self.config.max_history_size
        )
        
        self.performance_monitor = PerformanceMonitor(
            monitoring_interval=self.config.monitoring_interval,
            history_size=self.config.max_history_size,
            enable_auto_optimization=self.config.enable_auto_optimization
        )
        
        # State tracking
        self.active_operations: Dict[str, Dict[str, Any]] = {}
        self.processing_sessions: Dict[str, str] = {}  # operation_id -> session_id
        
        # Setup logging
        self.logger = logging.getLogger("veridoc_integrated_error_handler")
        
        # Start monitoring if enabled
        if self.config.enable_performance_monitoring:
            self.start_monitoring()
    
    def start_monitoring(self):
        """Start all monitoring systems."""
        try:
            self.diagnostics.start_monitoring()
            self.performance_monitor.start_monitoring()
            self.logger.info("Integrated monitoring started")
        except Exception as e:
            self.logger.error(f"Failed to start monitoring: {e}")
    
    def stop_monitoring(self):
        """Stop all monitoring systems."""
        try:
            self.diagnostics.stop_monitoring()
            self.performance_monitor.stop_monitoring()
            self.logger.info("Integrated monitoring stopped")
        except Exception as e:
            self.logger.error(f"Failed to stop monitoring: {e}")
    
    def start_processing_operation(self, 
                                 operation_name: str,
                                 operation_params: Optional[Dict[str, Any]] = None) -> str:
        """
        Start a new processing operation with full monitoring.
        
        Args:
            operation_name: Name of the operation
            operation_params: Optional parameters for the operation
        
        Returns:
            Operation ID for tracking
        """
        operation_id = f"{operation_name}_{int(time.time() * 1000)}"
        
        # Start debug session
        session_id = self.diagnostics.start_debug_session(f"session_{operation_id}")
        self.processing_sessions[operation_id] = session_id
        
        # Start performance profiling
        profile_id = self.diagnostics.start_operation_profiling(operation_name)
        
        # Start performance monitoring context
        self.performance_monitor.start_processing_timer()
        
        # Track operation
        self.active_operations[operation_id] = {
            'operation_name': operation_name,
            'session_id': session_id,
            'profile_id': profile_id,
            'start_time': time.time(),
            'params': operation_params or {},
            'errors': [],
            'warnings': []
        }
        
        self.logger.info(f"Started processing operation: {operation_id}")
        return operation_id
    
    def handle_processing_error(self,
                              operation_id: str,
                              error: Exception,
                              stage: ProcessingStage,
                              context: Dict[str, Any],
                              image_data: Optional[np.ndarray] = None) -> Tuple[bool, Optional[Any]]:
        """
        Handle processing error with full integration.
        
        Args:
            operation_id: ID of the operation where error occurred
            error: The exception that occurred
            stage: Processing stage where error occurred
            context: Additional context information
            image_data: Image data for debugging (optional)
        
        Returns:
            Tuple of (recovery_successful, recovered_result)
        """
        if operation_id not in self.active_operations:
            self.logger.warning(f"Unknown operation ID: {operation_id}")
            return False, None
        
        operation = self.active_operations[operation_id]
        
        # Add operation context
        enhanced_context = {
            **context,
            'operation_id': operation_id,
            'operation_name': operation['operation_name'],
            'operation_params': operation['params']
        }
        
        # Handle error with error handler
        success, result = self.error_handler.handle_error(
            error, stage, enhanced_context, image_data
        )
        
        # Record error in operation
        operation['errors'].append({
            'error': str(error),
            'stage': stage.value,
            'timestamp': time.time(),
            'recovery_successful': success
        })
        
        # Save debug image if available and in debug mode
        if self.config.save_debug_artifacts and image_data is not None:
            try:
                save_debug_image(
                    self.diagnostics, 
                    image_data, 
                    f"error_{stage.value}_{int(time.time())}"
                )
            except Exception as e:
                self.logger.warning(f"Failed to save debug image: {e}")
        
        # Update diagnostics
        if not success:
            session_id = operation['session_id']
            if session_id in self.diagnostics.debug_sessions:
                self.diagnostics.debug_sessions[session_id].total_errors += 1
        
        return success, result
    
    def add_processing_warning(self,
                             operation_id: str,
                             warning_message: str,
                             stage: ProcessingStage,
                             context: Optional[Dict[str, Any]] = None):
        """
        Add a processing warning to the operation.
        
        Args:
            operation_id: ID of the operation
            warning_message: Warning message
            stage: Processing stage where warning occurred
            context: Additional context information
        """
        if operation_id not in self.active_operations:
            return
        
        operation = self.active_operations[operation_id]
        operation['warnings'].append({
            'message': warning_message,
            'stage': stage.value,
            'timestamp': time.time(),
            'context': context or {}
        })
        
        # Update diagnostics
        session_id = operation['session_id']
        if session_id in self.diagnostics.debug_sessions:
            self.diagnostics.debug_sessions[session_id].total_warnings += 1
        
        self.logger.warning(f"Operation {operation_id}: {warning_message}")
    
    def complete_processing_operation(self,
                                    operation_id: str,
                                    success: bool = True,
                                    result_data: Optional[Dict[str, Any]] = None,
                                    input_size: Optional[Tuple[int, int]] = None,
                                    output_size: Optional[Tuple[int, int]] = None) -> Dict[str, Any]:
        """
        Complete a processing operation and generate comprehensive report.
        
        Args:
            operation_id: ID of the operation to complete
            success: Whether the operation was successful
            result_data: Optional result data
            input_size: Input image size
            output_size: Output image size
        
        Returns:
            Comprehensive operation report
        """
        if operation_id not in self.active_operations:
            self.logger.warning(f"Unknown operation ID: {operation_id}")
            return {}
        
        operation = self.active_operations[operation_id]
        
        # Complete performance profiling
        profile = self.diagnostics.end_operation_profiling(
            operation['profile_id'],
            success=success,
            error_message=None if success else "Operation failed",
            input_size=input_size,
            output_size=output_size
        )
        
        # Stop processing timer
        processing_duration = self.performance_monitor.stop_processing_timer()
        
        # End debug session
        session = self.diagnostics.end_debug_session(operation['session_id'])
        
        # Calculate confidence score
        error_count = len(operation['errors'])
        processing_results = result_data or {}
        confidence_score = self.error_handler.calculate_confidence_score(
            processing_results, error_count
        )
        
        # Determine if manual review is needed
        needs_manual_review = (
            confidence_score < self.config.confidence_threshold or
            self.error_handler.should_require_manual_review(confidence_score)
        )
        
        # Generate comprehensive report
        report = {
            'operation_id': operation_id,
            'operation_name': operation['operation_name'],
            'success': success,
            'duration': time.time() - operation['start_time'],
            'processing_duration': processing_duration,
            'confidence_score': confidence_score,
            'needs_manual_review': needs_manual_review,
            'error_count': error_count,
            'warning_count': len(operation['warnings']),
            'errors': operation['errors'],
            'warnings': operation['warnings'],
            'performance_profile': {
                'duration': profile.duration,
                'memory_peak': profile.memory_peak,
                'cpu_peak': profile.cpu_peak,
                'input_size': profile.input_size,
                'output_size': profile.output_size
            } if profile else None,
            'debug_session': {
                'session_id': session.session_id,
                'artifacts_count': len(session.artifacts_saved),
                'total_errors': session.total_errors,
                'total_warnings': session.total_warnings
            } if session else None,
            'result_data': result_data
        }
        
        # Clean up
        del self.active_operations[operation_id]
        if operation_id in self.processing_sessions:
            del self.processing_sessions[operation_id]
        
        self.logger.info(f"Completed operation {operation_id}: "
                        f"Success={success}, Confidence={confidence_score:.2f}, "
                        f"Errors={error_count}, Duration={report['duration']:.2f}s")
        
        return report
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status."""
        return {
            'timestamp': time.time(),
            'active_operations': len(self.active_operations),
            'error_handler_status': {
                'total_errors': len(self.error_handler.error_history),
                'recent_confidence_scores': self.error_handler.confidence_scores[-5:],
                'manual_review_flags': len(self.error_handler.manual_review_flags)
            },
            'performance_status': self.performance_monitor.get_performance_summary(300),  # Last 5 minutes
            'diagnostics_status': {
                'active_sessions': len(self.diagnostics.debug_sessions),
                'total_profiles': len(self.diagnostics.processing_profiles),
                'health_records': len(self.diagnostics.health_history)
            }
        }
    
    def force_system_optimization(self) -> Dict[str, Any]:
        """Force system optimization and return results."""
        optimization_results = {}
        
        try:
            # Memory optimization
            memory_result = self.performance_monitor.force_optimization('memory_cleanup')
            optimization_results['memory_cleanup'] = {
                'success': memory_result.success,
                'memory_freed_mb': memory_result.memory_freed_mb,
                'time_taken': memory_result.time_taken
            }
        except Exception as e:
            optimization_results['memory_cleanup'] = {'error': str(e)}
        
        try:
            # Cache optimization
            cache_result = self.performance_monitor.force_optimization('cache_cleanup')
            optimization_results['cache_cleanup'] = {
                'success': cache_result.success,
                'memory_freed_mb': cache_result.memory_freed_mb,
                'time_taken': cache_result.time_taken
            }
        except Exception as e:
            optimization_results['cache_cleanup'] = {'error': str(e)}
        
        return optimization_results
    
    def export_comprehensive_report(self, 
                                  output_path: Optional[str] = None,
                                  include_debug_data: bool = False) -> str:
        """
        Export comprehensive system report.
        
        Args:
            output_path: Path for the report file
            include_debug_data: Whether to include detailed debug data
        
        Returns:
            Path to the exported report
        """
        if output_path is None:
            output_path = f"logs/comprehensive_report_{int(time.time())}.json"
        
        # Generate comprehensive report
        report = {
            'timestamp': time.time(),
            'system_status': self.get_system_status(),
            'error_diagnostics': self.error_handler.generate_diagnostic_report(),
            'performance_summary': self.performance_monitor.get_performance_summary(),
            'diagnostics_summary': self.diagnostics.get_performance_summary(),
            'health_summary': self.diagnostics.get_system_health_summary(),
            'configuration': {
                'debug_mode': self.config.debug_mode,
                'save_debug_artifacts': self.config.save_debug_artifacts,
                'enable_performance_monitoring': self.config.enable_performance_monitoring,
                'enable_auto_optimization': self.config.enable_auto_optimization,
                'confidence_threshold': self.config.confidence_threshold
            }
        }
        
        if include_debug_data:
            report['debug_sessions'] = {
                session_id: session for session_id, session in self.diagnostics.debug_sessions.items()
            }
            report['recent_alerts'] = self.performance_monitor.get_recent_alerts(20)
        
        # Save report
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        import json
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        self.logger.info(f"Comprehensive report exported to {output_path}")
        return output_path
    
    def cleanup(self):
        """Cleanup all error handling components."""
        try:
            # Complete any active operations
            for operation_id in list(self.active_operations.keys()):
                self.complete_processing_operation(operation_id, success=False)
            
            # Stop monitoring
            self.stop_monitoring()
            
            # Cleanup components
            self.error_handler.cleanup()
            self.diagnostics.cleanup()
            self.performance_monitor.cleanup()
            
            self.logger.info("Integrated error handler cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")


# Convenience decorators for easy integration
def with_error_handling(integrated_handler: IntegratedErrorHandler, 
                       operation_name: str,
                       stage: ProcessingStage):
    """Decorator for automatic error handling integration."""
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            operation_id = integrated_handler.start_processing_operation(
                operation_name, 
                {'args_count': len(args), 'kwargs_keys': list(kwargs.keys())}
            )
            
            try:
                result = func(*args, **kwargs)
                
                # Complete operation successfully
                report = integrated_handler.complete_processing_operation(
                    operation_id, 
                    success=True,
                    result_data={'result_type': type(result).__name__}
                )
                
                return result
                
            except Exception as e:
                # Handle error
                context = {
                    'function_name': func.__name__,
                    'args_count': len(args),
                    'kwargs': kwargs
                }
                
                success, recovered_result = integrated_handler.handle_processing_error(
                    operation_id, e, stage, context
                )
                
                # Complete operation with error
                integrated_handler.complete_processing_operation(
                    operation_id, 
                    success=success,
                    result_data={'error': str(e), 'recovery_attempted': True}
                )
                
                if success and recovered_result is not None:
                    return recovered_result
                else:
                    raise  # Re-raise if recovery failed
        
        return wrapper
    return decorator


def with_performance_monitoring(integrated_handler: IntegratedErrorHandler):
    """Decorator for automatic performance monitoring."""
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            with integrated_handler.performance_monitor.performance_context(func.__name__):
                return func(*args, **kwargs)
        return wrapper
    return decorator