#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
PY="${PYTHON:-.venv/bin/python}"
if [[ ! -x "$PY" ]]; then PY="python3"; fi
if ! "$PY" -c 'import streamlit, rasterio, fastapi' >/dev/null 2>&1; then
  echo "Streamlit/model dependencies are missing. Install with: pip install -r requirements-ui.txt" >&2
  exit 1
fi
exec "$PY" -m streamlit run streamlit_app.py --server.address 0.0.0.0 --server.port "${PORT:-8501}" --server.headless true
