"""
Unit tests for ICAO Rule Validators
Tests specialized validation methods for different rule categories
"""

import pytest
import numpy as np
from unittest.mock import Mock, patch

from rules.rule_validators import (
    ICAORuleValidators,
    FaceFeatures,
    ImageQualityMetrics,
    LightingMetrics,
    ValidationCategory
)
from rules.icao_rules_engine import ICAORulesEngine, RuleDefinition, RuleSeverity


class TestICAORuleValidators:
    """Test suite for ICAO Rule Validators"""
    
    @pytest.fixture
    def mock_rules_engine(self):
        """Mock rules engine for testing"""
        engine = Mock(spec=ICAORulesEngine)
        
        # Mock rule definitions
        glasses_rule = RuleDefinition(
            rule_id="ICAO.3.2.1",
            name="tinted_lenses",
            parameters={"allowed": False, "detection_threshold": 0.3},
            severity=RuleSeverity.CRITICAL,
            regulation="ICAO Doc 9303 Part 3 Section 3.2.1",
            description="Tinted lenses not permitted"
        )
        
        expression_rule = RuleDefinition(
            rule_id="ICAO.4.1.1",
            name="neutral_expression",
            parameters={"mouth_openness_max": 0.1},
            severity=RuleSeverity.MAJOR,
            regulation="ICAO Doc 9303 Part 4 Section 1.1",
            description="Neutral expression required"
        )
        
        quality_rule = RuleDefinition(
            rule_id="ICAO.5.1.1",
            name="sharpness",
            parameters={"min_laplacian_variance": 100},
            severity=RuleSeverity.MAJOR,
            regulation="ICAO Doc 9303 Part 5 Section 1.1",
            description="Photo must be sharp"
        )
        
        # Configure mock methods
        engine.get_glasses_rules.return_value = {"tinted_lenses": glasses_rule}
        engine.get_head_covering_rules.return_value = {}
        engine.get_expression_rules.return_value = {"neutral_expression": expression_rule}
        engine.get_photo_quality_rules.return_value = {"sharpness": quality_rule}
        engine.get_style_lighting_rules.return_value = {}
        
        return engine
    
    @pytest.fixture
    def validators(self, mock_rules_engine):
        """Create validators instance with mock engine"""
        return ICAORuleValidators(mock_rules_engine)
    
    @pytest.fixture
    def sample_face_features(self):
        """Sample face features for testing"""
        return FaceFeatures(
            eye_positions=((100, 150), (200, 150)),
            eye_openness=(0.8, 0.9),
            mouth_position=(150, 200),
            mouth_openness=0.05,
            face_orientation=(0.0, 2.0, 1.0),  # pitch, yaw, roll
            glasses_detected=True,
            glasses_confidence=0.7,
            glasses_type="prescription",
            head_covering_detected=False,
            head_covering_confidence=0.1,
            head_covering_type=None,
            face_visibility_ratio=0.95
        )
    
    @pytest.fixture
    def sample_quality_metrics(self):
        """Sample quality metrics for testing"""
        return ImageQualityMetrics(
            sharpness_laplacian=150.0,
            sharpness_sobel=75.0,
            sharpness_fft=0.4,
            brightness_mean=120.0,
            brightness_std=25.0,
            contrast_ratio=0.7,
            color_cast_angle=5.0,
            noise_level=0.05,
            compression_artifacts=0.02
        )
    
    @pytest.fixture
    def sample_lighting_metrics(self):
        """Sample lighting metrics for testing"""
        return LightingMetrics(
            shadow_intensity=0.15,
            highlight_intensity=0.1,
            lighting_uniformity=0.85,
            flash_reflection_detected=False,
            flash_reflection_intensity=0.05,
            red_eye_detected=False,
            background_uniformity=0.92
        )
    
    def test_validate_glasses_compliance(self, validators, sample_face_features, mock_rules_engine):
        """Test glasses compliance validation"""
        # Mock the validate_rule_compliance method
        mock_result = Mock()
        mock_result.passes = True
        mock_result.confidence = 0.8
        mock_rules_engine.validate_rule_compliance.return_value = mock_result
        
        results = validators.validate_glasses_compliance(sample_face_features)
        
        assert len(results) == 1
        assert results[0] == mock_result
        mock_rules_engine.validate_rule_compliance.assert_called()
    
    def test_validate_head_covering_compliance(self, validators, sample_face_features, mock_rules_engine):
        """Test head covering compliance validation"""
        results = validators.validate_head_covering_compliance(sample_face_features)
        
        # Should return empty list since no head covering rules in mock
        assert len(results) == 0
    
    def test_validate_expression_compliance(self, validators, sample_face_features, mock_rules_engine):
        """Test expression compliance validation"""
        mock_result = Mock()
        mock_result.passes = True
        mock_rules_engine.validate_rule_compliance.return_value = mock_result
        
        results = validators.validate_expression_compliance(sample_face_features)
        
        assert len(results) == 1
        assert results[0] == mock_result
    
    def test_validate_quality_compliance(self, validators, sample_quality_metrics, mock_rules_engine):
        """Test quality compliance validation"""
        mock_result = Mock()
        mock_result.passes = True
        mock_rules_engine.validate_rule_compliance.return_value = mock_result
        
        results = validators.validate_quality_compliance(sample_quality_metrics)
        
        assert len(results) == 1
        assert results[0] == mock_result
    
    def test_validate_lighting_compliance(self, validators, sample_lighting_metrics, mock_rules_engine):
        """Test lighting compliance validation"""
        results = validators.validate_lighting_compliance(sample_lighting_metrics)
        
        # Should return empty list since no lighting rules in mock
        assert len(results) == 0
    
    def test_validate_tinted_lenses(self, validators, sample_face_features, mock_rules_engine):
        """Test tinted lenses validation"""
        rule_def = Mock()
        rule_def.rule_id = "ICAO.3.2.1"
        rule_def.parameters = {"detection_threshold": 0.3}
        
        mock_result = Mock()
        mock_result.passes = False  # Tinted lenses detected
        mock_rules_engine.validate_rule_compliance.return_value = mock_result
        
        result = validators._validate_tinted_lenses(rule_def, sample_face_features)
        
        assert result == mock_result
        mock_rules_engine.validate_rule_compliance.assert_called_with(
            "ICAO.3.2.1", sample_face_features.glasses_confidence
        )
    
    def test_validate_heavy_frames(self, validators, sample_face_features, mock_rules_engine):
        """Test heavy frames validation"""
        rule_def = Mock()
        rule_def.rule_id = "ICAO.3.2.2"
        rule_def.parameters = {"max_frame_width_ratio": 0.15}
        
        # Test with heavy frames
        face_features_heavy = sample_face_features
        face_features_heavy.glasses_type = "heavy"
        
        mock_result = Mock()
        mock_result.passes = False
        mock_rules_engine.validate_rule_compliance.return_value = mock_result
        
        result = validators._validate_heavy_frames(rule_def, face_features_heavy)
        
        assert result == mock_result
        mock_rules_engine.validate_rule_compliance.assert_called_with(
            "ICAO.3.2.2", face_features_heavy.glasses_confidence
        )
    
    def test_validate_neutral_expression(self, validators, sample_face_features, mock_rules_engine):
        """Test neutral expression validation"""
        rule_def = Mock()
        rule_def.rule_id = "ICAO.4.1.1"
        rule_def.parameters = {"mouth_openness_max": 0.1}
        
        mock_result = Mock()
        mock_result.passes = True  # Mouth openness is 0.05, within limit
        mock_rules_engine.validate_rule_compliance.return_value = mock_result
        
        result = validators._validate_neutral_expression(rule_def, sample_face_features)
        
        assert result == mock_result
        mock_rules_engine.validate_rule_compliance.assert_called_with(
            "ICAO.4.1.1", sample_face_features.mouth_openness
        )
    
    def test_validate_direct_gaze(self, validators, sample_face_features, mock_rules_engine):
        """Test direct gaze validation"""
        rule_def = Mock()
        rule_def.rule_id = "ICAO.4.1.2"
        rule_def.parameters = {"max_gaze_deviation_degrees": 5.0}
        
        mock_result = Mock()
        mock_result.passes = True  # Yaw is 2.0, within limit
        mock_rules_engine.validate_rule_compliance.return_value = mock_result
        
        result = validators._validate_direct_gaze(rule_def, sample_face_features)
        
        assert result == mock_result
        # Should be called with absolute yaw value (2.0)
        mock_rules_engine.validate_rule_compliance.assert_called_with(
            "ICAO.4.1.2", 2.0
        )
    
    def test_validate_eyes_open(self, validators, sample_face_features, mock_rules_engine):
        """Test eyes open validation"""
        rule_def = Mock()
        rule_def.rule_id = "ICAO.4.1.3"
        rule_def.parameters = {"min_eye_openness": 0.7}
        
        mock_result = Mock()
        mock_result.passes = True  # Min eye openness is 0.8, above limit
        mock_rules_engine.validate_rule_compliance.return_value = mock_result
        
        result = validators._validate_eyes_open(rule_def, sample_face_features)
        
        assert result == mock_result
        # Should be called with minimum eye openness (0.8)
        mock_rules_engine.validate_rule_compliance.assert_called_with(
            "ICAO.4.1.3", 0.8
        )
    
    def test_validate_sharpness(self, validators, sample_quality_metrics, mock_rules_engine):
        """Test sharpness validation"""
        rule_def = Mock()
        rule_def.rule_id = "ICAO.5.1.1"
        rule_def.parameters = {"min_laplacian_variance": 100}
        
        mock_result = Mock()
        mock_result.passes = True  # Laplacian variance is 150, above minimum
        mock_rules_engine.validate_rule_compliance.return_value = mock_result
        
        result = validators._validate_sharpness(rule_def, sample_quality_metrics)
        
        assert result == mock_result
        mock_rules_engine.validate_rule_compliance.assert_called_with(
            "ICAO.5.1.1", sample_quality_metrics.sharpness_laplacian
        )
    
    def test_validate_religious_head_covering(self, validators, mock_rules_engine):
        """Test religious head covering validation"""
        rule_def = Mock()
        rule_def.rule_id = "ICAO.3.3.1"
        rule_def.parameters = {"face_visibility_requirement": 0.85}
        
        # Test with religious head covering
        face_features = FaceFeatures(
            eye_positions=((100, 150), (200, 150)),
            eye_openness=(0.8, 0.9),
            mouth_position=(150, 200),
            mouth_openness=0.05,
            face_orientation=(0.0, 0.0, 0.0),
            glasses_detected=False,
            glasses_confidence=0.0,
            glasses_type=None,
            head_covering_detected=True,
            head_covering_confidence=0.8,
            head_covering_type="religious",
            face_visibility_ratio=0.9
        )
        
        mock_result = Mock()
        mock_result.passes = True  # Face visibility 0.9 > requirement 0.85
        mock_rules_engine.validate_rule_compliance.return_value = mock_result
        
        result = validators._validate_religious_head_covering(rule_def, face_features)
        
        assert result == mock_result
        mock_rules_engine.validate_rule_compliance.assert_called_with(
            "ICAO.3.3.1", 0.9
        )
    
    def test_validate_no_head_covering(self, validators, sample_face_features, mock_rules_engine):
        """Test validation when no head covering is detected"""
        rule_def = Mock()
        rule_def.rule_id = "ICAO.3.3.1"
        rule_def.parameters = {"face_visibility_requirement": 0.85}
        
        mock_result = Mock()
        mock_result.passes = True  # No head covering, full visibility
        mock_rules_engine.validate_rule_compliance.return_value = mock_result
        
        result = validators._validate_religious_head_covering(rule_def, sample_face_features)
        
        assert result == mock_result
        mock_rules_engine.validate_rule_compliance.assert_called_with(
            "ICAO.3.3.1", 1.0  # Full face visibility
        )


class TestFaceFeatures:
    """Test FaceFeatures dataclass"""
    
    def test_face_features_creation(self):
        """Test creating face features"""
        features = FaceFeatures(
            eye_positions=((100, 150), (200, 150)),
            eye_openness=(0.8, 0.9),
            mouth_position=(150, 200),
            mouth_openness=0.05,
            face_orientation=(0.0, 2.0, 1.0),
            glasses_detected=True,
            glasses_confidence=0.7,
            glasses_type="prescription",
            head_covering_detected=False,
            head_covering_confidence=0.1,
            head_covering_type=None,
            face_visibility_ratio=0.95
        )
        
        assert features.eye_positions == ((100, 150), (200, 150))
        assert features.glasses_detected is True
        assert features.glasses_confidence == 0.7
        assert features.head_covering_detected is False
        assert features.face_visibility_ratio == 0.95


class TestImageQualityMetrics:
    """Test ImageQualityMetrics dataclass"""
    
    def test_quality_metrics_creation(self):
        """Test creating quality metrics"""
        metrics = ImageQualityMetrics(
            sharpness_laplacian=150.0,
            sharpness_sobel=75.0,
            sharpness_fft=0.4,
            brightness_mean=120.0,
            brightness_std=25.0,
            contrast_ratio=0.7,
            color_cast_angle=5.0,
            noise_level=0.05,
            compression_artifacts=0.02
        )
        
        assert metrics.sharpness_laplacian == 150.0
        assert metrics.brightness_mean == 120.0
        assert metrics.contrast_ratio == 0.7
        assert metrics.noise_level == 0.05


class TestLightingMetrics:
    """Test LightingMetrics dataclass"""
    
    def test_lighting_metrics_creation(self):
        """Test creating lighting metrics"""
        metrics = LightingMetrics(
            shadow_intensity=0.15,
            highlight_intensity=0.1,
            lighting_uniformity=0.85,
            flash_reflection_detected=False,
            flash_reflection_intensity=0.05,
            red_eye_detected=False,
            background_uniformity=0.92
        )
        
        assert metrics.shadow_intensity == 0.15
        assert metrics.lighting_uniformity == 0.85
        assert metrics.flash_reflection_detected is False
        assert metrics.background_uniformity == 0.92


if __name__ == "__main__":
    pytest.main([__file__])