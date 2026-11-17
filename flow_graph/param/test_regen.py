"""U3 regen orchestrator tests (flow_graph/param/regen.py + regen_manifest.json).

The regen entry is the engine v2 update+check since the P4 flip; the v1
pipeline survives behind --legacy with its manifest, receipt and vouch
machinery unchanged, and the tests below hold both:

  1. the legacy manifest is a DAG: manifest order is a valid topological
     order, names unique, deps known, and every stage argv target exists on
     disk (the --legacy machinery's data contract);
  2. regen --check is the engine v2 check and is green at the current HEAD;
  3. the v1 quick write test retired at the flip (the v1 writers re-serialize
     the shared graph out of the canonical form; see the skipped test);
  4. the receipt-vouch semantics and the committed receipt's structural
     invariants hold for the --legacy artifacts they describe.
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
    """RETIRED with the v1 quick-write machinery (the P4 flip): `regen --quick`
    still runs the v1 solver stages under --legacy, but the v1 writers
    re-serialize the shared graph out of the engine v2 canonical form, so the
    test can no longer run them against the reference tree. The v2 what-if is
    the default path itself (about two minutes, update + fresh check); the
    byte-stability contract is the idempotency gate
    (flow_graph/check_regen_idempotent.py) and the engine's own determinism
    proofs (flow_graph/v2/test_core.py)."""
    import pytest
    pytest.skip('the v1 quick write test retired at the P4 flip (see the docstring)')

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
