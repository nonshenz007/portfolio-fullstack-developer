"""
PRODUCTION-GRADE Export Controller with Verification Gating
Blocks exports unless 100% validation success rate achieved.
"""

from typing import Dict, Any, List, Tuple
import os
from pathlib import Path
from datetime import datetime

from .verification_engine import VerificationEngine
from .pdf_template_engine import PDFTemplateEngine

class ExportController:
    """
    STRICT verification-gated export system.
    Export only proceeds if ALL invoices pass validation.
    """
    
    def __init__(self):
        self.verification_engine = VerificationEngine()
        self.pdf_engine = PDFTemplateEngine()
        
    def validate_and_export(self, invoices: List[Dict[str, Any]], 
                           export_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        PRODUCTION-GRADE export with strict validation gating.
        Returns export result with validation details.
        """
        
        # PHASE 1: Comprehensive validation
        validation_result = self.verification_engine.verify_invoice_batch(invoices)
        
        # PHASE 2: Check success rate
        success_rate = validation_result.get('success_rate', 0)
        total_invoices = len(invoices)
        valid_invoices = validation_result.get('valid_count', 0)
        
        # STRICT GATING: Must be 100% success
        if success_rate < 100.0:
            return {
                'export_success': False,
                'validation_passed': False,
                'success_rate': success_rate,
                'total_invoices': total_invoices,
                'valid_invoices': valid_invoices,
                'invalid_invoices': total_invoices - valid_invoices,
                'error_summary': validation_result.get('error_summary', []),
                'export_blocked_reason': f'Validation failed: {success_rate:.1f}% success rate. Requires 100%.',
                'export_path': None
            }
        
        # PHASE 3: Proceed with export
        try:
            export_path = self._create_export_structure(export_config)
            exported_files = []
            
            for invoice in invoices:
                pdf_path = self._generate_invoice_pdf(invoice, export_path)
                if pdf_path:
                    exported_files.append(pdf_path)
            
            return {
                'export_success': True,
                'validation_passed': True,
                'success_rate': 100.0,
                'total_invoices': total_invoices,
                'valid_invoices': valid_invoices,
                'exported_files': exported_files,
                'export_path': export_path,
                'validation_summary': validation_result
            }
            
        except Exception as e:
            return {
                'export_success': False,
                'validation_passed': True,
                'export_error': str(e),
                'export_path': None
            }
    
    def _create_export_structure(self, config: Dict[str, Any]) -> str:
        """
        Create proper export folder structure:
        LedgerFlow/<Company>/<Date>/
        """
        base_path = Path.home() / "Desktop" / "LedgerFlow"
        company_name = config.get('business_name', 'Company').replace(' ', '_')
        date_str = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        export_path = base_path / company_name / date_str
        export_path.mkdir(parents=True, exist_ok=True)
        
        return str(export_path)
    
    def _generate_invoice_pdf(self, invoice: Dict[str, Any], export_path: str) -> str:
        """
        Generate individual invoice PDF using production engine.
        """
        invoice_number = invoice.get('invoice_number', 'INV_001')
        filename = f"{invoice_number}.pdf"
        filepath = os.path.join(export_path, filename)
        
        # Use template_type for PDF generation (from UI selection)
        template_type = invoice.get('template_type', 'gst_einvoice')
        
        # Map template_type to PDF engine methods
        if template_type == 'gst_einvoice':
            return self.pdf_engine.generate_gst_invoice(invoice, filepath)
        elif template_type == 'bahrain_vat':
            return self.pdf_engine.generate_vat_invoice(invoice, filepath)
        elif template_type == 'plain_cash':
            return self.pdf_engine.generate_plain_invoice(invoice, filepath)
        else:
            # Fallback to legacy invoice_type mapping for compatibility
            invoice_type = invoice.get('invoice_type', 'plain')
            if invoice_type == 'gst':
                return self.pdf_engine.generate_gst_invoice(invoice, filepath)
            elif invoice_type == 'vat':
                return self.pdf_engine.generate_vat_invoice(invoice, filepath)
            else:
                return self.pdf_engine.generate_plain_invoice(invoice, filepath)
    
    def get_validation_errors(self, invoices: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Get detailed validation errors for UI display.
        """
        validation_result = self.verification_engine.verify_invoice_batch(invoices)
        return validation_result.get('error_summary', [])
