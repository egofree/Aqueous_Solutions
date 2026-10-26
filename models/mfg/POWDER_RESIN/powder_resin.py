"""POWDER_RESIN manufacturing model, AQS-PLAN-006 work order (X-MFG lane, FOUNDRY-POWDER_RESIN-10 M3).

Graph revision AC. Study. Not a PE stamp. Reads params.json only.
PTFE powder line: pin mill + cyclone classifier + collector (AQS-DUTY-072; PTFE is
not melt-processable, ULLMANN_FLUOROPOLY; 316L mill, PE-lined collector). Fluoro-
polymer powder arrives from POLY_F N4. No measured rate is claimed anywhere.
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
# ---------------- frame ----------------
frame = box(0, 0, 0, L, W, 40)
for (px, py) in ((0, 0), (L - 60, 0), (0, W - 60), (L - 60, W - 60)):
    frame = frame.union(box(px, py, 40, 60, 60, 1420))                 # posts to the z 1480 datum
frame = frame.union(box(0, 0, 1460, L, W, 40))                         # top rail z 1460..1500
parts["frame"] = frame

# ---------------- pin mill (316L) at -X ----------------
parts["mill"] = rod(110.0, (260.0, 400.0, 300.0), "X", 240).union(rod(45.0, (120.0, 400.0, 300.0), "X", 140))
parts["mill_motor"] = box(60.0, 330.0, 240.0, 100.0, 140.0, 120)

# ---------------- cyclone classifier + collector ----------------
parts["cyclone"] = rod(110.0, (620.0, 400.0, 300.0), "Z", 520).union(
    cq.Workplane("XY").circle(110).workplane(offset=520).circle(40).loft(ruled=True).translate((620, 400, 300)))
parts["collector"] = box(760.0, 250.0, 240.0, 340.0, 300.0, 460).cut(
    box(775.0, 265.0, 255.0, 310.0, 270.0, 430.0))                  # PE-lined collector
# ---------------- ducts: mill -> cyclone -> collector ----------------
parts["duct_mill_cyc"] = rod(40.0, (380.0, 400.0, 400.0), "X", 140)
parts["duct_cyc_col"] = tube(40.0, 34.0, (620.0, 400.0, 820.0), "Z", 40)

# ---------------- nozzle hardware ----------------
parts["powder_inlet"] = box(-30.0, 340.0, 40.0, 40.0, 120.0, 100.0)   # N1 -X z 160, full height
parts["powder_out"] = box(1440.0, 300.0, 240.0, 60.0, 200.0, 160.0)   # N2 +X at the collector
parts["drain_well"] = tube(30.5, DN15, (400, 400, 0), "Z", 50)        # N3 (nominal)
parts["vent_stub"] = tube(DN15, DN15 - W15, (620.0, 400.0, 860.0), "Z", 340)   # N4 to the z 1200 datum

# ---------------- process inventory ----------------
inv = {"powder_inventory": box(790.0, 280.0, 300.0, 280.0, 240.0, 350.0)}   # powder in the collector

# ---------------- export, checks, BOM --------------------------------------------
asm = cq.Assembly(name="POWDER_RESIN")
for k, v in list(parts.items()) + list(inv.items()):
    asm.add(v, name=k)
out = HERE / "export"; out.mkdir(exist_ok=True)
asm.export(str(out / "powder_resin.step"))

body = None
for k, v in parts.items():
    body = v if body is None else body.union(v)
body = body.clean()
cap_solid = body.val()
cap_solid.exportStl(str(out / "powder_resin.stl"), tolerance=0.4, angularTolerance=0.4, ascii=True)

EXTERNAL = ("powder_inlet", "powder_out")
in_env = None
for k, v in parts.items():
    if k in EXTERNAL:
        continue
    in_env = v if in_env is None else in_env.union(v)
in_env_solid = in_env.val()
in_env_solid.exportStl(str(out / "powder_resin_in_envelope.stl"), tolerance=0.4, angularTolerance=0.4, ascii=True)
in_env_solid.scale(0.001).exportStl(str(HERE.parents[2] / "cad" / "stl" / "POWDER_RESIN.stl"),
                                    tolerance=0.0005, angularTolerance=0.4, ascii=True)

ALL = list(parts.values()) + list(inv.values())
sb = cq.Compound.makeCompound([parts["mill"].val()]).BoundingBox()
tb_ = cq.Compound.makeCompound([v.val() for v in ALL]).BoundingBox()
slack = 50.0
inside_shell = bool(sb.xmin >= -1 and sb.xmax <= L + 1 and sb.ymin >= -1 and sb.ymax <= W + 1
                    and sb.zmin >= -1 and sb.zmax <= H + 1)
overhang = {"-X": round(-tb_.xmin, 1), "+X": round(tb_.xmax - L, 1),
            "-Y": round(-tb_.ymin, 1), "+Y": round(tb_.ymax - W, 1)}
overhang_ok = all(v <= slack + 1 for v in overhang.values())
valid = all(v.val().isValid() for v in ALL)
rho = {"frame": 7.85e-6, "mill": 7.85e-6, "mill_motor": 7.85e-6, "cyclone": 7.85e-6,
       "collector": 7.85e-6, "duct_mill_cyc": 7.85e-6, "duct_cyc_col": 7.85e-6,
       "powder_inlet": 7.85e-6, "powder_out": 7.85e-6, "drain_well": 7.85e-6, "vent_stub": 7.85e-6}
mass = {k: round(v.val().Volume() * rho[k], 1) for k, v in parts.items()}
report = {
    "mill_bbox_mm": [round(sb.xlen, 1), round(sb.ylen, 1), round(sb.zlen, 1)],
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
    ["1", f"Frame: base {L} x {W} x 40, four 60 x 60 posts", 1, "carbon steel", mass["frame"], "make",
     "WORK_ORDER step 1; AQS-DUTY-072 line-machine class"],
    ["2", f"Pin mill OD 220 x 240, 316L ({D['mill_kWh_kg']} kWh/kg specific energy)", 1, "316L",
     round(mass["mill"] + mass["mill_motor"], 1), "make", "design mill row; duty section 3"],
    ["3", "Cyclone classifier OD 220 x 520 + cone", 1, "316L", mass["cyclone"], "make", "duty section 2"],
    ["4", "PE-lined collector 340 x 300 x 460", 1, "CS with PE liner", mass["collector"], "make",
     "duty section 3 (PE-lined collector)"],
    ["5", "Ducts: mill -> cyclone OD 80, cyclone -> collector return", 2, "316L",
     round(mass["duct_mill_cyc"] + mass["duct_cyc_col"], 1), "make", "WO step 4"],
    ["6", "N1 powder inlet chute -X z 160 (from POLY_F N4)", 1, "carbon steel", mass["powder_inlet"], "make",
     "task-04 schedule N1"],
    ["7", "N2 powder stock out +X at the collector (to STOCK_OUT N6)", 1, "carbon steel", mass["powder_out"],
     "make", "task-04 schedule N2"],
    ["8", "N3 nominal drain + N4 vent riser to the z 1200 datum", 2, "carbon steel",
     round(mass["drain_well"] + mass["vent_stub"], 1), "make", "task-04 schedule N3/N4"],
]
with open(HERE / "bom.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["item", "description", "qty", "material", "mass_kg", "make_or_buy", "basis"])
    w.writerows(rows)
(HERE / "fasteners.csv").write_text(
    'item,size,grade,qty,location,basis\n'
    '1,M10 anchor,ISO 898-1 8.8,4,frame to slab,study\n')
(HERE / "WORK_ORDER.md").write_text(
    "# Work order POWDER_RESIN\n\nAuthority: AQS-DUTY-072 (X-MFG lane). LIVE unit - PTFE powder line.\n\n"
    "1. Fabricate the frame; set on anchors.\n"
    "2. Fit the pin mill with its drive (316L); fit the cyclone and the PE-lined collector.\n"
    "3. Route the ducts mill -> cyclone -> collector; prove the airflow.\n"
    "4. Fit the N1 inlet chute, N2 powder outlet, N3 drain and N4 vent.\n"
    "5. Test: mill trial on PTFE rework, then classifier cut-size check.\n"
    "6. Inspect against models/mfg/POWDER_RESIN/export/powder_resin.step; record dimensions on the traveller.\n")
(HERE / "check.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report))
