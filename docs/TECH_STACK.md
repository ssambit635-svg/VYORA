> **Vyora implementation status (21 Nov 2026):** this document is now aligned to the team's presentation. The deck's Streamlit interface is implemented in `streamlit_app.py`; the existing React/FastAPI app is retained as an alternate UI/API. No trained checkpoint or SEN12MS subset is bundled, and the ML evaluation status remains **not run**.

# Vyora — technical stack

## Deck-aligned stack

| Layer | Choice | Status / honest scope |
|---|---|---|
| UI | Streamlit | Deck-aligned upload, scene selection, side-by-side comparison, consistency view and exports (`streamlit_app.py`) |
| Alternate interface/API | React + Vite + TypeScript; FastAPI + Uvicorn | Existing richer responsive UI/API, optional; same model code path |
| SAR/GeoTIFF I/O | Rasterio, NumPy, GDAL-compatible GeoTIFF | Two-band VV/VH reading, grid/CRS checks and CRS/extent-preserving preview export are implemented. The code does **not** radiometrically calibrate/terrain-correct Sentinel-1 data |
| ML | PyTorch, compact ResU-Net | Implemented generator accepts 2 channels and emits 3. Training code exists, but no real paired dataset/checkpoint is present |
| Training target | SEN12MS Sentinel-2 visible R/G/B | Proposed source in the presentation; must still be acquired, licence-checked, cloud screened, scaled and validated for alignment |
| Loss | L1 reconstruction + SSIM structure + edge preservation | Implemented. No adversarial loss; Pix2Pix/PatchGAN is future scope only |
| Evaluation | NumPy; MAE, PSNR, SSIM, edge alignment, latency | Evaluation status is not run on real held-out data. Do not quote smoke-test numbers |
| Visualization | Streamlit; Matplotlib for offline inspection | Streamlit UI implemented; Matplotlib remains optional for analysis/report panels |
| Data manifest | JSON + Python | Records tile, scene group, split, paths, source and licence; split leakage checked |
| Storage | Local filesystem + in-memory inference results | No cloud APIs, paid services, account, or database |

## Input contract

1. Preferred input: prepared GeoTIFF with VV as band 1 and VH as band 2.
2. Inputs must already be radiometrically calibrated, terrain corrected and co-registered. The app currently performs per-band finite-value handling, 2nd–98th percentile scaling, light median filtering, and resize to 256×256. It does not perform SNAP-style calibration.
3. Preview-only PNG/JPEG and synthetic gallery samples are accepted for interface demonstration. A grayscale image is duplicated to fill two channels and explicitly marked as a preview, not real dual-pol data.
4. Optical targets are visible R/G/B, co-registered and cloud-screened. Record the scale in the manifest (`optical_scale`; default 10000 for integer-scaled reflectance, set to 1 for normalized reflectance).
5. GeoTIFF export keeps source CRS and extent while producing a 256×256 visual preview; it is not a full-resolution analytical raster.

## Model

```text
VV ─┐
    ├─ compact ResU-Net + skip connections ─→ 3-channel Sentinel-2-style RGB estimate
VH ─┘

objective = L1 + λ₁·(1 − SSIM) + λ₂·edge loss
```

The generator has only an RGB output. No learned confidence/class heads are included because the paired image data does not provide uncertainty labels or land-cover masks. The UI consistency cue is original-vs-flipped prediction agreement, **not calibrated uncertainty**. Feature shares come from a fixed display-palette lookup, **not a trained classifier/segmentation model**.

## Data and evaluation protocol

- Train/validation/test split by geographic `scene_group`, never random neighboring patches.
- Check VV/VH/optical registration, CRS, transform, dimensions, target band order and scale.
- Screen cloudy optical targets; record source, licence, acquisition date, polarization, product level and preprocessing.
- Compare against a documented simple baseline and report MAE/PSNR/SSIM/edge on held-out regions; state device and latency method.
- Save raw evaluation JSON and representative successes/failures. Do not report metrics from synthetic demo scenes or temporary smoke data.

## Commands

```bash
# Presentation-aligned UI
pip install -r requirements-ui.txt
bash scripts/run_streamlit.sh

# Optional React/FastAPI UI
cd frontend && npm install && npm run build && cd ..
bash scripts/run_local.sh

# Train/evaluate only after licensed paired data and a validated manifest exist
python -m ml.src.train --config ml/configs/train_default.json
python -m ml.src.evaluate --manifest data/manifests/tiles.json \
  --checkpoint backend/checkpoints/vyora_resunet.pt --output docs/evaluation_results.json
```
