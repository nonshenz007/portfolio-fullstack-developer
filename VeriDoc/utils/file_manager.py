"""
Lightweight file utilities used by the VeriDoc app.
"""

from __future__ import annotations

import os
from typing import Iterable, List, Optional, Tuple
import shutil
import hashlib
from glob import glob
from pathlib import Path


class FileManager:
    def __init__(self, base_dir: str | None = None) -> None:
        self.base_dir = base_dir or os.getcwd()

    # Back-compat alias used by some utilities/tests
    @property
    def base_directory(self) -> str:
        return self.base_dir

    def ensure_directory_exists(self, path: str) -> bool:
        os.makedirs(path, exist_ok=True)
        return True

    def create_directory(self, path: str, parents: bool = True) -> Tuple[bool, str]:
        try:
            if parents:
                os.makedirs(path, exist_ok=True)
            else:
                os.mkdir(path)
            return True, ""
        except Exception as e:
            return False, str(e)

    def is_supported_image_file(self, path: str, exts: Iterable[str] | None = None) -> bool:
        if not os.path.isfile(path):
            return False
        allowed = list(exts) if exts else ["jpg", "jpeg", "png", "bmp", "tiff"]
        _, ext = os.path.splitext(path)
        return ext.lower().lstrip('.') in allowed

    def get_unique_filename(self, directory: str, filename: str) -> str:
        name, ext = os.path.splitext(filename)
        candidate = os.path.join(directory, filename)
        if not os.path.exists(candidate):
            return filename
        i = 1
        while True:
            alt = f"{name}_{i}{ext}"
            candidate = os.path.join(directory, alt)
            if not os.path.exists(candidate):
                return alt
            i += 1

    # --- Extra helpers required by tests ---
    def validate_path(self, path: str, max_length: int = 255) -> Tuple[bool, str]:
        invalid_chars = set('<>:"|?*')
        if any(c in invalid_chars for c in path):
            return False, "Path contains invalid characters"
        if len(path) > max_length:
            return False, "Path is too long"
        return True, ""

    def get_file_info(self, path: str) -> Optional[dict]:
        try:
            if not os.path.exists(path):
                return None
            p = Path(path)
            info = {
                'name': p.name,
                'stem': p.stem,
                'suffix': p.suffix,
                'is_file': p.is_file(),
                'is_directory': p.is_dir(),
                'size_bytes': p.stat().st_size,
                'is_image': self.is_supported_image_file(path) if p.is_file() else False,
            }
            if info['is_image'] and p.is_file():
                try:
                    from PIL import Image
                    with Image.open(path) as im:
                        info['image_width'], info['image_height'] = im.size
                        info['image_format'] = im.format
                except Exception:
                    pass
            return info
        except Exception as e:
            return {'error': str(e)}

    def copy_file(self, src: str, dst: str, overwrite: bool = True) -> Tuple[bool, str]:
        try:
            if os.path.exists(dst) and not overwrite:
                return False, "Destination file already exists"
            shutil.copy2(src, dst)
            return True, ""
        except Exception as e:
            return False, str(e)

    def move_file(self, src: str, dst: str, overwrite: bool = True) -> Tuple[bool, str]:
        try:
            if os.path.exists(dst) and not overwrite:
                return False, "Destination file already exists"
            shutil.move(src, dst)
            return True, ""
        except Exception as e:
            return False, str(e)

    def delete_file(self, path: str) -> Tuple[bool, str]:
        try:
            if not os.path.exists(path):
                return False, "File does not exist"
            os.remove(path)
            return True, ""
        except Exception as e:
            return False, str(e)

    def list_files(self, directory: str, pattern: str = "*", recursive: bool = False) -> List[str]:
        search_path = os.path.join(directory, "**", pattern) if recursive else os.path.join(directory, pattern)
        return sorted(glob(search_path, recursive=recursive))

    def list_image_files(self, directory: str) -> List[str]:
        files = []
        for ext in ["*.jpg", "*.jpeg", "*.png", "*.bmp", "*.tiff"]:
            files.extend(self.list_files(directory, ext, recursive=False))
        return sorted(files)

    def get_file_hash(self, path: str, algo: str = "md5") -> Optional[str]:
        try:
            h = hashlib.new(algo)
            with open(path, 'rb') as f:
                for chunk in iter(lambda: f.read(8192), b""):
                    h.update(chunk)
            return h.hexdigest()
        except Exception:
            return None

    def get_safe_filename(self, name: str) -> str:
        """Sanitize a potentially unsafe filename to a safe variant.
        Mirrors expectations in tests (replace invalid chars, trim, and fallback names).
        """
        if not name:
            return "unnamed_file"
        invalid = '<>:"|?*'
        cleaned = ''.join('_' if c in invalid else c for c in name)
        cleaned = cleaned.strip().strip('.')
        if not cleaned:
            return "filename"
        while '  ' in cleaned:
            cleaned = cleaned.replace('  ', ' ')
        cleaned = cleaned.replace(' ', '_')
        cleaned = cleaned.replace('..', '.')
        return cleaned


