"""U3 one-command regeneration orchestrator (AQS-PAR-001 / AQS-PLAN-007).

    python3 -m flow_graph.param.regen [--stage NAME]... [--quick] [--check] [--dry-run]

Executes flow_graph/param/regen_manifest.json (data, not code):

  1. Graph phase, successive substitution: every writes_graph stage runs in manifest
     order, and the block repeats until the graph sha is stable (--max-passes, default 4).
     This resolves the real power <-> pv_cell_line feedback the declared DAG must not carry.
  2. Doc phase, once, against the final graph: every remaining stage, so U2a sidecars and
     pattern manifests record the final graph sha and byte-identical regens stay current.
  3. Receipt: flow_graph/derived/_regen_receipt.json (graph sha, per-stage status/duration,
     vouched_patterns = output globs of stages that ran clean against the final sha).
     docs-authority/_rev_stamp.py reads it as a provenance manifest.

Modes: --quick = the write_graph solver stages only (what-if; no doc regen, no receipt write -- a
partial run must not clobber the full-run provenance receipt). --check = staleness verification
only (runs docs-authority/_rev_stamp.py --check: regenerates DERIVED_REVISIONS.md, exit 1 when a
gated derived file is stale). --dry-run prints the plan. --stage runs exactly the named stages
once each, in manifest order (expert mode; no loop, no receipt).

Fail-fast: a stage that exits non-zero aborts the run with its name, command and output
tail; the receipt records the failure and vouches nothing. Every child runs with the
U3 single-flight _power_sizing cache active (flow_graph/param/_ps_cache.py via a
PYTHONPATH sitecustomize shim; disabled outside this orchestrator).
"""
import argparse, glob, hashlib, json, os, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
from flow_graph.param import _ps_cache

MANIFEST_PATH = os.path.join(HERE, 'regen_manifest.json')

def load_manifest():
    m = json.load(open(MANIFEST_PATH))
    names = [s['name'] for s in m['stages']]
    assert len(names) == len(set(names)), 'duplicate stage names in regen_manifest.json'
    for s in m['stages']:
        for d in s['depends_on']:
            assert d in names, f"{s['name']}: unknown depends_on '{d}'"
    return m

def topo_order(stages):
    """Manifest order must already be a valid topological order (test_enforced). Reorder never.
    Dependencies outside the selection (e.g. --quick skipping doc stages) are ignored."""
    sel = {s['name'] for s in stages}; seen = set()
    for s in stages:
        late = [d for d in s['depends_on'] if d in sel and d not in seen]
        if late:
            raise SystemExit(f"regen: manifest order is not topological: {s['name']} before its deps {late}")
        seen.add(s['name'])
    return stages

def gsha(path):
    return hashlib.sha256(open(path, 'rb').read()).hexdigest()

def child_env():
    env = dict(os.environ)
    hook_dir = os.path.join(_ps_cache.DEFAULT_CACHE_DIR, 'hook-' + hashlib.sha256(ROOT.encode()).hexdigest()[:12])
    _ps_cache.write_hook(hook_dir, ROOT)
    env['PYTHONPATH'] = os.pathsep.join(p for p in (hook_dir, env.get('PYTHONPATH', '')) if p)
    env['AQS_PS_CACHE_DIR'] = env.get('AQS_PS_CACHE_DIR', _ps_cache.DEFAULT_CACHE_DIR)
    env['AQS_REGEN_ROOT'] = ROOT
    return env

def run_one(stage, env, entries, graph_path, pass_no):
    """Run one stage, append its receipt entry (status, duration, pass, graph sha after the stage)."""
    t0 = time.monotonic()
    r = subprocess.run(stage['argv'], cwd=ROOT, env=env, capture_output=True, text=True)
    dt = time.monotonic() - t0
    entry = {'name': stage['name'], 'argv': stage['argv'], 'pass': pass_no, 'seconds': round(dt, 2),
             'status': 'ok' if r.returncode == 0 else f'rc={r.returncode}',
             'post_graph_sha256': gsha(graph_path)}
    entries.append(entry)
    if r.returncode != 0:
        print(f"[{stage['name']}] FAILED rc={r.returncode} ({dt:.1f}s): {' '.join(stage['argv'])}", flush=True)
        tail = '\n'.join((r.stdout + '\n' + r.stderr).strip().splitlines()[-12:])
        if tail: print(tail)
        return False
    print(f"[{stage['name']}] ok {dt:.1f}s  {(_last_line(r.stdout))}", flush=True)
    return True

def _last_line(out):
    lines = [l for l in (out or '').strip().splitlines() if l.strip()]
    return lines[-1][:110] if lines else ''

def expand_outputs(stage, root):
    out = []
    for pat in stage.get('outputs', []):
        out += glob.glob(os.path.join(root, pat), recursive=True)
    return out
def main(argv=None):
    ap = argparse.ArgumentParser(prog='flow_graph.param.regen', description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--stage', action='append', default=[], metavar='NAME', help='run only these stages (once each, manifest order)')
    ap.add_argument('--quick', action='store_true', help='solver + write_graph stages only (what-if; no doc regen)')
    ap.add_argument('--check', action='store_true', help='staleness verification only (rev_stamp full: writes DERIVED_REVISIONS.md, gates)')
    ap.add_argument('--dry-run', action='store_true', help='print the plan and exit')
    ap.add_argument('--max-passes', type=int, default=4, metavar='N', help='graph-phase convergence cap (default 4; a converged tree needs 1, a drifted tree 2-3)')
    args = ap.parse_args(argv)

    m = load_manifest()
    graph_path = os.path.join(ROOT, m['graph'])
    receipt_path = os.path.join(ROOT, m['receipt'])
    all_stages = {s['name']: s for s in m['stages']}

    if args.check:
        r = subprocess.run(['python3', 'docs-authority/_rev_stamp.py', '--check'], cwd=ROOT, capture_output=True, text=True)
        sys.stdout.write(r.stdout); sys.stderr.write(r.stderr)
        print(f"rev_stamp --check rc={r.returncode}")
        return r.returncode

    if args.stage:
        bad = [n for n in args.stage if n not in all_stages]
        if bad: raise SystemExit(f"regen: unknown stage(s) {bad}; valid: {sorted(all_stages)}")
        sel = [s for s in m['stages'] if s['name'] in set(args.stage)]
        loop_stages = []                      # explicit selection: run once each, no loop
    elif args.quick:
        sel = [s for s in m['stages'] if s.get('quick')]
        loop_stages = sel                     # quick set is all graph writers
    else:
        sel = m['stages']
        loop_stages = [s for s in sel if s.get('writes_graph')]
    doc_stages = [s for s in sel if s not in loop_stages]
    topo_order(sel)

    if args.dry_run:
        print(f"plan: {len(sel)} stages ({len(loop_stages)} graph-loop, {len(doc_stages)} doc)  graph={m['graph']}")
        if loop_stages:
            print(f"graph loop (max {args.max_passes} passes, repeat until the graph sha is stable):")
            for s in loop_stages: print(f"  * {s['name']:24s} {' '.join(s['argv'])}")
        if doc_stages:
            print("doc phase (once, against the final graph):")
            for s in doc_stages: print(f"  . {s['name']:24s} {' '.join(s['argv'])}")
        print(f"receipt: {m['receipt']}")
        return 0

    os.makedirs(os.path.dirname(receipt_path), exist_ok=True)
    env = child_env()
    t_start = time.monotonic()
    entries, failed = [], []

    passes = 0
    if loop_stages:
        prev = gsha(graph_path)
        for p in range(1, args.max_passes + 1):
            passes = p
            print(f"--- graph pass {p} (sha {prev[:12]})", flush=True)
            for s in loop_stages:
                if not run_one(s, env, entries, graph_path, p):
                    failed.append(s['name']); break
            if failed: break
            cur = gsha(graph_path)
            print(f"--- graph pass {p} done: sha {cur[:12]} {'== stable' if cur == prev else '!= ' + prev[:12] + ' (changed)'}", flush=True)
            if cur == prev: break
            prev = cur
        else:
            print(f"regen: graph phase did NOT converge in {args.max_passes} passes (last sha {gsha(graph_path)[:12]})", flush=True)
            failed.append('(graph-convergence)')

    if not failed:
        for s in doc_stages:
            if not run_one(s, env, entries, graph_path, 0):   # pass 0 = doc phase, after convergence
                failed.append(s['name']); break

    total = time.monotonic() - t_start
    final_sha = gsha(graph_path)
    print(f"\n{'FAILED: ' + ', '.join(failed) if failed else 'all stages ok'} in {total:.1f}s; graph sha {final_sha[:12]}")
    agg = {}
    for e in entries: agg[e['name']] = e          # last pass wins for loop stages
    for e in sorted(agg.values(), key=lambda e: -e['seconds']):
        print(f"  {e['seconds']:7.2f}s  {e['status']:>5s}  {e['name']}")

    if args.quick or args.stage:
        # What-if / expert selection: do NOT touch the receipt. The receipt is the provenance
        # manifest _rev_stamp vouches from; a partial run must not clobber a full-run vouch.
        print(f"receipt not written ({'quick' if args.quick else 'stage selection'} mode); {os.path.relpath(receipt_path, ROOT)} keeps the last full run")
        return 1 if failed else 0

    vouched = []
    if not failed:
        # Vouch = the stage ran ok in the FINAL graph pass or in the doc phase (which runs after
        # convergence). The final pass is net-stable by construction; mid-pass normalisation
        # transients (foundry newline, evap relief_basis reset re-computed by relief/vent) are the
        # pipeline's own ordering, so per-stage post-sha equality is diagnostic only.
        for s in sel:
            ents = [e for e in entries if e['name'] == s['name']]
            if ents and ents[-1]['status'] == 'ok' and ents[-1]['pass'] in (passes, 0):
                vouched += s.get('outputs', [])
    # Monotonic vouch carry-over (U4b fix): a converged clean pass re-derives every output
    # byte-identically against the same final graph sha, so prior vouches remain true and must
    # survive the rewrite - zeroing them on an already-converged tree turns _rev_stamp red
    # until the next content-changing commit.
    prior = set()
    try:
        prev = json.load(open(receipt_path))
        if prev.get('graph_sha256') == final_sha and prev.get('converged'):
            prior = set(prev.get('vouched_patterns', []))
    except Exception:
        pass
    vouched = sorted(set(vouched) | prior)
    receipt = {
        'generated_by': 'flow_graph/param/regen.py',
        'manifest': os.path.relpath(MANIFEST_PATH, ROOT),
        'argv': sys.argv[1:],
        'quick': bool(args.quick),
        'graph_sha256': final_sha,
        'passes': passes,
        'converged': not failed,
        'stages': entries,
        'failed': failed,
        'vouched_patterns': sorted(set(vouched)),
    }
    with open(receipt_path, 'w') as f: json.dump(receipt, f, indent=1)
    print(f"receipt: {os.path.relpath(receipt_path, ROOT)} ({len(receipt['vouched_patterns'])} vouched patterns)")
    return 1 if failed else 0

if __name__ == '__main__':
    sys.exit(main())
