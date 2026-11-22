"""Held-out evaluation for the Vyora baseline.

Only writes a results file when BOTH a validated test manifest and a checkpoint
exist. If either is missing it prints why and writes nothing: no placeholder or
invented numbers are ever produced.

Usage: python -m ml.src.evaluate --manifest data/manifests/tiles.json \
           --checkpoint backend/checkpoints/vyora_resunet.pt
"""
from __future__ import annotations

import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from PIL import Image

from ml.src.data import load_manifest, normalise_sar_pair, optical_target

ROOT = Path(__file__).resolve().parents[2]


def _display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def _gaussian_filter(image: np.ndarray, sigma: float = 1.5, size: int = 11) -> np.ndarray:
    coords = np.arange(size) - (size - 1) / 2
    kernel = np.exp(-(coords ** 2) / (2 * sigma ** 2))
    kernel /= kernel.sum()
    pad = size // 2
    out = image.astype(np.float32).copy()
    for axis in (0, 1):
        pad_width = [(0, 0), (0, 0), (0, 0)]
        pad_width[axis] = (pad, pad)
        padded = np.pad(out, pad_width, mode="reflect")
        smoothed = np.zeros_like(out)
        for k in range(size):
            index = [slice(None), slice(None), slice(None)]
            index[axis] = slice(k, k + out.shape[axis])
            smoothed += kernel[k] * padded[tuple(index)]
        out = smoothed
    return out


def ssim(pred: np.ndarray, target: np.ndarray) -> float:
    c1, c2 = 0.01 ** 2, 0.03 ** 2
    values = []
    for ch in range(3):
        p, t = pred[..., ch, None], target[..., ch, None]
        mp, mt = _gaussian_filter(p), _gaussian_filter(t)
        vp = _gaussian_filter(p * p) - mp * mp
        vt = _gaussian_filter(t * t) - mt * mt
        cov = _gaussian_filter(p * t) - mp * mt
        score = ((2 * mp * mt + c1) * (2 * cov + c2)) / (
            (mp ** 2 + mt ** 2 + c1) * (vp + vt + c2)
        )
        values.append(float(score.mean()))
    return float(np.mean(values))


def edge_preservation(pred: np.ndarray, target: np.ndarray) -> float:
    def edges(x: np.ndarray) -> np.ndarray:
        grey = x.mean(axis=2)
        gy, gx = np.gradient(grey)
        return np.sqrt(gx ** 2 + gy ** 2)

    a, b = np.log1p(edges(pred) * 8).ravel(), np.log1p(edges(target) * 8).ravel()
    denom = np.sqrt(((a - a.mean()) ** 2).sum() * ((b - b.mean()) ** 2).sum())
    return float(np.clip(((a - a.mean()) * (b - b.mean())).sum() / denom, 0, 1)) if denom else 0.0


def pseudocolour_baseline(sar: np.ndarray) -> np.ndarray:
    """Non-ML intensity-to-palette transform used as a documented comparison."""
    palette = np.array([[0.09, 0.42, 0.62], [0.23, 0.61, 0.36], [0.78, 0.69, 0.50], [0.85, 0.55, 0.39]])
    levels = np.clip((sar * 4).astype(int), 0, 3)
    return palette[levels]


def summarise(pairs: list[tuple[np.ndarray, np.ndarray]], predictor) -> dict:
    maes, psnrs, ssims, edge_scores = [], [], [], []
    perfect = 0
    for sar, target in pairs:
        pred = predictor(sar)
        mse = float(np.mean((pred - target) ** 2))
        maes.append(float(np.abs(pred - target).mean()))
        if mse <= 1e-12:
            perfect += 1
        else:
            psnrs.append(10.0 * np.log10(1.0 / mse))
        ssims.append(ssim(pred, target))
        edge_scores.append(edge_preservation(pred, target))
    return {
        "tiles": len(pairs),
        "MAE_L1": round(float(np.mean(maes)), 5),
        "PSNR_dB": round(float(np.mean(psnrs)), 5) if psnrs else None,
        "PSNR_perfect_tiles": perfect,
        "SSIM": round(float(np.mean(ssims)), 5),
        "edge_preservation": round(float(np.mean(edge_scores)), 5),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", default="data/manifests/tiles.json")
    parser.add_argument("--checkpoint", default="backend/checkpoints/vyora_resunet.pt")
    parser.add_argument("--output", default="docs/evaluation_results.json")
    parser.add_argument("--latency-runs", type=int, default=5)
    args = parser.parse_args()

    manifest, checkpoint = ROOT / args.manifest, ROOT / args.checkpoint
    if not manifest.is_file():
        print(f"No evaluation performed: manifest not found at {manifest}.")
        return
    if not checkpoint.is_file():
        print(f"No evaluation performed: checkpoint not found at {checkpoint}.")
        return

    rows = [r for r in load_manifest(manifest) if r["split"] == "test"]
    if not rows:
        print("No evaluation performed: manifest contains no 'test' split tiles.")
        return

    pairs = [(normalise_sar_pair(row), optical_target(row)) for row in rows]
    baseline = summarise(
        [(sar.mean(axis=-1), target) for sar, target in pairs], pseudocolour_baseline
    )

    import torch

    from ml.src.model import build_model

    saved = torch.load(checkpoint, map_location="cpu", weights_only=True)
    model = build_model(int(saved.get("base_channels", 24)), input_channels=int(saved.get("input_channels", 2)))
    model.load_state_dict(saved["state_dict"])
    model.eval()

    def predict(sar: np.ndarray) -> np.ndarray:
        x = torch.from_numpy(np.moveaxis(sar, -1, 0)[None, ...].copy()).float()
        with torch.inference_mode():
            rgb = model(x)
        return rgb[0].permute(1, 2, 0).numpy()

    model_scores = summarise(pairs, predict)
    timings = []
    with torch.inference_mode():
        for sar, _target in pairs[: max(1, args.latency_runs)]:
            x = torch.from_numpy(np.moveaxis(sar, -1, 0)[None, ...].copy()).float()
            start = time.perf_counter()
            model(x)
            timings.append((time.perf_counter() - start) * 1000)
    model_scores["median_latency_ms_cpu"] = round(float(np.median(timings)), 2)

    result = {
        "status": "evaluated",
        "date": datetime.now(timezone.utc).isoformat(),
        "checkpoint": _display_path(checkpoint),
        "manifest": _display_path(manifest),
        "split": "test (geographically separated scene groups)",
        "methods": {
            "pseudocolour_baseline": baseline,
            "resunet_model": model_scores,
        },
        "caveat": "Similarity to paired optical references on a small curated set; not a claim of true-colour reconstruction.",
    }
    output = ROOT / args.output
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
