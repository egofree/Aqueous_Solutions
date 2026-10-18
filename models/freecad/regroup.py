"""L-1 flow-adjacency regroup (AQS-BLD-010 rev D, A-M-223). Runs in build_plant.py after resolve_overlaps, before the rated rooms.
Objective per unit: sum of plan Manhattan distances (centre to centre) to every unit it shares a flow-graph stream with.
Greedy: each L-1 equipment unit, in order of largest objective, tries plan offsets on a 500 mm grid within +/-12 m and takes the
best position that is clear (GAP) of all equipment, corridors, stairs, shafts and rated walls on its level and stays on the plate.
Accepts a move only if it cuts that unit's objective by at least 1 m. Three passes. Moves append to CAD_MOVES.json
(from_clash_with = 'REGROUP') so the line list and isometrics follow; totals go to CAD_REGROUP.json."""
import json
from pathlib import Path
import FreeCAD as App
import clash_equip_rules as CR
GAP = 100.0; STEP = 500.0; REACH = 12000.0; MIN_GAIN = 1000.0
Z_LM1 = (-7000.0, -500.0)
def _bb(o):
    b = o.Shape.BoundBox; return [b.XMin, b.YMin, b.ZMin, b.XMax, b.YMax, b.ZMax]
def _ov(a, b, g):
    return all(a[i] < b[i + 3] + g and b[i] < a[i + 3] + g for i in range(2)) and a[2] < b[5] - 1 and b[2] < a[5] - 1
def _inside(a, b):
    return all(b[i] - 1 <= a[i] and a[i + 3] <= b[i + 3] + 1 for i in range(3))
def regroup(doc, plate, graph, moves_log, out):
    eq = [o for o in doc.Objects if CR.is_equipment(o)]
    obst = [o for o in doc.Objects if CR.is_obstacle(o)]
    B = {o.Name: _bb(o) for o in eq + obst}; EQ = {o.Name for o in eq}
    by_label = {}
    for o in eq: by_label.setdefault(o.Label, o)
    nb = {}
    for e in json.load(open(graph))['edges']:
        a, b = e.get('from_unit_id'), e.get('to_unit_id')
        if a in by_label and b in by_label and a != b:
            nb.setdefault(a, set()).add(b); nb.setdefault(b, set()).add(a)
    cen = lambda k: ((B[k][0] + B[k][3]) / 2, (B[k][1] + B[k][4]) / 2)
    def cost(lab, c=None):
        c = c or cen(by_label[lab].Name)
        return sum(abs(c[0] - cen(by_label[n].Name)[0]) + abs(c[1] - cen(by_label[n].Name)[1]) for n in nb.get(lab, ()))
    lm1 = [o for o in by_label.values() if Z_LM1[0] <= B[o.Name][2] <= Z_LM1[1] and o.Label in nb]
    before = sum(cost(o.Label) for o in lm1)
    rng = [i * STEP for i in range(-int(REACH / STEP), int(REACH / STEP) + 1)]
    new = []
    for _ in range(3):
        moved = False
        for o in sorted(lm1, key=lambda o: -cost(o.Label)):
            M = B[o.Name]; c0 = cen(o.Name); base = cost(o.Label)
            near = [k for k in B if k != o.Name and B[k][2] < M[5] - 1 and M[2] < B[k][5] - 1]
            cands = sorted(((cost(o.Label, (c0[0] + dx, c0[1] + dy)), dx, dy) for dx in rng for dy in rng if dx or dy))
            for cst, dx, dy in cands:
                if base - cst < MIN_GAIN: break
                N = [M[0] + dx, M[1] + dy, M[2], M[3] + dx, M[4] + dy, M[5]]
                if not CR.on_site(N, M, plate): continue
                if any(_ov(N, B[k], GAP * 0.5) and not (k in EQ and (_inside(B[k], N) or _inside(N, B[k]))) for k in near): continue
                # never swallow another unit or step into a container
                d = App.Vector(dx, dy, 0)
                for x in [o] + [x for x in doc.Objects if x.Label in ("LBL_" + o.Label, "LBL_%s_L0" % o.Label)]:
                    pl = x.Placement; pl.Base = pl.Base + d; x.Placement = pl
                B[o.Name] = N; new.append(dict(unit=o.Label, from_clash_with='REGROUP', dx_mm=round(dx), dy_mm=round(dy), gain_m=round((base - cst) / 1000, 1)))
                moved = True; break
        if not moved: break
    after = sum(cost(o.Label) for o in lm1)
    log = json.load(open(moves_log)) if Path(moves_log).exists() else []
    json.dump(log + new, open(moves_log, 'w'), indent=1)
    json.dump(dict(units=len(lm1), moves=len(new), adjacency_before_m=round(before / 1000, 1), adjacency_after_m=round(after / 1000, 1), moves_list=new), open(out, 'w'), indent=1)
    print("  regroup: %d L-1 units, %d moves, adjacency %.0f -> %.0f m" % (len(lm1), len(new), before / 1000, after / 1000))
