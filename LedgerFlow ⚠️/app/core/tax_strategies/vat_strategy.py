"""
VAT (Value Added Tax) Strategy for Bahrain

This module implements the VAT tax calculation strategy for Bahrain businesses.
It supports Arabic locale and proper rounding rules as per Bahrain VAT law.

Key features:
- Standard 10% VAT rate with 0% for exempt items
- Arabic locale support for tax descriptions
- Proper rounding rules for BHD currency
- VAT number validation for Bahrain
"""

import re
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Optional, Tuple
from .base import TaxStrategy, TaxContext, TaxResult, InvoiceItem, TaxCalculationException


def money(x) -> Decimal:
    """Helper function to convert to Decimal and round to 3 decimal places for BHD"""
    if isinstance(x, Decimal):
        return x.quantize(Decimal('0.001'), rounding=ROUND_HALF_UP)
    return Decimal(str(x)).quantize(Decimal('0.001'), rounding=ROUND_HALF_UP)


class VATStrategy(TaxStrategy):
    """
    VAT (Value Added Tax) calculation strategy for Bahrain
    
    This strategy implements the Bahrain VAT system with proper rounding
    rules for BHD currency and Arabic locale support.
    """
    
    # VAT rate slabs as per Bahrain VAT law
    VAT_RATES = {
        0: {
            'description': 'Zero Rated / Exempt',
            'description_ar': 'معفى من الضريبة / صفر بالمائة',
            'items': [
                'basic food items', 'medical supplies', 'education materials',
                'exports', 'precious metals', 'residential property',
                'milk', 'bread', 'rice', 'medicines', 'books'
            ]
        },
        10: {
            'description': 'Standard Rate',
            'description_ar': 'المعدل القياسي',
            'items': [
                'most goods', 'services', 'electronics', 'clothing',
                'restaurants', 'hotels', 'entertainment', 'fuel',
                'automobiles', 'furniture', 'appliances'
            ]
        }
    }
    
    def __init__(self, locale: str = 'en'):
        """
        Initialize VAT strategy
        
        Args:
            locale: Language locale ('en' for English, 'ar' for Arabic)
        """
        super().__init__()
        self.locale = locale
        self.is_arabic = locale == 'ar'
    
    def calculate_tax(self, item: InvoiceItem, context: TaxContext) -> TaxResult:
        """
        Calculate VAT for a single invoice item
        
        VAT is calculated as: VAT = Net Amount × VAT Rate / 100
        """
        try:
            # Calculate basic amounts with BHD precision (3 decimal places)
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
                    total_tax=Decimal('0.000'),
                    total_amount=net_amount,
                    is_exempt=True,
                    exemption_reason=exemption_reason
                )
            
            # Get applicable VAT rate
            vat_rate = self.get_applicable_tax_rate(item, context)
            
            # Calculate VAT amount
            vat_amount = money(net_amount * vat_rate / Decimal('100'))
            total_amount = money(net_amount + vat_amount)
            
            return TaxResult(
                gross_amount=gross_amount,
                discount_amount=discount_amount,
                net_amount=net_amount,
                total_tax=vat_amount,
                total_amount=total_amount,
                vat_amount=vat_amount,
                vat_rate=vat_rate,
                tax_breakdown={
                    'vat_description': self._get_vat_description(vat_rate),
                    'vat_description_ar': self._get_vat_description_ar(vat_rate)
                }
            )
                
        except Exception as e:
            raise TaxCalculationException(
                f"VAT calculation failed: {str(e)}", 
                item.item_name, 
                context
            )
    
    def validate_tax_number(self, tax_number: str, context: TaxContext) -> bool:
        """
        Validate Bahrain VAT number format
        
        Bahrain VAT number format: 9 digits
        Format: XXXXXXXXX (9 digits)
        """
        if not tax_number:
            return False
        
        # Remove any spaces or hyphens
        clean_number = re.sub(r'[\s\-]', '', tax_number)
        
        # Check if it's exactly 9 digits
        if len(clean_number) != 9 or not clean_number.isdigit():
            return False
        
        # Additional validation could include check digit verification
        # For now, we'll just validate the format
        return True
    
    def get_tax_breakdown(self, items: List[InvoiceItem], context: TaxContext) -> Dict[str, Decimal]:
        """
        Get detailed VAT breakdown for multiple items
        """
        breakdown = {
            'total_vat': Decimal('0.000'),
            'total_tax': Decimal('0.000'),
            'by_rate': {},
            'by_rate_ar': {}  # Arabic descriptions
        }
        
        for item in items:
            result = self.calculate_tax(item, context)
            
            breakdown['total_vat'] += result.vat_amount
            breakdown['total_tax'] += result.total_tax
            
            # Group by VAT rate
            rate_key = f"VAT_{result.vat_rate}%"
            rate_key_ar = f"ضريبة القيمة المضافة {result.vat_rate}%"
            
            if rate_key not in breakdown['by_rate']:
                breakdown['by_rate'][rate_key] = Decimal('0.000')
                breakdown['by_rate_ar'][rate_key_ar] = Decimal('0.000')
            
            breakdown['by_rate'][rate_key] += result.vat_amount
            breakdown['by_rate_ar'][rate_key_ar] += result.vat_amount
        
        return breakdown
    
    def get_applicable_tax_rate(self, item: InvoiceItem, context: TaxContext) -> Decimal:
        """
        Determine the applicable VAT rate for an item
        
        Priority:
        1. Explicit tax_rate in item
        2. Product category lookup
        3. Item name lookup
        4. Default rate (10%)
        """
        # Use explicit tax rate if provided
        if item.tax_rate is not None:
            return Decimal(str(item.tax_rate))
        
        # Try product category lookup
        if item.product_category:
            rate = self._get_rate_by_category(item.product_category)
            if rate is not None:
                return Decimal(str(rate))
        
        # Try item name lookup
        rate = self._get_rate_by_item_name(item.item_name)
        if rate is not None:
            return Decimal(str(rate))
        
        # Default to 10% (standard VAT rate in Bahrain)
        return Decimal('10.00')
    
    def is_exempt(self, item: InvoiceItem, context: TaxContext) -> Tuple[bool, Optional[str]]:
        """
        Check if an item is VAT exempt
        """
        # Check for explicit exemption category
        if context.exemption_category:
            reason = context.exemption_category
            if self.is_arabic:
                reason = f"معفى تحت الفئة: {reason}"
            return True, reason
        
        # Check if item falls under 0% VAT category
        rate = self.get_applicable_tax_rate(item, context)
        if rate == Decimal('0.00'):
            reason = "Zero-rated item"
            if self.is_arabic:
                reason = "سلعة معفاة من الضريبة"
            return True, reason
        
        return False, None
    
    def get_supported_countries(self) -> List[str]:
        """Get list of countries supported by VAT strategy"""
        return ['Bahrain', 'BH']
    
    def get_supported_currencies(self) -> List[str]:
        """Get list of currencies supported by VAT strategy"""
        return ['BHD']
    
    def _get_rate_by_category(self, category: str) -> Optional[float]:
        """Get VAT rate by product category"""
        category_rates = {
            'food_basic': 0,
            'medicines': 0,
            'education': 0,
            'electronics': 10,
            'automobiles': 10,
            'textiles': 10,
            'furniture': 10,
            'services': 10,
        }
        
        return category_rates.get(category.lower())
    
    def _get_rate_by_item_name(self, item_name: str) -> Optional[float]:
        """Get VAT rate by item name lookup"""
        item_name_lower = item_name.lower()
        
        for rate, rate_info in self.VAT_RATES.items():
            for item in rate_info['items']:
                if item in item_name_lower or item_name_lower in item:
                    return float(rate)
        
        return None
    
    def _get_vat_description(self, rate: Decimal) -> str:
        """Get English description for VAT rate"""
        rate_int = int(rate)
        if rate_int in self.VAT_RATES:
            return self.VAT_RATES[rate_int]['description']
        return f"VAT {rate}%"
    
    def _get_vat_description_ar(self, rate: Decimal) -> str:
        """Get Arabic description for VAT rate"""
        rate_int = int(rate)
        if rate_int in self.VAT_RATES:
            return self.VAT_RATES[rate_int]['description_ar']
        return f"ضريبة القيمة المضافة {rate}%"
    
    def format_amount_arabic(self, amount: Decimal) -> str:
        """Format amount for Arabic display"""
        # Convert to Arabic numerals if needed
        arabic_numerals = '٠١٢٣٤٥٦٧٨٩'
        english_numerals = '0123456789'
        
        amount_str = str(amount)
        if self.is_arabic:
            # Convert to Arabic numerals
            for eng, ar in zip(english_numerals, arabic_numerals):
                amount_str = amount_str.replace(eng, ar)
        
        return amount_str
    
    def get_currency_symbol(self) -> str:
        """Get currency symbol for display"""
        if self.is_arabic:
            return 'د.ب'  # Arabic BHD symbol
        return 'BHD'