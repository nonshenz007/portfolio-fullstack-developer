"""
Core Processing Controller for VeriDoc

Provides the main entry point for all photo processing operations.
This is the single, unified processing pipeline that coordinates all components.
"""

import logging
import time
import cv2
import numpy as np
from typing import Dict, List, Optional, Any, Callable
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum

from .config_manager import ConfigManager

logger = logging.getLogger(__name__)


class ProcessingStage(Enum):
    """Enumeration of processing stages for progress tracking."""
    INITIALIZING = "initializing"
    LOADING_IMAGE = "loading_image"
    DETECTING_FACE = "detecting_face"
    VALIDATING_COMPLIANCE = "validating_compliance"
    APPLYING_AUTOFIX = "applying_autofix"
    FINALIZING = "finalizing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class ProcessingProgress:
    """Progress information for UI updates."""
    stage: ProcessingStage
    progress_percent: float
    message: str
    details: Optional[str] = None
    timestamp: float = field(default_factory=time.time)


@dataclass
class ProcessingResult:
    """Result of photo processing operation."""
    success: bool
    compliance_score: float
    passes_requirements: bool
    face_detected: bool
    issues: List[str]
    suggestions: List[str]
    processing_time: float
    auto_fix_applied: bool = False
    export_path: Optional[str] = None
    error_message: Optional[str] = None
    # Enhanced result data
    face_metrics: Optional[Any] = None
    validation_details: Optional[Any] = None
    processing_stages: List[ProcessingProgress] = field(default_factory=list)


@dataclass
class ValidationResult:
    """Result of validation-only operation."""
    success: bool
    compliance_score: float
    passes_requirements: bool
    face_detected: bool
    issues: List[str]
    suggestions: List[str]
    processing_time: float
    face_metrics: Optional[Any] = None
    validation_details: Optional[Any] = None


@dataclass
class AutoFixResult:
    """Result of auto-fix operation."""
    success: bool
    improvements: List[str]
    before_score: float
    after_score: float
    fixed_image_path: Optional[str]
    processing_time: float
    error_message: Optional[str] = None


@dataclass
class BatchResult:
    """Result of batch processing operation."""
    total_images: int
    successful: int
    failed: int
    results: List[ProcessingResult]
    processing_time: float
    summary: Dict[str, Any]


class ProcessingController:
    """
    Main processing controller for VeriDoc Core.
    
    This class provides the single entry point for all photo processing operations.
    It coordinates face detection, validation, and auto-fix functionality in a
    unified, reliable pipeline.
    """
    
    def __init__(self, config_manager: Optional[ConfigManager] = None):
        """
        Initialize the processing controller.
        
        Args:
            config_manager: Configuration manager instance
        """
        self.config_manager = config_manager or ConfigManager()
        self.logger = logging.getLogger(__name__)
        
        # Progress callback for UI updates
        self.progress_callback: Optional[Callable[[ProcessingProgress], None]] = None
        
        # Initialize components (lazy loading for better startup performance)
        self._face_detector = None
        self._icao_validator = None
        self._autofix_engine = None
        self._quality_checker = None
        
        # Processing statistics
        self.stats = {
            'total_processed': 0,
            'successful': 0,
            'failed': 0,
            'average_processing_time': 0.0,
            'last_reset': time.time()
        }
        
        self.logger.info("ProcessingController initialized")
    
    def set_progress_callback(self, callback: Callable[[ProcessingProgress], None]):
        """
        Set callback function for progress updates.
        
        Args:
            callback: Function to call with progress updates
        """
        self.progress_callback = callback
    
    def _report_progress(self, stage: ProcessingStage, progress: float, message: str, details: str = None):
        """
        Report processing progress to callback if set.
        
        Args:
            stage: Current processing stage
            progress: Progress percentage (0-100)
            message: Progress message
            details: Optional detailed information
        """
        if self.progress_callback:
            progress_info = ProcessingProgress(
                stage=stage,
                progress_percent=progress,
                message=message,
                details=details
            )
            try:
                self.progress_callback(progress_info)
            except Exception as e:
                self.logger.warning(f"Progress callback failed: {e}")
    
    @property
    def face_detector(self):
        """Lazy-loaded face detector."""
        if self._face_detector is None:
            try:
                from detection.face_detector import FaceDetector
                self._face_detector = FaceDetector()
                self.logger.info("Face detector initialized")
            except Exception as e:
                self.logger.error(f"Failed to initialize face detector: {e}")
                raise RuntimeError(f"Face detector initialization failed: {e}")
        return self._face_detector
    
    @property
    def icao_validator(self):
        """Lazy-loaded ICAO validator."""
        if self._icao_validator is None:
            try:
                from validation.icao_validator import ICAOValidator
                format_rules = self.config_manager.formats
                self._icao_validator = ICAOValidator(format_rules)
                self.logger.info("ICAO validator initialized")
            except Exception as e:
                self.logger.error(f"Failed to initialize ICAO validator: {e}")
                raise RuntimeError(f"ICAO validator initialization failed: {e}")
        return self._icao_validator
    
    @property
    def autofix_engine(self):
        """Lazy-loaded auto-fix engine."""
        if self._autofix_engine is None:
            try:
                from autofix.auto_enhancer import AutoEnhancer
                self._autofix_engine = AutoEnhancer()
                self.logger.info("Auto-fix engine initialized successfully")
            except Exception as e:
                self.logger.error(f"Failed to initialize auto-fix engine: {e}")
                return None
        return self._autofix_engine
    
    @property
    def quality_checker(self):
        """Lazy-loaded quality checker."""
        if self._quality_checker is None:
            try:
                # TODO: Implement QualityChecker in task 6
                # For now, return None to indicate not available
                self.logger.info("Quality checker not yet implemented")
                return None
            except Exception as e:
                self.logger.error(f"Failed to initialize quality checker: {e}")
                return None
        return self._quality_checker
    
    def process_image(self, image_path: str, format_name: str, apply_autofix: bool = False) -> ProcessingResult:
        """
        Process a single image for compliance validation with optional auto-fix.
        
        This is the main processing pipeline that coordinates all components:
        1. Load and validate image
        2. Detect face and extract metrics
        3. Validate compliance against format requirements
        4. Apply auto-fix if requested and beneficial
        5. Re-validate if auto-fix was applied
        
        Args:
            image_path: Path to the image file
            format_name: Name of the format to validate against
            apply_autofix: Whether to apply auto-fix if issues are found
            
        Returns:
            ProcessingResult with comprehensive validation results
        """
        start_time = time.time()
        processing_stages = []
        
        try:
            # Stage 1: Initialize and validate inputs
            self._report_progress(ProcessingStage.INITIALIZING, 0, "Initializing processing")
            
            if not Path(image_path).exists():
                return self._create_error_result(
                    start_time, "Image file not found", 
                    ["Please check the file path and try again"],
                    processing_stages
                )
            
            format_config = self.config_manager.get_format_config(format_name)
            if not format_config:
                return self._create_error_result(
                    start_time, f"Unknown format: {format_name}",
                    ["Please select a valid format"],
                    processing_stages
                )
            
            self.logger.info(f"Processing image: {image_path} with format: {format_name}")
            
            # Stage 2: Load image
            self._report_progress(ProcessingStage.LOADING_IMAGE, 10, "Loading image")
            image = self._load_image(image_path)
            if image is None:
                return self._create_error_result(
                    start_time, "Failed to load image",
                    ["Please ensure the image file is valid and not corrupted"],
                    processing_stages
                )
            
            # Stage 3: Face detection
            self._report_progress(ProcessingStage.DETECTING_FACE, 25, "Detecting face")
            face_result = self.face_detector.detect_face(image)
            
            if not face_result.face_found:
                return ProcessingResult(
                    success=False,
                    compliance_score=0.0,
                    passes_requirements=False,
                    face_detected=False,
                    issues=[face_result.error_message or "No face detected"],
                    suggestions=[
                        "Ensure photo shows a clear frontal face",
                        "Use better lighting to make face more visible",
                        "Remove shadows from face area",
                        "Try a different photo angle"
                    ],
                    processing_time=time.time() - start_time,
                    processing_stages=processing_stages
                )
            
            # Stage 4: ICAO compliance validation
            self._report_progress(ProcessingStage.VALIDATING_COMPLIANCE, 50, "Validating compliance")
            compliance_result = self.icao_validator.validate_compliance(
                image, face_result.face_metrics, format_name
            )
            
            # Convert validation issues to simple strings for backward compatibility
            issues = [issue.message for issue in compliance_result.issues]
            suggestions = [issue.suggestion for issue in compliance_result.issues if issue.suggestion]
            
            # Stage 5: Auto-fix if requested and beneficial
            auto_fix_applied = False
            enhanced_image = image
            if apply_autofix and not compliance_result.overall_pass and self.autofix_engine:
                self._report_progress(ProcessingStage.APPLYING_AUTOFIX, 75, "Applying auto-fix")

                # Check if issues are auto-fixable
                fixable_issues = [issue for issue in compliance_result.issues if issue.auto_fixable]
                if fixable_issues:
                    try:
                        # Extract issue messages for auto-fix
                        issue_messages = [issue.message for issue in fixable_issues]

                        # Apply auto-fix using the AutoEnhancer
                        enhanced_image, operations = self.autofix_engine.enhance_photo(
                            image, issue_messages
                        )

                        if enhanced_image is not image:  # Check if image was actually modified
                            auto_fix_applied = True
                            self.logger.info(f"Applied auto-fix operations: {operations}")

                            # Re-validate the enhanced image
                            self._report_progress(ProcessingStage.APPLYING_AUTOFIX, 85, "Re-validating enhanced image")
                            enhanced_face_result = self.face_detector.detect_face(enhanced_image)

                            if enhanced_face_result.face_found:
                                enhanced_compliance_result = self.icao_validator.validate_compliance(
                                    enhanced_image, enhanced_face_result.face_metrics, format_name
                                )

                                # Update results with enhanced image validation
                                if enhanced_compliance_result.overall_pass:
                                    compliance_result = enhanced_compliance_result
                                    face_result = enhanced_face_result
                                    issues = [issue.message for issue in enhanced_compliance_result.issues]
                                    suggestions = [issue.suggestion for issue in enhanced_compliance_result.issues if issue.suggestion]
                                    self.logger.info("Auto-fix successful - image now passes validation")
                                else:
                                    self.logger.info("Auto-fix applied but image still needs manual review")
                            else:
                                self.logger.warning("Auto-fix applied but face detection failed on enhanced image")
                        else:
                            self.logger.info("No auto-fix operations were applicable")

                    except Exception as e:
                        self.logger.error(f"Auto-fix failed: {e}")
                        auto_fix_applied = False
            
            # Stage 6: Finalize
            self._report_progress(ProcessingStage.FINALIZING, 90, "Finalizing results")
            
            processing_time = time.time() - start_time
            
            # Update statistics
            self._update_stats(True, processing_time)
            
            self._report_progress(ProcessingStage.COMPLETED, 100, "Processing completed")
            
            return ProcessingResult(
                success=True,
                compliance_score=compliance_result.compliance_score,
                passes_requirements=compliance_result.overall_pass,
                face_detected=face_result.face_found,
                issues=issues,
                suggestions=suggestions,
                processing_time=processing_time,
                auto_fix_applied=auto_fix_applied,
                face_metrics=face_result.face_metrics,
                validation_details=compliance_result,
                processing_stages=processing_stages
            )
            
        except Exception as e:
            self.logger.error(f"Error processing image {image_path}: {e}", exc_info=True)
            self._update_stats(False, time.time() - start_time)
            self._report_progress(ProcessingStage.FAILED, 0, f"Processing failed: {str(e)}")
            
            return ProcessingResult(
                success=False,
                compliance_score=0.0,
                passes_requirements=False,
                face_detected=False,
                issues=[f"Processing error: {str(e)}"],
                suggestions=["Please try again or contact support"],
                processing_time=time.time() - start_time,
                error_message=str(e),
                processing_stages=processing_stages
            )
    
    def _load_image(self, image_path: str) -> Optional[np.ndarray]:
        """
        Load image from file with error handling.
        
        Args:
            image_path: Path to image file
            
        Returns:
            Loaded image as numpy array or None if failed
        """
        try:
            image = cv2.imread(image_path)
            if image is None:
                self.logger.error(f"Failed to load image: {image_path}")
                return None
            
            # Validate image dimensions
            if image.shape[0] < 100 or image.shape[1] < 100:
                self.logger.error(f"Image too small: {image.shape}")
                return None
            
            # Optimize image size for processing if too large
            max_size = self.config_manager.get_setting('processing.max_image_size', 2000)
            if image.shape[0] > max_size or image.shape[1] > max_size:
                scale = min(max_size / image.shape[1], max_size / image.shape[0])
                new_width = int(image.shape[1] * scale)
                new_height = int(image.shape[0] * scale)
                image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_LANCZOS4)
                self.logger.info(f"Resized image to {new_width}x{new_height} for processing")
            
            return image
            
        except Exception as e:
            self.logger.error(f"Error loading image {image_path}: {e}")
            return None
    
    def _create_error_result(self, start_time: float, error_message: str, 
                           suggestions: List[str], processing_stages: List[ProcessingProgress]) -> ProcessingResult:
        """
        Create a standardized error result.
        
        Args:
            start_time: Processing start time
            error_message: Error message
            suggestions: List of suggestions
            processing_stages: Processing stages completed
            
        Returns:
            ProcessingResult indicating failure
        """
        self._update_stats(False, time.time() - start_time)
        self._report_progress(ProcessingStage.FAILED, 0, error_message)
        
        return ProcessingResult(
            success=False,
            compliance_score=0.0,
            passes_requirements=False,
            face_detected=False,
            issues=[error_message],
            suggestions=suggestions,
            processing_time=time.time() - start_time,
            error_message=error_message,
            processing_stages=processing_stages
        )
    
    def _update_stats(self, success: bool, processing_time: float):
        """
        Update processing statistics.
        
        Args:
            success: Whether processing was successful
            processing_time: Time taken for processing
        """
        self.stats['total_processed'] += 1
        if success:
            self.stats['successful'] += 1
        else:
            self.stats['failed'] += 1
        
        # Update average processing time
        total_time = self.stats['average_processing_time'] * (self.stats['total_processed'] - 1)
        self.stats['average_processing_time'] = (total_time + processing_time) / self.stats['total_processed']
    
    def batch_process(self, image_paths: List[str], format_name: str, 
                     apply_autofix: bool = False) -> BatchResult:
        """
        Process multiple images in batch with progress tracking and error recovery.
        
        Args:
            image_paths: List of paths to image files
            format_name: Name of the format to validate against
            apply_autofix: Whether to apply auto-fix for each image
            
        Returns:
            BatchResult with summary of all processing results
        """
        start_time = time.time()
        results = []
        successful = 0
        failed = 0
        
        self.logger.info(f"Starting batch processing of {len(image_paths)} images with format: {format_name}")
        
        # Validate format before processing any images
        format_config = self.config_manager.get_format_config(format_name)
        if not format_config:
            self.logger.error(f"Invalid format for batch processing: {format_name}")
            return BatchResult(
                total_images=len(image_paths),
                successful=0,
                failed=len(image_paths),
                results=[],
                processing_time=time.time() - start_time,
                summary={
                    "error": f"Invalid format: {format_name}",
                    "total_images": len(image_paths),
                    "successful": 0,
                    "failed": len(image_paths),
                    "success_rate": 0.0,
                    "format_used": format_name
                }
            )
        
        # Process each image with error recovery
        for i, image_path in enumerate(image_paths):
            try:
                # Report batch progress
                batch_progress = (i / len(image_paths)) * 100
                self._report_progress(
                    ProcessingStage.INITIALIZING, 
                    batch_progress,
                    f"Processing image {i+1} of {len(image_paths)}",
                    f"Current: {Path(image_path).name}"
                )
                
                result = self.process_image(image_path, format_name, apply_autofix)
                results.append(result)
                
                if result.success:
                    successful += 1
                    self.logger.debug(f"Successfully processed: {image_path}")
                else:
                    failed += 1
                    self.logger.warning(f"Failed to process: {image_path} - {result.error_message}")
                    
            except Exception as e:
                # Continue processing even if individual image fails
                failed += 1
                error_result = ProcessingResult(
                    success=False,
                    compliance_score=0.0,
                    passes_requirements=False,
                    face_detected=False,
                    issues=[f"Batch processing error: {str(e)}"],
                    suggestions=["Check image file and try again"],
                    processing_time=0.0,
                    error_message=str(e)
                )
                results.append(error_result)
                self.logger.error(f"Error in batch processing {image_path}: {e}", exc_info=True)
        
        processing_time = time.time() - start_time
        
        # Calculate detailed statistics
        compliance_scores = [r.compliance_score for r in results if r.success]
        avg_compliance = sum(compliance_scores) / len(compliance_scores) if compliance_scores else 0.0
        
        face_detection_rate = sum(1 for r in results if r.face_detected) / len(results) if results else 0.0
        
        # Categorize issues
        issue_categories = {}
        for result in results:
            for issue in result.issues:
                category = self._categorize_issue(issue)
                issue_categories[category] = issue_categories.get(category, 0) + 1
        
        summary = {
            "total_images": len(image_paths),
            "successful": successful,
            "failed": failed,
            "success_rate": successful / len(image_paths) if image_paths else 0,
            "average_processing_time": processing_time / len(image_paths) if image_paths else 0,
            "total_processing_time": processing_time,
            "format_used": format_name,
            "average_compliance_score": avg_compliance,
            "face_detection_rate": face_detection_rate,
            "auto_fix_applied": apply_autofix,
            "common_issues": issue_categories,
            "timestamp": time.time()
        }
        
        self.logger.info(f"Batch processing completed: {successful}/{len(image_paths)} successful "
                        f"(success rate: {summary['success_rate']:.1%})")
        
        # Report final progress
        self._report_progress(
            ProcessingStage.COMPLETED, 
            100,
            f"Batch processing completed: {successful}/{len(image_paths)} successful"
        )
        
        return BatchResult(
            total_images=len(image_paths),
            successful=successful,
            failed=failed,
            results=results,
            processing_time=processing_time,
            summary=summary
        )
    
    def _categorize_issue(self, issue: str) -> str:
        """
        Categorize an issue for statistics.
        
        Args:
            issue: Issue description
            
        Returns:
            Issue category
        """
        issue_lower = issue.lower()
        if 'face' in issue_lower and ('detect' in issue_lower or 'found' in issue_lower):
            return 'face_detection'
        elif 'background' in issue_lower:
            return 'background'
        elif 'dimension' in issue_lower or 'size' in issue_lower:
            return 'dimensions'
        elif 'sharp' in issue_lower or 'blur' in issue_lower:
            return 'sharpness'
        elif 'bright' in issue_lower or 'dark' in issue_lower or 'light' in issue_lower:
            return 'lighting'
        elif 'position' in issue_lower or 'center' in issue_lower:
            return 'positioning'
        else:
            return 'other'
    
    def validate_only(self, image_path: str, format_name: str) -> ValidationResult:
        """
        Validate an image without applying any fixes.
        
        This method performs only validation steps without any auto-fix attempts.
        It's useful for getting compliance assessment without modifying the image.
        
        Args:
            image_path: Path to the image file
            format_name: Name of the format to validate against
            
        Returns:
            ValidationResult with validation results only
        """
        start_time = time.time()
        
        try:
            # Use the main processing pipeline but skip auto-fix
            result = self.process_image(image_path, format_name, apply_autofix=False)
            
            # Convert to ValidationResult
            return ValidationResult(
                success=result.success,
                compliance_score=result.compliance_score,
                passes_requirements=result.passes_requirements,
                face_detected=result.face_detected,
                issues=result.issues,
                suggestions=result.suggestions,
                processing_time=result.processing_time,
                face_metrics=result.face_metrics,
                validation_details=result.validation_details
            )
            
        except Exception as e:
            self.logger.error(f"Error validating image {image_path}: {e}", exc_info=True)
            return ValidationResult(
                success=False,
                compliance_score=0.0,
                passes_requirements=False,
                face_detected=False,
                issues=[f"Validation error: {str(e)}"],
                suggestions=["Please try again or contact support"],
                processing_time=time.time() - start_time
            )
    
    def auto_fix_image(self, image_path: str, issues: List[str], format_name: str) -> AutoFixResult:
        """
        Apply auto-fix to an image for specific issues.
        
        Args:
            image_path: Path to the image file
            issues: List of issues to fix
            format_name: Name of the format to validate against
            
        Returns:
            AutoFixResult with fix results
        """
        start_time = time.time()
        
        try:
            if not self.autofix_engine:
                return AutoFixResult(
                    success=False,
                    improvements=[],
                    before_score=0.0,
                    after_score=0.0,
                    fixed_image_path=None,
                    processing_time=time.time() - start_time,
                    error_message="Auto-fix engine not available"
                )
            
            # Get initial validation score
            initial_result = self.validate_only(image_path, format_name)
            before_score = initial_result.compliance_score
            
            # TODO: Implement actual auto-fix in task 5
            # For now, return placeholder result
            self.logger.info(f"Would apply auto-fix for issues: {issues}")
            
            return AutoFixResult(
                success=False,
                improvements=[],
                before_score=before_score,
                after_score=before_score,
                fixed_image_path=None,
                processing_time=time.time() - start_time,
                error_message="Auto-fix not yet implemented"
            )
            
        except Exception as e:
            self.logger.error(f"Error in auto-fix for {image_path}: {e}", exc_info=True)
            return AutoFixResult(
                success=False,
                improvements=[],
                before_score=0.0,
                after_score=0.0,
                fixed_image_path=None,
                processing_time=time.time() - start_time,
                error_message=str(e)
            )
    
    def get_available_formats(self) -> Dict[str, str]:
        """
        Get list of available validation formats.
        
        Returns:
            Dictionary mapping format names to display names
        """
        try:
            return self.config_manager.get_available_formats()
        except Exception as e:
            self.logger.error(f"Error getting available formats: {e}")
            return {}
    
    def get_format_requirements(self, format_name: str) -> Optional[Dict[str, Any]]:
        """
        Get requirements for a specific format.
        
        Args:
            format_name: Name of the format
            
        Returns:
            Format requirements dictionary or None if not found
        """
        try:
            return self.config_manager.get_format_config(format_name)
        except Exception as e:
            self.logger.error(f"Error getting format requirements for {format_name}: {e}")
            return None
    
    def validate_format_config(self, format_name: str) -> bool:
        """
        Validate that a format configuration is complete and usable.
        
        Args:
            format_name: Name of the format to validate
            
        Returns:
            True if format is valid and usable, False otherwise
        """
        try:
            return self.config_manager.validate_format_config(format_name)
        except Exception as e:
            self.logger.error(f"Error validating format config {format_name}: {e}")
            return False
    
    def reload_configuration(self):
        """
        Reload configuration from files and reinitialize components.
        
        This method reloads all configuration files and reinitializes
        components that depend on configuration.
        """
        try:
            self.config_manager.reload_configurations()
            
            # Reset lazy-loaded components to pick up new configuration
            self._icao_validator = None
            
            self.logger.info("Configuration reloaded successfully")
            
        except Exception as e:
            self.logger.error(f"Error reloading configuration: {e}")
            raise RuntimeError(f"Configuration reload failed: {e}")
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """
        Get processing statistics.
        
        Returns:
            Dictionary with processing statistics
        """
        return {
            **self.stats,
            'success_rate': self.stats['successful'] / max(1, self.stats['total_processed']),
            'failure_rate': self.stats['failed'] / max(1, self.stats['total_processed']),
            'uptime_seconds': time.time() - self.stats['last_reset']
        }
    
    def reset_stats(self):
        """Reset processing statistics."""
        self.stats = {
            'total_processed': 0,
            'successful': 0,
            'failed': 0,
            'average_processing_time': 0.0,
            'last_reset': time.time()
        }
        self.logger.info("Processing statistics reset")
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform a health check of all components.
        
        Returns:
            Dictionary with health status of all components
        """
        health_status = {
            'overall_healthy': True,
            'components': {},
            'timestamp': time.time()
        }
        
        # Check configuration manager
        try:
            formats = self.config_manager.get_available_formats()
            health_status['components']['config_manager'] = {
                'healthy': True,
                'formats_loaded': len(formats),
                'message': 'Configuration manager operational'
            }
        except Exception as e:
            health_status['overall_healthy'] = False
            health_status['components']['config_manager'] = {
                'healthy': False,
                'error': str(e),
                'message': 'Configuration manager failed'
            }
        
        # Check face detector
        try:
            detector = self.face_detector  # This will initialize if needed
            health_status['components']['face_detector'] = {
                'healthy': True,
                'message': 'Face detector operational'
            }
        except Exception as e:
            health_status['overall_healthy'] = False
            health_status['components']['face_detector'] = {
                'healthy': False,
                'error': str(e),
                'message': 'Face detector failed to initialize'
            }
        
        # Check ICAO validator
        try:
            validator = self.icao_validator  # This will initialize if needed
            health_status['components']['icao_validator'] = {
                'healthy': True,
                'message': 'ICAO validator operational'
            }
        except Exception as e:
            health_status['overall_healthy'] = False
            health_status['components']['icao_validator'] = {
                'healthy': False,
                'error': str(e),
                'message': 'ICAO validator failed to initialize'
            }
        
        # Check auto-fix engine (optional)
        autofix_available = self.autofix_engine is not None
        health_status['components']['autofix_engine'] = {
            'healthy': True,  # Not having autofix is not a health issue
            'available': autofix_available,
            'message': 'Auto-fix engine available' if autofix_available else 'Auto-fix engine not implemented'
        }
        
        return health_status