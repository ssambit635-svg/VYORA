# Evaluation report

## Status: not evaluated

**No trained checkpoint, paired training set or held-out test set is bundled with this repository. No model accuracy, SSIM, MAE or latency benchmark is claimed.** The cells below are intentionally `TBD`; they must be filled only from a saved evaluation output produced by `python -m ml.src.evaluate`.

### Dataset split

| Split | Scene groups | Number of tiles | Notes |
|---|---:|---:|---|
| Train | TBD | TBD | No test-scene overlap |
| Validation | TBD | TBD | Used for model choices |
| Test | TBD | TBD | Held out until final assessment |

### Model comparison (held-out)

| Method | MAE/L1 | PSNR (dB) | SSIM | Edge preservation | Median latency | Notes |
|---|---:|---:|---:|---:|---|
| Pseudocolour baseline | TBD | TBD | TBD | TBD | TBD | Non-ML comparison; not yet computed |
| Vyora VV/VH ResU-Net | TBD | TBD | TBD | TBD | TBD | Not trained; no result exists |

## What the app *does* report today

For each live request, the backend computes and the UI displays only:

- **Observed runtime** — wall-clock milliseconds measured for this request on this machine.
- **Input→output edge agreement proxy** — Pearson correlation of log-magnitude Sobel-like gradients of the input tile and the output image. This measures structural retention between the two images; it is **not** accuracy, SSIM against an optical reference, or geographic correctness.
- **Confidence distribution** — share of the produced confidence map in low (<0.45), medium (0.45–0.70) and high (≥0.70) bands. In development mode this is rule agreement; it is not uncertainty calibration.
- **Held-out status** — shown as `Not run` until a real evaluation exists.

These values are computed from the actual arrays returned by that request. No number is hard-coded in the UI.

## How to produce a real report

```bash
# requires a validated manifest with a 'test' split and a trained checkpoint
python -m ml.src.evaluate \
  --manifest data/manifests/tiles.json \
  --checkpoint backend/checkpoints/vyora_resunet.pt \
  --output docs/evaluation_results.json
```

`ml/src/evaluate.py` streams the held-out tiles, computes MAE, PSNR, full-image SSIM and edge preservation for both the model and a documented intensity-to-palette baseline, records CPU inference time, and saves the worst-MAE input/reference/prediction/error panels. Report only if the manifest is genuinely scene/region-held-out and the paired data is prepared/licensed. If the manifest, checkpoint, or test data is missing/invalid, it reports the reason and writes no metrics.

## Required evidence still to add

- Run the evaluator to create worst-MAE held-out input / optical reference / model output / error panels. The evaluator now saves these automatically; no real panels exist until a real model/data evaluation is run.
- Explain at least one failure case honestly; worst-MAE panels are automatically listed in the JSON report.
- A confidence-map example on a real scene.
- A latency table with the test device and repeat count.

## Language rules

Use: “on our held-out curated test set”, “estimated colour interpretation”, “the confidence layer indicates method consistency”.

Never use: “real satellite colours restored”, “guaranteed flood map”, “works for all SAR imagery”, or any percentage without a documented target, split and calculation.
