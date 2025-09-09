# backend — INTERVIEW_BRIEF

1) Snapshot
- Purpose: TODO. Users: TODO. Problem: TODO.
- Stack & versions: Express
- Build commands:
- `npm run start`
- Entry points & boot:
- `npm run start`
- `server.js`

2) Architecture Map
- Folder tree (top 2 levels):
```
backend/
  backend/
    package-lock.json
    package.json
  package-lock.json
  package.json
  server.js
```
- Component responsibilities: TODO
- Data flow: request → controller/service → db/cache → response (map with file pointers) — TODO
- External services/APIs: TODO (list and where used)

3) Interfaces
- REST Endpoints (Node/Express etc.):
| METHOD | PATH | Auth? | Handler file | Notes |
|---|---|---|---|---|
| GET | `/health` | TODO | `server.js` | best-effort |
| GET | `/version` | TODO | `server.js` | best-effort |
| GET | `/` | TODO | `server.js` | best-effort |
| POST | `/license/validate` | TODO | `server.js` | best-effort |

- REST Endpoints (FastAPI/Flask/Django):
_None detected_

- Frontend routes/screens:
_None detected_

- CLI scripts/daemons/crons: TODO

4) Data & Config
- Schemas/Models:
  - TODO

- ENV & secrets (keys, purpose, defaults):
- `PORT`
- Migrations & seed strategy: TODO

5) Core Logic Deep Dives (best-effort)
- TODO: List 5–10 critical modules with key functions (inputs/outputs/side-effects) and rationale.

6) Reliability, Security, Performance
- Failure modes & graceful handling: TODO
- AuthN/AuthZ, validation, rate limiting, CORS: 
- TODO
- Perf notes (N+1 risks, indexing, caching): TODO

7) Deploy & Ops
- Flow Dev → Staging → Prod: TODO
- Docker/CI:
- TODO
- Hosting & probes: TODO

8) Testing & QA
- Test framework hints:
- TODO
- How to run tests: TODO
- Manual test checklist: TODO

9) Interview Q&A
- 12 likely questions with crisp answers referencing this codebase: TODO
- 2 debugging stories, 1 scalability tradeoff, 1 security hardening step: TODO
- 1-week roadmap with impact: TODO

10) Flash Cards (one-liners)
- TODO: 15 concise takeaways (e.g., “CORS configured in X…”, “This index prevents Y…”) 
