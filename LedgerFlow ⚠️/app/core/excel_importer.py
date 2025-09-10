import pandas as pd
import numpy as np
from app.models.product import Product
from app.core.diagnostics_logger import DiagnosticsLogger
import secrets

class ExcelCatalogImporter:
    """Handles importing product catalogs from Excel files"""
    
    REQUIRED_COLUMNS = [
        'Product Name',
        'Base Price'
    ]
    
    OPTIONAL_COLUMNS = [
        'SKU/HSN',
        'GST Rate',
        'VAT Rate',
        'Brand',
        'Category',
        'Unit',
        'Quantity'  # Add this line
    ]
    
    @classmethod
    def import_catalog(cls, file_path, db_session):
        """Import products from Excel file and return results"""
        diagnostics = DiagnosticsLogger()
        import_batch_id = secrets.token_urlsafe(8)
        
        try:
            # Read Excel file
            diagnostics.info(f"Reading Excel file: {file_path}")
            df = pd.read_excel(file_path)
            
            # Log column names for debugging
            diagnostics.info(f"Found columns: {', '.join(df.columns)}")
            
            # Validate required columns
            missing_cols = [col for col in cls.REQUIRED_COLUMNS if col not in df.columns]
            if missing_cols:
                error_msg = f"Missing required columns: {', '.join(missing_cols)}"
                diagnostics.error(error_msg)
                return {
                    'success': False,
                    'error': error_msg
                }
            
            # Process each row
            imported_count = 0
            updated_count = 0
            
            for _, row in df.iterrows():
                try:
                    # Generate a unique code if SKU/HSN is not provided
                    code = str(row.get('SKU/HSN', secrets.token_urlsafe(8)))
                    
                    # Prepare product data
                    product_data = {
                        'name': row['Product Name'],
                        'code': code,
                        'category': row.get('Category', None),
                        'unit': row.get('Unit', 'Nos'),  # Default unit is Nos
                        'mrp': float(row['Base Price']),
                        'sale_price': float(row['Base Price']),
                        'gst_rate': float(row.get('GST Rate', 18)),  # Default GST 18%
                        'vat_rate': float(row.get('VAT Rate', 10)),  # Default VAT 10%
                        'hsn_code': code,
                        'stock_quantity': float(row.get('Quantity', 0)),  # Read from Excel, default to 0 if not present
                        'reorder_level': 10,    # Default reorder level
                        'is_active': True,
                        'import_batch_id': import_batch_id,
                        'avg_quantity_sold': float(5),
                        'popularity_score': float(0.5)
                    }
                    
                    # Check if product exists
                    existing_product = Product.query.filter_by(code=product_data['code']).first()
                    
                    if existing_product:
                        # Update existing product
                        for key, value in product_data.items():
                            setattr(existing_product, key, value)
                        updated_count += 1
                    else:
                        # Create new product
                        new_product = Product(**product_data)
                        db_session.add(new_product)
                        imported_count += 1
                    
                except Exception as row_error:
                    diagnostics.error(f"Error processing row: {row_error}")
                    continue
            
            db_session.commit()
            return {
                'success': True,
                'imported': imported_count,
                'updated': updated_count
            }
            
        except Exception as e:
            db_session.rollback()
            error_msg = f"Failed to import products: {str(e)}"
            diagnostics.error(error_msg)
            return {
                'success': False,
                'error': error_msg
            }