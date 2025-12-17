from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when, avg, count, sum as fsum

HIGH_RISK_MCC = {"electronics", "travel"}

def main():
    spark = SparkSession.builder.appName("gold_features").getOrCreate()

    tx = spark.read.parquet("out/silver/transactions")
    accounts = spark.read.parquet("out/silver/accounts")

    tx_feat = (
        tx.withColumn("is_high_risk_mcc", when(col("merchant_category").isin(list(HIGH_RISK_MCC)), 1).otherwise(0))
    )

    # Simple account-level features (demo)
    features = (
        tx_feat.groupBy("account_id")
              .agg(
                  count("*").alias("tx_count"),
                  avg("amount").alias("avg_amount"),
                  fsum("is_high_risk_mcc").alias("high_risk_mcc_count"),
                  fsum("is_fraud").alias("fraud_label_sum")
              )
    )

    gold = features.join(accounts, on="account_id", how="left")

    gold.write.mode("overwrite").parquet("out/gold/risk_features")

    print("✅ Wrote Gold feature table to out/gold/risk_features")
    spark.stop()

if __name__ == "__main__":
    main()
