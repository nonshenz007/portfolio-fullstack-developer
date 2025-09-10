from __future__ import annotations

from datetime import datetime
from dataclasses import dataclass, asdict
from typing import List, Any, Optional
from enum import Enum


class Severity(Enum):
    """Validation severity levels"""
    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"


class RiskLevel(Enum):
    """Risk levels for validation results"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ValidationError:
    """Represents a validation error with details"""
    error_type: str
    severity: Severity
    field: str
    message: str
    current_value: Any
    expected_value: Any = None
    suggestion: str = None
    invoice_number: str = None


@dataclass
class ValidationResult:
    """Complete validation result for an invoice"""
    invoice_number: str
    is_valid: bool
    errors: List[ValidationError]
    warnings: List[ValidationError]
    info: List[ValidationError]
    compliance_score: float  # 0-100
    risk_level: RiskLevel
    validation_timestamp: datetime
    hash_signature: str


@dataclass
class ValidationContext:
    """Context for validation operations"""
    country: str
    business_state: str
    invoice_type: str
    template_type: Optional[str] = None
    ui_params: Optional[dict] = None


# Export asdict function for serialization
__all__ = ['ValidationError', 'ValidationResult', 'ValidationContext', 'Severity', 'RiskLevel', 'asdict'] 