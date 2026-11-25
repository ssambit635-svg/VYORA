# Model card — Vyora paired-PNG prototype

## Current checkpoint status

The repository contains a **legacy experimental checkpoint**, trained from the earlier A→B manifest direction. A folder audit shows that A files usually have RGB channel variation while B files are grayscale. The loader converted A to grayscale and trained against grayscale B targets. Therefore the checkpoint did **not** learn the intended grayscale-to-colour mapping; do not present it as a colourization model.

| Field | Legacy checkpoint |
|---|---|
| Input used in old run | A-side PNG converted to grayscale, duplicated into two channels |
| Target used in old run | B-side PNG; sampled targets were grayscale |
| Architecture | Compact ResU-Net encoder/decoder with skip connections |
| Checkpoint | `backend/checkpoints/vyora_resunet.pt` |
| Training reported | CPU; 1,000 train tiles, 200 validation tiles, 5 epochs |
| Evaluation | 200 of 4,576 test tiles, historical old-direction audit; not a colourization benchmark |
| Geospatial metadata | None in PNG input |

## Corrected experiment direction

The folder audit suggests testing grayscale B input → A-side target. The updated manifest builder defaults to that direction and records the side explicitly. This is a **working assumption based on PNG channel statistics**, not proof that B is Sentinel-1 SAR or that A is true optical satellite imagery. Verify one pair visually and check source provenance before calling it SAR-to-optical.

The old checkpoint must not be resumed for the corrected direction. Train a separate checkpoint from scratch, select with validation data, and report test results only after the target files are confirmed colourful and correctly paired.

## Intended and prohibited use

For now, educational exploration and a hackathon demonstrator only. Not for official maps, flood/cyclone warnings, evacuation, emergency response, safety-critical decisions, land-cover statistics, or recovering true visible colour.

## Metrics and outputs

- The model predicts image pixels; it has no learned water/flood/vegetation/building classes or uncertainty head.
- The consistency layer compares original and horizontally flipped predictions. It is not calibrated uncertainty.
- The live structure proxy compares input/output gradient patterns. It is not accuracy against the paired target.
- RGB channel spread diagnoses whether a prediction is nearly grayscale; it is not a quality score alone.

## Key limitations

- A/B sensor semantics, licence, provenance, and exact geographic split are not independently verified.
- PNGs have no CRS/transform; no spatially correct map can be produced from them.
- Visual similarity to a paired target is not geographic correctness or operational utility.
- The 34 GB source archive is not included in GitHub.
