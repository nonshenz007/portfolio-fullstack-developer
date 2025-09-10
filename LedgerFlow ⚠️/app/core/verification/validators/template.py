from __future__ import annotations

from typing import List, Dict, Any
from ..base import BaseValidator
from ..models import ValidationContext


class TemplateValidator(BaseValidator):
    """Validates template-specific compliance requirements"""
    
    def validate(self, invoice_data: Dict[str, Any], context: ValidationContext) -> List[ValidationError]:
        """Validate template compliance"""
        errors = []
        
        template_type = context.template_type or invoice_data.get('template_type')
        if not template_type:
            return errors
        
        # Get template requirements
        template_req = self.rules_config.get_template_requirements(template_type)
        if not template_req:
            return errors
        
        # Check required fields
        for field in template_req.required_fields:
            if field not in invoice_data or invoice_data[field] is None:
                errors.append(self._create_error(
                    error_type='missing_template_field',
                    severity='critical',
                    field=field,
                    message=f"Required {template_type} field missing: {field}",
                    current_value=None,
                    expected_value=f"Valid {field}",
                    suggestion=f"Ensure {template_type} template generates all required fields"
                ))
        
        # Check currency compliance
        expected_currency = template_req.currency
        actual_currency = invoice_data.get('currency')
        if actual_currency != expected_currency:
            errors.append(self._create_error(
                error_type='currency_mismatch',
                severity='critical',
                field='currency',
                message=f"Currency doesn't match template requirement",
                current_value=actual_currency,
                expected_value=expected_currency,
                suggestion=f"Ensure {template_type} uses {expected_currency} currency"
            ))
        
        # Validate tax structure
        expected_tax = template_req.tax_structure
        if expected_tax == 'gst':
            # GST invoices must have CGST/SGST or IGST
            has_gst_tax = any([
                invoice_data.get('cgst_amount', 0) > 0,
                invoice_data.get('sgst_amount', 0) > 0,
                invoice_data.get('igst_amount', 0) > 0
            ])
            if not has_gst_tax and invoice_data.get('total_amount', 0) > 0:
                errors.append(self._create_error(
                    error_type='missing_gst_tax',
                    severity='critical',
                    field='gst_tax',
                    message="GST template must have GST tax calculations",
                    current_value="No GST tax found",
                    expected_value="CGST+SGST or IGST",
                    suggestion="Ensure GST tax calculation is working"
                ))
        
        elif expected_tax == 'vat':
            # VAT invoices must have VAT amount
            vat_amount = invoice_data.get('vat_amount', 0)
            if vat_amount <= 0 and invoice_data.get('total_amount', 0) > 0:
                errors.append(self._create_error(
                    error_type='missing_vat_tax',
                    severity='critical',
                    field='vat_amount',
                    message="VAT template must have VAT tax calculations",
                    current_value=vat_amount,
                    expected_value="> 0",
                    suggestion="Ensure VAT tax calculation is working"
                ))
        
        elif expected_tax == 'none':
            # Cash invoices must have zero tax
            tax_amount = invoice_data.get('tax_amount', 0)
            if tax_amount > 0:
                errors.append(self._create_error(
                    error_type='unexpected_tax_in_cash',
                    severity='critical',
                    field='tax_amount',
                    message="Cash template should not have tax",
                    current_value=tax_amount,
                    expected_value=0,
                    suggestion="Ensure cash invoices have zero tax"
                ))
        
        return errors 