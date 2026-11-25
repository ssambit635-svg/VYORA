# Vyora

**HK26-PS-19 — Deep Learning-Based SAR Image Colorization & Geospatial Visual Interpretation**

> **Honest status (21 Nov 2026):** this repository includes a locally trained 19.2 MB grayscale-A-to-RGB-B PNG prototype checkpoint and a small held-out subset evaluation. It is not a verified VV/VH or geospatial model. The 34 GB image archive is not bundled. Read [the evaluation report](docs/EVALUATION.md) before presenting any metrics.

## Project

Vyora is an early image-to-image prototype: it takes a grayscale A-side PNG tile and predicts an **estimated RGB-style B-side image**. The current checkpoint was trained with A duplicated into two input channels; it does not use separate VV/VH channels. The estimate is for visual exploration—not recovered true colour, official mapping, or disaster warning.

## Deck-aligned stack and interfaces

- **React/Vite + FastAPI** local web app with image upload, model inference, before/after slider, consistency overlay, and PNG/JSON export.
- PyTorch compact ResU-Net generator: current prototype uses grayscale A-side input → RGB-style estimate.
- Offline training/evaluation scripts; the evaluation report compares against a simple baseline and saves failure-case panels.
- Optional GeoTIFF code path exists for compatible dual-band inputs/checkpoints, but it is **not compatible with the current PNG-trained checkpoint**.
- No paid APIs/cloud services; inference currently runs on the user's laptop, not a public hosted service.

## Run the React + FastAPI prototype locally

Install Python dependencies once from the repository root:

```powershell
python -m pip install -r backend/requirements.txt
```

In one PowerShell window, start the API:

```powershell
python -m uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port 8000
```

In a second window, install frontend packages once and start Vite:

```powershell
cd frontend
npm install
npm run dev -- --host 0.0.0.0
```

Open the local URL Vite prints (usually `http://localhost:5173`). The API docs are at `http://localhost:8000/docs`. Keep both windows running. The checkpoint is tracked in Git at `backend/checkpoints/vyora_resunet.pt`; the raw image archive is not.


## Input contract and safe interpretation

- **Current checkpoint input:** a 256×256 grayscale A-side PNG. The value is duplicated into two model channels; this is not genuine VV/VH.
- A separate GeoTIFF pathway exists in code, but it is not compatible with this PNG-trained checkpoint. It requires a compatible dual-band checkpoint and already calibrated/co-registered input.
- A PNG has no map CRS/transform, so its result cannot be a georeferenced map. The optional GeoTIFF export is a model-size preview, not a full-resolution analytical raster.
- The flip-view cue is method consistency, not calibrated uncertainty. Palette shares are not learned land-cover labels.

## Data and model status

The prototype was trained locally from the team's paired A/B PNG export. The raw archive is **not downloaded into or bundled with this repository**. The current model is a PNG prototype, not a verified Sentinel-1/Sentinel-2 GeoTIFF training product. For a separate GeoTIFF experiment, use the [official dataset page](https://mediatum.ub.tum.de/1474000) and keep the Toolbox clone's `splits/` lists available.

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

If your extracted folder contains `train_A`, `train_B`, `val_A`, `val_B`, `test_A`, and `test_B`, you can create a paired manifest directly:

```bash
python scripts/prepare_png_split_manifest.py \
  --data-root "data/raw/SEN12MS/archive/sen12ms_SUMMER" \
  --licence-note "SEN12MS official download; verify the applicable terms"
python -m ml.src.train --config ml/configs/train_default.json \
  --epochs 5 --max-train-tiles 1000 --max-validation-tiles 200
python -m ml.src.evaluate --manifest data/manifests/tiles.json \
  --checkpoint backend/checkpoints/vyora_resunet.pt --max-test-tiles 200
```

The manifest step checks that A/B filenames pair in each split. The green/colourful B-side images are training targets; the app receives A and must learn to predict B. The current checkpoint was trained on only 1,000 tiles for 5 epochs, so colour can be muted or grey. The script supports safe fine-tuning without overwriting the original checkpoint:

```powershell
python -m ml.src.train --config ml/configs/train_default.json --resume-checkpoint backend/checkpoints/vyora_resunet.pt --epochs 5 --max-train-tiles 1000 --max-validation-tiles 200
```

It writes `backend/checkpoints/vyora_resunet_finetuned.pt` by default and retains the best validation weights; the original stays untouched. Then compare it on the held-out test subset with a separate report and example folder before using it:

```powershell
python -m ml.src.evaluate --manifest data/manifests/tiles.json --checkpoint backend/checkpoints/vyora_resunet_finetuned.pt --max-test-tiles 200 --seed 42 --output docs/evaluation_results_finetuned.json --examples-dir docs/evaluation_examples_finetuned
```

Do not promote a checkpoint unless validation and held-out comparisons support it. PNGs have no map coordinates, and the 34 GB source archive should stay out of Git.

## Documentation

- [Architecture](docs/ARCHITECTURE.md) · [Technical stack](docs/TECH_STACK.md) · [API](docs/API.md)
- [PPT alignment & selection plan](docs/PPT_ALIGNMENT_AND_SELECTION_GUIDE.md)
- [Demo script](docs/DEMO_SCRIPT.md) · [Test checklist](docs/TEST_CHECKLIST.md)
- [Install/troubleshooting](docs/INSTALL.md) · [Licences](docs/LICENSES_AND_ATTRIBUTION.md)
