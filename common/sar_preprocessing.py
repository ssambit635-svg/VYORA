"""The single SAR normalization pipeline shared by training and inference."""
from __future__ import annotations

import numpy as np
from PIL import Image, ImageFilter


def normalize_sar_pair(channels: np.ndarray, size: int = 256, despeckle: bool = True) -> np.ndarray:
    """Normalize VV/VH independently and return HxWx2 float32 in [0, 1].

    The order deliberately matches inference: per-band 2nd/98th percentile
    clipping, 8-bit quantization, optional 3x3 median filter, then Lanczos resize.
    This is display/model normalization, not radiometric calibration.
    """
    channels = np.asarray(channels)
    if channels.ndim != 3 or channels.shape[-1] != 2:
        raise ValueError(f"Expected an H x W x 2 VV/VH array, got {channels.shape}.")
    if size < 1:
        raise ValueError("size must be positive.")
    output = []
    for index in range(2):
        band = np.asarray(channels[..., index], dtype=np.float32)
        finite = np.isfinite(band)
        if not finite.any():
            raise ValueError(f"SAR channel {index + 1} contains no finite pixels.")
        low, high = np.percentile(band[finite], (2, 98))
        if high <= low:
            scaled = np.zeros(band.shape, dtype=np.uint8)
        else:
            scaled_float = np.clip((np.nan_to_num(band, nan=low) - low) / (high - low), 0, 1)
            scaled = np.round(scaled_float * 255).astype(np.uint8)
        image = Image.fromarray(scaled, mode="L")
        if despeckle:
            image = image.filter(ImageFilter.MedianFilter(size=3))
        if image.size != (size, size):
            image = image.resize((size, size), Image.Resampling.LANCZOS)
        output.append(np.asarray(image, dtype=np.float32) / 255.0)
    return np.stack(output, axis=-1).astype(np.float32)
