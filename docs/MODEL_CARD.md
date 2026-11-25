# Model card — Vyora paired-PNG prototype

## Current checkpoint

`backend/checkpoints/vyora_resunet_b_to_a.pt` is the corrected prototype checkpoint included in the repository. It uses grayscale B-side PNG input (copied into two identical model channels) to predict A-side image pixels. The direction is based on sampled A/B RGB statistics, not verified sensor provenance: do not claim that this is a calibrated Sentinel-1 VV/VH → Sentinel-2 model.

| Field | Current implementation |
|---|---|
| Architecture | Compact ResU-Net encoder/decoder with skip connections |
| Input / target | Grayscale B-side PNG → A-side RGB-style PNG |
| Training reported | CPU; 1,000 train tiles, 200 validation tiles, 5 epochs |
| Best validation loss | 0.16335 at epoch 5 |
| Evaluation | 200 of 4,576 supplied test tiles; see [EVALUATION.md](EVALUATION.md) |
| Geospatial metadata | None in PNG; output is not georeferenced |
| Classification | No water/flood/vegetation/building/land-cover head |

A legacy A→B checkpoint is also present for history/compatibility. It was trained against grayscale B targets and is not a valid colourization model. Use the `b_to_a` checkpoint for the current experiment.

## Performance caveat

On the reported test subset, the ResU-Net has lower MAE and higher SSIM than a simple pseudocolour baseline. However, average prediction RGB spread is only 0.03778 versus 0.13053 in the paired target, indicating under-colourization. Some worst-error examples are substantially worse than the average. This is early evidence, not production validation.

## Intended use

Educational exploration and a hackathon demonstration only. Treat output as a rough visual estimate; consult original imagery and authoritative sources.

## Not intended for

Official maps, flood/cyclone warnings, evacuation, emergency response, safety-critical decisions, land-cover statistics, or recovering true visible colour.

## Metric meanings

- Flip-view consistency is prediction stability under a simple transformation, not calibrated uncertainty.
- The live structure proxy compares input/output gradient patterns; it is not accuracy against the paired target.
- RGB channel spread diagnoses colour collapse; it is not a quality score by itself.

## Known limitations

- A/B sensor semantics, data licence, source provenance, and geographic independence of folder splits are not independently verified.
- PNGs have no CRS/transform.
- Visual similarity to paired pixels is not geographic correctness or operational utility.
- The source archive is not included in GitHub.
