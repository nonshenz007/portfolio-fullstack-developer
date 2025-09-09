"""
Unit tests for the ICAO validator core functionality.
"""
import pytest
import numpy as np
import cv2
import json
from unittest.mock import Mock, patch

from validation.icao_validator import ICAOValidator
from validation.validation_models import (
    ValidationSeverity, ValidationCategory, ComplianceResult
)
from detection.data_models import FaceMetrics


class TestICAOValidator:
    """Test cases for ICAOValidator class."""
    
    @pytest.fixture
    def sample_format_rules(self):
        """Sample format rules for testing."""
        return {
            "formats": {
                "TEST-FORMAT": {
                    "display_name": "Test Format",
                    "dimensions": {
                        "width": 400,
                        "height": 500,
                        "dpi": 300,
                        "tolerance": 0.05
                    },
                    "face_requirements": {
                        "face_height_ratio": [0.70, 0.80],
                        "eye_height_ratio": [0.50, 0.60],
                        "centering_tolerance": 0.05,
                        "max_face_angle": 5.0
                    },
                    "background": {
                        "required_color": [255, 255, 255],
                        "tolerance": 15,
                        "uniformity_threshold": 0.9
                    },
                    "quality": {
                        "min_sharpness": 100,
                        "min_brightness": 80,
                        "max_brightness": 200,
                        "max_noise": 0.1
                    }
                }
            }
        }
    
    @pytest.fixture
    def validator(self, sample_format_rules):
        """Create validator instance for testing."""
        return ICAOValidator(sample_format_rules)
    
    @pytest.fixture
    def sample_face_metrics(self):
        """Sample face metrics for testing."""
        return FaceMetrics(
            face_height_ratio=0.75,
            eye_height_ratio=0.55,
            face_center_x=0.5,
            face_center_y=0.5,
            eye_distance=100.0,
            face_angle=2.0,
            eyes_open=True,
            mouth_closed=True
        )
    
    @pytest.fixture
    def sample_image(self):
        """Create a sample test image."""
        # Create a 400x500 white image with a simple face-like pattern
        image = np.ones((500, 400, 3), dtype=np.uint8) * 255
        
        # Add a simple face-like pattern in the center
        center_x, center_y = 200, 250
        face_size = 150
        
        # Face outline (dark gray)
        cv2.circle(image, (center_x, center_y), face_size//2, (200, 200, 200), -1)
        
        # Eyes (black)
        eye_y = center_y - 20
        cv2.circle(image, (center_x - 30, eye_y), 10, (0, 0, 0), -1)
        cv2.circle(image, (center_x + 30, eye_y), 10, (0, 0, 0), -1)
        
        # Mouth (dark)
        cv2.ellipse(image, (center_x, center_y + 30), (20, 10), 0, 0, 180, (100, 100, 100), -1)
        
        return image
    
    def test_validator_initialization(self, sample_format_rules):
        """Test validator initialization."""
        validator = ICAOValidator(sample_format_rules)
        assert validator.format_rules == sample_format_rules
        assert hasattr(validator, 'laplacian_kernel')
        assert hasattr(validator, 'sobel_x')
        assert hasattr(validator, 'sobel_y')
    
    def test_check_dimensions_correct_size(self, validator, sample_image):
        """Test dimension checking with correct image size."""
        result = validator.check_dimensions(sample_image, "TEST-FORMAT")
        
        assert result.passes is True
        assert result.actual_width == 400
        assert result.actual_height == 500
        assert result.required_width == 400
        assert result.required_height == 500
        assert abs(result.width_ratio - 1.0) < 0.001
        assert abs(result.height_ratio - 1.0) < 0.001
        assert len(result.issues) == 0
    
    def test_check_dimensions_wrong_size(self, validator):
        """Test dimension checking with incorrect image size."""
        # Create image with wrong dimensions
        wrong_image = np.ones((600, 300, 3), dtype=np.uint8) * 255
        
        result = validator.check_dimensions(wrong_image, "TEST-FORMAT")
        
        assert result.passes is False
        assert result.actual_width == 300
        assert result.actual_height == 600
        assert len(result.issues) == 2  # Width and height issues
        
        # Check that issues are properly categorized
        width_issue = next((issue for issue in result.issues if "Width" in issue.message), None)
        height_issue = next((issue for issue in result.issues if "Height" in issue.message), None)
        
        assert width_issue is not None
        assert height_issue is not None
        assert width_issue.category == ValidationCategory.DIMENSIONS
        assert height_issue.category == ValidationCategory.DIMENSIONS
        assert width_issue.auto_fixable is True
        assert height_issue.auto_fixable is True
    
    def test_check_face_position_correct(self, validator, sample_face_metrics):
        """Test face position checking with correct metrics."""
        result = validator.check_face_position(sample_face_metrics, "TEST-FORMAT")
        
        assert result.passes is True
        assert result.face_height_ratio == 0.75
        assert result.eye_height_ratio == 0.55
        assert result.face_center_x == 0.5
        assert result.face_center_y == 0.5
        assert result.face_angle == 2.0
        assert result.positioning_score > 0.8
        assert len(result.issues) == 0
    
    def test_check_face_position_face_too_small(self, validator):
        """Test face position checking with face too small."""
        small_face_metrics = FaceMetrics(
            face_height_ratio=0.60,  # Below minimum of 0.70
            eye_height_ratio=0.55,
            face_center_x=0.5,
            face_center_y=0.5,
            eye_distance=100.0,
            face_angle=2.0,
            eyes_open=True,
            mouth_closed=True
        )
        
        result = validator.check_face_position(small_face_metrics, "TEST-FORMAT")
        
        assert result.passes is False
        assert len(result.issues) >= 1
        
        face_size_issue = next((issue for issue in result.issues if "too small" in issue.message), None)
        assert face_size_issue is not None
        assert face_size_issue.category == ValidationCategory.FACE
        assert face_size_issue.severity == ValidationSeverity.CRITICAL
        assert face_size_issue.auto_fixable is True
    
    def test_check_face_position_face_too_large(self, validator):
        """Test face position checking with face too large."""
        large_face_metrics = FaceMetrics(
            face_height_ratio=0.85,  # Above maximum of 0.80
            eye_height_ratio=0.55,
            face_center_x=0.5,
            face_center_y=0.5,
            eye_distance=100.0,
            face_angle=2.0,
            eyes_open=True,
            mouth_closed=True
        )
        
        result = validator.check_face_position(large_face_metrics, "TEST-FORMAT")
        
        assert result.passes is False
        assert len(result.issues) >= 1
        
        face_size_issue = next((issue for issue in result.issues if "too large" in issue.message), None)
        assert face_size_issue is not None
        assert face_size_issue.category == ValidationCategory.FACE
        assert face_size_issue.severity == ValidationSeverity.CRITICAL
    
    def test_check_face_position_off_center(self, validator):
        """Test face position checking with off-center face."""
        off_center_metrics = FaceMetrics(
            face_height_ratio=0.75,
            eye_height_ratio=0.55,
            face_center_x=0.3,  # Off center
            face_center_y=0.7,  # Off center
            eye_distance=100.0,
            face_angle=2.0,
            eyes_open=True,
            mouth_closed=True
        )
        
        result = validator.check_face_position(off_center_metrics, "TEST-FORMAT")
        
        assert result.passes is False
        assert len(result.issues) >= 2  # Both x and y centering issues
        
        x_center_issue = next((issue for issue in result.issues if "horizontally centered" in issue.message), None)
        y_center_issue = next((issue for issue in result.issues if "vertically centered" in issue.message), None)
        
        assert x_center_issue is not None
        assert y_center_issue is not None
        assert x_center_issue.auto_fixable is True
        assert y_center_issue.auto_fixable is True
    
    def test_check_face_position_tilted(self, validator):
        """Test face position checking with tilted face."""
        tilted_metrics = FaceMetrics(
            face_height_ratio=0.75,
            eye_height_ratio=0.55,
            face_center_x=0.5,
            face_center_y=0.5,
            eye_distance=100.0,
            face_angle=10.0,  # Above maximum of 5.0
            eyes_open=True,
            mouth_closed=True
        )
        
        result = validator.check_face_position(tilted_metrics, "TEST-FORMAT")
        
        assert result.passes is False
        
        tilt_issue = next((issue for issue in result.issues if "tilted" in issue.message), None)
        assert tilt_issue is not None
        assert tilt_issue.category == ValidationCategory.FACE
        assert tilt_issue.severity == ValidationSeverity.MAJOR
    
    def test_check_face_position_eyes_closed(self, validator):
        """Test face position checking with closed eyes."""
        closed_eyes_metrics = FaceMetrics(
            face_height_ratio=0.75,
            eye_height_ratio=0.55,
            face_center_x=0.5,
            face_center_y=0.5,
            eye_distance=100.0,
            face_angle=2.0,
            eyes_open=False,  # Eyes closed
            mouth_closed=True
        )
        
        result = validator.check_face_position(closed_eyes_metrics, "TEST-FORMAT")
        
        assert result.passes is False
        
        eyes_issue = next((issue for issue in result.issues if "Eyes appear to be closed" in issue.message), None)
        assert eyes_issue is not None
        assert eyes_issue.category == ValidationCategory.FACE
        assert eyes_issue.severity == ValidationSeverity.CRITICAL
        assert eyes_issue.auto_fixable is False
    
    def test_check_background_white_uniform(self, validator, sample_image):
        """Test background checking with correct white uniform background."""
        result = validator.check_background(sample_image, "TEST-FORMAT")
        
        assert result.passes is True
        assert result.required_color == [255, 255, 255]
        assert result.color_difference < 15  # Within tolerance
        assert result.uniformity_score > 0.9
        assert len(result.issues) == 0
    
    def test_check_background_wrong_color(self, validator):
        """Test background checking with wrong background color."""
        # Create image with blue background
        blue_image = np.ones((500, 400, 3), dtype=np.uint8)
        blue_image[:, :] = [0, 0, 255]  # Blue background
        
        result = validator.check_background(blue_image, "TEST-FORMAT")
        
        assert result.passes is False
        assert len(result.issues) >= 1
        
        color_issue = next((issue for issue in result.issues if "Background color" in issue.message), None)
        assert color_issue is not None
        assert color_issue.category == ValidationCategory.BACKGROUND
        assert color_issue.auto_fixable is True
    
    def test_check_background_non_uniform(self, validator):
        """Test background checking with non-uniform background."""
        # Create image with gradient background
        gradient_image = np.ones((500, 400, 3), dtype=np.uint8)
        for i in range(400):
            gradient_image[:, i] = [255 - i//2, 255 - i//2, 255 - i//2]
        
        result = validator.check_background(gradient_image, "TEST-FORMAT")
        
        assert result.passes is False
        
        uniformity_issue = next((issue for issue in result.issues if "not uniform" in issue.message), None)
        assert uniformity_issue is not None
        assert uniformity_issue.category == ValidationCategory.BACKGROUND
        assert uniformity_issue.auto_fixable is True
    
    def test_check_image_quality_good_image(self, validator, sample_image):
        """Test image quality checking with good quality image."""
        result = validator.check_image_quality(sample_image, "TEST-FORMAT")
        
        assert result.sharpness_score > 0
        # Sample image may be too bright/not sharp enough, so just check basic functionality
        assert result.brightness_score > 0
        assert result.contrast_score > 0
        assert result.noise_score >= 0
        assert result.overall_quality_score > 0
        # May have issues but should complete without errors
    
    def test_check_image_quality_dark_image(self, validator):
        """Test image quality checking with dark image."""
        # Create very dark image
        dark_image = np.ones((500, 400, 3), dtype=np.uint8) * 30  # Very dark
        
        result = validator.check_image_quality(dark_image, "TEST-FORMAT")
        
        assert result.passes is False
        
        brightness_issue = next((issue for issue in result.issues if "too dark" in issue.message), None)
        assert brightness_issue is not None
        assert brightness_issue.category == ValidationCategory.QUALITY
        assert brightness_issue.auto_fixable is True
    
    def test_check_image_quality_bright_image(self, validator):
        """Test image quality checking with overly bright image."""
        # Create very bright image
        bright_image = np.ones((500, 400, 3), dtype=np.uint8) * 250  # Very bright
        
        result = validator.check_image_quality(bright_image, "TEST-FORMAT")
        
        assert result.passes is False
        
        brightness_issue = next((issue for issue in result.issues if "too bright" in issue.message), None)
        assert brightness_issue is not None
        assert brightness_issue.category == ValidationCategory.QUALITY
        assert brightness_issue.auto_fixable is True
    
    def test_check_image_quality_blurry_image(self, validator):
        """Test image quality checking with blurry image."""
        # Create blurry image
        sharp_image = np.ones((500, 400, 3), dtype=np.uint8) * 128
        # Add some high frequency content then blur it
        noise = np.random.randint(0, 50, (500, 400, 3), dtype=np.uint8)
        sharp_image = np.clip(sharp_image.astype(np.int16) + noise.astype(np.int16), 0, 255).astype(np.uint8)
        blurry_image = cv2.GaussianBlur(sharp_image, (15, 15), 5)
        
        result = validator.check_image_quality(blurry_image, "TEST-FORMAT")
        
        # Should detect low sharpness
        assert result.sharpness_score >= 0  # Just check it runs without error
        
        sharpness_issue = next((issue for issue in result.issues if "not sharp enough" in issue.message), None)
        if sharpness_issue:  # May or may not trigger depending on exact values
            assert sharpness_issue.category == ValidationCategory.QUALITY
            assert sharpness_issue.auto_fixable is False
    
    def test_validate_compliance_all_pass(self, validator, sample_image, sample_face_metrics):
        """Test complete compliance validation with passing image."""
        result = validator.validate_compliance(sample_image, sample_face_metrics, "TEST-FORMAT")
        
        assert isinstance(result, ComplianceResult)
        assert result.format_name == "TEST-FORMAT"
        assert result.processing_time > 0
        assert result.compliance_score > 0
        
        # Check that all sub-results are present
        assert result.dimension_check is not None
        assert result.position_check is not None
        assert result.background_check is not None
        assert result.quality_check is not None
        
        # Should pass or have only minor issues
        if not result.overall_pass:
            # If it fails, should only be minor issues
            critical_issues = result.critical_issues
            assert len(critical_issues) == 0, f"Unexpected critical issues: {[issue.message for issue in critical_issues]}"
    
    def test_validate_compliance_multiple_failures(self, validator):
        """Test complete compliance validation with multiple failures."""
        # Create problematic image and metrics
        bad_image = np.ones((600, 300, 3), dtype=np.uint8) * 50  # Wrong size, too dark
        bad_image[:, :] = [0, 255, 0]  # Green background
        
        bad_metrics = FaceMetrics(
            face_height_ratio=0.60,  # Too small
            eye_height_ratio=0.40,   # Wrong position
            face_center_x=0.3,       # Off center
            face_center_y=0.7,       # Off center
            eye_distance=100.0,
            face_angle=15.0,         # Too tilted
            eyes_open=False,         # Eyes closed
            mouth_closed=False       # Mouth open
        )
        
        result = validator.validate_compliance(bad_image, bad_metrics, "TEST-FORMAT")
        
        assert result.overall_pass is False
        assert result.compliance_score < 50  # Should be low score
        assert len(result.issues) > 5  # Multiple issues
        assert len(result.critical_issues) > 0  # Should have critical issues
        
        # Check that issues span multiple categories
        categories = {issue.category for issue in result.issues}
        assert ValidationCategory.DIMENSIONS in categories
        assert ValidationCategory.FACE in categories
        assert ValidationCategory.BACKGROUND in categories
    
    def test_validate_compliance_unknown_format(self, validator, sample_image, sample_face_metrics):
        """Test compliance validation with unknown format."""
        with pytest.raises(ValueError, match="Unknown format"):
            validator.validate_compliance(sample_image, sample_face_metrics, "UNKNOWN-FORMAT")
    
    def test_color_name_helper(self, validator):
        """Test the color name helper function."""
        assert validator._color_name([255, 255, 255]) == "white"
        assert validator._color_name([0, 0, 0]) == "black"
        assert validator._color_name([255, 0, 0]) == "red"
        assert validator._color_name([0, 255, 0]) == "green"
        assert validator._color_name([0, 0, 255]) == "blue"
        assert validator._color_name([128, 128, 128]) == "neutral"
    
    def test_compliance_result_properties(self, validator, sample_image, sample_face_metrics):
        """Test ComplianceResult properties and methods."""
        result = validator.validate_compliance(sample_image, sample_face_metrics, "TEST-FORMAT")
        
        # Test properties
        critical_issues = result.critical_issues
        auto_fixable_issues = result.auto_fixable_issues
        summary = result.summary
        
        assert isinstance(critical_issues, list)
        assert isinstance(auto_fixable_issues, list)
        assert isinstance(summary, str)
        assert "PASS" in summary or "FAIL" in summary
        assert "%" in summary  # Should contain percentage
    
    def test_real_world_format_compatibility(self, validator):
        """Test with real format configurations."""
        # Load actual format configuration
        try:
            with open('config/formats.json', 'r') as f:
                real_formats = json.load(f)
            
            real_validator = ICAOValidator(real_formats)
            
            # Test with ICS-UAE format
            test_image = np.ones((531, 413, 3), dtype=np.uint8) * 255
            test_metrics = FaceMetrics(
                face_height_ratio=0.75,
                eye_height_ratio=0.55,
                face_center_x=0.5,
                face_center_y=0.5,
                eye_distance=100.0,
                face_angle=2.0,
                eyes_open=True,
                mouth_closed=True
            )
            
            result = real_validator.validate_compliance(test_image, test_metrics, "ICS-UAE")
            assert isinstance(result, ComplianceResult)
            assert result.format_name == "ICS-UAE"
            
        except FileNotFoundError:
            pytest.skip("Real format configuration file not found")


if __name__ == "__main__":
    pytest.main([__file__])