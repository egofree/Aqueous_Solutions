"""X-GOV-20 gate: no vendor-data, vendor-skid or vendor-quote basis in docs or code (owner decision 2026-10-15: no vendor skids).
Plan text that names the rule itself is exempt."""
import glob, os, re
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PAT = re.compile(r'vendor (data|skid|quote|package|stamp|datasheet)', re.I)
EXEMPT = {'docs-authority/_task_plan_gen.py', 'docs-authority/TASK_PLAN.md', 'flow_graph/param/test_no_vendor_basis.py'}
def test_no_vendor_basis():
    bad = []
    for f in glob.glob(os.path.join(ROOT, 'docs-authority/**/*.*'), recursive=True) + glob.glob(os.path.join(ROOT, 'flow_graph/**/*.py'), recursive=True) + glob.glob(os.path.join(ROOT, 'models/mfg/**/*.md'), recursive=True):
        r = os.path.relpath(f, ROOT)
        if r in EXEMPT or not f.endswith(('.md', '.py', '.json', '.csv')): continue
        for i, l in enumerate(open(f, errors='ignore'), 1):
            if PAT.search(l): bad.append(f'{r}:{i}')
    assert not bad, bad[:20]
