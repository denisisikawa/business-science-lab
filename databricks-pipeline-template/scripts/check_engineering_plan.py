"""Validate a declarative lab design plan. Does not deploy or inspect a workspace."""
import argparse
import json
from pathlib import Path, PurePosixPath
import re

POLICY = Path(__file__).resolve().parents[1] / 'standards/engineering.json'

def validate_plan(plan, policy=None):
    policy = policy or json.loads(POLICY.read_text(encoding='utf-8'))
    def require(condition, message):
        if not condition:
            raise ValueError(message)
    def named(value):
        return isinstance(value, str) and re.fullmatch(policy['identifier_pattern'], value) is not None
    require(isinstance(plan, dict), 'Plan must be an object')
    require(plan.get('policy_version') == policy['version'], 'Unsupported policy version')
    env = plan.get('environment')
    require(env in policy['environments'], 'Unknown environment')
    catalog = policy['catalog_prefix'] + '_' + env
    directories = plan.get('directories')
    require(isinstance(directories, list) and bool(directories), 'Directories required')
    for directory in directories:
        require(isinstance(directory, str) and bool(directory), 'Invalid directory')
        path = PurePosixPath(directory)
        require(not path.is_absolute() and ':' not in directory and '\\' not in directory and '..' not in path.parts, 'Unsafe directory: ' + directory)
        require(bool(path.parts) and path.parts[0] in policy['directory_roots'], 'Unknown directory root: ' + directory)
    objects = plan.get('objects')
    require(isinstance(objects, list) and bool(objects), 'Objects required')
    identities = set()
    for item in objects:
        require(isinstance(item, dict), 'Object definition must be an object')
        schema, name = item.get('schema'), item.get('name')
        require(item.get('catalog') == catalog, 'Cross-environment catalog or invalid catalog')
        require(schema in policy['schemas'] and named(name), 'Invalid schema or object name')
        require(item.get('kind') in ('table','view'), 'Unsupported object kind')
        identity = (catalog, schema, name)
        require(identity not in identities, 'Duplicate object')
        identities.add(identity)
        columns = item.get('columns')
        require(isinstance(columns, list) and bool(columns), 'Columns required')
        names = []
        for column in columns:
            require(isinstance(column, dict) and isinstance(column.get('name'),str) and re.fullmatch(policy['column_pattern'],column['name']) is not None, 'Invalid column')
            names.append(column['name'])
            require(type(column.get('nullable')) is bool, 'Explicit nullability required')
            dtype = column.get('type')
            valid = isinstance(dtype, str) and dtype in ('string','date','timestamp','bigint','int','boolean')
            decimal = re.fullmatch(r'decimal\((\d+),(\d+)\)', dtype or '') if isinstance(dtype, str) else None
            if decimal:
                precision, scale = map(int, decimal.groups())
                valid = 1 <= precision <= 38 and 0 <= scale <= precision
            require(valid, 'Invalid or unsupported type')
            if column['name'] in ('amount','total_amount'):
                require(dtype == policy['money_type'], 'Money must use the contract decimal type')
        require(len(names) == len(set(names)), 'Duplicate column')
        require(set(policy['required_columns'][schema]).issubset(names), 'Missing layer metadata or contract fields')
        for column in columns:
            if column['name'] in policy['required_columns'][schema]:
                require(column['nullable'] is False, 'Contract fields cannot be nullable')
                require(column['type'] == policy['required_types'][schema][column['name']], 'Contract field type mismatch')
        grain = item.get('grain')
        require(isinstance(grain, list) and bool(grain) and len(grain)==len(set(grain)) and set(grain).issubset(names), 'Invalid grain')
        key = item.get('business_key', [])
        require(isinstance(key,list) and len(key)==len(set(key)) and set(key).issubset(names), 'Invalid business key')
        for column in columns:
            if column['name'] in key or column['name'] in grain:
                require(column['nullable'] is False, 'Key/grain fields cannot be nullable')
        if schema == 'silver':
            require(key == policy['silver_key'] and grain == key, 'Silver transaction key/grain differs from lab contract')
        if schema == 'gold':
            require(grain == policy['gold_grain'], 'Gold grain differs from lab contract')
        if schema in ('silver','gold'):
            require(item.get('currency') == policy['currency'], 'Unsupported currency')
    job = plan.get('job')
    require(isinstance(job,dict) and named(job.get('name')), 'Invalid job')
    require(job['name'].endswith('_'+env), 'Job name must identify the environment')
    tasks = job.get('tasks')
    require(isinstance(tasks,list) and bool(tasks), 'Tasks required')
    require(all(isinstance(t,dict) and named(t.get('key')) for t in tasks), 'Invalid task key')
    keys = [t['key'] for t in tasks]
    require(len(keys)==len(set(keys)), 'Duplicate task key')
    graph = {}
    for task in tasks:
        deps = task.get('depends_on')
        require(isinstance(deps,list) and len(deps)==len(set(deps)) and set(deps).issubset(keys), 'Invalid dependency')
        graph[task['key']] = deps
        require(type(task.get('timeout_seconds')) is int and task['timeout_seconds']>0, 'Positive timeout required')
        require(type(task.get('max_retries')) is int and task['max_retries']>=0, 'Invalid retries')
        require(type(task.get('idempotent')) is bool, 'Idempotence declaration required')
        if task['max_retries']:
            require(task['idempotent'] and bool(task.get('idempotency_evidence')), 'Retry requires declared idempotence and evidence reference')
    seen, active = set(), set()
    def visit(key):
        require(key not in active, 'Dependency cycle')
        if key in seen:
            return
        active.add(key)
        for dependency in graph[key]:
            visit(dependency)
        active.remove(key)
        seen.add(key)
    for key in keys:
        visit(key)
    return {'objects':len(objects), 'tasks':len(tasks), 'policy_version':policy['version']}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan',type=Path,required=True)
    args=parser.parse_args()
    try:
        result=validate_plan(json.loads(args.plan.read_text(encoding='utf-8')))
    except (ValueError,TypeError,KeyError) as error:
        parser.exit(1, 'INVALID PLAN: '+str(error)+'\n')
    print('VALID LAB DESIGN PLAN: '+json.dumps(result))
    print('This checks declarations only, not runtime, IAM, deployment or financial approval.')

if __name__=='__main__':
    main()
