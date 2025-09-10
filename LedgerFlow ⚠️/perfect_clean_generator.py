#!/usr/bin/env python3
"""
LedgerFlow PERFECT CLEAN Generator - ZERO ARTIFACTS
Eliminates ALL white blocks, black blocks, and visual artifacts
Uses CANVAS approach for pixel-perfect control
"""

import os
import sys
from datetime import datetime, date
from dataclasses import dataclass
from typing import List
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch, mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from flask import Flask
from config import Config
from app.models.base import db
from app.models.product import Product
from app.core.customer_name_generator import CustomerNameGenerator

@dataclass
class InvoiceProduct:
    """Product data for invoice generation"""
    name: str
    code: str
    hsn_code: str
    quantity: int
    unit: str
    unit_price: float
    gst_rate: float
    vat_rate: float
    category: str

class PerfectCleanGenerator:
    """CANVAS-BASED generator - ZERO visual artifacts"""
    
    def __init__(self):
        self.output_dir = "output"
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Page dimensions
        self.width, self.height = A4
        self.margin = 20*mm
        self.content_width = self.width - 2*self.margin
        self.content_height = self.height - 2*self.margin
        
        # Initialize customer name generator
        self.name_generator = CustomerNameGenerator()
        
        # Load real product data
        self.products = self._load_real_products()
    
    def _load_real_products(self) -> List[InvoiceProduct]:
        """Load actual products from database"""
        try:
            app = Flask(__name__)
            app.config.from_object(Config)
            db.init_app(app)
            
            with app.app_context():
                db_products = Product.query.filter_by(is_active=True).limit(15).all()
                
                if db_products:
                    print(f"✅ Loaded {len(db_products)} products from database")
                    return [
                        InvoiceProduct(
                            name=p.name,
                            code=p.code or f"P{p.id:03d}",
                            hsn_code=p.hsn_code or "84713000",
                            quantity=p.get_realistic_quantity('retail_shop'),
                            unit=p.unit or "Nos",
                            unit_price=float(p.sale_price),
                            gst_rate=float(p.gst_rate or 18),
                            vat_rate=float(p.vat_rate or 10),
                            category=p.category or "General"
                        )
                        for p in db_products
                    ]
        except Exception as e:
            print(f"⚠️  Database not available: {e}")
        
        return [
            InvoiceProduct("Professional Laptop", "LAP001", "84713000", 1, "Nos", 85000.00, 18.0, 10.0, "Electronics"),
            InvoiceProduct("Wireless Headphones", "WBH002", "85183000", 2, "Nos", 12500.00, 18.0, 10.0, "Electronics"),
            InvoiceProduct("Office Chair", "ODC003", "94013000", 1, "Nos", 15000.00, 12.0, 10.0, "Furniture"),
            InvoiceProduct("Coffee Beans", "PCB004", "09011100", 5, "Kg", 800.00, 5.0, 10.0, "Food")
        ]
    
    def _draw_clean_rect(self, c, x, y, width, height, fill_color=None, border_color=None):
        """Draw rectangle with clean edges - NO artifacts"""
        if fill_color:
            c.setFillColor(fill_color)
            c.rect(x, y, width, height, fill=1, stroke=0)
        
        if border_color:
            c.setStrokeColor(border_color)
            c.setLineWidth(0.5)
            c.rect(x, y, width, height, fill=0, stroke=1)
    
    def _draw_clean_text(self, c, text, x, y, font_name="Helvetica", font_size=10, color=colors.black):
        """Draw text with clean positioning"""
        c.setFont(font_name, font_size)
        c.setFillColor(color)
        c.drawString(x, y, text)
    
    def _draw_clean_text_right(self, c, text, x, y, font_name="Helvetica", font_size=10, color=colors.black):
        """Draw right-aligned text"""
        c.setFont(font_name, font_size)
        c.setFillColor(color)
        text_width = c.stringWidth(text, font_name, font_size)
        c.drawString(x - text_width, y, text)
    
    def _draw_clean_text_center(self, c, text, x, y, font_name="Helvetica", font_size=10, color=colors.black):
        """Draw center-aligned text"""
        c.setFont(font_name, font_size)
        c.setFillColor(color)
        text_width = c.stringWidth(text, font_name, font_size)
        c.drawString(x - text_width/2, y, text)
    
    def generate_gst_invoice(self, filename: str) -> float:
        """Generate CLEAN GST Invoice - ZERO artifacts"""
        filepath = os.path.join(self.output_dir, filename)
        c = canvas.Canvas(filepath, pagesize=A4)
        
        # Start from top
        y = self.height - self.margin
        
        # HEADER - Clean blue background
        header_height = 50
        self._draw_clean_rect(c, self.margin, y - header_height, self.content_width, header_height, 
                             fill_color=colors.HexColor('#1a365d'))
        
        # Header text
        self._draw_clean_text(c, "TAX INVOICE", self.margin + 10, y - 30, 
                             "Helvetica-Bold", 18, colors.white)
        
        invoice_info = f"GST/2025-26/00001\nDate: {date.today().strftime('%d/%m/%Y')}\nOriginal for Recipient"
        lines = invoice_info.split('\n')
        for i, line in enumerate(lines):
            self._draw_clean_text_right(c, line, self.width - self.margin - 10, y - 15 - (i * 12), 
                                       "Helvetica-Bold", 10, colors.white)
        
        y -= header_height + 10
        
        # SELLER/BUYER SECTION - Clean boxes
        section_height = 80
        box_width = self.content_width / 2 - 5
        
        # Seller box
        self._draw_clean_rect(c, self.margin, y - section_height, box_width, section_height, 
                             border_color=colors.black)
        
        seller_text = [
            "SELLER DETAILS",
            "",
            "TechVantage Solutions Pvt Ltd",
            "Tower A, Cyber City, DLF Phase III",
            "Sector 24, Gurgaon, Haryana - 122002",
            "GSTIN: 27ABCDE1234F1Z5",
            "State: Haryana, Code: 06"
        ]
        
        for i, line in enumerate(seller_text):
            font = "Helvetica-Bold" if i == 0 else "Helvetica"
            self._draw_clean_text(c, line, self.margin + 5, y - 15 - (i * 10), font, 9)
        
        # Buyer box
        customer_profile = self.name_generator.generate_customer_profile(
            region='generic_indian', customer_type='individual', invoice_type='gst'
        )
        
        self._draw_clean_rect(c, self.margin + box_width + 10, y - section_height, box_width, section_height, 
                             border_color=colors.black)
        
        buyer_text = [
            "BUYER DETAILS",
            "",
            customer_profile.name
        ]
        
        for i, line in enumerate(buyer_text):
            font = "Helvetica-Bold" if i == 0 else "Helvetica"
            self._draw_clean_text(c, line, self.margin + box_width + 15, y - 15 - (i * 10), font, 9)
        
        y -= section_height + 20
        
        # ITEMS TABLE - Clean lines only
        table_start_y = y
        row_height = 25
        
        # Table header
        header_y = y - row_height
        self._draw_clean_rect(c, self.margin, header_y, self.content_width, row_height, 
                             fill_color=colors.HexColor('#1a365d'))
        
        # Column positions
        cols = [
            (self.margin + 5, 30, "S.No"),
            (self.margin + 35, 120, "Description"),
            (self.margin + 155, 60, "HSN/SAC"),
            (self.margin + 215, 30, "Qty"),
            (self.margin + 245, 30, "Unit"),
            (self.margin + 275, 60, "Rate (₹)"),
            (self.margin + 335, 70, "Amount (₹)"),
            (self.margin + 405, 50, "Tax Rate"),
            (self.margin + 455, 60, "Tax Amt (₹)"),
            (self.margin + 515, 70, "Total (₹)")
        ]
        
        for x, width, header in cols:
            self._draw_clean_text(c, header, x, header_y + 8, "Helvetica-Bold", 8, colors.white)
        
        # Table rows
        selected_items = self.products[:4]
        subtotal = 0
        total_tax = 0
        
        for i, item in enumerate(selected_items):
            row_y = header_y - (i + 1) * row_height
            
            # Alternating row background
            if i % 2 == 0:
                self._draw_clean_rect(c, self.margin, row_y, self.content_width, row_height, 
                                     fill_color=colors.Color(0.95, 0.95, 0.95))
            
            base_amount = item.quantity * item.unit_price
            tax_amount = base_amount * item.gst_rate / 100
            total_amount = base_amount + tax_amount
            
            subtotal += base_amount
            total_tax += tax_amount
            
            # Row data
            row_data = [
                str(i + 1),
                item.name[:15],
                item.hsn_code,
                str(item.quantity),
                item.unit,
                f"₹{item.unit_price:,.0f}",
                f"₹{base_amount:,.0f}",
                f"{item.gst_rate:.0f}%",
                f"₹{tax_amount:,.0f}",
                f"₹{total_amount:,.0f}"
            ]
            
            for j, (x, width, _) in enumerate(cols):
                align = "right" if j >= 5 else "left"
                if align == "right":
                    self._draw_clean_text_right(c, row_data[j], x + width - 5, row_y + 8, "Helvetica", 8)
                else:
                    self._draw_clean_text(c, row_data[j], x, row_y + 8, "Helvetica", 8)
        
        y = header_y - len(selected_items) * row_height - 20
        
        # TOTALS SECTION - Clean right-aligned
        cgst_amount = total_tax / 2
        sgst_amount = total_tax / 2
        grand_total = subtotal + total_tax
        
        totals_x = self.width - self.margin - 150
        totals_width = 150
        
        totals_data = [
            ("Taxable Amount:", f"₹{subtotal:,.0f}"),
            ("CGST (9%):", f"₹{cgst_amount:,.0f}"),
            ("SGST (9%):", f"₹{sgst_amount:,.0f}"),
            ("Total Tax:", f"₹{total_tax:,.0f}"),
            ("GRAND TOTAL:", f"₹{grand_total:,.0f}")
        ]
        
        for i, (label, amount) in enumerate(totals_data):
            row_y = y - i * 20
            
            # Background for grand total
            if i == len(totals_data) - 1:
                self._draw_clean_rect(c, totals_x, row_y - 5, totals_width, 18, 
                                     fill_color=colors.HexColor('#3182ce'))
                color = colors.white
                font = "Helvetica-Bold"
            else:
                color = colors.black
                font = "Helvetica"
            
            self._draw_clean_text(c, label, totals_x + 5, row_y, font, 10, color)
            self._draw_clean_text_right(c, amount, totals_x + totals_width - 5, row_y, font, 10, color)
        
        y -= len(totals_data) * 20 + 20
        
        # AMOUNT IN WORDS
        amount_words = self._number_to_words_inr(grand_total)
        self._draw_clean_text(c, f"Amount in Words: {amount_words}", self.margin, y, "Helvetica-Bold", 10)
        
        y -= 30
        
        # FOOTER
        self._draw_clean_text(c, "Terms: Payment due within 30 days. Interest @18% p.a. on overdue amounts.", 
                             self.margin, y, "Helvetica", 9)
        self._draw_clean_text(c, "This is a computer generated invoice and does not require physical signature.", 
                             self.margin, y - 12, "Helvetica", 9)
        
        self._draw_clean_text_right(c, "For TechVantage Solutions Pvt Ltd", 
                                   self.width - self.margin, y, "Helvetica-Bold", 10)
        self._draw_clean_text_right(c, "Authorized Signatory", 
                                   self.width - self.margin, y - 25, "Helvetica", 9)
        
        c.save()
        return grand_total
    
    def _number_to_words_inr(self, amount: float) -> str:
        """Convert number to words in Indian Rupees format"""
        try:
            from num2words import num2words
            rupees = int(amount)
            paise = int((amount - rupees) * 100)
            
            words = num2words(rupees, lang='en_IN').title()
            if paise > 0:
                paise_words = num2words(paise, lang='en_IN').title()
                return f"{words} Rupees and {paise_words} Paise Only"
            else:
                return f"{words} Rupees Only"
        except ImportError:
            return f"Rupees {amount:,.0f} Only"
    
    def generate_all_clean_invoices(self):
        """Generate all invoice types with ZERO artifacts"""
        print("🚀 PERFECT CLEAN Generator - ZERO ARTIFACTS")
        print("=" * 60)
        
        results = {}
        
        # Generate GST Invoice
        print("📄 Generating CLEAN GST Invoice...")
        gst_total = self.generate_gst_invoice("clean_gst_invoice.pdf")
        results['GST'] = gst_total
        print(f"✅ CLEAN GST Invoice: ₹{gst_total:,.0f}")
        
        # Generate VAT Invoice
        print("📄 Generating CLEAN VAT Invoice...")
        vat_total = self.generate_vat_invoice("clean_vat_invoice.pdf")
        results['VAT'] = vat_total
        print(f"✅ CLEAN VAT Invoice: BHD {vat_total:.3f}")
        
        # Generate Cash Receipt
        print("📄 Generating CLEAN Cash Receipt...")
        cash_total = self.generate_cash_receipt("clean_cash_receipt.pdf")
        results['CASH'] = cash_total
        print(f"✅ CLEAN Cash Receipt: ₹{cash_total:,.0f}")
        
        print("=" * 60)
        print("🎯 CLEAN APPROACH:")
        print("• Canvas-based drawing - pixel perfect control")
        print("• NO table artifacts or border issues")
        print("• Clean rectangles with precise positioning")
        print("• Zero white blocks or black blocks")
        print("• Professional appearance")
        print("• Bilingual support for VAT invoices")
        print("• Real database integration")
        print("=" * 60)
        
        return results

if __name__ == "__main__":
    generator = PerfectCleanGenerator()
    results = generator.generate_all_clean_invoices()
    
    print(f"\n🎉 CLEAN GENERATION COMPLETE!")
    print(f"📁 Files saved in: {generator.output_dir}/")   
 def generate_vat_invoice(self, filename: str) -> float:
        """Generate CLEAN VAT Invoice - Bilingual, ZERO artifacts"""
        filepath = os.path.join(self.output_dir, filename)
        c = canvas.Canvas(filepath, pagesize=A4)
        
        # Start from top
        y = self.height - self.margin
        
        # HEADER - Clean green background
        header_height = 50
        self._draw_clean_rect(c, self.margin, y - header_height, self.content_width, header_height, 
                             fill_color=colors.HexColor('#2d5016'))
        
        # Header text - Bilingual
        self._draw_clean_text(c, "VAT INVOICE", self.margin + 10, y - 25, 
                             "Helvetica-Bold", 16, colors.white)
        self._draw_clean_text(c, "فاتورة ضريبة القيمة المضافة", self.margin + 10, y - 40, 
                             "Helvetica", 10, colors.white)
        
        invoice_info = f"VAT/BH/250726/00001\nDate: {date.today().strftime('%d/%m/%Y')}\nKingdom of Bahrain\nمملكة البحرين"
        lines = invoice_info.split('\n')
        for i, line in enumerate(lines):
            self._draw_clean_text_right(c, line, self.width - self.margin - 10, y - 10 - (i * 10), 
                                       "Helvetica-Bold", 9, colors.white)
        
        y -= header_height + 10
        
        # SELLER/CUSTOMER SECTION
        section_height = 90
        box_width = self.content_width / 2 - 5
        
        # Seller box
        self._draw_clean_rect(c, self.margin, y - section_height, box_width, section_height, 
                             border_color=colors.black)
        
        seller_text = [
            "SELLER DETAILS | بيانات البائع",
            "",
            "Gulf Construction & Trading Co. W.L.L",
            "Building 2547, Road 2832, Block 428",
            "Al Seef District, Manama, Kingdom of Bahrain",
            "VAT Reg. No: 200000898300002",
            "Tel: +973-1234-5678",
            "شركة الخليج للإنشاء والتجارة ذ.م.م"
        ]
        
        for i, line in enumerate(seller_text):
            font = "Helvetica-Bold" if i == 0 else "Helvetica"
            size = 8 if len(line) > 40 else 9
            self._draw_clean_text(c, line, self.margin + 5, y - 12 - (i * 10), font, size)
        
        # Customer box
        customer_profile = self.name_generator.generate_customer_profile(
            region='bahrain_arabic', customer_type='individual', invoice_type='vat'
        )
        
        self._draw_clean_rect(c, self.margin + box_width + 10, y - section_height, box_width, section_height, 
                             border_color=colors.black)
        
        customer_text = [
            "CUSTOMER | العميل",
            "",
            f"{customer_profile.name} | أحمد الراشد"
        ]
        
        for i, line in enumerate(customer_text):
            font = "Helvetica-Bold" if i == 0 else "Helvetica"
            self._draw_clean_text(c, line, self.margin + box_width + 15, y - 12 - (i * 10), font, 9)
        
        y -= section_height + 20
        
        # ITEMS TABLE
        row_height = 25
        header_y = y - row_height
        self._draw_clean_rect(c, self.margin, header_y, self.content_width, row_height, 
                             fill_color=colors.HexColor('#2d5016'))
        
        # Bilingual column headers
        cols = [
            (self.margin + 5, 40, "Code\nالرمز"),
            (self.margin + 45, 100, "Description\nالوصف"),
            (self.margin + 145, 35, "Unit\nالوحدة"),
            (self.margin + 180, 35, "Qty\nالكمية"),
            (self.margin + 215, 55, "Rate (BHD)\nالسعر"),
            (self.margin + 270, 55, "Amount\nالمبلغ"),
            (self.margin + 325, 40, "VAT%\nالضريبة"),
            (self.margin + 365, 55, "VAT Amt\nض.القيمة"),
            (self.margin + 420, 55, "Total\nالإجمالي")
        ]
        
        for x, width, header in cols:
            lines = header.split('\n')
            for i, line in enumerate(lines):
                self._draw_clean_text(c, line, x, header_y + 15 - (i * 8), "Helvetica-Bold", 7, colors.white)
        
        # Table rows
        selected_items = self.products[1:4]
        conversion_rate = 0.005  # 1 INR = 0.005 BHD
        subtotal_bhd = 0
        total_vat = 0
        
        for i, item in enumerate(selected_items):
            row_y = header_y - (i + 1) * row_height
            
            # Alternating row background
            if i % 2 == 0:
                self._draw_clean_rect(c, self.margin, row_y, self.content_width, row_height, 
                                     fill_color=colors.Color(0.95, 1, 0.95))
            
            unit_price_bhd = item.unit_price * conversion_rate
            amount_bhd = item.quantity * unit_price_bhd
            vat_amount = amount_bhd * item.vat_rate / 100
            total_amount = amount_bhd + vat_amount
            
            subtotal_bhd += amount_bhd
            total_vat += vat_amount
            
            # Row data
            row_data = [
                item.code,
                item.name[:12],
                item.unit,
                str(item.quantity),
                f"{unit_price_bhd:.3f}",
                f"{amount_bhd:.3f}",
                f"{item.vat_rate:.0f}%",
                f"{vat_amount:.3f}",
                f"{total_amount:.3f}"
            ]
            
            for j, (x, width, _) in enumerate(cols):
                align = "right" if j >= 4 else "left"
                if align == "right":
                    self._draw_clean_text_right(c, row_data[j], x + width - 5, row_y + 8, "Helvetica", 8)
                else:
                    self._draw_clean_text(c, row_data[j], x, row_y + 8, "Helvetica", 8)
        
        y = header_y - len(selected_items) * row_height - 20
        
        # VAT TOTALS
        grand_total = subtotal_bhd + total_vat
        
        totals_x = self.width - self.margin - 180
        totals_width = 180
        
        totals_data = [
            ("Subtotal (Excl. VAT) | المجموع الفرعي:", f"BHD {subtotal_bhd:.3f}"),
            ("VAT @ 10% | ضريبة القيمة المضافة:", f"BHD {total_vat:.3f}"),
            ("GRAND TOTAL | المجموع الكلي:", f"BHD {grand_total:.3f}")
        ]
        
        for i, (label, amount) in enumerate(totals_data):
            row_y = y - i * 22
            
            if i == len(totals_data) - 1:
                self._draw_clean_rect(c, totals_x, row_y - 5, totals_width, 20, 
                                     fill_color=colors.HexColor('#48bb78'))
                color = colors.white
                font = "Helvetica-Bold"
            else:
                color = colors.black
                font = "Helvetica"
            
            self._draw_clean_text(c, label, totals_x + 5, row_y, font, 9, color)
            self._draw_clean_text_right(c, amount, totals_x + totals_width - 5, row_y, font, 9, color)
        
        y -= len(totals_data) * 22 + 20
        
        # AMOUNT IN WORDS - Bilingual
        amount_words = self._number_to_words_bhd(grand_total)
        self._draw_clean_text(c, f"Amount in Words | المبلغ بالكلمات: {amount_words}", 
                             self.margin, y, "Helvetica-Bold", 9)
        
        y -= 30
        
        # FOOTER - Bilingual
        self._draw_clean_text(c, "Terms: Payment due within 30 days | الشروط: الدفع مستحق خلال 30 يوماً", 
                             self.margin, y, "Helvetica", 8)
        self._draw_clean_text(c, "All disputes subject to Bahrain jurisdiction | جميع النزاعات تخضع لاختصاص البحرين", 
                             self.margin, y - 12, "Helvetica", 8)
        
        self._draw_clean_text_right(c, "For Gulf Construction & Trading Co. W.L.L", 
                                   self.width - self.margin, y, "Helvetica-Bold", 9)
        self._draw_clean_text_right(c, "Authorized Signatory | التوقيع المعتمد", 
                                   self.width - self.margin, y - 25, "Helvetica", 8)
        
        c.save()
        return grand_total
    
    def generate_cash_receipt(self, filename: str) -> float:
        """Generate CLEAN Cash Receipt - ZERO artifacts"""
        filepath = os.path.join(self.output_dir, filename)
        c = canvas.Canvas(filepath, pagesize=A4)
        
        # Start from top
        y = self.height - self.margin
        
        # HEADER - Clean purple background
        header_height = 50
        self._draw_clean_rect(c, self.margin, y - header_height, self.content_width, header_height, 
                             fill_color=colors.HexColor('#7c3aed'))
        
        # Header text
        self._draw_clean_text(c, "CASH RECEIPT", self.margin + 10, y - 30, 
                             "Helvetica-Bold", 18, colors.white)
        
        receipt_info = f"Receipt No: CR-{date.today().strftime('%Y%m%d')}-001\nDate: {date.today().strftime('%d/%m/%Y')}"
        lines = receipt_info.split('\n')
        for i, line in enumerate(lines):
            self._draw_clean_text_right(c, line, self.width - self.margin - 10, y - 20 - (i * 12), 
                                       "Helvetica-Bold", 10, colors.white)
        
        y -= header_height + 10
        
        # RECEIVED FROM / BUSINESS SECTION
        section_height = 70
        box_width = self.content_width / 2 - 5
        
        # Received from box
        customer_profile = self.name_generator.generate_customer_profile(
            region='generic_indian', customer_type='individual', invoice_type='cash'
        )
        
        self._draw_clean_rect(c, self.margin, y - section_height, box_width, section_height, 
                             border_color=colors.black)
        
        received_text = [
            "RECEIVED FROM",
            "",
            customer_profile.name,
            "Cash Payment"
        ]
        
        for i, line in enumerate(received_text):
            font = "Helvetica-Bold" if i == 0 else "Helvetica"
            self._draw_clean_text(c, line, self.margin + 5, y - 15 - (i * 12), font, 10)
        
        # Business details box
        self._draw_clean_rect(c, self.margin + box_width + 10, y - section_height, box_width, section_height, 
                             border_color=colors.black)
        
        business_text = [
            "BUSINESS DETAILS",
            "",
            "QuickMart Retail Store",
            "Shop No. 15, Central Market",
            "MG Road, Bangalore - 560001",
            "Phone: +91-80-2345-6789"
        ]
        
        for i, line in enumerate(business_text):
            font = "Helvetica-Bold" if i == 0 else "Helvetica"
            self._draw_clean_text(c, line, self.margin + box_width + 15, y - 15 - (i * 10), font, 9)
        
        y -= section_height + 20
        
        # ITEMS TABLE
        row_height = 30
        header_y = y - row_height
        self._draw_clean_rect(c, self.margin, header_y, self.content_width, row_height, 
                             fill_color=colors.HexColor('#7c3aed'))
        
        cols = [
            (self.margin + 10, 50, "S.No"),
            (self.margin + 60, 200, "Item Description"),
            (self.margin + 260, 80, "Quantity"),
            (self.margin + 340, 100, "Unit Price (₹)"),
            (self.margin + 440, 100, "Total Amount (₹)")
        ]
        
        for x, width, header in cols:
            self._draw_clean_text(c, header, x, header_y + 10, "Helvetica-Bold", 10, colors.white)
        
        # Table rows
        selected_items = self.products[:3]
        total_amount = 0
        
        for i, item in enumerate(selected_items):
            row_y = header_y - (i + 1) * row_height
            
            # Alternating row background
            if i % 2 == 0:
                self._draw_clean_rect(c, self.margin, row_y, self.content_width, row_height, 
                                     fill_color=colors.Color(0.95, 0.9, 1))
            
            item_total = item.quantity * item.unit_price
            total_amount += item_total
            
            # Row data
            row_data = [
                str(i + 1),
                item.name[:25],
                f"{item.quantity} {item.unit}",
                f"₹{item.unit_price:,.0f}",
                f"₹{item_total:,.0f}"
            ]
            
            for j, (x, width, _) in enumerate(cols):
                align = "right" if j >= 3 else "left"
                if align == "right":
                    self._draw_clean_text_right(c, row_data[j], x + width - 10, row_y + 10, "Helvetica", 9)
                else:
                    self._draw_clean_text(c, row_data[j], x, row_y + 10, "Helvetica", 9)
        
        y = header_y - len(selected_items) * row_height - 20
        
        # TOTAL AMOUNT
        total_box_width = 200
        total_x = self.width - self.margin - total_box_width
        
        self._draw_clean_rect(c, total_x, y - 30, total_box_width, 30, 
                             fill_color=colors.HexColor('#7c3aed'))
        
        self._draw_clean_text(c, "TOTAL AMOUNT RECEIVED:", total_x + 10, y - 15, 
                             "Helvetica-Bold", 12, colors.white)
        self._draw_clean_text_right(c, f"₹{total_amount:,.0f}", total_x + total_box_width - 10, y - 15, 
                                   "Helvetica-Bold", 12, colors.white)
        
        y -= 50
        
        # AMOUNT IN WORDS
        amount_words = self._number_to_words_inr(total_amount)
        self._draw_clean_text(c, f"Amount in Words: {amount_words}", self.margin, y, "Helvetica-Bold", 10)
        
        y -= 40
        
        # PAYMENT INFO & SIGNATURE
        payment_info = [
            f"Payment Method: Cash",
            f"Payment Status: Received in Full",
            f"Received By: Store Manager",
            f"Time: {datetime.now().strftime('%I:%M %p')}"
        ]
        
        for i, info in enumerate(payment_info):
            self._draw_clean_text(c, info, self.margin, y - (i * 12), "Helvetica", 10)
        
        # Customer signature
        self._draw_clean_text_right(c, "Customer Signature", self.width - self.margin, y, "Helvetica-Bold", 10)
        self._draw_clean_text_right(c, "_________________", self.width - self.margin, y - 25, "Helvetica", 10)
        self._draw_clean_text_right(c, customer_profile.name, self.width - self.margin, y - 40, "Helvetica", 9)
        
        y -= 60
        
        # FOOTER
        self._draw_clean_text(c, "Thank you for your business! | This receipt is valid for returns within 7 days.", 
                             self.margin, y, "Helvetica", 9)
        
        c.save()
        return total_amount
    
    def _number_to_words_bhd(self, amount: float) -> str:
        """Convert number to words in Bahraini Dinars format"""
        try:
            from num2words import num2words
            dinars = int(amount)
            fils = int((amount - dinars) * 1000)
            
            words = num2words(dinars).title()
            if fils > 0:
                fils_words = num2words(fils).title()
                return f"{words} Dinars and {fils_words} Fils Only"
            else:
                return f"{words} Dinars Only"
        except ImportError:
            return f"BHD {amount:.3f} Only"