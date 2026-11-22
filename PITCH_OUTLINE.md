# Voltrix deck presenter notes — aligned to the attached PDF

This file gives spoken notes for the existing 9-slide deck; it does not alter the presentation. Do not present proposed work as completed. See `docs/PPT_ALIGNMENT_AND_SELECTION_GUIDE.md` for the serious gaps and selection priorities.

1. **Title / team:** State HK26-PS-19 and team names. Before submission, replace `[ADD TEAM ID]` and `[ADD PS CODE]` with the official values.
2. **Problem:** SAR records backscatter, not visible colour. Brightness depends on roughness, moisture, geometry and polarization; the slide illustration is synthetic, not a satellite scene.
3. **Solution:** Planned mapping is prepared Sentinel-1 VV/VH to Sentinel-2-style visible imagery using paired examples. Explain that this is an estimate and keep the original SAR for review.
4. **Stack:** Streamlit UI, Rasterio/NumPy for geospatial I/O, PyTorch U-Net baseline. Current app normalizes prepared input but does not radiometrically calibrate or terrain-correct it.
5. **Architecture:** Scene-group split, U-Net training and held-out metrics. The code path exists; actual paired-data training and evaluation are not yet complete.
6. **Role of AI:** Only call it learned inference after loading a team-trained checkpoint. Current default is a deterministic development fallback; there are no real-data metrics.
7. **Difference:** VV/VH input, structural skip connections, paired optical-style target, and original-SAR comparison are the intended contribution. Do not claim validated feature segmentation or calibrated uncertainty.
8. **Impact/future:** Describe beneficiaries as intended users, not measured impact. Next work: lawful data preparation, expert review, held-out evaluation, model checkpoint and comprehension testing.
9. **Team:** Confirm the official Team ID, PS code, names and roll numbers.

## Safe answer if asked for accuracy

“We do not have a real held-out result to report yet. The current output in this demo is development mode unless we show our own trained checkpoint and saved evaluation report. We will report only metrics tied to a region-separated test set.”
