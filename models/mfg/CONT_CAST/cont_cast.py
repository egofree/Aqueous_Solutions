"""CONT_CAST manufacturing model, AQS-PLAN-006 work order (X-MFG lane, FOUNDRY-CONT_CAST-10 M3).

Graph revision AC. Study. Not a PE stamp. Reads params.json only.
Two-strand horizontal semi-continuous caster: water-cooled copper mould, withdrawal
rolls, run-out table and billet bed on a common frame (AQS-DUTY-072; AQS-SIZE-FOUNDRY
mould basis). Layout choices named in params.json (layout_note); heights, bores and
ratings per docs-authority/nozzles/CONT_CAST.csv (task-04 schedule). No measured rate
is claimed anywhere.
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
MY = [280.0, 520.0]                                   # the two strand centrelines

# ---------------- frame: base + legs + table deck ----------------
frame = box(0, 0, 0, L, W, 40)                                     # base plate
for (px, py) in ((0, 0), (L - 40, 0), (0, W - 40), (L - 40, W - 40)):
    frame = frame.union(box(px, py, 40, 40, 40, 560))
frame = frame.union(box(0, 0, 580, L, W, 30))                      # table deck z 580..610
frame = frame.union(box(60, 0, 40, 60, W, 1420))                   # gantry leg -X (mould-change hoist)
frame = frame.union(box(L - 120, 0, 40, 60, W, 1420))              # gantry leg +X
frame = frame.union(box(0, 0, 1460, L, 60, 40))                    # hoist beam z 1460..1500
parts["frame"] = frame

# ---------------- mould: water-cooled copper block pair (-X end, z 600 class) ------
mould = box(60, 200, 600, 220, 400, 200)                           # mould housing
mould = mould.cut(box(80, 240, 620, 180, 160, 160))                # strand cavities
for yy in MY:
    mould = mould.cut(rod(45.0, (-5.0, yy, 160.0), "X", 140))      # N1 melt inlet pass into the mould
parts["mould"] = mould
parts["mould_jacket"] = box(50, 190, 590, 240, 420, 30)            # water jacket plate

# ---------------- withdrawal rolls (two per strand) ----------------
rolls = None
for yy in MY:
    for zz in (640.0,):
        for xx in (340.0, 520.0):
            q = rod(45.0, (xx, yy, zz), "X", 90).union(rod(12.0, (xx + 45.0, yy, zz), "X", 25))
            rolls = q if rolls is None else rolls.union(q)
parts["withdrawal_rolls"] = rolls

# ---------------- run-out table (roller conveyor) ----------------
runout = None
for xx in range(700, 1420, 90):
    for yy in MY:
        q = rod(30.0, (xx, yy, 636.0), "Y", 120)   # 2 mm into the deck: fuses
        runout = q if runout is None else runout.union(q)
parts["runout_rollers"] = runout

# ---------------- billet bed (+X end) ----------------
parts["billet_bed"] = box(1400, 180, 575, 100, 440, 35)   # overlaps the deck: fuses

# ---------------- water manifold for the mould ----------------
parts["water_manifold"] = tube(18.0, 14.0, (170.0, 120.0, 605.0), "Y", 560)

# ---------------- nozzle hardware ----------------
parts["melt_inlet"] = tube(DN15, DN15 - W15, (-40.0, 400.0, 160.0), "X", 110)      # N1 -X z 160
parts["billet_stop"] = box(1470.0, 200.0, 610.0, 30.0, 400.0, 120)                 # N2 billet/stock stop +X
st = None
for sx in (400.0, 640.0):
    q = tube(DN15, DN15 - W15, (sx, W - 34.0, 600.0), "Y", 40)                     # N3 stock stubs +Y z 600
    st = q if st is None else st.union(q)
parts["stock_stubs"] = st
parts["drain_well"] = tube(30.5, DN15, (400, 400, 0), "Z", 50)                     # N4
parts["vent_stub"] = tube(DN15, DN15 - W15, (750.0, 400.0, 605.0), "Z", 195)       # N5 up to z 800; 5 mm into the deck: fuses

# ---------------- process inventory solids (not BOM parts) -----------------------
inv = {}
billets = None
for yy in MY:
    q = box(280.0, yy - 40.0, 610.0, 1120.0, 80.0, 80.0)                           # strands on the run-out
    billets = q if billets is None else billets.union(q)
inv["strand_inventory"] = billets

# ---------------- export, checks, BOM --------------------------------------------
asm = cq.Assembly(name="CONT_CAST")
for k, v in list(parts.items()) + list(inv.items()):
    asm.add(v, name=k)
out = HERE / "export"; out.mkdir(exist_ok=True)
asm.export(str(out / "cont_cast.step"))

body = None
for k, v in parts.items():
    body = v if body is None else body.union(v)
cap_solid = body.val()
cap_solid.exportStl(str(out / "cont_cast.stl"), tolerance=0.4, angularTolerance=0.4, ascii=True)

EXTERNAL = ("melt_inlet", "billet_stop", "stock_stubs")   # schedule hardware outside the frame faces
in_env = None
for k, v in parts.items():
    if k in EXTERNAL:
        continue
    in_env = v if in_env is None else in_env.union(v)
in_env_solid = in_env.val()
in_env_solid.exportStl(str(out / "cont_cast_in_envelope.stl"), tolerance=0.4, angularTolerance=0.4, ascii=True)
in_env_solid.scale(0.001).exportStl(str(HERE.parents[2] / "cad" / "stl" / "CONT_CAST.stl"),
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
rho = {"frame": 7.85e-6, "mould": 8.96e-6, "mould_jacket": 7.85e-6, "withdrawal_rolls": 7.85e-6,
       "runout_rollers": 7.85e-6, "billet_bed": 7.85e-6, "water_manifold": 7.85e-6,
       "melt_inlet": 7.85e-6, "billet_stop": 7.85e-6, "stock_stubs": 7.85e-6, "drain_well": 7.85e-6,
       "vent_stub": 7.85e-6}
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
    ["1", f"Caster frame: base {L} x {W} x 40, four posts, table deck z 580..610", 1, "carbon steel",
     mass["frame"], "make", "WORK_ORDER step 1; AQS-DUTY-072 line-machine class"],
    ["2", f"Two-strand mould housing 220 x 400 x 200, water-cooled copper cavities ({D['mould']})", 1,
     "Cu block in a CS housing", mass["mould"] + mass["mould_jacket"], "make",
     "AQS-SIZE-FOUNDRY mould basis; N1 melt inlet -X z 160"],
    ["3", "Withdrawal rolls, 2 per strand, OD 90 with drive quills", 4, "carbon steel",
     mass["withdrawal_rolls"], "make", "WO step 3"],
    ["4", "Run-out roller conveyor, rollers OD 60 at 90 mm pitch", 16, "carbon steel",
     mass["runout_rollers"], "make", "WO step 3"],
    ["5", "Billet bed +X 100 x 440 x 30 with stop", 1, "carbon steel",
     round(mass["billet_bed"] + mass["billet_stop"], 1), "make", "task-04 schedule N2"],
    ["6", "Mould water manifold DN36 class", 1, "carbon steel", mass["water_manifold"], "make",
     "mould cooling per AQS-SIZE-FOUNDRY"],
    ["7", "N3 as-cast stock DN15 stubs +Y z 600", 2, "carbon steel", mass["stock_stubs"], "make",
     "task-04 schedule N3"],
    ["8", "N1 melt inlet DN15 -X z 160 (from IND_MELT N8)", 1, "carbon steel", mass["melt_inlet"], "make",
     "task-04 schedule N1"],
    ["9", "N4 drain well + N5 vent stub", 2, "carbon steel", round(mass["drain_well"] + mass["vent_stub"], 1),
     "make", "task-04 schedule N4/N5"],
]
with open(HERE / "bom.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["item", "description", "qty", "material", "mass_kg", "make_or_buy", "basis"])
    w.writerows(rows)
fast = ('item,size,grade,qty,location,basis\n'
        '1,M10 stud + nut (ISO 4014 / ISO 4032),ISO 898-1 8.8,8,roll stands,study\n'
        '2,M12 anchor,ISO 898-1 8.8,4,frame to slab,study\n')
(HERE / "fasteners.csv").write_text(fast)
wo = (f"# Work order CONT_CAST\n\nAuthority: AQS-DUTY-072 (X-MFG lane). LIVE unit - two-strand caster.\n\n"
      f"1. Fabricate the frame {L} x {W} x 40 base with posts and table deck; set on anchors.\n"
      f"2. Fit the copper mould housing with its water jacket; prove the coolant circuit.\n"
      f"3. Set the withdrawal rolls and run-out rollers; align the strand lines to the mould.\n"
      f"4. Fit the N1 melt inlet, N3 stock stubs, N4 drain and N5 vent.\n"
      f"5. Test: water-side pressure hold, then a dry strand pull; first cast from IND_MELT N8.\n"
      f"6. Inspect against models/mfg/CONT_CAST/export/cont_cast.step; record dimensions on the traveller.\n")
(HERE / "WORK_ORDER.md").write_text(wo)
(HERE / "check.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report))
