import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
import random
import json

# ─── CONFIG ───────────────────────────────────────────────
SEED = 42
N_ACCOUNTS = 5000
N_TRANSACTIONS = 200000
FRAUD_RATE = 0.025  # 2.5% fraud rate - realistic for financial data
OUTPUT_DIR = Path("data/raw")

np.random.seed(SEED)
random.seed(SEED)

HIGH_RISK_MCC = [5912, 7995, 5999, 4829, 6051]

def generate_accounts(n: int) -> pd.DataFrame:
    print(f"Generating {n} accounts...")
    account_ids = [f"ACC{str(i).zfill(6)}" for i in range(n)]
    accounts = pd.DataFrame({
        "account_id": account_ids,
        "account_age_days": np.random.randint(30, 3650, n),
        "credit_limit": np.random.choice([1000, 2500, 5000, 10000, 25000, 50000], n, p=[0.15, 0.25, 0.30, 0.20, 0.08, 0.02]),
        "account_type": np.random.choice(["checking", "savings", "credit"], n, p=[0.45, 0.35, 0.20]),
        "customer_segment": np.random.choice(["retail", "premium", "business"], n, p=[0.65, 0.25, 0.10]),
        "kyc_verified": np.random.choice([True, False], n, p=[0.92, 0.08]),
    })
    return accounts

def generate_transactions(accounts: pd.DataFrame, n: int) -> pd.DataFrame:
    print(f"Generating {n} transactions...")
    account_ids = accounts["account_id"].values
    transactions = pd.DataFrame({
        "transaction_id": [f"TXN{str(i).zfill(8)}" for i in range(n)],
        "account_id": np.random.choice(account_ids, n),
        "amount": np.abs(np.random.lognormal(mean=4.5, sigma=1.2, size=n)).round(2),
        "mcc_code": np.random.choice([5411, 5812, 5912, 7995, 5999, 4829, 6051, 5691, 5734, 4111], n, p=[0.25, 0.20, 0.10, 0.05, 0.10, 0.05, 0.03, 0.10, 0.07, 0.05]),
        "transaction_type": np.random.choice(["purchase", "withdrawal", "transfer", "payment"], n, p=[0.60, 0.15, 0.15, 0.10]),
        "channel": np.random.choice(["online", "pos", "atm", "mobile"], n, p=[0.35, 0.40, 0.10, 0.15]),
        "hour_of_day": np.random.choice(range(24), n, p=[0.01,0.01,0.01,0.01,0.01,0.02,0.03,0.05,0.06,0.07,0.07,0.07,0.07,0.07,0.07,0.07,0.06,0.06,0.05,0.05,0.04,0.03,0.02,0.01]),
        "day_of_week": np.random.randint(0, 7, n),
        "is_international": np.random.choice([True, False], n, p=[0.08, 0.92]),
    })
    base_date = datetime(2024, 1, 1)
    transactions["timestamp"] = [base_date + timedelta(days=random.randint(0, 364), hours=int(transactions["hour_of_day"].iloc[i])) for i in range(n)]
    n_fraud = int(n * FRAUD_RATE)
    fraud_indices = np.random.choice(n, n_fraud, replace=False)
    transactions["is_fraud"] = 0
    transactions.loc[fraud_indices, "is_fraud"] = 1
    transactions.loc[fraud_indices[:n_fraud//3], "amount"] = np.random.uniform(2000, 15000, len(fraud_indices[:n_fraud//3])).round(2)
    transactions.loc[fraud_indices[n_fraud//3:2*n_fraud//3], "mcc_code"] = np.random.choice(HIGH_RISK_MCC, len(fraud_indices[n_fraud//3:2*n_fraud//3]))
    transactions.loc[fraud_indices[2*n_fraud//3:], "hour_of_day"] = np.random.choice([1, 2, 3, 4], len(fraud_indices[2*n_fraud//3:]))
    transactions.loc[fraud_indices[:n_fraud//2], "is_international"] = True
    return transactions

def main():
    print("=" * 50)
    print("Financial Risk ML Platform — Data Ingestion")
    print("=" * 50)
    accounts = generate_accounts(N_ACCOUNTS)
    transactions = generate_transactions(accounts, N_TRANSACTIONS)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    accounts.to_parquet(OUTPUT_DIR / "accounts.parquet", index=False)
    transactions.to_parquet(OUTPUT_DIR / "transactions.parquet", index=False)
    print(f"✅ Saved {len(accounts):,} accounts")
    print(f"✅ Saved {len(transactions):,} transactions")
    print(f"✅ Fraud rate: {transactions['is_fraud'].mean():.2%}")

if __name__ == "__main__":
    main()