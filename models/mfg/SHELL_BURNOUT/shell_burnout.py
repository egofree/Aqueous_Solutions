"""SHELL_BURNOUT manufacturing model, AQS-PLAN-006 work order (X-MFG lane, FOUNDRY-SHELL_BURNOUT-10 M3).

Graph revision AC. Study. Not a PE stamp. Reads params.json only.
Flash-dewax + shell-fire box furnace at 900 C (AQS-DUTY-072): fired shells to
INV_CAST N1, wax condensate reclaimed to WAX_PATTERN N2, unrecovered wax to the
oil line, off-gas burned/vented per the duty sheet. No measured rate is claimed.
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
CX, CY = 450.0, 450.0

# ---------------- casing: CS shell t4 with a front-loading door ----------------
casing = box(0, 0, 0, L, W, H).cut(box(4, 4, 4, L - 8, W - 8, 1442))
casing = casing.cut(box(380.0, 350.0, 60.0, 240.0, 300.0, 500.0))   # door opening -X
casing = casing.cut(rod(45.0, (CX, -5.0, 160.0), "Y", 90.0))        # N1 shell inlet pass (low, -Y? keep -Y front)
casing = casing.cut(rod(45.0, (L - 5.0, 400.0, 600.0), "X", 90.0))     # N2 fired-shell out pass +X z 600
casing = casing.cut(rod(DN15 + 1, (CX + 150.0, W + 5.0, 600.0), "Y", 30))   # N3/N4 stub rows
casing = casing.cut(rod(DN15 + 1, (CX + 250.0, W + 5.0, 600.0), "Y", 30))
casing = casing.cut(rod(DN15 + 1, (700.0, -5.0, 600.0), "Y", 90.0)) # N5 off-gas pass -Y z 600
casing = casing.cut(rod(30.5, (400, 400, -5.0), "Z", 85.0))         # N6 drain pass
casing = casing.cut(rod(DN15 + 1, (400, 400, 800.0), "Z", 40))      # N7 vent pass
parts["casing"] = casing
parts["door"] = box(360.0, 340.0, 50.0, 30.0, 320.0, 520.0)         # front door slab (open position x -30..0 gap)

# ---------------- hot face + element grooves ----------------
fibre = box(4, 4, 4, L - 8, W - 8, 1442).cut(box(154, 154, 154, L - 308, W - 308, 1142))
fibre = fibre.cut(box(60.0, 340.0, 60.0, 200.0, 220.0, 520.0))      # door throat recess
parts["hot_face"] = fibre
parts["hearth_plate"] = box(160.0, 160.0, 160.0, L - 320.0, W - 320.0, 60)   # hearth z 160..220

# ---------------- dewax condenser pan + off-gas collector ----------------
parts["condenser_pan"] = box(560.0, 250.0, 100.0, 220.0, 400.0, 80.0)   # N3 wax condensate pan
parts["offgas_collector"] = box(650.0, 340.0, 480.0, 150.0, 220.0, 160.0)   # N5 collector hood -Y

# ---------------- nozzle hardware ----------------
parts["shell_inlet"] = box(-30.0, 340.0, 40.0, 40.0, 120.0, 150.0)  # N1 -X z 160, full height
parts["fired_out"] = box(990.0, 340.0, 550.0, 40.0, 120.0, 100.0)  # N2 +X z 600, crossing the +X casing wall
parts["condensate_stub"] = tube(DN15, DN15 - W15, (CX + 150.0, W - 34.0, 600.0), "Y", 40)   # N3 +Y
parts["wax_stub"] = tube(DN15, DN15 - W15, (CX + 250.0, W - 34.0, 600.0), "Y", 40)          # N4 +Y
parts["offgas_stub"] = tube(DN15, DN15 - W15, (700.0, -34.0, 600.0), "Y", 40)               # N5 -Y
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

EXTERNAL = ("shell_inlet", "fired_out", "condensate_stub", "wax_stub", "offgas_stub")
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
slack = 50.0
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
report = {
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
     round(mass["casing"] + mass["door"], 1), "make", "duty section 3; WORK_ORDER step 1"],
    ["2", "Ceramic-fibre hot face", 1, "ceramic-fibre board 128 kg/m3", mass["hot_face"], "make",
     "design lining; SCHACHT2004 class"],
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
(HERE / "WORK_ORDER.md").write_text(
    "# Work order SHELL_BURNOUT\n\nAuthority: AQS-DUTY-072 (X-MFG lane). LIVE unit - dewax + burnout furnace.\n\n"
    "1. Fabricate the casing; fit the t-hot-face lining and the hearth plate.\n"
    "2. Hang the front door; prove the seal.\n"
    "3. Fit the condensate pan and the off-gas collector; route N3/N4 to WAX_PATTERN and the oil line.\n"
    "4. Fit N1/N2 shell pass-throughs, N5 off-gas stub, N6 drain and N7 vent.\n"
    "5. Wire the 0.25 kW dewax heaters; interlock the door and the off-gas draft.\n"
    "6. Test: dewax curve with a green shell, then the fire cycle to 900 C.\n"
    "7. Inspect against models/mfg/SHELL_BURNOUT/export/shell_burnout.step; record dimensions on the traveller.\n")
(HERE / "check.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report))
