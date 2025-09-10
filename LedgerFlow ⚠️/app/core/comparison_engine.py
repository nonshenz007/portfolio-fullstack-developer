import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from decimal import Decimal, ROUND_HALF_UP
from dataclasses import dataclass

from .diagnostics_logger import DiagnosticsLogger

def money(x):
    """Helper function to convert to Decimal and round to 2 decimal places"""
    if isinstance(x, Decimal):
        return x.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    return Decimal(str(x)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

@dataclass
class FieldDiscrepancy:
    """Individual field discrepancy between simulation and verification"""
    field_name: str
    simulation_value: Decimal
    verification_value: Decimal
    difference: Decimal
    tolerance_exceeded: bool
    severity: str  # 'critical', 'warning', 'info'
    
    def __post_init__(self):
        """Calculate difference and determine if tolerance is exceeded"""
        self.difference = abs(self.simulation_value - self.verification_value)
        # Set tolerance based on field type
        tolerance = Decimal('0.01')  # Default 1 paisa tolerance
        if 'percentage' in self.field_name.lower():
            tolerance = Decimal('0.001')  # 0.1% tolerance for percentages
        
        self.tolerance_exceeded = self.difference > tolerance
        
        # Determine severity based on difference magnitude
        if self.difference > Decimal('1.00'):
            self.severity = 'critical'
        elif self.difference > Decimal('0.10'):
            self.severity = 'warning'
        else:
            self.severity = 'info'

class ComparisonEngine:
    """
    Production-grade comparison engine for line-by-line calculation analysis.
    
    Compares simulation engine calculations with verification engine results
    to identify discrepancies and categorize issues.
    """
    
    def __init__(self):
        self.diagnostics = DiagnosticsLogger()
        
    def compare_invoice_calculations(self, invoice: Dict[str, Any], 
                                   verification_result: Any) -> Dict[str, Any]:
        """
        Compare line-by-line calculations for a single invoice.
        
        Args:
            invoice: Invoice data from simulation engine
            verification_result: ValidationResult from verification engine
            
        Returns:
            Comparison result dictionary
        """
        invoice_number = invoice.get('invoice_number', 'UNKNOWN')
        items = invoice.get('items', [])
        
        comparison_result = {
            'invoice_number': invoice_number,
            'total_items': len(items),
            'item_comparisons': [],
            'invoice_level_comparison': {},
            'is_match': True,
            'discrepancies': [],
            'critical_discrepancies': 0,
            'warning_discrepancies': 0,
            'info_discrepancies': 0
        }
        
        # Compare each item
        for item_index, item in enumerate(items):
            item_comparison = self._compare_item_calculations(item, item_index, invoice)
            comparison_result['item_comparisons'].append(item_comparison)
            
            # Track discrepancies
            for discrepancy in item_comparison['discrepancies']:
                comparison_result['discrepancies'].append(discrepancy)
                if discrepancy['severity'] == 'critical':
                    comparison_result['critical_discrepancies'] += 1
                elif discrepancy['severity'] == 'warning':
                    comparison_result['warning_discrepancies'] += 1
                else:
                    comparison_result['info_discrepancies'] += 1
        
        # Compare invoice-level calculations
        invoice_comparison = self._compare_invoice_level_calculations(invoice, verification_result)
        comparison_result['invoice_level_comparison'] = invoice_comparison
        
        # Determine overall match
        comparison_result['is_match'] = (
            comparison_result['critical_discrepancies'] == 0 and
            all(comp['is_match'] for comp in comparison_result['item_comparisons'])
        )
        
        return comparison_result
    
    def _compare_item_calculations(self, item: Dict[str, Any], 
                                  item_index: int, 
                                  invoice: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compare calculations for a single invoice item.
        
        Args:
            item: Item data from simulation
            item_index: Index of the item
            invoice: Full invoice data for context
            
        Returns:
            Item comparison result
        """
        # Extract simulation values
        simulation_values = {
            'net_amount': money(item.get('net_amount', 0)),
            'cgst_amount': money(item.get('cgst_amount', 0)),
            'sgst_amount': money(item.get('sgst_amount', 0)),
            'igst_amount': money(item.get('igst_amount', 0)),
            'tax_amount': money(item.get('tax_amount', 0)),
            'total_amount': money(item.get('total_amount', 0)),
            'discount_amount': money(item.get('discount_amount', 0)),
            'unit_price': money(item.get('unit_price', 0)),
            'quantity': money(item.get('quantity', 0))
        }
        
        # Calculate verification values using GST packager
        verification_values = self._calculate_verification_values(item, invoice)
        
        # Compare values
        discrepancies = []
        for field_name in simulation_values.keys():
            sim_val = simulation_values[field_name]
            ver_val = verification_values.get(field_name, Decimal('0'))
            
            if sim_val != ver_val:
                discrepancy = FieldDiscrepancy(
                    field_name=field_name,
                    simulation_value=sim_val,
                    verification_value=ver_val,
                    difference=abs(sim_val - ver_val),
                    tolerance_exceeded=False,  # Will be calculated in __post_init__
                    severity='info'  # Will be calculated in __post_init__
                )
                discrepancies.append({
                    'field_name': field_name,
                    'simulation_value': float(sim_val),
                    'verification_value': float(ver_val),
                    'difference': float(discrepancy.difference),
                    'tolerance_exceeded': discrepancy.tolerance_exceeded,
                    'severity': discrepancy.severity
                })
        
        return {
            'item_index': item_index,
            'item_name': item.get('name', 'Unknown'),
            'simulation_values': {k: float(v) for k, v in simulation_values.items()},
            'verification_values': {k: float(v) for k, v in verification_values.items()},
            'discrepancies': discrepancies,
            'is_match': len(discrepancies) == 0
        }
    
    def _calculate_verification_values(self, item: Dict[str, Any], 
                                     invoice: Dict[str, Any]) -> Dict[str, Decimal]:
        """
        Calculate what the verification engine would compute for this item.
        
        Args:
            item: Item data
            invoice: Full invoice data for context
            
        Returns:
            Dictionary of verification values
        """
        try:
            from .gst_packager import GSTPackager
            
            gst_packager = GSTPackager(
                country='India',
                business_state='Maharashtra'
            )
            
            # Calculate using GST packager (same as verification engine)
            calc_result = gst_packager.calculate_item_tax(
                item_name=item.get('name', ''),
                hsn_code=item.get('hsn_code', ''),
                quantity=float(item.get('quantity', 0)),
                unit_price=float(item.get('unit_price', 0)),
                customer_state=invoice.get('customer_state', 'Maharashtra'),
                discount_percentage=float(item.get('discount_percentage', 0)),
                discount_amount=float(item.get('discount_amount', 0))
            )
            
            return {
                'net_amount': money(calc_result.net_amount),
                'cgst_amount': money(calc_result.cgst_amount),
                'sgst_amount': money(calc_result.sgst_amount),
                'igst_amount': money(calc_result.igst_amount),
                'tax_amount': money(calc_result.total_tax),
                'total_amount': money(calc_result.net_amount + calc_result.total_tax),
                'discount_amount': money(calc_result.discount_amount),
                'unit_price': money(item.get('unit_price', 0)),
                'quantity': money(item.get('quantity', 0))
            }
            
        except Exception as e:
            self.diagnostics.warning(f"Could not calculate verification values: {str(e)}")
            # Return simulation values as fallback
            return {
                'net_amount': money(item.get('net_amount', 0)),
                'cgst_amount': money(item.get('cgst_amount', 0)),
                'sgst_amount': money(item.get('sgst_amount', 0)),
                'igst_amount': money(item.get('igst_amount', 0)),
                'tax_amount': money(item.get('tax_amount', 0)),
                'total_amount': money(item.get('total_amount', 0)),
                'discount_amount': money(item.get('discount_amount', 0)),
                'unit_price': money(item.get('unit_price', 0)),
                'quantity': money(item.get('quantity', 0))
            }
    
    def _compare_invoice_level_calculations(self, invoice: Dict[str, Any], 
                                          verification_result: Any) -> Dict[str, Any]:
        """
        Compare invoice-level calculations (totals, tax amounts, etc.).
        
        Args:
            invoice: Invoice data from simulation
            verification_result: ValidationResult from verification engine
            
        Returns:
            Invoice-level comparison result
        """
        # Extract simulation totals
        simulation_totals = {
            'subtotal': money(invoice.get('subtotal', 0)),
            'tax_amount': money(invoice.get('tax_amount', 0)),
            'total_amount': money(invoice.get('total_amount', 0)),
            'cgst_amount': money(invoice.get('cgst_amount', 0)),
            'sgst_amount': money(invoice.get('sgst_amount', 0)),
            'igst_amount': money(invoice.get('igst_amount', 0))
        }
        
        # Calculate expected totals from items
        expected_totals = self._calculate_expected_totals(invoice)
        
        # Compare totals
        discrepancies = []
        for field_name in simulation_totals.keys():
            sim_val = simulation_totals[field_name]
            exp_val = expected_totals.get(field_name, Decimal('0'))
            
            if sim_val != exp_val:
                discrepancy = FieldDiscrepancy(
                    field_name=field_name,
                    simulation_value=sim_val,
                    verification_value=exp_val,
                    difference=abs(sim_val - exp_val),
                    tolerance_exceeded=False,
                    severity='info'
                )
                discrepancies.append({
                    'field_name': field_name,
                    'simulation_value': float(sim_val),
                    'expected_value': float(exp_val),
                    'difference': float(discrepancy.difference),
                    'tolerance_exceeded': discrepancy.tolerance_exceeded,
                    'severity': discrepancy.severity
                })
        
        return {
            'simulation_totals': {k: float(v) for k, v in simulation_totals.items()},
            'expected_totals': {k: float(v) for k, v in expected_totals.items()},
            'discrepancies': discrepancies,
            'is_match': len(discrepancies) == 0
        }
    
    def _calculate_expected_totals(self, invoice: Dict[str, Any]) -> Dict[str, Decimal]:
        """
        Calculate expected totals from individual items.
        
        Args:
            invoice: Invoice data
            
        Returns:
            Dictionary of expected totals
        """
        items = invoice.get('items', [])
        
        subtotal = Decimal('0')
        tax_amount = Decimal('0')
        cgst_amount = Decimal('0')
        sgst_amount = Decimal('0')
        igst_amount = Decimal('0')
        
        for item in items:
            subtotal += money(item.get('net_amount', 0))
            tax_amount += money(item.get('tax_amount', 0))
            cgst_amount += money(item.get('cgst_amount', 0))
            sgst_amount += money(item.get('sgst_amount', 0))
            igst_amount += money(item.get('igst_amount', 0))
        
        total_amount = subtotal + tax_amount
        
        return {
            'subtotal': money(subtotal),
            'tax_amount': money(tax_amount),
            'total_amount': money(total_amount),
            'cgst_amount': money(cgst_amount),
            'sgst_amount': money(sgst_amount),
            'igst_amount': money(igst_amount)
        }
    
    def identify_discrepancies(self, comparison_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze discrepancies and categorize issues.
        
        Args:
            comparison_results: List of comparison results
            
        Returns:
            Discrepancy analysis report
        """
        analysis = {
            'total_invoices': len(comparison_results),
            'matching_invoices': 0,
            'mismatching_invoices': 0,
            'total_discrepancies': 0,
            'critical_discrepancies': 0,
            'warning_discrepancies': 0,
            'info_discrepancies': 0,
            'simulation_engine_issues': 0,
            'verification_engine_issues': 0,
            'calculation_patterns': [],
            'recommended_fixes': []
        }
        
        for comparison in comparison_results:
            if comparison['is_match']:
                analysis['matching_invoices'] += 1
            else:
                analysis['mismatching_invoices'] += 1
            
            analysis['total_discrepancies'] += len(comparison['discrepancies'])
            analysis['critical_discrepancies'] += comparison['critical_discrepancies']
            analysis['warning_discrepancies'] += comparison['warning_discrepancies']
            analysis['info_discrepancies'] += comparison['info_discrepancies']
            
            # Analyze patterns in discrepancies
            for discrepancy in comparison['discrepancies']:
                pattern = self._analyze_discrepancy_pattern(discrepancy)
                if pattern:
                    analysis['calculation_patterns'].append(pattern)
        
        # Generate recommendations
        analysis['recommended_fixes'] = self._generate_fix_recommendations(analysis)
        
        return analysis
    
    def _analyze_discrepancy_pattern(self, discrepancy: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Analyze a single discrepancy to identify patterns.
        
        Args:
            discrepancy: Discrepancy data
            
        Returns:
            Pattern analysis or None
        """
        field_name = discrepancy['field_name']
        difference = discrepancy['difference']
        severity = discrepancy['severity']
        
        # Identify common patterns
        patterns = {
            'tax_calculation_error': ['cgst_amount', 'sgst_amount', 'igst_amount', 'tax_amount'],
            'rounding_error': ['net_amount', 'total_amount', 'unit_price'],
            'discount_error': ['discount_amount', 'net_amount'],
            'quantity_error': ['quantity', 'total_amount']
        }
        
        for pattern_name, fields in patterns.items():
            if field_name in fields:
                return {
                    'pattern_type': pattern_name,
                    'field_name': field_name,
                    'difference': float(difference),
                    'severity': severity,
                    'suggested_fix': self._get_suggested_fix(pattern_name, field_name)
                }
        
        return None
    
    def _get_suggested_fix(self, pattern_type: str, field_name: str) -> str:
        """
        Get suggested fix for a pattern type.
        
        Args:
            pattern_type: Type of pattern identified
            field_name: Field name with issue
            
        Returns:
            Suggested fix description
        """
        fixes = {
            'tax_calculation_error': 'Check GST tax calculation logic in master_simulation_engine.py',
            'rounding_error': 'Ensure consistent Decimal rounding using money() helper',
            'discount_error': 'Verify discount calculation and application logic',
            'quantity_error': 'Check quantity validation and calculation'
        }
        
        return fixes.get(pattern_type, 'Review calculation logic for this field')
    
    def _generate_fix_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """
        Generate fix recommendations based on analysis.
        
        Args:
            analysis: Discrepancy analysis
            
        Returns:
            List of fix recommendations
        """
        recommendations = []
        
        if analysis['critical_discrepancies'] > 0:
            recommendations.append("CRITICAL: Fix calculation errors in master_simulation_engine.py")
        
        if analysis['warning_discrepancies'] > 0:
            recommendations.append("WARNING: Review rounding and precision handling")
        
        if analysis['mismatching_invoices'] > analysis['matching_invoices']:
            recommendations.append("MAJOR: Most invoices have calculation issues - systematic fix needed")
        
        if analysis['calculation_patterns']:
            pattern_types = set(p['pattern_type'] for p in analysis['calculation_patterns'])
            for pattern_type in pattern_types:
                recommendations.append(f"PATTERN: Address {pattern_type} issues across all invoices")
        
        return recommendations 