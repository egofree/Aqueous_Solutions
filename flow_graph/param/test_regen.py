"""U3 regen orchestrator tests (flow_graph/param/regen.py + regen_manifest.json).

Covers the acceptance properties of the manifest and the orchestrator:
  1. the manifest is a DAG: manifest order is a valid topological order, names unique, deps known;
  2. every stage argv target exists on disk (script file or -m module path);
  3. a --quick run succeeds and leaves every quick-stage output non-empty (quick runs the
     write_graph solver stages in place; on a converged tree it is byte-stable and writes nothing,
     on a drifted tree it re-stamps the graph - which is the orchestrator doing its job);
  4. regen --check is green at the current HEAD (the X-GOV-06 gated set is regenerated/vouched);
  5. receipt vouches are per-stage verifications (U4c): a stage that failed, was skipped or was
     unstable at the final graph sha vouches nothing, and every committed vouched pattern maps to
     a stage whose receipt entry is ok and stable;
  6. the gate trusts a receipt on graph-sha match alone (see test_governance.py).
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


def _regen_module():
    import importlib.util, sys
    sys.path.insert(0, ROOT)
    spec = importlib.util.spec_from_file_location('aqs_regen', os.path.join(ROOT, 'flow_graph/param/regen.py'))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_vouches_only_verified_stages(tmp_path):
    """U4c: compute_vouches vouches a stage only when it ran ok in the final phase AND verified
    byte-stable; a partly stable stage vouches its stable files individually; a failed, skipped
    or aborted run vouches nothing; an unconverged graph phase vouches nothing at all."""
    R = _regen_module()
    # Synthetic tree: stage A owns a/dir.md and is stable; stage B owns b/x.svg and b/y.svg,
    # ran ok but oscillated on b/y.svg (unstable across the final pass); stage C failed.
    a_dir = tmp_path / 'a'; b_dir = tmp_path / 'b'; a_dir.mkdir(); b_dir.mkdir()
    (a_dir / 'dir.md').write_text('A')
    (b_dir / 'x.svg').write_text('<x/>')
    (b_dir / 'y.svg').write_text('<y2/>')          # final content (was <y/> before the pass)
    S = lambda n, outs: {'name': n, 'outputs': outs, 'amends': []}
    sa, sb, sc = S('a', ['a/dir.md']), S('b', ['b/x.svg', 'b/y.svg']), S('c', ['c/z.md'])
    loop = []
    entries = [{'name': 'a', 'status': 'ok', 'pass': 0},
               {'name': 'b', 'status': 'ok', 'pass': 0},
               {'name': 'c', 'status': 'rc=1', 'pass': 0}]
    stable = {'a': True, 'b': False}
    before = {str(a_dir / 'dir.md'): 'h1', str(b_dir / 'x.svg'): 'h2', str(b_dir / 'y.svg'): 'h_old', str(tmp_path / 'c' / 'z.md'): 'h3'}
    after = {str(a_dir / 'dir.md'): 'h1', str(b_dir / 'x.svg'): 'h2', str(b_dir / 'y.svg'): 'h_new', str(tmp_path / 'c' / 'z.md'): 'h3'}
    pats, files = R.compute_vouches([sa, sb, sc], loop, entries, stable, graph_converged=True,
                                    doc_aborted=False, doc_before=before, doc_after=after, passes=2, root=str(tmp_path))
    assert pats == ['a/dir.md'], (pats, files)          # stable stage -> glob vouched
    assert sorted(files) == ['b/x.svg'], (pats, files)  # partly stable stage -> only the stable file
    # A failing stage vouches nothing anywhere:
    pats2, files2 = R.compute_vouches([sa, sb, sc], loop, [{'name': 'a', 'status': 'ok', 'pass': 0},
                                                           {'name': 'b', 'status': 'ok', 'pass': 0},
                                                           {'name': 'c', 'status': 'rc=1', 'pass': 0}],
                                      {'a': True, 'b': True}, True, False, before, after, 2, str(tmp_path))
    assert 'c/z.md' not in pats2 + files2
    # An unconverged graph phase or an aborted doc phase vouches nothing for doc stages:
    assert R.compute_vouches([sa], loop, entries, stable, graph_converged=False,
                             doc_aborted=False, doc_before=before, doc_after=after, passes=2, root=str(tmp_path)) == ([], [])
    pats3, files3 = R.compute_vouches([sa, sb], loop, entries, {'a': True, 'b': True}, True,
                                      doc_aborted=True, doc_before=before, doc_after=after, passes=2, root=str(tmp_path))
    assert pats3 == [] and files3 == []


def test_receipt_vouches_map_to_ok_stable_stages():
    """U4c structural invariant: every vouched pattern in the committed receipt belongs to a
    manifest stage whose receipt entry ran ok and was verified stable; vouched files exist."""
    import json
    rp = os.path.join(ROOT, 'flow_graph/derived/_regen_receipt.json')
    if not os.path.exists(rp):
        return  # no receipt yet (fresh clone); regen writes one
    r = json.load(open(rp))
    m = _manifest()
    by_name = {s['name']: s for s in m['stages']}
    status = {e['name']: e for e in r.get('stages', [])}
    if any('stable' not in e for e in status.values()):
        return  # pre-U4c receipt (no per-stage stability); the next full regen rewrites it
    for pat in r.get('vouched_patterns', []):
        owners = [n for n, s in by_name.items() if pat in s.get('outputs', []) + s.get('amends', [])]
        assert owners, f'vouched pattern {pat} is not declared as any stage output/amend'
        assert any(status[n].get('status') == 'ok' and status[n].get('stable') for n in owners if n in status), pat
    for f in r.get('vouched_files', []):
        assert os.path.exists(os.path.join(ROOT, f)), f
        import fnmatch
        assert any(fnmatch.fnmatch(f, g) for n, s in by_name.items() for g in s.get('outputs', []) + s.get('amends', [])), f
