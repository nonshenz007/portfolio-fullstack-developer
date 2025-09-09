#!/usr/bin/env python3
"""
Audit images under apps/web/public/images for empties and duplicates.

Outputs a concise report grouping exact duplicates (by MD5) and listing 0‑byte files.
Safe read‑only script — does not modify files.
"""
import hashlib
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]  # repo root
IMAGES_DIR = ROOT / 'apps' / 'web' / 'public' / 'images'

def md5sum(path: Path, chunk_size: int = 8192) -> str:
    h = hashlib.md5()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(chunk_size), b''):
            h.update(chunk)
    return h.hexdigest()

def main() -> None:
    if not IMAGES_DIR.exists():
        print(f"images dir not found: {IMAGES_DIR}")
        return

    images: list[Path] = []
    for p in IMAGES_DIR.rglob('*'):
        if p.is_file() and p.suffix.lower() in {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg'}:
            images.append(p)

    empties = [p for p in images if p.stat().st_size == 0]
    digests: dict[str, list[Path]] = {}
    for p in images:
        try:
            d = md5sum(p)
        except Exception as e:
            print(f"ERR reading {p}: {e}")
            continue
        digests.setdefault(d, []).append(p)

    dup_groups = [paths for paths in digests.values() if len(paths) > 1]

    print('=== Image Audit Report ===')
    print(f"Scanned: {len(images)} files under {IMAGES_DIR}")
    print(f"Empty files: {len(empties)}")
    print(f"Duplicate groups: {len(dup_groups)} (exact byte matches)\n")

    if empties:
        print('Empty files (0 bytes):')
        for p in sorted(empties):
            print(f" - {p.relative_to(ROOT)}")
        print()

    if dup_groups:
        print('Duplicate groups (keep one, remove the rest if unused):')
        for group in dup_groups:
            print('---')
            for p in sorted(group):
                print(f" {p.relative_to(ROOT)}")

    print('\nTip: Update code to reference a single canonical asset or switch to remote Unsplash fallbacks (already enabled).')

if __name__ == '__main__':
    main()

