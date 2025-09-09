#!/usr/bin/env python3
"""
ICAO Rules Engine Demonstration
Shows how to use the ICAO Rules Engine for photo validation
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rules.icao_rules_engine import ICAORulesEngine, RuleSeverity
from rules.rule_validators import (
    ICAORuleValidators,
    FaceFeatures,
    ImageQualityMetrics,
    LightingMetrics
)


def main():
    """Demonstrate ICAO Rules Engine functionality"""
    
    print("=== ICAO Rules Engine Demonstration ===\n")
    
    # Initialize the rules engine
    print("1. Initializing ICAO Rules Engine...")
    try:
        rules_engine = ICAORulesEngine(rules_directory="config")
        print(f"✓ Loaded ICAO rules successfully")
        
        # Show version info
        version_info = rules_engine.get_version_info()
        print(f"   Version: {version_info['version']}")
        print(f"   Total rules: {version_info['total_rules']}")
        print(f"   Available variations: {', '.join(version_info['available_variations'])}")
        print()
        
    except Exception as e:
        print(f"✗ Failed to load ICAO rules: {e}")
        return
    
    # Show rule categories
    print("2. Available Rule Categories:")
    
    glasses_rules = rules_engine.get_glasses_rules()
    print(f"   • Glasses rules: {len(glasses_rules)}")
    for name, rule in glasses_rules.items():
        print(f"     - {rule.rule_id}: {rule.description}")
    
    expression_rules = rules_engine.get_expression_rules()
    print(f"   • Expression rules: {len(expression_rules)}")
    for name, rule in expression_rules.items():
        print(f"     - {rule.rule_id}: {rule.description}")
    
    quality_rules = rules_engine.get_photo_quality_rules()
    print(f"   • Quality rules: {len(quality_rules)}")
    for name, rule in quality_rules.items():
        print(f"     - {rule.rule_id}: {rule.description}")
    
    lighting_rules = rules_engine.get_style_lighting_rules()
    print(f"   • Lighting rules: {len(lighting_rules)}")
    for name, rule in lighting_rules.items():
        print(f"     - {rule.rule_id}: {rule.description}")
    
    print()
    
    # Demonstrate rule validation
    print("3. Rule Validation Examples:")
    
    # Test individual rule validation
    print("\n   Testing individual rules:")
    
    # Test tinted lenses rule (should fail)
    result = rules_engine.validate_rule_compliance("ICAO.3.2.1", 0.8)  # High detection confidence
    print(f"   • Tinted lenses (confidence 0.8): {'PASS' if result.passes else 'FAIL'}")
    print(f"     Suggestion: {result.suggestion}")
    
    # Test sharpness rule (should pass)
    result = rules_engine.validate_rule_compliance("ICAO.5.1.1", 150)  # Good sharpness
    print(f"   • Sharpness (value 150): {'PASS' if result.passes else 'FAIL'}")
    print(f"     Suggestion: {result.suggestion}")
    
    # Test sharpness rule (should fail)
    result = rules_engine.validate_rule_compliance("ICAO.5.1.1", 50)  # Poor sharpness
    print(f"   • Sharpness (value 50): {'PASS' if result.passes else 'FAIL'}")
    print(f"     Suggestion: {result.suggestion}")
    
    print()
    
    # Demonstrate comprehensive validation
    print("4. Comprehensive Validation Example:")
    
    # Create sample face features (compliant)
    compliant_features = FaceFeatures(
        eye_positions=((100, 150), (200, 150)),
        eye_openness=(0.9, 0.9),
        mouth_position=(150, 200),
        mouth_openness=0.02,
        face_orientation=(0.0, 0.0, 0.0),
        glasses_detected=False,
        glasses_confidence=0.0,
        glasses_type=None,
        head_covering_detected=False,
        head_covering_confidence=0.0,
        head_covering_type=None,
        face_visibility_ratio=1.0
    )
    
    # Create sample quality metrics (high quality)
    quality_metrics = ImageQualityMetrics(
        sharpness_laplacian=200.0,
        sharpness_sobel=100.0,
        sharpness_fft=0.6,
        brightness_mean=140.0,
        brightness_std=20.0,
        contrast_ratio=0.75,
        color_cast_angle=3.0,
        noise_level=0.02,
        compression_artifacts=0.01
    )
    
    # Initialize validators
    validators = ICAORuleValidators(rules_engine)
    
    # Run comprehensive validation
    print("\n   Validating compliant photo:")
    
    glasses_results = validators.validate_glasses_compliance(compliant_features)
    expression_results = validators.validate_expression_compliance(compliant_features)
    quality_results = validators.validate_quality_compliance(quality_metrics)
    
    all_results = glasses_results + expression_results + quality_results
    
    # Show results summary
    passing_results = [r for r in all_results if r.passes]
    failing_results = [r for r in all_results if not r.passes]
    
    print(f"   • Total rules checked: {len(all_results)}")
    print(f"   • Passing: {len(passing_results)}")
    print(f"   • Failing: {len(failing_results)}")
    
    if failing_results:
        print("\n   Failed rules:")
        for result in failing_results:
            print(f"     - {result.rule_id}: {result.suggestion}")
    
    # Show rules by severity
    print("\n5. Rules by Severity:")
    
    critical_rules = rules_engine.get_rules_by_severity(RuleSeverity.CRITICAL)
    major_rules = rules_engine.get_rules_by_severity(RuleSeverity.MAJOR)
    minor_rules = rules_engine.get_rules_by_severity(RuleSeverity.MINOR)
    
    print(f"   • Critical: {len(critical_rules)} rules")
    print(f"   • Major: {len(major_rules)} rules")
    print(f"   • Minor: {len(minor_rules)} rules")
    
    # Demonstrate country variations
    print("\n6. Country Variations:")
    
    available_variations = version_info['available_variations']
    print(f"   Available variations: {', '.join(available_variations)}")
    
    if "us_strict" in available_variations:
        print("\n   Testing US strict variation:")
        rules_engine.set_country_variation("us_strict")
        print(f"   Current variation: {rules_engine.current_variation}")
        
        # Reset to standard
        rules_engine.set_country_variation("standard_icao")
    
    print("\n=== Demonstration Complete ===")


if __name__ == "__main__":
    main()