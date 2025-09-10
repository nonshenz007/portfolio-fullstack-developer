from __future__ import annotations

from typing import List, Dict, Any
from ..base import BaseValidator
from ..models import ValidationContext


class BusinessLogicValidator(BaseValidator):
    """Validates business logic rules and patterns"""
    
    def validate(self, invoice_data: Dict[str, Any], context: ValidationContext) -> List[ValidationError]:
        """Validate business logic rules"""
        errors = []
        
        business_rules = self.rules_config.business_rules
        
        # Check for excessive discounts
        items = invoice_data.get('items', [])
        for i, item in enumerate(items):
            discount_pct = float(item.get('discount_percentage', 0))
            if discount_pct > business_rules.max_discount_percentage:
                errors.append(self._create_error(
                    error_type='high_discount',
                    severity='warning',
                    field=f'items[{i}].discount_percentage',
                    message=f"Item {i+1}: Discount percentage is very high ({discount_pct}%)",
                    current_value=discount_pct,
                    expected_value=f"<= {business_rules.max_discount_percentage}%",
                    suggestion="Verify discount is authorized"
                ))
        
        # Check for round number patterns (suspicious)
        total_amount = float(invoice_data.get('total_amount', 0))
        if total_amount > 1000 and total_amount % 100 == 0:
            errors.append(self._create_error(
                error_type='round_number',
                severity='warning',
                field='total_amount',
                message="Invoice total is a round number",
                current_value=total_amount,
                suggestion="Verify calculation accuracy"
            ))
        
        # Validate business style characteristics if specified
        if context.ui_params and 'business_style' in context.ui_params:
            business_style = context.ui_params['business_style']
            style_expectations = self.rules_config.get_business_style_expectations(business_style)
            if style_expectations:
                self._validate_business_style(invoice_data, style_expectations, business_style, errors)
        
        return errors
    
    def _validate_business_style(self, invoice_data: Dict[str, Any], expectations, business_style: str, errors: List):
        """Validate invoice characteristics match the specified business style"""
        item_count = len(invoice_data.get('items', []))
        total_amount = float(invoice_data.get('total_amount', 0))
        
        # Check item count patterns
        if item_count < expectations.min_items or item_count > expectations.max_items:
            errors.append(self._create_error(
                error_type='business_style_item_mismatch',
                severity='warning',
                field='items',
                message=f"Item count unusual for {business_style}",
                current_value=item_count,
                expected_value=f"{expectations.min_items}-{expectations.max_items}",
                suggestion=f"Verify {business_style} item patterns"
            ))
        
        # Check amount patterns
        if total_amount < expectations.min_amount or total_amount > expectations.max_amount:
            errors.append(self._create_error(
                error_type='business_style_amount_mismatch',
                severity='warning',
                field='total_amount',
                message=f"Amount unusual for {business_style}",
                current_value=total_amount,
                expected_value=f"{expectations.min_amount}-{expectations.max_amount}",
                suggestion=f"Verify {business_style} amount patterns"
            )) 