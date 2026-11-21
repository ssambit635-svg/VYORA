# DrishtiSAR — Product Requirements Document

**Version:** 0.1 (Hackathon MVP)  
**Status:** Approved concept  
**Problem statement:** HK26-PS-19 — SAR Image Colorization Using Deep Learning  
**Build constraint:** 2–3 days, no paid APIs or services, first AI/ML project, phone-accessible web app

---

## 1. Product vision

**DrishtiSAR** is a confidence-aware AI tool that converts difficult-to-interpret grayscale Synthetic Aperture Radar (SAR) imagery into an estimated colour geographic representation. It helps a non-SAR specialist rapidly distinguish likely water, vegetation, built-up, and bare/other regions while making uncertainty visible.

The product is designed as a **decision-support demonstrator** for rapid coastal and disaster interpretation. It does **not** claim to produce the exact natural optical photograph or replace an official disaster, weather, or mapping service.

### Elevator pitch
> When cloud cover or darkness makes optical imagery unavailable, DrishtiSAR transforms SAR imagery into an interpretable, confidence-aware colour view so responders and planners can inspect likely geographic features faster.

---

## 2. Problem

SAR imagery is valuable because it can be acquired under conditions where optical imagery is difficult to use. However, SAR data is noisy, grayscale, and unfamiliar to many users. A person without radar-image expertise may struggle to distinguish water, vegetation, urban structures, and other land features quickly.

A plain image colourization demo is insufficient because visually plausible colours can hide uncertainty or distort geographic structure. The solution must improve interpretability **and** help users understand how much to trust the output.

---

## 3. Target users

| Persona | Need | DrishtiSAR value |
|---|---|---|
| Disaster-response analyst | Quickly inspect a radar scene after adverse weather | Interpretable colour output, confidence view, and feature probabilities |
| Urban/coastal planner | Compare geographic patterns in sample scenes | Built-up, vegetation, and water interpretation layers |
| Student/research demonstrator | Explain SAR-to-optical-style deep learning clearly | Transparent pipeline, metrics, and comparison slider |
| Hackathon judge | Verify that the solution is both useful and technically credible | Working end-to-end AI model with honest limitations |

---

## 4. Product goals

### Primary goals
1. Accept a prepared single-channel SAR image (`.png`, `.jpg`, `.jpeg`; GeoTIFF is a stretch goal).
2. Preprocess the image and run a locally hosted deep-learning inference model.
3. Produce an estimated three-channel colour interpretation image.
4. Display input and output using a before/after comparison slider.
5. Show feature-likelihood values for **water**, **vegetation**, **built-up**, and **bare/other**.
6. Show a per-pixel or tiled **confidence/uncertainty map**.
7. Show model/runtime metadata and structure-preservation metrics for prepared evaluation scenes.
8. Work in a responsive phone browser while the model runs on a local laptop server.
9. Require no paid API, subscription, or cloud GPU for demo inference.

### Secondary goals
- Demonstrate a coastal Odisha / cyclone-response use case with curated sample imagery.
- Let users download the colour interpretation image and a compact JSON result.
- Include a demo gallery so the application remains reliable if a user upload fails.

---

## 5. Non-goals for the MVP

- Claiming the output is a true, ground-truth RGB satellite image.
- Producing official cyclone, flood, evacuation, or disaster warnings.
- Global, real-time satellite-stream ingestion.
- Training a model inside the web application.
- Building an operational GIS platform or performing legal/official mapping.
- Guaranteeing that every arbitrary SAR sensor, polarization, or GeoTIFF format is supported.

---

## 6. MVP user flow

1. User opens DrishtiSAR on desktop or phone.
2. User selects a curated demo scene or uploads a supported SAR image.
3. User reviews a brief limitation notice and taps **Interpret Scene**.
4. Backend preprocesses the image and runs the model.
5. The result screen displays:
   - Original SAR image
   - Colour interpretation output
   - Drag comparison slider
   - Feature-probability cards
   - Confidence/uncertainty heatmap
   - Inference time and model version
   - Plain-language limitation statement
6. User optionally downloads the output image and JSON summary.

---

## 7. Functional requirements

### FR-01: Demo gallery
The app must provide at least four prepared scenes:
- water/coastal region;
- vegetation/agricultural region;
- dense or mixed built-up region;
- mixed scene relevant to a disaster-response narrative.

**Acceptance:** A user can obtain a full result without uploading a file.

### FR-02: File input and validation
The app must accept PNG/JPEG SAR demo images up to a defined safe size (target: 10 MB). It must reject unsupported file types with a helpful message.

**Acceptance:** Invalid files do not reach model inference and show an actionable error.

### FR-03: Preprocessing
The backend must normalize the SAR image into a model-compatible single-channel tensor and resize/crop it to the inference tile size (target: `256 × 256`). Optional lightweight despeckling may be used if it improves results consistently.

**Acceptance:** The same prepared input returns a deterministic, valid tensor and result.

### FR-04: Deep-learning inference
The app must load a saved model checkpoint and infer an RGB-style colour interpretation image. The model must run on CPU for the demo fallback.

**Acceptance:** A prepared scene completes inference within a target of 10 seconds on the demonstration laptop.

### FR-05: Interpretability layers
The result must display four normalized likelihood scores: water, vegetation, built-up, and bare/other. These may be calculated from a lightweight auxiliary prediction head or documented colour/feature mapping.

**Acceptance:** Scores are visible, sum approximately to 100%, and are labelled as model estimates.

### FR-06: Confidence display
The result must show an uncertainty/confidence view. The first MVP may use model confidence from softmax probabilities or variation across test-time augmentations/Monte Carlo dropout.

**Acceptance:** The app clearly labels high-, medium-, and low-confidence regions and does not describe confidence as ground truth.

### FR-07: Comparison experience
The user must be able to compare input and output via a slider and toggle the confidence layer.

**Acceptance:** The primary result is usable at a 360 px-wide phone viewport.

### FR-08: Evaluation panel
For curated test scenes, show at least:
- Structural Similarity Index (SSIM) or a clearly named structural proxy;
- edge/structure preservation score;
- inference time;
- dataset split and model version.

**Acceptance:** Metrics are generated from a held-out evaluation split, not invented values.

### FR-09: Download/export
The app must allow a user to download:
- the output PNG;
- a JSON summary containing model version, timestamp, feature estimates, and confidence summary.

### FR-10: Limitations and privacy notice
A visible notice must state that the output is an AI-estimated interpretation, not an official map or true-colour reconstruction. Uploaded files should be processed in memory and not persisted by default.

---

## 8. Non-functional requirements

| Area | Requirement |
|---|---|
| Cost | All MVP libraries, datasets, and model operations must be free/open-source or use permitted free access. |
| Reliability | Demo gallery and locally stored model must work even if public internet is unavailable. |
| Performance | Target under 10 seconds for a prepared `256 × 256` scene on CPU; report actual observed inference time. |
| Mobile | Result screens must work on a modern Android/Chrome phone at 360 px width. |
| Accessibility | Buttons must have text labels; colour should not be the only way confidence is communicated. |
| Safety | No operational disaster directives; clear uncertainty and limitation language. |
| Privacy | No user account; do not permanently store uploads or location metadata in MVP. |

---

## 9. Success measures

### Hackathon success
- A judge can run a sample in under one minute.
- The team can explain the SAR → model → confidence-output pipeline in under 45 seconds.
- The model beats a simple non-ML pseudocolour baseline on at least one measured structural metric or a clearly stated qualitative evaluation.
- Four curated scenes produce stable, visually useful results.
- Every claim on slides matches measured model results.

### Product success
- Users correctly identify the intended dominant feature class in a small internal test using the output more often than using raw SAR alone.
- Users understand that red/low-confidence areas require verification.

---

## 10. Scope prioritization

### Must-have
- Curated SAR demo images
- Trained lightweight colourization model
- Web UI with upload/gallery
- Input/output comparison slider
- Confidence view
- Feature cards
- Evaluation metrics on held-out samples
- Mobile-responsive layout
- Local demo mode

### Should-have
- PNG + JSON export
- Basic image-history panel (current browser session only)
- Odisha coastal/cyclone scenario page

### Could-have
- GeoTIFF input through `rasterio`
- Map overlay for curated georeferenced sample
- Before/after change comparison
- Optional online frontend deployment

### Will not build in this hackathon
- Live Sentinel API ingestion
- Full GIS vector export
- A large GAN/diffusion/transformer pipeline
- Native Android app

---

## 11. Milestones — 3-day plan

### Day 1: Data and model baseline
- Select/licence-check paired SAR and optical image patches.
- Establish preprocessing and train/validate a compact U-Net or ResU-Net baseline.
- Save checkpoint, test outputs, and generate baseline metrics.

### Day 2: Product integration
- Build API endpoints and inference service.
- Build responsive UI, sample gallery, comparison slider, result cards, and confidence layer.
- Integrate four verified demo scenes.

### Day 3: Evidence and presentation
- Run held-out evaluation and document actual results.
- Test laptop-local and phone-on-LAN workflow.
- Prepare demo script, model card, data card, architecture diagram, PPT, and fallback screenshots/video.

---

## 12. Risks and mitigations

| Risk | Mitigation |
|---|---|
| Outputs look attractive but are geographically misleading | Present output as estimated interpretation; show uncertainty; validate against held-out paired data. |
| GAN training is unstable | Use a compact supervised U-Net/ResU-Net baseline first; add adversarial loss only after baseline works. |
| Dataset download/processing is too large | Curate a documented small patch subset before integration. |
| Free GPU access unavailable | Train a smaller model; save weights; demo CPU inference locally. |
| Uploaded SAR formats vary | Support only documented image formats in MVP; use curated gallery as reliable fallback. |
| Judges ask whether colours are “real” | State the limitation clearly and point to confidence/structure preservation. |
| Internet fails | Bundle model, sample scenes, frontend build, and backend on the laptop. |

---

## 13. Approval

This PRD defines the **hackathon MVP**. Features outside the Must-have scope require explicit approval only after the end-to-end baseline is working.
