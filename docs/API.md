# Vyora API (alternate React/FastAPI interface)

Base URL: `http://localhost:8000` (or laptop LAN address); interactive docs at `/docs`. The deck-aligned Streamlit UI runs separately on port 8501 and calls the same local inference functions directly.

Uploads/results are held in memory only, with short-lived result IDs. No user images are written to disk.

## `GET /api/health`

Reports `mode`, `model_version`, `is_ai_inference`, checkpoint availability and disclaimer. A development fallback is never reported as trained AI.

## `GET /api/demo-scenes`

Lists the four bundled **synthetic**, non-georeferenced illustrations and their explicit `data_note`.

## `POST /api/infer`

Send either one multipart `file` or form field `demo_scene_id` (not both).

| Input | Rules |
|---|---|
| Two-band GeoTIFF | Up to 50 MB; band 1=VV, band 2=VH; CRS/transform retained. Must already be calibrated, terrain-corrected and co-registered. |
| PNG/JPEG preview | Up to 10 MB; single-channel data is duplicated across the model channels and is not true dual-pol input. |
| Demo scene | ID returned by `/api/demo-scenes`; synthetic only. |

```bash
curl -F 'file=@prepared-vv-vh.tif;type=image/tiff' http://localhost:8000/api/infer
curl -F 'demo_scene_id=coastal-water' http://localhost:8000/api/infer
```

The response includes mode/version, input kind, channels and preprocessing, source CRS/transform when present, feature-share caveat, consistency-method caveat, runtime and result URLs. Values depend on the actual request; no held-out metrics are inserted.

```json
{
  "mode": "development",
  "model_version": "dev-heuristic-v0",
  "is_ai_inference": false,
  "input": {
    "channels": 2,
    "polarizations": ["VV", "VH"],
    "input_kind": "geotiff-vv-vh",
    "crs": "<input CRS>",
    "preprocessing": "per-band robust normalization and 256x256 resize"
  },
  "outputs": {
    "colour": "3-channel estimated visual interpretation PNG",
    "geotiff": "extent/CRS-preserving 256x256 preview, only for GeoTIFF input"
  },
  "metrics": {"held_out_evaluation": "not_run"},
  "urls": {
    "input": "/api/results/<id>/input",
    "colour": "/api/results/<id>/image",
    "confidence": "/api/results/<id>/confidence",
    "geotiff": "/api/results/<id>/geotiff",
    "json": "/api/results/<id>/export"
  }
}
```

## Result endpoints

- `GET /api/results/{id}/input` — input preview PNG.
- `GET /api/results/{id}/image` — estimated RGB-style PNG.
- `GET /api/results/{id}/confidence` — consistency-visualization PNG (not calibrated uncertainty).
- `GET /api/results/{id}/geotiff` — CRS/extent-preserving preview if source was georeferenced; `404` otherwise.
- `GET /api/results/{id}/export` — JSON response summary.

Result assets expire after the configured in-memory retention interval. Unknown/expired IDs return 404.

## Safety notes

- GeoTIFF output is resized to the 256×256 model canvas. It is not a full-resolution scientific product.
- Rasterio handles file I/O; this API does not perform Sentinel-1 radiometric calibration or terrain correction.
- Restrict the service to a trusted LAN; no authentication/rate-limiting is configured for public exposure.
