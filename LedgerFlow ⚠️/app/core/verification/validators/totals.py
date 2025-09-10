from __future__ import annotations

from typing import List, Dict, Any
from decimal import Decimal, ROUND_HALF_UP
from ..base import BaseValidator
from ..models import ValidationContext


class TotalsValidator(BaseValidator):
    """Validates invoice totals and calculations"""
    
    def validate(self, invoice_data: Dict[str, Any], context: ValidationContext) -> List[ValidationError]:
        """Validate invoice totals"""
        errors = []
        
        try:
            items = invoice_data.get('items', [])
            invoice_type = context.invoice_type
            business_rules = self.rules_config.business_rules
            
            # Calculate expected totals with precise decimal handling
            expected_subtotal = sum(Decimal(str(item.get('net_amount', 0))).quantize(Decimal('0.01')) for item in items)
            expected_tax = sum(Decimal(str(item.get('tax_amount', 0))).quantize(Decimal('0.01')) for item in items)
            
            # For cash invoices, total should equal subtotal (no tax added to total)
            if invoice_type == 'cash':
                expected_total = expected_subtotal
            else:
                expected_total = expected_subtotal + expected_tax
            
            # Check actual totals with precise decimal handling
            actual_subtotal = Decimal(str(invoice_data.get('subtotal', 0))).quantize(Decimal('0.01'))
            actual_tax = Decimal(str(invoice_data.get('tax_amount', 0))).quantize(Decimal('0.01'))
            actual_total = Decimal(str(invoice_data.get('total_amount', 0))).quantize(Decimal('0.01'))
            
            # Validate subtotal (allow 2.0 tolerance for realistic variations)
            if abs(actual_subtotal - expected_subtotal) > Decimal('2.0'):
                subtotal_diff = abs(actual_subtotal - expected_subtotal)
                errors.append(self._create_error(
                    error_type='subtotal_mismatch',
                    severity='critical',
                    field='subtotal',
                    message=f"Subtotal doesn't match sum of item amounts (diff: {float(subtotal_diff):.2f})",
                    current_value=float(actual_subtotal),
                    expected_value=float(expected_subtotal),
                    suggestion="Recalculate subtotal from all item net amounts using consistent rounding"
                ))
            
            # Validate tax total (allow 2.0 tolerance for realistic variations)
            if abs(actual_tax - expected_tax) > Decimal('2.0'):
                tax_diff = abs(actual_tax - expected_tax)
                errors.append(self._create_error(
                    error_type='tax_total_mismatch',
                    severity='critical',
                    field='tax_amount',
                    message=f"Tax total doesn't match sum of item taxes (diff: {float(tax_diff):.2f})",
                    current_value=float(actual_tax),
                    expected_value=float(expected_tax),
                    suggestion="Recalculate total tax from all item tax amounts using consistent rounding"
                ))
            
            # Validate grand total (allow 2.0 tolerance for realistic variations)
            if abs(actual_total - expected_total) > Decimal('2.0'):
                total_diff = abs(actual_total - expected_total)
                if invoice_type == 'cash':
                    message = f"Total amount doesn't match subtotal (cash invoice) (diff: {float(total_diff):.2f})"
                    suggestion = "For cash invoices, total should equal subtotal using consistent rounding"
                else:
                    message = f"Total amount doesn't match subtotal + tax (diff: {float(total_diff):.2f})"
                    suggestion = "Recalculate total as subtotal + tax amount using consistent rounding"
                
                errors.append(self._create_error(
                    error_type='total_mismatch',
                    severity='critical',
                    field='total_amount',
                    message=message,
                    current_value=float(actual_total),
                    expected_value=float(expected_total),
                    suggestion=suggestion
                ))
            
            # Check amount limits
            if actual_total > business_rules.max_invoice_amount:
                errors.append(self._create_error(
                    error_type='amount_too_high',
                    severity='critical',
                    field='total_amount',
                    message=f"Invoice amount exceeds maximum limit",
                    current_value=float(actual_total),
                    expected_value=f"<= {business_rules.max_invoice_amount}"
                ))
            
            if actual_total < business_rules.min_invoice_amount:
                errors.append(self._create_error(
                    error_type='amount_too_low',
                    severity='critical',
                    field='total_amount',
                    message=f"Invoice amount below minimum limit",
                    current_value=float(actual_total),
                    expected_value=f">= {business_rules.min_invoice_amount}"
                ))
        
        except (ValueError, TypeError, KeyError) as e:
            errors.append(self._create_error(
                error_type='total_calculation_error',
                severity='critical',
                field='totals',
                message=f"Error calculating totals: {str(e)}",
                current_value=None,
                suggestion="Check all numeric fields for valid values"
            ))
        
        return errors 