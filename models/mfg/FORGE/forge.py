"""FORGE manufacturing model, AQS-PLAN-006 work order (X-MFG lane, tier 7, route hold).

Graph revision AD. Study. Not a PE stamp. Sizes and counts come from the plant graph through the shared reader (models/mfg/lib/graph_node.py); the params.json write-back merges the builder-owned blocks only. and
rebuilds every solid.

Machine: open-die hydraulic press, N+1 former of ROLL (duty section 2:
standby-zero design-day rate, energized on the roll-stand outage at the 10 kg/d
bar class, outage_d 2, press_t 25, ram_mm 200, connected_kW 11; A-M-282/A-M-283).
A real machine drawn per the duty section 3 construction: cast-steel platens and
ram, H13 die blocks, twin-housing frame with crown, bolster bed, and the
hydraulic power unit and control pedestal as purchased envelopes per plan rule 6.
The H13 die set is the purchased consumable (buy row). There is no piped process
connection on the graph for this unit (duty section 4: no nozzle schedule is
issued), so no nozzle hardware is drawn - the named hold sits in WORK_ORDER W12.
No measured rate anywhere.

Placement frame: x along 1500 mm, y along 800 mm, z up, origin at the envelope
corner. Connection hardware: none (no schedule).
"""
import json, math, pathlib, sys

import cadquery as cq

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
from lib import fasteners, graph_node, materials              # noqa: E402
from tracker import stl_bbox_mm                    # noqa: E402  (gate-consistent STL reader)

GN = graph_node.graph_node("FORGE")        # the plant graph is the sole authority
P = GN.as_params()                            # W2 keys (size_mm, graph_revision, unit_id, nozzles, design)
P.update({k: v for k, v in json.loads((HERE / "params.json").read_text()).items() if k not in P or P[k] in (None, {}) })   # builder-owned blocks only (assumptions/form/material class do not live on the graph)
L, W, H = (float(v) for v in P["size_mm"])         # 1500 x 800 x 1500
REV = P["graph_revision"]
UNIT = P["unit_id"]
_g = json.loads((HERE.parents[2] / "flow_graph" / "plant_flow_graph.json").read_text())
DS = (next(n for n in _g["nodes"] if n["unit_id"] == UNIT).get("params") or {}).get("design") or {}

RHO_CAST = 7600.0                  # cast steel (platens, ram, housings), study value (DIETER1988 class)
RHO_TOOL = materials.density("tool_steel")   # 7850, H13 class table
RHO_CS = materials.density("CS")

RAM_D = float(DS.get("ram_mm") or 200.0)     # node design ram_mm 200
T_PLINTH = 60.0
PL_X0, PL_Z1 = 340.0, 1360.0       # housing plates: x 340..440 and 1060..1160, z 60..1360
CROWN_Z0, CROWN_Z1 = 1360.0, 1500.0
BOLSTER_Z0, BOLSTER_Z1 = 560.0, 680.0
RAM_Z0, RAM_Z1 = 900.0, 1160.0     # ram cylinder span in the crown gap
DIE_T = 120.0                      # H13 die block pair (top die under the ram, bottom die on the bolster)


def box(x, y, z, dx, dy, dz):
    return cq.Workplane().box(dx, dy, dz, centered=False).translate((x, y, z))


def rod(r, p, axis, ln):
    d = {"X": ((1, 0, 0), (0, 1, 0)), "Y": ((0, 1, 0), (1, 0, 0)), "Z": ((0, 0, 1), (1, 0, 0))}[axis]
    pl = cq.Plane(origin=p, xDir=d[1], normal=d[0])
    return cq.Workplane(pl).circle(r).extrude(ln)


parts = {}

# ---------------------------------------------------------------- plinth
parts["plinth"] = box(0, 0, 0, L, W, T_PLINTH)

# ---------------------------------------------------------------- twin housing plates + crown
parts["housing_a"] = box(PL_X0, 200.0, T_PLINTH, 100.0, 400.0, PL_Z1 - T_PLINTH)
parts["housing_b"] = box(L - PL_X0 - 100.0, 200.0, T_PLINTH, 100.0, 400.0, PL_Z1 - T_PLINTH)
parts["crown"] = box(PL_X0 - 40.0, 180.0, CROWN_Z0, L - 2 * (PL_X0 - 40.0), 440.0, CROWN_Z1 - CROWN_Z0)

# ---------------------------------------------------------------- ram cylinder + ram platen + H13 dies
parts["ram_cylinder"] = rod(RAM_D / 2 + 40.0, (L / 2, 400.0, RAM_Z0), "Z", RAM_Z1 - RAM_Z0)
parts["ram_platen"] = box(L / 2 - 200.0, 240.0, RAM_Z0 - 120.0, 400.0, 320.0, 120.0)
parts["die_top"] = box(L / 2 - 120.0, 320.0, RAM_Z0 - 120.0 - DIE_T, 240.0, 160.0, DIE_T)
parts["bolster"] = box(PL_X0 - 40.0, 200.0, BOLSTER_Z0, L - 2 * (PL_X0 - 40.0), 400.0, BOLSTER_Z1 - BOLSTER_Z0)
parts["die_bottom"] = box(L / 2 - 120.0, 320.0, BOLSTER_Z1, 240.0, 160.0, DIE_T)

# ---------------------------------------------------------------- hydraulic power unit + control pedestal (purchased envelopes)
parts["hpu_skid"] = box(1200.0, 80.0, T_PLINTH, 300.0, 440.0, 640.0)
parts["control_pedestal"] = box(40.0, 80.0, T_PLINTH, 240.0, 320.0, 900.0)

# ---------------------------------------------------------------- guard rail around the die zone (A-MACH: guard drawn)
posts = None
for gx, gy in ((620.0, 60.0), (880.0, 60.0), (620.0, 740.0), (880.0, 740.0)):
    p_ = cq.Workplane("XY", origin=(gx, gy, T_PLINTH)).circle(10.0).extrude(420.0)
    posts = p_ if posts is None else posts.union(p_)
rails = None
for gy in (60.0, 740.0):
    for zz in (300.0, 420.0):
        r_ = cq.Workplane("YZ", origin=(620.0, gy, zz)).circle(10.0).extrude(260.0)
        rails = r_ if rails is None else rails.union(r_)
for zz in (300.0, 420.0):
    r_ = box(610.0, 50.0, zz, 280.0, 20.0, 20.0)
    rails = rails.union(r_)
parts["guard_rail"] = posts.union(rails)

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
    "frame": (vol["housing_a"] + vol["housing_b"] + vol["crown"]) * RHO_CAST / 1e9,
    "ram_group": (vol["ram_cylinder"] + vol["ram_platen"]) * RHO_CAST / 1e9,
    "bolster": vol["bolster"] * RHO_CAST / 1e9,
    "die_set": (vol["die_top"] + vol["die_bottom"]) * RHO_TOOL / 1e9,
    "guard_rail": vol["guard_rail"] * RHO_CS / 1e9,
    "hpu_skid": vol["hpu_skid"] * RHO_CS / 1e9,
    "control_pedestal": vol["control_pedestal"] * RHO_CS / 1e9,
}
mass = {k: round(v, 1) for k, v in mass.items()}
report = {
    "bbox_mm": dims, "inside_size_mm": inside, "size_mm": [L, W, H],
    "size_basis": "A-M-199 forming class N+1 rated envelope (A-M-282)",
    "graph_revision": REV,
    "solids": len(solid_val.Solids()), "all_parts_valid": valid,
    "machine": {
        "frame": {"housing_x_mm": [PL_X0, PL_X0 + 100.0, L - PL_X0 - 100.0, L - PL_X0],
                  "crown_z_mm": [CROWN_Z0, CROWN_Z1],
                  "basis": "twin-housing open-die frame, cast-steel class (duty section 3, "
                  "DIETER1988)"},
        "ram": {"dia_mm": RAM_D, "span_z_mm": [RAM_Z0 - 120.0 - DIE_T, RAM_Z1],
                "basis": f"node design ram_mm {RAM_D:g}; press_t {DS.get('press_t')} is the "
                "node rating; cast-steel ram and platens (duty section 3)"},
        "die_set": {"t_mm": DIE_T, "basis": "H13 die blocks (duty section 3, ASM_V1); "
                    "purchased consumable pair, buy; the re-cuttable cast alternative is the "
                    "duty alternative row"},
        "bolster": {"z_mm": [BOLSTER_Z0, BOLSTER_Z1]},
        "purchased": "hydraulic power unit and control pedestal on their bays, drawn as "
        "their envelopes per plan rule 6 (connected_kW 11 is the node rating)",
        "guard": "die-zone guard rail on 4 posts, 2 rail tiers (A-MACH: guard drawn)"},
    "standby": {"state": "standby_rated N+1 former of ROLL (A-M-282/A-M-283); energized on "
                f"the roll-stand outage at the bar class (outage_d {DS.get('outage_d')}); "
                "design-day rate zero on the graph",
                "basis": "duty section 2 sizing study"},
    "material": {"class": "H13 die blocks + cast-steel platens/ram on the open-die press",
                 "ca_mm": 0.0,
                 "basis": "duty section 3 (X-MAT-22); CA 0 mm - dry hot-work contact, no "
                 "corrosive stream (AQS-STD-001 shop rule)"},
    "a_mach": {"guard": "die-zone guard rail drawn (A-MACH)",
               "anchors": "8 M16 wedge anchors, plinth to slab (fasteners.csv)",
               "purchased": "HPU skid and control pedestal (connected_kW 11, node design)"},
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
     mass["plinth"], "make", "dry forge-floor service, CA 0 mm (AQS-STD-001 shop rule); "
     "anchors in fasteners.csv"],
    ["2", f"Twin-housing frame: housing plates 100 t with crown beam z {CROWN_Z0:g}..{CROWN_Z1:g}",
     1, "cast steel", mass["frame"], "make",
     "duty section 3: cast-steel platens/frame (DIETER1988); N+1 former of ROLL (A-M-282); "
     "study sections (WORK_ORDER W12)"],
    ["3", f"Ram group: cylinder OD {RAM_D + 80:g} (node design ram_mm {RAM_D:g}) with platen, "
          f"press_t {DS.get('press_t')} node rating", 1, "cast steel", mass["ram_group"], "make",
     "duty section 3: cast-steel ram and platens; the hydraulic cylinder package purchases "
     "at fabrication (WORK_ORDER W12)"],
    ["4", f"Bolster bed z {BOLSTER_Z0:g}..{BOLSTER_Z1:g}", 1, "cast steel", mass["bolster"],
     "make", "duty section 3 platen class"],
    ["5", f"H13 die block pair, t{DIE_T:g} (open-die flat dies)", 1, "H13 tool steel (consumable)",
     mass["die_set"], "buy", "duty section 3 (ASM_V1); consumable set, buy; the re-cuttable "
     "cast alternative is the duty alternative row (not drawn)"],
    ["6", "Die-zone guard rail, 4 posts x 2 tiers (A-MACH: guard drawn)", 1, "CS tube",
     mass["guard_rail"], "make", "guard over the die zone; layout choice (WORK_ORDER W12)"],
    ["7", "Hydraulic power unit skid on the +X bay (purchased, envelope and interface)", 1,
     "purchased skid (envelope)", mass["hpu_skid"], "buy",
     "purchased per plan rule 6; connected_kW 11 is the node rating; standby unit (A-M-282)"],
    ["8", "Control pedestal on the -X floor (purchased, envelope and interface)", 1,
     "purchased pedestal (envelope)", mass["control_pedestal"], "buy",
     "purchased per plan rule 6"],
    ["9", "Nozzle set: none - no piped process connection on the graph, no schedule issued "
          "(duty section 4; hold, WORK_ORDER W12)", 0, "n/a", 0.0, "n/a",
     "no nozzle hardware drawn; a schedule row lands as a DN15 set-in when the graph rates "
     "an edge"],
]
with open(HERE / "bom.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["item", "description", "qty", "material", "mass_kg", "make_or_buy", "basis"])
    w.writerows(rows)

# ---------------------------------------------------------------- fasteners (W5)
fasteners.write_fasteners(HERE / "fasteners.csv", [
    [None, "M16 wedge anchor", fasteners.grade_for("CS"), 8,
     "plinth to slab, 4 per rail (count from the model)",
     "grade rule AQS-PLAN-006 W5: 8.8 on carbon steel; study length, confirmed at fabrication"],
    [None, "M24 stud + nut (ISO 4014 / ISO 4032)", fasteners.grade_for("CS"), 8,
     "crown-to-housing ties and bolster hold-downs",
     "grade rule W5: 8.8 on carbon steel; study torque, confirmed at fabrication"],
])

# ---------------------------------------------------------------- builder-owned params blocks
p = json.loads((HERE / "params.json").read_text())
p.pop("graph", None)
p["envelope"] = {
    "size_mm": [L, W, H],
    "basis": "A-M-199 forming class N+1 rated envelope (A-M-282)",
    "frame": {"housing_x_mm": [PL_X0, L - PL_X0 - 100.0], "crown_z_mm": [CROWN_Z0, CROWN_Z1]},
    "purchased_bays": {"hpu_x_mm": [1200.0, 1500.0], "pedestal_x_mm": [40.0, 280.0]},
}
p["design"] = {
    "machine": "open-die hydraulic press, N+1 former of ROLL (node design machine)",
    "mat": "H13 die blocks + cast-steel platens/ram (duty section 3)",
    "ca_mm": 0.0,
    "wall_basis": "study cast-steel sections; no thickness booked on the node (WORK_ORDER W12)",
    "internals": "none drawn (node internals row none)",
    "purchased": f"HPU skid and control pedestal (connected_kW {DS.get('connected_kW')} node "
                 "design), drawn as their envelopes (plan rule 6); the H13 die pair is the "
                 "purchased consumable",
}
p["layout"] = {
    "frame": "origin at the envelope corner; twin housings x 340..440 / 1060..1160 on the "
             "plinth, crown across the top; ram centreline at x 750; bolster bed mid-height; "
             "HPU bay +X, control pedestal -X; die-zone guard rail between them",
    "nozzle_spread": "no piped process connection on the graph (duty section 4); no nozzle "
                     "hardware drawn (hold, WORK_ORDER W12)",
    "hardware_idiom": "no connection hardware; bbox within the node envelope",
}
(HERE / "params.json").write_text(json.dumps(p, indent=1) + "\n")

print(json.dumps({k: report[k] for k in ("bbox_mm", "inside_size_mm", "solids",
                                         "part_mass_kg")}), flush=True)
