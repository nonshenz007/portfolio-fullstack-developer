"""
Main Processing Pipeline

Orchestrates the complete image processing workflow:
- Face detection with YOLOv8 + MediaPipe
- Background segmentation with SAM/U2Net
- Quality analysis and validation
- AI-powered enhancement with ESRGAN/NAFNet
- Compliance validation against ICAO standards
- Idempotent auto-fix loops with re-validation
"""

import time
import logging
from typing import Dict, List, Optional
from datetime import datetime
import numpy as np
import cv2
from pathlib import Path

from ..contracts import (
    IProcessingPipeline, ProcessingJob, ProcessingReport, ProcessingResult,
    ProcessingMetrics, FaceDetectionResult, SegmentationResult, 
    EnhancementResult, ComplianceResult, ValidationIssue
)


class MainProcessingPipeline(IProcessingPipeline):
    """
    Main processing pipeline that orchestrates:
    - AI-powered face detection and analysis
    - Background processing and validation
    - Quality enhancement and optimization
    - Compliance validation and certification
    - Auto-fix loops with re-validation
    """
    
    def __init__(self, security_manager=None, performance_monitor=None):
        self.logger = logging.getLogger(__name__)
        self.security_manager = security_manager
        self.performance_monitor = performance_monitor
        
        # Initialize AI components
        self._initialize_ai_components()
        
        # Processing configuration
        self.max_autofix_iterations = 3
        self.quality_threshold = 0.95
        self.compliance_threshold = 0.95
        
        # Processing statistics
        self.processing_stats = {
            'total_processed': 0,
            'successful_fixes': 0,
            'failed_fixes': 0,
            'average_iterations': 0.0
        }
        
        self.logger.info("Main processing pipeline initialized")
    
    def _initialize_ai_components(self):
        """Initialize AI model components"""
        try:
            # Face detection (YOLOv8 + MediaPipe)
            from .ai_models.face_detector import AdvancedFaceDetector
            self.face_detector = AdvancedFaceDetector()
            
            # Background processing (SAM + U2Net)
            from .ai_models.background_processor import AdvancedBackgroundProcessor
            self.background_processor = AdvancedBackgroundProcessor()
            
            # Enhancement engine (ESRGAN + NAFNet)
            from .ai_models.enhancement_engine import AdvancedEnhancementEngine
            self.enhancement_engine = AdvancedEnhancementEngine()
            
            # Quality analyzer
            from .ai_models.quality_analyzer import AdvancedQualityAnalyzer
            self.quality_analyzer = AdvancedQualityAnalyzer()
            
            # Compliance validator
            from .validation.compliance_validator import ICOAComplianceValidator
            self.compliance_validator = ICOAComplianceValidator()
            
            self.logger.info("AI components initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize AI components: {e}")
            raise
    
    def process_image(self, job: ProcessingJob) -> ProcessingReport:
        """Process single image through complete pipeline"""
        start_time = time.time()
        processing_metrics = ProcessingMetrics(
            processing_time_ms=0.0,
            memory_usage_mb=0.0,
            cpu_usage_percent=0.0,
            operations_performed=[],
            ai_model_inference_times={}
        )
        
        try:
            self.logger.info(f"Processing image: {job.input_path}")
            
            # Load and validate input image
            image = self._load_and_validate_image(job.input_path)
            if image is None:
                return self._create_error_report(job, "Failed to load input image", processing_metrics)
            
            processing_metrics.operations_performed.append("image_load")
            
            # Initialize results
            face_detection_result = None
            segmentation_result = None
            enhancement_results = []
            quality_analysis = None
            compliance_results = []
            issues = []
            
            # Start idempotent processing loop
            current_image = image.copy()
            iteration = 0
            max_iterations = self.max_autofix_iterations
            
            while iteration < max_iterations:
                iteration += 1
                self.logger.debug(f"Processing iteration {iteration} for {job.job_id}")
                
                # Step 1: Face Detection
                face_start = time.time()
                face_detection_result = self.face_detector.detect_face(current_image, job.context)
                processing_metrics.ai_model_inference_times['face_detection'] = (time.time() - face_start) * 1000
                processing_metrics.operations_performed.append(f"face_detection_iter{iteration}")
                
                if not face_detection_result.face_found:
                    issues.append(ValidationIssue(
                        severity="CRITICAL",
                        category="FACE_DETECTION",
                        code="NO_FACE_FOUND",
                        message="No face detected in image",
                        details={"confidence": face_detection_result.confidence}
                    ))
                    break
                
                # Step 2: Background Segmentation
                seg_start = time.time()
                segmentation_result = self.background_processor.segment_background(current_image, job.context)
                processing_metrics.ai_model_inference_times['segmentation'] = (time.time() - seg_start) * 1000
                processing_metrics.operations_performed.append(f"segmentation_iter{iteration}")
                
                # Step 3: Quality Analysis
                quality_start = time.time()
                quality_analysis = self.quality_analyzer.comprehensive_quality_check(current_image)
                processing_metrics.ai_model_inference_times['quality_analysis'] = (time.time() - quality_start) * 1000
                processing_metrics.operations_performed.append(f"quality_analysis_iter{iteration}")
                
                # Step 4: Compliance Validation
                comp_start = time.time()
                compliance_result = self.compliance_validator.validate_icao_compliance(
                    current_image, face_detection_result, job.context
                )
                processing_metrics.ai_model_inference_times['compliance_validation'] = (time.time() - comp_start) * 1000
                processing_metrics.operations_performed.append(f"compliance_validation_iter{iteration}")
                
                compliance_results.append(compliance_result)
                
                # Check if image meets quality and compliance thresholds
                meets_quality = quality_analysis.score >= self.quality_threshold
                meets_compliance = compliance_result.score >= self.compliance_threshold
                
                if meets_quality and meets_compliance:
                    self.logger.info(f"Image passed validation on iteration {iteration}")
                    break
                
                # Collect issues for auto-fix
                all_issues = quality_analysis.issues + compliance_result.issues
                
                # Step 5: Auto-fix Enhancement
                if iteration < max_iterations:
                    enhancement_start = time.time()
                    enhancement_result = self.enhancement_engine.auto_fix_issues(
                        current_image, all_issues, job.context
                    )
                    processing_metrics.ai_model_inference_times['enhancement'] = (time.time() - enhancement_start) * 1000
                    processing_metrics.operations_performed.append(f"enhancement_iter{iteration}")
                    
                    enhancement_results.append(enhancement_result)
                    
                    if enhancement_result.enhanced_image is not None:
                        current_image = enhancement_result.enhanced_image
                        self.logger.debug(f"Applied enhancements: {enhancement_result.operations_applied}")
                    else:
                        self.logger.warning(f"Enhancement failed on iteration {iteration}")
                        break
                else:
                    self.logger.warning(f"Reached maximum iterations ({max_iterations}) without full compliance")
            
            # Save processed image
            success = self._save_processed_image(current_image, job.output_path)
            if not success:
                issues.append(ValidationIssue(
                    severity="ERROR",
                    category="OUTPUT",
                    code="SAVE_FAILED",
                    message="Failed to save processed image",
                    details={"output_path": str(job.output_path)}
                ))
            
            # Update processing metrics
            processing_time_ms = (time.time() - start_time) * 1000
            processing_metrics.processing_time_ms = processing_time_ms
            processing_metrics.memory_usage_mb = self._get_memory_usage()
            processing_metrics.cpu_usage_percent = self._get_cpu_usage()
            
            # Generate security signature
            security_signature = ""
            if self.security_manager and success:
                try:
                    image_data = cv2.imencode('.jpg', current_image)[1].tobytes()
                    security_signature = self.security_manager.generate_security_signature(
                        image_data, job.context
                    )
                except Exception as e:
                    self.logger.error(f"Failed to generate security signature: {e}")
            
            # Create processing report
            report = ProcessingReport(
                job_id=job.job_id,
                success=success and len([i for i in issues if i.severity == "CRITICAL"]) == 0,
                processing_time_ms=processing_time_ms,
                face_detection=face_detection_result,
                segmentation=segmentation_result,
                enhancements=enhancement_results,
                quality_analysis=quality_analysis,
                compliance_results=compliance_results,
                issues=issues,
                metrics=processing_metrics,
                security_signature=security_signature,
                context=job.context
            )
            
            # Update statistics
            self._update_processing_statistics(report, iteration)
            
            # Log processing completion
            if self.security_manager:
                self.security_manager.audit_logger.log_processing_event(
                    operation="image_processing",
                    resource=str(job.input_path),
                    result=ProcessingResult.SUCCESS if report.success else ProcessingResult.FAILURE,
                    metrics=processing_metrics,
                    context=job.context
                )
            
            self.logger.info(f"Processing completed: {job.job_id} (success: {report.success}, iterations: {iteration})")
            return report
            
        except Exception as e:
            self.logger.error(f"Processing failed for {job.job_id}: {e}")
            
            # Create error metrics
            processing_metrics.processing_time_ms = (time.time() - start_time) * 1000
            processing_metrics.operations_performed.append("error")
            
            return self._create_error_report(job, str(e), processing_metrics)
    
    def process_batch(self, jobs: List[ProcessingJob]) -> List[ProcessingReport]:
        """Process batch of images with optimization"""
        self.logger.info(f"Processing batch of {len(jobs)} images")
        
        reports = []
        for job in jobs:
            try:
                report = self.process_image(job)
                reports.append(report)
            except Exception as e:
                self.logger.error(f"Batch processing failed for job {job.job_id}: {e}")
                error_report = self._create_error_report(
                    job, f"Batch processing error: {e}",
                    ProcessingMetrics(0.0, 0.0, 0.0, ["batch_error"], {})
                )
                reports.append(error_report)
        
        return reports
    
    def get_processing_status(self, job_id: str) -> Dict[str, any]:
        """Get processing status for job (placeholder)"""
        # This would integrate with the processing controller
        return {
            'job_id': job_id,
            'status': 'NOT_IMPLEMENTED',
            'message': 'Status tracking not implemented in pipeline'
        }
    
    def cancel_job(self, job_id: str, context) -> bool:
        """Cancel processing job (placeholder)"""
        # This would integrate with the processing controller
        self.logger.warning(f"Job cancellation not implemented in pipeline: {job_id}")
        return False
    
    def _load_and_validate_image(self, image_path: Path) -> Optional[np.ndarray]:
        """Load and validate input image"""
        try:
            if not image_path.exists():
                self.logger.error(f"Image file does not exist: {image_path}")
                return None
            
            # Load image
            image = cv2.imread(str(image_path))
            if image is None:
                self.logger.error(f"Failed to load image: {image_path}")
                return None
            
            # Basic validation
            height, width = image.shape[:2]
            if height < 100 or width < 100:
                self.logger.error(f"Image too small: {width}x{height}")
                return None
            
            if height > 4000 or width > 4000:
                self.logger.warning(f"Large image detected: {width}x{height} - may affect performance")
            
            return image
            
        except Exception as e:
            self.logger.error(f"Image validation failed: {e}")
            return None
    
    def _save_processed_image(self, image: np.ndarray, output_path: Path) -> bool:
        """Save processed image to output path"""
        try:
            # Ensure output directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save image with high quality
            success = cv2.imwrite(str(output_path), image, [
                cv2.IMWRITE_JPEG_QUALITY, 95,
                cv2.IMWRITE_PNG_COMPRESSION, 1
            ])
            
            if success:
                self.logger.debug(f"Image saved: {output_path}")
            else:
                self.logger.error(f"Failed to save image: {output_path}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Image save failed: {e}")
            return False
    
    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        try:
            import psutil
            process = psutil.Process()
            return process.memory_info().rss / (1024 * 1024)  # MB
        except Exception:
            return 0.0
    
    def _get_cpu_usage(self) -> float:
        """Get current CPU usage percentage"""
        try:
            import psutil
            return psutil.cpu_percent(interval=0.1)
        except Exception:
            return 0.0
    
    def _create_error_report(self, job: ProcessingJob, error_message: str, 
                           metrics: ProcessingMetrics) -> ProcessingReport:
        """Create error processing report"""
        error_issue = ValidationIssue(
            severity="CRITICAL",
            category="PROCESSING",
            code="PROCESSING_ERROR",
            message=error_message,
            details={"job_id": job.job_id}
        )
        
        return ProcessingReport(
            job_id=job.job_id,
            success=False,
            processing_time_ms=metrics.processing_time_ms,
            face_detection=None,
            segmentation=None,
            enhancements=[],
            quality_analysis=None,
            compliance_results=[],
            issues=[error_issue],
            metrics=metrics,
            security_signature="",
            context=job.context
        )
    
    def _update_processing_statistics(self, report: ProcessingReport, iterations: int):
        """Update processing statistics"""
        try:
            self.processing_stats['total_processed'] += 1
            
            if report.success:
                self.processing_stats['successful_fixes'] += 1
            else:
                self.processing_stats['failed_fixes'] += 1
            
            # Update average iterations
            total = self.processing_stats['total_processed']
            current_avg = self.processing_stats['average_iterations']
            self.processing_stats['average_iterations'] = ((current_avg * (total - 1)) + iterations) / total
            
        except Exception as e:
            self.logger.error(f"Failed to update processing statistics: {e}")
    
    def get_pipeline_statistics(self) -> Dict[str, any]:
        """Get pipeline processing statistics"""
        return {
            'timestamp': datetime.now().isoformat(),
            'processing_stats': self.processing_stats.copy(),
            'ai_components_status': {
                'face_detector': 'OPERATIONAL',
                'background_processor': 'OPERATIONAL', 
                'enhancement_engine': 'OPERATIONAL',
                'quality_analyzer': 'OPERATIONAL',
                'compliance_validator': 'OPERATIONAL'
            },
            'configuration': {
                'max_autofix_iterations': self.max_autofix_iterations,
                'quality_threshold': self.quality_threshold,
                'compliance_threshold': self.compliance_threshold
            }
        }
