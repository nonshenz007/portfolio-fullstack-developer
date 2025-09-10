# INTERVIEW BRIEF — LedgerFlow

## 1) Snapshot
- Purpose: Professional invoice generator with PDF export, Excel import, and simulation engine; targets SMEs and operations teams needing compliant PDF invoices at scale.
- Users: Admin, auditor, and viewer roles; bulk generation for back-office tasks; dashboard for monitoring.
- Problem: Automates invoice creation with tax compliance, templating, and integrity verification (VeriChain), reducing manual errors and time.

- Tech Stack:
  - Backend: Python 3, Flask `2.3.3`, Flask‑Login, Flask‑CORS, SQLAlchemy `2.x`, Alembic, Redis (optional), Gunicorn.
  - PDF/Office: WeasyPrint, ReportLab, PyPDF2, openpyxl.
  - DB: SQLite (default, `config.py`), Postgres compatible via SQLAlchemy.
  - Infra: Dockerfile + docker‑compose, Make targets, pytest + hypothesis.

- Entry Points / Boot
  - App: `app.py` initializes Flask, SQLAlchemy, LoginManager; registers `app/api/config.py` blueprint; creates admin on first boot.
  - Config: `config.py` centralizes DB URI, folders, and generation/tax settings.
  - Migrations: `alembic/` with `alembic.ini`.

## 2) Architecture Map
- Folder Tree (top 2 levels)
  - `app/`
    - `models/` SQLAlchemy models (Invoice, Product, Customer, User, Settings, TemplateType, BaseModel)
    - `core/` business engines (importers, simulators, PDF/signing, VeriChain, security)
    - `api/` blueprints (e.g., `config.py`)
    - `static/`, `templates/` assets
  - `alembic/` migrations, `Dockerfile`, `requirements.txt`, `tests/`, `templates/`

- Responsibilities
  - `app.py`: Routes (auth, invoices, products, export), extension init, admin bootstrap.
  - `app/models/*`: Domain schema + methods, integrity helpers (hashing, roles).
  - `app/core/*`: “Crystal Core” engines: import, simulate, verify, export, sign, access control.
  - `app/api/config.py`: Runtime config/schema endpoints with hot‑reload.

- Data Flow (typical invoice generation)
  Request → `/api/invoices/generate` → services (catalog/import, simulator, verification) → DB persist (Invoice, Items) → PDF export → Response with IDs/links.

- External Services
  - WeasyPrint/ReportLab for PDF; optional Redis; OS filesystem for exports/certificates; no third‑party SaaS required.

## 3) Interfaces
- REST Endpoints (app.py + blueprint)
  - METHOD | PATH | Auth? | Handler | Validation | Errors
  - POST | `/api/auth/login` | Session | `app.py` | form JSON, password hash | 401 on invalid
  - POST | `/api/auth/logout` | Session | `app.py` | N/A | 200
  - GET  | `/api/auth/status` | Session | `app.py` | N/A | 200/401
  - GET  | `/api/templates` | Session | `app.py` | N/A | 200
  - POST | `/api/products/import` | Admin | `app.py` | file type/size | 400/413
  - GET  | `/api/products` | Session | `app.py` | query params | 200
  - POST | `/api/products` | Admin | `app.py` | JSON schema | 400
  - PUT  | `/api/products/<id>` | Admin | `app.py` | JSON schema | 400/404
  - DELETE | `/api/products/<id>` | Admin | `app.py` | N/A | 404
  - POST | `/api/invoices/generate` | Session | `app.py` | JSON payload | 400/500
  - POST | `/api/invoices/preview` | Session | `app.py` | JSON payload | 400/500
  - GET  | `/api/export/pdf/<invoice_id>` | Session | `app.py` | id path | 404
  - POST | `/api/export/pdf` | Session | `app.py` | JSON selection | 400
  - POST | `/api/invoices/export/pdf/batch` | Session | `app.py` | JSON selection | 400
  - GET  | `/api/admin/status` | Admin | `app.py` | N/A | 200
  - GET  | `/api/pages/<page>` | Session | `app.py` | N/A | 404
  - GET  | `/api/config/status` | Session | `app/api/config.py` | N/A | 200
  - GET  | `/api/config/schema/<name>` | Session | `app/api/config.py` | N/A | 404
  - POST | `/api/config/<name>/validate` | Session | `app/api/config.py` | JSON schema | 400
  - POST | `/api/config/<name>/reload` | Admin | `app/api/config.py` | N/A | 500

- Frontend routes/screens
  - Server‑rendered pages in `app.py`: `/`, `/dashboard`, `/import`, `/generate`, `/manual`, `/export`, `/settings`, `/login`, `/onboarding`.

- CLI/Daemons
  - `run_tests.py` for CI; utilities in `tools/` for validation/triage/audit; gunicorn when containerized.

## 4) Data & Config
- Schemas (SQLAlchemy)
  - `BaseModel` (`app/models/base.py`): `id` PK, timestamps, `to_dict`, `generate_hash`.
  - `Invoice` (`app/models/invoice.py`): invoice_number (unique), type, template_type (Enum), dates, customer FK, subtotal/taxes/total, tax breakdown, status/method, metadata (tenant_id, trace_id, verichain_hash, generation_metadata), business fields, and export references.
  - `Product`, `Customer`, `User` (roles: ADMIN/AUDITOR/VIEWER), `Settings`, `TemplateType`.

- ENV/Secrets (`config.py`)
  - `SECRET_KEY`, `SQLALCHEMY_DATABASE_URI` (defaults to SQLite), upload/export folders, logging level, session cookie policies.

- Migration/Seed
  - Alembic migrations; DB bootstrap in `app.py` (creates admin user if none exists).

## 5) Core Logic Deep Dives
1) `app/core/invoice_generator.py`
   - Generates invoices from catalog/orders; handles template selection and totals; returns in‑DB `Invoice` plus artifacts.
2) `app/core/pdf_template_engine.py` and WeasyPrint integration
   - Renders compliant PDFs from HTML+CSS templates; supports multiple templates.
3) `app/core/verichain_engine.py`
   - Produces integrity hashes and verification logs; exposes verification endpoints.
4) `app/core/excel_importer.py`
   - Reads Excel catalogs (openpyxl), validates schema, upserts products/customers.
5) `app/core/security_manager.py` and `app/core/access_control.py`
   - Centralized access guards (admin_required, auditor_or_admin_required, etc.) used by routes; consistent friendly 403s.
6) `app/api/config.py`
   - Exposes JSON schema, validation and hot‑reload for runtime configs; strict JSON validation and error codes.
7) `app/models/user.py`
   - Role model, password hashing, permission helpers used throughout route guards.

## 6) Reliability, Security, Performance
- Failure Modes: Invalid Excel → 400 with detailed errors; PDF generation exceptions → guarded with error logs and retries; export cleanup helpers.
- Auth: Flask‑Login sessions, secure cookies, role‑based access checks; CORS enabled for admin UI.
- Validation: JSON schema for config, request validation at endpoints, size/type checks for uploads.
- Rate Limiting/CORS: CORS enabled; rate limiting TODO for export/generate burst endpoints.
- Performance: SQL indexes on frequent lookups (ids, trace_id); caching flags in `Config`; batch PDF export avoids N+1 by prefetching.

## 7) Deploy & Ops
- Workflow: Dev (Flask) → CI (pytest/hypothesis) → Docker build → Prod (gunicorn).
- Dockerfiles/CI: `Dockerfile`, `docker-compose.yml`; env‑driven DB; health at `/api/admin/status`.
- Logs/Alerts: Logs in `app/logs`, structured debug toggles; add Prometheus client if needed.

## 8) Testing & QA
- Tests: `tests/` unit + integration; property tests via hypothesis.
- Run: `pytest -q` or `python run_tests.py`.
- Coverage Gaps: Load tests for batch export, edge tax rules, and multi‑tenant isolation.
- Manual Checklist: Login flow, import sample Excel, generate N invoices, preview/download PDF, verify/verichain logs, role guard checks.

## 9) Interview Q&A Pack
1) Where do auth routes live?
   - In `app.py` (e.g., `/api/auth/login`, `/api/auth/status`), backed by `app/models/user.py` with password hashing and role checks.
2) How are invoices generated and verified?
   - `/api/invoices/generate` orchestrates `app/core/invoice_generator.py` then `verichain_engine.py` for integrity; see also PDF export endpoints.
3) How do you validate runtime configs?
   - `app/api/config.py` exposes schema and `/validate` route; uses `get_config_manager().validate_config(...)` returning detailed errors and 400 on invalid.
4) What guards admin actions?
   - Decorators from `app/core/access_control.py` (e.g., `admin_required`) applied to routes handling templates/exports.
5) What’s the default DB and where is it configured?
   - SQLite; set in `config.py` → `SQLALCHEMY_DATABASE_URI`, changeable via env for Postgres.
6) How are PDFs rendered?
   - WeasyPrint/ReportLab; templates under `app/templates/pdf`, HTML/CSS based rendering with WeasyPrint engine.
7) What’s VeriChain?
   - Integrity layer producing hashes and verification records; endpoints: `/api/verichain/*` in `app.py`.
8) How do uploads work safely?
   - `Config.ALLOWED_EXTENSIONS` + `MAX_CONTENT_LENGTH`; files saved under `app/data/uploads` and processed server‑side.
9) How is session security handled?
   - HttpOnly cookies, strong session protection, configurable lifetime; CSRF mitigation for forms; token endpoints are server‑only.
10) How do you avoid N+1?
   - Use joins/prefetch where needed and batch fetch before export; indexing hot fields (trace_id, invoice_number).
11) How are migrations handled?
   - Alembic; run via CLI; models map 1:1 to migration revisions.
12) How do you debug a failed PDF export?
   - Reproduce with small payload on `/api/export/pdf`, inspect logs in `app/logs`, capture HTML preview, add guard/retry around renderer.

- Debugging stories
  - Excel schema drift: Detected via openpyxl validation; returned 400 with row/column hints; added column mapping and stricter schema.
  - WeasyPrint edge fonts: PDF glyph fallback broke totals; embedded fonts + preflight fixed; regression test added.

- Scalability tradeoff
  - Chose synchronous generation for simplicity; at high volume, move long‑running export to background workers and streaming downloads.

- Security hardening step
  - Centralized role checks; added trace_id correlation and tamper detection flags; locked upload types and size limits.

- If I had 1 week
  - Add rate limiting + background queue (RQ/Celery) for batch exports, DB indexes review, and audit log viewer with filters.

## 10) Flash Cards
- “Auth/session via Flask‑Login; roles gate dangerous routes.”
- “Default DB is SQLite; switch via `SQLALCHEMY_DATABASE_URI`.”
- “PDFs rendered by WeasyPrint/ReportLab templates.”
- “Config schema validated at `/api/config/*`.”
- “Excel importer normalizes catalog and upserts.”
- “VeriChain records integrity hashes per invoice.”
- “Exports: single and batch with zipped delivery.”
- “Admin bootstrap creates default admin if none.”
- “Error → 400 on validation; 500 guarded with logs.”
- “Uploads validated by extension + size.”
- “Trace IDs correlate requests in logs.”
- “Alembic tracks schema versions.”
- “CORS enabled for UI; secure cookies for sessions.”
- “Performance flags in `Config` for caching.”
- “Gunicorn container entry for prod.”

---

## Universal Hot‑Seat Prep
- Walkthrough: Snapshot → App init in `app.py` → Core flow: import products → generate invoices → export PDFs → Deploy via Docker/Gunicorn.
- Why this stack: Mature ecosystem, rich PDF tooling, strong ORM, quick to deliver with Flask’s simplicity.
- Debug a prod 500: Repro failing route, inspect logs with trace_id, isolate module (PDF/import), add guard/retry; postmortem with actionable fixes.
- Explain auth: Session cookies, role model in `app/models/user.py`, secure login/logout, role‑gated endpoints.
- Scale to 10×: Move batch work to queues, add caching, DB indexing, streaming downloads, rate limiting.

## 60‑Minute Cram Checklist
1) Read this brief; open `app.py` and `app/models/invoice.py`.
2) Memorize three endpoints and one model.
3) Dockerfile + run command; DB URI in `config.py`.
4) Fix idea: queue exports; Perf idea: prefetch joins for batch.

## Red Flags to Avoid
- Don’t over‑index on libraries—explain why choices drive outcomes.
- If unsure: “I’d confirm the exact call signature, but logic is X → Y → Z, implemented in `app.py` lines ~A–B.”
- Keep answers 30–45s, reference file paths.

