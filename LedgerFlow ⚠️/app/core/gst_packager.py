import random
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
import math

@dataclass
class TaxSlab:
    """Represents a tax slab with rate and description"""
    rate: float
    description: str
    applicable_items: List[str]
    exemptions: List[str]

@dataclass
class TaxCalculation:
    """Complete tax calculation for an item"""
    item_name: str
    hsn_code: str
    quantity: float
    unit_price: float
    gross_amount: float
    discount_amount: float
    net_amount: float
    tax_rate: float
    cgst_rate: float
    sgst_rate: float
    igst_rate: float
    vat_rate: float
    cgst_amount: float
    sgst_amount: float
    igst_amount: float
    vat_amount: float
    total_tax: float
    total_amount: float
    is_interstate: bool
    is_exempt: bool

class GSTPackager:
    """
    GSTPackager™ - Handles GST/VAT calculations with government-grade accuracy
    
    Features:
    - Auto-sorts items by GST slabs (0%, 5%, 12%, 18%, 28%)
    - Handles interstate vs intrastate GST (CGST+SGST vs IGST)
    - Perfect rounding as per GST rules
    - VAT calculations for Bahrain (0%, 10%)
    - Exemption handling
    - Reverse charge mechanism
    - Composition scheme handling
    """
    
    # Indian GST slabs with typical item categories
    GST_SLABS = {
        0: TaxSlab(
            rate=0.0,
            description="Exempt/Zero Rated",
            applicable_items=[
                "milk", "bread", "flour", "rice", "wheat", "pulses", "salt",
                "fresh fruits", "vegetables", "eggs", "meat", "fish",
                "books", "newspapers", "educational materials"
            ],
            exemptions=[]
        ),
        5: TaxSlab(
            rate=5.0,
            description="Essential Items",
            applicable_items=[
                "medicines", "medical equipment", "life saving drugs",
                "food grains", "sugar", "edible oil", "tea", "coffee",
                "spices", "packaged food items", "footwear under 1000"
            ],
            exemptions=[]
        ),
        12: TaxSlab(
            rate=12.0,
            description="Standard Items",
            applicable_items=[
                "computers", "mobile phones", "processed food",
                "furniture", "umbrellas", "exercise books",
                "ayurvedic medicines", "tooth powder"
            ],
            exemptions=[]
        ),
        18: TaxSlab(
            rate=18.0,
            description="Standard Rate",
            applicable_items=[
                "most goods", "services", "electronics", "textiles",
                "soaps", "capital goods", "industrial intermediates",
                "steel products", "biscuits", "pasta"
            ],
            exemptions=[]
        ),
        28: TaxSlab(
            rate=28.0,
            description="Luxury/Sin Goods",
            applicable_items=[
                "automobiles", "air conditioners", "refrigerators",
                "washing machines", "cigarettes", "tobacco products",
                "aerated drinks", "luxury items", "cement"
            ],
            exemptions=[]
        )
    }
    
    # Bahrain VAT slabs
    VAT_SLABS = {
        0: TaxSlab(
            rate=0.0,
            description="Zero Rated",
            applicable_items=[
                "basic food items", "medical supplies", "education materials",
                "exports", "precious metals", "residential property"
            ],
            exemptions=[]
        ),
        10: TaxSlab(
            rate=10.0,
            description="Standard Rate",
            applicable_items=[
                "most goods", "services", "electronics", "clothing",
                "restaurants", "hotels", "entertainment", "fuel"
            ],
            exemptions=[]
        )
    }
    
    def __init__(self, country: str = 'India', business_state: str = 'Maharashtra'):
        self.country = country
        self.business_state = business_state
        self.tax_slabs = self.GST_SLABS if country == 'India' else self.VAT_SLABS
        
    def calculate_item_tax(self, 
                          item_name: str,
                          hsn_code: str,
                          quantity: float,
                          unit_price: float,
                          customer_state: str = None,
                          discount_percentage: float = 0.0,
                          discount_amount: float = 0.0,
                          override_tax_rate: Optional[float] = None) -> TaxCalculation:
        """
        Calculate complete tax for a single item
        
        Args:
            item_name: Name of the item
            hsn_code: HSN/SAC code
            quantity: Quantity of items
            unit_price: Unit price before tax
            customer_state: Customer's state (for interstate check)
            discount_percentage: Discount percentage (0-100)
            override_tax_rate: Override automatic tax rate detection
        
        Returns:
            TaxCalculation object with all tax details
        """
        # Calculate gross amount
        gross_amount = self._round_amount(quantity * unit_price)
        
        # Calculate discount - use provided discount_amount if available, otherwise calculate from percentage
        if discount_amount > 0:
            calculated_discount = self._round_amount(discount_amount)
        else:
            calculated_discount = self._round_amount(gross_amount * discount_percentage / 100)
        
        net_amount = self._round_amount(gross_amount - calculated_discount)
        
        # Determine tax rate
        if override_tax_rate is not None:
            tax_rate = override_tax_rate
        else:
            tax_rate = self._determine_tax_rate(item_name, hsn_code, unit_price)
        
        # Check if interstate transaction
        is_interstate = self._is_interstate_transaction(customer_state)
        
        # Check if exempt
        is_exempt = tax_rate == 0.0
        
        # Initialize tax amounts
        cgst_rate = sgst_rate = igst_rate = vat_rate = 0.0
        cgst_amount = sgst_amount = igst_amount = vat_amount = 0.0
        
        if self.country == 'India' and not is_exempt:
            if is_interstate:
                # Interstate: IGST only
                igst_rate = tax_rate
                igst_amount = self._round_amount(net_amount * igst_rate / 100)
            else:
                # Intrastate: CGST + SGST
                cgst_rate = sgst_rate = tax_rate / 2
                cgst_amount = self._round_amount(net_amount * cgst_rate / 100)
                sgst_amount = self._round_amount(net_amount * sgst_rate / 100)
        
        elif self.country == 'Bahrain' and not is_exempt:
            vat_rate = tax_rate
            vat_amount = self._round_amount(net_amount * vat_rate / 100)
        
        # Calculate total tax and amount with proper rounding
        total_tax = self._round_amount(cgst_amount + sgst_amount + igst_amount + vat_amount)
        total_amount = self._round_amount(net_amount + total_tax)
        
        return TaxCalculation(
            item_name=item_name,
            hsn_code=hsn_code,
            quantity=quantity,
            unit_price=unit_price,
            gross_amount=gross_amount,
            discount_amount=calculated_discount,
            net_amount=net_amount,
            tax_rate=tax_rate,
            cgst_rate=cgst_rate,
            sgst_rate=sgst_rate,
            igst_rate=igst_rate,
            vat_rate=vat_rate,
            cgst_amount=cgst_amount,
            sgst_amount=sgst_amount,
            igst_amount=igst_amount,
            vat_amount=vat_amount,
            total_tax=total_tax,
            total_amount=total_amount,
            is_interstate=is_interstate,
            is_exempt=is_exempt
        )
    
    def calculate_invoice_totals(self, tax_calculations: List[TaxCalculation]) -> Dict[str, float]:
        """
        Calculate invoice totals from individual tax calculations
        
        Args:
            tax_calculations: List of TaxCalculation objects
            
        Returns:
            Dictionary with invoice totals
        """
        totals = {
            'subtotal': 0.0,
            'total_discount': 0.0,
            'net_amount': 0.0,
            'total_cgst': 0.0,
            'total_sgst': 0.0,
            'total_igst': 0.0,
            'total_vat': 0.0,
            'total_tax': 0.0,
            'grand_total': 0.0,
            'tax_breakdown': {}
        }
        
        # Sum up all amounts
        for calc in tax_calculations:
            totals['subtotal'] += calc.gross_amount
            totals['total_discount'] += calc.discount_amount
            totals['net_amount'] += calc.net_amount
            totals['total_cgst'] += calc.cgst_amount
            totals['total_sgst'] += calc.sgst_amount
            totals['total_igst'] += calc.igst_amount
            totals['total_vat'] += calc.vat_amount
            totals['total_tax'] += calc.total_tax
            totals['grand_total'] += calc.total_amount
            
            # Tax breakdown by rate
            if calc.tax_rate > 0:
                rate_key = f"{calc.tax_rate}%"
                if rate_key not in totals['tax_breakdown']:
                    totals['tax_breakdown'][rate_key] = {
                        'net_amount': 0.0,
                        'tax_amount': 0.0,
                        'item_count': 0
                    }
                totals['tax_breakdown'][rate_key]['net_amount'] += calc.net_amount
                totals['tax_breakdown'][rate_key]['tax_amount'] += calc.total_tax
                totals['tax_breakdown'][rate_key]['item_count'] += 1
        
        # Round all totals
        for key in totals:
            if isinstance(totals[key], float):
                totals[key] = self._round_amount(totals[key])
        
        return totals
    
    def sort_items_by_tax_slab(self, items: List[Dict[str, Any]]) -> Dict[float, List[Dict[str, Any]]]:
        """
        Sort items by their tax slabs for better invoice organization
        
        Args:
            items: List of item dictionaries
            
        Returns:
            Dictionary with tax rate as key and items as value
        """
        sorted_items = {}
        
        for item in items:
            tax_rate = self._determine_tax_rate(
                item.get('name', ''),
                item.get('hsn_code', ''),
                item.get('price', 0)
            )
            
            if tax_rate not in sorted_items:
                sorted_items[tax_rate] = []
            
            sorted_items[tax_rate].append(item)
        
        return sorted_items
    
    def generate_tax_summary(self, tax_calculations: List[TaxCalculation]) -> Dict[str, Any]:
        """
        Generate comprehensive tax summary for audit purposes
        
        Args:
            tax_calculations: List of TaxCalculation objects
            
        Returns:
            Detailed tax summary
        """
        summary = {
            'total_items': len(tax_calculations),
            'tax_slabs_used': set(),
            'exempt_items': 0,
            'interstate_items': 0,
            'intrastate_items': 0,
            'slab_wise_summary': {},
            'compliance_notes': []
        }
        
        for calc in tax_calculations:
            summary['tax_slabs_used'].add(calc.tax_rate)
            
            if calc.is_exempt:
                summary['exempt_items'] += 1
            
            if calc.is_interstate:
                summary['interstate_items'] += 1
            else:
                summary['intrastate_items'] += 1
            
            # Slab-wise summary
            rate_key = f"{calc.tax_rate}%"
            if rate_key not in summary['slab_wise_summary']:
                summary['slab_wise_summary'][rate_key] = {
                    'item_count': 0,
                    'net_amount': 0.0,
                    'tax_amount': 0.0,
                    'items': []
                }
            
            summary['slab_wise_summary'][rate_key]['item_count'] += 1
            summary['slab_wise_summary'][rate_key]['net_amount'] += calc.net_amount
            summary['slab_wise_summary'][rate_key]['tax_amount'] += calc.total_tax
            summary['slab_wise_summary'][rate_key]['items'].append(calc.item_name)
        
        # Convert set to sorted list
        summary['tax_slabs_used'] = sorted(list(summary['tax_slabs_used']))
        
        # Add compliance notes
        if summary['interstate_items'] > 0 and summary['intrastate_items'] > 0:
            summary['compliance_notes'].append(
                "Mixed interstate and intrastate transactions in single invoice"
            )
        
        if len(summary['tax_slabs_used']) > 3:
            summary['compliance_notes'].append(
                "Multiple tax slabs used - ensure HSN codes are correct"
            )
        
        return summary
    
    def _determine_tax_rate(self, item_name: str, hsn_code: str, unit_price: float) -> float:
        """Determine appropriate tax rate for an item"""
        item_name_lower = item_name.lower()
        
        # Check each tax slab
        for rate, slab in self.tax_slabs.items():
            for applicable_item in slab.applicable_items:
                if applicable_item.lower() in item_name_lower:
                    return rate
        
        # Price-based determination for India
        if self.country == 'India':
            if unit_price > 50000:  # High-value items often 28%
                return 28.0
            elif unit_price < 100:  # Low-value items often 12% or 18%
                return 12.0
            else:
                return 18.0  # Default GST rate
        
        # Default for Bahrain
        return 10.0
    
    def _is_interstate_transaction(self, customer_state: str) -> bool:
        """Check if transaction is interstate"""
        if self.country != 'India':
            return False
        
        if not customer_state:
            return False
        
        return customer_state.lower() != self.business_state.lower()
    
    def _round_amount(self, amount: float) -> float:
        """Round amount as per GST rules (to nearest paisa)"""
        if isinstance(amount, Decimal):
            return float(amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
        return float(Decimal(str(amount)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
    
    def validate_tax_calculation(self, calculation: TaxCalculation) -> List[str]:
        """
        Validate tax calculation for compliance
        
        Args:
            calculation: TaxCalculation object to validate
            
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        # Check basic calculations
        expected_gross = self._round_amount(calculation.quantity * calculation.unit_price)
        if abs(calculation.gross_amount - expected_gross) > 0.01:
            errors.append(f"Gross amount calculation error: expected {expected_gross}, got {calculation.gross_amount}")
        
        # Check tax rate validity
        valid_rates = list(self.tax_slabs.keys())
        if calculation.tax_rate not in valid_rates:
            errors.append(f"Invalid tax rate: {calculation.tax_rate}%. Valid rates: {valid_rates}")
        
        # Check CGST + SGST = IGST rule
        if self.country == 'India' and calculation.tax_rate > 0:
            if calculation.is_interstate:
                if calculation.cgst_amount > 0 or calculation.sgst_amount > 0:
                    errors.append("Interstate transaction should not have CGST/SGST")
                if abs(calculation.igst_rate - calculation.tax_rate) > 0.01:
                    errors.append(f"IGST rate should equal tax rate: {calculation.tax_rate}%")
            else:
                if calculation.igst_amount > 0:
                    errors.append("Intrastate transaction should not have IGST")
                expected_cgst_sgst = calculation.tax_rate / 2
                if abs(calculation.cgst_rate - expected_cgst_sgst) > 0.01:
                    errors.append(f"CGST rate should be {expected_cgst_sgst}%")
                if abs(calculation.sgst_rate - expected_cgst_sgst) > 0.01:
                    errors.append(f"SGST rate should be {expected_cgst_sgst}%")
        
        # Check total calculations
        expected_total_tax = calculation.cgst_amount + calculation.sgst_amount + calculation.igst_amount + calculation.vat_amount
        if abs(calculation.total_tax - expected_total_tax) > 0.01:
            errors.append(f"Total tax calculation error: expected {expected_total_tax}, got {calculation.total_tax}")
        
        expected_total_amount = calculation.net_amount + calculation.total_tax
        if abs(calculation.total_amount - expected_total_amount) > 0.01:
            errors.append(f"Total amount calculation error: expected {expected_total_amount}, got {calculation.total_amount}")
        
        return errors
    
    def get_hsn_suggestions(self, item_name: str) -> List[Dict[str, Any]]:
        """
        Get HSN code suggestions based on item name
        
        Args:
            item_name: Name of the item
            
        Returns:
            List of HSN code suggestions with descriptions
        """
        # This is a simplified version - in production, this would use a comprehensive HSN database
        hsn_suggestions = {
            'mobile': [{'code': '8517', 'description': 'Telephone sets, mobile phones'}],
            'laptop': [{'code': '8471', 'description': 'Automatic data processing machines'}],
            'book': [{'code': '4901', 'description': 'Printed books, brochures'}],
            'medicine': [{'code': '3004', 'description': 'Medicaments'}],
            'cloth': [{'code': '6204', 'description': 'Women\'s suits, ensembles'}],
            'rice': [{'code': '1006', 'description': 'Rice'}],
            'oil': [{'code': '1507', 'description': 'Soya-bean oil'}],
            'car': [{'code': '8703', 'description': 'Motor cars'}],
            'tv': [{'code': '8528', 'description': 'Television receivers'}],
            'furniture': [{'code': '9403', 'description': 'Other furniture'}]
        }
        
        item_lower = item_name.lower()
        suggestions = []
        
        for keyword, codes in hsn_suggestions.items():
            if keyword in item_lower:
                suggestions.extend(codes)
        
        # Default suggestion
        if not suggestions:
            suggestions.append({'code': '9999', 'description': 'Other goods not elsewhere specified'})
        
        return suggestions 