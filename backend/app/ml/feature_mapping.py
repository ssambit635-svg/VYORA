"""Deterministic development-mode SAR interpretation.

IMPORTANT: this module is a transparency/fallback aid, NOT a trained model and NOT
an AI inference result. It maps backscatter intensity + local texture to a small
set of hand-defined colour palettes using fixed rules. Every response produced
here is labelled ``is_ai_inference = false`` and ``mode = development``.

It exists so the complete product flow (upload -> processing -> comparison ->
confidence -> export) can be demonstrated before a checkpoint is trained.
"""
from __future__ import annotations

import numpy as np

from app.core.config import FEATURE_LABELS

# Representative display colours, in sRGB 0-1. These are illustrative palette
# choices, not measurements of real land cover.
PALETTE = np.array(
    [
        [0.09, 0.42, 0.62],  # water: deep blue-teal
        [0.23, 0.61, 0.36],  # vegetation: green
        [0.85, 0.55, 0.39],  # built-up: warm terracotta
        [0.78, 0.69, 0.50],  # bare / other: sand
    ],
    dtype=np.float32,
)


def _smoothstep(edge0: float, edge1: float, x: np.ndarray) -> np.ndarray:
    t = np.clip((x - edge0) / (edge1 - edge0), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def _box_mean(arr: np.ndarray, radius: int) -> np.ndarray:
    padded = np.pad(arr, radius, mode="reflect")
    integral = np.pad(padded, ((1, 0), (1, 0)), mode="constant").cumsum(0).cumsum(1)
    window = 2 * radius + 1
    h, w = arr.shape
    total = integral[window:, window:] - integral[:-window, window:]
    total -= integral[window:, :-window] - integral[:-window, :-window]
    return total / float(window * window)


def _local_stats(tile: np.ndarray, radius: int = 7) -> tuple[np.ndarray, np.ndarray]:
    mean = _box_mean(tile, radius)
    mean_sq = _box_mean(tile * tile, radius)
    std = np.sqrt(np.maximum(mean_sq - mean * mean, 0.0))
    return mean, std


def feature_memberships(tile: np.ndarray) -> np.ndarray:
    """Return float32 array of shape (4, H, W) with non-negative memberships.

    Rules (documented, fixed, hand-authored):
      water      = low backscatter and low-to-moderate texture
      vegetation = medium backscatter with visible texture
      built_up   = high backscatter with strong texture / bright structures
      bare_other = remaining neutral, low-texture surface
    """
    mean, std = _local_stats(tile)
    texture = np.clip(std / 0.22, 0.0, 1.0)

    water = (1.0 - _smoothstep(0.16, 0.42, mean)) * (1.0 - 0.6 * _smoothstep(0.25, 0.75, texture))
    # Strong texture with mid/high backscatter indicates compact structures.
    built = _smoothstep(0.10, 0.30, texture) * (0.35 + 0.65 * _smoothstep(0.35, 0.65, mean))
    # Fields have mid backscatter and moderate (row-like) texture; very strong
    # texture is attributed to built-up instead.
    vegetation = (
        _smoothstep(0.15, 0.35, mean)
        * (1.0 - _smoothstep(0.55, 0.75, mean))
        * (0.20 + 0.80 * _smoothstep(0.10, 0.30, texture))
        * (1.0 - 0.75 * _smoothstep(0.35, 0.80, texture))
    )
    bare = (1.0 - _smoothstep(0.05, 0.25, texture)) * (
        0.35 + 0.65 * (1.0 - _smoothstep(0.60, 0.90, mean))
    )

    memberships = np.stack([water, vegetation, built, bare]).astype(np.float32)
    memberships = np.maximum(memberships, 1e-4)
    return memberships / memberships.sum(axis=0, keepdims=True)


def interpret(tile: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return (colour RGB uint8, confidence float32 [0,1], memberships [4,H,W])."""
    memberships = feature_memberships(tile)

    # Colour = palette mixture + mild structure-preserving brightness modulation.
    colour = np.einsum("cp,cxy->xyp", PALETTE, memberships)
    _mean, std = _local_stats(tile)
    shading = 0.82 + 0.24 * tile + 0.16 * np.clip(std / 0.25, 0.0, 1.0)
    colour = np.clip(colour * shading[..., None], 0.0, 1.0)
    rgb = np.round(colour * 255.0).astype(np.uint8)

    # Confidence = agreement of the rule-based memberships under horizontal
    # mirroring (a deterministic consistency check, NOT model uncertainty),
    # plus local consistency of the dominant class.
    flipped = feature_memberships(np.ascontiguousarray(tile[:, ::-1]))[:, :, ::-1]
    agreement = np.sum(memberships * flipped, axis=0)
    dominant = np.argmax(memberships, axis=0).astype(np.float32)
    agreement_mask = (np.argmax(flipped, axis=0) == np.argmax(memberships, axis=0)).astype(np.float32)
    local_agreement = _box_mean(agreement_mask, 5)
    del dominant  # kept out of the formula intentionally; only class agreement is used
    confidence = 0.30 + 0.68 * (0.6 * agreement + 0.4 * local_agreement)
    confidence = np.clip(confidence, 0.15, 0.98).astype(np.float32)

    mean_memberships = memberships.mean(axis=(1, 2))
    mean_memberships = mean_memberships / mean_memberships.sum()
    return rgb, confidence, mean_memberships.astype(np.float32)


def confidence_heatmap(confidence: np.ndarray) -> np.ndarray:
    """Map scalar confidence to a red/amber/teal RGB heatmap for display."""
    stops = np.array(
        [
            [0.00, 0.89, 0.34, 0.34],  # low -> red
            [0.50, 0.90, 0.66, 0.23],  # medium -> amber
            [1.00, 0.18, 0.66, 0.54],  # high -> teal
        ],
        dtype=np.float32,
    )
    out = np.zeros((*confidence.shape, 3), dtype=np.float32)
    for channel in range(3):
        out[..., channel] = np.interp(confidence, stops[:, 0], stops[:, 1 + channel])
    return np.round(np.clip(out, 0, 1) * 255).astype(np.uint8)
