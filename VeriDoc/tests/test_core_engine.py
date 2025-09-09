import os
import json
from pathlib import Path

import cv2
import numpy as np

from engine.veridoc_engine import VeriDocEngine, Rules


def test_core_pipeline_end_to_end(tmp_path: Path):
    rules_path = str(Path('config/icao_rules.json').resolve())
    assert os.path.exists(rules_path)

    engine = VeriDocEngine(rules_path)
    img_path = str(Path('test_images/ics/compliant_ics_uae.jpg').resolve())
    assert os.path.exists(img_path)

    bgr = engine.import_image(img_path)
    assert isinstance(bgr, np.ndarray)
    assert bgr.ndim == 3 and bgr.shape[2] == 3

    lm = engine.detect_landmarks(bgr)
    measures = engine.measure_geometry(bgr, lm, engine.rules)
    assert 'head_ratio' in measures

    fixed = engine.autofix(bgr, measures, engine.rules)
    report = engine.validate(measures, engine.rules)
    out_dir = tmp_path / 'out'
    out_dir.mkdir(parents=True, exist_ok=True)

    out_path = engine.export(fixed, str(out_dir), 'sample', engine.rules, report)
    assert os.path.exists(out_path)

    # Validate dimensions and size
    out_img = cv2.imread(out_path)
    assert out_img is not None
    h, w = out_img.shape[:2]
    assert (w, h) == (engine.rules.output.width_px, engine.rules.output.height_px)
    size_kb = os.path.getsize(out_path) / 1024.0
    assert size_kb <= engine.rules.output.max_kb + 2  # allow small overhead

    # SUMMARY.json and CHECKS.csv appended
    summary = out_dir / 'SUMMARY.json'
    checks = out_dir / 'CHECKS.csv'
    assert summary.exists()
    assert checks.exists()
    data = json.loads(summary.read_text())
    assert isinstance(data, list) and len(data) >= 1


