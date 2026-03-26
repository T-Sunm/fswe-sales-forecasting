# Backend API Service

FastAPI service for sales forecasting inference and explainable AI (XAI) via SHAP.

## Features

- **Prediction** — Sales forecasts using a trained LightGBM model loaded from the filesystem.
- **XAI** — SHAP-based local and global feature importance, with Gemini AI natural-language summaries.
- **Analytics** — Aggregated sales and inventory queries from the `marts` layer in PostgreSQL.
- **Health** — Service liveness endpoint.

---

## Project Structure

```
backend/
├── src/
│   ├── api/
│   │   ├── main.py           # FastAPI app, middleware, router registration
│   │   ├── dependencies.py   # Shared dependencies (DB session, model)
│   │   ├── schemas.py        # Pydantic request/response models
│   │   └── routers/
│   │       ├── prediction.py # POST /api/v1/predict
│   │       ├── xai.py        # GET  /api/v1/xai/*
│   │       ├── analytics.py  # GET  /api/v1/analytics/*
│   │       ├── data.py       # GET  /api/v1/data/*
│   │       ├── models.py     # GET  /api/v1/models
│   │       └── health.py     # GET  /health
│   ├── core/
│   │   ├── model.py          # LightGBM loader from shared/models/
│   │   ├── forecasting.py    # Recursive forecasting logic
│   │   └── xai_explainer.py  # SHAP explainer + Gemini summarization
│   ├── data_loader/          # PostgreSQL connection & queries
│   └── config.py             # Settings and constants
├── run.py                    # Uvicorn entry point
├── pyproject.toml
└── .env.example
```

---

## Quick Start

### 1. Install dependencies

```bash
uv sync
```

### 2. Configure environment

```bash
cp .env.example .env
```

| Variable         | Description                    | Default     |
|------------------|--------------------------------|-------------|
| `GEMINI_API_KEY` | Google Gemini API key (XAI)    | *(required)*|
| `DEBUG`          | Enable debug mode              | `False`     |
| `API_HOST`       | Bind host                      | `0.0.0.0`  |
| `API_PORT`       | API port                       | `8000`      |
| `SECRET_KEY`     | Signing secret                 | *(change me)*|
| `DATABASE_URL`   | PostgreSQL connection string   | `postgresql://postgres:changeme@localhost:5432/sales_forecasting` |

### 3. Prepare model artifacts

The API loads the model directly from the shared filesystem — no model registry required.

```
shared/
└── models/
    ├── lgbm_baseline.pkl    # Trained LightGBM model
    └── feature_stats.json   # Feature statistics for preprocessing
```

If these files are missing, run the training pipeline first:

```bash
cd ../ml
uv run python scripts/train.py
```

### 4. Start PostgreSQL

```bash
cd ../data_pipeline/infra/postgres
docker-compose up -d
```

### 5. Run the API

```bash
# From the backend/ directory
python run.py

# Or directly via uvicorn:
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
```

Interactive docs available at: `http://localhost:8000/docs`

---

## API Endpoints

| Method | Path                      | Description                            |
|--------|---------------------------|----------------------------------------|
| `GET`  | `/health`                 | Service liveness check                 |
| `POST` | `/api/v1/predict`         | Generate a sales forecast              |
| `GET`  | `/api/v1/xai/local`       | SHAP local explanation for a prediction|
| `GET`  | `/api/v1/xai/global`      | SHAP global feature importance         |
| `GET`  | `/api/v1/analytics/*`     | Aggregated sales and inventory data    |
| `GET`  | `/api/v1/models`          | Info about the currently loaded model  |
