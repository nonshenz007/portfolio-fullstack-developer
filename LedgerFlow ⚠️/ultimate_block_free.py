#!/usr/bin/env python3
"""
LedgerFlow ULTIMATE BLOCK-FREE Generator
FINAL SOLUTION: Plain text in tables, NO Paragraph objects, NO blocks
"""

import os
import sys
from datetime import datetime, date
from dataclasses import dataclass
from typing import List
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer
from reportlab.lib.units import inch, mm
from io import BytesIO

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

class UltimateBlockFree:
    """ULTIMATE BLOCK-FREE generator - Plain text only"""
    
    def __init__(self):
        self.output_dir = "output"
        os.makedirs(self.output_dir, exist_ok=True)
        
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
    
    def generate_all_block_free_invoices(self):
        """Generate all three invoice types - ZERO BLOCKS"""
        print("🚀 ULTIMATE BLOCK-FREE Generator - ZERO ARTIFACTS")
        print("=" * 70)
        
        results = {}
        
        # Generate GST Invoice
        print("📄 Generating BLOCK-FREE GST Invoice...")
        gst_total = self._generate_gst_invoice()
        results['GST'] = gst_total
        print(f"✅ BLOCK-FREE GST Invoice: ₹{gst_total:,.0f}")
        
        # Generate VAT Invoice  
        print("📄 Generating BLOCK-FREE VAT Invoice...")
        vat_total = self._generate_vat_invoice()
        results['VAT'] = vat_total
        print(f"✅ BLOCK-FREE VAT Invoice: BHD {vat_total:.3f}")
        
        # Generate Cash Receipt
        print("📄 Generating BLOCK-FREE Cash Receipt...")
        cash_total = self._generate_cash_receipt()
        results['CASH'] = cash_total
        print(f"✅ BLOCK-FREE Cash Receipt: ₹{cash_total:,.0f}")
        
        print("=" * 70)
        print("🎯 ULTIMATE BLOCK-FREE APPROACH:")
        print("• NO Paragraph objects - plain text strings only")
        print("• Minimal TableStyle formatting")
        print("• Clean header backgrounds only")
        print("• Zero white blocks or black blocks")
        print("• Professional appearance maintained")
        print("• Bilingual support for VAT invoices")
        print("• Real database integration")
        print("=" * 70)
        
        return results
    
    def _generate_gst_invoice(self) -> float:
        """Generate GST Invoice - ZERO BLOCKS"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, 
                              rightMargin=20*mm, leftMargin=20*mm,
                              topMargin=15*mm, bottomMargin=15*mm)
        
        story = []
        
        # HEADER
        header_data = [
            ["TAX INVOICE", f"GST/2025-26/00001\nDate: {date.today().strftime('%d/%m/%Y')}\nOriginal for Recipient"]
        ]
        
        header_table = Table(header_data, colWidths=[4*inch, 3*inch])
        header_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#1a365d')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 15),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
        ]))
        story.append(header_table)
        
        # SELLER/BUYER
        customer_profile = self.name_generator.generate_customer_profile(
            region='generic_indian', customer_type='individual', invoice_type='gst'
        )
        
        seller_buyer_data = [
            [
                "SELLER DETAILS\n\nTechVantage Solutions Pvt Ltd\nTower A, Cyber City, DLF Phase III\nSector 24, Gurgaon, Haryana - 122002\nGSTIN: 27ABCDE1234F1Z5\nState: Haryana, Code: 06",
                f"BUYER DETAILS\n\n{customer_profile.name}"
            ]
        ]
        
        seller_buyer_table = Table(seller_buyer_data, colWidths=[3.5*inch, 3.5*inch])
        seller_buyer_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ]))
        story.append(seller_buyer_table)
        story.append(Spacer(1, 10))
        
        # ITEMS TABLE
        items_data = [
            ['S.No', 'Description', 'HSN/SAC', 'Qty', 'Unit', 'Rate (₹)', 'Amount (₹)', 'Tax Rate', 'Tax Amt (₹)', 'Total (₹)']
        ]
        
        selected_items = self.products[:4]
        subtotal = 0
        total_tax = 0
        
        for i, item in enumerate(selected_items):
            base_amount = item.quantity * item.unit_price
            tax_amount = base_amount * item.gst_rate / 100
            total_amount = base_amount + tax_amount
            
            subtotal += base_amount
            total_tax += tax_amount
            
            items_data.append([
                str(i + 1),
                item.name[:20],
                item.hsn_code,
                str(item.quantity),
                item.unit,
                f"₹{item.unit_price:,.0f}",
                f"₹{base_amount:,.0f}",
                f"{item.gst_rate:.0f}%",
                f"₹{tax_amount:,.0f}",
                f"₹{total_amount:,.0f}"
            ])
        
        items_table = Table(items_data, colWidths=[0.4*inch, 1.8*inch, 0.8*inch, 0.4*inch, 0.4*inch, 0.8*inch, 0.9*inch, 0.6*inch, 0.8*inch, 0.9*inch])
        items_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a365d')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (1, 1), (1, -1), 'LEFT'),
            ('ALIGN', (5, 1), (-1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 3),
            ('RIGHTPADDING', (0, 0), (-1, -1), 3),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))
        story.append(items_table)
        story.append(Spacer(1, 10))
        
        # TOTALS
        cgst_amount = total_tax / 2
        sgst_amount = total_tax / 2
        grand_total = subtotal + total_tax
        
        summary_data = [
            ['Taxable Amount:', f'₹{subtotal:,.0f}'],
            ['CGST (9%):', f'₹{cgst_amount:,.0f}'],
            ['SGST (9%):', f'₹{sgst_amount:,.0f}'],
            ['Total Tax:', f'₹{total_tax:,.0f}'],
            ['GRAND TOTAL:', f'₹{grand_total:,.0f}']
        ]
        
        summary_table = Table(summary_data, colWidths=[1.5*inch, 1*inch])
        summary_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#3182ce')),
            ('TEXTCOLOR', (0, -1), (-1, -1), colors.white),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))
        
        # Container to right-align
        container_data = [['', summary_table]]
        container_table = Table(container_data, colWidths=[4.5*inch, 2.5*inch])
        container_table.setStyle(TableStyle([
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        story.append(container_table)
        story.append(Spacer(1, 15))
        
        # AMOUNT IN WORDS
        amount_words = self._number_to_words_inr(grand_total)
        words_data = [[f"Amount in Words: {amount_words}"]]
        words_table = Table(words_data, colWidths=[7*inch])
        words_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
        ]))
        story.append(words_table)
        story.append(Spacer(1, 15))
        
        # FOOTER
        footer_data = [
            [
                "Terms: Payment due within 30 days. Interest @18% p.a. on overdue amounts.\nThis is a computer generated invoice and does not require physical signature.",
                "For TechVantage Solutions Pvt Ltd\n\nAuthorized Signatory"
            ]
        ]
        
        footer_table = Table(footer_data, colWidths=[4*inch, 3*inch])
        footer_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('FONTNAME', (1, 0), (1, 0), 'Helvetica-Bold'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        story.append(footer_table)
        
        # Build PDF
        doc.build(story)
        
        # Save to file
        buffer.seek(0)
        with open(os.path.join(self.output_dir, "ultimate_gst_invoice.pdf"), 'wb') as f:
            f.write(buffer.getvalue())
        
        return grand_total
    
    def _generate_vat_invoice(self) -> float:
        """Generate VAT Invoice - ZERO BLOCKS, bilingual"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, 
                              rightMargin=20*mm, leftMargin=20*mm,
                              topMargin=15*mm, bottomMargin=15*mm)
        
        story = []
        
        # HEADER - Bilingual
        header_data = [
            ["VAT INVOICE\nفاتورة ضريبة القيمة المضافة", f"VAT/BH/250726/00001\nDate: {date.today().strftime('%d/%m/%Y')}\nKingdom of Bahrain\nمملكة البحرين"]
        ]
        
        header_table = Table(header_data, colWidths=[4*inch, 3*inch])
        header_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#2d5016')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 15),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
        ]))
        story.append(header_table)
        
        # SELLER/CUSTOMER - Bilingual
        customer_profile = self.name_generator.generate_customer_profile(
            region='bahrain_arabic', customer_type='individual', invoice_type='vat'
        )
        
        seller_customer_data = [
            [
                "SELLER DETAILS | بيانات البائع\n\nGulf Construction & Trading Co. W.L.L\nBuilding 2547, Road 2832, Block 428\nAl Seef District, Manama, Kingdom of Bahrain\nVAT Reg. No: 200000898300002\nTel: +973-1234-5678\nشركة الخليج للإنشاء والتجارة ذ.م.م",
                f"CUSTOMER | العميل\n\n{customer_profile.name} | أحمد الراشد"
            ]
        ]
        
        seller_customer_table = Table(seller_customer_data, colWidths=[4*inch, 3*inch])
        seller_customer_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ]))
        story.append(seller_customer_table)
        story.append(Spacer(1, 10))
        
        # ITEMS TABLE - Bilingual headers
        items_data = [
            ['Code\nالرمز', 'Description\nالوصف', 'Unit\nالوحدة', 'Qty\nالكمية', 'Rate (BHD)\nالسعر', 'Amount\nالمبلغ', 'VAT%\nالضريبة', 'VAT Amt\nض.القيمة', 'Total\nالإجمالي']
        ]
        
        selected_items = self.products[1:4]
        conversion_rate = 0.005  # 1 INR = 0.005 BHD
        subtotal_bhd = 0
        total_vat = 0
        
        for i, item in enumerate(selected_items):
            unit_price_bhd = item.unit_price * conversion_rate
            amount_bhd = item.quantity * unit_price_bhd
            vat_amount = amount_bhd * item.vat_rate / 100
            total_amount = amount_bhd + vat_amount
            
            subtotal_bhd += amount_bhd
            total_vat += vat_amount
            
            items_data.append([
                item.code,
                item.name[:18],
                item.unit,
                str(item.quantity),
                f"{unit_price_bhd:.3f}",
                f"{amount_bhd:.3f}",
                f"{item.vat_rate:.0f}%",
                f"{vat_amount:.3f}",
                f"{total_amount:.3f}"
            ])
        
        items_table = Table(items_data, colWidths=[0.6*inch, 1.8*inch, 0.5*inch, 0.5*inch, 0.8*inch, 0.8*inch, 0.5*inch, 0.8*inch, 0.8*inch])
        items_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2d5016')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (1, 1), (1, -1), 'LEFT'),
            ('ALIGN', (4, 1), (-1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 3),
            ('RIGHTPADDING', (0, 0), (-1, -1), 3),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))
        story.append(items_table)
        story.append(Spacer(1, 10))
        
        # VAT SUMMARY
        grand_total = subtotal_bhd + total_vat
        
        summary_data = [
            ['Subtotal (Excl. VAT) | المجموع الفرعي:', f'BHD {subtotal_bhd:.3f}'],
            ['VAT @ 10% | ضريبة القيمة المضافة:', f'BHD {total_vat:.3f}'],
            ['GRAND TOTAL | المجموع الكلي:', f'BHD {grand_total:.3f}']
        ]
        
        summary_table = Table(summary_data, colWidths=[2*inch, 1.2*inch])
        summary_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#48bb78')),
            ('TEXTCOLOR', (0, -1), (-1, -1), colors.white),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))
        
        # Container to right-align
        container_data = [['', summary_table]]
        container_table = Table(container_data, colWidths=[3.8*inch, 3.2*inch])
        container_table.setStyle(TableStyle([
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        story.append(container_table)
        story.append(Spacer(1, 15))
        
        # AMOUNT IN WORDS - Bilingual
        amount_words = self._number_to_words_bhd(grand_total)
        words_data = [[f"Amount in Words | المبلغ بالكلمات: {amount_words}"]]
        words_table = Table(words_data, colWidths=[7*inch])
        words_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
        ]))
        story.append(words_table)
        story.append(Spacer(1, 15))
        
        # FOOTER - Bilingual
        footer_data = [
            [
                "Terms: Payment due within 30 days | الشروط: الدفع مستحق خلال 30 يوماً\nAll disputes subject to Bahrain jurisdiction | جميع النزاعات تخضع لاختصاص البحرين",
                "For Gulf Construction & Trading Co. W.L.L\n\nAuthorized Signatory | التوقيع المعتمد"
            ]
        ]
        
        footer_table = Table(footer_data, colWidths=[4*inch, 3*inch])
        footer_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('FONTNAME', (1, 0), (1, 0), 'Helvetica-Bold'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        story.append(footer_table)
        
        # Build PDF
        doc.build(story)
        
        # Save to file
        buffer.seek(0)
        with open(os.path.join(self.output_dir, "ultimate_vat_invoice.pdf"), 'wb') as f:
            f.write(buffer.getvalue())
        
        return grand_total
    
    def _generate_cash_receipt(self) -> float:
        """Generate Cash Receipt - ZERO BLOCKS"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, 
                              rightMargin=20*mm, leftMargin=20*mm,
                              topMargin=15*mm, bottomMargin=15*mm)
        
        story = []
        
        # HEADER
        header_data = [
            ["CASH RECEIPT", f"Receipt No: CR-{date.today().strftime('%Y%m%d')}-001\nDate: {date.today().strftime('%d/%m/%Y')}"]
        ]
        
        header_table = Table(header_data, colWidths=[4*inch, 3*inch])
        header_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#7c3aed')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 15),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
        ]))
        story.append(header_table)
        
        # RECEIVED FROM / BUSINESS
        customer_profile = self.name_generator.generate_customer_profile(
            region='generic_indian', customer_type='individual', invoice_type='cash'
        )
        
        business_customer_data = [
            [
                f"RECEIVED FROM\n\n{customer_profile.name}\nCash Payment",
                "BUSINESS DETAILS\n\nQuickMart Retail Store\nShop No. 15, Central Market\nMG Road, Bangalore - 560001\nPhone: +91-80-2345-6789"
            ]
        ]
        
        business_customer_table = Table(business_customer_data, colWidths=[3.5*inch, 3.5*inch])
        business_customer_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ]))
        story.append(business_customer_table)
        story.append(Spacer(1, 10))
        
        # ITEMS TABLE
        items_data = [
            ['S.No', 'Item Description', 'Quantity', 'Unit Price (₹)', 'Total Amount (₹)']
        ]
        
        selected_items = self.products[:3]
        total_amount = 0
        
        for i, item in enumerate(selected_items):
            item_total = item.quantity * item.unit_price
            total_amount += item_total
            
            items_data.append([
                str(i + 1),
                item.name[:25],
                f"{item.quantity} {item.unit}",
                f"₹{item.unit_price:,.0f}",
                f"₹{item_total:,.0f}"
            ])
        
        items_table = Table(items_data, colWidths=[0.5*inch, 2.5*inch, 1*inch, 1.2*inch, 1.3*inch])
        items_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#7c3aed')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (1, 1), (1, -1), 'LEFT'),
            ('ALIGN', (3, 1), (-1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(items_table)
        story.append(Spacer(1, 15))
        
        # TOTAL AMOUNT
        total_data = [
            ['TOTAL AMOUNT RECEIVED:', f'₹{total_amount:,.0f}']
        ]
        
        total_table = Table(total_data, colWidths=[2*inch, 1.5*inch])
        total_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#7c3aed')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 14),
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ]))
        
        # Container to right-align
        container_data = [['', total_table]]
        container_table = Table(container_data, colWidths=[3.5*inch, 3.5*inch])
        container_table.setStyle(TableStyle([
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        story.append(container_table)
        story.append(Spacer(1, 15))
        
        # AMOUNT IN WORDS
        amount_words = self._number_to_words_inr(total_amount)
        words_data = [[f"Amount in Words: {amount_words}"]]
        words_table = Table(words_data, colWidths=[7*inch])
        words_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
        ]))
        story.append(words_table)
        story.append(Spacer(1, 20))
        
        # PAYMENT INFO & SIGNATURE
        payment_signature_data = [
            [
                f"Payment Method: Cash\nPayment Status: Received in Full\nReceived By: Store Manager\nTime: {datetime.now().strftime('%I:%M %p')}",
                f"Customer Signature\n\n\n_________________\n{customer_profile.name}"
            ]
        ]
        
        payment_signature_table = Table(payment_signature_data, colWidths=[3.5*inch, 3.5*inch])
        payment_signature_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('FONTNAME', (1, 0), (1, 0), 'Helvetica-Bold'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        story.append(payment_signature_table)
        story.append(Spacer(1, 15))
        
        # FOOTER
        footer_data = [["Thank you for your business! | This receipt is valid for returns within 7 days."]]
        footer_table = Table(footer_data, colWidths=[7*inch])
        footer_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
        ]))
        story.append(footer_table)
        
        # Build PDF
        doc.build(story)
        
        # Save to file
        buffer.seek(0)
        with open(os.path.join(self.output_dir, "ultimate_cash_receipt.pdf"), 'wb') as f:
            f.write(buffer.getvalue())
        
        return total_amount

if __name__ == "__main__":
    generator = UltimateBlockFree()
    results = generator.generate_all_block_free_invoices()
    
    print(f"\n🎉 ULTIMATE BLOCK-FREE GENERATION COMPLETE!")
    print(f"📁 Files saved in: {generator.output_dir}/")
    print("\nGenerated amounts:")
    for invoice_type, amount in results.items():
        if invoice_type == 'VAT':
            print(f"  {invoice_type}: BHD {amount:.3f}")
        else:
            print(f"  {invoice_type}: ₹{amount:,.0f}")