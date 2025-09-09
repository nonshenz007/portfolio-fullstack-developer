# INTERVIEW BRIEF — ChaiOS (Cross‑Platform POS)

## 1) Snapshot
- Purpose: Cross‑platform POS with inventory, sales tracking, reporting, and offline‑first storage; deployable to Android/iOS/Web/Desktop.
- Users: Store owners and staff; biometric/device security optional; responsive UI for tablets and PCs.
- Problem: Reliable sales and inventory operations without constant connectivity, with export/printing.

- Tech Stack
  - App: Flutter `3.x`, Provider, Hive/Hive‑Flutter, local_auth, secure storage, Sentry.
  - Backend (optional, local): Node/Express (`backend/server.js`) for health/version/license mock.
  - Reporting: `pdf`/`printing` packages, CSV exports.

- Entry Points / Boot
  - Flutter: `lib/main.dart` initializes Logging, GlobalErrorHandler, HiveService, migrations, then runs `ChaiOS` app.
  - Providers: `SalesProvider`, `SettingsProvider`, `AuthProvider`, `AppShellController` wired in `ChaiOS` widget.
  - Backend: `backend/server.js` (Express) with `/health`, `/version`, `/license/validate`.

## 2) Architecture Map
- Folder Tree (top 2 levels)
  - `lib/`
    - `core/` (app_shell, hive service, security/auth, navigation, api config)
    - `features/` (sales, settings, home) with providers + screens
    - `theme/` styles
    - `main.dart`
  - `backend/` Node Express server for utility endpoints

- Responsibilities
  - `core/database/hive_service.dart`: Box registration, init, migrations, backups.
  - `core/security/auth_provider.dart`: App lock/biometric gating.
  - `features/*/providers`: Domain state + persistence; `SalesProvider` drives POS flows.
  - `core/app_shell.dart` and `core/navigation/bottom_nav_controller.dart`: Scaffold and navigation.

- Data Flow
  - UI → Provider action → Hive persistence (offline) → UI updates; optional backend endpoints for license/health checks.

- External Services
  - Optional Express backend; Sentry telemetry.

## 3) Interfaces
- Backend REST (Express)
  - METHOD | PATH | Auth? | Handler | Validation | Errors
  - GET | `/health` | No | `backend/server.js` | N/A | 200
  - GET | `/version` | No | `backend/server.js` | N/A | 200/500
  - GET | `/` | No | `backend/server.js` | N/A | 200
  - POST | `/license/validate` | No | `backend/server.js` | `{ key: string }` | 400/500

- Frontend Routes/Screens (Flutter)
  - `/home` → `features/home/screens/home_screen.dart`
  - `/settings` → `features/settings/screens/settings_screen.dart`
  - `/onboarding` → `features/settings/screens/onboarding_screen.dart`
  - Root gate renders `OnboardingScreen` or `LockScreen` or `AppShell` via `_RootGate` in `main.dart`.

- CLI/Jobs
  - N/A for the Flutter app; use `flutter build` targets; backend `npm start`.

## 4) Data & Config
- Hive Boxes / Models
  - See `core/hive_boxes.dart` and providers for schemas; indexes implemented via box keys; relationships handled in app logic.

- ENV/Secrets
  - Flutter config (e.g., API base, Sentry DSN) in constants or runtime config; backend uses `PORT`.

- Migration/Seed
  - `HiveService.migrate()` performs local migrations; onboarding flow seeds defaults.

## 5) Core Logic Deep Dives
1) `lib/main.dart`
   - Boot sequence: Logging → Error Handler → Hive init/migrate → Sentry → Providers → Root gate.
2) `core/database/hive_service.dart`
   - Opens/registers boxes, handles schema versions, and compaction.
3) `features/sales/providers/sales_provider.dart`
   - Sales lifecycle, totals, and receipt generation hooks.
4) `core/security/auth_provider.dart` + `core/security/lock_screen.dart`
   - App lock, biometric auth integration, idle timeout.
5) `core/app_shell.dart` + bottom nav
   - Main shell, layout responsiveness, routing.

## 6) Reliability, Security, Performance
- Failure Modes: Hive corruption → safe reopen/migrate; auth failures → lockout; printing not available → fallbacks.
- Security: Optional biometric via `local_auth`; secure storage for sensitive keys; gate settings by role if enabled.
- Performance: Offline‑first with Hive; lazy lists; limited rebuilds via Provider; batched writes.

## 7) Deploy & Ops
- Flutter build: `flutter build apk/ipa/web/windows/linux`.
- Backend: `npm start` in `backend/` (Express 5.1).
- Logging: `LoggingService` centralizes logs; Sentry DSN optional.

## 8) Testing & QA
- Tests: `integration_test/` and widget tests (if present).
- Manual: Onboarding → add sale → view analytics → lock/unlock → export/print sample.
- Coverage gaps: Edge sync/merge across devices; inventory rebuild.

## 9) Interview Q&A Pack
1) How does the app decide the first screen?
   - `_RootGate` in `main.dart` checks `SettingsProvider.isAppSetup` and `AuthProvider.isLocked`.
2) Where are migrations handled?
   - `HiveService.migrate()` invoked during boot.
3) What’s the offline story?
   - Hive local storage for all critical entities; providers synchronize UI state.
4) How is authentication enforced?
   - `AuthProvider` + `LockScreen`; optional biometrics via `local_auth`.
5) How do you add a new feature area?
   - Create `features/<name>/providers` and `features/<name>/screens`, wire into `routes` in `ChaiOS`.
6) Any backend dependencies?
   - Optional Express server for license/health; core app works offline.
7) How are errors captured?
   - `GlobalErrorHandler` and Sentry integration.
8) How are receipts generated?
   - `pdf` + `printing` packages; invoked from provider flows.
9) How do you keep UI responsive?
   - Provider pattern, async IO, batched Hive ops.
10) How do you protect data?
   - Encrypted storage options and biometric lock; minimize PII.
11) How do you theme?
   - `theme/app_theme.dart` centralizes color/typography.
12) What’s your testing strategy?
   - Integration tests for core flows; manual smoke on target platforms.

- Debugging stories
  - Hive migration edge: recovered by staged migration and fallback defaults; added backup before upgrade.
  - Print scaling bug: DPI mismatch fixed by device‑aware scaling and paper size presets.

- Scalability tradeoff
  - Local‑only simplifies reliability; for sync multi‑device, add background sync and conflict resolution.

- Security hardening step
  - Screen lock on idle + biometric gating, encrypt sensitive values; review logs for PII.

- If I had 1 week
  - Add store/test fixtures, export/import backup tooling, and basic role permissions for multi‑user shops.

## 10) Flash Cards
- “Root gate: onboarding → lock → app shell.”
- “Offline‑first via Hive; providers drive UI.”
- “Sentry captures crashes; global handler guards init.”
- “Printing via `pdf`/`printing` packages.”
- “Backend optional: Express health/version/license.”
- “Migrations run on boot.”
- “Secure storage + local_auth for lock.”
- “Bottom nav routes the core tabs.”
- “Sales provider owns sales lifecycle.”
- “Responsive layouts for tablet/desktop.”
- “CSV/PDF exports available.”
- “Themes centralized in `app_theme.dart`.”
- “Logging service wraps app‑wide logs.”
- “Boxes defined in `hive_boxes.dart`.”
- “Routes set in `MaterialApp.routes`.”

---

## Universal Hot‑Seat Prep
- Walkthrough: Snapshot → Arch Map (`core`,`features`) → Core flow: sale entry → Hive persist → receipt/export → Deploy builds.
- Why this stack: Excellent cross‑platform reach and offline story; fast UI iteration.
- Debug a prod 500: N/A mobile; repro with logs, isolate provider or IO, add guards; postmortem migration path.
- Explain auth: App lock + biometrics; gated settings if multi‑user enabled.
- Scale to 10×: Background sync, conflict resolution, and paginated lists.

## 60‑Minute Cram Checklist
1) Read this brief; scan `main.dart`.
2) Skim `HiveService` and one provider.
3) Memorize: Root gate logic, one export path.
4) Prepare 1 migration fix + 1 perf idea.

## Red Flags to Avoid
- Don’t drown in plugin details; describe flows.
- If unsure: “I’d verify X, but concept is Y. Implemented in `lib/main.dart`.”
- Keep answers tight and outcome‑oriented.

