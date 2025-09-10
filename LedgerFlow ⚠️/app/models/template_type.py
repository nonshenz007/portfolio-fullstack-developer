from enum import Enum

class TemplateType(Enum):
    """
    Enum for invoice template types.
    
    Values:
    - GST_EINVOICE: GST e-Invoice template for India
    - BAHRAIN_VAT: VAT invoice template for Bahrain
    - PLAIN_CASH: Plain cash invoice template
    """
    GST_EINVOICE = "gst_einvoice"
    BAHRAIN_VAT = "bahrain_vat"
    PLAIN_CASH = "plain_cash"
    
    @classmethod
    def from_invoice_type(cls, invoice_type):
        """
        Convert legacy invoice_type string to TemplateType enum.
        
        Args:
            invoice_type: String value ('gst', 'vat', 'cash')
            
        Returns:
            TemplateType enum value
        """
        mapping = {
            'gst': cls.GST_EINVOICE,
            'vat': cls.BAHRAIN_VAT,
            'cash': cls.PLAIN_CASH
        }
        return mapping.get(invoice_type.lower(), cls.GST_EINVOICE)
    
    @classmethod
    def to_invoice_type(cls, template_type):
        """
        Convert TemplateType enum to legacy invoice_type string.
        
        Args:
            template_type: TemplateType enum value
            
        Returns:
            String value ('gst', 'vat', 'cash')
        """
        mapping = {
            cls.GST_EINVOICE: 'gst',
            cls.BAHRAIN_VAT: 'vat',
            cls.PLAIN_CASH: 'cash'
        }
        return mapping.get(template_type, 'gst')