#!/usr/bin/env python3
"""
Check if we can access real imported products from the database
"""

import os
import sys

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

try:
    from app import create_app
    from app.models.product import Product
    from app.models.base import db
    
    app = create_app()
    
    with app.app_context():
        # Check if we have any products
        product_count = Product.query.count()
        print(f"📊 Total products in database: {product_count}")
        
        if product_count > 0:
            # Get first 10 products
            products = Product.query.filter_by(is_active=True).limit(10).all()
            
            print("\n📦 Sample products from imported catalog:")
            print("-" * 80)
            for i, p in enumerate(products, 1):
                print(f"{i:2d}. {p.name[:40]:<40} | ₹{p.sale_price:>8,.0f} | GST: {p.gst_rate:>4.1f}% | HSN: {p.hsn_code or 'N/A'}")
            
            print(f"\n✅ Found {len(products)} active products for invoice generation")
            
            # Show categories
            categories = db.session.query(Product.category).distinct().all()
            print(f"\n📂 Product categories: {', '.join([c[0] for c in categories if c[0]])}")
            
        else:
            print("⚠️  No products found in database. Using demo products instead.")
            
except Exception as e:
    print(f"❌ Database access failed: {str(e)}")
    print("Using premium demo products for invoice generation.")