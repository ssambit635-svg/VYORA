#!/usr/bin/env python3
"""Create a region-safe paired manifest from SEN12MS toolbox train/test lists."""
from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from ml.src.data import load_manifest  # noqa: E402
from ml.src.sen12ms import create_sen12ms_manifest  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-root", required=True, help="Extracted SEN12MS root directory")
    parser.add_argument("--train-list", required=True, help="Toolbox train_list .txt file")
    parser.add_argument("--test-list", required=True, help="Toolbox test_list .txt (hold-out scenes)")
    parser.add_argument("--output", default=str(ROOT / "data/manifests/tiles.json"))
    parser.add_argument("--vv-band", type=int, required=True, help="verified 1-based VV band index in each S1 tile")
    parser.add_argument("--vh-band", type=int, required=True, help="verified 1-based VH band index in each S1 tile")
    parser.add_argument("--rgb-bands", type=int, nargs=3, required=True, metavar=("R", "G", "B"),
                        help="verified 1-based S2 band indexes in RGB order")
    parser.add_argument("--optical-scale", type=float, required=True,
                        help="verified divisor for S2 reflectance values (for example, 10000 only if metadata confirms it)")
    parser.add_argument("--validation-fraction", type=float, default=0.1,
                        help="Share of training ROI groups reserved for validation")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--licence-note", required=True,
                        help="Write the actual source/licence note from the dataset terms")
    args = parser.parse_args()

    manifest = create_sen12ms_manifest(
        args.data_root, args.train_list, args.test_list, args.output,
        vv_band=args.vv_band, vh_band=args.vh_band, rgb_bands=tuple(args.rgb_bands),
        optical_scale=args.optical_scale, validation_fraction=args.validation_fraction,
        seed=args.seed, licence_note=args.licence_note,
    )
    rows = load_manifest(manifest)
    print(f"Manifest: {manifest}")
    print(f"Tiles: {len(rows)}; splits: {dict(Counter(row['split'] for row in rows))}")
    print("Check exact S1/S2 band order, reflectance scale, cloud quality, licence and co-registration before training.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
