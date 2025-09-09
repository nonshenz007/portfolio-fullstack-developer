"""
ICAO Standards Validation Test Suite

This module provides comprehensive testing against official ICAO standards
and validates compliance detection accuracy with known violations.
"""

import pytest
import numpy as np
import cv2
import json
import time
from pathlib import Path
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass, asdict

from ai.ai_engine import AIEngine
from validation.icao_validator import ICAOValidator
from rules.icao_rules_engine import ICAORulesEngine
from core.processing_controller import ProcessingController
from core.config_manager import ConfigManager
from quality.quality_engine import QualityEngine
from autofix.autofix_engine import AutoFixEngine


@dataclass
class ICAOTestCase:
    """Test case for ICAO compliance validation"""
    name: str
    image_path: str
    expected_compliance: bool
    expected_violations: List[str]
    violation_categories: List[str]
    confidence_threshold: float = 0.8
    description: str = ""


@dataclass
class ValidationMetrics:
    """Metrics for validation accuracy assessment"""
    true_positives: int = 0
    false_positives: int = 0
    true_negatives: int = 0
    false_negatives: int = 0
    
    @property
    def accuracy(self) -> float:
        total = self.true_positives + self.false_positives + self.true_negatives + self.false_negatives
        if total == 0:
            return 0.0
        return (self.true_positives + self.true_negatives) / total
    
    @property
    def precision(self) -> float:
        if self.true_positives + self.false_positives == 0:
            return 0.0
        return self.true_positives / (self.true_positives + self.false_positives)
    
    @property
    def recall(self) -> float:
        if self.true_positives + self.false_negatives == 0:
            return 0.0
        return self.true_positives / (self.true_positives + self.false_negatives)
    
    @property
    def f1_score(self) -> float:
        if self.precision + self.recall == 0:
            return 0.0
        return 2 * (self.precision * self.recall) / (self.precision + self.recall)


class ICAOStandardsValidator:
    """Comprehensive ICAO standards validation system"""
    
    def __init__(self):
        self.config_manager = ConfigManager()
        self.processing_controller = ProcessingController(self.config_manager)
        self.ai_engine = AIEngine()
        self.icao_validator = ICAOValidator(ICAORulesEngine())
        self.quality_engine = QualityEngine()
        self.autofix_engine = AutoFixEngine(self.ai_engine)
        
        # Load ICAO test cases
        self.test_cases = self._load_icao_test_cases()
        
        # Performance tracking
        self.performance_metrics = {
            'processing_times': [],
            'memory_usage': [],
            'accuracy_scores': []
        }
    
    def _load_icao_test_cases(self) -> List[ICAOTestCase]:
        """Load ICAO test cases from configuration"""
        test_cases = []
        
        # Compliant test cases
        compliant_cases = [
            ICAOTestCase(
                name="perfect_passport_photo",
                image_path="test_images/icao_compliant/perfect_passport.jpg",
                expected_compliance=True,
                expected_violations=[],
                violation_categories=[],
                description="Perfect ICAO compliant passport photo"
            ),
            ICAOTestCase(
                name="good_lighting_neutral_expression",
                image_path="test_images/icao_compliant/good_lighting.jpg",
                expected_compliance=True,
                expected_violations=[],
                violation_categories=[],
                description="Good lighting with neutral expression"
            ),
            ICAOTestCase(
                name="clear_glasses_compliant",
                image_path="test_images/icao_compliant/clear_glasses.jpg",
                expected_compliance=True,
                expected_violations=[],
                violation_categories=[],
                description="Clear prescription glasses - compliant"
            )
        ]
        
        # Non-compliant test cases
        non_compliant_cases = [
            ICAOTestCase(
                name="tinted_glasses_violation",
                image_path="test_images/icao_violations/tinted_glasses.jpg",
                expected_compliance=False,
                expected_violations=["ICAO.3.2.1"],
                violation_categories=["glasses"],
                description="Tinted glasses violation"
            ),
            ICAOTestCase(
                name="heavy_frame_glasses",
                image_path="test_images/icao_violations/heavy_frames.jpg",
                expected_compliance=False,
                expected_violations=["ICAO.3.2.2"],
                violation_categories=["glasses"],
                description="Heavy frame glasses obscuring eyes"
            ),
            ICAOTestCase(
                name="smiling_expression",
                image_path="test_images/icao_violations/smiling.jpg",
                expected_compliance=False,
                expected_violations=["ICAO.4.1.1"],
                violation_categories=["expression"],
                description="Smiling expression - not neutral"
            ),
            ICAOTestCase(
                name="poor_lighting_shadows",
                image_path="test_images/icao_violations/shadows.jpg",
                expected_compliance=False,
                expected_violations=["ICAO.6.2.1"],
                violation_categories=["lighting"],
                description="Poor lighting with shadows"
            ),
            ICAOTestCase(
                name="non_white_background",
                image_path="test_images/icao_violations/colored_background.jpg",
                expected_compliance=False,
                expected_violations=["ICAO.6.1.1"],
                violation_categories=["background"],
                description="Non-white background"
            ),
            ICAOTestCase(
                name="blurry_image",
                image_path="test_images/icao_violations/blurry.jpg",
                expected_compliance=False,
                expected_violations=["ICAO.5.1.1"],
                violation_categories=["quality"],
                description="Blurry/out of focus image"
            ),
            ICAOTestCase(
                name="hat_head_covering",
                image_path="test_images/icao_violations/hat.jpg",
                expected_compliance=False,
                expected_violations=["ICAO.3.3.2"],
                violation_categories=["head_covering"],
                description="Hat/non-religious head covering"
            ),
            ICAOTestCase(
                name="off_center_positioning",
                image_path="test_images/icao_violations/off_center.jpg",
                expected_compliance=False,
                expected_violations=["ICAO.4.2.1"],
                violation_categories=["positioning"],
                description="Face not properly centered"
            )
        ]
        
        test_cases.extend(compliant_cases)
        test_cases.extend(non_compliant_cases)
        
        return test_cases
    
    def validate_compliance_detection_accuracy(self) -> Dict[str, Any]:
        """Validate compliance detection accuracy against known violations"""
        print("🔍 Validating compliance detection accuracy...")
        
        overall_metrics = ValidationMetrics()
        category_metrics = {}
        detailed_results = []
        
        for test_case in self.test_cases:
            print(f"  Testing: {test_case.name}")
            
            # Create synthetic test image if file doesn't exist
            if not Path(test_case.image_path).exists():
                test_image = self._create_synthetic_test_image(test_case)
            else:
                test_image = cv2.imread(test_case.image_path)
            
            if test_image is None:
                print(f"    ⚠️  Could not load test image: {test_case.image_path}")
                continue
            
            # Process image and get validation results
            start_time = time.time()
            try:
                result = self.processing_controller.process_image(
                    test_image, 
                    format_name="ICAO",
                    options={"validate_only": True}
                )
                processing_time = time.time() - start_time
                self.performance_metrics['processing_times'].append(processing_time)
                
                # Analyze results
                predicted_compliance = result.validation_result.passes_requirements
                predicted_violations = [r.rule_id for r in result.validation_result.rule_results if not r.passes]
                
                # Update metrics
                if test_case.expected_compliance and predicted_compliance:
                    overall_metrics.true_positives += 1
                elif not test_case.expected_compliance and not predicted_compliance:
                    overall_metrics.true_negatives += 1
                elif test_case.expected_compliance and not predicted_compliance:
                    overall_metrics.false_negatives += 1
                else:
                    overall_metrics.false_positives += 1
                
                # Track category-specific metrics
                for category in test_case.violation_categories:
                    if category not in category_metrics:
                        category_metrics[category] = ValidationMetrics()
                    
                    category_violations = [v for v in predicted_violations 
                                         if self._get_violation_category(v) == category]
                    expected_violations = [v for v in test_case.expected_violations 
                                         if self._get_violation_category(v) == category]
                    
                    if expected_violations and category_violations:
                        category_metrics[category].true_positives += 1
                    elif not expected_violations and not category_violations:
                        category_metrics[category].true_negatives += 1
                    elif expected_violations and not category_violations:
                        category_metrics[category].false_negatives += 1
                    else:
                        category_metrics[category].false_positives += 1
                
                # Store detailed results
                detailed_results.append({
                    'test_case': test_case.name,
                    'expected_compliance': test_case.expected_compliance,
                    'predicted_compliance': predicted_compliance,
                    'expected_violations': test_case.expected_violations,
                    'predicted_violations': predicted_violations,
                    'processing_time': processing_time,
                    'confidence': result.validation_result.confidence_score,
                    'correct_prediction': (test_case.expected_compliance == predicted_compliance)
                })
                
                print(f"    ✅ Processed in {processing_time:.3f}s - "
                      f"{'✓' if test_case.expected_compliance == predicted_compliance else '✗'}")
                
            except Exception as e:
                print(f"    ❌ Error processing {test_case.name}: {str(e)}")
                detailed_results.append({
                    'test_case': test_case.name,
                    'error': str(e),
                    'processing_time': 0,
                    'correct_prediction': False
                })
        
        # Generate comprehensive report
        report = {
            'overall_accuracy': overall_metrics.accuracy,
            'overall_precision': overall_metrics.precision,
            'overall_recall': overall_metrics.recall,
            'overall_f1_score': overall_metrics.f1_score,
            'category_metrics': {
                category: {
                    'accuracy': metrics.accuracy,
                    'precision': metrics.precision,
                    'recall': metrics.recall,
                    'f1_score': metrics.f1_score
                }
                for category, metrics in category_metrics.items()
            },
            'performance_metrics': {
                'avg_processing_time': np.mean(self.performance_metrics['processing_times']),
                'max_processing_time': np.max(self.performance_metrics['processing_times']),
                'min_processing_time': np.min(self.performance_metrics['processing_times'])
            },
            'detailed_results': detailed_results,
            'test_summary': {
                'total_tests': len(self.test_cases),
                'passed_tests': sum(1 for r in detailed_results if r.get('correct_prediction', False)),
                'failed_tests': sum(1 for r in detailed_results if not r.get('correct_prediction', False)),
                'error_tests': sum(1 for r in detailed_results if 'error' in r)
            }
        }
        
        print(f"\n📊 Validation Results:")
        print(f"  Overall Accuracy: {report['overall_accuracy']:.3f}")
        print(f"  Precision: {report['overall_precision']:.3f}")
        print(f"  Recall: {report['overall_recall']:.3f}")
        print(f"  F1 Score: {report['overall_f1_score']:.3f}")
        print(f"  Avg Processing Time: {report['performance_metrics']['avg_processing_time']:.3f}s")
        
        return report
    
    def _create_synthetic_test_image(self, test_case: ICAOTestCase) -> np.ndarray:
        """Create synthetic test image for testing purposes"""
        # Create a basic synthetic image based on test case requirements
        image = np.ones((600, 480, 3), dtype=np.uint8) * 255  # White background
        
        # Add a simple face representation
        face_center = (240, 300)
        face_radius = 80
        
        # Draw face (skin tone)
        cv2.circle(image, face_center, face_radius, (220, 180, 140), -1)
        
        # Add eyes
        eye_y = face_center[1] - 20
        cv2.circle(image, (face_center[0] - 25, eye_y), 8, (50, 50, 50), -1)
        cv2.circle(image, (face_center[0] + 25, eye_y), 8, (50, 50, 50), -1)
        
        # Add mouth
        mouth_y = face_center[1] + 30
        cv2.ellipse(image, (face_center[0], mouth_y), (15, 5), 0, 0, 180, (100, 50, 50), 2)
        
        # Modify based on test case violations
        if "tinted_glasses" in test_case.name:
            # Add tinted glasses
            cv2.rectangle(image, (face_center[0] - 40, eye_y - 15), 
                         (face_center[0] + 40, eye_y + 15), (50, 50, 50), -1)
        
        if "smiling" in test_case.name:
            # Make mouth appear to be smiling
            cv2.ellipse(image, (face_center[0], mouth_y), (20, 10), 0, 0, 180, (100, 50, 50), 3)
        
        if "colored_background" in test_case.name:
            # Change background color
            image[:, :] = (200, 200, 255)  # Light blue background
            # Redraw face
            cv2.circle(image, face_center, face_radius, (220, 180, 140), -1)
            cv2.circle(image, (face_center[0] - 25, eye_y), 8, (50, 50, 50), -1)
            cv2.circle(image, (face_center[0] + 25, eye_y), 8, (50, 50, 50), -1)
            cv2.ellipse(image, (face_center[0], mouth_y), (15, 5), 0, 0, 180, (100, 50, 50), 2)
        
        if "blurry" in test_case.name:
            # Apply blur
            image = cv2.GaussianBlur(image, (15, 15), 5)
        
        return image
    
    def _get_violation_category(self, rule_id: str) -> str:
        """Get violation category from rule ID"""
        if "3.2" in rule_id or "3.3" in rule_id:
            return "glasses" if "3.2" in rule_id else "head_covering"
        elif "4.1" in rule_id:
            return "expression"
        elif "4.2" in rule_id:
            return "positioning"
        elif "5." in rule_id:
            return "quality"
        elif "6." in rule_id:
            return "lighting" if "6.2" in rule_id or "6.3" in rule_id else "background"
        return "unknown"


@pytest.fixture
def icao_validator():
    """Fixture for ICAO standards validator"""
    return ICAOStandardsValidator()


class TestICAOStandardsValidation:
    """Test suite for ICAO standards validation"""
    
    def test_compliance_detection_accuracy(self, icao_validator):
        """Test compliance detection accuracy against known violations"""
        report = icao_validator.validate_compliance_detection_accuracy()
        
        # Assert minimum accuracy requirements
        assert report['overall_accuracy'] >= 0.85, f"Overall accuracy {report['overall_accuracy']:.3f} below threshold"
        assert report['overall_precision'] >= 0.80, f"Precision {report['overall_precision']:.3f} below threshold"
        assert report['overall_recall'] >= 0.80, f"Recall {report['overall_recall']:.3f} below threshold"
        
        # Assert performance requirements
        assert report['performance_metrics']['avg_processing_time'] <= 5.0, \
            f"Average processing time {report['performance_metrics']['avg_processing_time']:.3f}s exceeds threshold"
        
        # Save detailed report
        report_path = Path("test_results/icao_validation_report.json")
        report_path.parent.mkdir(exist_ok=True)
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"📄 Detailed report saved to: {report_path}")
    
    def test_category_specific_accuracy(self, icao_validator):
        """Test accuracy for specific violation categories"""
        report = icao_validator.validate_compliance_detection_accuracy()
        
        # Check category-specific performance
        required_categories = ['glasses', 'expression', 'quality', 'lighting', 'background']
        
        for category in required_categories:
            if category in report['category_metrics']:
                metrics = report['category_metrics'][category]
                assert metrics['accuracy'] >= 0.75, \
                    f"{category} accuracy {metrics['accuracy']:.3f} below threshold"
                print(f"✅ {category.title()} category accuracy: {metrics['accuracy']:.3f}")
    
    def test_processing_performance(self, icao_validator):
        """Test processing performance requirements"""
        # Test with various image sizes
        test_sizes = [(480, 600), (960, 1200), (1920, 2400)]
        
        for width, height in test_sizes:
            # Create test image
            test_image = np.ones((height, width, 3), dtype=np.uint8) * 255
            
            # Add simple face
            face_center = (width // 2, height // 2)
            face_radius = min(width, height) // 8
            cv2.circle(test_image, face_center, face_radius, (220, 180, 140), -1)
            
            # Measure processing time
            start_time = time.time()
            result = icao_validator.processing_controller.process_image(
                test_image, 
                format_name="ICAO",
                options={"validate_only": True}
            )
            processing_time = time.time() - start_time
            
            # Assert performance requirements
            max_time = 3.0 if width <= 960 else 8.0  # Larger images can take longer
            assert processing_time <= max_time, \
                f"Processing time {processing_time:.3f}s exceeds {max_time}s for {width}x{height} image"
            
            print(f"✅ {width}x{height} processed in {processing_time:.3f}s")


if __name__ == "__main__":
    # Run validation when executed directly
    validator = ICAOStandardsValidator()
    report = validator.validate_compliance_detection_accuracy()
    
    print("\n" + "="*60)
    print("ICAO STANDARDS VALIDATION COMPLETE")
    print("="*60)
    print(f"Overall Accuracy: {report['overall_accuracy']:.1%}")
    print(f"Precision: {report['overall_precision']:.1%}")
    print(f"Recall: {report['overall_recall']:.1%}")
    print(f"F1 Score: {report['overall_f1_score']:.1%}")
    print(f"Average Processing Time: {report['performance_metrics']['avg_processing_time']:.3f}s")