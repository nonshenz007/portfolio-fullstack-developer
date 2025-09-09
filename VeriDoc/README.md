# VeriDoc (Windows) — Offline ICAO/ICS Photo Compliance

## Mission
Turn raw headshots into **ICAO/ICS-compliant** passport/visa photos **in seconds**, saving typing-centre staff hours of Photoshop.

## Non-Negotiables
- **Offline-only**, zero telemetry. Free/open libs only.
- **Accuracy first** (Doc 9303 rules).
- **Config-driven** thresholds via `config/rules.json` (with ICS overlay in `config/ics_rules.json`).
- Windows desktop; one-click build to `.\dist\VeriDoc.exe`.

## Golden Rules (must pass or flag)
- **Output preset (default 35×45 @300 DPI):** 413×531 px, 300 DPI, JPEG quality ~92, ≤200 KB, sRGB, EXIF stripped.
- **Geometry:** face (chin–crown) 0.62–0.69 H; eye line 33–36% from top; yaw/roll < ±2°; centered ±3%.
- **Background:** plain light neutral (target RGB [240,240,240] tol ±8); uniformity σ ≤ 4.0; no edges/shadows/texture.
- **Sharpness:** Laplacian var ≥ 120 (or equivalent MTF surrogate).
- **Brightness/Contrast:** mean 110–200 (0–255); norm. RMS contrast 0.25–0.75; avoid blown/crushed regions.
- **Color & artifacts:** natural skin tone; no red-eye; minimal JPEG blocking/halos.
- **Glasses/Head-cover:** no tint; frames not covering eyes; no glare. Religious head-cover OK if full face visible.
- **Expression/Framing:** neutral, mouth closed, eyes open; single subject; straight-on.

> Auto-fix where safe (crop/scale, levels, background smoothing, gentle sharpen, red-eye). Otherwise **flag with explicit reason**.

## Core Capabilities
- Import JPG/PNG (strip EXIF) → validate → **auto-correct** → export exact px/DPI/KB.
- **Batch queue** with progress + **per-image reasons**; on-screen Export Summary (no PDF).
- **Modern dark UI**: Home, Import & Queue, Editor (before/after + live rule panel), Batch, Export, Settings, Help (1-page visual).
- Undo/Redo, keyboard shortcuts, minimal EN text (AR/HI stubs).
- Crash logs to `.\logs\YYYY-MM-DD_HHMMSS.log`.

## Performance Targets
- Cold start < 2 s on low-end PC; smooth batch of 20 images.
- ≥95% of compliant inputs pass without manual edits.

## Config Schema (edit to tune)
```json
{
  "version": "1.0",
  "output": { "width_px": 413, "height_px": 531, "dpi": 300, "jpeg_quality": 92, "max_kb": 200 },
  "face": { "min_ratio": 0.62, "max_ratio": 0.69, "eye_line_pct_from_top": [0.33, 0.36], "max_rotation_deg": 2.0 },
  "background": { "rgb_target": [240,240,240], "tolerance": 8, "uniformity_sigma_max": 4.0 },
  "sharpness": { "lap_var_min": 120.0 },
  "brightness": { "mean_min": 110, "mean_max": 200 },
  "contrast": { "min": 0.25, "max": 0.75 },
  "exif_strip": true
}
```

## How to run
- UI app (backend-wired): `python main.py`
- Headless batch CLI: `python tools/validate_cli.py --input <folder> --format <FORMAT_NAME> --out <out_dir>`

## CLI batch (headless)
```bash
python tools/validate_cli.py --input tests --format ICS-UAE --out export
```

### Deterministic Core (SPEC) CLI
```bash
python tools/validate_cli.py --input tests --format ICS-UAE --out export --core --rules config/icao_rules.json
# Force classical-only (disable AI)
python tools/validate_cli.py --input tests --format ICS-UAE --out export --core --rules config/icao_rules.json --no-ai
```
Outputs per run:
- `export/SUMMARY.json` and `export/summary.csv` (overall)
- Legacy `export/summary.json` may also be present for compatibility.

## Configuration
- Main rules: `config/rules.json`
- ICS overlay (DPI, max_kb): `config/ics_rules.json`
- SPEC rules (ICAO/ICS): `config/icao_rules.json`

## Build (Windows EXE)
- Install: `pip install pyinstaller`
- Build: `pyinstaller --noconfirm --windowed --name VeriDoc main.py`
- Output: `dist/VeriDoc/VeriDoc.exe`

For headless CLI build:
```bat
pyinstaller --noconfirm --onefile --name VeriDocCLI tools/validate_cli.py
```

## Offline AI Models (optional but recommended)
- YuNet face detector (ONNX) and ISNet background model are supported for robust detection/segmentation.
- Download models:
```bash
python tools/fetch_models.py
```
- Models are stored under `models/` and used automatically when present. Fallbacks: MediaPipe (if installed) → Haar/GrabCut.

## Validation & Auto-Fix (Single Source of Truth)

All final compliance decisions are routed through `validation/format_validator.py` (FormatValidator). Both pipelines defer to this validator for pass/fail.

Closed-loop auto-fix: the unified engine applies targeted fixes (background normalization, mild lighting, centering/cropping) and re-validates up to 3 times, stopping early on pass. If a failure is fundamentally unfixable (e.g., excessive blur), it fails fast with reasons.

Environment flags:
- `VERIDOC_NO_AI=1`: disable optional AI deps (default in CI)
- `VERIDOC_FORCE_AI=1`: force-enable AI even if disabled
- `VERIDOC_STRONG_BG_FIX=1`: opt-in to aggressive background normalization; conservative mode is default

Headless UI/tests: `QT_QPA_PLATFORM=offscreen` is set in tests for CI.

CLI single-image validator:
```bash
python tools/validate_one.py sample.jpg US-Visa
```
Prints detailed per-check results. Exit codes: 0 pass, 1 fail, 2 setup issue.
