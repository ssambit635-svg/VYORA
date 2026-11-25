# Evaluation and direction audit

## Current status

The latest audit found that the original manifest had the image direction reversed for the intended grayscale-to-colour demo:

| Folder | Sample | Images with RGB spread > 0.02 | Mean RGB spread |
|---|---:|---:|---:|
| train_A | 100 | 99 | 0.14233 |
| train_B | 100 | 0 | 0.00000 |
| val_A | 100 | 97 | 0.12458 |
| val_B | 100 | 0 | 0.00000 |
| test_A | 100 | 99 | 0.11702 |
| test_B | 100 | 0 | 0.00000 |
- The previous manifest fed A (which training converted to grayscale) and used B as target. The B targets had `mean_rgb_channel_spread = 0.00000`.
- The previous checkpoint therefore learned **grayscale A → grayscale B**, not grayscale SAR-like input → colour image.

The 200-tile numbers below are retained as a **historical pipeline check only**. They are not a valid colourization benchmark and must not be presented as proof that Vyora predicts colour. A corrected manifest now defaults to grayscale B input → colour-bearing A target, subject to verifying the dataset semantics. The old checkpoint is incompatible and must not be fine-tuned for the corrected direction.

## Historical metrics: old A→B direction

Reported run: CPU, 1,000 train tiles, 200 validation tiles, 5 epochs; evaluation on 200 of 4,576 test tiles, seed 42. Folder-split geographic independence was not independently verified.

| Method | MAE ↓ | PSNR (dB) ↑ | SSIM ↑ | Edge preservation ↑ | Mean RGB spread (prediction) | Mean RGB spread (target) |
|---|---:|---:|---:|---:|---:|---:|
| Pseudocolour baseline | 0.22571 | 11.55409 | 0.24056 | 0.21084 | 0.41310 | 0.00000 |
| ResU-Net checkpoint | 0.15514 | 15.72773 | 0.44559 | 0.45740 | 0.00471 | 0.00000 |

The target spread of zero means the targets loaded by that run were effectively grayscale. Similarity metrics against those targets do not establish colour recovery, geographic correctness, or operational utility. The reported CPU median latency was 86.07 ms for the latest audit run; live request time varies by machine and includes other processing.

## Correct workflow before retraining

1. Regenerate the manifest with `--input-side B` (the default), so grayscale B is the model input and A is the target.
2. Check a matched pair with `scripts/inspect_png_pair.py`; verify the target has non-zero RGB spread and visually matches the intended colour image.
3. Train from scratch to a **new checkpoint path**. Do not resume the old A→B checkpoint; the input-side marker intentionally makes the trainer reject it.
4. Select checkpoints only using validation loss. Then evaluate once on the held-out test subset and inspect paired target/prediction/error panels.

Example Windows commands:

```powershell
python scripts/prepare_png_split_manifest.py --data-root "$env:OneDrive\Desktop\imagery data\archive\sen12ms_SUMMER" --input-side B --licence-note "Record the actual source and terms"
python -m ml.src.train --config ml/configs/train_default.json --epochs 5 --max-train-tiles 1000 --max-validation-tiles 200 --output-checkpoint backend/checkpoints/vyora_resunet_b_to_a.pt
python -m ml.src.evaluate --manifest data/manifests/tiles.json --checkpoint backend/checkpoints/vyora_resunet_b_to_a.pt --max-test-tiles 200 --seed 42 --output docs/evaluation_results_b_to_a.json --examples-dir docs/evaluation_examples_b_to_a
```

The 1,000-tile, 5-epoch CPU run previously took over 30 minutes. It may still underfit; more data/epochs can take substantially longer and are not guaranteed to improve visual quality. Do not overwrite or promote the current checkpoint until the corrected run is verified.

## Colour diagnostic

`mean_rgb_channel_spread` is the average per-pixel difference between the largest and smallest RGB channel: near zero means nearly grayscale; a larger value means more channel separation. Compare prediction with target. It is a colour-collapse diagnostic, not a quality score by itself.

## Live UI values are not accuracy

- **Observed runtime:** time for the current request on this machine.
- **Structure proxy:** correlation of image gradients between input and output; not accuracy or comparison with the paired target.
- **Mean consistency:** agreement between original and flipped model predictions; not calibrated uncertainty or truth.
- **No classification:** the model does not identify water, floods, vegetation, buildings, or land-cover percentages.

Until a corrected B→A evaluation is run, report the metrics above only as an audit of the old direction—not as colorization performance.
