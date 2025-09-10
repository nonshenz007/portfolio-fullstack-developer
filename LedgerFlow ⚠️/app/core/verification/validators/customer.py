from __future__ import annotations

import re
from typing import List, Dict, Any
from ..base import BaseValidator
from ..models import ValidationContext


class CustomerValidator(BaseValidator):
    """Validates customer information and contact details"""
    
    def validate(self, invoice_data: Dict[str, Any], context: ValidationContext) -> List[ValidationError]:
        """Validate customer information"""
        errors = []
        
        customer_name = invoice_data.get('customer_name', '')
        if len(customer_name.strip()) < 2:
            errors.append(self._create_error(
                error_type='invalid_customer_name',
                severity='critical',
                field='customer_name',
                message="Customer name is too short",
                current_value=customer_name,
                expected_value="At least 2 characters"
            ))
        
        # Validate GST number format (if present)
        customer_gst = invoice_data.get('customer_gst_number')
        if customer_gst and context.country == 'India':
            gst_pattern = self.rules_config.gst_patterns.customer_gst
            if not re.match(gst_pattern, customer_gst):
                errors.append(self._create_error(
                    error_type='invalid_gst_format',
                    severity='critical',
                    field='customer_gst_number',
                    message="Invalid GST number format",
                    current_value=customer_gst,
                    expected_value="15-digit GST format",
                    suggestion="Use format: 22AAAAA0000A1Z5"
                ))
        
        # Validate phone number (if present)
        customer_phone = invoice_data.get('customer_phone')
        if customer_phone:
            # Remove common separators
            clean_phone = re.sub(r'[+\-\s\(\)]', '', customer_phone)
            if not clean_phone.isdigit() or len(clean_phone) < 10:
                errors.append(self._create_error(
                    error_type='invalid_phone',
                    severity='warning',
                    field='customer_phone',
                    message="Phone number format may be invalid",
                    current_value=customer_phone,
                    suggestion="Use format: +91-9876543210"
                ))
        
        return errors 