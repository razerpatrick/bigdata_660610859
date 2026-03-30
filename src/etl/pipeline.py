from pyspark.sql import SparkSession
from pyspark.sql.functions import col, year, month, avg, sum as _sum, desc

from src.etl.schemas import *
from src.etl.transformations import *

def run_pipeline():
    spark = SparkSession.builder.appName("AccountingPipeline").getOrCreate()

    # ---------------- RAW ----------------
    df_txn = spark.read.csv("data/transactions.csv", header=True, schema=transactions_schema)
    df_cat = spark.read.csv("data/categories.csv", header=True, schema=categories_schema)
    df_mer = spark.read.csv("data/merchants.csv", header=True, schema=merchants_schema)

    df_txn.write.mode("overwrite").parquet("output/raw/transactions/")
    df_cat.write.mode("overwrite").parquet("output/raw/categories/")
    df_mer.write.mode("overwrite").parquet("output/raw/merchants/")

    # ---------------- STAGED ----------------
    df_clean = filter_valid_transactions(df_txn)
    df_clean.write.mode("overwrite").parquet("output/staged/transactions/")

    # ---------------- ENRICH ----------------
    df_enriched = enrich_with_lookups(df_clean, df_cat, df_mer)
    df_enriched = categorize_spending(df_enriched)

    df_enriched.write.mode("overwrite").parquet("output/analytics/enriched_transactions/")

    # ---------------- ANALYTICS ----------------

    # 1. Monthly by category
    monthly = (
        df_enriched
        .withColumn("year", year("date"))
        .withColumn("month", month("date"))
        .groupBy("year", "month", "category_name")
        .agg(_sum("amount").alias("total_amount"))
    )

    monthly.write.mode("overwrite").parquet("output/analytics/monthly_by_category/")

    # 2. Yearly by member
    yearly_member = (
        df_enriched
        .withColumn("year", year("date"))
        .groupBy("year", "member_id")
        .agg(_sum("amount").alias("total_amount"))
    )

    yearly_member.write.mode("overwrite").parquet("output/analytics/yearly_by_member/")

    # 3. Top merchants per year
    from pyspark.sql.window import Window
    from pyspark.sql.functions import row_number

    w = Window.partitionBy("year").orderBy(desc("total_amount"))

    top_merchants = (
        df_enriched
        .withColumn("year", year("date"))
        .groupBy("year", "merchant_name")
        .agg(_sum("amount").alias("total_amount"))
        .withColumn("rank", row_number().over(w))
        .filter(col("rank") <= 10)
    )

    top_merchants.write.mode("overwrite").parquet("output/analytics/top_merchants_by_year/")

    # 4. Avg per year
    avg_year = (
        df_enriched
        .withColumn("year", year("date"))
        .groupBy("year")
        .agg(avg("amount").alias("avg_amount"))
    )

    avg_year.write.mode("overwrite").parquet("output/analytics/avg_amount_by_year/")

    spark.stop()


if __name__ == "__main__":
    run_pipeline()