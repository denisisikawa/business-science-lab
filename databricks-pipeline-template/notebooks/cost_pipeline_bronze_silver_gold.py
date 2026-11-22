"""Financial cost contract, local acceptance backend and optional Spark/Delta adapter.

Spark/Delta execution requires a configured runtime; local mode uses SQLite.
"""
import argparse
import csv
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
from pipeline_contract import FIELDS, normalize, run_local_batch

def ingest_bronze(spark, source_table, target_path, *, jdbc_options, batch_id,
                  transaction_app_id, transaction_version):
    """An immutable source batch must reuse app ID and version on retry."""
    if not batch_id or not transaction_app_id or transaction_version < 0:
        raise ValueError("Batch ID, stable app ID and nonnegative transaction version required")
    if not {"url", "driver"}.issubset(jdbc_options):
        raise ValueError("Explicit JDBC url and driver are required; inject credentials privately")
    from pyspark.sql import functions as F
    raw = spark.read.format("jdbc").options(**jdbc_options).option("dbtable", source_table).load()
    missing = set(FIELDS) - set(raw.columns)
    if missing:
        raise ValueError("Missing source fields: " + ", ".join(sorted(missing)))
    bronze = raw.select(*(F.col(c).cast("string").alias(c) for c in FIELDS))
    bronze = (bronze.withColumn("_batch_id", F.lit(batch_id))
              .withColumn("_source_table", F.lit(source_table))
              .withColumn("_ingested_at", F.current_timestamp())
              .withColumn("load_date", F.current_date()))
    (bronze.write.format("delta").mode("append").partitionBy("load_date")
     .option("txnAppId", transaction_app_id).option("txnVersion", transaction_version)
     .save(target_path))
    return bronze

def transform_spark(spark, raw):
    """Use the exact same row contract as local acceptance tests, then Spark windows."""
    from pyspark.sql import functions as F, types as T, Window
    missing = set(FIELDS) - set(raw.columns)
    if missing:
        raise ValueError("Missing source fields: " + ", ".join(sorted(missing)))
    spark.conf.set("spark.sql.session.timeZone", "UTC")
    # Make the pure row contract available to Python workers.
    spark.sparkContext.addPyFile(str(HERE / "pipeline_contract.py"))
    schema = T.StructType([T.StructField("record", T.MapType(T.StringType(), T.StringType())),
                           T.StructField("reasons", T.ArrayType(T.StringType())),
                           T.StructField("known_amount", T.DecimalType(18, 2))])
    @F.udf(schema)
    def parse_row(value):
        record, reasons, amount = normalize(value.asDict())
        return record, reasons, amount
    staged = raw.withColumn("_parsed", parse_row(F.struct(*(F.col(c).cast("string").alias(c) for c in FIELDS))))
    for c in (*FIELDS, "row_hash"):
        staged = staged.withColumn("_" + c, F.col("_parsed.record").getItem(c))
    staged = staged.withColumn("_reasons", F.col("_parsed.reasons"))
    valid = staged.where(F.size("_reasons") == 0)
    keys = ["_source_system", "_transaction_id"]
    conflicts = (valid.groupBy(*keys, "_updated_at").agg(F.countDistinct("_row_hash").alias("_versions"))
                 .where("_versions > 1").select(*keys).distinct().withColumn("_conflict", F.lit(True)))
    staged = staged.join(conflicts, keys, "left")
    staged = staged.withColumn("_reasons", F.when(F.col("_conflict"),
                              F.array(F.lit("conflicting_version"))).otherwise(F.col("_reasons")))
    rejected = staged.where(F.size("_reasons") > 0)
    valid = staged.where(F.size("_reasons") == 0)
    window = Window.partitionBy(*keys).orderBy(F.col("_updated_at").desc(), F.col("_row_hash"))
    ranked = valid.withColumn("_rank", F.row_number().over(window))
    winners = ranked.where("_rank = 1")
    accepted = winners.select(
        F.col("_source_system").alias("source_system"), F.col("_transaction_id").alias("transaction_id"),
        F.to_timestamp("_updated_at").alias("updated_at"), F.to_date("_month").alias("month"),
        *(F.col("_" + c).alias(c) for c in ("cost_center", "category", "vendor", "currency")),
        F.col("_parsed.known_amount").alias("amount"), F.col("_row_hash").alias("row_hash"),
        F.to_json(F.struct(*(F.col(c) for c in raw.columns))).alias("source_record"))
    discarded = ranked.where("_rank > 1")
    # Counts include duplicates/older versions; all malformed amounts remain visible.
    report = {"input_rows": raw.count(), "accepted_rows": accepted.count(),
              "rejected_rows": rejected.count(), "duplicate_or_superseded_rows": discarded.count()}
    if report["input_rows"] != sum(report[k] for k in ("accepted_rows", "rejected_rows", "duplicate_or_superseded_rows")):
        raise RuntimeError("Input row reconciliation failed")
    def total(frame):
        value = frame.agg(F.sum("_parsed.known_amount").alias("amount")).first()["amount"]
        return value or 0
    if total(staged) != total(winners) + total(rejected) + total(discarded):
        raise RuntimeError("Known input amount reconciliation failed")
    return accepted, rejected, discarded, report

def load_silver_cost(spark, bronze_path, silver_path, quarantine_path):
    from delta.tables import DeltaTable
    from pyspark.sql import functions as F
    accepted, rejected, discarded, report = transform_spark(
        spark, spark.read.format("delta").load(bronze_path))
    # Full Bronze snapshot -> full quarantine snapshot, preserving the raw source row.
    rejected.write.format("delta").mode("overwrite").option("overwriteSchema", "true").save(quarantine_path)
    discarded.write.format("delta").mode("overwrite").option("overwriteSchema", "true").save(quarantine_path + "_superseded")
    if DeltaTable.isDeltaTable(spark, silver_path):
        table = DeltaTable.forPath(spark, silver_path)
        join = "t.source_system = s.source_system AND t.transaction_id = s.transaction_id"
        collisions = table.toDF().alias("t").join(accepted.alias("s"), F.expr(join)).where(
            "t.updated_at = s.updated_at AND t.row_hash <> s.row_hash")
        if collisions.limit(1).count():
            raise ValueError("Conflicting version against persisted Silver")
        (table.alias("t").merge(accepted.alias("s"), join)
         .whenMatchedUpdateAll(condition="s.updated_at > t.updated_at")
         .whenNotMatchedInsertAll().execute())
    else:
        accepted.write.format("delta").mode("errorifexists").save(silver_path)
    return spark.read.format("delta").load(silver_path), report

def build_gold_aggregates(spark, silver_path, gold_path):
    from pyspark.sql import functions as F
    silver = spark.read.format("delta").load(silver_path)
    monthly = silver.groupBy("month", "cost_center", "category").agg(
        F.sum("amount").alias("total_amount"), F.count("*").alias("transaction_count"))
    if silver.agg(F.sum("amount")).first()[0] != monthly.agg(F.sum("total_amount")).first()[0]:
        raise RuntimeError("Silver/Gold reconciliation failed")
    monthly.write.format("delta").mode("overwrite").save(gold_path)
    return monthly

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", type=Path, required=True)
    parser.add_argument("--database", type=Path, required=True)
    parser.add_argument("--batch-id", required=True)
    args = parser.parse_args(argv)
    with args.csv.open(encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream)
        if not set(FIELDS).issubset(reader.fieldnames or []):
            raise ValueError("CSV schema does not satisfy the contract")
        records = list(reader)
    print(json.dumps(run_local_batch(args.database, records, args.batch_id), indent=2))

if __name__ == "__main__":
    main()
