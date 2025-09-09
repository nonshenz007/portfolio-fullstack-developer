import os
import sys
import json
from pathlib import Path
from PIL import Image


def test_validate_one_cli_runs(tmp_path, monkeypatch):
    # Create sample image
    img_path = tmp_path / 'img.jpg'
    Image.new('RGB', (413, 531), (255, 255, 255)).save(img_path)

    # Run the CLI as a module
    cli_path = Path(__file__).resolve().parents[1] / 'tools' / 'validate_one.py'
    assert cli_path.exists()

    import subprocess
    env = dict(os.environ)
    env['VERIDOC_NO_AI'] = '1'
    env['QT_QPA_PLATFORM'] = 'offscreen'
    proc = subprocess.run([sys.executable, str(cli_path), str(img_path), 'ICS-UAE'], capture_output=True, text=True, env=env)
    # It may fail compliance on synthetic, but should return JSON and exit 0/1
    assert proc.returncode in (0, 1)
    data = json.loads(proc.stdout)
    assert 'overall_pass' in data and 'overall_score' in data

