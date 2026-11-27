"""Reject structural corruption before computing revenue-assurance results."""
import csv
import json
import re
import tempfile
import unittest
from pathlib import Path

from simulator import generate
from sandbox_engine import reconcile

class InputContractTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.reset()

    def reset(self):
        generate(self.root, customers=2, months=2, seed=42, anomaly_rate=0)

    def edit(self, name, change):
        path = self.root / (name+'.csv')
        with path.open(newline='',encoding='utf-8') as stream:
            reader=csv.DictReader(stream)
            fields=reader.fieldnames
            rows=list(reader)
        change(rows)
        with path.open('w',newline='',encoding='utf-8') as stream:
            writer=csv.DictWriter(stream,fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)

    def invalid(self, table, change, reason):
        self.reset()
        self.edit(table,change)
        with self.assertRaisesRegex(ValueError,reason):
            reconcile(self.root)

    def test_duplicate_keys_are_rejected_not_overwritten(self):
        for table in ('products','contract_items','service_usage','invoice_items'):
            with self.subTest(table=table):
                self.invalid(table,lambda rows:rows.append(rows[0].copy()),'duplicate_key')

    def test_invoice_id_and_item_period_are_independently_unique(self):
        self.invalid('invoice_items',lambda rows:rows[1].update(invoice_item_id=rows[0]['invoice_item_id']),'duplicate_key_invoice_item_id')
        self.invalid('invoice_items',lambda rows:rows.append(dict(rows[0],invoice_item_id='new-invoice-id')),'duplicate_key_item_id_period')

    def test_parent_references_fail_clearly(self):
        cases=[('contract_items',{'product_id':'unknown'},'unknown_product'),
               ('service_usage',{'item_id':'unknown'},'unknown_item'),
               ('invoice_items',{'item_id':'unknown'},'unknown_item')]
        for table,change,reason in cases:
            with self.subTest(table=table):
                self.invalid(table,lambda rows:rows[0].update(change),reason)

    def test_invoice_without_usage_evidence_cannot_be_silently_ignored(self):
        self.invalid('invoice_items',lambda rows:rows[0].update(period='2025-03'),'missing_usage_evidence')

    def test_periods_must_be_real_months(self):
        for table in ('service_usage','invoice_items'):
            for value in ('2025-13','2025-1','0000-01','2025-01-01'):
                with self.subTest(table=table,value=value):
                    self.invalid(table,lambda rows:rows[0].update(period=value),'invalid_period')

    def test_money_and_quantities_have_explicit_integer_domains(self):
        cases=[('contract_items','unit_price_cents','1.5','invalid_unit_price'),
               ('contract_items','unit_price_cents','-1','invalid_unit_price'),
               ('contract_items','unit_price_cents','0','nonpositive_unit_price'),
               ('contract_items','quantity','0','nonpositive_quantity'),
               ('contract_items','quantity','NaN','invalid_quantity'),
               ('products','unit_price_cents','0','nonpositive_unit_price'),
               ('service_usage','delivered_quantity','-1','invalid_delivered'),
               ('invoice_items','billed_cents','1.00','invalid_billed'),
               ('invoice_items','billed_cents','-1','invalid_billed')]
        for table,field,value,reason in cases:
            with self.subTest(table=table,field=field,value=value):
                self.invalid(table,lambda rows:rows[0].update({field:value}),reason)

    def test_missing_attributes_and_invalid_models_fail(self):
        self.invalid('products',lambda rows:rows[0].update(billing_model='other'),'invalid_billing_model')
        self.invalid('contract_items',lambda rows:rows[0].update(contract_id=' '),'missing_contract_id')
        self.invalid('contract_items',lambda rows:rows[0].update(item_id=' padded '),'noncanonical_item_id')

    def test_csv_headers_and_shape_fail_even_without_facts(self):
        cases=[('item_id,period\n','invalid_headers'),
               ('item_id,period,delivered_quantity,period\n','invalid_headers'),
               ('item_id,period,delivered_quantity\nitem,2025-01\n','malformed_csv_row'),
               ('item_id,period,delivered_quantity\nitem,2025-01,1,extra\n','malformed_csv_row')]
        for content,reason in cases:
            with self.subTest(reason=reason,content=content):
                self.reset()
                (self.root/'service_usage.csv').write_text(content,encoding='utf-8')
                with self.assertRaisesRegex(ValueError,reason):
                    reconcile(self.root)

    def test_missing_billing_and_zero_charge_remain_business_findings(self):
        self.edit('invoice_items',lambda rows:rows.pop(0))
        result=reconcile(self.root)
        self.assertEqual(len(result['rows']),1)
        self.assertEqual(result['rows'][0]['defect'],'MISSING_BILLING')
        self.reset()
        self.edit('invoice_items',lambda rows:rows[0].update(billed_cents='0'))
        result=reconcile(self.root)
        self.assertEqual(len(result['rows']),1)
        self.assertEqual(result['rows'][0]['defect'],'UNDERBILLING')
        self.assertGreater(result['rows'][0]['gap'],0)

    def test_local_and_browser_engine_source_are_identical(self):
        project=Path(__file__).resolve().parents[1]
        html=(project.parent/'docs/revenueguard-sandbox/index.html').read_text(encoding='utf-8')
        match=re.search(r'const\s+ENGINE\s*=\s*',html)
        embedded,_=json.JSONDecoder().raw_decode(html[match.end():])
        self.assertEqual(embedded,(project/'sandbox_engine.py').read_text(encoding='utf-8'))

if __name__=='__main__':
    unittest.main()
