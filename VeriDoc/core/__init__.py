"""
VeriDoc Core Module

This module contains the core processing components for the VeriDoc system.
It provides the main processing controller and configuration management.
"""

__version__ = "2.0.0"
__author__ = "VeriDoc Team"

from .processing_controller import ProcessingController
from .config_manager import ConfigManager

__all__ = [
    "ProcessingController",
    "ConfigManager",
]