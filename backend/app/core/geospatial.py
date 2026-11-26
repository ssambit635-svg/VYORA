"""Dual-polarization SAR decoding and georeferenced preview export.

GeoTIFF inputs must already be radiometrically calibrated and co-registered;
this module performs robust per-band display normalization, not SNAP-equivalent
radiometric/terrain correction. Band order for uploaded GeoTIFFs is VV=1, VH=2.
"""
from __future__ import annotations

import io
from dataclasses import dataclass
from pathlib import Path
import sys

import numpy as np
from PIL import Image, UnidentifiedImageError

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
from common.sar_preprocessing import normalize_sar_pair  # noqa: E402
from .config import MAX_IMAGE_PIXELS, MAX_UPLOAD_BYTES, TILE_SIZE
from .preprocess import ImageValidationError


@dataclass
class DecodedSAR:
    channels: np.ndarray  # H x W x 2, source scale
    source_width: int
    source_height: int
    filename: str
    profile: dict | None = None
    crs: str | None = None
    transform: tuple[float, ...] | None = None
    input_kind: str = "single-channel-preview"

    @property
    def has_georeferencing(self) -> bool:
        """True only when a CRS and non-identity affine transform are present."""
        identity = (1.0, 0.0, 0.0, 0.0, 1.0, 0.0)
        return bool(
            self.profile is not None
            and self.crs
            and self.transform is not None
            and not np.allclose(self.transform, identity)
        )


def decode_sar(payload: bytes, filename: str, content_type: str | None = None) -> DecodedSAR:
    """Decode a two-band VV/VH GeoTIFF or a labelled single-channel preview.

    A PNG/JPEG is duplicated into two identical channels only for the bundled
    synthetic/UI workflow. This is explicitly not genuine dual-polarization data.
    """
    if not payload:
        raise ImageValidationError("The uploaded file is empty.")
    if len(payload) > MAX_UPLOAD_BYTES:
        raise ImageValidationError(f"Image is larger than the {MAX_UPLOAD_BYTES // (1024 * 1024)} MB upload limit.")
    suffix = Path(filename).suffix.lower()
    if suffix not in {".tif", ".tiff"} and len(payload) > 10 * 1024 * 1024:
        raise ImageValidationError("PNG/JPEG preview is larger than the 10 MB limit.")
    if suffix in {".tif", ".tiff"}:
        if payload[:4] not in (b"II*\x00", b"MM\x00*", b"II+\x00", b"MM\x00+"):
            raise ImageValidationError("Invalid TIFF signature.")
        try:
            import rasterio
            from rasterio.io import MemoryFile
        except ImportError as exc:
            raise ImageValidationError("GeoTIFF support is not installed. Install backend requirements.") from exc
        try:
            with MemoryFile(payload) as memfile:
                with memfile.open() as dataset:
                    if dataset.count < 2:
                        raise ImageValidationError("GeoTIFF needs two bands in the documented order: VV band 1, VH band 2.")
                    if dataset.width * dataset.height > MAX_IMAGE_PIXELS:
                        raise ImageValidationError("GeoTIFF dimensions are too large for the local demo.")
                    vv = dataset.read(1, masked=True).astype(np.float32).filled(np.nan)
                    vh = dataset.read(2, masked=True).astype(np.float32).filled(np.nan)
                    profile = dataset.profile.copy()
                    crs = dataset.crs.to_string() if dataset.crs else None
                    transform = tuple(dataset.transform)[:6]
                    width, height = dataset.width, dataset.height
        except ImageValidationError:
            raise
        except Exception as exc:
            raise ImageValidationError("GeoTIFF could not be read. Check that it is a valid, uncompressed or tiled raster.") from exc
        return DecodedSAR(np.stack([vv, vh], axis=-1), width, height, filename, profile, crs, transform, "geotiff-vv-vh")

    if suffix not in {".png", ".jpg", ".jpeg"}:
        raise ImageValidationError("Use a two-band GeoTIFF (VV band 1, VH band 2) or a PNG/JPEG preview.")
    try:
        with Image.open(io.BytesIO(payload)) as image:
            image.load()
            if image.format not in {"PNG", "JPEG"}:
                raise ImageValidationError("Only PNG/JPEG previews and GeoTIFF inputs are supported.")
            if image.width * image.height > MAX_IMAGE_PIXELS:
                raise ImageValidationError("Image dimensions are too large for the local demo.")
            grey = np.asarray(image.convert("L"), dtype=np.float32)
    except (UnidentifiedImageError, OSError) as exc:
        raise ImageValidationError("The image could not be decoded.") from exc
    return DecodedSAR(np.stack([grey, grey], axis=-1), image.width, image.height, filename, input_kind="single-channel-preview-duplicated")


def preprocess_pair(channels: np.ndarray, size: int = TILE_SIZE, despeckle: bool = True) -> np.ndarray:
    """Shared training/inference normalization; not physical SAR calibration."""
    try:
        return normalize_sar_pair(channels, size=size, despeckle=despeckle)
    except ValueError as exc:
        raise ImageValidationError(str(exc)) from exc


def geotiff_bytes(rgb: np.ndarray, profile: dict) -> bytes:
    """Write model-sized RGB preview with the source extent/CRS preserved."""
    try:
        import rasterio
        from affine import Affine
        from rasterio.io import MemoryFile
    except ImportError as exc:
        raise RuntimeError("GeoTIFF export requires rasterio and affine.") from exc
    height, width = rgb.shape[:2]
    out_profile = profile.copy()
    source_transform = profile.get("transform")
    out_profile.pop("blockxsize", None)
    out_profile.pop("blockysize", None)
    out_profile.pop("nodata", None)
    out_profile.update(driver="GTiff", count=3, dtype="uint8", width=width, height=height, compress="deflate", photometric="RGB")
    if source_transform is not None:
        sx = profile["width"] / width
        sy = profile["height"] / height
        out_profile["transform"] = source_transform @ Affine.scale(sx, sy)
    with MemoryFile() as memfile:
        with memfile.open(**out_profile) as ds:
            ds.write(np.moveaxis(rgb.astype(np.uint8), -1, 0))
            ds.update_tags(AREA_OR_POINT="Area", VYORA_OUTPUT="estimated RGB-style interpretation; not true-colour ground truth")
        return memfile.read()
