"""X-PAR-04. Study envelope STLs (cad/stl/<UNIT>.stl, metres, one tray at the origin; --all prunes files of units no longer sized) from the sized
graph values: params.sizing.size_mm where a sizing calculation exists, else params.size_mm.
Each envelope is a thick-walled open-top tray: the outer faces sit exactly on the claimed envelope
(the registry bounding-box rule is unchanged) and the walls step inward, so every file is a solid
manifold mesh with real wall thickness instead of a zero-thickness box surface that slicers and
CAD kernels reject as a single-surface shell.
Built with CadQuery. Run: <cadquery python> -m flow_graph.param.envelopes UNIT [UNIT ...]"""
import glob, json, os, sys
import cadquery as cq
from . import solver
WALL = 0.010   # m, inward wall and floor thickness (clamped for small envelopes)

def size_of(n):
    p = n.get('params', {})
    s = (p.get('sizing') or {}).get('size_mm') or p.get('size_mm')
    if not s: raise KeyError(f"{n.get('unit_id')}: no size_mm on the graph")
    return s

def tray(L, W, H):
    t = min(WALL, L / 3.0, W / 3.0, H / 3.0)
    outer = cq.Workplane().box(L, W, H, centered=False)
    cavity = (cq.Workplane().box(L - 2 * t, W - 2 * t, H - t, centered=False)
              .translate((t, t, t)))          # open at the top: floor + four walls, all t thick
    return outer.cut(cavity)

def write(units, prune=False):
    g = json.load(open(os.path.join(solver.ROOT, 'flow_graph/plant_flow_graph.json'))); N = {n['unit_id']: n for n in g['nodes']}
    if prune:
        reg = os.path.join(solver.ROOT, 'cad/stl')
        keep = set(units)
        removed = []
        for f in sorted(glob.glob(os.path.join(reg, '*.stl'))):
            u = os.path.basename(f)[:-4]
            n = N.get(u)
            gone = n is None or n.get('presence') == 'absent'   # a present unit without a graph size
            if gone and u not in keep:                           # keeps its file: re-trayed from the
                os.remove(f); removed.append(os.path.basename(f))  # registry bbox by --repair, not resized
        if removed: print('pruned', len(removed), 'envelope files of units no longer in the graph:', ' '.join(sorted(removed)))
    for u in units:
        L, W, H = [v / 1000 for v in size_of(N[u])]
        path = os.path.join(solver.ROOT, 'cad/stl', f'{u}.stl')
        cq.exporters.export(tray(L, W, H), path, exportType='STL', opt={'ascii': True, 'tolerance': 0.001, 'angularTolerance': 0.2})
        print(u, L, W, H)

def sized_units():
    g = json.load(open(os.path.join(solver.ROOT, 'flow_graph/plant_flow_graph.json')))
    return [n['unit_id'] for n in g['nodes'] if (n.get('params', {}).get('sizing') or {}).get('size_mm') or n.get('params', {}).get('size_mm')]

def repair():
    """Re-tray files of present units that have no graph size, at each file's own bounding box:
    a geometry repair (wall thickness) that changes no claimed size. Sizes for these units are
    re-sourced as a separate task (the GA carries block sizes, not per-unit sizes)."""
    import trimesh
    g = json.load(open(os.path.join(solver.ROOT, 'flow_graph/plant_flow_graph.json')))
    N = {n['unit_id']: n for n in g['nodes']}
    reg = os.path.join(solver.ROOT, 'cad/stl')
    n = 0
    for f in sorted(glob.glob(os.path.join(reg, '*.stl'))):
        u = os.path.basename(f)[:-4]
        node = N.get(u)
        if node and node.get('presence') != 'absent' and u not in sized_units():
            m = trimesh.load(f)
            L, W, H = (m.bounds[1] - m.bounds[0]).tolist()
            cq.exporters.export(tray(L, W, H), f, exportType='STL', opt={'ascii': True, 'tolerance': 0.001, 'angularTolerance': 0.2})
            n += 1
    print('re-trayed', n, 'files of present units without graph sizes')

if __name__ == '__main__':
    if sys.argv[1:] == ['--all']: write(sized_units(), prune=True); sys.exit()
    if sys.argv[1:] == ['--repair']: repair(); sys.exit()
    write(sys.argv[1:] or [f'EW_{i}' for i in range(1, 10)] + ['EVAP_ACID', 'EVAP_BASE'])
