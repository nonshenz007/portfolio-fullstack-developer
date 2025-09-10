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
    
    def generate_gst_invoice(self, filename: str) -> float:
        """Generate CLEAN GST Invoice - ZERO artifacts"""
        filepath = os.path.join(self.output_dir, filename)
        c = canvas.Canvas(filepath, pagesize=A4)
        
        # Start from top
        y = self.height - self.margin
        
        # HEADER - Clean blue background, NO borders
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
        
        y -= header_height + 15
        
        # SELLER/BUYER SECTION - Clean boxes with minimal borders
        section_height = 80
        box_width = self.content_width / 2 - 5
        
        # Seller box - light gray background, no heavy borders
        self._draw_clean_rect(c, self.margin, y - section_height, box_width, section_height, 
                             fill_color=colors.Color(0.98, 0.98, 0.98))
        
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
                             fill_color=colors.Color(0.98, 0.98, 0.98))
        
        buyer_text = [
            "BUYER DETAILS",
            "",
            customer_profile.name
        ]
        
        for i, line in enumerate(buyer_text):
            font = "Helvetica-Bold" if i == 0 else "Helvetica"
            self._draw_clean_text(c, line, self.margin + box_width + 15, y - 15 - (i * 10), font, 9)
        
        y -= section_height + 25
        
        # ITEMS TABLE - Clean design, NO grid lines
        row_height = 25
        
        # Table header - clean background
        header_y = y - row_height
        self._draw_clean_rect(c, self.margin, header_y, self.content_width, row_height, 
                             fill_color=colors.HexColor('#1a365d'))
        
        # Column headers
        headers = ["S.No", "Description", "HSN/SAC", "Qty", "Unit", "Rate (₹)", "Amount (₹)", "Tax Rate", "Tax Amt (₹)", "Total (₹)"]
        col_positions = [self.margin + 10, self.margin + 40, self.margin + 160, self.margin + 220, 
                        self.margin + 250, self.margin + 280, self.margin + 340, self.margin + 410, 
                        self.margin + 460, self.margin + 520]
        
        for i, header in enumerate(headers):
            self._draw_clean_text(c, header, col_positions[i], header_y + 8, "Helvetica-Bold", 8, colors.white)
        
        # Table rows - alternating clean backgrounds
        selected_items = self.products[:4]
        subtotal = 0
        total_tax = 0
        
        for i, item in enumerate(selected_items):
            row_y = header_y - (i + 1) * row_height
            
            # Clean alternating row background
            if i % 2 == 0:
                self._draw_clean_rect(c, self.margin, row_y, self.content_width, row_height, 
                                     fill_color=colors.Color(0.97, 0.97, 0.97))
            
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
            
            for j, data in enumerate(row_data):
                if j >= 5:  # Right align amounts
                    self._draw_clean_text_right(c, data, col_positions[j] + 60, row_y + 8, "Helvetica", 8)
                else:
                    self._draw_clean_text(c, data, col_positions[j], row_y + 8, "Helvetica", 8)
        
        y = header_y - len(selected_items) * row_height - 25
        
        # TOTALS SECTION - Clean right-aligned boxes
        cgst_amount = total_tax / 2
        sgst_amount = total_tax / 2
        grand_total = subtotal + total_tax
        
        totals_x = self.width - self.margin - 160
        totals_width = 160
        
        totals_data = [
            ("Taxable Amount:", f"₹{subtotal:,.0f}"),
            ("CGST (9%):", f"₹{cgst_amount:,.0f}"),
            ("SGST (9%):", f"₹{sgst_amount:,.0f}"),
            ("Total Tax:", f"₹{total_tax:,.0f}"),
            ("GRAND TOTAL:", f"₹{grand_total:,.0f}")
        ]
        
        for i, (label, amount) in enumerate(totals_data):
            row_y = y - i * 22
            
            # Clean background for grand total
            if i == len(totals_data) - 1:
                self._draw_clean_rect(c, totals_x, row_y - 3, totals_width, 18, 
                                     fill_color=colors.HexColor('#3182ce'))
                color = colors.white
                font = "Helvetica-Bold"
            else:
                color = colors.black
                font = "Helvetica"
            
            self._draw_clean_text(c, label, totals_x + 5, row_y, font, 10, color)
            self._draw_clean_text_right(c, amount, totals_x + totals_width - 5, row_y, font, 10, color)
        
        y -= len(totals_data) * 22 + 25
        
        # AMOUNT IN WORDS
        amount_words = self._number_to_words_inr(grand_total)
        self._draw_clean_text(c, f"Amount in Words: {amount_words}", self.margin, y, "Helvetica-Bold", 10)
        
        y -= 35
        
        # FOOTER - Clean text only
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
        print("📄 Generating ULTRA CLEAN GST Invoice...")
        gst_total = self.generate_gst_invoice("ultra_clean_gst.pdf")
        results['GST'] = gst_total
        print(f"✅ ULTRA CLEAN GST Invoice: ₹{gst_total:,.0f}")
        
        # Generate VAT Invoice
        print("📄 Generating ULTRA CLEAN VAT Invoice...")
        vat_total = self.generate_vat_invoice("ultra_clean_vat.pdf")
        results['VAT'] = vat_total
        print(f"✅ ULTRA CLEAN VAT Invoice: BHD {vat_total:.3f}")
        
        # Generate Cash Receipt
        print("📄 Generating ULTRA CLEAN Cash Receipt...")
        cash_total = self.generate_cash_receipt("ultra_clean_cash.pdf")
        results['CASH'] = cash_total
        print(f"✅ ULTRA CLEAN Cash Receipt: ₹{cash_total:,.0f}")
        
        print("=" * 60)
        print("🎯 ULTRA CLEAN APPROACH:")
        print("• Canvas-based drawing - pixel perfect control")
        print("• NO table borders or grid artifacts")
        print("• Clean backgrounds with subtle colors")
        print("• Zero white blocks or black blocks")
        print("• Professional minimalist design")
        print("• Bilingual support for VAT invoices")
        print("• Real database integration")
        print("=" * 60)
        
        return results

if __name__ == "__main__":
    generator = PerfectCleanGenerator()
    results = generator.generate_all_clean_invoices()
    
    print(f"\n🎉 ULTRA CLEAN GENERATION COMPLETE!")
    print(f"📁 Files saved in: {generator.output_dir}/")    
 
   def generate_vat_invoice(self, filename: str) -> float:
        """Generate ULTRA CLEAN VAT Invoice - Bilingual, ZERO artifacts"""
        filepath = os.path.join(self.output_dir, filename)
        c = canvas.Canvas(filepath, pagesize=A4)
        
        # Start from top
        y = self.height - self.margin
        
        # HEADER - Clean green background, NO borders
        header_height = 55
        self._draw_clean_rect(c, self.margin, y - header_height, self.content_width, header_height, 
                             fill_color=colors.HexColor('#2d5016'))
        
        # Header text - Bilingual
        self._draw_clean_text(c, "VAT INVOICE", self.margin + 10, y - 25, 
                             "Helvetica-Bold", 16, colors.white)
        self._draw_clean_text(c, "فاتورة ضريبة القيمة المضافة", self.margin + 10, y - 42, 
                             "Helvetica", 10, colors.white)
        
        invoice_info = f"VAT/BH/250726/00001\nDate: {date.today().strftime('%d/%m/%Y')}\nKingdom of Bahrain\nمملكة البحرين"
        lines = invoice_info.split('\n')
        for i, line in enumerate(lines):
            self._draw_clean_text_right(c, line, self.width - self.margin - 10, y - 12 - (i * 10), 
                                       "Helvetica-Bold", 9, colors.white)
        
        y -= header_height + 15
        
        # SELLER/CUSTOMER SECTION - Clean backgrounds
        section_height = 90
        box_width = self.content_width / 2 - 5
        
        # Seller box
        self._draw_clean_rect(c, self.margin, y - section_height, box_width, section_height, 
                             fill_color=colors.Color(0.97, 1, 0.97))
        
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
                             fill_color=colors.Color(0.97, 1, 0.97))
        
        customer_text = [
            "CUSTOMER | العميل",
            "",
            f"{customer_profile.name} | أحمد الراشد"
        ]
        
        for i, line in enumerate(customer_text):
            font = "Helvetica-Bold" if i == 0 else "Helvetica"
            self._draw_clean_text(c, line, self.margin + box_width + 15, y - 12 - (i * 10), font, 9)
        
        y -= section_height + 25
        
        # ITEMS TABLE - Ultra clean design
        row_height = 28
        header_y = y - row_height
        self._draw_clean_rect(c, self.margin, header_y, self.content_width, row_height, 
                             fill_color=colors.HexColor('#2d5016'))
        
        # Bilingual headers
        headers = ["Code\nالرمز", "Description\nالوصف", "Unit\nالوحدة", "Qty\nالكمية", 
                  "Rate (BHD)\nالسعر", "Amount\nالمبلغ", "VAT%\nالضريبة", "VAT Amt\nض.القيمة", "Total\nالإجمالي"]
        col_positions = [self.margin + 5, self.margin + 45, self.margin + 145, self.margin + 180, 
                        self.margin + 215, self.margin + 270, self.margin + 325, self.margin + 365, self.margin + 420]
        
        for i, header in enumerate(headers):
            lines = header.split('\n')
            for j, line in enumerate(lines):
                self._draw_clean_text(c, line, col_positions[i], header_y + 18 - (j * 8), 
                                     "Helvetica-Bold", 7, colors.white)
        
        # Table rows
        selected_items = self.products[1:4]
        conversion_rate = 0.005  # 1 INR = 0.005 BHD
        subtotal_bhd = 0
        total_vat = 0
        
        for i, item in enumerate(selected_items):
            row_y = header_y - (i + 1) * row_height
            
            # Clean alternating backgrounds
            if i % 2 == 0:
                self._draw_clean_rect(c, self.margin, row_y, self.content_width, row_height, 
                                     fill_color=colors.Color(0.98, 1, 0.98))
            
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
            
            for j, data in enumerate(row_data):
                if j >= 4:  # Right align amounts
                    self._draw_clean_text_right(c, data, col_positions[j] + 50, row_y + 10, "Helvetica", 8)
                else:
                    self._draw_clean_text(c, data, col_positions[j], row_y + 10, "Helvetica", 8)
        
        y = header_y - len(selected_items) * row_height - 25
        
        # VAT TOTALS - Ultra clean
        grand_total = subtotal_bhd + total_vat
        
        totals_x = self.width - self.margin - 190
        totals_width = 190
        
        totals_data = [
            ("Subtotal (Excl. VAT) | المجموع الفرعي:", f"BHD {subtotal_bhd:.3f}"),
            ("VAT @ 10% | ضريبة القيمة المضافة:", f"BHD {total_vat:.3f}"),
            ("GRAND TOTAL | المجموع الكلي:", f"BHD {grand_total:.3f}")
        ]
        
        for i, (label, amount) in enumerate(totals_data):
            row_y = y - i * 24
            
            if i == len(totals_data) - 1:
                self._draw_clean_rect(c, totals_x, row_y - 3, totals_width, 20, 
                                     fill_color=colors.HexColor('#48bb78'))
                color = colors.white
                font = "Helvetica-Bold"
            else:
                color = colors.black
                font = "Helvetica"
            
            self._draw_clean_text(c, label, totals_x + 5, row_y, font, 9, color)
            self._draw_clean_text_right(c, amount, totals_x + totals_width - 5, row_y, font, 9, color)
        
        y -= len(totals_data) * 24 + 25
        
        # AMOUNT IN WORDS - Bilingual
        amount_words = self._number_to_words_bhd(grand_total)
        self._draw_clean_text(c, f"Amount in Words | المبلغ بالكلمات: {amount_words}", 
                             self.margin, y, "Helvetica-Bold", 9)
        
        y -= 35
        
        # FOOTER - Bilingual, clean
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
        """Generate ULTRA CLEAN Cash Receipt - ZERO artifacts"""
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
        
        y -= header_height + 15
        
        # RECEIVED FROM / BUSINESS SECTION - Clean backgrounds
        section_height = 70
        box_width = self.content_width / 2 - 5
        
        # Received from box
        customer_profile = self.name_generator.generate_customer_profile(
            region='generic_indian', customer_type='individual', invoice_type='cash'
        )
        
        self._draw_clean_rect(c, self.margin, y - section_height, box_width, section_height, 
                             fill_color=colors.Color(0.98, 0.95, 1))
        
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
                             fill_color=colors.Color(0.98, 0.95, 1))
        
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
        
        y -= section_height + 25
        
        # ITEMS TABLE - Ultra clean
        row_height = 30
        header_y = y - row_height
        self._draw_clean_rect(c, self.margin, header_y, self.content_width, row_height, 
                             fill_color=colors.HexColor('#7c3aed'))
        
        headers = ["S.No", "Item Description", "Quantity", "Unit Price (₹)", "Total Amount (₹)"]
        col_positions = [self.margin + 10, self.margin + 60, self.margin + 260, self.margin + 340, self.margin + 440]
        
        for i, header in enumerate(headers):
            self._draw_clean_text(c, header, col_positions[i], header_y + 10, "Helvetica-Bold", 10, colors.white)
        
        # Table rows
        selected_items = self.products[:3]
        total_amount = 0
        
        for i, item in enumerate(selected_items):
            row_y = header_y - (i + 1) * row_height
            
            # Clean alternating backgrounds
            if i % 2 == 0:
                self._draw_clean_rect(c, self.margin, row_y, self.content_width, row_height, 
                                     fill_color=colors.Color(0.98, 0.95, 1))
            
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
            
            for j, data in enumerate(row_data):
                if j >= 3:  # Right align amounts
                    self._draw_clean_text_right(c, data, col_positions[j] + 90, row_y + 10, "Helvetica", 9)
                else:
                    self._draw_clean_text(c, data, col_positions[j], row_y + 10, "Helvetica", 9)
        
        y = header_y - len(selected_items) * row_height - 25
        
        # TOTAL AMOUNT - Ultra clean highlight
        total_box_width = 220
        total_x = self.width - self.margin - total_box_width
        
        self._draw_clean_rect(c, total_x, y - 35, total_box_width, 35, 
                             fill_color=colors.HexColor('#7c3aed'))
        
        self._draw_clean_text(c, "TOTAL AMOUNT RECEIVED:", total_x + 10, y - 15, 
                             "Helvetica-Bold", 12, colors.white)
        self._draw_clean_text_right(c, f"₹{total_amount:,.0f}", total_x + total_box_width - 10, y - 15, 
                                   "Helvetica-Bold", 14, colors.white)
        
        y -= 55
        
        # AMOUNT IN WORDS
        amount_words = self._number_to_words_inr(total_amount)
        self._draw_clean_text(c, f"Amount in Words: {amount_words}", self.margin, y, "Helvetica-Bold", 10)
        
        y -= 40
        
        # PAYMENT INFO & SIGNATURE - Clean layout
        payment_info = [
            f"Payment Method: Cash",
            f"Payment Status: Received in Full",
            f"Received By: Store Manager",
            f"Time: {datetime.now().strftime('%I:%M %p')}"
        ]
        
        for i, info in enumerate(payment_info):
            self._draw_clean_text(c, info, self.margin, y - (i * 12), "Helvetica", 10)
        
        # Customer signature area
        self._draw_clean_text_right(c, "Customer Signature", self.width - self.margin, y, "Helvetica-Bold", 10)
        self._draw_clean_text_right(c, "_________________", self.width - self.margin, y - 25, "Helvetica", 10)
        self._draw_clean_text_right(c, customer_profile.name, self.width - self.margin, y - 40, "Helvetica", 9)
        
        y -= 70
        
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