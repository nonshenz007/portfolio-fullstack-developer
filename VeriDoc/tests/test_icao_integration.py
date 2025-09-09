"""
Integration tests for ICAO Rules Engine
Tests the complete workflow from rule loading to validation
"""

import pytest
import tempfile
import os
import json
from pathlib import Path

from rules.icao_rules_engine import ICAORulesEngine, RuleSeverity
from rules.rule_validators import (
    ICAORuleValidators, 
    FaceFeatures, 
    ImageQualityMetrics, 
    LightingMetrics
)


class TestICAOIntegration:
    """Integration tests for complete ICAO validation workflow"""
    
    @pytest.fixture
    def temp_config_dir(self):
        """Create temporary config directory with ICAO rules"""
        temp_dir = tempfile.mkdtemp()
        
        # Copy the actual ICAO rules file to temp directory
        source_file = Path("config/icao_rules_2023.json")
        if source_file.exists():
            import shutil
            dest_file = Path(temp_dir) / "icao_rules_2023.json"
            shutil.copy2(source_file, dest_file)
        
        yield temp_dir
        
        # Cleanup
        import shutil
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def rules_engine(self, temp_config_dir):
        """Create rules engine with actual ICAO rules"""
        return ICAORulesEngine(rules_directory=temp_config_dir)
    
    @pytest.fixture
    def validators(self, rules_engine):
        """Create validators with rules engine"""
        return ICAORuleValidators(rules_engine)
    
    @pytest.fixture
    def compliant_face_features(self):
        """Face features that should pass all ICAO rules"""
        return FaceFeatures(
            eye_positions=((100, 150), (200, 150)),
            eye_openness=(0.9, 0.9),  # Eyes wide open
            mouth_position=(150, 200),
            mouth_openness=0.02,  # Mouth closed
            face_orientation=(0.0, 0.0, 0.0),  # Perfect frontal pose
            glasses_detected=False,  # No glasses
            glasses_confidence=0.0,
            glasses_type=None,
            head_covering_detected=False,  # No head covering
            head_covering_confidence=0.0,
            head_covering_type=None,
            face_visibility_ratio=1.0  # Full face visible
        )
    
    @pytest.fixture
    def high_quality_metrics(self):
        """Quality metrics that should pass all ICAO rules"""
        return ImageQualityMetrics(
            sharpness_laplacian=200.0,  # High sharpness
            sharpness_sobel=100.0,
            sharpness_fft=0.6,
            brightness_mean=140.0,  # Good brightness
            brightness_std=20.0,
            contrast_ratio=0.75,  # Good contrast
            color_cast_angle=3.0,  # Minimal color cast
            noise_level=0.02,  # Low noise
            compression_artifacts=0.01  # Minimal artifacts
        )
    
    @pytest.fixture
    def good_lighting_metrics(self):
        """Lighting metrics that should pass all ICAO rules"""
        return LightingMetrics(
            shadow_intensity=0.05,  # Minimal shadows
            highlight_intensity=0.05,
            lighting_uniformity=0.95,  # Very uniform
            flash_reflection_detected=False,
            flash_reflection_intensity=0.02,
            red_eye_detected=False,
            background_uniformity=0.98  # Very uniform background
        )
    
    def test_complete_validation_workflow(self, validators, compliant_face_features, 
                                        high_quality_metrics, good_lighting_metrics):
        """Test complete validation workflow with compliant inputs"""
        
        # Test glasses validation
        glasses_results = validators.validate_glasses_compliance(compliant_face_features)
        assert len(glasses_results) > 0
        
        # Most glasses rules should pass for compliant features
        passing_glasses = [r for r in glasses_results if r.passes]
        assert len(passing_glasses) >= len(glasses_results) // 2
        
        # Test expression validation
        expression_results = validators.validate_expression_compliance(compliant_face_features)
        assert len(expression_results) > 0
        
        # Most expression rules should pass
        passing_expression = [r for r in expression_results if r.passes]
        assert len(passing_expression) >= len(expression_results) // 2
        
        # Test quality validation
        quality_results = validators.validate_quality_compliance(high_quality_metrics)
        assert len(quality_results) > 0
        
        # Most quality rules should pass
        passing_quality = [r for r in quality_results if r.passes]
        assert len(passing_quality) >= len(quality_results) // 2
        
        # Test lighting validation
        lighting_results = validators.validate_lighting_compliance(good_lighting_metrics)
        
        # Collect all results
        all_results = glasses_results + expression_results + quality_results + lighting_results
        
        # Verify we have comprehensive validation
        assert len(all_results) > 0
        
        # Check that results have proper structure
        for result in all_results:
            assert hasattr(result, 'rule_id')
            assert hasattr(result, 'passes')
            assert hasattr(result, 'confidence')
            assert hasattr(result, 'severity')
            assert result.confidence >= 0.0
            assert result.confidence <= 1.0
    
    def test_non_compliant_validation(self, validators):
        """Test validation with non-compliant inputs"""
        
        # Create non-compliant face features
        non_compliant_features = FaceFeatures(
            eye_positions=((100, 150), (200, 150)),
            eye_openness=(0.3, 0.4),  # Eyes mostly closed
            mouth_position=(150, 200),
            mouth_openness=0.8,  # Mouth wide open
            face_orientation=(15.0, 20.0, 10.0),  # Head tilted significantly
            glasses_detected=True,
            glasses_confidence=0.9,
            glasses_type="heavy",  # Heavy frames
            head_covering_detected=True,
            head_covering_confidence=0.8,
            head_covering_type="non_religious",  # Non-religious covering
            face_visibility_ratio=0.6  # Partially obscured face
        )
        
        # Test validation
        results = validators.validate_expression_compliance(non_compliant_features)
        
        # Should have some failing results
        failing_results = [r for r in results if not r.passes]
        assert len(failing_results) > 0
        
        # Check that failing results have low confidence or specific issues
        for result in failing_results:
            assert result.confidence < 1.0 or "below minimum" in result.suggestion
    
    def test_country_variation_workflow(self, rules_engine, validators, compliant_face_features):
        """Test workflow with different country variations"""
        
        # Test with standard ICAO
        rules_engine.set_country_variation("standard_icao")
        standard_results = validators.validate_glasses_compliance(compliant_face_features)
        
        # Test with US strict variation (if available)
        available_variations = rules_engine.get_version_info()["available_variations"]
        if "us_strict" in available_variations:
            rules_engine.set_country_variation("us_strict")
            us_results = validators.validate_glasses_compliance(compliant_face_features)
            
            # Results should be similar but may have different requirements
            assert len(us_results) == len(standard_results)
    
    def test_rule_severity_filtering(self, rules_engine):
        """Test filtering rules by severity"""
        
        critical_rules = rules_engine.get_rules_by_severity(RuleSeverity.CRITICAL)
        major_rules = rules_engine.get_rules_by_severity(RuleSeverity.MAJOR)
        minor_rules = rules_engine.get_rules_by_severity(RuleSeverity.MINOR)
        
        # Should have rules in each category
        assert len(critical_rules) > 0
        assert len(major_rules) > 0
        
        # Verify severity is correctly set
        for rule in critical_rules:
            assert rule.severity == RuleSeverity.CRITICAL
        
        for rule in major_rules:
            assert rule.severity == RuleSeverity.MAJOR
    
    def test_comprehensive_rule_coverage(self, rules_engine):
        """Test that all major ICAO rule categories are covered"""
        
        all_rules = rules_engine.get_all_rules()
        rule_ids = [rule.rule_id for rule in all_rules]
        
        # Should have rules from major categories
        glasses_rules = [rid for rid in rule_ids if "3.2" in rid]  # Glasses section
        expression_rules = [rid for rid in rule_ids if "4.1" in rid or "4.2" in rid]  # Expression section
        quality_rules = [rid for rid in rule_ids if "5." in rid]  # Quality section
        lighting_rules = [rid for rid in rule_ids if "6." in rid]  # Lighting section
        
        assert len(glasses_rules) > 0, "Should have glasses rules"
        assert len(expression_rules) > 0, "Should have expression rules"
        assert len(quality_rules) > 0, "Should have quality rules"
        assert len(lighting_rules) > 0, "Should have lighting rules"
        
        # Verify all rules have proper regulation references
        for rule in all_rules:
            assert rule.regulation, f"Rule {rule.rule_id} missing regulation reference"
            assert "ICAO" in rule.regulation, f"Rule {rule.rule_id} should reference ICAO"
    
    def test_version_info_completeness(self, rules_engine):
        """Test that version information is complete"""
        
        version_info = rules_engine.get_version_info()
        
        # Should have all required fields
        required_fields = ['version', 'current_variation', 'available_variations', 'total_rules']
        for field in required_fields:
            assert field in version_info, f"Missing version info field: {field}"
        
        # Should have reasonable values
        assert version_info['total_rules'] > 10, "Should have substantial number of rules"
        assert len(version_info['available_variations']) > 0, "Should have available variations"


if __name__ == "__main__":
    pytest.main([__file__])