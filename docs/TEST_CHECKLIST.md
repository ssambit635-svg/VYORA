# Test checklist

Record format: date / tester / environment / result / notes.

## Automated results already recorded

| Date | Test | Environment | Result | Notes |
|---|---|---|---|---|
| 21 Nov 2026 | `pytest backend/tests ml/tests -q` (13 tests) | Python 3.11, FastAPI TestClient, Rasterio, PyTorch CPU | **PASS** | API honesty; synthetic scene flow; Int16 TIFF VV/VH round-trip with NoData + CRS/bounds; training-pair alignment and relative manifest-root checks; upload validation; dual-channel preprocessing; split-leakage rejection; 2→3 ResU-Net shape |
| 21 Nov 2026 | `npm run build` | Node 22, Vite 6.4.6, TypeScript strict | **PASS** | 181.5 kB JS / 22 kB CSS bundle generated with no type errors |
| 21 Nov 2026 | Live server smoke tests | Uvicorn `0.0.0.0:8000`, Streamlit `0.0.0.0:8501`, curl | **PASS** | API health/demo/inference and Streamlit home return 200; Streamlit AppTest ran the synthetic scene with no exceptions |
| 21 Nov 2026 | Regenerate demo data | `scripts/generate_demo_scenes.py` | **PASS** | Four deterministic 256×256 synthetic PNGs and manifest produced |
| 21 Nov 2026 | All four demo scenes end-to-end | `scripts/validate_demo.py` | **PASS** | Valid PNG dimensions, finite consistency visualization, feature shares sum to 1 |
| 21 Nov 2026 | Training/evaluation mechanics only | PyTorch CPU; temporary synthetic fixture and checkpoint in `/tmp` | **PASS** | 2-channel training, checkpoint loading, model-mode inference and MAE/PSNR/SSIM/edge evaluation ran. Synthetic fixture metrics are not results, are not in the report, and are not used as accuracy evidence |

## Manual checks — complete one full pass before judging

| Area | Test | Status | Device / browser | Notes |
|---|---|---|---|---|
| Model | All four demo scenes produce an output after a clean restart | Pending | Laptop | Use scripts/validate_demo.py |
| Model | Output has no NaN/Inf and valid dimensions | PASS (automated) | pytest | 256×256 PNG assets verified |
| API | Invalid type, corrupt file, oversized upload give clear errors | PASS (automated) | pytest | 400 responses asserted |
| API | Health fails clearly if checkpoint absent | PASS (automated) | pytest | Mode=development, checkpoint_available=false |
| UI | Demo works at desktop and Android/Chrome phone widths | **Pending real device** | Laptop + phone | CSS breakpoints defined at 1000/760/560 px; no browser binary in the build sandbox |
| UI | Slider and confidence toggle are touch usable | Pending real device | Phone | Pointer events + `touch-action: none`; keyboard arrows supported |
| UI | Disclaimer remains visible on result screen | PASS (code) | Laptop | Disclaimer box inside result side panel and mode banner |
| Local demo | Works with internet disabled after bundling | Pending | Laptop | All assets local; no external requests in frontend |
| Export | Output PNG and JSON download correctly | PASS (API) | pytest + curl | UI download links use same-origin URLs with `download` attributes |
| Pitch | Every member explains limitations and metrics | Pending | Team | Use docs/DEMO_SCRIPT.md and PITCH_OUTLINE.md |

## Suggested phone run

1. Find the laptop LAN IP: `hostname -I` (Linux) or `ipconfig` (Windows).
2. Phone and laptop on the same Wi-Fi; open `http://<LAN-IP>:8501` for the deck-aligned Streamlit interface. The optional React/FastAPI app is on port 8000.
3. Allow the firewall prompt for Python on private networks.
4. Run a synthetic preview and (if available) a prepared VV/VH GeoTIFF; confirm disclaimer, side-by-side view, consistency caveat and PNG/JSON/GeoTIFF preview exports.
5. Record device model, browser version, result and any bug in the table above.

## Known gaps / risks

- No real phone was available in the build environment; the mobile layout is implemented and statically reviewed but must be confirmed on hardware.
- No trained checkpoint or paired dataset exists: all model-mode, held-out metric and real-scene checks are intentionally blocked until data and training are added.
