"""
Custom exceptions for LedgerFlow system hardening
"""

class LedgerFlowException(Exception):
    """Base exception for all LedgerFlow errors"""
    pass

class RetryableException(LedgerFlowException):
    """Exception that should trigger retry logic"""
    pass

class InvoiceNumberCollisionException(RetryableException):
    """Invoice number collision detected - should trigger retry"""
    def __init__(self, invoice_number: str, tenant_id: str = None):
        self.invoice_number = invoice_number
        self.tenant_id = tenant_id
        message = f"Invoice number collision detected: {invoice_number}"
        if tenant_id:
            message += f" for tenant {tenant_id}"
        super().__init__(message)

class TaxCalculationException(LedgerFlowException):
    """Tax calculation error"""
    pass

class PDFGenerationException(RetryableException):
    """PDF generation failed"""
    pass

class ConfigurationException(LedgerFlowException):
    """Configuration validation error"""
    pass

class CircuitBreakerOpenException(LedgerFlowException):
    """Circuit breaker is open - service unavailable"""
    pass