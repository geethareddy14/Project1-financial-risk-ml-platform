from pyspark.sql import SparkSession
from pyspark.sql.functions import col, to_timestamp

def main():
    spark = SparkSession.builder.appName("silver_clean").getOrCreate()

    tx = spark.read.parquet("out/bronze/transactions")
    accounts = spark.read.parquet("out/bronze/accounts")

    # Basic type casting + cleaning (demo)
    tx_clean = (
        tx.withColumn("amount", col("amount").cast("double"))
          .withColumn("is_fraud", col("is_fraud").cast("int"))
          .withColumn("timestamp", to_timestamp(col("timestamp")))
          .dropna(subset=["transaction_id", "account_id", "amount", "timestamp"])
    )

    accounts_clean = (
        accounts.withColumn("account_age_days", col("account_age_days").cast("int"))
                .withColumn("credit_limit", col("credit_limit").cast("double"))
                .dropna(subset=["account_id", "customer_id"])
    )

    tx_clean.write.mode("overwrite").parquet("out/silver/transactions")
    accounts_clean.write.mode("overwrite").parquet("out/silver/accounts")

    print("✅ Wrote Silver datasets to out/silver/")
    spark.stop()

if __name__ == "__main__":
    main()
