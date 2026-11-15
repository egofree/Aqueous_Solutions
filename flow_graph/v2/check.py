"""engine v2: the check — recompute and compare. The source tree is never written.

check(graph_path, committed_manifest_path) recomputes the solve in memory, renders
the model to bytes, compares them with the committed artifacts, compares the
current input/code hashes with the committed manifest, and reports everything
that would change. Abstentions fail closed: a missing committed manifest, a
missing input file or an unknown dimension is a failure, never a warning.
"""
import hashlib, json, os, sys

from . import manifest as MF
from . import solve as SL
from .graph_io import bytes as render
from .grid import Grid


def check(graph_path=None, manifest_path=None, inputs=None):
    """Returns (ok: bool, report_lines: list[str]). Pure; writes nothing."""
    lines = []
    graph_path = graph_path or os.path.join(SL.ROOT, SL.GRAPH_PATH)
    mpath = manifest_path or os.path.join(SL.ROOT, 'flow_graph/derived/_input_manifest_v2.json')
    inputs = inputs or {}
    ok = True

    if not os.path.exists(mpath):
        return False, [f'FAIL: no committed manifest at {mpath}; run the update once to establish it']

    with open(mpath, encoding='utf-8') as f:
        committed = json.load(f)

    current = MF.build(SL.FNS)
    if current['code'] != committed.get('code'):
        changed = _changed_functions(current, committed)
        lines.append(f'stale (code changed): {changed or "the engine package"}')
        ok = False
    for p, sha in current['inputs'].items():
        if not os.path.exists(os.path.join(MF.ROOT, p)):
            lines.append(f'FAIL: declared input {p} is missing'); ok = False
        elif committed['inputs'].get(p) != sha:
            lines.append(f'stale (input changed): {p}'); ok = False

    try:
        model = SL.solve(inputs, graph_path)
    except Exception as e:                                   # the solve must not crash silently
        return False, [f'FAIL: the solve raised: {type(e).__name__}: {e}']

    try:
        with open(graph_path, 'rb') as f:
            committed_bytes = f.read()
    except OSError as e:
        return False, [f'FAIL: the graph is unreadable: {e}']
    rendered = render(model, Grid.load())
    if rendered != committed_bytes:
        n = _first_diff(committed_bytes, rendered)
        lines.append(f'stale (file): {SL.GRAPH_PATH} differs from the render (first difference at byte {n})')
        ok = False
    if committed.get('artifact_sha256') != hashlib.sha256(rendered).hexdigest():
        lines.append(f'stale (content): {SL.GRAPH_PATH} is not the render this manifest describes')
        ok = False

    if ok:
        lines.append('check: fresh — regeneration would reproduce every committed byte')
    return ok, lines


def _changed_functions(current, committed):
    old = dict(committed.get('functions') or [])
    return sorted(name for name, fp in current['functions'] if old.get(name) != fp)


def _first_diff(a, b):
    for i, (x, y) in enumerate(zip(a, b)):
        if x != y:
            return i
    return min(len(a), len(b))


def update(graph_path=None, manifest_path=None, inputs=None):
    """The engine's single writer entry: solve, write the graph atomically, write
    the manifest. Returns the report lines of a post-write check (which must be
    fresh — a check that fails right after an update is a bug in the engine)."""
    graph_path = graph_path or os.path.join(SL.ROOT, SL.GRAPH_PATH)
    manifest_path = manifest_path or os.path.join(SL.ROOT, 'flow_graph/derived/_input_manifest_v2.json')
    inputs = inputs or {}
    from .graph_io import write
    model = SL.solve(inputs, graph_path)
    write(graph_path, model, Grid.load())
    m = MF.build(SL.FNS, artifact_sha=hashlib.sha256(render(model, Grid.load())).hexdigest())
    with open(manifest_path, 'w', encoding='utf-8') as f:
        f.write(MF.dumps(m))
    ok, lines = check(graph_path, manifest_path, inputs)
    return ok, lines


def main():
    ok, lines = check()
    for ln in lines:
        print(ln)
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
