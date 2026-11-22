"""Train the compact ResU-Net baseline on a validated paired-tile manifest.

Usage:
  python -m ml.src.train --config ml/configs/train_default.json

There is no bundled training data. Supply your own licensed, aligned SAR/optical
tiles and a manifest built with ml.src.data.build_manifest. Do not report
metrics until an evaluation on the held-out split has been run.
"""
from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

import numpy as np
import torch

from ml.src.data import get_dataset_class, load_manifest
from ml.src.losses import total_loss
from ml.src.model import build_model, parameter_count

ROOT = Path(__file__).resolve().parents[2]


def _seed_everything(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


def _resolve(path: str) -> Path:
    p = Path(path)
    return p if p.is_absolute() else ROOT / p


def main() -> None:
    parser = argparse.ArgumentParser(description="Train Vyora ResU-Net baseline")
    parser.add_argument("--config", default="ml/configs/train_default.json")
    args = parser.parse_args()
    config = json.loads(Path(args.config).read_text(encoding="utf-8"))
    _seed_everything(int(config.get("seed", 42)))

    manifest_path = _resolve(config["manifest"])
    rows = load_manifest(manifest_path)
    groups: dict[str, list[dict]] = {}
    for row in rows:
        groups.setdefault(row["split"], []).append(row)
    if not groups.get("train") or not groups.get("validation"):
        raise SystemExit("Manifest needs both train and validation tiles.")

    PairedTileDataset = get_dataset_class()
    from torch.utils.data import DataLoader

    size = int(config.get("tile_size", 256))
    loaders = {
        split: DataLoader(
            PairedTileDataset(items, size=size, augment=(split == "train")),
            batch_size=int(config.get("batch_size", 8)),
            shuffle=(split == "train"),
            num_workers=int(config.get("num_workers", 0)),
        )
        for split, items in groups.items()
    }

    device = torch.device("cuda" if torch.cuda.is_available() and config.get("use_cuda") else "cpu")
    input_channels = int(config.get("input_channels", 2))
    if input_channels != 2:
        raise SystemExit("Vyora's documented Sentinel-1 baseline requires exactly VV + VH (2 input channels).")
    model = build_model(int(config.get("base_channels", 24)), input_channels=input_channels).to(device)
    print(f"Model: ResU-Net, {parameter_count(model):,} parameters, device={device}")
    optimizer = torch.optim.AdamW(model.parameters(), lr=float(config.get("lr", 1e-3)))
    weights = {k: float(config.get(k, default)) for k, default in {
        "w_colour": 1.0, "w_ssim": 0.2, "w_edge": 0.1,
    }.items()}

    best = float("inf")
    checkpoint_path = _resolve(config["checkpoint"])
    checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
    for epoch in range(1, int(config["epochs"]) + 1):
        model.train()
        train_loss = 0.0
        for sar, target in loaders["train"]:
            sar, target = sar.to(device), target.to(device)
            optimizer.zero_grad(set_to_none=True)
            rgb = model(sar)
            loss = total_loss(rgb, target, **weights)
            loss["total"].backward()
            optimizer.step()
            train_loss += loss["total"].item() * len(sar)
        train_loss /= max(len(loaders["train"].dataset), 1)

        model.eval()
        val_loss = 0.0
        with torch.inference_mode():
            for sar, target in loaders["validation"]:
                sar, target = sar.to(device), target.to(device)
                rgb = model(sar)
                loss = total_loss(rgb, target, **weights)
                val_loss += loss["total"].item() * len(sar)
        val_loss /= max(len(loaders["validation"].dataset), 1)
        print(f"epoch {epoch:03d} train={train_loss:.4f} validation={val_loss:.4f}")

        if val_loss < best:
            best = val_loss
            torch.save(
                {
                    "state_dict": model.state_dict(),
                    "base_channels": int(config.get("base_channels", 24)),
                    "input_channels": input_channels,
                    "version": str(config.get("version", "resunet-v0.1")),
                    "epoch": epoch,
                    "validation_loss": round(val_loss, 6),
                    "seed": int(config.get("seed", 42)),
                },
                checkpoint_path,
            )
    print(f"Best validation loss {best:.4f}; checkpoint: {checkpoint_path}")


if __name__ == "__main__":
    main()
