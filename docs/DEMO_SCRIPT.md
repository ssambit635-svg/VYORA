# Vyora live demo script (2–3 minutes)

## Before the room

- Install `requirements-ui.txt`; run `bash scripts/run_streamlit.sh` and confirm the app at port 8501.
- Prepare one legally usable, calibrated/co-registered two-band GeoTIFF (VV band 1, VH band 2) if available. Confirm CRS, transform and output bounds. Never improvise calibration claims.
- Keep the synthetic gallery fallback available if the real input/checkpoint fails; label it synthetic and development-mode.
- Confirm checkpoint status in the UI. Do not call a fallback output AI-generated.

## Talk track

**Problem (20 sec):** “Sentinel-1 records microwave backscatter, not visible RGB. Dual-pol VV/VH is information-rich but difficult for non-specialists to scan. We are building a visual interpretation aid, not a map or warning product.”

**Method (30 sec):** “Our target workflow pairs calibrated Sentinel-1 VV/VH with co-registered Sentinel-2 visible targets. A compact U-Net is our stable first baseline. We split by geographic scene group to avoid nearby-patch leakage.”

**Demo (45 sec):** Choose Upload SAR raster and load a prepared two-band GeoTIFF. Explain that bands 1/2 are VV/VH and show the CRS/extent. Interpret, compare the original radar preview with the estimated optical-style output, toggle the consistency map and download PNG/JSON/GeoTIFF preview. Explain that the preview export preserves the input extent and CRS but is 256×256, not an analytical product.

**Evidence (30 sec):** “The app status tells us whether a trained checkpoint is loaded. The bundled gallery is synthetic. We have no real-data held-out evaluation to report yet, so we will not invent MAE, SSIM, PSNR or accuracy.” If the team has subsequently trained and evaluated, replace this line with exact split/hardware/result evidence and show the saved report.

**Limits (20 sec):** “An optical reference may differ in date, clouds and illumination, so generated appearance is not recovered true colour. Our consistency cue is flip-view agreement, not calibrated uncertainty. Always inspect original SAR and authoritative products.”

## Fallback

If no trained checkpoint exists, say explicitly: “This run is the development fallback to demonstrate UI and input/export plumbing; it is not the learned model.” If no lawful real GeoTIFF is available, use the synthetic scene and explain it has no geography or polarizations.
