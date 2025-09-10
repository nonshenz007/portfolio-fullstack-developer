"""
GST (Goods and Services Tax) Strategy for India

This module implements the GST tax calculation strategy for Indian businesses.
It handles CGST/SGST for intrastate transactions and IGST for interstate transactions.

Key features:
- CGST = SGST split logic for intrastate transactions
- IGST for interstate transactions  
- GST rate determination based on HSN codes and product categories
- GST number validation
- Exemption handling
"""

import re
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Optional, Tuple
from .base import TaxStrategy, TaxContext, TaxResult, InvoiceItem, TaxCalculationException


def money(x) -> Decimal:
    """Helper function to convert to Decimal and round to 2 decimal places"""
    if isinstance(x, Decimal):
        return x.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    return Decimal(str(x)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


class GSTStrategy(TaxStrategy):
    """
    GST (Goods and Services Tax) calculation strategy for India
    
    This strategy implements the Indian GST system with proper CGST/SGST
    splitting for intrastate transactions and IGST for interstate transactions.
    """
    
    # GST rate slabs as per Indian GST law
    GST_RATES = {
        0: {
            'description': 'Exempt/Zero Rated',
            'items': [
                'milk', 'bread', 'flour', 'rice', 'wheat', 'pulses', 'salt',
                'fresh fruits', 'vegetables', 'eggs', 'meat', 'fish',
                'books', 'newspapers', 'educational materials'
            ]
        },
        5: {
            'description': 'Essential Items',
            'items': [
                'medicines', 'medical equipment', 'life saving drugs',
                'food grains', 'sugar', 'edible oil', 'tea', 'coffee',
                'spices', 'packaged food items', 'footwear under 1000'
            ]
        },
        12: {
            'description': 'Standard Items',
            'items': [
                'computers', 'mobile phones', 'processed food',
                'furniture', 'umbrellas', 'exercise books',
                'ayurvedic medicines', 'tooth powder'
            ]
        },
        18: {
            'description': 'Standard Rate',
            'items': [
                'most goods', 'services', 'electronics', 'textiles',
                'soaps', 'capital goods', 'industrial intermediates',
                'steel products', 'biscuits', 'pasta'
            ]
        },
        28: {
            'description': 'Luxury/Sin Goods',
            'items': [
                'automobiles', 'air conditioners', 'refrigerators',
                'washing machines', 'cigarettes', 'tobacco products',
                'aerated drinks', 'luxury items', 'cement'
            ]
        }
    }
    
    def __init__(self):
        """Initialize GST strategy"""
        super().__init__()
    
    def calculate_tax(self, item: InvoiceItem, context: TaxContext) -> TaxResult:
        """
        Calculate GST for a single invoice item
        
        For intrastate transactions: CGST = SGST = GST_Rate / 2
        For interstate transactions: IGST = GST_Rate
        """
        try:
            # Calculate basic amounts
            gross_amount = money(item.calculate_gross_amount())
            discount_amount = money(item.calculate_discount_amount())
            net_amount = money(item.calculate_net_amount())
            
            # Check if item is exempt
            is_exempt, exemption_reason = self.is_exempt(item, context)
            
            if is_exempt:
                return TaxResult(
                    gross_amount=gross_amount,
                    discount_amount=discount_amount,
                    net_amount=net_amount,
                    total_tax=Decimal('0.00'),
                    total_amount=net_amount,
                    is_exempt=True,
                    exemption_reason=exemption_reason
                )
            
            # Get applicable tax rate
            tax_rate = self.get_applicable_tax_rate(item, context)
            
            # Calculate tax based on interstate/intrastate
            if context.is_interstate:
                # Interstate: IGST only
                igst_rate = tax_rate
                igst_amount = money(net_amount * igst_rate / Decimal('100'))
                
                return TaxResult(
                    gross_amount=gross_amount,
                    discount_amount=discount_amount,
                    net_amount=net_amount,
                    total_tax=igst_amount,
                    total_amount=money(net_amount + igst_amount),
                    igst_amount=igst_amount,
                    igst_rate=igst_rate
                )
            else:
                # Intrastate: CGST + SGST (equal split)
                cgst_rate = sgst_rate = tax_rate / Decimal('2')
                cgst_amount = money(net_amount * cgst_rate / Decimal('100'))
                sgst_amount = money(net_amount * sgst_rate / Decimal('100'))
                total_tax = money(cgst_amount + sgst_amount)
                
                return TaxResult(
                    gross_amount=gross_amount,
                    discount_amount=discount_amount,
                    net_amount=net_amount,
                    total_tax=total_tax,
                    total_amount=money(net_amount + total_tax),
                    cgst_amount=cgst_amount,
                    sgst_amount=sgst_amount,
                    cgst_rate=cgst_rate,
                    sgst_rate=sgst_rate
                )
                
        except Exception as e:
            raise TaxCalculationException(
                f"GST calculation failed: {str(e)}", 
                item.item_name, 
                context
            )
    
    def validate_tax_number(self, tax_number: str, context: TaxContext) -> bool:
        """
        Validate GST number format
        
        GST number format: 15 characters
        - First 2 digits: State code
        - Next 10 characters: PAN
        - 13th character: Entity number
        - 14th character: Z (default)
        - 15th character: Check digit
        """
        if not tax_number or len(tax_number) != 15:
            return False
        
        # GST number pattern: 2 digits + 10 alphanumeric + 1 digit + Z + 1 alphanumeric
        pattern = r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$'
        
        return bool(re.match(pattern, tax_number.upper()))
    
    def get_tax_breakdown(self, items: List[InvoiceItem], context: TaxContext) -> Dict[str, Decimal]:
        """
        Get detailed tax breakdown for multiple items
        """
        breakdown = {
            'total_cgst': Decimal('0.00'),
            'total_sgst': Decimal('0.00'),
            'total_igst': Decimal('0.00'),
            'total_tax': Decimal('0.00'),
            'by_rate': {}
        }
        
        for item in items:
            result = self.calculate_tax(item, context)
            
            breakdown['total_cgst'] += result.cgst_amount
            breakdown['total_sgst'] += result.sgst_amount
            breakdown['total_igst'] += result.igst_amount
            breakdown['total_tax'] += result.total_tax
            
            # Group by tax rate
            if context.is_interstate:
                rate_key = f"IGST_{result.igst_rate}%"
                if rate_key not in breakdown['by_rate']:
                    breakdown['by_rate'][rate_key] = Decimal('0.00')
                breakdown['by_rate'][rate_key] += result.igst_amount
            else:
                cgst_key = f"CGST_{result.cgst_rate}%"
                sgst_key = f"SGST_{result.sgst_rate}%"
                
                if cgst_key not in breakdown['by_rate']:
                    breakdown['by_rate'][cgst_key] = Decimal('0.00')
                if sgst_key not in breakdown['by_rate']:
                    breakdown['by_rate'][sgst_key] = Decimal('0.00')
                    
                breakdown['by_rate'][cgst_key] += result.cgst_amount
                breakdown['by_rate'][sgst_key] += result.sgst_amount
        
        return breakdown
    
    def get_applicable_tax_rate(self, item: InvoiceItem, context: TaxContext) -> Decimal:
        """
        Determine the applicable GST rate for an item
        
        Priority:
        1. Explicit tax_rate in item
        2. HSN code lookup
        3. Product category lookup
        4. Default rate (18%)
        """
        # Use explicit tax rate if provided
        if item.tax_rate is not None:
            return Decimal(str(item.tax_rate))
        
        # Try HSN code lookup (simplified - in real implementation would use HSN database)
        if item.hsn_sac_code:
            rate = self._get_rate_by_hsn(item.hsn_sac_code)
            if rate is not None:
                return Decimal(str(rate))
        
        # Try product category lookup
        if item.product_category:
            rate = self._get_rate_by_category(item.product_category)
            if rate is not None:
                return Decimal(str(rate))
        
        # Try item name lookup
        rate = self._get_rate_by_item_name(item.item_name)
        if rate is not None:
            return Decimal(str(rate))
        
        # Default to 18% (most common GST rate)
        return Decimal('18.00')
    
    def is_exempt(self, item: InvoiceItem, context: TaxContext) -> Tuple[bool, Optional[str]]:
        """
        Check if an item is GST exempt
        """
        # Check for explicit exemption category
        if context.exemption_category:
            return True, f"Exempt under category: {context.exemption_category}"
        
        # Check if item falls under 0% GST category
        rate = self.get_applicable_tax_rate(item, context)
        if rate == Decimal('0.00'):
            return True, "Zero-rated item"
        
        return False, None
    
    def get_supported_countries(self) -> List[str]:
        """Get list of countries supported by GST strategy"""
        return ['India']
    
    def get_supported_currencies(self) -> List[str]:
        """Get list of currencies supported by GST strategy"""
        return ['INR']
    
    def _get_rate_by_hsn(self, hsn_code: str) -> Optional[float]:
        """
        Get GST rate by HSN code
        
        This is a simplified implementation. In production, this would
        query a comprehensive HSN code database.
        """
        # Simplified HSN to rate mapping
        hsn_rates = {
            '1001': 0,    # Wheat
            '1006': 0,    # Rice
            '0401': 0,    # Milk
            '8517': 12,   # Mobile phones
            '8471': 18,   # Computers
            '8703': 28,   # Motor cars
        }
        
        return hsn_rates.get(hsn_code[:4])  # Use first 4 digits
    
    def _get_rate_by_category(self, category: str) -> Optional[float]:
        """Get GST rate by product category"""
        category_rates = {
            'food_grains': 0,
            'medicines': 5,
            'electronics': 18,
            'automobiles': 28,
            'textiles': 12,
            'furniture': 18,
        }
        
        return category_rates.get(category.lower())
    
    def _get_rate_by_item_name(self, item_name: str) -> Optional[float]:
        """Get GST rate by item name lookup"""
        item_name_lower = item_name.lower()
        
        for rate, rate_info in self.GST_RATES.items():
            for item in rate_info['items']:
                if item in item_name_lower or item_name_lower in item:
                    return float(rate)
        
        return None