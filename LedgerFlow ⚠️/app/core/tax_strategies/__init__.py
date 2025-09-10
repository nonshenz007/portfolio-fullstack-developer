"""
Tax Strategy Pattern System

This module implements a pluggable tax calculation system using the Strategy pattern.
It supports GST (India), VAT (Bahrain), and NoTax strategies with plugin discovery.

Requirements addressed:
- FR-2: Pluggable tax rules for new countries
- NFR Internationalization: Support for different tax systems
"""

from .base import TaxStrategy, TaxContext, TaxResult, InvoiceItem, TaxCalculationException
from .factory import TaxStrategyFactory
from .gst_strategy import GSTStrategy
from .vat_strategy import VATStrategy
from .no_tax_strategy import NoTaxStrategy

__all__ = [
    'TaxStrategy',
    'TaxContext', 
    'TaxResult',
    'InvoiceItem',
    'TaxCalculationException',
    'TaxStrategyFactory',
    'GSTStrategy',
    'VATStrategy',
    'NoTaxStrategy'
]