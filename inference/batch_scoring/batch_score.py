import pandas as pd
import joblib
from pathlib import Path

MODEL_PATH = Path("models/logreg.joblib")

def main():
    # Expecting the same CSV used for training (demo)
    df = pd.read_csv("out/gold/risk_features.csv")

    feature_cols = ["tx_count", "avg_amount", "high_risk_mcc_count", "account_age_days", "credit_limit"]
    X = df[feature_cols].fillna(0)

    # For demo: load model saved locally (you can also load from MLflow later)
    model = joblib.load(MODEL_PATH)

    df["risk_score"] = model.predict_proba(X)[:, 1]
    df["risk_flag"] = (df["risk_score"] >= 0.5).astype(int)

    Path("out/predictions").mkdir(parents=True, exist_ok=True)
    df.to_csv("out/predictions/batch_scored.csv", index=False)

    print("✅ Wrote predictions to out/predictions/batch_scored.csv")


if __name__ == "__main__":
    main()
