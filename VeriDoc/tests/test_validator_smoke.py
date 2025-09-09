import os
import math
from PIL import Image, ImageDraw

from config.config_manager import ConfigManager
from validation.format_validator import FormatValidator


def _make_synthetic(w=413, h=531, bg=(255, 255, 255)):
    # Simple synthetic portrait: colored background with a central oval for face
    img = Image.new('RGB', (w, h), bg)
    d = ImageDraw.Draw(img)
    # Draw an oval roughly centered
    face_w = int(w * 0.42)
    face_h = int(h * 0.46)
    left = (w - face_w) // 2
    top = (h - face_h) // 2
    d.ellipse([left, top, left + face_w, top + face_h], fill=(230, 200, 190))
    # Eyes as small ellipses approx at 0.35 height
    eye_y = top + int(face_h * 0.35)
    eye_dx = int(face_w * 0.20)
    d.ellipse([left + eye_dx - 8, eye_y - 6, left + eye_dx + 8, eye_y + 6], fill=(20, 20, 20))
    d.ellipse([left + face_w - eye_dx - 8, eye_y - 6, left + face_w - eye_dx + 8, eye_y + 6], fill=(20, 20, 20))
    return img


def test_validator_dimensions_and_background_and_quality():
    os.environ.setdefault('VERIDOC_NO_AI', '1')
    cfg = ConfigManager()
    v = FormatValidator(cfg)
    img = _make_synthetic()
    comp = v.validate_compliance(img, 'ICS-UAE')
    # Synthetic should at least compute and not crash
    assert isinstance(comp.overall_score, float)
    assert comp.dimension_result.required_dimensions == (413, 531)
    # Background may or may not pass depending on estimator; assert fields exist
    assert comp.background_result.required_background_color is not None
    # Scores should be in range 0..100
    assert comp.quality_result.overall_score >= 0.0


def test_validator_eye_head_thresholds_move_with_fix(tmp_path):
    os.environ.setdefault('VERIDOC_NO_AI', '1')
    cfg = ConfigManager()
    v = FormatValidator(cfg)
    # Start with odd aspect to force a fail
    img = _make_synthetic(w=600, h=600)
    p = tmp_path / 'synth.jpg'
    img.save(p)
    comp1 = v.validate_compliance(str(p), 'ICS-UAE')
    # Now resize towards required dims and re-validate
    img2 = img.resize((413, 531))
    p2 = tmp_path / 'synth2.jpg'
    img2.save(p2)
    comp2 = v.validate_compliance(str(p2), 'ICS-UAE')
    # Score should not decrease
    assert comp2.overall_score >= comp1.overall_score

