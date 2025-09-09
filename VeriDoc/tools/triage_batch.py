#!/usr/bin/env python3
"""
Triage a directory of images against a given format and emit CSV of results.

Usage:
  python tools/triage_batch.py <dir> <format>

Environment:
  VERIDOC_NO_AI=1 (default) for deterministic, offline validation
  QT_QPA_PLATFORM=offscreen (default) to avoid GUI deps
"""

from __future__ import annotations

import os
import sys
import csv
from pathlib import Path
from typing import List, Dict, Any


def main() -> int:
    if len(sys.argv) < 3:
        print("Usage: python tools/triage_batch.py <dir> <format>")
        return 2

    root = Path(sys.argv[1])
    fmt = sys.argv[2]

    if not root.exists() or not root.is_dir():
        print(f"Directory not found: {root}")
        return 2

    os.environ.setdefault('VERIDOC_NO_AI', '1')
    os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

    try:
        # Ensure project root on path
        project_root = Path(__file__).resolve().parents[1]
        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))
        from config.config_manager import ConfigManager
        from validation.format_validator import FormatValidator
    except Exception as e:
        print(f"Setup issue: {e}")
        return 2

    cfg = ConfigManager()
    canonical = cfg.get_canonical_key(fmt)
    validator = FormatValidator(cfg)

    exts = {'.jpg', '.jpeg', '.png', '.bmp', '.tif', '.tiff'}
    files: List[Path] = [p for p in root.rglob('*') if p.is_file() and p.suffix.lower() in exts]

    writer = csv.writer(sys.stdout)
    writer.writerow(["file", "pass", "score", "failing_checks"])  # minimal per spec

    for p in files:
        try:
            comp, report = validator.validate(str(p), canonical, return_details=True)
            failing: List[str] = []
            checks = getattr(report, 'checks', None) or getattr(report, 'check_details', None) or []
            for c in checks:
                try:
                    if not bool(c.get('ok', False)):
                        failing.append(str(c.get('name', 'check')))
                except Exception:
                    continue
            writer.writerow([
                str(p),
                'PASS' if bool(getattr(comp, 'passes', False)) else 'FAIL',
                f"{float(getattr(comp, 'overall_score', 0.0)):.1f}",
                ';'.join(failing)
            ])
        except Exception as e:
            writer.writerow([str(p), 'ERROR', '0.0', f"error: {e}"])

    return 0


if __name__ == '__main__':
    sys.exit(main())


