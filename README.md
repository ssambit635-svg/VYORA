# Vyora

**HK26-PS-19 — Deep Learning-Based SAR Image Colorization & Geospatial Visual Interpretation**

> **Honest status (21 Nov 2026):** no SEN12MS subset, trained checkpoint or real-data evaluation is bundled. The demo defaults to a labelled deterministic development fallback. Synthetic scenes are not satellite data. Never describe current fallback outputs as learned AI inference.

## Project

Vyora is designed to map paired Sentinel-1 VV/VH backscatter to an **estimated optical-style RGB visual layer**, keeping the original radar view beside the estimate. The planned supervised baseline is a compact two-input ResU-Net trained against paired Sentinel-2 visible targets. It is for visual exploration, not recovered true colour, official mapping or disaster warning.

## Deck-aligned stack and interfaces

- **Streamlit** is implemented as the presentation-aligned interface.
- PyTorch compact ResU-Net generator, VV/VH (2 channels) → RGB-style (3 channels).
- Rasterio/NumPy for two-band GeoTIFF input and CRS/extent-preserving 256×256 preview export.
- Region-grouped JSON manifest and offline train/evaluation scripts.
- The earlier **React/Vite + FastAPI** app remains available as an alternate responsive web UI and API; both use the same inference code.
- No paid APIs/cloud services; the laptop runs locally and can be shared over the same Wi-Fi.

## Run the presentation version

```bash
python3 -m venv .venv
source .venv/bin/activate              # Windows: .venv\\Scripts\\activate
pip install -r requirements-ui.txt
bash scripts/run_streamlit.sh
```

Open `http://localhost:8501` on the laptop or `http://<laptop-LAN-IP>:8501` on a phone on the same Wi-Fi. For a trained checkpoint, install CPU/GPU PyTorch separately using the official wheel instructions and place the checkpoint at `backend/checkpoints/vyora_resunet.pt` (ignored by Git).

## Alternate React + FastAPI version

```bash
pip install -r backend/requirements.txt
cd frontend && npm install && npm run build && cd ..
bash scripts/run_local.sh
```

Open `http://localhost:8000` (API docs: `/docs`). The app launcher prints its LAN address.

## Input contract and safe interpretation

- Preferred input is a **prepared two-band GeoTIFF**: VV is band 1 and VH is band 2. It must already be radiometrically calibrated, terrain-corrected, and co-registered. Current code does robust per-band 2nd–98th percentile normalization, not physical Sentinel-1 calibration.
- PNG/JPEG and gallery scenes exist only for interface testing; grayscale previews are duplicated into the two channels and clearly marked as not genuine dual-pol data.
- The GeoTIFF download is a model-size preview (256×256) retaining source CRS and extent—not a full-resolution or calibrated analytical raster.
- The current flip-view cue is method consistency, not calibrated uncertainty. Feature-share cards are a fixed palette lookup, not learned land-cover segmentation.

## Data and model status

The deck proposes SEN12MS paired Sentinel-1/Sentinel-2 imagery. The data is **not downloaded or bundled**. Verify access/licence, calibrate and co-register VV/VH, cloud-screen visible targets, record band scale/order, and split by geographic scene group before training. Only then run:

```bash
python -m ml.src.train --config ml/configs/train_default.json
python -m ml.src.evaluate --manifest data/manifests/tiles.json \
  --checkpoint backend/checkpoints/vyora_resunet.pt --output docs/evaluation_results.json
```

See [Data card](docs/DATA_CARD.md), [Model card](docs/MODEL_CARD.md), and [Evaluation](docs/EVALUATION.md). Held-out results are currently **not run**; temporary smoke data is not evidence and no smoke metrics are claimed.

## Documentation

- [Architecture](docs/ARCHITECTURE.md) · [Technical stack](docs/TECH_STACK.md) · [API](docs/API.md)
- [PPT alignment & selection plan](docs/PPT_ALIGNMENT_AND_SELECTION_GUIDE.md)
- [Demo script](docs/DEMO_SCRIPT.md) · [Test checklist](docs/TEST_CHECKLIST.md)
- [Install/troubleshooting](docs/INSTALL.md) · [Licences](docs/LICENSES_AND_ATTRIBUTION.md)
