"""TI_CELL manufacturing model, AQS-PLAN-006 work order (X-MFG lane, FOUNDRY-TI_CELL-10 M3).

Graph revision AC. Study. Not a PE stamp. Reads params.json only.
Kroll train in one frame: chlorinator (TiO2 + 2C + 2Cl2 -> TiCl4 + 2CO at 800 C), TiCl4
condenser, and the Mg-reduction retort (TiCl4 + 2Mg -> Ti + 2MgCl2 at 900 C, batch
campaigns at the 0.5 kg/d Ti scale, AQS-BAL-KROLL). The chlorine loop closes with
MG_POT: its N6 chlorinator feed is this train's N9, and the retort MgCl2 returns
through N6 (A-M-280 ruling, A-M-284 D-DOCK feedstock). Layout choices named in
params.json (layout_note); heights, bores and ratings per
docs-authority/nozzles/TI_CELL.csv (task-04 schedule). Materials per
docs-authority/duties/TI_CELL.md section 3. No measured rate is claimed anywhere.
"""
import csv, json, math, pathlib
import cadquery as cq

HERE = pathlib.Path(__file__).parent
P = json.loads((HERE / "params.json").read_text())
A = P["assumptions"]
D = P["design"]
L, W, H = P["size_mm"]

def box(x, y, z, dx, dy, dz):
    return cq.Workplane().box(dx, dy, dz, centered=False).translate((x, y, z))

def tube(r_out, r_in, p, axis, ln):
    d = {"X": ((1, 0, 0), (0, 1, 0)), "Y": ((0, 1, 0), (1, 0, 0)), "Z": ((0, 0, 1), (1, 0, 0))}[axis]
    pl = cq.Plane(origin=p, xDir=d[1], normal=d[0])
    return cq.Workplane(pl).circle(r_out).circle(r_in).extrude(ln)

def rod(r, p, axis, ln):
    return tube(r, 0, p, axis, ln)

def cyl_z(x, y, z, r, h):
    return rod(r, (x, y, z), "Z", h)

def cone_z(x, y, z, r_bot, r_top, h):
    return cq.Workplane("XY").circle(r_bot).workplane(offset=h).circle(r_top).loft(ruled=True).translate((x, y, z))

parts = {}
RC, RD = A["chlorinator_r_mm"], A["chlorinator_r_mm"]          # chlorinator radius 90
RV, RRed = A["condenser_r_mm"], A["retort_r_mm"]               # 70 / 100
cx, cy = 170.0, 560.0                                          # chlorinator centre
vx, vy = 400.0, 560.0                                          # condenser centre
rx_, ry_ = 660.0, 520.0                                        # reduction retort centre
DN15, W15 = A["DN15_OD_mm"] / 2, A["DN15_wall_mm"]

# ---------------- chlorinator: retort + heater band + charge hopper ----------------
parts["chlorinator"] = cyl_z(cx, cy, 240, RC, 640).union(cone_z(cx, cy, 880, 80, 35, 70))
parts["chlorinator_band"] = ring_z_local = tube(RC + 15, RC, (cx, cy, 260), "Z", 320)
# ---------------- TiCl4 condenser + water band --------------------------------------
parts["condenser"] = cyl_z(vx, vy, 240, RV, 420)
parts["condenser_band"] = tube(RV + 15, RV, (vx, vy, 300), "Z", 200)
# ---------------- Mg-reduction retort + furnace box + Mg charge hopper --------------
parts["reduction_retort"] = cyl_z(rx_, ry_, 200, RRed, 520)
parts["furnace_box"] = box(rx_ - 100, ry_ - 120, 60, 200, 240, 420)
parts["mg_hopper"] = cone_z(rx_, ry_, 720, 55, 20, 240)
# ---------------- interconnects ------------------------------------------------------
parts["x_chlor_cond"] = cyl_z(0, 0, 0, 1, 1).cut(rod(1, (0, 0, 0), "X", 1))  # placeholder replaced below
parts["x_chlor_cond"] = rod(12, (cx + RC - 2, cy, 560), "X", vx - RV - cx - RC + 4)
parts["x_cond_retort"] = rod(12, (vx + RV - 2, vy, 600), "X", rx_ - RRed - vx - RV + 4)
# ---------------- MgCl2 drag-out trough ---------------------------------------------
parts["mgcl2_trough"] = box(80, 60, 40, 640, 110, 90).cut(box(88, 68, 48, 624, 94, 74))

# ---------------- skid: base plate, posts, retort lift beam, vessel pedestals -------
# The batch retort lifts in and out per campaign, so the frame carries a top lift
# beam; the pedestals hold the vessels at the interconnect heights (AQS-DUTY-072).
frame = box(0, 0, 0, L, W, 60)                                     # base plate
for (px, py) in ((0, 0), (L - 40, 0), (0, W - 40), (L - 40, W - 40)):
    frame = frame.union(box(px, py, 60, 40, 40, 1500))             # posts to the lift beam
frame = frame.union(box(0, 380, 1560, L, 40, 40))                  # retort lift beam z 1560..1600
frame = frame.union(box(cx - RC - 20, cy - RC - 20, 60, 2 * RC + 40, 2 * RC + 40, 180))   # chlorinator pedestal z 60..240
frame = frame.union(box(vx - RV - 20, vy - RV - 20, 60, 2 * RV + 40, 2 * RV + 40, 180))   # condenser pedestal
frame = frame.union(box(rx_ - RRed - 20, ry_ - RRed - 20, 60, 2 * RRed + 40, 2 * RRed + 40, 140))  # retort pedestal z 60..200
parts["skid_frame"] = frame

# ---------------- nozzle hardware (task-04 schedule; attached to the vessels) -------
# N2 dense grit / N10 rutile / N11 carbon: charge chutes on the chlorinator (-X face)
ch = None
for yy in (500.0, 560.0, 620.0):
    q = box(55, yy - 30, 130, 50, 60, 90)
    ch = q if ch is None else ch.union(q)
parts["charge_chutes"] = ch
# N3/N9 chlorine DN15 stubs (-Y shell of the chlorinator at z 160)
st = None
for xx in (140.0, 200.0):
    q = tube(DN15, DN15 - W15, (xx, 455.0, 160.0), "Y", 60)
    st = q if st is None else st.union(q)
parts["cl2_stubs"] = st
# N12 CO export DN15 (+Y shell at z 600)
parts["co_stub"] = tube(DN15, DN15 - W15, (cx, cy + RC - 10.0, 600.0), "Y", 55)
# N1 slag tap spout (+X shell at z 600)
slag = rod(30.0, (cx + RC - 10.0, cy, 570.0), "X", 60).cut(rod(12.0, (cx + RC - 20.0, cy, 565.0), "X", 90))
parts["slag_spout"] = slag
# N4/N5 harvest ports (+X on the retort at z 600)
h = None
for yy in (460.0, 580.0):
    q = tube(45.0, 32.0, (rx_ + RRed - 15.0, yy, 600.0), "X", 50)
    h = q if h is None else h.union(q)
parts["harvest_ports"] = h
# N6 MgCl2 return DN15 + N7 drag-out DN15 (+Y shell of the retort at z 600)
s2 = None
for xx in (620.0, 720.0):
    q = tube(DN15, DN15 - W15, (xx, 550.0, 600.0), "Y", 65)
    s2 = q if s2 is None else s2.union(q)
parts["mgcl2_stubs"] = s2
# N8 Mg reductant chute (-X on the retort at z 160)
parts["mg_chute"] = box(535.0, ry_ - 30.0, 130, 40, 60, 90)
# N13 drain well (through the chlorinator pedestal to the bottom-schedule sump face z 50)
parts["drain_well"] = tube(30.0, DN15, (cx, cy, 0), "Z", 250)
# N14 vent: riser from the condenser top to the schedule datum z 800
parts["vent_riser"] = tube(DN15, DN15 - W15, (vx, vy, 660.0), "Z", 140)
parts["vent_stub"] = tube(DN15, DN15 - W15, (vx, vy + DN15, 800.0), "Y", -40)

# ---------------- process inventory solids (not BOM parts) -------------------------
inv = {"ti_sponge": cyl_z(rx_ - 30, ry_, 200, 55, 300)}      # sponge mass in the retort (study fill)

# ---------------- export, checks, BOM ----------------------------------------------
asm = cq.Assembly(name="TI_CELL")
for k, v in list(parts.items()) + list(inv.items()):
    asm.add(v, name=k)
out = HERE / "export"; out.mkdir(exist_ok=True)
asm.export(str(out / "ti_cell.step"))

body = None
for k, v in parts.items():
    body = v if body is None else body.union(v)
cap_solid = body.val()
cap_solid.exportStl(str(out / "ti_cell.stl"), tolerance=0.4, angularTolerance=0.4, ascii=True)

EXTERNAL = ()   # the schedule hardware attaches to the vessels and stays in envelope
in_env = None
for k, v in parts.items():
    if k in EXTERNAL:
        continue
    in_env = v if in_env is None else in_env.union(v)
in_env_solid = in_env.val()
in_env_solid.exportStl(str(out / "ti_cell_in_envelope.stl"), tolerance=0.4, angularTolerance=0.4, ascii=True)
in_env_solid.scale(0.001).exportStl(str(HERE.parents[2] / "cad" / "stl" / "TI_CELL.stl"),
                                    tolerance=0.0005, angularTolerance=0.4, ascii=True)

ALL = list(parts.values()) + list(inv.values())
vessel_parts = [parts[k] for k in ("chlorinator", "condenser", "reduction_retort")]
sb = cq.Compound.makeCompound([v.val() for v in vessel_parts]).BoundingBox()
tb_ = cq.Compound.makeCompound([v.val() for v in ALL]).BoundingBox()
slack = 50.0
inside_shell = bool(sb.xmin >= -1 and sb.xmax <= L + 1 and sb.ymin >= -1 and sb.ymax <= W + 1
                    and sb.zmin >= -1 and sb.zmax <= H + 1)
overhang = {"-X": round(-tb_.xmin, 1), "+X": round(tb_.xmax - L, 1),
            "-Y": round(-tb_.ymin, 1), "+Y": round(tb_.ymax - W, 1)}
overhang_ok = all(v <= slack + 1 for v in overhang.values())
valid = all(v.val().isValid() for v in ALL)
rho = {"chlorinator": 7.85e-6, "chlorinator_band": 7.85e-6, "condenser": 7.85e-6,
       "condenser_band": 7.85e-6, "reduction_retort": 7.85e-6, "furnace_box": 7.85e-6,
       "mg_hopper": 7.85e-6, "x_chlor_cond": 7.85e-6, "x_cond_retort": 7.85e-6,
       "mgcl2_trough": 7.85e-6, "charge_chutes": 7.85e-6, "cl2_stubs": 7.85e-6,
       "co_stub": 7.85e-6, "slag_spout": 7.85e-6, "harvest_ports": 7.85e-6,
       "mgcl2_stubs": 7.85e-6, "mg_chute": 7.85e-6, "drain_well": 7.85e-6, "vent_stub": 7.85e-6, "vent_riser": 7.85e-6, "skid_frame": 7.85e-6}
mass = {k: round(v.val().Volume() * rho[k], 1) for k, v in parts.items()}
report = {
    "vessel_bbox_mm": [round(sb.xlen, 1), round(sb.ylen, 1), round(sb.zlen, 1)],
    "vessel_bbox_abs": [round(sb.xmin, 1), round(sb.ymin, 1), round(sb.zmin, 1),
                        round(sb.xmax, 1), round(sb.ymax, 1), round(sb.zmax, 1)],
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
    ["1", f"Kroll chlorinator retort, OD {2 * RC} x 640 mm at 800 C", 1, "carbon steel (dry hot Cl2)",
     mass["chlorinator"], "make", "duty section 2/3; TiO2 + 2C + 2Cl2 -> TiCl4 + 2CO at 800 C; heater band item 2"],
    ["2", f"Chlorinator heater band, OD {2 * (RC + 15)} x 320 mm", 1, "CS with element pockets",
     mass["chlorinator_band"], "make", "AQS-DUTY-072 section 4; hold duty per the design row"],
    ["3", f"TiCl4 condenser, OD {2 * RV} x 420 mm with the water band", 1, "carbon steel",
     round(mass["condenser"] + mass["condenser_band"], 1), "make", "duty section 2; condenser at 300..500 water band"],
    ["4", f"Mg-reduction retort, OD {2 * RRed} x 520 mm at {D['retort_T_C']:.0f} C", 1, "carbon steel (retort class)",
     mass["reduction_retort"], "make", "duty section 2; batch campaigns at the 0.5 kg/d Ti scale"],
    ["5", "Reduction furnace box 200 x 240 x 420", 1, "CS with element pockets",
     mass["furnace_box"], "make", "AQS-DUTY-072 section 4"],
    ["6", "Mg charge hopper cone on the retort", 1, "carbon steel", mass["mg_hopper"], "make",
     f"{D['mg_kg_d']} kg/d Mg reductant per campaign (AQS-BAL-KROLL)"],
    ["7", "Interconnects: chlorinator->condenser and condenser->retort, OD 24 t 2", 2, "carbon steel (dry hot Cl2/TiCl4)",
     round(mass["x_chlor_cond"] + mass["x_cond_retort"], 1), "make", "WO step 4; slope per the isometric"],
    ["8", "MgCl2 drag-out trough 640 x 110 x 90", 1, "carbon steel", mass["mgcl2_trough"], "make",
     "salt drag-out to the flux-cover source (task-04 schedule N7)"],
    ["9", f"N2/N10/N11 charge chutes -X z 160 ({D['tio2_kg_d']} kg/d TiO2-class + {D['c_kg_d']} kg/d carbon + grit)", 3,
     "CS chute, refractory throat", mass["charge_chutes"], "make", "task-04 schedule N2/N10/N11; A-M-284 feedstock ruling"],
    ["10", f"N3/N9 chlorine DN15 stubs -Y z 600 ({D['cl2_kg_d']} kg/d loop with MG_POT)", 2,
     "carbon steel (dry hot Cl2)", mass["cl2_stubs"], "make", "task-04 schedule N3/N9; A-M-280 ruling"],
    ["11", f"N12 CO export DN15 +Y z 600 ({D['co_kg_d']} kg/d, fuel-gas class)", 1, "carbon steel",
     mass["co_stub"], "make", "task-04 schedule N12"],
    ["12", "N1 slag tap spout +Y z 600", 1, "carbon (refractory class)", mass["slag_spout"], "make",
     "task-04 schedule N1 (solids, bore not calculated)"],
    ["13", "N4/N5 harvest ports +X z 600 (Ti sponge/powder to vacuum melt)", 2, "carbon steel",
     mass["harvest_ports"], "make", "task-04 schedule N4/N5; harvest at the campaign end"],
    ["14", "N6/N7 MgCl2 DN15 stubs +Y z 600 (return to MG_POT; drag-out to flux)", 2, "carbon steel",
     mass["mgcl2_stubs"], "make", f"task-04 schedule N6/N7; {D['mgcl2_gross_kg_d']} kg/d gross loop"],
    ["15", "N8 Mg reductant chute -X z 160 on the retort", 1, "CS chute", mass["mg_chute"], "make",
     "task-04 schedule N8"],
    ["16", "N13 drain well + N14 vent riser and stub", 3, "carbon steel", round(mass["drain_well"] + mass["vent_stub"] + mass["vent_riser"], 1),
     "make", "task-04 schedule N13/N14"],
    ["17", "Skid frame: base plate 800 x 800 x 60, four posts, retort lift beam z 1560..1600, vessel pedestals", 1,
     "carbon steel", mass["skid_frame"], "make",
     "the batch retort lifts in and out per campaign; X-ASM-01 install sequence"],
]
with open(HERE / "bom.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["item", "description", "qty", "material", "mass_kg", "make_or_buy", "basis"])
    w.writerows(rows)
fast = ('item,size,grade,qty,location,basis\n'
        '1,M10 stud + nut (ISO 4014 / ISO 4032),ISO 898-1 8.8,12,retort flange and harvest ports,study\n'
        '2,M8 x 25 hopper bolts,ISO 898-1 8.8,8,Mg hopper rim,study\n')
(HERE / "fasteners.csv").write_text(fast)
wo = (f"# Work order TI_CELL\n\nAuthority: AQS-DUTY-072 (X-MFG lane). LIVE unit - Kroll train on the D-DOCK feedstock (A-M-284).\n\n"
      f"1. Fabricate the chlorinator retort OD {2 * RC} x 640 mm with the heater band; dry-out per the refractory class.\n"
      f"2. Fabricate the TiCl4 condenser OD {2 * RV} x 420 mm with the water band; prove the coolant loop.\n"
      f"3. Fabricate the reduction retort OD {2 * RRed} x 520 mm and the furnace box; leak-check under vacuum.\n"
      f"4. Set the interconnects with the stated slope; dry Cl2 service, no dead legs.\n"
      f"5. Mount the charge chutes (N2/N10/N11), the Cl2 stubs (N3/N9), the CO export (N12) and the slag spout (N1).\n"
      f"6. Mount the harvest ports (N4/N5), the MgCl2 stubs (N6/N7), the Mg chute (N8), drain (N13) and vent (N14).\n"
      f"7. Campaign test: chlorination run to TiCl4, then the reduction batch; harvest the sponge at N4/N5.\n"
      f"8. Inspect against models/mfg/TI_CELL/export/ti_cell.step; record dimensions on the traveller.\n")
(HERE / "WORK_ORDER.md").write_text(wo)
(HERE / "check.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report))
