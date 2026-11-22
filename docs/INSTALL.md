# Installation and local demo

## Presentation-aligned Streamlit UI

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-ui.txt
bash scripts/run_streamlit.sh
```

Open `http://localhost:8501` or use the laptop's LAN IP on the same Wi-Fi. This is the UI named in the attached deck. For a trained checkpoint, install compatible PyTorch CPU/GPU wheels separately; no checkpoint is bundled.


## Requirements

- Python 3.10 or 3.11
- Node.js 18+ and npm
- A laptop and (optional) a phone on the same Wi-Fi

## First-time setup

```bash
# from the repository root
python3 -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install -r backend/requirements.txt

cd frontend
npm install
npm run build                        # creates frontend/dist, served by FastAPI
cd ..
```

Regenerate the synthetic demo scenes only if needed:

```bash
.venv/bin/python scripts/generate_demo_scenes.py
```

## Run

```bash
bash scripts/run_local.sh
```

The script binds Uvicorn to `0.0.0.0:8000`, prints the laptop LAN IP and opens a single app at:

- Laptop: `http://localhost:8000`
- Phone on same Wi-Fi: `http://<printed-LAN-IP>:8000`
- API docs: `http://localhost:8000/docs`

Stop with `Ctrl+C`.

## Frontend development mode (optional)

For hot reload, run the API and Vite separately:

```bash
# terminal 1
VYORA_MODE=development .venv/bin/python -m uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port 8000

# terminal 2
cd frontend && npm run dev
```

Vite proxies `/api/*` to `http://127.0.0.1:8000`. This mode is for development; use the built frontend for the final phone demo.

## Inference modes

| Setting | Behaviour |
|---|---|
| `VYORA_MODE=development` (default when no checkpoint) | Deterministic, labelled development fallback; no AI claim |
| `VYORA_MODE=auto` | Uses `backend/checkpoints/vyora_resunet.pt` if the file and PyTorch exist, else development mode |
| `VYORA_MODE=model` | Requires a valid checkpoint and PyTorch; fails over to development mode with a logged reason if unavailable |

Check `GET /api/health` to confirm `mode`, `model_version` and `is_ai_inference`.

## Adding a trained model (later)

```bash
pip install torch --index-url https://download.pytorch.org/whl/cpu
python -m ml.src.train --config ml/configs/train_default.json
```

Then restart the server; `auto` mode will load the checkpoint. Do not claim accuracy until `python -m ml.src.evaluate` has been run on a held-out manifest.

## Troubleshooting

| Symptom | Fix |
|---|---|
| `/api/health` unreachable | Start the backend; check port 8000 is free |
| Phone shows blank page | Use the LAN IP, not `localhost`; check firewall; confirm frontend was built |
| Gallery images missing | Run the demo scene generator; check `data/manifests/demo_scenes.json` |
| `npm run build` type errors | Ensure `npm install` completed and Node 18+ is used |
| Mode says development unexpectedly | No checkpoint / no torch / `VYORA_MODE=development`; check health `runner_note` |
