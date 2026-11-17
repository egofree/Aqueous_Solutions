"""X-GOV-06 revision control of drawings and derived files (AQS-GOV-006).

Since the P4 flip the staleness rule is engine v2's: one check, one verdict.
flow_graph.v2.check.check() recomputes the solve in memory, renders the
registry, and compares every governed artifact byte for byte against the
committed tree, with the committed input manifest deciding whether the
inputs or the engine code moved. This module renders that verdict:
docs-authority/DERIVED_REVISIONS.md lists every derived file with its status,
current or stale, from the check's per-file report. Files whose writers
retired with the v1 machinery and whose families have not landed in the v2
registry are retained data: their row says so, and they do not gate. The
class and by-design tables keep their rows (the by-design set is now the
manifest mechanisms and the retained v1 bookkeeping files).

The commit-order rule and the receipt verification leg retired at the flip: a file
is stale because its re-render differs from its committed bytes, never
because of commit history, and run health lives in the untracked
flow_graph/derived/_regen_run.json of the --legacy pipeline. The step-4
input-census printer retired with it: the v2 input manifest
(flow_graph/derived/_input_manifest_v2.json, written by the update) is the
staleness rule, not a parallel candidate.

Writes docs-authority/DERIVED_REVISIONS.md (file and status only, rewritten
only on a content change); exit 1 with --check when a gated file is stale.
--check-only evaluates and prints the summary without writing the file.
--report prints the per-file table without writing. The everyday gate is
`python3 -m flow_graph.param.regen --check`, which runs the same v2 check.
"""
import fnmatch, json, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GP = 'flow_graph/plant_flow_graph.json'
MANIFEST = json.load(open(os.path.join(ROOT, 'flow_graph/param/regen_manifest.json')))
DERIVED = ['media/*', 'flow_graph/views/*', 'flow_graph/derived/*', 'docs-authority/duties/*.md',
           'docs-authority/sizing/*.md', 'docs-authority/pid/*', 'docs-authority/LOAD_LIST.md', 'docs-authority/ONE_LINE.md', 'docs-authority/BALANCE_RECONCILIATION.md',
           'docs-authority/O2_SOURCE.md', 'docs-authority/ASSUMPTIONS_REGISTER.md', 'docs-authority/MODEL_WORKBOOK.xlsx', 'design_tool/aqs_design_tool/data/candidate_mvs.json']
# Every file a default-run pipeline stage writes or amends is derived too, read from the manifest so a new stage is gated
# without editing this list. The "cad" group is left out: the CAD builders are declared build steps of engine v2 and their
# outputs are covered by the CAD byte gate.
DERIVED = sorted(set(DERIVED) | {g for st in MANIFEST['stages'] if st.get('group') != 'cad' for g in st.get('outputs', []) + st.get('amends', [])})
CLASS = {'media/logo3.png': 'artwork, not derived', 'media/verify_view*.png': 'manual capture in GUI FreeCAD (models/freecad/verify_view_png.py)'}
# the manifest mechanisms themselves, and the v1 bookkeeping files the P6
# cleanup deletes: retained data, not gated rows
BY_DESIGN = {
    'docs-authority/sizing/SANITATION.md': 'X-SAN-01 graph-writer module (flow_graph/param/sanitation.py); owner-lane port pending (R11 close-out)',
    'media/_generated.json': 'the v1 pattern manifest (retained data; the P6 cleanup deletes it)',
    'flow_graph/derived/_regen_receipt.json': 'the v1 provenance receipt (retained data; written only by regen --legacy)',
    'flow_graph/derived/_input_manifest.json': 'the v1 input manifest (retained data; the rule is _input_manifest_v2.json)',
    'flow_graph/derived/_input_manifest_v2.json': 'manifest mechanism itself (the engine v2 input manifest, written by the update)',
    'docs-authority/DERIVED_REVISIONS.md': 'this register (its own row would change with each write)'}

RETAINED = 'retained v1 output (writer retired at the P4 flip; unruled by engine v2)'


def git(*a):
    return subprocess.run(['git', *a], cwd=ROOT, capture_output=True, text=True, check=True).stdout


def _verdicts():
    """Run the engine v2 check and map its report onto per-file staleness.
    Returns (check_ok, stale_paths, ruled, fail_closed). ruled marks the file
    set the check actually compares (registry documents, the duty fragment
    pages and the graph); a code or input fingerprint failure fails closed
    over every ruled file."""
    sys.path.insert(0, ROOT)
    from flow_graph.v2 import check as V2
    ok, lines = V2.check()
    stale, fail_closed = set(), False
    for ln in lines:
        if ln.startswith('FAIL:'):
            fail_closed = True
            continue
        m = re.match(r'stale \(code changed\)|stale \(input changed\)', ln)
        if m:
            fail_closed = True
            continue
        m = re.match(r'stale \((?:content|missing document|file|fragment)\): (\S+)', ln)
        if m:
            stale.add(m.group(1))
    return ok, stale, fail_closed


def compute():
    """Read-only evaluation from the engine v2 check's verdicts: returns
    (rows, stale count, gated-stale list, graph revision, check verdict);
    writes nothing."""
    ok, stale, fail_closed = _verdicts()
    from flow_graph.v2.render import RENDERS
    rev = json.load(open(os.path.join(ROOT, GP)))['revision']
    files = [f for f in git('ls-files').splitlines() if any(fnmatch.fnmatch(f, p) for p in DERIVED)]
    registry = {p for p, _ in RENDERS}
    ruled = sorted((registry | {GP}) & set(files))
    dirty = set(git('status', '--porcelain').split())
    rows, bad = [], []
    for f in sorted(files):
        cl = next((v for k, v in CLASS.items() if fnmatch.fnmatch(f, k)), None)
        if cl:
            rows.append((f, '-', cl)); continue
        bd = next((v for k, v in BY_DESIGN.items() if fnmatch.fnmatch(f, k)), None)
        if bd:
            rows.append((f, '-', 'by design: ' + bd)); continue
        if f in dirty:
            rows.append((f, 'working tree', 'current')); continue   # status only is written (render)
        if f not in registry and f != GP:
            rows.append((f, '-', RETAINED)); continue
        st = 'stale' if (fail_closed or f in stale) else 'current'
        rows.append((f, '-', st))
        if st == 'stale':
            bad.append(f)
    return rows, sum(r[2] == 'stale' for r in rows), bad, rev, ok


def render(rows, n, rev, ok):
    """Register text from the evaluated rows: the file set with its status,
    and the check verdict. Pure function of (file, status); the register
    changes only when a file's status, the file set, the revision or the
    verdict changes."""
    verdict = 'fresh - regeneration would reproduce every committed byte' if ok \
        else 'stale - run python3 -m flow_graph.param.regen'
    md = ['# Derived file revisions', '', 'Document number: AQS-GOV-006', 'Revision: D', f'Graph: {GP} Revision {rev}.',
          f'Verdict: the engine v2 check is {verdict}.',
          'Generated by `docs-authority/_rev_stamp.py` (X-GOV-06) from the engine v2 check. Do not edit this page by hand.', '',
          '| Rev | Description | Date |', '|---|---|---|',
          '| A | First issue: the derived-file stamp register. | 2026-10-15 |',
          '| B | Purpose and scope added per the documentation style guide (AQS-DOC-002). Tracking rule unchanged. | 2026-10-25 |',
          '| C | The graph commit column is no longer written to this page; it is reported on demand. A graph commit no longer rewrites every row. | 2026-11-04 |',
          '| D | The staleness rule is the engine v2 check: one recomputed render compared byte for byte against the committed tree, with the input manifest deciding whether the inputs or the engine moved. The commit-order rule and the receipt verification leg retired; outputs whose writers retired with the v1 machinery are retained data and do not gate. | 2026-11-16 |', '',
          '## 1. Purpose and scope', '',
          'This page lists every derived file and states whether it is current with the plant graph. A file is stale when its recomputed render differs from its committed bytes; the everyday gate is `python3 -m flow_graph.param.regen --check`. Files whose writers retired with the v1 pipeline are retained data: their row says so and they do not gate.', '',
          '`python3 docs-authority/_rev_stamp.py --report` prints the table without writing this page; `--check` fails on any stale file and writes nothing.', '',
          f'{len(rows)} derived files, {n} stale.', '',
          '| File | Status |', '|---|---|'] + [f'| `{a}` | {c} |' for a, b, c in rows]
    return '\n'.join(md) + '\n'


def main():
    rows, n, bad, rev, ok = compute()
    if '--report' in sys.argv:
        print(f'graph revision {rev}, engine v2 check {"fresh" if ok else "STALE"}')
        for a, b, c in rows: print(f'{a}\t{b}\t{c}')
    elif '--check-only' not in sys.argv:
        out = os.path.join(ROOT, 'docs-authority/DERIVED_REVISIONS.md'); text = render(rows, n, rev, ok)
        if not os.path.exists(out) or open(out).read() != text:   # write only on a content change
            open(out, 'w').write(text)
    print(len(rows), 'files', n, 'stale', 'gated stale:', bad)
    if ('--check' in sys.argv or '--check-only' in sys.argv) and (bad or not ok): sys.exit(1)
if __name__ == '__main__': main()
