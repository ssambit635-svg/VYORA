"""Leakage-checked paired VV/VH -> optical tile dataset.

A row may use separate `sar_vv_path`/`sar_vh_path` files, or a native stacked
`sar_path` GeoTIFF with explicit 1-based `vv_band`/`vh_band` selectors.
Multispectral targets use explicit `optical_bands` in R/G/B order. GeoTIFF
pairs must be co-registered before being added to a manifest.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

import numpy as np
from PIL import Image

from common.sar_preprocessing import normalize_sar_pair as _shared_normalize_sar_pair

BASE_COLUMNS = {"tile_id", "scene_group", "split", "optical_path", "source", "licence"}
VALID_SPLITS = {"train", "validation", "test"}


class ManifestError(ValueError):
    pass


def _paths(row: dict) -> tuple[str, ...]:
    if "sar_vv_path" in row and "sar_vh_path" in row:
        return row["sar_vv_path"], row["sar_vh_path"], row["optical_path"]
    if "sar_path" in row:
        return row["sar_path"], row["optical_path"]
    raise ManifestError("Rows need separate sar_vv_path/sar_vh_path or one stacked sar_path with VV/VH band indexes.")


def _validate_geotiff_layout(row: dict, paths: list[Path]) -> None:
    """Validate raster grid and explicit 1-based band indexes when inputs are TIFFs."""
    if not all(path.suffix.lower() in {".tif", ".tiff"} for path in paths):
        return
    try:
        import rasterio
    except ImportError as exc:
        raise ManifestError("Install rasterio to validate GeoTIFF pairing and grid alignment.") from exc
    if "sar_vv_path" in row and "sar_vh_path" in row:
        vv_idx = int(row.get("vv_band", 1))
        vh_idx = int(row.get("vh_band", 1))
        try:
            with rasterio.open(paths[0]) as vv, rasterio.open(paths[1]) as vh, rasterio.open(paths[2]) as optical:
                rasters = (vv, vh, optical)
                indexes = (vv_idx, vh_idx)
                grids = [(ds.width, ds.height, ds.crs, ds.transform) for ds in rasters]
                opt_bands = tuple(int(i) for i in row.get("optical_bands", (1, 2, 3)))
                if vv_idx < 1 or vv_idx > vv.count or vh_idx < 1 or vh_idx > vh.count:
                    raise ManifestError(f"Invalid VV/VH band index for {row['tile_id']}.")
                if "optical_bands" not in row and optical.count != 3:
                    raise ManifestError(f"Set optical_bands=[R,G,B] for multispectral target {row['tile_id']}.")
                if len(opt_bands) != 3 or min(opt_bands) < 1 or max(opt_bands) > optical.count:
                    raise ManifestError(f"Invalid optical_bands for {row['tile_id']}.")
        except ManifestError:
            raise
        except Exception as exc:
            raise ManifestError(f"Could not inspect GeoTIFFs for {row['tile_id']}: {exc}") from exc
        if not (grids[0] == grids[1] == grids[2]):
            raise ManifestError(f"VV, VH and optical grids are not co-registered for {row['tile_id']}.")
        return

    if "vv_band" not in row or "vh_band" not in row:
        raise ManifestError(f"Stacked GeoTIFF {row['tile_id']} must declare 1-based vv_band and vh_band.")
    try:
        with rasterio.open(paths[0]) as sar, rasterio.open(paths[1]) as optical:
            vv_idx, vh_idx = int(row["vv_band"]), int(row["vh_band"])
            opt_bands = tuple(int(i) for i in row.get("optical_bands", (1, 2, 3)))
            if min(vv_idx, vh_idx) < 1 or max(vv_idx, vh_idx) > sar.count:
                raise ManifestError(f"Invalid VV/VH band index for {row['tile_id']}.")
            if len(opt_bands) != 3 or min(opt_bands) < 1 or max(opt_bands) > optical.count:
                raise ManifestError(f"optical_bands must list 3 valid R/G/B indexes for {row['tile_id']}.")
            sar_grid = (sar.width, sar.height, sar.crs, sar.transform)
            optical_grid = (optical.width, optical.height, optical.crs, optical.transform)
    except ManifestError:
        raise
    except Exception as exc:
        raise ManifestError(f"Could not inspect GeoTIFFs for {row['tile_id']}: {exc}") from exc
    if sar_grid != optical_grid:
        raise ManifestError(f"SAR and optical grids are not co-registered for {row['tile_id']}.")


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
        _validate_geotiff_layout(row, resolved)
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
        _validate_geotiff_layout(row, [Path(item) for item in _paths(row)])
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
            if not indexes or min(indexes) < 1 or max(indexes) > ds.count:
                raise ValueError(f"{path} has {ds.count} bands, needs 1-based indexes {indexes}.")
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
    """Return VV/VH in H x W x 2 from separate files or a stacked GeoTIFF."""
    if "sar_vv_path" in row and "sar_vh_path" in row:
        vv = _read_image(row["sar_vv_path"], (int(row.get("vv_band", 1)),))[..., :1]
        vh = _read_image(row["sar_vh_path"], (int(row.get("vh_band", 1)),))[..., :1]
        if vv.shape[:2] != vh.shape[:2]:
            raise ValueError(f"VV and VH dimensions are not aligned for {row['tile_id']}.")
        pair = np.concatenate((vv, vh), axis=-1)
    elif "vv_band" in row and "vh_band" in row:
        path = row["sar_path"]
        if Path(path).suffix.lower() not in {".tif", ".tiff"}:
            raise ValueError("Explicit VV/VH band indexes require a multiband GeoTIFF.")
        vv = _read_image(path, (int(row["vv_band"]),))[..., :1]
        vh = _read_image(path, (int(row["vh_band"]),))[..., :1]
        pair = np.concatenate((vv, vh), axis=-1)
    else:
        legacy = _read_image(row["sar_path"], (1,))
        pair = np.repeat(legacy, 2, axis=-1)
    return _shared_normalize_sar_pair(pair, size=size)


def normalise_sar(path_or_row: str | Path | dict, size: int = 256) -> np.ndarray:
    """Compatibility wrapper; pair rows return HxWx2, path inputs one channel."""
    if isinstance(path_or_row, dict):
        return normalise_sar_pair(path_or_row, size)
    image = _read_image(path_or_row, (1,))
    return _resize_float(image[..., :1], size)[..., 0]


def optical_target(row: dict, size: int = 256) -> np.ndarray:
    path = Path(row["optical_path"])
    is_tiff = path.suffix.lower() in {".tif", ".tiff"}
    if is_tiff:
        import rasterio
        with rasterio.open(path) as dataset:
            if "optical_bands" not in row and dataset.count != 3:
                raise ValueError(f"Set optical_bands=[R,G,B] for multispectral target {row['tile_id']}.")
            bands = tuple(int(i) for i in row.get("optical_bands", (1, 2, 3)))
            if len(bands) != 3 or min(bands) < 1 or max(bands) > dataset.count:
                raise ValueError(f"optical_bands must specify 3 valid 1-based R/G/B indexes for {row['tile_id']}.")
        target = _read_image(path, bands).astype(np.float32)
        # Confirm scale from the exact SEN12MS release/metadata. The default is common
        # for integer-scaled reflectance; set optical_scale=1 for [0,1] inputs.
        scale = float(row.get("optical_scale", 10000.0))
        if scale <= 0:
            raise ValueError(f"optical_scale must be positive for {row['tile_id']}.")
        target = np.clip(np.nan_to_num(target / scale), 0, 1)
    else:
        target = np.asarray(_read_image(path), dtype=np.float32)
        if target.shape[-1] < 3:
            raise ValueError(f"Optical target needs three visible bands (R/G/B order): {row['tile_id']}.")
        target = np.clip(target[..., :3] / 255.0, 0, 1)
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
