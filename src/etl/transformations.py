from pyspark.sql import DataFrame
from pyspark.sql.functions import col, when, abs as spark_abs, to_date

def filter_valid_transactions(df: DataFrame) -> DataFrame:
    return (
        df
        .withColumn("amount", col("amount").cast("double"))
        .withColumn("date", to_date(col("date")))
        .filter(col("amount").isNotNull())
        .filter(col("date").between("2016-01-01", "2025-12-31"))
    )


def categorize_spending(df: DataFrame) -> DataFrame:
    return df.withColumn(
        "spending_tier",
        when(spark_abs(col("amount")) < 10, "micro")
        .when((spark_abs(col("amount")) >= 10) & (spark_abs(col("amount")) < 50), "small")
        .when((spark_abs(col("amount")) >= 50) & (spark_abs(col("amount")) < 200), "medium")
        .otherwise("large")
    )


def enrich_with_lookups(
    df: DataFrame,
    df_categories: DataFrame,
    df_merchants: DataFrame
) -> DataFrame:

    df_joined = df.join(df_categories, on="category_id", how="left")

    df_joined = df_joined.join(
        df_merchants,
        on="merchant_id",
        how="left"
    )

    return df_joined