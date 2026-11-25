# Evaluation report

## Current status: corrected B→A PNG prototype evaluated

The paired-folder audit found A mostly colour-bearing and B grayscale in the sampled files. The corrected experiment uses grayscale B as input and A as target. This is based on image-channel statistics only; it does **not** prove that B is Sentinel-1 SAR or A is true optical imagery. The supplied folder split's geographic independence was not independently verified.

### Training and test subset

- Training: CPU, 1,000 train tiles, 200 validation tiles, 5 epochs.
- Best validation loss: 0.16335 at epoch 5.
- Test: 200 of 4,576 tiles, seed 42; 200 scene groups.
- Median CPU inference latency reported by the evaluator: 81.69 ms.

### Paired-target comparison

| Method | MAE ↓ | PSNR (dB) ↑ | SSIM ↑ | Edge preservation ↑ | Mean RGB spread (prediction) | Mean RGB spread (target) |
|---|---:|---:|---:|---:|---:|---:|
| Pseudocolour baseline | 0.35373 | 8.13531 | 0.24769 | 0.23112 | 0.39119 | 0.13053 |
| B→A ResU-Net | 0.09632 | 20.99456 | 0.67069 | 0.35000 | 0.03778 | 0.13053 |

The model is substantially closer to paired targets than this simple baseline on this subset. But its average RGB spread is only about 29% of the target spread, so the output is still noticeably under-coloured. The saved worst-error panels include cases where target spread is 0.57–0.74 but model spread is around 0.03. This is an important failure mode, not a detail to hide.

These scores measure pixel similarity to this paired PNG test subset only. They do not prove true-colour recovery, sensor identity, geographic correctness, or emergency-response usefulness. Do not call the 99% flip consistency “99% accurate.”

## Reproduce the local report

```powershell
python -m ml.src.evaluate --manifest data/manifests/tiles.json --checkpoint backend/checkpoints/vyora_resunet_b_to_a.pt --max-test-tiles 200 --seed 42 --output docs/evaluation_results_b_to_a.json --examples-dir docs/evaluation_examples_b_to_a
```

The report JSON and example panels are generated locally and ignored by Git because they can contain local paths/derived imagery. The 34 GB source archive and manifest are not in the repository.

## What the UI values mean

- **Observed runtime:** time for the current request on this machine.
- **Structure proxy:** correlation of image gradients between input and output; not accuracy against target.
- **Mean consistency:** agreement between original and flipped model predictions; not calibrated uncertainty or truth.
- **RGB channel spread:** a colour-collapse diagnostic, not a quality score by itself.
- **No classification:** the model does not identify water, floods, vegetation, buildings, or land-cover percentages.

## Next scientific improvements

1. Verify source semantics/licence and that the B→A pairing represents the intended task.
2. Improve colour fidelity using validation-only model selection; preserve the test split for final reporting.
3. Verify geographic separation by ROI/scene before making generalization claims.
4. Get feedback from remote-sensing users before describing the prototype as decision support.
