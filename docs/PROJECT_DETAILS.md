> **Project note (21 Nov 2026):** this specification was written under the working name **DrishtiSAR**. The repository product is now branded **VYORA**; read every reference to DrishtiSAR below as Vyora. The problem statement (HK26-PS-19) and requirements are unchanged. Implementation status and any deviations are recorded in [IMPLEMENTATION_DECISIONS.md](IMPLEMENTATION_DECISIONS.md).

# DrishtiSAR — Project Details

> **Controlling scope (21 Nov 2026):** follow the attached Voltrix deck: prepared Sentinel-1 VV/VH dual-pol GeoTIFF → paired Sentinel-2 visible target → compact 2→3 channel U-Net baseline → side-by-side review and geospatial preview export. Streamlit is the deck-aligned interface. Older single-channel assumptions in this specification are legacy text. No real paired subset or trained checkpoint is currently bundled; do not present the fallback as AI output.

**Project:** DrishtiSAR  
**Tagline:** From radar texture to confidence-aware geographic interpretation.  
**Problem statement:** HK26-PS-19 — SAR Image Colorization Using Deep Learning

---

## 1. Project summary

Vyora is a local-first geospatial visual-interpretation prototype planned to map prepared **Sentinel-1 VV/VH dual-polarization** input to an estimated Sentinel-2-style RGB layer. The current default run is a labelled development fallback: there is no trained checkpoint or paired dataset bundled yet.

The app displays more than a colourized output. It makes three questions visible:

1. **What structure did the SAR image contain?** — original SAR image.
2. **What geographic appearance does the model estimate?** — colour interpretation output.
3. **How stable is the generated appearance under a simple view change?** — flip-view consistency cue and palette shares, explicitly not calibrated probabilities or land-cover labels.

The final prototype is designed around a coastal/disaster-response demonstration but remains useful for urban, agricultural, and water-body scenes.

---

## 2. The problem in simple terms

A normal optical satellite image is intuitive because water, vegetation, roads, and buildings often look visually distinct. SAR images instead record radar backscatter. They are useful in difficult observing conditions but can appear grainy and monochrome.

The challenge asks for deep-learning colourization that improves visual interpretation while retaining relevant geographical information. A correct solution must therefore avoid treating this as decorative recolouring. It must preserve meaningful boundaries, patterns, and land-cover clues.

---

## 3. Proposed solution

### Product statement
> Vyora is intended to learn a mapping from paired Sentinel-1 VV/VH and Sentinel-2 visible patches. The training-data and checkpoint milestone is not yet complete; until then, the demo is a clearly labelled product-flow prototype.

### Main differentiators

| Common colourization demo | DrishtiSAR |
|---|---|
| Only produces a colourful image | Produces colour, confidence, feature likelihoods, and metrics |
| Implies output is a real photograph | Clearly labels output as an AI estimate |
| No evidence that structure was retained | Shows structural/edge-preservation evidence |
| Generic satellite use case | Focuses on rapid coastal and disaster interpretation |
| Works only on a desktop notebook | Provides a responsive app usable from phones |

---

## 4. User scenario

### Scenario: rapid post-event scene review

A response analyst receives a SAR scene from a cloudy coastal region. An optical image is unavailable or difficult to interpret quickly.

1. The analyst opens DrishtiSAR from a phone or laptop.
2. They select the coastal demo scene or upload a supported SAR image.
3. The app returns an estimated colour interpretation.
4. The analyst compares the raw SAR texture and predicted output with a slider.
5. The analyst turns on the confidence layer.
6. Low-confidence regions are flagged for confirmation through trusted imagery or official data.

**Important boundary:** The analyst does not use DrishtiSAR alone to issue a warning or make a safety-critical decision.

---

## 5. Inputs and outputs

### Inputs

| Input | MVP support | Notes |
|---|---|---|
| Prepared Sentinel-1 dual-pol GeoTIFF | Target input | VV/VH order and CRS/affine metadata; physical calibration must happen upstream |
| Paired Sentinel-2 visible target | Required for training | Must be cloud-screened, co-registered, scaled and legally reusable |
| Synthetic grayscale preview | UI fallback only | Duplicated into two channels; not real SAR or dual-pol evidence |
| Scene metadata | Optional | Scene name, source/date, polarization, location label; no user location required |

### Outputs

| Output | Purpose |
|---|---|
| Estimated RGB-style colour interpretation | Easier visual recognition of land patterns |
| Input/output comparison slider | Helps users check that the raw SAR structure has not been hidden |
| Water/vegetation/built-up/bare-other likelihoods | Provides a simple feature-level interpretation |
| Confidence/uncertainty map | Identifies areas that require manual verification |
| Structural and edge-preservation metrics | Technical evidence for model evaluation |
| PNG and JSON export | Enables presentation/demo hand-off |

---

## 6. End-to-end architecture

```text
                         TRAINING (before demo)
Paired SAR + optical tiles
        │
        ├─ pair validation / normalization / tiling
        ├─ train ResU-Net or U-Net image-to-image model
        ├─ evaluate held-out scenes and save metrics
        └─ export model checkpoint + model metadata

                         INFERENCE (web application)
Phone/laptop browser
        │
        ├─ choose demo scene or upload image
        ▼
React user interface
        │  HTTPS/LAN HTTP
        ▼
FastAPI inference service
        ├─ validate and normalize image
        ├─ optional light despeckling
        ├─ PyTorch model inference
        ├─ confidence calculation
        ├─ feature-score calculation
        └─ create result JSON + output PNG
        ▼
Responsive result view
        ├─ comparison slider
        ├─ output and confidence overlays
        ├─ feature cards
        ├─ metric panel
        └─ download controls
```

---

## 7. ML design

### Baseline model
A compact **U-Net/ResU-Net encoder-decoder** maps normalized, paired VV/VH tiles (2 input channels) to a three-channel Sentinel-2-style visible target. The trained checkpoint is not yet available.

This is deliberately selected over a large GAN/transformer/diffusion model because it is:
- more likely to train stably in the available time;
- practical on a free notebook GPU or a compact curated dataset;
- easier for a first ML team to explain;
- lightweight enough for local CPU inference after training.

### Candidate objective

```text
Total Loss = colour reconstruction loss
           + structure/SSIM-oriented loss
           + edge-preservation loss
```

The exact coefficients must be selected through validation, documented, and never invented for slides.

### Confidence approach

MVP options, from simplest to more advanced:
1. **Output-consistency confidence:** confidence derived from normalized local model response and output stability.
2. **Test-time augmentation:** infer on small flips/rotations and treat agreement as higher confidence.
3. **Monte Carlo dropout:** run repeated inferences with dropout enabled and use prediction variance as uncertainty.

The chosen method must be implemented honestly and described in the model card.

### Feature probabilities
The preferred method is a small auxiliary feature head trained on available labels/derived masks. If labels are not available in time, the team may implement clearly labelled **estimated feature indicators** based on the output/model confidence—but must not represent them as independently validated segmentation results.

---

## 8. Data plan

### Training-pair requirements
The model requires matched or near-time matched pairs:
- SAR input tile from a consistent sensor configuration where possible;
- optical RGB reference tile aligned to the same geographic footprint;
- clear documentation of acquisition timing, cloud filtering, spatial resolution, and transformations;
- train/validation/test split by geographic scene, not random adjacent tiles only, to reduce leakage.

### Curated data approach
For the hackathon MVP, use a documented, legally usable subset of pairs rather than trying to ingest global archives. The subset should include at least:
- coastal/water;
- vegetation/agriculture;
- urban/built-up;
- mixed terrain.

### Data quality checks
- Confirm input/target tile alignment visually.
- Exclude obviously cloudy or mismatched optical reference tiles.
- Preserve source attribution and licence information.
- Ensure test scenes are not reused during model fitting.

---

## 9. Evaluation plan

### Quantitative evaluation
Evaluate the final model on held-out scenes using:
- MAE / L1 reconstruction error;
- SSIM, if implemented correctly;
- edge-preservation score, comparing derived edges of target and prediction;
- median CPU inference time.

Metrics measure similarity to the paired optical target; they do not prove that the generated colour is a true reconstruction in all conditions.

### Qualitative evaluation
Prepare a grid of held-out examples with:
- SAR input;
- optical reference used only for evaluation;
- DrishtiSAR output;
- simple pseudocolour baseline;
- confidence overlay.

### Comparison baseline
Use a non-ML intensity-based pseudocolour transform. The purpose is to demonstrate why learned geographic interpretation is more useful than merely applying a colour palette.

---

## 10. Key messages for the pitch

### Problem
> SAR works when the sky does not cooperate, but raw SAR imagery is difficult for non-specialists to interpret.

### Solution
> DrishtiSAR uses deep learning to turn radar texture into a confidence-aware colour interpretation, not simply a prettier image.

### Innovation
> It preserves geographic structure, quantifies confidence, and exposes low-trust areas rather than hiding uncertainty behind attractive colours.

### Impact
> It can support faster first-look analysis of coastal, urban, agricultural, and disaster-related scenes.

### Responsible AI statement
> DrishtiSAR is a decision-support demonstrator. It does not replace official remote-sensing analysis, weather warnings, or ground verification.

---

## 11. Hackathon demo plan

1. **Open on a phone:** show responsive home screen and one-line limitation statement.
2. **Choose coastal sample:** avoid relying on a random upload first.
3. **Run model:** show a short processing state.
4. **Reveal comparison slider:** raw SAR on left, predicted interpretation on right.
5. **Toggle confidence layer:** point out a low-confidence region and explain verification.
6. **Show feature cards and metrics:** demonstrate AI evidence, not only a UI.
7. **Download JSON/PNG:** show practical output.
8. **End with impact:** rapid first-look interpretation when optical imagery is difficult.

---

## 12. Explicit limitations

- A colourized output may be visually plausible without being geographically exact.
- Model quality depends on the sensor type, polarization, timing, registration, and data distribution used during training.
- A small hackathon dataset cannot claim global generalization.
- Confidence indicates model uncertainty, not real-world certainty.
- Any operational use would require robust validation by domain experts and comparison with authoritative geospatial data.

---

## 13. Deliverables

- Working responsive web application
- Saved model checkpoint and reproducible inference script
- Curated demo scenes and documented source/licence data
- Evaluation notebook/report with real metrics
- Architecture diagram
- README, model card, data card, API document, demo script, test checklist
- Presentation deck and short backup demo video/screenshots
