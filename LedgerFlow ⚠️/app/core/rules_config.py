from __future__ import annotations

from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
from pathlib import Path
import yaml


class InvoicePatterns(BaseModel):
    """Invoice number patterns by country and type"""
    India: Dict[str, str] = Field(default_factory=dict)
    Bahrain: Dict[str, str] = Field(default_factory=dict)


class TemplateRequirements(BaseModel):
    """Template-specific field requirements"""
    required_fields: List[str]
    currency: str
    tax_structure: str
    compliance_level: str


class BusinessRules(BaseModel):
    """Business rules and constraints"""
    max_invoice_amount: float = 10000000
    max_items_per_invoice: int = 50
    min_invoice_amount: float = 0.01
    max_discount_percentage: float = 50
    future_date_tolerance_days: int = 0
    past_date_tolerance_days: int = 365


class TaxTolerances(BaseModel):
    """Tax calculation tolerances"""
    tax_calculation: float = 2.0
    cgst_sgst: float = 1.0
    igst: float = 1.0
    vat: float = 1.0
    invoice_tax_total: float = 2.0


class ComplianceScoring(BaseModel):
    """Compliance scoring weights"""
    critical_error_penalty: int = 20
    warning_penalty: int = 5
    base_score: int = 100


class RiskLevels(BaseModel):
    """Risk level thresholds"""
    critical_threshold: int = 0
    high_threshold: int = 70
    medium_threshold: int = 85
    low_threshold: int = 100


class BusinessStyleExpectations(BaseModel):
    """Business style expectations"""
    min_items: int
    max_items: int
    min_amount: float
    max_amount: float


class GstPatterns(BaseModel):
    """GST number validation patterns"""
    business_gst: str
    customer_gst: str


class HsnPatterns(BaseModel):
    """HSN code validation"""
    basic: str
    high_value_threshold: float


class SampleInvoiceNumbers(BaseModel):
    """Sample invoice numbers for error messages"""
    gst: str
    vat: str
    cash: str
    plain: str


class RulesConfig(BaseModel):
    """Complete verification rules configuration"""
    invoice_patterns: InvoicePatterns
    template_requirements: Dict[str, TemplateRequirements]
    business_rules: BusinessRules
    tax_tolerances: TaxTolerances
    compliance_scoring: ComplianceScoring
    risk_levels: RiskLevels
    business_style_expectations: Dict[str, BusinessStyleExpectations]
    gst_patterns: GstPatterns
    hsn_patterns: HsnPatterns
    sample_invoice_numbers: SampleInvoiceNumbers
    required_fields: List[str]
    required_item_fields: List[str]
    severity_levels: List[str]
    risk_levels_list: List[str]

    @classmethod
    def load_from_yaml(cls, yaml_path: str | Path) -> RulesConfig:
        """Load configuration from YAML file"""
        yaml_path = Path(yaml_path)
        if not yaml_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {yaml_path}")
        
        with open(yaml_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        return cls(**data)

    def get_invoice_pattern(self, country: str, invoice_type: str) -> Optional[str]:
        """Get invoice pattern for country and type"""
        country_patterns = getattr(self.invoice_patterns, country, {})
        return country_patterns.get(invoice_type)

    def get_template_requirements(self, template_type: str) -> Optional[TemplateRequirements]:
        """Get template requirements for template type"""
        return self.template_requirements.get(template_type)

    def get_business_style_expectations(self, business_style: str) -> Optional[BusinessStyleExpectations]:
        """Get business style expectations"""
        return self.business_style_expectations.get(business_style)

    def get_sample_invoice_number(self, invoice_type: str) -> str:
        """Get sample invoice number for invoice type"""
        return getattr(self.sample_invoice_numbers, invoice_type, "INV-2025-000001") 