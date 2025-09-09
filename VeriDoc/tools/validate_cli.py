#!/usr/bin/env python3
"""
Simple CLI to validate and auto-correct images in batch and emit CSV/JSON summaries.
Usage:
  python tools/validate_cli.py --input <folder> --format <FORMAT_NAME> --out <out_dir>
"""

import argparse
import json
import csv
import os
import sys
from pathlib import Path

# Ensure project root is on sys.path so `config` and other modules can be imported
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from config.config_manager import ConfigManager
from engine.image_processor import ImageProcessor, ProcessingOptions


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True, help='Input folder with images')
    parser.add_argument('--format', required=True, help='Target format key (e.g., ICS-UAE)')
    parser.add_argument('--out', required=True, help='Output directory')
    parser.add_argument('--core', action='store_true', help='Use deterministic core engine (ICAO/ICS)')
    parser.add_argument('--rules', default='config/icao_rules.json', help='Rules JSON path for core engine')
    parser.add_argument('--no-ai', action='store_true', help='Disable AI models (force classical heuristics)')
    parser.add_argument('--autofix', action='store_true', help='Enable targeted auto-fixes when validation fails')
    parser.add_argument('--strict-bg', action='store_true', help='Use strict background mode (more uniform, less natural edges)')
    args = parser.parse_args()

    if args.no_ai:
        os.environ['VERIDOC_NO_AI'] = '1'

    cfg = ConfigManager()
    proc = ImageProcessor("config")
    core = None
    if args.core:
        try:
            from engine.veridoc_engine import VeriDocEngine  # type: ignore
        except Exception as e:
            print(f"Core engine not available: {e}")
            sys.exit(1)
        core = VeriDocEngine(args.rules)

    in_dir = Path(args.input)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    images = []
    for p in in_dir.rglob('*'):
        if p.suffix.lower() in {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif'}:
            images.append(str(p))

    results = []
    if core is None:
        for img in images:
            options = ProcessingOptions(
                auto_enhance=args.autofix,
                normalize_background=not args.strict_bg,
                auto_crop_to_face=True,
                validate_before_processing=True,
                validate_after_processing=True,
                output_format="JPEG",
                output_quality=92,
                output_dpi=300
            )
            output_file = out_dir / f"processed_{Path(img).name}"
            res = proc.process_image(img, str(output_file), args.format, options)
            item = {
                'file': img,
                'success': res.success,
                'export_path': res.output_path,
                'processing_time': res.processing_time,
                'error': res.error_message,
            }
            if res.validation_report_after:
                vr = res.validation_report_after
                item['overall_pass'] = vr.passes
                item['score'] = vr.score
                # Collect explicit reasons (messages) for failures
                try:
                    item['reasons'] = [iss.message for iss in res.issues]
                except Exception:
                    item['reasons'] = []
            else:
                item['overall_pass'] = res.success
                item['score'] = 0.8 if res.success else 0.0
                item['reasons'] = []
            results.append(item)
    else:
        # Deterministic core path: SUMMARY.json and CHECKS.csv written per image
        os.makedirs(out_dir, exist_ok=True)
        import time
        for img in images:
            try:
                base = Path(img).stem
                t0 = time.time()
                bgr = core.import_image(img)
                lm = core.detect_landmarks(bgr)
                measures = core.measure_geometry(bgr, lm, core.rules)
                fixed = core.autofix(bgr, measures, core.rules)
                report = core.validate(measures, core.rules)
                export_path = core.export(fixed, str(out_dir), base, core.rules, report)
                t1 = time.time() - t0
                item = {
                    'file': img,
                    'success': True,
                    'export_path': export_path,
                    'processing_time': t1,
                    'error': None,
                    'overall_pass': len(report.fails) == 0,
                    'score': None,
                    'reasons': [f.code for f in report.fails]
                }
            except Exception as e:
                item = {
                    'file': img,
                    'success': False,
                    'export_path': None,
                    'processing_time': 0.0,
                    'error': str(e),
                    'overall_pass': False,
                    'score': None,
                    'reasons': [str(e)]
                }
            results.append(item)

    # Write JSON
    # Keep legacy summary.json path for compatibility
    json_path = out_dir / 'summary.json'
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)

    # Write CSV
    csv_path = out_dir / 'summary.csv'
    headers = ['file', 'success', 'overall_pass', 'score', 'export_path', 'processing_time', 'error']
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        for r in results:
            writer.writerow({k: r.get(k) for k in headers})

    # Also emit SPEC artifacts in core mode naming convention at root level
    if core is not None:
        # pass-through: core.export already appended per-image entries into SUMMARY.json and CHECKS.csv
        print(f"Core artifacts: {out_dir}/SUMMARY.json and {out_dir}/CHECKS.csv updated")

    print(f"Wrote: {json_path}")
    print(f"Wrote: {csv_path}")


if __name__ == '__main__':
    main()


