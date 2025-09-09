"""
Image Processing Engine for VeriDoc

Handles core image processing operations including resizing, cropping,
enhancement, and format compliance processing.
"""

import os
import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
from typing import Optional, Tuple, Dict, Any, List
from dataclasses import dataclass
from pathlib import Path

from validation.format_validator import FormatValidator, ValidationReport
from validation.validation_models import ValidationIssue, ValidationSeverity


@dataclass
class ProcessingOptions:
    """Configuration options for image processing."""
    
    # Output format options
    output_format: str = "JPEG"
    output_quality: int = 95
    output_dpi: int = 300
    
    # Resize options
    target_width: Optional[int] = None
    target_height: Optional[int] = None
    maintain_aspect_ratio: bool = True
    upscale_allowed: bool = False
    
    # Enhancement options
    auto_enhance: bool = True
    brightness_adjustment: float = 0.0  # -1.0 to 1.0
    contrast_adjustment: float = 0.0    # -1.0 to 1.0
    sharpness_adjustment: float = 0.0   # -1.0 to 1.0
    
    # Crop options
    auto_crop_to_face: bool = False
    crop_padding: float = 0.1  # Percentage padding around face
    
    # Background options
    normalize_background: bool = False
    target_background_color: Tuple[int, int, int] = (240, 240, 240)
    
    # Validation options
    validate_before_processing: bool = True
    validate_after_processing: bool = True
    stop_on_validation_failure: bool = False


@dataclass
class ProcessingResult:
    """Result of image processing operation."""
    
    success: bool
    input_path: str
    output_path: Optional[str]
    processing_time: float
    operations_performed: List[str]
    validation_report_before: Optional[ValidationReport]
    validation_report_after: Optional[ValidationReport]
    issues: List[ValidationIssue]
    error_message: Optional[str] = None
    
    @property
    def improvement_score(self) -> float:
        """Calculate improvement score from before/after validation."""
        if not self.validation_report_before or not self.validation_report_after:
            return 0.0
        
        before_score = self.validation_report_before.score
        after_score = self.validation_report_after.score
        
        return max(0.0, after_score - before_score)


class ImageProcessor:
    """Main image processing engine for VeriDoc."""
    
    def __init__(self, config_dir: str = "config"):
        """Initialize the image processor.
        
        Args:
            config_dir: Directory containing format configurations
        """
        self.config_dir = Path(config_dir)
        self.validator = FormatValidator(config_dir)
        self.supported_formats = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
        
    def process_image(self, 
                     input_path: str, 
                     output_path: str,
                     format_id: str,
                     options: Optional[ProcessingOptions] = None) -> ProcessingResult:
        """Process a single image according to format requirements.
        
        Args:
            input_path: Path to input image
            output_path: Path for output image
            format_id: Format configuration to use
            options: Processing options
            
        Returns:
            ProcessingResult with processing details
        """
        start_time = cv2.getTickCount()
        
        if options is None:
            options = ProcessingOptions()
        
        operations_performed = []
        issues = []
        validation_before = None
        validation_after = None
        
        try:
            # Validate input file exists
            if not os.path.exists(input_path):
                return ProcessingResult(
                    success=False,
                    input_path=input_path,
                    output_path=None,
                    processing_time=0.0,
                    operations_performed=[],
                    validation_report_before=None,
                    validation_report_after=None,
                    issues=[],
                    error_message=f"Input file not found: {input_path}"
                )
            
            # Load image
            image = self._load_image(input_path)
            if image is None:
                return ProcessingResult(
                    success=False,
                    input_path=input_path,
                    output_path=None,
                    processing_time=0.0,
                    operations_performed=[],
                    validation_report_before=None,
                    validation_report_after=None,
                    issues=[],
                    error_message="Failed to load image"
                )
            
            # Initial validation
            if options.validate_before_processing:
                try:
                    validation_before = self.validator.validate_image(input_path, format_id)
                    if options.stop_on_validation_failure and not validation_before.passes:
                        return ProcessingResult(
                            success=False,
                            input_path=input_path,
                            output_path=None,
                            processing_time=self._calculate_processing_time(start_time),
                            operations_performed=operations_performed,
                            validation_report_before=validation_before,
                            validation_report_after=None,
                            issues=validation_before.issues,
                            error_message="Validation failed before processing"
                        )
                except Exception as e:
                    issues.append(ValidationIssue(
                        category="validation",
                        severity=ValidationSeverity.MINOR,
                        message=f"Pre-processing validation failed: {str(e)}",
                        suggestion="Check image file integrity",
                        auto_fixable=False
                    ))
            
            # Process image
            processed_image = self._process_image_pipeline(image, format_id, options, operations_performed)
            
            # Create output directory if needed
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Save processed image
            self._save_image(processed_image, output_path, options)
            operations_performed.append(f"save_{options.output_format.lower()}")
            
            # Post-processing validation
            if options.validate_after_processing:
                try:
                    validation_after = self.validator.validate_image(output_path, format_id)
                except Exception as e:
                    issues.append(ValidationIssue(
                        category="validation",
                        severity=ValidationSeverity.MINOR,
                        message=f"Post-processing validation failed: {str(e)}",
                        suggestion="Check output file integrity",
                        auto_fixable=False
                    ))
            
            processing_time = self._calculate_processing_time(start_time)
            
            return ProcessingResult(
                success=True,
                input_path=input_path,
                output_path=output_path,
                processing_time=processing_time,
                operations_performed=operations_performed,
                validation_report_before=validation_before,
                validation_report_after=validation_after,
                issues=issues
            )
            
        except Exception as e:
            return ProcessingResult(
                success=False,
                input_path=input_path,
                output_path=output_path,
                processing_time=self._calculate_processing_time(start_time),
                operations_performed=operations_performed,
                validation_report_before=validation_before,
                validation_report_after=validation_after,
                issues=issues,
                error_message=str(e)
            )
    
    def _load_image(self, image_path: str) -> Optional[np.ndarray]:
        """Load image from file path."""
        try:
            # Try with OpenCV first
            image = cv2.imread(image_path)
            if image is not None:
                return image
            
            # Fallback to PIL
            with Image.open(image_path) as pil_image:
                # Convert to RGB if needed
                if pil_image.mode != 'RGB':
                    pil_image = pil_image.convert('RGB')
                
                # Convert PIL to OpenCV format
                opencv_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
                return opencv_image
                
        except Exception as e:
            print(f"Error loading image {image_path}: {e}")
            return None
    
    def _process_image_pipeline(self, 
                               image: np.ndarray, 
                               format_id: str, 
                               options: ProcessingOptions,
                               operations_performed: List[str]) -> np.ndarray:
        """Execute the image processing pipeline."""
        
        processed_image = image.copy()
        
        # Get format configuration
        format_config = self.validator.formats.get(format_id, {})
        
        # 1. Resize if needed
        if options.target_width or options.target_height:
            processed_image = self._resize_image(processed_image, options)
            operations_performed.append("resize")
        
        # 2. Auto-crop to face if enabled
        if options.auto_crop_to_face:
            processed_image = self._auto_crop_to_face(processed_image, options)
            operations_performed.append("auto_crop")
        
        # 3. Normalize background if enabled
        if options.normalize_background:
            processed_image = self._normalize_background(processed_image, options)
            operations_performed.append("normalize_background")
        
        # 4. Apply enhancements
        if options.auto_enhance or any([
            options.brightness_adjustment != 0,
            options.contrast_adjustment != 0,
            options.sharpness_adjustment != 0
        ]):
            processed_image = self._enhance_image(processed_image, options)
            operations_performed.append("enhance")
        
        # 5. Apply format-specific adjustments
        processed_image = self._apply_format_specific_adjustments(processed_image, format_config)
        operations_performed.append("format_adjustments")
        
        return processed_image
    
    def _resize_image(self, image: np.ndarray, options: ProcessingOptions) -> np.ndarray:
        """Resize image according to options."""
        height, width = image.shape[:2]
        
        if options.target_width and options.target_height:
            if options.maintain_aspect_ratio:
                # Calculate scaling to fit within target dimensions
                scale_w = options.target_width / width
                scale_h = options.target_height / height
                scale = min(scale_w, scale_h)
                
                # Don't upscale unless allowed
                if scale > 1.0 and not options.upscale_allowed:
                    scale = 1.0
                
                new_width = int(width * scale)
                new_height = int(height * scale)
            else:
                new_width = options.target_width
                new_height = options.target_height
        elif options.target_width:
            scale = options.target_width / width
            if scale > 1.0 and not options.upscale_allowed:
                scale = 1.0
            new_width = int(width * scale)
            new_height = int(height * scale)
        elif options.target_height:
            scale = options.target_height / height
            if scale > 1.0 and not options.upscale_allowed:
                scale = 1.0
            new_width = int(width * scale)
            new_height = int(height * scale)
        else:
            return image
        
        return cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_LANCZOS4)
    
    def _auto_crop_to_face(self, image: np.ndarray, options: ProcessingOptions) -> np.ndarray:
        """Auto-crop image to focus on detected face."""
        # This is a simplified implementation
        # In a full implementation, you'd use proper face detection
        
        height, width = image.shape[:2]
        
        # For now, assume face is in the center with some padding
        padding = options.crop_padding
        
        # Calculate crop bounds (simplified)
        crop_width = width * (1.0 - 2 * padding)
        crop_height = height * (1.0 - 2 * padding)
        
        x1 = int((width - crop_width) / 2)
        y1 = int((height - crop_height) / 2)
        x2 = x1 + int(crop_width)
        y2 = y1 + int(crop_height)
        
        return image[y1:y2, x1:x2]
    
    def _normalize_background(self, image: np.ndarray, options: ProcessingOptions) -> np.ndarray:
        """Normalize background color."""
        # This is a simplified background normalization
        # In practice, you'd use more sophisticated background detection
        
        # Convert to HSV for better color manipulation
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        # Create a mask for background pixels (simplified approach)
        # This assumes background is in the outer regions
        height, width = image.shape[:2]
        mask = np.zeros((height, width), dtype=np.uint8)
        
        # Sample outer regions
        border_width = max(5, min(width, height) // 20)
        mask[:border_width, :] = 255  # Top
        mask[-border_width:, :] = 255  # Bottom
        mask[:, :border_width] = 255  # Left
        mask[:, -border_width:] = 255  # Right
        
        # Get background color statistics
        background_pixels = image[mask > 0]
        if len(background_pixels) > 0:
            mean_color = np.mean(background_pixels, axis=0)
            target_color = np.array(options.target_background_color[::-1])  # BGR format
            
            # Apply color correction
            color_diff = target_color - mean_color
            corrected = image.astype(np.float32) + color_diff
            corrected = np.clip(corrected, 0, 255).astype(np.uint8)
            
            return corrected
        
        return image
    
    def _enhance_image(self, image: np.ndarray, options: ProcessingOptions) -> np.ndarray:
        """Apply image enhancements."""
        # Convert to PIL for easier enhancement operations
        pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        
        # Apply brightness adjustment
        if options.brightness_adjustment != 0:
            enhancer = ImageEnhance.Brightness(pil_image)
            factor = 1.0 + options.brightness_adjustment
            pil_image = enhancer.enhance(factor)
        
        # Apply contrast adjustment
        if options.contrast_adjustment != 0:
            enhancer = ImageEnhance.Contrast(pil_image)
            factor = 1.0 + options.contrast_adjustment
            pil_image = enhancer.enhance(factor)
        
        # Apply sharpness adjustment
        if options.sharpness_adjustment != 0:
            enhancer = ImageEnhance.Sharpness(pil_image)
            factor = 1.0 + options.sharpness_adjustment
            pil_image = enhancer.enhance(factor)
        
        # Auto-enhance if enabled
        if options.auto_enhance:
            # Apply subtle automatic enhancements
            
            # Slight contrast boost
            enhancer = ImageEnhance.Contrast(pil_image)
            pil_image = enhancer.enhance(1.1)
            
            # Slight sharpness boost
            enhancer = ImageEnhance.Sharpness(pil_image)
            pil_image = enhancer.enhance(1.05)
        
        # Convert back to OpenCV format
        return cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
    
    def _apply_format_specific_adjustments(self, image: np.ndarray, format_config: Dict) -> np.ndarray:
        """Apply format-specific adjustments based on configuration."""
        # This would implement format-specific processing rules
        # For now, just return the image as-is
        return image
    
    def _save_image(self, image: np.ndarray, output_path: str, options: ProcessingOptions):
        """Save processed image to file."""
        # Convert to PIL for saving with proper quality and DPI settings
        pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        
        # Set DPI
        dpi = (options.output_dpi, options.output_dpi)
        
        # Save with appropriate settings
        if options.output_format.upper() in ['JPEG', 'JPG']:
            pil_image.save(output_path, 'JPEG', quality=options.output_quality, dpi=dpi, optimize=True)
        elif options.output_format.upper() == 'PNG':
            pil_image.save(output_path, 'PNG', dpi=dpi, optimize=True)
        else:
            pil_image.save(output_path, options.output_format.upper(), dpi=dpi)
    
    def _calculate_processing_time(self, start_tick: int) -> float:
        """Calculate processing time in seconds."""
        end_tick = cv2.getTickCount()
        return (end_tick - start_tick) / cv2.getTickFrequency()
    
    def get_supported_formats(self) -> List[str]:
        """Get list of supported image formats."""
        return self.supported_formats.copy()
    
    def validate_input_file(self, file_path: str) -> bool:
        """Check if input file is a supported image format."""
        if not os.path.exists(file_path):
            return False
        
        ext = os.path.splitext(file_path)[1].lower()
        return ext in self.supported_formats

