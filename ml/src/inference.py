"""Run a trained VV/VH checkpoint on GeoTIFF or a grayscale preview."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "backend"))

from app.core.geospatial import decode_sar, geotiff_bytes, preprocess_pair  # noqa: E402
from app.ml.model_runner import CheckpointRunner  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", required=True, help="2-band VV/VH GeoTIFF, or a labelled grayscale preview")
    parser.add_argument("--checkpoint", default=str(ROOT / "backend" / "checkpoints" / "vyora_resunet.pt"))
    parser.add_argument("--output", default="ml_output.png")
    args = parser.parse_args()
    checkpoint = Path(args.checkpoint)
    if not checkpoint.is_file():
        raise SystemExit(f"No checkpoint at {checkpoint}. Train a model first; development mode is not ML inference.")
    payload = Path(args.image).read_bytes()
    decoded = decode_sar(payload, Path(args.image).name)
    result = CheckpointRunner(checkpoint).infer(preprocess_pair(decoded.channels))
    output = Path(args.output)
    if decoded.profile and output.suffix.lower() in {".tif", ".tiff"}:
        output.write_bytes(geotiff_bytes(result.colour, decoded.profile))
    else:
        Image.fromarray(result.colour, mode="RGB").save(output)
    print(json.dumps({
        "mode": result.mode, "model_version": result.model_version,
        "is_ai_inference": result.is_ai_inference,
        "input_kind": decoded.input_kind, "crs": decoded.crs,
        "feature_estimates": result.feature_estimates,
        "confidence_method": result.confidence_method, "output": str(output),
    }, indent=2))


if __name__ == "__main__":
    main()
