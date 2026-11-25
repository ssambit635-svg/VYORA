# Vyora API

Base URL: `http://localhost:8000` (or laptop LAN address); interactive docs at `/docs`. React/Vite is the accepted primary UI. Streamlit is optional and uses the same model/input checks.

Uploads are processed in memory. Generated result assets are held in a bounded, expiring in-memory cache; user input files are not written to disk.

## `GET /api/health`

Returns runtime mode, checkpoint/version, input representation, accepted model input, PyTorch availability, checkpoint availability, and disclaimer. Always check this endpoint before describing an inference as AI. A development fallback is never reported as trained AI.

## `GET /api/demo-scenes`

Lists four bundled **synthetic**, non-georeferenced illustrations and their explicit `data_note`. They are interface previews, not model-training/evaluation data.

## `POST /api/infer`

Send either one multipart `file` or form field `demo_scene_id` (not both).

| Input | Rules |
|---|---|
| Current B→A PNG checkpoint | Accepts a grayscale paired PNG tile; the single channel is duplicated to two model channels. A GeoTIFF is rejected because this checkpoint was not trained on VV/VH. |
| VV/VH-trained checkpoint | Accepts a two-band GeoTIFF (band 1=VV, band 2=VH); rejects a single-channel PNG/JPEG preview as not genuine dual-pol. |
| Development fallback | Accepts previews for interface testing, clearly labelled as non-AI. |
| GeoTIFF limits | Up to 50 MB; must already be radiometrically calibrated, terrain-corrected and co-registered. CRS/transform are preserved in preview export. |
| PNG/JPEG limits | Up to 10 MB. PNG has no geospatial coordinates. |

For the current checkpoint, use a grayscale PNG upload. The synthetic gallery is not shown as a trained-scene substitute in the React PNG-prototype mode.

```bash
curl -F 'file=@paired-grayscale-tile.png;type=image/png' http://localhost:8000/api/infer
```

The response includes model/mode/input details, consistency-method caveat, runtime, evaluation status for the exact checkpoint, and result URLs. Class shares are empty for the current PNG model because it has no classification head. A legacy or development path may expose explicitly labelled palette/rule-derived shares; these are not validated classes.

Example response fields (illustrative only):

```json
{
  "mode": "model",
  "model_version": "resunet-paired-png-prototype-v0.2-b-to-a",
  "is_ai_inference": true,
  "input": {
    "channels": 2,
    "polarizations": ["duplicated grayscale preview", "not genuine dual-pol"],
    "input_kind": "single-channel-preview-duplicated",
    "crs": null,
    "preprocessing": "independent robust normalization, despeckle and resize to 256x256"
  },
  "feature_estimates": {},
  "confidence_method": "original-vs-flipped output consistency; not calibrated uncertainty",
  "metrics": {
    "held_out_evaluation": "documented_200_tile_subset_geographic_independence_unverified"
  },
  "urls": {
    "input": "/api/results/<id>/input",
    "colour": "/api/results/<id>/image",
    "confidence": "/api/results/<id>/confidence",
    "json": "/api/results/<id>/export",
    "geotiff": null
  }
}
```

The subset status means a report exists for this exact prototype. It does not mean this request's tile was evaluated or that geographic independence was established. Other checkpoints return `not_evaluated_for_this_checkpoint`.

## Result endpoints

- `GET /api/results/{id}/input` — input preview PNG.
- `GET /api/results/{id}/image` — estimated RGB-style PNG.
- `GET /api/results/{id}/confidence` — consistency-visualization PNG, not calibrated uncertainty.
- `GET /api/results/{id}/geotiff` — CRS/extent-preserving preview if source was georeferenced and checkpoint/input contract allowed inference; otherwise 404.
- `GET /api/results/{id}/export` — JSON result summary.

Unknown/expired IDs return 404.

## Safety notes

- GeoTIFF output is resized to the 256×256 model canvas. It is not a full-resolution analytical raster.
- Rasterio handles file I/O; the service does not perform physical Sentinel-1 calibration or terrain correction.
- Restrict the service to a trusted LAN; public authentication and rate limiting are not configured.
