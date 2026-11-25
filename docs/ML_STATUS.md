# ML status

## Current prototype

- The repository contains the team's **19.2 MB ResU-Net checkpoint** at `backend/checkpoints/vyora_resunet.pt`.
- It was trained locally on a subset of paired PNGs: grayscale A-side input, duplicated into two model channels, with RGB B-side images as targets. It is **not** a verified dual-polarization VV/VH model.
- Reported run: CPU, 1,000 train tiles, 200 validation tiles, 5 epochs; best validation loss 0.27527 at epoch 5.
- A reported evaluation on 200 of 4,576 supplied test tiles (seed 42; 200 scene groups) is documented in [EVALUATION.md](EVALUATION.md). The supplied folder split's geographic independence was not independently verified.
- The 34 GB source archive and local tile manifest are intentionally not in GitHub. PNGs do not carry geospatial coordinates.

## What the code supports

- `scripts/prepare_png_split_manifest.py` matches same-named A/B files and preserves train/validation/test folders. It treats A as grayscale and B as RGB.
- `scripts/prepare_sen12ms_manifest.py` is a separate path for inspected and aligned source GeoTIFFs with explicit band/scale choices. Do not use it to imply that the PNG checkpoint is dual-pol.
- `ml/src/train.py` preflights the splits and saves the best validation checkpoint. It now supports safe fine-tuning from an existing checkpoint into a separate output file; it refuses incompatible input representations and preserves the old checkpoint.
- `ml/src/evaluate.py` compares against a simple palette baseline, reports paired-target metrics including an RGB channel-spread diagnostic, and saves error panels. These metrics are similarity measures, not geographic accuracy.
- The local React/FastAPI app uses a model checkpoint when available. For this PNG checkpoint it accepts grayscale A-side PNG input; it cannot produce map coordinates from PNG.

## What remains unverified

- The user's source imagery, licensing terms, and exact A/B pairing cannot be independently inspected in this repository.
- The provided train/validation/test folders may share geographic areas; that has not been checked.
- Colour recovery quality is limited by the small CPU training run. Inspect paired reference panels and re-evaluate before replacing the current checkpoint.
- The model has no land-cover, water, flood, or building classification head; consistency is not calibrated uncertainty.
- Synthetic demo scenes are illustrations, not real satellite data.
