# Sales Forecasting with Explainable AI (XAI)

## Executive Summary

This repository defines an integrated sales forecasting system resolving the Walmart Recruiting II Sales in Stormy Weather analytical challenge. The defining problem requires predictive algorithms to quantify how severe meteorological phenomena influence the purchasing velocity of weather-sensitive retail inventory across diverse geographic locations. The foundational training data originates directly from the official Kaggle competition registry [//www.kaggle.com/competitions/walmart-recruiting-sales-in-stormy-weather].

The technical implementation unifies a centralized data warehouse methodology with a structured Machine Learning Operations pipeline. The infrastructure relies on PostgreSQL as the foundational Relational Database Management System. Data Build Tool executes structured query logic to map raw inputs into analytical dimensional models. The machine learning sequence incorporates Optuna for mathematical hyperparameter optimization. A FastAPI application serves inference payloads. A Streamlit graphical interface visualizes Explainable Artificial Intelligence interpretations.

## Architectural Hierarchy

![System Integration Architecture](images/main.png)

The physical distribution of files reflects stringent structural separation defining specific operational scopes.

```text
sales_forecasting_xai/
├── backend/                # Application Programming Interface network endpoints
├── data_pipeline/          # Database runtime and analytical query formulation
│   ├── dbt/                # Data Build Tool dimensional transformations
│   └── infra/              # Virtual container orchestration definitions
├── web_ui/               # Graphical interface application elements
├── ml/                     # Machine learning algorithms and tuning matrices
└── shared/                 # Centralized parameter targets and temporary local storage
```

The operational domains enforce strict capability boundaries.

| Directory Module | Evaluated Capability |
|---|---|
| data_pipeline | Database infrastructure provisioning alongside analytical logic aggregation |
| ml | Predictive algorithm mathematical training and modeling configurations |
| shared | Global variable assignments enforcing parameter inheritance |
| backend | Endpoint mapping logic distributing trained model inferences |
| web_ui | Graphical translation protocols analyzing interpretation patterns |

## Deployment Strategy

### Required Dependencies

The implementation requires specific host libraries.

* A container runtime environment
* Python version 3.10 and above
* The uv package manager
* Free network ports spanning 5432 for database access
* Free network ports spanning 8000 for backend routing and 8501 for frontend display

### Execution Sequence

Step 1. Start PostgreSQL.
```bash
cd data_pipeline/infra/postgres
docker compose up -d
```

Step 2. Prepare data and train the model.
```bash
cd ml
uv run python scripts/prepare_data.py
uv run python scripts/tune.py
uv run python scripts/train.py --best-params outputs/best_params.json
```

Step 3. Start backend and frontend from the project root.
```bash
docker compose up -d
```

- Backend API: `http://localhost:8000` — docs at `/docs`
- Dashboard: `http://localhost:8501`

## Environment Configuration

The application authenticates using variables located within the root environment configuration file.

| Environment Variable | Operational Boundary |
|---|---|
| POSTGRES_USER | Master username for PostgreSQL authentication |
| POSTGRES_PASSWORD | Security key for PostgreSQL access |
| POSTGRES_DB | Target database namespace |
| POSTGRES_HOST | Database host network address |
| POSTGRES_PORT | Database communication port |

## Strategic Decisions

The system topology reflects precise engineering decisions.

* PostgreSQL and Data Build Tool. PostgreSQL provides a standard relational engine simplifying data persistence. Data Build Tool guarantees idempotency and testability for SQL transformations.
* Optuna. Optuna applies mathematical optimization techniques to replace exhaustive grid search matrices.
* FastAPI and Streamlit. FastAPI implements asynchronous task execution supporting simultaneous client connections. Streamlit facilitates the mathematical translation of Explainable Artificial Intelligence matrices into visual representation charts.

## Navigation Guide

The repository enforces modular separation of concerns.

1. Application Frontend. Evaluates the interactive components and Explainable Artificial Intelligence frameworks.
2. Application Backend. Outlines the prediction rendering boundaries.
3. Machine Learning Logic. Describes the pipeline constructing the LightGBM models.
4. Database Infrastructure. Contextualizes the containerized PostgreSQL environment.
5. Analytical Models. Delineates the Data Build Tool structured queries.
6. Shared Resources. Identifies centralized parameter constraints and local staging records.
