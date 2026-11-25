from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest
from PIL import Image
import rasterio
from rasterio.transform import from_origin

from backend.app.core.geospatial import preprocess_pair
from ml.src.data import ManifestError, build_manifest, load_manifest, normalise_sar_pair, optical_target
from ml.src.evaluate import _mean_scores, _panel, score_one
from ml.src.train import manifest_uses_geotiff
from ml.src.sen12ms import create_sen12ms_manifest
from scripts.inspect_png_pair import _stats
from scripts.prepare_png_split_manifest import pair_row


def test_png_training_does_not_require_rasterio_but_geotiff_training_does():
    png_rows = [{"sar_vv_path": "train_B/tile.png", "sar_vh_path": "train_B/tile.png", "optical_path": "train_A/tile.png"}]
    tif_rows = [{"sar_path": "scene.tif", "optical_path": "target.tiff"}]
    assert not manifest_uses_geotiff(png_rows)
    assert manifest_uses_geotiff(tif_rows)


def test_training_and_inference_use_identical_sar_preprocessing():
    vv = np.tile(np.linspace(-20, 5, 40, dtype=np.float32), (32, 1))
    vh = np.tile(np.linspace(-30, 0, 40, dtype=np.float32)[::-1], (32, 1))
    channels = np.stack((vv, vh), axis=-1)
    assert np.array_equal(preprocess_pair(channels, size=16), normalise_sar_pair_from_array(channels, size=16))


def normalise_sar_pair_from_array(channels: np.ndarray, size: int):
    from common.sar_preprocessing import normalize_sar_pair
    return normalize_sar_pair(channels, size=size)


def test_evaluation_metrics_and_failure_panel_are_well_formed():
    target = np.zeros((16, 16, 3), dtype=np.float32)
    scores = score_one(target, target)
    assert scores["MAE_L1"] == 0 and scores["PSNR_dB"] is None
    assert scores["mean_rgb_channel_spread"] == 0
    assert scores["target_rgb_channel_spread"] == 0
    average = _mean_scores([scores])
    assert average["PSNR_perfect_tiles"] == 1 and average["tiles"] == 1
    sar = np.zeros((16, 16, 2), dtype=np.float32)
    assert _panel(sar, target, target).size == (16 * 4, 16 + 26)


def test_evaluation_reports_colour_collapse_against_rgb_reference():
    target = np.zeros((16, 16, 3), dtype=np.float32)
    target[..., 1] = 0.8  # vivid green reference image
    grey_prediction = np.repeat(target[..., 1:2] * 0.5, 3, axis=2)
    scores = score_one(grey_prediction, target)
    assert scores["mean_rgb_channel_spread"] == 0
    assert scores["target_rgb_channel_spread"] > 0.7


def test_png_inspector_distinguishes_green_target_from_grayscale(tmp_path: Path):
    path = tmp_path / "green.png"
    green = np.zeros((8, 8, 3), dtype=np.uint8)
    green[..., 1] = 200
    Image.fromarray(green, mode="RGB").save(path)
    mode, size, means, spread = _stats(path)
    assert mode == "RGB" and size == (8, 8)
    assert means[1] > means[0] and means[1] > means[2]
    assert spread > 0.7


def test_png_manifest_reverses_to_grayscale_B_input_and_coloured_A_target(tmp_path: Path):
    a_path = tmp_path / "train_A" / "tile.png"
    b_path = tmp_path / "train_B" / "tile.png"
    row = pair_row("tile", "train", a_path, b_path, tmp_path, "B", "test source")
    assert row["input_side"] == "B" and row["target_side"] == "A"
    assert row["sar_vv_path"] == "train_B/tile.png"
    assert row["sar_vh_path"] == "train_B/tile.png"
    assert row["optical_path"] == "train_A/tile.png"


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


def test_sen12ms_stacked_s1_and_multispectral_s2_bands(tmp_path: Path):
    transform = from_origin(500000, 2200000, 10, 10)
    common = {"driver": "GTiff", "width": 16, "height": 12, "dtype": "int16",
              "crs": "EPSG:32645", "transform": transform}
    s1_path, s2_path = tmp_path / "ROIs1868_summer_s1_0_p0.tif", tmp_path / "ROIs1868_summer_s2_0_p0.tif"
    with rasterio.open(s1_path, "w", **common, count=2) as ds:
        vv = np.tile(np.arange(16, dtype=np.int16) * 50, (12, 1))
        vh = np.tile(np.arange(16, dtype=np.int16)[::-1] * 40, (12, 1))
        ds.write(np.stack((vv, vh)))
    with rasterio.open(s2_path, "w", **common, count=4) as ds:
        for band, value in enumerate((1000, 2000, 3000, 4000), start=1):
            ds.write(np.full((12, 16), value, dtype=np.int16), band)
    row = {"tile_id": "ROIs1868_summer_0", "scene_group": "ROIs1868", "split": "train",
           "sar_path": s1_path.name, "vv_band": 1, "vh_band": 2,
           "optical_path": s2_path.name, "optical_bands": [4, 3, 2], "optical_scale": 10000,
           "source": "SEN12MS test fixture", "licence": "test-only"}
    manifest = build_manifest([row], tmp_path / "manifests/tiles.json", root=tmp_path)
    loaded = load_manifest(manifest)[0]
    sar = normalise_sar_pair(loaded, size=16)
    target = optical_target(loaded, size=16)
    assert sar.shape == (16, 16, 2) and not np.allclose(sar[..., 0], sar[..., 1])
    assert target[8, 8] == pytest.approx([0.4, 0.3, 0.2], abs=1e-6)


def test_sen12ms_stacked_s1_and_multispectral_s2_bands(tmp_path: Path):
    transform = from_origin(500000, 2200000, 10, 10)
    common = {"driver": "GTiff", "width": 16, "height": 12, "dtype": "int16",
              "crs": "EPSG:32645", "transform": transform}
    s1_path, s2_path = tmp_path / "ROIs1868_summer_s1_0_p0.tif", tmp_path / "ROIs1868_summer_s2_0_p0.tif"
    with rasterio.open(s1_path, "w", **common, count=2) as ds:
        vv = np.tile(np.arange(16, dtype=np.int16) * 50, (12, 1))
        vh = np.tile(np.arange(16, dtype=np.int16)[::-1] * 40, (12, 1))
        ds.write(np.stack((vv, vh)))
    with rasterio.open(s2_path, "w", **common, count=4) as ds:
        for band, value in enumerate((1000, 2000, 3000, 4000), start=1):
            ds.write(np.full((12, 16), value, dtype=np.int16), band)
    row = {"tile_id": "ROIs1868_summer_0", "scene_group": "ROIs1868", "split": "train",
           "sar_path": s1_path.name, "vv_band": 1, "vh_band": 2,
           "optical_path": s2_path.name, "optical_bands": [4, 3, 2], "optical_scale": 10000,
           "source": "SEN12MS-format test fixture", "licence": "test-only"}
    manifest = build_manifest([row], tmp_path / "manifests/tiles.json", root=tmp_path)
    loaded = load_manifest(manifest)[0]
    sar = normalise_sar_pair(loaded, size=16)
    target = optical_target(loaded, size=16)
    assert sar.shape == (16, 16, 2) and not np.allclose(sar[..., 0], sar[..., 1])
    assert target[8, 8] == pytest.approx([0.4, 0.3, 0.2], abs=1e-6)


def test_sen12ms_toolbox_lists_create_paired_manifest_and_roi_validation(tmp_path: Path):
    root = tmp_path / "dataset"
    root.mkdir()
    transform = from_origin(500000, 2200000, 10, 10)
    profile = {"driver": "GTiff", "width": 16, "height": 12, "dtype": "int16",
               "count": 4, "crs": "EPSG:32645", "transform": transform}
    train_files, test_files = [], []
    for split, rois in (("train", ("ROIs0000", "ROIs0001", "ROIs0002")), ("test", ("ROIs0003",))):
        for roi in rois:
            for season in ("spring", "summer"):
                stem = f"{roi}_{season}"
                for sensor in ("s1", "s2"):
                    with rasterio.open(root / f"{stem}_{sensor}_0_p0.tif", "w", **profile) as ds:
                        for band in range(1, 5):
                            ds.write(np.full((12, 16), 1000 * band, dtype=np.int16), band)
                train_files.append(f"{stem}_s1_0_p0.tif") if split == "train" else test_files.append(f"{stem}_s1_0_p0.tif")
    (root / "train_list.txt").write_text("\n".join(train_files), encoding="utf-8")
    (root / "test_list.txt").write_text("\n".join(test_files), encoding="utf-8")
    manifest = create_sen12ms_manifest(root, "train_list.txt", "test_list.txt", tmp_path / "out/manifest.json",
                                       vv_band=1, vh_band=2, rgb_bands=(4, 3, 2), optical_scale=10000,
                                       validation_fraction=0.34, licence_note="synthetic test fixture")
    rows = load_manifest(manifest)
    split_groups = {split: {row["scene_group"] for row in rows if row["split"] == split}
                    for split in ("train", "validation", "test")}
    assert all(split_groups[a].isdisjoint(split_groups[b]) for a, b in (("train", "validation"), ("train", "test"), ("validation", "test")))
    assert len([row for row in rows if row["split"] == "test"]) == 2
    assert all(row["vv_band"] == 1 and row["vh_band"] == 2 and row["optical_bands"] == [4, 3, 2] for row in rows)


def test_png_a_b_split_folders_make_manifest_and_pairs(tmp_path: Path):
    root = tmp_path / "paired_png"
    for split in ("train", "val", "test"):
        (root / f"{split}_A").mkdir(parents=True)
        (root / f"{split}_B").mkdir(parents=True)
        name = "ROIs1868_summer_s000147_p000612.png"
        Image.fromarray(np.full((24, 32, 3), [20, 120, 200], dtype=np.uint8)).save(root / f"{split}_A" / name)
        Image.fromarray(np.tile(np.arange(32, dtype=np.uint8), (24, 1))).save(root / f"{split}_B" / name)
    output = tmp_path / "manifest.json"
    result = subprocess.run([
        sys.executable, "scripts/prepare_png_split_manifest.py", "--data-root", str(root),
        "--output", str(output), "--licence-note", "synthetic test fixture",
    ], cwd=Path(__file__).resolve().parents[2], check=True, capture_output=True, text=True)
    assert "Paired PNG tiles: 3" in result.stdout
    rows = load_manifest(output)
    train = next(row for row in rows if row["split"] == "train")
    sar = normalise_sar_pair(train, size=16)
    target = optical_target(train, size=16)
    assert train["input_side"] == "B" and train["target_side"] == "A"
    assert Path(train["sar_vv_path"]).parent.name == "train_B"
    assert Path(train["optical_path"]).parent.name == "train_A"
    assert sar.shape == (16, 16, 2) and np.array_equal(sar[..., 0], sar[..., 1])
    assert target.shape == (16, 16, 3) and target[8, 8, 1] == pytest.approx(120 / 255, abs=1e-5)


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
