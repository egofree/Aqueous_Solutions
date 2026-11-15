"""Input-hash manifest (pipeline step 4): build, staleness verdict, and the read-audit capture.

The migration plan's check for this step: a test that changes each declared input and expects
the dependent outputs to show stale. Cases 2-4 below are exactly that, on a sandbox tree.
"""
import json, os, subprocess, sys

import pytest

from flow_graph.param import input_manifest as IM

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def stage(name, outputs, depends_on=None):
    return {'name': name, 'argv': ['python3', '-m', 'x', name], 'outputs': outputs,
            'depends_on': depends_on or [], 'quick': False, 'writes_graph': False}


@pytest.fixture()
def sand(tmp_path):
    """A sandbox tree: two inputs, two stages, two outputs (present on disk)."""
    root = tmp_path
    (root / 'a.txt').write_text('alpha\n')
    (root / 'b.txt').write_text('beta\n')
    (root / 'out1.txt').write_text('out1\n')
    (root / 'out2.txt').write_text('out2\n')
    rm = {'stages': [stage('S1', ['out1.txt']), stage('S2', ['out2.txt'])]}
    cap = {
        'S1': {'paths': {str(root / 'a.txt')}, 'status': 'ok', 'complete': True},
        'S2': {'paths': {str(root / 'a.txt'), str(root / 'b.txt')}, 'status': 'ok', 'complete': True},
    }
    return root, rm, cap


def test_manifest_is_byte_stable(sand):
    root, rm, cap = sand
    a = IM.build(cap, str(root), 'g' * 64)
    b = IM.build(dict(cap, S1=dict(cap['S1'], paths=set(cap['S1']['paths']))), str(root), 'g' * 64)
    assert json.dumps(a, indent=1, sort_keys=True) == json.dumps(b, indent=1, sort_keys=True)


def test_fresh_then_each_input_change_shows_dependent_outputs_stale(sand):
    root, rm, cap = sand
    im = IM.build(cap, str(root), 'g' * 64)
    sm = IM.output_stage_map(rm, str(root))
    assert IM.verdict(im, sm, 'out1.txt', str(root))[0] == 'fresh'
    assert IM.verdict(im, sm, 'out2.txt', str(root))[0] == 'fresh'
    # change each declared input in turn; the dependents go stale, the rest stay fresh
    (root / 'a.txt').write_text('ALPHA\n')
    assert IM.verdict(im, sm, 'out1.txt', str(root))[0] == 'stale'
    assert IM.verdict(im, sm, 'out2.txt', str(root))[0] == 'stale'
    (root / 'a.txt').write_text('alpha\n')
    (root / 'b.txt').write_text('BETA\n')
    assert IM.verdict(im, sm, 'out1.txt', str(root))[0] == 'fresh'
    assert IM.verdict(im, sm, 'out2.txt', str(root))[0] == 'stale'


def test_vanished_input_and_failed_producer(sand):
    root, rm, cap = sand
    (root / 'b.txt').unlink()
    im = IM.build(cap, str(root), 'g' * 64)
    sm = IM.output_stage_map(rm, str(root))
    assert IM.verdict(im, sm, 'out2.txt', str(root))[0] == 'stale'
    cap2 = {'S1': {'paths': set(cap['S1']['paths']), 'status': 'rc=1', 'complete': True}}
    im2 = IM.build(cap2, str(root), 'g' * 64)
    v, d = IM.verdict(im2, sm, 'out1.txt', str(root))
    assert v == 'stale' and 'rc=1' in d


def test_abstentions(sand):
    root, rm, cap = sand
    sm = IM.output_stage_map(rm, str(root))
    assert IM.verdict(None, sm, 'out1.txt', str(root))[0] == 'no-manifest'
    im = IM.build({'S2': cap['S2']}, str(root), 'g' * 64)          # S1 missing -> no-entry
    assert IM.verdict(im, sm, 'out1.txt', str(root))[0] == 'no-entry'
    cap3 = {'S1': {'paths': set(), 'status': 'ok', 'complete': False}}
    im3 = IM.build(cap3, str(root), 'g' * 64)
    assert IM.verdict(im3, sm, 'out1.txt', str(root))[0] == 'capture-incomplete'
    assert IM.verdict(im3, sm, 'no-such-output.txt', str(root))[0] == 'no-stage'


def test_census_counts_disagreements_both_ways(sand):
    root, rm, cap = sand
    im = IM.build(cap, str(root), 'g' * 64)
    sm = IM.output_stage_map(rm, str(root))
    (root / 'a.txt').write_text('ALPHA\n')
    c = IM.census(im, sm, str(root), {'out1.txt': 'current', 'out2.txt': 'stale',
                                      'unrelated.txt': 'current'})
    assert set(c['input_stale']) == {'out1.txt'}       # committed rule says current, inputs say stale
    assert c['agree'] == 1 and c['unmeasured'] == 1    # out2 agrees (both stale); unrelated unmeasured
    (root / 'a.txt').write_text('alpha\n')
    c = IM.census(im, sm, str(root), {'out1.txt': 'stale'})
    assert set(c['input_fresh']) == {'out1.txt'} and c['agree'] == 0
    c = IM.census(im, sm, str(root), {'out1.txt': 'current', 'out2.txt': 'current'})
    assert c['agree'] == 2 and not c['input_stale'] and not c['input_fresh']


def test_read_audit_hook_records_project_reads_and_excludes_bookkeeping(tmp_path):
    """Run the hook in a subprocess: a project read is recorded, writes and bookkeeping are not."""
    script = f'''
import sys
sys.path.insert(0, {str(ROOT)!r})
from flow_graph.param import input_audit
base = {str(tmp_path / "cap")!r}
root = {str(tmp_path)!r}
rec = input_audit.install(root=root, base=base)
open({str(tmp_path / "a.txt")!r}).read()                       # recorded (create it first)
open({str(tmp_path / "a.txt")!r}, "w").write("alpha\\n")        # write: not recorded
open({str(tmp_path / ".git")!r} + "/config").read()             # .git: not recorded
input_audit.dump()
'''
    (tmp_path / 'a.txt').write_text('x\n')
    (tmp_path / '.git').mkdir()
    (tmp_path / '.git' / 'config').write_text('[x]\n')
    r = subprocess.run([sys.executable, '-c', script], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    sidecars = list(tmp_path.glob('cap.*'))
    assert len(sidecars) == 1
    recorded = json.load(open(sidecars[0]))
    assert recorded == [str(tmp_path / 'a.txt')]


def test_wrapper_runs_a_stage_and_dumps_one_merged_sidecar(tmp_path):
    """The real wiring: wrapper -> regen --dry-run, shim installs the hook, sidecar carries the read."""
    shim = tmp_path / 'shim'
    shim.mkdir()
    (shim / 'sitecustomize.py').write_text(
        'try:\n    import input_audit\n    input_audit.install()\nexcept Exception:\n    pass\n')
    env = dict(os.environ, AQS_INPUT_AUDIT=str(tmp_path / 'cap'),
               PYTHONPATH=os.pathsep.join([str(shim), os.path.join(ROOT, 'flow_graph', 'param')]))
    env.pop('PYTHONSTARTUP', None)
    r = subprocess.run([sys.executable, '-m', 'flow_graph.param.input_audit', '--capture', str(tmp_path / 'cap'),
                        '--', sys.executable, '-m', 'flow_graph.param.regen', '--dry-run'],
                       cwd=ROOT, env=env, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    sidecars = list(tmp_path.glob('cap.*'))
    assert len(sidecars) == 1
    recorded = json.load(open(sidecars[0]))
    assert os.path.join(ROOT, 'flow_graph/param/regen_manifest.json') in recorded
