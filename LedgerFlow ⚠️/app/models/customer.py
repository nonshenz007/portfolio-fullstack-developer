from .base import db, BaseModel
import random
from faker import Faker

class Customer(BaseModel):
    """Customer model for generating realistic customer data"""
    __tablename__ = 'customers'
    
    # Basic Information
    name = db.Column(db.String(200), nullable=False)
    company_name = db.Column(db.String(200))
    customer_type = db.Column(db.String(50), default='individual')  # individual, business
    
    # Contact Information
    email = db.Column(db.String(150))
    phone = db.Column(db.String(20))
    mobile = db.Column(db.String(20))
    
    # Address
    address_line1 = db.Column(db.String(200))
    address_line2 = db.Column(db.String(200))
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))
    country = db.Column(db.String(100))
    postal_code = db.Column(db.String(20))
    
    # Tax Information
    gst_number = db.Column(db.String(20))  # For Indian GST
    vat_number = db.Column(db.String(20))  # For Bahrain VAT
    pan_number = db.Column(db.String(20))  # PAN for Indian customers
    
    # Business Information
    purchase_frequency = db.Column(db.Float, default=0.5)  # 0-1 scale
    avg_transaction_value = db.Column(db.Float, default=5000)
    customer_category = db.Column(db.String(50))  # premium, regular, occasional
    credit_limit = db.Column(db.Float, default=0)
    
    # Statistical Data
    total_purchases = db.Column(db.Float, default=0)
    last_purchase_date = db.Column(db.DateTime)
    loyalty_score = db.Column(db.Float, default=0.5)  # 0-1 scale
    
    # Metadata
    is_active = db.Column(db.Boolean, default=True)
    notes = db.Column(db.Text)
    
    # Relationships
    invoices = db.relationship('Invoice', back_populates='customer', lazy='dynamic')
    
    def __repr__(self):
        return f'<Customer {self.name}>'
    
    @classmethod
    def generate_random(cls, customer_type='individual', country='India'):
        """Generate random customer data for simulation"""
        fake = Faker('en_IN' if country == 'India' else 'en_US')
        
        customer = cls()
        
        if customer_type == 'business':
            customer.company_name = fake.company()
            customer.name = fake.name()
            customer.customer_type = 'business'
            customer.avg_transaction_value = random.uniform(10000, 100000)
            customer.purchase_frequency = random.uniform(0.6, 0.9)
        else:
            customer.name = fake.name()
            customer.customer_type = 'individual'
            customer.avg_transaction_value = random.uniform(1000, 20000)
            customer.purchase_frequency = random.uniform(0.2, 0.6)
        
        # Contact details
        customer.email = fake.email()
        customer.phone = fake.phone_number()
        customer.mobile = fake.phone_number()
        
        # Address
        customer.address_line1 = fake.street_address()
        customer.city = fake.city()
        customer.state = fake.state() if country == 'India' else fake.state_abbr()
        customer.country = country
        customer.postal_code = fake.postcode()
        
        # Tax numbers
        if country == 'India':
            # Generate realistic GST number format
            state_codes = ['27', '29', '24', '07', '06', '04', '22', '33']
            customer.gst_number = f"{random.choice(state_codes)}{''.join([str(random.randint(0,9)) for _ in range(13)])}"
            customer.pan_number = f"{''.join([random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ') for _ in range(5)])}"
            customer.pan_number += f"{random.randint(1000, 9999)}"
            customer.pan_number += random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
        else:  # Bahrain
            customer.vat_number = f"BH{random.randint(100000000, 999999999)}"
        
        # Customer category
        categories = ['premium', 'regular', 'occasional']
        weights = [0.2, 0.5, 0.3]
        customer.customer_category = random.choices(categories, weights=weights)[0]
        
        # Loyalty score based on category
        loyalty_scores = {'premium': 0.8, 'regular': 0.5, 'occasional': 0.2}
        customer.loyalty_score = loyalty_scores[customer.customer_category] + random.uniform(-0.1, 0.1)
        
        return customer
    
    def get_purchase_probability(self, days_since_last_purchase=0):
        """Calculate probability of purchase based on customer behavior"""
        base_probability = self.purchase_frequency * self.loyalty_score
        
        # Reduce probability as days increase
        time_factor = max(0, 1 - (days_since_last_purchase / 90))
        
        # Category multiplier
        category_multipliers = {
            'premium': 1.5,
            'regular': 1.0,
            'occasional': 0.5
        }
        
        multiplier = category_multipliers.get(self.customer_category, 1.0)
        
        return min(1.0, base_probability * time_factor * multiplier) 