# Implementation decisions and current scope

The repository contains two distinct inference paths. Do not merge their claims:

1. **Current demonstrated checkpoint:** grayscale B-side PNG → A-side PNG estimate (`vyora_resunet_b_to_a.pt`). The source semantics are not independently verified.
2. **Geospatial research path:** two-channel VV/VH GeoTIFF → three-channel optical-style target. The manifest, data loader, model architecture, normalization, evaluation and CRS-aware preview code exist, but this path has no compatible trained checkpoint or verified real-data evaluation in the repository.

| Decision | Why | Current state / limitation |
|---|---|---|
| Train a compact ResU-Net | Small, interpretable image-to-image baseline for CPU demo | Trained for 5 CPU epochs on 1,000 paired PNG train tiles; 200 validation tiles; see evaluation report |
| Keep input representation in checkpoint metadata | Prevent accidental use of PNG-trained weights on true VV/VH inputs | API and Streamlit now validate the model/input contract; PNG checkpoint rejects GeoTIFF inference |
| Keep checkpoint metadata portable | Avoid publishing private workstation paths in future checkpoints | Trainer now stores repo-relative manifest references or only an external manifest basename |
| Avoid synthetic/heuristic class claims | No supervised water/vegetation/building masks for the current checkpoint | PNG checkpoint returns no class shares; UI says pixel prediction only |
| Use flip TTA only as a consistency cue | No calibration labels or uncertainty evaluation exist | UI/export explicitly describe prediction stability, not calibrated uncertainty |
| Retain separate GeoTIFF pipeline | Required for a future genuine VV/VH model | Code-level I/O and synthetic round-trip tests exist; current PNG checkpoint cannot run on this input |
| React/Vite + FastAPI is accepted interface | Matches current user choice | Streamlit remains an optional alternate, not the primary live UI |
| Keep uploads in memory | Privacy by default | API stores generated results in a bounded, expiring in-memory cache; does not write uploads to disk |

## Evidence now available

- Corrected B→A training and 200-tile subset evaluation are documented in `docs/EVALUATION.md`.
- Automated backend/ML tests and frontend production build run in the repository; see `docs/TEST_CHECKLIST.md`.
- Real phone/offline rehearsal, source licence/provenance, and geographic split independence remain manual/unverified.

## Remaining work outside a code-only completion

- Verify exact archive source, terms, sensor semantics, and the geographic independence of the PNG folders.
- If the final deliverable must be true VV/VH→optical, acquire/verify paired geospatial data and train/evaluate a **separate** VV/VH checkpoint. Do not repurpose this PNG checkpoint.
- If the presentation lists land-cover probabilities, provide labeled masks and train/evaluate a classification head or revise the claim; the current image-to-image model cannot produce valid classes.
- Verify actual event Team ID/member details and rehearse the app on the presentation laptop and phone.
