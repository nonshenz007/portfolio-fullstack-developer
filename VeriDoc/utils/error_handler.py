"""
Comprehensive error handling and diagnostics system for Veridoc photo verification.
Provides robust error recovery, detailed logging, and performance monitoring.

NOTE: This module is deprecated. Use core.error_handler instead for consistency.
"""

import logging
import traceback
import time
import psutil
import os
import json
import threading
from typing import Dict, List, Optional, Any, Callable, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
import numpy as np
from datetime import datetime

# Import core error handler to maintain compatibility
from core.error_handler import get_error_handler as get_core_error_handler


class ErrorSeverity(Enum):
    """Error severity levels for classification and handling."""
    CRITICAL = "critical"
    MAJOR = "major"
    MINOR = "minor"
    WARNING = "warning"
    INFO = "info"


class ProcessingStage(Enum):
    """Processing stages for error context tracking."""
    IMAGE_LOADING = "image_loading"
    FACE_DETECTION = "face_detection"
    LANDMARK_ANALYSIS = "landmark_analysis"
    ICAO_VALIDATION = "icao_validation"
    QUALITY_ASSESSMENT = "quality_assessment"
    AUTO_FIX = "auto_fix"
    EXPORT = "export"
    BATCH_PROCESSING = "batch_processing"


@dataclass
class ErrorContext:
    """Comprehensive error context information."""
    error_id: str
    timestamp: float
    stage: ProcessingStage
    severity: ErrorSeverity
    message: str
    exception_type: str
    stack_trace: str
    image_path: Optional[str] = None
    image_dimensions: Optional[Tuple[int, int]] = None
    processing_params: Optional[Dict[str, Any]] = None
    system_metrics: Optional[Dict[str, Any]] = None
    recovery_attempted: bool = False
    recovery_successful: bool = False
    confidence_score: Optional[float] = None


@dataclass
class RecoveryStrategy:
    """Error recovery strategy definition."""
    name: str
    applicable_stages: List[ProcessingStage]
    applicable_errors: List[str]
    max_attempts: int
    recovery_function: Callable
    fallback_strategy: Optional[str] = None


@dataclass
class ProcessingMetrics:
    """System performance and resource metrics."""
    cpu_usage: float
    memory_usage: float
    memory_available: float
    processing_time: float
    gpu_usage: Optional[float] = None
    disk_io: Optional[Dict[str, float]] = None
    network_io: Optional[Dict[str, float]] = None


@dataclass
class DiagnosticInfo:
    """Comprehensive diagnostic information."""
    system_info: Dict[str, Any]
    processing_history: List[ErrorContext]
    performance_metrics: ProcessingMetrics
    confidence_scores: List[float]
    manual_review_flags: List[str]
    debug_artifacts: List[str]


class ProcessingErrorHandler:
    """
    Comprehensive error handling system with recovery strategies,
    detailed logging, and performance monitoring.
    """
    
    def __init__(self, 
                 debug_mode: bool = False,
                 save_debug_artifacts: bool = False,
                 debug_output_dir: str = "temp/debug"):
        """
        Initialize the error handler with configuration options.
        
        Args:
            debug_mode: Enable detailed debugging and intermediate step saving
            save_debug_artifacts: Save intermediate processing steps for analysis
            debug_output_dir: Directory for saving debug artifacts
        """
        self.debug_mode = debug_mode
        self.save_debug_artifacts = save_debug_artifacts
        self.debug_output_dir = Path(debug_output_dir)
        self.debug_output_dir.mkdir(parents=True, exist_ok=True)
        
        # Error tracking
        self.error_history: List[ErrorContext] = []
        self.recovery_attempts: Dict[str, int] = {}
        self.confidence_scores: List[float] = []
        self.manual_review_flags: List[str] = []
        
        # Performance monitoring
        self.performance_history: List[ProcessingMetrics] = []
        self.processing_start_time: Optional[float] = None
        
        # Setup logging
        self._setup_logging()
        
        # Initialize recovery strategies
        self._initialize_recovery_strategies()
        
        # System monitoring
        self._start_system_monitoring()
    
    def _setup_logging(self):
        """Setup comprehensive logging system."""
        # Create logs directory
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # Configure main logger
        self.logger = logging.getLogger("veridoc_error_handler")
        self.logger.setLevel(logging.DEBUG if self.debug_mode else logging.INFO)
        
        # File handler for detailed logs
        file_handler = logging.FileHandler(log_dir / "error_diagnostics.log")
        file_handler.setLevel(logging.DEBUG)
        
        # Console handler for immediate feedback
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)
        
        # Detailed formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def _initialize_recovery_strategies(self):
        """Initialize error recovery strategies."""
        self.recovery_strategies: Dict[str, RecoveryStrategy] = {
            'face_detection_failed': RecoveryStrategy(
                name="Face Detection Recovery",
                applicable_stages=[ProcessingStage.FACE_DETECTION],
                applicable_errors=['no_face_detected', 'low_confidence_detection'],
                max_attempts=3,
                recovery_function=self._recover_face_detection
            ),
            'image_enhancement': RecoveryStrategy(
                name="Image Enhancement Recovery",
                applicable_stages=[ProcessingStage.IMAGE_LOADING, ProcessingStage.QUALITY_ASSESSMENT],
                applicable_errors=['poor_image_quality', 'low_resolution', 'poor_lighting'],
                max_attempts=2,
                recovery_function=self._recover_image_quality
            ),
            'memory_optimization': RecoveryStrategy(
                name="Memory Optimization Recovery",
                applicable_stages=list(ProcessingStage),
                applicable_errors=['memory_error', 'out_of_memory'],
                max_attempts=1,
                recovery_function=self._recover_memory_issues
            ),
            'validation_inconsistency': RecoveryStrategy(
                name="Validation Consistency Recovery",
                applicable_stages=[ProcessingStage.ICAO_VALIDATION],
                applicable_errors=['inconsistent_results', 'validation_conflict'],
                max_attempts=2,
                recovery_function=self._recover_validation_issues
            ),
            'auto_fix_degradation': RecoveryStrategy(
                name="Auto-Fix Quality Recovery",
                applicable_stages=[ProcessingStage.AUTO_FIX],
                applicable_errors=['quality_degradation', 'fix_failed'],
                max_attempts=1,
                recovery_function=self._recover_auto_fix_issues
            )
        }
    
    def _start_system_monitoring(self):
        """Start background system monitoring."""
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self._monitor_system_resources)
        self.monitoring_thread.daemon = True
        self.monitoring_thread.start()
    
    def _monitor_system_resources(self):
        """Monitor system resources in background."""
        while self.monitoring_active:
            try:
                metrics = self._collect_system_metrics()
                self.performance_history.append(metrics)
                
                # Keep only recent metrics (last 100 entries)
                if len(self.performance_history) > 100:
                    self.performance_history = self.performance_history[-100:]
                
                # Check for resource issues
                self._check_resource_warnings(metrics)
                
                time.sleep(5)  # Monitor every 5 seconds
            except Exception as e:
                self.logger.warning(f"System monitoring error: {e}")
                time.sleep(10)  # Wait longer on error
    
    def _collect_system_metrics(self) -> ProcessingMetrics:
        """Collect current system performance metrics."""
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        
        processing_time = 0.0
        if self.processing_start_time:
            processing_time = time.time() - self.processing_start_time
        
        return ProcessingMetrics(
            cpu_usage=cpu_percent,
            memory_usage=memory.percent,
            memory_available=memory.available / (1024**3),  # GB
            processing_time=processing_time
        )
    
    def _check_resource_warnings(self, metrics: ProcessingMetrics):
        """Check for resource usage warnings."""
        if metrics.memory_usage > 85:
            self.logger.warning(f"High memory usage: {metrics.memory_usage:.1f}%")
            self._flag_for_manual_review("high_memory_usage")
        
        if metrics.cpu_usage > 90:
            self.logger.warning(f"High CPU usage: {metrics.cpu_usage:.1f}%")
    
    def handle_error(self, 
                    error: Exception,
                    stage: ProcessingStage,
                    context: Dict[str, Any],
                    image_data: Optional[np.ndarray] = None) -> Tuple[bool, Optional[Any]]:
        """
        Handle processing errors with comprehensive recovery strategies.
        
        Args:
            error: The exception that occurred
            stage: Processing stage where error occurred
            context: Additional context information
            image_data: Image data for debugging (optional)
        
        Returns:
            Tuple of (recovery_successful, recovered_result)
        """
        error_id = f"{stage.value}_{int(time.time())}"
        
        # Create error context
        error_context = ErrorContext(
            error_id=error_id,
            timestamp=time.time(),
            stage=stage,
            severity=self._classify_error_severity(error, stage),
            message=str(error),
            exception_type=type(error).__name__,
            stack_trace=traceback.format_exc(),
            image_path=context.get('image_path'),
            image_dimensions=context.get('image_dimensions'),
            processing_params=context.get('processing_params'),
            system_metrics=asdict(self._collect_system_metrics())
        )
        
        # Log error with full context
        self._log_error(error_context)
        
        # Save debug artifacts if enabled
        if self.save_debug_artifacts and image_data is not None:
            self._save_debug_artifact(error_context, image_data, context)
        
        # Attempt recovery
        recovery_successful, result = self._attempt_recovery(error_context, context, image_data)
        
        # Update error context with recovery results
        error_context.recovery_attempted = True
        error_context.recovery_successful = recovery_successful
        
        # Store error in history
        self.error_history.append(error_context)
        
        # Check if manual review is needed
        if not recovery_successful or error_context.severity in [ErrorSeverity.CRITICAL, ErrorSeverity.MAJOR]:
            self._flag_for_manual_review(f"error_{error_id}")
        
        return recovery_successful, result
    
    def _classify_error_severity(self, error: Exception, stage: ProcessingStage) -> ErrorSeverity:
        """Classify error severity based on type and stage."""
        error_type = type(error).__name__
        
        # Critical errors that prevent processing
        if error_type in ['MemoryError', 'SystemError', 'OSError']:
            return ErrorSeverity.CRITICAL
        
        # Major errors that significantly impact results
        if stage == ProcessingStage.FACE_DETECTION and error_type in ['ValueError', 'RuntimeError']:
            return ErrorSeverity.MAJOR
        
        # Minor errors that can be recovered from
        if error_type in ['UserWarning', 'DeprecationWarning']:
            return ErrorSeverity.WARNING
        
        # Default to major for unknown errors
        return ErrorSeverity.MAJOR
    
    def _log_error(self, error_context: ErrorContext):
        """Log error with comprehensive context information."""
        log_level = {
            ErrorSeverity.CRITICAL: logging.CRITICAL,
            ErrorSeverity.MAJOR: logging.ERROR,
            ErrorSeverity.MINOR: logging.WARNING,
            ErrorSeverity.WARNING: logging.WARNING,
            ErrorSeverity.INFO: logging.INFO
        }[error_context.severity]
        
        self.logger.log(log_level, 
            f"Error {error_context.error_id} in {error_context.stage.value}: "
            f"{error_context.message}")
        
        if self.debug_mode:
            self.logger.debug(f"Full error context: {asdict(error_context)}")
    
    def _save_debug_artifact(self, 
                           error_context: ErrorContext, 
                           image_data: np.ndarray,
                           context: Dict[str, Any]):
        """Save debug artifacts for error analysis."""
        try:
            import cv2
            
            artifact_dir = self.debug_output_dir / error_context.error_id
            artifact_dir.mkdir(exist_ok=True)
            
            # Save error image
            if image_data is not None:
                cv2.imwrite(str(artifact_dir / "error_image.jpg"), image_data)
            
            # Save error context as JSON
            with open(artifact_dir / "error_context.json", 'w') as f:
                json.dump(asdict(error_context), f, indent=2, default=str)
            
            # Save processing context
            with open(artifact_dir / "processing_context.json", 'w') as f:
                json.dump(context, f, indent=2, default=str)
            
            self.logger.debug(f"Debug artifacts saved to {artifact_dir}")
            
        except Exception as e:
            self.logger.warning(f"Failed to save debug artifacts: {e}")
    
    def _attempt_recovery(self, 
                         error_context: ErrorContext,
                         context: Dict[str, Any],
                         image_data: Optional[np.ndarray]) -> Tuple[bool, Optional[Any]]:
        """Attempt error recovery using appropriate strategies."""
        error_type = error_context.exception_type.lower()
        stage = error_context.stage
        
        # Find applicable recovery strategies
        applicable_strategies = []
        for strategy_name, strategy in self.recovery_strategies.items():
            if (stage in strategy.applicable_stages and 
                any(error_key in error_context.message.lower() or 
                    error_key in error_type for error_key in strategy.applicable_errors)):
                applicable_strategies.append(strategy)
        
        # Try recovery strategies in order
        for strategy in applicable_strategies:
            strategy_key = f"{error_context.error_id}_{strategy.name}"
            attempts = self.recovery_attempts.get(strategy_key, 0)
            
            if attempts < strategy.max_attempts:
                self.logger.info(f"Attempting recovery with strategy: {strategy.name}")
                self.recovery_attempts[strategy_key] = attempts + 1
                
                try:
                    result = strategy.recovery_function(error_context, context, image_data)
                    if result is not None:
                        self.logger.info(f"Recovery successful with strategy: {strategy.name}")
                        return True, result
                except Exception as recovery_error:
                    self.logger.warning(f"Recovery strategy {strategy.name} failed: {recovery_error}")
        
        # No recovery successful
        self.logger.error(f"All recovery strategies failed for error {error_context.error_id}")
        return False, None
    
    def _recover_face_detection(self, 
                              error_context: ErrorContext,
                              context: Dict[str, Any],
                              image_data: Optional[np.ndarray]) -> Optional[Any]:
        """Recovery strategy for face detection failures."""
        if image_data is None:
            return None
        
        try:
            import cv2
            
            # Try image enhancement
            enhanced = cv2.convertScaleAbs(image_data, alpha=1.2, beta=30)
            
            # Try histogram equalization
            if len(enhanced.shape) == 3:
                enhanced = cv2.cvtColor(enhanced, cv2.COLOR_BGR2GRAY)
            enhanced = cv2.equalizeHist(enhanced)
            
            # Convert back to color if needed
            if len(image_data.shape) == 3:
                enhanced = cv2.cvtColor(enhanced, cv2.COLOR_GRAY2BGR)
            
            return enhanced
            
        except Exception as e:
            self.logger.warning(f"Face detection recovery failed: {e}")
            return None
    
    def _recover_image_quality(self,
                             error_context: ErrorContext,
                             context: Dict[str, Any],
                             image_data: Optional[np.ndarray]) -> Optional[Any]:
        """Recovery strategy for image quality issues."""
        if image_data is None:
            return None
        
        try:
            import cv2
            
            # Apply noise reduction
            denoised = cv2.bilateralFilter(image_data, 9, 75, 75)
            
            # Apply sharpening
            kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
            sharpened = cv2.filter2D(denoised, -1, kernel)
            
            return sharpened
            
        except Exception as e:
            self.logger.warning(f"Image quality recovery failed: {e}")
            return None
    
    def _recover_memory_issues(self,
                             error_context: ErrorContext,
                             context: Dict[str, Any],
                             image_data: Optional[np.ndarray]) -> Optional[Any]:
        """Recovery strategy for memory issues."""
        try:
            import gc
            
            # Force garbage collection
            gc.collect()
            
            # Reduce image size if too large
            if image_data is not None and image_data.size > 10000000:  # 10M pixels
                import cv2
                height, width = image_data.shape[:2]
                new_height, new_width = height // 2, width // 2
                resized = cv2.resize(image_data, (new_width, new_height))
                return resized
            
            return image_data
            
        except Exception as e:
            self.logger.warning(f"Memory recovery failed: {e}")
            return None
    
    def _recover_validation_issues(self,
                                 error_context: ErrorContext,
                                 context: Dict[str, Any],
                                 image_data: Optional[np.ndarray]) -> Optional[Any]:
        """Recovery strategy for validation inconsistencies."""
        try:
            # Return a partial validation result with lower confidence
            return {
                'partial_validation': True,
                'confidence_score': 0.5,
                'requires_manual_review': True,
                'recovery_applied': True
            }
        except Exception as e:
            self.logger.warning(f"Validation recovery failed: {e}")
            return None
    
    def _recover_auto_fix_issues(self,
                               error_context: ErrorContext,
                               context: Dict[str, Any],
                               image_data: Optional[np.ndarray]) -> Optional[Any]:
        """Recovery strategy for auto-fix quality degradation."""
        try:
            # Return original image with flag for manual processing
            return {
                'original_image': image_data,
                'auto_fix_failed': True,
                'requires_manual_fix': True,
                'recovery_applied': True
            }
        except Exception as e:
            self.logger.warning(f"Auto-fix recovery failed: {e}")
            return None
    
    def calculate_confidence_score(self, 
                                 processing_results: Dict[str, Any],
                                 error_count: int = 0) -> float:
        """
        Calculate confidence score based on processing results and error history.
        
        Args:
            processing_results: Results from processing pipeline
            error_count: Number of errors encountered
        
        Returns:
            Confidence score between 0.0 and 1.0
        """
        base_confidence = 1.0
        
        # Reduce confidence based on errors
        error_penalty = min(error_count * 0.1, 0.5)
        base_confidence -= error_penalty
        
        # Adjust based on processing quality
        if 'face_detection_confidence' in processing_results:
            face_conf = processing_results['face_detection_confidence']
            base_confidence *= face_conf
        
        if 'validation_consistency' in processing_results:
            validation_conf = processing_results['validation_consistency']
            base_confidence *= validation_conf
        
        # Consider system performance
        if self.performance_history:
            recent_metrics = self.performance_history[-1]
            if recent_metrics.memory_usage > 90:
                base_confidence *= 0.9
            if recent_metrics.cpu_usage > 95:
                base_confidence *= 0.9
        
        # Ensure confidence is within bounds
        confidence = max(0.0, min(1.0, base_confidence))
        self.confidence_scores.append(confidence)
        
        return confidence
    
    def _flag_for_manual_review(self, reason: str):
        """Flag processing result for manual review."""
        flag = f"{datetime.now().isoformat()}_{reason}"
        self.manual_review_flags.append(flag)
        self.logger.warning(f"Flagged for manual review: {reason}")
    
    def should_require_manual_review(self, confidence_score: float) -> bool:
        """Determine if manual review is required based on confidence and errors."""
        # Low confidence requires manual review
        if confidence_score < 0.7:
            return True
        
        # Recent critical errors require manual review
        recent_errors = [e for e in self.error_history[-10:] 
                        if e.severity == ErrorSeverity.CRITICAL]
        if recent_errors:
            return True
        
        # Multiple recent errors require manual review
        recent_major_errors = [e for e in self.error_history[-5:] 
                              if e.severity == ErrorSeverity.MAJOR]
        if len(recent_major_errors) >= 2:
            return True
        
        return False
    
    def start_processing_timer(self):
        """Start timing for processing operation."""
        self.processing_start_time = time.time()
    
    def stop_processing_timer(self) -> float:
        """Stop timing and return processing duration."""
        if self.processing_start_time:
            duration = time.time() - self.processing_start_time
            self.processing_start_time = None
            return duration
        return 0.0
    
    def get_diagnostic_info(self) -> DiagnosticInfo:
        """Get comprehensive diagnostic information."""
        return DiagnosticInfo(
            system_info={
                'cpu_count': psutil.cpu_count(),
                'memory_total': psutil.virtual_memory().total / (1024**3),
                'python_version': os.sys.version,
                'platform': os.name
            },
            processing_history=self.error_history[-20:],  # Last 20 errors
            performance_metrics=self.performance_history[-1] if self.performance_history else None,
            confidence_scores=self.confidence_scores[-10:],  # Last 10 scores
            manual_review_flags=self.manual_review_flags[-10:],  # Last 10 flags
            debug_artifacts=list(os.listdir(self.debug_output_dir)) if self.debug_output_dir.exists() else []
        )
    
    def generate_diagnostic_report(self) -> Dict[str, Any]:
        """Generate comprehensive diagnostic report."""
        diagnostic_info = self.get_diagnostic_info()
        
        # Calculate statistics
        error_stats = {}
        for error in diagnostic_info.processing_history:
            stage = error.stage.value
            severity = error.severity.value
            key = f"{stage}_{severity}"
            error_stats[key] = error_stats.get(key, 0) + 1
        
        avg_confidence = np.mean(diagnostic_info.confidence_scores) if diagnostic_info.confidence_scores else 0.0
        
        return {
            'timestamp': datetime.now().isoformat(),
            'system_info': diagnostic_info.system_info,
            'error_statistics': error_stats,
            'average_confidence': avg_confidence,
            'manual_review_count': len(diagnostic_info.manual_review_flags),
            'recent_errors': [asdict(e) for e in diagnostic_info.processing_history],
            'performance_summary': asdict(diagnostic_info.performance_metrics) if diagnostic_info.performance_metrics else None,
            'debug_artifacts_count': len(diagnostic_info.debug_artifacts)
        }
    
    def cleanup(self):
        """Cleanup resources and stop monitoring."""
        self.monitoring_active = False
        if hasattr(self, 'monitoring_thread'):
            self.monitoring_thread.join(timeout=5)
        
        # Save final diagnostic report
        try:
            report = self.generate_diagnostic_report()
            report_path = Path("logs") / f"diagnostic_report_{int(time.time())}.json"
            with open(report_path, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            self.logger.info(f"Final diagnostic report saved to {report_path}")
        except Exception as e:
            self.logger.warning(f"Failed to save diagnostic report: {e}")


# Compatibility function to redirect to core error handler
def get_processing_error_handler():
    """
    Get a processing error handler that uses the core error handler for consistency.

    This function is deprecated. Use core.error_handler.get_error_handler() instead.
    """
    return get_core_error_handler()


# Maintain backward compatibility
ProcessingErrorHandler = get_processing_error_handler