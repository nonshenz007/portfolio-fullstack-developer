from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from datetime import datetime
import os
from flask import render_template
from app.models.template_type import TemplateType
import qrcode
from io import BytesIO
import base64
import pdfkit
import tempfile

class PDFTemplateEngine:
    """
    Enhanced PDF template engine for LedgerFlow.
    Generates three distinct invoice formats using Jinja templates:
    - GST E-Invoice (India)
    - Bahrain VAT Invoice
    - Plain Cash Invoice
    """
    
    def __init__(self):
        self.page_width = A4[0]
        self.page_height = A4[1]
        self.template_path = "pdf"  # Relative to templates directory
    
    def generate_invoice_pdf(self, invoice, output_path: str) -> str:
        """Generate PDF invoice based on template type"""
        try:
            # Determine template type from invoice
            template_type = getattr(invoice, 'template_type', TemplateType.GST_EINVOICE)
            
            # If template_type is not set but invoice_type is, convert it
            if not template_type and hasattr(invoice, 'invoice_type'):
                template_type = TemplateType.from_invoice_type(invoice.invoice_type)
            
            # Render the appropriate template
            if template_type == TemplateType.GST_EINVOICE:
                return self._generate_gst_invoice(invoice, output_path)
            elif template_type == TemplateType.BAHRAIN_VAT:
                return self._generate_vat_invoice(invoice, output_path)
            elif template_type == TemplateType.PLAIN_CASH:
                return self._generate_cash_invoice(invoice, output_path)
            else:
                # Default to GST if template type is not recognized
                return self._generate_gst_invoice(invoice, output_path)
                
        except Exception as e:
            print(f"PDF generation error: {str(e)}")
            # Create a basic fallback PDF
            return self._generate_fallback_pdf(invoice, output_path)
    
    def _generate_gst_invoice(self, invoice, output_path: str) -> str:
        """Generate GST (India) invoice using Jinja template"""
        # Generate QR code if needed
        if not hasattr(invoice, 'qr_code'):
            invoice.qr_code = self._generate_qr_code(invoice)
            
        # Prepare template data
        template_data = self._prepare_template_data(invoice, TemplateType.GST_EINVOICE)
        
        # Render the template
        html_content = render_template(f"{self.template_path}/gst_einvoice.html", invoice=template_data)
        
        # Convert HTML to PDF
        return self._html_to_pdf(html_content, output_path)
    
    def _generate_vat_invoice(self, invoice, output_path: str) -> str:
        """Generate VAT (Bahrain) invoice using Jinja template"""
        # Prepare template data
        template_data = self._prepare_template_data(invoice, TemplateType.BAHRAIN_VAT)
        
        # Render the template
        html_content = render_template(f"{self.template_path}/bahrain_vat.html", invoice=template_data)
        
        # Convert HTML to PDF
        return self._html_to_pdf(html_content, output_path)
    
    def _generate_cash_invoice(self, invoice, output_path: str) -> str:
        """Generate Cash/Plain invoice using Jinja template"""
        # Prepare template data
        template_data = self._prepare_template_data(invoice, TemplateType.PLAIN_CASH)
        
        # Render the template
        html_content = render_template(f"{self.template_path}/plain_cash.html", invoice=template_data)
        
        # Convert HTML to PDF
        return self._html_to_pdf(html_content, output_path)
    
    def _prepare_template_data(self, invoice, template_type):
        """
        Prepares the data dictionary based on template type.
        Only includes fields required by the specific template.
        
        Args:
            invoice: The invoice object
            template_type: The TemplateType enum value
            
        Returns:
            Dict with template-specific data
        """
        # Common data for all templates
        data = invoice
        
        # Template-specific data
        if template_type == TemplateType.GST_EINVOICE:
            # Generate QR code if not already present
            if not hasattr(invoice, 'qr_code'):
                data.qr_code = self._generate_qr_code(invoice)
            
            # Set IRN and Ack No if not present
            if not hasattr(invoice, 'irn'):
                data.irn = f"IRN{invoice.invoice_number}"
            if not hasattr(invoice, 'ack_no'):
                data.ack_no = f"ACK{invoice.invoice_number}"
                
            # Set page metadata
            data.page_size = "A4"
            data.page_orientation = "portrait"
            data.margins = {"top": "10mm", "right": "10mm", "bottom": "10mm", "left": "10mm"}
            
        elif template_type == TemplateType.BAHRAIN_VAT:
            # Set page metadata
            data.page_size = "A4"
            data.page_orientation = "portrait"
            data.margins = {"top": "10mm", "right": "10mm", "bottom": "10mm", "left": "10mm"}
            data.embedded_fonts = {
                "arabic": "Amiri, Arial Unicode MS, sans-serif"
            }
            
        elif template_type == TemplateType.PLAIN_CASH:
            # Set page metadata
            data.page_size = "A4"
            data.page_orientation = "portrait"
            data.margins = {"top": "10mm", "right": "10mm", "bottom": "10mm", "left": "10mm"}
        
        return data
    
    def _generate_qr_code(self, invoice):
        """
        Generates a QR code for GST e-invoices.
        
        Args:
            invoice: The invoice object
            
        Returns:
            Base64 encoded QR code image
        """
        try:
            # QR code payload format for GST e-invoice:
            # Format: GSTIN|Invoice Number|Invoice Date|Total Amount|HSN Code|CGST Amount|SGST Amount
            seller_gstin = getattr(invoice, 'business_tax_number', '22AAAAA0000A1Z5')
            
            # Get HSN code from first item or use default
            hsn_code = "998431"  # Default HSN code
            if hasattr(invoice, 'items') and invoice.items and hasattr(invoice.items[0], 'hsn_sac_code'):
                hsn_code = invoice.items[0].hsn_sac_code or hsn_code
            
            # Format date as YYYY-MM-DD
            invoice_date = invoice.invoice_date.strftime('%Y-%m-%d') if hasattr(invoice, 'invoice_date') else datetime.now().strftime('%Y-%m-%d')
            
            # Get tax amounts
            cgst_amount = getattr(invoice, 'cgst_amount', 0)
            sgst_amount = getattr(invoice, 'sgst_amount', 0)
            
            # Create QR code payload
            qr_payload = f"{seller_gstin}|{invoice.invoice_number}|{invoice_date}|{invoice.total_amount}|{hsn_code}|{cgst_amount}|{sgst_amount}"
            
            # Generate QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(qr_payload)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Convert to base64
            buffered = BytesIO()
            img.save(buffered)
            img_str = base64.b64encode(buffered.getvalue()).decode()
            
            return f"data:image/png;base64,{img_str}"
        except Exception as e:
            print(f"Error generating QR code: {str(e)}")
            return ""
    
    def _html_to_pdf(self, html_content, output_path):
        """
        Converts HTML content to PDF.
        
        Args:
            html_content: The HTML content to convert
            output_path: The path to save the PDF
            
        Returns:
            The output path
        """
        try:
            # Create a temporary HTML file
            with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as temp_html:
                temp_html.write(html_content.encode('utf-8'))
                temp_html_path = temp_html.name
            
            # Convert HTML to PDF using pdfkit
            options = {
                'page-size': 'A4',
                'margin-top': '10mm',
                'margin-right': '10mm',
                'margin-bottom': '10mm',
                'margin-left': '10mm',
                'encoding': 'UTF-8',
                'no-outline': None
            }
            
            pdfkit.from_file(temp_html_path, output_path, options=options)
            
            # Clean up temporary file
            os.unlink(temp_html_path)
            
            return output_path
        except Exception as e:
            print(f"Error converting HTML to PDF: {str(e)}")
            # Fall back to the basic PDF generation
            return self._generate_fallback_pdf({"invoice_number": "ERROR", "invoice_date": datetime.now()}, output_path)
    
    def _generate_fallback_pdf(self, invoice, output_path: str) -> str:
        """Generate a basic fallback PDF if other methods fail"""
        c = canvas.Canvas(output_path, pagesize=A4)
        width, height = A4
        
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, height - 50, "INVOICE")
        
        c.setFont("Helvetica", 12)
        c.drawString(50, height - 100, f"Invoice No: {getattr(invoice, 'invoice_number', 'N/A')}")
        c.drawString(50, height - 120, f"Date: {getattr(invoice, 'invoice_date', datetime.now()).strftime('%d-%m-%Y')}")
        c.drawString(50, height - 140, f"Customer: {getattr(invoice, 'customer_name', 'N/A')}")
        c.drawString(50, height - 160, f"Total: ₹{getattr(invoice, 'total_amount', 0):.2f}")
        
        c.save()
        return output_path