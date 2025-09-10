from __future__ import annotations

from typing import List, Dict, Any
from decimal import Decimal
from ..base import BaseValidator
from ..models import ValidationContext


class TaxValidator(BaseValidator):
    """Validates tax calculations using GSTPackager"""
    
    def __init__(self, rules_config, gst_packager, diagnostics_logger=None):
        super().__init__(rules_config, diagnostics_logger)
        self.gst_packager = gst_packager
    
    def validate(self, invoice_data: Dict[str, Any], context: ValidationContext) -> List[ValidationError]:
        """Validate tax calculations using GSTPackager"""
        errors = []
        
        items = invoice_data.get('items', [])
        customer_state = invoice_data.get('customer_state')
        tax_tolerances = self.rules_config.tax_tolerances
        
        # Track total tax for invoice-level validation
        calculated_total_tax = Decimal('0')
        
        for i, item in enumerate(items):
            try:
                # Use the tax_rate from the item if available, otherwise calculate it
                override_tax_rate = item.get('tax_rate')
                
                # Calculate expected tax using GSTPackager
                expected_calc = self.gst_packager.calculate_item_tax(
                    item_name=item.get('name', ''),
                    hsn_code=item.get('hsn_code', ''),
                    quantity=float(item.get('quantity', 0)),
                    unit_price=float(item.get('unit_price', 0)),
                    customer_state=customer_state,
                    discount_percentage=float(item.get('discount_percentage', 0)),
                    discount_amount=float(item.get('discount_amount', 0)),
                    override_tax_rate=override_tax_rate
                )
                
                # Check if actual values match expected (with tolerance for rounding differences)
                actual_tax = Decimal(str(item.get('tax_amount', 0)))
                calculated_total_tax += Decimal(str(expected_calc.total_tax))
                
                if abs(actual_tax - Decimal(str(expected_calc.total_tax))) > Decimal(str(tax_tolerances.tax_calculation)):
                    tax_diff = abs(actual_tax - Decimal(str(expected_calc.total_tax)))
                    errors.append(self._create_error(
                        error_type='tax_mismatch',
                        severity='critical',
                        field=f'items[{i}].tax_amount',
                        message=f"Item {i+1}: Tax amount doesn't match calculation (diff: {float(tax_diff):.2f})",
                        current_value=float(actual_tax),
                        expected_value=expected_calc.total_tax,
                        suggestion=f"Recalculate tax using rate {expected_calc.tax_rate}% for item '{item.get('name', '')}'"
                    ))
                
                # Validate GST breakdown for India
                if context.country == 'India' and context.invoice_type == 'gst':
                    actual_cgst = Decimal(str(item.get('cgst_amount', 0)))
                    actual_sgst = Decimal(str(item.get('sgst_amount', 0)))
                    actual_igst = Decimal(str(item.get('igst_amount', 0)))
                    
                    # Check if CGST+SGST or IGST breakdown is correct
                    if customer_state == context.business_state:
                        # Intra-state: should have CGST+SGST
                        expected_cgst = Decimal(str(expected_calc.cgst_amount))
                        expected_sgst = Decimal(str(expected_calc.sgst_amount))
                        
                        if (abs(actual_cgst - expected_cgst) > Decimal(str(tax_tolerances.cgst_sgst)) or 
                            abs(actual_sgst - expected_sgst) > Decimal(str(tax_tolerances.cgst_sgst))):
                            cgst_diff = abs(actual_cgst - expected_cgst)
                            sgst_diff = abs(actual_sgst - expected_sgst)
                            errors.append(self._create_error(
                                error_type='gst_breakdown_mismatch',
                                severity='critical',
                                field=f'items[{i}].cgst_sgst',
                                message=f"Item {i+1}: CGST/SGST breakdown is incorrect (CGST diff: {float(cgst_diff):.2f}, SGST diff: {float(sgst_diff):.2f})",
                                current_value=f"CGST: {float(actual_cgst)}, SGST: {float(actual_sgst)}",
                                expected_value=f"CGST: {float(expected_cgst)}, SGST: {float(expected_sgst)}",
                                suggestion=f"Recalculate CGST and SGST using rate {expected_calc.cgst_rate}% each for item '{item.get('name', '')}'"
                            ))
                    else:
                        # Inter-state: should have IGST
                        expected_igst = Decimal(str(expected_calc.igst_amount))
                        if abs(actual_igst - expected_igst) > Decimal(str(tax_tolerances.igst)):
                            igst_diff = abs(actual_igst - expected_igst)
                            errors.append(self._create_error(
                                error_type='igst_mismatch',
                                severity='critical',
                                field=f'items[{i}].igst_amount',
                                message=f"Item {i+1}: IGST amount is incorrect (diff: {float(igst_diff):.2f})",
                                current_value=float(actual_igst),
                                expected_value=float(expected_igst),
                                suggestion=f"Recalculate IGST using rate {expected_calc.igst_rate}% for item '{item.get('name', '')}'"
                            ))
                
                # Validate VAT for Bahrain
                elif context.country == 'Bahrain' and context.invoice_type == 'vat':
                    actual_vat = Decimal(str(item.get('vat_amount', 0)))
                    expected_vat = Decimal(str(expected_calc.vat_amount if hasattr(expected_calc, 'vat_amount') else expected_calc.total_tax))
                    
                    if abs(actual_vat - expected_vat) > Decimal(str(tax_tolerances.vat)):
                        vat_diff = abs(actual_vat - expected_vat)
                        errors.append(self._create_error(
                            error_type='vat_mismatch',
                            severity='critical',
                            field=f'items[{i}].vat_amount',
                            message=f"Item {i+1}: VAT amount is incorrect (diff: {float(vat_diff):.2f})",
                            current_value=float(actual_vat),
                            expected_value=float(expected_vat),
                            suggestion=f"Recalculate VAT using rate {expected_calc.vat_rate}% for item '{item.get('name', '')}'"
                        ))
                        
            except Exception as e:
                errors.append(self._create_error(
                    error_type='tax_calculation_error',
                    severity='critical',
                    field=f'items[{i}].tax',
                    message=f"Item {i+1}: Could not validate tax calculation",
                    current_value=str(e),
                    suggestion="Verify tax calculation manually"
                ))
        
        # Validate that invoice total tax matches sum of item taxes
        invoice_tax_amount = Decimal(str(invoice_data.get('tax_amount', 0)))
        if abs(invoice_tax_amount - calculated_total_tax) > Decimal(str(tax_tolerances.invoice_tax_total)):
            tax_diff = abs(invoice_tax_amount - calculated_total_tax)
            errors.append(self._create_error(
                error_type='invoice_tax_mismatch',
                severity='critical',
                field='tax_amount',
                message=f"Invoice tax total doesn't match sum of item taxes (diff: {float(tax_diff):.2f})",
                current_value=float(invoice_tax_amount),
                expected_value=float(calculated_total_tax),
                suggestion="Recalculate total tax amount from all items using consistent rounding"
            ))
        
        return errors 