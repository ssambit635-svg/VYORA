"""Training losses: colour reconstruction + structure + edge preservation."""
from __future__ import annotations

import torch
import torch.nn.functional as F


def _gaussian_window(size: int = 11, sigma: float = 1.5) -> torch.Tensor:
    coords = torch.arange(size, dtype=torch.float32)
    g = torch.exp(-((coords - (size - 1) / 2) ** 2) / (2 * sigma ** 2))
    window = g[:, None] * g[None, :]
    return (window / window.sum())[None, None, ...]


def ssim_loss(pred: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
    """Differentiable average SSIM loss for 3-channel images in [0, 1]."""
    window = _gaussian_window().to(pred.device)
    pad = 5

    def stats(x: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        mean = F.conv2d(x, window.expand(3, 1, -1, -1), padding=pad, groups=3)
        mean_sq = F.conv2d(x * x, window.expand(3, 1, -1, -1), padding=pad, groups=3)
        var = (mean_sq - mean * mean).clamp_min(0)
        return mean, var, x

    mp, vp, _ = stats(pred)
    mt, vt, _ = stats(target)
    cov = F.conv2d(pred * target, window.expand(3, 1, -1, -1), padding=pad, groups=3) - mp * mt
    c1, c2 = 0.01 ** 2, 0.03 ** 2
    ssim = ((2 * mp * mt + c1) * (2 * cov + c2)) / ((mp ** 2 + mt ** 2 + c1) * (vp + vt + c2))
    return 1.0 - ssim.mean()


def _sobel() -> tuple[torch.Tensor, torch.Tensor]:
    kx = torch.tensor([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], dtype=torch.float32)
    return kx[None, None, ...], kx.T[None, None, ...]


def _gradient_magnitude(x: torch.Tensor, kx: torch.Tensor, ky: torch.Tensor) -> torch.Tensor:
    gx = F.conv2d(x, kx.expand(3, 1, 3, 3), padding=1, groups=3)
    gy = F.conv2d(x, ky.expand(3, 1, 3, 3), padding=1, groups=3)
    return torch.sqrt(gx ** 2 + gy ** 2 + 1e-8).mean(dim=1, keepdim=True)


def edge_loss(pred: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
    kx, ky = _sobel()
    return F.l1_loss(_gradient_magnitude(pred, kx, ky), _gradient_magnitude(target, kx, ky))


def total_loss(
    pred: torch.Tensor,
    target: torch.Tensor,
    feature_logits: torch.Tensor | None = None,
    feature_target: torch.Tensor | None = None,
    w_colour: float = 1.0,
    w_ssim: float = 0.2,
    w_edge: float = 0.1,
    w_feature: float = 0.1,
) -> dict[str, torch.Tensor]:
    parts = {
        "colour": F.l1_loss(pred, target),
        "structure": ssim_loss(pred, target),
        "edge": edge_loss(pred, target),
    }
    if feature_logits is not None and feature_target is not None:
        parts["feature"] = F.cross_entropy(feature_logits, feature_target)
    total = (
        w_colour * parts["colour"]
        + w_ssim * parts["structure"]
        + w_edge * parts["edge"]
        + (w_feature * parts.get("feature", torch.zeros((), device=pred.device)))
    )
    parts["total"] = total
    return parts
