"""Equipment overlap resolver (AQS-BLD-010 rev C, A-M-220). Runs in build_plant.py after placement, before the rated rooms.
For each partly overlapping pair of equipment solids (a solid wholly inside another's box is an internal, e.g. COLD_BOX
internals, and is left), the smaller one moves in plan by the least penetration + GAP along +/-X or +/-Y, to the first
position whose box is clear of all equipment, corridors, stairs, shafts and rated walls on its level and stays on the plate
(or in its yard). Labels move with it. Logs every move to ../../docs-authority/inventory/CAD_MOVES.json."""
import json, re
from pathlib import Path
import FreeCAD as App
import clash_equip_rules as CR
GAP = 100.0
def _bb(o):
    b = o.Shape.BoundBox; return [b.XMin, b.YMin, b.ZMin, b.XMax, b.YMax, b.ZMax]
def _ov(a, b, g=0.0):  # plan gap g; vertical overlap strict (a tank top touching the floor above is not a clash)
    return all(a[i] < b[i + 3] + g and b[i] < a[i + 3] + g for i in range(2)) and a[2] < b[5] - 1 and b[2] < a[5] - 1
def _inside(a, b):
    return all(b[i] - 1 <= a[i] and a[i + 3] <= b[i + 3] + 1 for i in range(3))
def resolve(doc, plate=None, log=None):
    eq = [o for o in doc.Objects if CR.is_equipment(o)]
    obst = [o for o in doc.Objects if CR.is_obstacle(o)]
    B = {o.Name: _bb(o) for o in eq + obst}
    moves = []; EQ = {o.Name for o in eq}
    def free(k, N, me):
        if k == me or not _ov(N, B[k], GAP*0.5): return True
        if k in EQ and (_inside(B[k], N) or _inside(N, B[k])): return True   # container / internal pair
        return False
    def place(m, F):
        M = B[m.Name]
        cands = [((F[3] - M[0]) + GAP, 0), (-(M[3] - F[0]) - GAP, 0), (0, (F[4] - M[1]) + GAP), (0, -(M[4] - F[1]) - GAP)]
        for step in range(0, 80):
            for dx, dy in sorted(cands, key=lambda c: abs(c[0]) + abs(c[1])):
                ex = step*200.0*((dx > 0) - (dx < 0)); ey = step*200.0*((dy > 0) - (dy < 0))
                N = [M[0] + dx + ex, M[1] + dy + ey, M[2], M[3] + dx + ex, M[4] + dy + ey, M[5]]
                if plate and not CR.on_site(N, M, plate): continue
                if not all(free(k, N, m.Name) for k in B): continue
                d = App.Vector(dx + ex, dy + ey, 0)
                for o in [m] + [x for x in doc.Objects if x.Label in ("LBL_" + m.Label, "LBL_%s_L0" % m.Label)]:
                    pl = o.Placement; pl.Base = pl.Base + d; o.Placement = pl
                B[m.Name] = N; return d
        return None
    def solid_ov(a, b):
        try: return a.Shape.common(b.Shape).Volume >= 1e6
        except Exception: return False
    for _ in range(8):
        changed = False
        for i, a in enumerate(eq):
            for b in eq[i + 1:] + obst:
                A, Bb = B[a.Name], B[b.Name]
                if not _ov(A, Bb): continue
                if b.Name in EQ and (_inside(A, Bb) or _inside(Bb, A)): continue
                if not solid_ov(a, b): continue
                if b.Name in EQ:
                    m, f = (a, b) if a.Shape.Volume <= b.Shape.Volume else (b, a)
                    order = [(m, f), (f, m)]
                else:
                    order = [(a, b)]
                for m, f in order:
                    d = place(m, B[f.Name])
                    if d is not None:
                        moves.append(dict(unit=m.Label, from_clash_with=f.Label, dx_mm=round(d.x), dy_mm=round(d.y))); changed = True; break
                else:
                    moves.append(dict(unit=order[0][0].Label, from_clash_with=order[0][1].Label, dx_mm=None, dy_mm=None, note='no free position within 16 m'))
        if not changed: break
    # keep only the final state of unresolved notes
    ok = {(x['unit'], x['from_clash_with']) for x in moves if x['dx_mm'] is not None}
    moves = [x for x in moves if x['dx_mm'] is not None or (x['unit'], x['from_clash_with']) not in ok]
    if log:
        json.dump(moves, open(log, 'w'), indent=1)
    print("  overlap resolver: %d moves, %d unresolved" % (sum(1 for x in moves if x['dx_mm'] is not None), sum(1 for x in moves if x['dx_mm'] is None)))
    return moves
