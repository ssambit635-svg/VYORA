# Vyora architecture — aligned to the presentation

## Intended supervised workflow

```text
SEN12MS / licensed paired scenes (not currently bundled)
 Sentinel-1 VV + VH         Sentinel-2 visible R/G/B targets
          │                               │
          └─ validate pair/grid, scale, clouds, source and licence ─┘
                                  │
                     scene-group train/validation/test split
                                  │
           compact ResU-Net: 2 input channels → 3 RGB-style channels
                    L1 + SSIM + edge reconstruction objective
                                  │
              held-out MAE / PSNR / SSIM / edge + failure review
                                  │
                            checkpoint
```

## Local inference paths

```text
Streamlit UI (deck-aligned, port 8501) ─┐
                                       ├─ decode VV/VH → robust per-band normalize
React UI + FastAPI (optional, port 8000)┘  → checkpoint or labelled dev fallback
                                               → RGB preview + consistency cue
                                               → PNG / JSON / georeferenced preview GeoTIFF
```

`streamlit_app.py` is the interface named in the presentation. The React/Vite + FastAPI interface is retained as an alternate richer web UI and API; both use the same preprocessing and `model_runner` path.

## Runtime/data limitations

- No trained checkpoint or paired training subset is included. Default output is the deterministic labelled development fallback.
- The synthetic gallery images are single-channel illustrations. They are duplicated into two input channels only for product-flow demos and are **not** real VV/VH or SEN12MS samples.
- Uploaded GeoTIFF band order is fixed: VV=1, VH=2. Inputs must already be radiometrically calibrated, terrain-corrected and co-registered. Current code performs robust normalization, not physical calibration.
- The GeoTIFF export is a 256×256 model preview with source extent/CRS preserved. It is not a full-resolution, calibrated science product.
- Model output is estimated optical-style appearance, not recovered true colour. TTA agreement is not calibrated uncertainty; palette feature shares are not trained land-cover labels.

## Component map

| Component | Location | Responsibility |
|---|---|---|
| Deck-aligned UI | `streamlit_app.py` | Upload, demo selection, comparison, consistency cue, exports |
| Alternate web UI | `frontend/src/` | Responsive browser UI, comparison slider, API-driven results |
| API | `backend/app/api/routes.py` | Health, demos, inference and result exports |
| GeoTIFF handling | `backend/app/core/geospatial.py` | VV/VH decode, robust normalization, CRS/extent-aware preview export |
| Model runner | `backend/app/ml/model_runner.py` | Checkpoint vs explicit development mode; flip-view agreement |
| Model | `ml/src/model.py` | Compact dual-input ResU-Net generator (2→3 channels) |
| Training/data/evaluation | `ml/src/{data,train,evaluate}.py` | Leakage-checked manifests, paired training, held-out evaluation |

## Run

- Deck-aligned Streamlit: `pip install -r requirements-ui.txt && bash scripts/run_streamlit.sh` (port 8501).
- Alternate React/FastAPI: build `frontend` then run `bash scripts/run_local.sh` (port 8000).
