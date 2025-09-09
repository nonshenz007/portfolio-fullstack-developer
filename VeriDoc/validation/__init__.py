"""
VeriDoc Validation Module

This module contains the authoritative ICAO compliance validation system.
It provides a single, consistent validation engine for all photo compliance checks.
"""

from .icao_validator import ICAOValidator
from .validation_models import (
    ComplianceResult, DimensionResult, PositionResult, 
    BackgroundResult, QualityResult, ValidationIssue,
    ValidationSeverity, ValidationCategory
)

__all__ = [
    "ICAOValidator",
    "ComplianceResult",
    "DimensionResult", 
    "PositionResult",
    "BackgroundResult",
    "QualityResult",
    "ValidationIssue",
    "ValidationSeverity",
    "ValidationCategory",
]