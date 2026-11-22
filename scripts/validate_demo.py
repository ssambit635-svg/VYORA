"""Validate every bundled demo scene end to end after a clean start.

No accuracy claims: this only checks that the app returns valid, finite outputs.
Usage: .venv/bin/python scripts/validate_demo.py
"""
from __future__ import annotations

import io
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402


def main() -> int:
    with TestClient(app) as client:
        health = client.get("/api/health").json()
        print(f"mode={health['mode']}  model={health['model_version']}  ai={health['is_ai_inference']}")
        scenes = client.get("/api/demo-scenes").json()["scenes"]
        for scene in scenes:
            response = client.post("/api/infer", data={"demo_scene_id": scene["id"]})
            if response.status_code != 200:
                print(f"FAIL {scene['id']}: {response.text}")
                return 1
            result = response.json()
            colour = np.asarray(Image.open(io.BytesIO(client.get(result["urls"]["colour"]).content)))
            conf = np.asarray(Image.open(io.BytesIO(client.get(result["urls"]["confidence"]).content)), dtype=np.float32)
            shares = result["feature_estimates"]
            ok = (
                colour.shape == (256, 256, 3)
                and conf.shape == (256, 256, 3)
                and np.isfinite(conf).all()
                and abs(sum(shares.values()) - 1) < 1e-3
            )
            print(f"{'PASS' if ok else 'FAIL'} {scene['id']:16s} runtime={result['metrics']['runtime_ms']}ms shares={shares}")
            if not ok:
                return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
