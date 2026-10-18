"""Solid clash check of the built plant.FCStd (AQS-BLD-010 rev B, X-BLD-04 follow-up): new building elements (FR_* rated rooms,
STAIR_*, ELEV_*, DOCK_APRON_N, SERVICE_ENTRY) against every other Part solid. A clash = common volume > 0.001 m3, excluding slabs,
horizontal assemblies, groups, labels and the elements' own family. Writes ../../docs-authority/inventory/CAD_CLASH.json.
    freecadcmd clash_check.py"""
import json, re, FreeCAD as App
from pathlib import Path
here = Path(__file__).resolve().parent
doc = App.openDocument(str(here / "plant.FCStd"))
NEW = ("FR_", "STAIR_", "ELEV_", "DOCK_APRON", "SERVICE_ENTRY", "FB_CRYO_H2_PART", "CRYO_EGRESS")
SKIPP = ("LOBBY", "CORR_", "TOILET", "WETROOM", "OVERFLOW_APRON", "GROUND_PLANE", "RACK_", "HDR_", "MASSING_", "LED_", "GROW_TRAY", "HABITATION", "FARM", "MFG_SHOP", "WAFER_FAB", "FAB_PREP", "DOCK", "HA_", "SLAB", "LBL", "LABEL", "SIGN", "TXT", "FB_", "ENV_", "PLATE", "CORE", "TERRACE", "RAIL", "ROOF", "ARRAY", "GRID", "LEVEL", "CAMPUS", "SITE")
objs = [o for o in doc.Objects if hasattr(o, "Shape") and o.TypeId.startswith("Part::") and not o.Shape.isNull() and o.Shape.Volume > 1e3]
new = [o for o in objs if o.Name.startswith(NEW) or o.Label.startswith(NEW)]
oth = [o for o in objs if not (o.Name.startswith(NEW) or o.Label.startswith(NEW)) and not any(k in o.Label.upper() for k in SKIPP) and not re.match(r"^CRYO(_B\d+)?$", o.Label)]  # CRYO = room envelope
hits = []
for a in new:
    ba = a.Shape.BoundBox
    for b in oth:
        if not ba.intersect(b.Shape.BoundBox): continue
        try: v = a.Shape.common(b.Shape).Volume/1e9
        except Exception: continue
        if v > 0.001: hits.append(dict(a=a.Label, b=b.Label, m3=round(v, 3)))
json.dump(dict(new=len(new), others=len(oth), clashes=hits), open(here.parents[1] / "docs-authority/inventory/CAD_CLASH.json", "w"), indent=1)
print("new", len(new), "others", len(oth), "clashes", len(hits))
for h in hits[:60]: print(h)
