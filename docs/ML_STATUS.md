# ML status

## Current prototype

- The repository includes two checkpoints: the earlier **legacy A→B** experiment and the newer `backend/checkpoints/vyora_resunet_b_to_a.pt` B→A PNG prototype.
- A/B folder samples showed A mostly colour-bearing and B grayscale. The corrected model takes grayscale B-side PNG input (duplicated into two channels) and predicts A-side pixels. This is based on image-channel statistics, not verified SAR/optical sensor metadata.
- Corrected run: CPU, 1,000 train tiles, 200 validation tiles, 5 epochs; best validation loss 0.16335 at epoch 5.
- Corrected held-out subset report: 200 of 4,576 test tiles, seed 42; details in [EVALUATION.md](EVALUATION.md). Folder-split geographic independence was not independently verified.
- The model beats the simple baseline on paired-pixel metrics in this subset, but output colour remains muted: mean prediction RGB spread 0.03778 vs target 0.13053.
- The 34 GB archive, tile manifest, and generated evaluation panels/reports are not in GitHub.

## Reproducibility and safety

- `scripts/prepare_png_split_manifest.py` defaults to grayscale B-side input → A-side target and records `input_side`/`target_side`. The trainer rejects stale PNG manifests without explicit direction and rejects effectively grayscale targets before writing a checkpoint.
- The old A→B checkpoint must not be used as evidence of colourization or resumed for the corrected mapping.
- The API can load the corrected checkpoint via `VYORA_CHECKPOINT=backend/checkpoints/vyora_resunet_b_to_a.pt`.
- `ml/src/evaluate.py` compares paired-target similarity against a palette baseline, reports RGB-spread diagnostics, and saves worst-error panels. Metrics are not geographic accuracy.

## Limitations still open

- Source dataset semantics, licence, sensor identity, and exact geographic split have not been independently verified.
- A/B PNGs carry no CRS/transform; the current model is not a georeferenced mapping product.
- Colour recovery is still weak on many samples, despite better average similarity scores than the simple baseline.
- No flood, water, vegetation, building, or land-cover classification head exists. Flip consistency is not calibrated uncertainty.
