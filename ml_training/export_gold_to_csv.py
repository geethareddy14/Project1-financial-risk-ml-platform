from pyspark.sql import SparkSession

def main():
    spark = SparkSession.builder.appName("export_gold_to_csv").getOrCreate()
    df = spark.read.parquet("out/gold/risk_features")

    # Single CSV file for demo (small datasets only)
    (df.coalesce(1)
       .write.mode("overwrite")
       .option("header", True)
       .csv("out/gold/risk_features_csv"))

    print("✅ Exported Gold features to out/gold/risk_features_csv/")
    spark.stop()

if __name__ == "__main__":
    main()
