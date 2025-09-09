"""
Data models for ICAO compliance validation.
"""
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from enum import Enum


class ValidationSeverity(Enum):
    """Severity levels for validation issues."""
    CRITICAL = "critical"
    MAJOR = "major"
    MINOR = "minor"


class ValidationCategory(Enum):
    """Categories of validation issues."""
    FACE = "face"
    BACKGROUND = "background"
    QUALITY = "quality"
    DIMENSIONS = "dimensions"


@dataclass
class ValidationIssue:
    """Represents a specific validation issue."""
    category: ValidationCategory
    severity: ValidationSeverity
    message: str
    suggestion: str
    auto_fixable: bool
    rule_reference: Optional[str] = None


@dataclass
class DimensionResult:
    """Result of dimension validation."""
    passes: bool
    actual_width: int
    actual_height: int
    required_width: int
    required_height: int
    actual_dpi: Optional[int]
    required_dpi: int
    width_ratio: float
    height_ratio: float
    issues: List[ValidationIssue]


@dataclass
class PositionResult:
    """Result of face position validation."""
    passes: bool
    face_height_ratio: float
    eye_height_ratio: float
    face_center_x: float
    face_center_y: float
    face_angle: float
    centering_score: float
    positioning_score: float
    issues: List[ValidationIssue]


@dataclass
class BackgroundResult:
    """Result of background validation."""
    passes: bool
    dominant_color: List[int]  # RGB values
    required_color: List[int]  # RGB values
    color_difference: float
    uniformity_score: float
    required_uniformity: float
    issues: List[ValidationIssue]


@dataclass
class QualityResult:
    """Result of image quality validation."""
    passes: bool
    sharpness_score: float
    brightness_score: float
    contrast_score: float
    noise_score: float
    overall_quality_score: float
    issues: List[ValidationIssue]


@dataclass
class ComplianceResult:
    """Overall compliance validation result."""
    overall_pass: bool
    compliance_score: float  # 0-100
    dimension_check: DimensionResult
    position_check: PositionResult
    background_check: BackgroundResult
    quality_check: QualityResult
    issues: List[ValidationIssue]
    format_name: str
    processing_time: float
    
    @property
    def critical_issues(self) -> List[ValidationIssue]:
        """Get all critical issues."""
        return [issue for issue in self.issues if issue.severity == ValidationSeverity.CRITICAL]
    
    @property
    def auto_fixable_issues(self) -> List[ValidationIssue]:
        """Get all auto-fixable issues."""
        return [issue for issue in self.issues if issue.auto_fixable]
    
    @property
    def summary(self) -> str:
        """Get a summary of the validation result."""
        if self.overall_pass:
            return f"PASS - Compliance score: {self.compliance_score:.1f}%"
        else:
            critical_count = len(self.critical_issues)
            total_issues = len(self.issues)
            return f"FAIL - {total_issues} issues ({critical_count} critical), Score: {self.compliance_score:.1f}%"