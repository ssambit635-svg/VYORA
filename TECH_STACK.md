# DrishtiSAR — Technical Stack and Architecture

**Principles:** free/open-source first, no paid API, reliable local demo, phone-accessible UI, compact model, and clear separation between training and inference.

---

## 1. Stack at a glance

| Layer | Primary choice | Why it fits the MVP |
|---|---|---|
| Frontend | React + Vite + TypeScript | Fast responsive UI development and easy component structure |
| Styling | Tailwind CSS or scoped CSS | Rapid mobile-first design; choose one only to avoid setup overhead |
| Image comparison | Custom React slider or small open-source comparison component | Core visual interaction with minimal complexity |
| Charts | Recharts | Simple feature-score/confidence charts |
| Backend/API | Python FastAPI + Uvicorn | Good validation, automatic API docs, clean Python/ML integration |
| ML framework | PyTorch | Straightforward U-Net/ResU-Net training and inference |
| Image processing | Pillow + OpenCV | Image validation, resize, normalization, edge maps, optional despeckling |
| Raster support | Rasterio (stretch goal) | Read GeoTIFF only after PNG/JPEG workflow works |
| Model | Compact U-Net / ResU-Net | Stable, explainable image-to-image baseline suitable for small curated data |
| Metrics | scikit-image + NumPy | SSIM, edge maps, utility calculations |
| Data handling | Pandas + NumPy | Dataset manifests and reproducible preprocessing |
| Storage | Local filesystem + in-memory requests | No account/database needed for MVP |
| Tests | Pytest + frontend smoke tests | Fast API and inference-path validation |
| Version control | Git + GitHub | Reproducibility and submission evidence |

---

## 2. Recommended repository structure

```text
drishtisar/
├── README.md
├── LICENSE
├── .gitignore
├── docs/
│   ├── PRD.md
│   ├── PROJECT_DETAILS.md
│   ├── TECH_STACK.md
│   ├── APP_DOCUMENTATION_REQUIREMENTS.md
│   ├── ARCHITECTURE.md
│   ├── MODEL_CARD.md
│   ├── DATA_CARD.md
│   ├── API.md
│   ├── EVALUATION.md
│   └── DEMO_SCRIPT.md
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── api/
│   │   └── types/
│   └── package.json
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── api/
│   │   ├── services/
│   │   ├── ml/
│   │   ├── schemas/
│   │   └── core/
│   ├── requirements.txt
│   └── tests/
├── ml/
│   ├── notebooks/
│   ├── src/
│   │   ├── data.py
│   │   ├── model.py
│   │   ├── train.py
│   │   ├── evaluate.py
│   │   └── inference.py
│   ├── configs/
│   └── checkpoints/              # do not commit large checkpoints unless permitted
├── data/
│   ├── manifests/
│   ├── demo_samples/
│   └── README.md                 # source/licence instructions, not raw huge data
├── assets/
│   └── screenshots/
└── scripts/
    ├── run_local.sh
    └── validate_demo.py
```

---

## 3. Frontend specification

### Required screens

| Screen | Main elements |
|---|---|
| Home | Project statement, demo-scene cards, upload area, limitation notice |
| Processing | File details, progress state, cancellation/retry action |
| Results | Comparison slider, confidence toggle, feature cards, metrics, downloads |
| About/Method | Plain-language pipeline, data/source attribution, limitations |

### Core components

```text
AppShell
├── Header
├── ScenePicker
├── UploadDropzone
├── ProcessingState
├── ResultWorkspace
│   ├── ImageComparisonSlider
│   ├── ConfidenceOverlayToggle
│   ├── FeatureLikelihoodCards
│   ├── EvaluationMetrics
│   ├── DownloadPanel
│   └── LimitationNotice
└── MethodAndCredits
```

### Mobile requirements
- Design from 360 px width upward.
- Make all controls thumb-friendly (minimum ~44 px target).
- Stack result panels vertically on mobile.
- Do not use hover-only actions.
- Use text labels in addition to red/yellow/green confidence colours.
- Compress displayed images but retain original model result for export.

---

## 4. Backend/API specification

### API endpoints

| Method | Endpoint | Function |
|---|---|---|
| `GET` | `/api/health` | Verify server, model version, and readiness |
| `GET` | `/api/demo-scenes` | List packaged demo scenes and metadata |
| `POST` | `/api/infer` | Validate image, execute inference, return result metadata and URLs/base64 |
| `GET` | `/api/results/{id}/image` | Serve predicted output for session result |
| `GET` | `/api/results/{id}/confidence` | Serve confidence image for session result |
| `GET` | `/api/results/{id}/export` | Download JSON summary |

### `POST /api/infer` input contract

```json
{
  "file": "multipart image file",
  "source_type": "upload | demo",
  "demo_scene_id": "optional-demo-id"
}
```

### Result contract (example)

```json
{
  "result_id": "uuid",
  "model_version": "resunet-v0.1",
  "input": {
    "width": 256,
    "height": 256,
    "source_type": "demo"
  },
  "outputs": {
    "colour_image_url": "/api/results/uuid/image",
    "confidence_image_url": "/api/results/uuid/confidence"
  },
  "feature_estimates": {
    "water": 0.48,
    "vegetation": 0.27,
    "built_up": 0.18,
    "bare_other": 0.07
  },
  "confidence_summary": {
    "level": "medium",
    "mean": 0.74
  },
  "runtime_ms": 1320,
  "disclaimer": "AI-estimated geographic interpretation; not an official map or true-colour reconstruction."
}
```

### Upload safeguards
- Accept only documented MIME types.
- Limit files to 10 MB for MVP.
- Decode safely with Pillow/OpenCV and reject malformed files.
- Strip metadata where possible before storing/displaying.
- Do not retain uploads after the browser session/demo unless explicitly required.
- Rate limit locally if exposed on a shared network.

---

## 5. Model/training stack

### Model baseline

```text
Input: normalized 1 × 256 × 256 SAR tile
        ↓
ResU-Net encoder/decoder
        ↓
Output: 3 × 256 × 256 RGB-style colour interpretation
Optional: auxiliary feature-confidence head
```

### Data transformations

1. Load SAR and optical reference tile.
2. Confirm pair alignment and dataset split membership.
3. Apply SAR normalization (document method: e.g., percentile clipping + min-max scaling).
4. Resize/crop both tiles consistently to `256 × 256`.
5. Apply paired augmentations only to the training set.
6. Store a CSV/JSON manifest with source, scene group, split, and licence.

### Suggested dependencies

```text
python>=3.10
fastapi
uvicorn[standard]
pydantic
python-multipart
torch
torchvision
numpy
pandas
pillow
opencv-python-headless
scikit-image
scikit-learn
pytest
httpx
```

Training notebook can additionally use:

```text
jupyter
matplotlib
tqdm
albumentations   # optional; use only for paired transformations
rasterio         # optional GeoTIFF support
```

---

## 6. Confidence and metrics implementation

### Minimum confidence implementation
Use test-time augmentation on the input (for example, original + horizontal flip), invert outputs to a common orientation, and calculate agreement. Higher agreement means higher model consistency.

### Advanced confidence implementation
Enable dropout during repeated inference and use output variance to build an uncertainty heatmap.

### Metrics

| Metric | Purpose | Important rule |
|---|---|---|
| L1 / MAE | Basic colour-target difference | Report on a held-out set only |
| SSIM | Structural similarity | Use same preprocessing for baseline and model |
| Edge preservation | Boundary/structure retention | Document edge method and threshold |
| Inference latency | Demo feasibility | State device used and median over several runs |

---

## 7. Local-first deployment architecture

### Hackathon mode: recommended

```text
Laptop
├── FastAPI backend on 0.0.0.0:8000
├── built React files served by backend or a local frontend server
├── saved PyTorch model checkpoint
└── packaged demo images

Phones on same Wi-Fi
└── open http://LAPTOP-LAN-IP:8000
```

Advantages:
- no paid hosting;
- no dependency on an external API during judging;
- model stays on the laptop;
- phones can still interact with the application.

### Optional online mode
- Deploy the static React frontend to a free static host such as Vercel if it is available and permitted.
- Keep the ML API on a free CPU service only if it is tested well before judging.
- Never depend solely on a free hosted backend because cold starts, quotas, or network access can fail.

---

## 8. Development environment

| Need | Recommendation |
|---|---|
| Python runtime | Python 3.10 or 3.11 virtual environment |
| Model training | Free notebook GPU where available; local CPU fallback for tiny experiments |
| IDE | VS Code / Jupyter Notebook |
| Source control | Git repository with `.env`, raw data, and large checkpoints ignored |
| Package management | `pip` + `requirements.txt` for speed; lock versions before final demo |
| Browser testing | Chrome on laptop and Android Chrome on one real phone |

---

## 9. Testing checklist

### Backend
- Health endpoint reports model loaded.
- Every demo scene returns a valid output.
- Unsupported file, oversized file, and corrupt image return friendly errors.
- Result JSON includes all required fields.
- Inference works after server restart.

### Model
- Held-out metrics are saved with date/model version.
- Model checkpoint is bundled/accessible locally.
- Output size and value ranges are valid.
- Confidence output does not contain NaN/Inf.

### Frontend
- Home, demo, result, and download flows work at 360 px and desktop width.
- Compare slider can be used by touch.
- Confidence legend is readable without colour perception alone.
- No external image/CDN is necessary for the local demo.

### Presentation
- Demo runs once with internet disabled.
- A backup screen recording/screenshots are available.
- Team members can explain every displayed metric and limitation.

---

## 10. Technology decisions deliberately avoided

| Avoided choice | Reason |
|---|---|
| Paid generative-image or vision APIs | Violates no-payment constraint and weakens ML credibility |
| Large diffusion models | Too much compute/time; output may hallucinate geographic detail |
| GAN-first workflow | Training instability is risky for the available schedule |
| Live satellite APIs as a required feature | Network/API failures can break judging demo |
| Native Android application | Adds unnecessary build effort when a responsive web app meets phone need |
| Docker as a dependency for judging | Useful later, but not required for the fastest reliable MVP |
