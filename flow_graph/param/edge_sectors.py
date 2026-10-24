"""Set each edge's from_sector_id and to_sector_id from the sector of the unit at that end.

Writers create edges with sector ids typed by hand, and a unit can later move to another
sector. The node record is the single source for a unit's sector, so this stage runs last in the
graph phase and copies it onto every edge. Ends whose unit is not a node (boundary sinks such
as HEAT_SINK) keep the sector the writer gave them.

Usage: python3 -m flow_graph.param.edge_sectors [--write]
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
GP = os.path.join(ROOT, 'flow_graph', 'plant_flow_graph.json')


def apply(write=False):
    g = json.load(open(GP))
    sector = {n['unit_id']: n.get('sector_id') for n in g['nodes'] if n.get('sector_id')}
    changed = []
    for e in g['edges']:
        for end in ('from', 'to'):
            s = sector.get(e[f'{end}_unit_id'])
            if s and e.get(f'{end}_sector_id') != s:
                changed.append((e['stream_id'], end, e.get(f'{end}_sector_id'), s))
                e[f'{end}_sector_id'] = s
    if write and changed:
        open(GP, 'w').write(json.dumps(g, indent=2) + '\n')
    return changed


def main():
    for sid, end, old, new in apply(write='--write' in sys.argv):
        print(f'{sid} {end}: {old} -> {new}')


if __name__ == '__main__':
    main()
