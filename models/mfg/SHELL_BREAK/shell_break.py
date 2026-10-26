"""SHELL_BREAK manufacturing model, AQS-PLAN-006 work order (X-MFG lane, FOUNDRY-SHELL_BREAK-10 M3).

Graph revision AC. Study. Not a PE stamp. Reads params.json only.
Vibratory shell knock-out station with reclaim sieve (AQS-DUTY-072): the cast
tree arrives from INV_CAST N4, the vibratory table breaks the shell, the sieve
splits reclaim stucco/flour from the spent silica export. No measured rate is
claimed anywhere.
"""
import csv, json, math, pathlib
import cadquery as cq

HERE = pathlib.Path(__file__).parent
P = json.loads((HERE / "params.json").read_text())
A = P["assumptions"]
D = P["design"]
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
# ---------------- frame + vibratory table ----------------
frame = box(0, 0, 0, L, W, 40)
for (px, py) in ((0, 0), (L - 60, 0), (0, W - 60), (L - 60, W - 60)):
    frame = frame.union(box(px, py, 40, 60, 60, 560))
frame = frame.union(box(70, 0, 580, 830.0, W, 30))               # feed deck: inset from the mast corner seam
frame = frame.union(box(80, 80, 40, 60, 60, 1460))              # enclosure service mast (corner clear of the corner-post seam)
parts["frame"] = frame
parts["vib_table"] = box(100.0, 200.0, 610.0, 700.0, 400.0, 60)  # vibratory table z 610..670
parts["vib_drive"] = box(120.0, 220.0, 500.0, 120.0, 120.0, 110)  # drive unit under the table
# ---------------- reclaim sieve (inclined) + reclaim pan ----------------
sieve = box(860.0, 200.0, 700.0, 30.0, 400.0, 30).union(box(1230.0, 200.0, 700.0, 30.0, 400.0, 30))
for i in range(6):                                                   # mesh cross-bars (open top: no internal void)
    sieve = sieve.union(box(890.0 + i * 60.0, 200.0, 700.0, 24.0, 400.0, 26.0))
parts["sieve"] = sieve
parts["reclaim_pan"] = box(880.0, 220.0, 580.0, 360.0, 360.0, 40)
# ---------------- enclosure hood over the table ----------------
parts["enclosure"] = box(80.0, 180.0, 700.0, 860.0, 440.0, 250.0).cut(
    box(100.0, 200.0, 670.0, 820.0, 400.0, 280.0))
# ---------------- nozzle hardware ----------------
parts["cast_inlet"] = box(-30.0, 340.0, 40.0, 40.0, 120.0, 130.0)   # N1 -X z 160, full height
parts["casting_out"] = box(1460.0, 200.0, 600.0, 40.0, 400.0, 100)  # N2 +X z 600
parts["spent_out"] = box(1400.0, 60.0, 600.0, 40.0, 200.0, 100)     # N3 +X z 600 (spent silica)
parts["reclaim_out"] = box(900.0, W - 30.0, 550.0, 200.0, 40.0, 100)  # N4 +Y z 600
parts["silica_out"] = box(1300.0, W - 30.0, 550.0, 120.0, 40.0, 100)  # N5 +Y z 600
parts["drain_well"] = tube(30.5, DN15, (400, 400, 0), "Z", 50)        # N6
parts["vent_stub"] = tube(DN15, DN15 - W15, (110.0, 110.0, 1460.0), "Z", 40)   # N7 on the mast at the z 1500 datum

# ---------------- process inventory ----------------
inv = {"cast_tree_inventory": box(150.0, 320.0, 670.0, 400.0, 160.0, 60.0)}   # cast tree on the table

# ---------------- export, checks, BOM --------------------------------------------
asm = cq.Assembly(name="SHELL_BREAK")
for k, v in list(parts.items()) + list(inv.items()):
    asm.add(v, name=k)
out = HERE / "export"; out.mkdir(exist_ok=True)
asm.export(str(out / "shell_break.step"))

body = None
for k, v in parts.items():
    body = v if body is None else body.union(v)
cap_solid = body.val()
cap_solid.exportStl(str(out / "shell_break.stl"), tolerance=0.4, angularTolerance=0.4, ascii=True)

EXTERNAL = ("cast_inlet", "casting_out", "spent_out", "reclaim_out", "silica_out")
in_env = None
for k, v in parts.items():
    if k in EXTERNAL:
        continue
    in_env = v if in_env is None else in_env.union(v)
in_env_solid = in_env.val()
in_env_solid.exportStl(str(out / "shell_break_in_envelope.stl"), tolerance=0.4, angularTolerance=0.4, ascii=True)
in_env_solid.scale(0.001).exportStl(str(HERE.parents[2] / "cad" / "stl" / "SHELL_BREAK.stl"),
                                    tolerance=0.0005, angularTolerance=0.4, ascii=True)

ALL = list(parts.values()) + list(inv.values())
sb = cq.Compound.makeCompound([parts["frame"].val()]).BoundingBox()
tb_ = cq.Compound.makeCompound([v.val() for v in ALL]).BoundingBox()
slack = 50.0
inside_shell = bool(sb.xmin >= -1 and sb.xmax <= L + 1 and sb.ymin >= -1 and sb.ymax <= W + 1
                    and sb.zmin >= -1 and sb.zmax <= H + 1)
overhang = {"-X": round(-tb_.xmin, 1), "+X": round(tb_.xmax - L, 1),
            "-Y": round(-tb_.ymin, 1), "+Y": round(tb_.ymax - W, 1)}
overhang_ok = all(v <= slack + 1 for v in overhang.values())
valid = all(v.val().isValid() for v in ALL)
rho = {"frame": 7.85e-6, "vib_table": 7.85e-6, "vib_drive": 7.85e-6, "sieve": 7.85e-6,
       "reclaim_pan": 7.85e-6, "enclosure": 7.85e-6, "cast_inlet": 7.85e-6, "casting_out": 7.85e-6,
       "spent_out": 7.85e-6, "reclaim_out": 7.85e-6, "silica_out": 7.85e-6,
       "drain_well": 7.85e-6, "vent_stub": 7.85e-6}
mass = {k: round(v.val().Volume() * rho[k], 1) for k, v in parts.items()}
report = {
    "frame_bbox_mm": [round(sb.xlen, 1), round(sb.ylen, 1), round(sb.zlen, 1)],
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
    ["1", f"Frame: base {L} x {W} x 40, four posts, feed deck -X", 1, "carbon steel",
     mass["frame"], "make", "WORK_ORDER step 1; AQS-DUTY-072 knock-out station"],
    ["2", f"Vibratory table 700 x 400 x 60 with the {D['table_kW']} kW drive", 1, "carbon steel",
     round(mass["vib_table"] + mass["vib_drive"], 1), "make", f"design table {D['table_kW']} kW"],
    ["3", "Reclaim sieve (inclined) with mesh window + reclaim pan", 1, "carbon steel",
     round(mass["sieve"] + mass["reclaim_pan"], 1), "make",
     f"reclaim {D['reclaim_kg_d']} kg/d of {D['spent_shell_kg_d']} kg/d spent shell"],
    ["4", "Station enclosure hood", 1, "carbon steel", mass["enclosure"], "make", "WO step 4; dust control"],
    ["5", "N1 cast-tree inlet -X z 160 (from INV_CAST N4)", 1, "carbon steel", mass["cast_inlet"], "make",
     "task-04 schedule N1"],
    ["6", "N2 investment castings +X z 600; N3 spent silica +X z 600; N4 reclaim +Y z 600; N5 silica return +Y z 600",
     4, "carbon steel", round(mass["casting_out"] + mass["spent_out"] + mass["reclaim_out"] + mass["silica_out"], 1),
     "make", "task-04 schedule N2..N5"],
    ["7", "N6 drain well + N7 vent stub", 2, "carbon steel", round(mass["drain_well"] + mass["vent_stub"], 1),
     "make", "task-04 schedule N6/N7"],
]
with open(HERE / "bom.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["item", "description", "qty", "material", "mass_kg", "make_or_buy", "basis"])
    w.writerows(rows)
(HERE / "fasteners.csv").write_text(
    'item,size,grade,qty,location,basis\n'
    '1,M10 anchor,ISO 898-1 8.8,4,frame to slab,study\n')
(HERE / "WORK_ORDER.md").write_text(
    "# Work order SHELL_BREAK\n\nAuthority: AQS-DUTY-072 (X-MFG lane). LIVE unit - vibratory knock-out.\n\n"
    "1. Fabricate the frame and feed deck; set on anchors.\n"
    "2. Fit the vibratory table with the drive; prove the isolation mounts.\n"
    "3. Fit the reclaim sieve and pan at the stated slope.\n"
    "4. Mount the enclosure hood; fit the N1 inlet, N2..N5 outlets, N6 drain and N7 vent.\n"
    "5. Test: table vibration survey, then a trial knock-out of an INV_CAST campaign tree.\n"
    "6. Inspect against models/mfg/SHELL_BREAK/export/shell_break.step; record dimensions on the traveller.\n")
(HERE / "check.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report))
