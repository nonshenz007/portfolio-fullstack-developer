import pandas as pd
import numpy as np
from datetime import datetime
import re
import secrets
from app.models import Product
from app.models.base import db

class ExcelImporter:
    """Service for importing products from Excel files"""
    
    def __init__(self):
        self.import_batch_id = secrets.token_urlsafe(8)
        self.errors = []
        self.warnings = []
        
    def import_products(self, filepath):
        """Import products from Excel file"""
        try:
            # Read Excel file
            df = pd.read_excel(filepath)
            
            # Validate and normalize columns
            df = self._normalize_columns(df)
            
            if not self._validate_required_columns(df):
                return {
                    'success': False,
                    'error': 'Missing required columns',
                    'errors': self.errors
                }
            
            # Process each row
            imported_count = 0
            skipped_count = 0
            
            for index, row in df.iterrows():
                try:
                    product = self._create_product_from_row(row, index)
                    if product:
                        db.session.add(product)
                        imported_count += 1
                    else:
                        skipped_count += 1
                except Exception as e:
                    self.errors.append(f"Row {index + 2}: {str(e)}")
                    skipped_count += 1
            
            # Commit all products
            db.session.commit()
            
            return {
                'success': True,
                'imported_count': imported_count,
                'skipped_count': skipped_count,
                'total_rows': len(df),
                'errors': self.errors,
                'warnings': self.warnings,
                'import_batch_id': self.import_batch_id
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'error': f"Failed to read Excel file: {str(e)}"
            }
    
    def _normalize_columns(self, df):
        """Normalize column names for consistency"""
        # Common column name mappings
        column_mappings = {
            'item': 'name',
            'item_name': 'name',
            'product': 'name',
            'product_name': 'name',
            'description': 'name',
            'price': 'sale_price',
            'selling_price': 'sale_price',
            'rate': 'sale_price',
            'gst': 'gst_rate',
            'gst%': 'gst_rate',
            'gst_percentage': 'gst_rate',
            'tax': 'gst_rate',
            'tax%': 'gst_rate',
            'vat': 'vat_rate',
            'vat%': 'vat_rate',
            'hsn': 'hsn_code',
            'hsn_sac': 'hsn_code',
            'sac': 'hsn_code',
            'sku': 'code',
            'item_code': 'code',
            'product_code': 'code',
            'uom': 'unit',
            'unit_of_measure': 'unit'
        }
        
        # Normalize column names (lowercase and strip)
        df.columns = df.columns.str.lower().str.strip()
        
        # Apply mappings
        df = df.rename(columns=column_mappings)
        
        return df
    
    def _validate_required_columns(self, df):
        """Validate that required columns exist"""
        required_columns = ['name', 'sale_price']
        missing_columns = []
        
        for col in required_columns:
            if col not in df.columns:
                missing_columns.append(col)
                self.errors.append(f"Missing required column: {col}")
        
        return len(missing_columns) == 0
    
    def _create_product_from_row(self, row, index):
        """Create a Product object from a DataFrame row"""
        # Skip empty rows
        if pd.isna(row.get('name')) or str(row.get('name')).strip() == '':
            self.warnings.append(f"Row {index + 2}: Skipped due to empty name")
            return None
        
        # Extract and validate data
        name = str(row.get('name')).strip()
        
        # Price validation
        try:
            sale_price = float(row.get('sale_price', 0))
            if sale_price <= 0:
                self.errors.append(f"Row {index + 2}: Invalid price {sale_price}")
                return None
        except (ValueError, TypeError):
            self.errors.append(f"Row {index + 2}: Invalid price format")
            return None
        
        # Create product
        product = Product(
            name=name,
            sale_price=sale_price,
            import_batch_id=self.import_batch_id
        )
        
        # Optional fields
        
        # MRP
        if 'mrp' in row and not pd.isna(row['mrp']):
            try:
                product.mrp = float(row['mrp'])
            except:
                product.mrp = sale_price
        else:
            product.mrp = sale_price
        
        # Product code
        if 'code' in row and not pd.isna(row['code']):
            product.code = str(row['code']).strip()
        else:
            # Generate unique code
            product.code = f"PRD-{secrets.token_hex(4).upper()}"
        
        # Category
        if 'category' in row and not pd.isna(row['category']):
            product.category = str(row['category']).strip()
        
        # Unit
        if 'unit' in row and not pd.isna(row['unit']):
            product.unit = str(row['unit']).strip()
        else:
            product.unit = 'Nos'
        
        # GST Rate
        if 'gst_rate' in row and not pd.isna(row['gst_rate']):
            try:
                gst_rate = float(str(row['gst_rate']).replace('%', ''))
                # Validate GST rate
                valid_gst_rates = [0, 5, 12, 18, 28]
                if gst_rate in valid_gst_rates:
                    product.gst_rate = gst_rate
                else:
                    # Find closest valid rate
                    product.gst_rate = min(valid_gst_rates, key=lambda x: abs(x - gst_rate))
                    self.warnings.append(f"Row {index + 2}: GST rate {gst_rate}% adjusted to {product.gst_rate}%")
            except:
                product.gst_rate = 18  # Default GST
        else:
            # Auto-infer GST based on category or price
            product.gst_rate = self._infer_gst_rate(product)
        
        # VAT Rate (for Bahrain)
        if 'vat_rate' in row and not pd.isna(row['vat_rate']):
            try:
                vat_rate = float(str(row['vat_rate']).replace('%', ''))
                product.vat_rate = vat_rate if vat_rate in [0, 10] else 10
            except:
                product.vat_rate = 10
        
        # HSN Code
        if 'hsn_code' in row and not pd.isna(row['hsn_code']):
            product.hsn_code = str(row['hsn_code']).strip()
        
        # Calculate discount percentage
        if product.mrp > product.sale_price:
            product.discount_percentage = ((product.mrp - product.sale_price) / product.mrp) * 100
        
        # Set statistical data for realistic generation
        product.avg_quantity_sold = self._estimate_avg_quantity(product)
        product.popularity_score = self._calculate_popularity_score(product)
        
        return product
    
    def _infer_gst_rate(self, product):
        """Infer GST rate based on product characteristics"""
        name_lower = product.name.lower()
        
        # Essential items - 0% or 5%
        if any(word in name_lower for word in ['milk', 'bread', 'flour', 'rice', 'wheat', 'pulse', 'salt']):
            return 0
        elif any(word in name_lower for word in ['medicine', 'drug', 'tablet', 'syrup']):
            return 5
        
        # Standard items - 12%
        elif any(word in name_lower for word in ['mobile', 'computer', 'laptop', 'phone']):
            return 12
        
        # Luxury items - 28%
        elif any(word in name_lower for word in ['gold', 'diamond', 'jewel', 'luxury', 'premium']):
            return 28
        elif product.sale_price > 50000:  # High-value items
            return 28
        
        # Default - 18%
        return 18
    
    def _estimate_avg_quantity(self, product):
        """Estimate average quantity sold based on product type and price"""
        # Lower price = higher quantity typically
        if product.sale_price < 100:
            return np.random.uniform(10, 50)
        elif product.sale_price < 1000:
            return np.random.uniform(5, 20)
        elif product.sale_price < 10000:
            return np.random.uniform(2, 10)
        else:
            return np.random.uniform(1, 5)
    
    def _calculate_popularity_score(self, product):
        """Calculate product popularity score (0-1)"""
        # Factors: price point, discount, category
        score = 0.5  # Base score
        
        # Discount factor
        if product.discount_percentage > 20:
            score += 0.2
        elif product.discount_percentage > 10:
            score += 0.1
        
        # Price factor (mid-range products are more popular)
        if 500 <= product.sale_price <= 5000:
            score += 0.2
        
        # Category factor
        if product.category:
            popular_categories = ['electronics', 'grocery', 'clothing', 'mobile']
            if any(cat in str(product.category).lower() for cat in popular_categories):
                score += 0.1
        
        return min(1.0, score) 