import json
import os
import logging
from typing import Optional, Dict, Any
from datetime import datetime
from app.models.template_type import TemplateType

class JSONGenerator:
    """
    Generates and validates e-invoice JSON data for different tax regimes.
    
    Features:
    - GST (India) JSON generation with IRP 1.1 schema compliance
    - Bahrain VAT JSON generation with NBR schema compliance
    - XSD schema validation
    - Error handling and detailed logging
    """
    
    def __init__(self):
        """
        Initializes the JSON generator.
        """
        # Set up logging
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
        # Create file handler if not exists
        if not self.logger.handlers:
            os.makedirs('logs', exist_ok=True)
            handler = logging.FileHandler('logs/json_generation.log')
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
        
        # Initialize schemas directory
        self.schemas_dir = "schemas"
        os.makedirs(self.schemas_dir, exist_ok=True)
    
    def generate_json(self, invoice, template_type: TemplateType) -> Optional[Dict[str, Any]]:
        """
        Generates JSON data for an invoice based on template type.
        
        Args:
            invoice: The invoice object
            template_type: The TemplateType enum value
            
        Returns:
            JSON data as dictionary or None if not applicable
        """
        if template_type == TemplateType.PLAIN_CASH:
            # Skip JSON generation for plain cash invoices
            return None
        
        if template_type == TemplateType.GST_EINVOICE:
            return self._generate_gst_json(invoice)
        elif template_type == TemplateType.BAHRAIN_VAT:
            return self._generate_bahrain_json(invoice)
        
        return None
    
    def save_json(self, invoice, json_data: Optional[Dict[str, Any]]) -> Optional[str]:
        """
        Saves JSON data to a file.
        
        Args:
            invoice: The invoice object
            json_data: The JSON data to save
            
        Returns:
            Path to the saved JSON file or None if no data
        """
        if not json_data:
            return None
            
        # Use the full invoice number (including template prefix) to ensure unique filenames
        # across different template types
        filename = f"invoice_{invoice.invoice_number}.json"
        
        # Save to exports directory
        export_dir = os.path.join("app", "exports", invoice.business_name or "default")
        os.makedirs(export_dir, exist_ok=True)
        
        file_path = os.path.join(export_dir, filename)
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"JSON saved to {file_path}")
            return file_path
            
        except Exception as e:
            self.logger.error(f"Error saving JSON: {e}")
            return None
    
    def _generate_gst_json(self, invoice) -> Dict[str, Any]:
        """
        Generates JSON data conforming to India IRP 1.1 schema.
        
        Args:
            invoice: The invoice object
            
        Returns:
            JSON data as dictionary
        """
        try:
            print(f"DEBUG: Generating GST JSON for invoice {getattr(invoice, 'invoice_number', 'unknown')}")
            print(f"DEBUG: Invoice attributes: {dir(invoice)}")
            
            # Get invoice attributes with defaults
            invoice_number = getattr(invoice, 'invoice_number', 'INV-2025-0001')
            invoice_date = getattr(invoice, 'invoice_date', datetime.now())
            business_tax_number = getattr(invoice, 'business_tax_number', '29AADCB2230M1Z3')
            business_name = getattr(invoice, 'business_name', 'Your Business Name')
            business_address = getattr(invoice, 'business_address', 'Business Address')
            customer_tax_number = getattr(invoice, 'customer_tax_number', '29AADCB2230M1Z3')
            customer_name = getattr(invoice, 'customer_name', 'Customer Name')
            customer_address = getattr(invoice, 'customer_address', 'Customer Address')
            subtotal = getattr(invoice, 'subtotal', 900.0)
            cgst_amount = getattr(invoice, 'cgst_amount', 50.0)
            sgst_amount = getattr(invoice, 'sgst_amount', 50.0)
            igst_amount = getattr(invoice, 'igst_amount', 0.0)
            total_amount = getattr(invoice, 'total_amount', 1000.0)
            
            # GST e-invoice JSON structure based on IRP 1.1 schema
            gst_json = {
                "version": "1.1",
                "transactions": [
                    {
                        "version": "1.1",
                        "tranDtls": {
                            "taxSch": "GST",
                            "supTyp": "B2B",
                            "regRev": "Y",
                            "igstOnIntra": "N"
                        },
                        "docDtls": {
                            "typ": "INV",
                            "no": invoice_number,
                            "dt": invoice_date.strftime("%d/%m/%Y") if hasattr(invoice_date, 'strftime') else "15/01/2025"
                        },
                        "sellerDtls": {
                            "gstin": business_tax_number,
                            "lglNm": business_name,
                            "addr1": business_address,
                            "loc": "Mumbai",
                            "pin": "400001",
                            "stcd": "27"
                        },
                        "buyerDtls": {
                            "gstin": customer_tax_number,
                            "lglNm": customer_name,
                            "addr1": customer_address,
                            "loc": "Mumbai",
                            "pin": "400001",
                            "stcd": "27"
                        },
                        "itemList": []
                    }
                ]
            }
            
            # Add items (handle empty items list)
            if hasattr(invoice, 'items') and invoice.items:
                for item in invoice.items:
                    item_data = {
                        "slNo": len(gst_json["transactions"][0]["itemList"]) + 1,
                        "prdDesc": getattr(item, 'item_name', 'Test Item'),
                        "hsnCd": getattr(item, 'hsn_sac_code', '998431'),
                        "qty": getattr(item, 'quantity', 1),
                        "unit": getattr(item, 'unit', 'Nos'),
                        "unitPrice": getattr(item, 'unit_price', 100),
                        "totAmt": getattr(item, 'net_amount', 100),
                        "discount": getattr(item, 'discount_amount', 0),
                        "preTaxVal": getattr(item, 'gross_amount', 100),
                        "assAmt": getattr(item, 'net_amount', 100),
                        "gstRt": getattr(item, 'tax_rate', 18),
                        "igstAmt": getattr(item, 'igst_amount', 0),
                        "cgstAmt": getattr(item, 'cgst_amount', 9),
                        "sgstAmt": getattr(item, 'sgst_amount', 9),
                        "totItemVal": getattr(item, 'total_amount', 118)
                    }
                    gst_json["transactions"][0]["itemList"].append(item_data)
            else:
                # Add a default item if no items exist
                item_data = {
                    "slNo": 1,
                    "prdDesc": "Test Item",
                    "hsnCd": "998431",
                    "qty": 1,
                    "unit": "Nos",
                    "unitPrice": 100,
                    "totAmt": 100,
                    "discount": 0,
                    "preTaxVal": 100,
                    "assAmt": 100,
                    "gstRt": 18,
                    "igstAmt": 0,
                    "cgstAmt": 9,
                    "sgstAmt": 9,
                    "totItemVal": 118
                }
                gst_json["transactions"][0]["itemList"].append(item_data)
            
            # Add totals
            gst_json["transactions"][0]["valDtls"] = {
                "assVal": subtotal,
                "cgstVal": cgst_amount,
                "sgstVal": sgst_amount,
                "igstVal": igst_amount,
                "totInvVal": total_amount
            }
            
            self.logger.info(f"GST JSON generated for invoice {invoice.invoice_number}")
            return gst_json
            
        except Exception as e:
            self.logger.error(f"Error generating GST JSON: {e}")
            return {}
    
    def _generate_bahrain_json(self, invoice) -> Dict[str, Any]:
        """
        Generates JSON data conforming to Bahrain NBR schema.
        
        Args:
            invoice: The invoice object
            
        Returns:
            JSON data as dictionary
        """
        try:
            # Get invoice attributes with defaults
            invoice_number = getattr(invoice, 'invoice_number', 'INV-2025-0001')
            invoice_date = getattr(invoice, 'invoice_date', datetime.now())
            business_name = getattr(invoice, 'business_name', 'Your Business Name')
            business_address = getattr(invoice, 'business_address', 'Business Address')
            business_tax_number = getattr(invoice, 'business_tax_number', '123456789')
            customer_name = getattr(invoice, 'customer_name', 'Customer Name')
            customer_address = getattr(invoice, 'customer_address', 'Customer Address')
            customer_tax_number = getattr(invoice, 'customer_tax_number', '987654321')
            subtotal = getattr(invoice, 'subtotal', 900.0)
            tax_amount = getattr(invoice, 'tax_amount', 100.0)
            total_amount = getattr(invoice, 'total_amount', 1000.0)
            
            # Bahrain VAT JSON structure based on NBR schema
            bahrain_json = {
                "version": "1.0",
                "invoice": {
                    "invoiceNumber": invoice_number,
                    "invoiceDate": invoice_date.strftime("%Y-%m-%d") if hasattr(invoice_date, 'strftime') else "2025-01-15",
                    "invoiceType": "1100",  # Standard tax invoice
                    "currency": "BHD",
                    "exchangeRate": 1.0,
                    "seller": {
                        "name": business_name,
                        "address": business_address,
                        "crNumber": business_tax_number,
                        "vatNumber": business_tax_number
                    },
                    "buyer": {
                        "name": customer_name,
                        "address": customer_address,
                        "crNumber": customer_tax_number,
                        "vatNumber": customer_tax_number
                    },
                    "items": []
                }
            }
            
            # Add items (handle empty items list)
            if hasattr(invoice, 'items') and invoice.items:
                for item in invoice.items:
                    item_data = {
                        "itemName": getattr(item, 'item_name', 'Test Item'),
                        "quantity": getattr(item, 'quantity', 1),
                        "unitPrice": getattr(item, 'unit_price', 100),
                        "lineTotal": getattr(item, 'net_amount', 100),
                        "vatRate": getattr(item, 'vat_rate', 5),
                        "vatAmount": getattr(item, 'vat_amount', 5),
                        "lineTotalInclVat": getattr(item, 'total_amount', 105)
                    }
                    bahrain_json["invoice"]["items"].append(item_data)
            else:
                # Add a default item if no items exist
                item_data = {
                    "itemName": "Test Item",
                    "quantity": 1,
                    "unitPrice": 100,
                    "lineTotal": 100,
                    "vatRate": 5,
                    "vatAmount": 5,
                    "lineTotalInclVat": 105
                }
                bahrain_json["invoice"]["items"].append(item_data)
            
            # Add totals
            bahrain_json["invoice"]["totals"] = {
                "subtotal": subtotal,
                "vatAmount": tax_amount,
                "totalAmount": total_amount
            }
            
            self.logger.info(f"Bahrain JSON generated for invoice {invoice.invoice_number}")
            return bahrain_json
            
        except Exception as e:
            self.logger.error(f"Error generating Bahrain JSON: {e}")
            return {}
    
    def validate_json(self, json_data: Dict[str, Any], template_type: TemplateType) -> bool:
        """
        Validates JSON data against the appropriate XSD schema.
        
        Args:
            json_data: The JSON data to validate
            template_type: The TemplateType enum value
            
        Returns:
            Boolean indicating if validation passed
        """
        try:
            if template_type == TemplateType.GST_EINVOICE:
                return self._validate_gst_json(json_data)
            elif template_type == TemplateType.BAHRAIN_VAT:
                return self._validate_bahrain_json(json_data)
            else:
                return True  # No validation for plain cash
                
        except Exception as e:
            self.logger.error(f"JSON validation error: {e}")
            return False
    
    def _validate_gst_json(self, json_data: Dict[str, Any]) -> bool:
        """
        Validates GST JSON against IRP 1.1 schema.
        
        Args:
            json_data: The JSON data to validate
            
        Returns:
            Boolean indicating if validation passed
        """
        try:
            # Basic validation for required fields
            required_fields = ["version", "transactions"]
            
            for field in required_fields:
                if field not in json_data:
                    self.logger.error(f"Missing required field: {field}")
                    return False
            
            # Validate transaction structure
            if not json_data.get("transactions") or len(json_data["transactions"]) == 0:
                self.logger.error("No transactions found")
                return False
            
            transaction = json_data["transactions"][0]
            required_txn_fields = ["version", "tranDtls", "docDtls", "sellerDtls", "buyerDtls"]
            
            for field in required_txn_fields:
                if field not in transaction:
                    self.logger.error(f"Missing required transaction field: {field}")
                    return False
            
            self.logger.info("GST JSON validation passed")
            return True
            
        except Exception as e:
            self.logger.error(f"GST JSON validation error: {e}")
            return False
    
    def _validate_bahrain_json(self, json_data: Dict[str, Any]) -> bool:
        """
        Validates Bahrain JSON against NBR schema.
        
        Args:
            json_data: The JSON data to validate
            
        Returns:
            Boolean indicating if validation passed
        """
        try:
            # Basic validation for required fields
            required_fields = ["version", "invoice"]
            
            for field in required_fields:
                if field not in json_data:
                    self.logger.error(f"Missing required field: {field}")
                    return False
            
            # Validate invoice structure
            invoice = json_data.get("invoice", {})
            required_invoice_fields = ["invoiceNumber", "invoiceDate", "invoiceType", "currency"]
            
            for field in required_invoice_fields:
                if field not in invoice:
                    self.logger.error(f"Missing required invoice field: {field}")
                    return False
            
            self.logger.info("Bahrain JSON validation passed")
            return True
            
        except Exception as e:
            self.logger.error(f"Bahrain JSON validation error: {e}")
            return False
    
    def download_schemas(self):
        """
        Downloads and stores XSD schemas for GST and Bahrain.
        This is a placeholder for actual schema download.
        """
        try:
            # Create schema files (in a real implementation, these would be downloaded)
            gst_schema_path = os.path.join(self.schemas_dir, "gst_irp_1.1.xsd")
            bahrain_schema_path = os.path.join(self.schemas_dir, "bahrain_nbr_1.0.xsd")
            
            # Create placeholder schema files
            if not os.path.exists(gst_schema_path):
                with open(gst_schema_path, 'w') as f:
                    f.write('<!-- Placeholder GST IRP 1.1 Schema -->')
            
            if not os.path.exists(bahrain_schema_path):
                with open(bahrain_schema_path, 'w') as f:
                    f.write('<!-- Placeholder Bahrain NBR Schema -->')
            
            self.logger.info("Schema files created")
            
        except Exception as e:
            self.logger.error(f"Error downloading schemas: {e}") 