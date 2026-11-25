#!/usr/bin/env python3
"""Build a Vyora manifest from paired train_A/B, val_A/B, and test_A/B PNG folders."""
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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-root", required=True, type=Path,
                        help="Folder containing train_A/train_B, val_A/val_B, test_A/test_B")
    parser.add_argument("--output", default=str(ROOT / "data/manifests/tiles.json"))
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
                tile_id = f"{split}-{key}"
                rows.append({
                    "tile_id": tile_id,
                    # The source package's directory splits are trusted as provided.
                    # Split-qualified groups avoid falsely asserting geographic separation.
                    "scene_group": f"{split}:{key}",
                    "split": split,
                    "sar_vv_path": a_files[key].relative_to(root).as_posix(),
                    "sar_vh_path": a_files[key].relative_to(root).as_posix(),
                    "optical_path": b_files[key].relative_to(root).as_posix(),
                    "source": "SEN12MS A/B PNG export; folder pairing used as supplied",
                    "licence": args.licence_note,
                })
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
    print("Prototype assumptions: A is treated as grayscale input (duplicated into two model channels); B is treated as RGB target.")
    print("This uses the supplied folder splits; it does not verify VV/VH encoding, geospatial metadata, or geographic independence.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
