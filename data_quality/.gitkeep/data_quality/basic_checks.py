import pandas as pd

REQUIRED_TX_COLS = {"transaction_id", "account_id", "amount", "timestamp"}

def main():
    df = pd.read_csv("sample_data/transactions.csv")

    missing_cols = REQUIRED_TX_COLS - set(df.columns)
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")

    if df["amount"].isna().mean() > 0.01:
        raise ValueError("Too many null amounts")

    print("✅ Basic data quality checks passed.")

if __name__ == "__main__":
    main()
