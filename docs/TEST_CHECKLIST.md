# Test checklist

Record manual checks as: date / tester / environment / result / notes.

## Automated verification in this workspace (21 Nov 2026)

| Test | Result | Notes |
|---|---|---|
| `python -m py_compile ml/src/train.py ml/src/evaluate.py backend/app/ml/model_runner.py backend/app/api/routes.py streamlit_app.py` | **PASS** | Syntax check for edited Python modules |
| `.venv/bin/python -m pytest backend/tests ml/tests -q` | **31 passed, 1 skipped** | Includes API validation, synthetic GeoTIFF CRS/bounds round-trip, PNG/GeoTIFF model-input contract, checkpoint-specific evaluation labeling, private-path sanitization, paired-data/split checks and training/evaluation mechanics |
| `npm run build` | **PASS** | Vite 6.4.6 + TypeScript strict; production bundle built |
| `git diff --check` | **PASS** | No whitespace errors |

The workspace has no PyTorch installation, so this run did **not** load the tracked checkpoint or perform fresh training/inference. The user's earlier Windows health check and training/evaluation are separate reported results. One test is skipped by the existing suite; review test output before merging if skip behavior changes.

## Manual final-demo checks (pending on the user's machine)

| Area | Check | Status | Notes |
|---|---|---|---|
| Checkpoint | After setting `VYORA_CHECKPOINT`, `/api/health` reports model mode, AI inference true, and B→A version | Pending after final training | A development fallback is not a trained result |
| Model | Upload a grayscale paired PNG; check output is finite, 256×256 and visually inspect target/error panels | Pending after final training | Do not use the held-out test set for tuning |
| Input contract | Current PNG checkpoint rejects a true VV/VH GeoTIFF with a clear message | API contract test passes | A separate dual-pol checkpoint is required for VV/VH inference |
| Export | Output PNG/JSON download and inspect | API tests pass; browser check pending | PNG model output has no CRS/transform |
| UI | Desktop then 360px Android/Chrome phone run: upload, slider, consistency toggle, disclaimer | Pending real device | Save date, browser/device and result |
| Offline/LAN | Run app with internet off; then optional phone on same Wi-Fi via laptop LAN IP | Pending | Record firewall/port issues |
| Dataset/legal | Confirm exact archive source, licence/terms, A/B semantics, and permitted checkpoint sharing | Pending | Keep raw imagery/manifest out of Git |
| Final deck | Verify title/team placeholders, PS code, model/input claims, and whether slides say React or Streamlit | Pending manual PDF review | Original PDF is not stored in this checkout |

## Ground-truth and claims guardrails

- The B→A report covers 200 of 4,576 supplied test tiles (seed 42); geographic independence is unverified.
- Average prediction RGB spread in the saved report is 0.03778 vs 0.13053 for the target. A visually green example does not erase the average muted-colour finding.
- Flip consistency is not calibrated uncertainty; the PNG checkpoint has no class head.
- The bundled gallery is synthetic, not real satellite evidence.
