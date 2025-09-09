"""
ICAO Compliance Tests with Reference Images
Tests the system against official ICAO standards and reference images.
"""

import pytest
import numpy as np
import cv2
import json
from pathlib import Path
from unittest.mock import Mock, patch
import tempfile
from typing import Dict, List, Tuple

from validation.icao_validator import ICAOValidator
from rules.icao_rules_engine import ICAORulesEngine
from ai.ai_engine import AIEngine
from quality.quality_engine import QualityEngine


class ICAOReferenceImageGenerator:
    """Generate reference images for ICAO compliance testing"""
    
    @staticmethod
    def create_compliant_reference():
        """Create ICAO-compliant reference image"""
        # Standard passport photo dimensions (35mm x 45mm at 300 DPI)
        img = np.ones((531, 413, 3), dtype=np.uint8) * 255  # White background
        
        # Face positioned according to ICAO standards
        # Face height should be 70-80% of image height
        face_height = int(531 * 0.75)  # 75% of image height
        face_width = int(face_height * 0.8)  # Proportional width
        
        center_x = 413 // 2
        center_y = int(531 * 0.55)  # Eye level at 50-60% from bottom
        
        # Draw face outline
        cv2.ellipse(img, (center_x, center_y), (face_width//2, face_height//2), 
                   0, 0, 360, (220, 180, 160), -1)
        
        # Eyes at proper position (50-60% from bottom)
        eye_y = int(531 * 0.55)
        eye_distance = face_width // 3
        left_eye = (center_x - eye_distance//2, eye_y)
        right_eye = (center_x + eye_distance//2, eye_y)
        
        cv2.circle(img, left_eye, 8, (50, 50, 50), -1)
        cv2.circle(img, right_eye, 8, (50, 50, 50), -1)
        
        # Nose
        nose_tip = (center_x, eye_y + face_height//6)
        cv2.line(img, (center_x, eye_y + 20), nose_tip, (180, 140, 120), 2)
        
        # Mouth (closed, neutral expression)
        mouth_y = eye_y + face_height//3
        cv2.ellipse(img, (center_x, mouth_y), (20, 6), 0, 0, 180, (120, 80, 80), 2)
        
        return img
    
    @staticmethod
    def create_glasses_violation():
        """Create image with glasses violations"""
        img = ICAOReferenceImageGenerator.create_compliant_reference()
        
        # Add tinted glasses (ICAO violation)
        center_x, center_y = 413 // 2, int(531 * 0.55)
        eye_distance = 80
        
        # Tinted lenses
        cv2.ellipse(img, (center_x - eye_distance//2, center_y), (25, 15), 
                   0, 0, 360, (100, 100, 100), -1)  # Dark tinted
        cv2.ellipse(img, (center_x + eye_distance//2, center_y), (25, 15), 
                   0, 0, 360, (100, 100, 100), -1)  # Dark tinted
        
        # Heavy frames
        cv2.ellipse(img, (center_x - eye_distance//2, center_y), (30, 20), 
                   0, 0, 360, (50, 50, 50), 5)  # Thick frame
        cv2.ellipse(img, (center_x + eye_distance//2, center_y), (30, 20), 
                   0, 0, 360, (50, 50, 50), 5)  # Thick frame
        
        return img
    
    @staticmethod
    def create_head_covering_violation():
        """Create image with head covering violations"""
        img = ICAOReferenceImageGenerator.create_compliant_reference()
        
        # Add non-religious head covering (hat)
        center_x, center_y = 413 // 2, int(531 * 0.55)
        face_height = int(531 * 0.75)
        
        # Baseball cap
        cap_points = np.array([
            [center_x - 60, center_y - face_height//2 - 20],
            [center_x + 60, center_y - face_height//2 - 20],
            [center_x + 80, center_y - face_height//2 + 10],
            [center_x - 80, center_y - face_height//2 + 10]
        ], np.int32)
        
        cv2.fillPoly(img, [cap_points], (100, 150, 200))  # Blue cap
        
        return img
    
    @staticmethod
    def create_expression_violation():
        """Create image with expression violations"""
        img = ICAOReferenceImageGenerator.create_compliant_reference()
        
        center_x = 413 // 2
        eye_y = int(531 * 0.55)
        face_height = int(531 * 0.75)
        
        # Smiling mouth (violation of neutral expression)
        mouth_y = eye_y + face_height//3
        cv2.ellipse(img, (center_x, mouth_y), (25, 12), 0, 0, 180, (120, 80, 80), -1)
        
        # Teeth showing
        cv2.ellipse(img, (center_x, mouth_y - 3), (20, 6), 0, 0, 180, (255, 255, 255), -1)
        
        # Squinting eyes (not looking directly at camera)
        cv2.ellipse(img, (center_x - 30, eye_y), (12, 6), 0, 0, 360, (50, 50, 50), -1)
        cv2.ellipse(img, (center_x + 30, eye_y), (12, 6), 0, 0, 360, (50, 50, 50), -1)
        
        return img
    
    @staticmethod
    def create_lighting_violation():
        """Create image with lighting violations"""
        img = ICAOReferenceImageGenerator.create_compliant_reference()
        
        # Add harsh shadows
        shadow_mask = np.zeros(img.shape[:2], dtype=np.uint8)
        cv2.ellipse(shadow_mask, (300, 300), (100, 150), 45, 0, 180, 255, -1)
        
        # Apply shadow
        img[shadow_mask > 0] = (img[shadow_mask > 0] * 0.4).astype(np.uint8)
        
        # Add flash reflection on forehead
        cv2.ellipse(img, (413//2, int(531 * 0.45)), (30, 20), 0, 0, 360, (255, 255, 255), -1)
        
        return img
    
    @staticmethod
    def create_background_violation():
        """Create image with background violations"""
        img = ICAOReferenceImageGenerator.create_compliant_reference()
        
        # Change background to non-white
        background_mask = np.ones(img.shape[:2], dtype=np.uint8) * 255
        
        # Create face mask to preserve face
        center_x, center_y = 413 // 2, int(531 * 0.55)
        face_height = int(531 * 0.75)
        face_width = int(face_height * 0.8)
        
        cv2.ellipse(background_mask, (center_x, center_y), 
                   (face_width//2 + 20, face_height//2 + 20), 0, 0, 360, 0, -1)
        
        # Apply blue background
        img[background_mask > 0] = [200, 150, 100]  # Blue background
        
        return img
    
    @staticmethod
    def create_quality_violation():
        """Create image with quality violations"""
        img = ICAOReferenceImageGenerator.create_compliant_reference()
        
        # Apply blur (sharpness violation)
        img = cv2.GaussianBlur(img, (15, 15), 0)
        
        # Add noise
        noise = np.random.randint(-30, 30, img.shape, dtype=np.int16)
        img = np.clip(img.astype(np.int16) + noise, 0, 255).astype(np.uint8)
        
        # Reduce contrast
        img = cv2.convertScaleAbs(img, alpha=0.5, beta=50)
        
        return img


class TestICAOComplianceValidation:
    """Test ICAO compliance validation against reference images"""
    
    @pytest.fixture
    def icao_reference_images(self):
        """Generate ICAO reference images for testing"""
        generator = ICAOReferenceImageGenerator()
        
        return {
            'compliant': generator.create_compliant_reference(),
            'glasses_violation': generator.create_glasses_violation(),
            'head_covering_violation': generator.create_head_covering_violation(),
            'expression_violation': generator.create_expression_violation(),
            'lighting_violation': generator.create_lighting_violation(),
            'background_violation': generator.create_background_violation(),
            'quality_violation': generator.create_quality_violation()
        }
    
    @pytest.fixture
    def icao_validator_setup(self):
        """Setup ICAO validator with mocked dependencies"""
        with patch('rules.icao_rules_engine.ICAORulesEngine') as mock_rules:
            # Mock ICAO rules
            mock_rules.return_value.load_icao_rules.return_value = Mock(
                glasses_rules=Mock(
                    tinted_lenses_allowed=False,
                    max_frame_width_ratio=0.15,
                    glare_detection_threshold=0.2
                ),
                expression_rules=Mock(
                    max_mouth_openness=0.1,
                    max_smile_intensity=0.2,
                    direct_gaze_required=True
                ),
                quality_rules=Mock(
                    min_sharpness_score=0.7,
                    min_lighting_score=0.8,
                    max_shadow_intensity=0.3
                ),
                background_rules=Mock(
                    required_color=(255, 255, 255),
                    uniformity_threshold=0.9,
                    color_tolerance=10
                )
            )
            
            validator = ICAOValidator()
            return validator
    
    def test_compliant_image_validation(self, icao_reference_images, icao_validator_setup):
        """Test that compliant reference image passes all ICAO checks"""
        validator = icao_validator_setup
        compliant_image = icao_reference_images['compliant']
        
        # Mock face features for compliant image
        mock_features = Mock(
            glasses_detected=False,
            head_covering_detected=False,
            mouth_openness=0.05,
            smile_intensity=0.1,
            eye_contact_score=0.95,
            face_position_score=0.9
        )
        
        # Mock quality metrics
        mock_quality = Mock(
            sharpness_score=0.85,
            lighting_score=0.90,
            background_uniformity=0.95,
            shadow_intensity=0.1
        )
        
        with patch.object(validator, '_extract_face_features', return_value=mock_features), \
             patch.object(validator, '_assess_image_quality', return_value=mock_quality):
            
            result = validator.validate_full_compliance(compliant_image, mock_features, mock_quality)
            
            assert result.overall_compliance >= 85.0
            assert result.passes_requirements is True
            assert all(rule.passes for rule in result.rule_results if rule.rule_id in [
                'glasses_compliance', 'expression_neutral', 'background_white'
            ])
    
    def test_glasses_violation_detection(self, icao_reference_images, icao_validator_setup):
        """Test detection of glasses violations"""
        validator = icao_validator_setup
        glasses_violation_image = icao_reference_images['glasses_violation']
        
        # Mock face features with glasses violations
        mock_features = Mock(
            glasses_detected=True,
            glasses_type='tinted',
            frame_width_ratio=0.25,  # Exceeds ICAO limit
            glare_intensity=0.4      # Exceeds ICAO limit
        )
        
        mock_quality = Mock(sharpness_score=0.85, lighting_score=0.90)
        
        with patch.object(validator, '_extract_face_features', return_value=mock_features), \
             patch.object(validator, '_assess_image_quality', return_value=mock_quality):
            
            result = validator.validate_glasses_compliance(glasses_violation_image, mock_features)
            
            assert result.passes is False
            assert 'tinted' in result.violation_details.lower() or 'glare' in result.violation_details.lower()
            assert result.regulation_reference == "ICAO Doc 9303 Part 3 Section 3.2"
    
    def test_head_covering_violation_detection(self, icao_reference_images, icao_validator_setup):
        """Test detection of head covering violations"""
        validator = icao_validator_setup
        head_covering_image = icao_reference_images['head_covering_violation']
        
        # Mock face features with non-religious head covering
        mock_features = Mock(
            head_covering_detected=True,
            head_covering_type='hat',  # Non-religious
            face_visibility_ratio=0.75  # Below ICAO requirement
        )
        
        mock_quality = Mock(sharpness_score=0.85, lighting_score=0.90)
        
        with patch.object(validator, '_extract_face_features', return_value=mock_features), \
             patch.object(validator, '_assess_image_quality', return_value=mock_quality):
            
            result = validator.validate_head_covering_compliance(head_covering_image, mock_features)
            
            assert result.passes is False
            assert 'non-religious' in result.violation_details.lower() or 'hat' in result.violation_details.lower()
            assert result.regulation_reference == "ICAO Doc 9303 Part 3 Section 3.3"
    
    def test_expression_violation_detection(self, icao_reference_images, icao_validator_setup):
        """Test detection of expression violations"""
        validator = icao_validator_setup
        expression_violation_image = icao_reference_images['expression_violation']
        
        # Mock face features with expression violations
        mock_features = Mock(
            mouth_openness=0.25,      # Exceeds ICAO limit
            smile_intensity=0.4,      # Exceeds ICAO limit
            eye_contact_score=0.6,    # Below ICAO requirement
            teeth_visible=True        # ICAO violation
        )
        
        with patch.object(validator, '_extract_face_features', return_value=mock_features):
            result = validator.validate_expression_compliance(mock_features)
            
            assert result.passes is False
            assert any(keyword in result.violation_details.lower() 
                      for keyword in ['smile', 'mouth', 'teeth', 'expression'])
            assert result.regulation_reference == "ICAO Doc 9303 Part 4 Section 1"
    
    def test_lighting_violation_detection(self, icao_reference_images, icao_validator_setup):
        """Test detection of lighting violations"""
        validator = icao_validator_setup
        lighting_violation_image = icao_reference_images['lighting_violation']
        
        # Mock quality metrics with lighting violations
        mock_quality = Mock(
            lighting_score=0.4,       # Below ICAO requirement
            shadow_intensity=0.6,     # Exceeds ICAO limit
            flash_reflection=0.3,     # Exceeds ICAO limit
            brightness_uniformity=0.5 # Below ICAO requirement
        )
        
        mock_features = Mock(glasses_detected=False, head_covering_detected=False)
        
        with patch.object(validator, '_assess_image_quality', return_value=mock_quality):
            result = validator.validate_style_and_lighting(lighting_violation_image, mock_features)
            
            assert result.passes is False
            assert any(keyword in result.violation_details.lower() 
                      for keyword in ['shadow', 'lighting', 'flash', 'reflection'])
            assert result.regulation_reference == "ICAO Doc 9303 Part 6 Section 2"
    
    def test_background_violation_detection(self, icao_reference_images, icao_validator_setup):
        """Test detection of background violations"""
        validator = icao_validator_setup
        background_violation_image = icao_reference_images['background_violation']
        
        # Mock quality metrics with background violations
        mock_quality = Mock(
            background_color=(200, 150, 100),  # Not white
            background_uniformity=0.7,         # Below ICAO requirement
            color_deviation=25                 # Exceeds ICAO tolerance
        )
        
        mock_features = Mock(glasses_detected=False, head_covering_detected=False)
        
        with patch.object(validator, '_assess_image_quality', return_value=mock_quality):
            result = validator.validate_style_and_lighting(background_violation_image, mock_features)
            
            assert result.passes is False
            assert 'background' in result.violation_details.lower()
            assert result.regulation_reference == "ICAO Doc 9303 Part 6 Section 1"
    
    def test_quality_violation_detection(self, icao_reference_images, icao_validator_setup):
        """Test detection of quality violations"""
        validator = icao_validator_setup
        quality_violation_image = icao_reference_images['quality_violation']
        
        # Mock quality metrics with quality violations
        mock_quality = Mock(
            sharpness_score=0.4,      # Below ICAO requirement
            noise_level=0.8,          # Exceeds ICAO limit
            contrast_score=0.3,       # Below ICAO requirement
            compression_artifacts=0.6  # Exceeds ICAO limit
        )
        
        mock_features = Mock(glasses_detected=False, head_covering_detected=False)
        
        with patch.object(validator, '_assess_image_quality', return_value=mock_quality):
            result = validator.validate_photo_quality_compliance(quality_violation_image, mock_quality)
            
            assert result.passes is False
            assert any(keyword in result.violation_details.lower() 
                      for keyword in ['sharpness', 'blur', 'quality', 'noise'])
            assert result.regulation_reference == "ICAO Doc 9303 Part 5 Section 1"


class TestICAORuleImplementation:
    """Test implementation of specific ICAO rules"""
    
    def test_face_positioning_rules(self):
        """Test ICAO face positioning rules implementation"""
        with patch('rules.icao_rules_engine.ICAORulesEngine') as mock_rules:
            mock_rules.return_value.get_face_positioning_rules.return_value = Mock(
                face_height_ratio_min=0.70,
                face_height_ratio_max=0.80,
                eye_height_ratio_min=0.50,
                eye_height_ratio_max=0.60,
                centering_tolerance=0.05
            )
            
            validator = ICAOValidator()
            
            # Test compliant positioning
            compliant_features = Mock(
                face_height_ratio=0.75,
                eye_height_ratio=0.55,
                horizontal_centering=0.02
            )
            
            result = validator._validate_face_positioning(compliant_features)
            assert result.passes is True
            
            # Test non-compliant positioning
            non_compliant_features = Mock(
                face_height_ratio=0.65,  # Below minimum
                eye_height_ratio=0.45,   # Below minimum
                horizontal_centering=0.08 # Exceeds tolerance
            )
            
            result = validator._validate_face_positioning(non_compliant_features)
            assert result.passes is False
    
    def test_dimension_requirements(self):
        """Test ICAO dimension requirements"""
        with patch('rules.icao_rules_engine.ICAORulesEngine') as mock_rules:
            mock_rules.return_value.get_dimension_rules.return_value = Mock(
                min_width_mm=35,
                min_height_mm=45,
                min_dpi=300,
                max_file_size_mb=10
            )
            
            validator = ICAOValidator()
            
            # Test compliant dimensions
            compliant_image = np.ones((531, 413, 3), dtype=np.uint8)  # 45mm x 35mm at 300 DPI
            
            result = validator._validate_image_dimensions(compliant_image, dpi=300)
            assert result.passes is True
            
            # Test non-compliant dimensions
            non_compliant_image = np.ones((400, 300, 3), dtype=np.uint8)  # Too small
            
            result = validator._validate_image_dimensions(non_compliant_image, dpi=300)
            assert result.passes is False
    
    def test_color_space_requirements(self):
        """Test ICAO color space requirements"""
        with patch('rules.icao_rules_engine.ICAORulesEngine') as mock_rules:
            mock_rules.return_value.get_color_rules.return_value = Mock(
                required_color_space='sRGB',
                bit_depth_min=8,
                color_accuracy_threshold=0.8
            )
            
            validator = ICAOValidator()
            
            # Test compliant color image
            color_image = np.ones((531, 413, 3), dtype=np.uint8) * 128
            
            result = validator._validate_color_requirements(color_image)
            assert result.passes is True
            
            # Test grayscale image (should fail for color requirement)
            grayscale_image = np.ones((531, 413), dtype=np.uint8) * 128
            
            result = validator._validate_color_requirements(grayscale_image)
            assert result.passes is False


class TestICAOComplianceReporting:
    """Test ICAO compliance reporting functionality"""
    
    def test_detailed_compliance_report_generation(self, icao_reference_images):
        """Test generation of detailed compliance reports"""
        with patch('rules.icao_rules_engine.ICAORulesEngine'):
            validator = ICAOValidator()
            
            # Mock comprehensive validation results
            mock_results = [
                Mock(rule_id='glasses', passes=True, score=95.0, 
                     regulation_reference='ICAO Doc 9303 Part 3 Section 3.2'),
                Mock(rule_id='expression', passes=False, score=65.0,
                     regulation_reference='ICAO Doc 9303 Part 4 Section 1',
                     violation_details='Mouth slightly open, smile detected'),
                Mock(rule_id='background', passes=True, score=90.0,
                     regulation_reference='ICAO Doc 9303 Part 6 Section 1'),
                Mock(rule_id='lighting', passes=False, score=70.0,
                     regulation_reference='ICAO Doc 9303 Part 6 Section 2',
                     violation_details='Shadow detected on left side of face')
            ]
            
            report = validator.generate_compliance_report(mock_results)
            
            assert report is not None
            assert 'overall_compliance' in report
            assert 'rule_results' in report
            assert 'violations' in report
            assert 'regulation_references' in report
            
            # Check that violations are properly categorized
            violations = report['violations']
            assert len(violations) == 2  # expression and lighting
            assert any(v['rule_id'] == 'expression' for v in violations)
            assert any(v['rule_id'] == 'lighting' for v in violations)
    
    def test_regulation_reference_accuracy(self):
        """Test that regulation references are accurate and complete"""
        with patch('rules.icao_rules_engine.ICAORulesEngine') as mock_rules:
            # Mock rules with official ICAO references
            mock_rules.return_value.get_all_rules.return_value = {
                'glasses_tinted': {
                    'regulation': 'ICAO Doc 9303 Part 3 Section 3.2.1',
                    'description': 'Tinted lenses are not permitted'
                },
                'expression_neutral': {
                    'regulation': 'ICAO Doc 9303 Part 4 Section 1.1',
                    'description': 'Subject must have neutral expression'
                },
                'background_white': {
                    'regulation': 'ICAO Doc 9303 Part 6 Section 1.1',
                    'description': 'Background must be white and uniform'
                }
            }
            
            validator = ICAOValidator()
            
            # Verify that each rule has proper regulation reference
            rules = validator.rules_engine.get_all_rules()
            
            for rule_id, rule_data in rules.items():
                assert 'regulation' in rule_data
                assert rule_data['regulation'].startswith('ICAO Doc 9303')
                assert 'Part' in rule_data['regulation']
                assert 'Section' in rule_data['regulation']


if __name__ == "__main__":
    pytest.main([__file__, "-v"])