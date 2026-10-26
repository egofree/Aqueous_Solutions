"""INV_CAST manufacturing model, AQS-PLAN-006 work order (X-MFG lane, FOUNDRY-INV_CAST-10 M3).

Graph revision AC. Study. Not a PE stamp. Reads params.json only.
Investment casting tilt-pour station: fired-shell mould clamp, pour cup and tilt
station, campaign of 8 moulds (AQS-DUTY-072). Melt arrives from IND_MELT N14.
Layout choices named in params.json (layout_note); heights, bores and ratings per
docs-authority/nozzles/INV_CAST.csv (task-04 schedule). No measured rate is claimed.
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
# ---------------- frame: base, posts, table deck ----------------
frame = box(0, 0, 0, L, W, 40)
for (px, py) in ((0, 0), (L - 40, 0), (0, W - 40), (L - 40, W - 40)):
    frame = frame.union(box(px, py, 40, 40, 40, 560))
frame = frame.union(box(0, 0, 580, L, W, 30))                      # table deck z 580..610
frame = frame.union(box(200, 0, 40, 60, W, 1420))                  # gantry leg (mould change-out hoist)
frame = frame.union(box(L - 260, 0, 40, 60, W, 1420))              # gantry leg +X
frame = frame.union(box(0, 0, 1460, L, 60, 40))                    # hoist beam z 1460..1500
parts["frame"] = frame

# ---------------- mould clamp station (fired shell, campaign of 8) ----------------
clamp = box(200.0, 250.0, 610.0, 300.0, 300.0, 260.0)
clamp = clamp.cut(box(230.0, 280.0, 640.0, 240.0, 240.0, 240.0))   # mould cavity, open through the top
parts["mould_clamp"] = clamp
cone_from = cq.Workplane("XY").circle(90).workplane(offset=120).circle(50).loft(ruled=True).translate((680.0, 400.0, 790.0))
parts["pour_station"] = box(560.0, 250.0, 610.0, 240.0, 300.0, 180.0).union(cone_from)

# ---------------- cast-out roller bed (+X) ----------------
bed = None
for xx in range(950, 1440, 100):
    for yy in (280.0, 520.0):
        q = rod(30.0, (xx, yy, 636.0), "Y", 120)
        bed = q if bed is None else bed.union(q)
parts["cast_out_bed"] = bed

# ---------------- nozzle hardware ----------------
parts["shell_inlet"] = box(-30.0, 340.0, 40.0, 40.0, 120.0, 150)   # N1 -X z 160, full height to the base
st = None
stands = None
for sx in (240.0, 400.0):
    q = tube(DN15, DN15 - W15, (sx, -34.0, 160.0), "Y", 40)        # N2/N3 melt DN15 -Y z 160
    st = q if st is None else st.union(q)
    pd = box(sx - 20.0, -30.0, 30.0, 40.0, 46.0, 120.0)            # pipe stand to the base: fuses
    stands = pd if stands is None else stands.union(pd)
parts["melt_stubs"] = st
parts["melt_stub_stands"] = stands
parts["cast_out_stop"] = box(1470.0, 250.0, 610.0, 30.0, 300.0, 120)   # N4 +X z 600
parts["drain_well"] = tube(30.5, DN15, (400, 400, 0), "Z", 50)     # N5
parts["vent_stub"] = tube(DN15, DN15 - W15, (750.0, 400.0, 610.0), "Z", 190)   # N6 up to z 800

# ---------------- process inventory ----------------
inv = {"mould_inventory": box(240.0, 290.0, 650.0, 220.0, 220.0, 150.0)}   # shell mould stack in the clamp

# ---------------- export, checks, BOM --------------------------------------------
asm = cq.Assembly(name="INV_CAST")
for k, v in list(parts.items()) + list(inv.items()):
    asm.add(v, name=k)
out = HERE / "export"; out.mkdir(exist_ok=True)
asm.export(str(out / "inv_cast.step"))

body = None
for k, v in parts.items():
    body = v if body is None else body.union(v)
cap_solid = body.val()
cap_solid.exportStl(str(out / "inv_cast.stl"), tolerance=0.4, angularTolerance=0.4, ascii=True)

EXTERNAL = ("shell_inlet", "cast_out_stop", "melt_stubs", "melt_stub_stands")   # -Y schedule hardware at the frame faces
in_env = None
for k, v in parts.items():
    if k in EXTERNAL:
        continue
    in_env = v if in_env is None else in_env.union(v)
in_env_solid = in_env.val()
in_env_solid.exportStl(str(out / "inv_cast_in_envelope.stl"), tolerance=0.4, angularTolerance=0.4, ascii=True)
in_env_solid.scale(0.001).exportStl(str(HERE.parents[2] / "cad" / "stl" / "INV_CAST.stl"),
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
rho = {"frame": 7.85e-6, "mould_clamp": 7.85e-6, "pour_station": 7.85e-6, "cast_out_bed": 7.85e-6,
       "shell_inlet": 7.85e-6, "melt_stubs": 7.85e-6, "cast_out_stop": 7.85e-6,
       "drain_well": 7.85e-6, "vent_stub": 7.85e-6, "melt_stub_stands": 7.85e-6}
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
    ["1", f"Frame: base {L} x {W} x 40, four posts, table deck z 580..610", 1, "carbon steel",
     mass["frame"], "make", "WORK_ORDER step 1; AQS-DUTY-072 line-machine class"],
    ["2", f"Shell-mould clamp station 300 x 300 x 260 (campaign of {D['molds_per_campaign']} moulds)", 1,
     "carbon steel", mass["mould_clamp"], "make", "design campaign row; task-04 schedule N1"],
    ["3", "Tilt-pour station with pour cone", 1, "carbon steel + refractory", mass["pour_station"], "make",
     "task-04 schedule N2/N3; melt from IND_MELT N14"],
    ["4", "Cast-out roller bed +X with stop", 1, "carbon steel",
     round(mass["cast_out_bed"] + mass["cast_out_stop"], 1), "make", "task-04 schedule N4"],
    ["5", "N1 fired-shell inlet chute -X z 160", 1, "carbon steel", mass["shell_inlet"], "make",
     "task-04 schedule N1 (from SHELL_BURNOUT N2)"],
    ["6", "N2/N3 melt DN15 stubs -Y z 160", 2, "carbon steel", mass["melt_stubs"], "make",
     "task-04 schedule N2/N3"],
    ["7", "N2/N3 melt-stub pipe stands to the base", 2, "carbon steel", mass["melt_stub_stands"], "make", "WO step 4"],
    ["8", "N5 drain well + N6 vent stub", 2, "carbon steel", round(mass["drain_well"] + mass["vent_stub"], 1),
     "make", "task-04 schedule N5/N6"],
]
with open(HERE / "bom.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["item", "description", "qty", "material", "mass_kg", "make_or_buy", "basis"])
    w.writerows(rows)
(HERE / "fasteners.csv").write_text(
    'item,size,grade,qty,location,basis\n'
    '1,M12 stud + nut (ISO 4014 / ISO 4032),ISO 898-1 8.8,8,clamp station,study\n'
    '2,M12 anchor,ISO 898-1 8.8,4,frame to slab,study\n')
(HERE / "WORK_ORDER.md").write_text(
    f"# Work order INV_CAST\n\nAuthority: AQS-DUTY-072 (X-MFG lane). LIVE unit - investment tilt-pour station.\n\n"
    f"1. Fabricate the frame {L} x {W} x 40 base with posts and table deck; set on anchors.\n"
    f"2. Fit the shell-mould clamp station; prove the {D['molds_per_campaign']}-mould campaign clamp.\n"
    f"3. Set the tilt-pour station and the cast-out roller bed; align to the clamp.\n"
    f"4. Fit the N1 shell inlet, N2/N3 melt stubs, N5 drain and N6 vent.\n"
    f"5. Test: clamp-pressure hold, then a trial pour from IND_MELT N14.\n"
    f"6. Inspect against models/mfg/INV_CAST/export/inv_cast.step; record dimensions on the traveller.\n")
(HERE / "check.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report))
