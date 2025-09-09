"""
Advanced Quality Analyzer

Comprehensive image quality analysis including:
- Sharpness analysis using multiple metrics
- Lighting quality and uniformity assessment  
- Compression artifact detection
- Overall quality scoring
"""

import cv2
import numpy as np
import logging
from typing import Dict, List
import time

from ...contracts import IQualityAnalyzer, ComplianceResult, ValidationIssue, BoundingBox


class AdvancedQualityAnalyzer(IQualityAnalyzer):
    """
    Advanced quality analyzer providing:
    - Multi-metric sharpness analysis
    - Professional lighting assessment
    - Compression artifact detection
    - Comprehensive quality scoring
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Quality thresholds
        self.thresholds = {
            'min_sharpness_laplacian': 120.0,
            'min_brightness': 80,
            'max_brightness': 220,
            'min_contrast': 30.0,
            'max_noise_level': 25.0,
            'min_overall_quality': 0.7
        }
        
        self.logger.info("Advanced quality analyzer initialized")
    
    def analyze_sharpness(self, image: np.ndarray) -> float:
        """Analyze image sharpness using Laplacian variance"""
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            return float(laplacian_var)
            
        except Exception as e:
            self.logger.error(f"Sharpness analysis failed: {e}")
            return 0.0
    
    def analyze_lighting(self, image: np.ndarray, face_region: BoundingBox) -> Dict[str, float]:
        """Analyze lighting quality and uniformity"""
        try:
            metrics = {}
            
            # Extract face region if provided
            if face_region:
                x, y, w, h = int(face_region.x), int(face_region.y), int(face_region.width), int(face_region.height)
                face_img = image[y:y+h, x:x+w]
            else:
                face_img = image
            
            gray_face = cv2.cvtColor(face_img, cv2.COLOR_BGR2GRAY)
            
            # Brightness analysis
            metrics['mean_brightness'] = float(np.mean(gray_face))
            metrics['brightness_std'] = float(np.std(gray_face))
            
            # Lighting uniformity
            # Calculate coefficient of variation
            cv_brightness = metrics['brightness_std'] / max(metrics['mean_brightness'], 1.0)
            metrics['lighting_uniformity'] = max(0.0, 1.0 - cv_brightness)
            
            # Shadow detection using gradient analysis
            sobelx = cv2.Sobel(gray_face, cv2.CV_64F, 1, 0, ksize=3)
            sobely = cv2.Sobel(gray_face, cv2.CV_64F, 0, 1, ksize=3)
            gradient_magnitude = np.sqrt(sobelx**2 + sobely**2)
            
            # High gradients in dark regions suggest shadows
            dark_mask = gray_face < 100
            shadow_score = np.mean(gradient_magnitude[dark_mask]) if np.any(dark_mask) else 0.0
            metrics['shadow_severity'] = min(1.0, shadow_score / 50.0)
            
            # Overall lighting quality
            brightness_score = 1.0 - abs(128 - metrics['mean_brightness']) / 128.0
            uniformity_score = metrics['lighting_uniformity']
            shadow_penalty = 1.0 - metrics['shadow_severity']
            
            metrics['lighting_quality'] = (brightness_score + uniformity_score + shadow_penalty) / 3.0
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Lighting analysis failed: {e}")
            return {'lighting_quality': 0.0}
    
    def analyze_compression(self, image: np.ndarray) -> Dict[str, float]:
        """Analyze compression artifacts"""
        try:
            metrics = {}
            
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # JPEG blocking artifacts detection
            # Look for 8x8 block patterns typical in JPEG compression
            height, width = gray.shape
            
            # Horizontal blocking
            h_diff = []
            for y in range(8, height, 8):
                if y < height - 1:
                    diff = np.mean(np.abs(gray[y-1, :].astype(float) - gray[y, :].astype(float)))
                    h_diff.append(diff)
            
            # Vertical blocking  
            v_diff = []
            for x in range(8, width, 8):
                if x < width - 1:
                    diff = np.mean(np.abs(gray[:, x-1].astype(float) - gray[:, x].astype(float)))
                    v_diff.append(diff)
            
            blocking_h = np.mean(h_diff) if h_diff else 0.0
            blocking_v = np.mean(v_diff) if v_diff else 0.0
            metrics['blocking_artifacts'] = (blocking_h + blocking_v) / 2.0
            
            # Ringing artifacts detection using high-frequency analysis
            kernel = np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]], dtype=np.float32)
            edges = cv2.filter2D(gray.astype(np.float32), -1, kernel)
            ringing_estimate = np.std(edges)
            metrics['ringing_artifacts'] = min(1.0, ringing_estimate / 50.0)
            
            # Overall compression quality
            blocking_score = max(0.0, 1.0 - metrics['blocking_artifacts'] / 10.0)
            ringing_score = max(0.0, 1.0 - metrics['ringing_artifacts'])
            metrics['compression_quality'] = (blocking_score + ringing_score) / 2.0
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Compression analysis failed: {e}")
            return {'compression_quality': 1.0}
    
    def comprehensive_quality_check(self, image: np.ndarray) -> ComplianceResult:
        """Comprehensive quality analysis"""
        try:
            issues = []
            requirements_met = {}
            measurements = {}
            
            # Sharpness analysis
            sharpness = self.analyze_sharpness(image)
            measurements['sharpness_laplacian'] = sharpness
            
            if sharpness >= self.thresholds['min_sharpness_laplacian']:
                requirements_met['sharpness'] = True
            else:
                requirements_met['sharpness'] = False
                issues.append(ValidationIssue(
                    severity="ERROR",
                    category="QUALITY",
                    code="LOW_SHARPNESS",
                    message=f"Image sharpness {sharpness:.1f} below minimum {self.thresholds['min_sharpness_laplacian']}",
                    details={
                        'measured': sharpness,
                        'minimum': self.thresholds['min_sharpness_laplacian']
                    },
                    suggested_fix="Apply sharpening filter or capture new image"
                ))
            
            # Lighting analysis (without face region for now)
            lighting_metrics = self.analyze_lighting(image, None)
            measurements.update(lighting_metrics)
            
            # Check brightness
            brightness = lighting_metrics.get('mean_brightness', 0)
            if self.thresholds['min_brightness'] <= brightness <= self.thresholds['max_brightness']:
                requirements_met['brightness'] = True
            else:
                requirements_met['brightness'] = False
                issues.append(ValidationIssue(
                    severity="WARNING",
                    category="QUALITY",
                    code="POOR_BRIGHTNESS",
                    message=f"Brightness {brightness:.1f} outside acceptable range {self.thresholds['min_brightness']}-{self.thresholds['max_brightness']}",
                    details={
                        'measured': brightness,
                        'min_acceptable': self.thresholds['min_brightness'],
                        'max_acceptable': self.thresholds['max_brightness']
                    },
                    suggested_fix="Adjust lighting or exposure"
                ))
            
            # Check lighting uniformity
            uniformity = lighting_metrics.get('lighting_uniformity', 0)
            if uniformity >= 0.7:
                requirements_met['lighting_uniformity'] = True
            else:
                requirements_met['lighting_uniformity'] = False
                issues.append(ValidationIssue(
                    severity="WARNING",
                    category="QUALITY",
                    code="POOR_LIGHTING",
                    message=f"Lighting uniformity {uniformity:.3f} below acceptable level",
                    details={
                        'measured': uniformity,
                        'minimum': 0.7
                    },
                    suggested_fix="Use more even lighting setup"
                ))
            
            # Contrast analysis
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            contrast = float(np.std(gray))
            measurements['contrast'] = contrast
            
            if contrast >= self.thresholds['min_contrast']:
                requirements_met['contrast'] = True
            else:
                requirements_met['contrast'] = False
                issues.append(ValidationIssue(
                    severity="WARNING",
                    category="QUALITY",
                    code="LOW_CONTRAST",
                    message=f"Image contrast {contrast:.1f} below minimum {self.thresholds['min_contrast']}",
                    details={
                        'measured': contrast,
                        'minimum': self.thresholds['min_contrast']
                    },
                    suggested_fix="Increase contrast or improve lighting"
                ))
            
            # Noise analysis
            kernel = np.array([[-1,-1,-1], [-1,8,-1], [-1,-1,-1]])
            noise_estimate = float(np.mean(np.abs(cv2.filter2D(gray, -1, kernel))))
            measurements['noise_level'] = noise_estimate
            
            if noise_estimate <= self.thresholds['max_noise_level']:
                requirements_met['noise'] = True
            else:
                requirements_met['noise'] = False
                issues.append(ValidationIssue(
                    severity="WARNING",
                    category="QUALITY",
                    code="NOISE_HIGH",
                    message=f"Noise level {noise_estimate:.1f} exceeds maximum {self.thresholds['max_noise_level']}",
                    details={
                        'measured': noise_estimate,
                        'maximum': self.thresholds['max_noise_level']
                    },
                    suggested_fix="Apply noise reduction or improve capture conditions"
                ))
            
            # Compression analysis
            compression_metrics = self.analyze_compression(image)
            measurements.update(compression_metrics)
            
            # Check compression quality
            compression_quality = compression_metrics.get('compression_quality', 1.0)
            if compression_quality >= 0.8:
                requirements_met['compression'] = True
            else:
                requirements_met['compression'] = False
                issues.append(ValidationIssue(
                    severity="INFO",
                    category="QUALITY",
                    code="COMPRESSION_ARTIFACTS",
                    message=f"Compression quality {compression_quality:.3f} shows visible artifacts",
                    details={
                        'measured': compression_quality,
                        'blocking_artifacts': compression_metrics.get('blocking_artifacts', 0),
                        'ringing_artifacts': compression_metrics.get('ringing_artifacts', 0)
                    },
                    suggested_fix="Use higher quality image or less compression"
                ))
            
            # Calculate overall quality score
            quality_scores = [
                min(1.0, sharpness / self.thresholds['min_sharpness_laplacian']),
                1.0 - abs(128 - brightness) / 128.0,
                uniformity,
                min(1.0, contrast / self.thresholds['min_contrast']),
                max(0.0, 1.0 - noise_estimate / self.thresholds['max_noise_level']),
                compression_quality
            ]
            
            overall_score = np.mean(quality_scores)
            measurements['overall_quality_score'] = overall_score
            
            # Check overall quality threshold
            if overall_score >= self.thresholds['min_overall_quality']:
                requirements_met['overall_quality'] = True
            else:
                requirements_met['overall_quality'] = False
                issues.append(ValidationIssue(
                    severity="ERROR",
                    category="QUALITY",
                    code="OVERALL_QUALITY_LOW",
                    message=f"Overall quality score {overall_score:.3f} below minimum {self.thresholds['min_overall_quality']}",
                    details={
                        'measured': overall_score,
                        'minimum': self.thresholds['min_overall_quality'],
                        'component_scores': {
                            'sharpness': quality_scores[0],
                            'brightness': quality_scores[1],
                            'uniformity': quality_scores[2],
                            'contrast': quality_scores[3],
                            'noise': quality_scores[4],
                            'compression': quality_scores[5]
                        }
                    },
                    suggested_fix="Improve multiple quality aspects or recapture image"
                ))
            
            return ComplianceResult(
                passed=len([i for i in issues if i.severity in ["CRITICAL", "ERROR"]]) == 0,
                score=overall_score,
                issues=issues,
                requirements_met=requirements_met,
                measurements=measurements,
                timestamp=time.time()
            )
            
        except Exception as e:
            self.logger.error(f"Comprehensive quality check failed: {e}")
            return ComplianceResult(
                passed=False,
                score=0.0,
                issues=[ValidationIssue(
                    severity="CRITICAL",
                    category="QUALITY",
                    code="ANALYSIS_ERROR",
                    message=f"Quality analysis failed: {str(e)}",
                    details={}
                )],
                requirements_met={},
                measurements={},
                timestamp=time.time()
            )
