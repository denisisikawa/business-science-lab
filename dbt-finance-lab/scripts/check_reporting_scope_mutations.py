"""Prove independent coverage detects losses shared by staging and mart."""
import json
from pathlib import Path
import duckdb

PROJECT = Path(__file__).resolve().parents[1]

def main():
    manifest = json.loads((PROJECT/'target/manifest.json').read_text(encoding='utf-8'))
    compiled = PROJECT/'target/compiled/finance_dbt_lab/tests'
    queries = {name:(compiled/(name+'.sql')).read_text(encoding='utf-8') for name in
               ('assert_reporting_scope_coverage','assert_reporting_scope_valid','assert_monthly_costs_reconcile')}
    con = duckdb.connect(':memory:')
    try:
        con.execute('attach ? as source (read_only)',[str(PROJECT/'finance_lab.duckdb')])
        for name, resource in [('finance_reporting_scope','seed'),('stg_finance_costs','model'),('fct_monthly_costs','model')]:
            node=manifest['nodes'][resource+'.finance_dbt_lab.'+name]
            schema=node['schema'].replace('"','""')
            con.execute('create table '+name+' as select * from source."'+schema+'"."'+name+'"')
            for key in queries:
                queries[key]=queries[key].replace(node['relation_name'],name)
        for query in queries.values():
            if con.execute(query).fetchall():
                raise RuntimeError('Unmodified build must pass all controls')
        print('PASS: unmodified scope, coverage and reconciliation')
        missing = "month='2026-02-01' and cost_center='CC-100' and category='Cloud'"
        cases=[
            ('whole month missing from both', ["delete from stg_finance_costs where month='2026-02-01'", "delete from fct_monthly_costs where month='2026-02-01'"],6,True),
            ('all facts missing from both', ['delete from stg_finance_costs','delete from fct_monthly_costs'],18,True),
            ('one group missing from both', ['delete from stg_finance_costs where '+missing,'delete from fct_monthly_costs where '+missing],1,True),
            ('staging-only loss', ['delete from stg_finance_costs where '+missing],1,False),
            ('mart-only loss', ['delete from fct_monthly_costs where '+missing],1,False),
            ('unexpected group in both', ["update stg_finance_costs set cost_center='CC-EXTRA' where "+missing,"update fct_monthly_costs set cost_center='CC-EXTRA' where "+missing],2,False),
            ('scope excludes an observed group', ['delete from finance_reporting_scope where '+missing],1,False),
        ]
        for label,mutations,count,old_control_passes in cases:
            con.execute('begin transaction')
            try:
                for mutation in mutations:
                    con.execute(mutation)
                failures=con.execute(queries['assert_reporting_scope_coverage']).fetchall()
                if len(failures)!=count:
                    raise RuntimeError('Unexpected coverage result for '+label)
                if old_control_passes and con.execute(queries['assert_monthly_costs_reconcile']).fetchall():
                    raise RuntimeError('Expected shared loss to escape staging-to-mart reconciliation')
                print('PASS: coverage detects '+label+' ('+str(count)+' groups)')
            finally:
                con.execute('rollback')
        invalid_scope=[
            ('duplicate', 'insert into finance_reporting_scope select * from finance_reporting_scope limit 1'),
            ('non-month-start', "update finance_reporting_scope set month='2026-02-02' where month='2026-02-01'"),
            ('blank center', "update finance_reporting_scope set cost_center=' ' where cost_center='CC-100'"),
        ]
        for label,mutation in invalid_scope:
            con.execute('begin transaction')
            try:
                con.execute(mutation)
                if not con.execute(queries['assert_reporting_scope_valid']).fetchall():
                    raise RuntimeError('Invalid scope not detected: '+label)
                print('PASS: rejects scope '+label)
            finally:
                con.execute('rollback')
        for query in queries.values():
            if con.execute(query).fetchall():
                raise RuntimeError('Baseline not preserved')
        print('PASS: seven coverage scenarios and three invalid-scope scenarios; source DB read-only')
    finally:
        con.close()

if __name__=='__main__':
    main()
