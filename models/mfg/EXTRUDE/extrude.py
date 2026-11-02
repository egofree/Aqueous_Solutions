"""EXTRUDE manufacturing model, AQS-PLAN-006 work order (X-MFG lane, tier 7, route hold).

Graph revision AD. Study. Not a PE stamp. Reads params.json only (W2 fields by the
tracker; the envelope, design and layout blocks beside them are builder-owned) and
rebuilds every solid.

Machine: horizontal profile press, N+1 former of ROLL (duty section 2:
standby-zero design-day rate, energized on the roll-stand outage on profile-class
lots, outage_d 2, press_t 50, container_mm 60, connected_kW 15; A-M-282/A-M-283).
A real machine drawn per the duty section 3 construction: H13 extrusion die in a
tool-steel container liner on the press frame, main ram from the rear platen,
billet loader, run-out chute, and the hydraulic power unit and control pedestal
as purchased envelopes per plan rule 6. The H13 die set is the purchased
consumable (buy row). Schedule rows: N1/N2 solids at DN15 (bore not calculated,
W4), N3/N4 DN15 atmospheric tube. Connection hardware draws flush at the
envelope faces: nothing protrudes (A-core 2). No measured rate anywhere.

Placement frame: x along 1500 mm (x 0 = billet-loader tail, x 1500 = run-out
discharge), y along 800 mm, z up, origin at the envelope corner. The schedule
faces map to compass by the registered layout choice (params.json layout block);
heights, bores and ratings are docs-authority/nozzles/EXTRUDE.csv verbatim.
"""
import json, math, pathlib, sys

import cadquery as cq

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
from lib import dn, fasteners, materials          # noqa: E402
from tracker import stl_bbox_mm                    # noqa: E402  (gate-consistent STL reader)

P = json.loads((HERE / "params.json").read_text())
L, W, H = (float(v) for v in P["size_mm"])         # 1500 x 800 x 1500
REV = P["graph_revision"]
UNIT = P["unit_id"]
_g = json.loads((HERE.parents[2] / "flow_graph" / "plant_flow_graph.json").read_text())
DS = (next(n for n in _g["nodes"] if n["unit_id"] == UNIT).get("params") or {}).get("design") or {}

RHO_CS = materials.density("CS")
RHO_TOOL = materials.density("tool_steel")

CONT_D = float(DS.get("container_mm") or 60.0)     # node design container_mm 60 (container bore)
RAM_D = CONT_D + 20.0                              # ram OD, study (hold, W12)
T_PLINTH = 60.0
PLAT_Y = 400.0                                     # press centreline
REAR_X, FRONT_X = 160.0, 640.0                     # rear platen and die-holder front face
BILLET_Z = 160.0                                   # N1 datum
OUT_Z = 600.0                                      # N2 datum


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

# ---------------------------------------------------------------- press frame: rear platen, front platen, tie rods, bed
parts["rear_platen"] = box(REAR_X - 80.0, PLAT_Y - 200.0, 300.0, 120.0, 400.0, 900.0)
parts["front_platen"] = box(FRONT_X, PLAT_Y - 200.0, 300.0, 120.0, 400.0, 900.0)
ties = None
for ty in (240.0, 560.0):
    for tz in (380.0, 1100.0):
        t_ = rod(28.0, (REAR_X, ty, tz), "X", FRONT_X + 120.0 - REAR_X)
        ties = t_ if ties is None else ties.union(t_)
parts["tie_rods"] = ties
parts["bed"] = box(REAR_X - 80.0, 100.0, T_PLINTH, FRONT_X + 200.0 - REAR_X + 80.0, 600.0, 240.0)

# ---------------------------------------------------------------- container (tool-steel liner) + die holder + H13 die
parts["container"] = tube(CONT_D / 2 + 60.0, CONT_D / 2, (FRONT_X - 300.0, PLAT_Y, OUT_Z - CONT_D / 2 - 60.0),
                          "X", 300.0)
parts["die_holder"] = box(FRONT_X - 0.0, PLAT_Y - 140.0, OUT_Z - 140.0, 60.0, 280.0, 280.0)
parts["h13_die"] = box(FRONT_X + 60.0, PLAT_Y - 90.0, OUT_Z - 90.0, 50.0, 180.0, 180.0)

# ---------------------------------------------------------------- main ram (from the rear platen)
parts["main_ram"] = rod(RAM_D / 2, (REAR_X + 40.0, PLAT_Y, OUT_Z - CONT_D / 2), "X", FRONT_X - 300.0 - REAR_X)
parts["ram_nut"] = rod(RAM_D / 2 + 30.0, (REAR_X + 40.0, PLAT_Y, OUT_Z - CONT_D / 2), "X", 60.0)

# ---------------------------------------------------------------- billet loader (-X tail, z 160) + run-out chute (+X discharge, z 600)
parts["billet_loader"] = box(0.0, PLAT_Y - 70.0, BILLET_Z - 40.0, 160.0, 140.0, 80.0)
parts["runout_chute"] = box(FRONT_X + 110.0, PLAT_Y - 90.0, OUT_Z - 30.0, 400.0, 180.0, 30.0)
for sx, sy in ((1160.0, 240.0), (1360.0, 240.0), (1160.0, 560.0), (1360.0, 560.0)):
    parts["runout_chute"] = parts["runout_chute"].union(box(sx - 20.0, sy - 20.0, T_PLINTH, 40.0, 40.0, OUT_Z - 30.0 - T_PLINTH))

# ---------------------------------------------------------------- HPU skid + control pedestal (purchased envelopes)
parts["hpu_skid"] = box(0.0, 620.0, T_PLINTH, 300.0, 160.0, 700.0)
parts["control_pedestal"] = box(680.0, 620.0, T_PLINTH, 240.0, 160.0, 900.0)

# ---------------------------------------------------------------- nozzle hardware (schedule verbatim, flush at the envelope faces)
r15, w15 = dn15()
noz = {}
# N1 solids billet in: -X face at z 160, drawn at DN15 (bore not calculated), riding the loader
noz["N1_billet_in"] = tube(r15, w15, (0.0, PLAT_Y, BILLET_Z), "X", 60.0)
# N2 solids rod/profile out: +X face at z 600, drawn at DN15 (bore not calculated), on the chute nose
noz["N2_profile_out"] = tube(r15, w15, (L - 60.0, PLAT_Y, OUT_Z), "X", 60.0)
noz["N3_drain"] = tube(30.5, r15, (500.0, 400.0, 0.0), "Z", T_PLINTH)
noz["N4_vent_riser"] = tube(r15, w15, (FRONT_X + 60.0, PLAT_Y, 1140.0), "Z", H - 1140.0)
for k, v in noz.items():
    parts[k] = v

# ---------------------------------------------------------------- guard rail around the die zone (A-MACH: guard drawn)
posts = None
for gx, gy in ((760.0, 180.0), (760.0, 620.0)):
    p_ = cq.Workplane("XY", origin=(gx, gy, T_PLINTH)).circle(10.0).extrude(360.0)
    posts = p_ if posts is None else posts.union(p_)
rails = None
for zz in (240.0, 360.0):
    r_ = cq.Workplane("YZ", origin=(760.0, 180.0, zz)).circle(10.0).extrude(440.0)
    rails = r_ if rails is None else rails.union(r_)
for zz in (240.0, 360.0):
    rails = rails.union(box(750.0, 170.0, zz, 20.0, 460.0, 20.0))
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
    "frame": (vol["rear_platen"] + vol["front_platen"] + vol["tie_rods"] + vol["bed"]) * RHO_CS / 1e9,
    "container_group": (vol["container"] + vol["die_holder"] + vol["main_ram"] + vol["ram_nut"]) * RHO_TOOL / 1e9,
    "h13_die": vol["h13_die"] * RHO_TOOL / 1e9,
    "loader_chute": (vol["billet_loader"] + vol["runout_chute"]) * RHO_CS / 1e9,
    "guard_rail": vol["guard_rail"] * RHO_CS / 1e9,
    "hpu_skid": vol["hpu_skid"] * RHO_CS / 1e9,
    "control_pedestal": vol["control_pedestal"] * RHO_CS / 1e9,
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
                "front-platen head and flushes at the envelope top (hold, WORK_ORDER W12)"
    drawn[tag] = {"style": "tube", "dn": r["size"], "face": r["face"], "height_mm": r["height_mm"],
                  "drawn_height_mm": {"N1": float(BILLET_Z), "N2": float(OUT_Z), "N3": 0.0,
                                      "N4": float(H)}[tag],
                  "schedule_rating": r["rating"], "service": r["service"], "note": note}
report = {
    "bbox_mm": dims, "inside_size_mm": inside, "size_mm": [L, W, H],
    "size_basis": "A-M-199 forming class N+1 rated envelope (A-M-282)",
    "graph_revision": REV,
    "solids": len(solid_val.Solids()), "all_parts_valid": valid,
    "machine": {
        "frame": {"platen_x_mm": [REAR_X, FRONT_X + 120.0],
                  "basis": "tie-rod press frame, CS platens (study sections, WORK_ORDER W12)"},
        "container": {"bore_mm": CONT_D, "x_mm": [FRONT_X - 300.0, FRONT_X],
                      "basis": f"node design container_mm {CONT_D:g}; tool-steel liner "
                      "(duty section 3); the H13 extrusion die is the consumable buy set"},
        "ram": {"dia_mm": RAM_D, "basis": "study ram OD (container bore + 20); the hydraulic "
                "cylinder package purchases at fabrication (WORK_ORDER W12)",
                "press_t": f"{DS.get('press_t')} node rating"},
        "purchased": "HPU skid and control pedestal on their bays, drawn as their envelopes "
        "per plan rule 6 (connected_kW 15 is the node rating)",
        "guard": "die-zone guard rail on the operator side (A-MACH: guard drawn)",
        "nitrided_die_land": "the duty section 3 nitrided-die-land first-article item is a "
        "process note, not geometry"},
    "standby": {"state": "standby_rated N+1 former of ROLL (A-M-282/A-M-283); energized on "
                f"the roll-stand outage on profile-class lots (outage_d {DS.get('outage_d')}); "
                "design-day rate zero on the graph",
                "basis": "duty section 2 sizing study"},
    "material": {"class": "H13 extrusion die + tool-steel container liner on the press frame",
                 "ca_mm": 0.0,
                 "basis": "duty section 3 (X-MAT-22, ASM_V1/DIETER1988); CA 0 mm - dry "
                 "hot-work contact, no corrosive stream (AQS-STD-001 shop rule)"},
    "a_mach": {"guard": "die-zone guard rail drawn (A-MACH)",
               "anchors": "8 M16 wedge anchors, plinth to slab (fasteners.csv)",
               "purchased": "HPU skid and control pedestal (connected_kW 15, node design)"},
    "nozzles_drawn": drawn,
    "nozzle_count_schedule": len(schedule),
    "nozzle_idiom": "atmospheric open-bore connections flush at the envelope faces (duty "
    "section 4); the solids rows (N1 billet, N2 rod/profile) are drawn at DN15 labeled bore "
    "not calculated (W4 rule); the schedule faces map to compass by the registered layout "
    "(params.json layout block); the schedule rating column (Class 150) is carried verbatim "
    "as text; datums are the schedule placeholders (holds, WORK_ORDER W12)",
    "part_mass_kg": mass, "cadquery": cq.__version__,
}
(HERE / "check.json").write_text(json.dumps(report, indent=2) + "\n")

# ---------------------------------------------------------------- BOM (generated from the model)
import csv  # noqa: E402
rows = [
    ["1", f"Plinth {L:g} x {W:g} x {T_PLINTH:g} (CS, anchor bosses)", 1, "carbon steel",
     mass["plinth"], "make", "dry forge-floor service, CA 0 mm (AQS-STD-001 shop rule); "
     "anchors in fasteners.csv"],
    ["2", "Press frame: rear and front platens, 4 tie rods, bed", 1, "carbon steel",
     mass["frame"], "make", "study sections (WORK_ORDER W12); N+1 former of ROLL (A-M-282); "
     "press_t 50 node rating"],
    ["3", f"Container group: tool-steel liner bore {CONT_D:g} (node design container_mm) in "
          "its housing, die holder, main ram with nut", 1, "tool steel",
     mass["container_group"], "make", "duty section 3 (DIETER1988); ram OD is the study "
     "value (hold, WORK_ORDER W12); the hydraulic cylinder package purchases at fabrication"],
    ["4", "H13 extrusion die", 1, "H13 tool steel (consumable)", mass["h13_die"], "buy",
     "duty section 3 (ASM_V1); consumable, buy; nitrided die land where galling is measured "
     "(first-article item, duty section 3)"],
    ["5", "Billet loader (-X, z 160) and run-out chute (+X, z 600) on legs", 1, "carbon steel",
     mass["loader_chute"], "make", "schedule N1/N2 interface furniture; study geometry "
     "(WORK_ORDER W12)"],
    ["6", "Die-zone guard rail on the operator side (A-MACH: guard drawn)", 1, "CS tube",
     mass["guard_rail"], "make", "guard over the die zone; layout choice (WORK_ORDER W12)"],
    ["7", "Hydraulic power unit skid on the -X floor bay (purchased, envelope and interface)",
     1, "purchased skid (envelope)", mass["hpu_skid"], "buy",
     "purchased per plan rule 6; connected_kW 15 is the node rating; standby unit (A-M-282)"],
    ["8", "Control pedestal (purchased, envelope and interface)", 1,
     "purchased pedestal (envelope)", mass["control_pedestal"], "buy",
     "purchased per plan rule 6"],
    ["9", "Nozzle set per docs-authority/nozzles/EXTRUDE.csv: 4 connections flush at the "
          "envelope faces (2 solids rows at DN15, bore not calculated; DN15 drain; DN15 vent "
          "riser)", len(schedule), "carbon steel", mass["nozzles"], "make",
     "schedule tags/faces/heights verbatim; atmospheric per duty section 4"],
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
     "tie-rod nuts and die-holder clamp",
     "grade rule W5: 8.8 on carbon steel; study torque, confirmed at fabrication"],
])

# ---------------------------------------------------------------- builder-owned params blocks
p = json.loads((HERE / "params.json").read_text())
p.pop("graph", None)
p["envelope"] = {
    "size_mm": [L, W, H],
    "basis": "A-M-199 forming class N+1 rated envelope (A-M-282)",
    "frame": {"platen_x_mm": [REAR_X, FRONT_X + 120.0], "centreline_y_mm": PLAT_Y},
    "purchased_bays": {"hpu_xy_mm": [0.0, 300.0, 620.0, 780.0],
                       "pedestal_xy_mm": [680.0, 920.0, 620.0, 780.0]},
}
p["design"] = {
    "machine": "horizontal profile press, N+1 former of ROLL (node design machine)",
    "mat": "H13 extrusion die + tool-steel container liner (duty section 3)",
    "ca_mm": 0.0,
    "wall_basis": "study CS frame sections and ram OD; no thickness booked on the node "
                  "(WORK_ORDER W12)",
    "internals": "none drawn (node internals row none)",
    "purchased": f"HPU skid and control pedestal (connected_kW {DS.get('connected_kW')} node "
                 "design), drawn as their envelopes (plan rule 6); the H13 die is the "
                 "purchased consumable",
}
p["layout"] = {
    "frame": "origin at the envelope corner; press centreline y 400; rear platen x 80..200, "
             "front platen x 640..760; container x 340..640 at the z 600 axis; billet loader "
             "-X at z 160, run-out chute +X at z 600; HPU bay -X floor, control pedestal "
             "centre-rear; die-zone guard rail on the operator side",
    "nozzle_spread": "the schedule gives inlet/outlet/bottom/top and heights only; N1 rides "
                     "the billet loader at -X z 160; N2 rides the chute nose at +X z 600; N3 "
                     "drain under the frame; N4 vent riser to the envelope top; per-tag "
                     "positions in check.nozzles_drawn",
    "hardware_idiom": "connection hardware flush at the envelope faces; nothing protrudes, "
                      "bbox within the node envelope",
}
(HERE / "params.json").write_text(json.dumps(p, indent=1) + "\n")

print(json.dumps({k: report[k] for k in ("bbox_mm", "inside_size_mm", "solids",
                                         "nozzle_count_schedule", "part_mass_kg")}), flush=True)
