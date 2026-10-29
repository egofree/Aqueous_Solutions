"""Standby feed routes sized for the case that puts them in service (owner decision 2026-10-29, X-RTE, A-M-418).

A standby route carries no flow on the design day. It is finished when it carries the rate of the case that puts it in
service (its rated case), so that the tool it feeds, its source unit and its line are sized for that case. Each row of
ROUTES names the standby route, the primary route it stands in for, and the case. The rated rate is the design-day rate of
the primary route, because the tool downstream needs the same feed whichever route brings it. On the design day the route
stays at zero, which the balance keeps.

The outage a standby route covers lasts standby_outage_d days, the N+1 outage basis of the foundry melt backups (A-M-283).
A route drawn from a store makes the store hold the rated rate for that outage on top of its own holding (the hold_kg
parameter, read by docs-authority/_storage_sizing.py). A route drawn from a melt furnace makes the furnace run the extra
heats for the rated rate during the outage (the heats parameter); the furnace rating is unchanged because each heat is the
same charge.

Run: python3 -m flow_graph.param.standby_routes"""
import json, math
from . import drivers as DR

TAG = 'X-RTE TF (A-M-418)'
# (standby route, primary route it stands in for, rated case)
ROUTES = (
    ('STOCK_TO_WIRE_DRAW', 'S57', 'MET_MELT is out of service and copper rod from the METAL_STORE dock buffer feeds the wire drawer'),
)

def design(g, d=None):
    d = d or DR.load(); od = DR.val(d, 'standby_outage_d')
    E = {e['stream_id']: e for e in g['edges']}; N = {n['unit_id']: n for n in g['nodes']}
    out = {}
    for sid, prim, case in ROUTES:
        e = E[sid]; rated = float(E[prim]['rate']['value'] or 0); src = N[e['from_unit_id']]
        row = dict(rated_kg_d=rated, outage_d=od, backs_up=prim, case=case, source=src['unit_id'])
        sz = (src.get('params') or {}).get('sizing') or {}
        if sz.get('crucible_kg'):   # a melt furnace: extra heats in the outage
            row['heats_d'] = math.ceil(((sz.get('charge_kg_d') or 0) + rated)/sz['crucible_kg'])
        else:                       # a store: hold the rated feed for the outage
            row['hold_kg'] = rated*od
        out[sid] = row
    return out

def tf(g, d=None):
    r = design(g, d); E = {e['stream_id']: e for e in g['edges']}
    for sid, row in r.items():
        e = E[sid]
        p = dict(rate_normal_kg_d=0.0, rate_rated_kg_d=round(row['rated_kg_d'], 4), rated_case=row['case'], backs_up=row['backs_up'],
                 outage_d=row['outage_d'], basis='A-M-418; flow_graph/param/standby_routes.py')
        if 'hold_kg' in row: p['hold_kg'] = round(row['hold_kg'], 4)
        if 'heats_d' in row: p['source_heats_d_in_outage'] = row['heats_d']
        e['params'] = p
        e['rate'] = {'value': 0.0, 'unit': 'kg/d', 'status': 'study',
                     'note': f"{TAG}: zero on the design day; rated {row['rated_kg_d']:.4f} kg/d (the {row['backs_up']} rate) when {row['case']}, for {row['outage_d']:g} d (standby_routes.py)."}
    return r

if __name__ == '__main__':
    import os
    R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    g = json.load(open(os.path.join(R, 'flow_graph/plant_flow_graph.json')))
    print(json.dumps(design(g), default=str))
