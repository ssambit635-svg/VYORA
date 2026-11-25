# Vyora — technical stack and current contract

## Implemented stack

| Layer | Choice | Current status |
|---|---|---|
| Primary UI | React + Vite + TypeScript | Accepted local interface; upload, compare slider, consistency cue and PNG/JSON export |
| API | FastAPI + Uvicorn | Health/capability, demo, inference, result and export endpoints |
| Alternate UI | Streamlit | Optional; kept aligned with checkpoint/input contract, not the primary accepted UI |
| Image I/O | Pillow, NumPy, Rasterio | PNG/JPEG previews and 2-band GeoTIFF decoding, normalization, CRS-aware preview export |
| ML | PyTorch compact ResU-Net | Architecture accepts 2 channels and emits 3; current trained checkpoint is grayscale B→A paired PNG, not VV/VH |
| Training | JSON manifests, PyTorch | Paired PNG and explicit VV/VH/optical GeoTIFF paths; checkpoint input representation is recorded and validated |
| Evaluation | NumPy | MAE, PSNR, SSIM, edge comparison, RGB-spread diagnostic, subset sampling, failure panels |
| Storage | Local files + bounded in-memory result cache | Uploads are not written to disk; result cache expires and has a fixed size bound |
| Hosting/cost | Local-first | No paid API or hosted inference service is required |

## Current checkpoint input/output

```text
one grayscale B-side PNG → copy same image into 2 input channels
                    → ResU-Net (2→3)
                    → estimate resembling paired A-side PNG
```

The A/B source meaning and license have not been independently verified. The checkpoint is not a Sentinel-1 VV/VH model. API and Streamlit input checks reject a GeoTIFF with this checkpoint; the model must not silently treat VV/VH as its grayscale training input.

## Separate geospatial code path

A separate training/inference data path supports explicit VV and VH band selectors, visible RGB target selectors, scene-group splits, GeoTIFF grid checks, and CRS/extent-preserving preview export. It still requires a compatible VV/VH-trained checkpoint and verified data. The runtime does **not** perform radiometric calibration, terrain correction, cloud screening, or co-registration; those must be completed upstream and validated.

## Model/interpretation limits

- The current PNG model predicts image pixels only. It has no supervised water/vegetation/building classifier; the backend returns no class shares for it.
- Flip-view agreement is a consistency/stability cue, not calibrated uncertainty or probability of correctness.
- PNGs have no CRS/transform; their result cannot be a georeferenced map.
- The held-out report covers 200 of 4,576 supplied test tiles, seed 42. Geographic independence is unverified; the recorded average RGB spread shows under-colourization.
- Four bundled gallery scenes are synthetic UI fallbacks, not training or test data.

## Commands

See [`INSTALL.md`](INSTALL.md) for the Windows PowerShell flow to select `backend/checkpoints/vyora_resunet_b_to_a.pt`, start the FastAPI service and run React/Vite. Training/evaluation commands and caveats are in `README.md` and `docs/EVALUATION.md`.
