# Implementation Plan

- [x] 1. Set up database migration framework and atomic counter service
  - Create Alembic migration configuration with PostgreSQL support
  - Implement atomic counter service using DB sequences (primary) and Redis INCR (fallback) to handle ≤ 1,000 req/s
  - Add composite unique constraints (invoice_number, tenant_id) for multi-tenant support
  - Implement retry logic (≤ 3 attempts) with InvoiceNumberCollisionException
  - Execute DB migration 001: Add sequences + unique constraints with duplicate scan & fix
  - _Requirements: FR-1, FR-7, Migration DB-001_

- [x] 2. Implement tax strategy pattern system with plugin support
  - Create abstract TaxStrategy base class accepting TaxContext and outputting TaxResult with Decimal precision
  - Implement GSTStrategy with unit tests proving CGST = SGST split logic
  - Implement VATStrategy with rounding rules and Arabic locale support
  - Implement NoTaxStrategy for plain cash invoices
  - Add entry_points configuration for plugin discovery (≤ 1 day integration target)
  - Create comprehensive unit tests for all tax calculation strategies
  - _Requirements: FR-2, NFR Internationalization_

- [x] 3. Create centralized configuration management with hot-reload
  - Implement configuration in app/config/*.yaml with JSON-Schema validation
  - Return HTTP 400 with validation errors for unknown keys
  - Implement hot-reload using double-read-swap pattern (zero downtime)
  - Execute DB migration 002: Migrate boolean toggles to realism_profile enum (basic, realistic, advanced)
  - Add SIGHUP signal handler for config reload
  - _Requirements: FR-3, Migration DB-002, DO-4_

- [x] 4. Harden Master Simulation Engine with decimal precision and resilience
  - Replace all float calculations with Decimal throughout the engine
  - Implement retryable failures (network, PDF) with ≤ 3 retries and exponential back-off
  - Mark failed batches with last_error after max retries
  - Allow partial success with per-invoice failure reporting in UI
  - Execute DB migration 003: Add trace_id, generation_metadata, retry_count, last_error columns
  - _Requirements: FR-9, Migration DB-003_

- [x] 5. Implement comprehensive testing framework with quality gates
  - Achieve pytest --cov ≥ 90% coverage with gate enforcement
  - Implement ruff & mypy --strict static analysis (clean)
  - Create Hypothesis property tests for tax maths and counter monotonicity
  - Set up CI matrix: Python 3.9-3.11, OS: Ubuntu, Windows, macOS
  - Create tests/perf/test_generate_100.py benchmark (≤ 60s target)
  - Add Lighthouse accessibility CI with score thresholds
  - _Requirements: QA Requirements 1-6_

- [ ] 6. Create schema-driven UI system with accessibility compliance
  - Build /generate form client-side from /api/schema/simulation-config endpoint
  - Auto-remove/add fields when backend schema changes with sensible defaults
  - Implement client validation matching server JSON-Schema
  - Add accessible error messages with ARIA live regions (WCAG-AA)
  - Support Arabic locale with RTL rendering
  - Execute Config migration 001: Generate JSON-Schema from SimulationConfig
  - _Requirements: FR-4, FR-11, NFR Internationalization, Migration Config-001_

- [ ] 7. Implement monitoring and alerting system
  - Expose /metrics with Prometheus counters: invoices_generated_total, pdf_failures_total, histogram invoice_generation_duration_seconds
  - Create alert rules: PDF failure rate > 0.1% (5 min) → warning, Invoice collisions > 0 (1 min) → critical
  - Build /admin/health dashboard with 5s refresh rate
  - Label metrics by tenant but expose only to that tenant's dashboard
  - Implement immutable audit logs queryable via /admin/audit
  - _Requirements: FR-8, FR-7, NFR Auditability_

- [ ] 8. Build PDF export system with integrity validation
  - Export 100 invoices to single ZIP in < 10s
  - Ensure each PDF passes PyPDF2 parse test with 0 corrupted files
  - Include manifest.json with SHA-256 checksums in ZIP
  - Stream export with Content-Disposition: attachment header
  - Achieve P95 export time ≤ 5s
  - _Requirements: FR-6, FR-10_

- [ ] 9. Implement security and file handling
  - Implement JWT with rotation and CSRF on mutating routes
  - Add file upload scanning for security
  - Support .xlsx, .xls files up to 5 MB with required columns: Product Name, Base Price (case-insensitive)
  - Create mapping wizard showing detected fields before commit
  - Import ≥ 10,000 rows in ≤ 30s on 4-core laptop
  - Achieve OWASP ZAP report with 0 high/critical issues
  - _Requirements: FR-5, NFR Security_

- [ ] 10. Implement performance optimization and SLO compliance
  - Generate 100 invoices (mixed GST/VAT) in ≤ 60s on 2 CPU/4GB RAM
  - Achieve P95 export time ≤ 5s
  - Pass memory leak test (1,000 batch loop) with RSS delta < 5%
  - Ensure < 0.1% failed invoices/month reliability target
  - Implement graceful degradation under load
  - _Requirements: FR-10, NFR Reliability_

- [ ] 11. Set up deployment and operations pipeline
  - Create GitHub Actions to build Docker image ghcr.io/org/ledgerflow:<sha> on every push to main
  - Implement blue-green deploy script with Kubernetes service swap after readiness probes pass (60s)
  - Configure Alembic migrations to auto-run on pod start (alembic upgrade head) with downgrade safeguards
  - Verify portability on macOS, Linux, Windows with make dev-up setup in ≤ 5 min
  - _Requirements: DO-1, DO-2, DO-3, NFR Portability_

- [ ] 12. Implement multi-tenant data isolation
  - Scope every API call by tenant_id in JWT
  - Forbid cross-tenant queries using SQLAlchemy filters
  - Enforce composite unique key invoice_number + tenant_id
  - Label metrics by tenant but expose only to that tenant's dashboard
  - Implement strict data isolation validation and testing
  - _Requirements: FR-7_

- [ ] 13. Implement internationalization and accessibility
  - Externalize UI text to i18n JSON files
  - Support RTL rendering for Arabic VAT users
  - Ensure Arabic VAT users can complete full flow
  - Achieve Lighthouse accessibility score ≥ 90
  - Implement colour contrast ratio ≥ 4.5:1
  - Add ARIA live regions for dynamic error announcements
  - _Requirements: FR-11, NFR Internationalization_

- [ ] 14. Implement maintainability and code quality
  - Ensure new tax strategy can be added with < 200 LOC change outside plugin
  - Pass CodeQL & flake8 analysis
  - Maintain cyclomatic complexity < 15 per function
  - Implement comprehensive error handling and logging
  - Create developer documentation and plugin examples
  - _Requirements: NFR Maintainability_

- [ ] 15. Final validation and production readiness
  - Validate all functional requirements (FR-1 through FR-11) are met
  - Confirm all non-functional requirements (reliability, maintainability, security, portability, internationalization, auditability) are satisfied
  - Execute all quality assurance requirements (test coverage, static analysis, property tests, CI matrix, performance bench, accessibility CI)
  - Verify deployment & ops requirements (Docker builds, blue-green deploy, migrations, config hot-reload)
  - Complete all migration requirements (DB migrations 001-003, Config migration 001)
  - Achieve 10/10 production-grade status certification
  - _Requirements: All FR, NFR, QA, DO, and Migration requirements_