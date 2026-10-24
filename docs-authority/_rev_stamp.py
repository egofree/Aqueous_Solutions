"""X-GOV-06 revision control of drawings and derived files (AQS-GOV-006).
Each derived file is tied to the graph commit it was made from: the newest commit touching flow_graph/plant_flow_graph.json at or before the
file's own last commit. A file is stale when the graph has changed since. A file whose regeneration is byte-identical cannot clear that
commit-based staleness (git sees no change), so generators also record their provenance: pattern manifests (duties/_generated.json,
media/_generated.json) clear every file matching a pattern, per-file manifests (*._generated.json, e.g. sizing/REACTOR_DESIGN._generated.json)
record (file, graph_sha256) rows, a data sidecar <NAME>.json with a matching _generated_from.graph_sha256 clears its <NAME>.md twin, and
the U3 regen receipt (flow_graph/derived/_regen_receipt.json, written by flow_graph/param/regen.py) vouches the output globs of every stage
that ran clean against the current graph.
The graph sha is computed at check time: a manifest row matching the current graph counts the file as current. Writes docs-authority/DERIVED_REVISIONS.md; exit 1 with --check when a
GATED file is stale. --check-only evaluates and prints the summary without writing the file.
U3 gated expansion (2026-10-18): GATED is no longer a 3-file list — every DERIVED file is gated unless it is classified. CLASS keeps the
by-design artwork/superseded/manual-capture files, BY_DESIGN keeps the documented one-shots and blocked generators (frozen studies, sheets
of deleted edges pending retirement, the manifest mechanisms themselves), and the iso-sheet orphan rule keys off the regenerated
iso/ISO_SHEETS.csv. Anything else that is stale fails the gate: run python3 -m flow_graph.param.regen."""
import json, os, subprocess, sys, fnmatch
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); GP = 'flow_graph/plant_flow_graph.json'
DERIVED = ['docs-authority/iso/*', 'iso/*', 'media/*', 'media/pfd/*', 'flow_graph/views/*', 'flow_graph/derived/*', 'docs-authority/duties/*.md',
           'docs-authority/sizing/*.md', 'docs-authority/pid/*', 'docs-authority/LOAD_LIST.md', 'docs-authority/ONE_LINE.md', 'docs-authority/BALANCE_RECONCILIATION.md',
           'docs-authority/O2_SOURCE.md', 'docs-authority/ASSUMPTIONS_REGISTER.md', 'docs-authority/MODEL_WORKBOOK.xlsx', 'design_tool/aqs_design_tool/data/candidate_mvs.json']
# Every file a default-run pipeline stage writes or amends is derived too, read from the manifest so a new stage is gated
# without editing this list. The "cad" group is left out: it runs only with regen --cad on a machine with the CAD toolchains.
_MAN = json.load(open(os.path.join(ROOT, 'flow_graph/param/regen_manifest.json')))
DERIVED = sorted(set(DERIVED) | {g for st in _MAN['stages'] if st.get('group') != 'cad' for g in st.get('outputs', []) + st.get('amends', [])})
CLASS = {'iso/*': 'superseded by docs-authority/iso/*.svg (AQS-ISO-002, _iso_sheets.py); generator pfd_scripts/iso_fab.py retired',
         'media/logo3.png': 'artwork, not derived', 'media/verify_view*.png': 'manual capture in GUI FreeCAD (models/freecad/verify_view_png.py)'}
# documented one-shots and blocked generators: derived files the U3 orchestrator does not regenerate, with the reason (U3 gated expansion)
BY_DESIGN = {
    'docs-authority/sizing/SANITATION.md': 'X-SAN-01 graph-writer module (flow_graph/param/sanitation.py); owner-lane port pending (R11 close-out)',
    'media/_generated.json': 'manifest mechanism itself (pattern vouching source, regen_derived.py)',
    'flow_graph/derived/_regen_receipt.json': 'manifest mechanism itself (U3 regen provenance receipt)'}
FILE_MANIFESTS = ['docs-authority/sizing/REACTOR_DESIGN._generated.json']
RECEIPT = 'flow_graph/derived/_regen_receipt.json'
def git(*a): return subprocess.run(['git', *a], cwd=ROOT, capture_output=True, text=True, check=True).stdout
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
    for man in ('docs-authority/duties/_generated.json', 'media/_generated.json'):   # generators re-derived these outputs from this exact graph
        m = os.path.join(ROOT, man)
        if os.path.exists(m) and json.load(open(m)).get('graph_sha256') == gsha: checked += json.load(open(m)).get('patterns', [])
    rp = os.path.join(ROOT, RECEIPT)                                                  # U3: regen receipt vouches stage output globs
    if os.path.exists(rp):
        try:
            r = json.load(open(rp))
            if r.get('graph_sha256') == gsha and r.get('converged'): checked += r.get('vouched_patterns', [])
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
    orphans = iso_orphans()   # sheets of deleted/rerouted edges: present as svg, absent from the regenerated route table
    for f in sorted(files):
        c = last.get(f)
        if c is None or f in dirty: rows.append((f, 'working tree', 'current' if f in dirty else 'untracked')); continue
        cl = next((v for k, v in CLASS.items() if fnmatch.fnmatch(f, k)), None)
        if cl: rows.append((f, '-', cl)); continue
        bd = next((v for k, v in BY_DESIGN.items() if fnmatch.fnmatch(f, k)), None)
        if bd: rows.append((f, '-', 'by design: ' + bd)); continue
        if f in orphans: rows.append((f, '-', 'by design: sheet of a deleted/rerouted edge (not in regenerated iso/ISO_SHEETS.csv); retirement pending the graph lane')); continue
        if any(fnmatch.fnmatch(f, k) for k in checked) or vouched.get(f) == gsha: rows.append((f, head_g[0][:7] + ' (re-derived, unchanged)', 'current')); continue
        made = next((g for g in graph if g[1] <= c[1]), None)
        st = 'current' if made and made[0] == head_g[0] else 'stale'
        rows.append((f, (made[0][:7] if made else '-'), st))
        if st == 'stale': bad.append(f)   # U3 gated expansion: every unclassified DERIVED file gates
    n = sum(r[2] == 'stale' for r in rows)
    return rows, n, bad, rev, head_g

def iso_orphans():
    """iso/*.svg files with no row in the regenerated docs-authority/iso/ISO_SHEETS.csv (edges deleted from the graph)."""
    p = os.path.join(ROOT, 'docs-authority/iso/ISO_SHEETS.csv')
    if not os.path.exists(p): return set()
    import csv
    have = {os.path.basename(f) for f in glob_iso()}
    listed = {r.get('line', '') + '.svg' for r in csv.DictReader(open(p))}
    return {f'docs-authority/iso/{b}' for b in have - listed}

def glob_iso():
    import glob as _g
    return sorted(_g.glob(os.path.join(ROOT, 'docs-authority/iso', '*.svg')))

def main():
    rows, n, bad, rev, head_g = compute()
    if '--check-only' not in sys.argv:
        md = ['# Derived file revisions', '', 'Document number: AQS-GOV-006', 'Revision: A', f'Graph: {GP} revision {rev}, last graph commit {head_g[0][:7]}.',
              'Generated by `docs-authority/_rev_stamp.py` (X-GOV-06). A file is stale when the graph changed after the file was last written.', '',
              f'{len(rows)} derived files, {n} stale (gated set: every file not classified by-design; regenerate with `python3 -m flow_graph.param.regen`).', '',
              '| File | Made from graph commit | Status |', '|---|---|---|'] + [f'| `{a}` | {b} | {c} |' for a, b, c in rows]
        open(os.path.join(ROOT, 'docs-authority/DERIVED_REVISIONS.md'), 'w').write('\n'.join(md) + '\n')
    print(len(rows), 'files', n, 'stale', 'gated stale:', bad)
    if ('--check' in sys.argv or '--check-only' in sys.argv) and bad: sys.exit(1)
if __name__ == '__main__': main()
