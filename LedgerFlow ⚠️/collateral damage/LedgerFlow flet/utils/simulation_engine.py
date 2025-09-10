import asyncio
import hashlib
import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from utils.invoice_generator import generate_plain_invoices

@dataclass
class SimulationParams:
    """Parameters for invoice simulation"""
    revenue_target: float
    start_date: str
    end_date: str
    business_style: str
    template_type: str
    catalog_file: Optional[str] = None
    max_invoices_per_day: int = 15
    min_invoice_amount: float = 100
    max_invoice_amount: float = 10000
    tax_style: str = "Randomized"  # Fixed, Randomized, Market Pattern
    sku_distribution: str = "Weighted"  # Weighted, Uniform
    price_rounding: int = 1  # ₹1, ₹10, ₹50
    test_mode: bool = False

@dataclass 
class VerificationResult:
    """Results of invoice verification"""
    revenue_match_score: float
    tax_validation_pass: bool
    template_conformity_pass: bool
    distribution_realism_score: float
    overall_score: float
    
    def is_export_ready(self) -> bool:
        return self.overall_score >= 85.0

class SimulationEngine:
    """Async-safe invoice simulation engine with verification"""
    
    def __init__(self):
        self.simulation_results: List[Dict] = []
        self.verification_result: Optional[VerificationResult] = None
        self.is_running = False
        self.catalog_items = self._load_default_catalog()
        
    def _load_default_catalog(self) -> List[Dict]:
        """Load default product catalog"""
        return [
            {"name": "Crocin 500mg", "category": "Medical", "price_range": [15, 45]},
            {"name": "Basmati Rice 5kg", "category": "Grocery", "price_range": [200, 400]},
            {"name": "Cotton Saree", "category": "Textile", "price_range": [800, 2500]},
            {"name": "Mobile Phone", "category": "Electronics", "price_range": [8000, 25000]},
            {"name": "Office Supplies", "category": "Stationery", "price_range": [50, 300]}
        ]
    
    async def run_simulation(self, params: SimulationParams) -> Tuple[List[Dict], VerificationResult]:
        """
        Run invoice simulation asynchronously
        
        Args:
            params: Simulation parameters
            
        Returns:
            Tuple of (invoices, verification_result)
        """
        if self.is_running:
            raise RuntimeError("Simulation already in progress")
            
        self.is_running = True
        
        try:
            # Run simulation in executor to avoid blocking
            loop = asyncio.get_event_loop()
            invoices = await loop.run_in_executor(
                None, 
                self._generate_invoices_sync, 
                params
            )
            
            # Run verification
            verification = await self._verify_invoices(invoices, params)
            
            self.simulation_results = invoices
            self.verification_result = verification
            
            return invoices, verification
            
        finally:
            self.is_running = False
    
    def _generate_invoices_sync(self, params: SimulationParams) -> List[Dict]:
        """Synchronous invoice generation (runs in executor)"""
        try:
            invoices = generate_plain_invoices(
                revenue_target=params.revenue_target,
                start_date=params.start_date,
                end_date=params.end_date,
                business_style=params.business_style,
                template_type=params.template_type
            )
            
            # Apply advanced parameters
            invoices = self._apply_advanced_params(invoices, params)
            
            # Add VeriChain hashes
            invoices = self._add_verichain_hashes(invoices)
            
            return invoices
            
        except Exception as e:
            print(f"Invoice generation error: {e}")
            return []
    
    def _apply_advanced_params(self, invoices: List[Dict], params: SimulationParams) -> List[Dict]:
        """Apply advanced simulation parameters"""
        for invoice in invoices:
            # Apply price rounding
            for item in invoice.get("items", []):
                rate = item.get("rate", 0)
                rounded_rate = self._round_price(rate, params.price_rounding)
                item["rate"] = rounded_rate
                item["amount"] = item["qty"] * rounded_rate
            
            # Recalculate totals
            self._recalculate_invoice_totals(invoice, params.template_type)
            
        return invoices
    
    def _round_price(self, price: float, rounding: int) -> float:
        """Round price to specified increment"""
        if rounding == 1:
            return round(price, 2)
        elif rounding == 10:
            return round(price / 10) * 10
        elif rounding == 50:
            return round(price / 50) * 50
        return price
    
    def _recalculate_invoice_totals(self, invoice: Dict, template_type: str):
        """Recalculate invoice totals after modifications"""
        items = invoice.get("items", [])
        subtotal = sum(item.get("amount", 0) for item in items)
        invoice["subtotal"] = round(subtotal, 2)
        
        if template_type == "GST":
            total_gst = sum(item.get("total_gst", 0) for item in items)
            invoice["grand_total"] = round(subtotal + total_gst, 2)
        elif template_type == "VAT":
            total_vat = sum(item.get("vat_amount", 0) for item in items)
            invoice["grand_total"] = round(subtotal + total_vat, 2)
        else:
            invoice["grand_total"] = subtotal
            
        invoice["total"] = invoice["grand_total"]
    
    def _add_verichain_hashes(self, invoices: List[Dict]) -> List[Dict]:
        """Add VeriChain audit trail hashes"""
        previous_hash = "0" * 64  # Genesis hash
        
        for invoice in invoices:
            # Create hash input
            hash_input = f"{invoice['invoice_number']}{invoice['date']}{invoice['total']}{invoice['template_type']}{previous_hash}"
            
            # Generate SHA-256 hash
            current_hash = hashlib.sha256(hash_input.encode()).hexdigest()
            
            invoice["verichain_hash"] = current_hash
            invoice["previous_hash"] = previous_hash
            
            previous_hash = current_hash
            
        return invoices
    
    async def _verify_invoices(self, invoices: List[Dict], params: SimulationParams) -> VerificationResult:
        """Verify generated invoices against parameters"""
        if not invoices:
            return VerificationResult(0, False, False, 0, 0)
        
        # Revenue target match
        total_revenue = sum(inv.get("total", 0) for inv in invoices)
        revenue_variance = abs(total_revenue - params.revenue_target) / params.revenue_target
        revenue_match_score = max(0, 100 * (1 - revenue_variance))
        
        # Tax validation
        tax_validation_pass = await self._validate_tax_calculations(invoices, params.template_type)
        
        # Template conformity
        template_conformity_pass = await self._validate_template_conformity(invoices, params.template_type)
        
        # Distribution realism
        distribution_score = await self._calculate_distribution_realism(invoices)
        
        # Calculate overall score
        overall_score = (
            revenue_match_score * 0.3 +
            (100 if tax_validation_pass else 0) * 0.25 +
            (100 if template_conformity_pass else 0) * 0.25 +
            distribution_score * 0.2
        )
        
        return VerificationResult(
            revenue_match_score=round(revenue_match_score, 1),
            tax_validation_pass=tax_validation_pass,
            template_conformity_pass=template_conformity_pass,
            distribution_realism_score=round(distribution_score, 1),
            overall_score=round(overall_score, 1)
        )
    
    async def _validate_tax_calculations(self, invoices: List[Dict], template_type: str) -> bool:
        """Validate tax calculations are correct"""
        for invoice in invoices:
            if template_type == "GST":
                # Check GST calculations
                total_gst = invoice.get("total_gst", 0)
                calculated_gst = sum(item.get("total_gst", 0) for item in invoice.get("items", []))
                if abs(total_gst - calculated_gst) > 0.01:
                    return False
                    
            elif template_type == "VAT":
                # Check VAT calculations
                total_vat = invoice.get("total_vat", 0)
                calculated_vat = sum(item.get("vat_amount", 0) for item in invoice.get("items", []))
                if abs(total_vat - calculated_vat) > 0.01:
                    return False
        
        return True
    
    async def _validate_template_conformity(self, invoices: List[Dict], template_type: str) -> bool:
        """Validate invoices conform to template requirements"""
        required_fields = {
            "Plain": ["invoice_number", "date", "customer_name", "items", "total"],
            "GST": ["invoice_number", "date", "customer_name", "items", "total_gst", "gstin"],
            "VAT": ["invoice_number", "date", "customer_name", "items", "total_vat", "vat_reg_number"]
        }
        
        fields_to_check = required_fields.get(template_type, required_fields["Plain"])
        
        for invoice in invoices:
            for field in fields_to_check:
                if field not in invoice or invoice[field] is None:
                    return False
                    
            # Check template_type field matches
            if invoice.get("template_type") != template_type:
                return False
        
        return True
    
    async def _calculate_distribution_realism(self, invoices: List[Dict]) -> float:
        """Calculate how realistic the invoice distribution is"""
        if len(invoices) < 3:
            return 50.0  # Not enough data
        
        # Check date distribution
        dates = [inv.get("date") for inv in invoices]
        unique_dates = len(set(dates))
        date_diversity = (unique_dates / len(dates)) * 100
        
        # Check amount distribution (should not be too uniform)
        amounts = [inv.get("total", 0) for inv in invoices]
        amount_variance = self._calculate_variance(amounts)
        
        # Check customer distribution  
        customers = [inv.get("customer_name") for inv in invoices]
        unique_customers = len(set(customers))
        customer_diversity = min((unique_customers / len(customers)) * 100, 100)
        
        # Combine scores
        realism_score = (date_diversity * 0.3 + amount_variance * 0.4 + customer_diversity * 0.3)
        return min(realism_score, 100.0)
    
    def _calculate_variance(self, values: List[float]) -> float:
        """Calculate variance score for realism (0-100)"""
        if len(values) < 2:
            return 50.0
            
        mean_val = sum(values) / len(values)
        variance = sum((x - mean_val) ** 2 for x in values) / len(values)
        std_dev = variance ** 0.5
        
        # Convert to 0-100 score (higher variance = more realistic)
        coefficient_of_variation = (std_dev / mean_val) if mean_val > 0 else 0
        return min(coefficient_of_variation * 200, 100)  # Scale to 0-100
    
    def get_sample_invoices(self, count: int = 3) -> List[Dict]:
        """Get sample invoices for preview"""
        if not self.simulation_results:
            return []
        return random.sample(self.simulation_results, min(count, len(self.simulation_results)))
    
    def export_config_snapshot(self, params: SimulationParams) -> Dict:
        """Export current configuration as snapshot"""
        return {
            "timestamp": datetime.now().isoformat(),
            "parameters": {
                "revenue_target": params.revenue_target,
                "start_date": params.start_date,
                "end_date": params.end_date,
                "business_style": params.business_style,
                "template_type": params.template_type,
                "max_invoices_per_day": params.max_invoices_per_day,
                "tax_style": params.tax_style,
                "sku_distribution": params.sku_distribution,
                "price_rounding": params.price_rounding
            },
            "results_summary": {
                "total_invoices": len(self.simulation_results),
                "total_revenue": sum(inv.get("total", 0) for inv in self.simulation_results),
                "verification_score": self.verification_result.overall_score if self.verification_result else 0
            }
        }

# Global instance
simulation_engine = SimulationEngine() 