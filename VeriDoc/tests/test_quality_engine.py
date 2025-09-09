"""
Unit tests for the Advanced Quality Engine

Tests comprehensive quality assessment including sharpness, lighting,
color accuracy, noise, and resolution analysis.
"""

import unittest
import numpy as np
import cv2
from unittest.mock import Mock, patch
import tempfile
import os

from quality.quality_engine import QualityEngine, QualityMetrics, OverallQualityScore
from quality.sharpness_analyzer import SharpnessAnalyzer
from quality.lighting_analyzer import LightingAnalyzer
from quality.color_analyzer import ColorAnalyzer
from quality.noise_analyzer import NoiseAnalyzer
from quality.resolution_validator import ResolutionValidator


class TestQualityEngine(unittest.TestCase):
    """Test cases for QualityEngine class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.quality_engine = QualityEngine()
        
        # Create test images
        self.test_image_color = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        self.test_image_gray = np.random.randint(0, 255, (480, 640), dtype=np.uint8)
        self.face_region = np.random.randint(0, 255, (200, 200, 3), dtype=np.uint8)
        
        # Create sharp test image
        self.sharp_image = self._create_sharp_test_image()
        
        # Create blurry test image
        self.blurry_image = self._create_blurry_test_image()
        
        # Create noisy test image
        self.noisy_image = self._create_noisy_test_image()
    
    def _create_sharp_test_image(self):
        """Create a sharp test image with clear edges."""
        image = np.zeros((480, 640), dtype=np.uint8)
        
        # Add sharp geometric shapes
        cv2.rectangle(image, (100, 100), (200, 200), 255, -1)
        cv2.circle(image, (400, 300), 50, 128, -1)
        cv2.line(image, (0, 240), (640, 240), 200, 2)
        
        return image
    
    def _create_blurry_test_image(self):
        """Create a blurry test image."""
        sharp_image = self._create_sharp_test_image()
        # Apply Gaussian blur
        blurry_image = cv2.GaussianBlur(sharp_image, (15, 15), 5.0)
        return blurry_image
    
    def _create_noisy_test_image(self):
        """Create a noisy test image."""
        clean_image = self._create_sharp_test_image()
        # Add Gaussian noise
        noise = np.random.normal(0, 25, clean_image.shape).astype(np.int16)
        noisy_image = np.clip(clean_image.astype(np.int16) + noise, 0, 255).astype(np.uint8)
        return noisy_image
    
    def test_quality_engine_initialization(self):
        """Test QualityEngine initialization."""
        self.assertIsInstance(self.quality_engine, QualityEngine)
        self.assertIsInstance(self.quality_engine.sharpness_analyzer, SharpnessAnalyzer)
        self.assertIsInstance(self.quality_engine.lighting_analyzer, LightingAnalyzer)
        self.assertIsInstance(self.quality_engine.color_analyzer, ColorAnalyzer)
        self.assertIsInstance(self.quality_engine.noise_analyzer, NoiseAnalyzer)
        self.assertIsInstance(self.quality_engine.resolution_validator, ResolutionValidator)
    
    def test_assess_image_quality_color(self):
        """Test comprehensive quality assessment on color image."""
        result = self.quality_engine.assess_image_quality(self.test_image_color, self.face_region)
        
        self.assertIsInstance(result, QualityMetrics)
        self.assertIsInstance(result.overall_score, float)
        self.assertGreaterEqual(result.overall_score, 0.0)
        self.assertLessEqual(result.overall_score, 100.0)
        
        # Check individual scores
        self.assertIsInstance(result.sharpness_score, float)
        self.assertIsInstance(result.lighting_score, float)
        self.assertIsInstance(result.color_score, float)
        self.assertIsInstance(result.noise_score, float)
        self.assertIsInstance(result.resolution_score, float)
        
        # Check detailed metrics
        self.assertIn('sharpness', result.detailed_metrics)
        self.assertIn('lighting', result.detailed_metrics)
        self.assertIn('color', result.detailed_metrics)
        self.assertIn('noise', result.detailed_metrics)
        self.assertIn('resolution', result.detailed_metrics)
        
        # Check issues and suggestions
        self.assertIsInstance(result.issues, list)
        self.assertIsInstance(result.suggestions, list)
    
    def test_assess_image_quality_grayscale(self):
        """Test quality assessment on grayscale image."""
        result = self.quality_engine.assess_image_quality(self.test_image_gray)
        
        self.assertIsInstance(result, QualityMetrics)
        self.assertIsInstance(result.overall_score, float)
        self.assertGreaterEqual(result.overall_score, 0.0)
        self.assertLessEqual(result.overall_score, 100.0)
    
    def test_assess_sharpness(self):
        """Test sharpness assessment."""
        # Test sharp image
        sharp_result = self.quality_engine.assess_sharpness(self.sharp_image)
        self.assertIsInstance(sharp_result, dict)
        self.assertIn('overall_score', sharp_result)
        
        # Test blurry image
        blurry_result = self.quality_engine.assess_sharpness(self.blurry_image)
        
        # Sharp image should have higher score than blurry image
        self.assertGreater(sharp_result['overall_score'], blurry_result['overall_score'])
    
    def test_analyze_lighting(self):
        """Test lighting analysis."""
        result = self.quality_engine.analyze_lighting(self.test_image_color, self.face_region)
        
        self.assertIsInstance(result, dict)
        self.assertIn('overall_score', result)
        self.assertIn('brightness_metrics', result)
        self.assertIn('shadow_metrics', result)
        self.assertIn('highlight_metrics', result)
        self.assertIn('uniformity_metrics', result)
    
    def test_evaluate_color_accuracy(self):
        """Test color accuracy evaluation."""
        result = self.quality_engine.evaluate_color_accuracy(self.test_image_color, self.face_region)
        
        self.assertIsInstance(result, dict)
        self.assertIn('overall_score', result)
        self.assertIn('white_balance_metrics', result)
        self.assertIn('color_cast_metrics', result)
        self.assertIn('saturation_metrics', result)
        self.assertIn('skin_tone_metrics', result)
    
    def test_measure_noise_levels(self):
        """Test noise level measurement."""
        # Test clean image
        clean_result = self.quality_engine.measure_noise_levels(self.sharp_image)
        
        # Test noisy image
        noisy_result = self.quality_engine.measure_noise_levels(self.noisy_image)
        
        self.assertIsInstance(clean_result, dict)
        self.assertIsInstance(noisy_result, dict)
        
        # Clean image should have higher score than noisy image
        self.assertGreater(clean_result['overall_score'], noisy_result['overall_score'])
    
    def test_validate_resolution(self):
        """Test resolution validation."""
        result = self.quality_engine.validate_resolution(self.test_image_color, target_dpi=300)
        
        self.assertIsInstance(result, dict)
        self.assertIn('overall_score', result)
        self.assertIn('pixel_metrics', result)
        self.assertIn('effective_resolution_metrics', result)
        self.assertIn('print_quality_metrics', result)
    
    def test_generate_quality_score_single_metric(self):
        """Test quality score generation with single metric."""
        quality_metric = QualityMetrics(
            sharpness_score=85.0,
            lighting_score=90.0,
            color_score=80.0,
            noise_score=88.0,
            resolution_score=92.0,
            overall_score=87.0,
            detailed_metrics={},
            issues=[],
            suggestions=[]
        )
        
        result = self.quality_engine.generate_quality_score([quality_metric])
        
        self.assertIsInstance(result, OverallQualityScore)
        self.assertIsInstance(result.score, float)
        self.assertIn(result.grade, ['excellent', 'good', 'fair', 'poor'])
        self.assertIsInstance(result.passes_threshold, bool)
        self.assertIsInstance(result.confidence, float)
        self.assertIsInstance(result.breakdown, dict)
    
    def test_generate_quality_score_multiple_metrics(self):
        """Test quality score generation with multiple metrics."""
        metrics = []
        for i in range(3):
            metric = QualityMetrics(
                sharpness_score=80.0 + i * 5,
                lighting_score=85.0 + i * 3,
                color_score=75.0 + i * 4,
                noise_score=82.0 + i * 2,
                resolution_score=88.0 + i * 1,
                overall_score=82.0 + i * 3,
                detailed_metrics={},
                issues=[],
                suggestions=[]
            )
            metrics.append(metric)
        
        result = self.quality_engine.generate_quality_score(metrics)
        
        self.assertIsInstance(result, OverallQualityScore)
        self.assertGreater(result.confidence, 0.0)
        self.assertLessEqual(result.confidence, 1.0)
    
    def test_generate_quality_score_empty_metrics(self):
        """Test quality score generation with empty metrics."""
        result = self.quality_engine.generate_quality_score([])
        
        self.assertIsInstance(result, OverallQualityScore)
        self.assertEqual(result.score, 0.0)
        self.assertEqual(result.grade, 'poor')
        self.assertFalse(result.passes_threshold)
        self.assertEqual(result.confidence, 0.0)
    
    def test_custom_configuration(self):
        """Test QualityEngine with custom configuration."""
        custom_config = {
            'sharpness_threshold': 80.0,
            'lighting_threshold': 85.0,
            'overall_threshold': 80.0,
            'weights': {
                'sharpness': 0.3,
                'lighting': 0.3,
                'color': 0.2,
                'noise': 0.1,
                'resolution': 0.1
            }
        }
        
        custom_engine = QualityEngine(custom_config)
        
        self.assertEqual(custom_engine.config['sharpness_threshold'], 80.0)
        self.assertEqual(custom_engine.config['weights']['sharpness'], 0.3)
    
    def test_error_handling(self):
        """Test error handling in quality assessment."""
        # Test with invalid image
        with self.assertRaises(Exception):
            self.quality_engine.assess_image_quality(None)
        
        # Test with empty image
        empty_image = np.array([])
        with self.assertRaises(Exception):
            self.quality_engine.assess_image_quality(empty_image)


class TestSharpnessAnalyzer(unittest.TestCase):
    """Test cases for SharpnessAnalyzer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = SharpnessAnalyzer()
        self.sharp_image = self._create_sharp_image()
        self.blurry_image = self._create_blurry_image()
    
    def _create_sharp_image(self):
        """Create a sharp test image."""
        image = np.zeros((200, 200), dtype=np.uint8)
        cv2.rectangle(image, (50, 50), (150, 150), 255, -1)
        cv2.circle(image, (100, 100), 30, 0, -1)
        return image
    
    def _create_blurry_image(self):
        """Create a blurry test image."""
        sharp = self._create_sharp_image()
        return cv2.GaussianBlur(sharp, (21, 21), 10.0)
    
    def test_analyze_sharp_image(self):
        """Test analysis of sharp image."""
        result = self.analyzer.analyze(self.sharp_image)
        
        self.assertIsInstance(result, dict)
        self.assertIn('overall_score', result)
        self.assertIn('raw_scores', result)
        self.assertIn('normalized_scores', result)
        self.assertIn('is_sharp', result)
        
        # Sharp image should have high score
        self.assertGreater(result['overall_score'], 70.0)
        self.assertTrue(result['is_sharp'])
    
    def test_analyze_blurry_image(self):
        """Test analysis of blurry image."""
        result = self.analyzer.analyze(self.blurry_image)
        
        self.assertIsInstance(result, dict)
        self.assertIn('overall_score', result)
        
        # Blurry image should have low score
        self.assertLess(result['overall_score'], 50.0)
        self.assertFalse(result['is_sharp'])
    
    def test_sharpness_comparison(self):
        """Test that sharp image scores higher than blurry image."""
        sharp_result = self.analyzer.analyze(self.sharp_image)
        blurry_result = self.analyzer.analyze(self.blurry_image)
        
        self.assertGreater(sharp_result['overall_score'], blurry_result['overall_score'])
    
    def test_algorithm_components(self):
        """Test individual sharpness algorithms."""
        result = self.analyzer.analyze(self.sharp_image)
        
        # Check that all algorithms are present
        self.assertIn('laplacian_variance', result['raw_scores'])
        self.assertIn('sobel_variance', result['raw_scores'])
        self.assertIn('fft_sharpness', result['raw_scores'])
        self.assertIn('gradient_magnitude', result['raw_scores'])
        self.assertIn('brenner_gradient', result['raw_scores'])
        
        # Check normalized scores
        for method in ['laplacian', 'sobel', 'fft', 'gradient', 'brenner']:
            self.assertIn(method, result['normalized_scores'])
            self.assertGreaterEqual(result['normalized_scores'][method], 0.0)
            self.assertLessEqual(result['normalized_scores'][method], 100.0)


class TestLightingAnalyzer(unittest.TestCase):
    """Test cases for LightingAnalyzer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = LightingAnalyzer()
        self.well_lit_image = self._create_well_lit_image()
        self.dark_image = self._create_dark_image()
        self.bright_image = self._create_bright_image()
    
    def _create_well_lit_image(self):
        """Create a well-lit test image."""
        image = np.full((200, 200, 3), 128, dtype=np.uint8)
        # Add some variation
        cv2.circle(image, (100, 100), 50, (150, 150, 150), -1)
        return image
    
    def _create_dark_image(self):
        """Create a dark test image."""
        return np.full((200, 200, 3), 50, dtype=np.uint8)
    
    def _create_bright_image(self):
        """Create a bright test image."""
        return np.full((200, 200, 3), 220, dtype=np.uint8)
    
    def test_analyze_well_lit_image(self):
        """Test analysis of well-lit image."""
        result = self.analyzer.analyze(self.well_lit_image)
        
        self.assertIsInstance(result, dict)
        self.assertIn('overall_score', result)
        self.assertIn('brightness_metrics', result)
        self.assertIn('shadow_metrics', result)
        self.assertIn('highlight_metrics', result)
        
        # Well-lit image should have good score
        self.assertGreater(result['overall_score'], 60.0)
    
    def test_analyze_dark_image(self):
        """Test analysis of dark image."""
        result = self.analyzer.analyze(self.dark_image)
        
        self.assertIn('brightness_metrics', result)
        brightness = result['brightness_metrics']['mean_brightness']
        self.assertLess(brightness, 80.0)  # Should detect as dark
    
    def test_analyze_bright_image(self):
        """Test analysis of bright image."""
        result = self.analyzer.analyze(self.bright_image)
        
        self.assertIn('brightness_metrics', result)
        brightness = result['brightness_metrics']['mean_brightness']
        self.assertGreater(brightness, 200.0)  # Should detect as bright
    
    def test_shadow_detection(self):
        """Test shadow detection functionality."""
        # Create image with shadows
        image = np.full((200, 200, 3), 150, dtype=np.uint8)
        # Add dark region (shadow)
        cv2.rectangle(image, (50, 50), (100, 100), (80, 80, 80), -1)
        
        result = self.analyzer.analyze(image)
        
        self.assertIn('shadow_metrics', result)
        shadow_metrics = result['shadow_metrics']
        self.assertIn('shadow_area_ratio', shadow_metrics)
        self.assertIn('has_significant_shadows', shadow_metrics)
    
    def test_highlight_detection(self):
        """Test highlight detection functionality."""
        # Create image with highlights
        image = np.full((200, 200, 3), 100, dtype=np.uint8)
        # Add bright region (highlight)
        cv2.circle(image, (100, 100), 30, (250, 250, 250), -1)
        
        result = self.analyzer.analyze(image)
        
        self.assertIn('highlight_metrics', result)
        highlight_metrics = result['highlight_metrics']
        self.assertIn('highlight_area_ratio', highlight_metrics)
        self.assertIn('has_significant_highlights', highlight_metrics)


class TestColorAnalyzer(unittest.TestCase):
    """Test cases for ColorAnalyzer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = ColorAnalyzer()
        self.neutral_image = self._create_neutral_image()
        self.color_cast_image = self._create_color_cast_image()
        self.face_region = self._create_face_region()
    
    def _create_neutral_image(self):
        """Create a neutral color image."""
        return np.full((200, 200, 3), (128, 128, 128), dtype=np.uint8)
    
    def _create_color_cast_image(self):
        """Create an image with color cast."""
        return np.full((200, 200, 3), (150, 120, 100), dtype=np.uint8)  # Warm cast
    
    def _create_face_region(self):
        """Create a face region with skin tones."""
        # Create skin-like colors
        return np.full((100, 100, 3), (180, 140, 120), dtype=np.uint8)
    
    def test_analyze_neutral_image(self):
        """Test analysis of neutral image."""
        result = self.analyzer.analyze(self.neutral_image)
        
        self.assertIsInstance(result, dict)
        self.assertIn('overall_score', result)
        self.assertIn('white_balance_metrics', result)
        self.assertIn('color_cast_metrics', result)
        
        # Neutral image should have good white balance
        wb_metrics = result['white_balance_metrics']
        self.assertTrue(wb_metrics['is_balanced'])
    
    def test_analyze_color_cast_image(self):
        """Test analysis of image with color cast."""
        result = self.analyzer.analyze(self.color_cast_image)
        
        cast_metrics = result['color_cast_metrics']
        self.assertIn('has_color_cast', cast_metrics)
        self.assertIn('dominant_cast', cast_metrics)
    
    def test_skin_tone_analysis(self):
        """Test skin tone analysis with face region."""
        result = self.analyzer.analyze(self.neutral_image, self.face_region)
        
        self.assertIn('skin_tone_metrics', result)
        skin_metrics = result['skin_tone_metrics']
        
        if skin_metrics:  # If skin was detected
            self.assertIn('skin_tone_score', skin_metrics)
            self.assertIn('has_valid_skin_tone', skin_metrics)
    
    def test_saturation_analysis(self):
        """Test saturation analysis."""
        # Create oversaturated image
        oversaturated = np.zeros((200, 200, 3), dtype=np.uint8)
        oversaturated[:, :, 0] = 255  # Pure red
        
        result = self.analyzer.analyze(oversaturated)
        
        self.assertIn('saturation_metrics', result)
        sat_metrics = result['saturation_metrics']
        self.assertIn('mean_saturation', sat_metrics)
        self.assertGreater(sat_metrics['mean_saturation'], 0.8)  # Should be highly saturated


class TestNoiseAnalyzer(unittest.TestCase):
    """Test cases for NoiseAnalyzer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = NoiseAnalyzer()
        self.clean_image = self._create_clean_image()
        self.noisy_image = self._create_noisy_image()
    
    def _create_clean_image(self):
        """Create a clean test image."""
        image = np.zeros((200, 200), dtype=np.uint8)
        cv2.rectangle(image, (50, 50), (150, 150), 128, -1)
        return image
    
    def _create_noisy_image(self):
        """Create a noisy test image."""
        clean = self._create_clean_image()
        noise = np.random.normal(0, 20, clean.shape).astype(np.int16)
        noisy = np.clip(clean.astype(np.int16) + noise, 0, 255).astype(np.uint8)
        return noisy
    
    def test_analyze_clean_image(self):
        """Test analysis of clean image."""
        result = self.analyzer.analyze(self.clean_image)
        
        self.assertIsInstance(result, dict)
        self.assertIn('overall_score', result)
        self.assertIn('sensor_noise_metrics', result)
        
        # Clean image should have high score
        self.assertGreater(result['overall_score'], 70.0)
    
    def test_analyze_noisy_image(self):
        """Test analysis of noisy image."""
        result = self.analyzer.analyze(self.noisy_image)
        
        self.assertIn('sensor_noise_metrics', result)
        noise_metrics = result['sensor_noise_metrics']
        self.assertIn('average_noise_level', noise_metrics)
        
        # Noisy image should have higher noise level
        self.assertGreater(noise_metrics['average_noise_level'], 5.0)
    
    def test_noise_comparison(self):
        """Test that clean image scores higher than noisy image."""
        clean_result = self.analyzer.analyze(self.clean_image)
        noisy_result = self.analyzer.analyze(self.noisy_image)
        
        self.assertGreater(clean_result['overall_score'], noisy_result['overall_score'])
    
    def test_compression_artifact_detection(self):
        """Test compression artifact detection."""
        # Create image with block artifacts (simplified)
        image = np.zeros((200, 200), dtype=np.uint8)
        # Add block pattern
        for i in range(0, 200, 8):
            for j in range(0, 200, 8):
                if (i // 8 + j // 8) % 2 == 0:
                    image[i:i+8, j:j+8] = 128
                else:
                    image[i:i+8, j:j+8] = 100
        
        result = self.analyzer.analyze(image)
        
        self.assertIn('compression_metrics', result)
        compression_metrics = result['compression_metrics']
        self.assertIn('block_artifacts', compression_metrics)


class TestResolutionValidator(unittest.TestCase):
    """Test cases for ResolutionValidator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.validator = ResolutionValidator()
        self.high_res_image = np.random.randint(0, 255, (1200, 1600, 3), dtype=np.uint8)
        self.low_res_image = np.random.randint(0, 255, (300, 400, 3), dtype=np.uint8)
    
    def test_analyze_high_resolution(self):
        """Test analysis of high resolution image."""
        result = self.validator.analyze(self.high_res_image, target_dpi=300)
        
        self.assertIsInstance(result, dict)
        self.assertIn('overall_score', result)
        self.assertIn('pixel_metrics', result)
        
        pixel_metrics = result['pixel_metrics']
        self.assertTrue(pixel_metrics['meets_minimum_resolution'])
        self.assertGreater(pixel_metrics['megapixels'], 1.0)
    
    def test_analyze_low_resolution(self):
        """Test analysis of low resolution image."""
        result = self.validator.analyze(self.low_res_image, target_dpi=300)
        
        pixel_metrics = result['pixel_metrics']
        # Low resolution image should not meet minimum requirements
        self.assertFalse(pixel_metrics['meets_minimum_resolution'])
    
    def test_print_quality_assessment(self):
        """Test print quality assessment."""
        result = self.validator.analyze(self.high_res_image, target_dpi=300)
        
        self.assertIn('print_quality_metrics', result)
        print_metrics = result['print_quality_metrics']
        self.assertIn('print_scenarios', print_metrics)
        self.assertIn('recommended_print_sizes', print_metrics)
    
    def test_effective_resolution_analysis(self):
        """Test effective resolution analysis."""
        result = self.validator.analyze(self.high_res_image)
        
        self.assertIn('effective_resolution_metrics', result)
        effective_metrics = result['effective_resolution_metrics']
        self.assertIn('effective_resolution_ratio', effective_metrics)
        self.assertIn('mtf_50_frequency', effective_metrics)
    
    def test_scaling_artifact_detection(self):
        """Test scaling artifact detection."""
        # Create upscaled image (simplified)
        small_image = np.random.randint(0, 255, (100, 100), dtype=np.uint8)
        upscaled_image = cv2.resize(small_image, (400, 400), interpolation=cv2.INTER_NEAREST)
        
        result = self.validator.analyze(upscaled_image)
        
        self.assertIn('scaling_metrics', result)
        scaling_metrics = result['scaling_metrics']
        self.assertIn('likely_upscaled', scaling_metrics)


if __name__ == '__main__':
    unittest.main()