# Model card — Vyora paired-PNG prototype

## Current status

**A local ResU-Net checkpoint is included in the repository.** It was trained from a user-provided paired PNG export—not from verified dual-polarization Sentinel-1 GeoTIFFs.

| Field | Current implementation |
|---|---|
| Task | Estimate an RGB-style B-side PNG from a grayscale A-side PNG |
| Input | A grayscale image copied into two identical model channels |
| Output | Three RGB image channels; not true-colour recovery |
| Architecture | Compact ResU-Net encoder/decoder with skip connections |
| Checkpoint | `backend/checkpoints/vyora_resunet.pt` |
| Training reported | CPU; 1,000 train tiles, 200 validation tiles, 5 epochs |
| Evaluation reported | 200 of 4,576 test tiles; see [EVALUATION.md](EVALUATION.md) |
| Geospatial metadata | None in PNG input; output is not georeferenced |
| Class prediction | None; no water/flood/vegetation/building classifier |

The B-side files are paired reference targets used during training/evaluation. In normal app use, the model receives A only and estimates B-like pixels. The latest 200-tile colour audit measured target RGB spread as 0.00000 and model output spread as 0.00471, which means the evaluator's loaded B targets are effectively grayscale. If the archive also contains green B images, first verify that the manifest points to those exact files; more training cannot restore colour from a grayscale target mapping.

## Intended use

Educational exploration and a hackathon demonstration of paired image-to-image learning. A human should treat the result as a rough visual estimate and consult the original imagery and authoritative sources.

## Not intended for

Official maps, flood/cyclone warnings, evacuation, emergency response, safety-critical decisions, land-cover statistics, or reconstructing real visible colour from SAR.

## What the model and UI metrics mean

- The model predicts RGB pixels only. It has no learned class or uncertainty head.
- The consistency layer compares predictions from the original and horizontally flipped input. It is not calibrated uncertainty or truth.
- The live “structure proxy” compares image-gradient patterns from input and output. It is not accuracy against B.
- A palette lookup is not a learned land-cover classifier.

## Limitations and risks

- Small training run: 1,000 train tiles and 5 CPU epochs; the model may underfit and average colours.
- The source A/B pairing and licence were not independently audited in this repository.
- The supplied folder split may not be geographically independent; that was not independently checked.
- Seasonal, cloud, acquisition-time and sensor differences can change the target appearance.
- PNGs have no CRS/transform; the current upload path cannot make a spatially correct map.
- The held-out metrics show pixel similarity to paired references on a 200-tile subset only, not geographic correctness or operational utility.

## How to improve responsibly

Fine-tune from the saved checkpoint to a separate file, select only on validation loss, then compare both models on the same untouched test subset. Inspect reference/prediction/error panels and the RGB channel-spread diagnostic. Promote a new checkpoint only if the test evidence and visible examples improve; preserve the existing checkpoint otherwise.
