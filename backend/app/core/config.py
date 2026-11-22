"""Central configuration for the Vyora inference service."""
from __future__ import annotations

import os
from pathlib import Path

# Repository layout: backend/app/core/config.py -> repo root is three levels up.
REPO_ROOT = Path(__file__).resolve().parents[3]
BACKEND_DIR = REPO_ROOT / "backend"
DATA_DIR = REPO_ROOT / "data"
DEMO_DIR = DATA_DIR / "demo_samples"
MANIFEST_PATH = DATA_DIR / "manifests" / "demo_scenes.json"
CHECKPOINT_PATH = Path(
    os.getenv("VYORA_CHECKPOINT", str(BACKEND_DIR / "checkpoints" / "vyora_resunet.pt"))
)
FRONTEND_DIST = REPO_ROOT / "frontend" / "dist"

TILE_SIZE = 256
MAX_UPLOAD_MB = 50
MAX_UPLOAD_BYTES = MAX_UPLOAD_MB * 1024 * 1024
MAX_IMAGE_PIXELS = 40_000_000  # decompression-bomb guard

# auto | development | model
MODE = os.getenv("VYORA_MODE", "auto").strip().lower()
RESULT_TTL_SECONDS = 15 * 60
MAX_CACHED_RESULTS = 40

ALLOWED_CONTENT_TYPES = {"image/png", "image/jpeg", "image/tiff", "application/geotiff"}

FEATURE_LABELS = ("water", "vegetation", "built_up", "bare_other")

DISCLAIMER = (
    "AI-estimated / heuristic geographic interpretation for first-look demonstration only. "
    "Not true-colour ground truth, not an official map, and not a disaster-warning system."
)
