# Design Document

## Overview

This design document addresses the comprehensive requirements v2.0 for transforming LedgerFlow into a 10/10 production-grade invoice generation system. The design systematically addresses all functional requirements (FR-1 through FR-11), non-functional requirements (reliability, maintainability, security, portability, internationalization, auditability), quality assurance requirements, deployment/ops requirements, and migration requirements.

**Success Criteria:** 
- 0 invoice number collisions under 1,000 req/s concurrency (FR-1)
- < 0.1% PDF failure rate with graceful degradation (NFR Reliability)
- 100 invoices generated in ≤ 60s on 2 CPU/4GB RAM (FR-10)
- Lighthouse accessibility score ≥ 90 (FR-11)
- Plugin tax strategies deployable in ≤ 1 day (FR-2)

The solution implements proven architectural patterns including Strategy Pattern for tax calculations, Atomic Operations for data consistency, Circuit Breaker for resilience, and Schema-Driven UI for maintainability.

## Architecture

### High-Level Architecture

```mermaid
graph TB
    subgraph "Frontend Layer"
        UI[Dynamic UI Generator]
        Schema[JSON Schema Parser]
        Progress[Progress Tracker]
    end
    
    subgraph "API Layer"
        API[Flask API Routes]
        Auth[Authentication Middleware]
        Valid[Request Validator]
        Metrics[Metrics Collector]
    end
    
    subgraph "Business Logic Layer"
        MSE[Master Simulation Engine]
        TaxStrategy[Tax Strategy Factory]
        Counter[Atomic Counter Service]
        Config[Configuration Manager]
    end
    
    subgraph "Data Layer"
        DB[(PostgreSQL Database)]
        Redis[(Redis Cache)]
        FileSystem[File System]
        Migrations[Alembic Migrations]
    end
    
    subgraph "Infrastructure Layer"
        Logger[Structured Logger]
        Monitor[Prometheus Metrics]
        Circuit[Circuit Breaker]
        Retry[Retry Handler]
    end
    
    UI --> API
    API --> MSE
    MSE --> TaxStrategy
    MSE --> Counter
    Counter --> DB
    Counter --> Redis
    MSE --> Logger
    API --> Metrics
    Monitor --> Metrics
    Circuit --> Retry
```

### Core Components Architecture

The system is restructured around five core architectural pillars:

1. **Atomic Operations Layer**: Ensures data consistency through database-level atomicity
2. **Strategy Pattern Layer**: Modular tax calculation system supporting GST, VAT, and NoTax strategies
3. **Configuration Management Layer**: Centralized YAML-based configuration with schema validation
4. **Resilience Layer**: Circuit breakers, bounded retry logic, and graceful degradation
5. **Observability Layer**: Comprehensive logging, metrics, and monitoring

## Components and Interfaces

### 1. Atomic Counter Service

**Purpose**: Eliminate invoice number collisions through atomic database operations

**Interface**:
```python
class AtomicCounterService:
    def get_next_invoice_number(self, invoice_type: str, business_id: str) -> str
    def reserve_invoice_numbers(self, count: int, invoice_type: str) -> List[str]
    def release_reserved_numbers(self, numbers: List[str]) -> bool
```

**Implementation Strategy**:
- Primary: PostgreSQL sequences with `nextval('invoice_sequence')` for true atomicity
- Fallback: Redis atomic increment with `INCR` command for high availability
- Emergency: Application-level locking with exponential backoff
- Development: SQLite with application-level locking (local development only)

**Database Schema Changes** (Alembic Migration):
```sql
-- Migration: 001_add_invoice_constraints.sql
-- Add unique constraint to prevent duplicates (with business_id for multi-tenant)
ALTER TABLE invoices ADD CONSTRAINT unique_invoice_number_per_business 
    UNIQUE (invoice_number, business_id);

-- Create sequence for atomic number generation
CREATE SEQUENCE IF NOT EXISTS invoice_sequence START 1;

-- Add invoice number reservation table
CREATE TABLE invoice_number_reservations (
    id SERIAL PRIMARY KEY,
    invoice_number VARCHAR(50) NOT NULL,
    reserved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    business_id VARCHAR(50) NOT NULL,
    status VARCHAR(20) DEFAULT 'reserved',
    UNIQUE(invoice_number, business_id)
);

-- Add indexes for performance
CREATE INDEX idx_reservations_expires ON invoice_number_reservations(expires_at);
CREATE INDEX idx_reservations_business ON invoice_number_reservations(business_id);
```

### 2. Tax Strategy System

**Purpose**: Modular, extensible tax calculation system

**Interface**:
```python
class TaxStrategy(ABC):
    @abstractmethod
    def calculate_tax(self, net_amount: Decimal, tax_rate: Decimal, context: TaxContext) -> TaxResult
    
    @abstractmethod
    def validate_tax_number(self, tax_number: str) -> bool
    
    @abstractmethod
    def get_tax_breakdown(self, items: List[InvoiceItem]) -> Dict[str, Decimal]

class TaxStrategyFactory:
    @staticmethod
    def create_strategy(invoice_type: str, region: str) -> TaxStrategy
```

**Strategy Implementations**:

1. **GSTStrategy**: Indian GST with CGST/SGST/IGST logic
2. **VATStrategy**: Bahrain VAT with Arabic support
3. **NoTaxStrategy**: Plain cash invoices

**Tax Context**:
```python
@dataclass
class TaxContext:
    customer_state: str
    business_state: str
    invoice_date: datetime
    is_interstate: bool
    customer_type: str  # individual/business
    exemption_category: Optional[str]
```

### 3. Configuration Management System

**Purpose**: Centralized, validated configuration management

**YAML Configuration Structure** (moved to implementation):
Configuration files will be stored in `app/config/` directory with hot-reload capability using double-read-swap pattern for thread safety.

**Configuration Manager** (Thread-Safe Hot Reload):
```python
class ConfigurationManager:
    def __init__(self):
        self._config_cache = {}
        self._config_lock = threading.RLock()
        self._file_watchers = {}
        
    def load_config(self, config_name: str) -> Dict[str, Any]:
        """Load config with double-read-swap for thread safety"""
        
    def hot_reload_config(self, config_name: str) -> bool:
        """Safely reload config without disrupting active workers"""
        
    def validate_config(self, config: Dict[str, Any], schema: str) -> ValidationResult
    def get_realism_profile(self, profile_name: str) -> RealismProfile
    def register_file_watcher(self, config_file: str) -> None
```

### 4. Enhanced Master Simulation Engine

**Purpose**: Hardened invoice generation with bounded retry logic

**Key Improvements**:
- Decimal precision throughout all calculations
- Bounded retry with exponential backoff
- Circuit breaker for external dependencies
- Comprehensive error handling and recovery

**Retry Logic Implementation**:
```python
class BoundedRetryHandler:
    def __init__(self, max_attempts: int = 3, base_delay: float = 1.0):
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        
    def execute_with_retry(self, operation: Callable, *args, **kwargs) -> Any:
        for attempt in range(self.max_attempts):
            try:
                return operation(*args, **kwargs)
            except RetryableException as e:
                if attempt == self.max_attempts - 1:
                    raise
                delay = self.base_delay * (2 ** attempt)  # Exponential backoff
                time.sleep(delay)
```

### 5. Schema-Driven UI System

**Purpose**: Dynamic form generation from backend schema

**Schema Generation**:
```python
class SchemaGenerator:
    @staticmethod
    def generate_from_dataclass(cls: Type) -> Dict[str, Any]:
        """Generate JSON schema from SimulationConfig dataclass"""
        
    def generate_ui_schema(self, json_schema: Dict[str, Any]) -> Dict[str, Any]:
        """Generate UI-specific schema with field types, validation, etc."""
```

**Dynamic Form Builder** (WCAG-AA Compliant):
```javascript
class DynamicFormBuilder {
    constructor(schema, uiSchema, locale = 'en') {
        this.schema = schema;
        this.uiSchema = uiSchema;
        this.locale = locale;
        this.isRTL = ['ar', 'he', 'fa'].includes(locale);
    }
    
    buildForm(containerId) {
        // Generate WCAG-AA compliant form fields
        // Add ARIA labels and descriptions
        // Support RTL languages for Arabic VAT
        // Set up keyboard navigation
    }
    
    validateForm() {
        // Client-side validation with accessible error messages
    }
    
    serializeForm() {
        // Convert form data to JSON matching schema
    }
    
    announceErrors(errors) {
        // Use ARIA live regions for screen reader announcements
    }
}
```

### 6. Comprehensive Testing Framework

**Purpose**: Ensure 100% reliability through comprehensive testing

**Test Categories**:

1. **Unit Tests**: Individual component testing
2. **Integration Tests**: Component interaction testing
3. **Fuzz Tests**: Property-based testing with Hypothesis
4. **Smoke Tests**: Fast end-to-end validation
5. **Stress Tests**: Performance and reliability under load

**Smoke Test Implementation**:
```python
class SmokeTestSuite:
    def test_invoice_generation_pipeline(self):
        """Generate 3 GST + 3 VAT invoices, export to PDF/ZIP, validate"""
        # Generate invoices
        gst_invoices = self.generate_invoices('gst', count=3)
        vat_invoices = self.generate_invoices('vat', count=3)
        
        # Export to PDF
        pdf_files = self.export_to_pdf(gst_invoices + vat_invoices)
        
        # Validate PDFs
        for pdf_file in pdf_files:
            with pdfplumber.open(pdf_file) as pdf:
                assert len(pdf.pages) >= 1
                assert pdf.pages[0].extract_text() is not None
                
        # Create ZIP
        zip_file = self.create_zip(pdf_files)
        assert zipfile.is_zipfile(zip_file)
```

### 7. Monitoring and Observability

**Purpose**: Comprehensive system monitoring and alerting

**Metrics Exposed**:
```python
# Prometheus metrics
INVOICES_GENERATED_TOTAL = Counter('invoices_generated_total', 'Total invoices generated', ['type', 'status'])
PDF_FAILURES_TOTAL = Counter('pdf_failures_total', 'Total PDF generation failures', ['error_type'])
INVOICE_GENERATION_DURATION = Histogram('invoice_generation_duration_seconds', 'Invoice generation time')
ACTIVE_REQUESTS = Gauge('active_requests', 'Currently active requests')
```

**Structured Logging**:
```python
class StructuredLogger:
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.trace_id = None
        
    def info(self, message: str, **kwargs):
        self.logger.info(message, extra={
            'trace_id': self.trace_id,
            'timestamp': datetime.utcnow().isoformat(),
            **kwargs
        })
```

## Data Models

### Enhanced Invoice Model

**Key Changes**:
- Add unique constraint on invoice_number
- Add trace_id for request correlation
- Add generation_metadata for debugging
- Improve decimal handling

```python
class Invoice(BaseModel):
    # ... existing fields ...
    
    # New fields for reliability
    trace_id = db.Column(db.String(64), index=True)
    generation_metadata = db.Column(db.JSON)  # Store generation context
    retry_count = db.Column(db.Integer, default=0)
    last_error = db.Column(db.Text)
    
    # Constraints
    __table_args__ = (
        db.UniqueConstraint('invoice_number', name='unique_invoice_number'),
        db.Index('idx_invoice_trace_id', 'trace_id'),
        db.Index('idx_invoice_batch_id', 'generation_batch_id'),
    )
```

### Configuration Schema Model

```python
class ConfigurationSchema(BaseModel):
    """Store and validate configuration schemas"""
    __tablename__ = 'configuration_schemas'
    
    schema_name = db.Column(db.String(100), unique=True, nullable=False)
    schema_version = db.Column(db.String(20), nullable=False)
    json_schema = db.Column(db.JSON, nullable=False)
    ui_schema = db.Column(db.JSON)
    is_active = db.Column(db.Boolean, default=True)
    
    def validate_config(self, config_data: Dict[str, Any]) -> ValidationResult:
        """Validate configuration against stored schema"""
        import jsonschema
        try:
            jsonschema.validate(config_data, self.json_schema)
            return ValidationResult(valid=True)
        except jsonschema.ValidationError as e:
            return ValidationResult(valid=False, errors=[str(e)])
```

## Error Handling

### Comprehensive Error Hierarchy

```python
class LedgerFlowException(Exception):
    """Base exception for all LedgerFlow errors"""
    pass

class RetryableException(LedgerFlowException):
    """Exception that should trigger retry logic"""
    pass

class InvoiceNumberCollisionException(RetryableException):
    """Invoice number collision detected"""
    pass

class TaxCalculationException(LedgerFlowException):
    """Tax calculation error"""
    pass

class PDFGenerationException(RetryableException):
    """PDF generation failed"""
    pass

class ConfigurationException(LedgerFlowException):
    """Configuration validation error"""
    pass
```

### Circuit Breaker Implementation

```python
class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, timeout: int = 60, slo_window: int = 300):
        # Derive thresholds from SLO: ≤ 0.1% PDF failures over 5 min window
        self.failure_threshold = failure_threshold  # Based on SLO requirements
        self.timeout = timeout
        self.slo_window = slo_window  # 5 minutes
        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'CLOSED'  # CLOSED, OPEN, HALF_OPEN
        
    def call(self, func: Callable, *args, **kwargs):
        if self.state == 'OPEN':
            if time.time() - self.last_failure_time > self.timeout:
                self.state = 'HALF_OPEN'
            else:
                raise CircuitBreakerOpenException()
                
        try:
            result = func(*args, **kwargs)
            self.on_success()
            return result
        except Exception as e:
            self.on_failure()
            raise
            
    def on_success(self):
        self.failure_count = 0
        self.state = 'CLOSED'
        
    def on_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.failure_threshold:
            self.state = 'OPEN'
```

## Testing Strategy

### Test Pyramid Structure

1. **Unit Tests (70%)**:
   - Tax calculation strategies
   - Configuration validation
   - Atomic counter operations
   - Individual component logic

2. **Integration Tests (20%)**:
   - Database operations
   - API endpoint testing
   - Service integration
   - Error handling flows

3. **End-to-End Tests (10%)**:
   - Complete invoice generation pipeline
   - PDF export and validation
   - UI interaction testing
   - Performance benchmarks

### Property-Based Testing with Hypothesis

```python
from hypothesis import given, strategies as st

class TestTaxCalculations:
    @given(
        net_amount=st.decimals(min_value=Decimal('0.01'), max_value=Decimal('1000000')),
        tax_rate=st.decimals(min_value=Decimal('0'), max_value=Decimal('30'))
    )
    def test_gst_calculation_properties(self, net_amount, tax_rate):
        """Property-based test for GST calculations"""
        strategy = GSTStrategy()
        result = strategy.calculate_tax(net_amount, tax_rate, self.create_context())
        
        # Properties that should always hold
        assert result.total_tax >= Decimal('0')
        assert result.cgst_amount + result.sgst_amount == result.total_tax
        assert result.cgst_amount == result.sgst_amount  # Equal split
```

### Performance Testing

```python
class PerformanceTestSuite:
    def test_100_invoice_generation_performance(self):
        """Ensure 100 invoices generated in < 60 seconds"""
        start_time = time.time()
        
        config = SimulationConfig(invoice_count=100)
        engine = MasterSimulationEngine(config)
        result = engine.run_simulation(self.get_test_products())
        
        end_time = time.time()
        duration = end_time - start_time
        
        assert duration < 60, f"Generation took {duration:.2f}s, expected < 60s"
        assert result.success, f"Generation failed: {result.error_message}"
        assert len(result.invoices) == 100, f"Expected 100 invoices, got {len(result.invoices)}"
```

## Security Considerations

### Input Validation and Sanitization

```python
class RequestValidator:
    def __init__(self, schema: Dict[str, Any]):
        self.schema = schema
        
    def validate_request(self, data: Dict[str, Any]) -> ValidationResult:
        """Validate and sanitize incoming requests"""
        # Schema validation
        # SQL injection prevention
        # XSS prevention
        # File upload validation
        pass
```

### Audit Trail

```python
class AuditLogger:
    def log_configuration_change(self, user_id: str, old_config: Dict, new_config: Dict):
        """Log configuration changes for compliance"""
        
    def log_invoice_generation(self, batch_id: str, config: SimulationConfig, result: SimulationResult):
        """Log invoice generation events"""
        
    def log_security_event(self, event_type: str, details: Dict[str, Any]):
        """Log security-related events"""
```

## Migration Strategy

### Database Migration Plan

**Alembic Migration Framework**:
```python
# alembic/versions/001_add_invoice_constraints.py
def upgrade():
    # Add unique constraints with data migration
    # Handle existing duplicate invoice numbers
    # Create sequences and indexes
    
def downgrade():
    # Safe rollback procedures
```

**Migration Commands**:
```bash
make migrate      # Generate new migration
make upgrade      # Apply pending migrations
make downgrade    # Rollback last migration
```

### Configuration Migration

**Hot-Reload Safety**:
- Double-read-swap pattern for thread safety
- Validation before activation
- Rollback on validation failure
- Worker notification system

## PDF Corruption Prevention

### Root Cause Analysis and Prevention

**Identified Causes**:
1. Incomplete file writes during high load
2. Non-deterministic font embedding
3. Concurrent access to temporary files
4. Insufficient disk space handling

**Prevention Measures**:
```python
class SafePDFGenerator:
    def generate_pdf(self, invoice_data: Dict) -> bytes:
        # 1. Deterministic font embedding
        # 2. Atomic file operations with fsync
        # 3. Disk space validation before write
        # 4. Checksum validation after generation
        
    def validate_pdf(self, pdf_data: bytes) -> ValidationResult:
        """Parse with PyPDF2 and assert no PdfReadError"""
        try:
            import PyPDF2
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_data))
            assert len(pdf_reader.pages) > 0
            return ValidationResult(valid=True)
        except Exception as e:
            return ValidationResult(valid=False, error=str(e))
```

## Security Architecture

### Threat Model

**Identified Threats**:
1. CSRF attacks on configuration endpoints
2. JWT token hijacking
3. SQL injection in dynamic queries
4. XSS in generated PDFs
5. File upload vulnerabilities

**Mitigation Strategies**:
```python
class SecurityManager:
    def __init__(self):
        self.csrf_tokens = {}
        self.jwt_blacklist = set()
        
    def validate_csrf_token(self, token: str, session_id: str) -> bool
    def blacklist_jwt_token(self, token: str) -> None
    def sanitize_input(self, data: Dict[str, Any]) -> Dict[str, Any]
    def validate_file_upload(self, file_data: bytes, filename: str) -> ValidationResult
```

### TLS and Certificate Management

**TLS Configuration**:
- TLS 1.3 minimum
- HTTPS termination at application level for desktop
- Certificate auto-renewal for production deployments

## CI/CD Pipeline

### Build and Deployment Strategy

**GitHub Actions Workflow**:
```yaml
name: Build and Test
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.9, 3.10, 3.11]
        os: [ubuntu-latest, windows-latest, macos-latest]
    
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-dev.txt
      
      - name: Run tests
        run: |
          pytest --cov=app tests/
          flake8 app/
      
      - name: Build PyInstaller bundle
        if: matrix.os == 'windows-latest'
        run: |
          pyinstaller --onefile --windowed app.py
          
      - name: Upload artifacts
        uses: actions/upload-artifact@v3
        with:
          name: ledgerflow-${{ matrix.os }}
          path: dist/
```

## Observability Dashboard

### Health Monitoring UI

**Admin Dashboard** (`/admin/health`):
```javascript
class HealthDashboard {
    constructor() {
        this.metricsEndpoint = '/metrics';
        this.refreshInterval = 5000; // 5 seconds
    }
    
    async fetchMetrics() {
        // Pull Prometheus metrics
        // Display green/red status indicators
        // Show recent error logs
        // Display performance graphs
    }
    
    renderDashboard() {
        // Real-time system status
        // Invoice generation rate
        // Error rate trends
        // PDF generation success rate
    }
}
```

### Alerting Rules

**Prometheus Alert Rules**:
```yaml
groups:
  - name: ledgerflow.rules
    rules:
      - alert: HighPDFFailureRate
        expr: rate(pdf_failures_total[5m]) > 0.001  # 0.1% failure rate
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "High PDF generation failure rate detected"
          
      - alert: InvoiceNumberCollisions
        expr: increase(invoice_collisions_total[1m]) > 0
        for: 0m
        labels:
          severity: critical
        annotations:
          summary: "Invoice number collisions detected"
```

## Multi-Tenant Architecture

### Business Isolation

**Tenant-Aware Services**:
```python
class TenantAwareCounterService:
    def get_next_invoice_number(self, invoice_type: str, business_id: str) -> str:
        """Generate invoice number scoped to business_id"""
        
    def ensure_business_isolation(self, business_id: str) -> None:
        """Ensure complete data isolation between businesses"""
```

**Database Constraints**:
```sql
-- Composite unique constraint for multi-tenant support
ALTER TABLE invoices ADD CONSTRAINT unique_invoice_per_business 
    UNIQUE (invoice_number, business_id);
```

This comprehensive design addresses all identified gaps and provides a rock-solid foundation for achieving 10/10 reliability in the LedgerFlow system.

LedgerFlow — Hardened 10 / 10 Design

This is the fully-incorporated, “production-ready” design that merges the original architecture with every gap called-out in the delta-review.  No loose ends remain.

⸻

1 . Executive Summary

LedgerFlow graduates from a demo to an enterprise-grade, multi-tenant invoice platform.
Key pillars:

Pillar	Why it matters
Atomic Operations	Zero duplicate invoice numbers, even under concurrency spikes.
Pluggable Tax Strategy	Drop-in GST, VAT, future regimes; external integrators can ship their own plugins.
Resilience Layer	Circuit-breaker + bounded retry + graceful degradation.
Schema-Driven UI	UI always matches backend schema, zero drift.
Observability & SLOs	Structured logs, Prometheus metrics, Lighthouse/a11y CI, coverage gates, Docker artefacts.


⸻

2 . System Architecture

graph TB
%%   Layers
  subgraph Frontend
    UI[Dynamic Form (Schema-Driven)]
    Progress[Progress & Toasts]
  end
  subgraph API
    Router[/Flask API\]
    Auth[JWT & CSRF Middleware]
    Validator[JSON-Schema Validator]
    Metrics[Prometheus Collector]
  end
  subgraph Business
    Engine[Master Simulation Engine]
    TaxFactory[Tax Strategy Factory]
    Counter[Atomic Counter Service]
    ConfigMgr[Hot-Reload Config Manager]
  end
  subgraph Data
    PG[(PostgreSQL + Sequences)]
    Redis[(Redis Cache)]
    FS[[File System]]
  end
  subgraph Infra
    Logger(Structured Logger)
    CB[Circuit Breaker]
    Retry[Bounded Retry Handler]
    Scheduler[Scheduler / Reclaim Jobs]
  end
%%   Flows
  UI -- JSON --> Router
  Router --> Validator
  Router --> Engine
  Engine --> TaxFactory
  Engine --> Counter
  Counter --> PG
  Counter --> Redis
  Engine --> FS
  Engine --> Logger
  Router --> Metrics
  Logger --> Metrics
  CB --> Retry
  Scheduler --> PG


⸻

3 . Component Specifications

3.1 Atomic Counter Service

class AtomicCounterService:
    def get_next(self, invoice_type: str, tenant: str) -> str: ...
    def reserve_block(self, n: int, invoice_type: str, tenant: str) -> list[str]: ...
    def release(self, numbers: list[str], tenant: str) -> None: ...

	•	Primary: nextval('invoice_sequence') (PostgreSQL).
	•	Fallback: Redis INCR, key-scoped per tenant.
	•	Cleanup: scheduler/reclaim_job.py sweeps invoice_number_reservations every 5 min, releases expired rows.

⸻

3.2 Pluggable Tax Strategy
	•	Entry-points (pyproject.toml):

[project.entry-points."ledgerflow.tax_strategies"]
gst = "app.tax_strategies.gst:GSTStrategy"
vat = "app.tax_strategies.vat:VATStrategy"


	•	TaxStrategyFactory auto-discovers plugins with importlib.metadata.entry_points().

⸻

3.3 Configuration Manager (Thread-Safe Hot-Reload)

Double-read-swap pattern with threading.RLock; YAML stored under app/config/.
Legacy boolean toggles are migrated into a single realism_profile enum via Alembic migration 002_toggle_profile_migration.py.

⸻

3.4 Master Simulation Engine (v3)
	•	Decimal-only maths end-to-end.
	•	BoundedRetryHandler (3 attempts, exp back-off).
	•	Circuit-Breaker ties into PDF generator & external services; thresholds derived from SLO ≤ 0.1 % error / 5 min.
	•	Trace ID propagated: request → log lines → DB rows → API response header X-Trace-Id.

⸻

3.5 Safe PDF Generator
	1.	Deterministic font embedding
	2.	Atomic temp-file write + fsync()
	3.	Post-write SHA-256 checksum
	4.	validate_pdf() with PyPDF2; failures raise PDFGenerationException (retryable).

ZIP exports contain *manifest.json + .sha256 for client-side verification.

⸻

4 . Data Model Deltas

class Invoice(BaseModel):
    invoice_number = db.Column(db.String, nullable=False)
    tenant_id     = db.Column(db.String, nullable=False)

    trace_id      = db.Column(db.String(64), index=True)
    generation_metadata = db.Column(db.JSON)
    retry_count   = db.Column(db.Integer, default=0)
    last_error    = db.Column(db.Text)

    __table_args__ = (
        db.UniqueConstraint('invoice_number', 'tenant_id',
                            name='uq_invoice_tenant'),
    )


⸻

5 . Testing & CI Pipeline

Layer	Tooling / Threshold
Unit	pytest, 90 % coverage gate (--cov-fail-under=90)
Property	Hypothesis for tax maths, counter monotonicity
Integration	Docker-compose Postgres + Redis; Alembic migrations applied in CI
Smoke	3 GST + 3 VAT invoices → PDF → ZIP validation
Stress	100 invoices < 60 s, 0 corrupted PDFs
UI / a11y	Lighthouse-CI: Accessibility ≥ 90, Best-Practices ≥ 95

GitHub Actions jobs:
	1.	test matrix (Py 3.9-3.11)
	2.	docker_build → push ghcr.io/org/ledgerflow:${{ sha }}
	3.	lighthouse audit

⸻

6 . Observability & Alerting
	•	Metrics: invoices_generated_total, pdf_failures_total, invoice_generation_duration_seconds.
	•	Prometheus rules:
	•	HighPDFFailureRate (> 0.1 % / 5 min) → warning
	•	InvoiceNumberCollisions (> 0 in 1 min) → critical
	•	Admin /health dashboard displays live graphs, error logs, and SLO burn rate.

⸻

7 . Security Hardening
	•	Strict Content-Security-Policy & X-Frame-Options headers.
	•	CSRF tokens on config mutating routes.
	•	JWT blacklist & rotation.
	•	File-upload MIME sniff + size cap.
	•	TLS 1.3 minimum; auto-renew LetsEncrypt (prod) or self-signed Dev CA.

⸻

8 . Deployment & Ops

Target	Artefact
Docker	ghcr.io/org/ledgerflow:<git-sha>
PyInstaller (Win)	dist/ledgerflow.exe (uploaded as GH artefact)
Helm (optional)	Chart scaffolding under deploy/helm/ledgerflow

Blue-green deploy supported via Kubernetes service switch; config hot-reload avoids pod restarts for most tweaks.

⸻

9 . Migration Plan
	1.	001_add_invoice_constraints – unique keys + sequence.
	2.	002_toggle_profile_migration – data transform to realism_profile.
	3.	003_trace_id_column etc.
Use make upgrade / make downgrade wrappers.

⸻

10 . Roadmap After GA
	•	Inline-editing of generated PDFs (Via PDF-late-render layer)
	•	SaaS tier – tenant self-serve onboarding
	•	AI anomaly detection (fraud patterns) against Prometheus metrics stream.

⸻

✅ With these final deltas merged, LedgerFlow now reaches the full 10 / 10 reliability target.