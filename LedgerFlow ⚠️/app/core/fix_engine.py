"""
Fix Engine for LedgerFlow Invoice Diagnostic System

This module implements the FixEngine, which is responsible for applying
targeted fixes to the invoice generation and verification pipeline based on
the analysis from the DiagnosticController.
"""

import os
import re
from typing import List, Dict, Any, Optional
from pathlib import Path
from decimal import Decimal, ROUND_HALF_UP

from .diagnostics_logger import DiagnosticsLogger

def money(x):
    """Helper function to convert to Decimal and round to 2 decimal places"""
    if isinstance(x, Decimal):
        return x.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    return Decimal(str(x)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

class FixEngine:
    """
    Production-grade fix engine for addressing calculation discrepancies.
    
    Identifies whether issues are in master_simulation_engine.py or verification_engine.py
    and applies targeted fixes to resolve calculation discrepancies.
    """

    def __init__(self):
        self.diagnostics = DiagnosticsLogger()
        self.fixes_applied = []
        
    def apply_fixes(self, discrepancy_report: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Apply targeted fixes based on discrepancy analysis.
        
        Args:
            discrepancy_report: Analysis of discrepancies from ComparisonEngine
            
        Returns:
            List of fix results
        """
        fix_results = []
        
        try:
            self.diagnostics.info("🔧 Starting fix application process...")
            
            # Analyze discrepancy patterns
            patterns = discrepancy_report.get('calculation_patterns', [])
            
            for pattern in patterns:
                fix_result = self._apply_pattern_fix(pattern)
                if fix_result:
                    fix_results.append(fix_result)
            
            # Apply general fixes if needed
            if discrepancy_report.get('critical_discrepancies', 0) > 0:
                general_fix = self._apply_general_fixes(discrepancy_report)
                if general_fix:
                    fix_results.append(general_fix)
            
            # Apply template formatting fixes
            template_fix = self._apply_template_formatting_fixes()
            if template_fix:
                fix_results.append(template_fix)
            
            self.diagnostics.info(f"✅ Applied {len(fix_results)} fixes")
            return fix_results
            
        except Exception as e:
            self.diagnostics.error(f"❌ Fix application failed: {str(e)}")
            return []
    
    def _apply_pattern_fix(self, pattern: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Apply fix for a specific calculation pattern.
        
        Args:
            pattern: Pattern analysis from ComparisonEngine
            
        Returns:
            Fix result or None if no fix applied
        """
        pattern_type = pattern.get('pattern_type')
        field_name = pattern.get('field_name')
        severity = pattern.get('severity')
        
        if pattern_type == 'tax_calculation_error':
            return self._fix_tax_calculation_error(field_name, pattern)
        elif pattern_type == 'rounding_error':
            return self._fix_rounding_error(field_name, pattern)
        elif pattern_type == 'discount_error':
            return self._fix_discount_error(field_name, pattern)
        elif pattern_type == 'quantity_error':
            return self._fix_quantity_error(field_name, pattern)
        
        return None
    
    def _fix_tax_calculation_error(self, field_name: str, pattern: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fix GST tax calculation errors in master_simulation_engine.py.

        Args:
            field_name: Field with calculation error
            pattern: Pattern analysis

        Returns:
            Fix result
        """
        try:
            # Read the master simulation engine file
            file_path = Path("app/core/master_simulation_engine.py")
            
            if not file_path.exists():
                return {
                    'fix_type': 'tax_calculation_error',
                    'target_file': str(file_path),
                    'applied': False,
                    'error': 'File not found'
                }
            
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Apply fixes based on field name
            fixes_applied = []
            
            if field_name in ['cgst_amount', 'sgst_amount', 'igst_amount']:
                # Fix GST tax calculation method
                content = self._fix_gst_tax_calculation_method(content)
                fixes_applied.append('GST tax calculation method')
            
            if field_name == 'tax_amount':
                # Fix total tax calculation
                content = self._fix_total_tax_calculation(content)
                fixes_applied.append('Total tax calculation')
            
            # Write the fixed content back
            with open(file_path, 'w') as f:
                f.write(content)
            
            return {
                'fix_type': 'tax_calculation_error',
                'target_file': str(file_path),
                'applied': True,
                'fixes_applied': fixes_applied,
                'pattern': pattern
            }
            
        except Exception as e:
            return {
                'fix_type': 'tax_calculation_error',
                'target_file': str(file_path),
                'applied': False,
                'error': str(e)
            }
    
    def _fix_gst_tax_calculation_method(self, content: str) -> str:
        """
        Fix GST tax calculation method in master_simulation_engine.py.
        
        Args:
            content: File content
            
        Returns:
            Fixed content
        """
        # Ensure proper Decimal usage in tax calculations
        decimal_fixes = [
            # Fix CGST calculation
            (
                r'cgst_amount = Decimal\(str\(tax_calc\.cgst_amount\)\)',
                'cgst_amount = money(tax_calc.cgst_amount)'
            ),
            # Fix SGST calculation
            (
                r'sgst_amount = Decimal\(str\(tax_calc\.sgst_amount\)\)',
                'sgst_amount = money(tax_calc.sgst_amount)'
            ),
            # Fix IGST calculation
            (
                r'igst_amount = Decimal\(str\(tax_calc\.igst_amount\)\)',
                'igst_amount = money(tax_calc.igst_amount)'
            ),
            # Fix total tax calculation
            (
                r'total_tax = cgst_amount \+ sgst_amount',
                'total_tax = money(cgst_amount + sgst_amount)'
            )
        ]
        
        for pattern, replacement in decimal_fixes:
            content = re.sub(pattern, replacement, content)
        
        return content
    
    def _fix_total_tax_calculation(self, content: str) -> str:
        """
        Fix total tax calculation in master_simulation_engine.py.
        
        Args:
            content: File content
            
        Returns:
            Fixed content
        """
        # Ensure total tax is calculated correctly
        fixes = [
            # Fix total tax calculation to use money() helper
            (
                r'total_tax = cgst_amount \+ sgst_amount \+ igst_amount',
                'total_tax = money(cgst_amount + sgst_amount + igst_amount)'
            ),
            # Fix tax amount assignment
            (
                r'item\[\'tax_amount\'\] = float\(total_tax\)',
                'item[\'tax_amount\'] = float(money(total_tax))'
            )
        ]
        
        for pattern, replacement in fixes:
            content = re.sub(pattern, replacement, content)
        
        return content
    
    def _fix_rounding_error(self, field_name: str, pattern: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fix rounding errors by ensuring consistent Decimal usage.
        
        Args:
            field_name: Field with rounding error
            pattern: Pattern analysis
            
        Returns:
            Fix result
        """
        try:
            file_path = Path("app/core/master_simulation_engine.py")
            
            if not file_path.exists():
                return {
                    'fix_type': 'rounding_error',
                    'target_file': str(file_path),
                    'applied': False,
                    'error': 'File not found'
                }
            
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Apply rounding fixes
            fixes_applied = []
            
            if field_name in ['net_amount', 'total_amount']:
                # Fix amount calculations to use money() helper
                content = self._fix_amount_calculations(content)
                fixes_applied.append('Amount calculations')
            
            if field_name == 'unit_price':
                # Fix unit price calculations
                content = self._fix_unit_price_calculations(content)
                fixes_applied.append('Unit price calculations')
            
            # Write the fixed content back
            with open(file_path, 'w') as f:
                f.write(content)
            
            return {
                'fix_type': 'rounding_error',
                'target_file': str(file_path),
                'applied': True,
                'fixes_applied': fixes_applied,
                'pattern': pattern
            }
            
        except Exception as e:
            return {
                'fix_type': 'rounding_error',
                'target_file': str(file_path),
                'applied': False,
                'error': str(e)
            }
    
    def _fix_amount_calculations(self, content: str) -> str:
        """
        Fix amount calculations to use consistent Decimal rounding.
        
        Args:
            content: File content
            
        Returns:
            Fixed content
        """
        fixes = [
            # Fix net amount calculation
            (
                r'item\[\'net_amount\'\] = round\(item\[\'gross_amount\'\] - discount_amount, 2\)',
                'item[\'net_amount\'] = float(money(item[\'gross_amount\'] - discount_amount))'
            ),
            # Fix total amount calculation
            (
                r'item\[\'total_amount\'\] = round\(item\[\'net_amount\'\] \+ tax_amount, 2\)',
                'item[\'total_amount\'] = float(money(item[\'net_amount\'] + tax_amount))'
            ),
            # Fix gross amount calculation
            (
                r'item\[\'gross_amount\'\] = round\(quantity \* unit_price, 2\)',
                'item[\'gross_amount\'] = float(money(quantity * unit_price))'
            )
        ]
        
        for pattern, replacement in fixes:
            content = re.sub(pattern, replacement, content)
        
        return content
    
    def _fix_unit_price_calculations(self, content: str) -> str:
        """
        Fix unit price calculations to use consistent Decimal rounding.
        
        Args:
            content: File content
            
        Returns:
            Fixed content
        """
        fixes = [
            # Fix unit price calculation
            (
                r'unit_price = round\(base_price \* price_variation, 2\)',
                'unit_price = float(money(base_price * price_variation))'
            ),
            # Fix unit price assignment
            (
                r'item\[\'unit_price\'\] = round\(item\[\'unit_price\'\] \* factor, 2\)',
                'item[\'unit_price\'] = float(money(item[\'unit_price\'] * factor))'
            )
        ]
        
        for pattern, replacement in fixes:
            content = re.sub(pattern, replacement, content)
        
        return content
    
    def _fix_discount_error(self, field_name: str, pattern: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fix discount calculation errors.
        
        Args:
            field_name: Field with discount error
            pattern: Pattern analysis
            
        Returns:
            Fix result
        """
        try:
            file_path = Path("app/core/master_simulation_engine.py")
            
            if not file_path.exists():
                return {
                    'fix_type': 'discount_error',
                    'target_file': str(file_path),
                    'applied': False,
                    'error': 'File not found'
                }
            
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Apply discount fixes
            fixes_applied = []
            
            if field_name in ['discount_amount', 'net_amount']:
                # Fix discount calculation
                content = self._fix_discount_calculations(content)
                fixes_applied.append('Discount calculations')
            
            # Write the fixed content back
            with open(file_path, 'w') as f:
                f.write(content)
            
            return {
                'fix_type': 'discount_error',
                'target_file': str(file_path),
                'applied': True,
                'fixes_applied': fixes_applied,
                'pattern': pattern
            }
            
        except Exception as e:
            return {
                'fix_type': 'discount_error',
                'target_file': str(file_path),
                'applied': False,
                'error': str(e)
            }
    
    def _fix_discount_calculations(self, content: str) -> str:
        """
        Fix discount calculations to use consistent Decimal rounding.
        
        Args:
            content: File content
            
        Returns:
            Fixed content
        """
        fixes = [
            # Fix discount amount calculation
            (
                r'discount_amount = round\(item\[\'gross_amount\'\] \* item\[\'discount_percentage\'\] / 100, 2\)',
                'discount_amount = float(money(item[\'gross_amount\'] * item[\'discount_percentage\'] / 100))'
            ),
            # Fix net amount after discount
            (
                r'item\[\'net_amount\'\] = round\(item\[\'gross_amount\'\] - discount_amount, 2\)',
                'item[\'net_amount\'] = float(money(item[\'gross_amount\'] - discount_amount))'
            )
        ]
        
        for pattern, replacement in fixes:
            content = re.sub(pattern, replacement, content)
        
        return content
    
    def _fix_quantity_error(self, field_name: str, pattern: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fix quantity calculation errors.
        
        Args:
            field_name: Field with quantity error
            pattern: Pattern analysis
            
        Returns:
            Fix result
        """
        try:
            file_path = Path("app/core/master_simulation_engine.py")
            
            if not file_path.exists():
                return {
                    'fix_type': 'quantity_error',
                    'target_file': str(file_path),
                    'applied': False,
                    'error': 'File not found'
                }
            
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Apply quantity fixes
            fixes_applied = []
            
            if field_name in ['quantity', 'total_amount']:
                # Fix quantity validation and calculation
                content = self._fix_quantity_calculations(content)
                fixes_applied.append('Quantity calculations')
            
            # Write the fixed content back
            with open(file_path, 'w') as f:
                f.write(content)
            
            return {
                'fix_type': 'quantity_error',
                'target_file': str(file_path),
                'applied': True,
                'fixes_applied': fixes_applied,
                'pattern': pattern
            }
            
        except Exception as e:
            return {
                'fix_type': 'quantity_error',
                'target_file': str(file_path),
                'applied': False,
                'error': str(e)
            }
    
    def _fix_quantity_calculations(self, content: str) -> str:
        """
        Fix quantity calculations to ensure proper validation.
        
        Args:
            content: File content
            
        Returns:
            Fixed content
        """
        fixes = [
            # Ensure quantity is always positive
            (
                r'quantity = random\.randint\(1, 5\)',
                'quantity = max(1, random.randint(1, 5))'
            ),
            # Fix quantity assignment
            (
                r'item\[\'quantity\'\] = quantity',
                'item[\'quantity\'] = max(1, quantity)'
            )
        ]
        
        for pattern, replacement in fixes:
            content = re.sub(pattern, replacement, content)
        
        return content
    
    def _apply_general_fixes(self, discrepancy_report: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Apply general fixes for critical discrepancies.
        
        Args:
            discrepancy_report: Discrepancy analysis
            
        Returns:
            Fix result or None
        """
        try:
            file_path = Path("app/core/master_simulation_engine.py")
            
            if not file_path.exists():
                return None
            
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Apply general fixes
            fixes_applied = []
            
            # Ensure money() helper is imported
            if 'def money(' not in content:
                content = self._add_money_helper(content)
                fixes_applied.append('Added money() helper function')
            
            # Ensure Decimal imports
            if 'from decimal import Decimal' not in content:
                content = self._add_decimal_imports(content)
                fixes_applied.append('Added Decimal imports')
            
            # Write the fixed content back
            with open(file_path, 'w') as f:
                f.write(content)
            
            return {
                'fix_type': 'general_fixes',
                'target_file': str(file_path),
                'applied': True,
                'fixes_applied': fixes_applied
            }
            
        except Exception as e:
            return {
                'fix_type': 'general_fixes',
                'target_file': str(file_path),
                'applied': False,
                'error': str(e)
            }
    
    def _add_money_helper(self, content: str) -> str:
        """
        Add money() helper function if not present.
        
        Args:
            content: File content
            
        Returns:
            Content with money() helper added
        """
        money_helper = '''
def money(x):
    """Helper function to convert to Decimal and round to 2 decimal places"""
    if isinstance(x, Decimal):
        return x.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    return Decimal(str(x)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

'''
        
        # Add after imports
        import_end = content.find('\n\n')
        if import_end != -1:
            content = content[:import_end] + money_helper + content[import_end:]
        
        return content
    
    def _add_decimal_imports(self, content: str) -> str:
        """
        Add Decimal imports if not present.
        
        Args:
            content: File content
            
        Returns:
            Content with Decimal imports added
        """
        decimal_import = 'from decimal import Decimal, ROUND_HALF_UP\n'
        
        # Add to existing imports
        if 'import random' in content:
            content = content.replace('import random', 'import random\nfrom decimal import Decimal, ROUND_HALF_UP')
        
        return content
    
    def _apply_template_formatting_fixes(self) -> Optional[Dict[str, Any]]:
        """
        Apply template formatting fixes for GST template.
        
        Returns:
            Fix result or None
        """
        try:
            template_path = Path("app/templates/pdf/gst_einvoice.html")
            
            if not template_path.exists():
                return {
                    'fix_type': 'template_formatting',
                    'target_file': str(template_path),
                    'applied': False,
                    'error': 'Template file not found'
                }
            
            with open(template_path, 'r') as f:
                content = f.read()
            
            # Apply formatting fixes
            fixes_applied = []
            
            # Fix numeric column alignment
            if 'text-align:right' not in content:
                content = self._fix_numeric_alignment(content)
                fixes_applied.append('Numeric column alignment')
            
            # Fix decimal formatting
            if '%.2f' not in content:
                content = self._fix_decimal_formatting(content)
                fixes_applied.append('Decimal formatting')
            
            # Write the fixed content back
            with open(template_path, 'w') as f:
                f.write(content)
            
            return {
                'fix_type': 'template_formatting',
                'target_file': str(template_path),
                'applied': True,
                'fixes_applied': fixes_applied
            }
            
        except Exception as e:
            return {
                'fix_type': 'template_formatting',
                'target_file': str(template_path),
                'applied': False,
                'error': str(e)
            }
    
    def _fix_numeric_alignment(self, content: str) -> str:
        """
        Fix numeric column alignment in GST template.
        
        Args:
            content: Template content
            
        Returns:
            Fixed content
        """
        # Add right alignment to numeric columns
        fixes = [
            # Fix HSN/SAC column
            (
                r'<th>HSN/SAC</th>',
                '<th style="text-align:right;">HSN/SAC</th>'
            ),
            # Fix CGST column
            (
                r'<th>CGST</th>',
                '<th style="text-align:right;">CGST</th>'
            ),
            # Fix SGST column
            (
                r'<th>SGST</th>',
                '<th style="text-align:right;">SGST</th>'
            ),
            # Fix Amount column
            (
                r'<th>Amount</th>',
                '<th style="text-align:right;">Amount</th>'
            )
        ]
        
        for pattern, replacement in fixes:
            content = re.sub(pattern, replacement, content)
        
        return content
    
    def _fix_decimal_formatting(self, content: str) -> str:
        """
        Fix decimal formatting in GST template.
        
        Args:
            content: Template content
            
        Returns:
            Fixed content
        """
        # Add decimal formatting to numeric values
        fixes = [
            # Fix amount formatting
            (
                r'\{\{ item\.net_amount \}\}',
                '{{ "%.2f"|format(item.net_amount) }}'
            ),
            (
                r'\{\{ item\.cgst_amount \}\}',
                '{{ "%.2f"|format(item.cgst_amount) }}'
            ),
            (
                r'\{\{ item\.sgst_amount \}\}',
                '{{ "%.2f"|format(item.sgst_amount) }}'
            ),
            (
                r'\{\{ item\.total_amount \}\}',
                '{{ "%.2f"|format(item.total_amount) }}'
            )
        ]
        
        for pattern, replacement in fixes:
            content = re.sub(pattern, replacement, content)
        
        return content