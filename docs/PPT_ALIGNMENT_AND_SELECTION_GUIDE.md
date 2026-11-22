# PPT alignment and selection guide

**Source deck:** `VYORA_VOLTRIX_HackKalp_Fully_Editable.pdf` (9 slides, attached by the team). This repo is adjusted to the deck's core technical story: prepared Sentinel-1 VV/VH → paired Sentinel-2 visible target → U-Net baseline → review/export.

## Serious issues to resolve before judging

1. **The biggest credibility gap is data/model status.** The deck says “Vyora learns” and shows a trained model path. The repository currently has no paired SEN12MS subset or trained checkpoint; the running API/Streamlit app defaults to deterministic development rules. A judge can expose this in one live inference. Do not disguise it. Highest-impact improvement: prepare and cite a small licensed paired subset, train a real dual-channel checkpoint, and report actual held-out-region evidence. If that cannot be completed, clearly call the app a development prototype and demonstrate the real preprocessing/training/evaluation pipeline—not fabricated AI output.
2. **Slide 1 has visible placeholders:** `Team ID: [ADD TEAM ID]` and `PS: [ADD PS CODE]`. They must be filled before submission. The PS code from the project context is `HK26-PS-19`; obtain the real Team ID from the event portal. This is the one unavoidable deck correction even if no content/layout changes are wanted.
3. **Calibration wording must be exact.** Current code performs robust per-band normalization; it does not implement Sentinel-1 radiometric calibration or terrain correction. Only upload prepared/calibrated/co-registered GeoTIFFs, or add and validate the official upstream preprocessing step. Do not tell judges Rasterio alone calibrates SAR.
4. **The output is not true colour.** Sentinel-2 is a paired visual target, acquired at a different time and subject to cloud/season/illumination differences. Keep “estimated optical-style layer” wording and show source SAR next to it.
5. **SEN12MS availability is not implementation evidence.** The slide's corpus size is a literature/source fact, not proof that the project has obtained, filtered, aligned, licensed, or trained on those samples. State precisely what data you actually prepared.
6. **Confidence and feature cards need careful labels.** The model has only an RGB reconstruction head. Flip-view agreement is a consistency cue, not calibrated uncertainty. Palette shares are not learned segmentation or class probabilities. Avoid calling either “accuracy” or “confidence probability.”
7. **Stack difference:** slide 4 names Streamlit. `streamlit_app.py` and `scripts/run_streamlit.sh` now provide that interface. The pre-existing React/FastAPI application remains an optional alternate. During judging, use the Streamlit version shown in the deck, not both UIs.

## Deck-to-repository map

| Slide | Deck claim | Repository support / remaining proof |
|---|---|---|
| 1 | Vyora, Voltrix, team members, PS | Brand and student names are in deck; Team ID and PS placeholders still need event values |
| 2 | SAR backscatter is not visible colour; non-specialist problem | UI and method docs state estimate/limitations; demo imagery is synthetic, not a live product |
| 3 | Sentinel-1 VV/VH → paired Sentinel-2 → U-Net → review | Dual-channel model, GeoTIFF decoder, manifest loader and Streamlit workflow now exist; no real checkpoint/data yet |
| 4 | SEN12MS, Python/NumPy/Rasterio/GDAL, PyTorch, Streamlit, PNG/GeoTIFF | Streamlit and Rasterio paths implemented; real dataset prep and physical calibration still needed |
| 5 | Inference and training/evaluation; regional split | Manifest prevents scene-group split leakage; training/evaluation code exists; only real-data run is missing |
| 6 | L1 baseline, optional PatchGAN, validation/limits | L1 + SSIM + edge objective implemented; no PatchGAN; evaluation not run. Do not imply AI assistants are core product functionality |
| 7 | dual-polarization contribution and review workflow | VV/VH API input and compare/export path implemented; no real-data evidence yet |
| 8 | beneficiaries, feasibility, future confidence/export | Export exists; impact is intended, not measured; user-comprehension review and expert validation remain future work |
| 9 | team | Confirm spelling/roll numbers and team identity against official registration |

## Best use of limited remaining time (ranked)

### P0 — integrity and demo success
- Fill the two slide-1 placeholders (official Team ID and `HK26-PS-19`).
- Run the exact deck-aligned Streamlit launch on the presentation laptop, not just a browser preview. Test one calibrated VV/VH TIFF and one synthetic fallback; rehearse no-internet startup.
- Put a visible “development mode / no trained checkpoint” message on the demo result until actual training succeeds.
- Confirm the GeoTIFF has VV first, VH second, correct CRS and transform; verify exported bounds and overlay against the source. The repository has a synthetic round-trip test, but the team must verify with its real data.

### P1 — evidence judges can trust
- Obtain permitted SEN12MS samples or another licensed paired source; record exact subset and license, scene IDs, products, acquisition dates, target scale/band order, cloud filters, co-registration and preprocessing.
- Create a small geographic holdout (separate scene groups/regions), not random neighboring tiles. Visually inspect several pairs before training.
- Train the 2→3 ResU-Net baseline and compare a simple fixed/pseudocolour baseline. Save the actual checkpoint locally and results JSON.
- Report MAE, PSNR, SSIM, edge alignment and CPU latency only with split size, region split, hardware and preprocessing. Show at least one good example and one failure/low-consistency case.

### P2 — selection polish
- Replace or supplement synthetic gallery images with a small legal, clearly attributed real pair; keep synthetic fallback offline.
- Have a SAR-aware mentor/user review band order, calibration assumptions, target pairing and generated output. Add one brief comprehension test only if you can honestly describe sample size and method.
- Rehearse a 3-minute story: problem → VV/VH distinction → paired learning → live compare → one measured result → failure/limits → next step.

## Reusable keywords (use only where true)

**Core:** dual-polarization SAR; Sentinel-1 GRD; VV/VH; paired Sentinel-1/Sentinel-2; SEN12MS; optical-style estimate; image-to-image translation; compact U-Net/ResU-Net; skip connections; supervised L1 reconstruction; SSIM; edge preservation; co-registration; CRS/affine transform; geospatial GeoTIFF; geographic/scene-group holdout; reproducible manifest; uncertainty/consistency caveat; human-in-the-loop review; local-first, open-source; cloud-independent demo.

**Avoid unless measured/implemented:** “real colours restored”; “cloud-proof flood map”; “real-time disaster response”; “accurate land-cover segmentation”; “calibrated confidence”; “180k images trained”; “works across all sensors”; “radiometric calibration in-app”; “expert validated”; any accuracy percentage without split and saved calculation.

## Recommended 20-second answer

“Vyora is a local-first prototype for an estimated optical-style view from dual-polarization Sentinel-1 VV/VH. Our intended baseline is a compact U-Net trained on paired Sentinel-2 visible targets, with region-wise holdout and structure-aware evaluation. We always preserve the radar view and geospatial reference, because generated appearance is not true colour. Today the UI and pipeline are implemented; the honest remaining milestone is a trained checkpoint and held-out real-data evidence.”

Use that final sentence only until the team has actually trained/evaluated. Update it with verifiable results afterward.
