from pyspark.sql.types import *

transactions_schema = StructType([
    StructField("transaction_id", StringType(), True),
    StructField("date", StringType(), True),
    StructField("member_id", StringType(), True),
    StructField("item_name", StringType(), True),
    StructField("category_id", StringType(), True),
    StructField("merchant_id", StringType(), True),
    StructField("amount", StringType(), True),
    StructField("payment_method", StringType(), True),
])

categories_schema = StructType([
    StructField("category_id", StringType(), True),
    StructField("category_name", StringType(), True),
    StructField("budget_type", StringType(), True),
])

merchants_schema = StructType([
    StructField("merchant_id", StringType(), True),
    StructField("merchant_name", StringType(), True),
    StructField("merchant_type", StringType(), True),
])