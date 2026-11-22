import importlib.util
import sqlite3
import sys
from pathlib import Path
import pytest

HERE = Path(__file__).resolve().parents[1] / 'databricks-pipeline-template/notebooks'
spec = importlib.util.spec_from_file_location('pipeline_contract', HERE / 'pipeline_contract.py')
contract = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = contract
spec.loader.exec_module(contract)

def row(**changes):
    return dict(source_system='erp', transaction_id='T1', updated_at='2025-02-01T10:00:00Z',
                month='2025-01-01', cost_center=' CC01 ', category='cloud', vendor='Vendor',
                currency='brl', amount='100.00', **{}) | changes

def test_grain_deduplication_and_cent_reconciliation():
    data = [row(), row(), row(transaction_id='T2'), row(transaction_id='CREDIT', amount='-10.25'),
            row(transaction_id='BAD', currency='USD'), row(transaction_id='MALFORMED', amount='NaN'),
            row(updated_at='2025-01-01T00:00:00Z', amount='80.00')]
    result = contract.transform_records(data)
    assert len(result['accepted']) == 3  # two legitimate same-month/vendor expenses + credit
    assert result['report']['accepted_cents'] == 18975
    assert result['report']['duplicates_rows'] == 1
    assert result['report']['superseded_rows'] == 1
    assert result['report']['unknown_amount_rows'] == 1
    assert result['report']['input_rows'] == 7
    assert {e['source_row'] for e in result['rejected']} == {5, 6}
    assert result['accepted'][0]['row']['cost_center'] == 'CC01'

def test_conflicting_versions_quarantine_entire_transaction():
    data = [row(), row(amount='999.00'), row(updated_at='2025-03-01T00:00:00Z')]
    result = contract.transform_records(data)
    assert not result['accepted']
    assert len(result['rejected']) == 3
    assert all(e['reasons'] == ['conflicting_version'] for e in result['rejected'])

@pytest.mark.parametrize('changes', [dict(month='2025-02-30'), dict(month='2025-01-02'),
    dict(updated_at='2025-01-01'), dict(amount='1.001'), dict(amount='Infinity'),
    dict(amount='10000000000000000'), dict(transaction_id=' '), dict(category='other')])
def test_malformed_rows_are_inspectable(changes):
    result = contract.transform_records([row(**changes)])
    assert len(result['rejected']) == 1
    assert result['rejected'][0]['raw'] == row(**changes)
    assert result['rejected'][0]['reasons']

def test_source_identity_and_utc_normalization():
    result = contract.transform_records([row(), row(source_system='other'),
        row(updated_at='2025-02-01T07:00:00-03:00')])
    assert len(result['accepted']) == 2
    assert len(result['duplicates']) == 1

def test_retry_late_arrival_and_new_version(tmp_path):
    db = tmp_path / 'costs.db'
    records = [row(), row(transaction_id='T2')]
    contract.run_local_batch(db, records, 'batch1')
    assert contract.run_local_batch(db, records, 'batch1')['replayed']
    contract.run_local_batch(db, records, 'batch2')
    contract.run_local_batch(db, [row(updated_at='2025-01-01T00:00:00Z', amount='10')], 'late')
    contract.run_local_batch(db, [row(updated_at='2025-03-01T00:00:00Z', amount='120')], 'revision')
    with sqlite3.connect(db) as c:
        assert c.execute('SELECT count(*),sum(amount_cents) FROM silver').fetchone() == (2, 22000)
        assert c.execute("SELECT batch_id FROM silver WHERE transaction_id='T1'").fetchone()[0] == 'revision'
    with pytest.raises(ValueError, match='different input'):
        contract.run_local_batch(db, [row(amount='200')], 'batch1')

def test_cross_batch_conflict_rolls_back_all_records(tmp_path):
    db = tmp_path / 'costs.db'
    contract.run_local_batch(db, [row()], 'first')
    with pytest.raises(ValueError, match='Conflicting'):
        contract.run_local_batch(db, [row(transaction_id='T2'), row(amount='999')], 'bad')
    with sqlite3.connect(db) as c:
        assert c.execute('SELECT count(*) FROM silver').fetchone()[0] == 1
        assert c.execute("SELECT count(*) FROM bronze WHERE batch_id='bad'").fetchone()[0] == 0
