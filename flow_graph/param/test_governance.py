"""X-GOV-05: every superseded plan page points at AQS-PLAN-007, and the register says so."""
import os, re
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
D = os.path.join(ROOT, 'docs-authority')

def test_superseded_plans_point_to_plan_007():
    """Every page the register marks superseded names a successor that is a current page;
    superseded plan pages point at the master task list AQS-PLAN-007."""
    reg = open(os.path.join(D, 'DOC_REGISTER.md')).read()
    current = set(re.findall(r"^\| (AQS-\S+) \| `[^`]+` \|[^\n]*\| current \|$", reg, flags=re.M))
    rows = re.findall(r"^\| (AQS-\S+) \| `docs-authority/([^`]+)` \|[^\n]*\| superseded by (AQS-\S+) \|$", reg, flags=re.M)
    assert rows
    for num, f, succ in rows:
        assert succ in current, (f, succ)
        if 'PLAN' in num or 'PLAN' in f.upper():
            assert 'AQS-PLAN-007' in open(os.path.join(D, f)).read()[:800], f

def test_gated_derived_files_not_stale():
    """X-GOV-06: pipeline outputs must be regenerated with the graph."""
    import subprocess, sys
    r = subprocess.run([sys.executable, os.path.join(D, '_rev_stamp.py'), '--check-only'], cwd=ROOT, capture_output=True, text=True)
    assert r.returncode == 0, r.stdout

def test_receipt_vouch_trust_is_sha_only():
    """U4c (2026-11-03): the gate trusts a regen receipt's vouches on a graph-sha match alone.
    `converged` is run-health reporting; one oscillating stage must not un-vouch the globs
    other stages verified (that global coupling turned a single flaky view into 959 false
    stale files at the gate)."""
    import importlib.util
    spec = importlib.util.spec_from_file_location('aqs_rev_stamp', os.path.join(D, '_rev_stamp.py'))
    rs = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(rs)
    r = {'graph_sha256': 'abc123', 'converged': False, 'vouched_patterns': ['docs-authority/duties/*'], 'vouched_files': ['flow_graph/views/pfd.svg']}
    assert rs.receipt_vouched(r, 'abc123') == ['docs-authority/duties/*', 'flow_graph/views/pfd.svg']
    assert rs.receipt_vouched(r, 'other-sha') == []
    assert rs.receipt_vouched({'graph_sha256': 'abc123'}, 'abc123') == []


def _rev_stamp_module():
    import importlib.util
    spec = importlib.util.spec_from_file_location('aqs_rev_stamp', os.path.join(D, '_rev_stamp.py'))
    rs = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(rs)
    return rs

def test_register_does_not_record_graph_commit():
    """AQS-GOV-006 Rev C: the register text depends on each file's status and the graph revision only.
    Two evaluations that differ only in the graph commit a file was made from render identical
    bytes, so a graph commit cannot produce a stamp-only rewrite of the register."""
    rs = _rev_stamp_module()
    a = [('docs-authority/LOAD_LIST.md', 'b1f7d71 (regenerated, no change)', 'current'), ('flow_graph/views/pfd.dot', 'working tree', 'current')]
    b = [('docs-authority/LOAD_LIST.md', 'd160aa5', 'current'), ('flow_graph/views/pfd.dot', '873b2d1', 'current')]
    assert rs.render(a, 0, 'AD') == rs.render(b, 0, 'AD')
    assert 'b1f7d71' not in rs.render(a, 0, 'AD')

def test_regen_check_is_read_only():
    """`python3 -m flow_graph.param.regen --check` must not write the register (it runs --check-only)."""
    src = open(os.path.join(ROOT, 'flow_graph', 'param', 'regen.py')).read()
    assert "'docs-authority/_rev_stamp.py', '--check-only'" in src
