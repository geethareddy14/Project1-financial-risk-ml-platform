from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field, validator
from typing import Optional
import joblib
import numpy as np
import json
import time
import logging
from pathlib import Path
from datetime import datetime

# ─── LOGGING ──────────────────────────────────────────────
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ─── APP SETUP ────────────────────────────────────────────
app = FastAPI(
    title="Financial Risk Scoring API",
    description="Real-time fraud detection and risk scoring for financial transactions",
    version="2.0.0"
)

# ─── MODEL LOADING ────────────────────────────────────────
MODEL_PATH = Path("models/xgb_fraud_model.joblib")
METRICS_PATH = Path("models/metrics.json")
THRESHOLD = 0.35

model = None
model_metrics = {}

@app.on_event("startup")
def load_model():
    global model, model_metrics
    try:
        model = joblib.load(MODEL_PATH)
        logger.info(f"✅ Model loaded from {MODEL_PATH}")
        if METRICS_PATH.exists():
            with open(METRICS_PATH) as f:
                model_metrics = json.load(f)
            logger.info(f"✅ Model metrics loaded — ROC-AUC: {model_metrics.get('roc_auc', 'N/A')}")
    except Exception as e:
        logger.error(f"❌ Failed to load model: {e}")

# ─── REQUEST / RESPONSE SCHEMAS ──