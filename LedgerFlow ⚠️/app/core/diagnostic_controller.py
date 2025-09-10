"""
Diagnostic Controller for Invoice Generation and Verification Pipeline

This module implements a comprehensive diagnostic system to identify and resolve
discrepancies between invoice generation and verification engines in LedgerFlow.
"""

import os
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

from .master_simulation_engine import MasterSimulationEngine, SimulationConfig
from .verification_engine import VerificationEngine, ValidationResult
from .diagnostics_logger import DiagnosticsLogger
from .comparison_engine import ComparisonEngine
from .fix_engine import FixEngine

@dataclass
class DiagnosticResult:
    """Complete diagnostic result with all analysis data"""
    test_invoices: List[Dict[str, Any]]
    comparison_results: List[Dict[str, Any]]
    discrepancy_report: Dict[str, Any]
    fix_results: List[Dict[str, Any]]
    validation_results: List[ValidationResult]
    sample_pdf_path: Optional[str]
    execution_log: List[str]
    success: bool
    error_message: Optional[str] = None

@dataclass
class ItemComparison:
    """Line-by-line comparison result for a single invoice item"""
    invoice_number: str
    item_index: int
    simulation_values: Dict[str, Decimal]
    verification_values: Dict[str, Decimal]
    discrepancies: List[Dict[str, Any]]
    is_match: bool

@dataclass
class FieldDiscrepancy:
    """Individual field discrepancy between simulation and verification"""
    field_name: str
    simulation_value: Decimal
    verification_value: Decimal
    difference: Decimal
    tolerance_exceeded: bool
    severity: str  # 'critical', 'warning', 'info'

class DiagnosticController:
    """
    Production-grade diagnostic controller for LedgerFlow invoice verification.
    
    Implements the complete diagnostic workflow:
    1. Generate test invoices
    2. Run verification on each invoice
    3. Compare simulation vs verification calculations
    4. Apply targeted fixes
    5. Validate fixes through re-testing
    6. Generate sample PDF output
    """
    
    def __init__(self):
        self.diagnostics = DiagnosticsLogger()
        self.comparison_engine = ComparisonEngine()
        self.fix_engine = FixEngine()
        self.execution_log = []
        
        # Create debug_out directory if it doesn't exist
        self.debug_out_dir = Path("debug_out")
        self.debug_out_dir.mkdir(exist_ok=True)
    
    def run_diagnostic(self) -> DiagnosticResult:
        """
        Main diagnostic workflow that orchestrates all steps.
        
        Returns:
            DiagnosticResult with complete analysis and fix results
        """
        start_time = datetime.now()
        self.execution_log = []
        
        try:
            self._log("🚀 Starting comprehensive diagnostic workflow")
            
            # STEP 1: Generate exactly 5 test invoices with today's date
            self._log("📊 Step 1: Generating 5 test invoices...")
            test_invoices = self.generate_test_invoices(count=5)
            
            if not test_invoices:
                return DiagnosticResult(
                    test_invoices=[],
                    comparison_results=[],
                    discrepancy_report={},
                    fix_results=[],
                    validation_results=[],
                    sample_pdf_path=None,
                    execution_log=self.execution_log,
                    success=False,
                    error_message="Failed to generate test invoices"
                )
            
            self._log(f"✅ Generated {len(test_invoices)} test invoices")
            
            # STEP 2: Run verification on each invoice
            self._log("🔍 Step 2: Running verification on all invoices...")
            verification_results = self.run_verification_on_invoices(test_invoices)
            
            # STEP 3: Compare simulation vs verification calculations
            self._log("⚖️ Step 3: Comparing simulation vs verification calculations...")
            comparison_results = self.compare_calculations(test_invoices, verification_results)
            
            # STEP 4: Analyze discrepancies and categorize issues
            self._log("📋 Step 4: Analyzing discrepancies...")
            discrepancy_report = self.analyze_discrepancies(comparison_results)
            
            # STEP 5: Apply targeted fixes
            self._log("🔧 Step 5: Applying targeted fixes...")
            fix_results = self.apply_fixes(discrepancy_report)
            
            # STEP 6: Re-validate after fixes
            self._log("✅ Step 6: Re-validating after fixes...")
            updated_invoices = self.apply_fixes_to_invoices(test_invoices, fix_results)
            final_validation_results = self.run_verification_on_invoices(updated_invoices)
            
            # STEP 7: Generate sample PDF (skip verification for invoice #1)
            self._log("📄 Step 7: Generating sample PDF...")
            sample_pdf_path = self.generate_sample_pdf(updated_invoices[0] if updated_invoices else None)
            
            # STEP 8: Final validation check
            success = self.validate_final_results(final_validation_results)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            self._log(f"⏱️ Diagnostic completed in {execution_time:.2f} seconds")

            return DiagnosticResult(
                test_invoices=updated_invoices,
                comparison_results=comparison_results,
                discrepancy_report=discrepancy_report,
                fix_results=fix_results,
                validation_results=final_validation_results,
                sample_pdf_path=sample_pdf_path,
                execution_log=self.execution_log,
                success=success
            )
            
        except Exception as e:
            self._log(f"❌ Diagnostic workflow failed: {str(e)}")
            return DiagnosticResult(
                test_invoices=[],
                comparison_results=[],
                discrepancy_report={},
                fix_results=[],
                validation_results=[],
                sample_pdf_path=None,
                execution_log=self.execution_log,
                success=False,
                error_message=str(e)
            )
    
    def generate_test_invoices(self, count: int = 5) -> List[Dict[str, Any]]:
        """
        Generate exactly 5 GST invoices with today's date.
        
        Args:
            count: Number of invoices to generate (default 5)
            
        Returns:
            List of invoice dictionaries
        """
        try:
            # Create configuration for test invoices
            config = SimulationConfig(
                invoice_count=count,
                date_range=(datetime.now().date(), datetime.now().date()),
                invoice_type='gst',
                template_type='gst_einvoice',
                business_style='retail_shop',
                country='India',
                business_state='Maharashtra',
                min_items_per_invoice=1,
                max_items_per_invoice=8,
                min_invoice_amount=100.0,
                max_invoice_amount=50000.0,
                business_name='Test Business',
                business_address='Test Address',
                business_gst_number='27AAAAA0000A1Z5'
            )
            
            # Create simulation engine
            simulation_engine = MasterSimulationEngine(config)
            
            # Load default products for testing
            products = [
                {
                    'name': 'Laptop Computer',
                    'code': 'LAP001',
                    'hsn_code': '84713000',
                    'sale_price': 45000,
                    'unit': 'Nos',
                    'gst_rate': 18,
                    'vat_rate': 10
                },
                {
                    'name': 'Mobile Phone',
                    'code': 'MOB001',
                    'hsn_code': '85171200',
                    'sale_price': 15000,
                    'unit': 'Nos',
                    'gst_rate': 18,
                    'vat_rate': 10
                },
                {
                    'name': 'Office Chair',
                    'code': 'CHR001',
                    'hsn_code': '94013000',
                    'sale_price': 8500,
                    'unit': 'Nos',
                    'gst_rate': 18,
                    'vat_rate': 10
                },
                {
                    'name': 'Consulting Service',
                    'code': 'SVC001',
                    'hsn_code': '998361',
                    'sale_price': 5000,
                    'unit': 'Hour',
                    'gst_rate': 18,
                    'vat_rate': 10
                }
            ]
            
            # Run simulation
            result = simulation_engine.run_simulation(products)
            
            if not result.success:
                self._log(f"❌ Simulation failed: {result.error_message}")
                return []
            
            invoices = result.invoices
            
            # Print detailed table for each invoice
            for i, invoice in enumerate(invoices):
                self._print_invoice_details(invoice, i + 1)
            
            self._log(f"✅ Generated {len(invoices)} test invoices successfully")
            return invoices
            
        except Exception as e:
            self._log(f"❌ Failed to generate test invoices: {str(e)}")
            return []
    
    def _print_invoice_details(self, invoice: Dict[str, Any], invoice_number: int):
        """Print detailed table for a single invoice"""
        self._log(f"\n📋 Invoice #{invoice_number}: {invoice['invoice_number']}")
        self._log(f"   Customer: {invoice['customer_name']}")
        self._log(f"   Date: {invoice['invoice_date']}")
        self._log(f"   GSTIN: {invoice.get('business_gst_number', 'N/A')}")
        
        # Print item details
        self._log("   Items:")
        for i, item in enumerate(invoice['items']):
            net_amount = item.get('net_amount', 0)
            cgst_calc = item.get('cgst_amount', 0)
            sgst_calc = item.get('sgst_amount', 0)
            total_line = item.get('total_amount', 0)
            
            self._log(f"     Item#{i+1}: {item['name']}")
            self._log(f"       Net: ₹{net_amount:.2f}, CGST: ₹{cgst_calc:.2f}, SGST: ₹{sgst_calc:.2f}, Total: ₹{total_line:.2f}")
        
        # Print invoice totals
            subtotal = invoice.get('subtotal', 0)
            tax_total = invoice.get('tax_amount', 0)
            grand_total = invoice.get('total_amount', 0)
        
        self._log(f"   Totals:")
        self._log(f"     Subtotal: ₹{subtotal:.2f}")
        self._log(f"     Tax Total: ₹{tax_total:.2f}")
        self._log(f"     Grand Total: ₹{grand_total:.2f}")
        self._log("")
    
    def run_verification_on_invoices(self, invoices: List[Dict[str, Any]]) -> List[ValidationResult]:
        """
        Run verify_invoice() on all generated invoice objects.
        
        Args:
            invoices: List of invoice dictionaries
            
        Returns:
            List of ValidationResult objects
        """
        verification_results = []
        verification_engine = VerificationEngine(
            country='India',
            business_state='Maharashtra'
        )
        
        for invoice in invoices:
            try:
                result = verification_engine.verify_invoice(invoice)
                verification_results.append(result)
                
                if result.is_valid:
                    self._log(f"✅ Invoice {invoice['invoice_number']}: Verification PASSED")
                else:
                    self._log(f"❌ Invoice {invoice['invoice_number']}: Verification FAILED")
                    for error in result.errors:
                        self._log(f"   Error: {error.message}")
                        
            except Exception as e:
                self._log(f"❌ Verification failed for invoice {invoice.get('invoice_number', 'UNKNOWN')}: {str(e)}")
                # Create a failed validation result
                from .verification_engine import ValidationError
                error = ValidationError(
                    error_type='verification_exception',
                    severity='critical',
                    field='verification',
                    message=f"Verification engine exception: {str(e)}",
                    current_value=None,
                    suggestion="Check invoice data format"
                )
                
                result = ValidationResult(
                    invoice_number=invoice.get('invoice_number', 'UNKNOWN'),
                    is_valid=False,
                    errors=[error],
                    warnings=[],
                    info=[],
                    compliance_score=0.0,
                    risk_level='critical',
                    validation_timestamp=datetime.now(),
                    hash_signature=''
                )
                verification_results.append(result)
        
        return verification_results
    
    def compare_calculations(self, invoices: List[Dict[str, Any]], 
                           verification_results: List[ValidationResult]) -> List[Dict[str, Any]]:
        """
        Compare simulation vs verification calculations line-by-line.
        
        Args:
            invoices: List of invoice dictionaries
            verification_results: List of ValidationResult objects
            
        Returns:
            List of comparison results
        """
        comparison_results = []
        
        for invoice, verification_result in zip(invoices, verification_results):
            comparison = self.comparison_engine.compare_invoice_calculations(invoice, verification_result)
            comparison_results.append(comparison)
            
            # Log comparison results
            if comparison['is_match']:
                self._log(f"✅ Invoice {invoice['invoice_number']}: Calculations MATCH")
            else:
                self._log(f"❌ Invoice {invoice['invoice_number']}: Calculations MISMATCH")
                for discrepancy in comparison['discrepancies']:
                    self._log(f"   Discrepancy: {discrepancy['field_name']} - Sim: {discrepancy['simulation_value']}, Ver: {discrepancy['verification_value']}")
        
        return comparison_results
    
    def analyze_discrepancies(self, comparison_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze discrepancies and categorize issues.
        
        Args:
            comparison_results: List of comparison results
            
        Returns:
            Discrepancy analysis report
        """
        return self.comparison_engine.identify_discrepancies(comparison_results)
    
    def apply_fixes(self, discrepancy_report: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Apply targeted fixes based on identified issues.
        
        Args:
            discrepancy_report: Analysis of discrepancies
            
        Returns:
            List of fix results
        """
        return self.fix_engine.apply_fixes(discrepancy_report)
    
    def apply_fixes_to_invoices(self, invoices: List[Dict[str, Any]], 
                               fix_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Apply fixes to the actual invoice data.
        
        Args:
            invoices: Original invoice data
            fix_results: Results from fix engine
            
        Returns:
            Updated invoice data with fixes applied
        """
        updated_invoices = invoices.copy()
        
        for fix_result in fix_results:
            if fix_result.get('applied', False):
                # Apply the fix to the invoice data
                fix_type = fix_result.get('fix_type')
                if fix_type == 'calculation_fix':
                    # Apply calculation fixes
                    updated_invoices = self._apply_calculation_fixes(updated_invoices, fix_result)
                elif fix_type == 'formatting_fix':
                    # Apply formatting fixes
                    updated_invoices = self._apply_formatting_fixes(updated_invoices, fix_result)
        
        return updated_invoices
    
    def _apply_calculation_fixes(self, invoices: List[Dict[str, Any]], 
                                fix_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Apply calculation fixes to invoices"""
        # This would implement specific calculation corrections
        # For now, return the original invoices
        return invoices
    
    def _apply_formatting_fixes(self, invoices: List[Dict[str, Any]], 
                               fix_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Apply formatting fixes to invoices"""
        # This would implement specific formatting corrections
        # For now, return the original invoices
        return invoices
    
    def validate_final_results(self, validation_results: List[ValidationResult]) -> bool:
        """
        Validate that all invoices pass verification after fixes.
        
        Args:
            validation_results: Final validation results
            
        Returns:
            True if all invoices pass, False otherwise
        """
        all_passed = all(result.is_valid for result in validation_results)
        
        if all_passed:
            self._log("✅ All invoices pass verification after fixes")
        else:
            failed_count = sum(1 for result in validation_results if not result.is_valid)
            self._log(f"❌ {failed_count} invoices still fail verification after fixes")
        
        return all_passed
    
    def generate_sample_pdf(self, invoice: Optional[Dict[str, Any]]) -> Optional[str]:
        """
        Generate sample PDF for invoice #1 (skip verification).
        
        Args:
            invoice: Invoice data to generate PDF for
        
        Returns:
            Path to generated PDF file, or None if failed
        """
        if not invoice:
            self._log("❌ No invoice provided for PDF generation")
            return None
        
        try:
            # Import PDF generation components
            from .pdf_template_engine import PDFTemplateEngine
            
            pdf_engine = PDFTemplateEngine()
            
            # Generate PDF with verification bypass
            pdf_path = self.debug_out_dir / "sample_ok.pdf"
            
            # Convert dictionary to object for PDF generation
            class MockInvoice:
                def __init__(self, data):
                    for key, value in data.items():
                        setattr(self, key, value)
                    
                    # Convert items to objects as well
                    if hasattr(self, 'items') and self.items:
                        mock_items = []
                        for item in self.items:
                            class MockItem:
                                def __init__(self, item_data):
                                    for key, value in item_data.items():
                                        setattr(self, key, value)
                            mock_items.append(MockItem(item))
                        self.items = mock_items
            
            mock_invoice = MockInvoice(invoice)
            
            # Generate PDF content
            pdf_path = pdf_engine.generate_invoice_pdf(mock_invoice, str(pdf_path))
            
            self._log(f"✅ Sample PDF generated: {pdf_path}")
            return str(pdf_path)
            
        except Exception as e:
            self._log(f"❌ Failed to generate sample PDF: {str(e)}")
            return None
    
    def _log(self, message: str):
        """Add message to execution log"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        log_entry = f"[{timestamp}] {message}"
        self.execution_log.append(log_entry)
        self.diagnostics.info(message)
    
    def get_execution_summary(self) -> Dict[str, Any]:
        """Get summary of diagnostic execution"""
        return {
            'total_log_entries': len(self.execution_log),
            'execution_log': self.execution_log[-20:],  # Last 20 entries
            'debug_out_directory': str(self.debug_out_dir),
            'timestamp': datetime.now().isoformat()
        }