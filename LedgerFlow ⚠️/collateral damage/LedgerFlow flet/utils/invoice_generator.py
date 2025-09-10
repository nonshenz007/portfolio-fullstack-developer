import random
from datetime import datetime, timedelta
from typing import List, Dict

# HSN/SAC codes for different product categories
HSN_CODES = {
    "Desi Medical": {
        "Crocin 500mg": "3004", "Paracetamol 650mg": "3004", "ORS Sachet": "3004",
        "Dettol Antiseptic": "3401", "Band-Aid": "3005", "Thermometer": "9025",
        "BP Monitor": "9018", "Surgical Mask": "6307", "Hand Sanitizer": "3401"
    },
    "Grocery": {
        "Basmati Rice 5kg": "1006", "Toor Dal 1kg": "0713", "Sunflower Oil 1L": "1512",
        "Sugar 1kg": "1701", "Tea Powder 250g": "0902", "Milk 1L": "0401",
        "Turmeric Powder": "0910", "Red Chili Powder": "0904", "Salt 1kg": "2501"
    },
    "Textile": {
        "Cotton Saree": "5208", "Silk Dupatta": "5007", "Kurta Set": "6203",
        "Bed Sheet Set": "6302", "Curtain Panel": "6303", "Towel Set": "6302"
    },
    "wholesale": {"Bulk Rice 25kg": "1006", "Oil Container 15L": "1512"},
    "retail": {"Mobile Phone": "8517", "Laptop Bag": "4202", "Power Bank": "8507"},
    "casual": {"Office Supplies": "4820", "Stationery Set": "4820"},
    "luxury": {"Premium Watch": "9101", "Gold Jewelry": "7113"}
}

def get_gst_rate(item_name: str, business_style: str) -> float:
    """Get GST rate based on item category"""
    # Medical items typically have lower GST
    if "Medical" in business_style:
        if any(med in item_name for med in ["Tablet", "Syrup", "Medicine", "Drug"]):
            return 5.0  # Essential medicines
        else:
            return 12.0  # Medical equipment
    
    # Food items
    elif "Grocery" in business_style:
        if any(food in item_name for food in ["Rice", "Dal", "Oil", "Sugar", "Salt"]):
            return 5.0  # Essential food items
        else:
            return 12.0  # Processed foods
    
    # Textiles
    elif "Textile" in business_style:
        return 12.0  # Most textiles
    
    # Default rates for other categories
    elif "luxury" in business_style:
        return 28.0  # Luxury items
    else:
        return 18.0  # Standard rate

def get_vat_rate(item_name: str, business_style: str) -> float:
    """Get VAT rate for Bahrain (0% or 10%)"""
    # Essential items are typically 0% VAT
    if any(essential in item_name.lower() for essential in ["milk", "rice", "bread", "medicine", "water"]):
        return 0.0
    else:
        return 10.0  # Standard VAT rate in Bahrain

def calculate_gst_breakdown(amount: float, gst_rate: float) -> Dict:
    """Calculate CGST and SGST breakdown"""
    total_gst = amount * (gst_rate / 100)
    cgst = total_gst / 2
    sgst = total_gst / 2
    return {
        "gst_rate": gst_rate,
        "total_gst": round(total_gst, 2),
        "cgst": round(cgst, 2),
        "sgst": round(sgst, 2)
    }

def amount_in_words_inr(amount: float) -> str:
    """Convert amount to words in Indian format"""
    ones = ["", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine"]
    teens = ["Ten", "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen", "Seventeen", "Eighteen", "Nineteen"]
    tens = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"]
    
    def convert_hundreds(n):
        result = ""
        if n >= 100:
            result += ones[n // 100] + " Hundred "
            n %= 100
        if n >= 20:
            result += tens[n // 10] + " "
            n %= 10
        elif n >= 10:
            result += teens[n - 10] + " "
            return result
        if n > 0:
            result += ones[n] + " "
        return result
    
    if amount == 0:
        return "Zero Only"
    
    amount = int(amount)
    crores = amount // 10000000
    amount %= 10000000
    lakhs = amount // 100000
    amount %= 100000
    thousands = amount // 1000
    amount %= 1000
    
    result = ""
    if crores > 0:
        result += convert_hundreds(crores) + "Crore "
    if lakhs > 0:
        result += convert_hundreds(lakhs) + "Lakh "
    if thousands > 0:
        result += convert_hundreds(thousands) + "Thousand "
    if amount > 0:
        result += convert_hundreds(amount)
    
    return "Indian Rupee " + result.strip() + " Only"

def generate_gstin() -> str:
    """Generate a realistic GSTIN number"""
    state_codes = ["29", "27", "09", "06", "24", "07"]  # Karnataka, Maharashtra, Delhi, Haryana, Gujarat, Uttar Pradesh
    state_code = random.choice(state_codes)
    pan_like = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=5))
    numbers = ''.join(random.choices('0123456789', k=4))
    entity_code = random.choice(['1', '2', '4'])
    check_digit = random.choice('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ')
    return f"{state_code}{pan_like}{numbers}{entity_code}Z{check_digit}"

def generate_vat_number() -> str:
    """Generate a realistic Bahrain VAT number"""
    return f"{random.randint(200000000, 999999999):09d}"

def generate_plain_invoices(revenue_target: float, start_date: str, end_date: str, business_style: str, template_type: str = "Plain") -> List[Dict]:
    """
    Generate realistic invoices for Indian/Bahrain businesses based on template type.
    
    Args:
        revenue_target: Target revenue amount (₹ or BHD)
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format  
        business_style: Business type ("Desi Medical", "Grocery", "Textile", etc.)
        template_type: "Plain", "GST", or "VAT"
    
    Returns:
        List of invoice dictionaries with template-specific fields
    """
    
    # Convert date strings to datetime objects
    start_dt = datetime.strptime(start_date, '%Y-%m-%d')
    end_dt = datetime.strptime(end_date, '%Y-%m-%d')
    
    # Business-specific item catalogs
    business_catalogs = {
        "Desi Medical": {
            "items": [
                "Crocin 500mg", "Paracetamol 650mg", "ORS Sachet", "Digene Tablet",
                "Vicks VapoRub", "Dettol Antiseptic", "Band-Aid", "Gauze Roll",
                "Betadine Solution", "Thermometer", "BP Monitor", "Glucose Strip",
                "Insulin Pen", "Syrup Bottle", "Tablet Strip", "Injection Vial",
                "Surgical Mask", "Hand Sanitizer", "Vitamin D3", "Calcium Tablet"
            ],
            "price_range": (10, 500),
            "qty_range": (1, 10)
        },
        "Grocery": {
            "items": [
                "Basmati Rice 5kg", "Toor Dal 1kg", "Sunflower Oil 1L", "Sugar 1kg",
                "Tea Powder 250g", "Milk 1L", "Bread Loaf", "Butter 100g",
                "Biscuit Pack", "Noodles Pack", "Salt 1kg", "Turmeric Powder",
                "Red Chili Powder", "Coriander Seeds", "Jeera Powder", "Garam Masala",
                "Onion 1kg", "Potato 1kg", "Tomato 1kg", "Ginger 250g"
            ],
            "price_range": (15, 300),
            "qty_range": (1, 8)
        },
        "Textile": {
            "items": [
                "Cotton Saree", "Silk Dupatta", "Kurta Set", "Palazzo Pants",
                "Cotton Shirt", "Denim Jeans", "Traditional Lehenga", "Shawl",
                "Bed Sheet Set", "Cushion Cover", "Table Runner", "Curtain Panel",
                "Towel Set", "Blanket", "Pillow Cover", "Fabric Meter",
                "Embroidered Suit", "Designer Blouse", "Men's Kurta", "Kids Dress"
            ],
            "price_range": (200, 3000),
            "qty_range": (1, 5)
        },
        "wholesale": {
            "items": [
                "Bulk Rice 25kg", "Oil Container 15L", "Sugar Sack 50kg", "Dal Bag 25kg",
                "Spice Mix Bulk", "Tea Chest 5kg", "Wheat Flour 25kg", "Onion Sack 50kg",
                "Potato Bag 25kg", "Bulk Detergent", "Soap Carton", "Biscuit Carton",
                "Milk Powder 5kg", "Dry Fruits 1kg", "Pulses Mix 10kg", "Salt Bag 25kg",
                "Cooking Oil Jerry", "Bulk Noodles", "Snack Box", "Beverage Crate"
            ],
            "price_range": (500, 5000),
            "qty_range": (1, 20)
        },
        "casual": {
            "items": [
                "Office Supplies", "Stationery Set", "Notebook Pack", "Pen Set",
                "Calculator", "File Folder", "Paper Ream", "Stapler",
                "Rubber Stamp", "Ink Pad", "Marker Set", "Whiteboard",
                "Computer Cable", "USB Drive", "Mouse Pad", "Keyboard",
                "Phone Cover", "Charger", "Earphones", "Screen Guard"
            ],
            "price_range": (50, 800),
            "qty_range": (1, 6)
        },
        "retail": {
            "items": [
                "Mobile Phone", "Tablet", "Laptop Bag", "Power Bank",
                "Bluetooth Speaker", "Headphones", "Smart Watch", "Camera",
                "Home Appliance", "Kitchen Gadget", "Electronic Item", "Tool Set",
                "Sports Equipment", "Book Collection", "Art Supplies", "Toy Set",
                "Beauty Product", "Perfume", "Wallet", "Handbag"
            ],
            "price_range": (200, 2000),
            "qty_range": (1, 4)
        },
        "luxury": {
            "items": [
                "Premium Watch", "Gold Jewelry", "Designer Handbag", "Luxury Perfume",
                "Premium Electronics", "Fine Artwork", "Silk Carpet", "Crystal Vase",
                "Premium Furniture", "Designer Clothing", "Luxury Bedding", "Fine China",
                "Premium Leather Goods", "Antique Piece", "Designer Shoes", "Luxury Skincare",
                "Premium Wine", "Gourmet Food", "High-end Gadget", "Collectible Item"
            ],
            "price_range": (1000, 15000),
            "qty_range": (1, 3)
        }
    }
    
    # Indian/Muslim customer names
    customer_names = [
        "Muhammad Irfan", "Aaliya Sharma", "Raj Patel", "Fatima Khan", 
        "Arjun Mehta", "Zara Ahmed", "Vikram Singh", "Aisha Begum",
        "Rohit Gupta", "Noor Fatima", "Amit Kumar", "Sana Sheikh",
        "Priya Verma", "Omar Hassan", "Deepak Yadav", "Mariam Ali",
        "Suresh Reddy", "Ayesha Siddiqui", "Ravi Sharma", "Hina Malik",
        "Ajay Joshi", "Rukhsar Khatoon", "Manoj Tiwari", "Shabana Ansari",
        "Kiran Jain", "Salma Begum", "Naveen Kumar", "Farah Ahmad",
        "Sandeep Agarwal", "Zeenat Khan", "Ramesh Iyer", "Nasreen Sheikh"
    ]
    
    # Get business catalog
    catalog = business_catalogs.get(business_style, business_catalogs["casual"])
    
    # Calculate number of invoices (15-40 range)
    num_invoices = random.randint(15, 40)
    
    # Calculate target per invoice (with some variance)
    base_amount_per_invoice = revenue_target / num_invoices
    
    # Currency based on template type
    currency = "BHD" if template_type == "VAT" else "INR"
    currency_symbol = "BD" if template_type == "VAT" else "₹"
    
    invoices = []
    total_generated = 0
    
    for i in range(num_invoices):
        # Generate random invoice number
        invoice_number = f"INV-{random.randint(10000, 99999)}"
        
        # Generate random date within range
        days_diff = (end_dt - start_dt).days
        random_days = random.randint(0, days_diff)
        invoice_date = (start_dt + timedelta(days=random_days)).strftime('%Y-%m-%d')
        
        # Select random customer
        customer_name = random.choice(customer_names)
        
        # Calculate target amount for this invoice (±30% variance)
        variance = random.uniform(0.7, 1.3)
        target_amount = base_amount_per_invoice * variance
        
        # Generate items for this invoice
        items = []
        current_total = 0
        num_items = random.randint(1, 5)  # 1-5 items per invoice
        
        for j in range(num_items):
            item_name = random.choice(catalog["items"])
            qty = random.randint(*catalog["qty_range"])
            
            if j == num_items - 1:  # Last item - adjust to meet target
                remaining = target_amount - current_total
                if remaining > 0:
                    rate = max(remaining / qty, catalog["price_range"][0])
                else:
                    rate = random.uniform(*catalog["price_range"])
            else:
                rate = random.uniform(*catalog["price_range"])
            
            # Round rate to 2 decimal places
            rate = round(rate, 2)
            item_total = qty * rate
            
            # Get HSN code for the item
            hsn_code = HSN_CODES.get(business_style, {}).get(item_name, "9999")
            
            item_data = {
                "name": item_name,
                "qty": qty,
                "rate": rate,
                "amount": round(item_total, 2),
                "hsn_code": hsn_code
            }
            
            # Add tax calculations based on template type
            if template_type == "GST":
                gst_rate = get_gst_rate(item_name, business_style)
                gst_breakdown = calculate_gst_breakdown(item_total, gst_rate)
                item_data.update(gst_breakdown)
                item_data["total_with_tax"] = round(item_total + gst_breakdown["total_gst"], 2)
            elif template_type == "VAT":
                vat_rate = get_vat_rate(item_name, business_style)
                vat_amount = round(item_total * (vat_rate / 100), 2)
                item_data.update({
                    "vat_rate": vat_rate,
                    "vat_amount": vat_amount,
                    "total_with_tax": round(item_total + vat_amount, 2)
                })
            else:  # Plain
                item_data["total_with_tax"] = round(item_total, 2)
            
            items.append(item_data)
            current_total += item_total
        
        # Calculate final totals based on template type
        subtotal = round(sum(item["amount"] for item in items), 2)
        
        # Initialize invoice structure
        invoice = {
            "invoice_number": invoice_number,
            "date": invoice_date,
            "customer_name": customer_name,
            "items": items,
            "subtotal": subtotal,
            "template_type": template_type,
            "currency": currency,
            "currency_symbol": currency_symbol
        }
        
        # Add template-specific calculations
        if template_type == "GST":
            total_cgst = round(sum(item.get("cgst", 0) for item in items), 2)
            total_sgst = round(sum(item.get("sgst", 0) for item in items), 2)
            total_gst = total_cgst + total_sgst
            grand_total = subtotal + total_gst
            
            invoice.update({
                "total_cgst": total_cgst,
                "total_sgst": total_sgst,
                "total_gst": total_gst,
                "grand_total": round(grand_total, 2),
                "amount_in_words": amount_in_words_inr(grand_total),
                "gstin": generate_gstin(),
                "customer_gstin": generate_gstin() if random.choice([True, False]) else None
            })
            
        elif template_type == "VAT":
            total_vat = round(sum(item.get("vat_amount", 0) for item in items), 2)
            grand_total = subtotal + total_vat
            
            invoice.update({
                "total_vat": total_vat,
                "grand_total": round(grand_total, 2),
                "vat_reg_number": generate_vat_number(),
                "customer_vat_reg": generate_vat_number() if random.choice([True, False]) else None
            })
            
        else:  # Plain
            invoice.update({
                "grand_total": subtotal,
                "amount_in_words": amount_in_words_inr(subtotal)
            })
        
        # For compatibility with existing code, keep "total" field
        invoice["total"] = invoice["grand_total"]
        
        invoices.append(invoice)
        total_generated += invoice["total"]
    
    # Adjust final invoice if we're too far from target (±10% tolerance)
    tolerance = revenue_target * 0.10
    if abs(total_generated - revenue_target) > tolerance:
        adjustment_factor = revenue_target / total_generated
        
        # Adjust ALL invoices to reach target
        for invoice in invoices:
            for item in invoice["items"]:
                item["rate"] = round(item["rate"] * adjustment_factor, 2)
                item["amount"] = round(item["qty"] * item["rate"], 2)
                
                # Recalculate taxes for adjusted amounts
                if template_type == "GST":
                    gst_rate = item["gst_rate"]
                    gst_breakdown = calculate_gst_breakdown(item["amount"], gst_rate)
                    item.update(gst_breakdown)
                    item["total_with_tax"] = round(item["amount"] + gst_breakdown["total_gst"], 2)
                elif template_type == "VAT":
                    vat_rate = item["vat_rate"]
                    vat_amount = round(item["amount"] * (vat_rate / 100), 2)
                    item["vat_amount"] = vat_amount
                    item["total_with_tax"] = round(item["amount"] + vat_amount, 2)
                else:
                    item["total_with_tax"] = item["amount"]
            
            # Recalculate invoice totals
            subtotal = round(sum(item["amount"] for item in invoice["items"]), 2)
            invoice["subtotal"] = subtotal
            
            if template_type == "GST":
                total_cgst = round(sum(item.get("cgst", 0) for item in invoice["items"]), 2)
                total_sgst = round(sum(item.get("sgst", 0) for item in invoice["items"]), 2)
                total_gst = total_cgst + total_sgst
                grand_total = subtotal + total_gst
                
                invoice.update({
                    "total_cgst": total_cgst,
                    "total_sgst": total_sgst,
                    "total_gst": total_gst,
                    "grand_total": round(grand_total, 2),
                    "amount_in_words": amount_in_words_inr(grand_total)
                })
            elif template_type == "VAT":
                total_vat = round(sum(item.get("vat_amount", 0) for item in invoice["items"]), 2)
                grand_total = subtotal + total_vat
                
                invoice.update({
                    "total_vat": total_vat,
                    "grand_total": round(grand_total, 2)
                })
            else:
                invoice.update({
                    "grand_total": subtotal,
                    "amount_in_words": amount_in_words_inr(subtotal)
                })
            
            invoice["total"] = invoice["grand_total"]
        
        # Recalculate total to verify adjustment worked
        total_generated = sum(invoice["total"] for invoice in invoices)
        print(f"📊 Revenue adjustment: Target: {revenue_target:,.0f}, Final: {total_generated:,.0f}, Variance: {abs(total_generated - revenue_target)/revenue_target*100:.1f}%")
    
    return invoices


def test_generator():
    """Test function to verify the invoice generator works correctly for all template types"""
    print("Testing Invoice Generator with Different Templates\n")
    
    # Test each template type
    template_tests = [
        {"type": "Plain", "target": 50000, "currency": "₹"},
        {"type": "GST", "target": 50000, "currency": "₹"},
        {"type": "VAT", "target": 20000, "currency": "BD"}  # Lower target for Bahrain
    ]
    
    for test in template_tests:
        print(f"=== {test['type']} Template Test ===")
        
        invoices = generate_plain_invoices(
            revenue_target=test["target"],
            start_date="2024-01-01",
            end_date="2024-01-31", 
            business_style="Desi Medical",
            template_type=test["type"]
        )
        
        total = sum(inv["total"] for inv in invoices)
        print(f"Generated {len(invoices)} invoices")
        print(f"Total revenue: {test['currency']}{total:,.2f}")
        print(f"Target was: {test['currency']}{test['target']:,.2f}")
        print(f"Variance: {((total - test['target']) / test['target']) * 100:.2f}%")
        
        # Show first invoice as sample
        if invoices:
            invoice = invoices[0]
            print(f"\nSample {test['type']} Invoice:")
            print(f"Number: {invoice['invoice_number']}")
            print(f"Date: {invoice['date']}")
            print(f"Customer: {invoice['customer_name']}")
            print(f"Items: {len(invoice['items'])}")
            print(f"Subtotal: {test['currency']}{invoice['subtotal']:,.2f}")
            
            if test['type'] == 'GST':
                print(f"CGST: {test['currency']}{invoice.get('total_cgst', 0):,.2f}")
                print(f"SGST: {test['currency']}{invoice.get('total_sgst', 0):,.2f}")
                print(f"GSTIN: {invoice.get('gstin', 'N/A')}")
                print(f"Amount in Words: {invoice.get('amount_in_words', 'N/A')[:50]}...")
            elif test['type'] == 'VAT':
                print(f"VAT: {test['currency']}{invoice.get('total_vat', 0):,.2f}")
                print(f"VAT Reg: {invoice.get('vat_reg_number', 'N/A')}")
            
            print(f"Grand Total: {test['currency']}{invoice['total']:,.2f}")
            
            # Show first item details
            if invoice['items']:
                item = invoice['items'][0]
                print(f"\nFirst Item Details:")
                print(f"  Name: {item['name']}")
                print(f"  HSN: {item['hsn_code']}")
                print(f"  Qty: {item['qty']}")
                print(f"  Rate: {test['currency']}{item['rate']:,.2f}")
                if test['type'] == 'GST':
                    print(f"  GST Rate: {item.get('gst_rate', 0)}%")
                    print(f"  CGST: {test['currency']}{item.get('cgst', 0):,.2f}")
                    print(f"  SGST: {test['currency']}{item.get('sgst', 0):,.2f}")
                elif test['type'] == 'VAT':
                    print(f"  VAT Rate: {item.get('vat_rate', 0)}%")
                    print(f"  VAT Amount: {test['currency']}{item.get('vat_amount', 0):,.2f}")
        
        print("\n" + "="*60 + "\n")

# Uncomment to test
# test_generator() 