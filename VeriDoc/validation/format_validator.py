"""
Format-specific validation engine for document photos.
"""
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass

import cv2
import numpy as np
from PIL import Image

from .validation_models import (
    ValidationIssue, ValidationSeverity, ValidationCategory,
    DimensionResult, PositionResult, BackgroundResult, QualityResult,
    ComplianceResult
)


@dataclass
class ValidationReport:
    """Complete validation report for an image."""
    image_path: str
    format_name: str
    compliance_result: ComplianceResult
    processing_time: float
    timestamp: str
    
    @property
    def passes(self) -> bool:
        """Whether the image passes validation."""
        return self.compliance_result.overall_pass
    
    @property
    def score(self) -> float:
        """Compliance score (0-100)."""
        return self.compliance_result.compliance_score
    
    @property
    def issues(self) -> List[ValidationIssue]:
        """All validation issues."""
        return self.compliance_result.issues
    
    @property
    def critical_issues(self) -> List[ValidationIssue]:
        """Critical validation issues."""
        return self.compliance_result.critical_issues


class FormatValidator:
    """Main format validation engine."""
    
    def __init__(self, config_dir: str = "config"):
        """Initialize the format validator.
        
        Args:
            config_dir: Directory containing format configuration files
        """
        self.config_dir = Path(config_dir)
        self.formats: Dict[str, Dict] = {}
        self.reload_configuration()
    
    def reload_configuration(self):
        """Load all format configurations."""
        formats_dir = self.config_dir / "formats"
        if formats_dir.exists():
            for format_file in formats_dir.glob("*.json"):
                try:
                    with open(format_file, 'r') as f:
                        format_data = json.load(f)
                        format_id = format_data.get('id', format_file.stem)
                        self.formats[format_id] = format_data
                except Exception as e:
                    print(f"Error loading format {format_file}: {e}")
        
        # Also load individual format files in config root
        for format_file in self.config_dir.glob("*_strict.json"):
            try:
                with open(format_file, 'r') as f:
                    format_data = json.load(f)
                    format_id = format_data.get('id', format_file.stem)
                    self.formats[format_id] = format_data
            except Exception as e:
                print(f"Error loading format {format_file}: {e}")
    
    def get_available_formats(self) -> List[str]:
        """Get list of available format IDs."""
        return list(self.formats.keys())
    
    def validate_image(self, image_path: str, format_id: str) -> ValidationReport:
        """Validate an image against a specific format.
        
        Args:
            image_path: Path to the image file
            format_id: ID of the format to validate against
            
        Returns:
            ValidationReport with validation results
        """
        start_time = time.time()
        
        if format_id not in self.formats:
            raise ValueError(f"Unknown format: {format_id}")
        
        format_config = self.formats[format_id]
        
        # Load image
        try:
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Could not load image: {image_path}")
        except Exception as e:
            # Create minimal failure report
            issues = [ValidationIssue(
                category=ValidationCategory.QUALITY,
                severity=ValidationSeverity.CRITICAL,
                message=f"Failed to load image: {str(e)}",
                suggestion="Ensure the file is a valid image format",
                auto_fixable=False
            )]
            
            compliance_result = ComplianceResult(
                overall_pass=False,
                compliance_score=0.0,
                dimension_check=self._create_empty_dimension_result(False),
                position_check=self._create_empty_position_result(False),
                background_check=self._create_empty_background_result(False),
                quality_check=self._create_empty_quality_result(False),
                issues=issues,
                format_name=format_id,
                processing_time=time.time() - start_time
            )
            
            return ValidationReport(
                image_path=image_path,
                format_name=format_id,
                compliance_result=compliance_result,
                processing_time=time.time() - start_time,
                timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
            )
        
        # Perform validation checks
        dimension_result = self._validate_dimensions(image, format_config)
        position_result = self._validate_face_position(image, format_config)
        background_result = self._validate_background(image, format_config)
        quality_result = self._validate_quality(image, format_config)
        
        # Combine all issues
        all_issues = []
        all_issues.extend(dimension_result.issues)
        all_issues.extend(position_result.issues)
        all_issues.extend(background_result.issues)
        all_issues.extend(quality_result.issues)
        
        # Calculate overall pass/fail
        overall_pass = (dimension_result.passes and 
                       position_result.passes and 
                       background_result.passes and 
                       quality_result.passes)
        
        # Calculate compliance score
        compliance_score = self._calculate_compliance_score(
            dimension_result, position_result, background_result, quality_result
        )
        
        processing_time = time.time() - start_time
        
        compliance_result = ComplianceResult(
            overall_pass=overall_pass,
            compliance_score=compliance_score,
            dimension_check=dimension_result,
            position_check=position_result,
            background_check=background_result,
            quality_check=quality_result,
            issues=all_issues,
            format_name=format_id,
            processing_time=processing_time
        )
        
        return ValidationReport(
            image_path=image_path,
            format_name=format_id,
            compliance_result=compliance_result,
            processing_time=processing_time,
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
        )
    
    def _validate_dimensions(self, image: np.ndarray, format_config: Dict) -> DimensionResult:
        """Validate image dimensions."""
        height, width = image.shape[:2]
        issues = []
        
        # Get dimension requirements
        dimensions = format_config.get('dimensions', {})
        pixel_constraints = dimensions.get('pixel_constraints', {})
        min_shorter_px = pixel_constraints.get('min_shorter_px', 300)
        max_longer_px = pixel_constraints.get('max_longer_px', 3000)
        dpi_min = dimensions.get('dpi_min', 300)
        
        # Check minimum dimensions
        shorter_side = min(width, height)
        longer_side = max(width, height)
        
        passes = True
        
        if shorter_side < min_shorter_px:
            issues.append(ValidationIssue(
                category=ValidationCategory.DIMENSIONS,
                severity=ValidationSeverity.MAJOR,
                message=f"Image too small: {shorter_side}px < {min_shorter_px}px minimum",
                suggestion="Use a higher resolution image",
                auto_fixable=False
            ))
            passes = False
        
        if longer_side > max_longer_px:
            issues.append(ValidationIssue(
                category=ValidationCategory.DIMENSIONS,
                severity=ValidationSeverity.MINOR,
                message=f"Image very large: {longer_side}px > {max_longer_px}px recommended",
                suggestion="Consider resizing for better performance",
                auto_fixable=True
            ))
        
        # Check aspect ratio
        aspect_ratios = dimensions.get('acceptable_aspect_ratios', [])
        if aspect_ratios:
            actual_ratio = width / height
            ratio_match = False
            
            for ratio_spec in aspect_ratios:
                target_ratio = ratio_spec.get('ratio', 1.0)
                tolerance = ratio_spec.get('tolerance', 0.05)
                
                if abs(actual_ratio - target_ratio) <= tolerance:
                    ratio_match = True
                    break
            
            if not ratio_match:
                issues.append(ValidationIssue(
                    category=ValidationCategory.DIMENSIONS,
                    severity=ValidationSeverity.MAJOR,
                    message=f"Aspect ratio {actual_ratio:.3f} doesn't match required ratios",
                    suggestion="Crop image to correct aspect ratio",
                    auto_fixable=True
                ))
                passes = False
        
        return DimensionResult(
            passes=passes,
            actual_width=width,
            actual_height=height,
            required_width=min_shorter_px,
            required_height=min_shorter_px,
            actual_dpi=None,  # Would need EXIF data
            required_dpi=dpi_min,
            width_ratio=1.0,
            height_ratio=1.0,
            issues=issues
        )
    
    def _validate_face_position(self, image: np.ndarray, format_config: Dict) -> PositionResult:
        """Validate face position and geometry."""
        issues = []

        # Analyze image to estimate face position dynamically
        height, width = image.shape[:2]

        # Convert to HSV for better skin detection
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Use actual face detector for better results
        from detection.face_detector import FaceDetector
        face_detector = FaceDetector()
        face_result = face_detector.detect_face(image)
        
        # Initialize default values
        face_height_ratio = 0.70  # Default assumption
        face_width_ratio = 0.50
        face_center_x = 0.5
        face_center_y = 0.5
        eye_height_ratio = 0.6
        face_angle = 0.0
        
        # If AI face detection works, use those results
        if face_result.face_found and face_result.bounding_box:
            bbox = face_result.bounding_box
            face_height_ratio = bbox.height / height
            face_width_ratio = bbox.width / width
            face_center_x = (bbox.x + bbox.width/2) / width
            face_center_y = (bbox.y + bbox.height/2) / height
            eye_height_ratio = (bbox.y + bbox.height * 0.35) / height
            face_angle = 0.0  # Could be enhanced with landmark detection
        else:
            # Fallback to skin detection
            skin_mask = self._detect_skin_areas(hsv)
            skin_pixels = cv2.countNonZero(skin_mask)
            
            # Estimate face region based on skin pixels
            if skin_pixels > 0:
                # Find contours of skin areas
                contours, _ = cv2.findContours(skin_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                if contours:
                    # Get largest skin region as potential face
                    largest_contour = max(contours, key=cv2.contourArea)
                    x, y, w, h = cv2.boundingRect(largest_contour)

                    # Calculate face ratios dynamically
                    face_height_ratio = h / height
                    face_width_ratio = w / width
                    face_center_x = (x + w/2) / width
                    face_center_y = (y + h/2) / height

                    # Estimate eye position (roughly 2/3 from top of face)
                    eye_height_ratio = (y + h * 0.35) / height

                    # Estimate face angle from bounding box
                    aspect_ratio = w / h if h > 0 else 1.0
                    face_angle = 0.0  # Simplified - could use more complex analysis
                else:
                    # Fallback to center-based estimation using image analysis
                    # Analyze image brightness distribution to estimate face position
                    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                    brightness_variation = cv2.Laplacian(gray, cv2.CV_64F)

                    # Use brightness variation to estimate face position
                    # (faces typically have more detail/contrast)
                    var_y = np.var(brightness_variation, axis=1)
                    var_x = np.var(brightness_variation, axis=0)

                    # Find region with highest variation (likely face area)
                    face_y_center = np.argmax(var_y) / height
                    face_x_center = np.argmax(var_x) / width

                    face_height_ratio = 0.75  # Standard assumption
                    eye_height_ratio = face_y_center + 0.08  # Eye level relative to face center
                    face_center_x = face_x_center
                    face_center_y = face_y_center
                    face_angle = 0.0  # Assume straight
            else:
                # No skin detected - use image analysis for consistent estimation
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

                # Find the region with highest edge density (likely face)
                edges = cv2.Canny(gray, 100, 200)
                edge_density_y = np.sum(edges, axis=1)
                edge_density_x = np.sum(edges, axis=0)

                # Find region with highest edge density
                face_y_idx = np.argmax(edge_density_y)
                face_x_idx = np.argmax(edge_density_x)

                face_center_y = face_y_idx / height
                face_center_x = face_x_idx / width
                face_height_ratio = 0.70  # Conservative estimate
                eye_height_ratio = face_center_y + 0.05  # Conservative eye position
                face_angle = 0.0  # Assume straight
        
        geometry = format_config.get('geometry', {})
        head_height = geometry.get('head_height_ratio', {})
        eye_level = geometry.get('eye_level_from_bottom_ratio', {})
        center_tolerance = geometry.get('center_tolerance', {})
        
        passes = True
        
        # Check head height ratio
        if head_height:
            min_ratio = head_height.get('min', 0.68)
            max_ratio = head_height.get('max', 0.82)
            
            if face_height_ratio < min_ratio:
                issues.append(ValidationIssue(
                    category=ValidationCategory.FACE,
                    severity=ValidationSeverity.MAJOR,
                    message=f"Head too small: {face_height_ratio:.2f} < {min_ratio}",
                    suggestion="Move closer to camera or crop tighter",
                    auto_fixable=True
                ))
                passes = False
            elif face_height_ratio > max_ratio:
                issues.append(ValidationIssue(
                    category=ValidationCategory.FACE,
                    severity=ValidationSeverity.MAJOR,
                    message=f"Head too large: {face_height_ratio:.2f} > {max_ratio}",
                    suggestion="Move further from camera or crop wider",
                    auto_fixable=True
                ))
                passes = False
        
        # Check eye level
        if eye_level:
            min_eye = eye_level.get('min', 0.55)
            max_eye = eye_level.get('max', 0.70)
            
            if eye_height_ratio < min_eye or eye_height_ratio > max_eye:
                issues.append(ValidationIssue(
                    category=ValidationCategory.FACE,
                    severity=ValidationSeverity.MAJOR,
                    message=f"Eye level {eye_height_ratio:.2f} outside range {min_eye}-{max_eye}",
                    suggestion="Adjust vertical positioning",
                    auto_fixable=True
                ))
                passes = False
        
        # Check centering
        if center_tolerance:
            h_tolerance = center_tolerance.get('horizontal_pct', 5.0) / 100.0
            v_tolerance = center_tolerance.get('vertical_pct', 5.0) / 100.0
            
            if abs(face_center_x - 0.5) > h_tolerance:
                issues.append(ValidationIssue(
                    category=ValidationCategory.FACE,
                    severity=ValidationSeverity.MINOR,
                    message="Face not horizontally centered",
                    suggestion="Center the face horizontally",
                    auto_fixable=True
                ))
            
            if abs(face_center_y - 0.5) > v_tolerance:
                issues.append(ValidationIssue(
                    category=ValidationCategory.FACE,
                    severity=ValidationSeverity.MINOR,
                    message="Face not vertically centered",
                    suggestion="Center the face vertically",
                    auto_fixable=True
                ))
        
        # Calculate dynamic centering and positioning scores
        # Centering score based on how close to center the face is
        center_distance = np.sqrt((face_center_x - 0.5)**2 + (face_center_y - 0.5)**2)
        centering_score = max(0, min(100, 100 - center_distance * 200))  # Closer to center = higher score

        # Positioning score based on face height and eye level compliance
        position_score = 100.0
        if head_height:
            if face_height_ratio < head_height.get('min', 0.68) or face_height_ratio > head_height.get('max', 0.82):
                position_score -= 20
        if eye_level:
            if eye_height_ratio < eye_level.get('min', 0.55) or eye_height_ratio > eye_level.get('max', 0.70):
                position_score -= 15

        # Angle penalty
        angle_penalty = abs(face_angle) * 5  # 5 points per degree off center
        positioning_score = max(0, min(100, position_score - angle_penalty))

        return PositionResult(
            passes=passes,
            face_height_ratio=face_height_ratio,
            eye_height_ratio=eye_height_ratio,
            face_center_x=face_center_x,
            face_center_y=face_center_y,
            face_angle=face_angle,
            centering_score=centering_score,
            positioning_score=positioning_score,
            issues=issues
        )
    
    def _validate_background(self, image: np.ndarray, format_config: Dict) -> BackgroundResult:
        """Validate background requirements."""
        issues = []
        
        background = format_config.get('background', {})
        required_type = background.get('required', 'plain_light_coloured')
        
        # Simple background analysis
        # Convert to RGB for color analysis
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Get dominant color (simplified)
        pixels = rgb_image.reshape(-1, 3)
        mean_color = np.mean(pixels, axis=0).astype(int)
        
        # Check if background is light enough - More realistic threshold
        brightness = np.mean(mean_color)
        min_brightness = background.get('lab_L_mean_min', 100)  # Reduced from 120 to 100
        
        passes = True
        
        if required_type == 'plain_light_coloured' and brightness < min_brightness:
            issues.append(ValidationIssue(
                category=ValidationCategory.BACKGROUND,
                severity=ValidationSeverity.MAJOR,
                message=f"Background too dark: {brightness:.1f} < {min_brightness}",
                suggestion="Use a lighter background",
                auto_fixable=True
            ))
            passes = False
        
        # Check uniformity (simplified) - More forgiving for real photos
        std_dev = np.std(pixels, axis=0)
        max_std = background.get('lab_L_stddev_max', 50.0)  # Increased from 25 to 50
        
        if np.mean(std_dev) > max_std:
            issues.append(ValidationIssue(
                category=ValidationCategory.BACKGROUND,
                severity=ValidationSeverity.MINOR,
                message="Background not uniform enough",
                suggestion="Use a plain, uniform background",
                auto_fixable=True
            ))
        
        # Calculate dynamic uniformity score
        # Analyze color variance in the image
        color_variance = np.var(pixels, axis=0)
        avg_variance = np.mean(color_variance)

        # Uniformity score based on inverse of variance (lower variance = higher uniformity)
        # More forgiving scoring for real photos
        uniformity_score = max(0, min(100, 100 - avg_variance / 5))  # Divided by 5 instead of 2

        # Calculate color difference from required color
        required_color = np.array([240, 240, 240])  # Light gray
        color_difference = np.linalg.norm(mean_color - required_color)

        return BackgroundResult(
            passes=passes,
            dominant_color=mean_color.tolist(),
            required_color=required_color.tolist(),
            color_difference=color_difference,
            uniformity_score=uniformity_score,
            required_uniformity=90.0,
            issues=issues
        )
    
    def _validate_quality(self, image: np.ndarray, format_config: Dict) -> QualityResult:
        """Validate image quality."""
        issues = []
        
        quality = format_config.get('quality', {})
        
        # Convert to grayscale for quality analysis
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Check sharpness using Laplacian variance - More realistic for phone cameras
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        min_sharpness = quality.get('blur_laplacian_var_min', 20.0)  # Reduced from 50 to 20
        
        passes = True
        
        if laplacian_var < min_sharpness:
            issues.append(ValidationIssue(
                category=ValidationCategory.QUALITY,
                severity=ValidationSeverity.MAJOR,
                message=f"Image too blurry: {laplacian_var:.1f} < {min_sharpness}",
                suggestion="Use a sharper image or better focus",
                auto_fixable=False
            ))
            passes = False
        
        # Check brightness - Use more realistic government standards
        brightness = np.mean(gray)
        min_brightness = quality.get('brightness_L_min', 50.0)  # Reduced from 60 to 50
        max_brightness = quality.get('brightness_L_max', 240.0)  # Increased from 220 to 240
        
        if brightness < min_brightness:
            issues.append(ValidationIssue(
                category=ValidationCategory.QUALITY,
                severity=ValidationSeverity.MAJOR,
                message=f"Image too dark: {brightness:.1f} < {min_brightness}",
                suggestion="Increase lighting or brightness",
                auto_fixable=True
            ))
            passes = False
        elif brightness > max_brightness:
            issues.append(ValidationIssue(
                category=ValidationCategory.QUALITY,
                severity=ValidationSeverity.MAJOR,
                message=f"Image too bright: {brightness:.1f} > {max_brightness}",
                suggestion="Reduce lighting or brightness",
                auto_fixable=True
            ))
            passes = False
        
        # Check contrast - Even more forgiving for real photos
        contrast = np.std(gray) / 255.0
        min_contrast = quality.get('contrast_min', 0.04)  # Reduced from 0.08 to 0.04
        
        if contrast < min_contrast:
            issues.append(ValidationIssue(
                category=ValidationCategory.QUALITY,
                severity=ValidationSeverity.MINOR,
                message=f"Low contrast: {contrast:.3f} < {min_contrast}",
                suggestion="Improve lighting contrast",
                auto_fixable=True
            ))
        
        # Calculate dynamic quality scores
        # Sharpness score (0-100) based on Laplacian variance
        sharpness_score = min(100.0, laplacian_var / 2.0)

        # Brightness score (0-100) - higher is better
        brightness_score = max(0, min(100, 100 - abs(brightness - 55) * 2))

        # Contrast score (0-100) based on actual contrast
        contrast_score = min(100.0, contrast * 20.0)  # Scale contrast to 0-100

        # Noise score (0-100) - estimate based on sharpness (inverse relationship)
        noise_score = max(0, min(100, 100 - (laplacian_var / 10.0)))

        # Overall quality score as weighted average
        overall_quality_score = (sharpness_score * 0.4 + brightness_score * 0.3 +
                               contrast_score * 0.2 + noise_score * 0.1)

        return QualityResult(
            passes=passes,
            sharpness_score=sharpness_score,
            brightness_score=brightness_score,
            contrast_score=contrast_score,
            noise_score=noise_score,
            overall_quality_score=overall_quality_score,
            issues=issues
        )
    
    def _calculate_compliance_score(self, dimension_result: DimensionResult,
                                  position_result: PositionResult,
                                  background_result: BackgroundResult,
                                  quality_result: QualityResult) -> float:
        """Calculate overall compliance score."""
        scores = []
        
        # Dimension score
        if dimension_result.passes:
            scores.append(100.0)
        else:
            scores.append(max(0.0, 100.0 - len(dimension_result.issues) * 20))
        
        # Position score
        scores.append(position_result.positioning_score)
        
        # Background score
        scores.append(background_result.uniformity_score)
        
        # Quality score
        scores.append(quality_result.overall_quality_score)
        
        return np.mean(scores)
    
    def _create_empty_dimension_result(self, passes: bool) -> DimensionResult:
        """Create empty dimension result for error cases."""
        return DimensionResult(
            passes=passes,
            actual_width=0,
            actual_height=0,
            required_width=0,
            required_height=0,
            actual_dpi=None,
            required_dpi=300,
            width_ratio=0.0,
            height_ratio=0.0,
            issues=[]
        )
    
    def _create_empty_position_result(self, passes: bool) -> PositionResult:
        """Create empty position result for error cases."""
        return PositionResult(
            passes=passes,
            face_height_ratio=0.0,
            eye_height_ratio=0.0,
            face_center_x=0.0,
            face_center_y=0.0,
            face_angle=0.0,
            centering_score=0.0,
            positioning_score=0.0,
            issues=[]
        )
    
    def _create_empty_background_result(self, passes: bool) -> BackgroundResult:
        """Create empty background result for error cases."""
        return BackgroundResult(
            passes=passes,
            dominant_color=[0, 0, 0],
            required_color=[240, 240, 240],
            color_difference=0.0,
            uniformity_score=0.0,
            required_uniformity=90.0,
            issues=[]
        )
    
    def _detect_skin_areas(self, hsv_image: np.ndarray) -> np.ndarray:
        """Simple skin detection using HSV color space."""
        # Define skin color range in HSV
        lower_skin = np.array([0, 20, 70], dtype=np.uint8)
        upper_skin = np.array([25, 255, 255], dtype=np.uint8)

        # Create mask for skin-colored pixels
        skin_mask = cv2.inRange(hsv_image, lower_skin, upper_skin)

        # Apply morphological operations to clean up the mask
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        skin_mask = cv2.morphologyEx(skin_mask, cv2.MORPH_OPEN, kernel, iterations=2)
        skin_mask = cv2.morphologyEx(skin_mask, cv2.MORPH_CLOSE, kernel, iterations=2)

        return skin_mask

    def _create_empty_quality_result(self, passes: bool) -> QualityResult:
        """Create empty quality result for error cases."""
        return QualityResult(
            passes=passes,
            sharpness_score=0.0,
            brightness_score=0.0,
            contrast_score=0.0,
            noise_score=0.0,
            overall_quality_score=0.0,
            issues=[]
        )

