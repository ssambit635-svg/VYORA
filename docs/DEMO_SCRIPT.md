# Vyora hackathon demo script (2–3 minutes)

## Before the room

- Start the FastAPI backend and React/Vite frontend; check the `PNG PROTOTYPE` status and confirm a checkpoint is loaded.
- Keep one 256×256 A-side PNG ready. Do not use a B-side target as the model input.
- Turn the consistency layer **off** initially so the judge sees the model estimate, not the green agreement overlay.
- Have `docs/EVALUATION.md` open for the exact test-subset evidence and caveats.

## Talk track

**Problem (20 sec):** “Radar imagery is powerful but difficult to read visually. We built a local prototype that learns an image-to-image mapping from paired A/B tiles.”

**Method (30 sec):** “This version takes a grayscale A-side PNG, duplicates it into two model channels, and predicts RGB-style pixels. It is not yet a verified Sentinel-1 VV/VH or map-coordinate workflow.”

**Demo (45 sec):** Upload the A-side tile, run inference, and move the slider between input and estimate. Toggle the consistency layer to show prediction stability under a flip; explain that stability is not confidence or accuracy. Download the PNG and JSON if asked.

**Evidence (30 sec):** “On a 200-tile subset of the supplied test split, the ResU-Net scored MAE 0.155, PSNR 15.73 dB and SSIM 0.446, compared with a simple pseudocolour baseline at MAE 0.226 and SSIM 0.241. This is similarity to paired PNG targets—not proof of true-colour recovery or geographic correctness. The folder split's geographic independence is unverified.”

**Limits and next step (20 sec):** “The checkpoint was trained on 1,000 tiles for five CPU epochs, so its colours can be muted. Our next validation step is to compare model predictions with the paired B-side references, fine-tune without touching the test set, and only keep a new model if held-out results improve.”

## If something fails

Say clearly that the local prototype is unavailable rather than presenting a screenshot as live inference. Do not claim that a synthetic scene or a consistency percentage is model accuracy.
