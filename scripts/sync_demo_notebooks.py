"""One-off maintenance helper: synchronize runnable Python and clear stale outputs."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for project, stem in [('fp-cost-forecast', 'it_cost_forecast'),
                      ('databricks-pipeline-template', 'cost_pipeline_bronze_silver_gold'),
                      ('ai-agent-fpa-query', 'genie_query_handler')]:
    path = ROOT / project / 'notebooks' / (stem + '.ipynb')
    notebook = json.loads(path.read_text(encoding='utf-8'))
    loader = f'''from pathlib import Path
import runpy
candidates = [base / "{project}/notebooks/{stem}.py" for base in (Path.cwd(), *Path.cwd().parents)]
candidates.append(Path.cwd() / "{stem}.py")
script_path = next((p for p in candidates if p.is_file()), None)
if script_path is None:
    raise RuntimeError("Run this notebook from the checked-out repository or its notebook directory")
demo = runpy.run_path(str(script_path))
'''
    examples = {
        'fp-cost-forecast': 'result = demo["run_forecast"](history_months=36)\nprint(result)\n',
        'ai-agent-fpa-query': 'result = demo["ask_genie"]("total IT cost for 2025-05", mode="local")\nprint(result)\n',
        'databricks-pipeline-template': '''import csv
source = script_path.parents[1] / "example.csv"
with source.open(encoding="utf-8", newline="") as stream:
    records = list(csv.DictReader(stream))
Path("reports").mkdir(exist_ok=True)
print(demo["run_local_batch"]("reports/local-costs.db", records, "example-1"))
'''}
    notebook['cells'] = [
        {'cell_type': 'markdown', 'metadata': {}, 'source': [
            '# Reproducible demonstration\n',
            'See the project README for execution mode, prerequisites and limitations.\n',
            'This notebook loads the adjacent tested Python script. Outputs are intentionally cleared.\n',
            'Run from the project repository or use the adjacent script CLI.\n']},
        {'cell_type': 'code', 'execution_count': None, 'metadata': {},
         'outputs': [], 'source': (loader + examples[project]).splitlines(keepends=True)}]
    path.write_text(json.dumps(notebook, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
