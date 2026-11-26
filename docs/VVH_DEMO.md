# VV/VH visual-demo mode (not a trained VV/VH model)

This path uses the user's downloaded SAFE measurement TIFFs to create a small, display-only VV/VH tile. The current SAFE files have no CRS and an identity transform, so the resulting preview is explicitly non-geospatial. The helper does not apply Sentinel-1 calibration, terrain correction, or geocoding. It is not a training/evaluation input and its output is not a model prediction.

## Prepare the local preview on Windows

Run from the VYORA repository root. The output is written under ignored `data/raw/` and is not added to Git.

```powershell
$safe = 'C:\Users\SAnjeeb\Downloads\vvvh zip\S1D_IW_GRDH_1SDV_20261030T001308_20261030T001333_005237_009F2E_2A00.SAFE'
$measurement = Join-Path $safe 'measurement'
$vv = Get-ChildItem -LiteralPath $measurement -Filter '*-vv-*.tiff' -File | Select-Object -First 1
$vh = Get-ChildItem -LiteralPath $measurement -Filter '*-vh-*.tiff' -File | Select-Object -First 1
if (-not $vv -or -not $vh) { throw 'VV/VH measurement TIFF not found.' }
python scripts/prepare_vvh_demo_tile.py --vv $vv.FullName --vh $vh.FullName --output data/raw/sentinel1/vvh_demo_256.tif --allow-unreferenced
```

The helper confirms equal source dimensions and affine metadata, downsamples the two distinct bands to 256×256 and records that the preview is not calibrated/geospatial/model output.

## Show the preview through the app's honest development fallback

Stop the current API process with Ctrl+C, then start a development-mode API from the repository root. Leave Vite running if it is already serving the UI.

```powershell
$env:VYORA_MODE = 'development'
Remove-Item Env:VYORA_CHECKPOINT -ErrorAction SilentlyContinue
python -m uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port 8000
```

Upload `data/raw/sentinel1/vvh_demo_256.tif`. The UI should say **DEVELOPMENT MODE — not AI inference**. This demonstrates the VV/VH input path using a fixed, hand-authored visualization only. It does not fulfill the trained VV/VH-to-optical model requirement. No GeoTIFF export is offered because the source measurements have no usable CRS/transform.

For a real VV/VH model, use a verified, calibrated/geocoded VV/VH plus paired optical-target dataset, train a `VV_VH_pair` checkpoint, and evaluate it on geographically held-out scenes. Do not relabel this demo fallback as that model.
