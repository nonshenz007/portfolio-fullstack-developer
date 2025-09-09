#!/usr/bin/env python3
"""
Download lightweight offline models (YuNet face detector, ISNet background) into models/.
"""
import os
import sys
import urllib.request
from pathlib import Path

YU_URL = "https://github.com/opencv/opencv_zoo/raw/main/models/face_detection_yunet/face_detection_yunet_2023mar.onnx"
IS_URL = "https://github.com/xuebinqin/BiSeNet/raw/master/res/isnet-general-use.onnx"


def download(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and dest.stat().st_size > 0:
        print(f"Exists: {dest}")
        return
    print(f"Downloading {url} -> {dest}")
    urllib.request.urlretrieve(url, str(dest))
    print(f"Saved: {dest}")


def main() -> int:
    root = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    models_dir = root / "models"
    try:
        download(YU_URL, models_dir / "face_detection_yunet_2023mar.onnx")
    except Exception as e:
        print(f"WARN: YuNet download failed: {e}")
    try:
        download(IS_URL, models_dir / "isnet-general-use.onnx")
    except Exception as e:
        print(f"WARN: ISNet download failed: {e}")
    return 0


if __name__ == "__main__":
    sys.exit(main())


