from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Dict, Any
from .models import ValidationError, ValidationContext


class BaseValidator(ABC):
    """Base interface for all validators"""
    
    def __init__(self, rules_config, diagnostics_logger=None):
        self.rules_config = rules_config
        self.diagnostics = diagnostics_logger
    
    @abstractmethod
    def validate(self, invoice_data: Dict[str, Any], context: ValidationContext) -> List[ValidationError]:
        """
        Validate invoice data and return list of validation errors
        
        Args:
            invoice_data: Dictionary containing invoice information
            context: Validation context with country, state, etc.
            
        Returns:
            List of ValidationError objects
        """
        pass
    
    def _create_error(self, error_type: str, severity: str, field: str, message: str, 
                     current_value: Any, expected_value: Any = None, suggestion: str = None,
                     invoice_number: str = None) -> ValidationError:
        """Helper method to create validation errors"""
        from .models import Severity
        
        severity_enum = Severity(severity)
        return ValidationError(
            error_type=error_type,
            severity=severity_enum,
            field=field,
            message=message,
            current_value=current_value,
            expected_value=expected_value,
            suggestion=suggestion,
            invoice_number=invoice_number
        ) 