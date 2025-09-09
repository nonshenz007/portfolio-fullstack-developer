# android — INTERVIEW_BRIEF

1) Snapshot
- Purpose: TODO. Users: TODO. Problem: TODO.
- Stack & versions: TODO
- Build commands:
- TODO
- Entry points & boot:
- TODO

2) Architecture Map
- Folder tree (top 2 levels):
```
android/
  app/
    src/
    build.gradle.kts
  gradle/
    wrapper/
  build.gradle.kts
  chaios_android.iml
  gradle.properties
  gradlew
  gradlew.bat
  local.properties
  settings.gradle.kts
```
- Component responsibilities: TODO
- Data flow: request → controller/service → db/cache → response (map with file pointers) — TODO
- External services/APIs: TODO (list and where used)

3) Interfaces
- REST Endpoints (Node/Express etc.):
_None detected_

- REST Endpoints (FastAPI/Flask/Django):
_None detected_

- Frontend routes/screens:
_None detected_

- CLI scripts/daemons/crons: TODO

4) Data & Config
- Schemas/Models:
  - TODO

- ENV & secrets (keys, purpose, defaults):
- TODO
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
