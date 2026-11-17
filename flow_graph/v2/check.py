"""engine v2: the check — recompute and compare. The source tree is never written.

check(graph_path, committed_manifest_path) recomputes the solve in memory, renders
the model to bytes, compares them with the committed artifacts, compares the
current input/code hashes with the committed manifest, and reports everything
that would change. The renderer registry is compared byte-exact; the duty-page
fragment registry is compared by containment: a generator-owned fragment must
OCCUR in its committed hand-authored page's bytes (position is the author's).
Abstentions fail closed: a missing committed manifest, a missing input file, a
missing duties directory or an unknown dimension is a failure, never a warning.
"""
import hashlib, json, os, re, sys

from . import inputs as IN
from . import manifest as MF
from . import solve as SL
from .graph_io import bytes as render
from .grid import Grid


def _fragment_model(graph_path, model, inputs):
    """The model the fragment rule renders under: the committed duty pages
    carry the canonical main-tree (baseline site) rates, so the rule
    re-renders them under that payload even when the caller passes a partial
    one - the engine's own P1 proofs pass drivers only, and a partial
    payload solves a different plant whose fragments would legitimately
    differ. The caller's model is reused when it already carries the site
    payload; a caller-supplied site profile always wins."""
    if (inputs or {}).get('site_profile') is not None:
        return model
    payload = dict(inputs or {})
    profile = os.path.join(MF.ROOT, 'flow_graph', 'param', 'sites', 'baseline.json')
    if os.path.exists(profile):
        with open(profile, encoding='utf-8') as f:
            payload['site_profile'] = json.load(f)
    return SL.solve(payload, graph_path)


def check(graph_path=None, manifest_path=None, inputs=None, artifact_root=None):
    """Returns (ok: bool, report_lines: list[str]). Pure; writes nothing.

    inputs: the caller's payload (a locale variant, a partial test payload);
    None builds the canonical payload (inputs.load plus the drawing
    inventory). graph_sha256 is always re-pinned to the committed graph
    file's SHA-256: the documents that cite the graph provenance must
    describe the graph as committed, not as some earlier caller loaded it."""
    lines = []
    graph_path = graph_path or os.path.join(MF.ROOT, SL.GRAPH_PATH)
    mpath = manifest_path or os.path.join(MF.ROOT, 'flow_graph/derived/_input_manifest_v2.json')
    inputs = dict(inputs) if inputs is not None else IN.load()
    for key, value in IN.drawing_payload():
        inputs.setdefault(key, value)      # the same payload completion update() renders with
    ok = True

    if not os.path.exists(mpath):
        return False, [f'FAIL: no committed manifest at {mpath}; run the update once to establish it']

    with open(mpath, encoding='utf-8') as f:
        committed = json.load(f)

    current = MF.build(SL.FNS, extra_input_paths=IN.auxiliary_files())
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
    inputs['graph_sha256'] = hashlib.sha256(committed_bytes).hexdigest()
    rendered = render(model, Grid.load())
    if rendered != committed_bytes:
        n = _first_diff(committed_bytes, rendered)
        lines.append(f'stale (file): {SL.GRAPH_PATH} differs from the render (first difference at byte {n})')
        ok = False
    if committed.get('artifact_sha256') != hashlib.sha256(rendered).hexdigest():
        lines.append(f'stale (content): {SL.GRAPH_PATH} is not the render this manifest describes')
        ok = False

    from .render import RENDERS
    for path, fn_r in RENDERS:
        doc_path = os.path.join(artifact_root or MF.ROOT, path)
        if not os.path.exists(doc_path):
            lines.append(f'stale (missing document): {path}'); ok = False
            continue
        with open(doc_path, 'rb') as f:
            committed_doc = f.read()
        doc_bytes = fn_r(model, inputs)
        if doc_bytes != committed_doc:
            lines.append(f'stale (content): {path} differs from its render (first difference at byte {_first_diff(committed_doc, doc_bytes)})')
            ok = False

    from .render import duties as DU
    # The fragment rule governs the committed main tree: its graph and its
    # pages live together. A sandbox graph (the P1 proofs update a tmp copy)
    # carries no duties pages to rule over, so there only the graph and the
    # renderer comparisons run.
    if os.path.realpath(graph_path) == os.path.realpath(os.path.join(MF.ROOT, SL.GRAPH_PATH)):
        sheets, bullets, seed = _duty_facts()
        if sheets is None:
            lines.append('FAIL: the duties directory is missing; the fragment rule cannot run')
            ok = False
        else:
            try:
                entries = DU.FRAGMENTS(model, sheets, bullets, seed)
            except Exception as e:                           # a registry that cannot be built fails closed
                lines.append(f'FAIL: the fragment registry could not be built: {type(e).__name__}: {e}')
                ok = False
            else:
                frag_ok, frag_lines = check_fragments(model, inputs, entries,
                                                      frag_model=_fragment_model(graph_path, model, inputs))
                lines.extend(frag_lines)
                ok = ok and frag_ok

    if ok:
        lines.append('check: fresh — regeneration would reproduce every committed byte')
    return ok, lines


def _duty_facts():
    """The I/O-side facts the fragment registry gates on: the committed sheet
    ids, the ids whose page carries the envelope bullet at all (page-state:
    the v1 patch idiom refreshes a bullet in place and never adds one), and
    the placement-seed blocks (the v1 hidden read, declared here at the
    engine's I/O boundary). Returns (None, None, None) when the duties
    directory is missing - the caller fails closed on it."""
    duties_dir = os.path.join(MF.ROOT, 'docs-authority', 'duties')
    if not os.path.isdir(duties_dir):
        return None, None, None
    sheets, bullets = set(), set()
    for name in sorted(os.listdir(duties_dir)):
        if not name.endswith('.md') or name.startswith('_'):
            continue
        with open(os.path.join(duties_dir, name), 'rb') as f:
            text = f.read().decode('utf-8', errors='replace')
        if re.search(r'^- Envelope \d', text, flags=re.M):    # the bullet, not the '- Envelope basis' line
            bullets.add(name[:-3])
        sheets.add(name[:-3])
    seed_path = os.path.join(MF.ROOT, 'flow_graph', 'placement_seed.json')
    seed = {}
    if os.path.exists(seed_path):
        with open(seed_path, encoding='utf-8') as f:
            seed = {u['unit_id']: u for u in json.load(f).get('units', []) if u.get('unit_id')}
    return sheets, bullets, seed


def check_fragments(model, inputs, entries, root=None, frag_model=None):
    """The hand-page staleness rule: every generator-owned fragment must OCCUR
    in its committed page's bytes. Containment, not position and not
    whole-file equality - the hand prose around the fragment is the author's,
    the fragment is the engine's. frag_model: the model the fragments render
    under (the canonical-payload model when the caller's payload is partial;
    defaults to the caller's model). Returns (ok, report_lines); a missing
    page or an absent fragment is 'stale (fragment): <page> <id>'. Pure;
    writes nothing."""
    root = root if root is not None else MF.ROOT
    fm = frag_model if frag_model is not None else model
    ok = True
    lines = []
    for path, fid, fn_r in entries:
        page_path = os.path.join(root, path)
        if not os.path.exists(page_path):
            lines.append(f'stale (fragment): {path} {fid} (page missing)')
            ok = False
            continue
        with open(page_path, 'rb') as f:
            page = f.read()
        if fn_r(fm, inputs) not in page:
            lines.append(f'stale (fragment): {path} {fid}')
            ok = False
    return ok, lines


def patch_fragments(model, inputs, entries, root=None, frag_model=None):
    """Regenerate the patches (the update-side of the fragment rule): for each
    entry whose fragment bytes are absent from the committed page, apply the
    v1 patch idiom the fragment came from (the section-1 line replace, the
    section-3 line replace, the section-2 span replace - the idioms ported in
    duties.apply_patch) and write the page atomically. This is the v1
    duty_basis stage's patch behavior, now a declared render-side update; a
    page the idiom cannot anchor on stays unchanged and keeps failing the
    check, loudly, for a hand or owner decision. frag_model: the model the
    fragments render under (see check_fragments). Returns the applied
    (page, fragment id) list."""
    root = root if root is not None else MF.ROOT
    from .render import duties as DU
    fm = frag_model if frag_model is not None else model
    applied = []
    for path, fid, fn_r in entries:
        page_path = os.path.join(root, path)
        if not os.path.exists(page_path):
            continue                                         # a missing page is the check's FAIL, not a patch
        with open(page_path, 'rb') as f:
            page_bytes = f.read()
        frag = fn_r(fm, inputs)
        if frag in page_bytes:
            continue                                         # fresh: nothing to patch
        patched = DU.apply_patch(page_bytes.decode('utf-8'), frag.decode('utf-8'), fid)
        if patched == page_bytes.decode('utf-8'):
            continue                                         # unpatchable: stays stale, loudly
        tmp = page_path + '.tmp'
        with open(tmp, 'wb') as f:
            f.write(patched.encode('utf-8'))
        os.replace(tmp, page_path)
        applied.append((path, fid))
    return applied


def _changed_functions(current, committed):
    old = dict(committed.get('functions') or [])
    return sorted(name for name, fp in current['functions'] if old.get(name) != fp)


def _first_diff(a, b):
    for i, (x, y) in enumerate(zip(a, b)):
        if x != y:
            return i
    return min(len(a), len(b))


def update(graph_path=None, manifest_path=None, inputs=None, artifact_root=None):
    """The engine's single writer entry: solve, write the graph atomically,
    write the renderer registry documents, regenerate the duty-page patches
    (every fragment whose bytes the committed page no longer carries is
    re-applied with its v1 patch idiom), write the manifest. Returns the
    report lines of a post-write check (which must be fresh — a check that
    fails right after an update is a bug in the engine). inputs: the caller's
    payload; None builds the canonical payload. The drawing inventory rides
    in on demand (the pid/drawings documents consume the committed CAD SVGs),
    and graph_sha256 is re-pinned to the bytes actually written, so the
    documents describe the graph as written."""
    graph_path = graph_path or os.path.join(MF.ROOT, SL.GRAPH_PATH)
    manifest_path = manifest_path or os.path.join(MF.ROOT, 'flow_graph/derived/_input_manifest_v2.json')
    inputs = dict(inputs) if inputs is not None else IN.load()
    for key, value in IN.drawing_payload():
        inputs.setdefault(key, value)
    from .graph_io import write
    model = SL.solve(inputs, graph_path)
    prev = None
    for _ in range(3):
        # the seed fixpoint: the composition reads the committed graph as its
        # seed, so a first write that moves the bytes (the one-time P4
        # re-issuance of the serialization, or a drifted tree) changes the
        # seed the next solve reads. Iterate until the written graph stops
        # moving; the documents must describe the settled graph.
        write(graph_path, model, Grid.load())
        with open(graph_path, 'rb') as f:
            cur = f.read()
        if cur == prev:
            break
        prev = cur
        model = SL.solve(inputs, graph_path)
    inputs['graph_sha256'] = hashlib.sha256(cur).hexdigest()
    from .render import RENDERS
    root = artifact_root or MF.ROOT
    for path, fn_r in RENDERS:
        doc = fn_r(model, inputs)
        target = os.path.join(root, path)
        os.makedirs(os.path.dirname(target), exist_ok=True)
        tmp = target + '.tmp'
        with open(tmp, 'wb') as f:
            f.write(doc)
        os.replace(tmp, target)
    # the patch pass is tree-locked like the fragment rule it serves: it
    # regenerates the committed main tree's pages from that same tree's graph
    sheets, bullets, seed = _duty_facts()
    applied = []
    if sheets is not None and \
            os.path.realpath(graph_path) == os.path.realpath(os.path.join(MF.ROOT, SL.GRAPH_PATH)):
        from .render import duties as DU
        entries = DU.FRAGMENTS(model, sheets, bullets, seed)
        applied = patch_fragments(model, inputs, entries,
                                  frag_model=_fragment_model(graph_path, model, inputs))
    m = MF.build(SL.FNS, extra_input_paths=IN.auxiliary_files(),
                 artifact_sha=hashlib.sha256(render(model, Grid.load())).hexdigest())
    with open(manifest_path, 'w', encoding='utf-8') as f:
        f.write(MF.dumps(m))
    ok, lines = check(graph_path, manifest_path, inputs, artifact_root)
    if applied:
        lines.append(f'patched (fragment): {len(applied)} generator-owned fragment(s) regenerated')
    return ok, lines


def main():
    ok, lines = check()
    for ln in lines:
        print(ln)
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
