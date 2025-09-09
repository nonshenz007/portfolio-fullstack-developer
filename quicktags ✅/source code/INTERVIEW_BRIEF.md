# source code — INTERVIEW_BRIEF

1) Snapshot
- Purpose: TODO. Users: TODO. Problem: TODO.
- Stack & versions: TODO
- Build commands:
- `pip install -r requirements.txt`
- Entry points & boot:
- TODO

2) Architecture Map
- Folder tree (top 2 levels):
```
source code/
  assets/
    arial.ttf
    arialbd.ttf
    Arialn.ttf
    ArialTh.ttf
    ARIBL0.ttf
    G_ari_bd.TTF
    G_ari_i.TTF
    GEO_AI__.TTF
    llll.pdf
    Roboto-Black.ttf
    Roboto-BlackItalic.ttf
    Roboto-Bold.ttf
    Roboto-BoldItalic.ttf
    Roboto-Italic.ttf
    Roboto-Light.ttf
    Roboto-LightItalic.ttf
    Roboto-Medium.ttf
    Roboto-MediumItalic.ttf
    Roboto-Regular.ttf
    Roboto-Thin.ttf
    Roboto-ThinItalic.ttf
    wow.pdf
  output/
    quicktags.exe
  temp/
    quicktag_prints/
    quicktag_prints 2/
  BARCODE_FIX_README.md
  build_fixed_exe.py
  build_requirements.txt
  create_windows_build.py
  CURRENT_QUALITY_TEST.png
  EmbeddedFont.py
  exe_test_barcode_1.png
  exe_test_barcode_2.png
  FINAL_REAL_scannable_barcode.png
  FINAL_SCANNABLE_barcode.png
  FIXED_REAL_EAN13_barcode.png
  IMPROVED_spacing_barcode.png
  NO_FALLBACK_barcode_1.png
  NO_FALLBACK_barcode_2.png
  oooo.pdf
  pil_import_test.png
  proper_ean13_generator.py
  PYINSTALLER_compatible_barcode_1.png
  PYINSTALLER_compatible_barcode_2.png
  quicktag.db
  Quicktags-AutoGeek.ico
  quicktags.py
  quicktags.spec
  quicktags_config.json
  quicktags_fixed_barcode_test.png
  QUICKTAGS_STYLE_TEST.png
  REAL_scannable_barcode_with_numbers.png
  REFERENCE_python_barcode.png
  requirements.txt
  SCANNABLE_REFERENCE_6285096738356.png
  SCANNABLE_test_barcode.png
  SCANNABLE_test_barcode_LARGE.png
  SIMPLE_barcode_1.png
  SIMPLE_barcode_2.png
  SIMPLE_barcode_3.png
  SIMPLE_barcode_4.png
  standalone_barcode_1_123456789012.png
  standalone_barcode_2_1234567890123.png
  standalone_barcode_3_9073403143863.png
  standalone_barcode_test.py
  standalone_maximum_quality_method.png
  standalone_minimal_method.png
  standalone_python-barcode_method.png
  standalone_simple_method.png
  test_barcode.py
  test_barcode_fix.py
  test_barcode_pil.png
  test_barcode_python_barcode.png
  test_barcode_python_barcode_improved.png
  test_barcode_simple_improved.png
  test_barcode_thermal_optimized.png
  test_bulletproof_barcode.py
  test_current_barcode.py
  test_direct_pil_barcode.png
  test_exe_compatibility.py
  test_fixed_barcode.png
  WORKING_barcode_test.png
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
- Pytest
- tests/ present
- How to run tests: TODO
- Manual test checklist: TODO

9) Interview Q&A
- 12 likely questions with crisp answers referencing this codebase: TODO
- 2 debugging stories, 1 scalability tradeoff, 1 security hardening step: TODO
- 1-week roadmap with impact: TODO

10) Flash Cards (one-liners)
- TODO: 15 concise takeaways (e.g., “CORS configured in X…”, “This index prevents Y…”) 
