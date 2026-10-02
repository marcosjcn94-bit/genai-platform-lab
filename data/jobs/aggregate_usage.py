"""Shared UTC/decimal transformation; works with local Spark and Databricks."""
import argparse

from pyspark.sql import SparkSession, functions as F
from pyspark.sql.types import (
    ArrayType, DoubleType, IntegerType, LongType, StringType, StructField, StructType,
)

EVENT_SCHEMA = StructType([
    StructField("record_id", StringType()), StructField("timestamp", StringType()),
    StructField("application", StringType()), StructField("model", StringType()),
    StructField("status", StringType()), StructField("prompt_tokens", LongType()),
    StructField("completion_tokens", LongType()), StructField("total_tokens", LongType()),
    StructField("duration_ms", DoubleType()), StructField("spend", StringType()),
])
EXPORT_SCHEMA = StructType([
    StructField("schema_version", IntegerType()),
    StructField("events", ArrayType(EVENT_SCHEMA)),
])

def read_export(spark, path):
    spark.conf.set("spark.sql.session.timeZone", "UTC")
    document = spark.read.schema(EXPORT_SCHEMA).option("multiline", True).json(path)
    if document.count() != 1 or document.filter(
        F.col("schema_version").isNull() | (F.col("schema_version") != 1) |
        F.col("events").isNull()
    ).count():
        raise ValueError("Expected one schema_version=1 export")
    return document.select(F.explode("events").alias("event")).select("event.*")

def aggregate_usage(frame):
    frame.sparkSession.conf.set("spark.sql.session.timeZone", "UTC")
    # Identical duplicates are harmless; conflicting records must stop the batch.
    frame = frame.dropDuplicates()
    if frame.groupBy("record_id").count().filter(F.col("count") > 1).limit(1).count():
        raise ValueError("Conflicting duplicate record_id")
    invalid = (F.col("record_id").isNull() | F.col("timestamp").isNull() |
               F.col("application").isNull() | F.col("model").isNull() |
               ~F.col("timestamp").rlike(r"(Z|\+00:00)$") |
               (F.col("status").isNotNull() & ~F.col("status").isin("success", "failure")))
    for name in ("prompt_tokens", "completion_tokens", "total_tokens", "duration_ms"):
        invalid = invalid | (F.col(name) < 0)
    if frame.filter(invalid).limit(1).count():
        raise ValueError("Invalid or non-UTC event")
    frame = frame.withColumn("day", F.to_date(F.to_timestamp("timestamp")))
    frame = frame.withColumn("money", F.col("spend").cast("decimal(24,12)"))
    if frame.filter(F.col("day").isNull() |
        (F.col("spend").isNotNull() & F.col("money").isNull()) |
        (F.col("money") < 0)).limit(1).count():
        raise ValueError("Invalid timestamp or decimal")
    expressions = [
        F.count("*").alias("requests"), F.count("status").alias("status_known"),
        F.sum(F.when(F.col("status") == "failure", 1)
              .when(F.col("status") == "success", 0)).alias("errors"),
        F.sum("money").alias("spend"), F.count("money").alias("spend_known"),
        F.avg("duration_ms").alias("latency_mean_ms"),
    ]
    for name in ("prompt_tokens", "completion_tokens", "total_tokens", "duration_ms"):
        expressions.extend([F.sum(name).alias(name), F.count(name).alias(name + "_known")])
    return frame.groupBy("day", "application", "model").agg(*expressions)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    spark = SparkSession.builder.appName("daily-platform-usage").getOrCreate()
    spark.sparkContext.setLogLevel("WARN")
    aggregate_usage(read_export(spark, args.input)).write.mode("overwrite").parquet(args.output)
    print("Parquet written; only available source fields were aggregated.")
    spark.stop()

if __name__ == "__main__":
    main()
