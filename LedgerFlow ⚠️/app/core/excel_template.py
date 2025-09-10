import pandas as pd
import numpy as np
from datetime import datetime
import os

class ExcelTemplateGenerator:
    """Generates Excel templates with sample data for product imports"""
    
    SAMPLE_PRODUCTS = [
        {
            'Product Name': 'LED Smart TV 55"',
            'SKU/HSN': '8528.72.00',
            'Base Price': 45999.00,
            'GST Rate': 18,
            'VAT Rate': 10,
            'Category': 'Electronics',
            'Unit': 'Nos',
            'Brand': 'Crystal Vision'
        },
        {
            'Product Name': 'Wireless Earbuds Pro',
            'SKU/HSN': '8518.30.00',
            'Base Price': 12999.00,
            'GST Rate': 18,
            'VAT Rate': 10,
            'Category': 'Electronics',
            'Unit': 'Pcs',
            'Brand': 'SoundMaster'
        }
    ]
    
    @classmethod
    def generate_template(cls, output_path):
        """Generate Excel template with sample data"""
        df = pd.DataFrame(cls.SAMPLE_PRODUCTS)
        
        # Create Excel writer with xlsxwriter engine
        writer = pd.ExcelWriter(output_path, engine='xlsxwriter')
        
        # Write data to Excel
        df.to_excel(writer, index=False, sheet_name='Products')
        
        # Get workbook and worksheet objects
        workbook = writer.book
        worksheet = writer.sheets['Products']
        
        # Add formats
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#D9EAD3',
            'border': 1
        })
        
        required_format = workbook.add_format({
            'bold': True,
            'bg_color': '#FCE5CD',
            'border': 1
        })
        
        # Format headers and highlight required columns
        for col_num, value in enumerate(df.columns.values):
            if value in ['Product Name', 'Base Price']:
                worksheet.write(0, col_num, f"{value} *", required_format)
            else:
                worksheet.write(0, col_num, value, header_format)
        
        # Set column widths
        worksheet.set_column('A:A', 30)  # Product Name
        worksheet.set_column('B:B', 15)  # SKU/HSN
        worksheet.set_column('C:C', 12)  # Base Price
        worksheet.set_column('D:D', 10)  # GST Rate
        worksheet.set_column('E:E', 10)  # VAT Rate
        worksheet.set_column('F:F', 15)  # Category
        worksheet.set_column('G:G', 10)  # Unit
        worksheet.set_column('H:H', 15)  # Brand
        
        # Add data validation
        price_validation = {'validate': 'decimal',
                          'criteria': '>',
                          'value': 0,
                          'error_title': 'Invalid Base Price',
                          'error_message': 'Base Price must be greater than 0'}
        
        rate_validation = {'validate': 'decimal',
                          'criteria': 'between',
                          'minimum': 0,
                          'maximum': 100,
                          'error_title': 'Invalid Rate',
                          'error_message': 'Rate must be between 0 and 100'}
        
        # Apply validations
        worksheet.data_validation('C2:C1048576', price_validation)  # Base Price
        worksheet.data_validation('D2:D1048576', rate_validation)   # GST Rate
        worksheet.data_validation('E2:E1048576', rate_validation)   # VAT Rate
        
        # Freeze top row
        worksheet.freeze_panes(1, 0)
        
        # Save the file
        writer.close() 