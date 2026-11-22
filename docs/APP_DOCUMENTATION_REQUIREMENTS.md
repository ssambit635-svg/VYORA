> **Project note (21 Nov 2026):** this specification was written under the working name **DrishtiSAR**. The repository product is now branded **VYORA**; read every reference to DrishtiSAR below as Vyora. The problem statement (HK26-PS-19) and requirements are unchanged. Implementation status and any deviations are recorded in [IMPLEMENTATION_DECISIONS.md](IMPLEMENTATION_DECISIONS.md).

# DrishtiSAR — Application Documentation Requirements

> **Vyora deck scope (21 Nov 2026):** the team presentation supersedes older single-channel suggestions below: prepared Sentinel-1 VV/VH GeoTIFF input, paired Sentinel-2 visible RGB target, compact 2→3 channel U-Net, geographic scene-group holdout, Streamlit interface, and CRS/extent-aware preview export. See `PPT_ALIGNMENT_AND_SELECTION_GUIDE.md` for status, caveats and judge-facing wording.

This document defines the documents and evidence required for a credible hackathon submission. The goal is not to create paperwork for its own sake; it is to ensure the team can prove that DrishtiSAR is a real, responsible AI/ML prototype.

---

## 1. Documentation package checklist

| Priority | File / artifact | Required purpose | Owner |
|---|---|---|---|
| Must | `README.md` | Let a judge run and understand the project quickly | Team lead |
| Must | `docs/PRD.md` | Define scope, user needs, goals, and non-goals | Product/pitch owner |
| Must | `docs/PROJECT_DETAILS.md` | Explain problem, solution, architecture, impact, and limitations | Product/pitch owner |
| Must | `docs/TECH_STACK.md` | Explain implementation decisions and local demo setup | Full-stack owner |
| Must | `docs/ARCHITECTURE.md` | One visual/data-flow diagram | Full-stack owner |
| Must | `docs/MODEL_CARD.md` | Make ML model transparent and reproducible | ML owner |
| Must | `docs/DATA_CARD.md` | Describe data provenance, licence, splits, and preprocessing | ML/data owner |
| Must | `docs/EVALUATION.md` | Report actual held-out metrics and baselines | ML owner |
| Must | `docs/API.md` | Describe frontend/backend integration and API examples | Backend owner |
| Must | `docs/DEMO_SCRIPT.md` | Ensure a reliable 3–5 minute demo | Presenter |
| Must | `docs/TEST_CHECKLIST.md` | Prevent demo-time failures | QA owner |
| Must | `LICENSES_AND_ATTRIBUTION.md` | Credit datasets, libraries, imagery, and icons | Team lead |
| Should | `INSTALL.md` | Step-by-step local setup for judges | Full-stack owner |
| Should | `PITCH_OUTLINE.md` | Slide sequence and speaking points | Presenter |
| Should | `assets/demo-video.mp4` | Backup if live demo fails | Presenter |
| Should | `assets/screenshots/` | Evidence for presentation and repository | Designer |

---

## 2. README requirements

The root README must be short enough for a judge to scan in two minutes.

### Required README sections

```markdown
# DrishtiSAR
One-line project statement

## Problem
Why raw SAR imagery is hard to interpret.

## Solution
What the application does, including confidence-aware output.

## Key features
- SAR-to-colour interpretation
- confidence overlay
- feature estimates
- local, phone-accessible demo

## Quick start
Exact commands to install and run frontend/backend.

## Demo
Screenshots/GIF and the preferred demo scene.

## Architecture
Link to architecture diagram.

## Model and data
Links to model card, data card, and evaluation report.

## Limitations
Not true-colour ground truth; not an official disaster-warning system.

## Team and acknowledgements
Names/roles, datasets, software licences.
```

### README acceptance criteria
- A fresh user can identify the value proposition in under 30 seconds.
- A fresh user can start the app using documented commands.
- No metric is shown without a source/evaluation document.
- Every external asset has attribution or is removed.

---

## 3. Model card requirements

Create `docs/MODEL_CARD.md` before final judging.

### Required fields

| Section | What to document |
|---|---|
| Model name/version | Example: `DrishtiSAR ResU-Net v0.1` |
| Task | SAR-to-RGB-style geographic interpretation |
| Input | Sensor assumptions, channel format, preprocessing, image size |
| Output | Three-channel estimate; confidence output; any feature estimates |
| Architecture | U-Net/ResU-Net details, parameters if available |
| Training data | Link to data card; number of scene groups/tiles; split policy |
| Training process | Hardware, epochs, optimizer, loss components, seed if feasible |
| Evaluation | Held-out metrics, baselines, test device for latency |
| Intended use | Educational, rapid first-look interpretation prototype |
| Out-of-scope use | Official mapping, safety-critical decisions, arbitrary unsupported sensors |
| Known limitations | Hallucination risk, domain shift, pair misalignment, confidence limits |
| Ethical/safety notes | Clear disclaimer and need for authoritative verification |

### Model card rule
Never write a result such as “95% accurate” unless the target, test split, metric definition, and calculation are documented.

---

## 4. Data card requirements

Create `docs/DATA_CARD.md` for each dataset or curated combined dataset.

### Required fields

| Section | What to document |
|---|---|
| Dataset name and source URL | Exact source, access date, licence/terms |
| Why it is used | Paired SAR/optical learning and evaluation |
| Data content | Sensor, bands/polarization, resolution, dates/scene types |
| Geographic coverage | Broad regions/scene groups; avoid claiming unverified coverage |
| Pairing method | How SAR and optical images were time/space matched |
| Filtering | Cloud handling, invalid tile removal, alignment checks |
| Preprocessing | Scaling, clipping, resizing, tiling, normalization |
| Split policy | Train/validation/test counts and scene-group separation |
| Data limitations | Seasonal mismatch, clouds, sensor differences, label/target uncertainty |
| Licence/attribution | Terms and required credit |

### Minimum evidence
- Save a CSV/JSON manifest with a unique tile ID, scene group, split, input path, target path, and source reference.
- Do not upload restricted raw imagery to a public repository.

---

## 5. Evaluation report requirements

Create `docs/EVALUATION.md`.

### Required tables

#### Dataset split

| Split | Scene groups | Number of tiles | Notes |
|---|---:|---:|---|
| Train | TBD | TBD | No test-scene overlap |
| Validation | TBD | TBD | Used for model choices |
| Test | TBD | TBD | Held out until final assessment |

#### Model comparison

| Method | MAE/L1 | SSIM | Edge preservation | Median latency | Notes |
|---|---:|---:|---:|---:|---|
| Pseudocolour baseline | TBD | TBD | TBD | TBD | Non-ML comparison |
| DrishtiSAR model | TBD | TBD | TBD | TBD | Held-out result |

### Required visuals
- At least four held-out input/target/output comparison panels.
- One failure/low-confidence example and an honest explanation.
- One confidence-map example.
- One chart or table of inference latency across sample scenes.

### Required language
Use phrases such as:
- “on our held-out curated test set”;
- “estimated colour interpretation”;
- “the confidence layer indicates model consistency/uncertainty.”

Do not use phrases such as:
- “real satellite colours restored”;
- “guaranteed flood map”;
- “works for all SAR imagery.”

---

## 6. Architecture-document requirements

Create `docs/ARCHITECTURE.md` containing one readable diagram and these explanations:

1. Dataset preparation and model training occur before user inference.
2. Browser uploads/chooses image.
3. FastAPI validates and preprocesses it.
4. PyTorch checkpoint creates output/confidence maps.
5. Browser receives output, metrics, and disclaimer.
6. Local-mode networking: laptop hosts the backend; phone connects through same Wi-Fi.

### Diagram rule
A single diagram should be legible in the PPT without tiny text. Use only the important components; do not add decorative cloud services that the prototype does not use.

---

## 7. API-document requirements

Create `docs/API.md`.

For each endpoint, document:
- method and path;
- purpose;
- request parameters;
- success response example;
- error response example;
- whether it writes data to disk;
- file-size/type restrictions.

### Mandatory endpoint evidence
- `/api/health` response screenshot or curl output;
- `/api/demo-scenes` response;
- `/api/infer` request and response example;
- a user-facing unsupported-file error.

---

## 8. Testing document requirements

Create `docs/TEST_CHECKLIST.md`.

### Required tests

| Area | Test |
|---|---|
| Model | Every packaged demo scene produces an output after a clean restart |
| Model | Output values have no NaN/Inf and valid dimensions |
| API | Invalid type, corrupt file, and oversized upload produce clear errors |
| API | Health endpoint fails clearly if model checkpoint is absent |
| UI | Demo works at desktop and Android/Chrome phone widths |
| UI | Slider and confidence toggle are touch usable |
| UI | Disclaimer remains visible on result screen |
| Local demo | Works with internet disabled after assets/models are bundled |
| Export | Output PNG and JSON download correctly |
| Pitch | Each team member can explain limitations and metrics |

Record date, tester, device/browser, pass/fail, and bug notes.

---

## 9. Demo-script requirements

Create `docs/DEMO_SCRIPT.md` with a timed 3–5 minute script.

### Required sequence
1. Problem: raw SAR is valuable but hard to read.
2. Stakeholder: disaster/land analyst needs a fast first look.
3. Solution: DrishtiSAR estimates colour and makes uncertainty visible.
4. Demo: select known coastal sample; run inference; use comparison slider.
5. Explain: show confidence map and feature estimates.
6. Evidence: show held-out metrics and baseline comparison.
7. Responsibility: state that it is not true-colour ground truth or an official warning product.
8. Close: explain scale-up path—more validated data, more sensor-specific models, expert evaluation.

### Backup plan
- Pre-record 30–60 second screen capture.
- Keep screenshots of all primary screens in presentation.
- Pack model and sample scenes locally.

---

## 10. Presentation evidence checklist

The slide deck must include:

- [ ] Problem statement ID and concise interpretation
- [ ] Why SAR is difficult for non-specialists
- [ ] User/use-case narrative
- [ ] System architecture diagram
- [ ] Model diagram and real data flow
- [ ] Data sources/licences at a readable level
- [ ] Output comparison slider screenshot
- [ ] Confidence/uncertainty explanation
- [ ] Held-out metric table, baseline comparison, and latency
- [ ] One known failure/limitation
- [ ] Zero-cost and local-demo story
- [ ] Roadmap

---

## 11. Final submission gate

Do not mark the project submission-ready until every statement below is true:

- [ ] The app runs from a fresh laptop setup using the documentation.
- [ ] The team has one working model checkpoint and a known fallback checkpoint.
- [ ] The four demo scenes are locally packaged and source-attributed.
- [ ] Reported numbers come from saved evaluation outputs.
- [ ] The app never describes an AI estimate as verified true-colour imagery.
- [ ] Local phone demonstration has been tested on a real phone.
- [ ] A backup demo video and screenshots exist.
- [ ] The README tells a judge exactly how to run the project.
- [ ] Dataset, library, image, and icon licences are acknowledged.
- [ ] Every team member can explain the model, confidence layer, limitations, and their own contribution.
