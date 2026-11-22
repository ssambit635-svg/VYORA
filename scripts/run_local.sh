#!/usr/bin/env bash
# Start the complete Vyora demo on one port. Laptop + phones on the same Wi-Fi.
set -euo pipefail
cd "$(dirname "$0")/.."

PY="${PYTHON:-.venv/bin/python}"
if [[ ! -x "$PY" ]]; then PY="python3"; fi

if ! "$PY" -c 'import fastapi, uvicorn, PIL, numpy' >/dev/null 2>&1; then
  echo "Missing Python dependencies. Run: pip install -r backend/requirements.txt" >&2
  exit 1
fi

if [[ ! -f frontend/dist/index.html ]]; then
  echo "Building frontend (one time)..."
  npm --prefix frontend run build
fi

LAN_IP="$(hostname -I 2>/dev/null | awk '{print $1}')"
PORT="${PORT:-8000}"
echo "Vyora ready:"
echo "  laptop: http://localhost:${PORT}"
echo "  phone:  http://${LAN_IP:-<laptop-LAN-IP>}:${PORT}  (same Wi-Fi)"
echo "  API:    http://localhost:${PORT}/docs"
echo "Press Ctrl+C to stop."

export VYORA_MODE="${VYORA_MODE:-auto}"
exec "$PY" -m uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port "$PORT"
