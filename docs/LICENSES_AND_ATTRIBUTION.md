# Licences and attribution

## Project content

- Application code, documentation and procedural demo generator: created for this hackathon project; no third-party code copied.
- Demo scene PNGs: generated locally by `scripts/generate_demo_scenes.py` from this repository. No external imagery, no third-party licence obligations. Clearly labelled synthetic.
- Icons: `lucide-react` (ISC licence) via npm. At runtime the built bundle contains only the icons used.
- No external fonts, stock photos, map tiles, audio or video are bundled.

## Open-source dependencies

| Dependency | Licence | Use |
|---|---|---|
| React / React DOM | MIT | Frontend UI |
| Vite | MIT | Frontend build |
| TypeScript | Apache-2.0 | Frontend type checking |
| lucide-react | ISC | Icons |
| FastAPI | MIT | HTTP API |
| Starlette / Uvicorn | BSD-3-Clause / BSD-3-Clause | ASGI server |
| Pydantic | MIT | Validation (via FastAPI) |
| Pillow | HPND | Image decode / PNG export |
| NumPy | BSD-3-Clause | Preprocessing and metrics |
| PyTorch (optional, model mode) | BSD-3-Clause | Training and checkpoint inference |
| Rasterio | BSD-3-Clause | GeoTIFF read/write and CRS metadata |
| Streamlit (optional UI) | Apache-2.0 | Deck-aligned local interface |
| pytest / httpx | MIT / BSD-3-Clause | Tests |

Installed dependency versions are recorded in `frontend/package.json`, `frontend/package-lock.json` and `backend/requirements.txt`.

## Data attribution

No external dataset is used. If licensed SAR/optical imagery is added later, record its exact source URL, access date, licence and required credit in `docs/DATA_CARD.md` and update this file before submission.
