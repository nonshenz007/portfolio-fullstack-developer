"""
Abstract base classes and data models for tax strategy system

This module defines the core interfaces and data structures for the tax strategy pattern.
All tax strategies must implement the TaxStrategy abstract base class.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal
from typing import Dict, List, Optional, Any
from datetime import datetime


@dataclass
class TaxContext:
    """
    Context information needed for tax calculations
    
    This class provides all the contextual information that tax strategies
    need to make accurate calculations, including customer location, business
    location, invoice date, and other relevant factors.
    """
    customer_state: str
    business_state: str
    invoice_date: datetime
    is_interstate: bool
    customer_type: str  # 'individual' or 'business'
    exemption_category: Optional[str] = None
    
    # Additional context for international support
    customer_country: str = 'India'
    business_country: str = 'India'
    currency: str = 'INR'
    
    # Business registration details
    business_tax_number: Optional[str] = None
    customer_tax_number: Optional[str] = None
    
    def __post_init__(self):
        """Validate context data"""
        if not self.customer_state or not self.business_state:
            raise ValueError("Customer and business states are required")
        
        if self.customer_type not in ['individual', 'business']:
            raise ValueError("Customer type must be 'individual' or 'business'")


@dataclass
class TaxResult:
    """
    Result of tax calculation with Decimal precision
    
    This class contains all tax calculation results with proper Decimal
    precision to avoid floating-point rounding errors.
    """
    # Basic amounts
    gross_amount: Decimal
    discount_amount: Decimal
    net_amount: Decimal
    total_tax: Decimal
    total_amount: Decimal
    
    # GST-specific breakdown
    cgst_amount: Decimal = Decimal('0.00')
    sgst_amount: Decimal = Decimal('0.00')
    igst_amount: Decimal = Decimal('0.00')
    
    # VAT-specific breakdown
    vat_amount: Decimal = Decimal('0.00')
    
    # Tax rates applied
    cgst_rate: Decimal = Decimal('0.00')
    sgst_rate: Decimal = Decimal('0.00')
    igst_rate: Decimal = Decimal('0.00')
    vat_rate: Decimal = Decimal('0.00')
    
    # Additional information
    is_exempt: bool = False
    exemption_reason: Optional[str] = None
    tax_breakdown: Dict[str, Decimal] = None
    
    def __post_init__(self):
        """Initialize tax_breakdown if not provided"""
        if self.tax_breakdown is None:
            self.tax_breakdown = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'gross_amount': str(self.gross_amount),
            'discount_amount': str(self.discount_amount),
            'net_amount': str(self.net_amount),
            'total_tax': str(self.total_tax),
            'total_amount': str(self.total_amount),
            'cgst_amount': str(self.cgst_amount),
            'sgst_amount': str(self.sgst_amount),
            'igst_amount': str(self.igst_amount),
            'vat_amount': str(self.vat_amount),
            'cgst_rate': str(self.cgst_rate),
            'sgst_rate': str(self.sgst_rate),
            'igst_rate': str(self.igst_rate),
            'vat_rate': str(self.vat_rate),
            'is_exempt': self.is_exempt,
            'exemption_reason': self.exemption_reason,
            'tax_breakdown': {k: str(v) for k, v in self.tax_breakdown.items()}
        }


@dataclass
class InvoiceItem:
    """
    Invoice item data for tax calculations
    
    This class represents a single line item on an invoice with all
    the information needed for tax calculations.
    """
    item_name: str
    quantity: Decimal
    unit_price: Decimal
    discount_percentage: Decimal = Decimal('0.00')
    discount_amount: Decimal = Decimal('0.00')
    
    # Product classification
    hsn_sac_code: Optional[str] = None
    product_category: Optional[str] = None
    
    # Tax rates (will be determined by strategy)
    tax_rate: Optional[Decimal] = None
    
    # Additional metadata
    unit: str = 'Nos'
    item_code: Optional[str] = None
    notes: Optional[str] = None
    
    def calculate_gross_amount(self) -> Decimal:
        """Calculate gross amount before discount"""
        return self.quantity * self.unit_price
    
    def calculate_discount_amount(self) -> Decimal:
        """Calculate discount amount"""
        if self.discount_amount > Decimal('0'):
            return self.discount_amount
        elif self.discount_percentage > Decimal('0'):
            gross = self.calculate_gross_amount()
            return gross * self.discount_percentage / Decimal('100')
        return Decimal('0.00')
    
    def calculate_net_amount(self) -> Decimal:
        """Calculate net amount after discount"""
        return self.calculate_gross_amount() - self.calculate_discount_amount()


class TaxStrategy(ABC):
    """
    Abstract base class for all tax calculation strategies
    
    This class defines the interface that all tax strategies must implement.
    Each strategy handles tax calculations for a specific tax system (GST, VAT, etc.).
    """
    
    @abstractmethod
    def calculate_tax(self, item: InvoiceItem, context: TaxContext) -> TaxResult:
        """
        Calculate tax for a single invoice item
        
        Args:
            item: Invoice item to calculate tax for
            context: Tax calculation context
            
        Returns:
            TaxResult with all calculated amounts and rates
            
        Raises:
            ValueError: If item or context data is invalid
            TaxCalculationException: If tax calculation fails
        """
        pass
    
    @abstractmethod
    def validate_tax_number(self, tax_number: str, context: TaxContext) -> bool:
        """
        Validate a tax registration number
        
        Args:
            tax_number: Tax number to validate
            context: Tax calculation context
            
        Returns:
            True if tax number is valid, False otherwise
        """
        pass
    
    @abstractmethod
    def get_tax_breakdown(self, items: List[InvoiceItem], context: TaxContext) -> Dict[str, Decimal]:
        """
        Get detailed tax breakdown for multiple items
        
        Args:
            items: List of invoice items
            context: Tax calculation context
            
        Returns:
            Dictionary with tax breakdown by category
        """
        pass
    
    @abstractmethod
    def get_applicable_tax_rate(self, item: InvoiceItem, context: TaxContext) -> Decimal:
        """
        Determine the applicable tax rate for an item
        
        Args:
            item: Invoice item
            context: Tax calculation context
            
        Returns:
            Applicable tax rate as Decimal
        """
        pass
    
    @abstractmethod
    def is_exempt(self, item: InvoiceItem, context: TaxContext) -> tuple[bool, Optional[str]]:
        """
        Check if an item is tax exempt
        
        Args:
            item: Invoice item
            context: Tax calculation context
            
        Returns:
            Tuple of (is_exempt, exemption_reason)
        """
        pass
    
    def get_strategy_name(self) -> str:
        """Get the name of this tax strategy"""
        return self.__class__.__name__
    
    def get_supported_countries(self) -> List[str]:
        """Get list of countries supported by this strategy"""
        return []
    
    def get_supported_currencies(self) -> List[str]:
        """Get list of currencies supported by this strategy"""
        return []


class TaxCalculationException(Exception):
    """Exception raised when tax calculation fails"""
    
    def __init__(self, message: str, item_name: str = None, context: TaxContext = None):
        super().__init__(message)
        self.item_name = item_name
        self.context = context
        self.message = message
    
    def __str__(self):
        if self.item_name:
            return f"Tax calculation failed for item '{self.item_name}': {self.message}"
        return f"Tax calculation failed: {self.message}"