#!/usr/bin/env python3
"""Inspect one A/B PNG pair referenced by a local training manifest.

Prints filenames and channel statistics only (never absolute paths), so the
output is safe to share without exposing a local dataset directory.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from ml.src.data import load_manifest, optical_target  # noqa: E402


def _stats(path: Path) -> tuple[str, tuple[int, int], np.ndarray, float]:
    with Image.open(path) as image:
        mode = image.mode
        rgb = np.asarray(image.convert("RGB"), dtype=np.float32) / 255.0
        means = rgb.reshape(-1, 3).mean(axis=0)
        spread = float(np.mean(rgb.max(axis=2) - rgb.min(axis=2)))
        return mode, image.size, means, spread


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", default="data/manifests/tiles.json")
    parser.add_argument("--tile-id", required=True, help="Exact tile_id from the manifest")
    args = parser.parse_args()

    try:
        rows = load_manifest(args.manifest)
    except Exception as exc:
        parser.error(f"Could not load/validate manifest: {exc}")
    row = next((item for item in rows if item.get("tile_id") == args.tile_id), None)
    if row is None:
        parser.error(f"Tile not found in manifest: {args.tile_id}")

    input_path = Path(row.get("sar_vv_path") or row.get("sar_path", ""))
    target_path = Path(row["optical_path"])
    input_side = row.get("input_side", "unspecified")
    target_side = row.get("target_side", "unspecified")
    for label, path in ((f"Input ({input_side}-side)", input_path), (f"Target ({target_side}-side)", target_path)):
        if not path.is_file():
            parser.error(f"{label} file is missing: {path.name}")
        mode, size, means, spread = _stats(path)
        print(f"{label}: {path.name}")
        print(f"  mode={mode}, size={size[0]}x{size[1]}")
        print(f"  RGB means=[{means[0]:.4f}, {means[1]:.4f}, {means[2]:.4f}]")
        print(f"  mean RGB channel spread={spread:.5f} (0 means grayscale)")

    try:
        loaded_target = optical_target(row)
    except Exception as exc:
        parser.error(f"Training pipeline could not read B target: {exc}")
    pipeline_spread = float(np.mean(loaded_target.max(axis=2) - loaded_target.min(axis=2)))
    print(f"B target after training preprocessing: mean RGB channel spread={pipeline_spread:.5f}")
    print("If the B file you expect to be green has near-zero spread, inspect the source file or manifest pairing before training.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
