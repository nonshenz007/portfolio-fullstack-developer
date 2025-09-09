"""
Face detection module for VeriDoc Core Rebuild.

This module provides reliable face detection using OpenCV Haar cascades
with MediaPipe enhancement for facial landmarks.
"""

from .face_detector import FaceDetector
from .data_models import (
    FaceDetectionResult,
    LandmarkResult,
    BoundingBox,
    FacialLandmarks,
    FaceMetrics
)

__all__ = [
    'FaceDetector',
    'FaceDetectionResult',
    'LandmarkResult',
    'BoundingBox',
    'FacialLandmarks',
    'FaceMetrics'
]