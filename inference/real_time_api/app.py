from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import numpy as np

app = FastAPI(title="Financial Risk Scoring API")

model = joblib.load("models/logreg.joblib")

class RiskRequest(BaseModel):
    tx_count: float
    avg_amount: float
    high_risk_mcc_count: float
    account_age_days: float
    credit_limit: float

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/score")
def score(req: RiskRequest):
    X = np.array([[req.tx_count, req.avg_amount, req.high_risk_mcc_count, req.account_age_days, req.credit_limit]])
    risk_score = float(model.predict_proba(X)[0][1])
    return {"risk_score": risk_score, "risk_flag": int(risk_score >= 0.5)}
