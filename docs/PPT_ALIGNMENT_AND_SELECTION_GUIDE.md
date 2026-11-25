# Problem-statement / presentation alignment

**Scope reference:** HK26-PS-19, “Deep Learning-Based SAR Image Colorization & Geospatial Visual Interpretation.” The source slide PDF is not stored in this repository, so the slide-by-slide table below is based on the deck claims recorded in this document and must be checked against the final submitted PDF.

## Honest current product

Vyora now has a trained **B→A paired-PNG ResU-Net prototype** and a React/Vite + FastAPI local app. A sampled folder audit found B grayscale and A mostly colour-bearing; this is not proof that B is Sentinel-1 VV/VH or A is Sentinel-2. The checkpoint duplicates one grayscale PNG channel into two model inputs. It is **not a trained dual-polarization SAR model** and is not compatible with true VV/VH GeoTIFF inference.

The user has reported seeing green output locally. The recorded 200-tile evaluation still reports prediction RGB spread `0.03778` versus target `0.13053`; describe the result as an early prototype and show examples honestly. Do not claim that one green-looking tile establishes true-colour recovery or geographic accuracy.

## Requirement status

| Requirement / feature | Status | Evidence or remaining limit |
|---|---|---|
| Trained image-to-image model | **Implemented for PNG prototype** | `backend/checkpoints/vyora_resunet_b_to_a.pt`; 5-epoch CPU run; see `docs/MODEL_CARD.md` and `docs/EVALUATION.md` |
| Paired test comparison and simple baseline | **Implemented, limited evidence** | 200 of 4,576 PNG test tiles, seed 42; geographic separation not independently verified |
| React web interface and local FastAPI inference | **Implemented** | React/Vite + FastAPI; this is the accepted live UI in the repo |
| Upload, input/output comparison, flip consistency | **Implemented** | PNG prototype only; flip-view agreement is not calibrated confidence |
| PNG + JSON export | **Implemented** | GeoTIFF export code is for georeferenced GeoTIFF inputs, not this PNG checkpoint |
| Input validation, memory-only upload processing | **Implemented** | API validation and in-memory result cache with TTL; automated tests cover malformed/oversized uploads |
| Four real, curated geospatial demo scenes | **Not implemented** | Bundled scenes are synthetic interface previews; React hides them for the PNG checkpoint rather than passing them off as real satellite data |
| Genuine Sentinel-1 VV/VH → Sentinel-2 visible model | **Not implemented** | GeoTIFF data/training pipeline exists, but no compatible VV/VH-trained checkpoint or independently verified paired source is available here |
| Land-cover class predictions (water/vegetation/buildings) | **Not implemented** | No class labels/head. The B→A checkpoint predicts pixels only; do not show fabricated class probabilities |
| Calibrated uncertainty | **Not implemented** | UI offers only original-vs-flipped prediction consistency |
| Geographic holdout / generalization evidence | **Not established** | The PNG folder split's geographic independence was not verified |
| 360px phone / no-internet demo | **Code ready, manual verification pending** | Responsive layout and local assets exist; confirm on the actual phone/laptop and record it in `docs/TEST_CHECKLIST.md` |
| Streamlit as the presentation UI | **Scope deviation** | `streamlit_app.py` exists as an alternate; React/Vite is the accepted interface. If the final deck explicitly says Streamlit, update that slide or make a deliberate UI choice before judging |
| Event Team ID / names / slide placeholders | **Manual check required** | Actual PDF and official registration details are not in this checkout; verify every title/team slide against the event portal |

## Deck-to-repository map

| Deck section | What can be shown now | What must not be overstated |
|---|---|---|
| Problem and intended users | SAR-like grayscale imagery can be difficult to scan; this is a local prototype | User benefit, response speed, and operational impact have not been measured |
| Method / AI | B→A paired-PNG ResU-Net, trained locally; code includes a separate two-band GeoTIFF data path | Do not call the current PNG model VV/VH, calibrated SAR, Sentinel-2, or a geospatial model |
| Live UI | Upload a paired grayscale PNG, run the checkpoint, compare input/output, view flip consistency, export PNG/JSON | Do not present synthetic previews as real imagery or consistency as accuracy/confidence |
| Evidence | On the reported subset, model MAE/SSIM beat the simple pseudocolour baseline | Test is limited to 200 tiles; geographic separation and source semantics remain unverified; output is under-coloured on average |
| Future / limitations | Describe validated VV/VH training, geographic holdout, class labels and expert review as next milestones | Do not imply those milestones are complete |
| Team / title | Use PS code HK26-PS-19 | Fill/verify official Team ID, member spelling, IDs and any placeholders manually |

## High-priority remaining work

1. Verify the exact source/archive name, terms, attribution, and what A/B actually represent. Keep the 34 GB archive and local manifest out of Git.
2. After the code changes are merged, perform the planned final B→A training run only if the verified local data/manifest is still the intended prototype task; evaluate the unchanged held-out split and inspect failures before replacing the checkpoint.
3. Before making the deck's central VV/VH claim, prepare a verified, licensed, co-registered Sentinel-1/Sentinel-2 dataset, train a separate 2-channel VV/VH checkpoint, and evaluate by geographically separate scenes. This is a distinct model/data milestone, not a quick patch to the PNG checkpoint.
4. Decide whether the final deck should describe the React app or the alternate Streamlit app. Do not claim both as the same judging interface.
5. Complete real-device phone/offline rehearsal and fill event/team placeholders.

## Safe 20-second explanation

“Vyora is a local image-to-image prototype. The checkpoint we can demonstrate today maps a grayscale paired PNG to an estimated colour-bearing paired image. We have a limited 200-tile comparison against a simple baseline, but the data source semantics and geographic independence are not verified. This is not yet a validated Sentinel-1 VV/VH to Sentinel-2 product, and the output is not ground truth.”
