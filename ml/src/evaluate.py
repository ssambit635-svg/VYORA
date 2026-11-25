"""Stream a held-out manifest through the model, compare to optical targets, and save worst-case panels.

No report is written unless a real test split and checkpoint exist.
"""
from __future__ import annotations

import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

from ml.src.data import load_manifest, normalise_sar_pair, optical_target

ROOT = Path(__file__).resolve().parents[2]


def _display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def _gaussian_filter(image: np.ndarray, sigma: float = 1.5, size: int = 11) -> np.ndarray:
    coords = np.arange(size, dtype=np.float32) - (size - 1) / 2
    kernel = np.exp(-(coords ** 2) / (2 * sigma ** 2))
    kernel /= kernel.sum()
    pad = size // 2
    out = image.astype(np.float32).copy()
    for axis in (0, 1):
        pad_width = [(0, 0), (0, 0), (0, 0)]
        pad_width[axis] = (pad, pad)
        padded = np.pad(out, pad_width, mode="reflect")
        smoothed = np.zeros_like(out)
        for k in range(size):
            index = [slice(None), slice(None), slice(None)]
            index[axis] = slice(k, k + out.shape[axis])
            smoothed += kernel[k] * padded[tuple(index)]
        out = smoothed
    return out


def ssim(pred: np.ndarray, target: np.ndarray) -> float:
    c1, c2 = 0.01 ** 2, 0.03 ** 2
    values = []
    for ch in range(3):
        p, t = pred[..., ch, None], target[..., ch, None]
        mp, mt = _gaussian_filter(p), _gaussian_filter(t)
        vp = np.maximum(_gaussian_filter(p * p) - mp * mp, 0)
        vt = np.maximum(_gaussian_filter(t * t) - mt * mt, 0)
        cov = _gaussian_filter(p * t) - mp * mt
        score = ((2 * mp * mt + c1) * (2 * cov + c2)) / (
            (mp ** 2 + mt ** 2 + c1) * (vp + vt + c2)
        )
        values.append(float(score.mean()))
    return float(np.mean(values))


def edge_preservation(pred: np.ndarray, target: np.ndarray) -> float:
    def edges(x: np.ndarray) -> np.ndarray:
        gy, gx = np.gradient(x.mean(axis=2))
        return np.sqrt(gx ** 2 + gy ** 2)

    a, b = np.log1p(edges(pred) * 8).ravel(), np.log1p(edges(target) * 8).ravel()
    denom = np.sqrt(((a - a.mean()) ** 2).sum() * ((b - b.mean()) ** 2).sum())
    return float(np.clip(((a - a.mean()) * (b - b.mean())).sum() / denom, 0, 1)) if denom else 0.0


def pseudocolour_baseline(sar: np.ndarray) -> np.ndarray:
    """A simple, non-ML comparator; not a scientific land-cover model."""
    palette = np.array([[0.09, 0.42, 0.62], [0.23, 0.61, 0.36], [0.78, 0.69, 0.50], [0.85, 0.55, 0.39]], dtype=np.float32)
    levels = np.clip((np.asarray(sar) * 4).astype(int), 0, 3)
    return palette[levels]


def score_one(pred: np.ndarray, target: np.ndarray) -> dict[str, float | None]:
    pred = np.clip(np.asarray(pred, dtype=np.float32), 0, 1)
    target = np.clip(np.asarray(target, dtype=np.float32), 0, 1)
    mse = float(np.mean((pred - target) ** 2))
    # Mean per-pixel RGB spread is a simple diagnostic for colour collapse:
    # grayscale predictions approach 0; colourful targets have a larger spread.
    pred_rgb_spread = float(np.mean(pred.max(axis=2) - pred.min(axis=2)))
    target_rgb_spread = float(np.mean(target.max(axis=2) - target.min(axis=2)))
    return {
        "MAE_L1": float(np.mean(np.abs(pred - target))),
        "PSNR_dB": None if mse <= 1e-12 else float(10.0 * np.log10(1.0 / mse)),
        "SSIM": ssim(pred, target),
        "edge_preservation": edge_preservation(pred, target),
        "mean_rgb_channel_spread": pred_rgb_spread,
        "target_rgb_channel_spread": target_rgb_spread,
    }


def manifest_input_representation(rows: list[dict]) -> str:
    """Infer the model contract from manifest metadata; reject ambiguous input."""
    png_rows = [row for row in rows if "A/B PNG export" in row.get("source", "")]
    if png_rows:
        sides = {row.get("input_side") for row in png_rows}
        if len(sides) != 1 or None in sides:
            raise ValueError("PNG evaluation manifest must declare one consistent input_side.")
        side = next(iter(sides))
        if side not in {"A", "B"}:
            raise ValueError(f"Unsupported PNG input_side: {side!r}.")
        return f"grayscale_{side}_PNG_duplicated"
    if any(
        row.get("sar_vv_path") or row.get("sar_vh_path") or row.get("vv_band") or row.get("vh_band")
        for row in rows
    ):
        return "VV_VH_pair"
    raise ValueError("Cannot infer manifest input representation; expected A/B PNG side metadata or explicit VV/VH fields.")


def validate_checkpoint_manifest(saved: dict, rows: list[dict]) -> None:
    expected = manifest_input_representation(rows)
    actual = str(saved.get("input_representation", "VV_VH_pair"))
    if actual != expected:
        raise ValueError(f"Checkpoint expects {actual}, but evaluation manifest provides {expected}.")


def _mean_scores(scores: list[dict[str, float | None]]) -> dict:
    if not scores:
        return {"tiles": 0, "MAE_L1": None, "PSNR_dB": None, "PSNR_perfect_tiles": 0, "SSIM": None, "edge_preservation": None}
    result = {"tiles": len(scores)}
    for key in scores[0]:
        values = [x[key] for x in scores if x[key] is not None]
        result[key] = round(float(np.mean(values)), 5) if values else None
    result["PSNR_perfect_tiles"] = sum(x["PSNR_dB"] is None for x in scores)
    return result


def _panel(sar: np.ndarray, target: np.ndarray, pred: np.ndarray) -> Image.Image:
    radar = np.stack((sar[..., 0], sar[..., 1], (sar[..., 0] + sar[..., 1]) / 2), axis=-1)
    error = np.clip(np.abs(pred - target) * 4, 0, 1)
    arrays = [radar, target, pred, error]
    titles = ["Input preview", "Paired target", "Model estimate", "Absolute error x4"]
    size = target.shape[0]
    panel = Image.new("RGB", (size * len(arrays), size + 26), "white")
    draw = ImageDraw.Draw(panel)
    for i, (arr, title) in enumerate(zip(arrays, titles)):
        image = Image.fromarray(np.round(np.clip(arr, 0, 1) * 255).astype(np.uint8), "RGB")
        panel.paste(image, (i * size, 26))
        draw.text((i * size + 4, 6), title, fill="black")
    return panel


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", default="data/manifests/tiles.json")
    parser.add_argument("--checkpoint", default="backend/checkpoints/vyora_resunet.pt")
    parser.add_argument("--output", default="docs/evaluation_results.json")
    parser.add_argument("--examples-dir", default="docs/evaluation_examples")
    parser.add_argument("--latency-runs", type=int, default=5)
    parser.add_argument("--worst-examples", type=int, default=4)
    parser.add_argument("--max-test-tiles", type=int, default=None, help="Deterministic test subset for a fast prototype check")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    manifest = Path(args.manifest)
    checkpoint = Path(args.checkpoint)
    manifest = manifest if manifest.is_absolute() else ROOT / manifest
    checkpoint = checkpoint if checkpoint.is_absolute() else ROOT / checkpoint
    if not manifest.is_file():
        parser.exit(1, f"No evaluation performed: manifest not found at {manifest}.\n")
    if not checkpoint.is_file():
        parser.exit(1, f"No evaluation performed: checkpoint not found at {checkpoint}.\n")
    if args.worst_examples < 1:
        parser.error("--worst-examples must be at least 1")

    try:
        rows = [r for r in load_manifest(manifest) if r["split"] == "test"]
    except Exception as exc:
        parser.exit(1, f"No evaluation performed: test manifest validation failed: {exc}\n")
    if not rows:
        parser.exit(1, "No evaluation performed: manifest contains no 'test' split tiles.\n")
    total_test_tiles = len(rows)
    if args.max_test_tiles is not None:
        if args.max_test_tiles < 1:
            parser.error("--max-test-tiles must be positive")
        if len(rows) > args.max_test_tiles:
            import random
            rows = random.Random(args.seed).sample(rows, args.max_test_tiles)
            print(f"Prototype evaluation subset: {len(rows)} of {total_test_tiles} test tiles (seed {args.seed}).")

    try:
        import torch
        from ml.src.model import build_model
        try:
            saved = torch.load(checkpoint, map_location="cpu", weights_only=True)
        except TypeError:
            saved = torch.load(checkpoint, map_location="cpu")
        if not isinstance(saved, dict) or "state_dict" not in saved:
            raise ValueError("checkpoint does not contain a state_dict")
        validate_checkpoint_manifest(saved, rows)
        model = build_model(int(saved.get("base_channels", 24)), input_channels=int(saved.get("input_channels", 2)))
        model.load_state_dict(saved["state_dict"])
        model.eval()
    except Exception as exc:
        parser.exit(1, f"No evaluation performed: checkpoint could not be loaded: {exc}\n")

    def predict(sar: np.ndarray) -> np.ndarray:
        x = torch.from_numpy(np.moveaxis(sar, -1, 0)[None, ...].copy()).float()
        with torch.inference_mode():
            return model(x)[0].permute(1, 2, 0).cpu().numpy()

    baseline_scores: list[dict[str, float]] = []
    model_scores: list[dict[str, float]] = []
    latencies: list[float] = []
    worst: list[tuple[float, str, Image.Image, dict]] = []
    try:
        for row in rows:
            sar = normalise_sar_pair(row)
            target = optical_target(row)
            baseline = pseudocolour_baseline(sar.mean(axis=-1))
            baseline_scores.append(score_one(baseline, target))
            start = time.perf_counter()
            pred = predict(sar)
            if len(latencies) < max(1, args.latency_runs):
                latencies.append((time.perf_counter() - start) * 1000)
            scores = score_one(pred, target)
            model_scores.append(scores)
            panel = _panel(sar, target, pred)
            detail = {"tile_id": row["tile_id"], "scene_group": row["scene_group"],
                      **{k: (round(v, 5) if v is not None else None) for k, v in scores.items()}}
            worst.append((scores["MAE_L1"], str(row["tile_id"]), panel, detail))
            worst.sort(key=lambda item: item[0], reverse=True)
            del worst[args.worst_examples:]
    except Exception as exc:
        parser.exit(1, f"No evaluation report written: failed while reading/evaluating a test tile: {exc}\n")

    examples_dir = Path(args.examples_dir)
    examples_dir = examples_dir if examples_dir.is_absolute() else ROOT / examples_dir
    examples_dir.mkdir(parents=True, exist_ok=True)
    example_meta = []
    for _mae, tile_id, image, detail in worst:
        safe_id = "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in tile_id)
        image_path = examples_dir / f"worst_{safe_id}.png"
        image.save(image_path)
        example_meta.append({**detail, "panel": _display_path(image_path)})

    png_folder_split = any("A/B PNG export" in row.get("source", "") for row in rows)
    split_note = (
        "provided train/validation/test folders (geographic independence not independently verified)"
        if png_folder_split else
        "test (manifest scene groups are kept exclusive across splits)"
    )
    result = {
        "status": "evaluated",
        "date": datetime.now(timezone.utc).isoformat(),
        "checkpoint": _display_path(checkpoint),
        "manifest": _display_path(manifest),
        "test_tiles": len(rows),
        "total_test_tiles_in_manifest": total_test_tiles,
        "test_scene_groups": len({row["scene_group"] for row in rows}),
        "split": split_note,
        "methods": {
            "pseudocolour_baseline": _mean_scores(baseline_scores),
            "resunet_model": _mean_scores(model_scores),
        },
        "median_latency_ms_cpu_first_runs": round(float(np.median(latencies)), 2) if latencies else None,
        "worst_test_examples_by_MAE": example_meta,
        "caveat": "Similarity to paired optical reference pixels on this held-out dataset split only; not true-colour recovery or geographic correctness.",
    }
    output = Path(args.output)
    output = output if output.is_absolute() else ROOT / output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
