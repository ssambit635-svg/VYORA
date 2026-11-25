# Vyora

**HK26-PS-19 — Deep Learning-Based SAR Image Colorization & Geospatial Visual Interpretation**

> **Honest status:** this repository contains a 19.2 MB legacy checkpoint, but the latest audit found its A→B training direction used grayscale targets. It is **not a valid colourization model**. The corrected B→A training path is being added; it needs a fresh local run on the user's data before the app can show a validated colour estimate. The 34 GB archive is not bundled.

## Project

Vyora is an early image-to-image prototype. Folder audit shows A PNGs usually carry colour and B PNGs are grayscale; the corrected experiment is **grayscale B-side input → A-side image estimate**. This is based only on image-channel statistics, not verified sensor metadata. The current checkpoint has the reverse mapping and should not be presented as successful colourization.

## Deck-aligned stack and interfaces

- **React/Vite + FastAPI** local web app with image upload, model inference, before/after slider, consistency overlay, and PNG/JSON export.
- PyTorch compact ResU-Net generator; corrected training manifest direction is grayscale B-side input → A-side target, subject to source verification.
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

- **Legacy checkpoint input:** a 256×256 grayscale-converted A-side PNG. It was trained against grayscale B targets and is not a valid colourization checkpoint.
- **Corrected experiment:** use grayscale B-side PNG as input and A-side PNG as target; both are duplicated/decoded according to the explicit manifest mapping. This still does not establish real VV/VH or geospatial input.
- A separate GeoTIFF pathway exists in code, but it is not compatible with this PNG-trained checkpoint. It requires a compatible dual-band checkpoint and already calibrated/co-registered input.
- A PNG has no map CRS/transform, so its result cannot be a georeferenced map. The optional GeoTIFF export is a model-size preview, not a full-resolution analytical raster.
- The flip-view cue is method consistency, not calibrated uncertainty. Palette shares are not learned land-cover labels.

## Data and model status

The team's paired A/B PNG archive is local and **not bundled with this repository**. A 100-image-per-folder audit found A mostly colour-bearing and B grayscale. The manifest builder now defaults to B-input/A-target; this direction still needs visual/source verification and a fresh training run. It is not a verified Sentinel-1/Sentinel-2 GeoTIFF training product. For a separate GeoTIFF experiment, use the [official dataset page](https://mediatum.ub.tum.de/1474000) and keep the Toolbox clone's `splits/` lists available.

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

Confirm the B input is grayscale and the A target has non-zero RGB spread and is visually the intended reference. The old A-input/B-target checkpoint is the wrong direction and must **not** be fine-tuned. When the pair is confirmed, train from scratch to a separate file:

```powershell
python -m ml.src.train --config ml/configs/train_default.json --epochs 5 --max-train-tiles 1000 --max-validation-tiles 200 --output-checkpoint backend/checkpoints/vyora_resunet_b_to_a.pt
```

This limited CPU run previously took over 30 minutes and may still underfit. Then evaluate the new checkpoint before switching the app to it:

```powershell
python -m ml.src.evaluate --manifest data/manifests/tiles.json --checkpoint backend/checkpoints/vyora_resunet_b_to_a.pt --max-test-tiles 200 --seed 42 --output docs/evaluation_results_b_to_a.json --examples-dir docs/evaluation_examples_b_to_a
```

Do not promote a checkpoint unless target pairing is verified and held-out examples/metrics support the change. PNGs have no map coordinates, and the 34 GB source archive should stay out of Git.
## Documentation

- [Architecture](docs/ARCHITECTURE.md) · [Technical stack](docs/TECH_STACK.md) · [API](docs/API.md)
- [PPT alignment & selection plan](docs/PPT_ALIGNMENT_AND_SELECTION_GUIDE.md)
- [Demo script](docs/DEMO_SCRIPT.md) · [Test checklist](docs/TEST_CHECKLIST.md)
- [Install/troubleshooting](docs/INSTALL.md) · [Licences](docs/LICENSES_AND_ATTRIBUTION.md)
