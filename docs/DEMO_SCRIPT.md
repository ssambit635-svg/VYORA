# Vyora hackathon demo script (2–3 minutes)

## Before the room

- Start the FastAPI backend and React/Vite frontend.
- **Do not present the legacy checkpoint as colourization:** it was trained A→B, while the folder audit found B grayscale and A colour-bearing.
- For a corrected demo, first regenerate the manifest B→A, verify one pair with `scripts/inspect_png_pair.py`, train a new checkpoint and inspect held-out panels. The new checkpoint must actually be selected by the API before the demo.
- Keep one verified grayscale input PNG ready and have `docs/EVALUATION.md` open. Do not imply that PNGs have map coordinates or verified VV/VH channels.

## Talk track after a corrected checkpoint is validated

**Problem (20 sec):** “Radar-like grayscale imagery can be hard to scan. We are testing whether paired image learning can produce a useful colour-style visual aid.”

**Method (30 sec):** “In this experiment, B is the grayscale input and A is the colour-bearing paired target, based on our folder audit. These are PNGs, so this does not verify sensor identity, VV/VH channels or geospatial coordinates.”

**Demo (45 sec):** Upload the verified grayscale input, run inference, and move the slider between input and estimate. Toggle the consistency layer to show prediction stability under a flip; explain that stability is not confidence or accuracy. Download the PNG and JSON if asked.

**Evidence (30 sec):** Show only the corrected checkpoint's report, with its split, hardware, target references and failure examples. The earlier 200-tile report used the reversed direction and is not a colourization benchmark.

**Limits (20 sec):** “This is an early visual estimate, not true-colour recovery, a map, land-cover classification or an emergency warning. We need better data provenance, geographic holdout and expert validation.”

## If corrected training is not complete

Present the app as a **pipeline demonstration only**, not as a successful colorization result. Show the folder audit and explain that the old checkpoint was trained in the wrong direction. Do not hide this by toggling or recolouring the output.
