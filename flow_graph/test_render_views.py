"""Layer-view render determinism (flow_graph/render_layer_views.py).

Graphviz dot 2.42.4 intermittently takes a "trouble in init_rank" error path on byte-identical
input and renders two layouts alternately (notes/fab_fabtools_m3_2026-11-02.md). A doc-phase
regen loop that re-rolls dot every pass can then oscillate forever and fail doc-convergence,
which used to poison the whole regen receipt (U4c, 2026-11-03). Two invariants prevent that:
  1. to_dot is a pure function of the graph (the flake lives in dot, not in the dot writer);
  2. an unchanged .dot keeps the existing SVG byte-identical (skip path), so repeated regen
     passes cannot flip a view layout, and a needed render repeats until two consecutive
     renders agree (render_svg_stable).
"""
import importlib.util, os, shutil, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _mod():
    sys.path.insert(0, ROOT)
    spec = importlib.util.spec_from_file_location('aqs_render_layer_views', os.path.join(ROOT, 'flow_graph/render_layer_views.py'))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def test_to_dot_is_deterministic():
    m = _mod()
    import json
    g = json.loads(m.GRAPH.read_text())
    view = m.filter_view(g, m.PRESETS['mfd'])
    assert m.to_dot(view, title='MFD campus / mass view') == m.to_dot(view, title='MFD campus / mass view')


def test_unchanged_dot_keeps_existing_svg(tmp_path):
    """The skip path: same dot text + an existing SVG means the SVG stays (no layout re-roll)."""
    from pathlib import Path
    m = _mod()
    dot = tmp_path / 'mfd.dot'; svg = tmp_path / 'mfd.svg'
    dot.write_text('digraph g { a -> b }')
    svg.write_text('<svg>committed layout</svg>')
    assert m.svg_is_current(dot, dot.read_text(), svg)
    assert not m.svg_is_current(dot, 'digraph g { a -> c }', svg)      # changed render input
    svg.unlink()
    assert not m.svg_is_current(dot, dot.read_text(), svg)             # no SVG to keep


def test_regenerate_is_byte_stable(tmp_path):
    """End to end: rendering a view twice over an unchanged graph leaves the SVG and the DOT
    byte-identical (second run takes the skip path). Skipped when graphviz is not installed."""
    import json
    if not (shutil.which('dot')):
        return  # graphviz not installed; the CAD-class skip convention applies
    m = _mod()
    out = tmp_path / 'views'
    r1 = subprocess.run([sys.executable, os.path.join(ROOT, 'flow_graph/render_layer_views.py'),
                         '--only', 'mfd', '--out-dir', str(out)],
                        cwd=ROOT, capture_output=True, text=True)
    assert r1.returncode == 0, r1.stdout[-2000:] + r1.stderr[-2000:]
    snap = {p.name: p.read_bytes() for p in out.iterdir()}
    r2 = subprocess.run([sys.executable, os.path.join(ROOT, 'flow_graph/render_layer_views.py'),
                         '--only', 'mfd', '--out-dir', str(out)],
                        cwd=ROOT, capture_output=True, text=True)
    assert r2.returncode == 0, r2.stdout[-2000:] + r2.stderr[-2000:]
    assert 'SVG kept (dot unchanged)' in r2.stdout, r2.stdout[-800:]
    assert {p.name: p.read_bytes() for p in out.iterdir()} == snap
