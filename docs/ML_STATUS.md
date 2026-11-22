# ML completion status

Checked on the active branch after the code-level smoke run.

| Area | Status |
|---|---|
| ResU-Net architecture | Implemented: VV/VH input (2 channels) → RGB-style output (3 channels) |
| GeoTIFF inference preprocessing | Implemented and tested with integer pixels and NoData values; expects prepared/calibrated input |
| Paired data loader | Implemented for aligned VV/VH and visible RGB tiles; CRS/transform checks and relative manifest paths covered by tests |
| Train/validation/test leakage guard | Implemented at `scene_group` level |
| Training loop | Implemented; one-epoch temporary smoke run completed on artificial PNG pairs only |
| Evaluation code | Implemented: MAE, PSNR, SSIM, edge alignment and latency |
| Real training data | **0 real paired tiles in this repository.** No SEN12MS subset or other licensed pair supplied |
| Real model training | **0 meaningful epochs / 0 real training steps.** No trained checkpoint exists |
| Real held-out evaluation | **Not run.** No real test split exists |
| Model accuracy | **Unknown.** Do not quote the smoke-run numbers; they came from synthetic fixtures and were not saved as project results |

The synthetic smoke run proves only that the training/evaluation scripts execute. It does not establish SAR colorization quality, geographic generalization, or useful confidence. Recheck the current workspace at any time with `python scripts/check_ml_readiness.py`.

## What is still required for a real model

1. Supply lawful, paired, co-registered Sentinel-1 VV/VH and Sentinel-2 visible tiles, with source/licence and scale metadata.
2. Confirm the Sentinel-1 data has undergone the required radiometric calibration and terrain correction upstream. This repository does not do that processing.
3. Assign `scene_group` by region/source scene and create separate train, validation and held-out test groups.
4. Train the 2→3 channel model; save the actual checkpoint outside Git if size/licence requires it.
5. Run evaluation on real held-out groups; inspect examples/failures and record hardware, split, preprocessing and metrics.
6. Only then claim that a trained model is present. Until then the live app correctly uses the labelled development fallback.
