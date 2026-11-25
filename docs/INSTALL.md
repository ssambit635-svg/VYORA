# Install and run Vyora

The current checked-in model is a **B→A paired-PNG prototype**. It is not a trained VV/VH GeoTIFF model. The 34 GB source archive and its manifest remain on the user's machine, not in Git.

## Prerequisites

- Python 3.10 or 3.11
- Node.js 18+ and npm
- For AI inference: a compatible PyTorch CPU/CUDA build. The API requirements file does not install PyTorch automatically.

## First-time setup (PowerShell)

From the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r backend/requirements.txt
python -m pip install torch --index-url https://download.pytorch.org/whl/cpu
cd frontend
npm install
cd ..
```

If PyTorch is already installed in the environment used for the previous training, do not reinstall it. For GPU PyTorch, follow the official install selector for the target machine instead of the CPU command above.

## Run the accepted React + FastAPI UI

Open PowerShell window 1 at the repository root:

```powershell
$env:VYORA_CHECKPOINT = "$PWD\backend\checkpoints\vyora_resunet_b_to_a.pt"
$env:VYORA_MODE = "auto"
python -m uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port 8000
```

Open PowerShell window 2:

```powershell
cd frontend
npm run dev -- --host 0.0.0.0
```

Open the Vite URL, usually `http://localhost:5173`. Keep both windows open. Check `http://localhost:8000/api/health` before the demo: it must say `mode: model`, `is_ai_inference: true`, and the B→A prototype model version. If it reports development mode, do not describe that request as AI inference.

The current checkpoint accepts grayscale PNG input only. A PNG result has no CRS/map coordinates. The server intentionally rejects a VV/VH GeoTIFF when this checkpoint is loaded.

## Optional built, one-port app

After building the frontend once:

```powershell
cd frontend
npm run build
cd ..
$env:VYORA_CHECKPOINT = "$PWD\backend\checkpoints\vyora_resunet_b_to_a.pt"
python -m uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port 8000
```

Then use `http://localhost:8000`. For a phone on the same Wi-Fi, use the laptop's LAN IP instead of `localhost`, allow the private-network firewall prompt, and keep both devices on that Wi-Fi.

## Optional Streamlit interface

`streamlit_app.py` is retained as an alternate interface. React/Vite remains the accepted primary UI. With Streamlit installed:

```powershell
$env:VYORA_CHECKPOINT = "$PWD\backend\checkpoints\vyora_resunet_b_to_a.pt"
python -m streamlit run streamlit_app.py --server.address 0.0.0.0 --server.port 8501
```

The current PNG checkpoint will only offer grayscale PNG input. A VV/VH-trained checkpoint is required before selecting a GeoTIFF input for AI inference.

## Checkpoint selection

If `VYORA_CHECKPOINT` is unset, the application defaults to `backend/checkpoints/vyora_resunet_b_to_a.pt`. Set the variable explicitly as shown above to make the demo choice unambiguous. To inspect the legacy A→B model, set it to `backend/checkpoints/vyora_resunet.pt` deliberately; do not use that checkpoint as colourization evidence. `VYORA_MODE=development` forces the hand-authored fallback; it is not trained AI. `VYORA_MODE=auto` loads a compatible checkpoint when PyTorch is available.

## Troubleshooting

| Symptom | Check |
|---|---|
| Health says `development` | Confirm the active Python environment has PyTorch, `VYORA_CHECKPOINT` points to the B→A file, and `VYORA_MODE` is not `development`; restart after changing environment variables |
| GeoTIFF rejected | Expected for the PNG checkpoint. A separately trained VV/VH checkpoint is needed |
| Vite cannot reach the API | Keep FastAPI running on port 8000; the Vite proxy uses the same machine's backend in local dev |
| Phone cannot open app | Use the laptop LAN IP, not `localhost`; check same Wi-Fi and firewall |
| Missing sample gallery | Bundled gallery scenes are synthetic UI previews, not real satellite evidence |
