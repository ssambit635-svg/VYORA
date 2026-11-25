# Vyora hackathon demo script (2–3 minutes)

## Before the room

- Start FastAPI with `VYORA_CHECKPOINT=backend/checkpoints/vyora_resunet_b_to_a.pt` and run the React/Vite frontend.
- Confirm the UI reports model version `resunet-paired-png-prototype-v0.2-b-to-a`.
- Keep a verified grayscale B-side PNG ready. Start with the consistency layer off so judges see the model estimate, not the green agreement overlay.
- Have `docs/EVALUATION.md` open to the 200-tile subset and its caveats.

## Talk track

**Problem (20 sec):** “Radar-like grayscale imagery can be difficult to scan visually. Vyora is a local prototype exploring whether paired image learning can provide a colour-style visual aid.”

**Method (30 sec):** “This checkpoint takes a grayscale B-side PNG, duplicates it into two model channels, and predicts pixels resembling its paired A-side image. The folder statistics suggest this direction, but sensor identity and source semantics are not independently verified.”

**Demo (45 sec):** Upload a grayscale B-side tile, run inference, and move the slider between input and estimate. Toggle the consistency layer briefly to show prediction stability under a flip; explain that stability is not confidence or accuracy. Download the PNG and JSON if asked.

**Evidence (30 sec):** “On 200 of 4,576 supplied test tiles, the model had MAE 0.096 and SSIM 0.671, compared with a simple pseudocolour baseline at MAE 0.354 and SSIM 0.248. The model remains under-coloured: average prediction RGB spread is 0.038 versus 0.131 in the target. Folder-split geographic independence was not verified.”

**Limits (20 sec):** “This is not true-colour recovery, a map, land-cover classification or an emergency warning. PNGs have no map coordinates, and we need verified source semantics, geographic holdout and expert validation.”

## If something fails

Present the app as a pipeline demonstration only; do not present screenshots as live inference. Do not hide muted outputs by enabling the consistency overlay, and do not call any displayed percentage accuracy.
