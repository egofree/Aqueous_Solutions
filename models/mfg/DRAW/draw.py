"""DRAW manufacturing model, AQS-PLAN-006 work order (X-MFG lane, tier 7, F-MACH).

Graph revision AD. Study. Not a PE stamp. Sizes and counts come from the plant graph through the shared reader (models/mfg/lib/graph_node.py); the params.json write-back merges the builder-owned blocks only. and
rebuilds every solid.

Machine: bench wire/rod draw bench, N+1 former of ROLL (duty section 2:
standby-zero design-day rate, energized on the roll-stand outage on wire-class
lots, outage_d 2, bench_mm 1200, 6 dies, connected_kW 3; A-M-282/A-M-283). A real
machine drawn per the duty section 3 construction: tungsten-carbide drawing dies
in tool-steel casings (consumable buy set) on the die stand, steel bench bed,
capstan drum with the drive group, gripper carriage, wire-guide sheaves, and the
die-zone/capstan guard (A-MACH). The capstan hardware carries the machine
lubricant programme - no wetted stream (duty section 3). The drive group and
control cabinet are purchased envelopes per plan rule 6. Schedule rows: N1 solids
wire at DN15 (bore not calculated, W4), N2/N3 DN15 atmospheric tube. Connection
hardware draws flush at the envelope faces: nothing protrudes (A-core 2). No
measured rate anywhere.

Placement frame: x along 1500 mm (x 0 = die-stand tail, x 1500 = capstan head),
y along 800 mm, z up, origin at the envelope corner. The schedule faces map to
compass by the registered layout choice (params.json layout block); heights,
bores and ratings are docs-authority/nozzles/DRAW.csv verbatim.
"""
import json, math, pathlib, sys

import cadquery as cq

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
from lib import dn, fasteners, graph_node, materials          # noqa: E402
from tracker import stl_bbox_mm                    # noqa: E402  (gate-consistent STL reader)

GN = graph_node.graph_node("DRAW")        # the plant graph is the sole authority
P = GN.as_params()                            # W2 keys (size_mm, graph_revision, unit_id, nozzles, design)
P.update({k: v for k, v in json.loads((HERE / "params.json").read_text()).items() if k not in P or P[k] in (None, {}) })   # builder-owned blocks only (assumptions/form/material class do not live on the graph)
L, W, H = (float(v) for v in P["size_mm"])         # 1500 x 800 x 1500
REV = P["graph_revision"]
UNIT = P["unit_id"]
_g = json.loads((HERE.parents[2] / "flow_graph" / "plant_flow_graph.json").read_text())
DS = (next(n for n in _g["nodes"] if n["unit_id"] == UNIT).get("params") or {}).get("design") or {}

RHO_CS = materials.density("CS")
RHO_TOOL = materials.density("tool_steel")

N_DIES = int(DS.get("dies") or 6)                  # node design dies 6
BENCH_L = float(DS.get("bench_mm") or 1200.0)      # node design bench_mm 1200
T_PLINTH = 60.0
CY = 400.0                                         # bench centreline
BED_X0 = 120.0
BED_Z0, BED_Z1 = 300.0, 420.0                      # bench bed section
CAP_D = 420.0                                      # capstan drum OD, study (hold, W12)
CAP_X = BED_X0 + BENCH_L                           # capstan head x
OUT_Z = 600.0                                      # N1 datum


def box(x, y, z, dx, dy, dz):
    return cq.Workplane().box(dx, dy, dz, centered=False).translate((x, y, z))


def rod(r, p, axis, ln):
    d = {"X": ((1, 0, 0), (0, 1, 0)), "Y": ((0, 1, 0), (1, 0, 0)), "Z": ((0, 0, 1), (1, 0, 0))}[axis]
    pl = cq.Plane(origin=p, xDir=d[1], normal=d[0])
    return cq.Workplane(pl).circle(r).extrude(ln)


def tube(r_out, r_in, p, axis, ln):
    d = {"X": ((1, 0, 0), (0, 1, 0)), "Y": ((0, 1, 0), (1, 0, 0)), "Z": ((0, 0, 1), (1, 0, 0))}[axis]
    pl = cq.Plane(origin=p, xDir=d[1], normal=d[0])
    return cq.Workplane(pl).circle(r_out).circle(r_in).extrude(ln)


def dn15():
    return dn.pipe_od("DN15") / 2, dn.pipe_od("DN15") / 2 - dn.pipe_wall("DN15", 40)


parts = {}

# ---------------------------------------------------------------- plinth
parts["plinth"] = box(0, 0, 0, L, W, T_PLINTH)

# ---------------------------------------------------------------- bench bed (steel channel) + legs
parts["bench_bed"] = box(BED_X0, CY - 120.0, BED_Z0, BENCH_L, 240.0, BED_Z1 - BED_Z0)
for lx, ly in ((BED_X0 + 20.0, CY - 320.0), (BED_X0 + 20.0, CY + 280.0),
               (CAP_X - 220.0, CY - 320.0), (CAP_X - 220.0, CY + 280.0)):
    parts["bench_bed"] = parts["bench_bed"].union(box(lx, ly, T_PLINTH, 60.0, 40.0, BED_Z0 - T_PLINTH))

# ---------------------------------------------------------------- die stand (-X head) with 6 carbide die casings
stand = box(BED_X0, CY - 160.0, BED_Z1, 160.0, 320.0, 360.0)
parts["die_stand"] = stand
dies = None
for i in range(N_DIES):
    dx = BED_X0 + 30.0 + (i % 3) * 45.0
    dz = BED_Z1 + 60.0 + (i // 3) * 110.0
    d_ = tube(35.0, 12.0, (dx, CY, dz), "X", 70.0)          # carbide die in its tool-steel casing
    dies = d_ if dies is None else dies.union(d_)
parts["die_set"] = dies

# ---------------------------------------------------------------- capstan drum + gripper carriage + wire guides
parts["capstan_drum"] = rod(CAP_D / 2, (CAP_X - 120.0, CY, OUT_Z + 120.0), "Y", 160.0)
parts["capstan_shaft"] = rod(40.0, (CAP_X - 260.0, CY, OUT_Z + 120.0), "Y", 320.0)
parts["gripper_carriage"] = box(BED_X0 + 300.0, CY - 70.0, BED_Z1 + 20.0, 140.0, 140.0, 90.0)
guides = None
for gx in (BED_X0 + 240.0, BED_X0 + 520.0, BED_X0 + 800.0):
    g_ = rod(25.0, (gx, CY - 110.0, OUT_Z - 20.0), "Z", 120.0)
    guides = g_ if guides is None else guides.union(g_)
parts["wire_guides"] = guides

# ---------------------------------------------------------------- drive group + control cabinet (purchased envelopes)
parts["drive_group"] = box(CAP_X - 60.0, CY - 150.0, T_PLINTH, L - (CAP_X - 60.0), 300.0, 520.0)
parts["control_cabinet"] = box(40.0, 620.0, T_PLINTH, 300.0, 160.0, 900.0)

# ---------------------------------------------------------------- guard rail over the die zone and capstan (A-MACH)
posts = None
for gx, gy in ((240.0, 140.0), (900.0, 140.0), (240.0, 660.0), (900.0, 660.0)):
    p_ = cq.Workplane("XY", origin=(gx, gy, T_PLINTH)).circle(10.0).extrude(760.0)
    posts = p_ if posts is None else posts.union(p_)
rails = None
for gy in (140.0, 660.0):
    for zz in (300.0, 420.0, 720.0):
        r_ = cq.Workplane("YZ", origin=(240.0, gy, zz)).circle(10.0).extrude(660.0)
        rails = r_ if rails is None else rails.union(r_)
for zz in (300.0, 420.0, 720.0):
    rails = rails.union(box(230.0, 130.0, zz, 680.0, 20.0, 20.0))
parts["guard_rail"] = posts.union(rails)

# ---------------------------------------------------------------- nozzle hardware (schedule verbatim, flush at the envelope faces)
r15, w15 = dn15()
noz = {}
# N1 solids wire out: +X face at z 600, drawn at DN15 (bore not calculated), on the take-off guide
noz["N1_wire_out"] = tube(r15, w15, (L - 60.0, CY, OUT_Z), "X", 60.0)
noz["N2_drain"] = tube(30.5, r15, (700.0, 400.0, 0.0), "Z", T_PLINTH)
noz["N3_vent_riser"] = tube(r15, w15, (CAP_X - 60.0, CY, 1140.0), "Z", H - 1140.0)
for k, v in noz.items():
    parts[k] = v

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
    "bench_bed": vol["bench_bed"] * RHO_CS / 1e9,
    "die_stand": vol["die_stand"] * RHO_CS / 1e9,
    "die_set": vol["die_set"] * RHO_TOOL / 1e9,
    "capstan_group": (vol["capstan_drum"] + vol["capstan_shaft"] + vol["gripper_carriage"]
                      + vol["wire_guides"]) * RHO_CS / 1e9,
    "drive_group": vol["drive_group"] * RHO_CS / 1e9,
    "control_cabinet": vol["control_cabinet"] * RHO_CS / 1e9,
    "guard_rail": vol["guard_rail"] * RHO_CS / 1e9,
    "nozzles": sum(vol[k] for k in noz) * RHO_CS / 1e9,
}
mass = {k: round(v, 1) for k, v in mass.items()}
schedule = [r for r in P["nozzles"]]
drawn = {}
for r in schedule:
    tag = r["tag"]
    note = "atmospheric open-bore DN15 tube, flush at the envelope face (duty section 4)"
    if r["size"] == "solids":
        note += "; solids row drawn at DN15, bore not calculated (W4 rule)"
    if r["face"] == "bottom":
        note += "; flush at the envelope bottom (schedule datum 50)"
    if r["face"] == "top":
        note += "; schedule datum 800 is the placeholder elevation - the riser stands on the " \
                "capstan head and flushes at the envelope top (hold, WORK_ORDER W12)"
    drawn[tag] = {"style": "tube", "dn": r["size"], "face": r["face"], "height_mm": r["height_mm"],
                  "drawn_height_mm": {"N1": float(OUT_Z), "N2": 0.0, "N3": float(H)}[tag],
                  "schedule_rating": r["rating"], "service": r["service"], "note": note}
report = {
    "bbox_mm": dims, "inside_size_mm": inside, "size_mm": [L, W, H],
    "size_basis": "A-M-199 forming class N+1 rated envelope (A-M-282)",
    "graph_revision": REV,
    "solids": len(solid_val.Solids()), "all_parts_valid": valid,
    "machine": {
        "bench": {"bed_x_mm": [BED_X0, CAP_X], "z_mm": [BED_Z0, BED_Z1],
                  "basis": f"node design bench_mm {BENCH_L:g}; steel bench (duty section 3)"},
        "die_set": {"count": N_DIES, "basis": "tungsten-carbide drawing dies in tool-steel "
                    "casings (duty section 3, DIETER1988 ch. 20/21); consumable buy set; the "
                    "polished-diamond last-pass alternative is the duty alternative row (not drawn)"},
        "capstan": {"od_mm": CAP_D, "axis_z_mm": OUT_Z + 120.0,
                    "basis": "study drum size (hold, WORK_ORDER W12); the capstan hardware "
                    "carries the machine lubricant programme - no wetted stream (duty section 3)"},
        "purchased": "drive group and control cabinet on their bays, drawn as their envelopes "
        "per plan rule 6 (connected_kW 3 is the node rating)",
        "guard": "die-zone and capstan guard rail on 4 posts x 3 tiers (A-MACH: guard drawn)"},
    "standby": {"state": "standby_rated N+1 former of ROLL (A-M-282/A-M-283); energized on "
                f"the roll-stand outage on wire-class lots (outage_d {DS.get('outage_d')}); "
                "design-day rate zero on the graph",
                "basis": "duty section 2 sizing study"},
    "material": {"class": "tungsten-carbide drawing dies in tool-steel casings; steel bench",
                 "ca_mm": 0.0,
                 "basis": "duty section 3 (X-MAT-22); CA 0 mm - dry process, no wetted stream "
                 "(AQS-STD-001 shop rule)"},
    "a_mach": {"guard": "die-zone and capstan guard rail drawn (A-MACH)",
               "anchors": "8 M12 wedge anchors, plinth to slab (fasteners.csv)",
               "purchased": "drive group and control cabinet (connected_kW 3, node design)"},
    "nozzles_drawn": drawn,
    "nozzle_count_schedule": len(schedule),
    "nozzle_idiom": "atmospheric open-bore connections flush at the envelope faces (duty "
    "section 4); the solids row (N1 wire) is drawn at DN15 labeled bore not calculated (W4 "
    "rule); the schedule faces map to compass by the registered layout (params.json layout "
    "block); the schedule rating column (Class 150) is carried verbatim as text; datums are "
    "the schedule placeholders (holds, WORK_ORDER W12)",
    "part_mass_kg": mass, "cadquery": cq.__version__,
}
(HERE / "check.json").write_text(json.dumps(report, indent=2) + "\n")

# ---------------------------------------------------------------- BOM (generated from the model)
import csv  # noqa: E402
rows = [
    ["1", f"Plinth {L:g} x {W:g} x {T_PLINTH:g} (CS, anchor bosses)", 1, "carbon steel",
     mass["plinth"], "make", "dry machine-shop floor service, CA 0 mm (AQS-STD-001 shop rule); "
     "anchors in fasteners.csv"],
    ["2", f"Bench bed {BENCH_L:g} long on 4 legs (node design bench_mm)", 1, "carbon steel",
     mass["bench_bed"] + mass["die_stand"], "make", "duty section 3: steel bench; study "
     "sections (WORK_ORDER W12); N+1 former of ROLL (A-M-282)"],
    ["3", f"Tungsten-carbide drawing die set, {N_DIES} dies in tool-steel casings", 1,
     "carbide + tool steel (consumable set)", mass["die_set"], "buy",
     "duty section 3 (DIETER1988 ch. 20/21); consumable, buy; the diamond last-pass "
     "alternative is the duty alternative row (not drawn)"],
    ["4", f"Capstan drum OD {CAP_D:g} with shaft, gripper carriage, wire-guide sheaves",
     1, "carbon steel", mass["capstan_group"], "make",
     "duty section 3 capstan hardware carries the machine lubricant programme (no wetted "
     "stream); drum size is the study value (hold, WORK_ORDER W12)"],
    ["5", "Drive group on the capstan bay (purchased, envelope and interface)", 1,
     "purchased drive (envelope)", mass["drive_group"], "buy",
     "purchased per plan rule 6; connected_kW 3 is the node rating; standby unit (A-M-282)"],
    ["6", "Control cabinet (purchased, envelope and interface)", 1,
     "purchased cabinet (envelope)", mass["control_cabinet"], "buy",
     "purchased per plan rule 6"],
    ["7", "Die-zone and capstan guard rail, 4 posts x 3 tiers (A-MACH: guard drawn)", 1,
     "CS tube", mass["guard_rail"], "make", "guard over the die zone and rotating capstan; "
     "layout choice (WORK_ORDER W12)"],
    ["8", "Nozzle set per docs-authority/nozzles/DRAW.csv: 3 connections flush at the "
          "envelope faces (1 solids row at DN15, bore not calculated; DN15 drain; DN15 vent "
          "riser)", len(schedule), "carbon steel", mass["nozzles"], "make",
     "schedule tags/faces/heights verbatim; atmospheric per duty section 4"],
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
    [None, "M12 stud + nut (ISO 4014 / ISO 4032)", fasteners.grade_for("CS"), 10,
     "die-stand clamp and capstan bearing blocks",
     "grade rule W5: 8.8 on carbon steel; study torque, confirmed at fabrication"],
])

# ---------------------------------------------------------------- builder-owned params blocks
p = json.loads((HERE / "params.json").read_text())
p.pop("graph", None)
p["envelope"] = {
    "size_mm": [L, W, H],
    "basis": "A-M-199 forming class N+1 rated envelope (A-M-282)",
    "bench": {"x_mm": [BED_X0, CAP_X], "z_mm": [BED_Z0, BED_Z1], "capstan_od_mm": CAP_D},
    "purchased_bays": {"drive_x_mm": [CAP_X - 60.0, L],
                       "cabinet_xy_mm": [40.0, 340.0, 620.0, 780.0]},
}
p["design"] = {
    "machine": "bench wire/rod draw bench, N+1 former of ROLL (node design machine)",
    "mat": "tungsten-carbide drawing dies in tool-steel casings; steel bench (duty section 3)",
    "ca_mm": 0.0,
    "wall_basis": "study bench sections and capstan size; no thickness booked on the node "
                  "(WORK_ORDER W12)",
    "internals": "none drawn (node internals row none)",
    "purchased": f"drive group and control cabinet (connected_kW {DS.get('connected_kW')} node "
                 "design), drawn as their envelopes (plan rule 6); the carbide die set is the "
                 "purchased consumable",
}
p["layout"] = {
    "frame": "origin at the envelope corner; bench centreline y 400; bed x 120..1320 at "
             "z 300..420; die stand on the -X head, capstan head +X with the drive bay "
             "behind it; control cabinet on the -X floor; guard rail over the die zone and "
             "capstan",
    "nozzle_spread": "the schedule gives outlet/bottom/top and heights only; N1 rides the "
                     "take-off guide at +X z 600; N2 drain under the bed centre; N3 vent "
                     "riser on the capstan head to the envelope top; per-tag positions in "
                     "check.nozzles_drawn",
    "hardware_idiom": "connection hardware flush at the envelope faces; nothing protrudes, "
                      "bbox within the node envelope",
}
(HERE / "params.json").write_text(json.dumps(p, indent=1) + "\n")

print(json.dumps({k: report[k] for k in ("bbox_mm", "inside_size_mm", "solids",
                                         "nozzle_count_schedule", "part_mass_kg")}), flush=True)
