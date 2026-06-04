# Financial Risk ML Platform

A production-grade machine learning platform for real-time financial fraud detection and risk scoring — built with XGBoost, FastAPI, Docker, and MLflow.

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![XGBoost](https://img.shields.io/badge/XGBoost-2.0-orange)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green)
![MLflow](https://img.shields.io/badge/MLflow-2.0+-red)
![Docker](https://img.shields.io/badge/Docker-ready-blue)

---

## Overview

This platform simulates an enterprise-scale fraud detection system processing **200,000+ daily financial transactions** across **5,000 accounts** — detecting anomalous patterns using behavioral feature engineering, gradient boosting models, and real-time inference APIs.

**Key Results:**
- ROC-AUC: ~0.92 on held-out test set
- PR-AUC: ~0.85 (critical for imbalanced fraud data)
- Inference latency: <3ms per transaction
- Fraud detection at 2.5% base rate with class imbalance handling

---

## Architecture

data_ingestion/          # Synthetic transaction data generation
generate_data.py         # 200K transactions with realistic fraud patterns
feature_engineering/     # Account-level behavioral features
build_features.py        # 17 engineered features from raw transactions
ml_training/             # Model training with XGBoost + SHAP
train_model.py           # XGBoost, early stopping, MLflow tracking
inference/               # Production FastAPI scoring service
app.py                   # Real-time + batch scoring endpoints
batch_scoring.py         # Offline batch pipeline
models/                  # Saved artifacts
xgb_fraud_model.joblib
metrics.json
feature_importance.csv
Dockerfile               # Containerized deployment
docker-compose.yml       # Full stack with MLflow

---

## Features Engineered

| Feature | Description |
|---|---|
| tx_count | Total transaction count per account |
| avg_amount | Average transaction amount |
| max_amount | Maximum single transaction amount |
| std_amount | Amount volatility |
| high_risk_mcc_count | Transactions at high-risk merchants |
| late_night_ratio | Ratio of 12AM-4AM transactions |
| international_ratio | Ratio of international transactions |
| online_ratio | Ratio of online channel transactions |
| utilization_ratio | Avg amount / credit limit |
| kyc_verified | KYC verification status |

---

## Fraud Patterns Detected

- **High-value anomalies** — Transactions significantly above account baseline
- **High-risk merchant activity** — Gambling, wire transfers, crypto exchanges
- **Late-night behavior** — Unusual transaction timing patterns
- **International velocity** — Abnormal international transaction ratios

---

## Model Performance

| Metric | Value |
|---|---|
| ROC-AUC | ~0.92 |
| PR-AUC | ~0.85 |
| Threshold | 0.35 (optimized for recall) |
| Training data | 160,000 accounts |
| Test data | 40,000 accounts |

**Why PR-AUC matters for fraud:** ROC-AUC can be misleadingly high on imbalanced datasets. PR-AUC directly measures performance on the minority (fraud) class — the metric that actually matters in production.

---

## API Endpoints

### Single Transaction Scoring
```bash
POST /score
{
  "account_id": "ACC000123",
  "tx_count": 45,
  "avg_amount": 120.50,
  "high_risk_mcc_count": 2,
  ...
}
```

Response:
```json
{
  "account_id": "ACC000123",
  "risk_score": 0.7823,
  "risk_flag": 1,
  "risk_level": "HIGH",
  "inference_time_ms": 2.4,
  "timestamp": "2024-06-04T14:30:00"
}
```

### Batch Scoring (up to 1000 transactions)
```bash
POST /score/batch
```

### Health Check
```bash
GET /health
GET /model/info
```

---

## Quick Start

**1. Install dependencies**
```bash
pip install -r requirements.txt
```

**2. Generate data**
```bash
python data_ingestion/generate_data.py
```

**3. Build features**
```bash
python feature_engineering/build_features.py
```

**4. Train model**
```bash
python ml_training/train_model.py
```

**5. Start API**
```bash
uvicorn inference.app:app --reload --port 8000
```

**6. Run with Docker**
```bash
docker-compose up
```

**7. View API docs**

http://localhost:8000/docs

---

## MLflow Experiment Tracking

```bash
mlflow ui
# Visit http://localhost:5000
```

Tracks: model parameters, ROC-AUC, PR-AUC, confusion matrix, feature importance

---

## Tech Stack

| Layer | Technology |
|---|---|
| Model | XGBoost 2.0 with early stopping |
| Explainability | SHAP TreeExplainer |
| API | FastAPI + Pydantic v2 |
| Experiment Tracking | MLflow |
| Containerization | Docker + Docker Compose |
| Data Format | Parquet (columnar, production standard) |
| Language | Python 3.10+ |

---

## Key Engineering Decisions

**Why XGBoost over deep learning?**
Gradient boosting outperforms neural networks on tabular financial data — faster training, better interpretability, and production-proven reliability in regulated environments.

**Why threshold 0.35 instead of 0.5?**
In fraud detection, false negatives (missed fraud) are more costly than false positives (unnecessary reviews). Lowering the threshold increases recall at the cost of some precision — the right tradeoff for financial risk.

**Why PR-AUC as primary metric?**
With 2.5% fraud rate, a model predicting all non-fraud achieves 97.5% accuracy. PR-AUC directly measures precision-recall tradeoff on the minority class — the only metric that matters for fraud detection.

---

## Author

**Geetha Bommareddy** — AI/ML Engineer | JPMC
[LinkedIn](https://www.linkedin.com/in/geethareddy521) | [Portfolio](https://geethareddy14.github.io/GeethaReddy-PortFolio/)