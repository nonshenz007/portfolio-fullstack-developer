import random
from datetime import datetime, timedelta
from typing import List, Dict, Any
from app.models import Invoice

class InvoiceSimulator:
    """
    Simplified invoice generator for LedgerFlow.
    """
    def __init__(self):
        self.generated_hashes = set()

    def simulate(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate mock invoices based on parameters"""
        invoices = []
        count = params.get('invoice_count', 1)
        invoice_type = params.get('invoice_type', 'gst')
        
        # Get date range
        start_date = params.get('start_date')
        end_date = params.get('end_date')
        
        # Provide defaults if None
        if start_date is None:
            start_date = datetime.now() - timedelta(days=30)
        if end_date is None:
            end_date = datetime.now()
        
        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
        if isinstance(end_date, str):
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
            
        for i in range(count):
            # Create random date in range
            random_days = random.randint(0, (end_date - start_date).days)
            invoice_date = start_date + timedelta(days=random_days)
            
            # Create mock customer name
            random_names = ["John Doe", "Ravi Kumar", "Sumith Enterprises", "Global Traders", "Tech Solutions"]
            customer_name = random.choice(random_names)
            
            # Create mock customer profile
            customer_profile = {
                'name': customer_name,
                'address': "123 Main Street, Mumbai",
                'phone': "9876543210",
                'email': "customer@example.com",
                'gst_number': "27AAAAA0000A1Z5",
                'vat_number': "VAT123456789"
            }
            
            # Generate unique invoice number using timestamp and random suffix
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            random_suffix = f"{random.randint(1000, 9999)}"
            invoice_number = f"INV-{timestamp}-{random_suffix}"
            
            # Create mock invoice
            invoice = {
                'invoice_number': invoice_number,
                'invoice_date': invoice_date.strftime('%Y-%m-%d'),
                'customer_name': customer_name,
                'customer_profile': customer_profile,
                'items': [],  # Will be filled by the route handler
                'subtotal': 0,  # Will be calculated by the route handler
                'tax': 0,      # Will be calculated by the route handler
                'total': 0     # Will be calculated by the route handler
            }
            
            invoices.append(invoice)
            
        return invoices