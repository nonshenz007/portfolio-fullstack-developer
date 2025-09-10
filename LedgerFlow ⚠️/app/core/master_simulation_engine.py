import random
import secrets
import json
import uuid
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import numpy as np
from pathlib import Path
import os
from decimal import Decimal, ROUND_HALF_UP

def money(x):
    """Helper function to convert to Decimal and round to 2 decimal places"""
    if isinstance(x, Decimal):
        return x.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    return Decimal(str(x)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

from .timeflow_engine import TimeFlowEngine
from .gst_packager import GSTPackager, TaxCalculation
from .verification_engine import VerificationEngine, ValidationResult
from .customer_name_generator import CustomerNameGenerator, CustomerProfile
from .verichain_engine import VeriChainEngine
from .diagnostics_logger import DiagnosticsLogger
from .retry_handler import (
    BoundedRetryHandler, 
    CircuitBreaker, 
    RetryableException,
    PDFGenerationException,
    InvoiceGenerationException,
    NetworkException,
    RetryExhaustedException
)
from app.models import Invoice

@dataclass
class SimulationConfig:
    """Complete simulation configuration with all UI toggle parameters"""
    # Basic parameters
    invoice_count: int = 100
    date_range: Tuple[datetime, datetime] = None
    invoice_type: str = 'gst'  # 'gst', 'vat', 'cash'
    template_type: str = 'gst_einvoice'  # 'gst_einvoice', 'bahrain_vat', 'plain_cash'
    business_style: str = 'retail_shop'
    country: str = 'India'
    business_state: str = 'Maharashtra'
    
    # Business info parameters
    business_name: str = 'Your Company Name'
    business_address: str = 'Company Address'
    business_gst_number: str = ''
    business_vat_number: str = ''
    
    # UI Toggle parameters - CRITICAL FOR PRODUCTION
    timeflow_mode: str = 'realistic'  # 'realistic', 'compressed', 'extended'
    entropy_mode: str = 'smart'  # 'smart', 'random', 'structured'
    reality_buffer: int = 75  # 0-100%
    believability_stress: int = 50  # 0-100%
    excluded_products: List[str] = None
    most_sold_products: List[str] = None  # UI product selection control
    least_sold_products: List[str] = None  # UI product selection control
    invoice_spacing: str = 'natural'  # 'natural', 'uniform', 'clustered'
    docuflex_formatter: bool = True
    
    # Advanced realism parameters
    customer_repeat_rate: float = 0.3  # 0-1, how often customers return
    seasonal_variation: float = 0.2  # 0-1, seasonal business fluctuation
    customer_return_rate: float = 0.3  # 0-1, probability of return customers
    
    # Regional settings
    customer_region: str = 'generic_indian'  # 'generic_indian', 'south_muslim', 'bahrain_arabic'
    customer_type_mix: str = 'mixed'  # 'individual', 'business', 'mixed'
    
    # Business parameters
    min_items_per_invoice: int = 1
    max_items_per_invoice: int = 50
    min_invoice_amount: float = 10.0
    max_invoice_amount: float = 100000.0
    
    # Revenue targeting
    revenue_target: Optional[float] = None
    revenue_distribution: str = 'realistic'  # 'realistic', 'uniform', 'skewed'
    
    # Quality controls
    enable_verification: bool = True
    min_compliance_score: float = 85.0
    audit_risk: str = 'medium'  # 'low', 'medium', 'high' - matches UI parameter
    
    def __post_init__(self):
        """Validate configuration parameters"""
        if self.excluded_products is None:
            self.excluded_products = []
        if self.most_sold_products is None:
            self.most_sold_products = []
        if self.least_sold_products is None:
            self.least_sold_products = []
        
        # Validate ranges
        if not 0 <= self.reality_buffer <= 100:
            raise ValueError("reality_buffer must be between 0 and 100")
        
        if not 0 <= self.believability_stress <= 100:
            raise ValueError("believability_stress must be between 0 and 100")
        
        if not 0 <= self.customer_repeat_rate <= 1:
            raise ValueError("customer_repeat_rate must be between 0 and 1")
        
        if not 0 <= self.seasonal_variation <= 1:
            raise ValueError("seasonal_variation must be between 0 and 1")
        
        if not 0 <= self.customer_return_rate <= 1:
            raise ValueError("customer_return_rate must be between 0 and 1")
        
        if not 0 <= self.min_compliance_score <= 100:
            raise ValueError("min_compliance_score must be between 0 and 100")
        
        # Validate business parameters
        if self.min_invoice_amount < 0:
            raise ValueError("min_invoice_amount cannot be negative")
        
        if self.max_invoice_amount <= self.min_invoice_amount:
            raise ValueError("max_invoice_amount must be greater than min_invoice_amount")
        
        if self.min_items_per_invoice < 1:
            raise ValueError("min_items_per_invoice must be at least 1")
        
        if self.max_items_per_invoice < self.min_items_per_invoice:
            raise ValueError("max_items_per_invoice must be greater than or equal to min_items_per_invoice")

@dataclass
class SimulationResult:
    """Complete simulation result with resilience tracking"""
    config: SimulationConfig
    invoices: List[Dict[str, Any]]
    validation_results: List[ValidationResult]
    statistics: Dict[str, Any]
    execution_time: float
    batch_id: str
    success: bool
    error_message: Optional[str] = None
    # New fields for resilience tracking (FR-9)
    trace_id: Optional[str] = None
    retry_count: int = 0
    failed_invoices: List[Dict[str, Any]] = None
    partial_success: bool = False
    generation_metadata: Optional[Dict[str, Any]] = None

class MasterSimulationEngine:
    """
    Production-grade master simulation engine that enforces ALL UI parameters exactly.
    
    CRITICAL REQUIREMENTS:
    1. Generate EXACTLY the number of invoices requested
    2. Respect ALL date, amount, and item limits
    3. Create distinct formats for GST/VAT/Plain
    4. Enforce revenue targets precisely
    5. Generate government-grade realistic data
    """
    
    def __init__(self, config: SimulationConfig):
        self.config = config
        # Generate unique batch ID with microsecond precision and random component
        timestamp = datetime.now()
        microsecond = timestamp.microsecond
        random_suffix = secrets.token_hex(6)  # 12 character random string
        self.batch_id = f"LF_{timestamp.strftime('%Y%m%d_%H%M%S')}_{microsecond:06d}_{random_suffix}"
        self.trace_id = str(uuid.uuid4())  # Generate trace ID for request correlation (FR-9)
        self.diagnostics = DiagnosticsLogger()
        
        def generate_unique_batch_id(self) -> str:
            """Generate a unique batch ID with maximum uniqueness"""
            timestamp = datetime.now()
            microsecond = timestamp.microsecond
            nanosecond = timestamp.nanosecond if hasattr(timestamp, 'nanosecond') else 0
            random_suffix = secrets.token_hex(8)  # 16 character random string
            process_id = os.getpid()
            return f"LF_{timestamp.strftime('%Y%m%d_%H%M%S')}_{microsecond:06d}_{nanosecond:09d}_{process_id:05d}_{random_suffix}"
        
        def regenerate_batch_id(self) -> str:
            """Regenerate the batch ID with maximum uniqueness"""
            self.batch_id = self.generate_unique_batch_id()
            return self.batch_id
        
        # Initialize resilience components (FR-9)
        self.retry_handler = BoundedRetryHandler(max_attempts=3, base_delay=1.0)
        self.circuit_breaker = CircuitBreaker(failure_threshold=5, timeout=60)
        self.logger = logging.getLogger(__name__)
        
        # Initialize sub-engines
        self.timeflow_engine = TimeFlowEngine(
            business_style=config.business_style,
            country=config.country
        )
        
        self.gst_packager = GSTPackager(country=config.country, business_state=config.business_state)
        self.verification_engine = VerificationEngine(country=config.country, business_state=config.business_state)
        self.customer_generator = CustomerNameGenerator()
        self.verichain_engine = VeriChainEngine()
        
        # Initialize data sources
        self.products = self._load_products()
        self.customers = []
        
        # Initialize invoice counter (will be set properly when database is available)
        self.invoice_counter = 1
        
        # Initialize resilience tracking
        self.failed_invoices = []
        self.retry_count = 0
        self.generation_metadata = {
            'trace_id': self.trace_id,
            'batch_id': self.batch_id,
            'start_time': datetime.now().isoformat(),
            'config_snapshot': asdict(config)
        }
        
    def _initialize_invoice_counter(self):
        """Initialize invoice counter from database when available"""
        try:
            from app.models import Invoice
            highest_number = Invoice.query.order_by(Invoice.invoice_number.desc()).first()
            if highest_number:
                # Extract the numeric part of the invoice number
                number_part = highest_number.invoice_number.split('/')[-1]
                if number_part.isdigit():
                    self.invoice_counter = int(number_part) + 1
                else:
                    self.invoice_counter = 1
            else:
                self.invoice_counter = 1
        except Exception:
            # If database is not available, use default
            self.invoice_counter = 1
        
        # Use timestamp-based unique counter to prevent conflicts
        timestamp = int(datetime.now().timestamp())
        self.invoice_counter = timestamp % 1000000  # Use last 6 digits of timestamp
        
        # Initialize tracking variables
        self.existing_customers = []
        
        # Validation counters
        self.generated_count = 0
        self.validation_failures = 0
        
        # Runtime data - clear any existing data
        self.generated_invoices = []
        self.validation_results = []
        self.customers = []
        # Don't overwrite products - they are set in run_simulation
        
    def run_simulation(self, products: List[Dict[str, Any]]) -> SimulationResult:
        """
        PRODUCTION-GRADE simulation with resilience and decimal precision.
        
        Implements FR-9 requirements:
        - Retryable failures with ≤ 3 retries and exponential back-off
        - Mark failed batches with last_error after max retries
        - Allow partial success with per-invoice failure reporting
        """
        start_time = datetime.now()
        
        try:
            self.logger.info(f"🚀 Starting resilient simulation batch {self.batch_id} with trace_id {self.trace_id}")
            self.diagnostics.info(f"📊 Target: {self.config.invoice_count} invoices, Type: {self.config.invoice_type}")
            
            # Update generation metadata
            self.generation_metadata.update({
                'products_count': len(products) if products else 0,
                'invoice_type': self.config.invoice_type,
                'target_count': self.config.invoice_count
            })
            
            # Validate products
            if not products:
                raise ValueError("No products provided for simulation")
            
            self.products = products
            self.diagnostics.info(f"🔍 DEBUG: Set {len(self.products)} products in simulation engine")
            
            # Initialize invoice counter from database
            self._initialize_invoice_counter()
            
            # STEP 1: Generate invoices with resilience
            self.diagnostics.info(f"🎯 Generating {self.config.invoice_count} invoices with resilience...")
            
            invoices = []
            total_revenue_generated = Decimal('0.00')  # Use Decimal for precision
            
            for i in range(self.config.invoice_count):
                invoice_result = self._generate_single_invoice_with_retry(i + 1)
                
                if invoice_result.success:
                    invoice = invoice_result.result
                    # Add trace_id and generation metadata to invoice
                    invoice['trace_id'] = self.trace_id
                    invoice['generation_metadata'] = {
                        'sequence_number': i + 1,
                        'retry_count': invoice_result.attempt_count - 1,
                        'generation_time': invoice_result.total_time
                    }
                    
                    invoices.append(invoice)
                    total_revenue_generated += money(invoice['total_amount'])
                    self.generated_count += 1
                else:
                    # Track failed invoice for partial success reporting
                    failed_invoice = {
                        'sequence_number': i + 1,
                        'error': str(invoice_result.error),
                        'retry_count': invoice_result.attempt_count,
                        'trace_id': self.trace_id
                    }
                    self.failed_invoices.append(failed_invoice)
                    
                    # Don't create fallback invoices - fail fast instead
                    self.logger.error(f"Invoice generation failed for sequence {i+1}: {str(invoice_result.error)}")
                    # Continue with partial success but don't add fallback
            
            # STEP 2: Adjust for revenue target if specified
            if self.config.revenue_target:
                self.diagnostics.info(f"💰 Adjusting for revenue target: ₹{self.config.revenue_target:,.2f}")
                invoices = self._adjust_for_revenue_target(invoices)
            
            # STEP 3: Apply invoice type specific formatting
            self.diagnostics.info(f"📋 Applying {self.config.invoice_type.upper()} format...")
            invoices = self._apply_invoice_type_formatting(invoices)
            
            # STEP 4: Final validation using VerificationEngine with resilience
            self.diagnostics.info("✅ Running final validation with VerificationEngine...")
            
            verification_results = []
            for invoice in invoices:
                try:
                    # Use circuit breaker for verification to prevent cascading failures
                    result = self.circuit_breaker.call(
                        self.verification_engine.verify_invoice, 
                        invoice
                    )
                    verification_results.append(result)
                except Exception as e:
                    self.logger.warning(f"Verification failed for invoice {invoice.get('invoice_number', 'unknown')}: {str(e)}")
                    # Create a basic validation result for failed verification
                    from .verification_engine import ValidationResult
                    failed_result = ValidationResult(
                        is_valid=False,
                        compliance_score=0.0,
                        risk_level='high',
                        errors=[f"Verification failed: {str(e)}"],
                        warnings=[],
                        invoice_number=invoice.get('invoice_number', 'unknown')
                    )
                    verification_results.append(failed_result)
            
            # Also run our internal validation for statistics
            internal_validation_results = self._run_final_validation(invoices)
            
            # STEP 5: Generate statistics with resilience metrics
            statistics = self._generate_production_statistics_with_resilience(invoices, internal_validation_results)
            
            # STEP 6: Generate VeriChain hashes with retry
            for invoice in invoices:
                try:
                    hash_result = self.retry_handler.execute_with_retry(
                        self.verichain_engine.hash_invoice_data,
                        invoice,
                        retryable_exceptions=[NetworkException]
                    )
                    if hash_result.success:
                        invoice['verichain_hash'] = hash_result.result
                    else:
                        self.logger.warning(f"Failed to generate VeriChain hash for invoice {invoice.get('invoice_number')}")
                        invoice['verichain_hash'] = 'HASH_GENERATION_FAILED'
                except Exception as e:
                    self.logger.error(f"VeriChain hash generation error: {str(e)}")
                    invoice['verichain_hash'] = 'HASH_ERROR'
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Update generation metadata
            self.generation_metadata.update({
                'end_time': datetime.now().isoformat(),
                'execution_time': execution_time,
                'generated_count': len(invoices),
                'failed_count': len(self.failed_invoices),
                'total_revenue': float(total_revenue_generated)
            })
            
            # Determine if this is partial success
            partial_success = len(self.failed_invoices) > 0 and len(invoices) > 0
            success = len(invoices) > 0  # Success if we generated at least some invoices
            
            result = SimulationResult(
                config=self.config,
                invoices=invoices,
                validation_results=verification_results,
                statistics=statistics,
                execution_time=execution_time,
                batch_id=self.batch_id,
                success=success,
                trace_id=self.trace_id,
                retry_count=self.retry_count,
                failed_invoices=self.failed_invoices,
                partial_success=partial_success,
                generation_metadata=self.generation_metadata
            )
            
            if partial_success:
                self.diagnostics.warning(f"⚠️ Partial success: {len(invoices)} invoices generated, {len(self.failed_invoices)} failed")
            else:
                self.diagnostics.info(f"✅ Full success: {len(invoices)} invoices generated")
            
            self.diagnostics.info(f"💰 Total revenue: ₹{float(total_revenue_generated):,.2f}")
            
            return result
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            error_msg = f"Resilient simulation failed: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            self.diagnostics.error(error_msg)
            
            # Update generation metadata with error information
            self.generation_metadata.update({
                'end_time': datetime.now().isoformat(),
                'execution_time': execution_time,
                'error': error_msg,
                'failed_completely': True
            })
            
            return SimulationResult(
                config=self.config,
                invoices=[],
                validation_results=[],
                statistics={},
                execution_time=execution_time,
                batch_id=self.batch_id,
                success=False,
                error_message=error_msg,
                trace_id=self.trace_id,
                retry_count=self.retry_count,
                failed_invoices=self.failed_invoices,
                partial_success=False,
                generation_metadata=self.generation_metadata
            )
    
    def _generate_single_invoice_with_retry(self, sequence_number: int):
        """
        Generate single invoice with retry logic (FR-9).
        
        Returns RetryResult with success status and invoice data or error.
        """
        def generate_invoice():
            try:
                return self._generate_single_invoice(sequence_number)
            except Exception as e:
                # Convert to retryable exception if appropriate
                if "network" in str(e).lower() or "timeout" in str(e).lower():
                    raise NetworkException(f"Network error during invoice generation: {str(e)}")
                elif "pdf" in str(e).lower():
                    raise PDFGenerationException(f"PDF error during invoice generation: {str(e)}")
                else:
                    raise InvoiceGenerationException(f"Invoice generation error: {str(e)}")
        
        return self.retry_handler.execute_with_retry(
            generate_invoice,
            retryable_exceptions=[
                InvoiceGenerationException,
                NetworkException,
                PDFGenerationException
            ]
        )
    
    def _generate_single_invoice(self, sequence_number: int) -> Dict[str, Any]:
        """
        Generate a single invoice with STRICT parameter enforcement.
        
        This method MUST respect:
        - min_items_per_invoice and max_items_per_invoice
        - min_invoice_amount and max_invoice_amount
        - date_range
        - invoice_type specific formatting
        """
        # Generate realistic invoice number
        invoice_number = self._generate_realistic_invoice_number()
        
        # Generate invoice date within specified range
        invoice_date = self._generate_invoice_date()
        
        # Generate customer based on region, type, and UI toggles
        customer = self._generate_customer_for_invoice(sequence_number)
        
        # Select items within constraints
        items_count = random.randint(
            self.config.min_items_per_invoice,
            self.config.max_items_per_invoice  # Use UI parameter directly
        )
        
        items = self._select_invoice_items(items_count)
        
        # Calculate amounts to meet constraints
        invoice_data = self._calculate_invoice_amounts(items, customer)
        
        # Apply invoice type specific formatting
        invoice = self._format_invoice_by_type({
            'invoice_number': invoice_number,
            'invoice_date': invoice_date.strftime('%Y-%m-%d'),
            'customer_name': customer['name'],
            'customer_address': customer['address'],
            'customer_phone': customer.get('phone', ''),
            'items': items,
            'subtotal': invoice_data['subtotal'],
            'tax_amount': invoice_data['tax_amount'],
            'total_amount': invoice_data['total_amount'],
            'business_name': self.config.business_name,
            'business_address': self.config.business_address,
            'template_type': self.config.template_type,
            'sequence_number': sequence_number
        })
        
        return invoice
    
    def _generate_realistic_invoice_number(self) -> str:
        """
        Generate realistic invoice numbers using atomic counter service.
        
        GST: Format like "GST/YYYY-YY/Sequential"
        VAT: Format like "VAT/BH/YYMMDD/Sequential"
        Cash: Format like "CASH/YY/Sequential"
        """
        try:
            # Use atomic counter service for collision-free invoice numbers
            from app.services.counter.atomic_counter_service import AtomicCounterService
            
            counter_service = AtomicCounterService()
            
            # Map invoice types to counter types
            counter_type = self.config.invoice_type.upper()
            tenant_id = getattr(self.config, 'tenant_id', 'default')
            
            # Generate unique invoice number using atomic counter service
            invoice_number = counter_service.get_next_invoice_number(counter_type, tenant_id)
            
            self.logger.info(f"Generated invoice number using atomic counter: {invoice_number}")
            return invoice_number
            
        except Exception as e:
            self.logger.warning(f"Atomic counter service failed: {e}. Using fallback method.")
            
            # Fallback to timestamp-based generation if atomic counter fails
            current_year = datetime.now().year
            timestamp = int(datetime.now().timestamp())
            microsecond = datetime.now().microsecond
            unique_counter = (timestamp + microsecond + self.invoice_counter) % 1000000
            
            # Increment counter for each invoice
            self.invoice_counter += 1
            
            if self.config.invoice_type == 'gst':
                # GST format: GST/YYYY-YY/Sequential with unique suffix
                fy_start = current_year if datetime.now().month >= 4 else current_year - 1
                fy_end = fy_start + 1
                invoice_number = f"GST/{fy_start}-{str(fy_end)[2:]}/{unique_counter:06d}"
            
            elif self.config.invoice_type == 'vat':
                # Bahrain VAT format: VAT/BH/YYMMDD/Sequential with unique suffix
                date_part = datetime.now().strftime('%y%m%d')
                invoice_number = f"VAT/BH/{date_part}/{unique_counter:04d}"
            
            else:  # cash/plain
                # Simple cash format: CASH/YY/Sequential with unique suffix
                year_short = str(current_year)[2:]
                invoice_number = f"CASH/{year_short}/{unique_counter:06d}"
            
            self.logger.info(f"Generated fallback invoice number: {invoice_number}")
            return invoice_number
    
    def _generate_invoice_date(self) -> datetime:
        """
        Generate invoice date within the specified date range.
        """
        if not self.config.date_range:
            # Default to last 30 days, ending yesterday to avoid future dates
            end_date = datetime.now() - timedelta(days=1)
            start_date = end_date - timedelta(days=30)
        else:
            start_date, end_date = self.config.date_range
            # Convert date to datetime for comparison
            from datetime import date
            if isinstance(start_date, date):
                start_date = datetime.combine(start_date, datetime.min.time())
            if isinstance(end_date, date):
                end_date = datetime.combine(end_date, datetime.min.time())
            
            # Ensure end date is not in the future
            now = datetime.now()
            if end_date > now:
                end_date = now - timedelta(days=1)
        
        # Generate random date within range
        time_diff = end_date - start_date
        if time_diff.days <= 0:
            return start_date
        
        random_days = random.randint(0, time_diff.days)
        
        invoice_date = start_date + timedelta(days=random_days)
        return invoice_date
    
    def _generate_customer_for_invoice(self, sequence_number: int) -> Dict[str, Any]:
        """Generate realistic customer based on business style and regional settings"""
        
        # Determine customer type based on business style
        customer_type = self._get_customer_type_for_invoice()
        
        # Calculate repeat rate based on business style
        repeat_rate = self._calculate_repeat_rate_by_business_style()
        
        # Determine if this should be a repeat customer
        stress_factor = self.config.believability_stress / 100.0
        is_repeat_customer = random.random() < (repeat_rate * stress_factor)
        
        if is_repeat_customer and self.existing_customers:
            # Select existing customer
            customer = self._select_return_customer(stress_factor)
            self.diagnostics.info(f"🔄 Using repeat customer: {customer['name']}")
            return customer
        
        # Generate new customer
        customer_profile = self.customer_generator.generate_customer_profile(
            region=self.config.customer_region,
            customer_type=customer_type,
            invoice_type=self.config.invoice_type
        )
        
        # Adjust customer behavior based on business style
        customer = {
            'name': customer_profile.name,
            'address': customer_profile.address,
            'phone': customer_profile.phone,
            'tax_number': customer_profile.gst_number if self.config.invoice_type == 'gst' else customer_profile.vat_number,
            'customer_type': customer_type,
            'business_style': self.config.business_style,
            'order_frequency': self._calculate_order_frequency_by_business_style(),
            'average_order_size': self._calculate_average_order_size_by_business_style(),
            'payment_preference': self._get_payment_preference_by_business_style(),
            'state': self.config.business_state  # Add state for GST tax calculation
        }
        
        # Add to existing customers for potential reuse
        self.existing_customers.append(customer)
        
        self.diagnostics.info(f"👤 Generated new customer: {customer['name']} ({customer_type})")
        return customer
    
    def _calculate_repeat_rate_by_business_style(self) -> float:
        """Calculate customer repeat rate based on business style"""
        base_rates = {
            'retail_shop': 0.4,      # High repeat rate for retail
            'wholesale': 0.6,         # Very high for wholesale
            'distributor': 0.7,       # Highest for distributors
            'manufacturer': 0.5,      # Medium-high for manufacturers
            'service_provider': 0.3,  # Lower for services
            'online_store': 0.2       # Lowest for online
        }
        
        base_rate = base_rates.get(self.config.business_style, 0.3)
        
        # Adjust based on reality buffer
        reality_adjustment = self.config.reality_buffer / 100.0
        adjusted_rate = base_rate * (0.5 + 0.5 * reality_adjustment)
        
        return min(adjusted_rate, 0.8)  # Cap at 80%
    
    def _select_return_customer(self, stress_factor: float) -> Dict[str, Any]:
        """
        Select return customer with believability stress applied.
        """
        if stress_factor > 0.7:
            # High stress = more randomness in customer selection
            return random.choice(self.existing_customers)
        else:
            # Low stress = prefer recent customers
            recent_customers = self.existing_customers[-20:] if len(self.existing_customers) > 20 else self.existing_customers
            return random.choice(recent_customers)
    
    def _get_customer_type_for_invoice(self) -> str:
        """Determine customer type based on business style and mix"""
        if self.config.customer_type_mix == 'individual':
            return 'individual'
        elif self.config.customer_type_mix == 'business':
            return 'business'
        else:  # mixed
            # Adjust based on business style
            business_weights = {
                'retail_shop': 0.7,      # Mostly individuals
                'wholesale': 0.9,        # Mostly businesses
                'distributor': 0.95,     # Almost all businesses
                'manufacturer': 0.8,     # Mostly businesses
                'service_provider': 0.5, # Mixed
                'online_store': 0.6      # Slightly more individuals
            }
            
            business_weight = business_weights.get(self.config.business_style, 0.5)
            return 'business' if random.random() < business_weight else 'individual'
    
    def _select_invoice_items(self, items_count: int) -> List[Dict[str, Any]]:
        """
        Select items for invoice ensuring variety and realistic combinations.
        """
        self.diagnostics.info(f"🔍 DEBUG: _select_invoice_items called with items_count={items_count}")
        self.diagnostics.info(f"🔍 DEBUG: self.products length = {len(self.products) if self.products else 0}")
        
        if not self.products:
            raise ValueError("No products available for selection")
        
        # Safety check: Never exceed 50 items (government compliance)
        items_count = min(items_count, 50)
        
        selected_items = []
        available_products = self.products.copy()
        
        for _ in range(items_count):
            if not available_products:
                # If we run out, allow repeats but with different quantities
                available_products = self.products.copy()
            
            product = random.choice(available_products)
            available_products.remove(product)  # Avoid immediate duplicates
            
            # Generate realistic quantity based on business style
            quantity = self._generate_realistic_quantity(product)
            
            # Calculate unit price with some variation
            base_price = float(product.get('sale_price', 100))
            price_variation = random.uniform(0.95, 1.05)  # ±5% variation
            unit_price = money(base_price * price_variation)
            
            item = {
                'name': product['name'],
                'code': product.get('code', ''),
                'hsn_code': product.get('hsn_code', ''),
                'quantity': quantity,
                'unit': product.get('unit', 'Nos'),
                'unit_price': float(unit_price),
                'gross_amount': float(money(Decimal(str(quantity)) * unit_price)),
                'discount_percentage': self._generate_realistic_discount(),
                'tax_rate': float(product.get('gst_rate', 0) if self.config.invoice_type == 'gst' else product.get('vat_rate', 0))
            }
            
            # Calculate net amount after discount
            discount_amount = money(Decimal(str(item['gross_amount'])) * Decimal(str(item['discount_percentage'])) / Decimal('100'))
            item['discount_amount'] = float(discount_amount)
            item['net_amount'] = float(money(Decimal(str(item['gross_amount'])) - discount_amount))
            
            selected_items.append(item)
        
        self.diagnostics.info(f"🔍 DEBUG: Selected {len(selected_items)} items so far")
        
        return selected_items
    
    def _generate_realistic_quantity(self, product: Dict[str, Any]) -> int:
        """
        Generate realistic quantities based on business style and product type.
        """
        business_style = self.config.business_style
        
        if business_style == 'retail_shop':
            return random.randint(1, 5)
        elif business_style == 'distributor':
            return random.randint(10, 100)
        elif business_style == 'exporter':
            return random.randint(50, 500)
        elif business_style == 'pharmacy':
            return random.randint(1, 10)
        elif business_style == 'it_service':
            return random.randint(1, 3)
        else:
            return random.randint(1, 10)
    
    def _generate_realistic_discount(self) -> float:
        """
        Generate realistic discount percentages.
        """
        # Most items have no discount
        if random.random() < 0.7:
            return 0.0
        
        # Some items have small discounts
        if random.random() < 0.8:
            return round(random.uniform(2, 10), 2)
        
        # Few items have larger discounts
        return round(random.uniform(10, 25), 2)
    
    def _calculate_invoice_amounts(self, items: List[Dict[str, Any]], customer: Dict[str, Any]) -> Dict[str, float]:
        """
        Calculate invoice amounts with full Decimal precision (FR-9).
        
        All calculations use Decimal throughout to eliminate floating-point precision errors.
        This ensures exact tax calculations matching the verification engine.
        """
        try:
            # First pass: Calculate taxes for all items using consistent method with Decimal precision
            for item in items:
                if self.config.invoice_type == 'gst':
                    self._calculate_gst_tax_decimal(item, customer)
                elif self.config.invoice_type == 'vat':
                    self._calculate_vat_tax_decimal(item)
                else:  # cash/plain - still calculate tax but don't add to total
                    # For cash invoices, calculate tax but don't add to total amount
                    customer = {'state': self.config.business_state}
                    self._calculate_gst_tax_decimal(item, customer)  # Use GST calculation for consistency
                    # But keep total_amount as net_amount for cash invoices
                    item['total_amount'] = float(money(Decimal(str(item['net_amount']))))
            
            # Calculate totals from items using Decimal precision throughout
            subtotal = money(sum(Decimal(str(item['net_amount'])) for item in items))
            total_tax = money(sum(Decimal(str(item['tax_amount'])) for item in items))
            total_amount = money(subtotal + total_tax)
            
            # For VAT invoices, ensure tax_amount is properly calculated from VAT amounts
            if self.config.invoice_type == 'vat':
                # Calculate total VAT with proper Decimal handling
                total_vat = money(sum(Decimal(str(item.get('vat_amount', 0))) for item in items))
                
                # Ensure total_tax is exactly the same as total_vat for consistency
                total_tax = total_vat
                
                # Calculate total amount with proper Decimal handling in a single step
                # This ensures the total matches what verification expects
                total_amount = money(subtotal + total_vat)
            
            # For cash invoices, keep total_amount as subtotal (no tax added to total)
            if self.config.invoice_type == 'cash':
                total_amount = subtotal
            
            # Check if we need to adjust for constraints using Decimal precision
            min_amount = Decimal(str(self.config.min_invoice_amount))
            max_amount = Decimal(str(self.config.max_invoice_amount))
            
            if total_amount < min_amount or total_amount > max_amount:
                # Calculate target amount within constraints
                target_amount = self._calculate_target_invoice_amount_decimal()
                target_amount = max(min_amount, min(max_amount, target_amount))
                
                # Simple proportional adjustment to meet target using Decimal precision
                if total_amount > 0:
                    adjustment_factor = target_amount / total_amount
                    self._adjust_invoice_amounts_decimal(items, adjustment_factor)
                    
                    # Recalculate taxes after adjustment using consistent method
                    for item in items:
                        if self.config.invoice_type == 'gst':
                            self._calculate_gst_tax_decimal(item, customer)
                        elif self.config.invoice_type == 'vat':
                            self._calculate_vat_tax_decimal(item)
                        else:  # cash/plain
                            customer = {'state': self.config.business_state}
                            self._calculate_gst_tax_decimal(item, customer)
                            item['total_amount'] = float(money(Decimal(str(item['net_amount']))))
                    
                    # Recalculate totals using Decimal precision
                    subtotal = money(sum(Decimal(str(item['net_amount'])) for item in items))
                    total_tax = money(sum(Decimal(str(item['tax_amount'])) for item in items))
                    total_amount = money(subtotal + total_tax)
                    
                    # For VAT invoices, ensure tax_amount is properly calculated from VAT amounts
                    if self.config.invoice_type == 'vat':
                        # Calculate total VAT with proper Decimal handling
                        total_vat = money(sum(Decimal(str(item.get('vat_amount', 0))) for item in items))
                        
                        # Ensure total_tax is exactly the same as total_vat for consistency
                        total_tax = total_vat
                        
                        # Calculate total amount with proper Decimal handling in a single step
                        # This ensures the total matches what verification expects
                        total_amount = money(subtotal + total_vat)
                    
                    # For cash invoices, keep total_amount as subtotal
                    if self.config.invoice_type == 'cash':
                        total_amount = subtotal
            
            return {
                'subtotal': float(subtotal),
                'tax_amount': float(total_tax),
                'total_amount': float(total_amount)
            }
            
        except Exception as e:
            # Log the error and raise as retryable exception
            self.logger.error(f"Invoice amount calculation failed: {str(e)}")
            raise InvoiceGenerationException(f"Amount calculation error: {str(e)}")
    
    def _calculate_target_invoice_amount_decimal(self) -> Decimal:
        """
        Calculate target invoice amount for revenue distribution using Decimal precision.
        """
        if hasattr(self.config, 'revenue_target') and self.config.revenue_target is not None and self.config.revenue_target > 0:
            # Distribute revenue target across invoices using Decimal precision
            revenue_target = Decimal(str(self.config.revenue_target))
            invoice_count = Decimal(str(self.config.invoice_count))
            target_per_invoice = money(revenue_target / invoice_count)
            
            # Apply reality buffer and stress factors
            reality_factor = Decimal(str(self.config.reality_buffer)) / Decimal('100')
            stress_factor = Decimal(str(self.config.believability_stress)) / Decimal('100')
            
            # Add realistic variation using Decimal precision
            import random
            variation = Decimal(str(random.uniform(-float(stress_factor), float(stress_factor))))
            target_amount = money(target_per_invoice * (Decimal('1') + variation) * reality_factor)
            
            # Ensure within constraints
            min_amount = Decimal(str(self.config.min_invoice_amount))
            max_amount = Decimal(str(self.config.max_invoice_amount))
            return max(min_amount, min(max_amount, target_amount))
        else:
            # No revenue target - use random amount within constraints
            import random
            min_amount = Decimal(str(self.config.min_invoice_amount))
            max_amount = Decimal(str(self.config.max_invoice_amount))
            random_amount = Decimal(str(random.uniform(float(min_amount), float(max_amount))))
            return money(random_amount)
    
    def _calculate_gst_tax_decimal(self, item: Dict[str, Any], customer: Dict[str, Any]) -> Decimal:
        """
        Calculate GST tax for an item with full Decimal precision (FR-9).
        
        This method ensures exact tax calculation matching the verification engine
        by using Decimal arithmetic throughout all calculations.
        """
        try:
            # Use the GSTPackager for consistent tax calculation
            # Pass the tax_rate from the item if available for consistency with verification engine
            override_tax_rate = item.get('tax_rate')
            tax_calc = self.gst_packager.calculate_item_tax(
                item_name=item.get('name', ''),
                hsn_code=item.get('hsn_code', ''),
                quantity=float(item.get('quantity', 0)),
                unit_price=float(item.get('unit_price', 0)),
                customer_state=customer.get('state', 'Maharashtra'),
                discount_percentage=float(item.get('discount_percentage', 0)),
                discount_amount=float(item.get('discount_amount', 0)),
                override_tax_rate=override_tax_rate
            )
            
            # Store all tax details in the item using Decimal precision
            item['tax_rate'] = float(money(Decimal(str(tax_calc.tax_rate))))
            item['cgst_rate'] = float(money(Decimal(str(tax_calc.cgst_rate))))
            item['sgst_rate'] = float(money(Decimal(str(tax_calc.sgst_rate))))
            item['igst_rate'] = float(money(Decimal(str(tax_calc.igst_rate))))
            item['vat_rate'] = float(money(Decimal(str(tax_calc.vat_rate))))
            item['cgst_amount'] = float(money(Decimal(str(tax_calc.cgst_amount))))
            item['sgst_amount'] = float(money(Decimal(str(tax_calc.sgst_amount))))
            item['igst_amount'] = float(money(Decimal(str(tax_calc.igst_amount))))
            item['vat_amount'] = float(money(Decimal(str(tax_calc.vat_amount))))
            item['tax_amount'] = float(money(Decimal(str(tax_calc.total_tax))))
            item['total_amount'] = float(money(Decimal(str(tax_calc.total_amount))))
            
            return money(Decimal(str(tax_calc.total_tax)))
            
        except Exception as e:
            self.logger.error(f"GST tax calculation failed for item {item.get('name', 'unknown')}: {str(e)}")
            raise InvoiceGenerationException(f"GST tax calculation error: {str(e)}")
    
    def _calculate_vat_tax_decimal(self, item: Dict[str, Any]) -> Decimal:
        """
        Calculate VAT tax for an item with full Decimal precision (FR-9).
        
        This method ensures consistent Decimal handling and rounding for VAT calculations
        to match the verification engine's expectations with complete precision.
        """
        try:
            # Use the GSTPackager for consistent VAT calculation
            # Handle potential None values and ensure we have a valid numeric tax rate
            vat_rate = item.get('vat_rate')
            tax_rate = item.get('tax_rate')
            
            # Ensure we have a valid tax rate, defaulting to 10% (standard Bahrain VAT rate) if none is specified
            override_tax_rate = vat_rate if vat_rate is not None else (tax_rate if tax_rate is not None else 10.0)
            
            # Convert all numeric inputs to proper Decimal types before calculation
            quantity = Decimal(str(item.get('quantity', 0)))
            unit_price = Decimal(str(item.get('unit_price', 0)))
            discount_percentage = Decimal(str(item.get('discount_percentage', 0)))
            discount_amount = Decimal(str(item.get('discount_amount', 0)))
            
            tax_calc = self.gst_packager.calculate_item_tax(
                item_name=item.get('name', ''),
                hsn_code=item.get('hsn_code', ''),
                quantity=float(quantity),
                unit_price=float(unit_price),
                customer_state='Bahrain',  # For VAT calculations
                discount_percentage=float(discount_percentage),
                discount_amount=float(discount_amount),
                override_tax_rate=override_tax_rate
            )
            
            # Calculate VAT directly to ensure consistency with verification engine using Decimal precision
            net_amount = Decimal(str(tax_calc.net_amount))
            vat_rate = Decimal(str(tax_calc.vat_rate))
            
            # Calculate VAT amount with proper Decimal handling using money() helper
            vat_amount = money(net_amount * vat_rate / Decimal('100'))
            
            # Calculate total amount with proper Decimal handling in a single step
            total_amount = money(net_amount + vat_amount)
            
            # Store VAT details in the item using money() helper for consistent rounding
            item['vat_rate'] = float(money(vat_rate))
            item['vat_amount'] = float(vat_amount)
            item['tax_amount'] = float(vat_amount)  # For VAT, tax_amount should equal vat_amount
            item['total_amount'] = float(total_amount)
            
            return vat_amount
            
        except Exception as e:
            self.logger.error(f"VAT tax calculation failed for item {item.get('name', 'unknown')}: {str(e)}")
            raise InvoiceGenerationException(f"VAT tax calculation error: {str(e)}")
    
    def _adjust_invoice_amounts_decimal(self, items: List[Dict[str, Any]], factor: Decimal) -> None:
        """
        Adjust all item amounts by a factor to meet constraints with full Decimal precision.
        """
        try:
            for item in items:
                # Adjust quantities and prices proportionally using Decimal for precision
                unit_price_decimal = Decimal(str(item['unit_price'])) * factor
                item['unit_price'] = float(money(unit_price_decimal))
                
                quantity_decimal = Decimal(str(item['quantity']))
                gross_amount_decimal = quantity_decimal * unit_price_decimal
                item['gross_amount'] = float(money(gross_amount_decimal))
                
                # Recalculate discount amount with Decimal precision
                discount_percentage_decimal = Decimal(str(item['discount_percentage']))
                discount_amount_decimal = money(gross_amount_decimal * discount_percentage_decimal / Decimal('100'))
                item['discount_amount'] = float(discount_amount_decimal)
                item['net_amount'] = float(money(gross_amount_decimal - discount_amount_decimal))
                
                # Note: Tax will be recalculated by the calling method using consistent tax calculation
                
        except Exception as e:
            self.logger.error(f"Invoice amount adjustment failed: {str(e)}")
            raise InvoiceGenerationException(f"Amount adjustment error: {str(e)}")
    
    def _calculate_target_invoice_amount(self) -> float:
        """
        Calculate target invoice amount for revenue distribution.
        """
        if hasattr(self.config, 'revenue_target') and self.config.revenue_target is not None and self.config.revenue_target > 0:
            # Distribute revenue target across invoices
            target_per_invoice = self.config.revenue_target / self.config.invoice_count
            
            # Apply reality buffer and stress factors
            reality_factor = self.config.reality_buffer / 100.0
            stress_factor = self.config.believability_stress / 100.0
            
            # Add realistic variation
            variation = random.uniform(-stress_factor, stress_factor)
            target_amount = target_per_invoice * (1 + variation) * reality_factor
            
            # Ensure within constraints
            return max(self.config.min_invoice_amount, 
                      min(self.config.max_invoice_amount, target_amount))
        else:
            # No revenue target - use random amount within constraints
            return random.uniform(self.config.min_invoice_amount, 
                                self.config.max_invoice_amount)
    
    def _calculate_gst_tax(self, item: Dict[str, Any], customer: Dict[str, Any]) -> float:
        """
        Calculate GST tax for an item with precise decimal handling.
        This method ensures exact tax calculation matching the verification engine with proper Decimal handling.
        """
        # Use the GSTPackager for consistent tax calculation
        # Pass the tax_rate from the item if available for consistency with verification engine
        override_tax_rate = item.get('tax_rate')
        tax_calc = self.gst_packager.calculate_item_tax(
            item_name=item.get('name', ''),
            hsn_code=item.get('hsn_code', ''),
            quantity=float(item.get('quantity', 0)),
            unit_price=float(item.get('unit_price', 0)),
            customer_state=customer.get('state', 'Maharashtra'),
            discount_percentage=float(item.get('discount_percentage', 0)),
            discount_amount=float(item.get('discount_amount', 0)),
            override_tax_rate=override_tax_rate
        )
        
        # Store all tax details in the item for consistency using money() helper for consistent rounding
        item['tax_rate'] = float(money(Decimal(str(tax_calc.tax_rate))))
        item['cgst_rate'] = float(money(Decimal(str(tax_calc.cgst_rate))))
        item['sgst_rate'] = float(money(Decimal(str(tax_calc.sgst_rate))))
        item['igst_rate'] = float(money(Decimal(str(tax_calc.igst_rate))))
        item['vat_rate'] = float(money(Decimal(str(tax_calc.vat_rate))))
        item['cgst_amount'] = float(money(Decimal(str(tax_calc.cgst_amount))))
        item['sgst_amount'] = float(money(Decimal(str(tax_calc.sgst_amount))))
        item['igst_amount'] = float(money(Decimal(str(tax_calc.igst_amount))))
        item['vat_amount'] = float(money(Decimal(str(tax_calc.vat_amount))))
        item['tax_amount'] = float(money(Decimal(str(tax_calc.total_tax))))
        item['total_amount'] = float(money(Decimal(str(tax_calc.total_amount))))
        
        return float(tax_calc.total_tax)
    
    def _calculate_vat_tax(self, item: Dict[str, Any]) -> float:
        """
        Calculate VAT tax for an item with proper Decimal handling.
        
        This method ensures consistent Decimal handling and rounding for VAT calculations
        to match the verification engine's expectations.
        
        The fix addresses the following issues:
        1. Inconsistent Decimal handling - All calculations now use the money() helper function
           to ensure consistent precision and rounding throughout the calculation process.
        2. Type conversion issues - All numeric inputs are explicitly converted to Decimal
           before calculations to prevent precision loss.
        3. Rounding consistency - The same ROUND_HALF_UP rounding method is used consistently
           for all monetary values, matching the verification engine's expectations.
        4. Tax rate handling - The method now properly handles different tax rate sources
           (vat_rate or tax_rate) and ensures they are converted to Decimal before calculations.
        
        This implementation ensures that invoices using the Bahrain VAT template pass verification
        by maintaining calculation consistency between invoice generation and verification.
        """
        # Use the GSTPackager for consistent VAT calculation
        # Pass the tax_rate from the item if available for consistency with verification engine
        # Handle potential None values and ensure we have a valid numeric tax rate
        vat_rate = item.get('vat_rate')
        tax_rate = item.get('tax_rate')
        
        # FIX: Ensure we have a valid tax rate, defaulting to 10% (standard Bahrain VAT rate) if none is specified
        # This fix ensures consistent tax rate handling between generation and verification
        override_tax_rate = vat_rate if vat_rate is not None else (tax_rate if tax_rate is not None else 10.0)
        
        # FIX: Convert all numeric inputs to proper Decimal types before calculation
        # This ensures precision is maintained throughout the calculation process
        # Using str() conversion prevents floating point precision issues
        quantity = Decimal(str(item.get('quantity', 0)))
        unit_price = Decimal(str(item.get('unit_price', 0)))
        discount_percentage = Decimal(str(item.get('discount_percentage', 0)))
        discount_amount = Decimal(str(item.get('discount_amount', 0)))
        
        tax_calc = self.gst_packager.calculate_item_tax(
            item_name=item.get('name', ''),
            hsn_code=item.get('hsn_code', ''),
            quantity=float(quantity),
            unit_price=float(unit_price),
            customer_state='Bahrain',  # For VAT calculations
            discount_percentage=float(discount_percentage),
            discount_amount=float(discount_amount),
            override_tax_rate=override_tax_rate
        )
        
        # FIX: Calculate VAT directly to ensure consistency with verification engine
        # Convert to Decimal using str() to avoid floating point precision issues
        net_amount = Decimal(str(tax_calc.net_amount))
        vat_rate = Decimal(str(tax_calc.vat_rate))
        
        # FIX: Calculate VAT amount with proper Decimal handling using money() helper
        # This ensures consistent rounding using ROUND_HALF_UP method
        vat_amount = money(net_amount * vat_rate / Decimal('100'))
        
        # FIX: Calculate total amount with proper Decimal handling in a single step
        # This ensures the total matches what verification expects
        total_amount = money(net_amount + vat_amount)
        
        # FIX: Store VAT details in the item using money() helper for consistent rounding
        # Convert back to float for JSON serialization, but only after all calculations are complete
        item['vat_rate'] = float(money(vat_rate))
        item['vat_amount'] = float(vat_amount)
        item['tax_amount'] = float(vat_amount)  # For VAT, tax_amount should equal vat_amount
        item['total_amount'] = float(total_amount)
        
        # The fix ensures that:
        # 1. All calculations use Decimal for precision
        # 2. All monetary values are rounded consistently using money() helper
        # 3. The tax_amount equals vat_amount for VAT invoices
        # 4. The total_amount is calculated as net_amount + vat_amount
        
        return float(vat_amount)
    
    def _adjust_invoice_amounts(self, items: List[Dict[str, Any]], factor: float) -> None:
        """
        Adjust all item amounts by a factor to meet constraints with proper Decimal handling.
        """
        for item in items:
            # Adjust quantities and prices proportionally using Decimal for precision
            factor_decimal = Decimal(str(factor))
            unit_price_decimal = Decimal(str(item['unit_price'])) * factor_decimal
            item['unit_price'] = float(money(unit_price_decimal))
            
            quantity_decimal = Decimal(str(item['quantity']))
            gross_amount_decimal = quantity_decimal * unit_price_decimal
            item['gross_amount'] = float(money(gross_amount_decimal))
            
            # Recalculate discount amount
            discount_percentage_decimal = Decimal(str(item['discount_percentage']))
            discount_amount_decimal = money(gross_amount_decimal * discount_percentage_decimal / Decimal('100'))
            item['discount_amount'] = float(discount_amount_decimal)
            item['net_amount'] = float(money(gross_amount_decimal - discount_amount_decimal))
            
            # Note: Tax will be recalculated by the calling method using consistent tax calculation
    
    def _format_invoice_by_type(self, invoice_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply invoice type specific formatting and fields.
        """
        if self.config.invoice_type == 'gst':
            return self._format_gst_invoice(invoice_data)
        elif self.config.invoice_type == 'vat':
            return self._format_vat_invoice(invoice_data)
        else:
            return self._format_cash_invoice(invoice_data)
    
    def _format_gst_invoice(self, invoice_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format invoice as GST invoice with all required fields.
        Uses consistent tax calculation from items.
        """
        # Calculate totals from items using money() helper for consistent rounding
        total_cgst = money(sum(item.get('cgst_amount', 0) for item in invoice_data['items']))
        total_sgst = money(sum(item.get('sgst_amount', 0) for item in invoice_data['items']))
        total_igst = money(sum(item.get('igst_amount', 0) for item in invoice_data['items']))
        total_tax = money(sum(item.get('tax_amount', 0) for item in invoice_data['items']))
        
        # Ensure tax_amount matches the sum of individual taxes
        calculated_tax_amount = money(total_cgst + total_sgst + total_igst)
        
        # Recalculate total_amount to ensure consistency
        total_amount = money(money(invoice_data['subtotal']) + calculated_tax_amount)
        
        # Always ensure business_gst_number is provided
        business_gst = self.config.business_gst_number
        if not business_gst:
            business_gst = "27AAAAA0000A1Z5"  # Default GST number if not provided
        
        invoice_data.update({
            'invoice_type': 'gst',
            'currency': 'INR',
            'currency_symbol': '₹',
            'cgst_amount': float(total_cgst),
            'sgst_amount': float(total_sgst),
            'igst_amount': float(total_igst),
            'tax_amount': float(calculated_tax_amount),
            'total_amount': float(total_amount),
            'business_gst_number': business_gst,
            'customer_gst_number': self._generate_customer_gst_number(),
            'place_of_supply': self._get_place_of_supply(),
            'tax_amount_in_words': self._amount_to_words(float(calculated_tax_amount)),
            'total_amount_in_words': self._amount_to_words(float(total_amount)),
            'declaration': 'This is a computer generated invoice.',
            'authorized_signatory': 'For ' + (invoice_data.get('business_name', 'Business Name'))
        })
        
        return invoice_data
    
    def _format_vat_invoice(self, invoice_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format invoice as VAT invoice with Bahrain specific fields.
        Uses consistent tax calculation from items.
        """
        # Calculate VAT from items using money() helper for consistent rounding
        total_vat = money(sum(item.get('vat_amount', 0) for item in invoice_data['items']))
        
        # Ensure tax_amount matches VAT amount
        invoice_data['tax_amount'] = float(total_vat)
        
        # Recalculate total_amount to ensure consistency
        total_amount = money(invoice_data['subtotal'] + total_vat)
        invoice_data['total_amount'] = float(total_amount)
        
        invoice_data.update({
            'invoice_type': 'vat',
            'currency': 'BHD',
            'currency_symbol': 'BD',
            'vat_amount': float(total_vat),
            'total_ex_vat': float(money(invoice_data['subtotal'])),
            'business_vat_number': self._generate_business_vat_number(),
            'customer_vat_number': self._generate_customer_vat_number(),
            'total_amount_in_words': self._amount_to_words_arabic(invoice_data['total_amount']),
            'vat_declaration': 'VAT Registration No: ' + self._generate_business_vat_number()
        })
        
        return invoice_data
    
    def _format_cash_invoice(self, invoice_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format invoice as simple cash invoice.
        For cash invoices, total_amount should equal subtotal (no tax added to total).
        """
        # For cash invoices, total_amount should equal subtotal
        invoice_data['total_amount'] = invoice_data['subtotal']
        
        invoice_data.update({
            'invoice_type': 'cash',
            'currency': 'INR',
            'currency_symbol': '₹',
            'total_amount_in_words': self._amount_to_words(invoice_data['total_amount']),
            'footer_text': 'For ' + (invoice_data.get('business_name', 'Business Name'))
        })
        
        return invoice_data
    
    def _validate_single_invoice(self, invoice: Dict[str, Any]) -> bool:
        """
        Validate a single invoice against all constraints.
        """
        try:
            # Check amount constraints
            total_amount = invoice['total_amount']
            if total_amount < self.config.min_invoice_amount or total_amount > self.config.max_invoice_amount:
                return False
            
            # Check items count
            items_count = len(invoice['items'])
            if items_count < self.config.min_items_per_invoice or items_count > self.config.max_items_per_invoice:
                return False
            
            # Check date range
            invoice_date = datetime.strptime(invoice['invoice_date'], '%Y-%m-%d')
            if self.config.date_range:
                start_date, end_date = self.config.date_range
                if invoice_date < start_date or invoice_date > end_date:
                    return False
            
            # Check required fields
            required_fields = ['invoice_number', 'customer_name', 'customer_address']
            for field in required_fields:
                if not invoice.get(field):
                    return False
            
            return True
            
        except Exception as e:
            self.diagnostics.error(f"Validation error: {str(e)}")
            return False
    
    def _generate_single_invoice_strict(self, sequence_number: int) -> Dict[str, Any]:
        """
        Generate invoice with stricter constraints when normal generation fails validation.
        """
        # Use minimum constraints to ensure validation passes
        invoice_number = self._generate_realistic_invoice_number()
        invoice_date = self._generate_invoice_date()
        customer = self._generate_customer_for_invoice(sequence_number)
        
        # Use minimum items
        items = self._select_invoice_items(self.config.min_items_per_invoice)
        
        # Ensure minimum amount
        target_amount = max(self.config.min_invoice_amount, 100)
        
        # Calculate current total first
        current_total = sum(item['net_amount'] for item in items)
        if current_total < target_amount:
            items = self._adjust_items_to_target_amount(items, target_amount)
        
        invoice_data = self._calculate_invoice_amounts(items, customer)
        
        invoice = self._format_invoice_by_type({
            'invoice_number': invoice_number,
            'invoice_date': invoice_date.strftime('%Y-%m-%d'),
            'customer_name': customer['name'],
            'customer_address': customer['address'],
            'customer_phone': customer.get('phone', ''),
            'items': items,
            'subtotal': invoice_data['subtotal'],
            'tax_amount': invoice_data['tax_amount'],
            'total_amount': invoice_data['total_amount'],
            'business_name': self.config.business_name,
            'business_address': self.config.business_address,
            'template_type': self.config.template_type,
            'sequence_number': sequence_number
        })
        
        return invoice
    

    
    def _adjust_items_to_target_amount(self, items: List[Dict[str, Any]], target_amount: float) -> List[Dict[str, Any]]:
        """
        Adjust item prices to reach target amount.
        """
        current_total = sum(item['net_amount'] for item in items)
        if current_total == 0:
            return items
        
        adjustment_factor = target_amount / current_total
        
        for item in items:
            item['unit_price'] = round(item['unit_price'] * adjustment_factor, 2)
            item['gross_amount'] = round(item['quantity'] * item['unit_price'], 2)
            item['net_amount'] = round(item['gross_amount'] * (1 - item['discount_percentage'] / 100), 2)
        
        return items
    
    def _generate_business_gst_number(self) -> str:
        """
        Generate realistic GST number for business.
        """
        # Use configured GST number if available
        if self.config.business_gst_number:
            return self.config.business_gst_number
        
        # Get state code based on business_state
        state_codes = {
            'Maharashtra': '27',
            'Delhi': '07',
            'Karnataka': '29',
            'Tamil Nadu': '33',
            'Gujarat': '24',
            'Uttar Pradesh': '09',
            'West Bengal': '19',
            'Telangana': '36',
            'Haryana': '06',
            'Kerala': '32'
        }
        
        state_code = state_codes.get(self.config.business_state, '27')  # Default to Maharashtra if state not found
        
        # Generate PAN part (5 letters, 4 numbers, 1 letter)
        letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        pan_letters = ''.join(random.choice(letters) for _ in range(5))
        pan_numbers = ''.join(str(random.randint(0, 9)) for _ in range(4))
        pan_last_letter = random.choice(letters)
        pan_part = f"{pan_letters}{pan_numbers}{pan_last_letter}"
        
        entity_code = "1"  # 1 for companies
        check_digit = "Z"  # Default check digit
        
        # Format: 27AAAAA0000A1Z5 (Maharashtra state code 27)
        return f"{state_code}{pan_part}{entity_code}{check_digit}{random.randint(0, 9)}"
    
    def _generate_customer_gst_number(self) -> str:
        """
        Generate GST number for customer (if business).
        """
        if random.random() < 0.3:  # 30% chance customer has GST
            state_codes = ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22", "23", "24", "25", "26", "27", "28", "29", "30", "31", "32", "33", "34", "35", "36", "37"]
            state_code = random.choice(state_codes)
            
            # Generate proper PAN format: 5 letters + 4 digits + 1 letter
            letters1 = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=5))
            digits = ''.join(random.choices('0123456789', k=4))
            letter2 = random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
            pan_part = f"{letters1}{digits}{letter2}"
            
            entity_code = random.choice(["1", "2", "3", "4"])
            check_digit = random.choice("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ")
            return f"{state_code}{pan_part}{entity_code}Z{check_digit}"
        return ""
    
    def _generate_business_vat_number(self) -> str:
        """
        Generate realistic VAT number for Bahrain business.
        """
        # Use configured VAT number if available
        if self.config.business_vat_number:
            return self.config.business_vat_number
        
        # Bahrain VAT format: 12345678901
        return f"1000{random.randint(100000, 999999)}1"
    
    def _generate_customer_vat_number(self) -> str:
        """
        Generate VAT number for customer (if business).
        """
        if random.random() < 0.2:  # 20% chance customer has VAT
            return f"2000{random.randint(100000, 999999)}1"
        return ""
    
    def _get_place_of_supply(self) -> str:
        """
        Get place of supply for GST invoice.
        """
        return f"27-Maharashtra"  # Default to Maharashtra
    
    def _amount_to_words(self, amount: float) -> str:
        """
        Convert amount to words (Indian format).
        """
        # Simplified implementation - in production, use a proper library
        if amount == 0:
            return "Zero Rupees Only"
        
        # Basic conversion for common amounts
        ones = ["", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten", 
                "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen", "Seventeen", 
                "Eighteen", "Nineteen"]
        
        tens = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"]
        
        int_amount = int(amount)
        
        if int_amount < 20:
            return f"{ones[int_amount]} Rupees Only"
        elif int_amount < 100:
            return f"{tens[int_amount // 10]} {ones[int_amount % 10]} Rupees Only".strip()
        elif int_amount < 1000:
            hundreds = int_amount // 100
            remainder = int_amount % 100
            result = f"{ones[hundreds]} Hundred"
            if remainder > 0:
                if remainder < 20:
                    result += f" {ones[remainder]}"
                else:
                    result += f" {tens[remainder // 10]} {ones[remainder % 10]}".strip()
            return f"{result} Rupees Only"
        else:
            # For larger amounts, use a simplified format
            return f"{int_amount} Rupees Only"
    
    def _amount_to_words_arabic(self, amount: float) -> str:
        """
        Convert amount to words (Arabic/Bahrain format).
        """
        # Simplified implementation for Bahrain Dinar
        int_amount = int(amount)
        return f"{int_amount} Bahraini Dinars Only"
    
    def _adjust_for_revenue_target(self, invoices: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Adjust invoices to meet revenue target while respecting all constraints"""
        if not self.config.revenue_target:
            return invoices
        
        current_total = sum(invoice['total_amount'] for invoice in invoices)
        target_total = self.config.revenue_target
        
        # Allow 10% tolerance for revenue target
        tolerance = target_total * 0.1
        if abs(current_total - target_total) <= tolerance:
            self.diagnostics.info(f"💰 Revenue target achieved within tolerance: ₹{current_total:,.2f} (target: ₹{target_total:,.2f})")
            return invoices
        
        self.diagnostics.info(f"💰 Adjusting revenue: Current ₹{current_total:,.2f} → Target ₹{target_total:,.2f}")
        
        # Simple proportional adjustment
        adjustment_factor = target_total / current_total if current_total > 0 else 1.0
        
        # Limit adjustment factor to prevent extreme changes
        adjustment_factor = max(0.5, min(2.0, adjustment_factor))
        
        adjusted_invoices = []
        total_adjusted = 0.0
        
        for invoice in invoices:
            # Simple proportional adjustment of total amount
            original_amount = invoice['total_amount']
            adjusted_amount = original_amount * adjustment_factor
            
            # Ensure within constraints
            adjusted_amount = max(self.config.min_invoice_amount, 
                                min(self.config.max_invoice_amount, adjusted_amount))
            
            # Create adjusted invoice
            adjusted_invoice = invoice.copy()
            
            # Proportionally adjust all amounts
            if original_amount > 0:
                scale_factor = adjusted_amount / original_amount
                adjusted_invoice['subtotal'] = float(money(invoice['subtotal'] * scale_factor))
                adjusted_invoice['tax_amount'] = float(money(invoice['tax_amount'] * scale_factor))
                adjusted_invoice['total_amount'] = float(money(adjusted_amount))
                
                # Adjust item amounts proportionally
                for item in adjusted_invoice['items']:
                    item['unit_price'] = float(money(item['unit_price'] * scale_factor))
                    item['gross_amount'] = float(money(item['gross_amount'] * scale_factor))
                    item['net_amount'] = float(money(item['net_amount'] * scale_factor))
                    item['tax_amount'] = float(money(item['tax_amount'] * scale_factor))
                    item['total_amount'] = float(money(item['total_amount'] * scale_factor))
            
            adjusted_invoices.append(adjusted_invoice)
            total_adjusted += adjusted_invoice['total_amount']
        
        # Final validation
        final_adjustment = target_total / total_adjusted if total_adjusted > 0 else 1.0
        
        if abs(final_adjustment - 1.0) > 0.1:  # If still off by more than 10%
            self.diagnostics.warning(f"⚠️ Revenue target not fully achieved: ₹{total_adjusted:,.2f} vs ₹{target_total:,.2f}")
        
        self.diagnostics.info(f"✅ Revenue adjustment complete: ₹{total_adjusted:,.2f}")
        return adjusted_invoices
    
    def _validate_revenue_constraints(self, invoices: List[Dict[str, Any]]) -> bool:
        """Validate that all revenue constraints are met"""
        if not invoices:
            return False
        
        total_revenue = sum(invoice['total_amount'] for invoice in invoices)
        invoice_count = len(invoices)
        
        # Check invoice count
        if invoice_count != self.config.invoice_count:
            self.diagnostics.error(f"❌ Invoice count mismatch: {invoice_count} vs {self.config.invoice_count}")
            return False
        
        # Check revenue target
        if self.config.revenue_target:
            revenue_tolerance = self.config.revenue_target * 0.1  # 10% tolerance
            if abs(total_revenue - self.config.revenue_target) > revenue_tolerance:
                self.diagnostics.error(f"❌ Revenue target not met: ₹{total_revenue:,.2f} vs ₹{self.config.revenue_target:,.2f}")
                return False
        
        # Check individual invoice amounts
        for invoice in invoices:
            amount = invoice['total_amount']
            if amount < self.config.min_invoice_amount or amount > self.config.max_invoice_amount:
                self.diagnostics.error(f"❌ Invoice amount out of bounds: ₹{amount:,.2f}")
                return False
        
        # Check item counts
        for invoice in invoices:
            item_count = len(invoice.get('items', []))
            if item_count < self.config.min_items_per_invoice or item_count > self.config.max_items_per_invoice:
                self.diagnostics.error(f"❌ Item count out of bounds: {item_count}")
                return False
        
        self.diagnostics.info(f"✅ All revenue constraints validated successfully")
        return True
    
    def _apply_invoice_type_formatting(self, invoices: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Apply final formatting specific to invoice type.
        """
        for invoice in invoices:
            if invoice['invoice_type'] == 'gst':
                # Ensure GST specific fields are present
                if 'cgst_amount' not in invoice:
                    invoice['cgst_amount'] = 0
                if 'sgst_amount' not in invoice:
                    invoice['sgst_amount'] = 0
                if 'igst_amount' not in invoice:
                    invoice['igst_amount'] = 0
                
                # Calculate totals from items
                invoice['cgst_amount'] = float(money(sum(item.get('cgst_amount', 0) for item in invoice['items'])))
                invoice['sgst_amount'] = float(money(sum(item.get('sgst_amount', 0) for item in invoice['items'])))
                invoice['igst_amount'] = float(money(sum(item.get('igst_amount', 0) for item in invoice['items'])))
                
            elif invoice['invoice_type'] == 'vat':
                # Ensure VAT specific fields are present
                if 'vat_amount' not in invoice:
                    invoice['vat_amount'] = invoice['tax_amount']
                if 'total_ex_vat' not in invoice:
                    invoice['total_ex_vat'] = invoice['subtotal']
        
        return invoices
    
    def _run_final_validation(self, invoices: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Run final validation on all invoices and return validation results.
        """
        validation_results = []
        
        for i, invoice in enumerate(invoices):
            validation_result = {
                'invoice_number': invoice['invoice_number'],
                'sequence_number': i + 1,
                'is_valid': True,
                'errors': [],
                'warnings': []
            }
            
            # Validate amount constraints
            if invoice['total_amount'] < self.config.min_invoice_amount:
                validation_result['is_valid'] = False
                validation_result['errors'].append(f"Total amount {invoice['total_amount']} below minimum {self.config.min_invoice_amount}")
            
            if invoice['total_amount'] > self.config.max_invoice_amount:
                validation_result['is_valid'] = False
                validation_result['errors'].append(f"Total amount {invoice['total_amount']} above maximum {self.config.max_invoice_amount}")
            
            # Validate items count
            items_count = len(invoice['items'])
            if items_count < self.config.min_items_per_invoice:
                validation_result['is_valid'] = False
                validation_result['errors'].append(f"Items count {items_count} below minimum {self.config.min_items_per_invoice}")
            
            if items_count > self.config.max_items_per_invoice:
                validation_result['is_valid'] = False
                validation_result['errors'].append(f"Items count {items_count} above maximum {self.config.max_items_per_invoice}")
            
            # Validate required fields
            required_fields = ['invoice_number', 'customer_name', 'customer_address', 'invoice_date']
            for field in required_fields:
                if not invoice.get(field):
                    validation_result['is_valid'] = False
                    validation_result['errors'].append(f"Missing required field: {field}")
            
            # Validate invoice type specific fields
            if invoice['invoice_type'] == 'gst':
                if not invoice.get('business_gst_number'):
                    validation_result['is_valid'] = False
                    validation_result['errors'].append("Missing business GST number - required for GST invoice")
                
                # Validate tax calculations
                total_tax = Decimal('0.00')
                for item in invoice['items']:
                    item_tax = Decimal(str(item.get('tax_amount', 0)))
                    total_tax += item_tax
                
                invoice_tax = Decimal(str(invoice.get('tax_amount', 0)))
                if abs(total_tax - invoice_tax) > Decimal('0.01'):
                    validation_result['is_valid'] = False
                    validation_result['errors'].append(f"Tax total {float(invoice_tax)} doesn't match sum of item taxes {float(total_tax)}")
                
                # Validate total amount
                subtotal = Decimal(str(invoice.get('subtotal', 0)))
                total = Decimal(str(invoice.get('total_amount', 0)))
                expected_total = subtotal + invoice_tax
                
                if abs(total - expected_total) > Decimal('0.01'):
                    validation_result['is_valid'] = False
                    validation_result['errors'].append(f"Total amount {float(total)} doesn't match subtotal + tax {float(expected_total)}")
                
            elif invoice['invoice_type'] == 'vat':
                if not invoice.get('business_vat_number'):
                    validation_result['is_valid'] = False
                    validation_result['errors'].append("Missing business VAT number - required for VAT invoice")
            
            validation_results.append(validation_result)
        
        return validation_results
    
    def _generate_production_statistics_with_resilience(self, invoices: List[Dict[str, Any]], validation_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate comprehensive statistics including resilience metrics (FR-9).
        """
        # Calculate basic statistics using Decimal for precision
        total_revenue = money(sum(Decimal(str(invoice['total_amount'])) for invoice in invoices))
        total_tax = money(sum(Decimal(str(invoice['tax_amount'])) for invoice in invoices))
        valid_invoices = sum(1 for result in validation_results if result.get('is_valid', True))
        
        # Calculate resilience metrics
        total_retries = sum(
            invoice.get('generation_metadata', {}).get('retry_count', 0) 
            for invoice in invoices
        )
        
        fallback_invoices = sum(
            1 for invoice in invoices 
            if invoice.get('generation_metadata', {}).get('is_fallback', False)
        )
        
        # Calculate by invoice type using Decimal precision
        type_stats = {}
        for invoice in invoices:
            inv_type = invoice['invoice_type']
            if inv_type not in type_stats:
                type_stats[inv_type] = {'count': 0, 'revenue': Decimal('0.00'), 'tax': Decimal('0.00')}
            type_stats[inv_type]['count'] += 1
            type_stats[inv_type]['revenue'] += money(invoice['total_amount'])
            type_stats[inv_type]['tax'] += money(invoice['tax_amount'])
        
        # Convert Decimal back to float for JSON serialization
        for stats in type_stats.values():
            stats['revenue'] = float(stats['revenue'])
            stats['tax'] = float(stats['tax'])
        
        # Calculate amount distribution using Decimal
        amounts = [money(invoice['total_amount']) for invoice in invoices]
        avg_amount = money(sum(amounts) / len(amounts)) if amounts else Decimal('0.00')
        min_amount = min(amounts) if amounts else Decimal('0.00')
        max_amount = max(amounts) if amounts else Decimal('0.00')
        
        statistics = {
            'total_invoices_generated': len(invoices),
            'total_invoices_requested': self.config.invoice_count,
            'generation_success_rate': len(invoices) / self.config.invoice_count if self.config.invoice_count > 0 else 0,
            'total_revenue': float(total_revenue),
            'revenue_target': self.config.revenue_target,
            'revenue_target_achievement': float(total_revenue / Decimal(str(self.config.revenue_target)) * 100) if self.config.revenue_target else 0,
            'total_tax_collected': float(total_tax),
            'valid_invoices_count': valid_invoices,
            'validation_success_rate': round(valid_invoices / len(invoices) * 100, 2) if invoices else 0,
            'average_invoice_amount': float(avg_amount),
            'minimum_invoice_amount': float(min_amount),
            'maximum_invoice_amount': float(max_amount),
            'invoice_type_distribution': type_stats,
            'date_range_used': {
                'start': self.config.date_range[0].strftime('%Y-%m-%d') if self.config.date_range else None,
                'end': self.config.date_range[1].strftime('%Y-%m-%d') if self.config.date_range else None
            },
            'parameters_enforced': {
                'min_items_per_invoice': self.config.min_items_per_invoice,
                'max_items_per_invoice': self.config.max_items_per_invoice,
                'min_invoice_amount': self.config.min_invoice_amount,
                'max_invoice_amount': self.config.max_invoice_amount,
                'customer_region': self.config.customer_region,
                'business_style': self.config.business_style
            },
            # New resilience metrics (FR-9)
            'resilience_metrics': {
                'total_retry_attempts': total_retries,
                'failed_invoices_count': len(self.failed_invoices),
                'fallback_invoices_count': fallback_invoices,
                'partial_success': len(self.failed_invoices) > 0 and len(invoices) > 0,
                'failure_rate': len(self.failed_invoices) / self.config.invoice_count if self.config.invoice_count > 0 else 0,
                'average_retries_per_invoice': total_retries / len(invoices) if invoices else 0,
                'trace_id': self.trace_id,
                'batch_id': self.batch_id
            }
        }
        
        return statistics
    
    def _generate_production_statistics(self, invoices: List[Dict[str, Any]], validation_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate comprehensive statistics for the simulation.
        """
        total_revenue = sum(invoice['total_amount'] for invoice in invoices)
        total_tax = sum(invoice['tax_amount'] for invoice in invoices)
        valid_invoices = sum(1 for result in validation_results if result['is_valid'])
        
        # Calculate by invoice type
        type_stats = {}
        for invoice in invoices:
            inv_type = invoice['invoice_type']
            if inv_type not in type_stats:
                type_stats[inv_type] = {'count': 0, 'revenue': 0, 'tax': 0}
            type_stats[inv_type]['count'] += 1
            type_stats[inv_type]['revenue'] += invoice['total_amount']
            type_stats[inv_type]['tax'] += invoice['tax_amount']
        
        # Calculate amount distribution
        amounts = [invoice['total_amount'] for invoice in invoices]
        avg_amount = sum(amounts) / len(amounts) if amounts else 0
        min_amount = min(amounts) if amounts else 0
        max_amount = max(amounts) if amounts else 0
        
        statistics = {
            'total_invoices_generated': len(invoices),
            'total_invoices_requested': self.config.invoice_count,
            'generation_success_rate': len(invoices) / self.config.invoice_count if self.config.invoice_count > 0 else 0,
            'total_revenue': round(total_revenue, 2),
            'revenue_target': self.config.revenue_target,
            'revenue_target_achievement': round(total_revenue / self.config.revenue_target * 100, 2) if self.config.revenue_target else 0,
            'total_tax_collected': round(total_tax, 2),
            'valid_invoices_count': valid_invoices,
            'validation_success_rate': round(valid_invoices / len(invoices) * 100, 2) if invoices else 0,
            'average_invoice_amount': round(avg_amount, 2),
            'minimum_invoice_amount': round(min_amount, 2),
            'maximum_invoice_amount': round(max_amount, 2),
            'invoice_type_distribution': type_stats,
            'date_range_used': {
                'start': self.config.date_range[0].strftime('%Y-%m-%d') if self.config.date_range else None,
                'end': self.config.date_range[1].strftime('%Y-%m-%d') if self.config.date_range else None
            },
            'parameters_enforced': {
                'min_items_per_invoice': self.config.min_items_per_invoice,
                'max_items_per_invoice': self.config.max_items_per_invoice,
                'min_invoice_amount': self.config.min_invoice_amount,
                'max_invoice_amount': self.config.max_invoice_amount,
                'customer_region': self.config.customer_region,
                'business_style': self.config.business_style
            }
        }
        
        return statistics
    
    def _generate_timestamps(self) -> List[datetime]:
        """Generate realistic timestamps using TimeFlowEngine"""
        if not self.config.date_range:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            date_range = (start_date, end_date)
        else:
            date_range = self.config.date_range
        
        timestamps = self.timeflow_engine.generate_invoice_timestamps(
            count=self.config.invoice_count,
            date_range=date_range,
            reality_buffer=self.config.reality_buffer,
            believability_stress=self.config.believability_stress
        )
        
        return timestamps
    
    def _generate_customers(self) -> List[CustomerProfile]:
        """Generate customer profiles using CustomerNameGenerator"""
        customers = self.customer_generator.generate_batch_customers(
            count=self.config.invoice_count,
            region=self.config.customer_region,
            customer_type=self.config.customer_type_mix,
            invoice_type=self.config.invoice_type,
            return_rate=self.config.customer_return_rate
        )
        
        return customers
    
    def _generate_invoices(self, timestamps: List[datetime]) -> List[Dict[str, Any]]:
        """Generate complete invoices with all details"""
        invoices = []
        
        for i, timestamp in enumerate(timestamps):
            try:
                # Get customer for this invoice
                customer = self.customers[i % len(self.customers)]
                
                # Generate invoice
                invoice = self._generate_single_invoice(i + 1, timestamp, customer)
                invoices.append(invoice)
                
            except Exception as e:
                self.diagnostics.error(f"Error generating invoice {i+1}: {str(e)}")
                continue
        
        return invoices
    
    def _generate_single_invoice_legacy(self, invoice_number: int, timestamp: datetime, customer: CustomerProfile) -> Dict[str, Any]:
        """Generate a single complete invoice (legacy method)"""
        # Generate invoice number
        invoice_num = self._generate_invoice_number(invoice_number)
        
        # Select items for this invoice
        items = self._select_invoice_items_legacy()
        
        # Calculate tax for each item
        tax_calculations = []
        for item in items:
            tax_calc = self.gst_packager.calculate_item_tax(
                item_name=item['name'],
                hsn_code=item.get('hsn_code', ''),
                quantity=item['quantity'],
                unit_price=item['unit_price'],
                customer_state=customer.state,
                discount_percentage=item.get('discount_percentage', 0),
                override_tax_rate=item.get('tax_rate')
            )
            tax_calculations.append(tax_calc)
        
        # Calculate invoice totals
        totals = self.gst_packager.calculate_invoice_totals(tax_calculations)
        
        # Build complete invoice
        invoice = {
            'invoice_number': invoice_num,
            'invoice_date': timestamp.strftime('%Y-%m-%d'),
            'invoice_time': timestamp.strftime('%H:%M:%S'),
            'invoice_type': self.config.invoice_type,
            'batch_id': self.batch_id,
            
            # Customer information
            'customer_name': customer.company_name or customer.name,
            'customer_address': f"{customer.address}, {customer.city}, {customer.state} {customer.postal_code}",
            'customer_phone': customer.phone,
            'customer_email': customer.email,
            'customer_gst_number': customer.gst_number,
            'customer_vat_number': customer.vat_number,
            'customer_state': customer.state,
            'customer_country': customer.country,
            'customer_type': customer.customer_type,
            
            # Business information (would come from settings)
            'business_name': 'LedgerFlow Demo Business',
            'business_address': 'Demo Address, Demo City',
            'business_gst_number': '27ABCDE1234F1Z5' if self.config.invoice_type == 'gst' else None,
            'business_vat_number': '123456789' if self.config.invoice_type == 'vat' else None,
            
            # Items
            'items': [self._tax_calc_to_item_dict(calc) for calc in tax_calculations],
            
            # Totals
            'subtotal': totals['subtotal'],
            'total_discount': totals['total_discount'],
            'net_amount': totals['net_amount'],
            'tax_amount': totals['total_tax'],
            'cgst_amount': totals['total_cgst'],
            'sgst_amount': totals['total_sgst'],
            'igst_amount': totals['total_igst'],
            'vat_amount': totals['total_vat'],
            'total_amount': totals['grand_total'],
            
            # Metadata
            'generation_timestamp': datetime.now().isoformat(),
            'simulation_config': asdict(self.config),
            'tax_summary': self.gst_packager.generate_tax_summary(tax_calculations)
        }
        
        return invoice
    
    def _generate_invoice_number(self, sequence: int) -> str:
        """Generate invoice number based on type and sequence"""
        year = datetime.now().year
        
        if self.config.invoice_type == 'gst':
            return f"GST-{year}-{sequence:06d}"
        elif self.config.invoice_type == 'vat':
            return f"VAT-{year}-{sequence:06d}"
        elif self.config.invoice_type == 'cash':
            return f"CASH-{year}-{sequence:06d}"
        else:
            return f"INV-{year}-{sequence:06d}"
    
    def _select_invoice_items_legacy(self) -> List[Dict[str, Any]]:
        """Select items for an invoice with realistic patterns (legacy method)"""
        # Determine number of items
        min_items = max(1, self.config.min_items_per_invoice)
        max_items = min(len(self.products), self.config.max_items_per_invoice)  # Use UI parameter directly
        
        # Apply reality buffer to item count
        if random.random() < self.config.reality_buffer:
            # Realistic distribution (more invoices with fewer items)
            if random.random() < 0.6:  # 60% have 1-3 items
                item_count = random.randint(1, min(3, max_items))
            elif random.random() < 0.3:  # 30% have 4-8 items
                item_count = random.randint(4, min(8, max_items))
            else:  # 10% have many items
                item_count = random.randint(max(9, min_items), max_items) if max_items >= 9 else random.randint(min_items, max_items)
        else:
            # Random distribution
            item_count = random.randint(min_items, max_items)
        
        # Select products
        selected_products = random.sample(self.products, item_count)
        
        # Generate quantities and prices
        items = []
        for product in selected_products:
            # Generate realistic quantity
            quantity = self._generate_realistic_quantity(product)
            
            # Apply price variation
            base_price = float(product.get('sale_price', product.get('price', 100)))
            unit_price = self._apply_price_variation(base_price)
            
            # Sometimes add discount
            discount_percentage = 0
            if random.random() < 0.2:  # 20% chance of discount
                discount_percentage = random.choice([5, 10, 15, 20])
            
            item = {
                'name': product.get('name', 'Unknown Product'),
                'code': product.get('code', 'UNKNOWN'),
                'hsn_code': product.get('hsn_code', ''),
                'unit': product.get('unit', 'Nos'),
                'quantity': quantity,
                'unit_price': unit_price,
                'discount_percentage': discount_percentage,
                'tax_rate': product.get('gst_rate' if self.config.invoice_type == 'gst' else 'vat_rate'),
                'category': product.get('category', ''),
                'description': product.get('description', '')
            }
            
            items.append(item)
        
        return items
    
    def _generate_realistic_quantity(self, product: Dict[str, Any]) -> float:
        """Generate realistic quantity based on product type"""
        # Base quantity distribution
        if random.random() < 0.7:  # 70% small quantities
            quantity = random.randint(1, 5)
        elif random.random() < 0.2:  # 20% medium quantities
            quantity = random.randint(6, 20)
        else:  # 10% large quantities
            quantity = random.randint(21, 100)
        
        # Adjust based on product price
        price = float(product.get('sale_price', product.get('price', 100)))
        if price > 10000:  # Expensive items
            quantity = min(quantity, 3)
        elif price < 100:  # Cheap items
            quantity = max(quantity, 2)
        
        return float(quantity)
    
    def _apply_price_variation(self, base_price: float) -> float:
        """Apply realistic price variation"""
        # Small variation for realism
        variation = random.uniform(-0.05, 0.05)  # ±5%
        
        # Apply believability stress
        if random.random() < self.config.believability_stress:
            variation = random.uniform(-0.15, 0.15)  # ±15%
        
        new_price = base_price * (1 + variation)
        return max(0.01, round(new_price, 2))
    
    def _tax_calc_to_item_dict(self, tax_calc: TaxCalculation) -> Dict[str, Any]:
        """Convert TaxCalculation to item dictionary"""
        return {
            'name': tax_calc.item_name,
            'hsn_code': tax_calc.hsn_code,
            'quantity': tax_calc.quantity,
            'unit_price': tax_calc.unit_price,
            'gross_amount': tax_calc.gross_amount,
            'discount_amount': tax_calc.discount_amount,
            'net_amount': tax_calc.net_amount,
            'tax_rate': tax_calc.tax_rate,
            'cgst_rate': tax_calc.cgst_rate,
            'sgst_rate': tax_calc.sgst_rate,
            'igst_rate': tax_calc.igst_rate,
            'vat_rate': tax_calc.vat_rate,
            'cgst_amount': tax_calc.cgst_amount,
            'sgst_amount': tax_calc.sgst_amount,
            'igst_amount': tax_calc.igst_amount,
            'vat_amount': tax_calc.vat_amount,
            'total_tax': tax_calc.total_tax,
            'total_amount': tax_calc.total_amount,
            'is_interstate': tax_calc.is_interstate,
            'is_exempt': tax_calc.is_exempt
        }
    
    def _apply_reality_adjustments(self):
        """Apply reality buffer and believability stress to all invoices"""
        # Sort invoices by date for sequence checks
        self.generated_invoices.sort(key=lambda x: x['invoice_date'])
        
        # Apply small variations to make it more realistic
        for i, invoice in enumerate(self.generated_invoices):
            # Sometimes adjust amounts slightly
            if random.random() < (1 - self.config.reality_buffer):
                # Add small rounding variations
                invoice['total_amount'] = round(invoice['total_amount'] + random.uniform(-0.5, 0.5), 2)
            
            # Sometimes adjust timestamps slightly
            if random.random() < self.config.believability_stress:
                original_time = datetime.strptime(f"{invoice['invoice_date']} {invoice['invoice_time']}", '%Y-%m-%d %H:%M:%S')
                adjusted_time = original_time + timedelta(minutes=random.randint(-30, 30))
                invoice['invoice_time'] = adjusted_time.strftime('%H:%M:%S')
    
    def _validate_invoices(self) -> List[ValidationResult]:
        """Validate all generated invoices"""
        validation_results = []
        
        for invoice in self.generated_invoices:
            result = self.verification_engine.verify_invoice(invoice)
            validation_results.append(result)
        
        return validation_results
    
    def _filter_invalid_invoices(self):
        """Filter out invoices that don't meet quality standards"""
        valid_invoices = []
        valid_results = []
        
        for invoice, result in zip(self.generated_invoices, self.validation_results):
            # Check compliance score
            if result.compliance_score < self.config.min_compliance_score:
                self.diagnostics.warning(f"Invoice {invoice['invoice_number']} filtered: low compliance score {result.compliance_score}")
                continue
            
            # Check risk level
            risk_levels = ['low', 'medium', 'high', 'critical']
            max_risk_index = risk_levels.index(self.config.max_risk_level)
            current_risk_index = risk_levels.index(result.risk_level)
            
            if current_risk_index > max_risk_index:
                self.diagnostics.warning(f"Invoice {invoice['invoice_number']} filtered: high risk level {result.risk_level}")
                continue
            
            valid_invoices.append(invoice)
            valid_results.append(result)
        
        self.generated_invoices = valid_invoices
        self.validation_results = valid_results
    
    def _generate_statistics(self) -> Dict[str, Any]:
        """Generate comprehensive statistics"""
        stats = {
            'generation_summary': {
                'total_invoices': len(self.generated_invoices),
                'batch_id': self.batch_id,
                'generation_time': datetime.now().isoformat(),
                'config': asdict(self.config)
            },
            'financial_summary': {
                'total_revenue': sum(inv['total_amount'] for inv in self.generated_invoices),
                'total_tax': sum(inv['tax_amount'] for inv in self.generated_invoices),
                'average_invoice_value': np.mean([inv['total_amount'] for inv in self.generated_invoices]) if self.generated_invoices else 0,
                'median_invoice_value': np.median([inv['total_amount'] for inv in self.generated_invoices]) if self.generated_invoices else 0,
                'min_invoice_value': min([inv['total_amount'] for inv in self.generated_invoices]) if self.generated_invoices else 0,
                'max_invoice_value': max([inv['total_amount'] for inv in self.generated_invoices]) if self.generated_invoices else 0
            },
            'customer_statistics': self.customer_generator.get_region_statistics(self.customers),
            'validation_summary': {
                'total_validated': len(self.validation_results),
                'valid_invoices': len([r for r in self.validation_results if r.is_valid]),
                'invalid_invoices': len([r for r in self.validation_results if not r.is_valid]),
                'average_compliance_score': np.mean([r.compliance_score for r in self.validation_results]) if self.validation_results else 0,
                'risk_distribution': self._calculate_risk_distribution()
            },
            'temporal_distribution': self._calculate_temporal_distribution(),
            'tax_analysis': self._calculate_tax_analysis()
        }
        
        return stats
    
    def _calculate_risk_distribution(self) -> Dict[str, int]:
        """Calculate risk level distribution"""
        distribution = {'low': 0, 'medium': 0, 'high': 0, 'critical': 0}
        
        for result in self.validation_results:
            distribution[result.risk_level] += 1
        
        return distribution
    
    def _calculate_temporal_distribution(self) -> Dict[str, Any]:
        """Calculate temporal distribution of invoices"""
        if not self.generated_invoices:
            return {}
        
        dates = [datetime.strptime(inv['invoice_date'], '%Y-%m-%d') for inv in self.generated_invoices]
        
        # Day of week distribution
        weekday_dist = {}
        for date in dates:
            weekday = date.strftime('%A')
            weekday_dist[weekday] = weekday_dist.get(weekday, 0) + 1
        
        # Hour distribution
        hour_dist = {}
        for inv in self.generated_invoices:
            hour = int(inv['invoice_time'].split(':')[0])
            hour_dist[hour] = hour_dist.get(hour, 0) + 1
        
        return {
            'date_range': {
                'start': min(dates).strftime('%Y-%m-%d'),
                'end': max(dates).strftime('%Y-%m-%d'),
                'span_days': (max(dates) - min(dates)).days + 1
            },
            'weekday_distribution': weekday_dist,
            'hour_distribution': hour_dist
        }
    
    def _calculate_tax_analysis(self) -> Dict[str, Any]:
        """Calculate tax analysis"""
        if not self.generated_invoices:
            return {}
        
        tax_rates = {}
        total_tax_by_rate = {}
        
        for invoice in self.generated_invoices:
            for item in invoice['items']:
                rate = item['tax_rate']
                tax_rates[rate] = tax_rates.get(rate, 0) + 1
                total_tax_by_rate[rate] = total_tax_by_rate.get(rate, 0) + item['total_tax']
        
        return {
            'tax_rate_distribution': tax_rates,
            'tax_amount_by_rate': total_tax_by_rate,
            'total_tax_collected': sum(inv['tax_amount'] for inv in self.generated_invoices),
            'tax_percentage_of_revenue': (sum(inv['tax_amount'] for inv in self.generated_invoices) / 
                                        sum(inv['total_amount'] for inv in self.generated_invoices)) * 100 if self.generated_invoices else 0
        }
    
    def _generate_verichain_hashes(self):
        """Generate blockchain-style verification hashes"""
        for invoice in self.generated_invoices:
            hash_signature = self.verichain_engine.hash_invoice_data(invoice)
            invoice['verichain_hash'] = hash_signature
    
    def export_simulation_data(self, output_dir: str):
        """Export all simulation data to files"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Export invoices
        invoices_file = output_path / f"invoices_{self.batch_id}.json"
        with open(invoices_file, 'w') as f:
            json.dump(self.generated_invoices, f, indent=2, default=str)
        
        # Export validation results
        validation_file = output_path / f"validation_{self.batch_id}.json"
        with open(validation_file, 'w') as f:
            json.dump([asdict(r) for r in self.validation_results], f, indent=2, default=str)
        
        # Export statistics
        stats_file = output_path / f"statistics_{self.batch_id}.json"
        statistics = self._generate_statistics()
        with open(stats_file, 'w') as f:
            json.dump(statistics, f, indent=2, default=str)
        
        self.diagnostics.info(f"Simulation data exported to {output_dir}")
        
        return {
            'invoices_file': str(invoices_file),
            'validation_file': str(validation_file),
            'statistics_file': str(stats_file)
        }
    
    def _load_products(self) -> List[Dict[str, Any]]:
        """
        Load product data for invoice generation.
        """
        # Default product catalog for testing
        default_products = [
            {
                'name': 'Laptop Computer',
                'code': 'LAP001',
                'hsn_code': '84713000',
                'sale_price': 45000,
                'unit': 'Nos',
                'gst_rate': 18,
                'vat_rate': 10
            },
            {
                'name': 'Mobile Phone',
                'code': 'MOB001',
                'hsn_code': '85171200',
                'sale_price': 15000,
                'unit': 'Nos',
                'gst_rate': 18,
                'vat_rate': 10
            },
            {
                'name': 'Office Chair',
                'code': 'CHR001',
                'hsn_code': '94013000',
                'sale_price': 8500,
                'unit': 'Nos',
                'gst_rate': 18,
                'vat_rate': 10
            },
            {
                'name': 'Consulting Service',
                'code': 'SVC001',
                'hsn_code': '998361',
                'sale_price': 5000,
                'unit': 'Hour',
                'gst_rate': 18,
                'vat_rate': 10
            }
        ]
        
        self.diagnostics.info(f"Using default product catalog with {len(default_products)} products")
        return default_products 

    def _calculate_order_frequency_by_business_style(self) -> float:
        """Calculate order frequency based on business style"""
        frequencies = {
            'retail_shop': 0.3,      # Low frequency, small orders
            'wholesale': 0.6,        # Medium frequency
            'distributor': 0.8,      # High frequency
            'manufacturer': 0.7,     # High frequency
            'service_provider': 0.4, # Medium frequency
            'online_store': 0.2      # Low frequency
        }
        
        return frequencies.get(self.config.business_style, 0.4)
    
    def _calculate_average_order_size_by_business_style(self) -> float:
        """Calculate average order size based on business style"""
        size_multipliers = {
            'retail_shop': 1.0,      # Base size
            'wholesale': 3.0,        # 3x larger
            'distributor': 5.0,      # 5x larger
            'manufacturer': 4.0,     # 4x larger
            'service_provider': 1.5, # 1.5x larger
            'online_store': 0.8      # Slightly smaller
        }
        
        return size_multipliers.get(self.config.business_style, 1.0)
    
    def _get_payment_preference_by_business_style(self) -> str:
        """Get payment preference based on business style"""
        preferences = {
            'retail_shop': ['cash', 'card', 'upi'],
            'wholesale': ['bank_transfer', 'cheque', 'credit'],
            'distributor': ['bank_transfer', 'credit', 'cheque'],
            'manufacturer': ['bank_transfer', 'credit', 'cheque'],
            'service_provider': ['card', 'bank_transfer', 'upi'],
            'online_store': ['card', 'upi', 'net_banking']
        }
        
        payment_options = preferences.get(self.config.business_style, ['cash', 'card'])
        return random.choice(payment_options) 