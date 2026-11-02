"""RES_HEAT manufacturing model, AQS-PLAN-006 work order (X-MFG lane, tier 6, route hold).

Graph revision AD. Study. Not a PE stamp. Reads params.json only (W2 fields by the
tracker; the envelope, design and layout blocks beside them are builder-owned) and
rebuilds every solid.

Machine: resistance radiant reheating box furnace, N+1 standby of the SHELL_BURNOUT /
SINTER heating duty (duty section 2: standby-zero design-day rate, energized on a
burnout-element outage during a shell campaign, outage_d 2, T_C 900, connected_kW 12;
A-M-282/A-M-283). A real machine drawn per the duty section 3 construction:
ceramic-fibre module lining + 80Ni-20Cr resistance elements on a mild-steel casing,
with the door face, hearth plate and element racks. There is no piped process
connection on the graph for this unit (duty section 4: no nozzle schedule is issued),
so no nozzle hardware is drawn - the named hold sits in WORK_ORDER W12. No measured
rate anywhere.

Placement frame: x along 1000 mm, y along 1000 mm, z up, origin at the envelope
corner. Connection hardware: none (no schedule). The controls cabinet (connected_kW
12) is a purchased envelope on the +X bay per plan rule 6.
"""
import json, math, pathlib, sys

import cadquery as cq

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
from lib import fasteners, materials              # noqa: E402
from tracker import stl_bbox_mm                    # noqa: E402  (gate-consistent STL reader)

P = json.loads((HERE / "params.json").read_text())
L, W, H = (float(v) for v in P["size_mm"])         # 1000 x 1000 x 1500
REV = P["graph_revision"]
UNIT = P["unit_id"]
_g = json.loads((HERE.parents[2] / "flow_graph" / "plant_flow_graph.json").read_text())
DS = (next(n for n in _g["nodes"] if n["unit_id"] == UNIT).get("params") or {}).get("design") or {}

RHO_CS = materials.density("CS")
RHO_ELEMENT = 8400.0               # 80Ni-20Cr, study value (ASM_V1 class; hold, W12)
RHO_FIBRE = 128.0                  # ceramic-fibre module 128 kg/m3 (IND_MELT lining class)

T_SHELL = 4.0                      # mild-steel casing, study fab-page value (hold, W12)
T_FIBRE = 100.0                    # fibre module lining, study (hold, W12)
CH_X, CH_Y = 660.0, 1000.0         # casing footprint
CH_Z0, CH_Z1 = 60.0, 1160.0        # casing on the plinth
T_PLINTH = 60.0
CX, CY = CH_X / 2, CH_Y / 2


def box(x, y, z, dx, dy, dz):
    return cq.Workplane().box(dx, dy, dz, centered=False).translate((x, y, z))


def rod(r, p, axis, ln):
    d = {"X": ((1, 0, 0), (0, 1, 0)), "Y": ((0, 1, 0), (1, 0, 0)), "Z": ((0, 0, 1), (1, 0, 0))}[axis]
    pl = cq.Plane(origin=p, xDir=d[1], normal=d[0])
    return cq.Workplane(pl).circle(r).extrude(ln)


parts = {}

# ---------------------------------------------------------------- plinth
parts["plinth"] = box(0, 0, 0, L, W, T_PLINTH)

# ---------------------------------------------------------------- casing (mild steel t4) + door face
casing = box(0, 0, CH_Z0, CH_X, CH_Y, CH_Z1 - CH_Z0).cut(
    box(T_SHELL, T_SHELL, CH_Z0 + T_SHELL, CH_X - 2 * T_SHELL, CH_Y - 2 * T_SHELL,
        CH_Z1 - CH_Z0 - 2 * T_SHELL))
parts["casing"] = casing
parts["door_face"] = box(0.0, 220.0, CH_Z0 + T_SHELL, 50.0, CH_Y - 440.0, CH_Z1 - CH_Z0 - 2 * T_SHELL)
for dz in (260.0, 520.0, 780.0):
    parts["door_face"] = parts["door_face"].union(box(0.0, 220.0 + dz - 240.0, CH_Z0 + T_SHELL,
                                                      50.0, 20.0, CH_Z1 - CH_Z0 - 2 * T_SHELL))

# ---------------------------------------------------------------- ceramic-fibre module lining
fibre = box(T_SHELL, T_SHELL, CH_Z0 + T_SHELL, CH_X - 2 * T_SHELL, CH_Y - 2 * T_SHELL,
            CH_Z1 - CH_Z0 - 2 * T_SHELL).cut(
    box(T_SHELL + T_FIBRE, T_SHELL + T_FIBRE, CH_Z0 + T_SHELL + T_FIBRE,
        CH_X - 2 * (T_SHELL + T_FIBRE), CH_Y - 2 * (T_SHELL + T_FIBRE),
        CH_Z1 - CH_Z0 - 2 * (T_SHELL + T_FIBRE)))
fibre = fibre.cut(box(0.0, 215.0, CH_Z0 + T_SHELL, 55.0 + T_FIBRE, CH_Y - 430.0,
                      CH_Z1 - CH_Z0 - 2 * T_SHELL))   # door recess
parts["fibre_lining"] = fibre

# ---------------------------------------------------------------- 80Ni-20Cr element racks (side walls + crown)
elements = None
for sy in (170.0, 830.0):
    for i in range(4):
        for zz in (240.0, 420.0, 600.0, 780.0):
            e = rod(12.0, (150.0 + i * 90.0, sy, zz), "X", 360.0)
            elements = e if elements is None else elements.union(e)
for i in range(3):
    e = rod(12.0, (200.0 + i * 120.0, 170.0, CH_Z1 - 190.0), "Y", 660.0)   # crown elements
    elements = elements.union(e) if elements is not None else e
parts["element_racks"] = elements

# ---------------------------------------------------------------- hearth plate
parts["hearth_plate"] = box(180.0, 160.0, CH_Z0 + T_SHELL + T_FIBRE,
                            CH_X - 420.0, CH_Y - 560.0, 30.0)

# ---------------------------------------------------------------- controls cabinet (+X bay, purchased envelope)
parts["controls_cabinet"] = box(CH_X, 0, 0, L - CH_X, 500.0, H).cut(
    box(CH_X + 8.0, 8.0, 8.0, L - CH_X - 16.0, 484.0, H - 16.0))

# ---------------------------------------------------------------- export
asm = cq.Assembly(name=UNIT)
for k, v in parts.items():
    asm.add(v, name=k)
out = HERE / "export"; out.mkdir(exist_ok=True)
asm.export(str(out / (UNIT.lower() + ".step")))

solid = None
for k, v in parts.items():
    solid = v if solid is None else solid.union(v)
solid_val = solid.val()
solid_val.exportStl(str(out / (UNIT.lower() + ".stl")), tolerance=0.4, angularTolerance=0.4, ascii=True)
solid_val.scale(0.001).exportStl(str(HERE.parents[2] / "cad" / "stl" / (UNIT + ".stl")),
                                 tolerance=0.0005, angularTolerance=0.4, ascii=True)

# ---------------------------------------------------------------- checks + report
dims = stl_bbox_mm(str(out / (UNIT.lower() + ".stl")))
inside = all(d <= s + 1.0 for d, s in zip(dims, [L, W, H]))
valid = all(v.val().isValid() for v in parts.values())
vol = {k: v.val().Volume() for k, v in parts.items()}
mass = {
    "plinth": vol["plinth"] * RHO_CS / 1e9,
    "casing": vol["casing"] * RHO_CS / 1e9,
    "door_face": vol["door_face"] * RHO_CS / 1e9,
    "fibre_lining": vol["fibre_lining"] * RHO_FIBRE / 1e9,
    "element_racks": vol["element_racks"] * RHO_ELEMENT / 1e9,
    "hearth_plate": vol["hearth_plate"] * RHO_CS / 1e9,
    "controls_cabinet": vol["controls_cabinet"] * RHO_CS / 1e9,
}
mass = {k: round(v, 1) for k, v in mass.items()}
report = {
    "bbox_mm": dims, "inside_size_mm": inside, "size_mm": [L, W, H],
    "size_basis": "A-M-199 melt class N+1 rated envelope (A-M-282)",
    "graph_revision": REV,
    "solids": len(solid_val.Solids()), "all_parts_valid": valid,
    "machine": {
        "casing": {"od_mm": [CH_X, CH_Y], "z_mm": [CH_Z0, CH_Z1], "wall_mm": T_SHELL,
                   "wall_basis": "study fab-page mild-steel t4 casing (no thickness booked on "
                   "the node - hold, WORK_ORDER W12)"},
        "lining": {"fibre_mm": T_FIBRE, "basis": "ceramic-fibre module lining (duty section 3, "
                   "SCHACHT2004 ch. 13 class; to 1100 C per ASM_V1), study t100 (hold, W12)"},
        "elements": {"material": "80Ni-20Cr, OD 24 rods in wall and crown racks",
                     "basis": f"duty section 3 element class; connected_kW {DS.get('connected_kW')} "
                     "is the node rating at the 900 C design (node design T_C); MoSi2 is the "
                     "duty alternative above 1100 C (not drawn)"},
        "door": "front door face on -X with recess; door interlock is loop hardware (W12)"},
    "standby": {"state": "standby_rated N+1 of the SHELL_BURNOUT / SINTER heating duty "
                "(A-M-282/A-M-283); energized on a burnout-element outage during a shell "
                f"campaign (outage_d {DS.get('outage_d')}); design-day rate zero on the graph",
                "basis": "duty section 2 sizing study"},
    "material": {"class": "mild-steel casing, ceramic-fibre module lining, 80Ni-20Cr elements",
                 "ca_mm": 0.0,
                 "basis": "duty section 3 (X-MAT-22); CA 0 mm - dry furnace service "
                 "(AQS-STD-001 shop rule)"},
    "a_mach_anchors": "8 M12 wedge anchors, plinth to slab (fasteners.csv)",
    "nozzles": "no piped process connection on the graph; no nozzle schedule is issued "
    "(duty section 4) - no nozzle hardware drawn (hold, WORK_ORDER W12)",
    "nozzle_count_schedule": 0,
    "part_mass_kg": mass, "cadquery": cq.__version__,
}
(HERE / "check.json").write_text(json.dumps(report, indent=2) + "\n")

# ---------------------------------------------------------------- BOM (generated from the model)
import csv  # noqa: E402
rows = [
    ["1", f"Plinth {L:g} x {W:g} x {T_PLINTH:g} (CS, anchor bosses)", 1, "carbon steel",
     mass["plinth"], "make", "dry furnace-shop service, CA 0 mm (AQS-STD-001 shop rule); "
     "anchors in fasteners.csv"],
    ["2", f"Furnace casing mild steel t{T_SHELL:g}, {CH_X:g} x {CH_Y:g} x {CH_Z1 - CH_Z0:g}, "
          "with front door face", 1, "carbon steel",
     round(mass["casing"] + mass["door_face"], 1), "make",
     "duty section 3: mild-steel casing; wall is the study fab-page value (hold, WORK_ORDER "
     "W12); N+1 standby of the SHELL_BURNOUT/SINTER heating duty (A-M-282)"],
    ["3", f"Ceramic-fibre module lining t{T_FIBRE:g}", 1, "ceramic-fibre module 128 kg/m3",
     mass["fibre_lining"], "make",
     "duty section 3 (SCHACHT2004 ch. 13; ASM_V1 to 1100 C); thickness is the study "
     "fab-page value (hold, WORK_ORDER W12)"],
    ["4", f"80Ni-20Cr resistance elements, OD 24, wall and crown racks "
          f"({DS.get('connected_kW')} kW connected, T_C {DS.get('T_C')} node design)", 16,
     "80Ni-20Cr (consumable set)", mass["element_racks"], "buy",
     "duty section 3 element class; element change-out is the consumable cycle the standby "
     "duty exists to cover (A-M-282)"],
    ["5", "Hearth plate on the lining floor", 1, "carbon steel", mass["hearth_plate"], "make",
     "reheating hearth (study, WORK_ORDER W12)"],
    ["6", f"Controls cabinet, {DS.get('connected_kW')} kW connected (node design), IP54", 1,
     "purchased cabinet (envelope)", mass["controls_cabinet"], "buy",
     "purchased per plan rule 6; standby unit (A-M-282); SCR package purchased at "
     "fabrication (WORK_ORDER W12)"],
]
with open(HERE / "bom.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["item", "description", "qty", "material", "mass_kg", "make_or_buy", "basis"])
    w.writerows(rows)

# ---------------------------------------------------------------- fasteners (W5)
fasteners.write_fasteners(HERE / "fasteners.csv", [
    [None, "M12 wedge anchor", fasteners.grade_for("CS"), 8,
     "plinth to slab, 4 per rail (count from the model)",
     "grade rule AQS-PLAN-006 W5: 8.8 on carbon steel; study length, confirmed at fabrication"],
    [None, "M10 stud + nut (ISO 4014 / ISO 4032)", fasteners.grade_for("CS"), 12,
     "door face hinge and casing roof hatch",
     "grade rule W5: 8.8 on carbon steel; study torque, confirmed at fabrication"],
])

# ---------------------------------------------------------------- builder-owned params blocks
p = json.loads((HERE / "params.json").read_text())
p.pop("graph", None)
p["envelope"] = {
    "size_mm": [L, W, H],
    "basis": "A-M-199 melt class N+1 rated envelope (A-M-282)",
    "casing": {"xy_mm": [CH_X, CH_Y], "z_mm": [CH_Z0, CH_Z1], "wall_mm": T_SHELL},
    "cabinet_bay": {"x_mm": [CH_X, L]},
}
p["design"] = {
    "machine": "resistance radiant reheating furnace, N+1 standby of the SHELL_BURNOUT/SINTER "
               "heating duty (node design service)",
    "mat": "mild-steel casing, ceramic-fibre module lining, 80Ni-20Cr resistance elements "
           "(duty section 3)",
    "ca_mm": 0.0,
    "wall_mm": T_SHELL, "wall_basis": "study fab-page mild-steel t4 casing (WORK_ORDER W12)",
    "internals": "none drawn (node internals row none); the hearth plate is furnace "
                 "furniture, a BOM part, not an internal",
    "purchased": f"controls cabinet {DS.get('connected_kW')} kW connected (node design), "
                 "drawn as its envelope (plan rule 6); SCR package at fabrication; the "
                 "80Ni-20Cr element set is a purchased consumable (buy row)",
}
p["layout"] = {
    "frame": "origin at the envelope corner; casing on the plinth x 0..660, y 0..1000, "
             "z 60..1160; door face -X; element racks on both walls and the crown; "
             "controls bay x 660..1000",
    "nozzle_spread": "no piped process connection on the graph (duty section 4); no nozzle "
                     "hardware drawn (hold, WORK_ORDER W12)",
    "hardware_idiom": "no connection hardware; bbox within the node envelope",
}
(HERE / "params.json").write_text(json.dumps(p, indent=1) + "\n")

print(json.dumps({k: report[k] for k in ("bbox_mm", "inside_size_mm", "solids",
                                         "part_mass_kg")}), flush=True)
