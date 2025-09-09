"""
Unit tests for AutoFixEngine and related components.
"""

import unittest
import numpy as np
import cv2
from unittest.mock import Mock, patch, MagicMock
import tempfile
import os

from autofix.autofix_engine import (
    AutoFixEngine, IssueAnalysis, CorrectionPlan, AutoFixResult,
    ImprovementMetrics, IssueCategory, FixPriority, ComplianceIssue, ValidationResult
)
from autofix.targeted_processor import TargetedProcessor
from autofix.background_processor import BackgroundProcessor
from autofix.lighting_corrector import LightingCorrector
from autofix.geometry_corrector import GeometryCorrector
from autofix.quality_verifier import QualityVerifier
from rules.icao_rules_engine import RuleResult, RuleSeverity
from ai.ai_engine import AIEngine


class TestAutoFixEngine(unittest.TestCase):
    """Test cases for AutoFixEngine class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create mock AI engine
        self.mock_ai_engine = Mock(spec=AIEngine)
        
        # Create test image
        self.test_image = np.random.randint(0, 255, (400, 300, 3), dtype=np.uint8)
        
        # Create AutoFixEngine instance
        self.autofix_engine = AutoFixEngine(self.mock_ai_engine)
        
        # Create mock validation result
        self.mock_validation_result = self._create_mock_validation_result()
    
    def _create_mock_validation_result(self):
        """Create a mock validation result for testing."""
        issues = [
            ComplianceIssue(
                category="background",
                severity="major",
                description="Non-uniform background",
                fix_suggestion="Replace with uniform background",
                auto_fixable=True,
                regulation_reference="ICAO.6.1.1"
            ),
            ComplianceIssue(
                category="lighting",
                severity="minor",
                description="Uneven lighting",
                fix_suggestion="Adjust lighting uniformity",
                auto_fixable=True,
                regulation_reference="ICAO.5.2.1"
            ),
            ComplianceIssue(
                category="glasses",
                severity="critical",
                description="Tinted glasses detected",
                fix_suggestion="Remove glasses or use clear lenses",
                auto_fixable=False,
                regulation_reference="ICAO.3.2.1"
            )
        ]
        
        rule_results = [
            RuleResult(
                rule_id="ICAO.6.1.1",
                rule_name="Background uniformity",
                passes=False,
                measured_value=0.6,
                required_value=0.9,
                confidence=0.8,
                severity=RuleSeverity.MAJOR,
                regulation_reference="ICAO Doc 9303 Part 6 Section 1.1",
                description="Background uniformity check",
                suggestion="Improve background uniformity"
            ),
            RuleResult(
                rule_id="ICAO.5.2.1",
                rule_name="Lighting uniformity",
                passes=False,
                measured_value=0.7,
                required_value=0.8,
                confidence=0.9,
                severity=RuleSeverity.MINOR,
                regulation_reference="ICAO Doc 9303 Part 5 Section 2.1",
                description="Lighting uniformity check",
                suggestion="Improve lighting uniformity"
            )
        ]
        
        return ValidationResult(
            overall_compliance=65.0,
            passes_requirements=False,
            rule_results=rule_results,
            issue_summary=issues,
            improvement_suggestions=["Fix background", "Improve lighting"],
            confidence_score=0.85
        )
    
    def test_analyze_issues_identifies_fixable_issues(self):
        """Test that analyze_issues correctly identifies fixable issues."""
        analysis = self.autofix_engine.analyze_issues(
            self.mock_validation_result, self.test_image
        )
        
        self.assertIsInstance(analysis, IssueAnalysis)
        self.assertEqual(len(analysis.fixable_issues), 2)  # background and lighting
        self.assertEqual(len(analysis.unfixable_issues), 1)  # glasses
        
        # Check that fixable issues are background and lighting
        fixable_categories = [issue.category for issue in analysis.fixable_issues]
        self.assertIn("background", fixable_categories)
        self.assertIn("lighting", fixable_categories)
        
        # Check that unfixable issue is glasses
        unfixable_categories = [issue.category for issue in analysis.unfixable_issues]
        self.assertIn("glasses", unfixable_categories)
    
    def test_analyze_issues_prioritizes_correctly(self):
        """Test that issues are prioritized correctly."""
        analysis = self.autofix_engine.analyze_issues(
            self.mock_validation_result, self.test_image
        )
        
        # Check priority order
        priorities = [priority for _, priority in analysis.fix_priority_order]
        
        # Should have HIGH priority for major issues and MEDIUM for minor
        self.assertIn(FixPriority.HIGH, priorities)
        self.assertIn(FixPriority.MEDIUM, priorities)
    
    def test_plan_corrections_creates_valid_plan(self):
        """Test that plan_corrections creates a valid correction plan."""
        analysis = self.autofix_engine.analyze_issues(
            self.mock_validation_result, self.test_image
        )
        
        plan = self.autofix_engine.plan_corrections(analysis, self.test_image)
        
        self.assertIsInstance(plan, CorrectionPlan)
        self.assertGreater(len(plan.corrections), 0)
        self.assertGreater(len(plan.execution_order), 0)
        
        # Check that corrections include expected operations
        operations = [correction['operation'] for correction in plan.corrections]
        self.assertIn('background_correction', operations)
        self.assertIn('lighting_correction', operations)
    
    def test_apply_corrections_with_mock_processors(self):
        """Test apply_corrections with mocked processors."""
        # Mock the processors
        self.autofix_engine.background_processor.replace_background = Mock(
            return_value=self.test_image
        )
        self.autofix_engine.lighting_corrector.adjust_lighting = Mock(
            return_value=self.test_image
        )
        self.autofix_engine.quality_verifier.verify_quality_preserved = Mock(
            return_value=True
        )
        
        # Create a simple correction plan
        plan = CorrectionPlan(
            corrections=[
                {
                    'operation': 'background_correction',
                    'category': 'background',
                    'parameters': {'target_color': (255, 255, 255)}
                }
            ],
            execution_order=['background_correction'],
            quality_checkpoints=['background_correction'],
            rollback_points=[],
            expected_improvements={'background_correction': 15.0}
        )
        
        result = self.autofix_engine.apply_corrections(
            self.test_image, plan, self.mock_validation_result
        )
        
        self.assertIsInstance(result, AutoFixResult)
        self.assertTrue(result.success)
        self.assertIn('background_correction', result.applied_corrections)
        self.assertTrue(result.quality_preserved)
    
    def test_calculate_improvement_metrics(self):
        """Test calculation of improvement metrics."""
        # Create before and after validation results
        before = self.mock_validation_result
        
        # Create improved after result
        after_rule_results = [
            RuleResult(
                rule_id="ICAO.6.1.1",
                rule_name="Background uniformity",
                passes=True,
                measured_value=0.95,
                required_value=0.9,
                confidence=0.9,
                severity=RuleSeverity.MAJOR,
                regulation_reference="ICAO Doc 9303 Part 6 Section 1.1",
                description="Background uniformity check",
                suggestion=""
            )
        ]
        
        after = ValidationResult(
            overall_compliance=85.0,
            passes_requirements=True,
            rule_results=after_rule_results,
            issue_summary=[],
            improvement_suggestions=[],
            confidence_score=0.9
        )
        
        metrics = self.autofix_engine.calculate_improvement_metrics(before, after)
        
        self.assertIn('overall_compliance_improvement', metrics)
        self.assertIn('success_rate', metrics)
        self.assertIn('confidence_score', metrics)
        
        # Check that improvement is positive
        self.assertGreater(metrics['overall_compliance_improvement'], 0)
    
    def test_issue_categorization(self):
        """Test that issues are correctly categorized."""
        issues = [
            ComplianceIssue("background", "major", "desc", "fix", True, "ref"),
            ComplianceIssue("lighting", "minor", "desc", "fix", True, "ref"),
            ComplianceIssue("geometry", "major", "desc", "fix", True, "ref"),
        ]
        
        categorized = self.autofix_engine._categorize_issues(issues)
        
        self.assertEqual(len(categorized[IssueCategory.BACKGROUND]), 1)
        self.assertEqual(len(categorized[IssueCategory.LIGHTING]), 1)
        self.assertEqual(len(categorized[IssueCategory.GEOMETRY]), 1)
        self.assertEqual(len(categorized[IssueCategory.GLASSES]), 0)
    
    def test_quality_risk_assessment(self):
        """Test quality risk assessment."""
        high_risk_issues = [
            ComplianceIssue("background", "critical", "desc", "fix", True, "ref"),
            ComplianceIssue("lighting", "critical", "desc", "fix", True, "ref"),
        ]
        
        low_risk_issues = [
            ComplianceIssue("geometry", "minor", "desc", "fix", True, "ref"),
        ]
        
        high_risk = self.autofix_engine._assess_quality_risk(high_risk_issues, self.test_image)
        low_risk = self.autofix_engine._assess_quality_risk(low_risk_issues, self.test_image)
        
        self.assertEqual(high_risk, "high")
        self.assertEqual(low_risk, "low")


class TestTargetedProcessor(unittest.TestCase):
    """Test cases for TargetedProcessor class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_ai_engine = Mock(spec=AIEngine)
        self.processor = TargetedProcessor(self.mock_ai_engine)
        self.test_image = np.random.randint(0, 255, (400, 300, 3), dtype=np.uint8)
    
    def test_background_uniformity_correction(self):
        """Test background uniformity correction."""
        # Mock face detection
        mock_face = Mock()
        mock_face.bbox = Mock()
        mock_face.bbox.x = 100
        mock_face.bbox.y = 50
        mock_face.bbox.width = 100
        mock_face.bbox.height = 120
        
        self.mock_ai_engine.detect_faces.return_value = [mock_face]
        
        parameters = {
            'target_color': (255, 255, 255),
            'correction_strength': 0.7
        }
        
        result = self.processor._correct_background_uniformity(self.test_image, parameters)
        
        self.assertEqual(result.shape, self.test_image.shape)
        self.assertEqual(result.dtype, self.test_image.dtype)
    
    def test_shadow_reduction(self):
        """Test shadow reduction functionality."""
        parameters = {
            'shadow_threshold': 80,
            'brightening_factor': 1.3
        }
        
        result = self.processor._reduce_shadows(self.test_image, parameters)
        
        self.assertEqual(result.shape, self.test_image.shape)
        self.assertEqual(result.dtype, self.test_image.dtype)
    
    def test_color_balance_correction(self):
        """Test color balance correction."""
        parameters = {
            'correction_strength': 0.5
        }
        
        result = self.processor._correct_color_balance(self.test_image, parameters)
        
        self.assertEqual(result.shape, self.test_image.shape)
        self.assertEqual(result.dtype, self.test_image.dtype)


class TestBackgroundProcessor(unittest.TestCase):
    """Test cases for BackgroundProcessor class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_ai_engine = Mock(spec=AIEngine)
        self.processor = BackgroundProcessor(self.mock_ai_engine)
        self.test_image = np.random.randint(0, 255, (400, 300, 3), dtype=np.uint8)
    
    def test_background_replacement(self):
        """Test background replacement functionality."""
        # Mock background segmentation
        mock_mask = np.random.randint(0, 2, (400, 300), dtype=np.uint8) * 255
        self.mock_ai_engine.segment_background.return_value = mock_mask
        
        result = self.processor.replace_background(
            self.test_image,
            target_color=(255, 255, 255),
            edge_refinement=True,
            preserve_hair_details=True
        )
        
        self.assertEqual(result.shape, self.test_image.shape)
        self.assertEqual(result.dtype, self.test_image.dtype)
    
    def test_background_uniformity_calculation(self):
        """Test background uniformity calculation."""
        # Create a mock background mask
        mask = np.zeros((400, 300), dtype=np.uint8)
        mask[200:, :] = 255  # Bottom half is background
        
        uniformity = self.processor._calculate_background_uniformity(self.test_image, mask)
        
        self.assertIsInstance(uniformity, float)
        self.assertGreaterEqual(uniformity, 0.0)
        self.assertLessEqual(uniformity, 1.0)


class TestLightingCorrector(unittest.TestCase):
    """Test cases for LightingCorrector class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.corrector = LightingCorrector()
        self.test_image = np.random.randint(0, 255, (400, 300, 3), dtype=np.uint8)
    
    def test_lighting_adjustment(self):
        """Test basic lighting adjustment."""
        result = self.corrector.adjust_lighting(
            self.test_image,
            adjustment_strength=0.3,
            preserve_skin_tones=True,
            reduce_shadows=True
        )
        
        self.assertEqual(result.shape, self.test_image.shape)
        self.assertEqual(result.dtype, self.test_image.dtype)
    
    def test_uneven_lighting_correction(self):
        """Test uneven lighting correction."""
        result = self.corrector.correct_uneven_lighting(
            self.test_image,
            correction_strength=0.5
        )
        
        self.assertEqual(result.shape, self.test_image.shape)
        self.assertEqual(result.dtype, self.test_image.dtype)
    
    def test_color_temperature_estimation(self):
        """Test color temperature estimation."""
        temperature = self.corrector._estimate_color_temperature(self.test_image)
        
        self.assertIsInstance(temperature, float)
        self.assertGreaterEqual(temperature, 2000)
        self.assertLessEqual(temperature, 10000)


class TestGeometryCorrector(unittest.TestCase):
    """Test cases for GeometryCorrector class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.corrector = GeometryCorrector()
        self.test_image = np.random.randint(0, 255, (400, 300, 3), dtype=np.uint8)
    
    def test_head_tilt_correction(self):
        """Test head tilt correction."""
        # This test will use the fallback OpenCV detection
        result = self.corrector.correct_head_tilt(
            self.test_image,
            max_tilt_degrees=2.0
        )
        
        self.assertEqual(result.shape, self.test_image.shape)
        self.assertEqual(result.dtype, self.test_image.dtype)
    
    def test_image_rotation(self):
        """Test image rotation functionality."""
        result = self.corrector._rotate_image(self.test_image, 5.0)
        
        self.assertEqual(result.shape, self.test_image.shape)
        self.assertEqual(result.dtype, self.test_image.dtype)
    
    def test_tilt_angle_calculation(self):
        """Test tilt angle calculation."""
        left_eye = (100, 150)
        right_eye = (200, 160)
        
        angle = self.corrector._calculate_tilt_angle(left_eye, right_eye)
        
        self.assertIsInstance(angle, float)
        # Should be a small positive angle for this example
        self.assertGreater(angle, 0)
        self.assertLess(angle, 10)


class TestQualityVerifier(unittest.TestCase):
    """Test cases for QualityVerifier class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_ai_engine = Mock(spec=AIEngine)
        
        # Mock quality metrics
        mock_quality_metrics = Mock()
        mock_quality_metrics.overall_score = 75.0
        mock_quality_metrics.sharpness_score = 80.0
        mock_quality_metrics.brightness_score = 70.0
        mock_quality_metrics.contrast_score = 85.0
        mock_quality_metrics.color_accuracy_score = 0.8
        mock_quality_metrics.noise_level = 0.05
        
        self.mock_ai_engine.assess_image_quality.return_value = mock_quality_metrics
        
        self.verifier = QualityVerifier(self.mock_ai_engine)
        self.test_image = np.random.randint(0, 255, (400, 300, 3), dtype=np.uint8)
    
    def test_quality_preservation_verification(self):
        """Test quality preservation verification."""
        # Create slightly different corrected image
        corrected_image = self.test_image.copy()
        corrected_image = cv2.GaussianBlur(corrected_image, (3, 3), 0.5)
        
        preserved = self.verifier.verify_quality_preserved(
            self.test_image, corrected_image, tolerance=10.0
        )
        
        self.assertIsInstance(preserved, bool)
    
    def test_improvement_quality_assessment(self):
        """Test improvement quality assessment."""
        corrected_image = self.test_image.copy()
        
        assessment = self.verifier.assess_improvement_quality(
            self.test_image, corrected_image
        )
        
        self.assertIn('improvement_score', assessment)
        self.assertIn('improvements', assessment)
        self.assertIn('degradation_areas', assessment)
        self.assertIn('overall_assessment', assessment)
        self.assertIn('recommendations', assessment)
    
    def test_compliance_quality_validation(self):
        """Test compliance quality validation."""
        validation = self.verifier.validate_compliance_quality(self.test_image)
        
        self.assertIn('overall_compliance', validation)
        self.assertIn('individual_results', validation)
        self.assertIn('quality_score', validation)
        self.assertIn('recommendations', validation)
        
        # Check individual results structure
        individual = validation['individual_results']
        expected_metrics = ['sharpness', 'brightness', 'contrast', 'noise', 'color_accuracy']
        
        for metric in expected_metrics:
            if metric in individual:
                self.assertIn('value', individual[metric])
                self.assertIn('passes', individual[metric])
    
    def test_sharpness_metrics_calculation(self):
        """Test sharpness metrics calculation."""
        metrics = self.verifier._calculate_sharpness_metrics(self.test_image)
        
        self.assertIn('sharpness', metrics)
        self.assertIn('sobel_sharpness', metrics)
        self.assertIsInstance(metrics['sharpness'], float)
        self.assertIsInstance(metrics['sobel_sharpness'], float)


class TestAutoFixIntegration(unittest.TestCase):
    """Integration tests for AutoFix components."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_ai_engine = Mock(spec=AIEngine)
        
        # Mock AI engine methods
        mock_quality_metrics = Mock()
        mock_quality_metrics.overall_score = 75.0
        mock_quality_metrics.sharpness_score = 80.0
        mock_quality_metrics.brightness_score = 70.0
        mock_quality_metrics.contrast_score = 85.0
        mock_quality_metrics.color_accuracy_score = 0.8
        mock_quality_metrics.noise_level = 0.05
        
        self.mock_ai_engine.assess_image_quality.return_value = mock_quality_metrics
        self.mock_ai_engine.detect_faces.return_value = []
        self.mock_ai_engine.segment_background.return_value = np.zeros((400, 300), dtype=np.uint8)
        
        self.autofix_engine = AutoFixEngine(self.mock_ai_engine)
        self.test_image = np.random.randint(0, 255, (400, 300, 3), dtype=np.uint8)
    
    def test_end_to_end_autofix_workflow(self):
        """Test complete end-to-end autofix workflow."""
        # Create validation result with fixable issues
        issues = [
            ComplianceIssue(
                category="background",
                severity="major",
                description="Non-uniform background",
                fix_suggestion="Replace with uniform background",
                auto_fixable=True,
                regulation_reference="ICAO.6.1.1"
            )
        ]
        
        validation_result = ValidationResult(
            overall_compliance=60.0,
            passes_requirements=False,
            rule_results=[],
            issue_summary=issues,
            improvement_suggestions=["Fix background"],
            confidence_score=0.8
        )
        
        # Run complete workflow
        analysis = self.autofix_engine.analyze_issues(validation_result, self.test_image)
        self.assertGreater(len(analysis.fixable_issues), 0)
        
        plan = self.autofix_engine.plan_corrections(analysis, self.test_image)
        self.assertGreater(len(plan.corrections), 0)
        
        # Mock the correction methods to avoid actual image processing
        with patch.object(self.autofix_engine.background_processor, 'replace_background', 
                         return_value=self.test_image):
            with patch.object(self.autofix_engine.quality_verifier, 'verify_quality_preserved',
                             return_value=True):
                result = self.autofix_engine.apply_corrections(
                    self.test_image, plan, validation_result
                )
        
        self.assertIsInstance(result, AutoFixResult)
        self.assertTrue(result.success)
        self.assertGreater(len(result.applied_corrections), 0)


if __name__ == '__main__':
    unittest.main()