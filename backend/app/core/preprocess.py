"""SAR image validation and deterministic preprocessing.

The pipeline is intentionally small and auditable:
1. strict MIME / format and size validation;
2. single-channel decode;
3. optional 3x3 median filter (light despeckling);
4. 2nd-98th percentile clipping and min-max normalisation;
5. deterministic resize to the inference tile size.

No EXIF/GPS metadata is retained: the image is decoded into a plain array.
"""
from __future__ import annotations

import io
from pathlib import Path
from PIL import Image, ImageFilter, UnidentifiedImageError
import numpy as np

from .config import ALLOWED_CONTENT_TYPES, MAX_IMAGE_PIXELS, MAX_UPLOAD_BYTES, TILE_SIZE


class ImageValidationError(ValueError):
    """Raised when an upload cannot be safely decoded as a supported SAR image."""


def validate_upload(filename: str, content_type: str | None, payload: bytes) -> None:
    if len(payload) == 0:
        raise ImageValidationError("The uploaded file is empty.")
    if len(payload) > MAX_UPLOAD_BYTES:
        raise ImageValidationError(
            f"Image is larger than the 10 MB demo limit ({len(payload) / 1_048_576:.1f} MB)."
        )
    suffix = Path(filename).suffix.lower()
    if suffix not in {".png", ".jpg", ".jpeg"}:
        raise ImageValidationError("Unsupported file type. Please upload a PNG or JPEG image.")
    if content_type and content_type.split(";")[0].strip().lower() not in ALLOWED_CONTENT_TYPES:
        raise ImageValidationError("Unsupported media type. Please upload a PNG or JPEG image.")
    if payload[:8] not in (b"\x89PNG\r\n\x1a\n", b"\xff\xd8\xff"):
        raise ImageValidationError("This does not look like a valid PNG or JPEG file.")


def decode_grayscale(payload: bytes) -> Image.Image:
    try:
        with Image.open(io.BytesIO(payload)) as img:
            img.load()
            width, height = img.size
            if width * height > MAX_IMAGE_PIXELS:
                raise ImageValidationError("Image dimensions are too large for the local demo.")
            if img.format not in ("PNG", "JPEG"):
                raise ImageValidationError("Only PNG and JPEG images are supported.")
            # Convert immediately: EXIF/GPS metadata is dropped here.
            return img.convert("L").copy()
    except (UnidentifiedImageError, OSError, ValueError) as exc:
        if isinstance(exc, ImageValidationError):
            raise
        raise ImageValidationError("The image could not be decoded. Try a different PNG or JPEG.") from exc


def preprocess_sar(
    image: Image.Image, size: int = TILE_SIZE, despeckle: bool = True
) -> np.ndarray:
    """Return a deterministic float32 tile in [0, 1]."""
    work = image
    if work.size != (size, size):
        work = work.resize((size, size), Image.Resampling.LANCZOS)
    arr = np.asarray(work, dtype=np.float32)
    if despeckle:
        filtered = Image.fromarray(arr.astype(np.uint8), mode="L").filter(
            ImageFilter.MedianFilter(size=3)
        )
        arr = np.asarray(filtered, dtype=np.float32)
    low, high = np.percentile(arr, (2, 98))
    if high <= low:
        return np.zeros_like(arr, dtype=np.float32)
    return np.clip((arr - low) / (high - low), 0.0, 1.0).astype(np.float32)


def to_display_array(tile: np.ndarray) -> np.ndarray:
    """Convert a normalised tile to uint8 for the comparison slider."""
    return np.clip(tile * 255.0, 0, 255).astype(np.uint8)
