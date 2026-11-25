#!/usr/bin/env python3
"""Inspect one real SEN12MS S1/S2 GeoTIFF pair before choosing manifest settings."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np


def describe(path: Path) -> dict:
    import rasterio

    with rasterio.open(path) as ds:
        result = {
            "path": str(path), "width": ds.width, "height": ds.height,
            "count": ds.count, "crs": str(ds.crs) if ds.crs else None,
            "transform": list(ds.transform)[:6], "bounds": list(ds.bounds),
            "nodata": ds.nodata, "dataset_tags": ds.tags(), "bands": [],
        }
        for index in range(1, ds.count + 1):
            band = ds.read(index, masked=True).astype(np.float32)
            values = band.compressed()
            item = {
                "index_1_based": index,
                "description": ds.descriptions[index - 1],
                "units": ds.units[index - 1],
                "color_interpretation": ds.colorinterp[index - 1].name,
                "tags": ds.tags(index),
                "valid_fraction": round(float(values.size / (ds.width * ds.height)), 6),
            }
            if values.size:
                item["valid_min_p02_p50_p98_max"] = [
                    float(v) for v in np.percentile(values, [0, 2, 50, 98, 100])
                ]
            result["bands"].append(item)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--s1", required=True, type=Path, help="One downloaded Sentinel-1 GeoTIFF")
    parser.add_argument("--s2", required=True, type=Path, help="Its matching Sentinel-2 GeoTIFF")
    args = parser.parse_args()
    if not args.s1.is_file() or not args.s2.is_file():
        parser.error("Both --s1 and --s2 must name existing files.")
    try:
        s1, s2 = describe(args.s1), describe(args.s2)
    except Exception as exc:
        parser.exit(2, f"Could not inspect the TIFFs: {exc}\n")

    same_grid = all(s1[k] == s2[k] for k in ("width", "height", "crs", "transform"))
    print(json.dumps({"same_grid": same_grid, "sentinel1": s1, "sentinel2": s2}, indent=2))
    if not same_grid:
        print("WARNING: these files are not on the same exact raster grid; do not train this pair without a verified resampling/alignment step.")
    print("Band indexes are not inferred from filenames. Use descriptions/tags/source metadata to choose VV, VH and RGB; confirm scale before creating the manifest.")
    return 0 if same_grid else 1


if __name__ == "__main__":
    raise SystemExit(main())
