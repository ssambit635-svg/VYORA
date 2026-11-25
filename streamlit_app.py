"""Deck-aligned Streamlit interface for the same local Vyora inference pipeline.

Run: streamlit run streamlit_app.py --server.address 0.0.0.0
The React/FastAPI app remains available as the richer API/UI variant.
"""
from __future__ import annotations

import io
import json
import sys
from pathlib import Path

import numpy as np
import streamlit as st
from PIL import Image

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "backend"))
from app.core.config import DEMO_DIR, MANIFEST_PATH
from app.core.geospatial import decode_sar, geotiff_bytes, preprocess_pair
from app.ml.model_runner import get_runner, incompatible_input_message, runner_status

st.set_page_config(page_title="Vyora | SAR interpretation", page_icon="🛰️", layout="wide")
st.markdown("""
<style>
:root { --ink:#e9f3f5; --muted:#9bb3ba; --panel:#10252d; --line:#23424a; --teal:#52e0c0; }
.stApp { background: radial-gradient(circle at 80% 0%, #163b45, #071419 48%); color:var(--ink); }
[data-testid="stSidebar"] { background:#0a1c22; }
h1,h2,h3,p,label { color:var(--ink)!important; }
[data-testid="stMetric"] { background:var(--panel); border:1px solid var(--line); padding:1rem; border-radius:12px; }
.vyora-note { border:1px solid #32635d; border-radius:12px; padding:1rem; background:#102b2b; }
</style>
""", unsafe_allow_html=True)

st.title("VYORA · SAR → optical-style visual interpretation")
st.caption("HK26-PS-19 · dual-polarization VV/VH workflow · local inference · not a warning product")
status = runner_status()
if status.is_ai_inference:
    st.success(f"Model checkpoint active: {status.model_version} · input representation: {status.input_representation}")
else:
    st.warning("DEVELOPMENT MODE — no trained AI checkpoint is loaded. The output is a rule-based interface demonstration, not model inference.")

is_png_checkpoint = (
    status.is_ai_inference
    and status.input_representation.startswith("grayscale_")
    and status.input_representation.endswith("_PNG_duplicated")
)
with MANIFEST_PATH.open(encoding="utf-8") as handle:
    scenes = json.load(handle).get("scenes", [])
labels = {scene["name"]: scene for scene in scenes}
if is_png_checkpoint:
    source_kind = "Upload grayscale PNG tile"
    st.info("This checkpoint is trained on grayscale paired PNG tiles. It cannot accept a true VV/VH GeoTIFF.")
else:
    source_kind = st.radio("Input source", ["Bundled demo preview", "Upload SAR raster"], horizontal=True)
source_path = None
upload = None
if source_kind == "Bundled demo preview":
    selected = st.selectbox("Synthetic demo scene", list(labels))
    scene = labels[selected]
    source_path = DEMO_DIR / scene["filename"]
    st.info(scene["data_note"])
else:
    if is_png_checkpoint:
        upload = st.file_uploader("Upload a grayscale PNG tile from your paired dataset.", type=["png"])
    else:
        upload = st.file_uploader("Upload a calibrated, co-registered Sentinel-1 GeoTIFF (VV band 1, VH band 2). PNG/JPEG are previews only, not true dual-pol.", type=["tif", "tiff", "png", "jpg", "jpeg"])

if st.button("Interpret scene", type="primary", width="stretch"):
    try:
        if upload is not None:
            payload, filename = upload.getvalue(), upload.name
        elif source_path is not None:
            payload, filename = source_path.read_bytes(), source_path.name
        else:
            st.stop()
        decoded = decode_sar(payload, filename)
        tile = preprocess_pair(decoded.channels)
        runner = get_runner()
        incompatibility = incompatible_input_message(runner, decoded.input_kind, filename)
        if incompatibility:
            raise ValueError(incompatibility)
        output = runner.infer(tile)
        mean_band = tile.mean(axis=-1)
        # VV=red, VH=green, mean=blue; a diagnostic radar composite, not optical RGB.
        radar_rgb = np.clip(np.stack((tile[..., 0], tile[..., 1], mean_band), axis=-1) * 255, 0, 255).astype(np.uint8)
        before = Image.fromarray(radar_rgb, mode="RGB")
        input_caption = (
            "Grayscale PNG input (duplicated model channels)"
            if decoded.input_kind == "single-channel-preview-duplicated"
            else "VV/VH radar composite (VV red, VH green; not optical RGB)"
        )
        after = Image.fromarray(output.colour, mode="RGB")
        confidence = Image.fromarray(output.confidence_image, mode="RGB")
        st.session_state["vyora_result"] = {
            "before": before, "after": after, "confidence": confidence,
            "output": output, "decoded": decoded, "input_caption": input_caption,
        }
    except Exception as error:
        st.error(f"Could not interpret this input: {error}")

result = st.session_state.get("vyora_result")
if result:
    output, decoded = result["output"], result["decoded"]
    st.markdown('<div class="vyora-note">Estimated appearance only. SAR measures returned microwave energy; output is not recovered true colour, a calibrated analytical raster, or an official map.</div>', unsafe_allow_html=True)
    left, right = st.columns(2)
    left.image(result["before"], caption=result["input_caption"], width="stretch")
    right.image(result["after"], caption="Estimated optical-style RGB layer", width="stretch")
    show_confidence = st.toggle("Show flip-view consistency layer (not calibrated uncertainty)")
    if show_confidence:
        st.image(result["confidence"], caption=output.confidence_method, width="stretch")
    m1, m2, m3 = st.columns(3)
    m1.metric("Model", output.model_version)
    m2.metric("Inference mode", "AI checkpoint" if output.is_ai_inference else "Development fallback")
    m3.metric("Input", decoded.input_kind)
    if output.feature_estimates:
        st.subheader("Palette-derived scene shares (not learned classes or validated segmentation)")
        cols = st.columns(4)
        for col, (name, share) in zip(cols, output.feature_estimates.items()):
            col.metric(name.replace("_", " ").title(), f"{share * 100:.1f}%")
    else:
        st.info("This checkpoint predicts image pixels only; no water/vegetation/building classifier is included.")
    png = io.BytesIO()
    result["after"].save(png, format="PNG")
    st.download_button("Download estimated PNG", png.getvalue(), "vyora-estimated.png", "image/png")
    if decoded.profile:
        tif_bytes = geotiff_bytes(output.colour, decoded.profile)
        st.download_button("Download extent/CRS-preserving GeoTIFF preview", tif_bytes, "vyora-estimated-preview.tif", "image/tiff")
    st.download_button("Download result JSON", json.dumps({
        "mode": output.mode, "model_version": output.model_version,
        "is_ai_inference": output.is_ai_inference, "input_kind": decoded.input_kind,
        "crs": decoded.crs, "transform": decoded.transform,
        "feature_estimates": output.feature_estimates,
        "confidence_method": output.confidence_method,
        "disclaimer": "Estimated visual interpretation; not true-colour ground truth or an official map.",
    }, indent=2), "vyora-result.json", "application/json")

st.divider()
st.caption(
    "Current checkpoint: grayscale paired PNG prototype; see docs/EVALUATION.md. "
    "It is not a verified Sentinel-1 VV/VH → Sentinel-2 model. GeoTIFF support in the pipeline requires a separately trained VV/VH checkpoint."
    if is_png_checkpoint else
    "GeoTIFF inputs must already be calibrated, terrain-corrected and co-registered. "
    "The current backend performs robust normalization only; it does not perform physical SAR calibration."
)
