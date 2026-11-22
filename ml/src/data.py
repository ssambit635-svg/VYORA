"""Leakage-checked manifest and paired VV/VH -> optical tile dataset.

Preferred manifest fields: tile_id, scene_group, split, sar_vv_path,
sar_vh_path, optical_path, source, licence. Legacy `sar_path` is allowed for
synthetic smoke tests only and is duplicated into VV/VH with a recorded warning.
GeoTIFF pairs must be co-registered before being added to a manifest.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

import numpy as np
from PIL import Image

BASE_COLUMNS = {"tile_id", "scene_group", "split", "optical_path", "source", "licence"}
VALID_SPLITS = {"train", "validation", "test"}


class ManifestError(ValueError):
    pass


def _paths(row: dict) -> tuple[str, ...]:
    if "sar_vv_path" in row and "sar_vh_path" in row:
        return row["sar_vv_path"], row["sar_vh_path"], row["optical_path"]
    if "sar_path" in row:
        return row["sar_path"], row["optical_path"]
    raise ManifestError("Rows must provide sar_vv_path + sar_vh_path (preferred) or legacy sar_path.")


def build_manifest(rows: list[dict], output_path: str | Path, root: str | Path | None = None) -> Path:
    root = Path(root).resolve() if root else Path(output_path).parent.resolve()
    seen_ids: set[str] = set()
    group_splits: dict[str, str] = {}
    for i, row in enumerate(rows):
        missing = BASE_COLUMNS - set(row)
        if missing:
            raise ManifestError(f"Row {i} is missing columns: {sorted(missing)}")
        if not row["tile_id"] or not row["scene_group"]:
            raise ManifestError(f"Row {i} needs non-empty tile_id and scene_group.")
        if row["tile_id"] in seen_ids:
            raise ManifestError(f"Duplicate tile_id: {row['tile_id']}")
        seen_ids.add(row["tile_id"])
        if row["split"] not in VALID_SPLITS:
            raise ManifestError(f"Row {row['tile_id']} has invalid split {row['split']!r}")
        previous = group_splits.setdefault(row["scene_group"], row["split"])
        if previous != row["split"]:
            raise ManifestError(f"Scene group {row['scene_group']!r} appears in both {previous} and {row['split']} (leakage).")
        resolved = []
        for item in _paths(row):
            path = Path(item)
            if not path.is_absolute():
                path = root / path
            if not path.is_file():
                raise ManifestError(f"Missing file for {row['tile_id']}: {path}")
            resolved.append(path)
        if all(path.suffix.lower() in {".tif", ".tiff"} for path in resolved):
            try:
                import rasterio
                with rasterio.open(resolved[0]) as vv, rasterio.open(resolved[1]) as vh, rasterio.open(resolved[2]) as optical:
                    grids = [(ds.width, ds.height, ds.crs, ds.transform) for ds in (vv, vh, optical)]
                if not (grids[0] == grids[1] == grids[2]):
                    raise ManifestError(f"VV, VH and optical grids are not co-registered for {row['tile_id']}.")
            except ImportError as exc:
                raise ManifestError("Install rasterio to validate GeoTIFF pairing and grid alignment.") from exc
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    root_reference = os.path.relpath(root, output.parent.resolve())
    output.write_text(
        json.dumps({"version": "2.1", "root": root_reference, "tiles": rows}, indent=2) + "\n",
        encoding="utf-8",
    )
    return output


def load_manifest(path: str | Path) -> list[dict]:
    manifest_path = Path(path).resolve()
    with manifest_path.open("r", encoding="utf-8") as fh:
        payload = json.load(fh)
    rows = payload["tiles"]
    root = Path(payload.get("root", "."))
    if not root.is_absolute():
        root = (manifest_path.parent / root).resolve()
    # Resolve rows relative to their declared data root, not the caller's CWD.
    group_splits: dict[str, str] = {}
    ids: set[str] = set()
    for row in rows:
        if row.get("split") not in VALID_SPLITS:
            raise ManifestError(f"Tile {row.get('tile_id')} has an invalid split {row.get('split')!r}.")
        if row["tile_id"] in ids:
            raise ManifestError(f"Duplicate tile_id: {row['tile_id']}")
        ids.add(row["tile_id"])
        old = group_splits.setdefault(row["scene_group"], row["split"])
        if old != row["split"]:
            raise ManifestError(f"Scene group {row['scene_group']!r} leaks across splits.")
        for key in _paths(row):
            image_path = Path(key)
            if not image_path.is_absolute():
                image_path = root / image_path
            if not image_path.is_file():
                raise ManifestError(f"Missing manifest image: {image_path}")
        for key in ("sar_vv_path", "sar_vh_path", "sar_path", "optical_path"):
            if key in row:
                image_path = Path(row[key])
                if not image_path.is_absolute():
                    row[key] = str((root / image_path).resolve())
    return rows


def _read_image(path: str | Path, bands: tuple[int, ...] | None = None) -> np.ndarray:
    path = Path(path)
    if path.suffix.lower() in {".tif", ".tiff"}:
        try:
            import rasterio
        except ImportError as exc:
            raise RuntimeError("Install rasterio to read SEN12MS/GeoTIFF training tiles.") from exc
        with rasterio.open(path) as ds:
            indexes = bands or tuple(range(1, min(ds.count, 3) + 1))
            if max(indexes) > ds.count:
                raise ValueError(f"{path} has {ds.count} bands, needs {indexes}.")
            data = ds.read(indexes, masked=True).astype(np.float32).filled(np.nan)
        return np.moveaxis(data, 0, -1)
    with Image.open(path) as img:
        if bands:
            arr = np.asarray(img.convert("L"), dtype=np.float32)
            if len(bands) == 1:
                return arr[..., None]
            return np.stack((arr, arr), axis=-1)
        return np.asarray(img.convert("RGB"), dtype=np.float32)


def _resize_float(image: np.ndarray, size: int) -> np.ndarray:
    channels = []
    for i in range(image.shape[-1]):
        band = image[..., i].astype(np.float32)
        finite = np.isfinite(band)
        if not finite.any():
            channels.append(np.zeros((size, size), dtype=np.float32))
            continue
        lo, hi = np.percentile(band[finite], (2, 98))
        norm = np.zeros_like(band) if hi <= lo else np.clip((np.nan_to_num(band, nan=lo) - lo) / (hi - lo), 0, 1)
        im = Image.fromarray(np.round(norm * 255).astype(np.uint8), mode="L")
        if im.size != (size, size):
            im = im.resize((size, size), Image.Resampling.BILINEAR)
        channels.append(np.asarray(im, dtype=np.float32) / 255.0)
    return np.stack(channels, axis=-1)


def normalise_sar_pair(row: dict, size: int = 256) -> np.ndarray:
    """Return VV/VH in H x W x 2. Legacy grayscale rows duplicate channels."""
    if "sar_vv_path" in row and "sar_vh_path" in row:
        vv = _read_image(row["sar_vv_path"], (1,))[..., :1]
        vh = _read_image(row["sar_vh_path"], (1,))[..., :1]
        if vv.shape[:2] != vh.shape[:2]:
            raise ValueError(f"VV and VH dimensions are not aligned for {row['tile_id']}.")
        pair = np.concatenate((vv, vh), axis=-1)
    else:
        legacy = _read_image(row["sar_path"], (1,))
        pair = np.repeat(legacy, 2, axis=-1)
    return _resize_float(pair, size)


def normalise_sar(path_or_row: str | Path | dict, size: int = 256) -> np.ndarray:
    """Compatibility wrapper; pair rows return HxWx2, path inputs one channel."""
    if isinstance(path_or_row, dict):
        return normalise_sar_pair(path_or_row, size)
    image = _read_image(path_or_row, (1,))
    return _resize_float(image[..., :1], size)[..., 0]


def optical_target(row: dict, size: int = 256) -> np.ndarray:
    path = Path(row["optical_path"])
    target = _read_image(path)
    if target.shape[-1] < 3:
        raise ValueError(f"Optical target needs three visible bands (R/G/B order): {row['tile_id']}.")
    target = target[..., :3].astype(np.float32)
    if path.suffix.lower() in {".tif", ".tiff"}:
        # Record optical_scale explicitly: raw Sentinel-2 surface reflectance is commonly
        # stored as integer-scaled values; pre-normalized data should set optical_scale=1.
        scale = float(row.get("optical_scale", 10000.0))
        if scale <= 0:
            raise ValueError(f"optical_scale must be positive for {row['tile_id']}.")
        target = np.clip(np.nan_to_num(target / scale), 0, 1)
    else:
        target = np.clip(target / 255.0, 0, 1)
    resized = []
    for channel in range(3):
        im = Image.fromarray(target[..., channel].astype(np.float32), mode="F")
        if im.size != (size, size):
            im = im.resize((size, size), Image.Resampling.BILINEAR)
        resized.append(np.asarray(im, dtype=np.float32))
    return np.stack(resized, axis=-1)


def get_dataset_class():
    """Import torch lazily so manifest tooling works without PyTorch installed."""
    import torch
    from torch.utils.data import Dataset

    class PairedTileDataset(Dataset):
        def __init__(self, rows: list[dict], size: int = 256, augment: bool = False):
            self.rows, self.size, self.augment = rows, size, augment

        def __len__(self) -> int:
            return len(self.rows)

        def __getitem__(self, index: int):
            row = self.rows[index]
            sar = normalise_sar_pair(row, self.size)
            target = optical_target(row, self.size)
            if self.augment:
                if np.random.rand() < 0.5:
                    sar, target = sar[:, ::-1], target[:, ::-1]
                if np.random.rand() < 0.5:
                    sar, target = sar[::-1, :], target[::-1, :]
            return torch.from_numpy(np.moveaxis(sar.copy(), -1, 0)), torch.from_numpy(np.moveaxis(target.copy(), -1, 0))

    return PairedTileDataset
