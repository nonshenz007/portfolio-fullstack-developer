import random
import numpy as np
from datetime import datetime, timedelta
import time
import secrets
from app.models import Product, Invoice, InvoiceItem, Customer, Settings
from app.models.base import db
from config import Config

class InvoiceGenerator:
    """Core engine for generating realistic invoices"""
    
    def __init__(self):
        self.generation_batch_id = secrets.token_urlsafe(8)
        self.customers = []
        self.products = []
        
    def generate_batch(self, count=100, date_range_days=30, invoice_type='gst', 
                      business_style='retail_shop', reality_buffer=85, 
                      believability_stress=15, deviation_control=None,
                      smart_entropy=True, customer_web_density=0.7):
        """Generate a batch of invoices with realistic parameters"""
        
        start_time = time.time()
        
        # Load products
        self.products = Product.query.filter_by(is_active=True).all()
        if not self.products:
            return {
                'success': False,
                'error': 'No products available. Please import products first.'
            }
        
        # Initialize parameters
        self.reality_buffer = reality_buffer / 100  # Convert to 0-1 scale
        self.believability_stress = believability_stress / 100
        self.deviation_control = deviation_control or {}
        self.smart_entropy = smart_entropy
        self.customer_web_density = customer_web_density
        self.business_style = business_style
        
        # Generate or load customers
        self._prepare_customer_base(count, invoice_type)
        
        # Generate date distribution
        dates = self._generate_date_distribution(count, date_range_days)
        
        # Generate invoices
        invoices = []
        for i in range(count):
            try:
                invoice = self._generate_invoice(
                    invoice_date=dates[i],
                    invoice_type=invoice_type
                )
                invoices.append(invoice)
                db.session.add(invoice)
                
                # Commit in batches for performance
                if (i + 1) % 50 == 0:
                    db.session.commit()
                    
            except Exception as e:
                print(f"Error generating invoice {i+1}: {str(e)}")
                continue
        
        # Final commit
        db.session.commit()
        
        execution_time = time.time() - start_time
        
        return {
            'success': True,
            'generated_count': len(invoices),
            'generation_batch_id': self.generation_batch_id,
            'execution_time': round(execution_time, 2),
            'avg_realism_score': np.mean([inv.realism_score for inv in invoices if inv.realism_score])
        }
    
    def generate_single(self, invoice_type='gst', business_style='retail_shop', **kwargs):
        """Generate a single invoice for preview"""
        self.products = Product.query.filter_by(is_active=True).all()
        if not self.products:
            raise ValueError('No products available')
        
        self.business_style = business_style
        self.reality_buffer = kwargs.get('reality_buffer', 85) / 100
        self.believability_stress = kwargs.get('believability_stress', 15) / 100
        self.smart_entropy = kwargs.get('smart_entropy', True)
        
        # Generate a random customer
        customer = Customer.generate_random(
            customer_type='business' if random.random() > 0.3 else 'individual',
            country='India' if invoice_type == 'gst' else 'Bahrain'
        )
        
        return self._generate_invoice(
            invoice_date=datetime.now(),
            invoice_type=invoice_type,
            customer=customer
        )
    
    def _prepare_customer_base(self, invoice_count, invoice_type):
        """Prepare realistic customer distribution"""
        # Calculate customer count based on web density
        unique_customers = int(invoice_count * (1 - self.customer_web_density))
        unique_customers = max(1, unique_customers)
        
        # Load existing customers
        country = 'India' if invoice_type == 'gst' else 'Bahrain'
        existing_customers = Customer.query.filter_by(country=country).limit(unique_customers // 2).all()
        
        # Generate new customers
        new_customer_count = unique_customers - len(existing_customers)
        for _ in range(new_customer_count):
            customer_type = 'business' if random.random() > 0.3 else 'individual'
            customer = Customer.generate_random(customer_type, country)
            db.session.add(customer)
            self.customers.append(customer)
        
        self.customers.extend(existing_customers)
        db.session.commit()
    
    def _generate_date_distribution(self, count, date_range_days):
        """Generate realistic date distribution"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=date_range_days)
        
        dates = []
        
        if self.reality_buffer > 0.7:
            # Realistic distribution - more recent dates
            for _ in range(count):
                # Exponential distribution favoring recent dates
                days_ago = np.random.exponential(scale=date_range_days/3)
                days_ago = min(days_ago, date_range_days)
                date = end_date - timedelta(days=days_ago)
                
                # Add business hours variation
                hour = np.random.normal(14, 3)  # Peak around 2 PM
                hour = max(9, min(20, int(hour)))  # Business hours 9-8
                minute = random.randint(0, 59)
                
                date = date.replace(hour=hour, minute=minute)
                dates.append(date)
        else:
            # Random distribution
            for _ in range(count):
                random_days = random.uniform(0, date_range_days)
                date = end_date - timedelta(days=random_days)
                dates.append(date)
        
        # Sort chronologically
        dates.sort()
        return dates
    
    def _generate_invoice(self, invoice_date, invoice_type, customer=None):
        """Generate a single invoice"""
        # Select customer
        if not customer:
            if self.customers and random.random() < self.customer_web_density:
                # Return customer
                customer = self._select_return_customer(invoice_date)
            else:
                # New customer
                customer = Customer.generate_random(
                    customer_type='business' if random.random() > 0.3 else 'individual',
                    country='India' if invoice_type == 'gst' else 'Bahrain'
                )
                db.session.add(customer)
        
        # Create invoice
        invoice = Invoice(
            invoice_number=Invoice.generate_invoice_number(invoice_type.upper()),
            invoice_type=invoice_type,
            invoice_date=invoice_date,
            customer=customer,
            customer_name=customer.company_name or customer.name,
            customer_address=f"{customer.address_line1}, {customer.city}, {customer.state}",
            customer_phone=customer.mobile or customer.phone,
            customer_tax_number=customer.gst_number if invoice_type == 'gst' else customer.vat_number,
            generation_batch_id=self.generation_batch_id,
            business_name=Settings.get_value('business_name'),
            business_address=Settings.get_value('business_address'),
            business_tax_number=Settings.get_value('business_gst') if invoice_type == 'gst' else Settings.get_value('business_vat')
        )
        
        # Set payment details
        invoice.payment_method = self._select_payment_method()
        invoice.payment_status = 'paid' if random.random() > 0.1 else 'pending'
        
        if invoice.payment_status == 'paid':
            # Payment within a few days
            days_to_payment = np.random.exponential(scale=2)
            invoice.payment_date = invoice_date + timedelta(days=min(days_to_payment, 30))
        
        # Generate invoice items
        items = self._generate_invoice_items(invoice, customer)
        invoice.items.extend(items)
        
        # Calculate totals
        invoice.calculate_totals()
        
        # Calculate realism score
        invoice.calculate_realism_score()
        
        # Update customer data
        customer.last_purchase_date = invoice_date
        customer.total_purchases += invoice.total_amount
        
        return invoice
    
    def _select_return_customer(self, invoice_date):
        """Select a return customer based on purchase probability"""
        weights = []
        
        for customer in self.customers:
            if customer.last_purchase_date:
                days_since = (invoice_date - customer.last_purchase_date).days
            else:
                days_since = 30
            
            probability = customer.get_purchase_probability(days_since)
            weights.append(probability)
        
        if sum(weights) == 0:
            return random.choice(self.customers)
        
        return random.choices(self.customers, weights=weights)[0]
    
    def _select_payment_method(self):
        """Select payment method based on business style"""
        methods = {
            'retail_shop': ['cash', 'card', 'upi'],
            'distributor': ['bank_transfer', 'cheque', 'cash'],
            'exporter': ['bank_transfer', 'letter_of_credit'],
            'pharmacy': ['cash', 'card', 'upi'],
            'it_service': ['bank_transfer', 'online_payment']
        }
        
        weights = {
            'retail_shop': [0.5, 0.3, 0.2],
            'distributor': [0.6, 0.3, 0.1],
            'exporter': [0.8, 0.2],
            'pharmacy': [0.6, 0.3, 0.1],
            'it_service': [0.7, 0.3]
        }
        
        style_methods = methods.get(self.business_style, ['cash', 'bank_transfer'])
        style_weights = weights.get(self.business_style, [0.5, 0.5])
        
        return random.choices(style_methods, weights=style_weights)[0]
    
    def _generate_invoice_items(self, invoice, customer):
        """Generate realistic invoice items"""
        # Determine item count
        style_config = Config.BUSINESS_STYLES.get(self.business_style, {})
        avg_items = style_config.get('avg_items_per_invoice', 5)
        
        # Add variation
        if self.smart_entropy:
            # Sometimes generate outliers
            if random.random() < self.believability_stress:
                item_count = random.choice([1, avg_items * 3])
            else:
                item_count = int(np.random.normal(avg_items, avg_items * 0.3))
        else:
            item_count = int(np.random.normal(avg_items, avg_items * 0.2))
        
        item_count = max(1, min(50, item_count))
        
        # Select products
        selected_products = self._select_products(item_count, customer)
        
        items = []
        is_interstate = self._is_interstate_transaction(invoice)
        
        for product in selected_products:
            # Generate quantity
            quantity = product.get_realistic_quantity(
                self.business_style,
                randomness_factor=1 - self.reality_buffer
            )
            
            # Apply price variation
            price_variance = self.deviation_control.get('price_variance', 0.05)
            price_multiplier = np.random.normal(1, price_variance)
            unit_price = product.sale_price * max(0.9, min(1.1, price_multiplier))
            
            # Create item
            item = InvoiceItem(
                product=product,
                item_name=product.name,
                item_code=product.code,
                hsn_sac_code=product.hsn_code,
                quantity=quantity,
                unit=product.unit,
                unit_price=round(unit_price, 2)
            )
            
            # Apply random discount sometimes
            if random.random() < 0.2:  # 20% chance of discount
                item.discount_percentage = random.choice([5, 10, 15, 20])
            
            # Calculate amounts
            item.calculate_amounts(invoice.invoice_type, is_interstate)
            
            items.append(item)
        
        return items
    
    def _select_products(self, count, customer):
        """Select products based on popularity and customer preferences"""
        # Weight products by popularity
        weights = [p.popularity_score for p in self.products]
        
        # Adjust weights based on customer category
        if customer.customer_category == 'premium':
            # Premium customers buy expensive items
            for i, product in enumerate(self.products):
                if product.sale_price > 5000:
                    weights[i] *= 2
        
        # Select products
        selected = []
        
        if self.smart_entropy and random.random() < 0.1:
            # Sometimes select same product multiple times (bulk orders)
            product = random.choices(self.products, weights=weights)[0]
            selected = [product] * min(count, 3)
            # Fill remaining with other products
            if count > 3:
                remaining = random.choices(self.products, weights=weights, k=count-3)
                selected.extend(remaining)
        else:
            # Normal selection
            selected = random.choices(self.products, weights=weights, k=count)
        
        return selected
    
    def _is_interstate_transaction(self, invoice):
        """Determine if transaction is interstate (for GST)"""
        if invoice.invoice_type != 'gst':
            return False
        
        # Simple logic: 20% chance of interstate
        return random.random() < 0.2 