LedgerFlow — Comprehensive Requirements v2.0

Scope: Everything the product must do to reach the 10 / 10 reliability, maintainability and usability target.

⸻

1 . Functional Requirements

Ref	User Story	Acceptance Criteria
FR-1	As a system administrator I never want duplicate invoice numbers, so that audits always pass.	1. Concurrency ≤ 1 000 req/s yields 0 collisions.2. Invoice numbers are allocated atomically via DB sequence (primary) or Redis INCR (fallback).3. Duplicate detected ⇒ system retries (≤ 3) then raises InvoiceNumberCollisionException.4. DB column (invoice_number, tenant_id) has a unique constraint.
FR-2	As a developer I want tax rules to be pluggable, so that new countries are drop-in.	1. Tax logic implemented as Strategy plugins discoverable by entry_points.2. GST, VAT, No-Tax strategies ship OOTB; new strategy integrates in ≤ 1 day.3. All strategies accept TaxContext and output TaxResult with Decimal precision.4. Unit tests prove GST split (CGST = SGST) and VAT rounding rules.
FR-3	As an operator I configure behaviour once, in YAML, and it hot-reloads safely.	1. Configuration lives under app/config/*.yaml, validated against JSON-Schema.2. Unknown keys → HTTP 400 with validation errors.3. Hot-reload uses double-read-swap; no downtime.4. Legacy boolean toggles merged into realism_profile enum (basic, realistic, advanced).
FR-4	As a business user I generate invoices through a guided UI that auto-updates when backend schema changes.	1. /generate form is built client-side from /api/schema/simulation-config.2. Removed fields disappear automatically; new fields render with sensible defaults.3. Client validation matches server JSON-Schema; failing fields announce accessible error messages (WCAG-AA).4. Arabic locale renders RTL correctly.
FR-5	As a user I import products from Excel with confidence.	1. Supported files: .xlsx, .xls, max 5 MB.2. Required columns: Product Name, Base Price (case-insensitive).3. Mapping wizard shows detected fields before commit.4. ≥ 10 000 rows import in ≤ 30 s on a 4-core laptop.
FR-6	As a user I export results as PDF or ZIP without corruption.	1. 100 invoices export to single ZIP < 10 s.2. Each PDF passes PyPDF2 parse test; 0 corrupted files.3. ZIP contains manifest.json + SHA-256 checksums.4. Export endpoint streams file with Content-Disposition: attachment.
FR-7	As a tenant admin I need strict data isolation.	1. Every API call is scoped by tenant_id in JWT.2. Cross-tenant queries forbidden by SQLAlchemy filter.3. Composite unique key invoice_number + tenant_id enforced.4. Metrics are labelled by tenant but exposed only to that tenant’s dashboard.
FR-8	As an operator I need clear system health & alerts.	1. /metrics exposes Prometheus counters: invoices_generated_total, pdf_failures_total, histogram invoice_generation_duration_seconds.2. Alert rules:  a. PDF failure rate > 0.1 % (5 min) → warning.  b. Invoice collisions > 0 (1 min) → critical.3. /admin/health dashboard refreshes every 5 s.
FR-9	As a user I expect generation to finish or fail gracefully.	1. Retryable failures (network, PDF) retried ≤ 3 with exponential back-off.2. After max retries the batch is marked failed with last_error.3. Partial success allowed; failures reported per-invoice in UI.
FR-10	As a performance tester I need the system to meet SLOs.	1. Generate 100 invoices (mixed GST/VAT) in ≤ 60 s on 2 CPU / 4 GB RAM.2. P95 export time ≤ 5 s.3. Memory leak test (1 000 batch loop) shows RSS delta < 5 %.
FR-11	As an accessibility assessor I need AA compliance.	1. Lighthouse a11y score ≥ 90.2. All form inputs labelled; dynamic errors announced via ARIA live regions.3. Colour contrast ratio ≥ 4.5 : 1.


⸻

2 . Non-Functional Requirements

NFR	Description	Measure
Reliability	Invoice generator must run 24 × 7 with graceful degradation.	< 0.1 % failed invoices / month.
Maintainability	New tax strategy added with < 200 LOC change outside plugin.	CodeQL & flake8 pass; cyclomatic complexity < 15 per fn.
Security	JWT w/ rotation; CSRF on mutating routes; file upload scanning.	OWASP ZAP report: high/critical issues = 0.
Portability	Runs via Docker; dev setup make dev-up within 5 min.	Verified on macOS, Linux, Windows.
Internationalisation	UI text externalised to i18n JSON; RTL supported.	Arabic VAT users can complete full flow.
Auditability	Every config change, generation job & security event recorded.	Audit logs immutable, queryable via /admin/audit.


⸻

3 . Quality-Assurance Requirements
	1.	Test Coverage Gate: pytest --cov must report ≥ 90 %.
	2.	Static Analysis: ruff & mypy --strict clean.
	3.	Property Tests: Hypothesis suite green (tax maths, counter monotonicity).
	4.	CI Matrix: Python 3.9 – 3.11, OS: Ubuntu, Windows, macOS.
	5.	Performance Bench: tests/perf/test_generate_100.py under 60 s.
	6.	Accessibility CI: Lighthouse score thresholds enforced.

⸻

4 . Deployment & Ops Requirements

Req	Detail
DO-1	GitHub Actions builds Docker image ghcr.io/org/ledgerflow:<sha> on every push to main.
DO-2	Blue-green deploy script swaps Kubernetes service after readiness probes pass (all healthchecks green for 60 s).
DO-3	Alembic migrations auto-run on pod start (alembic upgrade head) with safe-guard for downgrades.
DO-4	Config hot-reload: SIGHUP → ConfigManager reloads YAML; zero-downtime.


⸻

5 . Migration Requirements
	1.	DB 001: Add sequences + unique constraints (duplicate scan & fix).
	2.	DB 002: Migrate boolean toggles to realism_profile ENUM.
	3.	DB 003: Add trace_id, generation_metadata, retry_count, last_error.
	4.	Config 001: Generate JSON-Schema from SimulationConfig; serve at /api/schema/simulation-config.

⸻

✅ Meeting every item herein is necessary and sufficient for LedgerFlow to claim “10 / 10 production-grade” status.