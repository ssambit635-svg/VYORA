# Vyora

**HK26-PS-19 — Deep Learning-Based SAR Image Colorization & Geospatial Visual Interpretation**

> **Honest status:** the repository contains the legacy A→B checkpoint and the corrected 19.2 MB B→A PNG prototype checkpoint. The corrected model beats a simple baseline on a 200-tile subset, but its colours remain muted and the A/B sensor semantics/geographic independence are unverified. It is not a verified VV/VH or geospatial model. The 34 GB archive is not bundled.

## Project

Vyora is an early image-to-image prototype. Folder audit shows A PNGs usually carry colour and B PNGs are grayscale; the current experiment is **grayscale B-side input → A-side image estimate**. This direction is based only on image-channel statistics, not verified sensor metadata. The model output is still under-coloured and is not ground truth.

## Deck-aligned stack and interfaces

- **React/Vite + FastAPI** local web app with image upload, model inference, before/after slider, consistency overlay, and PNG/JSON export.
- PyTorch compact ResU-Net generator; current checkpoint uses grayscale B-side input → A-side target, subject to source verification.
- Offline training/evaluation scripts; the evaluation report compares against a simple baseline and saves failure-case panels.
- Optional GeoTIFF code path exists for compatible dual-band inputs/checkpoints, but it is **not compatible with the current PNG-trained checkpoint**.
- No paid APIs/cloud services; inference currently runs on the user's laptop, not a public hosted service.

## Run the React + FastAPI prototype locally

Install runtime dependencies once from the repository root (PyTorch is separate from `backend/requirements.txt`):

```powershell
python -m pip install -r backend/requirements.txt
python -m pip install torch --index-url https://download.pytorch.org/whl/cpu
```

Skip the PyTorch install if the active environment already has the compatible version used for training. Use the official PyTorch selector for a CUDA build.

In one PowerShell window from the repository root, select the corrected checkpoint and start the API:

```powershell
$env:VYORA_CHECKPOINT = "$PWD\backend\checkpoints\vyora_resunet_b_to_a.pt"
python -m uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port 8000
```

In a second window, install frontend packages once and start Vite:

```powershell
cd frontend
npm install
npm run dev -- --host 0.0.0.0
```

Open the local URL Vite prints (usually `http://localhost:5173`). The API docs are at `http://localhost:8000/docs`. Keep both windows running. The corrected checkpoint is `backend/checkpoints/vyora_resunet_b_to_a.pt`; the raw image archive and tile manifest are not in Git.


## Input contract and safe interpretation

- **Current checkpoint input:** a 256×256 grayscale B-side PNG, duplicated into two model channels; output estimates the paired A-side image.
- The legacy A→B checkpoint remains for history, but it was trained against grayscale B targets and is not a valid colourization checkpoint.
- The current B→A mapping is based on channel statistics, not verified sensor provenance; it does not establish genuine VV/VH or geospatial input.
- A separate GeoTIFF pathway exists in code, but it is not compatible with this PNG-trained checkpoint. It requires a compatible dual-band checkpoint and already calibrated/co-registered input.
- A PNG has no map CRS/transform, so its result cannot be a georeferenced map. The optional GeoTIFF export is a model-size preview, not a full-resolution analytical raster.
- The flip-view cue is method consistency, not calibrated uncertainty. Palette shares are not learned land-cover labels.

## Data and model status

The team's paired A/B PNG archive is local and **not bundled with this repository**. A 100-image-per-folder audit found A mostly colour-bearing and B grayscale. The corrected B-input/A-target model was trained and evaluated on a limited subset; metrics and caveats are in [Evaluation](docs/EVALUATION.md). The exact source semantics and licence still need verification. This is not a verified Sentinel-1/Sentinel-2 GeoTIFF training product. For a separate GeoTIFF experiment, use the [official dataset page](https://mediatum.ub.tum.de/1474000) and keep the Toolbox clone's `splits/` lists available.

First inspect a real matched pair (this prints band descriptions/tags, raw-value percentiles, CRS and transforms):

```bash
python scripts/inspect_sen12ms_pair.py --s1 /path/to/tile_s1.tif --s2 /path/to/tile_s2.tif
```

Use the source metadata to verify band indexes and optical scale, and visually check pair quality/clouds. Then generate the manifest. The example indexes/scale below are **not verified**; replace them if the inspection/source metadata says otherwise. The script requires these choices rather than silently assuming them. It pairs Toolbox list entries, reserves whole training ROIs for validation, and preserves the provided test list:

```bash
python scripts/prepare_sen12ms_manifest.py \
  --data-root /path/to/extracted/SEN12MS \
  --train-list /path/to/SEN12MS/splits/train_list.txt \
  --test-list /path/to/SEN12MS/splits/test_list.txt \
  --vv-band 1 --vh-band 2 \
  --rgb-bands 4 3 2 --optical-scale 10000 \
  --licence-note "<record the actual dataset terms and attribution>"
```

Classification label files are not used. Then train only after the manifest and preprocessing have been checked:

```bash
python -m ml.src.train --config ml/configs/train_default.json
python -m ml.src.evaluate --manifest data/manifests/tiles.json \
  --checkpoint backend/checkpoints/vyora_resunet.pt --output docs/evaluation_results.json
```

See [ML status](docs/ML_STATUS.md), [Data card](docs/DATA_CARD.md), [Model card](docs/MODEL_CARD.md), and [Evaluation](docs/EVALUATION.md). The report contains the team's limited 200-tile test-subset results and their caveats.

## Quick prototype for the downloaded A/B PNG folders

If your extracted folder contains `train_A`, `train_B`, `val_A`, `val_B`, `test_A`, and `test_B`, regenerate the local manifest using the audited direction. This overwrites only the ignored manifest file, not the images:

```powershell
python scripts/prepare_png_split_manifest.py --data-root "$env:OneDrive\Desktop\imagery data\archive\sen12ms_SUMMER" --input-side B --licence-note "Record the actual source and terms"
```

Then inspect a pair before training:

```powershell
python scripts/inspect_png_pair.py --manifest data/manifests/tiles.json --tile-id test-ROIs1868_summer_s000131_p000746
```

The B input is grayscale and the A target carries colour in the sampled data, but source/sensor semantics still need verification. The corrected checkpoint is already trained and tracked at `backend/checkpoints/vyora_resunet_b_to_a.pt`. The reported 200-tile subset metrics and important muted-colour failure cases are recorded in `docs/EVALUATION.md`. Keep the test split out of model selection, do not upload the 34 GB archive or local manifest, and do not describe the output as true colour or a verified map.
## Documentation

- [Architecture](docs/ARCHITECTURE.md) · [Technical stack](docs/TECH_STACK.md) · [API](docs/API.md)
- [PPT alignment & selection plan](docs/PPT_ALIGNMENT_AND_SELECTION_GUIDE.md)
- [Demo script](docs/DEMO_SCRIPT.md) · [Test checklist](docs/TEST_CHECKLIST.md)
- [Install/troubleshooting](docs/INSTALL.md) · [Final training runbook](docs/FINAL_TRAINING_RUNBOOK.md) · [Licences](docs/LICENSES_AND_ATTRIBUTION.md)
