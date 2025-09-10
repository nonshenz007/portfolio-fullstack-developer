from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
import os
from datetime import datetime
from config import Config
from app.core.pdf_template_engine import PDFTemplateEngine
from PyPDF2 import PdfMerger
import tempfile

class PDFExporter:
    """Service for exporting invoices as professional PDFs using distinct templates"""
    
    def __init__(self):
        self.template_engine = PDFTemplateEngine()
        
    def export_invoice(self, invoice, filename=None):
        """Export invoice to PDF using distinct templates"""
        if not filename:
            filename = f"{invoice.invoice_number}.pdf"
        
        # If filename is not a full path, create full path
        if not os.path.isabs(filename):
            filepath = os.path.join(Config.EXPORT_FOLDER, filename)
        else:
            filepath = filename
        
        # Ensure export directory exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # Use the new template engine for distinct layouts
        return self.template_engine.generate_invoice_pdf(invoice, filepath)
    
    def export_multiple(self, invoices, combined_filename=None):
        """Export multiple invoices and combine them into a single PDF"""
        if not invoices:
            raise ValueError("No invoices to export")
        
        if not combined_filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            combined_filename = f"invoices_combined_{timestamp}.pdf"
        
        # If filename is not a full path, create full path
        if not os.path.isabs(combined_filename):
            combined_filepath = os.path.join(Config.EXPORT_FOLDER, combined_filename)
        else:
            combined_filepath = combined_filename
        
        # Ensure export directory exists
        os.makedirs(os.path.dirname(combined_filepath), exist_ok=True)
        
        # Create temporary directory for individual PDFs
        with tempfile.TemporaryDirectory() as temp_dir:
            individual_paths = []
            
            # Generate individual PDFs
            for i, invoice in enumerate(invoices):
                temp_filename = f"temp_invoice_{i}_{invoice.invoice_number}.pdf"
                temp_path = os.path.join(temp_dir, temp_filename)
                
                try:
                    self.export_invoice(invoice, temp_path)
                    individual_paths.append(temp_path)
                except Exception as e:
                    print(f"Warning: Failed to export invoice {invoice.invoice_number}: {str(e)}")
                    continue
            
            # Combine PDFs
            if individual_paths:
                merger = PdfMerger()
                
                for pdf_path in individual_paths:
                    try:
                        merger.append(pdf_path)
                    except Exception as e:
                        print(f"Warning: Failed to merge PDF {pdf_path}: {str(e)}")
                        continue
                
                # Write combined PDF
                with open(combined_filepath, 'wb') as output_file:
                    merger.write(output_file)
                
                merger.close()
                return combined_filepath
            else:
                raise RuntimeError("No individual PDFs were successfully generated")
    
    def export_batch_organized(self, invoices, company_name=None, export_date=None):
        """Export invoices with organized folder structure"""
        from app.core.export_manager import ExportManager
        
        export_manager = ExportManager()
        return export_manager.export_invoices_batch(invoices, company_name, export_date) 