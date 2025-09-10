from __future__ import annotations

from typing import List, Dict, Any
from ..base import BaseValidator
from ..models import ValidationContext


class StructureValidator(BaseValidator):
    """Validates basic invoice structure and required fields"""
    
    def validate(self, invoice_data: Dict[str, Any], context: ValidationContext) -> List[ValidationError]:
        """Validate basic invoice structure"""
        errors = []
        
        # Check required fields
        for field in self.rules_config.required_fields:
            if field not in invoice_data or invoice_data[field] is None:
                errors.append(self._create_error(
                    error_type='missing_field',
                    severity='critical',
                    field=field,
                    message=f"Required field '{field}' is missing",
                    current_value=None,
                    suggestion=f"Add {field} to invoice data"
                ))
        
        # Validate items structure
        items = invoice_data.get('items', [])
        if not isinstance(items, list):
            errors.append(self._create_error(
                error_type='invalid_structure',
                severity='critical',
                field='items',
                message="Items must be a list",
                current_value=type(items).__name__,
                expected_value='list'
            ))
        elif len(items) == 0:
            errors.append(self._create_error(
                error_type='empty_items',
                severity='critical',
                field='items',
                message="Invoice must have at least one item",
                current_value=0,
                expected_value='>= 1'
            ))
        
        return errors 