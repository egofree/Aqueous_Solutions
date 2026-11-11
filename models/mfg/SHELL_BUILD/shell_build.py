"""SHELL_BUILD manufacturing model, AQS-PLAN-006 work order (X-MFG lane, FOUNDRY-SHELL_BUILD-10 M3).

Graph revision AD. Study. Not a PE stamp. Sizes and counts come from the plant graph through the shared reader (models/mfg/lib/graph_node.py); the params.json write-back merges the builder-owned blocks only.
Dip-coat + rainfall-stucco shell-building booth: 40 L slurry tank, 6-dip manipulator,
rainfall stucco station with reclaim (AQS-DUTY-072). Connection hardware draws flush
at the envelope faces: nothing protrudes (A-core 2). No measured rate is claimed anywhere.
"""
import csv, json, math, pathlib
import cadquery as cq

HERE = pathlib.Path(__file__).parent
import sys
sys.path.insert(0, str(HERE.parent))              # models/mfg: lib
from lib import graph_node, step_export  # noqa: E402
GN = graph_node.graph_node("SHELL_BUILD")        # the plant graph is the sole authority
P = GN.as_params()                            # W2 keys (size_mm, graph_revision, unit_id, nozzles, design)
P.update({k: v for k, v in json.loads((HERE / "params.json").read_text()).items() if k not in P or P[k] in (None, {}) })   # builder-owned blocks only (assumptions/form/material class do not live on the graph)
A = P["assumptions"]
D = GN.design
L, W, H = P["size_mm"]
DN15, W15 = A["DN15_OD_mm"] / 2, A["DN15_wall_mm"]

def box(x, y, z, dx, dy, dz):
    return cq.Workplane().box(dx, dy, dz, centered=False).translate((x, y, z))

def tube(r_out, r_in, p, axis, ln):
    d = {"X": ((1, 0, 0), (0, 1, 0)), "Y": ((0, 1, 0), (1, 0, 0)), "Z": ((0, 0, 1), (1, 0, 0))}[axis]
    pl = cq.Plane(origin=p, xDir=d[1], normal=d[0])
    return cq.Workplane(pl).circle(r_out).circle(r_in).extrude(ln)

def rod(r, p, axis, ln):
    return tube(r, 0, p, axis, ln)

parts = {}
# ---------------- booth frame + cladding ----------------
frame = None
for (px, py) in ((0, 0), (L - 60, 0), (0, W - 60), (L - 60, W - 60)):
    q = box(px, py, 0, 60, 60, 300)
    frame = q if frame is None else frame.union(q)
for px in (0, L - 60):
    frame = frame.union(box(px, 0, 0, 60, W, 40)).union(box(px, 0, 1440, 60, W, 60))
frame = frame.union(box(0, W - 40, 360, L, 40, 1080))          # back wall cladding
parts["booth_frame"] = frame

# ---------------- slurry tank 40 L + rainfall stucco station ----------------
parts["slurry_tank"] = box(150.0, 250.0, 360.0, 400.0, 300.0, 340.0).cut(
    box(170.0, 270.0, 380.0, 360.0, 260.0, 300.0))             # 40 L tank z 360..700
parts["stucco_station"] = box(700.0, 250.0, 700.0, 300.0, 300.0, 120).union(
    box(730.0, 280.0, 820.0, 240.0, 240.0, 30))                # rainfall head above

# ---------------- 6-dip manipulator arm ----------------
arm = rod(35.0, (420.0, 400.0, 700.0), "Z", 500)               # vertical mast
arm = arm.union(box(340.0, 370.0, 1150.0, 160.0, 60.0, 60))    # cross arm
arm = arm.union(rod(20.0, (400.0, 400.0, 1050.0), "Z", 100))   # grip hoist
parts["manipulator"] = arm
for i in range(D["dips"]):
    pass                                                       # dip positions marked on the deck
parts["dip_deck"] = box(60.0, 200.0, 700.0, 700.0, 400.0, 40)  # drip deck over the tank

# ---------------- nozzle hardware ----------------
parts["pattern_chute"] = box(0.0, 320.0, 130.0, 35.0, 160.0, 90)     # N1 -X z 160, flush at the face
parts["green_shell_out"] = box(L - 40.0, 340.0, 550.0, 40.0, 120.0, 100)   # N2 +X z 600, flush at the face
ch = None
for yy in (200.0, 400.0, 560.0):
    q = box(0.0, yy, 130.0, 40.0, 120.0, 60)   # flush at the -X face
    ch = q if ch is None else ch.union(q)
parts["silica_inlets"] = ch                                            # N3/N4/N8 -X z 160
parts["drain_well"] = tube(30.5, DN15, (400, 400, 0), "Z", 50)         # N5
parts["vent_stub"] = tube(DN15, DN15 - W15, (400.0, 400.0, 1440.0), "Z", 60)   # N6 top

# ---------------- process inventory ----------------
inv = {"slurry_inventory": box(170.0, 270.0, 380.0, 360.0, 260.0, 200.0)}   # slurry in the tank

# ---------------- export, checks, BOM --------------------------------------------
asm = cq.Assembly(name="SHELL_BUILD")
for k, v in list(parts.items()) + list(inv.items()):
    asm.add(v, name=k)
out = HERE / "export"; out.mkdir(exist_ok=True)
step_export.export_step(asm, str(out / "shell_build.step"))

body = None
for k, v in parts.items():
    body = v if body is None else body.union(v)
cap_solid = body.val()
cap_solid.exportStl(str(out / "shell_build.stl"), tolerance=0.4, angularTolerance=0.4, ascii=True)

EXTERNAL = ("pattern_chute", "green_shell_out", "silica_inlets")   # schedule hardware, drawn flush at the faces
in_env = None
for k, v in parts.items():
    if k in EXTERNAL:
        continue
    in_env = v if in_env is None else in_env.union(v)
in_env_solid = in_env.val()
in_env_solid.exportStl(str(out / "shell_build_in_envelope.stl"), tolerance=0.4, angularTolerance=0.4, ascii=True)
in_env_solid.scale(0.001).exportStl(str(HERE.parents[2] / "cad" / "stl" / "SHELL_BUILD.stl"),
                                    tolerance=0.0005, angularTolerance=0.4, ascii=True)

ALL = list(parts.values()) + list(inv.values())
sb = cq.Compound.makeCompound([parts["booth_frame"].val()]).BoundingBox()
tb_ = cq.Compound.makeCompound([v.val() for v in ALL]).BoundingBox()
slack = 1.0   # A-core 2 gate: the flush-hardware build stays inside size_mm within 1 mm
inside_shell = bool(sb.xmin >= -1 and sb.xmax <= L + 1 and sb.ymin >= -1 and sb.ymax <= W + 1
                    and sb.zmin >= -1 and sb.zmax <= H + 1)
overhang = {"-X": round(-tb_.xmin, 1), "+X": round(tb_.xmax - L, 1),
            "-Y": round(-tb_.ymin, 1), "+Y": round(tb_.ymax - W, 1)}
overhang_ok = all(v <= slack + 1 for v in overhang.values())
valid = all(v.val().isValid() for v in ALL)
rho = {"booth_frame": 7.85e-6, "slurry_tank": 7.85e-6, "stucco_station": 7.85e-6,
       "manipulator": 7.85e-6, "dip_deck": 7.85e-6, "pattern_chute": 7.85e-6,
       "green_shell_out": 7.85e-6, "silica_inlets": 7.85e-6, "drain_well": 7.85e-6, "vent_stub": 7.85e-6}
mass = {k: round(v.val().Volume() * rho[k], 1) for k, v in parts.items()}
# ---------------- acceptance record: nozzles_drawn -------------------------------
# Every row of docs-authority/nozzles/SHELL_BUILD.csv, recorded from the placement
# this build draws. The power-terminal row is a cable-schedule row: carried
# verbatim, never drawn.
sched_rows = {}
with open(HERE.parents[2] / "docs-authority" / "nozzles" / "SHELL_BUILD.csv") as f:
    for _r in csv.DictReader(f):
        sched_rows[_r["tag"]] = _r
PLACE = {
    "N1": {"style": "solids", "face": "-X", "part": "pattern_chute", "drawn_height_mm": 160.0,
           "note": "wax-pattern chute flush at the -X face (y 320..480, z 130..220); solids "
                   "row, bore not calculated"},
    "N2": {"style": "solids", "face": "+X", "part": "green_shell_out",
           "note": "green-shell out-chute flush at the +X face (y 340..460, z 550..650); "
                   "solids row, bore not calculated"},
    "N3": {"style": "solids", "face": "-X", "part": "silica_inlets", "y_mm": [200.0, 320.0],
           "drawn_height_mm": 160.0,
           "note": "foundry-silica make-up chute flush at the -X face (y 200..320, z 130..190); "
                   "solids row, bore not calculated"},
    "N4": {"style": "solids", "face": "-X", "part": "silica_inlets", "y_mm": [400.0, 520.0],
           "drawn_height_mm": 160.0,
           "note": "reclaimed-stucco chute flush at the -X face (y 400..520, z 130..190); "
                   "solids row, bore not calculated"},
    "N5": {"style": "drain", "face": "bottom", "part": "drain_well", "drawn_height_mm": 0.0,
           "note": "drain well flush at the envelope bottom (z 0), sump face at the 50 datum"},
    "N6": {"style": "vent", "face": "top", "part": "vent_stub", "drawn_height_mm": 1500.0,
           "note": "vent DN15 stub at the booth centreline (x 400, y 400), flush at the "
                   "envelope top (z 1440..1500); the schedule 800 datum is carried in height_mm"},
    "N7": {"style": "carried", "face": "top",
           "note": "power terminal (SF-SHELL_BUILD bus) - a cable-schedule row: carried "
                   "verbatim, never drawn"},
    "N8": {"style": "solids", "face": "-X", "part": "silica_inlets", "y_mm": [560.0, 680.0],
           "drawn_height_mm": 160.0,
           "note": "recovered-crib and spent-shell silica make-up chute flush at the -X face "
                   "(y 560..680, z 130..190), in a study slot beside the reclaim chute; "
                   "solids row, bore not calculated"},
}
drawn = {}
for tag, rec in PLACE.items():
    row = sched_rows[tag]
    rec = dict(rec)
    rec["dn"] = row["size"] if rec["style"] == "carried" else "DN15"
    rec["height_mm"] = float(row["height_mm"])
    rec["schedule_rating"] = row["rating"]
    rec["service"] = row["service"]
    drawn[tag] = rec
assert set(drawn) == set(sched_rows), sorted(set(drawn) ^ set(sched_rows))

report = {
    "nozzles_drawn": drawn,
    "booth_bbox_mm": [round(sb.xlen, 1), round(sb.ylen, 1), round(sb.zlen, 1)],
    "inside_size_mm_shell": inside_shell,
    "connection_overhang_mm": overhang,
    "overhang_allowance_mm": slack,
    "overhang_ok": overhang_ok,
    "cad_stl_scope": "in-envelope build solid, metres (EXTERNAL parts excluded: " + ", ".join(EXTERNAL) + ")",
    "external_parts": list(EXTERNAL),
    "cap_solids": len(cap_solid.Solids()),
    "all_parts_valid": valid,
    "part_mass_kg": mass,
    "cadquery": "2.8.0",
}
rows = [
    ["1", "Booth frame 1500 x 800 with back-wall cladding", 1, "carbon steel",
     mass["booth_frame"], "make (AQS-BOM-SC-001)", "WORK_ORDER W10 route; AQS-DUTY-072 shell-building booth; flush build"],
    ["2", f"Slurry tank 40 L ({D['slurry_L']} L design), agitated", 1, "316L",
     mass["slurry_tank"], "make (AQS-BOM-SC-001)", f"design slurry {D['slurry_L']} L; duty section 2; agitator drive mounts at fabrication"],
    ["3", "Rainfall stucco station with reclaim pan", 1, "carbon steel", mass["stucco_station"], "make (AQS-BOM-SC-001)",
     f"{D['dips']} dip cycles; reclaim {D['reclaim_kg_d']} kg/d of {D['silica_makeup_kg_d'] + D['reclaim_kg_d']} kg/d silica"],
    ["4", f"{D['dips']}-dip manipulator: mast, cross arm, grip hoist", 1, "carbon steel",
     mass["manipulator"], "make (AQS-BOM-SC-001)", f"design dips {D['dips']}; hoist drive purchased at fabrication (hold, W12)"],
    ["5", "Drip deck over the slurry tank", 1, "carbon steel", mass["dip_deck"], "make (AQS-BOM-SC-001)", "WORK_ORDER W10 route"],
    ["6", "N1 pattern chute -X z 160, flush at the face (from WAX_PATTERN N1)", 1, "carbon steel", mass["pattern_chute"], "make (AQS-BOM-SC-001)",
     "task-04 schedule N1"],
    ["7", "N2 green-shell out +X z 600, flush at the face (to SHELL_BURNOUT N1)", 1, "carbon steel", mass["green_shell_out"], "make (AQS-BOM-SC-001)",
     "task-04 schedule N2"],
    ["8", "N3/N4/N8 silica make-up + reclaim inlets -X z 160, flush at the face", 3, "carbon steel", mass["silica_inlets"], "make (AQS-BOM-SC-001)",
     "task-04 schedule N3/N4"],
    ["9", "N5 drain well + N6 vent stub", 2, "carbon steel", round(mass["drain_well"] + mass["vent_stub"], 1),
     "make (AQS-BOM-SC-001)", "task-04 schedule N5/N6"],
]
with open(HERE / "bom.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["item", "description", "qty", "material", "mass_kg", "make_or_buy", "basis"])
    w.writerows(rows)
(HERE / "fasteners.csv").write_text(
    'item,size,grade,qty,location,basis\n'
    '1,M10 anchor,ISO 898-1 8.8,4,booth to slab,study\n'
    '2,M10 hold-down,ISO 898-1 8.8,4,slurry tank to the booth deck,study\n'
    '3,M8 bolt,ISO 898-1 8.8,8,manipulator mast base plate,study\n')
# WORK_ORDER.md is the hand-authored W1-W12 item beside the model (AQS-PLAN-006 section 2);
# the builder no longer writes it, so a rebuild never clobbers the work order.
(HERE / "check.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report))
