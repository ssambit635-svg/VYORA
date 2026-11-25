"""Train the compact ResU-Net on paired Sentinel-1/optical tiles."""
from __future__ import annotations

import argparse
import csv
import json
import random
from pathlib import Path

import numpy as np

from ml.src.data import get_dataset_class, load_manifest

ROOT = Path(__file__).resolve().parents[2]


def _resolve(path: str | Path) -> Path:
    path = Path(path)
    return path if path.is_absolute() else ROOT / path


def _seed_everything(seed: int, torch) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    if hasattr(torch.backends, "cudnn"):
        torch.backends.cudnn.benchmark = False
        torch.backends.cudnn.deterministic = True


def _atomic_save(torch, payload: dict, path: Path) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    try:
        torch.save(payload, temporary)
        temporary.replace(path)
    finally:
        if temporary.exists():
            temporary.unlink()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="ml/configs/train_default.json")
    parser.add_argument("--epochs", type=int, default=None, help="Override configured epoch count for a short prototype run")
    parser.add_argument("--max-train-tiles", type=int, default=None, help="Use a deterministic subset to shorten a prototype run")
    parser.add_argument("--max-validation-tiles", type=int, default=None)
    args = parser.parse_args()
    config_path = _resolve(args.config)
    if not config_path.is_file():
        parser.error(f"Training config not found: {config_path}")
    try:
        config = json.loads(config_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        parser.error(f"Could not read training config {config_path}: {exc}")

    try:
        import torch
    except ImportError:
        parser.exit(2, "PyTorch is required to train. Install a CPU or CUDA build for your machine first.\n")
    try:
        from ml.src.losses import total_loss
        from ml.src.model import build_model, parameter_count
    except Exception as exc:
        parser.exit(2, f"Could not load the model code: {exc}\n")

    manifest_path = _resolve(config.get("manifest", "data/manifests/tiles.json"))
    if not manifest_path.is_file():
        parser.exit(2, f"Training cannot start: paired manifest not found: {manifest_path}\nPrepare real SEN12MS pairs first; no demo images are valid training data.\n")
    try:
        rows = load_manifest(manifest_path)
    except Exception as exc:
        parser.exit(2, f"Training cannot start: manifest/data validation failed: {exc}\n")

    groups: dict[str, list[dict]] = {}
    for row in rows:
        groups.setdefault(row["split"], []).append(row)
    if not groups.get("train") or not groups.get("validation"):
        parser.exit(2, "Manifest must contain non-empty train and validation splits; preserve the test split for final evaluation.\n")
    if not groups.get("test"):
        parser.exit(2, "Manifest has no held-out test split. Refusing to train without a planned final evaluation set.\n")

    seed = int(config.get("seed", 42))
    for split, limit in (("train", args.max_train_tiles), ("validation", args.max_validation_tiles)):
        if limit is not None:
            if limit < 1:
                parser.error(f"--max-{split}-tiles must be positive")
            if len(groups[split]) > limit:
                groups[split] = random.Random(seed + (split == "validation")).sample(groups[split], limit)
                print(f"Prototype subset: {split} uses {limit} of the available tiles.")
    epochs = args.epochs if args.epochs is not None else int(config.get("epochs", 20))
    if epochs < 1:
        parser.error("--epochs must be positive")

    try:
        import importlib.util
        if importlib.util.find_spec("rasterio") is None:
            parser.exit(2, "Rasterio is required to read the GeoTIFF training data. Install backend/requirements.txt.\n")
        PairedTileDataset = get_dataset_class()
    except Exception as exc:
        parser.exit(2, f"Could not initialize the tile reader: {exc}\n")

    size = int(config.get("tile_size", 256))
    batch_size = int(config.get("batch_size", 8))
    if size < 32 or batch_size < 1 or epochs < 1:
        parser.error("tile_size must be >= 32; batch_size and epochs must be positive.")
    datasets = {
        split: PairedTileDataset(items, size=size, augment=(split == "train"))
        for split, items in groups.items()
    }
    # Read one row from each split before creating a checkpoint, so common TIFF,
    # band, scale, and preprocessing problems produce a short actionable message.
    for split in ("train", "validation", "test"):
        if split not in datasets or not len(datasets[split]):
            continue
        try:
            sar, target = datasets[split][0]
            if tuple(sar.shape) != (2, size, size) or tuple(target.shape) != (3, size, size):
                raise ValueError(f"unexpected tensors {tuple(sar.shape)} and {tuple(target.shape)}")
            if not torch.isfinite(sar).all() or not torch.isfinite(target).all():
                raise ValueError("non-finite tensor values")
            saturation = float(((target <= 0.001) | (target >= 0.999)).float().mean())
            if saturation > 0.98:
                raise ValueError(f"{saturation:.1%} of the optical target is clipped to 0/1; check optical band order and optical_scale")
        except Exception as exc:
            tile_id = groups[split][0].get("tile_id", "unknown tile")
            parser.exit(2, f"Data preflight failed for {split} tile {tile_id}: {exc}\nCheck band indexes, scaling and TIFF readability.\n")

    _seed_everything(seed, torch)
    device = torch.device("cuda" if torch.cuda.is_available() and config.get("use_cuda", False) else "cpu")
    model = build_model(int(config.get("base_channels", 24)), input_channels=2).to(device)
    print(f"Model: ResU-Net, {parameter_count(model):,} parameters, device={device}")
    optimizer = torch.optim.AdamW(model.parameters(), lr=float(config.get("lr", 1e-3)))
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode="min", patience=2, factor=0.5)
    weights = {k: float(config.get(k, default)) for k, default in {
        "w_colour": 1.0, "w_ssim": 0.2, "w_edge": 0.1,
    }.items()}
    loaders = {}
    for split, dataset in datasets.items():
        generator = torch.Generator().manual_seed(seed)
        loaders[split] = torch.utils.data.DataLoader(
            dataset, batch_size=batch_size, shuffle=(split == "train"),
            num_workers=int(config.get("num_workers", 0)), generator=generator,
            pin_memory=(device.type == "cuda"),
        )

    checkpoint_path = _resolve(config.get("checkpoint", "backend/checkpoints/vyora_resunet.pt"))
    checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
    log_path = _resolve(config.get("log_csv", "backend/checkpoints/training_history.csv"))
    log_path.parent.mkdir(parents=True, exist_ok=True)
    patience = int(config.get("early_stopping_patience", 6))
    best, best_epoch, stale = float("inf"), 0, 0
    history = []
    try:
        for epoch in range(1, epochs + 1):
            model.train()
            train_sum, train_count = 0.0, 0
            for sar, target in loaders["train"]:
                sar, target = sar.to(device), target.to(device)
                optimizer.zero_grad(set_to_none=True)
                losses = total_loss(model(sar), target, **weights)
                losses["total"].backward()
                if float(config.get("gradient_clip", 1.0)) > 0:
                    torch.nn.utils.clip_grad_norm_(model.parameters(), float(config.get("gradient_clip", 1.0)))
                optimizer.step()
                train_sum += losses["total"].item() * len(sar)
                train_count += len(sar)
            if train_count == 0:
                parser.exit(2, "Training loader yielded no tiles. Check the manifest and input files.\n")
            train_loss = train_sum / train_count
            if not np.isfinite(train_loss):
                parser.exit(2, f"Non-finite training loss at epoch {epoch}; check input values and target scaling.\n")

            model.eval()
            val_sum, val_count = 0.0, 0
            with torch.inference_mode():
                for sar, target in loaders["validation"]:
                    sar, target = sar.to(device), target.to(device)
                    value = total_loss(model(sar), target, **weights)["total"].item()
                    val_sum += value * len(sar)
                    val_count += len(sar)
            if val_count == 0:
                parser.exit(2, "Validation loader yielded no tiles.\n")
            val_loss = val_sum / val_count
            if not np.isfinite(val_loss):
                parser.exit(2, f"Non-finite validation loss at epoch {epoch}; check input values and target scaling.\n")
            scheduler.step(val_loss)
            record = {"epoch": epoch, "train_loss": train_loss, "validation_loss": val_loss,
                      "learning_rate": optimizer.param_groups[0]["lr"]}
            history.append(record)
            print(f"epoch {epoch:03d}/{epochs} train={train_loss:.5f} validation={val_loss:.5f} lr={record['learning_rate']:.2g}")

            if np.isfinite(val_loss) and val_loss < best:
                best, best_epoch, stale = val_loss, epoch, 0
                png_prototype = any("A/B PNG export" in row.get("source", "") for row in rows)
                default_version = ("resunet-sen12ms-paired-png-prototype-v0.1" if png_prototype else "resunet-v0.1")
                configured_version = str(config.get("version", ""))
                if png_prototype and configured_version.startswith("resunet-vv-vh"):
                    configured_version = ""
                checkpoint = {
                    "state_dict": model.state_dict(), "base_channels": int(config.get("base_channels", 24)),
                    "input_channels": 2, "input_representation": "grayscale_A_PNG_duplicated" if png_prototype else "VV_VH_pair",
                    "version": configured_version or default_version,
                    "training_note": "A grayscale PNG duplicated into two channels; prototype only; not independently verified VV/VH." if png_prototype else "Paired VV/VH raster input",
                    "epoch": epoch, "validation_loss": float(val_loss), "seed": seed,
                    "manifest": str(manifest_path), "train_tiles": len(groups["train"]),
                    "validation_tiles": len(groups["validation"]),
                }
                _atomic_save(torch, checkpoint, checkpoint_path)
            else:
                stale += 1
            if patience > 0 and stale >= patience:
                print(f"Early stopping at epoch {epoch}; best validation epoch was {best_epoch}.")
                break
    except (RuntimeError, OSError, ValueError) as exc:
        parser.exit(2, f"Training stopped safely: {exc}\nTry a smaller batch_size if this is an out-of-memory error. A previous best checkpoint, if any, is preserved.\n")

    with log_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["epoch", "train_loss", "validation_loss", "learning_rate"])
        writer.writeheader()
        writer.writerows(history)
    if best_epoch == 0:
        parser.exit(2, "No finite validation loss was produced; no checkpoint was saved.\n")
    print(f"Best validation loss {best:.5f} at epoch {best_epoch}; checkpoint: {checkpoint_path}")
    print(f"Training history: {log_path}")
    print("Training complete is not a performance claim; run held-out evaluation before reporting results.")


if __name__ == "__main__":
    main()
