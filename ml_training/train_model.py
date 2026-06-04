import pandas as pd
import numpy as np
import joblib
import json
from pathlib import Path
from sklearn.model_selection import train_test_split, StratifiedKFold
from sklearn.metrics import (
    classification_report, roc_auc_score,
    average_precision_score, confusion_matrix
)
from sklearn.preprocessing import StandardScaler
import xgboost as xgb
import shap

try:
    import mlflow
    import mlflow.xgboost
    MLFLOW_AVAILABLE = True
except Exception:
    MLFLOW_AVAILABLE = False

# ─── CONFIG ───────────────────────────────────────────────
FEATURES_PATH = Path("data/features/account_features.parquet")
MODEL_DIR = Path("models")
THRESHOLD = 0.35  # Lower threshold for fraud — recall matters more than precision

FEATURE_COLS = [
    "tx_count", "avg_amount", "max_amount", "std_amount",
    "total_amount", "unique_mcc_count", "high_risk_mcc_count",
    "late_night_ratio", "online_ratio", "international_ratio",
    "account_age_days", "credit_limit", "utilization_ratio",
    "kyc_verified", "late_night_tx_count", "online_tx_count",
    "international_tx_count"
]

def load_features() -> tuple:
    print("Loading features...")
    df = pd.read_parquet(FEATURES_PATH)
    X = df[FEATURE_COLS].fillna(0)
    y = df["label"]
    print(f"  Dataset shape: {X.shape}")
    print(f"  Fraud rate: {y.mean():.2%}")
    return X, y

def train_model(X_train, y_train):
    """Train XGBoost with class weight balancing for imbalanced fraud data."""
    print("\nTraining XGBoost model...")

    scale_pos_weight = (y_train == 0).sum() / (y_train == 1).sum()
    print(f"  Class imbalance ratio: {scale_pos_weight:.1f}x — applying scale_pos_weight")

    model = xgb.XGBClassifier(
        n_estimators=500,
        max_depth=6,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        scale_pos_weight=scale_pos_weight,
        use_label_encoder=False,
        eval_metric="aucpr",
        early_stopping_rounds=30,
        random_state=42,
        n_jobs=-1
    )

    X_tr, X_val, y_tr, y_val = train_test_split(
        X_train, y_train, test_size=0.15, stratify=y_train, random_state=42
    )

    model.fit(
        X_tr, y_tr,
        eval_set=[(X_val, y_val)],
        verbose=50
    )

    print(f"  Best iteration: {model.best_iteration}")
    return model

def evaluate_model(model, X_test, y_test):
    """Comprehensive model evaluation."""
    print("\nEvaluating model...")

    probs = model.predict_proba(X_test)[:, 1]
    preds = (probs >= THRESHOLD).astype(int)

    auc_roc = roc_auc_score(y_test, probs)
    auc_pr = average_precision_score(y_test, probs)
    cm = confusion_matrix(y_test, preds)

    print(f"\n  ROC-AUC:  {auc_roc:.4f}")
    print(f"  PR-AUC:   {auc_pr:.4f}")
    print(f"\n  Confusion Matrix:")
    print(f"  TN={cm[0][0]:,}  FP={cm[0][1]:,}")
    print(f"  FN={cm[1][0]:,}  TP={cm[1][1]:,}")
    print(f"\n{classification_report(y_test, preds)}")

    metrics = {
        "roc_auc": float(auc_roc),
        "pr_auc": float(auc_pr),
        "threshold": THRESHOLD,
        "true_negatives": int(cm[0][0]),
        "false_positives": int(cm[0][1]),
        "false_negatives": int(cm[1][0]),
        "true_positives": int(cm[1][1]),
    }

    return metrics, probs

def compute_shap(model, X_test, feature_cols):
    """Compute SHAP values for model explainability."""
    print("\nComputing SHAP values...")
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X_test[:500])

    # Top features by mean absolute SHAP
    mean_shap = np.abs(shap_values).mean(axis=0)
    feature_importance = pd.DataFrame({
        "feature": feature_cols,
        "mean_shap": mean_shap
    }).sort_values("mean_shap", ascending=False)

    print("\n  Top 10 Features by SHAP importance:")
    print(feature_importance.head(10).to_string(index=False))

    return feature_importance

def save_artifacts(model, metrics, feature_importance):
    """Save model and evaluation artifacts."""
    MODEL_DIR.mkdir(exist_ok=True)

    # Save model
    model_path = MODEL_DIR / "xgb_fraud_model.joblib"
    joblib.dump(model, model_path)
    print(f"\n✅ Saved model to {model_path}")

    # Save metrics
    metrics_path = MODEL_DIR / "metrics.json"
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"✅ Saved metrics to {metrics_path}")

    # Save feature importance
    fi_path = MODEL_DIR / "feature_importance.csv"
    feature_importance.to_csv(fi_path, index=False)
    print(f"✅ Saved feature importance to {fi_path}")

def main():
    print("=" * 50)
    print("Financial Risk ML Platform — Model Training")
    print("=" * 50)

    X, y = load_features()

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, stratify=y, random_state=42
    )
    print(f"\n  Train: {len(X_train):,} | Test: {len(X_test):,}")

    if MLFLOW_AVAILABLE:
        mlflow.set_experiment("financial-risk-ml-platform")
        with mlflow.start_run():
            model = train_model(X_train, y_train)
            metrics, probs = evaluate_model(model, X_test, y_test)
            feature_importance = compute_shap(model, X_test, FEATURE_COLS)
            save_artifacts(model, metrics, feature_importance)
            mlflow.log_params({
                "model": "xgboost",
                "n_estimators": 500,
                "max_depth": 6,
                "threshold": THRESHOLD
            })
            mlflow.log_metrics({k: v for k, v in metrics.items() if isinstance(v, float)})
            mlflow.xgboost.log_model(model, artifact_path="model")
            print("✅ Logged to MLflow")
    else:
        model = train_model(X_train, y_train)
        metrics, probs = evaluate_model(model, X_test, y_test)
        feature_importance = compute_shap(model, X_test, FEATURE_COLS)
        save_artifacts(model, metrics, feature_importance)

    print("\n✅ Training pipeline complete!")

if __name__ == "__main__":
    main()