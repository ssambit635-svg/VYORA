"""Model interface with an explicit, labelled development fallback.

Two execution paths exist:

``model``       - loads a locally saved ResU-Net checkpoint (PyTorch, CPU).
``development`` - deterministic hand-authored feature mapping; never called AI.

There is no silent pretending: every output carries ``mode``, ``model_version``
and ``is_ai_inference`` so the UI and JSON export can label it correctly.
"""
from __future__ import annotations

import importlib.util
import logging
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from app.core.config import CHECKPOINT_PATH, FEATURE_LABELS, MODE, REPO_ROOT
from app.ml import feature_mapping

logger = logging.getLogger("vyora.ml")


@dataclass
class InferenceOutput:
    colour: np.ndarray  # uint8 RGB
    confidence: np.ndarray  # float32 in [0, 1]
    confidence_image: np.ndarray  # uint8 RGB heatmap
    feature_estimates: dict[str, float]
    mode: str
    model_version: str
    is_ai_inference: bool
    confidence_method: str
    feature_method: str


@dataclass
class RunnerStatus:
    mode: str
    model_version: str
    is_ai_inference: bool
    input_representation: str
    checkpoint_available: bool
    torch_available: bool
    reason: str


class _BaseRunner:
    mode: str = "development"
    model_version: str = "dev-heuristic-v0"
    is_ai_inference: bool = False
    input_representation: str = "VV_VH_pair"

    def infer(self, tile: np.ndarray) -> InferenceOutput:
        raise NotImplementedError


class DevelopmentRunner(_BaseRunner):
    input_representation = "development_preview"
    confidence_method = "deterministic local consistency of hand-authored rules (not model uncertainty)"
    feature_method = "mean of hand-authored backscatter/texture memberships (not validated segmentation)"

    def infer(self, tile: np.ndarray) -> InferenceOutput:
        preview = tile.mean(axis=2) if tile.ndim == 3 else tile
        rgb, confidence, memberships = feature_mapping.interpret(preview)
        return InferenceOutput(
            colour=rgb,
            confidence=confidence,
            confidence_image=feature_mapping.confidence_heatmap(confidence),
            feature_estimates={label: float(memberships[i]) for i, label in enumerate(FEATURE_LABELS)},
            mode=self.mode,
            model_version=self.model_version,
            is_ai_inference=self.is_ai_inference,
            confidence_method=self.confidence_method,
            feature_method=self.feature_method,
        )


class CheckpointRunner(_BaseRunner):
    mode = "model"
    is_ai_inference = True
    confidence_method = "test-time augmented output consistency (original vs horizontal flip); not calibrated uncertainty"
    feature_method = "nearest fixed display-palette share from generated RGB; not a learned classifier or validated land-cover map"

    def __init__(self, path: Path):
        import torch

        if str(REPO_ROOT) not in sys.path:
            sys.path.insert(0, str(REPO_ROOT))
        from ml.src.model import build_model  # imported only when a checkpoint exists

        try:
            saved = torch.load(path, map_location="cpu", weights_only=True)
        except TypeError:  # older torch
            saved = torch.load(path, map_location="cpu")

        if not isinstance(saved, dict) or "state_dict" not in saved:
            raise ValueError("Checkpoint must be a dict containing 'state_dict'.")
        state = saved["state_dict"]
        base = int(saved.get("base_channels", 24))
        input_channels = int(saved.get("input_channels", 2))
        self.input_channels = input_channels
        self.input_representation = str(saved.get("input_representation", "VV_VH_pair"))
        if self.input_representation != "VV_VH_pair":
            self.feature_method = "not provided: this image-to-image checkpoint has no land-cover classification head"
        self.model_version = str(saved.get("version", "resunet-unversioned"))
        self.model = build_model(base_channels=base, input_channels=input_channels)
        self.model.load_state_dict(state)
        self.model.eval()
        self.torch = torch

    def _predict(self, tile: np.ndarray) -> np.ndarray:
        if tile.ndim == 2:
            tile = np.stack([tile, tile], axis=-1)
        if tile.ndim != 3 or tile.shape[-1] != self.input_channels:
            raise ValueError(f"Checkpoint expects {self.input_channels} VV/VH channels; got shape {tile.shape}.")
        x = self.torch.from_numpy(np.moveaxis(tile, -1, 0)[None, ...].copy()).float()
        with self.torch.inference_mode():
            rgb = self.model(x)
        return rgb[0].permute(1, 2, 0).clamp(0, 1).cpu().numpy()

    def infer(self, tile: np.ndarray) -> InferenceOutput:
        rgb = self._predict(tile)
        rgb_flip = self._predict(np.ascontiguousarray(tile[:, ::-1]))[:, ::-1]
        # Average the two aligned visual predictions; consistency is only a method-stability proxy.
        agreement = np.clip(1.0 - np.abs(rgb - rgb_flip).mean(axis=2), 0.0, 1.0)
        rgb = 0.5 * (rgb + rgb_flip)
        confidence = np.clip(agreement, 0.02, 0.995).astype(np.float32)

        # PNG prototype has no validated class labels; do not manufacture class
        # shares from its RGB output. The legacy dual-pol demo may display only
        # palette-derived explanatory shares, never learned class probabilities.
        if self.input_representation == "VV_VH_pair":
            palette = feature_mapping.PALETTE
            flat = rgb.reshape(-1, 3)
            distances = ((flat[:, None, :] - palette[None, ...]) ** 2).sum(axis=2)
            nearest = np.argmin(distances, axis=1).reshape(rgb.shape[:2])
            counts = np.bincount(nearest.ravel(), minlength=4).astype(np.float32)
            counts = np.maximum(counts, 1e-4)
            shares = counts / counts.sum()
            feature_estimates = {label: float(shares[i]) for i, label in enumerate(FEATURE_LABELS)}
            total = sum(feature_estimates.values())
            feature_estimates = {k: round(v / total, 6) for k, v in feature_estimates.items()}
        else:
            feature_estimates = {}
        colour = np.round(np.clip(rgb, 0, 1) * 255).astype(np.uint8)
        return InferenceOutput(
            colour=colour,
            confidence=confidence,
            confidence_image=feature_mapping.confidence_heatmap(confidence),
            feature_estimates=feature_estimates,
            mode=self.mode,
            model_version=self.model_version,
            is_ai_inference=True,
            confidence_method=self.confidence_method,
            feature_method=self.feature_method,
        )


def torch_available() -> bool:
    return importlib.util.find_spec("torch") is not None


def _build_runner() -> tuple[_BaseRunner, str]:
    checkpoint_exists = CHECKPOINT_PATH.is_file()
    if MODE == "development":
        return DevelopmentRunner(), "VYORA_MODE=development forces the labelled development fallback."
    if MODE not in ("auto", "model"):
        return DevelopmentRunner(), f"Unknown VYORA_MODE={MODE!r}; using development fallback."
    if not checkpoint_exists:
        return (
            DevelopmentRunner(),
            f"No checkpoint found at {CHECKPOINT_PATH}; using labelled development fallback.",
        )
    if not torch_available():
        return DevelopmentRunner(), "PyTorch is not installed; using labelled development fallback."
    try:
        return CheckpointRunner(CHECKPOINT_PATH), f"Loaded checkpoint {CHECKPOINT_PATH.name}."
    except Exception as exc:  # pragma: no cover - depends on local checkpoint
        logger.exception("Could not load checkpoint: %s", exc)
        return DevelopmentRunner(), f"Checkpoint could not be loaded ({exc}); using development fallback."


_runner: _BaseRunner | None = None
_runner_reason = ""


def get_runner() -> _BaseRunner:
    global _runner, _runner_reason
    if _runner is None:
        _runner, _runner_reason = _build_runner()
        logger.info("Inference runner: %s (%s)", _runner.mode, _runner_reason)
    return _runner


def runner_status() -> RunnerStatus:
    runner = get_runner()
    # _build_runner sets the reason on first call; get_runner may be called twice.
    return RunnerStatus(
        mode=runner.mode,
        model_version=runner.model_version,
        is_ai_inference=runner.is_ai_inference,
        input_representation=runner.input_representation,
        checkpoint_available=CHECKPOINT_PATH.is_file(),
        torch_available=torch_available(),
        reason=_runner_reason,
    )


def evaluation_status_for_model(model_version: str, is_ai_inference: bool) -> str:
    """Only claim the report when the exact evaluated checkpoint is active."""
    if not is_ai_inference:
        return "not_evaluated"
    if model_version == "resunet-paired-png-prototype-v0.2-b-to-a":
        return "documented_200_tile_subset_geographic_independence_unverified"
    return "not_evaluated_for_this_checkpoint"


def incompatible_input_message(
    runner: _BaseRunner,
    input_kind: str,
    filename: str | None = None,
    *,
    is_synthetic_demo: bool = False,
) -> str | None:
    """Return an actionable error when a checkpoint's training input differs."""
    if not runner.is_ai_inference:
        return None  # the labelled development fallback accepts previews for UI testing
    representation = str(getattr(runner, "input_representation", ""))
    is_png_model = representation.startswith("grayscale_") and representation.endswith("_PNG_duplicated")
    if is_png_model and is_synthetic_demo:
        return "The synthetic gallery is not a paired training example. Upload a grayscale PNG from the paired dataset for this checkpoint."
    if is_png_model and input_kind == "geotiff-vv-vh":
        return (
            "This checkpoint was trained on grayscale paired PNG tiles, not separate VV/VH bands. "
            "Upload a PNG tile or select a VV/VH-trained checkpoint."
        )
    if is_png_model and filename and Path(filename).suffix.lower() != ".png":
        return "This checkpoint expects a PNG tile from the paired dataset; JPEG/other preview formats are not accepted."
    if representation == "VV_VH_pair" and input_kind == "single-channel-preview-duplicated":
        return (
            "This checkpoint expects distinct VV and VH bands. A single-channel PNG/JPEG preview "
            "is not genuine dual-polarization input."
        )
    return None
