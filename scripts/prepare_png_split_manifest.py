#!/usr/bin/env python3
"""Build a manifest from paired train_A/B, val_A/B, and test_A/B PNG folders.

For the current archive, folder audits show B is grayscale and A carries colour,
so B -> A is the default direction. Use --input-side A only for a different
package whose A side is the intended grayscale source.
"""
from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from ml.src.data import ManifestError, build_manifest, load_manifest  # noqa: E402

IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg"}


def _index_images(directory: Path) -> dict[str, Path]:
    if not directory.is_dir():
        raise ManifestError(f"Required folder is missing: {directory}")
    return {
        path.relative_to(directory).with_suffix("").as_posix(): path.resolve()
        for path in directory.rglob("*")
        if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES
    }


def _split_dirs(root: Path, split: str) -> tuple[Path, Path]:
    names = ("val", "validation") if split == "validation" else (split,)
    for alias in names:
        a_dir, b_dir = root / f"{alias}_A", root / f"{alias}_B"
        if a_dir.is_dir() or b_dir.is_dir():
            return a_dir, b_dir
    raise ManifestError(f"Could not find {split}_A and {split}_B folders below {root}.")


def pair_row(key: str, split: str, a_path: Path, b_path: Path, root: Path,
             input_side: str, licence: str) -> dict:
    """Make an explicit source→target row, keeping the folder side in metadata."""
    if input_side == "B":
        input_path, target_path = b_path, a_path
    else:
        input_path, target_path = a_path, b_path
    return {
        "tile_id": f"{split}-{key}",
        # Split-qualified groups avoid claiming geographic separation we have not checked.
        "scene_group": f"{split}:{key}",
        "split": split,
        "input_side": input_side,
        "target_side": "A" if input_side == "B" else "B",
        "sar_vv_path": input_path.relative_to(root).as_posix(),
        "sar_vh_path": input_path.relative_to(root).as_posix(),
        "optical_path": target_path.relative_to(root).as_posix(),
        "source": f"SEN12MS A/B PNG export; input_side={input_side}; folder pairing used as supplied",
        "licence": licence,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-root", required=True, type=Path,
                        help="Folder containing train_A/train_B, val_A/val_B, test_A/test_B")
    parser.add_argument("--output", default=str(ROOT / "data/manifests/tiles.json"))
    parser.add_argument("--input-side", choices=("A", "B"), default="B",
                        help="Which side is the grayscale model input (default B, based on the current archive audit)")
    parser.add_argument("--licence-note", required=True,
                        help="Record the dataset source/terms that apply to this downloaded package")
    args = parser.parse_args()
    root = args.data_root.resolve()
    if not root.is_dir():
        parser.error(f"Data root is not a folder: {root}")

    rows = []
    try:
        for split in ("train", "validation", "test"):
            a_dir, b_dir = _split_dirs(root, split)
            a_files, b_files = _index_images(a_dir), _index_images(b_dir)
            if not a_files or not b_files:
                raise ManifestError(f"{split} A/B folders contain no PNG/JPEG images.")
            missing_b, missing_a = set(a_files) - set(b_files), set(b_files) - set(a_files)
            if missing_b or missing_a:
                raise ManifestError(
                    f"Unpaired {split} files: {len(missing_b)} A files have no B match; "
                    f"{len(missing_a)} B files have no A match. First missing A/B keys: "
                    f"{sorted(missing_b)[:3]} / {sorted(missing_a)[:3]}"
                )
            for key in sorted(a_files):
                rows.append(pair_row(key, split, a_files[key], b_files[key], root, args.input_side, args.licence_note))
    except ManifestError as exc:
        parser.error(str(exc))

    output = args.output if Path(args.output).is_absolute() else ROOT / args.output
    try:
        manifest = build_manifest(rows, output, root=root)
        verified = load_manifest(manifest)
    except Exception as exc:
        parser.error(f"Could not write/validate manifest: {exc}")
    print(f"Manifest: {manifest}")
    print(f"Paired PNG tiles: {len(verified)}; split counts: {dict(Counter(r['split'] for r in verified))}")
    target_side = "A" if args.input_side == "B" else "B"
    print(f"Prototype mapping: grayscale {args.input_side}-side PNG input (duplicated into two channels) -> {target_side}-side RGB-style target.")
    print("This uses the supplied folder splits; it does not verify sensor/polarization encoding, geospatial metadata, geographic independence, or licence terms.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
