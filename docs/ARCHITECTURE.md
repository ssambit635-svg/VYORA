# Vyora architecture

## Two separate data/model contracts

The repository has an implemented paired-data training pipeline with two possible input representations. The current trained checkpoint is the **paired-PNG prototype**; it is not a Sentinel-1 VV/VH model.

```text
CURRENT DEMO MODEL
B-side grayscale PNG ── duplicate gray channel ── ResU-Net (2→3) ── A-side RGB-style estimate
       no CRS/transform          no separate VV/VH       PNG / JSON result

FUTURE GEOSPATIAL MODEL PATH (CODE EXISTS; NO COMPATIBLE TRAINED CHECKPOINT)
VV/VH GeoTIFF ── decode + robust display normalization ── ResU-Net (2→3)
     upstream calibration required; no physical calibration here
         └──── paired optical target / geographic split / evaluation ────┘
        ── RGB-style estimate + consistency view ── CRS/extent preview export
```

## Current React + FastAPI inference

```text
React/Vite browser
    │  same-origin API requests / local Vite proxy
    ▼
FastAPI
    ├─ validate PNG/JPEG or 2-band GeoTIFF input
    ├─ enforce checkpoint input contract (PNG model rejects VV/VH TIFF; VV/VH model rejects duplicated grayscale preview)
    ├─ normalize and resize to 256×256
    ├─ load selected PyTorch checkpoint or labelled development fallback
    ├─ estimate RGB-style pixels and flip-view consistency
    ├─ retain result assets in a bounded, expiring in-memory cache
    └─ serve PNG / JSON and, for georeferenced TIFF inputs, a CRS/extent-preserving preview
```

The accepted primary interface is React/Vite + FastAPI. `streamlit_app.py` remains optional. Both should load the explicit `VYORA_CHECKPOINT` path; the environment variable must be set to the B→A PNG checkpoint for the current demo. The default checkpoint path points to legacy A→B weights.

## Current checkpoint limitations

- `backend/checkpoints/vyora_resunet_b_to_a.pt` maps grayscale B-side PNG pixels to the paired A-side image. The two input channels are identical copies of one grayscale image.
- PNGs carry no CRS or affine transform, so this checkpoint cannot create a georeferenced result.
- The output is an image estimate, not recovered true colour, land-cover classification, or a disaster alert.
- Flip-view agreement is not calibrated uncertainty. Class shares are not supplied for this PNG model because it has no supervised classifier.
- The source archive, manifest, licence, sensor provenance and geographic independence are not bundled/independently verified.

## Component map

| Component | Location | Responsibility |
|---|---|---|
| Primary UI | `frontend/src/` | Upload, inference, comparison slider, consistency cue and exports |
| Optional UI | `streamlit_app.py` | Alternate local interface using the same model runner and input checks |
| API | `backend/app/api/routes.py` | Health/capabilities, demos, inference, result/export endpoints |
| GeoTIFF handling | `backend/app/core/geospatial.py` | Two-band read, robust normalization, CRS/extent-aware preview output |
| Model runner | `backend/app/ml/model_runner.py` | Checkpoint/fallback, input contract, flip consistency, evaluation labeling |
| Model | `ml/src/model.py` | Compact 2-channel/3-channel ResU-Net |
| Training/evaluation | `ml/src/{data,sen12ms,train,evaluate}.py` | Paired manifests, scene-group checks, model training and held-out metrics |

## Local run

See [`INSTALL.md`](INSTALL.md). For the current model, set `VYORA_CHECKPOINT` to `backend/checkpoints/vyora_resunet_b_to_a.pt` before starting the API/UI.
