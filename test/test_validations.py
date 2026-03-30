from chispa import assert_df_equality
from pyspark.sql import SparkSession

from src.etl.transformations import filter_valid_transactions

spark = SparkSession.builder.getOrCreate()


def test_filter_null_amount():
    df = spark.createDataFrame([
        ("2020-01-01", None),
        ("2020-01-01", "100")
    ], ["date", "amount"])

    result = filter_valid_transactions(df)

    assert result.count() == 1


def test_filter_invalid_date():
    df = spark.createDataFrame([
        ("2015-01-01", "100"),
        ("2020-01-01", "100"),
    ], ["date", "amount"])

    result = filter_valid_transactions(df)

    assert result.count() == 1


def test_keep_negative_amount():
    df = spark.createDataFrame([
        ("2020-01-01", "-50"),
    ], ["date", "amount"])

    result = filter_valid_transactions(df)

    assert result.count() == 1