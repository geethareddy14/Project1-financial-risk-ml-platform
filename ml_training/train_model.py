import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, roc_auc_score
from sklearn.linear_model import LogisticRegression

# Optional MLflow: if installed, it will log params/metrics
try:
    import mlflow
    import mlflow.sklearn
    MLFLOW_AVAILABLE = True
except Exception:
    MLFLOW_AVAILABLE = False


def main():
    # Demo: read the Gold feature table output.
    # If you're running this locally, convert parquet -> csv first, OR use pandas with pyarrow.
    # For simplicity, we expect a CSV export here (we'll add export later).
    df = pd.read_csv("out/gold/risk_features.csv")

    # Target label (demo): fraud_label_sum > 0
    df["label"] = (df["fraud_label_sum"] > 0).astype(int)

    feature_cols = ["tx_count", "avg_amount", "high_risk_mcc_count", "account_age_days", "credit_limit"]
    X = df[feature_cols].fillna(0)
    y = df["label"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )

    model = LogisticRegression(max_iter=1000)
    model.fit(X_train, y_train)

    probs = model.predict_proba(X_test)[:, 1]
    preds = (probs >= 0.5).astype(int)

    auc = roc_auc_score(y_test, probs) if len(set(y_test)) > 1 else None

    print("=== Classification Report ===")
    print(classification_report(y_test, preds))
    print("ROC-AUC:", auc)

    if MLFLOW_AVAILABLE:
        mlflow.set_experiment("financial-risk-ml-platform")
        with mlflow.start_run():
            mlflow.log_param("model", "logreg")
            mlflow.log_param("threshold", 0.5)
            if auc is not None:
                mlflow.log_metric("roc_auc", float(auc))
            mlflow.sklearn.log_model(model, artifact_path="model")
        print("✅ Logged run to MLflow.")


if __name__ == "__main__":
    main()
