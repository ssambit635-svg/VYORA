# Model card — Vyora Sentinel-1 VV/VH → Sentinel-2-style baseline

## Current status

**No paired SEN12MS subset or trained checkpoint is included. No held-out results are claimed.** The running demo defaults to `dev-heuristic-v0` and is not AI inference. Synthetic samples demonstrate only the interface; they are not satellite data.

| Field | Current status |
|---|---|
| Product task | Estimate an optical-style RGB visual layer from dual-polarization Sentinel-1 backscatter |
| Planned baseline | Compact ResU-Net generator, input VV+VH (2 channels), output RGB-style 3 channels |
| Active API runner | `dev-heuristic-v0` unless a checkpoint exists |
| Checkpoint | None bundled; expected at `backend/checkpoints/vyora_resunet.pt` |
| Training set | None bundled; SEN12MS is the intended source, subject to licence/access, pair/grid verification, and preprocessing |
| Evaluation | Not run on real paired data |

## Input contract

- Preferred inference input: calibrated, terrain-corrected, co-registered, two-band GeoTIFF, band 1 = VV and band 2 = VH.
- The service retains CRS and affine transform for the optional RGB-style GeoTIFF preview export.
- Per-band preprocessing: finite-value handling, 2nd–98th percentile normalization, light 3×3 median filtering and resize to 256×256.
- **This code does not perform Sentinel-1 radiometric calibration or terrain correction.** Supply already prepared imagery; verify the product level and units before model use.
- PNG/JPEG and synthetic demos are accepted for interface testing. A single channel is duplicated to two channels and marked `single-channel-preview-duplicated`; it is not valid dual-polarization model evidence.

## Architecture and objective

`ml/src/model.py` defines a compact ResU-Net encoder/decoder with skip connections. Its only trained output is a sigmoid RGB-style image. The training objective is paired L1 reconstruction, SSIM structure loss and edge-preservation loss. There is no GAN/PatchGAN in the current baseline; Pix2Pix is a future experiment only.

The model deliberately has **no learned confidence or land-cover class heads**: the paired image manifest has RGB targets but no uncertainty labels or class masks, so those heads could not be meaningfully supervised. This corrects the earlier prototype design. In checkpoint mode:

- the consistency layer is the agreement between original and horizontally flipped predictions; it is not calibrated uncertainty;
- the four feature-share cards are a fixed palette lookup on generated RGB, not learned classification or segmentation;
- neither should be described as accuracy, calibrated probability, or ground-truth land cover.

## Data preparation and splits

The preferred manifest schema is documented in `docs/DATA_CARD.md`. VV, VH and visible target bands must be aligned on the same grid. Geographic/scene groups are confined to one split. Sentinel-2 targets must be cloud-screened and the target scale/order recorded. The loader normalizes SAR bands independently; GeoTIFF optical targets use explicit `optical_scale` (default 10,000 for integer-scaled reflectance; set 1 for pre-normalized [0,1] data). Confirm source conventions before training.

Train with `python -m ml.src.train --config ml/configs/train_default.json`; evaluate only against a separate test-region split with `python -m ml.src.evaluate`. Do not use synthetic demo scenes as training or validation evidence.

## Intended and prohibited uses

Intended only for educational visual exploration, a hackathon demonstrator, or first-look browsing followed by specialist review. Not for official mapping, flood/cyclone warnings, evacuation, emergency response, safety-critical decisions, or reconstruction of true visible colour.

## Key limitations

- Optical appearance is an estimate from paired observations and varies with season, time, clouds, illumination and sensor geometry.
- Radar layover, shadow, speckle, terrain, calibration, co-registration and domain shift can invalidate the mapping.
- GeoTIFF export retains spatial extent/CRS but is a 256×256 model preview; it is not a calibrated science-ready product.
- Synthetic demos have no geography or optical reference.
- Visual plausibility is not geographic correctness.
