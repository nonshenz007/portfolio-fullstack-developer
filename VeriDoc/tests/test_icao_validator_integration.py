"""
Integration tests for ICAO validator with real-world scenarios.
"""
import pytest
import numpy as np
import cv2
import json
import os
from pathlib import Path

from validation.icao_validator import ICAOValidator
from validation.validation_models import ValidationSeverity, ValidationCategory
from detection.data_models import FaceMetrics


class TestICAOValidatorIntegration:
    """Integration tests for ICAO validator with realistic scenarios."""
    
    @pytest.fixture
    def real_format_rules(self):
        """Load real format rules from config file."""
        config_path = Path("config/formats.json")
        if not config_path.exists():
            pytest.skip("Format configuration file not found")
        
        with open(config_path, 'r') as f:
            return json.load(f)
    
    @pytest.fixture
    def validator(self, real_format_rules):
        """Create validator with real format rules."""
        return ICAOValidator(real_format_rules)
    
    def create_realistic_passport_photo(self, width=413, height=531, background_color=(255, 255, 255)):
        """Create a realistic passport photo for testing."""
        image = np.full((height, width, 3), background_color, dtype=np.uint8)
        
        # Add realistic face
        center_x, center_y = width // 2, int(height * 0.55)  # Face slightly above center
        face_width = int(width * 0.4)
        face_height = int(height * 0.35)
        
        # Face oval (skin tone)
        skin_color = (220, 180, 140)
        cv2.ellipse(image, (center_x, center_y), (face_width//2, face_height//2), 
                   0, 0, 360, skin_color, -1)
        
        # Eyes
        eye_y = center_y - face_height//6
        eye_spacing = face_width//4
        cv2.circle(image, (center_x - eye_spacing, eye_y), 8, (50, 50, 50), -1)  # Left eye
        cv2.circle(image, (center_x + eye_spacing, eye_y), 8, (50, 50, 50), -1)  # Right eye
        cv2.circle(image, (center_x - eye_spacing, eye_y), 3, (0, 0, 0), -1)    # Left pupil
        cv2.circle(image, (center_x + eye_spacing, eye_y), 3, (0, 0, 0), -1)    # Right pupil
        
        # Nose
        nose_y = center_y
        cv2.ellipse(image, (center_x, nose_y), (6, 12), 0, 0, 360, (200, 160, 120), -1)
        
        # Mouth
        mouth_y = center_y + face_height//4
        cv2.ellipse(image, (center_x, mouth_y), (15, 5), 0, 0, 360, (180, 120, 100), -1)
        
        # Hair
        hair_color = (80, 60, 40)
        cv2.ellipse(image, (center_x, center_y - face_height//3), 
                   (face_width//2 + 10, face_height//3), 0, 180, 360, hair_color, -1)
        
        return image
    
    def create_face_metrics_from_image(self, image, face_center_x_ratio=0.5, face_center_y_ratio=0.55):
        """Create realistic face metrics based on image dimensions."""
        height, width = image.shape[:2]
        
        # Calculate face dimensions (approximate)
        face_height = int(height * 0.35)  # Face takes up ~35% of image height
        eye_level = int(height * face_center_y_ratio - face_height * 0.15)  # Eyes slightly above face center
        
        return FaceMetrics(
            face_height_ratio=face_height / height,
            eye_height_ratio=eye_level / height,
            face_center_x=face_center_x_ratio,
            face_center_y=face_center_y_ratio,
            eye_distance=width * 0.15,  # Approximate eye distance
            face_angle=0.0,
            eyes_open=True,
            mouth_closed=True
        )
    
    def test_ics_uae_compliant_photo(self, validator):
        """Test with a compliant ICS-UAE photo."""
        # Create ICS-UAE compliant image
        image = self.create_realistic_passport_photo(413, 531, (255, 255, 255))
        face_metrics = self.create_face_metrics_from_image(image)
        
        result = validator.validate_compliance(image, face_metrics, "ICS-UAE")
        
        assert result.format_name == "ICS-UAE"
        assert result.compliance_score > 60  # Synthetic image may have some issues
        assert result.dimension_check.passes is True
        assert result.background_check.passes is True
        
        # Print results for debugging
        print(f"\nICS-UAE Compliant Test Results:")
        print(f"Overall Pass: {result.overall_pass}")
        print(f"Compliance Score: {result.compliance_score:.1f}%")
        print(f"Issues: {len(result.issues)}")
        for issue in result.issues:
            print(f"  - {issue.severity.value}: {issue.message}")
    
    def test_us_visa_compliant_photo(self, validator):
        """Test with a compliant US Visa photo."""
        # Create US Visa compliant image (square format)
        image = self.create_realistic_passport_photo(600, 600, (255, 255, 255))
        face_metrics = self.create_face_metrics_from_image(image, 0.5, 0.5)
        
        result = validator.validate_compliance(image, face_metrics, "US-Visa")
        
        assert result.format_name == "US-Visa"
        assert result.compliance_score > 60  # Synthetic image may have some issues
        assert result.dimension_check.passes is True
        assert result.background_check.passes is True
        
        print(f"\nUS Visa Compliant Test Results:")
        print(f"Overall Pass: {result.overall_pass}")
        print(f"Compliance Score: {result.compliance_score:.1f}%")
        print(f"Issues: {len(result.issues)}")
        for issue in result.issues:
            print(f"  - {issue.severity.value}: {issue.message}")
    
    def test_common_photo_problems(self, validator):
        """Test detection of common photo problems."""
        test_cases = [
            {
                "name": "Wrong background color",
                "image_params": {"background_color": (0, 0, 255)},  # Blue background
                "expected_issues": [ValidationCategory.BACKGROUND]
            },
            {
                "name": "Face too small",
                "face_params": {"face_center_y_ratio": 0.7},  # Face positioned lower
                "expected_issues": [ValidationCategory.FACE]
            },
            {
                "name": "Off-center face",
                "face_params": {"face_center_x_ratio": 0.3},  # Face to the left
                "expected_issues": [ValidationCategory.FACE]
            },
            {
                "name": "Wrong dimensions",
                "image_size": (400, 400),  # Wrong size for ICS-UAE
                "expected_issues": [ValidationCategory.DIMENSIONS]
            }
        ]
        
        for test_case in test_cases:
            print(f"\nTesting: {test_case['name']}")
            
            # Create image with specified parameters
            image_params = test_case.get("image_params", {})
            image_size = test_case.get("image_size", (413, 531))
            
            image = self.create_realistic_passport_photo(
                width=image_size[1], 
                height=image_size[0], 
                **image_params
            )
            
            # Create face metrics with specified parameters
            face_params = test_case.get("face_params", {})
            face_metrics = self.create_face_metrics_from_image(image, **face_params)
            
            result = validator.validate_compliance(image, face_metrics, "ICS-UAE")
            
            # Check that expected issue categories are present
            found_categories = {issue.category for issue in result.issues}
            expected_categories = set(test_case["expected_issues"])
            
            assert len(expected_categories.intersection(found_categories)) > 0, \
                f"Expected issues in categories {expected_categories}, but found {found_categories}"
            
            print(f"  Issues found: {len(result.issues)}")
            for issue in result.issues:
                print(f"    - {issue.category.value}: {issue.message}")
    
    def test_edge_case_dimensions(self, validator):
        """Test edge cases for dimension validation."""
        test_cases = [
            {"size": (531, 413), "name": "Swapped dimensions"},
            {"size": (100, 100), "name": "Too small"},
            {"size": (2000, 2000), "name": "Too large"},
            {"size": (413, 500), "name": "Close but wrong height"},
            {"size": (400, 531), "name": "Close but wrong width"},
        ]
        
        face_metrics = FaceMetrics(
            face_height_ratio=0.75,
            eye_height_ratio=0.55,
            face_center_x=0.5,
            face_center_y=0.5,
            eye_distance=100.0,
            face_angle=0.0,
            eyes_open=True,
            mouth_closed=True
        )
        
        for test_case in test_cases:
            print(f"\nTesting dimension edge case: {test_case['name']}")
            
            height, width = test_case["size"]
            image = np.ones((height, width, 3), dtype=np.uint8) * 255
            
            result = validator.validate_compliance(image, face_metrics, "ICS-UAE")
            
            print(f"  Dimension check passes: {result.dimension_check.passes}")
            print(f"  Width ratio: {result.dimension_check.width_ratio:.3f}")
            print(f"  Height ratio: {result.dimension_check.height_ratio:.3f}")
            
            if not result.dimension_check.passes:
                dimension_issues = [issue for issue in result.issues 
                                  if issue.category == ValidationCategory.DIMENSIONS]
                print(f"  Dimension issues: {len(dimension_issues)}")
                for issue in dimension_issues:
                    print(f"    - {issue.message}")
    
    def test_quality_variations(self, validator):
        """Test image quality detection with various quality levels."""
        base_image = self.create_realistic_passport_photo()
        face_metrics = self.create_face_metrics_from_image(base_image)
        
        quality_tests = [
            {
                "name": "Original quality",
                "transform": lambda img: img,
            },
            {
                "name": "Blurred image",
                "transform": lambda img: cv2.GaussianBlur(img, (15, 15), 5),
            },
            {
                "name": "Dark image",
                "transform": lambda img: (img * 0.3).astype(np.uint8),
            },
            {
                "name": "Bright image",
                "transform": lambda img: np.clip(img * 1.5, 0, 255).astype(np.uint8),
            },
            {
                "name": "Noisy image",
                "transform": lambda img: np.clip(
                    img + np.random.normal(0, 20, img.shape), 0, 255
                ).astype(np.uint8),
            },
            {
                "name": "Low contrast",
                "transform": lambda img: np.clip(
                    (img - 128) * 0.3 + 128, 0, 255
                ).astype(np.uint8),
            }
        ]
        
        for test in quality_tests:
            print(f"\nTesting quality: {test['name']}")
            
            test_image = test["transform"](base_image.copy())
            result = validator.validate_compliance(test_image, face_metrics, "ICS-UAE")
            
            quality_result = result.quality_check
            print(f"  Quality passes: {quality_result.passes}")
            print(f"  Sharpness: {quality_result.sharpness_score:.1f}")
            print(f"  Brightness: {quality_result.brightness_score:.1f}")
            print(f"  Contrast: {quality_result.contrast_score:.1f}")
            print(f"  Noise: {quality_result.noise_score:.3f}")
            print(f"  Overall quality: {quality_result.overall_quality_score:.3f}")
            
            quality_issues = [issue for issue in result.issues 
                            if issue.category == ValidationCategory.QUALITY]
            if quality_issues:
                print(f"  Quality issues: {len(quality_issues)}")
                for issue in quality_issues:
                    print(f"    - {issue.severity.value}: {issue.message}")
    
    def test_background_variations(self, validator):
        """Test background detection with various background types."""
        face_metrics = self.create_face_metrics_from_image(
            np.ones((531, 413, 3), dtype=np.uint8)
        )
        
        background_tests = [
            {
                "name": "Pure white",
                "color": (255, 255, 255),
                "should_pass": True
            },
            {
                "name": "Off-white",
                "color": (250, 250, 250),
                "should_pass": True
            },
            {
                "name": "Light gray",
                "color": (240, 240, 240),
                "should_pass": False
            },
            {
                "name": "Blue background",
                "color": (0, 0, 255),
                "should_pass": False
            },
            {
                "name": "Red background",
                "color": (255, 0, 0),
                "should_pass": False
            }
        ]
        
        for test in background_tests:
            print(f"\nTesting background: {test['name']}")
            
            image = self.create_realistic_passport_photo(
                background_color=test["color"]
            )
            
            result = validator.validate_compliance(image, face_metrics, "ICS-UAE")
            
            bg_result = result.background_check
            print(f"  Background passes: {bg_result.passes}")
            print(f"  Dominant color: {bg_result.dominant_color}")
            print(f"  Required color: {bg_result.required_color}")
            print(f"  Color difference: {bg_result.color_difference:.1f}")
            print(f"  Uniformity: {bg_result.uniformity_score:.3f}")
            
            if test["should_pass"]:
                # Should pass or have only minor background issues
                bg_issues = [issue for issue in result.issues 
                           if issue.category == ValidationCategory.BACKGROUND]
                critical_bg_issues = [issue for issue in bg_issues 
                                    if issue.severity == ValidationSeverity.CRITICAL]
                assert len(critical_bg_issues) == 0, \
                    f"Expected {test['name']} to pass, but got critical issues: {[i.message for i in critical_bg_issues]}"
            else:
                # Should have background issues
                bg_issues = [issue for issue in result.issues 
                           if issue.category == ValidationCategory.BACKGROUND]
                assert len(bg_issues) > 0, \
                    f"Expected {test['name']} to fail, but no background issues found"
    
    def test_performance_benchmarks(self, validator):
        """Test validation performance with various image sizes."""
        import time
        
        face_metrics = FaceMetrics(
            face_height_ratio=0.75,
            eye_height_ratio=0.55,
            face_center_x=0.5,
            face_center_y=0.5,
            eye_distance=100.0,
            face_angle=0.0,
            eyes_open=True,
            mouth_closed=True
        )
        
        size_tests = [
            {"size": (531, 413), "name": "Standard ICS-UAE"},
            {"size": (600, 600), "name": "Standard US Visa"},
            {"size": (1062, 826), "name": "2x ICS-UAE"},
            {"size": (2124, 1652), "name": "4x ICS-UAE"},
        ]
        
        print("\nPerformance Benchmarks:")
        print("Size\t\tTime (ms)\tScore")
        print("-" * 40)
        
        for test in size_tests:
            height, width = test["size"]
            image = np.ones((height, width, 3), dtype=np.uint8) * 255
            
            # Warm up
            validator.validate_compliance(image, face_metrics, "ICS-UAE")
            
            # Benchmark
            start_time = time.time()
            result = validator.validate_compliance(image, face_metrics, "ICS-UAE")
            end_time = time.time()
            
            processing_time_ms = (end_time - start_time) * 1000
            
            print(f"{test['name']:<15}\t{processing_time_ms:.1f}\t\t{result.compliance_score:.1f}%")
            
            # Ensure processing time is reasonable (under 5 seconds as per requirements)
            assert processing_time_ms < 5000, \
                f"Processing time {processing_time_ms:.1f}ms exceeds 5 second requirement"
    
    def test_batch_validation_consistency(self, validator):
        """Test that validation results are consistent across multiple runs."""
        image = self.create_realistic_passport_photo()
        face_metrics = self.create_face_metrics_from_image(image)
        
        # Run validation multiple times
        results = []
        for i in range(5):
            result = validator.validate_compliance(image, face_metrics, "ICS-UAE")
            results.append(result)
        
        # Check consistency
        first_result = results[0]
        for i, result in enumerate(results[1:], 1):
            assert result.overall_pass == first_result.overall_pass, \
                f"Run {i+1} overall_pass differs from first run"
            
            assert abs(result.compliance_score - first_result.compliance_score) < 0.1, \
                f"Run {i+1} compliance_score differs significantly from first run"
            
            assert len(result.issues) == len(first_result.issues), \
                f"Run {i+1} has different number of issues than first run"
        
        print(f"\nConsistency test passed: {len(results)} runs produced identical results")
        print(f"Compliance score: {first_result.compliance_score:.1f}%")
        print(f"Issues: {len(first_result.issues)}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])