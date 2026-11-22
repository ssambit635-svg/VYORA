from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest
from PIL import Image
import rasterio
from rasterio.transform import from_origin

from backend.app.core.geospatial import preprocess_pair
from ml.src.data import ManifestError, build_manifest, load_manifest, normalise_sar_pair, optical_target


def test_dual_pol_preprocessing_keeps_two_bands_distinct():
    vv = np.tile(np.linspace(0, 100, 32, dtype=np.float32), (24, 1))
    vh = np.tile(np.linspace(100, 0, 32, dtype=np.float32), (24, 1))
    prepared = preprocess_pair(np.stack((vv, vh), axis=-1), size=16, despeckle=False)
    assert prepared.shape == (16, 16, 2)
    assert np.isfinite(prepared).all()
    assert prepared.min() >= 0 and prepared.max() <= 1
    assert not np.allclose(prepared[..., 0], prepared[..., 1])


def test_paired_png_manifest_smoke_inputs(tmp_path: Path):
    vv = np.arange(64, dtype=np.uint8).reshape(8, 8)
    vh = (255 - vv).astype(np.uint8)
    target = np.stack((vv, vh, vv), axis=-1)
    for name, array in (("vv.png", vv), ("vh.png", vh), ("rgb.png", target)):
        Image.fromarray(array).save(tmp_path / name)
    row = {
        "tile_id": "tile-1", "scene_group": "scene-a", "split": "train",
        "sar_vv_path": "vv.png", "sar_vh_path": "vh.png", "optical_path": "rgb.png",
        "source": "unit test", "licence": "synthetic", "optical_scale": 255,
    }
    manifest = build_manifest([row], tmp_path / "manifest.json", root=tmp_path)
    loaded = json.loads(manifest.read_text())["tiles"][0]
    pair = normalise_sar_pair({key: str(tmp_path / loaded[key]) for key in ("sar_vv_path", "sar_vh_path")} | {"tile_id": "tile-1"}, size=16)
    assert pair.shape == (16, 16, 2)
    assert not np.allclose(pair[..., 0], pair[..., 1])


def test_int16_geotiff_training_pair_handles_nodata_and_alignment(tmp_path: Path):
    transform = from_origin(500000, 2200000, 10, 10)
    profile = {"driver": "GTiff", "width": 12, "height": 10, "dtype": "int16",
               "crs": "EPSG:32645", "transform": transform, "nodata": -9999}
    vv_path, vh_path, rgb_path = (tmp_path / n for n in ("vv.tif", "vh.tif", "rgb.tif"))
    for path, count in ((vv_path, 1), (vh_path, 1), (rgb_path, 3)):
        with rasterio.open(path, "w", **profile, count=count) as ds:
            for band in range(1, count + 1):
                values = np.full((10, 12), 1000 * band, dtype=np.int16)
                values[0, 0] = -9999
                ds.write(values, band)
    row = {"tile_id": "geo-1", "scene_group": "region-1", "split": "train",
           "sar_vv_path": "vv.tif", "sar_vh_path": "vh.tif", "optical_path": "rgb.tif",
           "optical_scale": 10000, "source": "synthetic test", "licence": "test-only"}
    manifest = build_manifest([row], tmp_path / "manifests/tiles.json", root=tmp_path)
    loaded = load_manifest(manifest)[0]
    sar = normalise_sar_pair(loaded, size=16)
    target = optical_target(loaded, size=16)
    assert sar.shape == (16, 16, 2) and target.shape == (16, 16, 3)
    assert np.isfinite(sar).all() and np.isfinite(target).all()


def test_manifest_resolves_relative_paths_from_declared_data_root(tmp_path: Path):
    data_root = tmp_path / "data"
    raw = data_root / "raw"
    raw.mkdir(parents=True)
    Image.fromarray(np.zeros((8, 8), dtype=np.uint8)).save(raw / "sar.png")
    Image.fromarray(np.zeros((8, 8, 3), dtype=np.uint8)).save(raw / "rgb.png")
    manifest_path = data_root / "manifests" / "tiles.json"
    row = {"tile_id": "tile", "scene_group": "scene", "split": "train",
           "sar_path": "raw/sar.png", "optical_path": "raw/rgb.png",
           "source": "unit", "licence": "synthetic"}
    build_manifest([row], manifest_path, root=data_root)
    loaded = load_manifest(manifest_path)
    assert Path(loaded[0]["sar_path"]).is_absolute()
    assert Path(loaded[0]["optical_path"]).is_file()


def test_manifest_rejects_scene_group_split_leakage(tmp_path: Path):
    img = np.zeros((8, 8), dtype=np.uint8)
    for name in ("sar.png", "rgb.png"):
        Image.fromarray(img if name == "sar.png" else np.zeros((8, 8, 3), dtype=np.uint8)).save(tmp_path / name)
    rows = []
    for tile, split in (("a", "train"), ("b", "test")):
        rows.append({"tile_id": tile, "scene_group": "same-area", "split": split,
                     "sar_path": "sar.png", "optical_path": "rgb.png", "source": "unit", "licence": "synthetic"})
    with pytest.raises(ManifestError, match="appears in both"):
        build_manifest(rows, tmp_path / "bad.json", root=tmp_path)


def test_resunet_has_two_input_and_three_output_channels():
    torch = pytest.importorskip("torch")
    from ml.src.model import build_model
    model = build_model(base_channels=4, input_channels=2).eval()
    with torch.inference_mode():
        rgb = model(torch.zeros(1, 2, 32, 32))
    assert tuple(rgb.shape) == (1, 3, 32, 32)
