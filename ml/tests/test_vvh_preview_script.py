import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import rasterio
from affine import Affine

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "prepare_vvh_demo_tile.py"


def _measurement(path: Path, values: np.ndarray) -> None:
    with rasterio.open(
        path, "w", driver="GTiff", width=values.shape[1], height=values.shape[0],
        count=1, dtype="uint16", transform=Affine.identity(),
    ) as dataset:
        dataset.write(values.astype(np.uint16), 1)


def test_unreferenced_safe_measurements_make_labelled_two_band_preview(tmp_path: Path):
    vv_path, vh_path = tmp_path / "source-vv.tiff", tmp_path / "source-vh.tiff"
    _measurement(vv_path, np.arange(64, dtype=np.uint16).reshape(8, 8))
    _measurement(vh_path, np.arange(64, dtype=np.uint16).reshape(8, 8)[::-1])
    output = tmp_path / "preview.tif"

    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--vv", str(vv_path), "--vh", str(vh_path),
         "--output", str(output), "--size", "32", "--allow-unreferenced"],
        cwd=ROOT, capture_output=True, text=True, check=True,
    )
    summary = json.loads(result.stdout)
    assert summary["bands"] == ["VV", "VH"]
    assert summary["geospatial"] is False
    assert "not a trained VV/VH model output" in summary["notice"]
    with rasterio.open(output) as dataset:
        assert dataset.count == 2 and (dataset.width, dataset.height) == (32, 32)
        assert dataset.crs is None
        assert dataset.tags()["VYORA_IS_AI_INFERENCE"] == "false"
        assert dataset.tags()["VYORA_GEOSPATIAL"] == "false"


def test_unreferenced_pair_requires_explicit_demo_acknowledgement(tmp_path: Path):
    vv_path, vh_path = tmp_path / "source-vv.tiff", tmp_path / "source-vh.tiff"
    values = np.arange(64, dtype=np.uint16).reshape(8, 8)
    _measurement(vv_path, values)
    _measurement(vh_path, values)
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--vv", str(vv_path), "--vh", str(vh_path),
         "--output", str(tmp_path / "preview.tif"), "--size", "32"],
        cwd=ROOT, capture_output=True, text=True,
    )
    assert result.returncode == 2
    assert "no usable CRS/transform" in result.stderr
