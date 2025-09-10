import pandas as pd
from datetime import datetime
import os
from config import Config

class ExcelExporter:
    """Service for exporting invoices to Excel format"""
    
    def export_invoices(self, invoices, filename=None):
        """Export multiple invoices to Excel with multiple sheets"""
        if not filename:
            filename = f"invoices_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        filepath = os.path.join(Config.EXPORT_FOLDER, filename)
        
        # Create Excel writer
        with pd.ExcelWriter(filepath, engine='xlsxwriter') as writer:
            # Get workbook and add formats
            workbook = writer.book
            
            # Define formats
            header_format = workbook.add_format({
                'bold': True,
                'bg_color': '#2c3e50',
                'font_color': 'white',
                'align': 'center',
                'valign': 'vcenter',
                'border': 1
            })
            
            currency_format = workbook.add_format({
                'num_format': '₹#,##0.00',
                'align': 'right'
            })
            
            date_format = workbook.add_format({
                'num_format': 'dd/mm/yyyy',
                'align': 'center'
            })
            
            # 1. Summary Sheet
            self._create_summary_sheet(writer, invoices, header_format, currency_format)
            
            # 2. Invoice Details Sheet
            self._create_details_sheet(writer, invoices, header_format, currency_format, date_format)
            
            # 3. Item Analysis Sheet
            self._create_items_sheet(writer, invoices, header_format, currency_format)
            
            # 4. Customer Analysis Sheet
            self._create_customer_sheet(writer, invoices, header_format, currency_format)
            
            # 5. Tax Summary Sheet (if applicable)
            if any(inv.invoice_type in ['gst', 'vat'] for inv in invoices):
                self._create_tax_sheet(writer, invoices, header_format, currency_format)
        
        return filepath
    
    def _create_summary_sheet(self, writer, invoices, header_format, currency_format):
        """Create summary statistics sheet"""
        summary_data = {
            'Metric': [
                'Total Invoices',
                'Total Revenue',
                'Average Invoice Value',
                'Total Tax Collected',
                'Total Discount Given',
                'Unique Customers',
                'Total Items Sold',
                'Date Range'
            ],
            'Value': [
                len(invoices),
                sum(inv.total_amount for inv in invoices),
                sum(inv.total_amount for inv in invoices) / len(invoices) if invoices else 0,
                sum(inv.tax_amount for inv in invoices),
                sum(inv.discount_amount for inv in invoices),
                len(set(inv.customer_id for inv in invoices if inv.customer_id)),
                sum(len(inv.items) for inv in invoices),
                f"{min(inv.invoice_date for inv in invoices).strftime('%d/%m/%Y')} - "
                f"{max(inv.invoice_date for inv in invoices).strftime('%d/%m/%Y')}" if invoices else 'N/A'
            ]
        }
        
        df = pd.DataFrame(summary_data)
        df.to_excel(writer, sheet_name='Summary', index=False)
        
        # Format the sheet
        worksheet = writer.sheets['Summary']
        
        # Set column widths
        worksheet.set_column('A:A', 25)
        worksheet.set_column('B:B', 20)
        
        # Apply header format
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)
        
        # Apply currency format to monetary values
        for row in [1, 2, 3, 4]:
            worksheet.write(row + 1, 1, summary_data['Value'][row], currency_format)
    
    def _create_details_sheet(self, writer, invoices, header_format, currency_format, date_format):
        """Create detailed invoice list"""
        details_data = []
        
        for invoice in invoices:
            details_data.append({
                'Invoice No': invoice.invoice_number,
                'Date': invoice.invoice_date,
                'Customer': invoice.customer_name,
                'Type': invoice.invoice_type.upper(),
                'Items': len(invoice.items),
                'Subtotal': invoice.subtotal,
                'Tax': invoice.tax_amount,
                'Discount': invoice.discount_amount,
                'Total': invoice.total_amount,
                'Payment Method': invoice.payment_method,
                'Payment Status': invoice.payment_status,
                'Realism Score': invoice.realism_score
            })
        
        df = pd.DataFrame(details_data)
        df.to_excel(writer, sheet_name='Invoice Details', index=False)
        
        # Format the sheet
        worksheet = writer.sheets['Invoice Details']
        
        # Set column widths
        column_widths = {
            'A:A': 20,  # Invoice No
            'B:B': 12,  # Date
            'C:C': 30,  # Customer
            'D:D': 8,   # Type
            'E:E': 8,   # Items
            'F:I': 15,  # Money columns
            'J:K': 15,  # Payment info
            'L:L': 12   # Score
        }
        
        for col_range, width in column_widths.items():
            worksheet.set_column(col_range, width)
        
        # Apply formats
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)
        
        # Format date column
        for row in range(len(details_data)):
            worksheet.write_datetime(row + 1, 1, details_data[row]['Date'], date_format)
            
            # Format currency columns
            for col in [5, 6, 7, 8]:  # Subtotal, Tax, Discount, Total
                worksheet.write(row + 1, col, details_data[row][df.columns[col]], currency_format)
    
    def _create_items_sheet(self, writer, invoices, header_format, currency_format):
        """Create item-wise analysis"""
        items_data = []
        
        for invoice in invoices:
            for item in invoice.items:
                items_data.append({
                    'Invoice No': invoice.invoice_number,
                    'Date': invoice.invoice_date,
                    'Customer': invoice.customer_name,
                    'Product': item.item_name,
                    'Code': item.item_code,
                    'Quantity': item.quantity,
                    'Unit': item.unit,
                    'Rate': item.unit_price,
                    'Discount%': item.discount_percentage,
                    'Net Amount': item.net_amount,
                    'Tax': item.cgst_amount + item.sgst_amount + item.igst_amount + item.vat_amount,
                    'Total': item.total_amount
                })
        
        df = pd.DataFrame(items_data)
        df.to_excel(writer, sheet_name='Item Details', index=False)
        
        # Format the sheet
        worksheet = writer.sheets['Item Details']
        
        # Apply header format
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)
    
    def _create_customer_sheet(self, writer, invoices, header_format, currency_format):
        """Create customer-wise summary"""
        customer_data = {}
        
        for invoice in invoices:
            customer = invoice.customer_name
            if customer not in customer_data:
                customer_data[customer] = {
                    'invoices': 0,
                    'total_amount': 0,
                    'total_items': 0,
                    'first_purchase': invoice.invoice_date,
                    'last_purchase': invoice.invoice_date
                }
            
            customer_data[customer]['invoices'] += 1
            customer_data[customer]['total_amount'] += invoice.total_amount
            customer_data[customer]['total_items'] += len(invoice.items)
            
            if invoice.invoice_date < customer_data[customer]['first_purchase']:
                customer_data[customer]['first_purchase'] = invoice.invoice_date
            if invoice.invoice_date > customer_data[customer]['last_purchase']:
                customer_data[customer]['last_purchase'] = invoice.invoice_date
        
        # Convert to DataFrame
        customer_list = []
        for customer, data in customer_data.items():
            customer_list.append({
                'Customer': customer,
                'Total Invoices': data['invoices'],
                'Total Amount': data['total_amount'],
                'Avg Invoice Value': data['total_amount'] / data['invoices'],
                'Total Items': data['total_items'],
                'First Purchase': data['first_purchase'],
                'Last Purchase': data['last_purchase']
            })
        
        df = pd.DataFrame(customer_list)
        df = df.sort_values('Total Amount', ascending=False)
        df.to_excel(writer, sheet_name='Customer Analysis', index=False)
        
        # Format the sheet
        worksheet = writer.sheets['Customer Analysis']
        
        # Apply header format
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)
    
    def _create_tax_sheet(self, writer, invoices, header_format, currency_format):
        """Create tax summary sheet"""
        tax_data = []
        
        for invoice in invoices:
            if invoice.invoice_type == 'gst':
                tax_data.append({
                    'Invoice No': invoice.invoice_number,
                    'Date': invoice.invoice_date,
                    'Customer': invoice.customer_name,
                    'GSTIN': invoice.customer_tax_number,
                    'Taxable Amount': invoice.subtotal,
                    'CGST': invoice.cgst_amount,
                    'SGST': invoice.sgst_amount,
                    'IGST': invoice.igst_amount,
                    'Total Tax': invoice.tax_amount,
                    'Total Amount': invoice.total_amount
                })
            elif invoice.invoice_type == 'vat':
                tax_data.append({
                    'Invoice No': invoice.invoice_number,
                    'Date': invoice.invoice_date,
                    'Customer': invoice.customer_name,
                    'VAT No': invoice.customer_tax_number,
                    'Taxable Amount': invoice.subtotal,
                    'VAT': invoice.tax_amount,
                    'Total Amount': invoice.total_amount
                })
        
        if tax_data:
            df = pd.DataFrame(tax_data)
            df.to_excel(writer, sheet_name='Tax Summary', index=False)
            
            # Format the sheet
            worksheet = writer.sheets['Tax Summary']
            
            # Apply header format
            for col_num, value in enumerate(df.columns.values):
                worksheet.write(0, col_num, value, header_format)
    
    def export_single_invoice(self, invoice, filename=None):
        """Export a single invoice to Excel"""
        if not filename:
            filename = f"invoice_{invoice.invoice_number}.xlsx"
        
        filepath = os.path.join(Config.EXPORT_FOLDER, filename)
        
        with pd.ExcelWriter(filepath, engine='xlsxwriter') as writer:
            # Invoice header data
            header_data = {
                'Field': ['Invoice Number', 'Date', 'Customer', 'Address', 'Phone', 'Tax Number'],
                'Value': [
                    invoice.invoice_number,
                    invoice.invoice_date.strftime('%d/%m/%Y'),
                    invoice.customer_name,
                    invoice.customer_address,
                    invoice.customer_phone,
                    invoice.customer_tax_number or 'N/A'
                ]
            }
            
            # Write header
            df_header = pd.DataFrame(header_data)
            df_header.to_excel(writer, sheet_name='Invoice', index=False, startrow=0)
            
            # Items data
            items_data = []
            for item in invoice.items:
                items_data.append({
                    'Item': item.item_name,
                    'HSN/Code': item.hsn_sac_code or item.item_code,
                    'Quantity': item.quantity,
                    'Unit': item.unit,
                    'Rate': item.unit_price,
                    'Amount': item.net_amount,
                    'Tax': item.cgst_amount + item.sgst_amount + item.igst_amount + item.vat_amount,
                    'Total': item.total_amount
                })
            
            # Write items
            df_items = pd.DataFrame(items_data)
            df_items.to_excel(writer, sheet_name='Invoice', index=False, startrow=10)
            
            # Summary
            summary_row = len(items_data) + 12
            summary_data = {
                'Field': ['Subtotal', 'Tax', 'Total'],
                'Value': [invoice.subtotal, invoice.tax_amount, invoice.total_amount]
            }
            
            df_summary = pd.DataFrame(summary_data)
            df_summary.to_excel(writer, sheet_name='Invoice', index=False, startrow=summary_row)
        
        return filepath 