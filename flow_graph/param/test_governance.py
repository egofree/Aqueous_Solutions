"""X-GOV-05: every superseded plan page points at AQS-PLAN-007, and the register says so."""
import os, re
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
D = os.path.join(ROOT, 'docs-authority')

def test_superseded_plans_point_to_plan_007():
    reg = open(os.path.join(D, 'DOC_REGISTER.md')).read()
    rows = re.findall(r"\| `docs-authority/([^`]+)` \|[^\n]*superseded by AQS-PLAN-007 \|", reg)
    assert len(rows) >= 10
    for f in rows:
        head = open(os.path.join(D, f)).read()[:800]
        assert 'AQS-PLAN-007' in head, f

def test_gated_derived_files_not_stale():
    """X-GOV-06: pipeline outputs must be regenerated with the graph."""
    import subprocess, sys
    r = subprocess.run([sys.executable, os.path.join(D, '_rev_stamp.py'), '--check-only'], cwd=ROOT, capture_output=True, text=True)
    assert r.returncode == 0, r.stdout
