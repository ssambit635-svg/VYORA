"""Generate deterministic SYNTHETIC SAR-like demo scenes.

These images are procedurally created illustrations of radar backscatter patterns.
They are NOT real SAR imagery, NOT georeferenced, and MUST be labelled as
synthetic in the UI and documentation. Replace them with licensed, aligned real
SAR scenes (and update the manifest) for a real model evaluation.

Usage: python scripts/generate_demo_scenes.py
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "demo_samples"
MANIFEST = ROOT / "data" / "manifests" / "demo_scenes.json"
SIZE = 256
YY, XX = np.mgrid[0:SIZE, 0:SIZE]


def _blur(arr: np.ndarray, radius: float = 1.2) -> np.ndarray:
    return np.asarray(
        Image.fromarray(np.clip(arr * 255, 0, 255).astype(np.uint8)).filter(
            ImageFilter.GaussianBlur(radius)
        ),
        dtype=np.float32,
    ) / 255.0


def _speckle(base: np.ndarray, rng: np.random.Generator, strength: float = 0.16) -> np.ndarray:
    noise = rng.gamma(shape=9.0, scale=1.0 / 9.0, size=base.shape).astype(np.float32)
    return np.clip(base * (1.0 + strength * (noise - 1.0)), 0.0, 1.0)


def _settlements(base: np.ndarray, rng: np.random.Generator, count: int) -> np.ndarray:
    out = base.copy()
    for _ in range(count):
        cx, cy = rng.integers(10, SIZE - 10, size=2)
        w, h = rng.integers(3, 9, size=2)
        out[max(cy - h, 0):cy + h, max(cx - w, 0):cx + w] = rng.uniform(0.70, 0.92)
    return out


def coastal(rng: np.random.Generator) -> np.ndarray:
    coast = 108 + 18 * np.sin(YY / 31.0) + 8 * np.sin(XX / 19.0)
    land = XX > coast
    base = np.where(land, 0.40, 0.075).astype(np.float32)
    # Tidal channels and shallow water
    channel = np.abs(YY - (170 + 26 * np.sin(XX / 27.0))) < 6
    base[channel] = 0.055
    shallow = (~land) & (XX > coast - 24)
    base[shallow] += 0.035
    # agricultural patches and aquaculture ponds on land
    for _ in range(22):
        x, y = rng.integers(120, 245, size=2)
        w, h = rng.integers(8, 22, size=2)
        base[y:y + h, x:x + w] = rng.uniform(0.30, 0.56)
        if rng.random() < 0.35:
            base[y:y + h // 2, x:x + w] = 0.10  # pond
    base[210:216, 150:245] += 0.25  # road / embankment
    return _speckle(_blur(base, 0.6), rng)


def agriculture(rng: np.random.Generator) -> np.ndarray:
    base = np.full((SIZE, SIZE), 0.34, dtype=np.float32)
    cell = 42
    for gy in range(0, SIZE, cell):
        for gx in range(0, SIZE, cell):
            h, w = min(cell, SIZE - gy), min(cell, SIZE - gx)
            level = float(rng.uniform(0.26, 0.58))
            field = np.full((h, w), level, dtype=np.float32)
            rows = 0.06 * np.sin(np.linspace(0, 26, w))[None, :]
            field += rows.astype(np.float32)
            base[gy:gy + h, gx:gx + w] = field
            if rng.random() < 0.4:  # hedgerow
                base[gy, gx:gx + w] += 0.16
    base[124:129, :] = 0.72  # main road
    base[:, 84:88] = 0.66
    base = _settlements(base, rng, 18)
    return _speckle(_blur(base, 0.5), rng, 0.19)


def urban(rng: np.random.Generator) -> np.ndarray:
    base = np.full((SIZE, SIZE), 0.36, dtype=np.float32)
    for x in range(0, SIZE, 32):
        base[:, x:x + 3] = rng.uniform(0.63, 0.82)
    for y in range(0, SIZE, 28):
        base[y:y + 3, :] = rng.uniform(0.62, 0.82)
    for _ in range(46):
        x, y = rng.integers(4, SIZE - 12, size=2)
        w, h = rng.integers(5, 13, size=2)
        bright = rng.uniform(0.60, 0.90)
        base[y:y + h, x:x + w] = bright
        base[y + h, x:x + w] += 0.10  # double-bounce-like edge
    base[188:196, :] = 0.075  # canal
    base[40:75, 165:210] = 0.27  # park
    return _speckle(_blur(base, 0.5), rng, 0.20)


def mixed(rng: np.random.Generator) -> np.ndarray:
    river = 78 + 34 * np.sin(XX / 39.0)
    in_river = np.abs(YY - river) < 16
    base = np.where(in_river, 0.07, 0.38).astype(np.float32)
    flood = (np.abs(YY - river) < 34) & (~in_river)
    base[flood] -= 0.11
    base[np.abs(YY - (river - 34)) < 2.5] += 0.32  # embankment
    for gy in range(0, SIZE, 48):
        for gx in range(0, SIZE, 48):
            h, w = min(44, SIZE - gy), min(44, SIZE - gx)
            base[gy:gy + h, gx:gx + w] += rng.uniform(-0.05, 0.12)
    base = _settlements(base, rng, 34)
    base[15:19, 20:235] = 0.68
    return _speckle(_blur(base, 0.6), rng, 0.18)


SCENES = [
    {
        "id": "coastal-water",
        "name": "Coastal water & delta",
        "scene_type": "water / coastal",
        "region_label": "Illustrative coastal landscape (synthetic)",
        "description": "Calm water, tidal channels, aquaculture ponds and a low-lying shoreline.",
        "generator": coastal,
    },
    {
        "id": "agriculture",
        "name": "Agricultural fields",
        "scene_type": "vegetation / agriculture",
        "region_label": "Illustrative agricultural landscape (synthetic)",
        "description": "Rectangular field parcels, hedgerows, a rural road and a small settlement.",
        "generator": agriculture,
    },
    {
        "id": "built-up",
        "name": "Dense built-up area",
        "scene_type": "urban / built-up",
        "region_label": "Illustrative urban landscape (synthetic)",
        "description": "Street grid, compact structures, bright linear returns and a canal.",
        "generator": urban,
    },
    {
        "id": "mixed-event",
        "name": "Mixed floodplain scene",
        "scene_type": "mixed / disaster-response narrative",
        "region_label": "Illustrative river-floodplain landscape (synthetic)",
        "description": "River, embankment, inundated margins, farmland and settlements.",
        "generator": mixed,
    },
]


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    entries = []
    for index, scene in enumerate(SCENES):
        rng = np.random.default_rng(20261121 + index)
        arr = np.clip(scene["generator"](rng), 0, 1)
        image = Image.fromarray(np.round(arr * 255).astype(np.uint8), mode="L")
        filename = f"{scene['id']}.png"
        image.save(OUT / filename, format="PNG", optimize=True)
        entries.append(
            {
                "id": scene["id"],
                "name": scene["name"],
                "scene_type": scene["scene_type"],
                "region_label": scene["region_label"],
                "description": scene["description"],
                "filename": filename,
                "data_note": (
                    "SYNTHETIC: procedurally generated backscatter-like illustration. "
                    "Not real SAR, not georeferenced, and not suitable for model accuracy claims."
                ),
            }
        )
        print(f"generated {filename}")
    manifest = {
        "version": "1.0",
        "generated": "2026-11-21",
        "source": "Procedural generator: scripts/generate_demo_scenes.py (MIT project code)",
        "licence": "Generated by this project; no third-party imagery used.",
        "warning": "Synthetic demonstration data only. Replace with licensed paired SAR/optical data before reporting accuracy.",
        "scenes": entries,
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {MANIFEST}")


if __name__ == "__main__":
    main()
