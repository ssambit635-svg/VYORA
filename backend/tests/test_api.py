"""End-to-end API tests for the local, development-mode demo flow."""
import io
import json

import numpy as np
import rasterio
from rasterio.io import MemoryFile
from rasterio.transform import from_origin
from PIL import Image

from app.core.preprocess import decode_grayscale, preprocess_sar


def test_health_reports_honest_mode(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["mode"] == "development"
    assert body["is_ai_inference"] is False
    assert body["model_version"] == "dev-heuristic-v0"
    assert "not an official map" in body["disclaimer"]


def test_demo_scenes(client):
    body = client.get("/api/demo-scenes").json()
    assert len(body["scenes"]) == 4
    first = body["scenes"][0]
    assert first["image_url"].startswith("/api/demo-scenes/")
    assert "SYNTHETIC" in first["data_note"]
    image = client.get(first["image_url"])
    assert image.status_code == 200
    assert image.headers["content-type"] == "image/png"


def test_demo_inference_and_exports(client):
    response = client.post("/api/infer", data={"demo_scene_id": "coastal-water", "source_type": "demo"})
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["result_id"]
    assert body["mode"] == "development"
    assert body["is_ai_inference"] is False
    assert set(body["feature_estimates"]) == {"water", "vegetation", "built_up", "bare_other"}
    assert abs(sum(body["feature_estimates"].values()) - 1.0) < 1e-3
    assert 0 <= body["confidence_summary"]["mean"] <= 1
    assert body["metrics"]["runtime_ms"] > 0
    assert body["metrics"]["held_out_evaluation"] == "not_run"

    for key in ("input", "colour", "confidence"):
        image = client.get(body["urls"][key])
        assert image.status_code == 200
        assert image.content[:8] == b"\x89PNG\r\n\x1a\n"
        shape = np.asarray(Image.open(io.BytesIO(image.content))).shape
        assert shape[:2] == (256, 256)

    exported = client.get(body["urls"]["json"])
    assert exported.status_code == 200
    assert json.loads(exported.content)["result_id"] == body["result_id"]


def test_dual_polarization_geotiff_round_trip(client):
    profile = {
        "driver": "GTiff", "height": 32, "width": 24, "count": 2,
        "dtype": "int16", "nodata": -9999, "crs": "EPSG:32645", "transform": from_origin(500000, 2200000, 10, 10),
    }
    with MemoryFile() as mem:
        with mem.open(**profile) as ds:
            vv = np.tile(np.linspace(0, 1000, 24, dtype=np.int16), (32, 1))
            vh = np.tile(np.linspace(1000, 0, 24, dtype=np.int16), (32, 1))
            vv[0, 0] = vh[0, 0] = -9999
            ds.write(np.stack([vv, vh]))
        payload = mem.read()

    response = client.post("/api/infer", files={"file": ("pair.tif", payload, "image/tiff")})
    assert response.status_code == 200, response.text
    result = response.json()
    assert result["input"]["input_kind"] == "geotiff-vv-vh"
    assert result["input"]["polarizations"] == ["VV", "VH"]
    assert result["input"]["crs"] == "EPSG:32645"
    assert result["input"]["width"] == 24 and result["input"]["height"] == 32
    geotiff = client.get(result["urls"]["geotiff"])
    assert geotiff.status_code == 200
    with MemoryFile(geotiff.content) as mem:
        with mem.open() as ds:
            assert ds.count == 3 and ds.crs.to_string() == "EPSG:32645"
            assert ds.bounds == rasterio.coords.BoundingBox(500000.0, 2199680.0, 500240.0, 2200000.0)


def test_deterministic_preprocessing_and_result(client):
    payload = (Image.new("L", (256, 256), 90)).tobytes()
    # png bytes
    buffer = io.BytesIO()
    Image.new("L", (256, 256), 90).save(buffer, format="PNG")
    file = ("sar.png", buffer.getvalue(), "image/png")
    a = client.post("/api/infer", files={"file": file}).json()
    b = client.post("/api/infer", files={"file": file}).json()
    assert a["feature_estimates"] == b["feature_estimates"]
    assert a["metrics"]["input_output_edge_agreement_proxy"] == b["metrics"]["input_output_edge_agreement_proxy"]
    assert payload  # keep the grayscale construction meaningful in the test

    tile = preprocess_sar(decode_grayscale(buffer.getvalue()))
    assert tile.shape == (256, 256)
    assert np.isfinite(tile).all()
    assert tile.min() >= 0 and tile.max() <= 1


def test_upload_validation(client):
    bad_type = client.post(
        "/api/infer",
        files={"file": ("notes.txt", b"not an image", "text/plain")},
    )
    assert bad_type.status_code == 400
    assert "GeoTIFF" in bad_type.json()["detail"]

    corrupt = client.post(
        "/api/infer",
        files={"file": ("fake.png", b"\x89PNG\r\n\x1a\ncorrupted", "image/png")},
    )
    assert corrupt.status_code == 400

    huge = client.post(
        "/api/infer",
        files={"file": ("huge.png", b"\x89PNG\r\n\x1a\n" + b"0" * (10 * 1024 * 1024), "image/png")},
    )
    assert huge.status_code == 400
    assert "10 MB" in huge.json()["detail"]

    both = client.post(
        "/api/infer",
        data={"demo_scene_id": "coastal-water"},
        files={"file": ("sar.png", b"x", "image/png")},
    )
    assert both.status_code == 400


def test_unknown_scene(client):
    assert client.post("/api/infer", data={"demo_scene_id": "does-not-exist"}).status_code == 404
