import os
import tempfile
from PIL import Image

from engine.image_processor import ImageProcessor, ProcessingOptions
from config.config_manager import ConfigManager


def test_summary_json_uppercase_written(tmp_path):
    # Create a simple white image
    img_path = tmp_path / "in.jpg"
    Image.new('RGB', (413, 531), (255, 255, 255)).save(img_path)

    cfg = ConfigManager()
    proc = ImageProcessor(cfg)
    opts = ProcessingOptions(format_name='ICS-UAE', output_directory=str(tmp_path), apply_background_processing=False, apply_face_cropping=False, validate_compliance=True)
    res = proc.process_image(str(img_path), opts)
    assert res.success
    out_dir = os.path.dirname(res.export_path)
    assert os.path.exists(os.path.join(out_dir, 'SUMMARY.json'))

