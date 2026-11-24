"""Reproduce the educational BRL 100,000 example with compiled dbt SQL in memory."""
import json
from decimal import Decimal
from pathlib import Path
import duckdb

PROJECT = Path(__file__).resolve().parents[1]

def main():
    manifest = json.loads((PROJECT / 'target/manifest.json').read_text(encoding='utf-8'))
    compiled = PROJECT / 'target/compiled/finance_dbt_lab'
    model = (compiled / 'models/marts/fct_monthly_costs.sql').read_text(encoding='utf-8')
    control = (compiled / 'tests/assert_monthly_costs_reconcile.sql').read_text(encoding='utf-8')
    for name in ('stg_finance_costs', 'fct_monthly_costs'):
        relation = manifest['nodes']['model.finance_dbt_lab.' + name]['relation_name']
        model = model.replace(relation, name)
        control = control.replace(relation, name)
    connection = duckdb.connect(':memory:')
    try:
        connection.execute("""create table stg_finance_costs (
            month date, cost_center varchar, category varchar, amount_brl decimal(18,2))""")
        connection.execute("""insert into stg_finance_costs values
            ('2026-01-01', 'Tecnologia', 'Cloud', 25000.00),
            ('2026-01-01', 'Tecnologia', 'Cloud', 15000.00),
            ('2026-01-01', 'Operacoes', 'Cloud', 35000.00),
            ('2026-01-01', 'Operacoes', 'Cloud', 25000.00)""")
        connection.execute('create table fct_monthly_costs as ' + model)
        if connection.execute(control).fetchall():
            raise RuntimeError('The correct educational example does not reconcile')
        before = connection.execute('select sum(total_amount_brl) from fct_monthly_costs').fetchone()[0]
        connection.execute("""update fct_monthly_costs set total_amount_brl = total_amount_brl +
            case when cost_center='Tecnologia' then 10000.00 else -10000.00 end""")
        after = connection.execute('select sum(total_amount_brl) from fct_monthly_costs').fetchone()[0]
        if before != Decimal('100000.00') or after != before:
            raise RuntimeError('The example must preserve the BRL 100,000 grand total')
        failures = connection.execute(control).fetchall()
        observed = {r[1]: (r[3], r[4]) for r in failures}
        expected = {
            'Tecnologia': (Decimal('40000.00'), Decimal('50000.00')),
            'Operacoes': (Decimal('60000.00'), Decimal('50000.00')),
        }
        if len(failures) != 2 or observed != expected:
            raise RuntimeError('The control did not return the expected two discrepancies')
        print('SYNTHETIC EDUCATIONAL EXAMPLE - not the default CSV dataset')
        print('Period: 2026-01-01; category: Cloud; currency: BRL')
        print('Cost center | Expected BRL | Reported BRL | Difference BRL')
        for center, (expected_amount, actual_amount) in sorted(observed.items()):
            print(f'{center} | {expected_amount:.2f} | {actual_amount:.2f} | {actual_amount-expected_amount:+.2f}')
        print(f'Grand total before: {before:.2f}; after: {after:.2f}')
        print('PASS: total-only comparison misses the error; compiled dbt control returns 2 failing groups')
        print('All data and mutations existed only in memory; no database file was opened')
    finally:
        connection.close()

if __name__ == '__main__':
    main()
