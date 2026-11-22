#!/usr/bin/env python3
"""Show whether Vyora can train/evaluate on real paired data yet."""
from __future__ import annotations

import importlib.util
import json
from collections import Counter
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from ml.src.data import ManifestError, load_manifest  # noqa: E402


def main() -> int:
    config_path = ROOT / "ml/configs/train_default.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))
    manifest = Path(config["manifest"])
    checkpoint = Path(config["checkpoint"])
    manifest = manifest if manifest.is_absolute() else ROOT / manifest
    checkpoint = checkpoint if checkpoint.is_absolute() else ROOT / checkpoint

    print("Vyora ML readiness")
    print(f"PyTorch installed: {'yes' if importlib.util.find_spec('torch') else 'no'}")
    print(f"Rasterio installed: {'yes' if importlib.util.find_spec('rasterio') else 'no'}")
    print(f"Manifest: {manifest} ({'found' if manifest.is_file() else 'missing'})")
    print(f"Checkpoint: {checkpoint} ({'found' if checkpoint.is_file() else 'missing'})")

    if not manifest.is_file():
        print("BLOCKED: no paired VV/VH + optical training manifest. No real training has run.")
        return 1
    try:
        rows = load_manifest(manifest)
    except (ManifestError, KeyError, ValueError) as exc:
        print(f"BLOCKED: manifest validation failed: {exc}")
        return 1
    counts = Counter(row["split"] for row in rows)
    print(f"Manifest tiles: {len(rows)}; splits: {dict(counts)}")
    if not all(counts.get(split, 0) for split in ("train", "validation", "test")):
        print("BLOCKED: train, validation and held-out test splits are all required.")
        return 1
    if any(row.get("source", "").lower().startswith("synthetic") for row in rows):
        print("BLOCKED: synthetic rows are smoke fixtures, not real training evidence.")
        return 1
    if not importlib.util.find_spec("torch"):
        print("BLOCKED: install PyTorch before training.")
        return 1
    print("READY TO TRAIN (not proof that training or evaluation has been completed).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
