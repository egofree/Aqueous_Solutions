"""FILM_CAST manufacturing model, AQS-PLAN-006 work order (X-MFG lane, FOUNDRY-FILM_CAST-10 M3).

Graph revision AC. Study. Not a PE stamp. Reads params.json only.
PVDF cast film/sheet line: 25 mm extruder, 200 mm die, OD 150 chill roll, winder
(AQS-DUTY-072; melt 220 C; 316L barrel, Hastelloy die). PVDF resin from POLY_F N5.
No measured rate is claimed anywhere.
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
# ---------------- frame: base + line bed ----------------
frame = box(0, 0, 0, L, W, 40)
for (px, py) in ((0, 0), (L - 60, 0), (0, W - 60), (L - 60, W - 60)):
    frame = frame.union(box(px, py, 40, 60, 60, 810))
frame = frame.union(box(0, 0, 830, L, W, 30))                    # line bed z 830..860
frame = frame.union(box(140, 0, 40, 60, W, 1420))                # gantry legs (roll change-out hoist)
frame = frame.union(box(1200, 0, 40, 60, W, 1420))
frame = frame.union(box(0, 0, 1460, L, W, 40))                   # hoist beam z 1460..1500
parts["frame"] = frame

# ---------------- extruder: barrel + hopper + drive (-X end) ----------------
parts["extruder_barrel"] = rod(D["extruder_D_mm"] / 2 + 8.0, (120.0, 400.0, 940.0), "X", 480)
parts["extruder_hopper"] = cq.Workplane("XY").circle(90).workplane(offset=160).circle(45).loft(ruled=True).translate((150.0, 400.0, 1000.0))
parts["extruder_drive"] = box(60.0, 340.0, 900.0, 90.0, 120.0, 120)
# ---------------- die (Hastelloy, 200 mm) at the barrel tip ----------------
parts["die"] = box(600.0, 300.0, 910.0, 90.0, 200.0, 120)
# ---------------- chill roll OD 150 + pressure roll ----------------
parts["chill_roll"] = rod(D["chill_roll_D_mm"] / 2, (760.0, 400.0, 990.0), "Y", 300)
parts["pressure_roll"] = rod(45.0, (830.0, 400.0, 990.0), "Y", 300)
# ---------------- draw rolls + winder (+X end) ----------------
dr = None
for xx in (980.0, 1100.0, 1220.0):
    q = rod(40.0, (xx, 400.0, 1000.0), "Y", 260)
    dr = q if dr is None else dr.union(q)
parts["draw_rolls"] = dr
parts["winder"] = rod(90.0, (1400.0, 400.0, 1000.0), "Y", 260)

# ---------------- nozzle hardware ----------------
parts["resin_inlet"] = tube(DN15, DN15 - W15, (-34.0, 400.0, 160.0), "X", 40)   # N2 -X z 160
parts["film_stop"] = box(1470.0, 250.0, 900.0, 30.0, 300.0, 160)                # N1 +X z 600..760
parts["drain_well"] = tube(30.5, DN15, (400, 400, 0), "Z", 50)                  # N3
parts["vent_stub"] = tube(DN15, DN15 - W15, (300.0, 80.0, 860.0), "Z", 340)     # N4 to the z 1200 datum

# ---------------- process inventory ----------------
inv = {"film_inventory": box(620.0, 360.0, 1000.0, 760.0, 80.0, 6.0)}           # film web on the line

# ---------------- export, checks, BOM --------------------------------------------
asm = cq.Assembly(name="FILM_CAST")
for k, v in list(parts.items()) + list(inv.items()):
    asm.add(v, name=k)
out = HERE / "export"; out.mkdir(exist_ok=True)
asm.export(str(out / "film_cast.step"))

body = None
for k, v in parts.items():
    body = v if body is None else body.union(v)
body = body.clean()
cap_solid = body.val()
cap_solid.exportStl(str(out / "film_cast.stl"), tolerance=0.4, angularTolerance=0.4, ascii=True)

EXTERNAL = ("resin_inlet", "film_stop")               # schedule hardware at the frame faces
in_env = None
for k, v in parts.items():
    if k in EXTERNAL:
        continue
    in_env = v if in_env is None else in_env.union(v)
in_env_solid = in_env.val()
in_env_solid.exportStl(str(out / "film_cast_in_envelope.stl"), tolerance=0.4, angularTolerance=0.4, ascii=True)
in_env_solid.scale(0.001).exportStl(str(HERE.parents[2] / "cad" / "stl" / "FILM_CAST.stl"),
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
rho = {"frame": 7.85e-6, "extruder_barrel": 7.85e-6, "extruder_hopper": 7.85e-6,
       "extruder_drive": 7.85e-6, "die": 8.9e-6, "chill_roll": 7.85e-6, "pressure_roll": 7.85e-6,
       "draw_rolls": 7.85e-6, "winder": 7.85e-6, "resin_inlet": 7.85e-6, "film_stop": 7.85e-6,
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
    ["1", f"Line frame: base {L} x {W} x 40, four posts, line bed z 830..860", 1, "carbon steel",
     mass["frame"], "make", "WORK_ORDER step 1; AQS-DUTY-072 line-machine class"],
    ["2", f"Extruder: barrel OD {D['extruder_D_mm'] + 16} x 480 with hopper and drive", 1,
     "316L barrel", round(mass["extruder_barrel"] + mass["extruder_hopper"] + mass["extruder_drive"], 1), "make",
     f"design extruder D{D['extruder_D_mm']}; melt {D['melt_C']:.0f} C; 316L barrel per duty section 3"],
    ["3", f"Die 200 mm wide, Hastelloy (design die row)", 1, "Hastelloy C-276", mass["die"], "make",
     f"design die {D['die_mm']} mm; Hastelloy die per duty section 3"],
    ["4", f"Chill roll OD {D['chill_roll_D_mm']} x 300 + pressure roll OD 90", 2, "carbon steel (jacket class)",
     round(mass["chill_roll"] + mass["pressure_roll"], 1), "make", "WO step 3"],
    ["5", "Draw rolls OD 80 at x 980/1100/1220", 3, "carbon steel", mass["draw_rolls"], "make", "WO step 3"],
    ["6", "Winder OD 180 x 260 at +X", 1, "carbon steel", mass["winder"], "make", "WO step 3"],
    ["7", "N2 PVDF resin DN15 inlet -X z 160 (from POLY_F N5)", 1, "carbon steel", mass["resin_inlet"], "make",
     "task-04 schedule N2"],
    ["8", "N1 film stock stop +X (solids, bore not calculated)", 1, "carbon steel", mass["film_stop"], "make",
     "task-04 schedule N1"],
    ["9", "N3 drain well + N4 vent stub", 2, "carbon steel", round(mass["drain_well"] + mass["vent_stub"], 1),
     "make", "task-04 schedule N3/N4"],
]
with open(HERE / "bom.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["item", "description", "qty", "material", "mass_kg", "make_or_buy", "basis"])
    w.writerows(rows)
(HERE / "fasteners.csv").write_text(
    'item,size,grade,qty,location,basis\n'
    '1,M10 anchor,ISO 898-1 8.8,4,frame to slab,study\n')
(HERE / "WORK_ORDER.md").write_text(
    "# Work order FILM_CAST\n\nAuthority: AQS-DUTY-072 (X-MFG lane). LIVE unit - PVDF cast film line.\n\n"
    "1. Fabricate the line frame with the bed; set on anchors.\n"
    "2. Fit the extruder (316L barrel), hopper and drive; fit the Hastelloy die.\n"
    "3. Set the chill roll, pressure roll, draw rolls and winder; align the web path.\n"
    "4. Fit the N2 resin inlet, N1 film stop, N3 drain and N4 vent.\n"
    "5. Test: extruder dry heat at 220 C, then a trial web from POLY_F N5 resin.\n"
    "6. Inspect against models/mfg/FILM_CAST/export/film_cast.step; record dimensions on the traveller.\n")
(HERE / "check.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report))
