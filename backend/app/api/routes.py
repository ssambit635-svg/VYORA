"""HTTP API for Vyora. All uploads are processed in memory and never persisted."""
from __future__ import annotations

import io
import json
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import Response
from PIL import Image
import numpy as np

from app.core.config import (
    DEMO_DIR,
    DISCLAIMER,
    MANIFEST_PATH,
    MAX_CACHED_RESULTS,
    RESULT_TTL_SECONDS,
)
from app.core.metrics import confidence_summary, edge_agreement
from app.core.geospatial import decode_sar, geotiff_bytes, preprocess_pair
from app.core.preprocess import ImageValidationError, to_display_array
from app.ml.model_runner import evaluation_status_for_model, get_runner, incompatible_input_message, runner_status

router = APIRouter(prefix="/api")
_results: dict[str, dict] = {}


def _png(image: Image.Image) -> bytes:
    buffer = io.BytesIO()
    image.save(buffer, format="PNG", optimize=True)
    return buffer.getvalue()


def _load_manifest() -> list[dict]:
    if not MANIFEST_PATH.is_file():
        return []
    with MANIFEST_PATH.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    return data.get("scenes", [])


def _find_scene(scene_id: str) -> dict:
    for scene in _load_manifest():
        if scene["id"] == scene_id:
            return scene
    raise HTTPException(status_code=404, detail=f"Unknown demo scene '{scene_id}'.")


def _cleanup() -> None:
    now = time.time()
    stale = [key for key, value in _results.items() if now - value["created"] > RESULT_TTL_SECONDS]
    for key in stale:
        _results.pop(key, None)
    while len(_results) > MAX_CACHED_RESULTS:
        _results.pop(next(iter(_results)))


def _store(payload: dict) -> str:
    _cleanup()
    result_id = uuid.uuid4().hex
    _results[result_id] = {"created": time.time(), **payload}
    return result_id


def _get_result(result_id: str) -> dict:
    value = _results.get(result_id)
    if value is None or time.time() - value["created"] > RESULT_TTL_SECONDS:
        raise HTTPException(status_code=404, detail="Result expired. Run the scene again.")
    return value


@router.get("/health")
def health() -> dict:
    status = runner_status()
    return {
        "status": "ok",
        "service": "vyora-inference",
        "mode": status.mode,
        "model_version": status.model_version,
        "is_ai_inference": status.is_ai_inference,
        "input_representation": status.input_representation,
        "accepted_model_input": (
            "grayscale paired PNG tile (single channel duplicated to two model channels)"
            if status.input_representation.startswith("grayscale_")
            else "two distinct VV/VH channels"
            if status.is_ai_inference
            else "image previews for labelled interface testing only; no trained model input contract"
        ),
        "checkpoint_available": status.checkpoint_available,
        "torch_available": status.torch_available,
        "runner_note": status.reason,
        "demo_scene_count": len(_load_manifest()),
        "disclaimer": DISCLAIMER,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/demo-scenes")
def demo_scenes() -> dict:
    scenes = [
        {
            "id": s["id"],
            "name": s["name"],
            "scene_type": s["scene_type"],
            "region_label": s["region_label"],
            "description": s["description"],
            "image_url": f"/api/demo-scenes/{s['id']}/image",
            "data_note": s["data_note"],
        }
        for s in _load_manifest()
    ]
    return {"scenes": scenes, "disclaimer": DISCLAIMER}


@router.get("/demo-scenes/{scene_id}/image")
def demo_scene_image(scene_id: str) -> Response:
    scene = _find_scene(scene_id)
    path = DEMO_DIR / scene["filename"]
    if not path.is_file():
        raise HTTPException(status_code=404, detail="Demo image file is missing.")
    return Response(path.read_bytes(), media_type="image/png", headers={"Cache-Control": "public, max-age=3600"})


@router.post("/infer")
async def infer(
    file: UploadFile | None = File(default=None),
    demo_scene_id: str | None = Form(default=None),
    source_type: str = Form(default="demo"),
) -> dict:
    started = time.perf_counter()
    if bool(file) == bool(demo_scene_id):
        raise HTTPException(
            status_code=400, detail="Provide either an image file or a demo_scene_id, not both."
        )

    if demo_scene_id:
        scene = _find_scene(demo_scene_id)
        path = DEMO_DIR / scene["filename"]
        if not path.is_file():
            raise HTTPException(status_code=404, detail="Demo image file is missing.")
        payload = path.read_bytes()
        filename, content_type, name = path.name, "image/png", scene["name"]
        source_kind = "demo"
    else:
        assert file is not None
        filename, content_type, name = file.filename or "upload", file.content_type, "Uploaded scene"
        payload = await file.read()
        source_kind = "upload"

    try:
        decoded = decode_sar(payload, filename, content_type)
        tile = preprocess_pair(decoded.channels)
    except ImageValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    runner = get_runner()
    incompatibility = incompatible_input_message(
        runner, decoded.input_kind, filename, is_synthetic_demo=(source_kind == "demo")
    )
    if incompatibility:
        raise HTTPException(status_code=400, detail=incompatibility)
    output = runner.infer(tile)
    runtime_ms = round((time.perf_counter() - started) * 1000, 1)

    preview_tile = tile.mean(axis=2)
    # VV=red, VH=green, mean=blue; this is a radar diagnostic composite, not optical RGB.
    dualpol_preview = np.clip(np.stack([tile[..., 0], tile[..., 1], preview_tile], axis=-1) * 255, 0, 255).astype(np.uint8)
    input_png = _png(Image.fromarray(dualpol_preview, mode="RGB"))
    colour_png = _png(Image.fromarray(output.colour, mode="RGB"))
    confidence_png = _png(Image.fromarray(output.confidence_image, mode="RGB"))
    conf_summary = confidence_summary(output.confidence)
    structural_proxy = round(edge_agreement(preview_tile, output.colour), 4)
    geo_png = geotiff_bytes(output.colour, decoded.profile) if decoded.profile else None

    summary = {
        "result_id": "",  # filled after the id is created
        "created_at": datetime.now(timezone.utc).isoformat(),
        "mode": output.mode,
        "model_version": output.model_version,
        "is_ai_inference": output.is_ai_inference,
        "source": {
            "type": source_kind,
            "name": name,
            "filename": filename,
            "scene_id": demo_scene_id if demo_scene_id else None,
        },
        "input": {
            "width": decoded.source_width, "height": decoded.source_height, "channels": 2,
            "polarizations": ["VV", "VH"] if decoded.input_kind == "geotiff-vv-vh" else ["duplicated grayscale preview", "not genuine dual-pol"],
            "input_kind": decoded.input_kind,
            "crs": decoded.crs, "transform": decoded.transform,
            "preprocessing": "independent 2nd-98th percentile normalization per VV/VH band, 3x3 median filter, resize to 256x256",
            "processing_note": "GeoTIFF must already be radiometrically calibrated, terrain-corrected and co-registered; this service only normalizes."
                if decoded.profile else "Preview channels are duplicated for interface testing; not genuine VV/VH input.",
        },
        "outputs": {"colour": "3-channel estimated interpretation PNG", "geotiff": "extent/CRS-preserving RGB preview" if geo_png else None},
        "feature_estimates": output.feature_estimates,
        "feature_method": output.feature_method,
        "confidence_summary": conf_summary,
        "confidence_method": output.confidence_method,
        "metrics": {
            "runtime_ms": runtime_ms,
            "input_output_edge_agreement_proxy": structural_proxy,
            "edge_method": "Pearson correlation of log Sobel-like gradients (structure proxy, not accuracy)",
            "held_out_evaluation": evaluation_status_for_model(output.model_version, output.is_ai_inference),
        },
        "disclaimer": DISCLAIMER,
        "privacy": "Uploaded bytes were processed in memory and not written to disk.",
    }
    result_id = _store(
        {
            "input_png": input_png,
            "colour_png": colour_png,
            "confidence_png": confidence_png,
            "geotiff": geo_png,
            "summary": summary,
        }
    )
    summary["result_id"] = result_id
    _results[result_id]["summary"] = summary
    summary["urls"] = {
        "input": f"/api/results/{result_id}/input",
        "colour": f"/api/results/{result_id}/image",
        "confidence": f"/api/results/{result_id}/confidence",
        "json": f"/api/results/{result_id}/export",
        "geotiff": f"/api/results/{result_id}/geotiff" if geo_png else None,
    }
    _results[result_id]["summary"] = summary
    return summary


@router.get("/results/{result_id}/image")
def result_image(result_id: str) -> Response:
    return Response(_get_result(result_id)["colour_png"], media_type="image/png")


@router.get("/results/{result_id}/confidence")
def result_confidence(result_id: str) -> Response:
    return Response(_get_result(result_id)["confidence_png"], media_type="image/png")


@router.get("/results/{result_id}/input")
def result_input(result_id: str) -> Response:
    return Response(_get_result(result_id)["input_png"], media_type="image/png")


@router.get("/results/{result_id}/geotiff")
def result_geotiff(result_id: str) -> Response:
    payload = _get_result(result_id).get("geotiff")
    if payload is None:
        raise HTTPException(status_code=404, detail="No geospatial metadata on this preview input.")
    return Response(payload, media_type="image/tiff", headers={"Content-Disposition": f'attachment; filename="vyora-{result_id[:8]}.tif"'})


@router.get("/results/{result_id}/export")
def result_export(result_id: str) -> Response:
    summary = _get_result(result_id)["summary"]
    return Response(
        json.dumps(summary, indent=2),
        media_type="application/json",
        headers={"Content-Disposition": f'attachment; filename="vyora-{result_id[:8]}.json"'},
    )
