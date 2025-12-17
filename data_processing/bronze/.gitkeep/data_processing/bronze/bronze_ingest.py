from pyspark.sql import SparkSession

def main():
    spark = SparkSession.builder.appName("bronze_ingest").getOrCreate()

    tx = (spark.read
          .option("header", True)
          .csv("sample_data/transactions.csv"))

    accounts = (spark.read
                .option("header", True)
                .csv("sample_data/accounts.csv"))

    # Placeholder: write to Delta bronze layer (local path for demo)
    tx.write.mode("overwrite").parquet("out/bronze/transactions")
    accounts.write.mode("overwrite").parquet("out/bronze/accounts")

    spark.stop()

if __name__ == "__main__":
    main()
