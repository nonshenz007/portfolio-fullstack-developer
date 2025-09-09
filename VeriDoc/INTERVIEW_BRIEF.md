# INTERVIEW BRIEF — VeriDoc (ICAO/ICS Photo Compliance)

## 1) Snapshot
- Purpose: Offline photo compliance system validating images against ICAO and regional (ICS/UAE) rules with batch processing and a clean desktop UI.
- Users: Photo studios, passport centers, operations desks needing deterministic validation and export.
- Problem: Automates face/format checks, background/quality validation, and reporting to reduce rejections.

- Tech Stack:
  - Desktop/UI: PySide6 `>=6.6`.
  - Imaging/ML: OpenCV `>=4.8`, Pillow `>=10`, optional MediaPipe, NumPy, Numba; ONNX support where applicable.
  - Infra/Build: PyInstaller, Watchdog hot‑reload, pytest + hypothesis.

- Entry Points / Boot
  - UI: `ui/main_window.py` via `launch_ui.py` / `launch_veridoc.py`.
  - Engine: `engine/veridoc_engine.py` orchestrates detection → validation → results.
  - CLI: `tools/validate_one.py`, `tools/validate_cli.py` for batch/headless.

## 2) Architecture Map
- Folder Tree (top 2 levels)
  - `ui/` main_window, batch processor, theme, UI bridge
  - `engine/` `veridoc_engine.py`, `image_processor.py`
  - `validation/` `icao_validator.py`, `format_validator.py`, data models
  - `detection/` face metrics models/inference
  - `config/` config manager, formats/rules
  - `tools/` CLI utilities (validate, triage, audit)

- Responsibilities
  - `ui/main_window.py`: Desktop UI for import, queue, preview, and results.
  - `engine/veridoc_engine.py`: Orchestrates processing pipeline, aggregates results, timings.
  - `validation/icao_validator.py`: Authoritative compliance checker (dimensions, position, background, quality) → `ComplianceResult`.
  - `validation/format_validator.py`: Format‑specific checks and rule application.

- Data Flow
  Import images → detection (face metrics) → `ICAOValidator.validate_compliance` → aggregate issues → UI/CLI report/export.

- External Services
  - None at runtime; optional model downloads in `tools/fetch_models.py`.

## 3) Interfaces
- CLI
  - `tools/validate_one.py` → validate single image; returns pass/fail + issues.
  - `tools/validate_cli.py` → batch validation with summaries and exit codes.

- UI Screens
  - Import (files/folder), queue list, preview pane, processing progress, results panel; defined in `ui/main_window.py`.

## 4) Data & Config
- Formats/Rules
  - Centralized in `config/` with JSON/YAML schemas; loaded by ConfigManager.
  - `validation/validation_models.py` defines typed results and severities.

- ENV/Secrets
  - None required offline; optional paths for models; logging level.

- Seed/Models
  - `training_data/` stores thresholds/history; tools to fetch and calibrate government standards.

## 5) Core Logic Deep Dives
1) `validation/icao_validator.py:ICAOValidator.validate_compliance(image, face_metrics, format_name)`
   - Runs dimension, position, background, and quality checks; aggregates `ValidationIssue`s; computes weighted compliance score.
2) `validation/icao_validator.py:_setup_validation_thresholds()`
   - Prepares kernels (Laplacian/Sobel) and thresholds for sharpness/edge detection.
3) `engine/image_processor.py`
   - Converts images to arrays, normalization, background analysis helpers.
4) `engine/veridoc_engine.py`
   - Coordinates detection → validation → result packaging with timings and logs.
5) `ui/ui_processing_bridge.py`
   - Threading/bridge between engine and UI for smooth progress updates.

## 6) Reliability, Security, Performance
- Failure Modes: Corrupted images → robust exceptions with user messaging; face not detected → specific issue code and hints; batch mode continues on errors.
- Security: Offline‑first; no PII leaves device; model files validated; logs anonymized.
- Performance: Vectorized NumPy/OpenCV ops; threshold checks tuned; potential GPU/OpenCL where available; batch pipeline avoids repeated IO.

## 7) Deploy & Ops
- Packaging: PyInstaller spec; outputs cross‑platform executables.
- Logging: `logs/` folder with diagnostics and timings; toggled by config.
- Health: UI status bar, CLI non‑zero exit on failures for CI integration.

## 8) Testing & QA
- Tests: `tests/` inc. `test_icao_validator.py`, `test_processing_api.py`, performance benchmarks.
- Run: `pytest -q`; add `-k icao` to focus on compliance.
- Coverage Gaps: Edge lighting/background scenarios; extreme resolutions.
- Manual Checklist: Validate known good/bad sets, verify issue severities, check batch latency and memory usage.

## 9) Interview Q&A Pack
1) Where is the authoritative validator?
   - `validation/icao_validator.py` with `validate_compliance`, producing a `ComplianceResult`.
2) How do you compute the score?
   - Weighted average across dimensions/position/background/quality; see weighting map inside `validate_compliance`.
3) How does UI remain responsive?
   - Processing bridge and threads; signals update progress while engine runs computation.
4) What if face detection fails?
   - Returns issues with `ValidationSeverity`; UI highlights and suggests re‑capture; batch continues.
5) How are formats configured?
   - Central `config/` schemas; `ConfigManager` loads rules; validators consume `format_rules` by key.
6) Can it run fully offline?
   - Yes, models and rules are local; no external calls in runtime path.
7) What are the main kernels used?
   - Laplacian + Sobel for sharpness/edge checks; uniformity for background.
8) How do you test quality thresholds?
   - Hypothesis/pytest with parametrized images; performance tests ensure latency budgets.
9) How do you package models?
   - Shipped with build or downloaded by `tools/fetch_models.py`; checksums recommended.
10) Where are batch tools?
   - `tools/validate_cli.py`, `tools/triage_batch.py` with summary exports.
11) How do you add a new government format?
   - Add rule config and mapping; extend `format_validator` if needed; plug into UI selection.
12) How do you debug false negatives?
   - Save intermediates (edges/background masks), compare thresholds; tune `format_rules` and re‑run benchmarks.

- Debugging stories
  - Underexposed images flagged background failure; added adaptive thresholding and improved uniformity scoring.
  - Face off‑center mis‑scored; refined position calculation with better face metrics and tolerance window.

- Scalability tradeoff
  - Chose deterministic validators over heavy models for speed/explainability; can integrate ONNX if higher accuracy needed.

- Security hardening step
  - Sandboxed file loading, disallow non‑image types; clean temp folders; ensure no network paths.

- If I had 1 week
  - Add GPU kernels where available, golden dataset with acceptance thresholds, and in‑UI diff tooling for QA.

## 10) Flash Cards
- “Authoritative ICAO validator in `validation/icao_validator.py`.”
- “Weighted compliance score across four checks.”
- “Runs entirely offline; no PII egress.”
- “UI/engine bridged with signals and threads.”
- “OpenCV + NumPy for core metrics.”
- “Configurable formats via `config/`.”
- “Batch tools in `tools/` for CI/ops.”
- “PyInstaller builds desktop binaries.”
- “Logs to `logs/` with timings.”
- “Hypothesis tests cover edge inputs.”
- “Uniformity/edges drive background/quality.”
- “Face metrics power position checks.”
- “Adaptive thresholds mitigate lighting variation.”
- “No external dependencies at runtime.”
- “Extend formats by adding rules + mapping.”

---

## Universal Hot‑Seat Prep
- Walkthrough: Snapshot → Arch Map (ui/engine/validation) → Core flow: import → detect → validate → UI results → Packaging.
- Why this stack: Native desktop UX, deterministic performance with OpenCV, easy packaging.
- Debug a prod 500: N/A (desktop); for crashes, repro with CLI, inspect logs, isolate step, add guard; postmortem thresholds.
- Explain auth: N/A; offline tool, focus on data privacy.
- Scale to 10×: Batch parallelism, GPU acceleration, caching model outputs.

## 60‑Minute Cram Checklist
1) Read this brief; open `validation/icao_validator.py`.
2) Skim `ui/main_window.py` and engine wiring.
3) Memorize scoring weights and result types.
4) Prepare one tuning idea + one packaging fix.

## Red Flags to Avoid
- Avoid library name‑dropping—explain the validation logic and thresholds.
- If unsure: “I’d verify the exact call signature, but logic is X → Y → Z, implemented in `validation/icao_validator.py`.”
- Keep answers tight with file references.

