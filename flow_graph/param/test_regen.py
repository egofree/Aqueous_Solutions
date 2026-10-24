"""U3 regen orchestrator tests (flow_graph/param/regen.py + regen_manifest.json).

Covers the four acceptance properties of the manifest and the orchestrator:
  1. the manifest is a DAG: manifest order is a valid topological order, names unique, deps known;
  2. every stage argv target exists on disk (script file or -m module path);
  3. a --quick run succeeds and leaves every quick-stage output non-empty (quick runs the
     write_graph solver stages in place; on a converged tree it is byte-stable and writes nothing,
     on a drifted tree it re-stamps the graph - which is the orchestrator doing its job);
  4. regen --check is green at the current HEAD (the X-GOV-06 gated set is regenerated/vouched).
"""
import glob, json, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MANIFEST = os.path.join(ROOT, 'flow_graph/param/regen_manifest.json')

def _manifest():
    return json.load(open(MANIFEST))

def test_manifest_is_a_dag_in_topological_order():
    m = _manifest()
    stages = m['stages']
    names = [s['name'] for s in stages]
    assert len(names) == len(set(names)), 'duplicate stage names'
    seen = set()
    for s in stages:
        for d in s['depends_on']:
            assert d in seen, f"{s['name']} depends on {d}, which appears LATER in the manifest (not a topological order)"
        seen.add(s['name'])
    assert any(s.get('writes_graph') for s in stages) and any(not s.get('writes_graph') for s in stages)

def test_stage_argv_targets_exist():
    m = _manifest()
    for s in m['stages']:
        argv = s['argv']
        assert argv and argv[0] in ('python3', 'bash'), f"{s['name']}: expected a python3 or bash argv, got {argv}"
        if argv[0] == 'bash':
            assert os.path.isfile(os.path.join(ROOT, argv[1])), f"{s['name']}: script {argv[1]} not found"
        elif '-m' in argv:
            mod = argv[argv.index('-m') + 1]
            path = os.path.join(ROOT, *mod.split('.')) + '.py'
            assert os.path.isfile(path), f"{s['name']}: module {mod} not found at {path}"
        else:
            assert os.path.isfile(os.path.join(ROOT, argv[1])), f"{s['name']}: script {argv[1]} not found"

def _run(*args):
    return subprocess.run([sys.executable, '-m', 'flow_graph.param.regen', *args], cwd=ROOT, capture_output=True, text=True)

def test_quick_run_ok_and_outputs_non_empty():
    r = _run('--quick')
    assert r.returncode == 0, r.stdout[-3000:] + r.stderr[-3000:]
    assert 'receipt not written' in r.stdout, '--quick must not clobber the full-run receipt'
    m = _manifest()
    quick = [s for s in m['stages'] if s.get('quick')]
    assert quick, 'no quick stages in manifest'
    for s in quick:
        files = []
        for pat in s['outputs']:
            files += glob.glob(os.path.join(ROOT, pat))
        assert files and all(os.path.getsize(f) > 0 for f in files), f"{s['name']}: empty/missing outputs for {s['outputs']}"

def test_check_green_at_head():
    r = _run('--check')
    assert r.returncode == 0, r.stdout[-3000:] + r.stderr[-3000:]


def test_full_regen_is_idempotent():
    """A full regen on a clean tree changes nothing, twice (flow_graph/check_regen_idempotent.py).
    Slow (two full runs), so it runs only when AQS_SLOW_TESTS=1; run the script directly
    before you push a generator change."""
    import pytest
    if os.environ.get('AQS_SLOW_TESTS') != '1':
        pytest.skip('set AQS_SLOW_TESTS=1 to run the full-regen idempotency check')
    extra = ['--repeat-only'] if os.environ.get('AQS_REGEN_REPEAT_ONLY') == '1' else []
    r = subprocess.run([sys.executable, 'flow_graph/check_regen_idempotent.py', *extra], cwd=ROOT, capture_output=True, text=True)
    assert r.returncode == 0, r.stdout[-3000:] + r.stderr[-3000:]
