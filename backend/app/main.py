"""FastAPI application and optional static frontend hosting (single-port LAN demo)."""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes import router
from app.core.config import FRONTEND_DIST

app = FastAPI(
    title="Vyora Inference API",
    version="0.1.0",
    description="Confidence-aware SAR interpretation demonstrator. Local-first, no paid services.",
)

# Phones on the same Wi-Fi reach the backend through the laptop's LAN address.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)
app.include_router(router)


@app.get("/api", include_in_schema=False)
def api_root() -> JSONResponse:
    return JSONResponse({"service": "Vyora API", "docs": "/docs", "health": "/api/health"})


if FRONTEND_DIST.is_dir() and (FRONTEND_DIST / "index.html").is_file():
    app.mount("/", StaticFiles(directory=FRONTEND_DIST, html=True), name="frontend")
