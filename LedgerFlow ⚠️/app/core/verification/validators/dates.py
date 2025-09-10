from __future__ import annotations

from datetime import datetime, timedelta
from typing import List, Dict, Any
from ..base import BaseValidator
from ..models import ValidationContext


class DatesValidator(BaseValidator):
    """Validates invoice dates and temporal patterns"""
    
    def validate(self, invoice_data: Dict[str, Any], context: ValidationContext) -> List[ValidationError]:
        """Validate invoice dates"""
        errors = []
        
        invoice_date_str = invoice_data.get('invoice_date')
        if not invoice_date_str:
            return errors
        
        try:
            if isinstance(invoice_date_str, str):
                invoice_date = datetime.strptime(invoice_date_str, '%Y-%m-%d')
            else:
                invoice_date = invoice_date_str
        except (ValueError, TypeError):
            errors.append(self._create_error(
                error_type='invalid_date_format',
                severity='critical',
                field='invoice_date',
                message="Invalid date format",
                current_value=invoice_date_str,
                expected_value='YYYY-MM-DD',
                suggestion="Use ISO date format: YYYY-MM-DD"
            ))
            return errors
        
        now = datetime.now()
        business_rules = self.rules_config.business_rules
        
        # Check future dates
        if invoice_date > now + timedelta(days=business_rules.future_date_tolerance_days):
            errors.append(self._create_error(
                error_type='future_date',
                severity='critical',
                field='invoice_date',
                message="Invoice date cannot be in the future",
                current_value=invoice_date.strftime('%Y-%m-%d'),
                expected_value=f"<= {now.strftime('%Y-%m-%d')}"
            ))
        
        # Check very old dates
        if invoice_date < now - timedelta(days=business_rules.past_date_tolerance_days):
            errors.append(self._create_error(
                error_type='old_date',
                severity='warning',
                field='invoice_date',
                message="Invoice date is very old",
                current_value=invoice_date.strftime('%Y-%m-%d'),
                suggestion="Verify if this date is correct"
            ))
        
        # Check weekend/holiday (for business logic)
        if invoice_date.weekday() == 6:  # Sunday
            errors.append(self._create_error(
                error_type='weekend_date',
                severity='warning',
                field='invoice_date',
                message="Invoice date is on a Sunday",
                current_value=invoice_date.strftime('%A, %Y-%m-%d'),
                suggestion="Verify if business operates on Sundays"
            ))
        
        return errors 