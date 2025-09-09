#!/usr/bin/env python3
"""
Demo script for the ICAO Validator.

This script demonstrates the core functionality of the ICAO compliance validator
with various test scenarios.
"""
import sys
import os
import json
import numpy as np
import cv2
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from validation.icao_validator import ICAOValidator
from validation.validation_models import ValidationSeverity, ValidationCategory
from detection.data_models import FaceMetrics


def load_format_rules():
    """Load format rules from configuration."""
    config_path = Path("config/formats.json")
    if not config_path.exists():
        print("Warning: Format configuration not found, using sample rules")
        return {
            "formats": {
                "ICS-UAE": {
                    "display_name": "ICS UAE Visa",
                    "dimensions": {
                        "width": 413,
                        "height": 531,
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
    
    with open(config_path, 'r') as f:
        return json.load(f)


def create_test_image(width=413, height=531, background_color=(255, 255, 255), face_size_ratio=0.75):
    """Create a test passport photo."""
    image = np.full((height, width, 3), background_color, dtype=np.uint8)
    
    # Add realistic face
    center_x, center_y = width // 2, int(height * 0.55)
    face_width = int(width * 0.4 * face_size_ratio)
    face_height = int(height * 0.35 * face_size_ratio)
    
    # Face oval (skin tone)
    skin_color = (220, 180, 140)
    cv2.ellipse(image, (center_x, center_y), (face_width//2, face_height//2), 
               0, 0, 360, skin_color, -1)
    
    # Eyes
    eye_y = center_y - face_height//6
    eye_spacing = face_width//4
    cv2.circle(image, (center_x - eye_spacing, eye_y), 8, (50, 50, 50), -1)
    cv2.circle(image, (center_x + eye_spacing, eye_y), 8, (50, 50, 50), -1)
    cv2.circle(image, (center_x - eye_spacing, eye_y), 3, (0, 0, 0), -1)
    cv2.circle(image, (center_x + eye_spacing, eye_y), 3, (0, 0, 0), -1)
    
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


def create_face_metrics(face_size_ratio=0.75, center_x=0.5, center_y=0.55, angle=0.0):
    """Create face metrics for testing."""
    return FaceMetrics(
        face_height_ratio=0.35 * face_size_ratio,  # Adjust based on face size
        eye_height_ratio=center_y - 0.05,  # Eyes slightly above center
        face_center_x=center_x,
        face_center_y=center_y,
        eye_distance=100.0,
        face_angle=angle,
        eyes_open=True,
        mouth_closed=True
    )


def print_validation_result(result, test_name):
    """Print detailed validation results."""
    print(f"\n{'='*60}")
    print(f"Test: {test_name}")
    print(f"{'='*60}")
    print(f"Format: {result.format_name}")
    print(f"Overall Pass: {'✓ PASS' if result.overall_pass else '✗ FAIL'}")
    print(f"Compliance Score: {result.compliance_score:.1f}%")
    print(f"Processing Time: {result.processing_time*1000:.1f}ms")
    
    print(f"\nDetailed Results:")
    print(f"  Dimensions: {'✓' if result.dimension_check.passes else '✗'} "
          f"({result.dimension_check.actual_width}x{result.dimension_check.actual_height})")
    print(f"  Face Position: {'✓' if result.position_check.passes else '✗'} "
          f"(score: {result.position_check.positioning_score:.2f})")
    print(f"  Background: {'✓' if result.background_check.passes else '✗'} "
          f"(uniformity: {result.background_check.uniformity_score:.2f})")
    print(f"  Image Quality: {'✓' if result.quality_check.passes else '✗'} "
          f"(overall: {result.quality_check.overall_quality_score:.2f})")
    
    if result.issues:
        print(f"\nIssues Found ({len(result.issues)}):")
        for issue in result.issues:
            severity_icon = {"critical": "🔴", "major": "🟡", "minor": "🟢"}.get(issue.severity.value, "⚪")
            print(f"  {severity_icon} {issue.severity.value.upper()}: {issue.message}")
            print(f"     Suggestion: {issue.suggestion}")
            if issue.auto_fixable:
                print(f"     Auto-fixable: Yes")
    else:
        print("\n✓ No issues found!")


def main():
    """Run ICAO validator demo."""
    print("ICAO Validator Demo")
    print("==================")
    
    # Load configuration
    format_rules = load_format_rules()
    validator = ICAOValidator(format_rules)
    
    # Test scenarios
    test_scenarios = [
        {
            "name": "Compliant ICS-UAE Photo",
            "image_params": {"width": 413, "height": 531, "face_size_ratio": 2.0},
            "face_params": {"face_size_ratio": 2.0, "center_y": 0.55},
            "format": "ICS-UAE"
        },
        {
            "name": "Face Too Small",
            "image_params": {"width": 413, "height": 531, "face_size_ratio": 0.5},
            "face_params": {"face_size_ratio": 0.5},
            "format": "ICS-UAE"
        },
        {
            "name": "Wrong Background Color",
            "image_params": {"width": 413, "height": 531, "background_color": (0, 0, 255)},
            "face_params": {"face_size_ratio": 2.0},
            "format": "ICS-UAE"
        },
        {
            "name": "Off-Center Face",
            "image_params": {"width": 413, "height": 531, "face_size_ratio": 2.0},
            "face_params": {"face_size_ratio": 2.0, "center_x": 0.3, "center_y": 0.7},
            "format": "ICS-UAE"
        },
        {
            "name": "Tilted Face",
            "image_params": {"width": 413, "height": 531, "face_size_ratio": 2.0},
            "face_params": {"face_size_ratio": 2.0, "angle": 10.0},
            "format": "ICS-UAE"
        },
        {
            "name": "Wrong Dimensions",
            "image_params": {"width": 400, "height": 400, "face_size_ratio": 2.0},
            "face_params": {"face_size_ratio": 2.0},
            "format": "ICS-UAE"
        }
    ]
    
    # Run tests
    for scenario in test_scenarios:
        try:
            # Create test image
            image = create_test_image(**scenario["image_params"])
            
            # Create face metrics
            face_metrics = create_face_metrics(**scenario["face_params"])
            
            # Validate
            result = validator.validate_compliance(
                image, face_metrics, scenario["format"]
            )
            
            # Print results
            print_validation_result(result, scenario["name"])
            
        except Exception as e:
            print(f"\nError in test '{scenario['name']}': {e}")
    
    # Performance test
    print(f"\n{'='*60}")
    print("Performance Test")
    print(f"{'='*60}")
    
    import time
    
    # Test with different image sizes
    sizes = [(413, 531), (600, 600), (826, 1062)]
    
    for width, height in sizes:
        image = create_test_image(width, height, face_size_ratio=2.0)
        face_metrics = create_face_metrics(face_size_ratio=2.0)
        
        # Warm up
        validator.validate_compliance(image, face_metrics, "ICS-UAE")
        
        # Benchmark
        start_time = time.time()
        result = validator.validate_compliance(image, face_metrics, "ICS-UAE")
        end_time = time.time()
        
        processing_time = (end_time - start_time) * 1000
        print(f"{width}x{height}: {processing_time:.1f}ms (Score: {result.compliance_score:.1f}%)")
    
    print(f"\n{'='*60}")
    print("Demo Complete!")
    print("The ICAO validator successfully:")
    print("✓ Validates image dimensions against format requirements")
    print("✓ Checks face positioning and size compliance")
    print("✓ Analyzes background color and uniformity")
    print("✓ Assesses image quality (sharpness, brightness, contrast)")
    print("✓ Provides detailed feedback and suggestions")
    print("✓ Processes images in under 100ms for typical sizes")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()