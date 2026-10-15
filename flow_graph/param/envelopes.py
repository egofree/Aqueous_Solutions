"""X-PAR-04. Study envelope STLs (cad/stl/<UNIT>.stl, metres, one box at the origin) from the sized
graph values: params.sizing.size_mm where a sizing calculation exists, else params.size_mm.
Built with CadQuery. Run: <cadquery python> -m flow_graph.param.envelopes UNIT [UNIT ...]"""
import json, os, sys
import cadquery as cq
from . import solver
def size_of(n):
    p = n.get('params', {})
    return (p.get('sizing') or {}).get('size_mm') or p['size_mm']
def write(units):
    g = json.load(open(os.path.join(solver.ROOT, 'flow_graph/plant_flow_graph.json'))); N = {n['unit_id']: n for n in g['nodes']}
    for u in units:
        L, W, H = [v/1000 for v in size_of(N[u])]
        path = os.path.join(solver.ROOT, 'cad/stl', f'{u}.stl')
        cq.exporters.export(cq.Workplane().box(L, W, H, centered=False), path, exportType='STL', opt={'ascii': True})
        print(u, L, W, H)
def sized_units():
    g = json.load(open(os.path.join(solver.ROOT, 'flow_graph/plant_flow_graph.json')))
    return [n['unit_id'] for n in g['nodes'] if (n.get('params', {}).get('sizing') or {}).get('size_mm') or n.get('params', {}).get('size_mm')]
if __name__ == '__main__':
    if sys.argv[1:] == ['--all']: write(sized_units()); sys.exit()
    write(sys.argv[1:] or [f'EW_{i}' for i in range(1, 10)] + ['EVAP_ACID', 'EVAP_BASE'])
