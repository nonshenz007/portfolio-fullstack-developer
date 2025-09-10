from __future__ import annotations

import re
from typing import List, Dict, Any
from ..base import BaseValidator
from ..models import ValidationContext


class ComplianceValidator(BaseValidator):
    """Validates government compliance requirements"""
    
    def validate(self, invoice_data: Dict[str, Any], context: ValidationContext) -> List[ValidationError]:
        """Validate compliance requirements"""
        errors = []
        
        invoice_type = context.invoice_type
        
        # GST compliance checks
        if context.country == 'India' and invoice_type == 'gst':
            # Check for mandatory GST fields
            business_gst = invoice_data.get('business_gst_number', '').strip()
            if not business_gst:
                errors.append(self._create_error(
                    error_type='missing_gst_number',
                    severity='critical',
                    field='business_gst_number',
                    message="Business GST number is required for GST invoice",
                    current_value=business_gst,
                    suggestion="Add valid 15-digit GST number"
                ))
            elif len(business_gst) != 15 or not re.match(self.rules_config.gst_patterns.business_gst, business_gst):
                errors.append(self._create_error(
                    error_type='invalid_gst_format',
                    severity='critical',
                    field='business_gst_number',
                    message="Business GST number format is invalid",
                    current_value=business_gst,
                    suggestion="Use format like: 27AAAAA0000A1Z5"
                ))
            
            # Check HSN codes for high-value invoices
            total_amount = float(invoice_data.get('total_amount', 0))
            high_value_threshold = self.rules_config.hsn_patterns.high_value_threshold
            if total_amount > high_value_threshold:
                items_without_hsn = [i for i, item in enumerate(invoice_data.get('items', [])) 
                                   if not item.get('hsn_code')]
                if items_without_hsn:
                    errors.append(self._create_error(
                        error_type='missing_hsn_high_value',
                        severity='warning',
                        field='items.hsn_code',
                        message=f"HSN codes missing for high-value invoice (₹{total_amount})",
                        current_value=f"{len(items_without_hsn)} items without HSN",
                        suggestion="Add HSN codes for all items in high-value invoices"
                    ))
        
        # VAT compliance checks
        if context.country == 'Bahrain' and invoice_type == 'vat':
            business_vat = invoice_data.get('business_vat_number', '').strip()
            if not business_vat or len(business_vat) < 10:
                errors.append(self._create_error(
                    error_type='missing_vat_number',
                    severity='critical',
                    field='business_vat_number',
                    message="Business VAT number is required for VAT invoice",
                    current_value=business_vat,
                    suggestion="Add valid VAT number"
                ))
        
        return errors 