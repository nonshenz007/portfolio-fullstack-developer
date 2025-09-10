from __future__ import annotations

import re
from typing import List, Dict, Any
from ..base import BaseValidator
from ..models import ValidationContext


class InvoiceNumberValidator(BaseValidator):
    """Validates invoice number format and patterns"""
    
    def validate(self, invoice_data: Dict[str, Any], context: ValidationContext) -> List[ValidationError]:
        """Validate invoice number format"""
        errors = []
        
        invoice_number = invoice_data.get('invoice_number', '')
        invoice_type = context.invoice_type
        
        # Get appropriate pattern
        pattern = self.rules_config.get_invoice_pattern(context.country, invoice_type)
        
        if pattern and not re.match(pattern, invoice_number):
            sample_number = self.rules_config.get_sample_invoice_number(invoice_type)
            errors.append(self._create_error(
                error_type='invalid_format',
                severity='critical',
                field='invoice_number',
                message=f"Invoice number format is invalid for {invoice_type} invoice",
                current_value=invoice_number,
                expected_value=f"Pattern: {pattern}",
                suggestion=f"Use format like: {sample_number}"
            ))
        
        return errors 