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
    """RETIRED with the v1 receipt machinery at the P4 flip: the receipt no
    longer vouches anything (its verification leg retired; run health lives in
    the untracked _regen_run.json of the --legacy pipeline). The staleness
    rule is the engine v2 check, whose verdict the register renders."""
    import pytest
    pytest.skip('the receipt-vouch machinery retired at the P4 flip')


def _rev_stamp_module():
    import importlib.util
    spec = importlib.util.spec_from_file_location('aqs_rev_stamp', os.path.join(D, '_rev_stamp.py'))
    rs = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(rs)
    return rs

def test_register_does_not_record_graph_commit():
    """AQS-GOV-006 Rev C/D: the register text depends on each file's status,
    the verdict and the graph revision only. Two evaluations that differ only
    in a per-file revision note render identical bytes, so a graph commit
    cannot produce a stamp-only rewrite of the register."""
    rs = _rev_stamp_module()
    a = [('docs-authority/LOAD_LIST.md', '-', 'current'), ('flow_graph/views/pfd.dot', 'working tree', 'current')]
    b = [('docs-authority/LOAD_LIST.md', 'd160aa5', 'current'), ('flow_graph/views/pfd.dot', '873b2d1', 'current')]
    assert rs.render(a, 0, 'AD', True) == rs.render(b, 0, 'AD', True)
    assert 'b1f7d71' not in rs.render(a, 0, 'AD', True)

def test_regen_check_is_read_only():
    """`python3 -m flow_graph.param.regen --check` must not write anything: it
    is the engine v2 check, pure, and the register write stays with
    docs-authority/_rev_stamp.py itself."""
    src = open(os.path.join(ROOT, 'flow_graph', 'param', 'regen.py')).read()
    check_part = src[src.index('def _run_v2_check'):src.index('def main(')]
    assert "os.replace" not in check_part and "'w'" not in check_part and '"w"' not in check_part
    from flow_graph.v2 import check as V2
    import inspect
    assert 'os.replace' not in inspect.getsource(V2.check)
