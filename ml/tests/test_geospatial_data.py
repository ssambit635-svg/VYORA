from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

from backend.app.core.geospatial import preprocess_pair
from ml.src.data import ManifestError, build_manifest, normalise_sar_pair


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
