"""
NoTax Strategy for Plain Cash Invoices

This module implements a no-tax calculation strategy for plain cash invoices
where no tax is applied to any items.

Key features:
- Zero tax calculation for all items
- Maintains consistent interface with other tax strategies
- Useful for cash-only businesses or tax-exempt transactions
"""

from decimal import Decimal
from typing import Dict, List, Optional, Tuple
from .base import TaxStrategy, TaxContext, TaxResult, InvoiceItem, TaxCalculationException


def money(x) -> Decimal:
    """Helper function to convert to Decimal and round to 2 decimal places"""
    if isinstance(x, Decimal):
        return x.quantize(Decimal('0.01'))
    return Decimal(str(x)).quantize(Decimal('0.01'))


class NoTaxStrategy(TaxStrategy):
    """
    No-tax calculation strategy for plain cash invoices
    
    This strategy applies zero tax to all items, making it suitable
    for cash-only businesses or tax-exempt transactions.
    """
    
    def __init__(self):
        """Initialize NoTax strategy"""
        super().__init__()
    
    def calculate_tax(self, item: InvoiceItem, context: TaxContext) -> TaxResult:
        """
        Calculate tax for a single invoice item (always zero)
        """
        try:
            # Calculate basic amounts
            gross_amount = money(item.calculate_gross_amount())
            discount_amount = money(item.calculate_discount_amount())
            net_amount = money(item.calculate_net_amount())
            
            # No tax applied
            return TaxResult(
                gross_amount=gross_amount,
                discount_amount=discount_amount,
                net_amount=net_amount,
                total_tax=Decimal('0.00'),
                total_amount=net_amount,
                is_exempt=True,
                exemption_reason="No tax applied - cash invoice"
            )
                
        except Exception as e:
            raise TaxCalculationException(
                f"NoTax calculation failed: {str(e)}", 
                item.item_name, 
                context
            )
    
    def validate_tax_number(self, tax_number: str, context: TaxContext) -> bool:
        """
        Validate tax number (always returns True for no-tax strategy)
        
        Since no tax is applied, any tax number format is acceptable
        or tax number can be empty.
        """
        return True
    
    def get_tax_breakdown(self, items: List[InvoiceItem], context: TaxContext) -> Dict[str, Decimal]:
        """
        Get detailed tax breakdown for multiple items (always zero)
        """
        return {
            'total_tax': Decimal('0.00'),
            'by_rate': {
                'No Tax': Decimal('0.00')
            },
            'exemption_reason': 'Cash invoice - no tax applied'
        }
    
    def get_applicable_tax_rate(self, item: InvoiceItem, context: TaxContext) -> Decimal:
        """
        Determine the applicable tax rate for an item (always zero)
        """
        return Decimal('0.00')
    
    def is_exempt(self, item: InvoiceItem, context: TaxContext) -> Tuple[bool, Optional[str]]:
        """
        Check if an item is tax exempt (always exempt for no-tax strategy)
        """
        return True, "Cash invoice - no tax applied"
    
    def get_supported_countries(self) -> List[str]:
        """Get list of countries supported by NoTax strategy"""
        return ['*']  # Universal - can be used in any country
    
    def get_supported_currencies(self) -> List[str]:
        """Get list of currencies supported by NoTax strategy"""
        return ['*']  # Universal - can be used with any currency