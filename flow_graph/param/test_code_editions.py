"""Q-018: every citation names the edition in force from the single edition table in code_basis.py (AQS-STD-007 Table 3.1).

Scans every tracked text file. Revision-history rows record what an earlier revision said and are skipped."""
import os, subprocess
from flow_graph.param import code_basis as CB
ROOT = CB.ROOT
SKIP = {'flow_graph/param/code_basis.py', 'flow_graph/param/test_code_editions.py'}
EXT = ('.md', '.py', '.json', '.csv', '.txt', '.yaml', '.yml', '.scad', '.html', '.js', '.ts', '.tsx')
def files():
    out = subprocess.run(['git', 'ls-files'], cwd=ROOT, capture_output=True, text=True).stdout.split('\n')
    return [f for f in out if f.endswith(EXT) and f not in SKIP and os.path.isfile(os.path.join(ROOT, f))]
def test_every_citation_names_the_edition_in_force():
    bad = []
    for f in files():
        try:
            text = open(os.path.join(ROOT, f), encoding='utf-8').read()
        except UnicodeDecodeError:
            continue
        bad += [f'{f}:{i} {c} (in force: {e})' for i, c, e in CB.stale(text)]
    assert not bad, 'citations of another edition (update flow_graph/param/code_basis.py EDITIONS or the citation):\n' + '\n'.join(bad[:40])
def test_edition_table_has_no_duplicates():
    names = [s for s, _, _, _ in CB.EDITIONS]
    assert len(names) == len(set(names))
