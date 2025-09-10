"""
LedgerFlow Simulation Engine
----------------------------
A production-grade invoice generation engine that creates realistic, 
statistically valid invoices based on configurable parameters.

This engine simulates invoices that match real-world business behavior
using the provided item catalog, invoice configuration, and invoice type.
"""

import random
import datetime
import math
import re
import uuid
from typing import List, Dict, Optional, Literal, Any
from dataclasses import dataclass
from datetime import date, datetime, timedelta
import argparse
import json
import sys


@dataclass
class SimulationConfig:
    revenue_target: float
    start_date: date
    end_date: date
    invoice_type: Literal['plain', 'gst', 'vat']
    min_items: int
    max_items: int
    min_invoice_amount: float
    max_invoice_amount: float
    item_filter_mode: Literal['all', 'selected']
    selected_items: List[str]
    name_type: Literal[
        'malabar_muslim', 'south_indian_generic', 
        'indian_company', 'bahrain_name', 'bahrain_company', 'it_company'
    ]
    realism_mode: Literal['random', 'pareto', 'equal']
    seed: Optional[int] = None
    invoice_count_mode: Optional[str] = 'auto'  # 'auto' or 'manual'
    manual_invoice_count: Optional[int] = None
    reality_buffer: Optional[float] = 0.0  # Percentage (0-50)
    distribution_mode: Optional[str] = 'even'  # 'even', 'weighted', 'burst'
    customer_repeat_rate: Optional[float] = 0.0  # Percentage (0-100)

# GST rates based on item categories
GST_RATES = {
    'Electronics': 18,
    'Furniture': 18,
    'Software': 18,
    'Services': 18,
    'Office Supplies': 12,
    'Stationery': 12,
    'Food': 5,
    'Books': 5,
    'Luxury': 28
}

# Default GST rate if category not found
DEFAULT_GST_RATE = 18

# VAT rate for Bahrain
BAHRAIN_VAT_RATE = 10

class InvoiceSimulator:
    """Main simulation engine that generates realistic invoices."""
    
    def __init__(self, config: SimulationConfig, catalog: List[Dict]):
        """
        Initialize the simulator with configuration and catalog.
        
        Args:
            config: Configuration parameters for the simulation
            catalog: List of items available for invoicing
        """
        self.config = config
        self.catalog = catalog
        
        # Set random seed for reproducibility if provided
        if config.seed is not None:
            random.seed(config.seed)
            
        # Filter catalog if needed
        if config.item_filter_mode == 'selected' and config.selected_items:
            self.catalog = [item for item in catalog 
                           if item['sku'] in config.selected_items or item['name'] in config.selected_items]
        
        # Generate customer pool based on name_type
        self.customers = self._generate_customer_pool()
        
        # Calculate simulation parameters
        self.date_range = (config.end_date - config.start_date).days + 1
        
        # Initialize invoice number counter
        self.invoice_counter = random.randint(1000, 9999)
        
    def simulate(self) -> List[Dict]:
        """
        Generate a list of realistic invoices based on configuration.
        
        Returns:
            List of invoice dictionaries
        """
        # Determine number of invoices based on mode
        if self.config.invoice_count_mode == 'manual' and self.config.manual_invoice_count:
            invoice_count = self.config.manual_invoice_count
        else:
            # Auto mode: determine based on revenue target and invoice amount bounds
            avg_invoice_amount = (self.config.min_invoice_amount + self.config.max_invoice_amount) / 2
            estimated_invoice_count = math.ceil(self.config.revenue_target / avg_invoice_amount)
            
            # Adjust for realism - don't create too many tiny invoices
            max_reasonable_count = self.date_range * 5  # Max 5 invoices per day on average
            invoice_count = min(estimated_invoice_count, max_reasonable_count)
        
        # Generate invoice dates based on distribution_mode
        invoice_dates = self._distribute_invoice_dates(invoice_count)
        
        # Generate customers for each invoice based on customer_repeat_rate
        invoice_customers = self._assign_customers_to_invoices(invoice_count)
        
        # Generate invoices
        invoices = []
        remaining_revenue = self.config.revenue_target
        
        for i in range(invoice_count):
            # For manual mode, distribute revenue evenly across invoices with reality buffer
            if self.config.invoice_count_mode == 'manual':
                base_amount = self.config.revenue_target / invoice_count
                
                # Apply reality buffer for variation
                reality_buffer = (self.config.reality_buffer or 0) / 100
                if reality_buffer > 0:
                    variation = 1 + random.uniform(-reality_buffer, reality_buffer)
                    target_amount = base_amount * variation
                    # Still respect min/max bounds
                    target_amount = max(min(target_amount, self.config.max_invoice_amount), 
                                      self.config.min_invoice_amount)
                else:
                    target_amount = base_amount
            else:
                # Auto mode: random amount within bounds
                target_amount = random.uniform(self.config.min_invoice_amount, self.config.max_invoice_amount)

            # Generate a single invoice
            invoice = self._generate_invoice(
                invoice_dates[i],
                invoice_customers[i],
                target_amount
            )
            invoices.append(invoice)

        # --- PATCH: Scale all invoice totals to match revenue target exactly in auto mode ---
        if self.config.invoice_count_mode == 'auto':
            total_generated = sum(inv['total'] for inv in invoices)
            if total_generated > 0:
                scale = self.config.revenue_target / total_generated
                for inv in invoices:
                    inv['subtotal'] = round(inv['subtotal'] * scale, 2)
                    inv['total'] = round(inv['total'] * scale, 2)
                    # Scale each item's amount and rate
                    for item in inv['items']:
                        item['amount'] = round(item['amount'] * scale, 2)
                        item['rate'] = round(item['rate'] * scale, 2)
        # --- END PATCH ---

        # After generating initial invoices, reconcile total revenue to match target within tolerance
        total_generated = sum(inv['total'] for inv in invoices)
        tolerance = 0.01  # Currency rounding tolerance
        diff = round(self.config.revenue_target - total_generated, 2)

        if abs(diff) > tolerance:
            # Try to adjust the last invoice if within bounds
            last_inv = invoices[-1]
            adj_successful = False

            if last_inv['invoice_type'] == 'Plain':
                new_total = last_inv['total'] + diff
                if self.config.min_invoice_amount <= new_total <= self.config.max_invoice_amount:
                    last_inv['subtotal'] = round(new_total, 2)
                    last_inv['total'] = round(new_total, 2)
                    adj_successful = True

            elif last_inv['invoice_type'] == 'GST':
                # subtotal + 18% = total -> subtotal = total / 1.18
                new_total = last_inv['total'] + diff
                new_subtotal = round(new_total / 1.18, 2)
                if self.config.min_invoice_amount <= new_total <= self.config.max_invoice_amount:
                    cgst = round(new_subtotal * 0.09, 2)
                    sgst = round(new_subtotal * 0.09, 2)
                    last_inv['subtotal'] = new_subtotal
                    last_inv['tax_breakup']['CGST'] = cgst
                    last_inv['tax_breakup']['SGST'] = sgst
                    last_inv['total'] = round(new_subtotal + cgst + sgst, 2)
                    adj_successful = True

            elif last_inv['invoice_type'] == 'VAT':
                new_total = last_inv['total'] + diff
                new_subtotal = round(new_total / 1.10, 2)
                if self.config.min_invoice_amount <= new_total <= self.config.max_invoice_amount:
                    vat_amt = round(new_subtotal * 0.10, 2)
                    last_inv['subtotal'] = new_subtotal
                    last_inv['VAT'] = vat_amt
                    last_inv['total'] = round(new_subtotal + vat_amt, 2)
                    adj_successful = True

            # If adjusting last invoice failed, create an adjustment invoice (Plain)
            if not adj_successful:
                adj_total = abs(diff)
                adj_total = max(self.config.min_invoice_amount, min(adj_total, self.config.max_invoice_amount))
                adj_subtotal = adj_total  # Plain invoice no tax
                adj_date = self.config.end_date
                self.invoice_counter += 1
                adj_invoice_id = f"ADJ/{adj_date.year}/{self.invoice_counter:05d}"
                invoices.append({
                    "invoice_type": "Plain",
                    "invoice_number": adj_invoice_id,
                    "date": adj_date.strftime("%Y-%m-%d"),
                    "customer": {"name": "Adjustment Entry"},
                    "items": [{
                        "item": "Adjustment",
                        "qty": 1,
                        "rate": adj_subtotal,
                        "amount": adj_subtotal
                    }],
                    "subtotal": adj_subtotal,
                    "total": adj_total,
                    "template_applied": "plain_template"
                })
        
        return invoices
    
    def _generate_invoice(self, invoice_date: datetime, customer_name: str, 
                         target_amount: Optional[float] = None) -> Dict:
        """
        Generate a single realistic invoice.
        
        Args:
            invoice_date: Date for the invoice
            customer_name: Name of the customer
            target_amount: Optional specific amount for this invoice to reach
            
        Returns:
            A complete invoice dictionary
        """
        # Generate a region-specific invoice number
        self.invoice_counter += 1
        if self.config.invoice_type == 'gst':
            # Format: GST/FY23-24/00001
            fy_year = invoice_date.year % 100
            next_fy = (fy_year + 1) % 100
            invoice_id = f"GST/FY{fy_year:02d}-{next_fy:02d}/{self.invoice_counter:05d}"
        elif self.config.invoice_type == 'vat':
            # Format: VAT-2024-00001
            invoice_id = f"VAT-{invoice_date.year}-{self.invoice_counter:05d}"
        else:
            # Format: INV/2024/00001
            invoice_id = f"INV/{invoice_date.year}/{self.invoice_counter:05d}"
        
        # Determine invoice target amount
        if target_amount is None:
            # Random amount within bounds
            invoice_amount = random.uniform(
                self.config.min_invoice_amount, 
                self.config.max_invoice_amount
            )
        else:
            # Use specific target amount but ensure it's within bounds
            invoice_amount = max(
                min(target_amount, self.config.max_invoice_amount),
                self.config.min_invoice_amount
            )
        
        # Determine number of items for this invoice
        item_count = random.randint(self.config.min_items, self.config.max_items)
        
        # Select random items from catalog (without duplicates)
        selected_items = random.sample(self.catalog, min(item_count, len(self.catalog)))
        
        # If we need more items than catalog has, allow repeats
        if item_count > len(self.catalog):
            additional_items = random.choices(
                self.catalog, 
                k=item_count - len(self.catalog)
            )
            selected_items.extend(additional_items)
        
        # Calculate item quantities and prices to reach target amount
        invoice_items = self._calculate_item_distribution(selected_items, invoice_amount)
        
        # Format invoice based on template type
        invoice = self._format_invoice_by_template(invoice_id, invoice_date, customer_name, invoice_items)
        
        return invoice
    
    def _format_invoice_by_template(self, invoice_id: str, invoice_date: datetime, 
                                   customer_name: str, items: List[Dict]) -> Dict:
        """
        Format the invoice according to the selected template type.
        
        Args:
            invoice_id: The invoice ID
            invoice_date: The invoice date
            customer_name: The customer name
            items: The invoice items
            
        Returns:
            A formatted invoice dictionary
        """
        invoice_type = self.config.invoice_type
        
        # Calculate subtotal
        subtotal = sum(item['amount'] for item in items)
        
        if invoice_type == 'plain':
            # Plain invoice - no tax
            return {
                "invoice_type": "Plain",
                "invoice_number": invoice_id,
                "date": invoice_date.strftime("%Y-%m-%d"),
                "customer": {"name": customer_name},
                "items": [
                    {
                        "name": item['name'],
                        "quantity": item['qty'],
                        "rate": item['rate'],
                        "amount": item['amount']
                    } for item in items
                ],
                "subtotal": round(subtotal, 2),
                "total": round(subtotal, 2),
                "payment_terms": "Net 30 days"
            }
            
        elif invoice_type == 'gst':
            # GST invoice - CGST/SGST split
            formatted_items = []
            total_tax = 0
            tax_breakup = {}
            
            for item in items:
                # Get GST rate based on item category
                category = item.get('category', 'default')
                gst_percent = GST_RATES.get(category, DEFAULT_GST_RATE)
                
                item_tax = (item['amount'] * gst_percent / 100)
                total_tax += item_tax
                
                # Track tax by rate for summary
                rate_key = f"{gst_percent}%"
                if rate_key not in tax_breakup:
                    tax_breakup[rate_key] = {"taxable": 0, "cgst": 0, "sgst": 0}
                
                tax_breakup[rate_key]["taxable"] += item['amount']
                tax_breakup[rate_key]["cgst"] += item_tax / 2
                tax_breakup[rate_key]["sgst"] += item_tax / 2
                
                formatted_items.append({
                    "name": item['name'],
                    "quantity": item['qty'],
                    "rate": item['rate'],
                    "amount": item['amount'],
                    "gst_rate": gst_percent,
                    "cgst": round(item_tax / 2, 2),
                    "sgst": round(item_tax / 2, 2)
                })
            
            # Round all tax values
            for rate in tax_breakup:
                tax_breakup[rate] = {k: round(v, 2) for k, v in tax_breakup[rate].items()}
            
            # Calculate overall CGST/SGST totals for the invoice
            total_cgst = round(total_tax / 2, 2)
            total_sgst = round(total_tax / 2, 2)
            
            return {
                "invoice_type": "GST",
                "invoice_number": invoice_id,
                "date": invoice_date.strftime("%Y-%m-%d"),
                "customer": {
                    "name": customer_name,
                    "gstin": f"27XXXXX0000X1Z{random.randint(0, 9)}"  # Sample GSTIN
                },
                "items": [
                    {
                        "item": item['name'],
                        "qty": item['qty'],
                        "rate": item['rate'],
                        "amount": item['amount'],
                        "gst_percent": item.get('gst_percent', DEFAULT_GST_RATE)
                    } for item in items
                ],
                "subtotal": round(subtotal, 2),
                "tax_breakup": {
                    "CGST": total_cgst,
                    "SGST": total_sgst,
                    "CGST_rate": 9,
                    "SGST_rate": 9
                },
                "total": round(subtotal + total_tax, 2),
                "template_applied": "gst_template",
                "gstin": f"27XXXXX0000X1Z{random.randint(0, 9)}"
            }
            
        elif invoice_type == 'vat':
            # VAT invoice - Bahrain format
            formatted_items = []
            total_vat = 0
            
            for item in items:
                item_vat = (item['amount'] * BAHRAIN_VAT_RATE / 100)
                total_vat += item_vat
                
                formatted_items.append({
                    "name": item['name'],
                    "quantity": item['qty'],
                    "rate": item['rate'],
                    "amount": item['amount'],
                    "vat_amount": round(item_vat, 2)
                })
            
            return {
                "invoice_type": "VAT",
                "invoice_number": invoice_id,
                "date": invoice_date.strftime("%Y-%m-%d"),
                "customer": {
                    "name": customer_name,
                    "vat_number": f"20{random.randint(1000, 9999)}00{random.randint(100, 999)}"  # Bahrain VAT format
                },
                "items": [
                    {
                        "item": item['name'],
                        "qty": item['qty'],
                        "rate": item['rate'],
                        "amount": item['amount'],
                        "vat_percent": BAHRAIN_VAT_RATE
                    } for item in items
                ],
                "subtotal": round(subtotal, 2),
                "VAT_rate": BAHRAIN_VAT_RATE,
                "VAT": round(total_vat, 2),
                "total": round(subtotal + total_vat, 2),
                "template_applied": "vat_template",
                "vat_number": f"20{random.randint(1000, 9999)}00{random.randint(100, 999)}"
            }
            
        else:
            # Fallback to plain invoice
            return {
                "invoice_type": "Plain",
                "invoice_number": invoice_id,
                "date": invoice_date.strftime("%Y-%m-%d"),
                "customer": {"name": customer_name},
                "items": [
                    {
                        "item": item['name'],
                        "qty": item['qty'],
                        "rate": item['rate'],
                        "amount": item['amount']
                    } for item in items
                ],
                "subtotal": round(subtotal, 2),
                "total": round(subtotal, 2),
                "template_applied": "plain_template"
            }
    
    def _calculate_item_distribution(self, items: List[Dict], target_amount: float) -> List[Dict]:
        """
        Calculate realistic quantities and prices for items to reach target amount.
        
        Args:
            items: List of catalog items to include
            target_amount: Target invoice amount to reach
            
        Returns:
            List of invoice items with quantities and calculated values
        """
        invoice_items = []
        
        # First pass: assign minimum quantities (usually 1)
        base_amount = 0
        for item in items:
            qty = random.randint(1, 3)  # Start with small quantities
            rate = item['price']
            
            # Apply small random variation to price (±5%) for realism
            rate = rate * random.uniform(0.95, 1.05)
            rate = round(rate, 2)
            
            amount = qty * rate
            base_amount += amount
            
            invoice_items.append({
                'sku': item['sku'],
                'name': item['name'],
                'qty': qty,
                'rate': rate,
                'amount': round(amount, 2),
                'gst_percent': item.get('gst_percent', 18),  # Default GST rate
                'vat_percent': item.get('vat_percent', 10)   # Default VAT rate
            })
        
        # Second pass: adjust quantities to reach target amount
        if base_amount < target_amount:
            # Need to increase quantities
            remaining = target_amount - base_amount
            
            # Sort items by price (ascending) for realistic distribution
            invoice_items.sort(key=lambda x: x['rate'])
            
            for item in invoice_items:
                if remaining <= 0:
                    break
                    
                # Calculate how much adding 1 to qty would increase total
                item_increase = item['rate']
                
                # Calculate max reasonable quantity increase
                max_increase = min(
                    math.floor(remaining / item_increase),
                    20  # Cap at reasonable quantity
                )
                
                if max_increase > 0:
                    increase = random.randint(1, max_increase)
                    new_qty = item['qty'] + increase
                    
                    # Update item values
                    item['qty'] = new_qty
                    item['amount'] = round(new_qty * item['rate'], 2)
                    
                    # Update remaining amount
                    remaining -= increase * item_increase
        
        elif base_amount > target_amount:
            # Need to decrease quantities (less common)
            # Just scale everything proportionally
            scale_factor = target_amount / base_amount
            
            for item in invoice_items:
                # Don't reduce below 1
                if item['qty'] > 1:
                    new_qty = max(1, round(item['qty'] * scale_factor))
                    
                    # Update item values
                    item['qty'] = new_qty
                    item['amount'] = round(new_qty * item['rate'], 2)
        
        return invoice_items
    
    def _distribute_invoice_dates(self, count: int) -> List[datetime]:
        """
        Distribute invoice dates across the date range based on distribution_mode.
        
        Args:
            count: Number of invoices to distribute
            
        Returns:
            List of datetime objects for invoice dates
        """
        start = datetime.combine(self.config.start_date, datetime.min.time())
        end = datetime.combine(self.config.end_date, datetime.min.time())
        
        distribution_mode = self.config.distribution_mode or 'even'
        
        if distribution_mode == 'even':
            # Evenly distribute across date range
            if count > 1:
                interval = (end - start) / (count - 1)
                dates = [start + interval * i for i in range(count)]
            else:
                dates = [start + (end - start) / 2]  # Middle of range for single invoice
                
        elif distribution_mode == 'burst':
            # Concentrate invoices in first 20% of time period
            burst_split = int(count * 0.8)
            burst_date_range = start + timedelta(days=int(self.date_range * 0.2))
            
            # Generate dates in both segments
            early_dates = [
                start + (burst_date_range - start) * random.random()
                for _ in range(burst_split)
            ]
            
            late_dates = [
                burst_date_range + (end - burst_date_range) * random.random()
                for _ in range(count - burst_split)
            ]
            
            dates = early_dates + late_dates
            
        elif distribution_mode == 'weighted':
            # More invoices toward end of period (weighted distribution)
            dates = []
            for _ in range(count):
                # Use power function to skew toward end of period
                random_factor = random.random() ** 0.5  # Square root for moderate skew
                date_offset = (end - start) * random_factor
                dates.append(start + date_offset)
            
        else:  # Default to even distribution for unknown modes
            # Even distribution as fallback
            if count > 1:
                interval = (end - start) / (count - 1)
                dates = [start + interval * i for i in range(count)]
            else:
                dates = [start + (end - start) / 2]
        
        # Sort dates chronologically
        dates.sort()
        
        # Add random hours for realism
        for i in range(len(dates)):
            business_hour = random.randint(9, 17)  # 9 AM to 5 PM
            dates[i] = dates[i].replace(hour=business_hour)
        
        return dates
    
    def _generate_customer_pool(self, pool_size: int = 20) -> List[str]:
        """
        Generate a pool of realistic customer names based on name_type.
        
        Args:
            pool_size: Number of customers to generate
            
        Returns:
            List of customer names
        """
        customers = []
        
        for _ in range(pool_size):
            customers.append(self._generate_customer_name(self.config.name_type))
            
        return customers
    
    def _generate_customer_name(self, name_type: str) -> str:
        """
        Generate a realistic customer name based on specified type.
        
        Args:
            name_type: Type of name to generate
            
        Returns:
            A realistic customer name
        """
        if name_type == 'malabar_muslim':
            first_names = [
                "Shabeer", "Nabeel", "Rafiya", "Niyas", "Safiya", "Rashid",
                "Faisal", "Jasmin", "Haris", "Lubna", "Shameer", "Nusrath",
                "Anwar", "Bushra", "Faizal", "Mumtaz", "Rizwan", "Sabira",
                "Thasneem", "Waseem", "Yasmin", "Zubair", "Asif", "Nasreen"
            ]
            last_names = [
                "Rahman", "Ashraf", "Kareem", "Faheem", "Hassan", "Salim",
                "Hameed", "Jabbar", "Latheef", "Mansoor", "Nazeer", "Qasim",
                "Rahiman", "Shamsuddin", "Thajuddin", "Usman", "Wahab", "Yaseen",
                "Zainuddin", "Ahmed", "Basheer", "Hakeem", "Jaleel", "Kaleel"
            ]
            
            return f"{random.choice(first_names)} {random.choice(last_names)}"
            
        elif name_type == 'south_indian_generic':
            first_names = [
                "Karthik", "Meena", "Deepa", "Arjun", "Priya", "Shankar",
                "Ramesh", "Lakshmi", "Suresh", "Divya", "Rajesh", "Kavitha",
                "Venkat", "Anjali", "Prakash", "Shobha", "Ganesh", "Radha",
                "Krishna", "Sudha", "Mohan", "Geetha", "Ravi", "Padma"
            ]
            last_names = [
                "Raj", "Menon", "Prabhu", "Nair", "Pillai", "Iyer",
                "Krishnan", "Varma", "Reddy", "Rao", "Hegde", "Shetty",
                "Kamath", "Pai", "Bhat", "Acharya", "Kurup", "Panicker",
                "Warrier", "Namboothiri", "Thampi", "Unni", "Nambiar", "Mani"
            ]
            
            return f"{random.choice(first_names)} {random.choice(last_names)}"
            
        elif name_type == 'indian_company':
            prefixes = [
                "Prateek", "Shakti", "Vetrivel", "Nova", "Surya", "Krishna",
                "Ganesh", "Lakshmi", "Shiva", "Durga", "Saraswati", "Indra"
            ]
            
            middle = [
                "Trading", "Enterprises", "Industries", "Distributors", "Marketing",
                "Commercial", "Business", "Mercantile", "Corporate", "Ventures"
            ]
            
            suffixes = [
                "Private Limited", "Pvt Ltd", "Limited", "LLP", "& Co",
                "Corporation", "India Pvt Ltd", "Enterprises", "& Sons", "Associates"
            ]
            
            # 70% chance of having a middle term
            if random.random() > 0.3:
                return f"{random.choice(prefixes)} {random.choice(middle)} {random.choice(suffixes)}"
            else:
                return f"{random.choice(prefixes)} {random.choice(suffixes)}"
                
        elif name_type == 'bahrain_name':
            first_names = [
                "Saeed", "Fatima", "Hussain", "Mariam", "Ahmed", "Layla",
                "Mohammed", "Noor", "Abdullah", "Zainab", "Khalid", "Aisha",
                "Hassan", "Amina", "Ibrahim", "Hessa", "Jassim", "Latifa"
            ]
            
            last_names = [
                "Al Mansoor", "Al Zayani", "Al Qasim", "Al Khalifa", "Al Aali",
                "Al Noaimi", "Al Mahmood", "Al Sayed", "Al Koheji", "Al Doseri",
                "Al Hamer", "Al Shaikh", "Al Saleh", "Al Fadhel", "Al Saad"
            ]
            
            return f"{random.choice(first_names)} {random.choice(last_names)}"
            
        elif name_type == 'bahrain_company':
            prefixes = [
                "Al Manama", "Gulf Gate", "BHR", "Middle East", "Arabian Gulf",
                "Bahrain", "Al Seef", "Al Salam", "Pearl", "Royal Bahrain"
            ]
            
            middle = [
                "Trading", "Technologies", "Contracting", "Industries", "Services",
                "Logistics", "Solutions", "International", "Commercial", "Group"
            ]
            
            suffixes = [
                "W.L.L.", "S.P.C.", "B.S.C.", "& Sons Trading", "Company",
                "Corporation", "Holdings", "Enterprises", "& Partners", "Limited"
            ]
            
            # 80% chance of having a middle term
            if random.random() > 0.2:
                return f"{random.choice(prefixes)} {random.choice(middle)} {random.choice(suffixes)}"
            else:
                return f"{random.choice(prefixes)} {random.choice(suffixes)}"
                
        elif name_type == 'it_company':
            prefixes = [
                "Codewave", "Netfinity", "Synaptix", "ByteLogic", "DataMatrix",
                "CloudSphere", "TechVista", "DigitalEdge", "InnovateHub", "CyberPeak"
            ]
            
            suffixes = [
                "Systems", "Solutions", "Technologies", "Innovations", "Software",
                "Dynamics", "Networks", "Labs", "Platforms", "Microsystems"
            ]
            
            # Add industry focus 30% of the time
            if random.random() > 0.7:
                focus = [
                    "AI", "Cloud", "DevOps", "FinTech", "Healthcare",
                    "Security", "Analytics", "Mobile", "IoT", "Blockchain"
                ]
                return f"{random.choice(prefixes)} {random.choice(focus)} {random.choice(suffixes)}"
            else:
                return f"{random.choice(prefixes)} {random.choice(suffixes)}"
            
        else:
            # Fallback to generic business name
            return f"Business {uuid.uuid4().hex[:8]}"
    
    def _assign_customers_to_invoices(self, count: int) -> List[str]:
        """
        Assign customers to invoices based on customer_repeat_rate.
        
        Args:
            count: Number of invoices
            
        Returns:
            List of customer names for each invoice
        """
        customer_repeat_rate = (self.config.customer_repeat_rate or 0) / 100
        
        if customer_repeat_rate == 0:
            # No repeat customers - use different customer for each invoice
            result = []
            for i in range(count):
                # Cycle through customers if we have more invoices than customers
                result.append(self.customers[i % len(self.customers)])
            return result
            
        elif customer_repeat_rate >= 80:
            # High repeat rate - 80% of invoices go to 20% of customers
            key_customer_count = max(1, len(self.customers) // 5)
            key_customers = random.sample(self.customers, key_customer_count)
            
            # 80% of invoices
            key_invoice_count = int(count * 0.8)
            
            # Assign key customers to 80% of invoices
            key_assignments = [random.choice(key_customers) for _ in range(key_invoice_count)]
            
            # Assign remaining customers to 20% of invoices
            regular_customers = [c for c in self.customers if c not in key_customers]
            if not regular_customers:
                regular_customers = self.customers  # Fallback
                
            regular_assignments = [random.choice(regular_customers) 
                                  for _ in range(count - key_invoice_count)]
            
            return key_assignments + regular_assignments
            
        else:
            # Medium repeat rate - use probability-based assignment
            used_customers = []
            result = []
            
            for _ in range(count):
                if used_customers and random.random() < customer_repeat_rate:
                    # Use an existing customer
                    customer = random.choice(used_customers)
                else:
                    # Use a new customer (or any customer if pool is small)
                    customer = random.choice(self.customers)
                    if customer not in used_customers:
                        used_customers.append(customer)
                
                result.append(customer)
            
            return result


def simulate_invoices(config: SimulationConfig, catalog: List[Dict]) -> List[Dict]:
    """
    Main entry point for invoice simulation.
    
    Args:
        config: Configuration parameters for the simulation
        catalog: List of items available for invoicing
        
    Returns:
        List of generated invoice dictionaries
    """
    simulator = InvoiceSimulator(config, catalog)
    return simulator.simulate()


def main():
    """
    Main entry point for the simulation engine.
    Parses command-line arguments, runs the simulation, and prints the result.
    """
    parser = argparse.ArgumentParser(description="LedgerFlow Simulation Engine")
    
    # Arguments for receiving JSON strings directly
    parser.add_argument("--config_json", type=str, required=True, help="JSON string of the simulation configuration")
    parser.add_argument("--catalog_json", type=str, required=True, help="JSON string of the item catalog")
    
    # Deprecated file-based arguments (for backward compatibility if needed)
    parser.add_argument("--config", type=str, help="Path to the configuration JSON file (deprecated)")
    parser.add_argument("--catalog", type=str, help="Path to the catalog JSON file (deprecated)")
    parser.add_argument("--output", type=str, help="Path to the output JSON file (deprecated)")

    args = parser.parse_args()

    try:
        # Load from JSON strings first
        config_data = json.loads(args.config_json)
        catalog_data = json.loads(args.catalog_json)
        
        # Convert date strings to date objects
        config_data['start_date'] = datetime.strptime(config_data['start_date'], '%Y-%m-%d').date()
        config_data['end_date'] = datetime.strptime(config_data['end_date'], '%Y-%m-%d').date()

        config = SimulationConfig(**config_data)
        
        # Run simulation
        simulator = InvoiceSimulator(config, catalog_data)
        invoices = simulator.simulate()
        
        # Prepare result
        result = {
            "status": "success",
            "invoices": invoices,
            "error": None
        }
        
    except Exception as e:
        # On error, format a consistent error response
        result = {
            "status": "error",
            "invoices": [],
            "error": str(e)
        }
        # Print error to stderr for logging in Rust
        print(f"Error in simulation engine: {e}", file=sys.stderr)
        
    # Print the final result to stdout
    print(json.dumps(result, indent=4))

if __name__ == "__main__":
    main() 