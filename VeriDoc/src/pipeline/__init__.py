"""
Government-Grade Processing Pipeline

This package implements the enterprise processing pipeline with:
- AI-powered face detection using YOLOv8
- Advanced background segmentation with SAM/U2Net
- Quality enhancement with ESRGAN/NAFNet
- Compliance validation and auto-fix loops
- Concurrent processing with back-pressure control
"""

from .processing_controller import ProcessingController
from .main_pipeline import MainProcessingPipeline

__all__ = [
    'ProcessingController',
    'MainProcessingPipeline'
]
