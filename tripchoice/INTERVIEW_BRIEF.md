# INTERVIEW BRIEF — TripChoice

## 1) Snapshot
- Purpose: Full‑featured travel package platform with dynamic pricing, CMS‑managed content, and lead generation; targets small/mid travel operators and marketing teams.
- Users: Sales reps, content editors, and end‑customers exploring packages on mobile/desktop.
- Problem: Centralizes package content + pricing logic and serves fast, accessible pages with graceful CMS fallbacks.

- Tech Stack:
  - Frontend: Next.js `14.2.32`, React `18.3`, TypeScript, TailwindCSS, Radix UI, Framer Motion, TanStack Query, Zod.
  - CMS/DB: Directus `10.x` (PostgreSQL), Directus Files CDN.
  - Infra: Node `>=18`, Vercel (frontend), Docker Compose for local Directus, Playwright/Cypress for QA.

- Entry Points / Boot:
  - App Router root: `apps/web/src/app/layout.tsx`, `apps/web/src/app/page.tsx`.
  - Scripts: `package.json` workspace scripts; dev via `npm run dev` (calls `dev-safe.js`) then Next `dev` in `apps/web`.
  - CMS seed/import: `directus/import-seed.js` and schema `directus/snapshot.json`.

## 2) Architecture Map
- Folder Tree (top 2 levels)
  - `apps/web/src/`
    - `app/` routes (App Router), global error/not-found, layout
    - `components/` UI + slices (Hero, Trust, search, grids)
    - `lib/` CMS access, pricing engine, analytics, validations
    - `hooks/` pricing hooks wrapped in TanStack Query
    - `types/` shared domain types
  - `directus/` schema snapshot and seed script
  - `cypress/`, `playwright.config.ts` end‑to‑end tests
  - `docs/`, `qa/` author docs and audit guides

- Component Responsibilities
  - `src/lib/pricing.ts`: Deterministic pricing engine with seasonal/weekend/origin multipliers and variant/rooming deltas.
  - `src/lib/cms.ts`: CMS client + rich fallback data for offline/seeded states.
  - `src/hooks/use-pricing.ts`: Orchestrates price rules + flash sales via React Query and returns computed breakdowns.
  - `src/app/*`: Route components, page composition, SEO, and SSR/ISR hooks.

- Data Flow
  1) UI route renders → components request data via `lib/cms.ts` or fallback.
  2) `use-pricing.ts` fetches price rules/flash sales and computes `PriceBreakdown` with `getPrice()`.
  3) User interactions (filters/date/variant) recompute memoized pricing → UI updates.

- External Services
  - Directus REST: seeded collections (packages, variants, reviews, rules). Seed/import in `directus/import-seed.js`.

## 3) Interfaces
- REST Endpoints (Internal): Next.js API routes are not used; data comes from Directus REST externally. Seed script uses Directus:
  - METHOD | PATH | Auth? | Handler | Validation | Errors
  - POST | `${DIRECTUS_URL}/items/<collection>` | Bearer | `directus/import-seed.js` | JSON schema at Directus | HTTP 4xx/5xx handled in script

- Frontend Routes (App Router)
  - `/` → `src/app/page.tsx` → uses `lib/cms.getPackages()`; fallback cards inline.
  - `/explore` → `src/app/explore/*` → grid + filters, `hooks/use-pricing`.
  - `/packages` → `src/app/packages/*` → listing and detail composition.
  - `/package` → `src/app/package/*` → detail/booking shell (variants, breakdown).
  - `/docs` → `src/app/docs/*` → author/ops docs.
  - Error screens: `src/app/error.tsx`, `not-found.tsx`.

- CLI / Jobs
  - `directus/import-seed.js` → seeds collections/files.
  - `scripts/ui-police.js`, `scripts/audit_images.py` → UI/image audits.

## 4) Data & Config
- Database Schemas (Directus snapshot excerpts)
  - `packages` (uuid id, slug unique, title, summary, destinations json, themes json, duration_days int, base_price_pp int, min_pax int, max_pax int, hero file uuid → `directus_files`, gallery json, inclusions/exclusions json, policies text, timestamps).
  - Related: variants, reviews, itinerary_days, price_rules, flash_sales (see `directus/snapshot.json`).

- ENV / Secrets
  - `DIRECTUS_URL`, `DIRECTUS_TOKEN` control CMS connectivity and auth (see `DEPLOYMENT.md`).

- Migration/Seed
  - Apply `directus/snapshot.json` then import items with `directus/import-seed.js`. App uses fallbacks if CMS unavailable.

## 5) Core Logic Deep Dives
1) `apps/web/src/lib/pricing.ts:getPrice(pkg, variantType, date, pax, originCity)`
   - Returns `{ pp, breakdown }`; multiplies base by season/weekend/origin; adds variant/rooming deltas; applies early/flash discounts; floors to ≥70% base.
2) `apps/web/src/hooks/use-pricing.ts:usePricing(options)`
   - Fetches price rules/flash sales via React Query; memoizes `PriceBreakdown`; exposes `isLoading`, `error`, `refetch`.
3) `apps/web/src/lib/cms.ts`
   - Provides typed accessors and rich fallback data so UX is resilient without CMS.
4) `apps/web/src/app/page.tsx`
   - Home composition + safety fallback cards if CMS fetch fails; drives top‑level SEO and hero.
5) `apps/web/src/lib/validations.ts` (if present) / Zod usage
   - Input and query param guards for forms/filters; prevents invalid state.
6) `playwright.config.ts` + `cypress/cypress.config.ts`
   - E2E harness for navigation, a11y, and performance budgets.

## 6) Reliability, Security, Performance
- Failure Modes: CMS offline → fallback data; image/CDN issues → placeholders; query errors surfaced via `error` boundary.
- Validation: Zod on inputs; type‑safe fetch; basic sanitization for query params.
- CORS/Auth: Frontend reads public Directus endpoints via server proxy or token on server (seed uses admin token only in CI/local).
- Performance: ISR/SSG where viable; TanStack Query caching; pricing is O(1); images optimized; Lighthouse tracked in `qa/`.

## 7) Deploy & Ops
- Workflow: Dev (local Next + Docker Directus) → Preview (Vercel) → Prod (Vercel + managed Directus/Postgres).
- Docker/CI: `docker-compose.yml` brings up Directus/Postgres; scripts seed; Playwright smoke during CI.
- Observability: Web Vitals, Vercel analytics; basic health checks from platform; manual runbooks in `DEPLOYMENT.md`.

## 8) Testing & QA
- Test Homes: `cypress/`, `tests/`, `playwright.config.ts`.
- Run: `npm run test:ui` (Playwright), Cypress via UI/CLI.
- Coverage Gaps: Deep CMS contract tests; image CDN failure simulations; rate‑limit behavior.
- Manual Checklist: Load `/`, explore filtering, package detail, pricing breakdown, mobile layout, keyboard nav, images lazy‑load.

## 9) Interview Q&A Pack
1) How is dynamic pricing computed?
   - In `apps/web/src/lib/pricing.ts` via season/weekend/origin multipliers plus variant/rooming deltas and early/flash discounts; returns a typed `PriceBreakdown`.
2) What happens if Directus is down?
   - `lib/cms.ts` exposes comprehensive fallback data; pages like `src/app/page.tsx` render meaningful defaults and keep UX functional.
3) Where are price rules and flash sales fetched?
   - `src/hooks/use-pricing.ts` using TanStack Query with `staleTime` of 30m and 5m respectively.
4) How do you ensure accessibility?
   - Radix primitives, semantic markup, tab/ARIA audit docs in `docs/` and `qa/a11y-testing-protocol.md`; Lighthouse budgets in `qa/`.
5) How are routes structured?
   - App Router under `src/app/*` with localized error/not‑found boundaries and a shared layout.
6) What external API contract exists?
   - Directus REST; schema captured in `directus/snapshot.json`; seed script `directus/import-seed.js` uses bearer auth.
7) Any SSR/ISR strategies?
   - Pages support static rendering with incremental revalidation for stable content; client‑side hooks for pricing interactivity.
8) How is type safety enforced?
   - `types/`, Zod validations for inputs, and typed fetch wrappers in `lib`.
9) Where are performance concerns tracked?
   - `PERFORMANCE.md`, `PERFORMANCE_REPORT.md`, plus Playwright trace; images pre‑optimized and lazy‑loaded.
10) How is image content handled?
   - `scripts/audit_images.py` and authoring guides in `docs/` ensure appropriate sizes and ART direction.
11) Any security considerations with tokens?
   - Admin tokens used only for local import; production uses server‑side environment with least privilege; no tokens on client.
12) How to add a new collection?
   - Update Directus schema, re‑apply `snapshot.json`, extend `lib/cms.ts` and downstream types/components.

- Debugging stories
  - CMS outage fallback: Simulated Directus 500s and verified `lib/cms.ts` fallbacks kept pages interactive; added retry/backoff and user messaging.
  - Pricing edge dates: Incorrect weekend detection around timezone boundaries; fixed by using `date.getDay()` consistently and tests in `hooks/use-pricing.ts` consumers.

- Scalability tradeoff
  - Chose CMS‑driven content with client caching over building a custom backend; faster iteration, but adds dependency on Directus uptime—mitigated via fallbacks and ISR.

- Security hardening step
  - Enforced server‑only usage of tokens; added Zod input guards and sanitization for filter/query params to prevent injection into fetch queries.

- If I had 1 week (impact → effort)
  - Add server actions for pricing precompute with caching (H), implement content webhooks to revalidate pages (M), and add contract tests against Directus snapshot (M).

## 10) Flash Cards
- “Pricing = base × season × weekend × origin ± deltas − discounts.”
- “Fallback data ensures UX when CMS is offline.”
- “Routes live in `src/app/*` with layout/error/not‑found.”
- “Directus schema tracked in `directus/snapshot.json`.”
- “Seeding uses `directus/import-seed.js` + bearer token.”
- “React Query caches price rules and flash sales.”
- “Zod validates inputs before computing pricing.”
- “Images are optimized; docs cover a11y and performance.”
- “Playwright/Cypress cover happy paths and smoke.”
- “SSR/ISR for stable pages; client hooks for live pricing.”
- “ENV: `DIRECTUS_URL`, `DIRECTUS_TOKEN` (server‑side).”
- “Types are centralized in `src/types`.”
- “UI built with Tailwind + Radix + Framer Motion.”
- “WCAG AA targeted; docs in `qa/` and `docs/`.”
- “Production: Vercel + managed Directus/Postgres.”

---

## Universal Hot‑Seat Prep
- Walkthrough: Snapshot → Arch Map (app/lib/hooks/directus) → Core flow: user picks variant/date → `use-pricing` → `getPrice` → render breakdown → Deploy: Vercel + Directus.
- Why this stack: Fast iteration, rich ecosystem, strong a11y and SSR/ISR story; Directus accelerates content ops.
- Debug a prod 500: Repro with failing Directus; inspect logs and fetch callers; add try/catch with user‑facing fallback; postmortem with SLA and monitors.
- Explain auth: No user auth in FE; Directus access via server env/token; public reads only client‑side.
- Scale to 10×: Cache reads, ISR with webhooks, CDN images, background jobs for computation, and rate‑limit seed/admin endpoints.

## 60‑Minute Cram Checklist
1) Read this brief aloud; open `src/lib/pricing.ts`.
2) Skim `src/app/page.tsx` and one explore/detail route.
3) Memorize 3 facts: Next 14.2, Directus 10, `getPrice()` formula.
4) Prepare one bug fix (timezone weekend) + one perf idea (server‑cached pricing).

## Red Flags to Avoid
- Don’t drift into tool trivia—focus on outcomes and contracts.
- If unsure: “I’d verify the exact call signature, but the logic is X → Y → Z, implemented in `apps/web/src/lib/pricing.ts`.”
- Keep answers crisp (30–45s) and concrete.

