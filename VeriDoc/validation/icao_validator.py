"""
Single authoritative ICAO compliance validator.

This module provides the definitive validation engine for photo compliance
against ICAO standards and government format requirements.
"""
import cv2
import numpy as np
import time
from typing import Dict, Any, List, Tuple, Optional
from PIL import Image, ExifTags

from detection.data_models import FaceMetrics
from .validation_models import (
    ComplianceResult, DimensionResult, PositionResult, 
    BackgroundResult, QualityResult, ValidationIssue,
    ValidationSeverity, ValidationCategory
)


class ICAOValidator:
    """
    Single authoritative ICAO compliance validator.
    
    This class serves as the single source of truth for all photo validation
    against ICAO standards and government format requirements.
    """
    
    def __init__(self, format_rules: Dict[str, Any]):
        """
        Initialize the ICAO validator.
        
        Args:
            format_rules: Dictionary containing format-specific validation rules
        """
        self.format_rules = format_rules
        self._setup_validation_thresholds()
    
    def _setup_validation_thresholds(self):
        """Setup internal validation thresholds."""
        # Sharpness detection kernels
        self.laplacian_kernel = np.array([[0, -1, 0], [-1, 4, -1], [0, -1, 0]])
        self.sobel_x = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]])
        self.sobel_y = np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]])
    
    def validate_compliance(
        self, 
        image: np.ndarray, 
        face_metrics: FaceMetrics, 
        format_name: str
    ) -> ComplianceResult:
        """
        Validate complete ICAO compliance for an image.
        
        Args:
            image: Input image as numpy array
            face_metrics: Detected face metrics
            format_name: Name of the format to validate against
            
        Returns:
            ComplianceResult with detailed validation results
        """
        start_time = time.time()
        
        if format_name not in self.format_rules['formats']:
            raise ValueError(f"Unknown format: {format_name}")
        
        format_config = self.format_rules['formats'][format_name]
        
        # Run all validation checks
        dimension_result = self.check_dimensions(image, format_name)
        position_result = self.check_face_position(face_metrics, format_name)
        background_result = self.check_background(image, format_name)
        quality_result = self.check_image_quality(image, format_name)
        
        # Collect all issues
        all_issues = []
        all_issues.extend(dimension_result.issues)
        all_issues.extend(position_result.issues)
        all_issues.extend(background_result.issues)
        all_issues.extend(quality_result.issues)
        
        # Calculate overall compliance
        overall_pass = (
            dimension_result.passes and
            position_result.passes and
            background_result.passes and
            quality_result.passes
        )
        
        # Calculate compliance score (weighted average)
        weights = {
            'dimensions': 0.25,
            'position': 0.30,
            'background': 0.20,
            'quality': 0.25
        }
        
        dimension_score = 100.0 if dimension_result.passes else max(0, 100 - len(dimension_result.issues) * 20)
        position_score = position_result.positioning_score * 100
        background_score = background_result.uniformity_score * 100
        quality_score = quality_result.overall_quality_score * 100
        
        compliance_score = (
            dimension_score * weights['dimensions'] +
            position_score * weights['position'] +
            background_score * weights['background'] +
            quality_score * weights['quality']
        )
        
        processing_time = time.time() - start_time
        
        return ComplianceResult(
            overall_pass=overall_pass,
            compliance_score=compliance_score,
            dimension_check=dimension_result,
            position_check=position_result,
            background_check=background_result,
            quality_check=quality_result,
            issues=all_issues,
            format_name=format_name,
            processing_time=processing_time
        )
    
    def check_dimensions(self, image: np.ndarray, format_name: str) -> DimensionResult:
        """
        Check image dimensions against format requirements.
        
        Args:
            image: Input image as numpy array
            format_name: Name of the format to validate against
            
        Returns:
            DimensionResult with dimension validation details
        """
        format_config = self.format_rules['formats'][format_name]
        dim_config = format_config['dimensions']
        
        height, width = image.shape[:2]
        required_width = dim_config['width']
        required_height = dim_config['height']
        required_dpi = dim_config['dpi']
        tolerance = dim_config['tolerance']
        
        # Calculate ratios
        width_ratio = width / required_width
        height_ratio = height / required_height
        
        # Check if dimensions are within tolerance
        width_ok = abs(width_ratio - 1.0) <= tolerance
        height_ok = abs(height_ratio - 1.0) <= tolerance
        
        issues = []
        
        if not width_ok:
            severity = ValidationSeverity.CRITICAL if abs(width_ratio - 1.0) > tolerance * 2 else ValidationSeverity.MAJOR
            issues.append(ValidationIssue(
                category=ValidationCategory.DIMENSIONS,
                severity=severity,
                message=f"Width {width}px doesn't match required {required_width}px (ratio: {width_ratio:.3f})",
                suggestion=f"Resize image to {required_width}x{required_height} pixels",
                auto_fixable=True,
                rule_reference="ICAO 9303 - Image dimensions"
            ))
        
        if not height_ok:
            severity = ValidationSeverity.CRITICAL if abs(height_ratio - 1.0) > tolerance * 2 else ValidationSeverity.MAJOR
            issues.append(ValidationIssue(
                category=ValidationCategory.DIMENSIONS,
                severity=severity,
                message=f"Height {height}px doesn't match required {required_height}px (ratio: {height_ratio:.3f})",
                suggestion=f"Resize image to {required_width}x{required_height} pixels",
                auto_fixable=True,
                rule_reference="ICAO 9303 - Image dimensions"
            ))
        
        # Try to get DPI from image metadata
        actual_dpi = self._get_image_dpi(image)
        if actual_dpi and actual_dpi < required_dpi * 0.9:
            issues.append(ValidationIssue(
                category=ValidationCategory.QUALITY,
                severity=ValidationSeverity.MAJOR,
                message=f"DPI {actual_dpi} is below required {required_dpi}",
                suggestion=f"Ensure image has at least {required_dpi} DPI for print quality",
                auto_fixable=False,
                rule_reference="ICAO 9303 - Print quality"
            ))
        
        return DimensionResult(
            passes=width_ok and height_ok,
            actual_width=width,
            actual_height=height,
            required_width=required_width,
            required_height=required_height,
            actual_dpi=actual_dpi,
            required_dpi=required_dpi,
            width_ratio=width_ratio,
            height_ratio=height_ratio,
            issues=issues
        )
    
    def check_face_position(self, face_metrics: FaceMetrics, format_name: str) -> PositionResult:
        """
        Validate face positioning using detected face metrics.
        
        Args:
            face_metrics: Detected face metrics
            format_name: Name of the format to validate against
            
        Returns:
            PositionResult with face positioning validation details
        """
        format_config = self.format_rules['formats'][format_name]
        face_config = format_config['face_requirements']
        
        # Get requirements
        face_height_range = face_config['face_height_ratio']
        eye_height_range = face_config['eye_height_ratio']
        centering_tolerance = face_config['centering_tolerance']
        max_face_angle = face_config['max_face_angle']
        
        issues = []
        
        # Check face height ratio
        face_height_ok = face_height_range[0] <= face_metrics.face_height_ratio <= face_height_range[1]
        if not face_height_ok:
            severity = ValidationSeverity.CRITICAL
            if face_metrics.face_height_ratio < face_height_range[0]:
                message = f"Face too small: {face_metrics.face_height_ratio:.3f} (min: {face_height_range[0]:.3f})"
                suggestion = "Move closer to camera or crop image to make face larger"
            else:
                message = f"Face too large: {face_metrics.face_height_ratio:.3f} (max: {face_height_range[1]:.3f})"
                suggestion = "Move away from camera or crop image to make face smaller"
            
            issues.append(ValidationIssue(
                category=ValidationCategory.FACE,
                severity=severity,
                message=message,
                suggestion=suggestion,
                auto_fixable=True,
                rule_reference="ICAO 9303 - Face size requirements"
            ))
        
        # Check eye height ratio
        eye_height_ok = eye_height_range[0] <= face_metrics.eye_height_ratio <= eye_height_range[1]
        if not eye_height_ok:
            severity = ValidationSeverity.MAJOR
            message = f"Eye level incorrect: {face_metrics.eye_height_ratio:.3f} (range: {eye_height_range[0]:.3f}-{eye_height_range[1]:.3f})"
            suggestion = "Adjust camera height so eyes are positioned correctly"
            
            issues.append(ValidationIssue(
                category=ValidationCategory.FACE,
                severity=severity,
                message=message,
                suggestion=suggestion,
                auto_fixable=True,
                rule_reference="ICAO 9303 - Eye positioning"
            ))
        
        # Check face centering
        center_x_ok = abs(face_metrics.face_center_x - 0.5) <= centering_tolerance
        center_y_ok = abs(face_metrics.face_center_y - 0.5) <= centering_tolerance
        
        if not center_x_ok:
            issues.append(ValidationIssue(
                category=ValidationCategory.FACE,
                severity=ValidationSeverity.MAJOR,
                message=f"Face not horizontally centered: {face_metrics.face_center_x:.3f} (should be ~0.5)",
                suggestion="Center the face horizontally in the frame",
                auto_fixable=True,
                rule_reference="ICAO 9303 - Face centering"
            ))
        
        if not center_y_ok:
            issues.append(ValidationIssue(
                category=ValidationCategory.FACE,
                severity=ValidationSeverity.MAJOR,
                message=f"Face not vertically centered: {face_metrics.face_center_y:.3f} (should be ~0.5)",
                suggestion="Center the face vertically in the frame",
                auto_fixable=True,
                rule_reference="ICAO 9303 - Face centering"
            ))
        
        # Check face angle
        angle_ok = abs(face_metrics.face_angle) <= max_face_angle
        if not angle_ok:
            issues.append(ValidationIssue(
                category=ValidationCategory.FACE,
                severity=ValidationSeverity.MAJOR,
                message=f"Face tilted: {face_metrics.face_angle:.1f}° (max: {max_face_angle}°)",
                suggestion="Keep head straight and level",
                auto_fixable=True,
                rule_reference="ICAO 9303 - Head position"
            ))
        
        # Check expression requirements
        expression_ok = True
        if not face_metrics.eyes_open:
            expression_ok = False
            issues.append(ValidationIssue(
                category=ValidationCategory.FACE,
                severity=ValidationSeverity.CRITICAL,
                message="Eyes appear to be closed",
                suggestion="Keep eyes open and looking at camera",
                auto_fixable=False,
                rule_reference="ICAO 9303 - Facial expression"
            ))
        
        if not face_metrics.mouth_closed:
            expression_ok = False
            issues.append(ValidationIssue(
                category=ValidationCategory.FACE,
                severity=ValidationSeverity.MAJOR,
                message="Mouth appears to be open",
                suggestion="Keep mouth closed with neutral expression",
                auto_fixable=False,
                rule_reference="ICAO 9303 - Facial expression"
            ))
        
        # Calculate scores
        centering_score = 1.0 - max(
            abs(face_metrics.face_center_x - 0.5) / 0.5,
            abs(face_metrics.face_center_y - 0.5) / 0.5
        )
        centering_score = max(0.0, min(1.0, centering_score))
        
        positioning_score = 0.0
        if face_height_ok:
            positioning_score += 0.4
        if eye_height_ok:
            positioning_score += 0.3
        if center_x_ok and center_y_ok:
            positioning_score += 0.2
        if angle_ok:
            positioning_score += 0.1
        
        # Overall pass requires all positioning AND expression requirements
        overall_pass = (face_height_ok and eye_height_ok and center_x_ok and 
                       center_y_ok and angle_ok and expression_ok)
        
        return PositionResult(
            passes=overall_pass,
            face_height_ratio=face_metrics.face_height_ratio,
            eye_height_ratio=face_metrics.eye_height_ratio,
            face_center_x=face_metrics.face_center_x,
            face_center_y=face_metrics.face_center_y,
            face_angle=face_metrics.face_angle,
            centering_score=centering_score,
            positioning_score=positioning_score,
            issues=issues
        )
    
    def check_background(self, image: np.ndarray, format_name: str) -> BackgroundResult:
        """
        Check background color and uniformity.
        
        Args:
            image: Input image as numpy array
            format_name: Name of the format to validate against
            
        Returns:
            BackgroundResult with background validation details
        """
        format_config = self.format_rules['formats'][format_name]
        bg_config = format_config['background']
        
        required_color = bg_config['required_color']  # RGB
        tolerance = bg_config['tolerance']
        required_uniformity = bg_config['uniformity_threshold']
        
        # Convert image to RGB if needed
        if len(image.shape) == 3 and image.shape[2] == 3:
            # Assume BGR (OpenCV format), convert to RGB
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        else:
            rgb_image = image
        
        # Sample background regions (edges of image)
        height, width = rgb_image.shape[:2]
        edge_width = min(50, width // 10)  # Sample from edges
        
        # Get background samples from all four edges
        top_edge = rgb_image[:edge_width, :].reshape(-1, 3)
        bottom_edge = rgb_image[-edge_width:, :].reshape(-1, 3)
        left_edge = rgb_image[:, :edge_width].reshape(-1, 3)
        right_edge = rgb_image[:, -edge_width:].reshape(-1, 3)
        
        background_samples = np.vstack([top_edge, bottom_edge, left_edge, right_edge])
        
        # Calculate dominant background color
        dominant_color = np.mean(background_samples, axis=0).astype(int)
        
        # Calculate color difference from required color
        color_diff = np.sqrt(np.sum((dominant_color - required_color) ** 2))
        
        # Calculate uniformity (standard deviation of background samples)
        uniformity_score = 1.0 - (np.std(background_samples) / 255.0)
        uniformity_score = max(0.0, min(1.0, uniformity_score))
        
        issues = []
        
        # Check color compliance
        color_ok = color_diff <= tolerance
        if not color_ok:
            severity = ValidationSeverity.CRITICAL if color_diff > tolerance * 2 else ValidationSeverity.MAJOR
            issues.append(ValidationIssue(
                category=ValidationCategory.BACKGROUND,
                severity=severity,
                message=f"Background color {dominant_color.tolist()} doesn't match required {required_color} (diff: {color_diff:.1f})",
                suggestion=f"Use a {self._color_name(required_color)} background",
                auto_fixable=True,
                rule_reference="ICAO 9303 - Background requirements"
            ))
        
        # Check uniformity
        uniformity_ok = uniformity_score >= required_uniformity
        if not uniformity_ok:
            issues.append(ValidationIssue(
                category=ValidationCategory.BACKGROUND,
                severity=ValidationSeverity.MAJOR,
                message=f"Background not uniform enough: {uniformity_score:.3f} (min: {required_uniformity:.3f})",
                suggestion="Use even lighting and avoid shadows on background",
                auto_fixable=True,
                rule_reference="ICAO 9303 - Background uniformity"
            ))
        
        return BackgroundResult(
            passes=bool(color_ok and uniformity_ok),
            dominant_color=dominant_color.tolist(),
            required_color=required_color,
            color_difference=float(color_diff),
            uniformity_score=float(uniformity_score),
            required_uniformity=required_uniformity,
            issues=issues
        )
    
    def check_image_quality(self, image: np.ndarray, format_name: str) -> QualityResult:
        """
        Assess image quality (sharpness, brightness, contrast).
        
        Args:
            image: Input image as numpy array
            format_name: Name of the format to validate against
            
        Returns:
            QualityResult with quality assessment details
        """
        format_config = self.format_rules['formats'][format_name]
        quality_config = format_config['quality']
        
        min_sharpness = quality_config['min_sharpness']
        min_brightness = quality_config['min_brightness']
        max_brightness = quality_config['max_brightness']
        max_noise = quality_config['max_noise']
        
        # Convert to grayscale for analysis
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Calculate sharpness using Laplacian variance
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        # Calculate sharpness using Sobel gradients
        sobel_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        sobel_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        sobel_magnitude = np.sqrt(sobel_x**2 + sobel_y**2)
        sobel_sharpness = np.mean(sobel_magnitude)
        
        # Combined sharpness score
        sharpness_score = (laplacian_var + sobel_sharpness) / 2
        
        # Calculate brightness
        brightness_score = np.mean(gray)
        
        # Calculate contrast (standard deviation)
        contrast_score = np.std(gray)
        
        # Calculate noise (high frequency content in smooth areas)
        # Use bilateral filter to preserve edges while smoothing
        smooth = cv2.bilateralFilter(gray, 9, 75, 75)
        noise_map = np.abs(gray.astype(float) - smooth.astype(float))
        noise_score = np.mean(noise_map) / 255.0
        
        # Overall quality score (normalized 0-1)
        sharpness_norm = min(1.0, sharpness_score / (min_sharpness * 2))
        brightness_norm = 1.0 if min_brightness <= brightness_score <= max_brightness else 0.5
        contrast_norm = min(1.0, contrast_score / 50.0)  # Normalize contrast
        noise_norm = max(0.0, 1.0 - (noise_score / max_noise))
        
        overall_quality = (sharpness_norm * 0.4 + brightness_norm * 0.3 + 
                          contrast_norm * 0.2 + noise_norm * 0.1)
        
        issues = []
        
        # Check sharpness
        if sharpness_score < min_sharpness:
            severity = ValidationSeverity.CRITICAL if sharpness_score < min_sharpness * 0.5 else ValidationSeverity.MAJOR
            issues.append(ValidationIssue(
                category=ValidationCategory.QUALITY,
                severity=severity,
                message=f"Image not sharp enough: {sharpness_score:.1f} (min: {min_sharpness})",
                suggestion="Use better focus, avoid camera shake, ensure good lighting",
                auto_fixable=False,
                rule_reference="ICAO 9303 - Image sharpness"
            ))
        
        # Check brightness
        if brightness_score < min_brightness:
            issues.append(ValidationIssue(
                category=ValidationCategory.QUALITY,
                severity=ValidationSeverity.MAJOR,
                message=f"Image too dark: {brightness_score:.1f} (min: {min_brightness})",
                suggestion="Increase lighting or camera exposure",
                auto_fixable=True,
                rule_reference="ICAO 9303 - Image brightness"
            ))
        elif brightness_score > max_brightness:
            issues.append(ValidationIssue(
                category=ValidationCategory.QUALITY,
                severity=ValidationSeverity.MAJOR,
                message=f"Image too bright: {brightness_score:.1f} (max: {max_brightness})",
                suggestion="Reduce lighting or camera exposure",
                auto_fixable=True,
                rule_reference="ICAO 9303 - Image brightness"
            ))
        
        # Check noise
        if noise_score > max_noise:
            issues.append(ValidationIssue(
                category=ValidationCategory.QUALITY,
                severity=ValidationSeverity.MINOR,
                message=f"Image too noisy: {noise_score:.3f} (max: {max_noise:.3f})",
                suggestion="Use better lighting, lower ISO, or noise reduction",
                auto_fixable=True,
                rule_reference="ICAO 9303 - Image quality"
            ))
        
        # Check contrast
        if contrast_score < 20:
            issues.append(ValidationIssue(
                category=ValidationCategory.QUALITY,
                severity=ValidationSeverity.MINOR,
                message=f"Low contrast: {contrast_score:.1f}",
                suggestion="Improve lighting contrast between subject and background",
                auto_fixable=True,
                rule_reference="ICAO 9303 - Image contrast"
            ))
        
        return QualityResult(
            passes=len(issues) == 0 or all(issue.severity == ValidationSeverity.MINOR for issue in issues),
            sharpness_score=float(sharpness_score),
            brightness_score=float(brightness_score),
            contrast_score=float(contrast_score),
            noise_score=float(noise_score),
            overall_quality_score=float(overall_quality),
            issues=issues
        )
    
    def _get_image_dpi(self, image: np.ndarray) -> Optional[int]:
        """
        Try to extract DPI information from image.
        
        Args:
            image: Input image as numpy array
            
        Returns:
            DPI value if available, None otherwise
        """
        # This is a simplified implementation
        # In practice, DPI would need to be extracted from image metadata
        # For now, return None as we can't get DPI from numpy array
        return None
    
    def _color_name(self, rgb_color: List[int]) -> str:
        """
        Get human-readable color name.
        
        Args:
            rgb_color: RGB color values
            
        Returns:
            Human-readable color name
        """
        r, g, b = rgb_color
        if r > 240 and g > 240 and b > 240:
            return "white"
        elif r < 50 and g < 50 and b < 50:
            return "black"
        elif r > g and r > b:
            return "red"
        elif g > r and g > b:
            return "green"
        elif b > r and b > g:
            return "blue"
        else:
            return "neutral"