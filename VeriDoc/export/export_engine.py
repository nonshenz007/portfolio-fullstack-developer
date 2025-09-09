"""
Main Export Engine for comprehensive export and reporting functionality.
Coordinates all export operations and provides unified interface.
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
from dataclasses import dataclass, asdict

from .report_generator import ReportGenerator
from .audit_logger import AuditLogger
from .metadata_embedder import MetadataEmbedder
from .visual_annotator import VisualAnnotator
from .batch_analyzer import BatchAnalyzer
from ..core.audit_logger import AuditLogger as CoreAuditLogger


@dataclass
class ExportOptions:
    """Configuration options for export operations."""
    include_pdf_report: bool = True
    include_json_report: bool = True
    embed_metadata: bool = True
    create_visual_annotations: bool = True
    include_audit_trail: bool = True
    export_directory: Optional[str] = None
    report_template: Optional[str] = None
    annotation_style: str = "detailed"  # "minimal", "detailed", "comprehensive"


@dataclass
class ExportResult:
    """Result of export operation."""
    success: bool
    export_path: str
    generated_files: List[str]
    pdf_report_path: Optional[str] = None
    json_report_path: Optional[str] = None
    annotated_image_path: Optional[str] = None
    audit_log_path: Optional[str] = None
    error_message: Optional[str] = None
    processing_time: float = 0.0


class ExportEngine:
    """
    Main export engine that coordinates all export and reporting operations.
    Provides unified interface for generating comprehensive compliance reports.
    """
    
    def __init__(self, config_manager=None, audit_logger=None):
        """Initialize export engine with configuration."""
        self.logger = logging.getLogger(__name__)
        self.config_manager = config_manager

        # Initialize sub-components
        self.report_generator = ReportGenerator(config_manager)
        # Use provided audit_logger or create a new one with separate database
        if audit_logger is not None:
            self.audit_logger = audit_logger
        else:
            # Use separate database to avoid schema conflicts with core audit logger
            self.audit_logger = AuditLogger(db_path="logs/export_audit_log.db")
        self.metadata_embedder = MetadataEmbedder()
        self.visual_annotator = VisualAnnotator()
        self.batch_analyzer = BatchAnalyzer()
        
        # Default export directory
        self.default_export_dir = "export"
        os.makedirs(self.default_export_dir, exist_ok=True)
    
    def export_single_result(self, 
                           processing_result: Dict[str, Any],
                           image_path: str,
                           options: ExportOptions = None) -> ExportResult:
        """
        Export results for a single image processing operation.
        
        Args:
            processing_result: Complete processing result with validation data
            image_path: Path to the original image
            options: Export configuration options
            
        Returns:
            ExportResult with paths to generated files
        """
        start_time = datetime.now()
        
        if options is None:
            options = ExportOptions()
            
        try:
            # Create export directory
            export_dir = self._create_export_directory(image_path, options)
            
            # Log export operation start
            if options.include_audit_trail:
                self.audit_logger.log_export_start(image_path, export_dir)
            
            generated_files = []
            
            # Generate PDF report
            pdf_path = None
            if options.include_pdf_report:
                pdf_path = self._generate_pdf_report(
                    processing_result, image_path, export_dir, options
                )
                if pdf_path:
                    generated_files.append(pdf_path)
            
            # Generate JSON report
            json_path = None
            if options.include_json_report:
                json_path = self._generate_json_report(
                    processing_result, image_path, export_dir
                )
                if json_path:
                    generated_files.append(json_path)
            
            # Create visual annotations
            annotated_path = None
            if options.create_visual_annotations:
                annotated_path = self._create_visual_annotations(
                    processing_result, image_path, export_dir, options
                )
                if annotated_path:
                    generated_files.append(annotated_path)
            
            # Embed metadata in image
            if options.embed_metadata and annotated_path:
                self._embed_compliance_metadata(
                    processing_result, annotated_path
                )
            
            # Log successful export
            if options.include_audit_trail:
                audit_path = self.audit_logger.log_export_complete(
                    image_path, export_dir, generated_files
                )
                generated_files.append(audit_path)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return ExportResult(
                success=True,
                export_path=export_dir,
                generated_files=generated_files,
                pdf_report_path=pdf_path,
                json_report_path=json_path,
                annotated_image_path=annotated_path,
                audit_log_path=audit_path if options.include_audit_trail else None,
                processing_time=processing_time
            )
            
        except Exception as e:
            self.logger.error(f"Export failed for {image_path}: {str(e)}")
            
            if options.include_audit_trail:
                self.audit_logger.log_export_error(image_path, str(e))
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return ExportResult(
                success=False,
                export_path="",
                generated_files=[],
                error_message=str(e),
                processing_time=processing_time
            )
    
    def export_batch_results(self,
                           batch_results: List[Dict[str, Any]],
                           options: ExportOptions = None) -> ExportResult:
        """
        Export results for batch processing operation with summary statistics.
        
        Args:
            batch_results: List of processing results from batch operation
            options: Export configuration options
            
        Returns:
            ExportResult with batch summary and individual reports
        """
        start_time = datetime.now()
        
        if options is None:
            options = ExportOptions()
            
        try:
            # Create batch export directory
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            batch_dir = os.path.join(
                options.export_directory or self.default_export_dir,
                f"batch_export_{timestamp}"
            )
            os.makedirs(batch_dir, exist_ok=True)
            
            # Log batch export start
            if options.include_audit_trail:
                self.audit_logger.log_batch_export_start(batch_dir, len(batch_results))
            
            generated_files = []
            
            # Generate batch analysis report
            batch_analysis = self.batch_analyzer.analyze_batch_results(batch_results)
            
            # Generate batch summary PDF
            if options.include_pdf_report:
                batch_pdf = self._generate_batch_pdf_report(
                    batch_analysis, batch_dir, options
                )
                if batch_pdf:
                    generated_files.append(batch_pdf)
            
            # Generate batch summary JSON
            if options.include_json_report:
                batch_json = self._generate_batch_json_report(
                    batch_analysis, batch_dir
                )
                if batch_json:
                    generated_files.append(batch_json)
            
            # Export individual results
            individual_results = []
            for result in batch_results:
                if 'image_path' in result:
                    individual_options = ExportOptions(
                        include_pdf_report=False,  # Skip individual PDFs for batch
                        include_json_report=True,
                        embed_metadata=options.embed_metadata,
                        create_visual_annotations=options.create_visual_annotations,
                        include_audit_trail=False,  # Handled at batch level
                        export_directory=batch_dir
                    )
                    
                    individual_result = self.export_single_result(
                        result, result['image_path'], individual_options
                    )
                    individual_results.append(individual_result)
                    generated_files.extend(individual_result.generated_files)
            
            # Log batch export completion
            if options.include_audit_trail:
                audit_path = self.audit_logger.log_batch_export_complete(
                    batch_dir, generated_files, batch_analysis
                )
                generated_files.append(audit_path)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return ExportResult(
                success=True,
                export_path=batch_dir,
                generated_files=generated_files,
                pdf_report_path=batch_pdf if options.include_pdf_report else None,
                json_report_path=batch_json if options.include_json_report else None,
                processing_time=processing_time
            )
            
        except Exception as e:
            self.logger.error(f"Batch export failed: {str(e)}")
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return ExportResult(
                success=False,
                export_path="",
                generated_files=[],
                error_message=str(e),
                processing_time=processing_time
            )
    
    def _create_export_directory(self, image_path: str, options: ExportOptions) -> str:
        """Create export directory for image results."""
        base_name = Path(image_path).stem
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        export_dir = os.path.join(
            options.export_directory or self.default_export_dir,
            f"{base_name}_{timestamp}"
        )
        
        os.makedirs(export_dir, exist_ok=True)
        return export_dir
    
    def _generate_pdf_report(self, processing_result: Dict[str, Any], 
                           image_path: str, export_dir: str, 
                           options: ExportOptions) -> Optional[str]:
        """Generate PDF compliance report."""
        try:
            return self.report_generator.generate_pdf_report(
                processing_result, image_path, export_dir, options.report_template
            )
        except Exception as e:
            self.logger.error(f"PDF report generation failed: {str(e)}")
            return None
    
    def _generate_json_report(self, processing_result: Dict[str, Any],
                            image_path: str, export_dir: str) -> Optional[str]:
        """Generate JSON compliance report."""
        try:
            return self.report_generator.generate_json_report(
                processing_result, image_path, export_dir
            )
        except Exception as e:
            self.logger.error(f"JSON report generation failed: {str(e)}")
            return None
    
    def _create_visual_annotations(self, processing_result: Dict[str, Any],
                                 image_path: str, export_dir: str,
                                 options: ExportOptions) -> Optional[str]:
        """Create visually annotated image showing compliance measurements."""
        try:
            return self.visual_annotator.create_annotated_image(
                processing_result, image_path, export_dir, options.annotation_style
            )
        except Exception as e:
            self.logger.error(f"Visual annotation failed: {str(e)}")
            return None
    
    def _embed_compliance_metadata(self, processing_result: Dict[str, Any],
                                 image_path: str) -> bool:
        """Embed compliance metadata in image EXIF data."""
        try:
            return self.metadata_embedder.embed_compliance_metadata(
                processing_result, image_path
            )
        except Exception as e:
            self.logger.error(f"Metadata embedding failed: {str(e)}")
            return False
    
    def _generate_batch_pdf_report(self, batch_analysis: Dict[str, Any],
                                 export_dir: str, options: ExportOptions) -> Optional[str]:
        """Generate batch summary PDF report."""
        try:
            return self.report_generator.generate_batch_pdf_report(
                batch_analysis, export_dir, options.report_template
            )
        except Exception as e:
            self.logger.error(f"Batch PDF report generation failed: {str(e)}")
            return None
    
    def _generate_batch_json_report(self, batch_analysis: Dict[str, Any],
                                  export_dir: str) -> Optional[str]:
        """Generate batch summary JSON report."""
        try:
            return self.report_generator.generate_batch_json_report(
                batch_analysis, export_dir
            )
        except Exception as e:
            self.logger.error(f"Batch JSON report generation failed: {str(e)}")
            return None
    
    def get_export_statistics(self) -> Dict[str, Any]:
        """Get export operation statistics."""
        return self.audit_logger.get_export_statistics()
    
    def cleanup_old_exports(self, days_old: int = 30) -> int:
        """Clean up export files older than specified days."""
        try:
            cleaned_count = 0
            cutoff_date = datetime.now().timestamp() - (days_old * 24 * 3600)
            
            for root, dirs, files in os.walk(self.default_export_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    if os.path.getmtime(file_path) < cutoff_date:
                        os.remove(file_path)
                        cleaned_count += 1
            
            self.logger.info(f"Cleaned up {cleaned_count} old export files")
            return cleaned_count
            
        except Exception as e:
            self.logger.error(f"Export cleanup failed: {str(e)}")
            return 0