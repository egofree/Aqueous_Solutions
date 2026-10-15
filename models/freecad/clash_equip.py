"""Equipment-to-equipment solid clash check (AQS-BLD-010 rev C). Every placed equipment solid against every other; envelopes,
zones (CLEAR_, KO_, CORR_, LOBBY), headers/racks, labels, slabs, rooms and building elements excluded. A clash = common volume
> 0.001 m3. Also lists equipment inside corridor zones (CORR_*). Writes ../../docs-authority/inventory/CAD_CLASH_EQUIP.json.
    freecadcmd clash_equip.py"""
import json, re, sys, FreeCAD as App
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent)); import clash_equip_rules as CR
from pathlib import Path
here = Path(__file__).resolve().parent
doc = App.openDocument(str(here / "plant.FCStd"))
objs = [o for o in doc.Objects if CR.is_equipment(o)]
hits = []
for i, a in enumerate(objs):
    ba = a.Shape.BoundBox
    for b in objs[i + 1:]:
        if not ba.intersect(b.Shape.BoundBox): continue
        bb = b.Shape.BoundBox
        A = [ba.XMin, ba.YMin, ba.ZMin, ba.XMax, ba.YMax, ba.ZMax]; Bq = [bb.XMin, bb.YMin, bb.ZMin, bb.XMax, bb.YMax, bb.ZMax]
        if all(Bq[k] - 1 <= A[k] and A[k + 3] <= Bq[k + 3] + 1 for k in range(3)) or all(A[k] - 1 <= Bq[k] and Bq[k + 3] <= A[k + 3] + 1 for k in range(3)):
            continue  # internal of a container (e.g. COLD_BOX internals)
        try: v = a.Shape.common(b.Shape).Volume/1e9
        except Exception: continue
        if v > 0.001: hits.append(dict(a=a.Label, b=b.Label, m3=round(v, 3)))
corr = [o for o in doc.Objects if hasattr(o, "Shape") and o.Label.startswith("CORR_") and not o.Shape.isNull()]
inc = []
for c in corr:
    for o in objs:
        if not c.Shape.BoundBox.intersect(o.Shape.BoundBox): continue
        try: v = c.Shape.common(o.Shape).Volume/1e9
        except Exception: continue
        if v > 0.001 and o.Label.startswith(("PART_",)) is False: inc.append(dict(corridor=c.Label, unit=o.Label, m3=round(v, 3)))
part = [o for o in doc.Objects if hasattr(o, "Shape") and o.Label.startswith("PART_") and not o.Shape.isNull()]
for p_ in part:
    for o in objs:
        if not p_.Shape.BoundBox.intersect(o.Shape.BoundBox): continue
        try: v = p_.Shape.common(o.Shape).Volume/1e9
        except Exception: continue
        if v > 0.001: hits.append(dict(a=p_.Label, b=o.Label, m3=round(v, 3)))
json.dump(dict(solids=len(objs), clashes=hits, in_corridor=inc), open(here.parents[1] / "docs-authority/inventory/CAD_CLASH_EQUIP.json", "w"), indent=1)
print("solids", len(objs), "clashes", len(hits), "in corridor", len(inc))
