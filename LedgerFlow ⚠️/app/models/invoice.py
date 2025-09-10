from .base import db, BaseModel
from datetime import datetime
import random
import string
import string
from decimal import Decimal, ROUND_HALF_UP
from sqlalchemy import Enum as SQLAEnum
from .template_type import TemplateType

def money(x):
    """Helper function to convert to Decimal and round to 2 decimal places"""
    if isinstance(x, Decimal):
        return x.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    return Decimal(str(x)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

class Invoice(BaseModel):
    """Invoice model for storing generated and manual invoices"""
    __tablename__ = 'invoices'
    
    # Invoice Information
    invoice_number = db.Column(db.String(50), unique=True, nullable=False)
    invoice_type = db.Column(db.String(20), nullable=False)  # cash, gst, vat
    # New field for template type
    template_type = db.Column(SQLAEnum(TemplateType, native_enum=False), 
                             default=TemplateType.GST_EINVOICE,
                             nullable=False)
    invoice_date = db.Column(db.DateTime, default=datetime.utcnow)
    due_date = db.Column(db.DateTime)
    
    # Customer Information
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'))
    customer = db.relationship('Customer', back_populates='invoices')
    
    # Quick customer info (for cash invoices)
    customer_name = db.Column(db.String(200))
    customer_address = db.Column(db.Text)
    customer_phone = db.Column(db.String(20))
    customer_tax_number = db.Column(db.String(50))
    
    # Amounts - stored as Float in DB but handled as Decimal in code
    subtotal = db.Column(db.Float, default=0)
    discount_amount = db.Column(db.Float, default=0)
    tax_amount = db.Column(db.Float, default=0)
    total_amount = db.Column(db.Float, default=0)
    
    # Tax Breakdown (for GST)
    cgst_amount = db.Column(db.Float, default=0)
    sgst_amount = db.Column(db.Float, default=0)
    igst_amount = db.Column(db.Float, default=0)
    
    # Payment Information
    payment_status = db.Column(db.String(20), default='pending')  # pending, partial, paid
    payment_method = db.Column(db.String(50))  # cash, card, bank_transfer, upi
    payment_date = db.Column(db.DateTime)
    
    # Additional Information
    notes = db.Column(db.Text)
    terms_conditions = db.Column(db.Text)
    reference_number = db.Column(db.String(50))  # PO number, etc.
    
    # Metadata
    is_manual = db.Column(db.Boolean, default=False)  # True if created manually
    generation_batch_id = db.Column(db.String(50))  # For bulk generation tracking
    realism_score = db.Column(db.Float)  # 0-100 score
    hash_signature = db.Column(db.String(64))  # SHA-256 hash
    verichain_hash = db.Column(db.String(64))  # VeriChain blockchain hash
    
    # New fields for system hardening (FR-1, FR-7, FR-9)
    tenant_id = db.Column(db.String(50), nullable=False, default='default')  # Multi-tenant support
    trace_id = db.Column(db.String(64), index=True)  # Request correlation
    generation_metadata = db.Column(db.JSON)  # Generation context for debugging
    retry_count = db.Column(db.Integer, default=0)  # Number of retry attempts
    last_error = db.Column(db.Text)  # Last error message
    
    # Business Info
    business_name = db.Column(db.String(200))
    business_address = db.Column(db.Text)
    business_tax_number = db.Column(db.String(50))
    business_logo_path = db.Column(db.String(200))
    
    # Relationships
    items = db.relationship('InvoiceItem', back_populates='invoice', cascade='all, delete-orphan')
    
    # Table constraints for system hardening
    __table_args__ = (
        # Composite unique constraint for multi-tenant support (FR-7)
        db.UniqueConstraint('invoice_number', 'tenant_id', name='uq_invoice_number_tenant'),
        # Indexes for performance
        db.Index('idx_invoice_trace_id', 'trace_id'),
        db.Index('idx_invoice_batch_id', 'generation_batch_id'),
        db.Index('idx_invoice_tenant_id', 'tenant_id'),
    )
    
    def __repr__(self):
        return f'<Invoice {self.invoice_number}>'
    
    def to_dict(self):
        """Convert invoice to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'invoice_number': self.invoice_number,
            'invoice_type': self.invoice_type,
            'template_type': self.template_type.value if self.template_type else TemplateType.GST_EINVOICE.value,
            'invoice_date': self.invoice_date.isoformat() if self.invoice_date else None,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'customer_name': self.customer_name,
            'customer_address': self.customer_address,
            'customer_phone': self.customer_phone,
            'customer_tax_number': self.customer_tax_number,
            'subtotal': str(money(self.subtotal or 0)),
            'discount_amount': str(money(self.discount_amount or 0)),
            'tax_amount': str(money(self.tax_amount or 0)),
            'total_amount': str(money(self.total_amount or 0)),
            'cgst_amount': str(money(self.cgst_amount or 0)),
            'sgst_amount': str(money(self.sgst_amount or 0)),
            'igst_amount': str(money(self.igst_amount or 0)),
            'payment_status': self.payment_status,
            'payment_method': self.payment_method,
            'payment_date': self.payment_date.isoformat() if self.payment_date else None,
            'notes': self.notes,
            'terms_conditions': self.terms_conditions,
            'reference_number': self.reference_number,
            'is_manual': self.is_manual,
            'generation_batch_id': self.generation_batch_id,
            'realism_score': str(money(self.realism_score or 0)),
            'hash_signature': self.hash_signature,
            'verichain_hash': self.verichain_hash,
            'business_name': self.business_name,
            'business_address': self.business_address,
            'business_tax_number': self.business_tax_number,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'items': [item.to_dict() for item in self.items] if self.items else []
        }
    
    @classmethod
    def generate_invoice_number(cls, invoice_type='INV', prefix='', tenant_id='default'):
        """
        Generate unique invoice number using atomic counter service
        
        DEPRECATED: Use AtomicCounterService.get_next_invoice_number() instead
        This method is kept for backward compatibility
        """
        from app.services.counter.atomic_counter_service import AtomicCounterService
        
        counter_service = AtomicCounterService()
        
        # Use prefix if provided, otherwise use invoice_type
        counter_type = prefix if prefix else invoice_type
        
        try:
            return counter_service.get_next_invoice_number(counter_type, tenant_id)
        except Exception as e:
            # Fallback to old method for backward compatibility
            import time
            timestamp = datetime.now().strftime('%Y%m%d')
            
            # Generate 4-digit random number for uniqueness
            random_suffix = ''.join(random.choices(string.digits, k=4))
            
            # Check for uniqueness and retry if needed
            attempt = 0
            while attempt < 100:  # Maximum 100 attempts to find unique number
                if prefix:
                    invoice_number = f"{prefix}-{timestamp}-{random_suffix}"
                else:
                    invoice_number = f"INV-{timestamp}-{random_suffix}"
                
                # Check if this number already exists for this tenant
                existing = cls.query.filter_by(
                    invoice_number=invoice_number, 
                    tenant_id=tenant_id
                ).first()
                if not existing:
                    return invoice_number
                
                # Generate new random suffix and try again
                random_suffix = ''.join(random.choices(string.digits, k=4))
                attempt += 1
            
            # Fallback if we couldn't find unique number (very unlikely)
            microseconds = int(time.time() * 1000) % 10000  # Get last 4 digits of milliseconds
            if prefix:
                return f"{prefix}-{timestamp}-{microseconds:04d}"
            else:
                return f"INV-{timestamp}-{microseconds:04d}"
    
    def calculate_totals(self):
        """Calculate invoice totals from items"""
        subtotal_decimal = sum(money(item.total_amount) for item in self.items)
        self.subtotal = float(subtotal_decimal)
        
        if self.invoice_type == 'gst':
            cgst_decimal = sum(money(item.cgst_amount) for item in self.items)
            sgst_decimal = sum(money(item.sgst_amount) for item in self.items)
            igst_decimal = sum(money(item.igst_amount) for item in self.items)
            
            self.cgst_amount = float(cgst_decimal)
            self.sgst_amount = float(sgst_decimal)
            self.igst_amount = float(igst_decimal)
            
            tax_decimal = cgst_decimal + sgst_decimal + igst_decimal
            self.tax_amount = float(tax_decimal)
        elif self.invoice_type == 'vat':
            tax_decimal = sum(money(item.vat_amount) for item in self.items)
            self.tax_amount = float(tax_decimal)
        else:
            tax_decimal = Decimal('0.00')
            self.tax_amount = 0
        
        discount_decimal = money(self.discount_amount or 0)
        total_decimal = subtotal_decimal + tax_decimal - discount_decimal
        self.total_amount = float(total_decimal)
        
        # Generate hash signature
        self.hash_signature = self.generate_hash()
    
    def calculate_realism_score(self):
        """Calculate how realistic this invoice appears"""
        score = 100.0
        
        # Check item count (too many or too few items reduce score)
        item_count = len(self.items)
        if item_count < 1 or item_count > 50:
            score -= 20
        elif item_count > 30:
            score -= 10
        
        # Check for duplicate items (slight reduction)
        unique_items = len(set(item.product_id for item in self.items))
        if unique_items < item_count:
            score -= 5
        
        # Check total amount range
        if self.total_amount < 10 or self.total_amount > 10000000:
            score -= 15
        
        # Check tax consistency
        if self.invoice_type in ['gst', 'vat'] and self.tax_amount == 0:
            score -= 25
        
        # Check customer information completeness
        if not self.customer_id and not self.customer_name:
            score -= 10
        
        # Check date validity
        if self.invoice_date > datetime.now():
            score -= 30
        
        # Bonus for payment method variety
        common_methods = ['cash', 'bank_transfer', 'card', 'upi']
        if self.payment_method in common_methods:
            score += 5
        
        self.realism_score = max(0, min(100, score))
        return self.realism_score


class InvoiceItem(BaseModel):
    """Invoice line items"""
    __tablename__ = 'invoice_items'
    
    # Relationships
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoices.id'), nullable=False)
    invoice = db.relationship('Invoice', back_populates='items')
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    product = db.relationship('Product')
    
    # Item Details
    item_name = db.Column(db.String(200), nullable=False)
    item_code = db.Column(db.String(50))
    hsn_sac_code = db.Column(db.String(20))  # For GST
    
    # Quantity and Price
    quantity = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(20), default='Nos')
    unit_price = db.Column(db.Float, nullable=False)
    
    # Amounts
    gross_amount = db.Column(db.Float)
    discount_percentage = db.Column(db.Float, default=0)
    discount_amount = db.Column(db.Float, default=0)
    net_amount = db.Column(db.Float)
    
    # Tax Information
    tax_rate = db.Column(db.Float, default=0)
    cgst_rate = db.Column(db.Float, default=0)
    sgst_rate = db.Column(db.Float, default=0)
    igst_rate = db.Column(db.Float, default=0)
    vat_rate = db.Column(db.Float, default=0)
    
    # Tax Amounts
    cgst_amount = db.Column(db.Float, default=0)
    sgst_amount = db.Column(db.Float, default=0)
    igst_amount = db.Column(db.Float, default=0)
    vat_amount = db.Column(db.Float, default=0)
    
    # Total
    total_amount = db.Column(db.Float, nullable=False)
    
    # Metadata
    notes = db.Column(db.Text)
    
    def calculate_amounts(self, invoice_type='cash', is_interstate=False):
        """Calculate all amounts for this item"""
        # Basic calculations using Decimal
        quantity_decimal = Decimal(str(self.quantity))
        unit_price_decimal = Decimal(str(self.unit_price))
        
        gross_decimal = money(quantity_decimal * unit_price_decimal)
        self.gross_amount = float(gross_decimal)
        
        discount_pct = Decimal(str(self.discount_percentage or 0))
        discount_decimal = money(gross_decimal * discount_pct / Decimal('100'))
        self.discount_amount = float(discount_decimal)
        
        net_decimal = money(gross_decimal - discount_decimal)
        self.net_amount = float(net_decimal)
        
        # Tax calculations based on invoice type
        if invoice_type == 'gst' and self.product:
            tax_rate = Decimal(str(self.product.gst_rate or 0))  # Handle None values
            
            if is_interstate:
                # IGST for interstate
                self.igst_rate = float(tax_rate)
                igst_decimal = money(net_decimal * tax_rate / Decimal('100'))
                self.igst_amount = float(igst_decimal)
                self.cgst_rate = self.sgst_rate = 0
                self.cgst_amount = self.sgst_amount = 0
                total_tax_decimal = igst_decimal
            else:
                # CGST + SGST for intrastate
                cgst_rate_decimal = sgst_rate_decimal = tax_rate / Decimal('2')
                self.cgst_rate = self.sgst_rate = float(cgst_rate_decimal)
                
                cgst_decimal = money(net_decimal * cgst_rate_decimal / Decimal('100'))
                sgst_decimal = money(net_decimal * sgst_rate_decimal / Decimal('100'))
                
                self.cgst_amount = float(cgst_decimal)
                self.sgst_amount = float(sgst_decimal)
                self.igst_rate = 0
                self.igst_amount = 0
                
                total_tax_decimal = cgst_decimal + sgst_decimal
            
        elif invoice_type == 'vat' and self.product:
            vat_rate_decimal = Decimal(str(self.product.vat_rate or 0))
            self.vat_rate = float(vat_rate_decimal)
            vat_decimal = money(net_decimal * vat_rate_decimal / Decimal('100'))
            self.vat_amount = float(vat_decimal)
            total_tax_decimal = vat_decimal
            
        else:  # Cash invoice
            total_tax_decimal = Decimal('0.00')
        
        total_decimal = money(net_decimal + total_tax_decimal)
        self.total_amount = float(total_decimal)
        
    def to_dict(self):
        """Convert invoice item to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'invoice_id': self.invoice_id,
            'product_id': self.product_id,
            'item_name': self.item_name,
            'item_code': self.item_code,
            'hsn_sac_code': self.hsn_sac_code,
            'quantity': str(money(self.quantity)),
            'unit': self.unit,
            'unit_price': str(money(self.unit_price)),
            'gross_amount': str(money(self.gross_amount or 0)),
            'discount_percentage': str(money(self.discount_percentage or 0)),
            'discount_amount': str(money(self.discount_amount or 0)),
            'net_amount': str(money(self.net_amount or 0)),
            'tax_rate': str(money(self.tax_rate or 0)),
            'cgst_rate': str(money(self.cgst_rate or 0)),
            'sgst_rate': str(money(self.sgst_rate or 0)),
            'igst_rate': str(money(self.igst_rate or 0)),
            'vat_rate': str(money(self.vat_rate or 0)),
            'cgst_amount': str(money(self.cgst_amount or 0)),
            'sgst_amount': str(money(self.sgst_amount or 0)),
            'igst_amount': str(money(self.igst_amount or 0)),
            'vat_amount': str(money(self.vat_amount or 0)),
            'total_amount': str(money(self.total_amount)),
            'notes': self.notes
        } 