# Implementation decisions and deck alignment

The team's attached Voltrix PDF is treated as the controlling technical scope. Product name remains **Vyora**; the earlier specs use DrishtiSAR as a working name.

| Decision | Reason | Result / limit |
|---|---|---|
| Align model input to VV + VH, output to RGB-style estimate | Deck's core claim and system diagram are explicitly dual-polarization | `ml/src/model.py` is now a 2-input/3-output ResU-Net generator; no checkpoint is supplied |
| Add Rasterio VV/VH GeoTIFF read and GeoTIFF preview export | Deck requires geospatial input/output and CRS/transform preservation | Implemented and round-trip tested on a synthetic raster; full analytical/resolution export is not claimed |
| Require pre-calibrated, terrain-corrected, co-registered SAR input | Rasterio/NumPy percentile scaling is not physical Sentinel-1 calibration | Current code normalizes bands; it does not run SNAP/GDAL calibration/terrain correction |
| Add Streamlit interface | Presentation names Streamlit | `streamlit_app.py` / `scripts/run_streamlit.sh` is deck-aligned; React + FastAPI stays optional, not the live pitch path |
| Dataset manifest accepts explicit VV, VH and optical target paths | Avoid silently treating grayscale as dual-pol and enable paired geospatial training | Scene-group split and TIFF grid checks added; real SEN12MS subset still absent |
| Remove unsupervised confidence/class model heads | No uncertainty labels or land-cover masks exist in paired image-only data | Confidence is TTA output agreement only; feature cards are fixed palette shares, neither a calibrated probability nor learned segmentation |
| Keep synthetic scenes only as clearly labelled UI fallbacks | No real licensed imagery bundled | Synthetic gallery is never training/evaluation evidence |
| Keep test/metrics language conservative | No real held-out evaluation | `docs/EVALUATION.md` remains Not run; smoke data must not be quoted |

## Highest-priority remaining work

1. Fill the PDF's visible Team ID placeholder and PS code (`HK26-PS-19`) using the official event registration.
2. Obtain and document lawful access to paired SEN12MS or other aligned SAR/optical samples; record product level, band order/scale, target scale, acquisition/cloud metadata, source and licence.
3. Validate upstream radiometric calibration/terrain correction and co-registration. This repository does not perform those geophysical steps.
4. Build scene-group splits, train an actual checkpoint, and run evaluation on held-out regions. Commit only small lawful artifacts; otherwise keep raw data/checkpoint outside Git and document where judges can access them.
5. Rehearse the Streamlit interface and a prepared GeoTIFF on the actual laptop/phone network.

See `docs/PPT_ALIGNMENT_AND_SELECTION_GUIDE.md` for slide mapping, judge keywords, risks and presentation priorities.
