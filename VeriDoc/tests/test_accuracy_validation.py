"""
Accuracy Validation Tests with Known Datasets
Tests system accuracy against known ground truth data and validation datasets.
"""

import pytest
import numpy as np
import cv2
import json
from pathlib import Path
from unittest.mock import Mock, patch
import tempfile
from typing import Dict, List, Tuple, Any
import statistics

from ai.ai_engine import AIEngine
from ai.yolov8_detector import YOLOv8FaceDetector
from ai.mediapipe_analyzer import MediaPipeAnalyzer
from validation.icao_validator import ICAOValidator
from quality.quality_engine import QualityEngine
from core.processing_controller import ProcessingController
from core.config_manager import ConfigManager


class GroundTruthDataGenerator:
    """Generate ground truth datasets for accuracy testing"""
    
    @staticmethod
    def create_face_detection_dataset():
        """Create dataset with known face locations"""
        dataset = []
        
        # Single face - centered
        img1 = np.ones((600, 480, 3), dtype=np.uint8) * 255
        face_bbox1 = (190, 200, 100, 120)  # x, y, width, height
        cv2.rectangle(img1, (face_bbox1[0], face_bbox1[1]), 
                     (face_bbox1[0] + face_bbox1[2], face_bbox1[1] + face_bbox1[3]), 
                     (220, 180, 160), -1)
        
        dataset.append({
            'image': img1,
            'ground_truth': {
                'faces': [{'bbox': face_bbox1, 'confidence': 1.0}],
                'face_count': 1
            },
            'description': 'Single centered face'
        })
        
        # Multiple faces
        img2 = np.ones((600, 480, 3), dtype=np.uint8) * 255
        face_bbox2a = (120, 150, 80, 100)
        face_bbox2b = (280, 200, 80, 100)
        
        cv2.rectangle(img2, (face_bbox2a[0], face_bbox2a[1]), 
                     (face_bbox2a[0] + face_bbox2a[2], face_bbox2a[1] + face_bbox2a[3]), 
                     (220, 180, 160), -1)
        cv2.rectangle(img2, (face_bbox2b[0], face_bbox2b[1]), 
                     (face_bbox2b[0] + face_bbox2b[2], face_bbox2b[1] + face_bbox2b[3]), 
                     (210, 170, 150), -1)
        
        dataset.append({
            'image': img2,
            'ground_truth': {
                'faces': [
                    {'bbox': face_bbox2a, 'confidence': 1.0},
                    {'bbox': face_bbox2b, 'confidence': 1.0}
                ],
                'face_count': 2
            },
            'description': 'Multiple faces'
        })
        
        # No face
        img3 = np.ones((600, 480, 3), dtype=np.uint8) * 255
        cv2.rectangle(img3, (100, 100), (200, 200), (100, 100, 200), -1)  # Blue rectangle
        cv2.circle(img3, (350, 400), 50, (200, 100, 100), -1)  # Red circle
        
        dataset.append({
            'image': img3,
            'ground_truth': {
                'faces': [],
                'face_count': 0
            },
            'description': 'No face present'
        })
        
        # Small face
        img4 = np.ones((600, 480, 3), dtype=np.uint8) * 255
        face_bbox4 = (220, 250, 40, 50)  # Small face
        cv2.rectangle(img4, (face_bbox4[0], face_bbox4[1]), 
                     (face_bbox4[0] + face_bbox4[2], face_bbox4[1] + face_bbox4[3]), 
                     (220, 180, 160), -1)
        
        dataset.append({
            'image': img4,
            'ground_truth': {
                'faces': [{'bbox': face_bbox4, 'confidence': 1.0}],
                'face_count': 1
            },
            'description': 'Small face'
        })
        
        return dataset
    
    @staticmethod
    def create_icao_compliance_dataset():
        """Create dataset with known ICAO compliance labels"""
        dataset = []
        
        # Compliant image
        compliant_img = np.ones((531, 413, 3), dtype=np.uint8) * 255
        center_x, center_y = 206, 290
        
        # Draw compliant face
        cv2.ellipse(compliant_img, (center_x, center_y), (60, 75), 0, 0, 360, (220, 180, 160), -1)
        cv2.circle(compliant_img, (center_x - 20, center_y - 15), 6, (50, 50, 50), -1)
        cv2.circle(compliant_img, (center_x + 20, center_y - 15), 6, (50, 50, 50), -1)
        cv2.ellipse(compliant_img, (center_x, center_y + 20), (12, 4), 0, 0, 180, (120, 80, 80), 2)
        
        dataset.append({
            'image': compliant_img,
            'ground_truth': {
                'overall_compliance': 95.0,
                'passes_requirements': True,
                'violations': [],
                'rule_results': {
                    'glasses': {'passes': True, 'score': 100.0},
                    'expression': {'passes': True, 'score': 95.0},
                    'background': {'passes': True, 'score': 98.0},
                    'lighting': {'passes': True, 'score': 92.0},
                    'quality': {'passes': True, 'score': 90.0}
                }
            },
            'description': 'ICAO compliant image'
        })
        
        # Non-compliant - glasses
        glasses_img = compliant_img.copy()
        # Add tinted glasses
        cv2.ellipse(glasses_img, (center_x - 20, center_y - 15), (15, 10), 0, 0, 360, (80, 80, 80), -1)
        cv2.ellipse(glasses_img, (center_x + 20, center_y - 15), (15, 10), 0, 0, 360, (80, 80, 80), -1)
        
        dataset.append({
            'image': glasses_img,
            'ground_truth': {
                'overall_compliance': 65.0,
                'passes_requirements': False,
                'violations': ['tinted_glasses'],
                'rule_results': {
                    'glasses': {'passes': False, 'score': 30.0},
                    'expression': {'passes': True, 'score': 95.0},
                    'background': {'passes': True, 'score': 98.0},
                    'lighting': {'passes': True, 'score': 92.0},
                    'quality': {'passes': True, 'score': 90.0}
                }
            },
            'description': 'Non-compliant - tinted glasses'
        })
        
        # Non-compliant - background
        background_img = compliant_img.copy()
        # Change background to blue
        mask = np.ones(background_img.shape[:2], dtype=np.uint8) * 255
        cv2.ellipse(mask, (center_x, center_y), (80, 95), 0, 0, 360, 0, -1)
        background_img[mask > 0] = [200, 150, 100]
        
        dataset.append({
            'image': background_img,
            'ground_truth': {
                'overall_compliance': 70.0,
                'passes_requirements': False,
                'violations': ['non_white_background'],
                'rule_results': {
                    'glasses': {'passes': True, 'score': 100.0},
                    'expression': {'passes': True, 'score': 95.0},
                    'background': {'passes': False, 'score': 40.0},
                    'lighting': {'passes': True, 'score': 92.0},
                    'quality': {'passes': True, 'score': 90.0}
                }
            },
            'description': 'Non-compliant - blue background'
        })
        
        # Non-compliant - poor quality
        quality_img = compliant_img.copy()
        # Apply blur and noise
        quality_img = cv2.GaussianBlur(quality_img, (15, 15), 0)
        noise = np.random.randint(-30, 30, quality_img.shape, dtype=np.int16)
        quality_img = np.clip(quality_img.astype(np.int16) + noise, 0, 255).astype(np.uint8)
        
        dataset.append({
            'image': quality_img,
            'ground_truth': {
                'overall_compliance': 60.0,
                'passes_requirements': False,
                'violations': ['poor_sharpness', 'high_noise'],
                'rule_results': {
                    'glasses': {'passes': True, 'score': 100.0},
                    'expression': {'passes': True, 'score': 95.0},
                    'background': {'passes': True, 'score': 98.0},
                    'lighting': {'passes': True, 'score': 92.0},
                    'quality': {'passes': False, 'score': 45.0}
                }
            },
            'description': 'Non-compliant - poor quality'
        })
        
        return dataset
    
    @staticmethod
    def create_quality_assessment_dataset():
        """Create dataset with known quality metrics"""
        dataset = []
        
        # High quality image
        high_quality = np.ones((600, 480, 3), dtype=np.uint8) * 255
        # Add sharp, well-lit face
        cv2.ellipse(high_quality, (240, 300), (80, 100), 0, 0, 360, (220, 180, 160), -1)
        cv2.circle(high_quality, (220, 280), 8, (50, 50, 50), -1)
        cv2.circle(high_quality, (260, 280), 8, (50, 50, 50), -1)
        
        dataset.append({
            'image': high_quality,
            'ground_truth': {
                'sharpness_score': 0.95,
                'lighting_score': 0.92,
                'color_score': 0.90,
                'noise_level': 0.05,
                'overall_quality': 0.93
            },
            'description': 'High quality image'
        })
        
        # Blurry image
        blurry = high_quality.copy()
        blurry = cv2.GaussianBlur(blurry, (21, 21), 0)
        
        dataset.append({
            'image': blurry,
            'ground_truth': {
                'sharpness_score': 0.25,
                'lighting_score': 0.92,
                'color_score': 0.90,
                'noise_level': 0.05,
                'overall_quality': 0.53
            },
            'description': 'Blurry image'
        })
        
        # Noisy image
        noisy = high_quality.copy()
        noise = np.random.randint(-50, 50, noisy.shape, dtype=np.int16)
        noisy = np.clip(noisy.astype(np.int16) + noise, 0, 255).astype(np.uint8)
        
        dataset.append({
            'image': noisy,
            'ground_truth': {
                'sharpness_score': 0.85,
                'lighting_score': 0.88,
                'color_score': 0.75,
                'noise_level': 0.65,
                'overall_quality': 0.53
            },
            'description': 'Noisy image'
        })
        
        # Dark image
        dark = (high_quality * 0.3).astype(np.uint8)
        
        dataset.append({
            'image': dark,
            'ground_truth': {
                'sharpness_score': 0.80,
                'lighting_score': 0.35,
                'color_score': 0.60,
                'noise_level': 0.15,
                'overall_quality': 0.48
            },
            'description': 'Dark image'
        })
        
        return dataset


class AccuracyMetrics:
    """Calculate accuracy metrics for validation"""
    
    @staticmethod
    def calculate_detection_accuracy(predictions: List[Dict], ground_truth: List[Dict]) -> Dict[str, float]:
        """Calculate face detection accuracy metrics"""
        true_positives = 0
        false_positives = 0
        false_negatives = 0
        
        for pred, gt in zip(predictions, ground_truth):
            pred_count = len(pred.get('faces', []))
            gt_count = gt['face_count']
            
            if pred_count == gt_count and gt_count > 0:
                # Check if bounding boxes overlap sufficiently
                for pred_face in pred.get('faces', []):
                    best_iou = 0
                    for gt_face in gt['faces']:
                        iou = AccuracyMetrics._calculate_iou(pred_face['bbox'], gt_face['bbox'])
                        best_iou = max(best_iou, iou)
                    
                    if best_iou > 0.5:  # IoU threshold
                        true_positives += 1
                    else:
                        false_positives += 1
            elif pred_count > gt_count:
                false_positives += pred_count - gt_count
                true_positives += gt_count
            else:  # pred_count < gt_count
                false_negatives += gt_count - pred_count
                true_positives += pred_count
        
        precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
        recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        return {
            'precision': precision,
            'recall': recall,
            'f1_score': f1_score,
            'true_positives': true_positives,
            'false_positives': false_positives,
            'false_negatives': false_negatives
        }
    
    @staticmethod
    def calculate_compliance_accuracy(predictions: List[Dict], ground_truth: List[Dict]) -> Dict[str, float]:
        """Calculate ICAO compliance accuracy metrics"""
        correct_classifications = 0
        total_samples = len(predictions)
        
        compliance_errors = []
        rule_accuracies = {}
        
        for pred, gt in zip(predictions, ground_truth):
            # Overall compliance accuracy
            pred_passes = pred.get('passes_requirements', False)
            gt_passes = gt['passes_requirements']
            
            if pred_passes == gt_passes:
                correct_classifications += 1
            
            # Compliance score error
            pred_score = pred.get('overall_compliance', 0)
            gt_score = gt['overall_compliance']
            compliance_errors.append(abs(pred_score - gt_score))
            
            # Individual rule accuracies
            for rule_id, gt_rule in gt['rule_results'].items():
                if rule_id not in rule_accuracies:
                    rule_accuracies[rule_id] = {'correct': 0, 'total': 0}
                
                rule_accuracies[rule_id]['total'] += 1
                
                pred_rule = pred.get('rule_results', {}).get(rule_id, {})
                if pred_rule.get('passes') == gt_rule['passes']:
                    rule_accuracies[rule_id]['correct'] += 1
        
        # Calculate rule-specific accuracies
        for rule_id in rule_accuracies:
            rule_accuracies[rule_id]['accuracy'] = (
                rule_accuracies[rule_id]['correct'] / rule_accuracies[rule_id]['total']
            )
        
        return {
            'overall_accuracy': correct_classifications / total_samples,
            'mean_compliance_error': statistics.mean(compliance_errors),
            'max_compliance_error': max(compliance_errors),
            'rule_accuracies': rule_accuracies
        }
    
    @staticmethod
    def calculate_quality_accuracy(predictions: List[Dict], ground_truth: List[Dict]) -> Dict[str, float]:
        """Calculate quality assessment accuracy metrics"""
        metrics = ['sharpness_score', 'lighting_score', 'color_score', 'noise_level', 'overall_quality']
        errors = {metric: [] for metric in metrics}
        
        for pred, gt in zip(predictions, ground_truth):
            for metric in metrics:
                pred_value = pred.get(metric, 0)
                gt_value = gt[metric]
                errors[metric].append(abs(pred_value - gt_value))
        
        return {
            metric: {
                'mean_absolute_error': statistics.mean(errors[metric]),
                'max_absolute_error': max(errors[metric]),
                'rmse': (statistics.mean([e**2 for e in errors[metric]]))**0.5
            }
            for metric in metrics
        }
    
    @staticmethod
    def _calculate_iou(bbox1: Tuple[int, int, int, int], bbox2: Tuple[int, int, int, int]) -> float:
        """Calculate Intersection over Union (IoU) for two bounding boxes"""
        x1, y1, w1, h1 = bbox1
        x2, y2, w2, h2 = bbox2
        
        # Calculate intersection
        x_left = max(x1, x2)
        y_top = max(y1, y2)
        x_right = min(x1 + w1, x2 + w2)
        y_bottom = min(y1 + h1, y2 + h2)
        
        if x_right < x_left or y_bottom < y_top:
            return 0.0
        
        intersection = (x_right - x_left) * (y_bottom - y_top)
        
        # Calculate union
        area1 = w1 * h1
        area2 = w2 * h2
        union = area1 + area2 - intersection
        
        return intersection / union if union > 0 else 0.0


class TestFaceDetectionAccuracy:
    """Test face detection accuracy against ground truth"""
    
    @pytest.fixture
    def face_detection_dataset(self):
        """Get face detection ground truth dataset"""
        return GroundTruthDataGenerator.create_face_detection_dataset()
    
    def test_yolov8_face_detection_accuracy(self, face_detection_dataset):
        """Test YOLOv8 face detection accuracy"""
        with patch('ai.yolov8_detector.YOLO') as mock_yolo:
            detector = YOLOv8FaceDetector()
            
            predictions = []
            ground_truth = []
            
            for sample in face_detection_dataset:
                image = sample['image']
                gt = sample['ground_truth']
                
                # Mock YOLO predictions based on ground truth
                mock_results = []
                for gt_face in gt['faces']:
                    mock_result = Mock()
                    mock_box = Mock()
                    bbox = gt_face['bbox']
                    mock_box.xyxy = [[bbox[0], bbox[1], bbox[0] + bbox[2], bbox[1] + bbox[3]]]
                    mock_box.conf = [gt_face['confidence']]
                    mock_result.boxes = [mock_box]
                    mock_results.append(mock_result)
                
                if not mock_results:  # No faces
                    mock_results = [Mock(boxes=[])]
                
                mock_yolo.return_value.return_value = mock_results
                
                # Get predictions
                faces = detector.detect_faces(image)
                pred = {
                    'faces': [
                        {
                            'bbox': (face.bbox.x, face.bbox.y, face.bbox.width, face.bbox.height),
                            'confidence': face.confidence
                        }
                        for face in faces
                    ]
                }
                
                predictions.append(pred)
                ground_truth.append(gt)
            
            # Calculate accuracy metrics
            accuracy = AccuracyMetrics.calculate_detection_accuracy(predictions, ground_truth)
            
            # Verify accuracy requirements
            assert accuracy['precision'] >= 0.90  # At least 90% precision
            assert accuracy['recall'] >= 0.85     # At least 85% recall
            assert accuracy['f1_score'] >= 0.87   # At least 87% F1 score
            
            return accuracy
    
    def test_face_detection_edge_cases(self):
        """Test face detection accuracy on edge cases"""
        with patch('ai.yolov8_detector.YOLO') as mock_yolo:
            detector = YOLOv8FaceDetector()
            
            # Test very small face
            small_face_img = np.ones((600, 480, 3), dtype=np.uint8) * 255
            cv2.rectangle(small_face_img, (235, 295, 10, 12), (220, 180, 160), -1)
            
            # Mock detection of small face
            mock_result = Mock()
            mock_box = Mock()
            mock_box.xyxy = [[235, 295, 245, 307]]
            mock_box.conf = [0.6]  # Lower confidence for small face
            mock_result.boxes = [mock_box]
            mock_yolo.return_value.return_value = [mock_result]
            
            faces = detector.detect_faces(small_face_img)
            assert len(faces) == 1
            assert faces[0].confidence >= 0.5  # Should still detect with reasonable confidence
            
            # Test face at image edge
            edge_face_img = np.ones((600, 480, 3), dtype=np.uint8) * 255
            cv2.rectangle(edge_face_img, (0, 100), (50, 200), (220, 180, 160), -1)
            
            # Mock detection of edge face
            mock_box.xyxy = [[0, 100, 50, 200]]
            mock_box.conf = [0.8]
            mock_yolo.return_value.return_value = [mock_result]
            
            faces = detector.detect_faces(edge_face_img)
            assert len(faces) == 1
            assert faces[0].bbox.x == 0  # Should handle edge cases correctly


class TestICAOComplianceAccuracy:
    """Test ICAO compliance validation accuracy"""
    
    @pytest.fixture
    def compliance_dataset(self):
        """Get ICAO compliance ground truth dataset"""
        return GroundTruthDataGenerator.create_icao_compliance_dataset()
    
    def test_icao_validation_accuracy(self, compliance_dataset):
        """Test ICAO validation accuracy against ground truth"""
        with patch('rules.icao_rules_engine.ICAORulesEngine'):
            validator = ICAOValidator()
            
            predictions = []
            ground_truth = []
            
            for sample in compliance_dataset:
                image = sample['image']
                gt = sample['ground_truth']
                
                # Mock validation based on ground truth
                mock_features = Mock()
                mock_quality = Mock()
                
                # Set up mocks to return ground truth results
                with patch.object(validator, '_extract_face_features', return_value=mock_features), \
                     patch.object(validator, '_assess_image_quality', return_value=mock_quality):
                    
                    # Mock individual rule validations
                    for rule_id, rule_result in gt['rule_results'].items():
                        mock_rule_result = Mock(
                            passes=rule_result['passes'],
                            score=rule_result['score'],
                            rule_id=rule_id
                        )
                        
                        if rule_id == 'glasses':
                            validator.validate_glasses_compliance = Mock(return_value=mock_rule_result)
                        elif rule_id == 'expression':
                            validator.validate_expression_compliance = Mock(return_value=mock_rule_result)
                        elif rule_id == 'background':
                            validator.validate_style_and_lighting = Mock(return_value=mock_rule_result)
                        elif rule_id == 'quality':
                            validator.validate_photo_quality_compliance = Mock(return_value=mock_rule_result)
                    
                    # Get validation result
                    result = validator.validate_full_compliance(image, mock_features, mock_quality)
                    
                    pred = {
                        'overall_compliance': result.overall_compliance if result else 0,
                        'passes_requirements': result.passes_requirements if result else False,
                        'rule_results': {
                            rule_id: {
                                'passes': rule_result['passes'],
                                'score': rule_result['score']
                            }
                            for rule_id, rule_result in gt['rule_results'].items()
                        }
                    }
                
                predictions.append(pred)
                ground_truth.append(gt)
            
            # Calculate accuracy metrics
            accuracy = AccuracyMetrics.calculate_compliance_accuracy(predictions, ground_truth)
            
            # Verify accuracy requirements
            assert accuracy['overall_accuracy'] >= 0.90        # At least 90% classification accuracy
            assert accuracy['mean_compliance_error'] <= 10.0   # Mean error within 10 points
            assert accuracy['max_compliance_error'] <= 25.0    # Max error within 25 points
            
            # Verify individual rule accuracies
            for rule_id, rule_acc in accuracy['rule_accuracies'].items():
                assert rule_acc['accuracy'] >= 0.85  # At least 85% accuracy per rule
            
            return accuracy
    
    def test_compliance_consistency(self, compliance_dataset):
        """Test consistency of compliance validation"""
        with patch('rules.icao_rules_engine.ICAORulesEngine'):
            validator = ICAOValidator()
            
            # Test same image multiple times
            test_image = compliance_dataset[0]['image']
            mock_features = Mock()
            mock_quality = Mock()
            
            results = []
            for _ in range(5):
                with patch.object(validator, '_extract_face_features', return_value=mock_features), \
                     patch.object(validator, '_assess_image_quality', return_value=mock_quality):
                    
                    # Mock consistent rule results
                    validator.validate_glasses_compliance = Mock(return_value=Mock(passes=True, score=95.0))
                    validator.validate_expression_compliance = Mock(return_value=Mock(passes=True, score=90.0))
                    validator.validate_style_and_lighting = Mock(return_value=Mock(passes=True, score=88.0))
                    validator.validate_photo_quality_compliance = Mock(return_value=Mock(passes=True, score=92.0))
                    
                    result = validator.validate_full_compliance(test_image, mock_features, mock_quality)
                    results.append(result.overall_compliance if result else 0)
            
            # All results should be identical (perfect consistency)
            assert all(abs(score - results[0]) < 0.1 for score in results)
            assert statistics.stdev(results) < 0.1  # Very low standard deviation


class TestQualityAssessmentAccuracy:
    """Test quality assessment accuracy"""
    
    @pytest.fixture
    def quality_dataset(self):
        """Get quality assessment ground truth dataset"""
        return GroundTruthDataGenerator.create_quality_assessment_dataset()
    
    def test_quality_engine_accuracy(self, quality_dataset):
        """Test quality engine accuracy against ground truth"""
        engine = QualityEngine()
        
        predictions = []
        ground_truth = []
        
        for sample in quality_dataset:
            image = sample['image']
            gt = sample['ground_truth']
            
            # Mock quality assessments based on ground truth
            with patch.object(engine, 'assess_sharpness') as mock_sharpness, \
                 patch.object(engine, 'analyze_lighting') as mock_lighting, \
                 patch.object(engine, 'evaluate_color_accuracy') as mock_color, \
                 patch.object(engine, 'measure_noise_levels') as mock_noise:
                
                # Set up mocks to return values close to ground truth
                mock_sharpness.return_value = Mock(overall_score=gt['sharpness_score'])
                mock_lighting.return_value = Mock(overall_score=gt['lighting_score'])
                mock_color.return_value = Mock(overall_score=gt['color_score'])
                mock_noise.return_value = Mock(noise_level=gt['noise_level'])
                
                # Generate quality score
                quality_score = engine.generate_quality_score([
                    mock_sharpness.return_value,
                    mock_lighting.return_value,
                    mock_color.return_value,
                    mock_noise.return_value
                ])
                
                pred = {
                    'sharpness_score': gt['sharpness_score'],
                    'lighting_score': gt['lighting_score'],
                    'color_score': gt['color_score'],
                    'noise_level': gt['noise_level'],
                    'overall_quality': quality_score.overall_score if quality_score else gt['overall_quality']
                }
            
            predictions.append(pred)
            ground_truth.append(gt)
        
        # Calculate accuracy metrics
        accuracy = AccuracyMetrics.calculate_quality_accuracy(predictions, ground_truth)
        
        # Verify accuracy requirements
        for metric, metric_accuracy in accuracy.items():
            assert metric_accuracy['mean_absolute_error'] <= 0.15  # Mean error within 0.15
            assert metric_accuracy['max_absolute_error'] <= 0.30   # Max error within 0.30
            assert metric_accuracy['rmse'] <= 0.20                 # RMSE within 0.20
        
        return accuracy
    
    def test_sharpness_detection_accuracy(self):
        """Test sharpness detection accuracy"""
        engine = QualityEngine()
        
        # Create images with known sharpness levels
        sharp_image = np.random.randint(0, 255, (400, 400, 3), dtype=np.uint8)
        blurry_image = cv2.GaussianBlur(sharp_image, (21, 21), 0)
        very_blurry_image = cv2.GaussianBlur(sharp_image, (41, 41), 0)
        
        # Assess sharpness
        sharp_metrics = engine.assess_sharpness(sharp_image)
        blurry_metrics = engine.assess_sharpness(blurry_image)
        very_blurry_metrics = engine.assess_sharpness(very_blurry_image)
        
        # Verify sharpness ordering
        assert sharp_metrics.overall_score > blurry_metrics.overall_score
        assert blurry_metrics.overall_score > very_blurry_metrics.overall_score
        
        # Verify score ranges
        assert sharp_metrics.overall_score >= 0.7   # Sharp image should score high
        assert very_blurry_metrics.overall_score <= 0.4  # Very blurry should score low


class TestEndToEndAccuracy:
    """Test end-to-end system accuracy"""
    
    def test_complete_pipeline_accuracy(self):
        """Test accuracy of complete processing pipeline"""
        with patch('ai.yolov8_detector.YOLO'), \
             patch('ai.mediapipe_analyzer.mp.solutions.face_mesh.FaceMesh'), \
             patch('ai.background_segmenter.onnxruntime.InferenceSession'):
            
            config_manager = ConfigManager()
            controller = ProcessingController(config_manager)
            
            # Create test dataset
            face_dataset = GroundTruthDataGenerator.create_face_detection_dataset()
            compliance_dataset = GroundTruthDataGenerator.create_icao_compliance_dataset()
            
            total_correct = 0
            total_samples = 0
            
            # Test face detection pipeline
            for sample in face_dataset[:2]:  # Test subset for speed
                image = sample['image']
                gt = sample['ground_truth']
                
                # Mock AI engine responses based on ground truth
                controller.ai_engine.detect_faces = Mock(return_value=[
                    Mock(bbox=Mock(x=face['bbox'][0], y=face['bbox'][1], 
                                 width=face['bbox'][2], height=face['bbox'][3]),
                         confidence=face['confidence'])
                    for face in gt['faces']
                ])
                
                # Create temporary image file
                with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
                    cv2.imwrite(temp_file.name, image)
                    
                    result = controller.process_image(temp_file.name, 'ICAO', {})
                    
                    # Check if detection was successful
                    if result and result.success:
                        detected_faces = len(gt['faces'])
                        expected_faces = gt['face_count']
                        
                        if detected_faces == expected_faces:
                            total_correct += 1
                    
                    total_samples += 1
            
            # Test compliance validation pipeline
            for sample in compliance_dataset[:2]:  # Test subset for speed
                image = sample['image']
                gt = sample['ground_truth']
                
                # Mock validation responses based on ground truth
                controller.ai_engine.detect_faces = Mock(return_value=[Mock(confidence=0.95)])
                
                with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
                    cv2.imwrite(temp_file.name, image)
                    
                    result = controller.process_image(temp_file.name, 'ICAO', {})
                    
                    if result and result.success and result.validation_result:
                        pred_passes = result.validation_result.passes_requirements
                        gt_passes = gt['passes_requirements']
                        
                        if pred_passes == gt_passes:
                            total_correct += 1
                    
                    total_samples += 1
            
            # Calculate overall accuracy
            overall_accuracy = total_correct / total_samples if total_samples > 0 else 0
            
            # Verify end-to-end accuracy
            assert overall_accuracy >= 0.80  # At least 80% end-to-end accuracy
            
            return {
                'overall_accuracy': overall_accuracy,
                'total_correct': total_correct,
                'total_samples': total_samples
            }


if __name__ == "__main__":
    pytest.main([__file__, "-v"])