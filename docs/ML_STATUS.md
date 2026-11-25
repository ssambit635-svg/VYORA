# ML status

## Current state after paired-folder audit

- The repository contains `backend/checkpoints/vyora_resunet.pt`, a **legacy experimental checkpoint**, not a validated colourization model.
- In the old manifest, A was treated as input and B as target. The training loader converts A to grayscale; the audit found B targets grayscale too. The checkpoint learned an effectively grayscale-to-grayscale mapping.
- A random sample of 100 files per folder found colour in A for 99/100 train and 99/100 test samples, and in B for 0/100 train and 0/100 test samples. This is visual-channel evidence only; it does not establish sensor semantics.
- The reported 200-tile evaluation is a historical check of the old direction. It is not evidence of colourization performance; see [EVALUATION.md](EVALUATION.md).
- The 34 GB image archive and local manifest are not in GitHub.

## Corrected PNG training path

- `scripts/prepare_png_split_manifest.py` now defaults to grayscale B-side input → A-side target, based on the channel audit. Use `--input-side A` only if another dataset's semantics require the reverse.
- The manifest records `input_side` and `target_side`; the trainer refuses old PNG manifests without these fields.
- Training preflight checks that the sampled PNG targets have visible RGB channel spread. It stops before writing a checkpoint if the targets are effectively grayscale.
- The old A→B checkpoint cannot be resumed for the new B→A task; the representation marker intentionally rejects it. Train from scratch to a new checkpoint name, then validate and evaluate it.
- This corrects the image direction only. It does not verify that the grayscale folder is genuine Sentinel-1 SAR, that the coloured folder is true optical imagery, or that the folder splits are geographically independent.

## Other code support and limitations

- `scripts/prepare_sen12ms_manifest.py` remains a separate path for inspected, aligned source GeoTIFFs with explicit band/scale choices.
- `ml/src/evaluate.py` compares paired-target similarity against a simple palette baseline, reports colour-spread diagnostics, and saves failure panels. Metrics are not geographic accuracy.
- The local React/FastAPI app can run the tracked legacy checkpoint; until a corrected checkpoint is trained, treat its output as a plumbing/demo result only.
- No flood, water, vegetation, building, or land-cover classification head exists. Flip consistency is not calibrated uncertainty.
