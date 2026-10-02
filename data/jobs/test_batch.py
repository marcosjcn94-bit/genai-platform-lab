import tempfile
from pathlib import Path
from pyspark.sql import SparkSession
from aggregate_usage import aggregate_usage, read_export

def main():
    spark = SparkSession.builder.master("local[2]").appName("batch-contract").getOrCreate()
    spark.conf.set("spark.sql.session.timeZone", "UTC")
    frame = read_export(spark, "/workspace/data/fixtures/usage-v1.json")
    result = aggregate_usage(frame)
    rows = {(str(r.day), r.application, r.model): r.asDict() for r in result.collect()}
    a = rows[("2026-01-01", "app-a", "primary")]
    assert a["requests"] == 2
    assert a["total_tokens"] == 30
    assert str(a["spend"]) == "0.300000000000"
    assert a["status_known"] == 1
    assert a["errors"] == 0
    assert a["latency_mean_ms"] == 1500
    b = rows[("2026-01-01", "app-b", "reserve")]
    assert b["spend"] is None
    assert b["spend_known"] == 0
    assert b["errors"] == 1
    path = tempfile.mkdtemp() + "/parquet"
    result.write.mode("overwrite").parquet(path)
    first = sorted(str(r) for r in spark.read.parquet(path).collect())
    result.write.mode("overwrite").parquet(path)
    assert first == sorted(str(r) for r in spark.read.parquet(path).collect())
    print("BATCH_OK: decimal, null, deduplication, known totals, Parquet idempotency")
    spark.stop()

if __name__ == "__main__":
    main()
