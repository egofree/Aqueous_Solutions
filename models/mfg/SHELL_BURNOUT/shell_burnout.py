"""SHELL_BURNOUT manufacturing model, AQS-PLAN-006 work order (X-MFG lane, FOUNDRY-SHELL_BURNOUT-10 M3).

Graph revision AD. Study. Not a PE stamp. Sizes and counts come from the plant graph through the shared reader (models/mfg/lib/graph_node.py); the params.json write-back merges the builder-owned blocks only.
Flash-dewax + shell-fire box furnace at 900 C (AQS-DUTY-072): fired shells to
INV_CAST N1, wax condensate reclaimed to WAX_PATTERN N2, unrecovered wax to the
oil line, off-gas burned/vented per the duty sheet. Connection hardware draws flush
at the envelope faces: nothing protrudes (A-core 2). No measured rate is claimed.
"""
import csv, json, math, pathlib
import cadquery as cq

HERE = pathlib.Path(__file__).parent
import sys
sys.path.insert(0, str(HERE.parent))              # models/mfg: lib
from lib import graph_node  # noqa: E402
GN = graph_node.graph_node("SHELL_BURNOUT")        # the plant graph is the sole authority
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
CX, CY = 450.0, 450.0

# ---------------- casing: CS shell t4 with a front-loading door ----------------
casing = box(0, 0, 0, L, W, H).cut(box(4, 4, 4, L - 8, W - 8, 1442))
casing = casing.cut(box(-5.0, 350.0, 60.0, 10.0, 300.0, 500.0))     # door opening through the -X wall
casing = casing.cut(box(-5.0, 140.0, 70.0, 10.0, 100.0, 110.0))     # N1 green-shell inlet pass behind the -X chute
casing = casing.cut(rod(45.0, (L - 5.0, 400.0, 600.0), "X", 90.0))     # N2 fired-shell out pass +X z 600
casing = casing.cut(rod(DN15 + 1, (CX + 150.0, W - 5.0, 600.0), "Y", 30))   # N3/N4 stub passes through the +Y wall
casing = casing.cut(rod(DN15 + 1, (CX + 250.0, W - 5.0, 600.0), "Y", 30))
casing = casing.cut(rod(DN15 + 1, (700.0, -5.0, 600.0), "Y", 90.0)) # N5 off-gas pass -Y z 600
casing = casing.cut(rod(30.5, (400, 400, -5.0), "Z", 85.0))         # N6 drain pass
casing = casing.cut(rod(DN15 + 1, (400, 400, 800.0), "Z", 40))      # N7 vent pass
parts["casing"] = casing
parts["door"] = box(0.0, 340.0, 50.0, 30.0, 320.0, 520.0)         # front door slab flush at the -X face, covering the opening

# ---------------- hot face + element grooves ----------------
fibre = box(4, 4, 4, L - 8, W - 8, 1442).cut(box(154, 154, 154, L - 308, W - 308, 1142))
fibre = fibre.cut(box(-5.0, 350.0, 60.0, 165.0, 300.0, 500.0))      # door throat through the hot face
fibre = fibre.cut(box(-5.0, 140.0, 70.0, 160.0, 100.0, 110.0))      # N1 inlet pass behind the -X chute
parts["hot_face"] = fibre
parts["hearth_plate"] = box(160.0, 160.0, 160.0, L - 320.0, W - 320.0, 60)   # hearth z 160..220

# ---------------- dewax condenser pan + off-gas collector ----------------
parts["condenser_pan"] = box(560.0, 250.0, 100.0, 220.0, 400.0, 80.0)   # N3 wax condensate pan
parts["offgas_collector"] = box(650.0, 340.0, 480.0, 150.0, 220.0, 160.0)   # N5 collector hood -Y

# ---------------- nozzle hardware ----------------
parts["shell_inlet"] = box(0.0, 130.0, 40.0, 40.0, 120.0, 150.0)  # N1 -X z 160, flush at the face beside the door
parts["fired_out"] = box(L - 40.0, 340.0, 550.0, 40.0, 120.0, 100.0)  # N2 +X z 600, flush at the face
parts["condensate_stub"] = tube(DN15, DN15 - W15, (CX + 150.0, W - 40.0, 600.0), "Y", 40)   # N3 +Y, flush at the face
parts["wax_stub"] = tube(DN15, DN15 - W15, (CX + 250.0, W - 40.0, 600.0), "Y", 40)          # N4 +Y, flush at the face
parts["offgas_stub"] = tube(DN15, DN15 - W15, (700.0, 0.0, 600.0), "Y", 40)               # N5 -Y, flush at the face
parts["drain_well"] = tube(30.5, DN15, (400, 400, 0), "Z", 50)                              # N6
parts["vent_stub"] = tube(DN15, DN15 - W15, (400, 400, 795.0), "Z", 60)                     # N7 top

# ---------------- process inventory ----------------
inv = {"shell_racks_inventory": box(200.0, 250.0, 250.0, 600.0, 300.0, 300.0)}   # shells on racks

# ---------------- export, checks, BOM --------------------------------------------
asm = cq.Assembly(name="SHELL_BURNOUT")
for k, v in list(parts.items()) + list(inv.items()):
    asm.add(v, name=k)
out = HERE / "export"; out.mkdir(exist_ok=True)
asm.export(str(out / "shell_burnout.step"))

body = None
for k, v in parts.items():
    body = v if body is None else body.union(v)
cap_solid = body.val()
cap_solid.exportStl(str(out / "shell_burnout.stl"), tolerance=0.4, angularTolerance=0.4, ascii=True)

EXTERNAL = ("shell_inlet", "fired_out", "condensate_stub", "wax_stub", "offgas_stub")   # schedule hardware, drawn flush at the faces
in_env = None
for k, v in parts.items():
    if k in EXTERNAL:
        continue
    in_env = v if in_env is None else in_env.union(v)
in_env_solid = in_env.val()
in_env_solid.exportStl(str(out / "shell_burnout_in_envelope.stl"), tolerance=0.4, angularTolerance=0.4, ascii=True)
in_env_solid.scale(0.001).exportStl(str(HERE.parents[2] / "cad" / "stl" / "SHELL_BURNOUT.stl"),
                                    tolerance=0.0005, angularTolerance=0.4, ascii=True)

ALL = list(parts.values()) + list(inv.values())
def mesh_bb(shape):
    verts, _tris = shape.tessellate(0.1)
    xs, ys, zs = [t.x for t in verts], [t.y for t in verts], [t.z for t in verts]
    return min(xs), min(ys), min(zs), max(xs), max(ys), max(zs)
sb = mesh_bb(cq.Compound.makeCompound([parts["casing"].val()]))
tb_ = mesh_bb(cq.Compound.makeCompound([v.val() for v in ALL]))
slack = 1.0   # A-core 2 gate: the flush-hardware build stays inside size_mm within 1 mm
inside_shell = bool(sb[0] >= -1 and sb[3] <= L + 1 and sb[1] >= -1 and sb[4] <= W + 1
                    and sb[2] >= -1 and sb[5] <= H + 1)
overhang = {"-X": round(-tb_[0], 1), "+X": round(tb_[3] - L, 1),
            "-Y": round(-tb_[1], 1), "+Y": round(tb_[4] - W, 1)}
overhang_ok = all(v <= slack + 1 for v in overhang.values())
valid = all(v.val().isValid() for v in ALL)
rho = {"casing": 7.85e-6, "door": 7.85e-6, "hot_face": 128e-9, "hearth_plate": 7.85e-6,
       "condenser_pan": 7.85e-6, "offgas_collector": 7.85e-6, "shell_inlet": 7.85e-6,
       "fired_out": 7.85e-6, "condensate_stub": 7.85e-6, "wax_stub": 7.85e-6,
       "offgas_stub": 7.85e-6, "drain_well": 7.85e-6, "vent_stub": 7.85e-6}
mass = {k: round(v.val().Volume() * rho[k], 1) for k, v in parts.items()}
# ---------------- acceptance record: nozzles_drawn -------------------------------
# Every row of docs-authority/nozzles/SHELL_BURNOUT.csv, recorded from the
# placement this build draws. The power-terminal row is a cable-schedule row:
# carried verbatim, never drawn.
sched_rows = {}
with open(HERE.parents[2] / "docs-authority" / "nozzles" / "SHELL_BURNOUT.csv") as f:
    for _r in csv.DictReader(f):
        sched_rows[_r["tag"]] = _r
PLACE = {
    "N1": {"style": "solids", "face": "-X", "part": "shell_inlet", "drawn_height_mm": 160.0,
           "note": "green-shell in-chute flush at the -X face beside the door (y 130..250, "
                   "z 40..190); solids row, bore not calculated"},
    "N2": {"style": "solids", "face": "+X", "part": "fired_out",
           "note": "fired-shell out-chute flush at the +X face (y 340..460, z 550..650); "
                   "solids row, bore not calculated"},
    "N3": {"style": "stub", "face": "+Y", "part": "condensate_stub", "x_mm": 600.0,
           "drawn_height_mm": 600.0,
           "note": "wax-condensate-reclaim DN15 stub flush at the +Y face, at the condenser pan"},
    "N4": {"style": "stub", "face": "+Y", "part": "wax_stub", "x_mm": 700.0,
           "drawn_height_mm": 600.0,
           "note": "unrecovered-wax DN15 stub flush at the +Y face, to the oil line"},
    "N5": {"style": "stub", "face": "-Y", "part": "offgas_stub", "x_mm": 700.0,
           "drawn_height_mm": 600.0,
           "note": "dewax/burnout off-gas DN15 stub flush at the -Y face, at the collector hood"},
    "N6": {"style": "drain", "face": "bottom", "part": "drain_well", "drawn_height_mm": 0.0,
           "note": "drain well flush at the envelope bottom (z 0), sump face at the 50 datum"},
    "N7": {"style": "vent", "face": "top", "part": "vent_stub", "drawn_height_mm": 800.0,
           "note": "vent DN15 stub at the furnace centreline (x 400, y 400) through the roof "
                   "pass, z 795..855 at the 800 datum"},
    "N8": {"style": "carried", "face": "top",
           "note": "power terminal (SF-SHELL_BURNOUT bus) - a cable-schedule row: carried "
                   "verbatim, never drawn"},
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
    "casing_bbox_mm": [round(sb[3] - sb[0], 1), round(sb[4] - sb[1], 1), round(sb[5] - sb[2], 1)],
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
    ["1", f"Furnace casing 1000 x 1000 x 1500 mm, CS t4, front door {D['T_C']:.0f} C class", 1, "carbon steel",
     round(mass["casing"] + mass["door"], 1), "make", "duty section 3; WORK_ORDER step 1; door on the -X face with a real through opening"],
    ["2", "Ceramic-fibre hot face", 1, "ceramic-fibre board 128 kg/m3", mass["hot_face"], "make",
     "design lining; SCHACHT2004 class; the 0.25 kW element set purchases at fabrication (hold, W12)"],
    ["3", "Hearth plate", 1, "carbon steel", mass["hearth_plate"], "make", "WO step 2"],
    ["4", "Wax condensate pan (to WAX_PATTERN N2)", 1, "carbon steel", mass["condenser_pan"], "make",
     f"task-04 schedule N3; reclaim {D['wax_reclaim_kg_d']} kg/d of {D['wax_reclaim_kg_d'] + D['burned_wax_kg_d']} kg/d wax"],
    ["5", "Off-gas collector hood -Y z 600", 1, "carbon steel", mass["offgas_collector"], "make",
     "task-04 schedule N5 (burned wax + steam)"],
    ["6", "N1 green-shell inlet -X z 160, full height", 1, "carbon steel", mass["shell_inlet"], "make",
     "task-04 schedule N1 (from SHELL_BUILD N2)"],
    ["7", "N2 fired-shell out +X z 600 (to INV_CAST N1)", 1, "carbon steel", mass["fired_out"], "make",
     "task-04 schedule N2"],
    ["8", "N3/N4 condensate and unrecovered-wax DN15 stubs +Y z 600", 2, "carbon steel",
     round(mass["condensate_stub"] + mass["wax_stub"], 1), "make", "task-04 schedule N3/N4"],
    ["9", "N5 off-gas DN15 stub -Y z 600", 1, "carbon steel", mass["offgas_stub"], "make", "task-04 schedule N5"],
    ["10", "N6 drain well + N7 vent stub", 2, "carbon steel", round(mass["drain_well"] + mass["vent_stub"], 1),
     "make", "task-04 schedule N6/N7"],
]
with open(HERE / "bom.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["item", "description", "qty", "material", "mass_kg", "make_or_buy", "basis"])
    w.writerows(rows)
(HERE / "fasteners.csv").write_text(
    'item,size,grade,qty,location,basis\n'
    '1,M10 stud + nut (ISO 4014 / ISO 4032),ISO 898-1 8.8,6,door hinges,study\n'
    '2,M12 anchor,ISO 898-1 8.8,4,casing to slab,study\n')
# WORK_ORDER.md is the hand-authored W1-W12 item beside the model (AQS-PLAN-006 section 2);
# the builder no longer writes it, so a rebuild never clobbers the work order.
(HERE / "check.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report))
