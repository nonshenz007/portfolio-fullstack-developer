#!/usr/bin/env python3
"""
Deterministic single-image validator CLI.

Usage:
  python tools/validate_one.py <image> <format-key>

Runs FaceDetector → Background analyze (if available) → Quality →
FormatValidator and prints detailed per-check results. Exit codes:
  0 pass, 1 fail, 2 setup issue.

Honors env flags:
  VERIDOC_NO_AI=1 to disable AI
  VERIDOC_FORCE_AI=1 to force AI even if disabled
"""

from __future__ import annotations

import os
import sys
import json
from pathlib import Path


def main() -> int:
    if len(sys.argv) < 3:
        print("Usage: python tools/validate_one.py <image> <format-key>")
        return 2

    image_path = sys.argv[1]
    format_key = sys.argv[2]

    # Deterministic/headless defaults
    os.environ.setdefault('VERIDOC_NO_AI', '1')
    os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

    # Import after env to keep optional deps gated
    try:
        # Ensure project root on path when run from arbitrary cwd
        project_root = Path(__file__).resolve().parents[1]
        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))
        from config.config_manager import ConfigManager
        from validation.format_validator import FormatValidator
    except Exception as e:
        print(f"Setup issue: {e}")
        return 2

    if not Path(image_path).exists():
        print(f"File not found: {image_path}")
        return 2

    cfg = ConfigManager()
    canonical = cfg.get_canonical_key(format_key)
    validator = FormatValidator(cfg)

    try:
        comp, report = validator.validate(image_path, canonical, return_details=True)
    except Exception as e:
        print(f"Validation error: {e}")
        return 2

    # Print structured results
    def to_py(x):
        # Convert numpy scalar types to native Python for JSON
        try:
            import numpy as _np
            if isinstance(x, (_np.generic,)):
                return x.item()
        except Exception:
            pass
        return x

    output = {
        'format': canonical,
        'overall_pass': bool(getattr(comp, 'passes', False)),
        'overall_score': float(getattr(comp, 'overall_score', 0.0)),
        'dimensions': {
            'passes': bool(comp.dimension_result.passes),
            'actual': tuple(map(to_py, comp.dimension_result.actual_dimensions)),
            'required': tuple(map(to_py, comp.dimension_result.required_dimensions)),
        },
        'position': {
            'passes': bool(comp.position_result.passes),
            'face_detected': bool(comp.position_result.face_detected),
            'face_height_ratio': float(comp.position_result.face_height_ratio),
            'eye_height_ratio': float(comp.position_result.eye_height_ratio),
            'centering_offset': float(comp.position_result.centering_offset),
        },
        'background': {
            'passes': bool(comp.background_result.passes),
            'detected': tuple(map(to_py, comp.background_result.background_color_detected)),
            'required': tuple(map(to_py, comp.background_result.required_background_color)),
            'difference': float(comp.background_result.color_difference),
        },
        'quality': {
            'passes': bool(comp.quality_result.passes_all_checks),
            'overall': float(comp.quality_result.overall_score),
            'failed_checks': [str(x) for x in comp.quality_result.failed_checks],
        },
        'issues': [i.message for i in getattr(comp, 'issues', [])],
        'suggestions': (report.suggestions if report else []),
        'checks': (getattr(report, 'checks', None) or getattr(report, 'check_details', None) or []),
    }
    print(json.dumps(output, indent=2))

    return 0 if output['overall_pass'] else 1


if __name__ == '__main__':
    sys.exit(main())


