"""Metrics that are actually computed on the processed image.

These are NOT held-out accuracy metrics. The only numbers shown in the UI are:
  * measured wall-clock inference time;
  * an input-to-output edge-agreement proxy (computed from the two arrays);
  * confidence distribution over the produced confidence map.
Held-out MAE/SSIM against paired optical references live in docs/EVALUATION.md
and are reported only when a real evaluation has been run.
"""
from __future__ import annotations

import numpy as np


def _sobel_magnitude(arr: np.ndarray) -> np.ndarray:
    gy, gx = np.gradient(arr.astype(np.float32))
    return np.sqrt(gx * gx + gy * gy)


def edge_agreement(input_tile: np.ndarray, colour: np.ndarray) -> float:
    """Pearson correlation of log edge magnitudes, clipped to [0, 1].

    This measures whether the output kept the *structure* of the input. It does
    not measure colour accuracy, class correctness or geographic truth.
    """
    src = np.log1p(_sobel_magnitude(input_tile) * 8.0)
    grey = np.asarray(colour, dtype=np.float32).mean(axis=2) / 255.0
    dst = np.log1p(_sobel_magnitude(grey) * 8.0)
    a = src - src.mean()
    b = dst - dst.mean()
    denom = float(np.sqrt((a * a).sum() * (b * b).sum()))
    if denom == 0.0:
        return 0.0
    return float(np.clip((a * b).sum() / denom, 0.0, 1.0))


def confidence_summary(confidence: np.ndarray) -> dict:
    c = np.asarray(confidence, dtype=np.float32)
    return {
        "mean": round(float(c.mean()), 4),
        "low_pct": round(float((c < 0.45).mean()) * 100, 2),
        "medium_pct": round(float(((c >= 0.45) & (c < 0.70)).mean()) * 100, 2),
        "high_pct": round(float((c >= 0.70).mean()) * 100, 2),
        "level": "high" if c.mean() >= 0.70 else "medium" if c.mean() >= 0.45 else "low",
        "method_note": "Ranges describe the displayed consistency map, not real-world certainty.",
    }
