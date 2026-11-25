# Evaluation report

## Current status: limited prototype evaluation completed

The team trained a **grayscale A-side PNG → RGB B-side PNG** prototype locally. This is not a verified Sentinel-1 VV/VH model. The test subset is small and the supplied folder split's geographic independence was not independently checked. Results measure similarity to paired PNG targets only—not true-colour recovery, map accuracy, or usefulness for emergency decisions.

### Run details reported by the team

- Training: CPU, 1,000 training tiles, 200 validation tiles, 5 epochs.
- Best validation loss: 0.27527 at epoch 5.
- Evaluation: 200 of 4,576 test tiles, seed 42; 200 scene groups.
- The original 34 GB image archive and tile manifest are not included in this repository.

### Held-out subset comparison

| Method | MAE ↓ | PSNR (dB) ↑ | SSIM ↑ | Edge preservation ↑ | Mean RGB spread (prediction) | Mean RGB spread (target) | Median CPU latency |
|---|---:|---:|---:|---:|---:|---:|---:|
| Pseudocolour baseline | 0.22571 | 11.55409 | 0.24056 | 0.21084 | 0.41310 | 0.00000 | — |
| ResU-Net prototype | 0.15514 | 15.72773 | 0.44559 | 0.45740 | 0.00471 | 0.00000 | 73.87 ms* |

Lower MAE and higher PSNR/SSIM/edge score indicate closer pixel/structure similarity to these paired targets. They do **not** establish geographic correctness. `*` Latency is a reported CPU evaluation measurement; live request time varies by machine and includes other processing.

## Why the app output looks grey: important audit finding

The latest colour audit found a **mean RGB channel spread of 0.00471 in the model output but 0.00000 in the paired targets loaded for these 200 test tiles**. A spread near zero means the arrays are effectively grayscale. This indicates the evaluator is currently reading grayscale B targets (or the manifest points to grayscale files), despite the team seeing green images elsewhere in the archive.

The first fix is therefore **verify the exact A/B paths in the manifest against one of the green B files**. Run `python scripts/inspect_png_pair.py --manifest data/manifests/tiles.json --tile-id test-ROIs1868_summer_s000131_p000746`; it prints the A/B filenames and RGB channel statistics without exposing absolute local paths. More epochs cannot teach colour if the target arrays being loaded have no colour variation. If the intended B image has colour but the manifest points elsewhere, correct/regenerate the manifest first. Keep the test set untouched when selecting the model. The limited 1,000-tile, 5-epoch run may also underfit, but it is not the only issue indicated by this report.

## Colour-collapse diagnostic

New evaluation runs also report `mean_rgb_channel_spread` for model output and reference. It is the average per-pixel difference between the largest and smallest RGB channel: near zero means the image is close to grey; a larger reference value with a much smaller prediction value is evidence of colour collapse. This is a diagnostic, not a quality score by itself.

## Interpretation of live UI values

- **Observed runtime:** time for that request on the current machine.
- **Structure proxy:** correlation of image gradients between input and output. It is not accuracy or a comparison with the paired B target.
- **Mean consistency:** agreement between original and flipped model predictions. It is not calibrated uncertainty or truth.
- **Held-out evaluation:** the table above; it is a small, locally run subset, not full-dataset validation.

## Reproduce / extend evaluation

```bash
python -m ml.src.evaluate \
  --manifest data/manifests/tiles.json \
  --checkpoint backend/checkpoints/vyora_resunet.pt \
  --max-test-tiles 200 --seed 42 \
  --output docs/evaluation_results.json \
  --examples-dir docs/evaluation_examples
```

The evaluator compares the model and a simple intensity-to-palette baseline and saves input/reference/prediction/error panels for the highest-MAE test cases. Keep the test split untouched while choosing training settings. The original manifest and generated report/panels stay local unless the team intentionally reviews and publishes them; do not publish absolute local paths or the 34 GB archive.

## Reporting language

Say: “On a 200-tile subset of our supplied test split, the prototype was more similar to paired PNG targets than a simple pseudocolour baseline.”

Do not say: “restores real satellite colours,” “verified VV/VH,” “geographically accurate,” “detects floods,” or “99% accurate.”
