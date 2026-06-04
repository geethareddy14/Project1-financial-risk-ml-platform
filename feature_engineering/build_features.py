import pandas as pd
import numpy as np
from pathlib import Path

RAW_DIR = Path("data/raw")
FEATURES_DIR = Path("data/features")

def load_data() -> tuple:
    print("Loading raw data...")
    accounts = pd.read_parquet(RAW_DIR / "accounts.parquet")
    transactions = pd.read_parquet(RAW_DIR / "transactions.parquet")
    print(f"  Loaded {len(accounts):,} accounts, {len(transactions):,} transactions")
    return accounts, transactions

def build_account_features(transactions: pd.DataFrame) -> pd.DataFrame:
    """Build aggregated account-level features."""
    print("Building account features...")

    HIGH_RISK_MCC = [5912, 7995, 5999, 4829, 6051]

    agg = transactions.groupby("account_id").agg(
        tx_count=("transaction_id", "count"),
        avg_amount=("amount", "mean"),
        max_amount=("amount", "max"),
        std_amount=("amount", "std"),
        total_amount=("amount", "sum"),
        unique_mcc_count=("mcc_code", "nunique"),
        international_tx_count=("is_international", "sum"),
        fraud_label_sum=("is_fraud", "sum"),
    ).reset_index()

    # High risk MCC count
    high_risk = transactions[transactions["mcc_code"].isin(HIGH_RISK_MCC)]
    high_risk_counts = high_risk.groupby("account_id").size().reset_index(name="high_risk_mcc_count")
    agg = agg.merge(high_risk_counts, on="account_id", how="left")
    agg["high_risk_mcc_count"] = agg["high_risk_mcc_count"].fillna(0)

    # Late night transaction ratio
    late_night = transactions[transactions["hour_of_day"].isin([0,1,2,3,4])]
    late_night_counts = late_night.groupby("account_id").size().reset_index(name="late_night_tx_count")
    agg = agg.merge(late_night_counts, on="account_id", how="left")
    agg["late_night_tx_count"] = agg["late_night_tx_count"].fillna(0)
    agg["late_night_ratio"] = agg["late_night_tx_count"] / agg["tx_count"]

    # Online transaction ratio
    online = transactions[transactions["channel"] == "online"]
    online_counts = online.groupby("account_id").size().reset_index(name="online_tx_count")
    agg = agg.merge(online_counts, on="account_id", how="left")
    agg["online_tx_count"] = agg["online_tx_count"].fillna(0)
    agg["online_ratio"] = agg["online_tx_count"] / agg["tx_count"]

    # International ratio
    agg["international_ratio"] = agg["international_tx_count"] / agg["tx_count"]

    # Fill NaN std for accounts with single transaction
    agg["std_amount"] = agg["std_amount"].fillna(0)

    return agg

def build_final_features(accounts: pd.DataFrame, agg: pd.DataFrame) -> pd.DataFrame:
    """Merge account metadata with aggregated features."""
    print("Building final feature set...")

    features = agg.merge(accounts, on="account_id", how="left")

    # Binary label — any fraud transaction on this account
    features["label"] = (features["fraud_label_sum"] > 0).astype(int)

    # Utilization ratio
    features["utilization_ratio"] = features["avg_amount"] / features["credit_limit"].clip(lower=1)

    # KYC flag
    features["kyc_verified"] = features["kyc_verified"].astype(int)

    print(f"  Feature set shape: {features.shape}")
    print(f"  Fraud accounts: {features['label'].sum():,} ({features['label'].mean():.2%})")

    return features

def main():
    print("=" * 50)
    print("Financial Risk ML Platform — Feature Engineering")
    print("=" * 50)

    accounts, transactions = load_data()
    agg = build_account_features(transactions)
    features = build_final_features(accounts, agg)

    FEATURES_DIR.mkdir(parents=True, exist_ok=True)
    output_path = FEATURES_DIR / "account_features.parquet"
    features.to_parquet(output_path, index=False)

    print(f"\n✅ Feature engineering complete!")
    print(f"   Output: {output_path}")
    print(f"   Shape: {features.shape}")
    print(f"   Features: {list(features.columns)}")

if __name__ == "__main__":
    main()