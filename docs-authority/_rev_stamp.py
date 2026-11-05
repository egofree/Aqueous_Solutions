"""X-GOV-06 revision control of drawings and derived files (AQS-GOV-006).
Each derived file is tied to the graph commit it was made from: the newest commit touching flow_graph/plant_flow_graph.json at or before the
file's own last commit. A file is stale when the graph has changed since. A file whose regeneration is byte-identical cannot clear that
commit-based staleness (git sees no change), so generators also record their provenance: pattern manifests (duties/_generated.json,
media/_generated.json) clear every file matching a pattern, per-file manifests (*._generated.json, e.g. sizing/REACTOR_DESIGN._generated.json)
record (file, graph_sha256) rows, a data sidecar <NAME>.json with a matching _generated_from.graph_sha256 clears its <NAME>.md twin, and
and the U3 regen receipt (flow_graph/derived/_regen_receipt.json, written by flow_graph/param/regen.py) vouches the stage output globs — and, for a
stage that was only partly stable, the individually verified files — that its run re-derived byte-stable against the current graph (vouched on a
graph-sha match alone; a failed or oscillating stage disqualifies exactly its own outputs, not the tree).
The graph sha is computed at check time: a manifest row matching the current graph counts the file as current. Writes docs-authority/DERIVED_REVISIONS.md (file and status only, rewritten only on a content change); exit 1 with --check when a
GATED file is stale. --check-only evaluates and prints the summary without writing the file. --report prints the graph commit
each file was made from, without writing.
U3 gated expansion (2026-10-18): GATED is no longer a 3-file list — every DERIVED file is gated unless it is classified. CLASS keeps the
by-design artwork/superseded/manual-capture files, BY_DESIGN keeps the documented one-shots and blocked generators (frozen studies, sheets
of deleted edges pending retirement, the manifest mechanisms themselves), Anything else that is stale fails the gate: run python3 -m flow_graph.param.regen."""
import json, os, subprocess, sys, fnmatch
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); GP = 'flow_graph/plant_flow_graph.json'
DERIVED = ['media/*', 'flow_graph/views/*', 'flow_graph/derived/*', 'docs-authority/duties/*.md',
           'docs-authority/sizing/*.md', 'docs-authority/pid/*', 'docs-authority/LOAD_LIST.md', 'docs-authority/ONE_LINE.md', 'docs-authority/BALANCE_RECONCILIATION.md',
           'docs-authority/O2_SOURCE.md', 'docs-authority/ASSUMPTIONS_REGISTER.md', 'docs-authority/MODEL_WORKBOOK.xlsx', 'design_tool/aqs_design_tool/data/candidate_mvs.json']
# Every file a default-run pipeline stage writes or amends is derived too, read from the manifest so a new stage is gated
# without editing this list. The "cad" group is left out: it runs only with regen --cad on a machine with the CAD toolchains.
_MAN = json.load(open(os.path.join(ROOT, 'flow_graph/param/regen_manifest.json')))
DERIVED = sorted(set(DERIVED) | {g for st in _MAN['stages'] if st.get('group') != 'cad' for g in st.get('outputs', []) + st.get('amends', [])})
CLASS = {'media/logo3.png': 'artwork, not derived', 'media/verify_view*.png': 'manual capture in GUI FreeCAD (models/freecad/verify_view_png.py)'}
# documented one-shots and blocked generators: derived files the U3 orchestrator does not regenerate, with the reason (U3 gated expansion)
BY_DESIGN = {
    'docs-authority/sizing/SANITATION.md': 'X-SAN-01 graph-writer module (flow_graph/param/sanitation.py); owner-lane port pending (R11 close-out)',
    'media/_generated.json': 'the manifest that lists generated media and the graph each was made from (regen_derived.py)',
    'flow_graph/derived/_regen_receipt.json': 'manifest mechanism itself (U3 regen provenance receipt)'}
FILE_MANIFESTS = ['docs-authority/sizing/REACTOR_DESIGN._generated.json']
RECEIPT = 'flow_graph/derived/_regen_receipt.json'
def git(*a): return subprocess.run(['git', *a], cwd=ROOT, capture_output=True, text=True, check=True).stdout
def receipt_vouched(receipt, gsha):
    """Globs and files a regen receipt vouches at graph sha `gsha` (empty at any other sha).
    The receipt lists only what its own regen run re-derived and observed byte-stable at
    receipt['graph_sha256'] (U4c, 2026-11-03), so a sha match is the only trust condition:
    `converged` is run-health information, not a vouch precondition — one oscillating stage
    must not un-vouch the 400+ globs other stages verified."""
    if receipt.get('graph_sha256') == gsha:
        return list(receipt.get('vouched_patterns', [])) + list(receipt.get('vouched_files', []))
    return []
def compute():
    """Read-only evaluation: returns (rows, stale count, gated-stale list, graph revision, head graph commit); writes nothing."""
    log = git('log', '--format=@%H %ct', '--name-only', '--no-renames'); last = {}; graph = []; cur = None
    for ln in log.splitlines():
        if ln.startswith('@'): h, t = ln[1:].split(); cur = (h, int(t))
        elif ln:
            last.setdefault(ln, cur)
            if ln == GP: graph.append(cur)
    files = [f for f in git('ls-files').splitlines() if any(fnmatch.fnmatch(f, p) for p in DERIVED)]
    head_g = graph[0]; rev = json.load(open(os.path.join(ROOT, GP)))['revision']; rows = []; bad = []
    dirty = set(git('status', '--porcelain').split())
    import hashlib; gsha = hashlib.sha256(open(os.path.join(ROOT, GP), 'rb').read()).hexdigest(); checked = []
    for man in ('docs-authority/duties/_generated.json', 'media/_generated.json'):   # generators derived again these outputs from this exact graph
        m = os.path.join(ROOT, man)
        if os.path.exists(m) and json.load(open(m)).get('graph_sha256') == gsha: checked += json.load(open(m)).get('patterns', [])
    rp = os.path.join(ROOT, RECEIPT)                                                  # U3: regen receipt vouches what its run verified
    if os.path.exists(rp):
        try:
            checked += receipt_vouched(json.load(open(rp)), gsha)
        except ValueError: pass
    vouched = {}   # derived file -> graph_sha256 it was regenerated from (per-file manifests and json sidecars beside the .md)
    for man in FILE_MANIFESTS:
        m = os.path.join(ROOT, man)
        if os.path.exists(m):
            rows_ = json.load(open(m)).get('files', {})
            vouched.update({f: s for f, s in rows_.items() if isinstance(s, str)})
    for f in sorted(files):
        if f.endswith('.md'):
            sc = os.path.join(ROOT, f[:-3] + 'json')   # data sidecar twin (U2a): generator wrote md+json from one graph read
            if os.path.exists(sc):
                try:
                    s = json.load(open(sc)).get('_generated_from', {}).get('graph_sha256')
                    if isinstance(s, str): vouched.setdefault(f, s)
                except ValueError: pass
    for f in sorted(files):
        c = last.get(f)
        if f == 'docs-authority/DERIVED_REVISIONS.md': rows.append((f, '-', 'this register (its own row would change with each write)')); continue
        if c is None or f in dirty: rows.append((f, 'working tree', 'current' if f in dirty else 'untracked')); continue   # status only is written (render)
        cl = next((v for k, v in CLASS.items() if fnmatch.fnmatch(f, k)), None)
        if cl: rows.append((f, '-', cl)); continue
        bd = next((v for k, v in BY_DESIGN.items() if fnmatch.fnmatch(f, k)), None)
        if bd: rows.append((f, '-', 'by design: ' + bd)); continue
        if any(fnmatch.fnmatch(f, k) for k in checked) or vouched.get(f) == gsha: rows.append((f, head_g[0][:7] + ' (regenerated, no change)', 'current')); continue
        made = next((g for g in graph if g[1] <= c[1]), None)
        st = 'current' if made and made[0] == head_g[0] else 'stale'
        rows.append((f, (made[0][:7] if made else '-'), st))
        if st == 'stale': bad.append(f)   # U3 gated expansion: every unclassified DERIVED file gates
    n = sum(r[2] == 'stale' for r in rows)
    return rows, n, bad, rev, head_g

def render(rows, n, rev):
    """Register text from the evaluated rows. Pure function of (file, status) and the graph revision:
    the graph commit each file was made from is not written, so a new graph commit does not rewrite
    every row and the register changes only when a file's status, the file set or the revision changes.
    `--report` prints the commit column at read time instead (AQS-GOV-006 Rev C)."""
    md = ['# Derived file revisions', '', 'Document number: AQS-GOV-006', 'Revision: C', f'Graph: {GP} Revision {rev}.',
          'Generated by `docs-authority/_rev_stamp.py` (X-GOV-06). Do not edit this page by hand.', '',
          '| Rev | Description | Date |', '|---|---|---|',
          '| A | First issue: the derived-file stamp register. | 2026-10-15 |',
          '| B | Purpose and scope added per the documentation style guide (AQS-DOC-002). Tracking rule unchanged. | 2026-10-25 |',
          '| C | The graph commit column is no longer written to this page; it is reported on demand with `python3 docs-authority/_rev_stamp.py --report`. A graph commit no longer rewrites every row. Tracking rule unchanged. | 2026-11-04 |', '',
          '## 1. Purpose and scope', '',
          'This page lists every derived file and states whether it is current with the plant graph. A file is stale when the graph changed after the file was last written and no regeneration since then has confirmed it. A file whose regeneration is byte-identical cannot show this by a new commit, so the regeneration records it in its provenance manifest instead.', '',
          'To see the graph commit each file was made from, run `python3 docs-authority/_rev_stamp.py --report`; it prints the full table without writing this page. `python3 -m flow_graph.param.regen` refreshes this page; `python3 -m flow_graph.param.regen --check` fails on any stale file and writes nothing.', '',
          f'{len(rows)} derived files, {n} stale (gated set: every file not classified by-design; regenerate with `python3 -m flow_graph.param.regen`).', '',
          '| File | Status |', '|---|---|'] + [f'| `{a}` | {c} |' for a, b, c in rows]
    return '\n'.join(md) + '\n'

def main():
    rows, n, bad, rev, head_g = compute()
    if '--report' in sys.argv:
        print(f'graph revision {rev}, last graph commit {head_g[0][:7]}')
        for a, b, c in rows: print(f'{a}\t{b}\t{c}')
    elif '--check-only' not in sys.argv:
        out = os.path.join(ROOT, 'docs-authority/DERIVED_REVISIONS.md'); text = render(rows, n, rev)
        if not os.path.exists(out) or open(out).read() != text:   # write only on a content change
            open(out, 'w').write(text)
    print(len(rows), 'files', n, 'stale', 'gated stale:', bad)
    if ('--check' in sys.argv or '--check-only' in sys.argv) and bad: sys.exit(1)
if __name__ == '__main__': main()
