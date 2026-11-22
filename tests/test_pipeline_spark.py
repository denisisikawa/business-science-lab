"""Opt-in Spark contract test; no claim of Databricks/Delta deployment."""
import importlib.util
import os
from pathlib import Path
import sys
import pytest

pytestmark = pytest.mark.skipif(os.getenv('RUN_SPARK_TESTS') != '1', reason='Requires Spark and Java 17')

def test_spark_typed_contract_matches_reference():
    from pyspark.sql import SparkSession
    here = Path(__file__).resolve().parents[1] / 'databricks-pipeline-template/notebooks'
    sys.path.insert(0, str(here))
    spec = importlib.util.spec_from_file_location('cost_pipeline', here / 'cost_pipeline_bronze_silver_gold.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    from pipeline_contract import FIELDS, transform_records
    base = dict(source_system='erp', transaction_id='1', updated_at='2025-02-01T00:00:00Z',
                month='2025-01-01', cost_center=' CC1 ', category='cloud', vendor='vendor', currency='BRL', amount='100.00')
    rows = [base, base.copy(), base | {'transaction_id': '2'},
            base | {'transaction_id': '3', 'amount': '-20.25'},
            base | {'transaction_id': '4', 'amount': 'NaN'},
            base | {'transaction_id': '5', 'currency': 'USD'},
            base | {'updated_at': '2025-01-01T00:00:00Z', 'amount': '90.00'}]
    spark = SparkSession.builder.master('local[2]').appName('financial-contract-test').getOrCreate()
    try:
        accepted, rejected, discarded, report = module.transform_spark(spark, spark.createDataFrame(rows))
        assert report == dict(input_rows=7, accepted_rows=3, rejected_rows=2, duplicate_or_superseded_rows=2)
        assert str(accepted.schema['amount'].dataType) == 'DecimalType(18,2)'
        reference = transform_records(rows)
        assert sum(r.amount for r in accepted.collect()) * 100 == reference['report']['accepted_cents']
        assert rejected.count() == 2 and discarded.count() == 2
    finally:
        spark.stop()
