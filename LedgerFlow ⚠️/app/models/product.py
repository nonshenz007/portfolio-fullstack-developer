from .base import db, BaseModel

class Product(BaseModel):
    """Product model for storing imported product catalog"""
    __tablename__ = 'products'
    
    # Basic Information
    name = db.Column(db.String(200), nullable=False)
    code = db.Column(db.String(50), unique=True)
    category = db.Column(db.String(100))
    unit = db.Column(db.String(20), default='Nos')
    
    # Pricing
    mrp = db.Column(db.Float, nullable=False)
    sale_price = db.Column(db.Float, nullable=False)
    discount_percentage = db.Column(db.Float, default=0)
    
    # Tax Information
    gst_rate = db.Column(db.Float, default=18)  # Indian GST
    vat_rate = db.Column(db.Float, default=10)  # Bahrain VAT
    hsn_code = db.Column(db.String(20))  # HSN/SAC code for GST
    
    # Stock Information (for realism)
    stock_quantity = db.Column(db.Integer, default=1000)
    reorder_level = db.Column(db.Integer, default=100)
    
    # Metadata
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    import_batch_id = db.Column(db.String(50))  # Track which import batch
    
    # Statistical Data (for realistic generation)
    avg_quantity_sold = db.Column(db.Float, default=5)
    popularity_score = db.Column(db.Float, default=0.5)  # 0-1 scale
    seasonal_factor = db.Column(db.JSON)  # Monthly variation
    
    def __repr__(self):
        return f'<Product {self.name}>'
    
    def calculate_tax(self, quantity, tax_type='GST'):
        """Calculate tax amount based on type"""
        base_amount = self.sale_price * quantity
        
        if tax_type == 'GST':
            tax_rate = self.gst_rate / 100
            # GST is split equally between CGST and SGST
            cgst = base_amount * (tax_rate / 2)
            sgst = base_amount * (tax_rate / 2)
            return {
                'cgst': round(cgst, 2),
                'sgst': round(sgst, 2),
                'total_tax': round(cgst + sgst, 2)
            }
        elif tax_type == 'VAT':
            vat = base_amount * (self.vat_rate / 100)
            return {
                'vat': round(vat, 2),
                'total_tax': round(vat, 2)
            }
        else:  # Cash/Plain invoice
            return {'total_tax': 0}
    
    def get_realistic_quantity(self, business_style, randomness_factor=0.2):
        """Generate realistic quantity based on business style and product popularity"""
        import random
        import numpy as np
        
        base_qty = self.avg_quantity_sold
        
        # Apply business style multiplier
        style_multipliers = {
            'retail_shop': 1.0,
            'distributor': 5.0,
            'exporter': 10.0,
            'pharmacy': 2.0,
            'it_service': 0.5
        }
        
        multiplier = style_multipliers.get(business_style, 1.0)
        adjusted_qty = base_qty * multiplier * self.popularity_score
        
        # Add randomness
        variance = adjusted_qty * randomness_factor
        final_qty = np.random.normal(adjusted_qty, variance)
        
        # Ensure positive integer
        return max(1, int(round(final_qty)))
        
    def to_dict(self):
        """Convert product to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'category': self.category,
            'unit': self.unit,
            'mrp': float(self.mrp),
            'sale_price': float(self.sale_price),
            'discount_percentage': float(self.discount_percentage or 0),
            'gst_rate': float(self.gst_rate or 0),
            'vat_rate': float(self.vat_rate or 0),
            'hsn_code': self.hsn_code,
            'stock_quantity': int(self.stock_quantity or 0),
            'reorder_level': int(self.reorder_level or 0),
            'description': self.description,
            'is_active': self.is_active,
            'import_batch_id': self.import_batch_id,
            'avg_quantity_sold': float(self.avg_quantity_sold or 0),
            'popularity_score': float(self.popularity_score or 0),
            'seasonal_factor': self.seasonal_factor,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        } 