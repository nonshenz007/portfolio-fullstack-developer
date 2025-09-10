from __future__ import annotations

import re
from typing import List, Dict, Any
from ..base import BaseValidator
from ..models import ValidationContext


class ItemsValidator(BaseValidator):
    """Validates invoice items and their properties"""
    
    def validate(self, invoice_data: Dict[str, Any], context: ValidationContext) -> List[ValidationError]:
        """Validate invoice items"""
        errors = []
        
        items = invoice_data.get('items', [])
        business_rules = self.rules_config.business_rules
        
        if len(items) > business_rules.max_items_per_invoice:
            errors.append(self._create_error(
                error_type='too_many_items',
                severity='critical',
                field='items',
                message=f"Invalid item count: {len(items)} (should be 1-{business_rules.max_items_per_invoice})",
                current_value=len(items),
                expected_value=f"1-{business_rules.max_items_per_invoice}",
                suggestion="Reduce items or split into multiple invoices"
            ))
        
        for i, item in enumerate(items):
            # Validate required item fields
            for field in self.rules_config.required_item_fields:
                if field not in item or item[field] is None:
                    errors.append(self._create_error(
                        error_type='missing_item_field',
                        severity='critical',
                        field=f'items[{i}].{field}',
                        message=f"Item {i+1}: Missing required field '{field}'",
                        current_value=None,
                        suggestion=f"Add {field} to item {i+1}"
                    ))
            
            # Validate numeric fields
            try:
                quantity = float(item.get('quantity', 0))
                if quantity <= 0:
                    errors.append(self._create_error(
                        error_type='invalid_quantity',
                        severity='critical',
                        field=f'items[{i}].quantity',
                        message=f"Item {i+1}: Quantity must be positive",
                        current_value=quantity,
                        expected_value="> 0"
                    ))
            except (ValueError, TypeError):
                errors.append(self._create_error(
                    error_type='invalid_quantity_format',
                    severity='critical',
                    field=f'items[{i}].quantity',
                    message=f"Item {i+1}: Quantity must be a number",
                    current_value=item.get('quantity'),
                    expected_value="Numeric value"
                ))
            
            try:
                unit_price = float(item.get('unit_price', 0))
                if unit_price < 0:
                    errors.append(self._create_error(
                        error_type='negative_price',
                        severity='critical',
                        field=f'items[{i}].unit_price',
                        message=f"Item {i+1}: Unit price cannot be negative",
                        current_value=unit_price,
                        expected_value=">= 0"
                    ))
            except (ValueError, TypeError):
                errors.append(self._create_error(
                    error_type='invalid_price_format',
                    severity='critical',
                    field=f'items[{i}].unit_price',
                    message=f"Item {i+1}: Unit price must be a number",
                    current_value=item.get('unit_price'),
                    expected_value="Numeric value"
                ))
            
            # Validate HSN code (if present)
            hsn_code = item.get('hsn_code')
            if hsn_code and context.country == 'India':
                hsn_pattern = self.rules_config.hsn_patterns.basic
                if not re.match(hsn_pattern, str(hsn_code)):
                    errors.append(self._create_error(
                        error_type='invalid_hsn_format',
                        severity='warning',
                        field=f'items[{i}].hsn_code',
                        message=f"Item {i+1}: HSN code format may be invalid",
                        current_value=hsn_code,
                        expected_value="4-8 digit number",
                        suggestion="Use 4, 6, or 8 digit HSN code"
                    ))
        
        return errors 