"""Prove the compiled dbt reconciliation rejects corrupt marts in memory only."""
import json
from pathlib import Path
import duckdb

PROJECT = Path(__file__).resolve().parents[1]

def main():
    manifest = json.loads((PROJECT / 'target/manifest.json').read_text(encoding='utf-8'))
    compiled = PROJECT / 'target/compiled/finance_dbt_lab/tests/assert_monthly_costs_reconcile.sql'
    query = compiled.read_text(encoding='utf-8')
    connection = duckdb.connect(':memory:')
    try:
        connection.execute('attach ? as source (read_only)', [str(PROJECT / 'finance_lab.duckdb')])
        for name in ('stg_finance_costs', 'fct_monthly_costs'):
            node = manifest['nodes']['model.finance_dbt_lab.' + name]
            relation = node['relation_name']
            # Copy built relations into isolated memory; the original DB is read-only.
            source = 'source."' + node['schema'].replace('"', '""') + '"."' + name + '"'
            connection.execute('create table ' + name + ' as select * from ' + source)
            query = query.replace(relation, name)
        if connection.execute(query).fetchall():
            raise RuntimeError('Unmodified build fails reconciliation')
        print('PASS: unmodified build reconciles')
        if connection.execute('select count(*) from fct_monthly_costs').fetchone()[0] < 2:
            raise RuntimeError('Mutation fixtures require at least two reporting groups')
        cases = {
            'missing group': 'delete from fct_monthly_costs where rowid=0',
            'unexpected group': "insert into fct_monthly_costs select cost_key || '-extra', month, cost_center || '-extra', category, total_amount_brl, transaction_count from fct_monthly_costs where rowid=0",
            'one-cent difference': 'update fct_monthly_costs set total_amount_brl=total_amount_brl+0.01 where rowid=0',
            'wrong transaction count': 'update fct_monthly_costs set transaction_count=transaction_count+1 where rowid=0',
            'null amount': 'update fct_monthly_costs set total_amount_brl=null where rowid=0',
            'null count': 'update fct_monthly_costs set transaction_count=null where rowid=0',
            'offsetting errors with unchanged grand total': 'update fct_monthly_costs set total_amount_brl=total_amount_brl+case when rowid=0 then 0.01 else -0.01 end where rowid in (0,1)',
        }
        for label, mutation in cases.items():
            connection.execute('begin transaction')
            try:
                connection.execute(mutation)
                if not connection.execute(query).fetchall():
                    raise RuntimeError('Undetected corruption: ' + label)
                print('PASS: detected ' + label)
            finally:
                connection.execute('rollback')
        if connection.execute(query).fetchall():
            raise RuntimeError('Mutation rollback did not preserve the baseline')
        print('PASS: baseline preserved; source database was never modified')
    finally:
        connection.close()

if __name__ == '__main__':
    main()
