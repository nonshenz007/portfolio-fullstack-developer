"""
VeriDoc Core Processing Engine

Main engine that coordinates validation, processing, and compliance checking
for document photos according to various international standards.
"""

import os
import time
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
from dataclasses import dataclass

from .image_processor import ImageProcessor, ProcessingOptions, ProcessingResult
from validation.format_validator import FormatValidator, ValidationReport
from validation.validation_models import ValidationIssue, ValidationSeverity


@dataclass
class EngineConfig:
    """Configuration for the VeriDoc engine."""
    
    # Directories
    config_dir: str = "config"
    models_dir: str = "models"
    output_dir: str = "output"
    
    # Processing defaults
    default_format: str = "ICS-UAE_FAIC_STRICT_v1"
    auto_select_best_format: bool = False
    
    # Quality settings
    output_quality: int = 95
    output_dpi: int = 300
    
    # Performance settings
    enable_caching: bool = True
    max_concurrent_processes: int = 4
    
    # Validation settings
    strict_validation: bool = True
    auto_fix_issues: bool = True


class VeriDocEngine:
    """Main VeriDoc processing engine."""
    
    def __init__(self, config: Optional[EngineConfig] = None):
        """Initialize the VeriDoc engine.
        
        Args:
            config: Engine configuration, uses defaults if not provided
        """
        self.config = config or EngineConfig()
        
        # Initialize core components
        self.validator = FormatValidator(self.config.config_dir)
        self.processor = ImageProcessor(self.config.config_dir)
        
        # Cache for format configurations
        self._format_cache: Dict[str, Dict] = {}
        
        # Statistics tracking
        self.stats = {
            'images_processed': 0,
            'images_passed': 0,
            'images_failed': 0,
            'total_processing_time': 0.0,
            'average_processing_time': 0.0
        }
        
    def process_single_image(self, 
                           input_path: str,
                           output_path: Optional[str] = None,
                           format_id: Optional[str] = None,
                           processing_options: Optional[ProcessingOptions] = None) -> ProcessingResult:
        """Process a single image through the complete VeriDoc pipeline.
        
        Args:
            input_path: Path to input image
            output_path: Path for output image (auto-generated if not provided)
            format_id: Format to validate against (uses default if not provided)
            processing_options: Custom processing options
            
        Returns:
            ProcessingResult with complete processing information
        """
        start_time = time.time()
        
        try:
            # Use default format if not specified
            if format_id is None:
                format_id = self.config.default_format
            
            # Auto-generate output path if not provided
            if output_path is None:
                output_path = self._generate_output_path(input_path, format_id)
            
            # Use default processing options if not provided
            if processing_options is None:
                processing_options = self._get_default_processing_options(format_id)
            
            # Process the image
            result = self.processor.process_image(
                input_path=input_path,
                output_path=output_path,
                format_id=format_id,
                options=processing_options
            )
            
            # Update statistics
            self._update_stats(result, time.time() - start_time)
            
            return result
            
        except Exception as e:
            # Create error result
            result = ProcessingResult(
                success=False,
                input_path=input_path,
                output_path=output_path,
                processing_time=time.time() - start_time,
                operations_performed=[],
                validation_report_before=None,
                validation_report_after=None,
                issues=[],
                error_message=f"Engine error: {str(e)}"
            )
            
            self._update_stats(result, time.time() - start_time)
            return result
    
    def validate_image(self, image_path: str, format_id: Optional[str] = None) -> ValidationReport:
        """Validate an image against format requirements.
        
        Args:
            image_path: Path to image file
            format_id: Format to validate against
            
        Returns:
            ValidationReport with validation results
        """
        if format_id is None:
            format_id = self.config.default_format
            
        return self.validator.validate_image(image_path, format_id)
    
    def get_available_formats(self) -> List[str]:
        """Get list of available format configurations."""
        return self.validator.get_available_formats()
    
    def get_format_info(self, format_id: str) -> Optional[Dict]:
        """Get detailed information about a format.
        
        Args:
            format_id: Format identifier
            
        Returns:
            Format configuration dictionary or None if not found
        """
        return self.validator.formats.get(format_id)
    
    def recommend_format(self, image_path: str) -> Tuple[str, float]:
        """Recommend the best format for an image based on validation scores.
        
        Args:
            image_path: Path to image file
            
        Returns:
            Tuple of (format_id, confidence_score)
        """
        best_format = self.config.default_format
        best_score = 0.0
        
        # Test all available formats
        for format_id in self.get_available_formats():
            try:
                validation_result = self.validate_image(image_path, format_id)
                if validation_result.score > best_score:
                    best_score = validation_result.score
                    best_format = format_id
            except Exception:
                continue
        
        return best_format, best_score
    
    def get_processing_suggestions(self, validation_report: ValidationReport) -> List[str]:
        """Get processing suggestions based on validation results.
        
        Args:
            validation_report: Validation report to analyze
            
        Returns:
            List of processing suggestions
        """
        suggestions = []
        
        for issue in validation_report.issues:
            if issue.auto_fixable:
                suggestions.append(issue.suggestion)
        
        # Add general suggestions based on overall score
        if validation_report.score < 50:
            suggestions.append("Consider retaking the photo with better lighting and positioning")
        elif validation_report.score < 80:
            suggestions.append("Minor adjustments may improve compliance")
        
        return list(set(suggestions))  # Remove duplicates
    
    def batch_process_directory(self, 
                              input_directory: str,
                              output_directory: Optional[str] = None,
                              format_id: Optional[str] = None,
                              processing_options: Optional[ProcessingOptions] = None) -> List[ProcessingResult]:
        """Process all images in a directory.
        
        Args:
            input_directory: Directory containing input images
            output_directory: Directory for output images
            format_id: Format to use for all images
            processing_options: Processing options
            
        Returns:
            List of ProcessingResult objects
        """
        results = []
        
        # Find all image files
        image_files = self._find_image_files(input_directory)
        
        # Set up output directory
        if output_directory is None:
            output_directory = os.path.join(input_directory, "veridoc_output")
        
        os.makedirs(output_directory, exist_ok=True)
        
        # Process each image
        for image_file in image_files:
            input_path = os.path.join(input_directory, image_file)
            output_filename = self._generate_output_filename(image_file, format_id or self.config.default_format)
            output_path = os.path.join(output_directory, output_filename)
            
            result = self.process_single_image(
                input_path=input_path,
                output_path=output_path,
                format_id=format_id,
                processing_options=processing_options
            )
            
            results.append(result)
        
        return results
    
    def get_engine_stats(self) -> Dict[str, Any]:
        """Get engine processing statistics."""
        return self.stats.copy()
    
    def reset_stats(self):
        """Reset engine statistics."""
        self.stats = {
            'images_processed': 0,
            'images_passed': 0,
            'images_failed': 0,
            'total_processing_time': 0.0,
            'average_processing_time': 0.0
        }
    
    def _generate_output_path(self, input_path: str, format_id: str) -> str:
        """Generate output path for processed image."""
        input_file = Path(input_path)
        
        # Create output directory
        output_dir = Path(self.config.output_dir) / format_id
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate output filename
        output_filename = f"{input_file.stem}_processed{input_file.suffix}"
        return str(output_dir / output_filename)
    
    def _generate_output_filename(self, input_filename: str, format_id: str) -> str:
        """Generate output filename for processed image."""
        input_file = Path(input_filename)
        return f"{input_file.stem}_{format_id}_processed{input_file.suffix}"
    
    def _get_default_processing_options(self, format_id: str) -> ProcessingOptions:
        """Get default processing options for a format."""
        # Get format configuration
        format_config = self.get_format_info(format_id)
        
        options = ProcessingOptions()
        options.output_quality = self.config.output_quality
        options.output_dpi = self.config.output_dpi
        
        if format_config:
            # Apply format-specific defaults
            dimensions = format_config.get('dimensions', {})
            
            # Set DPI from format config
            if 'dpi_min' in dimensions:
                options.output_dpi = max(options.output_dpi, dimensions['dpi_min'])
            
            # Enable auto-enhancements based on format requirements
            if format_config.get('quality', {}).get('auto_enhance', True):
                options.auto_enhance = True
            
            # Enable background normalization if required
            background = format_config.get('background', {})
            if background.get('required') == 'plain_light_coloured':
                options.normalize_background = True
        
        return options
    
    def _find_image_files(self, directory: str) -> List[str]:
        """Find all image files in a directory."""
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif'}
        image_files = []
        
        for filename in os.listdir(directory):
            if any(filename.lower().endswith(ext) for ext in image_extensions):
                image_files.append(filename)
        
        return sorted(image_files)
    
    def _update_stats(self, result: ProcessingResult, processing_time: float):
        """Update engine statistics."""
        self.stats['images_processed'] += 1
        self.stats['total_processing_time'] += processing_time
        
        if result.success:
            # Check if image passes validation
            if (result.validation_report_after and 
                result.validation_report_after.passes):
                self.stats['images_passed'] += 1
            else:
                self.stats['images_failed'] += 1
        else:
            self.stats['images_failed'] += 1
        
        # Update average processing time
        if self.stats['images_processed'] > 0:
            self.stats['average_processing_time'] = (
                self.stats['total_processing_time'] / self.stats['images_processed']
            )

