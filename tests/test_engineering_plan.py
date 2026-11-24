"""Observable design-policy checks; no workspace or deployment involved."""
import copy
import importlib.util
import json
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'databricks-pipeline-template'
spec = importlib.util.spec_from_file_location('engineering_plan', BASE / 'scripts/check_engineering_plan.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

@pytest.fixture
def plan():
    return json.loads((BASE / 'standards/example-plan.json').read_text(encoding='utf-8'))

def test_valid_plan_and_no_mutation(plan):
    before = copy.deepcopy(plan)
    assert module.validate_plan(plan) == {'objects':3,'tasks':3,'policy_version':'1.0'}
    assert plan == before

@pytest.mark.parametrize('change,reason', [
    (lambda p:p.update(policy_version='2'), 'policy version'),
    (lambda p:p.update(environment='unknown'), 'environment'),
    (lambda p:p['objects'][0].update(catalog='finance_lab_prod'), 'Cross-environment'),
    (lambda p:p['objects'][0].update(schema='default'), 'schema'),
    (lambda p:p['objects'][0].update(name='Custo Final'), 'object name'),
    (lambda p:p['objects'].append(copy.deepcopy(p['objects'][0])), 'Duplicate object'),
    (lambda p:p['objects'][1]['columns'][-1].update(type='double'), 'unsupported type'),
    (lambda p:p['objects'][1]['columns'][-1].update(type='decimal(20,2)'), 'Money'),
    (lambda p:p['objects'][1]['columns'][3].update(type='string'), 'type mismatch'),
    (lambda p:p['objects'][1]['columns'][0].update(nullable=True), 'nullable'),
    (lambda p:p['objects'][0]['columns'].pop(0), 'Missing layer'),
    (lambda p:p['objects'][1].update(business_key=['transaction_id']), 'Silver transaction'),
    (lambda p:p['objects'][2].update(grain=['month']), 'Gold grain'),
    (lambda p:p['objects'][2].update(currency='USD'), 'currency'),
    (lambda p:p['directories'].append('../outside'), 'Unsafe directory'),
    (lambda p:p['directories'].append('C:/outside'), 'Unsafe directory'),
    (lambda p:p['directories'].append('.'), 'directory root'),
    (lambda p:p['job']['tasks'].append(copy.deepcopy(p['job']['tasks'][0])), 'Duplicate task'),
    (lambda p:p['job']['tasks'][0].update(depends_on=['unknown']), 'dependency'),
    (lambda p:p['job']['tasks'][0].update(depends_on=['aggregate_gold']), 'cycle'),
    (lambda p:p['job']['tasks'][0].update(timeout_seconds=0), 'timeout'),
    (lambda p:p['job']['tasks'][0].update(max_retries=1), 'Retry requires'),
    (lambda p:p['job']['tasks'][0].update(max_retries=1,idempotent=True), 'Retry requires'),
    (lambda p:p['job'].update(name='finance_cost_pipeline_prod'), 'Job name'),
])
def test_rejects_unsafe_or_incompatible_plan(plan,change,reason):
    change(plan)
    with pytest.raises(ValueError,match=reason):
        module.validate_plan(plan)

def test_retry_declaration_with_reference_is_not_runtime_proof(plan):
    plan['job']['tasks'][0].update(max_retries=1,idempotent=True,idempotency_evidence='review-required-example')
    assert module.validate_plan(plan)['tasks'] == 3

def test_invalid_decimal_definition(plan):
    plan['objects'][1]['columns'].append({'name':'ratio','type':'decimal(2,3)','nullable':True})
    with pytest.raises(ValueError,match='unsupported type'):
        module.validate_plan(plan)
