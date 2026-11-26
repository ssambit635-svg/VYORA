#!/usr/bin/env python3
"""Make a small, explicitly non-geospatial VV/VH preview from SAFE measurements.

This is for a labelled visualization/demo path only. It does not perform
Sentinel-1 calibration, terrain correction, geocoding, or model training.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

IDENTITY_TRANSFORM = (1.0, 0.0, 0.0, 0.0, 1.0, 0.0)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vv", required=True, type=Path, help="Single-band VV measurement TIFF")
    parser.add_argument("--vh", required=True, type=Path, help="Single-band VH measurement TIFF")
    parser.add_argument("--output", required=True, type=Path, help="Output two-band preview GeoTIFF (VV=1, VH=2)")
    parser.add_argument("--size", type=int, default=256, help="Square preview side length (default: 256)")
    parser.add_argument(
        "--allow-unreferenced", action="store_true",
        help="Explicitly allow TIFFs with no CRS or with an identity transform; output remains non-geospatial.",
    )
    args = parser.parse_args()

    if args.size < 32 or args.size > 2048:
        parser.error("--size must be between 32 and 2048 pixels.")
    for path in (args.vv, args.vh):
        if not path.is_file():
            parser.error(f"Measurement TIFF not found: {path}")

    try:
        import rasterio
        from rasterio.enums import Resampling
        from rasterio.transform import Affine
    except ImportError as exc:
        parser.exit(2, f"GeoTIFF preview requires rasterio: {exc}\n")

    try:
        with rasterio.open(args.vv) as vv_ds, rasterio.open(args.vh) as vh_ds:
            if vv_ds.count != 1 or vh_ds.count != 1:
                parser.error("VV and VH inputs must each contain exactly one measurement band.")
            if (vv_ds.width, vv_ds.height) != (vh_ds.width, vh_ds.height):
                parser.error("VV and VH dimensions differ; refusing to pair mis-sized bands.")
            if vv_ds.crs != vh_ds.crs or vv_ds.transform != vh_ds.transform:
                parser.error("VV and VH CRS/transform differ; refusing to pair misaligned bands.")

            transform_tuple = tuple(vv_ds.transform)[:6]
            has_georef = vv_ds.crs is not None and transform_tuple != IDENTITY_TRANSFORM
            if not has_georef and not args.allow_unreferenced:
                parser.error(
                    "Input TIFFs have no usable CRS/transform. For a clearly non-geospatial visual demo only, "
                    "rerun with --allow-unreferenced. This does not make them suitable for geospatial analysis or training."
                )

            vv = vv_ds.read(
                1, out_shape=(args.size, args.size), masked=True,
                resampling=Resampling.average,
            ).astype(np.float32).filled(np.nan)
            vh = vh_ds.read(
                1, out_shape=(args.size, args.size), masked=True,
                resampling=Resampling.average,
            ).astype(np.float32).filled(np.nan)

            profile = {
                "driver": "GTiff", "width": args.size, "height": args.size,
                "count": 2, "dtype": "float32", "compress": "deflate",
            }
            if has_georef:
                profile["crs"] = vv_ds.crs
                profile["transform"] = vv_ds.transform * Affine.scale(vv_ds.width / args.size, vv_ds.height / args.size)
            else:
                profile["transform"] = Affine.identity()

        args.output.parent.mkdir(parents=True, exist_ok=True)
        with rasterio.open(args.output, "w", **profile) as output_ds:
            output_ds.write(vv, 1)
            output_ds.write(vh, 2)
            output_ds.set_band_description(1, "VV - raw measurement display sample; not radiometrically calibrated by this script")
            output_ds.set_band_description(2, "VH - raw measurement display sample; not radiometrically calibrated by this script")
            output_ds.update_tags(
                VYORA_DEMO_ONLY="true",
                VYORA_IS_AI_INFERENCE="false",
                VYORA_GEOSPATIAL="true" if has_georef else "false",
                VYORA_PROCESSING="downsampled display preview only; no calibration, terrain correction, or geocoding",
                VYORA_SOURCE_VV=args.vv.name,
                VYORA_SOURCE_VH=args.vh.name,
            )
    except SystemExit:
        raise
    except Exception as exc:
        parser.exit(2, f"Could not create VV/VH preview: {exc}\n")

    finite_vv, finite_vh = vv[np.isfinite(vv)], vh[np.isfinite(vh)]
    print(json.dumps({
        "output": str(args.output), "width": args.size, "height": args.size,
        "bands": ["VV", "VH"], "crs": str(profile.get("crs")) if has_georef else None,
        "geospatial": has_georef,
        "vv_p02_p50_p98": [float(v) for v in np.percentile(finite_vv, [2, 50, 98])] if finite_vv.size else None,
        "vh_p02_p50_p98": [float(v) for v in np.percentile(finite_vh, [2, 50, 98])] if finite_vh.size else None,
        "notice": "Illustrative VV/VH display preview only; not a trained VV/VH model output or analysis-ready calibrated product.",
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
