# Final B→A PNG training run (after code merge)

This runbook is for the existing grayscale paired-PNG prototype only. It does not create a genuine Sentinel-1 VV/VH model. The user's dataset stays in OneDrive; do not move or upload it.

## Before training

1. Pull/merge the code update into the Windows clone.
2. Activate the same Python environment used for the earlier run. Confirm PyTorch works with `python -c "import torch; print(torch.__version__)"`.
3. Keep the old known-good checkpoint safe. Train a **candidate** to a new filename; do not overwrite the existing model during experimentation.
4. Regenerate the local manifest with `--input-side B`, using the user's existing OneDrive archive path. The source/licence note must reflect the actual downloaded package, not an assumed SEN12MS licence.
5. Inspect at least one paired tile. Confirm grayscale B is the input and A is the intended colour-bearing target. If the green reference/source seems wrong, stop before training.

## Candidate training

Use the already-approved small-run limits if remaining on CPU. The previous 1,000-train / 200-validation / 5-epoch CPU run took over 30 minutes; a rerun is not guaranteed to improve output. Do not resume the old reversed A→B checkpoint.

```powershell
python -m ml.src.train --config ml/configs/train_default.json --epochs 5 --max-train-tiles 1000 --max-validation-tiles 200 --output-checkpoint backend/checkpoints/vyora_resunet_b_to_a_candidate.pt
```

The trainer now stores a repository-relative manifest reference or only `external:<filename>` in checkpoint metadata, not the OneDrive absolute path.

## Evaluate and decide

```powershell
python -m ml.src.evaluate --manifest data/manifests/tiles.json --checkpoint backend/checkpoints/vyora_resunet_b_to_a_candidate.pt --max-test-tiles 200 --seed 42 --output docs/evaluation_results_b_to_a_candidate.json --examples-dir docs/evaluation_examples_b_to_a_candidate
```

Inspect the metrics and target/prediction/error panels. Do not tune on the test subset. Promote the candidate only if validation results and visual checks support it; otherwise keep the existing checkpoint. Record that this test subset has already been used for prior evaluation and is not fresh independent evidence.

## Final smoke check

Point the app to the selected checkpoint with `VYORA_CHECKPOINT`, restart FastAPI, and check `/api/health`. It must report model mode, `is_ai_inference=true`, and the expected B→A version. Upload a grayscale PNG tile; verify the API rejects a VV/VH GeoTIFF with this PNG checkpoint. Confirm PNG and JSON downloads.

Before publishing a replacement checkpoint, verify its metadata has no workstation path and verify the data license/redistribution terms. Do not add the raw imagery or manifest to Git.
